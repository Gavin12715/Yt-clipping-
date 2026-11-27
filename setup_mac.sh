#!/bin/bash
# One-time setup for macOS. Run:  bash setup_mac.sh
set -e
cd "$(dirname "$0")"

PY=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12

# 1. Python 3.12 from python.org (works on Macs Homebrew no longer supports)
if [ ! -x "$PY" ]; then
  echo "Downloading Python 3.12 from python.org..."
  curl -fL -o /tmp/python312.pkg https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg
  echo "Installing Python (enter your Mac password; nothing shows while you type)..."
  sudo installer -pkg /tmp/python312.pkg -target /
  rm -f /tmp/python312.pkg
fi

# 2. libmagic (ClipsAI needs it to detect file types)
if ! ls /usr/local/lib/libmagic* /opt/homebrew/lib/libmagic* >/dev/null 2>&1; then
  if command -v brew >/dev/null; then
    brew install libmagic
  else
    echo "Homebrew not found; installing it (needed only for libmagic)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
    brew install libmagic
  fi
fi

# 3. Python packages (Intel Macs need older PyTorch-compatible versions)
if [ "$(uname -m)" = "x86_64" ]; then REQ=requirements-mac-intel.txt; else REQ=requirements.txt; fi
echo "Installing Python packages from $REQ (this takes a while)..."
rm -rf .venv
"$PY" -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r "$REQ"

# 4. ffmpeg: bundled copy via static-ffmpeg (downloads once)
.venv/bin/python -c "import static_ffmpeg; static_ffmpeg.add_paths(); print('ffmpeg ready')"

# 5. Quick check that everything imports
.venv/bin/python -c "import clipper, yt_dlp, clipsai, whisperx; print('All packages OK')"

[ -f .env ] || cp .env.example .env
chmod +x clip_mac.command
echo
echo "Done. Double-click clip_mac.command to make clips."
