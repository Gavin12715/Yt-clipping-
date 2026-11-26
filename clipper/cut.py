"""Cut a clip out of the source video and reframe it to vertical 9:16.

With a Hugging Face token (HF_TOKEN) ClipsAI tracks the active speaker's face.
Without one we fall back to a plain center crop with ffmpeg.
"""
import subprocess
from pathlib import Path


def _ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def trim(src, start, end, dst):
    """Frame-accurate trim (re-encodes so the cut doesn't snap to keyframes)."""
    _ffmpeg("-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", str(src),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "aac", "-movflags", "+faststart", str(dst))
    return Path(dst)


def center_crop_vertical(src, dst):
    _ffmpeg("-i", str(src),
            "-vf", "crop='min(iw,ih*9/16)':ih,scale=1080:1920,setsar=1",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-c:a", "copy", "-movflags", "+faststart", str(dst))
    return Path(dst)


def speaker_crop_vertical(src, dst, hf_token):
    from clipsai import MediaEditor, resize

    src, dst = Path(src).resolve(), Path(dst).resolve()
    crops = resize(video_file_path=str(src), pyannote_auth_token=hf_token,
                   aspect_ratio=(9, 16))
    editor = MediaEditor()
    editor.resize_video(
        original_video_file=editor.instantiate_as_temporal_media_file(str(src)),
        resized_video_file_path=str(dst),
        width=crops.crop_width,
        height=crops.crop_height,
        segments=crops.to_dict()["segments"],
    )
    return dst


def make_short(src, start, end, out_path, hf_token=None):
    """Trim [start, end] from src and save a 9:16 clip at out_path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.stem + ".trim.mp4")
    trim(src, start, end, tmp)
    try:
        if hf_token:
            speaker_crop_vertical(tmp, out_path, hf_token)
        else:
            center_crop_vertical(tmp, out_path)
    finally:
        tmp.unlink(missing_ok=True)
    return out_path
