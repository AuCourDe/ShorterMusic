# ShorterMusic

Automatyczne narzędzie do tworzenia miksów muzycznych z fragmentów wielu piosenek.

## Funkcjonalności

- **Analiza audio**: Wykrywanie najciekawszych fragmentów (7-30 sekund) na podstawie energii, BPM i tonacji
- **Inteligentne miksowanie**: Automatyczne dobieranie kolejności fragmentów dla płynnych przejść
- **Pobieranie z YouTube**: Obsługa playlist i pojedynczych utworów
- **Płynne przejścia**: Crossfade z różnymi krzywymi (linear, equal-power, exponential, S-curve)

## Instalacja

```bash
pip install -r requirements.txt
```

**Wymagania**: FFmpeg musi być zainstalowany w systemie.

## Szybki start

### Z plików lokalnych

```python
from App.core.app import ShorterMusicApp

app = ShorterMusicApp()

output = app.create_mix_from_files(
    file_paths=["song1.mp3", "song2.mp3", "song3.mp3"],
    segments_per_track=2,
    output_filename="my_mix.mp3"
)
```

### Z playlisty YouTube

```python
app = ShorterMusicApp()

output = app.create_mix_from_playlist(
    playlist_url="https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
    max_songs=5,
    segments_per_track=2,
    output_filename="playlist_mix.mp3"
)
```

### Z linków YouTube

```python
app = ShorterMusicApp()

output = app.create_mix_from_youtube_urls(
    urls=[
        "https://www.youtube.com/watch?v=VIDEO_ID_1",
        "https://www.youtube.com/watch?v=VIDEO_ID_2"
    ],
    segments_per_track=2,
    output_filename="youtube_mix.mp3"
)
```

## Interfejs CLI

```bash
python App/core/app.py
```

## Przykłady

Zobacz `example.py` dla więcej przykładów użycia.

## Struktura projektu

```
ShorterMusic/
├── App/
│   ├── audio_analysis/    # Analiza audio
│   ├── mixing/            # Miksowanie i przejścia
│   ├── youtube/           # Pobieranie z YouTube
│   ├── core/              # Główna logika aplikacji
│   └── utils/             # Narzędzia
├── data/
│   ├── downloads/         # Pobrane pliki
│   └── output/            # Wygenerowane miksy
├── PLAN.md                # Plan projektu
├── TODO.md                # Lista zadań
└── requirements.txt       # Zależności
```

## Algorytmy

### Wykrywanie fragmentów
- Analiza RMS energy
- Spectral flux detection
- Onset strength analysis
- Wykrywanie BPM i tonacji
- Ocena "interesującości" fragmentów

### Kolejność fragmentów
- Graf kompatybilności na podstawie:
  - Odległości tonalnej (key distance)
  - Różnicy BPM
  - Poziomu energii
- Rozwiązywanie TSP (greedy algorithm)

### Przejścia
- Crossfade (2-3 sekundy)
- Dopasowanie krzywej przejścia do kompatybilności
- Fade in/out na początku i końcu

## Licencja

MIT
