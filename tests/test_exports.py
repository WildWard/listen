"""Tests for the GUANO writer and the Whombat export. They make their own small WAV files, no recordings needed.

Run with:  python -m pytest tests      or      python tests/test_exports.py
"""
import json
import struct
import sys
import tempfile
import uuid
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from listen import guano, metadata, whombat  # noqa: E402
from listen.engine import Survey  # noqa: E402

SR = 384_000
EXISTING = ("GUANO|Version: 1.0\nTimestamp: 2026-07-04T21:30:00+02:00\nLoc Position: 47.5 19.04\n"
            "Make: Pettersson\nModel: D500X\nPET|Gain: 45\nNote: first line\\nsecond line")


def chunk(cid: bytes, body: bytes) -> bytes:
    return cid + struct.pack("<I", len(body)) + body + (b"\x00" if len(body) % 2 else b"")


def add_chunks(path: Path, chunks: list[bytes], before_data: bool = False) -> None:
    """Add RIFF chunks to a WAV file made by soundfile, after the audio or in front of it."""
    raw = path.read_bytes()
    extra = b"".join(chunks)
    if before_data:
        at = raw.index(b"data")
        raw = raw[:at] + extra + raw[at:]
    else:
        raw += extra
    path.write_bytes(raw[:4] + struct.pack("<I", len(raw) - 8) + raw[8:])


def make_wav(path: Path, seconds: float = 0.5, guano_text: str | None = None, odd: bool = False) -> np.ndarray:
    n = int(SR * seconds) + (1 if odd else 0)
    x = (0.3 * np.sin(2 * np.pi * 45_000 * np.arange(n) / SR)).astype(np.float32)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, x, SR, subtype="PCM_16")
    if guano_text is not None:
        add_chunks(path, [chunk(b"guan", guano_text.encode("utf8"))])
    return sf.read(path, dtype="int16")[0]


def chunk_ids(path: Path) -> list[bytes]:
    with open(path, "rb") as f:
        return [cid for cid, _, _ in guano._layout(f, path.stat().st_size)]


def survey_with(folder: Path, passes: list[dict], te: int = 1) -> Survey:
    s = Survey(folder, te)
    s.dir.mkdir(exist_ok=True)
    s.passes = [{"id": i, "label": None, "suggestion": None, "confidence": None, "cluster": 0, "calls": []} | p
                for i, p in enumerate(passes)]
    return s


CALLS = [{"t_start": 0.010, "duration_ms": 4.0, "f_min_khz": 40.0, "f_max_khz": 80.0, "main_bat": "yes"},
         {"t_start": 0.100, "duration_ms": 30.0, "f_min_khz": 108.0, "f_max_khz": 108.0, "main_bat": "yes"},
         {"t_start": 0.150, "duration_ms": 3.0, "f_min_khz": 20.0, "f_max_khz": 25.0, "main_bat": "no"}]


# ---------- GUANO ----------

def test_copy_keeps_audio_and_every_existing_field():
    d = Path(tempfile.mkdtemp())
    audio = make_wav(d / "a.wav", guano_text=EXISTING)
    before = (d / "a.wav").read_bytes()
    out = guano.write_copy(d / "a.wav", d / "out" / "a.wav", {"Species Manual ID": "Myotis myotis"})
    assert (d / "a.wav").read_bytes() == before                      # the original is untouched
    assert np.array_equal(sf.read(d / "out" / "a.wav", dtype="int16")[0], audio)
    back = guano.read_fields(d / "out" / "a.wav")
    assert back == out and back["Species Manual ID"] == "Myotis myotis"
    for key, value in guano.parse(EXISTING).items():                 # nothing the detector wrote is lost
        assert back[key] == value, key
    assert back["Note"] == "first line\nsecond line"                 # multi-line notes survive
    assert chunk_ids(d / "out" / "a.wav").count(b"guan") == 1


