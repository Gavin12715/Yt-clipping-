"""Find clip-worthy moments in a video with ClipsAI (WhisperX transcript + TextTiling)."""
from dataclasses import dataclass, asdict


@dataclass
class FoundClip:
    start: float
    end: float
    text: str

    @property
    def duration(self):
        return self.end - self.start

    def to_dict(self):
        return asdict(self)


def find_clips(video_path, min_duration=15, max_duration=60, model_size=None):
    """Transcribe the video and return clips between min_duration and max_duration seconds.

    model_size: Whisper model ("tiny", "base", "small", "medium", "large-v2").
    None lets ClipsAI pick (large-v2 on GPU, tiny on CPU).
    """
    from clipsai import ClipFinder, Transcriber

    transcription = Transcriber(model_size=model_size).transcribe(
        audio_file_path=str(video_path)
    )
    finder = ClipFinder(min_clip_duration=min_duration, max_clip_duration=max_duration)
    text = transcription.text
    return [
        FoundClip(c.start_time, c.end_time, text[c.start_char:c.end_char].strip())
        for c in finder.find_clips(transcription=transcription)
    ]
