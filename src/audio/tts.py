from __future__ import annotations

from pathlib import Path

import pyttsx3
import soundfile as sf
import numpy as np


def text_to_speech(text: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    engine = pyttsx3.init()
    temp_wav = out_path.with_suffix(".temp.wav")
    engine.save_to_file(text, str(temp_wav))
    engine.runAndWait()
    data, sr = sf.read(temp_wav)
    peak = max(1e-6, float(np.max(np.abs(data))))
    data = (data / peak) * 0.95
    sf.write(out_path, data, sr)
    try:
        temp_wav.unlink(missing_ok=True)
    except Exception:
        pass
    return out_path
