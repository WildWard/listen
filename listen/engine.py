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
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from . import calls as callmod, detect, embed, media, reference as refmod, timestamps

AUDIO_EXT = {".wav", ".WAV"}
UNUSUAL_GAP = 0.05   # flag constant-frequency calls at least 5% from every known species' frequency
MIN_CF_KHZ = 25.0
SURE = 0.7           # name a species at 70%+ confidence; below that, fall back to a confident genus


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
        self.reference_path: str | None = None
        self.reference_te = 1
        self.reference: dict | None = None
        if self.state_path.exists():
            self._load()

    # ---------- persistence ----------
    def _load(self) -> None:
        s = json.loads(self.state_path.read_text(encoding="utf8"))
        self.passes, self.skipped = s["passes"], s.get("skipped", [])
        self.time_expansion = s.get("time_expansion", self.time_expansion)
        self.emb = np.load(self.dir / "embeddings.npy")
        self.reference_path, self.reference_te = s.get("reference_path"), s.get("reference_te", 1)
        if self.reference_path and Path(self.reference_path).is_dir():
            try:  # cached, so this is quick
                self.reference = refmod.build(Path(self.reference_path), self.reference_te, progress=lambda m: None)
            except Exception:
                self.reference = None
        self.suggest()   # refresh suggestions and flags: surveys saved by older versions lack genus and unusual fields

    def save(self) -> None:
        self.dir.mkdir(exist_ok=True)
        self.state_path.write_text(json.dumps({"passes": self.passes, "skipped": self.skipped,
                                               "time_expansion": self.time_expansion, "reference_path": self.reference_path,
                                               "reference_te": self.reference_te, "saved": time.time()},
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
        self.flag_unusual()
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

    def set_reference(self, library: Path | None, te: int = 1, progress=print) -> None:
        """Learn species from a reference library (or forget it with None), then refresh suggestions."""
        if library is None:
            self.reference, self.reference_path = None, None
        else:
            library = Path(library).resolve()   # absolute, so the survey finds it again from anywhere
            self.reference = refmod.build(library, te, progress=progress)
            self.reference_path, self.reference_te = str(library), te
        self.suggest()
        self.save()

    def known_species(self) -> list[str]:
        ref = list(self.reference["species"]) if self.reference else []
        return sorted(set(ref) | {p["label"] for p in self.passes if p["label"]})

    def suggest(self) -> None:
        """Train on the reference library plus the expert's confirmed labels; suggest a species for the rest.
        Labels from this survey count three times as much as reference calls: they come from this site."""
        labelled = [p for p in self.passes if p["label"]]
        # features: Perch embedding plus the measured call parameters (weighted x3 so frequency counts)
        own = np.hstack([self.emb, np.repeat(np.stack([callmod.feature_vector(p.get("measures") or {}) for p in self.passes]), 3, axis=1)])             if self.passes else np.zeros((0, 1536 + 21), np.float32)
        X_parts, y_parts, w_parts = [], [], []
        if self.reference is not None and "F" in self.reference:
            X_parts.append(np.hstack([self.reference["X"], np.repeat(self.reference["F"], 3, axis=1)]))
            y_parts.append(self.reference["y"]); w_parts.append(np.ones(len(self.reference["y"])))
        if labelled:
            idx = np.array([p["id"] for p in labelled])
            X_parts.append(own[idx]); y_parts.append(np.array([p["label"] for p in labelled]))
            w_parts.append(np.full(len(idx), 3.0))
        for p in self.passes:
            p["suggestion"], p["confidence"], p["genus"], p["genus_confidence"] = None, None, None, None
        self.flag_unusual()
        if not X_parts:
            return
        X, y, w = np.concatenate(X_parts), np.concatenate(y_parts), np.concatenate(w_parts)
        if len(set(y)) < 2:
            return
        clf = make_pipeline(SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler(),
                            LogisticRegression(max_iter=4000, C=0.05, class_weight="balanced"))
        clf.fit(X, y, logisticregression__sample_weight=w)
        todo = [p for p in self.passes if not p["label"]]
        if not todo:
            return
        proba = clf.predict_proba(own[[p["id"] for p in todo]])
        # genus of each class: the first word of a binomial; one-word labels (genus or "Unknown") stand alone
        genus_of = np.array([c.split()[0] for c in clf.classes_])
        genera = np.unique(genus_of)
        for p, pr in zip(todo, proba):
            k = int(pr.argmax())
            p["suggestion"], p["confidence"] = str(clf.classes_[k]), round(float(pr[k]), 3)
            # when the species is uncertain but the genus isn't, say the genus: at new sites this was
            # right 94% of the time vs 80% for confident species calls (batlab accuracy_eval)
            gp = np.array([pr[genus_of == g].sum() for g in genera])
            g = int(gp.argmax())
            p["genus"], p["genus_confidence"] = ((str(genera[g]), round(float(gp[g]), 3))
                                                 if pr[k] < SURE and gp[g] >= SURE else (None, None))

    def known_frequencies(self) -> list[tuple[str, float]]:
        """Frequency bands that known constant-frequency species (horseshoe and leaf-nosed bats) call in,
        from the reference library and this survey's labels. Each species' passes are chained into bands
        (neighbours within 5%); a band counts when it holds at least a third of that species' passes, so
        stray calls in a reference file don't make a frequency "known", and a species with two bands keeps both."""
        f_by = {}
        if self.reference is not None and "F" in self.reference:
            F = self.reference["F"]
            for sp, fc, cf in zip(self.reference["y"], F[:, 0], F[:, -1]):
                if cf == 1 and np.isfinite(fc):
                    f_by.setdefault(str(sp), []).append(float(fc))
        for p in self.passes:
            m = p.get("measures") or {}
            if p["label"] and m.get("shape") in ("CF", "CF-FM"):
                f_by.setdefault(p["label"], []).append(float(m["f_char_khz"]))
        bands = []
        for sp, v in f_by.items():
            v = sorted(v)
            groups = [[v[0]]]
            for f in v[1:]:
                (groups[-1].append(f) if f - groups[-1][-1] <= 0.05 * f else groups.append([f]))
            # a single reference pass still counts: it is all the library knows about that species
            keep = [g for g in groups if len(g) >= max(2, len(v) / 3)] or [max(groups, key=len)]
            bands += [(sp, float(np.median(g))) for g in keep]
        return bands

    def flag_unusual(self, min_gap: float = UNUSUAL_GAP) -> None:
        """Flag constant-frequency passes whose call frequency is far from every known species.
        Such a pass may be a species missing from the library, or one worth a closer look: several
        cryptic South-East Asian bats were first noticed by calling at an unexpected frequency.
        See batlab FINDINGS, Test 8, for how often this is right."""
        known = self.known_frequencies()
        for p in self.passes:
            p["unusual"] = None
            m = p.get("measures") or {}
            if not known or p["label"] or m.get("shape") not in ("CF", "CF-FM") or m.get("n_calls", 0) < 3                     or (p.get("sound") or {}).get("type") == "unclear":
                continue
            fc = float(m["f_char_khz"])
            if fc < MIN_CF_KHZ:   # no constant-frequency bat calls this low; a flat tone here is noise or insects
                continue
            nearest, nf = min(known, key=lambda k: abs(k[1] - fc))
            gap = abs(nf - fc) / nf
            if gap >= min_gap:
                p["unusual"] = {"f_khz": round(fc, 1), "nearest": nearest, "nearest_khz": round(nf, 1), "gap": round(gap, 3)}

    def summary(self) -> dict:
        clusters = {}
        for p in self.passes:
            c = clusters.setdefault(p["cluster"], {"id": p["cluster"], "passes": [], "labels": {}, "suggestions": {},
                                                   "sounds": {}, "conf": [], "unusual": 0, "unusual_khz": []})
            c["passes"].append(p["id"])
            sound = (p.get("sound") or {}).get("hint")
            if sound:
                c["sounds"][sound] = c["sounds"].get(sound, 0) + 1
            if p.get("unusual"):
                c["unusual"] += 1
                c["unusual_khz"].append(p["unusual"]["f_khz"])
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
            c["unusual_khz"] = round(float(np.median(c["unusual_khz"])), 1) if c["unusual_khz"] else None
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
                "activity": activity, "time_source": sorted(s for s in sources if s),
                "known_species": self.known_species(),
                "reference": {"path": self.reference_path, "species": len(self.reference["species"]),
                              "passes": int(len(self.reference["y"]))} if self.reference else None}
