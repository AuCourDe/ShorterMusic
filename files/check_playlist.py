import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from App.youtube.playlist_downloader import PlaylistDownloader


def main():
    playlist_url = "https://youtube.com/playlist?list=PLrLiN32l7EHyQumwiQ_ZI-aFGsKrkxU6a&si=qywe23hAH7z8Ip_l"
    
    downloader = PlaylistDownloader()
    
    print("Getting playlist info...")
    info = downloader.get_playlist_info(playlist_url)
    
    print(f"Playlist: {info['title']}")
    print(f"Uploader: {info['uploader']}")
    print(f"Total videos: {info['num_videos']}")
    print(f"\nFirst 10 videos:")
    
    for i, entry in enumerate(info['entries'][:10]):
        print(f"{i+1}. {entry['title']}")


if __name__ == "__main__":
    main()
