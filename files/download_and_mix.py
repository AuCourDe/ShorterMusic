import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from App.core.app import ShorterMusicApp


def main():
    playlist_url = "https://youtube.com/playlist?list=PLrLiN32l7EHyQumwiQ_ZI-aFGsKrkxU6a&si=qywe23hAH7z8Ip_l"
    
    print("ShorterMusic - Playlist Processor")
    print("=" * 50)
    print(f"Playlist URL: {playlist_url}")
    print()
    
    app = ShorterMusicApp()
    
    try:
        output = app.create_mix_from_playlist(
            playlist_url=playlist_url,
            max_songs=5,
            segments_per_track=1,
            output_filename="youtube_playlist_mix.mp3"
        )
        
        print("\n" + "=" * 50)
        print("SUCCESS!")
        print(f"Mix created: {output}")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
