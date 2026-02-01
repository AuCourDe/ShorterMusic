import os
import subprocess

# =============================
# 1. LISTA TYTUŁÓW (wyczyszczona)
# =============================

titles = [
    "Koziołek Matołek",
    "Smerfy",
    "Muminki",
    "Krecik",
    "Przygody Kota Filemona",
    "Mała Syrenka",
    "Kubuś Puchatek",
    "Popeye",
    "Sąsiedzi",
    "Pocahontas"
]

# =============================================
# 2. Utworzenie folderu "audio" jeśli nie istnieje
# =============================================

os.makedirs("audio", exist_ok=True)

# =============================================
# 3. Pobieranie audio dla każdego tytułu
# =============================================

for title in titles:
    print(f"\n=== Pobieram: {title} ===")

    # wyszukiwane frazy
    search_queries = [
        f"ytsearch1:{title} intro",
        f"ytsearch1:{title} muzyka",
        f"ytsearch1:{title} sound"
    ]

    for query in search_queries:
        print(f"  -> Szukam: {query}")

        # komenda yt-dlp
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "-o", f"audio/{title}.%(ext)s",
            query
        ]

        try:
            subprocess.run(cmd, check=True)
            print("     ✔ znaleziono i pobrano!")
            break  # przerwij po pierwszym trafieniu
        except subprocess.CalledProcessError:
            print("     ✖ brak wyniku, próbuję kolejnej frazy...")

print("\n*** ZAKOŃCZONO ***")
