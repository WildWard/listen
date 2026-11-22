"""Write GUANO metadata: copies of labelled recordings that carry the expert's identification inside the file.

GUANO is the open metadata standard for bat recordings (https://github.com/riggsd/guano-spec): a 'guan' chunk
of "Key: value" text lines in the WAV file. Listen already reads it (metadata.py). This module writes it, so a
reviewed recording becomes a documented reference call that any GUANO-aware program can read.

Rules kept here:
  * The original recording is never changed. A copy is written, with the audio bytes copied as they are.
  * Every field already in the file is kept, including fields this program does not know.
  * Every other chunk of the WAV file (for example AudioMoth's comment) is kept.
"""
import os
import struct
from collections import Counter
from pathlib import Path

from . import __version__

VERSION_KEY = "GUANO|Version"
MULTILINE = {"Note"}                      # fields whose line breaks are written as the two characters \n
MAX_RIFF = 0xFFFFFFFF
_BLOCK = 1 << 20


def parse(text: str) -> dict[str, str]:
    """Fields of one GUANO block, in the order they appear. Keys are case-sensitive, as the standard says."""
    out = {}
    for line in text.lstrip("﻿").split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k:
            out[k] = v.replace("\\n", "\n") if k in MULTILINE else v
    return out


def serialise(fields: dict[str, str]) -> bytes:
    """One GUANO block as bytes: version first, then the rest of the GUANO namespace, then everything else
    in the order given. UTF-8, lines end with a line feed, padded to an even length."""
    f = {k: str(v) for k, v in fields.items() if v is not None and str(v) != ""}
    f[VERSION_KEY] = f.get(VERSION_KEY) or "1.0"
    keys = [VERSION_KEY] + [k for k in f if k.startswith("GUANO|") and k != VERSION_KEY] \
        + [k for k in f if not k.startswith("GUANO|")]
    lines = []
    for k in keys:
        v = f[k].replace("\r\n", "\n").replace("\r", "\n")
        v = v.replace("\n", "\\n") if k in MULTILINE else " ".join(v.split("\n"))
        lines.append(f"{k}: {v}")
    body = "\n".join(lines).encode("utf8")
    return body + b"\n" if len(body) % 2 else body


def _layout(f, size: int) -> list[tuple[bytes, int, int]]:
    """(chunk id, where its body starts, body length) for every chunk of a WAV file."""
    f.seek(0)
    head = f.read(12)
    if len(head) < 12 or head[8:12] != b"WAVE" or head[:4] != b"RIFF":
        raise ValueError("not a plain WAV file (RF64 and other containers are not supported)")
    out, pos = [], 12
    while pos + 8 <= size:
        f.seek(pos)
        cid, n = struct.unpack("<4sI", f.read(8))
        start = pos + 8
        n = min(n, size - start)          # a recorder that lost power can leave a length that runs past the end
        out.append((cid, start, n))
        pos = start + n + (n & 1)
    return out


def read_fields(path: Path) -> dict[str, str]:
    """Every GUANO field in a file. If software added a second block, its values win."""
    path = Path(path)
    fields = {}
    with open(path, "rb") as f:
        for cid, start, n in _layout(f, os.path.getsize(path)):
            if cid == b"guan":
                f.seek(start)
                fields |= parse(f.read(n).decode("utf8", "replace"))
    return fields


