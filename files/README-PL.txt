# ShorterMusic - Windows Ready Package

## Struktura folderu

```
ShorterMusic/
  ShorterMusic.exe     (główna aplikacja)
  data/
    downloads/         (tymczasowe pliki pobrane z YouTube)
    output/            (wygenerowane miks)
  bin/
    ffmpeg/
      ffmpeg.exe       (dołączony)
    yt-dlp/
      yt-dlp.exe       (dołączony)
  README-PL.txt        (ten plik)
```

## Jak uruchomić

1. Rozpakuj folder `ShorterMusic` w dowolnym miejscu na dysku.
2. Kliknij dwukrotnie `ShorterMusic.exe`.
3. Postępuj zgodnie z instrukcjami w konsoli.

## Wymagania

- **Brak** – wszystkie zależności są dołączone wewnątrz pliku EXE.
- Windows 10 lub nowszy (zalecany 64-bit).

## Uwagi

- Folder `data/downloads` przechowuje pliki pobrane z YouTube. Po zakończeniu sesji aplikacja zapyta, czy usunąć te pliki. Jeśli ich nie usuniesz, następy miks będzie korzystał ze wszystkich plików pozostawionych w tym folderze.
- Wynikowy miks zapisywany jest w `data/output`.
- Jeśli aplikacja nie może znaleźć `ffmpeg.exe` lub `yt-dlp.exe`, upewnij się, że znajdują się one w katalogach `bin/ffmpeg/` i `bin/yt-dlp/`.

## Budowanie EXE (dla deweloperów)

Jeśli chcesz przebudować plik EXE:

1. Upewnij się, że masz zainstalowane Python 3.10+ i aktywne środowisko wirtualne.
2. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
3. Umieść `ffmpeg.exe` w `bin/ffmpeg/` i `yt-dlp.exe` w `bin/yt-dlp/`.
4. Uruchom:
   ```
   pyinstaller ShorterMusic.spec
   ```
5. Gotowy plik EXE znajdziesz w `dist/ShorterMusic.exe`.

## Problemy i rozwiązania

- **„Nie znaleziono ffmpeg.exe”** – sprawdź, czy `ffmpeg.exe` jest w `bin/ffmpeg/`.
- **„Nie znaleziono yt-dlp.exe”** – sprawdź, czy `yt-dlp.exe` jest w `bin/yt-dlp/`.
- **Aplikacja nie startuje** – upewnij się, że nie używasz antywirusa blokującego EXE; dodaj folder do wyjątków.
- **Pobieranie z YouTube nie działa** – sprawdź połączenie z internetem; `yt-dlp` może wymagać aktualizacji (nie jest możliwe w wersji spakowanej).

## Licencja

Ta aplikacja jest dostarczana „tak jak jest”. Binarki ffmpeg i yt-dlp są objęte własnymi licencjami.
