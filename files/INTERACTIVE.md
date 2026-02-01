# ShorterMusic - Interaktywny Skrypt

Uruchom interaktywny skrypt, aby stworzyć miks:

```bash
./venv/bin/python interactive.py
```

lub

```bash
./interactive.py
```

## Funkcje skryptu:

1. **Wybór źródła:**
   - Pobierz playlistę z YouTube
   - Użyj plików z folderu `data/downloads`

2. **Konfiguracja pobierania (YouTube):**
   - Podaj URL playlisty
   - Ile utworów pobrać (0 = wszystkie)

3. **Konfiguracja segmentów:**
   - Liczba segmentów na utwór (domyślnie 1)
   - Zakres długości fragmentów (domyślnie 7-15 sekund)

4. **Pasek postępu:**
   - Wizualny pasek postępu podczas pobierania
   - Procentowe wykonanie

5. **Po zakończeniu:**
   - Pyta czy usunąć pobrane pliki z folderu downloads

## Przykład użycia:

```
============================================================
       ShorterMusic - Interactive Mix Creator
============================================================

Wybierz źródło utworów:
  1. Pobierz playlistę z YouTube
  2. Użyj plików z folderu downloads
  Wybierz (1-2): 1

Pobieranie z YouTube:
  Podaj URL playlisty YouTube: https://youtube.com/playlist?list=...
  Ile utworów pobrać? (0 = wszystkie): 5

  Pobieranie 5 utworów...
  [██████████████████████████████░░░░] 80.0% (4/5) ✓
  [██████████████████████████████████] 100.0% (5/5)
  Pobrano 5 plików

Konfiguracja segmentów:
  Liczba segmentów na utwór: 1

  Zakres długości fragmentów (w sekundach):
    Minimalna długość: 7
    Maksymalna długość: 15

  Nazwa pliku wyjściowego (bez rozszerzenia): my_mix

  Tworzenie miksu z 5 plików...
  1 segmentów na utwór
  Długość: 7.0s - 15.0s

  ✓ Miks utworzony: data/output/my_mix.mp3

  Usunąć pobrane pliki z folderu downloads? (t/n): t
  ✓ Usunięto 5 plików

============================================================
  Zakończono!
============================================================
```
