"""CSV of every pass and a one-page HTML survey report."""
import csv
import html
from collections import Counter
from datetime import datetime

from .engine import Survey


def export(survey: Survey) -> dict:
    out = survey.dir
    rows = []
    for p in survey.passes:
        species = p["label"] or p["suggestion"] or ""
        rows.append({"file": p["file"], "start_s": p["start"], "end_s": p["end"], "peak_khz": p["peak_khz"],
                     "species": species, "reviewed": "yes" if p["label"] else "no",
                     "confidence": "" if p["label"] else (p["confidence"] or ""), "cluster": p["cluster"]})
    for r, p in zip(rows, survey.passes):
        m = p.get("measures") or {}
        r.update({"time": (p.get("time") or {}).get("iso") or "", "call_shape": m.get("shape", ""),
                  "f_char_khz": m.get("f_char_khz", ""), "duration_ms": m.get("duration_ms", ""),
                  "sound_type": (p.get("sound") or {}).get("type", "")})
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

    reviewed = Counter(p["label"] for p in survey.passes if p["label"])
    suggested = Counter(p["suggestion"] for p in survey.passes if not p["label"] and p["suggestion"])
    unknown = sum(1 for p in survey.passes if not p["label"] and not p["suggestion"])
    species = sorted(set(reviewed) | set(suggested))
    table = "".join(
        f"<tr><td><i>{html.escape(s)}</i></td><td>{reviewed.get(s, 0)}</td><td>{suggested.get(s, 0)}</td></tr>"
        for s in species)
    files = len({p["file"] for p in survey.passes})
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Survey report</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:760px;margin:40px auto;padding:0 16px;color:#12201a}}
h1{{margin:0 0 4px}}table{{border-collapse:collapse;width:100%;margin:16px 0}}td,th{{border-bottom:1px solid #ddd;padding:8px;text-align:left}}
.note{{color:#56645c;font-size:13px}}</style></head><body>
<h1>Bat survey report</h1>
<p class="note">{html.escape(str(survey.folder))} · generated {datetime.now():%Y-%m-%d %H:%M} with WildWard Listen</p>
<p><b>{len(survey.passes)}</b> bat passes in <b>{files}</b> recordings. <b>{sum(reviewed.values())}</b> reviewed by an expert,
<b>{sum(suggested.values())}</b> suggested by the model and not yet reviewed, <b>{unknown}</b> unidentified.</p>
<table><tr><th>Species</th><th>Reviewed passes</th><th>Suggested, unreviewed</th></tr>{table}</table>
<p class="note">Suggestions come from a classifier trained on this survey's own reviewed passes. Treat unreviewed
suggestions as leads, not identifications. Skipped files: {len(survey.skipped)}.</p></body></html>"""
    report_path = out / "report.html"
    report_path.write_text(page, encoding="utf8")
    return {"csv": str(csv_path), "calls": str(calls_path), "report": str(report_path)}
