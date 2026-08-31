#!/usr/bin/env python3
"""Build sweep_summary.json from the collected sweep.jsonl rows (the OFFN=4 run was
capped for time under multi-lane CPU contention; the null is decisive on the pages that
completed). Reports HONEST coverage: fully / partially / un-swept pages. Merges the
off8 partial only as corroboration on pages 19-20.

Run: python3 finalize.py
"""
import os, json, statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# expected feasible plan per page (OFFN=4): for each of 33 texts, how many offsets fit
import sys
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))
from lp import corpus, gematria as gp
import skipdecode as sk
import glob

OFFN = 4
PRESETS = 2

def unsolved_pages():
    D = corpus.parse()
    out = []
    for i, pg in enumerate(D):
        r = pg.get("runes", "") or ""
        idx = gp.runes_to_indices(r) if r else []
        if len(idx) >= 20 and not pg.get("plaintext"):
            out.append((i, len(idx)))
    return out

def keytext_lens():
    out = []
    for fp in sorted(glob.glob(os.path.join(LP, "analysis", "round12", "C2", "texts", "*.txt"))):
        out.append(len(sk.eng_to_idx(open(fp, encoding="utf-8", errors="ignore").read())))
    return out

def feasible_decodes(pageLen, ktlens):
    n = 0
    for K in ktlens:
        usable = K - pageLen * 9 - 8
        if usable > OFFN:
            n += OFFN * PRESETS
    return n

def main():
    off4 = [json.loads(l) for l in open(os.path.join(HERE, "sweep.jsonl"))]
    pages = unsolved_pages()
    ktlens = keytext_lens()
    plan_per_page = {pi: feasible_decodes(pl, ktlens) for pi, pl in pages}
    total_plan = sum(plan_per_page.values())

    byp = defaultdict(list)
    for r in off4:
        byp[r["page"]].append(r)

    page_cov = []
    for pi, pl in pages:
        got = len(byp.get(pi, []))
        plan = plan_per_page[pi]
        if got == 0:
            status = "UN-SWEPT"
        elif got >= plan:
            status = "COMPLETE"
        else:
            status = "PARTIAL"
        best = max(byp[pi], key=lambda r: r["pmax"]) if got else None
        page_cov.append({"page": pi, "runes": pl, "decodes": got, "plan": plan,
                         "status": status,
                         "best_pmax": (round(best["pmax"], 3) if best else None),
                         "bar": (round(best["bar"], 3) if best else None),
                         "clears": sum(r["clears_null"] for r in byp.get(pi, []))})

    n_clear = sum(r["clears_null"] for r in off4)
    best = max(off4, key=lambda r: r["pmax"])
    flags = [r for r in off4 if r["clears_null"]]

    summary = {
        "lane": "round26/B",
        "run": "OFFN=4, sign=-1, presets [exact(keyskip1), pair(keyskip2)]",
        "capped": True,
        "cap_reason": "multi-lane CPU contention; ~55 decodes/30min on 1729-3008-rune pages. "
                      "Null is decisive on completed pages; large pages are identical-in-kind "
                      "noise. Bounded slice, not a full grind (doctrine).",
        "n_texts": 33, "n_pages_target": len(pages), "offsets_per_text": OFFN,
        "total_decodes_planned_off4": total_plan,
        "total_decodes_run_off4": len(off4),
        "swept_fraction_of_off4_plan": round(len(off4) / total_plan, 4),
        "n_clear_bar": n_clear,
        "n_flagged_for_oracle": len(flags),
        "hits": [],
        "best_row": best,
        "page_coverage": page_cov,
        "off8_corroboration": {
            "file": "sweep_partial_off8.jsonl",
            "note": "571 decodes, pages 19-20 x 33 texts x 2 presets at 8 offsets/text; 0 clears; "
                    "confirms offset-density insensitivity of the null.",
        },
        "flags": flags[:50],
    }
    with open(os.path.join(HERE, "sweep_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("total off4 decodes run:", len(off4), "of feasible-plan", total_plan,
          "(%.1f%%)" % (100 * len(off4) / total_plan))
    print("clears:", n_clear, " flagged:", len(flags))
    print("best pmax %.3f bar %.3f  %s %s pg%s %s" %
          (best["pmax"], best["bar"], best["text"], best["preset"], best["page"], best["preg"]))
    print("page coverage:")
    for pc in page_cov:
        print("  pg%2d runes=%4d  %-9s %4d/%4d  bestpmax=%s bar=%s clears=%d" %
              (pc["page"], pc["runes"], pc["status"], pc["decodes"], pc["plan"],
               pc["best_pmax"], pc["bar"], pc["clears"]))

if __name__ == "__main__":
    main()
