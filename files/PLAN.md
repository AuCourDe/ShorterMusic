# ShorterMusic - Plan Projektu

## Cel Aplikacji
Stworzenie aplikacji do automatycznego tworzenia miksów muzycznych z fragmentów wielu piosenek.

## Funkcjonalności Główne

### 1. Analiza Piosenek
- **Algorytm wykrywania najciekawszych fragmentów** (7-30 sekund)
  - Analiza energii audio (RMS, spectral flux)
  - Wykrywanie chorus/refrain
  - Analiza zmian dynamiki
  - Wykrywanie charakterystycznych elementów (wokal, drop, hook)

### 2. Wybór i Kolejność Fragmentów
- **Algorytm doboru kolejności**
  - Analiza zgodności tonalnej (key detection)
  - Dopasowanie BPM (tempo matching)
  - Analiza kompatybilności muzycznej
  - Automatyczne przejścia (crossfade, beatmatching)

### 3. Miksowanie
- **Płynne przejścia między fragmentami**
  - Crossfade z różnymi krzywymi
  - Beatmatching i tempo alignment
  - Equalizer dla płynnych przejść
  - Opcjonalny morphing audio

### 4. Pobieranie z YouTube
- **Obsługa playlist**
  - Pobieranie całej playlisty z URL
  - Pobieranie pojedynczych utworów
  - Konwersja do formatu audio (MP3/WAV)

## Architektura

### Folder Structure
```
App/
├── audio_analysis/          # Analiza audio
│   ├── energy_detector.py
│   ├── key_detector.py
│   ├── bpm_detector.py
│   └── segment_finder.py
├── mixing/                  # Miksowanie
│   ├── crossfade_engine.py
│   ├── beat_matcher.py
│   └── transition_manager.py
├── youtube/                 # Pobieranie z YouTube
│   ├── playlist_downloader.py
│   └── audio_converter.py
├── core/                    # Logika główna
│   ├── app.py
│   └── config.py
├── ui/                      # Interfejs użytkownika
│   └── web_interface.py
└── utils/                   # Narzędzia
    ├── audio_loader.py
    └── file_manager.py

data/                        # Dane tymczasowe
├── downloads/
├── processed/
└── output/

requirements.txt
README.md
```

## Technologie
- **Backend**: Python
- **Audio Processing**: librosa, pydub, soundfile
- **YouTube**: yt-dlp
- **Analiza**: numpy, scipy
- **UI**: Streamlit lub Flask + React

## Etapy Realizacji

1. **Faza 1**: Podstawowa analiza audio (energia, BPM)
2. **Faza 2**: Wykrywanie interesujących fragmentów
3. **Faza 3**: Prosty mikser z crossfade
4. **Faza 4**: Pobieranie z YouTube
5. **Faza 5**: Zaawansowane przejścia (beatmatching)
6. **Faza 6**: UI i finalizacja

## Algorytmy

### Wykrywanie Najciekawszych Fragmentów
1. Oblicz RMS energy dla każdego frame
2. Znajdź piki energii
3. Analizuj zmiany spectral flux
4. Zidentyfikuj sekcje o wysokiej aktywności
5. Oceń "interesującość" na podstawie:
   - Energii
   - Zmienności
   - Obecności wokalu (opcjonalnie)

### Kolejność Fragmentów
1. Wykryj key każdego fragmentu
2. Oblicz BPM
3. Utwórz graf kompatybilności
4. Znajdź optymalną ścieżkę (TSP lub greedy)
5. Minimalizuj sumę "kosztów" przejść

### Przejścia
1. Dopasuj tempo (time stretching)
2. Zastosuj crossfade (1-3 sekundy)
3. Opcjonalnie: EQ transition
4. Wygładź przejście (envelope shaping)
