# ShorterMusic

ShorterMusic automatically builds a single continuous mix from the most interesting
fragments of your tracks. For every song it analyses energy, tempo (BPM) and key,
picks the best segments, and stitches them together with smart crossfades. It can
also download the tracks straight from a YouTube playlist before mixing.

## Features

- Picks the highest-energy, most interesting segments of each track
- Beat-aware segment boundaries and key/BPM-based ordering of the mix
- Smooth equal-power / S-curve crossfades between segments
- Stereo output, peak-normalised with headroom (no clipping)
- Parallel analysis across all CPU cores
- Optional YouTube playlist / URL downloading

## Requirements

- Python 3.10–3.12 (3.11 recommended)
- [`ffmpeg`](https://ffmpeg.org/) and [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) available on your `PATH`

## Quick start

**Windows**

```bat
run.bat
```

**Linux / macOS**

```bash
./run.sh
```

Both launchers create a virtual environment, install dependencies and start the
interactive app. To run it manually:

```bash
python -m venv venv
venv/bin/python -m pip install -r requirements.txt   # Windows: venv\Scripts\python
python interactive.py
```

## Usage

1. Choose a source: a YouTube playlist or local files in `data/downloads`.
2. Set how many segments per track and the fragment length range (in seconds).
3. Pick an output name — the finished mix is written to `data/output`.

## How it works

```
load track ─▶ analyse (energy / BPM / key) ─▶ select best segments
          ─▶ order by key & tempo ─▶ crossfade ─▶ normalise ─▶ export mp3
```

The audio analysis runs in parallel, one process per track, to use every CPU core.

## Notes

- Tempo-matching time-stretch is disabled by default because the phase-vocoder
  artefacts hurt audio quality on percussive music. Enable it with
  `TransitionManager(enable_time_stretch=True)` if you want beat-matching.
- `data/`, `bin/` and `venv/` are git-ignored; supply your own `ffmpeg`/`yt-dlp`.
