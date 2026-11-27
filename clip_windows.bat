@echo off
REM Double-click to run on Windows.
cd /d "%~dp0"
.venv\Scripts\python -m clipper.pipeline %*
echo.
echo Clips are in the "clips" folder.
pause
