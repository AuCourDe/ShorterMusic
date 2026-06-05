#!/usr/bin/env python3
import sys
from pathlib import Path
from typing import List

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
sys.path.insert(0, str(BASE_DIR))

from App.core.app import ShorterMusicApp


def clear_screen():
    print("\033c", end="")


def print_header():
    print("=" * 60)
    print("       ShorterMusic - Interactive Mix Creator")
    print("=" * 60)
    print()


def get_choice(prompt: str, options: List[str], default: int = 0) -> int:
    while True:
        response = input(prompt).strip()
        if not response:
            return default
        try:
            choice = int(response)
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"  Enter a number between 1 and {len(options)}")
        except ValueError:
            print("  Enter a valid number")


def get_number(prompt: str, default: float = None, min_val: float = None, max_val: float = None) -> float:
    while True:
        response = input(prompt).strip()
        if not response and default is not None:
            return default
        try:
            value = float(response)
            if min_val is not None and value < min_val:
                print(f"  Value must be >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"  Value must be <= {max_val}")
                continue
            return value
        except ValueError:
            print("  Enter a valid number")


def get_yes_no(prompt: str, default: bool = False) -> bool:
    while True:
        response = input(prompt).strip().lower()
        if not response:
            return default
        if response in ('y', 'yes'):
            return True
        if response in ('n', 'no'):
            return False
        print("  Enter 'yes' or 'no' (y/n)")


def get_playlist_url() -> str:
    while True:
        url = input("  Enter YouTube playlist URL: ").strip()
        if url and ('youtube.com' in url or 'youtu.be' in url):
            return url
        print("  Enter a valid YouTube URL")


def get_local_files() -> List[str]:
    download_dir = Path("data/downloads")
    if not download_dir.exists():
        print(f"  Folder {download_dir} does not exist!")
        return []

    audio_files = list(download_dir.glob("*.mp3"))
    audio_files.extend(download_dir.glob("*.wav"))
    audio_files.extend(download_dir.glob("*.flac"))

    if not audio_files:
        print("  No audio files in the downloads folder!")
        return []

    audio_files.sort()

    print(f"\n  Found {len(audio_files)} audio files:")
    for i, file in enumerate(audio_files, 1):
        print(f"    {i}. {file.name}")

    if get_yes_no("\n  Use all files? (y/n): ", default=True):
        return [str(f) for f in audio_files]

    print("\n  Enter file numbers (comma-separated):")
    indices = input("  > ").strip()
    try:
        selected_indices = [int(x.strip()) - 1 for x in indices.split(',')]
        selected_files = []
        for idx in selected_indices:
            if 0 <= idx < len(audio_files):
                selected_files.append(str(audio_files[idx]))
            else:
                print(f"  Skipped invalid number: {idx + 1}")
        return selected_files
    except ValueError:
        print("  Invalid format, using all files")
        return [str(f) for f in audio_files]


def select_files(app: ShorterMusicApp) -> List[str]:
    print("Choose a track source:")
    print("  1. Download a YouTube playlist")
    print("  2. Use files from the downloads folder")

    source = get_choice("  Choose (1-2): ", ["YouTube", "Local"], default=0)

    if source == 1:
        print("\n  Using local files:")
        return get_local_files()

    print("\nDownloading from YouTube:")
    playlist_url = get_playlist_url()
    downloader = app.playlist_downloader

    print("\n  Checking playlist...")
    info = downloader.get_playlist_info(playlist_url)
    num_videos = info.get('num_videos', 0)

    if num_videos == 0:
        print("  No tracks found in the playlist (check the URL).")
        return []

    print(f"  The playlist contains {num_videos} tracks.")
    max_songs = get_number(
        f"  How many tracks to download? (Enter = all {num_videos}): ",
        default=0, min_val=0, max_val=num_videos
    )
    max_songs = int(max_songs) or None

    files = downloader.download_playlist(playlist_url, max_songs=max_songs, show_progress=True)
    print(f"\n  Downloaded {len(files)} files")
    return files


def main():
    clear_screen()
    print_header()

    app = ShorterMusicApp()

    files_to_process = select_files(app)
    if not files_to_process:
        print("\n  No files to process!")
        return

    print("\nSegment configuration:")
    segments_per_track = int(get_number("  Segments per track: ", default=1, min_val=1, max_val=5))

    print("\n  Fragment length range (in seconds):")
    min_duration = get_number("    Minimum length: ", default=7.0, min_val=3.0, max_val=30.0)
    max_duration = get_number("    Maximum length: ", default=15.0, min_val=min_duration, max_val=60.0)

    app.segment_finder.min_duration = min_duration
    app.segment_finder.max_duration = max_duration

    output_filename = input("\n  Output file name (without extension): ").strip() or "mix"
    if not output_filename.endswith('.mp3'):
        output_filename += '.mp3'

    print(f"\n  Creating a mix from {len(files_to_process)} files...")
    print(f"  {segments_per_track} segments per track")
    print(f"  Length: {min_duration}s - {max_duration}s\n")

    try:
        output_path = app.create_mix_from_files(
            files_to_process,
            segments_per_track=segments_per_track,
            output_filename=output_filename
        )
        print(f"\n  Mix created: {output_path}")
        print("\n" + "=" * 60)
        print("  Done!")
        print("=" * 60)
    except Exception as e:
        print(f"\n  Error while creating the mix: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrupted by the user")
    except Exception as e:
        print(f"\n  Unexpected error: {e}")
        import traceback
        traceback.print_exc()
