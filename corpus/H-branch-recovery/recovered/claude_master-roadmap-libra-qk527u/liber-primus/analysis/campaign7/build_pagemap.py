"""Build PAGE-MAP.md — the page-numbering Rosetta Stone.

Community sources use at least three numbering schemes for the same physical
pages (scream314 original jpg numbers, relikd 0-indexed images, krisyotam
%-split segments). Campaign VII showed this causes real errors (our 'page 49'
is not relikd image 49). This script aligns them mechanically: parse the
scream314 catalog (which carries 'NN.jpg - MM.jpg' headers = original->relikd),
extract each section's rune stream, and locate it exactly inside the krisyotam
corpus. Output: a single verified mapping table.
"""
import os
import re
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
from lp import gematria as gp  # noqa

LP = os.path.join(HERE, "..", "..", "data", "scream314_lp.md")
KRIS = os.path.join(HERE, "..", "..", "data", "krisyotam_runes.txt")


def kris_pages():
    txt = open(KRIS, encoding="utf-8").read()
    return [gp.runes_to_indices(s) for s in txt.split("%")
            if gp.runes_to_indices(s)]


def scream_sections():
    txt = open(LP, encoding="utf-8").read()
    out = []
    cur = None
    for ln in txt.splitlines():
        m = re.match(r"^## (.+)", ln)
        if m:
            cur = {"label": m.group(1).strip(), "runes": []}
            out.append(cur)
        elif cur is not None:
            cur["runes"].extend(gp.runes_to_indices(ln))
    return [s for s in out if s["runes"]]


def main():
    kris = kris_pages()
    flat = [i for pg in kris for i in pg]
    # page start offsets in the flat kris stream
    starts, off = [], 0
    for pg in kris:
        starts.append(off)
        off += len(pg)

    def locate(seq):
        """Find seq in flat kris stream; return (kris_page_first, kris_page_last)."""
        n, m = len(flat), len(seq)
        for i in range(n - m + 1):
            if flat[i:i + m] == seq:
                first = max(j for j, s in enumerate(starts) if s <= i)
                last = max(j for j, s in enumerate(starts) if s <= i + m - 1)
                return first, last, i
        return None

    rows = []
    for sec in scream_sections():
        label = sec["label"]
        parts = [p.strip() for p in label.split(" - ")]
        scream_lbl = parts[0]
        relikd_lbl = parts[1] if len(parts) > 1 else "(LP1 / unnumbered)"
        loc = locate(sec["runes"])
        rows.append({
            "label": label,
            "scream_jpg": scream_lbl,
            "relikd": relikd_lbl,
            "n_runes": len(sec["runes"]),
            "kris": f"{loc[0]}–{loc[1]}" if loc and loc[0] != loc[1]
                    else (str(loc[0]) if loc else "NOT IN KRIS (non-runic/LP1)"),
        })

    out_path = os.path.join(HERE, "..", "..", "PAGE-MAP.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# PAGE-MAP — the page-numbering Rosetta Stone\n\n")
        f.write("_Mechanically verified by exact rune-stream matching "
                "(`analysis/campaign7/build_pagemap.py`). Three schemes name the "
                "same physical pages: **scream314** original jpg numbers, "
                "**relikd** 0-indexed images, and **krisyotam** `%`-split segment "
                "indices (what `load_pages()` returns — what all our per-page "
                "scores refer to). Always say which scheme you mean._\n\n")
        f.write("| scream314 jpg | relikd img | runes | krisyotam idx |\n")
        f.write("|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['scream_jpg']} | {r['relikd']} | {r['n_runes']} | {r['kris']} |\n")
        f.write("\n**Key facts:** relikd images 49/50/51 are the base-60 token "
                "tables (non-runic, absent from the krisyotam rune corpus). "
                "krisyotam indices therefore do NOT equal relikd image numbers. "
                "Sections marked NOT IN KRIS are LP1/solved/non-runic material.\n")
    print(f"wrote {out_path}")
    for r in rows[:12]:
        print(f"  {r['label'][:34]:34} relikd={r['relikd']:>3} "
              f"runes={r['n_runes']:>4} kris={r['kris']}")
    print(f"  ... {len(rows)} sections total")


if __name__ == "__main__":
    main()
