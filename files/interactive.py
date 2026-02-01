#!/usr/bin/env python3
import sys
from pathlib import Path
import shutil
from typing import List

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
sys.path.insert(0, str(BASE_DIR))

from App.core.app import ShorterMusicApp
from App.utils.audio_loader import AudioLoader


def clear_screen():
    print("\033c", end="")


def print_header():
    print("=" * 60)
    print("       ShorterMusic - Interactive Mix Creator")
    print("=" * 60)
    print()


def get_choice(prompt: str, options: List[str], default: int = 0) -> int:
    while True:
        try:
            response = input(prompt).strip()
            if not response:
                return default
            
            choice = int(response)
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print(f"  Wprowadź liczbę od 1 do {len(options)}")
        except ValueError:
            print("  Wprowadź poprawną liczbę")


def get_number(prompt: str, default: float = None, min_val: float = None, max_val: float = None) -> float:
    while True:
        try:
            response = input(prompt).strip()
            if not response and default is not None:
                return default
            
            value = float(response)
            
            if min_val is not None and value < min_val:
                print(f"  Wartość musi być >= {min_val}")
                continue
            
            if max_val is not None and value > max_val:
                print(f"  Wartość musi być <= {max_val}")
                continue
            
            return value
        except ValueError:
            print("  Wprowadź poprawną liczbę")


def get_yes_no(prompt: str, default: bool = False) -> bool:
    while True:
        response = input(prompt).strip().lower()
        if not response:
            return default
        
        if response in ['t', 'tak', 'y', 'yes']:
            return True
        elif response in ['n', 'nie', 'no']:
            return False
        else:
            print("  Wprowadź 'tak' lub 'nie' (t/n)")


def get_playlist_url() -> str:
    while True:
        url = input("  Podaj URL playlisty YouTube: ").strip()
        if url and ('youtube.com' in url or 'youtu.be' in url):
            return url
        else:
            print("  Podaj poprawny URL YouTube")


def get_local_files() -> List[str]:
    download_dir = Path("data/downloads")
    
    if not download_dir.exists():
        print(f"  Folder {download_dir} nie istnieje!")
        return []
    
    audio_files = list(download_dir.glob("*.mp3"))
    audio_files.extend(download_dir.glob("*.wav"))
    audio_files.extend(download_dir.glob("*.flac"))
    
    if not audio_files:
        print("  Brak plików audio w folderze downloads!")
        return []
    
    audio_files.sort()
    
    print(f"\n  Znaleziono {len(audio_files)} plików audio:")
    for i, file in enumerate(audio_files, 1):
        print(f"    {i}. {file.name}")
    
    use_all = get_yes_no("\n  Użyć wszystkich plików? (t/n): ", default=True)
    
    if use_all:
        return [str(f) for f in audio_files]
    else:
        print("\n  Wybierz numery plików (oddzielone przecinkami):")
        indices = input("  > ").strip()
        
        try:
            selected_indices = [int(x.strip()) - 1 for x in indices.split(',')]
            selected_files = []
            
            for idx in selected_indices:
                if 0 <= idx < len(audio_files):
                    selected_files.append(str(audio_files[idx]))
                else:
                    print(f"  Pominięto nieprawidłowy numer: {idx + 1}")
            
            return selected_files
        except ValueError:
            print("  Błąd formatu, używam wszystkich plików")
            return [str(f) for f in audio_files]


def show_progress_bar(current: int, total: int, prefix: str = "", width: int = 40):
    if total == 0:
        percent = 100
    else:
        percent = (current / total) * 100
    
    filled = int(width * current / total) if total > 0 else width
    bar = '█' * filled + '░' * (width - filled)
    
    print(f"\r  {prefix} [{bar}] {percent:.1f}%", end='', flush=True)


def main():
    clear_screen()
    print_header()
    
    app = ShorterMusicApp()
    
    # Wybór źródła
    print("Wybierz źródło utworów:")
    print("  1. Pobierz playlistę z YouTube")
    print("  2. Użyj plików z folderu downloads")
    
    source_choice = get_choice("  Wybierz (1-2): ", ["YouTube", "Lokalne"], default=0)
    
    files_to_process = []
    
    if source_choice == 0:  # YouTube
        print("\nPobieranie z YouTube:")
        playlist_url = get_playlist_url()
        max_songs = get_number("  Ile utworów pobrać? (0 = wszystkie): ", default=5, min_val=0)
        
        if max_songs == 0:
            max_songs = None
        
        print("\n  Pobieranie playlisty...")
        downloader = app.playlist_downloader
        
        info = downloader.get_playlist_info(playlist_url)
        total_videos = info.get('num_videos', 0)
        
        if max_songs:
            total_videos = min(total_videos, max_songs)
        
        print(f"  Znaleziono {total_videos} utworów do pobrania")
        
        files_to_process = downloader.download_playlist(
            playlist_url,
            max_songs=max_songs,
            show_progress=True
        )
        
        print(f"\n  Pobrano {len(files_to_process)} plików")
    
    else:  # Lokalne pliki
        print("\n  Używanie plików lokalnych:")
        files_to_process = get_local_files()
    
    if not files_to_process:
        print("\n  Brak plików do przetworzenia!")
        return
    
    # Konfiguracja segmentów
    print("\nKonfiguracja segmentów:")
    segments_per_track = int(get_number("  Liczba segmentów na utwór: ", default=1, min_val=1, max_val=5))
    
    print("\n  Zakres długości fragmentów (w sekundach):")
    min_duration = get_number(f"    Minimalna długość: ", default=7.0, min_val=3.0, max_val=30.0)
    max_duration = get_number(f"    Maksymalna długość: ", default=15.0, min_val=min_duration, max_val=60.0)
    
    # Aktualizacja konfiguracji
    app.segment_finder.min_duration = min_duration
    app.segment_finder.max_duration = max_duration
    
    # Nazwa pliku wyjściowego
    output_filename = input("\n  Nazwa pliku wyjściowego (bez rozszerzenia): ").strip()
    if not output_filename:
        output_filename = "mix"
    
    if not output_filename.endswith('.mp3'):
        output_filename += '.mp3'
    
    # Tworzenie miksu
    print(f"\n  Tworzenie miksu z {len(files_to_process)} plików...")
    print(f"  {segments_per_track} segmentów na utwór")
    print(f"  Długość: {min_duration}s - {max_duration}s")
    print()
    
    try:
        output_path = app.create_mix_from_files(
            files_to_process,
            segments_per_track=segments_per_track,
            output_filename=output_filename
        )
        
        print(f"\n  ✓ Miks utworzony: {output_path}")
        
        # Pytanie o usunięcie plików
        if source_choice == 0:  # Tylko jeśli pobrano z YouTube
            print()
            delete_files = get_yes_no("  Usunąć pobrane pliki z folderu downloads? (t/n): ", default=False)
            
            if delete_files:
                download_dir = Path("data/downloads")
                deleted_count = 0
                
                for file in files_to_process:
                    try:
                        Path(file).unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"  Błąd usuwania {file}: {e}")
                
                print(f"  ✓ Usunięto {deleted_count} plików")
        
        print("\n" + "=" * 60)
        print("  Zakończono!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n  ✗ Błąd podczas tworzenia miksu: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Przerwano przez użytkownika")
    except Exception as e:
        print(f"\n  Wystąpił nieoczekiwany błąd: {e}")
        import traceback
        traceback.print_exc()
