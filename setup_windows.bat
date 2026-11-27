@echo off
REM One-time setup for Windows. Double-click this file.
cd /d "%~dp0"

where py >nul 2>nul || (
  echo Installing Python 3.12...
  winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
)
where ffmpeg >nul 2>nul || (
  echo Installing FFmpeg...
  winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
)

py -3.12 -m venv .venv || (
  echo.
  echo Python was just installed. Close this window and double-click setup_windows.bat again.
  pause & exit /b 1
)
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
REM Windows has no libmagic; this package bundles it
.venv\Scripts\pip uninstall -y python-magic
.venv\Scripts\pip install python-magic-bin

if not exist .env copy .env.example .env
echo.
echo Done. Double-click clip_windows.bat to make clips.
pause
