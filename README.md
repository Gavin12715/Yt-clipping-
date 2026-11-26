# YouTube Clipper

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gavin12715/Yt-clipping-/blob/main/clipper.ipynb)

**On iPad:** tap the badge above, then follow the steps at the top of the notebook. Everything runs on Google's servers.

Turns long YouTube videos into vertical Shorts and schedules them to your channel.

```
YouTube URL ─▶ yt-dlp ─▶ ClipsAI (transcribe + find clips) ─▶ ffmpeg / ClipsAI (9:16 crop) ─▶ Postiz ─▶ YouTube
             download     clipper/find_clips.py               clipper/cut.py                   clipper/postiz.py
```

| Piece   | Role                                                                 |
|---------|----------------------------------------------------------------------|
| yt-dlp  | Downloads the source video (or just a time range)                    |
| ClipsAI | Transcribes with WhisperX and picks self-contained clips by topic; optional speaker-tracking crop |
| Postiz  | Uploads each clip and schedules it on your connected YouTube channel |

## Setup

1. Install **Python 3.10+**, **ffmpeg** and **libmagic** (`brew install ffmpeg libmagic` on macOS).
2. Install the Python packages:
   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Set up **Postiz**: either use postiz.com, or self-host it with Docker
   (`docker compose up -d` in the postiz-app repo; the UI runs at http://localhost:4007).
   In Postiz, connect your YouTube channel, then go to **Settings → Public API** and copy the key.
4. `cp .env.example .env` and fill in `POSTIZ_API_KEY` and `POSTIZ_URL`.
   Optional: add `HF_TOKEN` (a Hugging Face token, after accepting the terms of
   `pyannote/speaker-diarization-3.0`) so crops follow whoever is speaking.
   Without it, clips use a center crop.

## Usage (computer)

```bash
# Make clips only (saved to clips/<video id>/ with clips.json)
python -m clipper.pipeline "https://www.youtube.com/watch?v=VIDEO_ID"

# Make clips and send them to Postiz as drafts to review before they go live
python -m clipper.pipeline "https://www.youtube.com/watch?v=VIDEO_ID" --post draft

# Schedule them automatically, one every 3 hours
python -m clipper.pipeline "URL" --post schedule --every 180

# Options
#   --max-clips 5      how many clips to keep (longest first)
#   --min 15 --max 60  clip length in seconds
#   --whisper small    Whisper model (bigger = more accurate, slower; default tiny on CPU)
#   --start 10:00 --end 40:00   only process part of a long video
#   --privacy unlisted
```

Single steps:

```bash
python -m clipper.download "URL" --start 1:30 --end 2:15
```

## Notes

- ClipsAI works best on talking videos (podcasts, interviews, streams with commentary).
- A GPU makes transcription and speaker-tracking much faster; CPU works but is slow.
- Only clip content you have the rights to use, or that falls under fair use (commentary, transformation).
  Reposting other creators' videos unchanged can get the channel copyright strikes or demonetized.