def test_block_follows_the_standard():
    d = Path(tempfile.mkdtemp())
    make_wav(d / "a.wav", guano_text=EXISTING)
    guano.write_copy(d / "a.wav", d / "b.wav", {"Species Manual ID": "Nyctalus noctula, Myotis myotis", "User|Őrség": "ő"})
    raw = (d / "b.wav").read_bytes()
    assert struct.unpack("<I", raw[4:8])[0] == len(raw) - 8          # RIFF length is right
    at = raw.rindex(b"guan")
    size = struct.unpack("<I", raw[at + 4: at + 8])[0]
    block = raw[at + 8: at + 8 + size]
    assert size % 2 == 0 and at + 8 + size == len(raw)               # even length, and it is the last chunk
    text = block.decode("utf8")
    assert text.startswith("GUANO|Version: 1.0\n") and "\r" not in text
    assert "Note: first line\\nsecond line" in text                  # a line break inside a value is written as \n
    assert "User|Őrség: ő" in text                                   # UTF-8


def test_file_without_guano_and_with_other_chunks():
    d = Path(tempfile.mkdtemp())
    audio = make_wav(d / "moth.wav", odd=True)                       # odd number of bytes of audio: needs a pad byte
    text = b"Recorded at 21:30:00 24/10/2026 (UTC+7) by AudioMoth 24E144085F256B7C"
    comment = b"INFO" + chunk(b"ICMT", text)
    add_chunks(d / "moth.wav", [chunk(b"LIST", comment)], before_data=True)
    assert metadata.read(d / "moth.wav")["serial"] == "24E144085F256B7C"
    guano.write_copy(d / "moth.wav", d / "out.wav", {"Species Manual ID": "Hipposideros larvatus"})
    assert chunk_ids(d / "out.wav") == [b"fmt ", b"LIST", b"data", b"guan"]
    assert np.array_equal(sf.read(d / "out.wav", dtype="int16")[0], audio)
    m = metadata.read(d / "out.wav")                                 # Listen's own reader still sees both
    assert m["serial"] == "24E144085F256B7C" and m["time"] == "2026-10-24T21:30:00"
    assert guano.read_fields(d / "out.wav") == {"GUANO|Version": "1.0", "Species Manual ID": "Hipposideros larvatus"}


def test_second_write_replaces_and_can_remove():
    d = Path(tempfile.mkdtemp())
    make_wav(d / "a.wav", guano_text=EXISTING)
    guano.write_copy(d / "a.wav", d / "b.wav", {"Species Manual ID": "Myotis myotis"})
    guano.write_copy(d / "b.wav", d / "c.wav", {"Species Manual ID": "Myotis blythii", "PET|Gain": None})
    back = guano.read_fields(d / "c.wav")
    assert back["Species Manual ID"] == "Myotis blythii" and "PET|Gain" not in back
    assert chunk_ids(d / "c.wav").count(b"guan") == 1


def test_never_writes_over_the_original():
    d = Path(tempfile.mkdtemp())
    make_wav(d / "a.wav")
    before = (d / "a.wav").read_bytes()
    try:
        guano.write_copy(d / "a.wav", d / "a.wav", {"Species Manual ID": "x"})
        raise AssertionError("should have refused")
    except ValueError:
        pass
    assert (d / "a.wav").read_bytes() == before


