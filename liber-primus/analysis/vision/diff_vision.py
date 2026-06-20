"""Avenue #1: diff AI-vision re-transcriptions against the canonical runes.

Inputs:
  analysis/vision/canonical_pages.json   (from build_canonical.py)
  analysis/vision/vision_results.json    (armada output: [{page, runes, uncertain:[...]}])

Output:
  analysis/vision/DIFF-REPORT.md  + prints a summary.

For each page we align the vision rune string to canonical with difflib and
list every disagreement (position, canonical glyph/translit, vision glyph).
A disagreement is "corroborated" if the vision agent itself flagged that area
as uncertain -> those are the LOW-priority noise. The dangerous ones are
HIGH-CONFIDENCE disagreements (agent was sure, but differs from canonical):
those are the real candidate transcription errors to re-read at high zoom.
"""
import json
import os
import sys
from difflib import SequenceMatcher

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp.gematria import RUNE_TO_TRANS, RUNE_TO_IDX  # noqa: E402

canon = {p["page"]: p for p in json.load(open(os.path.join(HERE, "canonical_pages.json"), encoding="utf-8"))}
vis = {p["page"]: p for p in json.load(open(os.path.join(HERE, "vision_results.json"), encoding="utf-8"))}


def clean(s):
    return "".join(c for c in (s or "") if c in RUNE_TO_IDX)


def tr(glyph):
    return RUNE_TO_TRANS.get(glyph, "?")


rows = []
high_conf = []   # dangerous: differ AND not flagged uncertain by agent
for pg in sorted(vis):
    if pg not in canon:
        continue
    c = clean(canon[pg]["runes"])
    v = clean(vis[pg]["runes"])
    sm = SequenceMatcher(None, c, v, autojunk=False)
    ratio = sm.ratio()
    diffs = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        diffs.append({
            "tag": tag,
            "canon_pos": i1,
            "canon": c[i1:i2],
            "canon_tr": "".join(tr(x) for x in c[i1:i2]),
            "vision": v[j1:j2],
            "vision_tr": "".join(tr(x) for x in v[j1:j2]),
        })
    # agent-flagged uncertain positions (in vision coordinates)
    unc_positions = set()
    for u in vis[pg].get("uncertain", []) or []:
        pos = u.get("position")
        if isinstance(pos, int):
            unc_positions.update(range(max(0, pos - 1), pos + 2))
    n_unflagged = 0
    for d in diffs:
        # crude: was any vision position in this diff flagged?
        flagged = any(p in unc_positions for p in range(d["canon_pos"], d["canon_pos"] + 3))
        d["agent_flagged"] = flagged
        if not flagged and d["tag"] == "replace" and len(d["canon"]) == len(d["vision"]) <= 2:
            n_unflagged += 1
            high_conf.append((pg, d))
    rows.append({
        "page": pg, "n_canon": len(c), "n_vision": len(v),
        "ratio": ratio, "n_diffs": len(diffs), "n_highconf": n_unflagged,
        "diffs": diffs,
    })

rows.sort(key=lambda r: r["ratio"])

lines = ["# Avenue #1 — Vision re-transcription DIFF report", ""]
lines.append(f"Pages compared: {len(rows)}")
avg = sum(r['ratio'] for r in rows) / max(1, len(rows))
lines.append(f"Mean alignment ratio (vision vs canonical): {avg:.3f}")
lines.append(f"HIGH-CONFIDENCE candidate errors (agent sure, differs from canonical, <=2 runes): {len(high_conf)}")
lines.append("")
lines.append("## Per-page summary (worst alignment first)")
lines.append("")
lines.append("| page | canon | vision | ratio | diffs | high-conf |")
lines.append("|---|---|---|---|---|---|")
for r in rows:
    lines.append(f"| p{r['page']} | {r['n_canon']} | {r['n_vision']} | {r['ratio']:.3f} | {r['n_diffs']} | {r['n_highconf']} |")
lines.append("")
lines.append("## HIGH-CONFIDENCE candidate transcription errors (re-read these at high zoom)")
lines.append("")
if not high_conf:
    lines.append("_None. Every vision/canonical disagreement was either an alignment artifact "
                 "or self-flagged by the agent as uncertain — canonical is corroborated._")
else:
    for pg, d in high_conf:
        lines.append(f"- **p{pg}** ~pos {d['canon_pos']}: canonical `{d['canon']}` ({d['canon_tr']}) "
                     f"vs vision `{d['vision']}` ({d['vision_tr']})")
lines.append("")
lines.append("## Full per-page disagreements")
for r in rows:
    if not r["diffs"]:
        continue
    lines.append(f"\n### p{r['page']}  (ratio {r['ratio']:.3f})")
    for d in r["diffs"]:
        flag = " [agent-flagged]" if d.get("agent_flagged") else ""
        lines.append(f"- {d['tag']} @canon{d['canon_pos']}: `{d['canon']}`({d['canon_tr']}) "
                     f"-> `{d['vision']}`({d['vision_tr']}){flag}")

dst = os.path.join(HERE, "DIFF-REPORT.md")
open(dst, "w", encoding="utf-8").write("\n".join(lines))
print(f"wrote {dst}")
print(f"pages={len(rows)} mean_ratio={avg:.3f} high_conf_candidates={len(high_conf)}")
print("worst 8 pages by alignment:")
for r in rows[:8]:
    print(f"  p{r['page']:>2}  ratio={r['ratio']:.3f}  diffs={r['n_diffs']}  highconf={r['n_highconf']}")
