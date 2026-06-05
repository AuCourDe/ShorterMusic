import os
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm


class PlaylistDownloader:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("data/downloads")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.yt_dlp_path = self._find_yt_dlp()

    def _find_yt_dlp(self) -> str:
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[3]))
        bundled_yt_dlp = base_dir / "bin" / "yt-dlp" / "yt-dlp.exe"
        if bundled_yt_dlp.exists():
            return str(bundled_yt_dlp)

        if sys.prefix != sys.base_prefix:
            venv_yt_dlp = Path(sys.prefix) / "bin" / "yt-dlp"
            if venv_yt_dlp.exists():
                return str(venv_yt_dlp)

        for path in os.environ.get("PATH", "").split(os.pathsep):
            yt_dlp = Path(path) / "yt-dlp"
            if yt_dlp.exists():
                return str(yt_dlp)

        return "yt-dlp"

    def download_audio(self, url: str, output_filename: Optional[str] = None) -> str:
        if output_filename:
            output_path = str(self.output_dir / f'{output_filename}.mp3')
        else:
            output_path = str(self.output_dir / '%(title)s.%(ext)s')
        
        cmd = [
            self.yt_dlp_path,
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "192",
            "-o", output_path,
            url
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if output_filename:
                return str(self.output_dir / f'{output_filename}.mp3')
            else:
                files = list(self.output_dir.glob("*.mp3"))
                return str(files[-1]) if files else ""
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to download {url}: {e.stderr}")

    def download_playlist(self, playlist_url: str, max_songs: Optional[int] = None, show_progress: bool = False) -> List[str]:
        info = self.get_playlist_info(playlist_url)
        
        if 'entries' not in info or not info['entries']:
            return [self.download_audio(playlist_url)]
        
        entries = info['entries']
        if max_songs:
            entries = entries[:max_songs]
        
        downloaded_files = []
        
        if show_progress:
            print(f"\n  Downloading {len(entries)} tracks...")
            for i, entry in enumerate(entries, 1):
                percent = (i - 1) / len(entries) * 100
                bar_length = 30
                filled = int(bar_length * (i - 1) / len(entries))
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {percent:.1f}% ({i}/{len(entries)})", end='', flush=True)
                
                try:
                    video_url = entry['url']
                    title = entry['title'].replace('/', '-').replace('\\', '-')
                    safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    output_filename = f"{len(downloaded_files)+1:02d} - {safe_title}"
                    filename = self.download_audio(video_url, output_filename)
                    
                    if filename and os.path.exists(filename):
                        downloaded_files.append(filename)
                        print(f"\r  [{bar}] {percent:.1f}% ({i}/{len(entries)}) ✓", end='', flush=True)
                    else:
                        print(f"\r  [{bar}] {percent:.1f}% ({i}/{len(entries)}) ✗", end='', flush=True)
                except Exception as e:
                    print(f"\r  [{bar}] {percent:.1f}% ({i}/{len(entries)}) ✗", end='', flush=True)
                    continue
            
            print(f"\r  [{'█' * 30}] 100.0% ({len(entries)}/{len(entries)})")
        else:
            for entry in tqdm(entries, desc="Downloading playlist"):
                try:
                    video_url = entry['url']
                    title = entry['title'].replace('/', '-').replace('\\', '-')
                    safe_title = ''.join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    output_filename = f"{len(downloaded_files)+1:02d} - {safe_title}"
                    filename = self.download_audio(video_url, output_filename)
                    
                    if filename and os.path.exists(filename):
                        downloaded_files.append(filename)
                        print(f"  ✓ Downloaded: {safe_title}")
                    else:
                        print(f"  ✗ Failed: {safe_title}")
                except Exception as e:
                    print(f"  ✗ Skipping {entry.get('title', 'unknown')}: {str(e)[:100]}")
                    continue
        
        return downloaded_files

    def get_playlist_info(self, playlist_url: str) -> Dict:
        cmd = [
            self.yt_dlp_path,
            "--flat-playlist",
            "--dump-json",
            playlist_url
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            entries = []
            for line in lines:
                if line.strip():
                    import json
                    try:
                        data = json.loads(line)
                        entries.append({
                            'title': data.get('title', 'Unknown'),
                            'url': data.get('url', data.get('webpage_url', '')),
                            'duration': data.get('duration', 0)
                        })
                    except json.JSONDecodeError:
                        continue
            
            return {
                'title': 'YouTube Playlist',
                'uploader': 'Unknown',
                'num_videos': len(entries),
                'entries': entries
            }
        except subprocess.CalledProcessError as e:
            return {
                'title': 'Unknown Playlist',
                'uploader': 'Unknown',
                'num_videos': 0,
                'entries': []
            }

    def download_multiple_urls(self, urls: List[str]) -> List[str]:
        downloaded_files = []
        
        for i, url in enumerate(tqdm(urls, desc="Downloading multiple URLs")):
            try:
                output_filename = f"track_{i+1:03d}"
                filename = self.download_audio(url, output_filename)
                if filename and os.path.exists(filename):
                    downloaded_files.append(filename)
            except Exception as e:
                print(f"Error downloading {url}: {e}")
                continue
        
        return downloaded_files

    def cleanup_downloaded_files(self, filenames: List[str]) -> None:
        for filename in filenames:
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception as e:
                print(f"Error removing {filename}: {e}")

    def get_downloaded_files(self) -> List[str]:
        audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
        files = []
        
        for ext in audio_extensions:
            files.extend(self.output_dir.glob(f'*{ext}'))
        
        return [str(f) for f in files]
