# ShorterMusic - TODO List

## Faza 1: Podstawowa Struktura i Analiza Audio
- [x] Stworzenie struktury folderów
- [ ] Utworzenie requirements.txt z zależnościami
- [ ] Implementacja audio_loader.py (wczytywanie plików audio)
- [ ] Implementacja energy_detector.py (analiza RMS energy)
- [ ] Implementacja bpm_detector.py (wykrywanie BPM)
- [ ] Testy podstawowych funkcji analizy

## Faza 2: Wykrywanie Fragmentów
- [ ] Implementacja segment_finder.py (znajdowanie fragmentów 7-30s)
- [ ] Algorytm oceny "interesującości" fragmentów
- [ ] Implementacja key_detector.py (wykrywanie tonacji)
- [ ] Testy wykrywania fragmentów na różnych gatunkach

## Faza 3: Miksowanie Podstawowe
- [ ] Implementacja crossfade_engine.py (prosty crossfade)
- [ ] Implementacja transition_manager.py (zarządzanie przejściami)
- [ ] Algorytm kolejności fragmentów (prosty - po kolei)
- [ ] Pierwszy działający miks z crossfade

## Faza 4: Pobieranie z YouTube
- [ ] Implementacja playlist_downloader.py
- [ ] Implementacja audio_converter.py (do WAV/MP3)
- [ ] Obsługa błędów pobierania
- [ ] Testy pobierania playlist

## Faza 5: Zaawansowane Miksowanie
- [ ] Implementacja beat_matcher.py (dopasowanie uderzeń)
- [ ] Algorytm optymalnej kolejności (graf kompatybilności)
- [ ] Zaawansowane przejścia (EQ, morphing)
- [ ] Time stretching dla dopasowania BPM

## Faza 6: UI i Finalizacja
- [ ] Interfejs webowy (Streamlit/Flask)
- [ ] Upload plików audio
- [ ] Wklejanie linku do playlisty YouTube
- [ ] Podgląd i pobieranie miksu
- [ ] Dokumentacja i README
- [ ] Testy end-to-end

## Priorytety
1. Wysoki: Faza 1-3 (działający prototyp)
2. Średni: Faza 4 (YouTube)
3. Niski: Faza 5-6 (ulepszenia i UI)
