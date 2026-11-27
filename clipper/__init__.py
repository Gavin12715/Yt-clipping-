"""YouTube clipping pipeline."""
import shutil

# Use a bundled ffmpeg/ffprobe if none is installed system-wide
# (e.g. Macs where Homebrew can't install ffmpeg).
if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
    try:
        import static_ffmpeg

        static_ffmpeg.add_paths()
    except ImportError:
        pass
