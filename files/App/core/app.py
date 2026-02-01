import sys
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from utils.audio_loader import AudioLoader
from audio_analysis.segment_finder import SegmentFinder
from mixing.transition_manager import TransitionManager
from youtube.playlist_downloader import PlaylistDownloader


class ShorterMusicApp:
    def __init__(self, sample_rate: int = 44100, output_sample_rate: Optional[int] = None,
                 output_dir: str = "data/output"):
        self.sample_rate = sample_rate
        self.output_sample_rate = output_sample_rate or sample_rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.audio_loader = AudioLoader(sample_rate=sample_rate)
        self.segment_finder = SegmentFinder(min_duration=7.0, max_duration=30.0)
        self.transition_manager = TransitionManager(sample_rate=sample_rate)
        self.playlist_downloader = PlaylistDownloader()

    def process_single_track(self, file_path: str, num_segments: int = 3) -> Dict:
        print(f"Processing track: {file_path}")
        
        audio, sr = self.audio_loader.load_audio(file_path)
        
        analysis = self.segment_finder.analyze_track_for_mixing(audio, sr, num_segments)
        
        segments = analysis['segments']
        
        segments_with_audio = []
        for segment in segments:
            segment_audio = self.segment_finder.extract_segment_audio(audio, segment)
            segment_audio = self.audio_loader.normalize_audio(segment_audio, target_dB=-3.0)
            segments_with_audio.append((segment, segment_audio))
        
        return {
            'file_path': file_path,
            'analysis': analysis,
            'segments_with_audio': segments_with_audio
        }

    def process_multiple_tracks(self, file_paths: List[str], num_segments: int = 2) -> List[Dict]:
        all_segments = []
        
        for file_path in file_paths:
            try:
                result = self.process_single_track(file_path, num_segments)
                all_segments.extend(result['segments_with_audio'])
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
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
        
        mix = self.audio_loader.apply_gain(mix, gain_db=3.0)
        
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
        
        output_path = self.create_mix_from_files(downloaded_files, segments_per_track, output_filename)
        
        return output_path

    def create_mix_from_youtube_urls(self, urls: List[str],
                                     segments_per_track: int = 2,
                                     output_filename: str = "youtube_mix.mp3") -> str:
        print("Downloading from YouTube URLs...")
        
        downloaded_files = self.playlist_downloader.download_multiple_urls(urls)
        
        if not downloaded_files:
            raise ValueError("No files downloaded")
        
        print(f"Downloaded {len(downloaded_files)} files")
        
        output_path = self.create_mix_from_files(downloaded_files, segments_per_track, output_filename)
        
        return output_path

    def get_mix_info(self, mix_segments: List[Dict]) -> Dict:
        if not mix_segments:
            return {}
        
        total_duration = sum(s[0]['duration'] for s in mix_segments)
        avg_bpm = np.mean([s[0]['bpm'] for s in mix_segments])
        
        keys = [(s[0]['key'], s[0]['mode']) for s in mix_segments]
        
        transitions = []
        for i in range(len(mix_segments) - 1):
            trans_info = self.transition_manager.get_transition_info(mix_segments[i][0], mix_segments[i+1][0])
            transitions.append(trans_info)
        
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
        file_paths = input("Enter file paths (comma-separated): ").strip().split(',')
        file_paths = [f.strip() for f in file_paths if f.strip()]
        
        if file_paths:
            output = app.create_mix_from_files(file_paths)
            print(f"\nMix created: {output}")
    
    elif choice == '2':
        playlist_url = input("Enter YouTube playlist URL: ").strip()
        max_songs = input("Max songs (optional, press Enter for all): ").strip()
        
        max_songs = int(max_songs) if max_songs else None
        
        if playlist_url:
            output = app.create_mix_from_playlist(playlist_url, max_songs)
            print(f"\nMix created: {output}")
    
    elif choice == '3':
        urls = input("Enter YouTube URLs (comma-separated): ").strip().split(',')
        urls = [u.strip() for u in urls if u.strip()]
        
        if urls:
            output = app.create_mix_from_youtube_urls(urls)
            print(f"\nMix created: {output}")
    
    elif choice == '4':
        print("Goodbye!")
        return
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
