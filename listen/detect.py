"""Find bat passes in ultrasonic recordings.

A pass is a short burst of echolocation calls (one bat flying by). We work at 384 kHz,
look for energy in the 15-180 kHz band well above the file's own noise floor, and merge
detections that are close in time into passes.
"""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

SR = 384_000
MIN_SR = 192_000          # below this the file can't hold most bat calls
FRAME, HOP = 2048, 1024   # ~5.3 ms frames
BAND = (15_000, 180_000)
WINDOW = 160_000          # one Perch input: 0.417 s real time, 5 s once slowed 12x


@dataclass
class Pass:
    file: str
    start: float        # seconds
    end: float
    peak_khz: float     # frequency with the most energy
    calls: int          # number of separate call frames above threshold
    snr_db: float


def load(path: Path, time_expansion: int = 1) -> np.ndarray:
    """Mono float32 at 384 kHz with low-frequency noise removed. Raises ValueError if unusable.

    time_expansion: how many times slower the file was saved than real time (many detectors and
    libraries store ultrasound slowed 10x or 16x). The real sample rate is file rate x factor."""
    info = sf.info(path)
    real_sr = info.samplerate * time_expansion
    if real_sr < MIN_SR:
        raise ValueError(f"sample rate {info.samplerate} Hz is too low for bat calls. "
                         "If these files are time-expanded, set the time-expansion factor (often 10 or 16).")
    x, _ = sf.read(path, dtype="float32", always_2d=True)
    x, sr = x[:, 0], real_sr
    if sr != SR:
        g = np.gcd(sr, SR)
        x = signal.resample_poly(x, SR // g, sr // g).astype(np.float32)
    sos = signal.butter(6, BAND, "bandpass", fs=SR, output="sos")
    return signal.sosfiltfilt(sos, x).astype(np.float32)


def tonal_snr_db(x: np.ndarray) -> np.ndarray:
    """Per frame: the strongest frequency bin's level above that bin's own noise floor.
    Bat calls are narrow and tonal, so they stand out per bin even when total energy is low.
    The floor is each bin's median over time: calls are narrow, so any single bin is quiet most of the time."""
    if len(x) < FRAME:
        x = np.pad(x, (0, FRAME - len(x)))
    f, _, S = signal.stft(x, fs=SR, nperseg=512, noverlap=512 - 256, boundary=None, padded=False)
    band = (f >= BAND[0]) & (f <= BAND[1])
    db = 20 * np.log10(np.abs(S[band]) + 1e-9)
    floor = np.median(db, axis=1, keepdims=True)
    snr = (db - floor).max(axis=0)
    # resample from 256-sample hops to our 1024-sample frames
    n = len(snr) // 4
    return snr[: n * 4].reshape(n, 4).max(axis=1)


def peak_frequency_khz(x: np.ndarray) -> float:
    f, p = signal.welch(x, fs=SR, nperseg=2048)
    band = (f >= BAND[0]) & (f <= BAND[1])
    return float(f[band][np.argmax(p[band])] / 1000)


def find_passes(x: np.ndarray, file: str, threshold_db: float = 18.0, merge_gap: float = 0.4,
                min_calls: int = 2) -> list[Pass]:
    """Frames with a tonal peak threshold_db above the noise floor are call frames; nearby frames form a pass."""
    e = tonal_snr_db(x)
    floor = 0.0
    hot = e > threshold_db
    if not hot.any():
        return []
    idx = np.flatnonzero(hot)
    t = idx * HOP / SR
    passes, start = [], 0
    for i in range(1, len(idx) + 1):
        if i == len(idx) or t[i] - t[i - 1] > merge_gap:
            seg = idx[start:i]
            calls = int(np.sum(np.diff(seg) > 2)) + 1  # separate bursts of hot frames
            if calls >= min_calls:
                s, en = seg[0] * HOP / SR, (seg[-1] * HOP + FRAME) / SR
                clip = x[int(s * SR): int(en * SR)]
                passes.append(Pass(file, round(s, 3), round(en, 3), round(peak_frequency_khz(clip), 1),
                                   calls, round(float(e[seg].max() - floor), 1)))
            start = i
    return passes


def pass_windows(x: np.ndarray, p: Pass, max_windows: int = 3) -> list[np.ndarray]:
    """Up to max_windows Perch-sized windows covering the loudest parts of a pass, peak-normalised."""
    a, b = int(p.start * SR), int(p.end * SR)
    centre_points = [(a + b) // 2] if b - a <= WINDOW else list(np.linspace(a + WINDOW // 2, b - WINDOW // 2, min(max_windows, int(np.ceil((b - a) / WINDOW)))).astype(int))
    out = []
    for c in centre_points:
        s = max(0, min(len(x) - WINDOW, c - WINDOW // 2))
        w = x[s: s + WINDOW]
        if len(w) < WINDOW:
            w = np.pad(w, (0, WINDOW - len(w)))
        out.append((w / (np.abs(w).max() + 1e-9)).astype(np.float32))
    return out
