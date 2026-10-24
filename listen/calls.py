"""Measure individual echolocation calls the way bat ecologists do by hand.

For each call: start/end/peak frequency, characteristic frequency, duration, bandwidth, slope
and a shape class. These are the standard parameters used in South-East Asian call libraries
and discriminant-function identification, so the export plugs into existing workflows.

Method: a fine-time spectrogram (0.17 ms steps), per-frequency noise floor, then for every
burst of loud frames we follow the loudest frequency through time (the call's ridge).
"""
from dataclasses import dataclass, asdict

import numpy as np
from scipy import signal

from .detect import SR, BAND

NPERSEG, HOP = 512, 64          # 1.33 ms window, 0.167 ms steps at 384 kHz
SNR_DB = 15                     # ridge points must be this far above the bin's noise floor
EDGE_DB = 20                    # call edges: where the ridge drops this far below the call's peak
MIN_MS, MAX_MS = 1.0, 120.0     # shorter fragments are clicks, echoes or noise, not calls
MAX_RISE_KHZ = 3.0              # bats sweep down; an FM "call" rising more than this is noise


@dataclass
class Call:
    t_start: float          # seconds within the clip
    duration_ms: float
    f_start_khz: float
    f_end_khz: float
    f_peak_khz: float       # frequency of maximum energy
    f_char_khz: float       # characteristic frequency: lowest-slope part near the end of the call
    f_min_khz: float
    f_max_khz: float
    bandwidth_khz: float
    slope_khz_ms: float     # mean slope of the middle 80%, negative = downward sweep
    shape: str              # CF, CF-FM, FM, QCF or FM-QCF
    snr_db: float


def _shape(duration_ms: float, bw: float, f: np.ndarray, t_ms: np.ndarray) -> str:
    """Classify the call outline. Thresholds follow common textbook definitions."""
    if len(f) < 3:
        return "FM"
    n = len(f)
    # constant-frequency part: the flat stretch before any terminal sweep (first 70% of the call)
    body = f[int(n * 0.05): max(int(n * 0.7), int(n * 0.05) + 2)]
    body_bw = body.max() - body.min()
    flat_tol = max(2.0, 0.025 * float(np.median(body)))   # ~2.5% of the tone, e.g. 3 kHz at 120 kHz
    if duration_ms >= 2.5 and body_bw <= flat_tol:
        return "CF-FM" if bw > flat_tol + 3 else "CF"
    end = f[int(n * 0.6):]
    end_slope = abs(np.polyfit(t_ms[int(n * 0.6):], end, 1)[0]) if len(end) > 2 else 99
    if bw >= 20 and end_slope < 1.0:
        return "FM-QCF"
    if bw < 15 and duration_ms >= 3:
        return "QCF"
    return "FM"


def measure_calls(clip: np.ndarray) -> list[Call]:
    f, t, S = signal.stft(clip, fs=SR, nperseg=NPERSEG, noverlap=NPERSEG - HOP, boundary=None, padded=False)
    band = (f >= BAND[0]) & (f <= BAND[1])
    f = f[band] / 1000
    db = 20 * np.log10(np.abs(S[band]) + 1e-9)
    db -= np.median(db, axis=1, keepdims=True)          # each bin relative to its own noise floor
    ridge_db = db.max(axis=0)
    ridge_f = f[db.argmax(axis=0)]
    hot = ridge_db > SNR_DB
    calls = []
    i, n = 0, len(hot)
    while i < n:
        if not hot[i]:
            i += 1
            continue
        j = i
        while j < n and (hot[j] or (j + 1 < n and hot[j + 1])):   # bridge one-frame dropouts
            j += 1
        seg = slice(i, j)
        peak = ridge_db[seg].max()
        keep = ridge_db[seg] > peak - EDGE_DB
        tt, ff = t[seg][keep], ridge_f[seg][keep]
        if len(tt) >= 3:
            dur = (tt[-1] - tt[0]) * 1000 + HOP / SR * 1000
            if MIN_MS <= dur <= MAX_MS:
                t_ms = (tt - tt[0]) * 1000
                ff_s = signal.medfilt(ff, 3) if len(ff) >= 3 else ff   # drop single-frame jumps (harmonics, echoes)
                k0, k1 = int(len(ff_s) * 0.1), max(int(len(ff_s) * 0.9), int(len(ff_s) * 0.1) + 2)
                slope = np.polyfit(t_ms[k0:k1], ff_s[k0:k1], 1)[0] if k1 - k0 >= 2 else 0.0
                # characteristic frequency: the flattest stretch in the last 40% of the call
                tail = ff_s[int(len(ff_s) * 0.6):]
                fchar = float(np.median(tail[np.abs(np.gradient(tail)) <= np.percentile(np.abs(np.gradient(tail)), 30)])) if len(tail) > 2 else float(ff_s[-1])
                bw = float(ff_s.max() - ff_s.min())
                shape = _shape(dur, bw, ff_s, t_ms)
                if shape not in ("CF", "CF-FM") and ff_s[-1] - ff_s[0] > MAX_RISE_KHZ:
                    i = j + 1
                    continue
                calls.append(Call(
                    t_start=round(float(tt[0]), 5), duration_ms=round(dur, 2),
                    f_start_khz=round(float(ff_s[0]), 1), f_end_khz=round(float(ff_s[-1]), 1),
                    f_peak_khz=round(float(ff[np.argmax(ridge_db[seg][keep])]), 1),
                    f_char_khz=round(fchar, 1), f_min_khz=round(float(ff_s.min()), 1),
                    f_max_khz=round(float(ff_s.max()), 1), bandwidth_khz=round(bw, 1),
                    slope_khz_ms=round(float(slope), 2), shape=shape,
                    snr_db=round(float(peak), 1)))
        i = j + 1
    return calls


