#!/bin/bash
# Double-click to run on macOS.
cd "$(dirname "$0")"
.venv/bin/python -m clipper.pipeline "$@"
echo
echo "Clips are in the 'clips' folder. Press Enter to close."
read
