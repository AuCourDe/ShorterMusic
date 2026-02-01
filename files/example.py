import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from App.core.app import ShorterMusicApp


def example_local_files():
    app = ShorterMusicApp()
    
    file_paths = [
        "path/to/song1.mp3",
        "path/to/song2.mp3",
        "path/to/song3.mp3"
    ]
    
    output = app.create_mix_from_files(
        file_paths=file_paths,
        segments_per_track=2,
        output_filename="my_mix.mp3"
    )
    
    print(f"Mix created: {output}")


def example_youtube_playlist():
    app = ShorterMusicApp()
    
    playlist_url = "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
    
    output = app.create_mix_from_playlist(
        playlist_url=playlist_url,
        max_songs=5,
        segments_per_track=2,
        output_filename="playlist_mix.mp3"
    )
    
    print(f"Mix created: {output}")


def example_youtube_urls():
    app = ShorterMusicApp()
    
    urls = [
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2",
        "https://www.youtube.com/watch?v=VIDEO_ID_3"
    ]
    
    output = app.create_mix_from_youtube_urls(
        urls=urls,
        segments_per_track=2,
        output_filename="youtube_mix.mp3"
    )
    
    print(f"Mix created: {output}")


def example_analyze_track():
    app = ShorterMusicApp()
    
    file_path = "path/to/song.mp3"
    
    result = app.process_single_track(file_path, num_segments=3)
    
    print(f"Track: {result['file_path']}")
    print(f"Found {len(result['segments_with_audio'])} segments:")
    
    for i, (segment, audio) in enumerate(result['segments_with_audio']):
        print(f"  Segment {i+1}:")
        print(f"    Time: {segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
        print(f"    Duration: {segment['duration']:.2f}s")
        print(f"    Key: {segment['key']} {segment['mode']}")
        print(f"    BPM: {segment['bpm']:.1f}")
        print(f"    Interest Score: {segment['interest_score']:.3f}")


if __name__ == "__main__":
    print("ShorterMusic Examples")
    print("=" * 40)
    print("1. Create mix from local files")
    print("2. Create mix from YouTube playlist")
    print("3. Create mix from YouTube URLs")
    print("4. Analyze a single track")
    
    choice = input("\nSelect example (1-4): ").strip()
    
    if choice == '1':
        example_local_files()
    elif choice == '2':
        example_youtube_playlist()
    elif choice == '3':
        example_youtube_urls()
    elif choice == '4':
        example_analyze_track()
    else:
        print("Invalid choice")