def dominant(calls: list[Call]) -> list[Call]:
    """The calls of the main bat in a pass: near the frequency of the loudest calls.
    Echoes, insects and other noise sit elsewhere in frequency and would skew the medians."""
    if not calls:
        return []
    near = lambda c, f0: abs(c.f_peak_khz - f0) <= max(6.0, 0.15 * f0)
    # anchor on the frequency shared by most of the 5 loudest calls (two bats in one pass split them)
    strong = sorted(calls, key=lambda c: -c.snr_db)[:5]
    f0 = max((c.f_peak_khz for c in strong), key=lambda f: sum(near(s, f) for s in strong))
    return [c for c in calls if near(c, f0)]


def summarise(calls: list[Call]) -> dict:
    """Median parameters over the main bat's best calls (the loudest half of its calls)."""
    if not calls:
        return {}
    main = dominant(calls)
    best = sorted(main, key=lambda c: -c.snr_db)[: max(3, len(main) // 2)]
    keys = ["duration_ms", "f_start_khz", "f_end_khz", "f_peak_khz", "f_char_khz", "bandwidth_khz", "slope_khz_ms"]
    out = {k: round(float(np.median([getattr(c, k) for c in best])), 2) for k in keys}
    shapes = [c.shape for c in best]
    out["shape"] = max(set(shapes), key=shapes.count)
    out["snr_db"] = round(float(np.median([c.snr_db for c in best])), 1)
    out["n_calls"] = len(main)
    starts = sorted(c.t_start for c in main)
    gaps = np.diff(starts) * 1000
    out["interval_ms"] = round(float(np.median(gaps)), 1) if len(gaps) else None
    return out


def sound_type(s: dict) -> dict:
    """Plain-language call type and the bat group it is typical of, from measured parameters.
    These are broad textbook patterns for South-East Asia, meant as a starting point for review,
    never as an identification."""
    if not s:
        return {"type": "unclear", "hint": "unclear calls (too faint to measure)"}
    sh, dur, fc, bw, fs = s["shape"], s["duration_ms"], s["f_char_khz"], s["bandwidth_khz"], s["f_start_khz"]
    # a pass needs a few clean calls to say anything; faint low "calls" are usually noise or insects
    if s.get("n_calls", 0) < 3 or (fc < 32 and s.get("snr_db", 99) < 25):
        return {"type": "unclear", "hint": "unclear calls (too few or too faint to measure)"}
    if sh in ("CF", "CF-FM") and dur >= 15:
        return {"type": f"long constant tone, about {fc:.0f} kHz", "hint": "typical of horseshoe bats (Rhinolophus)"}
    if sh in ("CF", "CF-FM"):
        return {"type": f"short constant tone, about {fc:.0f} kHz", "hint": "typical of leaf-nosed bats (Hipposideros and relatives)"}
    if sh == "FM" and dur <= 3.5 and bw >= 25 and fs >= 110:
        return {"type": f"very short, steep sweep from about {fs:.0f} kHz", "hint": "typical of woolly bats (Kerivoula) or tube-nosed bats (Murina)"}
    if fc < 32:
        return {"type": f"low, flat-ending call, about {fc:.0f} kHz", "hint": "typical of free-tailed or sheath-tailed bats (Molossidae, Emballonuridae)"}
    if sh in ("QCF", "FM-QCF"):
        return {"type": f"sweep ending in a flat tail, about {fc:.0f} kHz", "hint": "typical of vesper bats such as pipistrelles, or bent-winged bats (Miniopterus)"}
    return {"type": f"downward sweep ending near {fc:.0f} kHz", "hint": "typical of vesper bats such as Myotis"}


FEATURES = ["f_char_khz", "f_start_khz", "f_end_khz", "duration_ms", "bandwidth_khz", "slope_khz_ms"]


def feature_vector(s: dict) -> np.ndarray:
    """Measured call parameters as numbers for the classifier (NaN when a pass couldn't be measured).
    Frequency is what separates many Asian bats, e.g. Rhinolophus affinis ~73 kHz vs Hipposideros larvatus ~91 kHz."""
    v = [float(s.get(k, np.nan)) if s else np.nan for k in FEATURES]
    v.append(1.0 if s and s.get("shape") in ("CF", "CF-FM") else 0.0)
    return np.array(v, dtype=np.float32)


def as_rows(calls: list[Call], main: list[Call] | None = None) -> list[dict]:
    keep = {id(c) for c in (main or [])}
    return [asdict(c) | {"main_bat": "yes" if id(c) in keep else "no"} for c in calls]
