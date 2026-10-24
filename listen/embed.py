"""Perch 2.0 embeddings for time-expanded bat calls.

A 160,000-sample window at 384 kHz, fed to Perch as if it were 32 kHz audio, is the call
slowed down 12x: 12-192 kHz becomes 1-16 kHz, inside the range Perch was trained on.
"""
from pathlib import Path

import numpy as np

PERCH_DIR = Path.home() / ".cache/kagglehub/models/google/bird-vocalization-classifier/tensorFlow2/perch_v2_cpu/1"
_model = None


def _load():
    global _model
    if _model is None:
        import tensorflow as tf  # imported lazily: it takes a few seconds
        if not PERCH_DIR.exists():
            import kagglehub  # first run only, needs internet once
            kagglehub.model_download("google/bird-vocalization-classifier/tensorFlow2/perch_v2_cpu")
        _model = (tf, tf.saved_model.load(str(PERCH_DIR)).signatures["serving_default"])
    return _model


def embed(windows: np.ndarray, batch: int = 16, progress=None) -> np.ndarray:
    tf, model = _load()
    out = []
    for i in range(0, len(windows), batch):
        out.append(model(inputs=tf.constant(windows[i:i + batch]))["embedding"].numpy())
        if progress:
            progress(min(i + batch, len(windows)), len(windows))
    return np.concatenate(out) if out else np.zeros((0, 1536), np.float32)
