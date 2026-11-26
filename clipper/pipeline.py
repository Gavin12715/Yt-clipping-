"""YouTube URL -> download (yt-dlp) -> find clips (ClipsAI) -> 9:16 Shorts -> Postiz.

Examples:
    python -m clipper.pipeline URL                      # make clips only
    python -m clipper.pipeline URL --post draft         # + send to Postiz as drafts
    python -m clipper.pipeline URL --post schedule --every 180   # one every 3h
"""
import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path

from .cut import make_short
from .download import download
from .find_clips import find_clips


def _load_dotenv(path=".env"):
    p = Path(path)
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"\''))


def _title_for(clip, source_title):
    first = re.split(r"(?<=[.!?])\s", clip.text, maxsplit=1)[0]
    title = first if 15 <= len(first) <= 90 else source_title
    return f"{title[:90]} #shorts"


def run(url, out_dir="clips", max_clips=5, min_dur=15, max_dur=60,
        whisper_model=None, post=None, privacy="public", every_minutes=180,
        start=None, end=None):
    _load_dotenv()
    info = download(url, "downloads", start, end)
    src, title = info["filepath"], info.get("title", "")
    print(f"Downloaded: {title}")

    clips = find_clips(src, min_dur, max_dur, whisper_model)
    clips.sort(key=lambda c: c.duration, reverse=True)
    clips = clips[:max_clips]
    print(f"Found {len(clips)} clips")

    out = Path(out_dir) / info["id"]
    hf = os.environ.get("HF_TOKEN")
    results = []
    for i, c in enumerate(clips, 1):
        path = make_short(src, c.start, c.end, out / f"clip_{i:02d}.mp4", hf)
        results.append({**c.to_dict(), "file": str(path),
                        "title": _title_for(c, title)})
        print(f"  [{i}] {c.start:7.1f}-{c.end:7.1f}s -> {path}")

    if post:
        from .postiz import Postiz
        pz = Postiz()
        channel = pz.youtube_channel_id()
        when = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=10)
        credit = f"Source: {info.get('webpage_url', url)}"
        for r in results:
            res = pz.post_youtube_short(
                r["file"], r["title"], f"{r['text'][:4000]}\n\n{credit}",
                tags=["shorts"], when=when, privacy=privacy,
                channel_id=channel, mode=post)
            r["postiz"] = res
            print(f"  Postiz {post}: {r['title']} @ {when:%Y-%m-%d %H:%M} UTC")
            when += dt.timedelta(minutes=every_minutes)

    (out / "clips.json").write_text(json.dumps(results, indent=2))
    return results


def main():
    p = argparse.ArgumentParser(description="Turn a YouTube video into Shorts.")
    p.add_argument("url")
    p.add_argument("--max-clips", type=int, default=5)
    p.add_argument("--min", type=int, default=15, help="min clip seconds")
    p.add_argument("--max", type=int, default=60, help="max clip seconds")
    p.add_argument("--whisper", default=None, help="tiny|base|small|medium|large-v2")
    p.add_argument("--start", help="only use this part of the source, e.g. 10:00")
    p.add_argument("--end")
    p.add_argument("--post", choices=["draft", "schedule", "now"])
    p.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    p.add_argument("--every", type=int, default=180, help="minutes between scheduled posts")
    p.add_argument("--out", default="clips")
    a = p.parse_args()
    run(a.url, a.out, a.max_clips, a.min, a.max, a.whisper, a.post, a.privacy,
        a.every, a.start, a.end)


if __name__ == "__main__":
    main()
