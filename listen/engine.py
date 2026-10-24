"""A survey: a folder of recordings, the passes found in them, clusters, labels and suggestions.

Everything is saved in <folder>/.wildward/ so work survives closing the app:
  survey.json      passes, clusters, labels, suggestions
  embeddings.npy   one Perch embedding per pass (mean of its windows)
  media/           spectrogram PNGs and slowed WAVs per pass
"""
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import calls as callmod, detect, embed, media, timestamps

AUDIO_EXT = {".wav", ".WAV"}


class Survey:
    def __init__(self, folder: Path, time_expansion: int = 1):
        self.folder = Path(folder)
        self.dir = self.folder / ".wildward"
        self.media = self.dir / "media"
        self.state_path = self.dir / "survey.json"
        self.time_expansion = time_expansion
        self.passes: list[dict] = []
        self.emb = np.zeros((0, 1536), np.float32)
        self.skipped: list[dict] = []
        if self.state_path.exists():
            self._load()

    # ---------- persistence ----------
    def _load(self) -> None:
        s = json.loads(self.state_path.read_text(encoding="utf8"))
        self.passes, self.skipped = s["passes"], s.get("skipped", [])
        self.time_expansion = s.get("time_expansion", self.time_expansion)
        self.emb = np.load(self.dir / "embeddings.npy")

    def save(self) -> None:
        self.dir.mkdir(exist_ok=True)
        self.state_path.write_text(json.dumps({"passes": self.passes, "skipped": self.skipped,
                                               "time_expansion": self.time_expansion, "saved": time.time()},
                                              indent=1), encoding="utf8")
        np.save(self.dir / "embeddings.npy", self.emb)

    # ---------- processing ----------
    def scan(self, progress=print) -> None:
        """Find passes in every recording, make media, embed with Perch, cluster."""
        files = sorted(p for p in self.folder.rglob("*") if p.suffix in AUDIO_EXT and ".wildward" not in p.parts)
        self.media.mkdir(parents=True, exist_ok=True)
        passes, windows, owner = [], [], []
        for n, f in enumerate(files, 1):
            rel = str(f.relative_to(self.folder))
            try:
                x = detect.load(f, self.time_expansion)
            except Exception as e:  # unreadable or wrong rate: report it, keep going
                self.skipped.append({"file": rel, "reason": str(e)})
                continue
            file_time = timestamps.recording_start(f)
            for p in detect.find_passes(x, rel):
                pid = len(passes)
                clip = x[int(p.start * detect.SR): int(p.end * detect.SR)]
                media.spectrogram_png(clip[: detect.SR * 2], self.media / f"{pid}.png")
                media.slowed_wav(clip[: detect.SR * 2], self.media / f"{pid}.wav")
                measured = callmod.measure_calls(clip)
                summary = callmod.summarise(measured)
                d = asdict(p) | {"id": pid, "label": None, "suggestion": None, "confidence": None, "cluster": None,
                                 "time": timestamps.at(file_time, p.start), "measures": summary,
                                 "sound": callmod.sound_type(summary),
                                 "calls": callmod.as_rows(measured, callmod.dominant(measured) if measured else [])[:60]}
                passes.append(d)
                for w in detect.pass_windows(x, p):
                    windows.append(w)
                    owner.append(pid)
            progress(f"read {n}/{len(files)} files, {len(passes)} passes")
        self.passes = passes
        if windows:
            progress(f"listening to {len(windows)} call windows with Perch")
            W = embed.embed(np.stack(windows), progress=lambda a, b: progress(f"embedded {a}/{b}"))
            owner = np.array(owner)
            self.emb = np.stack([W[owner == i].mean(axis=0) for i in range(len(passes))])
        self.cluster()
        self.save()

    def remake_media(self) -> None:
        """Redraw spectrograms and audio clips from the recordings, without re-running detection."""
        self.media.mkdir(parents=True, exist_ok=True)
        by_file = {}
        for p in self.passes:
            by_file.setdefault(p["file"], []).append(p)
        for rel, ps in by_file.items():
            x = detect.load(self.folder / rel, self.time_expansion)
            for p in ps:
                clip = x[int(p["start"] * detect.SR): int(p["end"] * detect.SR)][: detect.SR * 2]
                media.spectrogram_png(clip, self.media / f"{p['id']}.png")
                media.slowed_wav(clip, self.media / f"{p['id']}.wav")

    def cluster(self, threshold: float = 0.25) -> None:
        if len(self.passes) < 2:
            for p in self.passes:
                p["cluster"] = 0
            return
        X = self.emb / (np.linalg.norm(self.emb, axis=1, keepdims=True) + 1e-9)
        ids = AgglomerativeClustering(n_clusters=None, distance_threshold=threshold, metric="cosine",
                                      linkage="average").fit_predict(X)
        # number clusters by size, biggest first, so the review starts where the most work is
        order = {c: i for i, (c, _) in enumerate(sorted(zip(*np.unique(ids, return_counts=True)), key=lambda t: -t[1]))}
        for p, c in zip(self.passes, ids):
            p["cluster"] = int(order[c])

    # ---------- review ----------
    def label(self, pass_ids: list[int], label: str | None) -> None:
        for i in pass_ids:
            self.passes[i]["label"] = (label or "").strip() or None
        self.suggest()
        self.save()

    def suggest(self) -> None:
        """Train on the expert's confirmed labels; suggest a species for everything else."""
        labelled = [p for p in self.passes if p["label"]]
        classes = {p["label"] for p in labelled}
        for p in self.passes:
            p["suggestion"], p["confidence"] = None, None
        if len(classes) < 2:
            return
        idx = np.array([p["id"] for p in labelled])
        y = np.array([p["label"] for p in labelled])
        clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1, class_weight="balanced"))
        clf.fit(self.emb[idx], y)
        todo = [p for p in self.passes if not p["label"]]
        if not todo:
            return
        proba = clf.predict_proba(self.emb[[p["id"] for p in todo]])
        for p, pr in zip(todo, proba):
            k = int(pr.argmax())
            p["suggestion"], p["confidence"] = str(clf.classes_[k]), round(float(pr[k]), 3)

    def summary(self) -> dict:
        clusters = {}
        for p in self.passes:
            c = clusters.setdefault(p["cluster"], {"id": p["cluster"], "passes": [], "labels": {}, "suggestions": {},
                                                   "sounds": {}, "conf": []})
            c["passes"].append(p["id"])
            sound = (p.get("sound") or {}).get("hint")
            if sound:
                c["sounds"][sound] = c["sounds"].get(sound, 0) + 1
            if p["label"]:
                c["labels"][p["label"]] = c["labels"].get(p["label"], 0) + 1
            elif p["suggestion"]:
                c["suggestions"][p["suggestion"]] = c["suggestions"].get(p["suggestion"], 0) + 1
                c["conf"].append(p["confidence"])
        for c in clusters.values():
            # review priority: groups the model is least sure about teach it the most, bigger groups save more clicks
            open_n = sum(1 for i in c["passes"] if not self.passes[i]["label"])
            unsure = 1 - (sum(c["conf"]) / len(c["conf"])) if c["conf"] else 1.0
            c["priority"] = round(unsure * (open_n ** 0.5), 3)
            del c["conf"]
        activity = {}
        for p in self.passes:
            h = (p.get("time") or {}).get("hour")
            if h is not None:
                who = p["label"] or (p.get("sound") or {}).get("hint", "unclear").split(" (")[0].replace("typical of ", "")
                activity.setdefault(h, {})
                activity[h][who] = activity[h].get(who, 0) + 1
        sources = {(p.get("time") or {}).get("source") for p in self.passes}
        return {"folder": str(self.folder), "time_expansion": self.time_expansion,
                "passes": [{k: v for k, v in p.items() if k != "calls"} for p in self.passes],
                "clusters": sorted(clusters.values(), key=lambda c: c["id"]), "skipped": self.skipped,
                "activity": activity, "time_source": sorted(s for s in sources if s)}
