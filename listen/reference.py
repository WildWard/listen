"""A reference library: identified recordings that teach Listen species before any review.

Layout: one sub-folder per species (or genus), named exactly as it should appear,
for example  My calls/Hipposideros larvatus/*.wav. Files may be real time or time-expanded;
set the factor per library, or put a file named te.txt containing e.g. 16 in a species folder.

The library is embedded once and cached in <library>/.wildward-reference.npz, so loading
it again is instant. Nothing leaves the computer.
"""
import json
from pathlib import Path

import numpy as np

from . import calls as callmod, detect, embed

CACHE = ".wildward-reference.npz"


def _te_for(folder: Path, default: int) -> int:
    f = folder / "te.txt"
    try:
        return int(f.read_text().strip()) if f.exists() else default
    except ValueError:
        return default


def build(library: Path, time_expansion: int = 1, progress=print, max_passes_per_file: int = 3) -> dict:
    """Embed the loudest passes of every reference recording. Returns {'X', 'y', 'files', 'species'}."""
    library = Path(library)
    cache = library / CACHE
    species_dirs = sorted(d for d in library.iterdir() if d.is_dir() and not d.name.startswith("."))
    signature = json.dumps([(d.name, sorted(p.name for p in d.glob("*.[wW][aA][vV]"))) for d in species_dirs] + [time_expansion, "v2"])
    if cache.exists():
        z = np.load(cache, allow_pickle=False)
        if str(z["signature"]) == signature:
            progress(f"Reference library loaded from cache: {len(set(z['y']))} species")
            return {"X": z["X"], "F": z["F"], "y": z["y"], "files": z["files"], "species": sorted(set(z["y"].tolist()))}
    windows, owner, labels, files, feats, skipped = [], [], [], [], [], 0
    for d in species_dirs:
        te = _te_for(d, time_expansion)
        for f in sorted(d.glob("*.[wW][aA][vV]")):
            try:
                x = detect.load(f, te)
            except Exception:
                skipped += 1
                continue
            for p in sorted(detect.find_passes(x, f.name), key=lambda p: -p.snr_db)[:max_passes_per_file]:
                for w in detect.pass_windows(x, p):   # same windows as a survey pass, so embeddings compare
                    windows.append(w)
                    owner.append(len(labels))
                labels.append(d.name)
                files.append(f"{d.name}/{f.name}")
                clip = x[int(p.start * detect.SR): int(p.end * detect.SR)]
                feats.append(callmod.feature_vector(callmod.summarise(callmod.measure_calls(clip))))
        progress(f"reference: read {d.name}")
    if not windows:
        raise ValueError("No bat calls found in the reference library. Check the folder layout and time-expansion factor.")
    progress(f"reference: listening to {len(windows)} call windows")
    W = embed.embed(np.stack(windows), progress=lambda a, b: progress(f"reference: embedded {a}/{b}"))
    owner = np.array(owner)
    X = np.stack([W[owner == i].mean(axis=0) for i in range(len(labels))])   # one vector per pass
    y, files, F = np.array(labels), np.array(files), np.stack(feats)
    np.savez_compressed(cache, X=X, F=F, y=y, files=files, signature=np.array(signature))
    progress(f"Reference library ready: {len(set(labels))} species, {len(labels)} passes, {skipped} files skipped")
    return {"X": X, "F": F, "y": y, "files": files, "species": sorted(set(labels))}
