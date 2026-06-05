import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from utils.audio_loader import AudioLoader
from audio_analysis.segment_finder import SegmentFinder
from mixing.transition_manager import TransitionManager
from youtube.playlist_downloader import PlaylistDownloader


def _to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim > 1:
        return np.mean(audio, axis=1)
    return audio


def _ensure_stereo(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return np.column_stack([audio, audio])
    if audio.shape[1] == 1:
        return np.column_stack([audio[:, 0], audio[:, 0]])
    return audio


def _process_track_worker(task):
    # Module-level so it is picklable for ProcessPoolExecutor (Windows 'spawn').
    file_path, num_segments, sample_rate, min_duration, max_duration = task

    loader = AudioLoader(sample_rate=sample_rate)
    finder = SegmentFinder(min_duration=min_duration, max_duration=max_duration)

    # Load stereo for the mix; analysis (energy/BPM/key) runs on a mono downmix.
    audio, sr = loader.load_audio(file_path, mono=False)
    analysis = finder.analyze_track_for_mixing(_to_mono(audio), sr, num_segments)

    segments_with_audio = []
    for segment in analysis['segments']:
        segment_audio = finder.extract_segment_audio(audio, segment)
        segment_audio = _ensure_stereo(segment_audio)
        segment_audio = loader.normalize_audio(segment_audio, target_dB=-3.0)
        segments_with_audio.append((segment, segment_audio))

    return segments_with_audio


class ShorterMusicApp:
    def __init__(self, sample_rate: int = 44100, output_sample_rate: Optional[int] = None,
                 output_dir: str = "data/output", max_workers: Optional[int] = None):
        self.sample_rate = sample_rate
        self.output_sample_rate = output_sample_rate or sample_rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Number of parallel worker processes; None means one per CPU core.
        self.max_workers = max_workers

        self.audio_loader = AudioLoader(sample_rate=sample_rate)
        self.segment_finder = SegmentFinder(min_duration=7.0, max_duration=30.0)
        self.transition_manager = TransitionManager(sample_rate=sample_rate)
        self.playlist_downloader = PlaylistDownloader()

    def process_single_track(self, file_path: str, num_segments: int = 3) -> Dict:
        print(f"Processing track: {file_path}")

        audio, sr = self.audio_loader.load_audio(file_path, mono=False)
        analysis = self.segment_finder.analyze_track_for_mixing(_to_mono(audio), sr, num_segments)

        segments_with_audio = []
        for segment in analysis['segments']:
            segment_audio = self.segment_finder.extract_segment_audio(audio, segment)
            segment_audio = _ensure_stereo(segment_audio)
            segment_audio = self.audio_loader.normalize_audio(segment_audio, target_dB=-3.0)
            segments_with_audio.append((segment, segment_audio))

        return {
            'file_path': file_path,
            'analysis': analysis,
            'segments_with_audio': segments_with_audio
        }

    def _process_sequential(self, file_paths: List[str], num_segments: int) -> List[Dict]:
        all_segments = []
        for file_path in file_paths:
            try:
                result = self.process_single_track(file_path, num_segments)
                all_segments.extend(result['segments_with_audio'])
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        return all_segments

    def process_multiple_tracks(self, file_paths: List[str], num_segments: int = 2) -> List[Dict]:
        num_workers = self.max_workers or os.cpu_count() or 1
        num_workers = max(1, min(num_workers, len(file_paths)))

        if num_workers == 1:
            return self._process_sequential(file_paths, num_segments)

        # Track analysis is CPU-bound; run one process per track to use all cores.
        print(f"Processing in parallel on {num_workers} cores...")

        tasks = [
            (file_path, num_segments, self.sample_rate,
             self.segment_finder.min_duration, self.segment_finder.max_duration)
            for file_path in file_paths
        ]

        results_by_index: Dict[int, List] = {}
        total = len(file_paths)

        try:
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                future_to_index = {
                    executor.submit(_process_track_worker, task): idx
                    for idx, task in enumerate(tasks)
                }
                for completed, future in enumerate(as_completed(future_to_index), start=1):
                    idx = future_to_index[future]
                    try:
                        results_by_index[idx] = future.result()
                    except Exception as e:
                        print(f"Error processing {file_paths[idx]}: {e}")
                        results_by_index[idx] = []
                    print(f"  Processed {completed}/{total}: {Path(file_paths[idx]).name}")
        except Exception as e:
            print(f"Parallel processing failed ({e}), falling back to sequential...")
            return self._process_sequential(file_paths, num_segments)

        # Reassemble in the original track order.
        all_segments = []
        for idx in range(total):
            all_segments.extend(results_by_index.get(idx, []))
        return all_segments

    def create_mix_from_files(self, file_paths: List[str],
                             segments_per_track: int = 2,
                             output_filename: str = "mix.mp3") -> str:
        print("Creating mix from files...")

        all_segments = self.process_multiple_tracks(file_paths, segments_per_track)
        if not all_segments:
            raise ValueError("No segments found to create mix")

        print(f"Found {len(all_segments)} segments")

        mix = self.transition_manager.create_mix(all_segments)

        if self.output_sample_rate != self.sample_rate:
            mix = self.audio_loader.resample(mix, self.sample_rate, self.output_sample_rate)

        # Leave ~2 dB of headroom so lossy MP3 encoding overshoot does not clip.
        mix = self.audio_loader.normalize_audio(mix, target_dB=-2.0)

        output_path = self.output_dir / output_filename
        self.audio_loader.save_audio(mix, str(output_path), sr=self.output_sample_rate)

        print(f"Mix saved to: {output_path}")
        return str(output_path)

    def create_mix_from_playlist(self, playlist_url: str,
                                 max_songs: Optional[int] = None,
                                 segments_per_track: int = 2,
                                 output_filename: str = "playlist_mix.mp3") -> str:
        print("Downloading playlist...")

        downloaded_files = self.playlist_downloader.download_playlist(playlist_url, max_songs)
        if not downloaded_files:
            raise ValueError("No files downloaded from playlist")

        print(f"Downloaded {len(downloaded_files)} files")
        return self.create_mix_from_files(downloaded_files, segments_per_track, output_filename)

    def create_mix_from_youtube_urls(self, urls: List[str],
                                     segments_per_track: int = 2,
                                     output_filename: str = "youtube_mix.mp3") -> str:
        print("Downloading from YouTube URLs...")

        downloaded_files = self.playlist_downloader.download_multiple_urls(urls)
        if not downloaded_files:
            raise ValueError("No files downloaded")

        print(f"Downloaded {len(downloaded_files)} files")
        return self.create_mix_from_files(downloaded_files, segments_per_track, output_filename)

    def get_mix_info(self, mix_segments: List[Dict]) -> Dict:
        if not mix_segments:
            return {}

        total_duration = sum(s[0]['duration'] for s in mix_segments)
        avg_bpm = np.mean([s[0]['bpm'] for s in mix_segments])
        keys = [(s[0]['key'], s[0]['mode']) for s in mix_segments]

        transitions = []
        for i in range(len(mix_segments) - 1):
            transitions.append(
                self.transition_manager.get_transition_info(mix_segments[i][0], mix_segments[i + 1][0])
            )

        return {
            'num_segments': len(mix_segments),
            'total_duration': total_duration,
            'average_bpm': avg_bpm,
            'keys': keys,
            'transitions': transitions
        }


def main():
    app = ShorterMusicApp()

    print("ShorterMusic - Audio Mix Creator")
    print("=" * 40)
    print("Options:")
    print("1. Create mix from local files")
    print("2. Create mix from YouTube playlist")
    print("3. Create mix from YouTube URLs")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == '1':
        file_paths = [f.strip() for f in input("Enter file paths (comma-separated): ").split(',') if f.strip()]
        if file_paths:
            print(f"\nMix created: {app.create_mix_from_files(file_paths)}")

    elif choice == '2':
        playlist_url = input("Enter YouTube playlist URL: ").strip()
        max_songs = input("Max songs (optional, press Enter for all): ").strip()
        max_songs = int(max_songs) if max_songs else None
        if playlist_url:
            print(f"\nMix created: {app.create_mix_from_playlist(playlist_url, max_songs)}")

    elif choice == '3':
        urls = [u.strip() for u in input("Enter YouTube URLs (comma-separated): ").split(',') if u.strip()]
        if urls:
            print(f"\nMix created: {app.create_mix_from_youtube_urls(urls)}")

    elif choice == '4':
        print("Goodbye!")
        return

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
