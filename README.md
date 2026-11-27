# YouTube Clipper

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Gavin12715/Yt-clipping-/blob/main/clipper.ipynb)

**On iPad:** tap the badge above (YouTube links may be blocked there; tick *UPLOAD_VIDEO_INSTEAD* to use a file), then follow the steps at the top of the notebook. Everything runs on Google's servers.

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

## Laptop setup (recommended)

Running on your own computer avoids YouTube's "confirm you're not a bot" block that cloud servers get.

1. On GitHub, tap **Code → Download ZIP** and unzip it (e.g. to your Desktop).
2. One-time install (≈10 min, downloads a few GB of AI models/libraries):
   - **Mac:** open Terminal, type `bash ` (with a space), drag `setup_mac.sh` into the window, press Return.
   - **Windows:** double-click `setup_windows.bat`. If it says Python was just installed, run it again.
3. Make clips: double-click **`clip_mac.command`** (Mac) or **`clip_windows.bat`** (Windows), paste a YouTube link, and answer **n** to the Postiz question.
   Clips appear in the `clips` folder.
   - Mac may say the file "can't be opened": right-click it → **Open** → **Open** (only the first time).
4. *(Optional)* Open `.env` in a text editor to add your Postiz key, or set `YTDLP_BROWSER=chrome`
   (Windows: `firefox`) if YouTube still asks you to sign in.

Older Intel Macs are supported (`setup_mac.sh` picks `requirements-mac-intel.txt` automatically) but are slow.
Without a graphics card, transcription runs on the CPU: roughly real-time with the default model,
so an hour-long video takes about an hour. Use `--start`/`--end` to only process part of it.

## Manual setup

1. Install **Python 3.10–3.13**, **ffmpeg** and **libmagic** (`brew install ffmpeg libmagic` on macOS;
   on Windows use `pip install python-magic-bin` instead of libmagic).
2. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. *(Optional, for auto-posting)* Postiz: use postiz.com (paid) or self-host it with Docker. Connect your YouTube
   channel, then copy the key from **Settings → Public API** into `.env` (`cp .env.example .env`).
4. *(Optional)* `HF_TOKEN` in `.env` (Hugging Face token, after accepting the terms of
   `pyannote/speaker-diarization-3.0`) makes crops follow whoever is speaking. Without it, clips use a center crop.

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
#   --browser chrome   use your browser's YouTube login if downloads get blocked
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
