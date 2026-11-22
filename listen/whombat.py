"""Export a survey for Whombat, the open-source annotation tool (https://mbsantiago.github.io/whombat/).

Two files in AOEF 1.1.0, the exchange format of the `soundevent` library that Whombat imports:
  whombat_dataset.json       the recordings (import this first, with the survey folder as audio directory)
  whombat_annotations.json   an annotation project: one clip per bat pass, one box per measured call

What goes in, and what does not:
  * A species tag only where a person identified the pass. Listen's own suggestions are left out.
  * The species tag goes on the clip and on the calls of the main bat in it, not on echoes or a second bat.
  * Reviewed passes arrive in Whombat as completed tasks, the rest as open tasks with the call boxes drawn.
Ids are derived from the survey name, file and time, so exporting twice gives the same ids.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

import soundfile as sf

from . import __version__

AOEF_VERSION = "1.1.0"
_NS = uuid.UUID("6f1b0c5e-3d1a-5b7e-9c55-2a7d1f0b6e11")
PAD_HZ = 1000.0    # a call's box follows its measured ridge; this margin keeps a flat (CF) call from being a line
PAD_S = 0.0005


def _id(*parts) -> str:
    return str(uuid.uuid5(_NS, "\x1f".join(str(p) for p in parts)))


def label_tag(label: str | None) -> tuple[str, str] | None:
    """The tag for an expert's label: a binomial is a species, a single word a genus. 'Unknown' gets no tag."""
    label = (label or "").strip()
    if not label or label.lower().startswith("unknown"):
        return None
    return ("species", label) if len(label.split()) >= 2 else ("genus", label)


def build(survey) -> tuple[dict, dict]:
    """(dataset, annotation project) as plain dictionaries in AOEF."""
    name = survey.folder.name
    now = datetime.now().isoformat(timespec="seconds")
    te = survey.time_expansion or 1
    tags: dict[tuple[str, str], int] = {}

    def tag_id(kv: tuple[str, str]) -> int:
        return tags.setdefault(kv, len(tags))

    recordings, clips, events, event_notes, clip_notes, tasks = {}, [], [], [], [], []
    for p in survey.passes:
        rel = p["file"]
        posix = Path(rel).as_posix()
        if rel not in recordings:
            info = sf.info(survey.folder / rel)
            rec = {"uuid": _id(name, "recording", posix), "path": posix,
                   # as soundevent defines them: the real duration and sample rate, not the slowed file's
                   "duration": round(info.frames / info.samplerate / te, 6), "channels": info.channels,
                   "samplerate": int(info.samplerate * te)}
            if te != 1:
                rec["time_expansion"] = float(te)
            meta = survey.files_meta.get(rel, {})
            if meta.get("time"):
                rec["date"], rec["time"] = meta["time"][:10], meta["time"][11:19]
            if "lat" in meta:
                rec["latitude"], rec["longitude"] = meta["lat"], meta["lon"]
            recordings[rel] = rec
        rec = recordings[rel]
        start, end = max(0.0, float(p["start"])), min(float(p["end"]), rec["duration"])
        clip = {"uuid": _id(name, "clip", posix, p["start"]), "recording": rec["uuid"],
                "start_time": round(start, 6), "end_time": round(end, 6)}
        clips.append(clip)
        kv = label_tag(p["label"])
        ann_ids = []
        for n, c in enumerate(p.get("calls") or []):
            t0 = start + float(c["t_start"])
            t1 = t0 + float(c["duration_ms"]) / 1000
            box = [round(max(0.0, t0 - PAD_S), 6), max(0.0, float(c["f_min_khz"]) * 1000 - PAD_HZ),
                   round(min(rec["duration"], t1 + PAD_S), 6), min(rec["samplerate"] / 2, float(c["f_max_khz"]) * 1000 + PAD_HZ)]
            ev = {"uuid": _id(name, "event", posix, p["start"], n), "recording": rec["uuid"],
                  "geometry": {"type": "BoundingBox", "coordinates": box}}
            events.append(ev)
            ann = {"uuid": _id(name, "event-annotation", posix, p["start"], n), "sound_event": ev["uuid"]}
            if kv and c.get("main_bat") == "yes":
                ann["tags"] = [tag_id(kv)]
            event_notes.append(ann)
            ann_ids.append(ann["uuid"])
        ca = {"uuid": _id(name, "clip-annotation", posix, p["start"]), "clip": clip["uuid"], "sound_events": ann_ids}
        if kv:
            ca["tags"] = [tag_id(kv)]
        elif p["label"]:   # reviewed, but the expert could not name it
            ca["notes"] = [{"uuid": _id(name, "note", posix, p["start"]),
                            "message": f"Reviewed in WildWard Listen as: {p['label']}"}]
        clip_notes.append(ca)
        tasks.append({"uuid": _id(name, "task", posix, p["start"]), "clip": clip["uuid"],
                      "status_badges": [{"state": "completed"}] if p["label"] else []})

    tag_list = [{"id": i, "key": k, "value": v} for (k, v), i in sorted(tags.items(), key=lambda kv: kv[1])]
    recs = list(recordings.values())
    made = f"Made by WildWard Listen {__version__} from the survey folder '{name}'."
    dataset = {"version": AOEF_VERSION, "created_on": now,
               "data": {"collection_type": "dataset", "uuid": _id(name, "dataset"), "name": name,
                        "description": made + " Recording paths are relative to the survey folder.",
                        "created_on": now, "recordings": recs}}
    project = {"version": AOEF_VERSION, "created_on": now,
               "data": {"collection_type": "annotation_project", "uuid": _id(name, "project"),
                        "name": f"{name} (WildWard Listen)",
                        "description": made + " One clip per bat pass, one box per measured call.",
                        "instructions": "Species and genus tags were given by a person in WildWard Listen. They sit on the "
                                        "clip and on the calls of the main bat in it. Boxes follow each call's measured "
                                        "ridge with a 1 kHz margin; calls after the 60th of a pass are not drawn. "
                                        "Clips without a tag have not been reviewed.",
                        "created_on": now, "tags": tag_list, "project_tags": [t["id"] for t in tag_list],
                        "recordings": recs, "clips": clips, "sound_events": events,
                        "sound_event_annotations": event_notes, "clip_annotations": clip_notes, "tasks": tasks}}
    return dataset, project


def export(survey) -> dict:
    dataset, project = build(survey)
    d_path, p_path = survey.dir / "whombat_dataset.json", survey.dir / "whombat_annotations.json"
    d_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf8")
    p_path.write_text(json.dumps(project, ensure_ascii=False, indent=1), encoding="utf8")
    data = project["data"]
    return {"dataset": str(d_path), "annotations": str(p_path), "recordings": len(data["recordings"]),
            "clips": len(data["clips"]), "sound_events": len(data["sound_events"]),
            "tagged_clips": sum(1 for c in data["clip_annotations"] if c.get("tags"))}
