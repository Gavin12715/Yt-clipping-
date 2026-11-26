"""Minimal client for the Postiz public API (upload media + schedule YouTube posts).

POSTIZ_URL:     https://api.postiz.com/public/v1 (cloud) or
                http://localhost:4007/api/public/v1 (self-hosted docker compose)
POSTIZ_API_KEY: Postiz -> Settings -> Public API
"""
import datetime as dt
import os
from pathlib import Path

import requests


class Postiz:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ["POSTIZ_API_KEY"]
        self.base = (base_url or os.environ.get("POSTIZ_URL")
                     or "https://api.postiz.com/public/v1").rstrip("/")

    def _req(self, method, path, **kw):
        r = requests.request(method, self.base + path,
                             headers={"Authorization": self.api_key},
                             timeout=600, **kw)
        if not r.ok:
            raise RuntimeError(f"Postiz {method} {path} -> {r.status_code}: {r.text}")
        return r.json()

    def integrations(self):
        """Connected channels: [{id, name, identifier ('youtube', ...), disabled, ...}]"""
        return self._req("GET", "/integrations")

    def youtube_channel_id(self):
        yt = [i for i in self.integrations()
              if i.get("identifier") == "youtube" and not i.get("disabled")]
        if not yt:
            raise RuntimeError("No YouTube channel connected in Postiz.")
        return yt[0]["id"]

    def upload(self, path):
        """Upload a file; returns {id, path, ...} to reference in a post."""
        path = Path(path)
        with path.open("rb") as f:
            return self._req("POST", "/upload",
                             files={"file": (path.name, f, "video/mp4")})

    def post_youtube_short(self, video_path, title, description="", tags=(),
                           when=None, privacy="public", channel_id=None,
                           mode="schedule"):
        """Upload a clip and create a YouTube post.

        mode: "draft" (review in the Postiz UI first), "schedule" (at `when`), or "now".
        privacy: "public", "unlisted" or "private".
        """
        media = self.upload(video_path)
        when = when or dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5)
        body = {
            "type": mode,
            "shortLink": False,
            "date": when.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "tags": [],
            "posts": [{
                "integration": {"id": channel_id or self.youtube_channel_id()},
                "value": [{"content": description or title,
                           "image": [{"id": media["id"], "path": media["path"]}]}],
                "settings": {
                    "__type": "youtube",
                    "title": title[:100],
                    "type": privacy,
                    "selfDeclaredMadeForKids": "no",
                    "tags": [{"value": t, "label": t} for t in tags],
                },
            }],
        }
        return self._req("POST", "/posts", json=body)
