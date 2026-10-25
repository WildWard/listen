"""Detector metadata stored inside WAV files: where, when and with what a recording was made.

Reads two common formats, without loading any audio:
  GUANO   the open bat-acoustics metadata standard (Wildlife Acoustics Song Meter, Pettersson,
          Elekon and others), a 'guan' chunk of "Key: value" lines, e.g. "Loc Position: 5.43 100.29"
  AudioMoth the comment AudioMoth firmware writes, e.g. "Recorded at 21:30:00 24/10/2026 (UTC+7)
          by AudioMoth 24E144085F256B7C ..."
Times are kept as the detector's local clock (time zone dropped), which is what "hour of the night" needs.
"""
import re
import struct
from datetime import datetime
from pathlib import Path

_AUDIOMOTH = re.compile(r"Recorded at (\d{2}:\d{2}:\d{2}) (\d{2}/\d{2}/\d{4})(?: \(UTC([+-]\d+(?::\d+)?)?\))? by AudioMoth ([0-9A-F]+)")


def _chunks(path: Path, limit: int = 64):
    """Yield (id, bytes) for the RIFF chunks of a WAV file, skipping the audio data itself."""
    with open(path, "rb") as f:
        head = f.read(12)
        if len(head) < 12 or head[:4] != b"RIFF" or head[8:12] != b"WAVE":
            return
        for _ in range(limit):
            h = f.read(8)
            if len(h) < 8:
                return
            cid, size = h[:4], struct.unpack("<I", h[4:])[0]
            if cid == b"data":
                f.seek(size + (size & 1), 1)
                continue
            body = f.read(min(size, 1 << 20))
            if size > len(body):
                f.seek(size - len(body), 1)
            if size & 1:
                f.seek(1, 1)
            yield cid, body


def _guano(text: str) -> dict:
    kv = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            kv[k.strip()] = v.strip()
    out = {"format": "GUANO"}
    if "Loc Position" in kv:
        try:
            lat, lon = (float(x) for x in kv["Loc Position"].replace(",", " ").split()[:2])
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                out["lat"], out["lon"] = lat, lon
        except ValueError:
            pass
    if "Timestamp" in kv:
        try:  # ISO 8601, possibly with a UTC offset: keep the local wall clock
            out["time"] = datetime.fromisoformat(kv["Timestamp"].replace("Z", "+00:00")).replace(tzinfo=None).isoformat()
        except ValueError:
            pass
    device = " ".join(x for x in (kv.get("Make"), kv.get("Model")) if x)
    if device:
        out["device"] = device
    if kv.get("Serial"):
        out["serial"] = kv["Serial"]
    if kv.get("TE"):
        try:
            out["time_expansion"] = int(float(kv["TE"]))
        except ValueError:
            pass
    return out


def read(path: Path) -> dict:
    """Metadata found in the file (possibly empty): time, lat, lon, device, serial, time_expansion, format."""
    out = {}
    try:
        for cid, body in _chunks(Path(path)):
            if cid == b"guan":   # software may add a second GUANO block when it edits a file: later values win
                out |= _guano(body.decode("utf-8", "replace").lstrip("﻿"))
            elif cid == b"LIST" and body[:4] == b"INFO":
                m = _AUDIOMOTH.search(body.decode("latin-1"))
                if m:
                    t = datetime.strptime(f"{m.group(2)} {m.group(1)}", "%d/%m/%Y %H:%M:%S")
                    out = {"format": "AudioMoth", "time": t.isoformat(), "device": "AudioMoth", "serial": m.group(4)} | out
    except OSError:
        pass
    return out if len(out) > 1 else {}   # a bare "format" with nothing useful counts as no metadata
