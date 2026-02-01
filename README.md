# ShorterMusic

Automatyczny kreator miksow muzycznych z fragmentow wielu utworow.

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

## Uklad menu

```
============================================================
       ShorterMusic - Interactive Mix Creator
============================================================

Wybierz zrodlo utworow (Choose source):
  [1] Pobierz playliste z YouTube
  [2] Uzyj plikow z folderu downloads

-----------------------------------------------------------
Po wyborze zrodla:
-----------------------------------------------------------

Konfiguracja segmentow:
  - Liczba segmentow na utwor: 1-5 (domyslnie: 1)
  - Minimalna dlugosc segmentu: 3-30s (domyslnie: 7s)
  - Maksymalna dlugosc segmentu: min-60s (domyslnie: 15s)
  - Nazwa pliku wyjsciowego (domyslnie: mix.mp3)

-----------------------------------------------------------
Po zakonczeniu:
-----------------------------------------------------------
  - Pytanie: Usunac pobrane pliki? (t/n)
  - Wyswietlenie sciezki do wygenerowanego miksu
```

---

## Dostepne opcje

### Opcja 1: Pobieranie z YouTube

1. Wprowadz URL playlisty YouTube
2. Podaj liczbe utworow do pobrania (0 = wszystkie)
3. Poczekaj na zakonczenie pobierania
4. Pliki zapisane w `data/downloads/`

### Opcja 2: Pliki lokalne

1. Umiesc pliki audio (MP3, WAV, FLAC) w `data/downloads/`
2. Wybierz opcje 2 z menu
3. Uzyj wszystkich plikow lub wybierz konkretne (numery oddzielone przecinkami)

---

## Parametry konfiguracyjne

| Parametr | Zakres | Domyslnie | Opis |
|----------|--------|-----------|------|
| Segmenty na utwor | 1-5 | 1 | Ile fragmentow wyciagnac z kazdego utworu |
| Min. dlugosc | 3-30s | 7s | Minimalna dlugosc segmentu |
| Max. dlugosc | min-60s | 15s | Maksymalna dlugosc segmentu |
| Nazwa pliku | dowolna | mix.mp3 | Nazwa pliku wyjsciowego |

---

## Struktura folderow

```
ShorterMusic/
├── windows.bat          # Launcher Windows
├── linux-mac.sh         # Launcher Linux/macOS
├── instrukcja.html      # Pelna dokumentacja HTML
├── README.md            # Ten plik
└── files/
    ├── interactive.py   # Glowny interfejs
    ├── run.bat          # Skrypt Windows
    ├── run.sh           # Skrypt Unix
    ├── requirements.txt # Zaleznosci Python
    ├── App/             # Kod aplikacji
    │   ├── core/        # Glowna logika
    │   ├── audio_analysis/  # Analiza audio
    │   ├── mixing/      # Miksowanie
    │   ├── youtube/     # Pobieranie YouTube
    │   └── utils/       # Narzedzia
    └── data/
        ├── downloads/   # Pliki zrodlowe
        ├── output/      # Gotowe miksy
        └── processed/   # Cache analizy
```

---

## Obslugiwane formaty

**Wejscie:** MP3, WAV, FLAC, OGG, M4A, WMA

**Wyjscie:** MP3 (192 kbps), WAV, FLAC, OGG

---

## Uzycie programistyczne

```python
from App.core.app import ShorterMusicApp

app = ShorterMusicApp()

# Z plikow lokalnych
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

## Rozwiazywanie problemow

| Problem | Rozwiazanie |
|---------|-------------|
| FFmpeg nie znaleziony | Zainstaluj FFmpeg lub umiesc w `bin/ffmpeg/` |
| Blad yt-dlp | Zaktualizuj: `pip install -U yt-dlp` |
| Brak plikow | Sprawdz czy pliki sa w `data/downloads/` |

---

## Dokumentacja

Pelna dokumentacja z GUI: [instrukcja.html](instrukcja.html)
