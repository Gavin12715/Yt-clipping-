#!/bin/bash
# One-time setup for macOS. Run:  bash setup_mac.sh
set -e
cd "$(dirname "$0")"

if ! command -v brew >/dev/null; then
  echo "Installing Homebrew (asks for your Mac password)..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi
brew install python@3.12 ffmpeg libmagic

PY="$(brew --prefix python@3.12)/bin/python3.12"
"$PY" -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

[ -f .env ] || cp .env.example .env
chmod +x clip_mac.command
echo
echo "Done. Double-click clip_mac.command to make clips."
