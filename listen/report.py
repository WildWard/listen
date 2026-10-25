"""CSV of every pass and a one-page HTML survey report."""
import csv
import html
from collections import Counter
from datetime import datetime
from pathlib import Path

from .engine import Survey


def export(survey: Survey) -> dict:
    out = survey.dir
    rows = []
    for p in survey.passes:
        species = p["label"] or (f'{p["genus"]} sp.' if p.get("genus") else p["suggestion"]) or ""
        rows.append({"file": p["file"], "start_s": p["start"], "end_s": p["end"], "peak_khz": p["peak_khz"],
                     "species": species, "reviewed": "yes" if p["label"] else "no",
                     "confidence": "" if p["label"] else (p["confidence"] or ""), "cluster": p["cluster"]})
    for r, p in zip(rows, survey.passes):
        m = p.get("measures") or {}
        r.update({"time": (p.get("time") or {}).get("iso") or "", "call_shape": m.get("shape", ""),
                  "f_char_khz": m.get("f_char_khz", ""), "duration_ms": m.get("duration_ms", ""),
                  "sound_type": (p.get("sound") or {}).get("type", ""),
                  "unusual_frequency": "yes" if p.get("unusual") else "",
                  "nearest_known_species": (p.get("unusual") or {}).get("nearest", "")})
    csv_path = out / "passes.csv"
    with csv_path.open("w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["file"])
        w.writeheader()
        w.writerows(rows)
    # one row per measured call: the format used for discriminant-function and library work
    calls_path = out / "calls.csv"
    call_rows = []
    for p in survey.passes:
        for c in p.get("calls", []):
            call_rows.append({"file": p["file"], "pass_id": p["id"], "pass_start_s": p["start"],
                              "species": p["label"] or p["suggestion"] or "", "reviewed": "yes" if p["label"] else "no"} | c)
    with calls_path.open("w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(call_rows[0]) if call_rows else ["file"])
        w.writeheader()
        w.writerows(call_rows)

    occ_path, n_occ = darwin_core(survey)

    reviewed = Counter(p["label"] for p in survey.passes if p["label"])
    suggested = Counter(p["suggestion"] for p in survey.passes if not p["label"] and p["suggestion"])
    unknown = sum(1 for p in survey.passes if not p["label"] and not p["suggestion"])
    species = sorted(set(reviewed) | set(suggested))
    table = "".join(
        f"<tr><td><i>{html.escape(s)}</i></td><td>{reviewed.get(s, 0)}</td><td>{suggested.get(s, 0)}</td></tr>"
        for s in species)
    files = len({p["file"] for p in survey.passes})
    wind = survey.wind_risk()
    wind_note = ""
    if wind["labelled"] + wind["by_sound"]:
        hours = sorted(wind["by_hour"].items(), key=lambda kv: -kv[1])[:3]
        busy_h = ", ".join(f"{h:02d}:00 ({n})" for h, n in hours)
        busy_n = ", ".join(f"{d} ({n})" for d, n in wind["top_nights"][:3])
        wind_note = (f"<h2>Open-air foragers (wind-turbine risk)</h2><p><b>{wind['labelled'] + wind['by_sound']}</b> passes of bats that hunt "
                     f"in open air, the group found flying at turbine height in Southeast Asia ({wind['labelled']} labelled, "
                     f"{wind['by_sound']} by call shape only). "
                     + (f"Busiest hours: {busy_h}. " if hours else "")
                     + (f"Busiest nights: {busy_n}. " if wind["top_nights"] else "")
                     + "Ground-level detectors under-sample bats at rotor height, so treat this as a lower bound and "
                     "pair it with detectors at height for an impact assessment.</p>")
    odd = [p for p in survey.passes if p.get("unusual")]
    odd_note = (f"<h2>Unusual frequencies</h2><p><b>{len(odd)}</b> unreviewed constant-frequency passes call at least 5% away from every "
                f"known species' frequency (around {', '.join(sorted({f'{p["unusual"]["f_khz"]:.0f}' for p in odd}, key=float))} kHz). "
                "They may be species missing from the reference library, or worth a closer look. Listed in passes.csv as "
                "<code>unusual_frequency = yes</code>.</p>") if odd else ""
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Survey report</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;color:#12201a}}
h1{{margin:0 0 4px}}table{{border-collapse:collapse;width:100%;margin:16px 0}}td,th{{border-bottom:1px solid #ddd;padding:8px;text-align:left}}
.note{{color:#56645c;font-size:13px}}</style></head><body>
<h1>Bat survey report</h1>
<p class="note">{html.escape(str(survey.folder))} · generated {datetime.now():%Y-%m-%d %H:%M} with WildWard Listen</p>
<p><b>{len(survey.passes)}</b> bat passes in <b>{files}</b> recordings. <b>{sum(reviewed.values())}</b> reviewed by an expert,
<b>{sum(suggested.values())}</b> suggested by the model and not yet reviewed, <b>{unknown}</b> unidentified.</p>
{odd_note}
{wind_note}
<table><tr><th>Species</th><th>Reviewed passes</th><th>Suggested, unreviewed</th></tr>{table}</table>
<p class="note">Suggestions come from a classifier trained on this survey's own reviewed passes. Treat unreviewed
suggestions as leads, not identifications. Skipped files: {len(survey.skipped)}.</p></body></html>"""
    report_path = out / "report.html"
    report_path.write_text(page, encoding="utf8")
    return {"csv": str(csv_path), "calls": str(calls_path), "report": str(report_path), "occurrences": str(occ_path),
            "n_occurrences": n_occ}


DWC_FIELDS = ["occurrenceID", "basisOfRecord", "eventDate", "scientificName", "taxonRank", "kingdom", "phylum", "class",
              "order", "decimalLatitude", "decimalLongitude", "geodeticDatum", "organismQuantity", "organismQuantityType",
              "samplingProtocol", "identificationVerificationStatus", "identificationRemarks", "associatedMedia",
              "occurrenceRemarks"]


def darwin_core(survey: Survey) -> tuple[Path, int]:
    """occurrences.csv in Darwin Core, the standard GBIF and most biodiversity databases import.
    One row per expert-reviewed pass with a species or genus name. Model suggestions are left out on
    purpose: databases should only receive identifications a person has checked."""
    rows = []
    for p in survey.passes:
        name = p["label"]
        if not name or name.lower().startswith("unknown"):
            continue
        meta = survey.files_meta.get(p["file"], {})
        m = p.get("measures") or {}
        parts = [f"{k} {m[k]}" for k in ("f_char_khz", "duration_ms") if m.get(k) is not None]
        rows.append({
            "occurrenceID": f"wildward-listen:{survey.folder.name}:{p['file']}:{p['start']:.2f}",
            "basisOfRecord": "MachineObservation",
            "eventDate": (p.get("time") or {}).get("iso") or "",
            "scientificName": name,
            "taxonRank": "species" if len(name.split()) >= 2 else "genus",
            "kingdom": "Animalia", "phylum": "Chordata", "class": "Mammalia", "order": "Chiroptera",
            "decimalLatitude": meta.get("lat", ""), "decimalLongitude": meta.get("lon", ""),
            "geodeticDatum": "WGS84" if "lat" in meta else "",
            "organismQuantity": 1, "organismQuantityType": "bat passes",
            "samplingProtocol": "passive acoustic monitoring" + (f", {meta['device']}" if meta.get("device") else ""),
            "identificationVerificationStatus": "verified by expert",
            "identificationRemarks": "identified from echolocation calls; reviewed in WildWard Listen",
            "associatedMedia": p["file"],
            "occurrenceRemarks": "call " + ", ".join(parts) + (f", shape {m['shape']}" if m.get("shape") else "") if parts else "",
        })
    path = survey.dir / "occurrences.csv"
    with path.open("w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=DWC_FIELDS)
        w.writeheader()
        w.writerows(rows)
    return path, len(rows)
