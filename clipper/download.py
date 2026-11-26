"""Download source videos with yt-dlp.

Usage:
    python -m clipper.download URL [--start 1:23 --end 2:10] [--out downloads]
"""
import argparse
import os
from pathlib import Path

import yt_dlp
from yt_dlp.utils import download_range_func, parse_duration


def download(url, out_dir="downloads", start=None, end=None, max_height=1080,
             cookies=None):
    """Download a video (or just the start-end section) and return its info dict.

    The returned dict includes "filepath" pointing to the saved .mp4, plus
    yt-dlp metadata (title, uploader, duration, ...) for later pipeline steps.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    opts = {
        "format": f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b",
        "merge_output_format": "mp4",
        "outtmpl": str(out_dir / "%(id)s%(section_start|)s.%(ext)s"),
        "writeinfojson": True,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    cookies = cookies or os.environ.get("YTDLP_COOKIES")
    if cookies and Path(cookies).exists():
        # Netscape cookies.txt from a logged-in YouTube account; avoids the
        # "Sign in to confirm you're not a bot" block on cloud servers.
        opts["cookiefile"] = str(cookies)
    if start is not None or end is not None:
        s = parse_duration(start) if start else 0
        e = parse_duration(end) if end else float("inf")
        opts["download_ranges"] = download_range_func(None, [(s, e)])
        opts["force_keyframes_at_cuts"] = True

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        info = ydl.sanitize_info(info)
    reqs = info.get("requested_downloads") or [{}]
    info["filepath"] = reqs[0].get("filepath")
    return info


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("url")
    p.add_argument("--start", help="clip start, e.g. 90 or 1:30")
    p.add_argument("--end", help="clip end, e.g. 2:45")
    p.add_argument("--out", default="downloads")
    p.add_argument("--max-height", type=int, default=1080)
    p.add_argument("--cookies", help="cookies.txt for YouTube (or set YTDLP_COOKIES)")
    a = p.parse_args()
    info = download(a.url, a.out, a.start, a.end, a.max_height, a.cookies)
    print(f"{info.get('title')} -> {info['filepath']}")


if __name__ == "__main__":
    main()
