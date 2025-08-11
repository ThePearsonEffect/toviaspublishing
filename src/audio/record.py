from __future__ import annotations

from pathlib import Path

import sounddevice as sd
import soundfile as sf


def record_microphone(out_path: Path, seconds: int = 60, sample_rate: int = 44100) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    sf.write(out_path, audio, sample_rate)
    return out_path
