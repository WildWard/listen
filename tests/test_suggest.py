"""Tests for the suggestion logic that need no recordings: made-up embeddings and call measurements.

Run with:  python -m pytest tests      or      python tests/test_suggest.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from listen.engine import REGIONS, Survey  # noqa: E402

RNG = np.random.default_rng(7)
DIM = 1536


def features(fc: float, cf: bool) -> np.ndarray:
    """A measured-call vector in the order the engine uses: f_char, f_start, f_end, duration, bandwidth, slope, CF flag."""
    return np.array([fc, fc + (1 if cf else 30), fc - 1, 30 if cf else 4, 2 if cf else 30, 0.1 if cf else 8, 1.0 if cf else 0.0], np.float32)


def library(species: dict) -> dict:
    """species: name -> (embedding centre, call frequency, is constant-frequency). Eight reference passes each."""
    X, F, y = [], [], []
    for name, (centre, fc, cf) in species.items():
        for _ in range(8):
            X.append(centre + 0.05 * RNG.standard_normal(DIM))
            F.append(features(fc * (1 + 0.02 * RNG.standard_normal()), cf))
            y.append(name)
    return {"X": np.array(X, np.float32), "F": np.array(F), "y": np.array(y), "files": np.array(y), "species": sorted(species)}


def survey_with(passes: list[tuple[np.ndarray, float, bool]], ref: dict, region: str | None = None) -> Survey:
    s = Survey(Path(tempfile.mkdtemp()))
    s.emb = np.array([e for e, _, _ in passes], np.float32)
    s.passes = [{"id": i, "file": f"rec_{i}.wav", "start": 0.0, "end": 1.0, "label": None, "cluster": 0,
                 "measures": {"f_char_khz": fc, "n_calls": 6, "shape": "CF" if cf else "FM"},
                 "sound": {"type": "tone", "hint": "typical of something"}} for i, (_, fc, cf) in enumerate(passes)]
    s.reference = ref
    if region:
        s.context["survey"]["region"] = region
    s.suggest()
    return s


CENTRES = {k: RNG.standard_normal(DIM) for k in "abc"}
LIB = library({
    "Rhinolophus hipposideros": (CENTRES["a"], 108.0, True),
    "Barbastella barbastellus": (CENTRES["b"], 33.0, False),
    "Hipposideros larvatus": (CENTRES["c"], 91.0, True),
})


def test_normal_pass_is_untouched():
    s = survey_with([(CENTRES["a"] + 0.05 * RNG.standard_normal(DIM), 108.5, True)], LIB)
    p = s.passes[0]
    assert p["suggestion"] == "Rhinolophus hipposideros"
    assert p["misfit"] is None


def test_wrong_octave_gets_a_note_and_keeps_the_suggestion():
    """The check itself: a horseshoe bat suggestion on a pass measured at 33 kHz gets a note, nothing else changes."""
    s = survey_with([(CENTRES["a"], 108.0, True)], LIB)
    p = {"measures": {"f_char_khz": 33.0, "n_calls": 6}, "sound": {"type": "sweep"}}
    note = s.frequency_mismatch(p, "Rhinolophus hipposideros", s.species_bands())
    assert note and note["f_khz"] == 33.0 and 100 < note["low"] <= note["high"] < 115
    assert s.frequency_mismatch(p, "Barbastella barbastellus", s.species_bands()) is None


def test_suggestions_are_identical_with_and_without_the_check():
    """A note must never change what Listen suggests."""
    import listen.engine as eng
    passes = [(CENTRES[k] + 0.3 * RNG.standard_normal(DIM), fc, cf) for k, fc, cf in
              [("a", 33.0, False), ("b", 108.0, True), ("c", 60.0, True), ("a", 108.0, True), ("b", 34.0, False)]]
    with_check = survey_with(passes, LIB)
    eng.FIT_MARGIN, old = 1e9, eng.FIT_MARGIN
    try:
        without = survey_with(passes, LIB)
    finally:
        eng.FIT_MARGIN = old
    assert [p["suggestion"] for p in with_check.passes] == [p["suggestion"] for p in without.passes]
    assert [p["confidence"] for p in with_check.passes] == [p["confidence"] for p in without.passes]
    assert any(p["misfit"] for p in with_check.passes) and not any(p["misfit"] for p in without.passes)


def test_faint_pass_gets_no_note():
    s = survey_with([(CENTRES["a"], 108.0, True)], LIB)
    p = {"measures": {"f_char_khz": 33.0, "n_calls": 2}, "sound": {"type": "tone"}}
    assert s.frequency_mismatch(p, "Rhinolophus hipposideros", s.species_bands()) is None
    p = {"measures": {"f_char_khz": 33.0, "n_calls": 9}, "sound": {"type": "unclear"}}
    assert s.frequency_mismatch(p, "Rhinolophus hipposideros", s.species_bands()) is None


def test_margin_allows_normal_variation():
    # 15% off the library's frequency is still the same species (clutter, Doppler, another population)
    s = survey_with([(CENTRES["b"] + 0.05 * RNG.standard_normal(DIM), 38.0, False)], LIB)
    assert s.passes[0]["misfit"] is None
    assert s.passes[0]["suggestion"] == "Barbastella barbastellus"


def test_region_list_flags_but_does_not_block():
    assert "Hungary" in REGIONS and len(REGIONS["Hungary"]["species"]) == 28
    a = CENTRES["c"] + 0.05 * RNG.standard_normal(DIM)
    s = survey_with([(a, 91.0, True), (CENTRES["a"] + 0.05 * RNG.standard_normal(DIM), 108.0, True)], LIB, region="Hungary")
    asian, local = s.passes
    assert asian["suggestion"] == "Hipposideros larvatus" and asian["unexpected"] == "Hungary"
    assert local["suggestion"] == "Rhinolophus hipposideros" and local["unexpected"] is None
    s2 = survey_with([(a, 91.0, True)], LIB)
    assert s2.passes[0]["unexpected"] is None   # no region chosen, no flag


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