def write_copy(src: Path, dst: Path, updates: dict[str, str | None]) -> dict[str, str]:
    """Copy src to dst with its GUANO fields changed by `updates` (a value of None removes a field).
    Returns the fields written. The audio and all other chunks are copied byte for byte."""
    src, dst = Path(src), Path(dst)
    if dst.exists() and os.path.samefile(src, dst):
        raise ValueError("refusing to write over the original recording")
    size = os.path.getsize(src)
    with open(src, "rb") as f:
        layout = _layout(f, size)
        if not any(cid == b"data" for cid, _, _ in layout):
            raise ValueError("no audio data found in the file")
        fields = {}
        for cid, start, n in layout:
            if cid == b"guan":
                f.seek(start)
                fields |= parse(f.read(n).decode("utf8", "replace"))
        for k, v in updates.items():
            if v is None:
                fields.pop(k, None)
            else:
                fields[k] = str(v)
        block = serialise(fields)
        keep = [(cid, start, n) for cid, start, n in layout if cid != b"guan"]
        total = 12 + sum(8 + n + (n & 1) for _, _, n in keep) + 8 + len(block)
        if total - 8 > MAX_RIFF:
            raise ValueError("file is too large for a plain WAV file")
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".part")
        try:
            with open(tmp, "wb") as out:
                out.write(b"RIFF" + struct.pack("<I", total - 8) + b"WAVE")
                for cid, start, n in keep:
                    out.write(struct.pack("<4sI", cid, n))
                    f.seek(start)
                    left = n
                    while left:
                        buf = f.read(min(_BLOCK, left))
                        if not buf:
                            raise ValueError("file ended early while copying")
                        out.write(buf)
                        left -= len(buf)
                    if n & 1:
                        out.write(b"\x00")
                out.write(struct.pack("<4sI", b"guan", len(block)) + block)
            os.replace(tmp, dst)
        finally:
            if tmp.exists():
                tmp.unlink()
    return parse(block.decode("utf8"))


def _by_count(names) -> str:
    """Names joined the GUANO way: comma-separated, the most frequent (the dominant species) first."""
    return ", ".join(n for n, _ in sorted(Counter(names).items(), key=lambda kv: (-kv[1], kv[0])))


def fields_for(survey, rel: str, existing: dict[str, str], sure: float = 0.7) -> dict[str, str] | None:
    """The GUANO fields Listen adds to one recording, or None when no pass in it has been identified by a person.
    Fields the detector already wrote (time, position, device) are left as they are."""
    passes = [p for p in survey.passes if p["file"] == rel]
    manual = [p["label"] for p in passes if p["label"] and not p["label"].lower().startswith("unknown")]
    if not manual:
        return None
    auto = [p["suggestion"] for p in passes
            if not p["label"] and p.get("suggestion") and (p.get("confidence") or 0) >= sure]
    meta = survey.files_meta.get(rel, {})
    ctx = survey.context_for(rel)
    up = {"Species Manual ID": _by_count(manual)}
    if auto:
        up["Species Auto ID"] = _by_count(auto)
    if "Timestamp" not in existing and meta.get("time"):
        up["Timestamp"] = meta["time"]
    if "Loc Position" not in existing and "lat" in meta:
        up["Loc Position"] = f"{meta['lat']:.6f} {meta['lon']:.6f}"
    if "TE" not in existing and survey.time_expansion != 1:
        up["TE"] = str(int(survey.time_expansion))
    if "Original Filename" not in existing:
        up["Original Filename"] = Path(rel).name
    if ctx.get("method"):   # GUANO's own example uses tags such as "hand-release"
        tags = [t.strip() for t in existing.get("Tags", "").split(",") if t.strip()]
        tag = ctx["method"].replace(" ", "-")
        if tag not in tags:
            up["Tags"] = ", ".join(tags + [tag])
    up["WildWard|Software"] = f"WildWard Listen {__version__}"
    up["WildWard|Passes"] = str(len(passes))
    up["WildWard|Reviewed Passes"] = str(sum(1 for p in passes if p["label"]))
    for key, name in (("habitat", "Habitat"), ("method", "Recording Method"), ("height_m", "Microphone Height m")):
        if ctx.get(key) is not None:
            up[f"WildWard|{name}"] = str(ctx[key])
    return up


def export_labelled(survey) -> dict:
    """Copies of every recording with at least one identified pass, into <survey>/.wildward/guano/, with the
    identification written as GUANO. Recordings nobody has reviewed are left out: a model's guess alone
    should not travel inside a file as if it were an identification."""
    out_dir = survey.dir / "guano"
    written, skipped = [], []
    for rel in sorted({p["file"] for p in survey.passes}):
        src = survey.folder / rel
        try:
            up = fields_for(survey, rel, read_fields(src))
            if up is None:
                continue
            write_copy(src, out_dir / rel, up)
            written.append(rel)
        except (OSError, ValueError) as e:
            skipped.append({"file": rel, "reason": str(e)})
    return {"folder": str(out_dir), "files": len(written), "skipped": skipped}