def test_only_identified_recordings_are_exported():
    d = Path(tempfile.mkdtemp())
    for name in ("one.wav", "site/two.wav", "three.wav", "four.wav"):
        make_wav(d / name, guano_text=EXISTING if name == "one.wav" else None)
    s = survey_with(d, [
        {"file": "one.wav", "start": 0.0, "end": 0.2, "label": "Myotis myotis"},
        {"file": "one.wav", "start": 0.2, "end": 0.4, "label": "Myotis myotis"},
        {"file": "one.wav", "start": 0.4, "end": 0.5, "label": "Nyctalus noctula"},
        {"file": "one.wav", "start": 0.3, "end": 0.4, "suggestion": "Eptesicus serotinus", "confidence": 0.9},
        {"file": "one.wav", "start": 0.1, "end": 0.2, "suggestion": "Plecotus auritus", "confidence": 0.4},
        {"file": str(Path("site") / "two.wav"), "start": 0.0, "end": 0.2, "label": "Barbastella barbastellus"},
        {"file": "three.wav", "start": 0.0, "end": 0.2, "suggestion": "Myotis myotis", "confidence": 0.95},
        {"file": "four.wav", "start": 0.0, "end": 0.2, "label": "Unknown bat"},
    ])
    s.context = {"survey": {"habitat": "edge", "method": "hand release", "height_m": 2.0}, "sites": {}}
    res = guano.export_labelled(s)
    assert res["files"] == 2 and not res["skipped"]
    out = d / ".wildward" / "guano"
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*.wav")) == ["one.wav", "site/two.wav"]
    one = guano.read_fields(out / "one.wav")
    assert one["Species Manual ID"] == "Myotis myotis, Nyctalus noctula"     # the dominant species first
    assert one["Species Auto ID"] == "Eptesicus serotinus"                  # only confident suggestions, unreviewed passes
    assert one["Timestamp"] == "2026-07-04T21:30:00+02:00" and one["Loc Position"] == "47.5 19.04"   # the detector's own
    assert one["Tags"] == "hand-release" and one["WildWard|Habitat"] == "edge"
    assert one["WildWard|Passes"] == "5" and one["WildWard|Reviewed Passes"] == "3"
    two = guano.read_fields(out / "site" / "two.wav")
    assert two["Original Filename"] == "two.wav" and "Species Auto ID" not in two


# ---------- Whombat ----------

def project_for(te: int = 1):
    d = Path(tempfile.mkdtemp())
    make_wav(d / "night1" / "a.wav", guano_text=EXISTING)
    make_wav(d / "b.wav")
    a = str(Path("night1") / "a.wav")
    s = survey_with(d, [
        {"file": a, "start": 0.05, "end": 0.30, "label": "Rhinolophus hipposideros", "calls": CALLS},
        {"file": a, "start": 0.35, "end": 0.45, "suggestion": "Myotis myotis", "confidence": 0.99, "calls": CALLS[:1]},
        {"file": "b.wav", "start": 0.0, "end": 0.2, "label": "Myotis", "calls": []},
        {"file": "b.wav", "start": 0.2, "end": 0.9, "label": "Unknown bat", "calls": CALLS[:1]},
    ], te)
    s.files_meta = {a: metadata.read(d / a)}
    return s, whombat.build(s)


def test_whombat_references_all_resolve():
    s, (dataset, project) = project_for()
    p = project["data"]
    assert project["version"] == dataset["version"] == "1.1.0"
    assert p["collection_type"] == "annotation_project" and dataset["data"]["collection_type"] == "dataset"
    recs = {r["uuid"] for r in p["recordings"]}
    clips = {c["uuid"] for c in p["clips"]}
    events = {e["uuid"] for e in p["sound_events"]}
    anns = {a["uuid"] for a in p["sound_event_annotations"]}
    tags = {t["id"] for t in p["tags"]}
    every = [x["uuid"] for k in ("recordings", "clips", "sound_events", "sound_event_annotations", "clip_annotations", "tasks")
             for x in p[k]] + [p["uuid"]]
    assert len(every) == len(set(every)) and all(uuid.UUID(u) for u in every)
    assert all(c["recording"] in recs for c in p["clips"]) and all(e["recording"] in recs for e in p["sound_events"])
    assert all(a["sound_event"] in events for a in p["sound_event_annotations"])
    assert all(t["clip"] in clips for t in p["tasks"]) and len(p["tasks"]) == len(p["clips"]) == 4
    for ca in p["clip_annotations"]:
        assert ca["clip"] in clips and all(x in anns for x in ca["sound_events"]) and all(t in tags for t in ca.get("tags", []))
    assert all(t in tags for a in p["sound_event_annotations"] for t in a.get("tags", []))
    assert dataset["data"]["recordings"] == p["recordings"]
    json.dumps(project)                                               # plain JSON types only


