"""Spectrogram thumbnails and slowed-down audio clips for the review screen."""
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image
from scipy import signal

from .detect import SR

# magma-like ramp: night -> violet -> magenta -> amber -> pale
_STOPS = np.array([[10, 21, 16], [59, 15, 112], [181, 54, 122], [233, 160, 75], [252, 239, 180]], np.float32)


def _colour(v: np.ndarray) -> np.ndarray:
    pos = np.clip(v, 0, 1) * (len(_STOPS) - 1)
    i = np.minimum(pos.astype(int), len(_STOPS) - 2)
    f = (pos - i)[..., None]
    return (_STOPS[i] * (1 - f) + _STOPS[i + 1] * f).astype(np.uint8)


def spectrogram_png(clip: np.ndarray, path: Path, width: int = 360, height: int = 140,
                    min_khz: int = 10, max_khz: int = 190) -> None:
    f, _, S = signal.stft(clip, fs=SR, nperseg=512, noverlap=384)
    keep = (f >= min_khz * 1000) & (f <= max_khz * 1000)
    db = 20 * np.log10(np.abs(S[keep]) + 1e-9)
    # show the top 40 dB, brightest calls near white; noise floor stays dark
    hi = np.percentile(db, 99.9)
    level = np.clip((db - (hi - 40)) / 40, 0, 1) ** 0.8
    img = _colour(level)[::-1]  # high frequencies on top
    Image.fromarray(img).resize((width, height), Image.BILINEAR).save(path, optimize=True)


def slowed_wav(clip: np.ndarray, path: Path, factor: int = 10) -> None:
    """Write the clip slowed down `factor` times so people can hear bat calls."""
    clip = clip / (np.abs(clip).max() + 1e-9) * 0.9
    sf.write(path, clip.astype(np.float32), SR // factor, subtype="PCM_16")
