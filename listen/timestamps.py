"""When was each pass recorded? Read it from common detector file names, else the file's date."""
import re
from datetime import datetime, timedelta
from pathlib import Path

# AudioMoth: 20261024_213000.WAV ; Song Meter: SM4_20261024_213000.wav ; Batlogger-style: 2026-10-24_21-30-00
_PATTERNS = [
    (re.compile(r"(\d{8})[_T-](\d{6})"), "%Y%m%d%H%M%S"),
    (re.compile(r"(\d{4}-\d{2}-\d{2})[ _T](\d{2}-\d{2}-\d{2})"), "%Y-%m-%d%H-%M-%S"),
]


def recording_start(path: Path) -> tuple[str | None, str]:
    """(ISO time or None, source) where source is 'filename', 'file date' or 'unknown'."""
    for rx, fmt in _PATTERNS:
        m = rx.search(path.stem)
        if m:
            try:
                return datetime.strptime(m.group(1) + m.group(2), fmt).isoformat(), "filename"
            except ValueError:
                pass
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat(), "file date"
    except OSError:
        return None, "unknown"


def at(file_time: tuple[str | None, str], offset_s: float) -> dict:
    iso, source = file_time
    if not iso:
        return {"iso": None, "hour": None, "source": source}
    t = datetime.fromisoformat(iso) + timedelta(seconds=offset_s)
    return {"iso": t.isoformat(timespec="seconds"), "hour": t.hour, "source": source}