def test_whombat_recordings_and_boxes():
    s, (_, project) = project_for()
    p = project["data"]
    rec = next(r for r in p["recordings"] if r["path"] == "night1/a.wav")    # forward slashes, relative to the survey folder
    assert rec["samplerate"] == SR and rec["channels"] == 1 and abs(rec["duration"] - 0.5) < 1e-6
    assert rec["date"] == "2026-07-04" and rec["time"] == "21:30:00" and rec["latitude"] == 47.5 and "time_expansion" not in rec
    fm, cf, other = (e["geometry"]["coordinates"] for e in p["sound_events"][:3])
    assert p["sound_events"][0]["geometry"]["type"] == "BoundingBox"
    assert abs(fm[0] - (0.05 + 0.010 - 0.0005)) < 1e-6 and abs(fm[2] - (0.05 + 0.010 + 0.004 + 0.0005)) < 1e-6   # seconds in the recording
    assert fm[1] == 39_000 and fm[3] == 81_000                               # hertz, with the 1 kHz margin
    assert cf[3] - cf[1] == 2_000                                            # a flat call still gets a box with height
    for box in (e["geometry"]["coordinates"] for e in p["sound_events"]):
        assert 0 <= box[0] < box[2] <= 0.5 + 1e-9 and 0 <= box[1] < box[3] <= SR / 2
    clip = p["clips"][3]                                                     # a pass that runs past the end of the file
    assert clip["end_time"] <= 0.5


def test_whombat_only_a_persons_labels_become_tags():
    s, (_, project) = project_for()
    p = project["data"]
    assert sorted((t["key"], t["value"]) for t in p["tags"]) == [("genus", "Myotis"), ("species", "Rhinolophus hipposideros")]
    assert "Myotis myotis" not in json.dumps(project)                        # the model's suggestion stays out
    tag = {(t["key"], t["value"]): t["id"] for t in p["tags"]}
    ca = p["clip_annotations"]
    assert ca[0]["tags"] == [tag[("species", "Rhinolophus hipposideros")]] and "tags" not in ca[1]
    assert ca[2]["tags"] == [tag[("genus", "Myotis")]]
    assert "tags" not in ca[3] and "Unknown bat" in ca[3]["notes"][0]["message"]
    by_event = {a["sound_event"]: a for a in p["sound_event_annotations"]}
    first = [by_event[e["uuid"]] for e in p["sound_events"][:3]]
    assert "tags" in first[0] and "tags" in first[1] and "tags" not in first[2]     # not the second bat's call
    states = [[b["state"] for b in t["status_badges"]] for t in p["tasks"]]
    assert states == [["completed"], [], ["completed"], ["completed"]]


def test_whombat_same_ids_every_time_and_time_expansion():
    s, (d1, p1) = project_for()
    d2, p2 = whombat.build(s)
    strip = lambda o: json.dumps({k: v for k, v in o["data"].items() if k != "created_on"}, sort_keys=True)
    assert strip(p1) == strip(p2) and strip(d1) == strip(d2)
    s10, (_, p10) = project_for(te=10)
    rec = p10["data"]["recordings"][0]
    assert rec["time_expansion"] == 10.0 and rec["samplerate"] == SR * 10 and abs(rec["duration"] - 0.05) < 1e-6


def test_export_writes_both_files():
    s, _ = project_for()
    res = whombat.export(s)
    project = json.loads(Path(res["annotations"]).read_text(encoding="utf8"))
    dataset = json.loads(Path(res["dataset"]).read_text(encoding="utf8"))
    assert res["recordings"] == 2 and res["clips"] == 4 and res["tagged_clips"] == 2 and res["sound_events"] == 5
    assert project["data"]["name"].endswith("(WildWard Listen)") and dataset["data"]["name"] == s.folder.name


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
