# ShorterMusic

Kreator miksów muzycznych z fragmentów wielu utworów.

## Szybki start

### Wymagania

- Python 3.8+ (zalecany 3.11+)
- FFmpeg (do eksportu MP3)
- yt-dlp (do pobierania z YouTube)

### Uruchomienie

**Windows:**
```batch
windows.bat
```

**Linux/macOS:**
```bash
./linux-mac.sh
```

**Alternatywnie:**
```bash
cd files
python interactive.py
```

---

## Układ menu

```
============================================================
       ShorterMusic - Interactive Mix Creator
============================================================

Wybierz źródło utworów (Choose source):
  [1] Pobierz playlistę z YouTube
  [2] Użyj plików z folderu downloads

-----------------------------------------------------------
Po wyborze źródła:
-----------------------------------------------------------

Konfiguracja segmentów:
  - Liczba segmentów na utwór: 1-5 (domyślnie: 1)
  - Minimalna długość segmentu: 3-30s (domyślnie: 7s)
  - Maksymalna długość segmentu: min-60s (domyślnie: 15s)
  - Nazwa pliku wyjściowego (domyślnie: mix.mp3)

-----------------------------------------------------------
Po zakończeniu:
-----------------------------------------------------------
  - Pytanie: Usunąć pobrane pliki? (t/n)
  - Wyświetlenie ścieżki do wygenerowanego miksu
```

---

## Dostępne opcje

### Opcja 1: Pobieranie z YouTube

1. Wprowadź URL playlisty YouTube
2. Podaj liczbę utworów do pobrania (0 = wszystkie)
3. Poczekaj na zakończenie pobierania
4. Pliki zapisane w `data/downloads/`

### Opcja 2: Pliki lokalne

1. Umieść pliki audio (MP3, WAV, FLAC) w `data/downloads/`
2. Wybierz opcję 2 z menu
3. Użyj wszystkich plików lub wybierz konkretne (numery oddzielone przecinkami)

---

## Parametry konfiguracyjne

| Parametr | Zakres | Domyślnie | Opis |
|----------|--------|-----------|------|
| Segmenty na utwór | 1-5 | 1 | Ile fragmentów wyciągnąć z każdego utworu |
| Min. długość | 3-30s | 7s | Minimalna długość segmentu |
| Max. długość | min-60s | 15s | Maksymalna długość segmentu |
| Nazwa pliku | dowolna | mix.mp3 | Nazwa pliku wyjściowego |

---

## Struktura folderów

```
ShorterMusic/
├── windows.bat          # Launcher Windows
├── linux-mac.sh         # Launcher Linux/macOS
├── instrukcja.html      # Pełna dokumentacja HTML
├── README.md            # Ten plik
└── files/
    ├── interactive.py   # Główny interfejs
    ├── requirements.txt # Zależności Python
    ├── App/             # Kod aplikacji
    │   ├── core/        # Główna logika
    │   ├── audio_analysis/  # Analiza audio
    │   ├── mixing/      # Miksowanie
    │   ├── youtube/     # Pobieranie YouTube
    │   └── utils/       # Narzędzia
    └── data/
        ├── downloads/   # Pliki źródłowe
        ├── output/      # Gotowe miksy
        └── processed/   # Cache analizy
```

---

## Obsługiwane formaty

**Wejście:** MP3, WAV, FLAC, OGG, M4A, WMA

**Wyjście:** MP3 (192 kbps), WAV, FLAC, OGG

---

## Użycie kodu

```python
from App.core.app import ShorterMusicApp

app = ShorterMusicApp()

# Z plików lokalnych
output = app.create_mix_from_files(
    file_paths=["song1.mp3", "song2.mp3"],
    segments_per_track=2,
    output_filename="my_mix.mp3"
)

# Z playlisty YouTube
output = app.create_mix_from_playlist(
    playlist_url="https://www.youtube.com/playlist?list=...",
    max_songs=5,
    output_filename="playlist_mix.mp3"
)
```

---

## Rozwiązywanie problemów

| Problem | Rozwiązanie |
|---------|-------------|
| FFmpeg nie znaleziony | Zainstaluj FFmpeg lub umieść w `bin/ffmpeg/` |
| Błąd yt-dlp | Zaktualizuj: `pip install -U yt-dlp` |
| Brak plików | Sprawdź czy pliki są w `data/downloads/` |

---

## Dokumentacja

Pełna dokumentacja z GUI: [instrukcja.html](instrukcja.html)
