"""Ledger rows for the blind adjudicator and the two sweeps that used it (lanes S1, S2). Idempotent."""
import collections
import json
import os

import common as cm

S1 = "liber-primus/analysis/round44/S1-blind-perl/"
S2 = "liber-primus/analysis/round44/S2-blind-glibc-clock/"
HERE = cm.HERE
cal = json.load(open(os.path.join(HERE, "calibration.json")))
c1 = json.load(open(os.path.join(HERE, "control.json")))
r1 = json.load(open(os.path.join(HERE, "results.json")))
p2 = os.path.join(HERE, "..", "S2-blind-glibc-clock")
c2 = json.load(open(os.path.join(p2, "control.json")))
r2 = json.load(open(os.path.join(p2, "results.json")))
DATE = "2026-11-12"
STATUS = lambda v: "negative" if v == "NEGATIVE" else "open" if v.startswith("FLAGGED") else "partially-run" if "incomplete" in v else "inconclusive"
COND = ("one draw per rune from rune 0 of page 0, no draws before it; a rejection consumes one draw or two (with or without the "
        "in-stream coin); at most 8/12/24 rejections in the first 64/120/262 runes; both key signs; any combiner constant, Atbash "
        "and Beaufort covered; no register conditional (any plaintext with IoC x 29 of about 1.4 or more over the page)")
NOTCOV = ("a warm-up before rune 0; a stream that starts at another section or page head; other reductions of the generator; a key "
          "pointer that stalls (F left in clear); rejection by deletion or rewrite without a draw; separators that consume draws; "
          "a plaintext that is near-uniform over 29 symbols")
rows = [
    {"id": "R44-I1-BLIND-ADJUDICATOR", "lane": "S1-blind-perl", "round": "44/S1", "date": DATE, "status": "measured",
     "hypothesis": "A correct key can be recognised without any language model, whatever the plaintext's language, spelling or "
                   "numbering and whatever constant or reflection sits in the combiner.",
     "threshold": "fixed in S1 PREREG section 3 from the null on 2,000,000 random keys: sums of squares >= 247 / 828 / 3564 at "
                  "L = 64 / 120 / 262 (IoC x 29 >= 1.316 / 1.436 / 1.40)",
     "threshold_fixed_in_advance": True, "positive_control": "passed",
     "control_detail": f"432 calibration plants (random keys; English letter-wise, English multigraph, Latin; as written / random "
                       f"relabelling / +7 constant / Beaufort; keyskip1 / skip_by_two / coin_from_key; both key signs): 431 pass "
                       f"stage 1, IoC x 29 minimum {cal['plant_ioc_L120']['min']:.3f} at L=120 and {cal['plant_ioc_L262']['min']:.3f} at "
                       f"L=262. Through the sweep binary: {c1['flagged']}/{c1['of']} Perl-seed plants and {c2['flagged']}/{c2['of']} glibc-seed "
                       f"plants flagged, 0 other seeds flagged in 40 windows of 2^18 seeds.",
     "result": {"statistic": "largest sum of squared symbol counts of the decode over key-pointer paths that jump only at "
                             "admissible sites (rejected draws equal; accepted draw differs from them by C[i]-C[i-1])",
                "null_stage1_pass_rate": 0.06, "null_stage2_pass_rate_measured": r1["stage3_rate_per_pair"],
                "null_full_page_ioc_x29": "about 1.10 +- 0.03 for an unselected random key",
                "cost": "about 4-5 microseconds per seed for four modes on one core",
                "verdict": "MEASURED: a language-model-free adjudicator with power >= 0.99 on plants and a directly measured null. "
                           "It covers the combiner-constant, reflection, numbering and register conditionals at once."},
     "coverage": COND, "not_covered": NOTCOV, "null": "2,000,000 random keys per stage length on the real page-0 head; the sweeps themselves",
     "evidence": [S1 + "blind.c", S1 + "calibration.json", S1 + "control.json", S1 + "PREREG.md",
                  "liber-primus/analysis/round44/A0-fresh-eyes-audit/blind_adjudicator_poc.py"],
     "reproduce": "cd " + S1 + " && python3 calibrate.py 2000000 && python3 run_s1.py control",
     "supersedes": [], "superseded_by": None, "reopens_if": "a plant in the covered class is shown to fail"},
    {"id": "R44-S1-BLIND-PERL-2E32", "lane": "S1-blind-perl", "round": "44/S1", "date": DATE, "status": STATUS(r1["verdict"]),
     "hypothesis": "The LP2 keystream is Perl int(rand(29)) after srand(s) for some 32-bit s (explicit or automatic): the whole "
                   "family, 2^32 keystreams.",
     "threshold": "PREREG section 3 and 7: FLAGGED if a (seed, mode) pair clears IoC x 29 >= 1.316 / 1.436 / 1.40 at L = 64 / 120 / 262; "
                  "NEGATIVE if none does, the control passed and all 2^32 seeds were evaluated",
     "threshold_fixed_in_advance": True, "positive_control": "passed" if c1["passed"] else "FAILED",
     "control_detail": f"{c1['flagged']}/{c1['of']} planted Perl seeds flagged in their true mode by the sweep binary (keystream from the "
                       f"perl binary itself), {c1['other_seeds_flagged']} other seeds flagged in 24 windows of 2^18 seeds.",
     "result": {"seeds_evaluated": r1["seeds_evaluated"], "complete": r1["complete"], "pairs_evaluated": r1["pairs_evaluated"],
                "stage3_records": r1["stage3_records"], "flagged": r1["flagged"], "max_ioc_x29_L262": r1["max_ioc_x29_L262"],
                "best_panel_pmax_among_top_rows": r1.get("best_panel_pmax_among_top_rows"), "verdict": r1["verdict"]},
     "coverage": "All 2^32 srand seeds; the idiom int(rand(29)); " + COND + " [plants: English letter-wise, English multigraph, Latin]",
     "not_covered": NOTCOV, "null": "the sweep itself (all but at most one seed are wrong keys)",
     "declares_sweep": True, "sweep_store": S1 + "sweep_rows_top.jsonl",
     "evidence": [S1 + "PREREG.md", S1 + "RESULTS.md", S1 + "results.json", S1 + "hist.json", S1 + "control.json"],
     "reproduce": "cd " + S1 + " && python3 run_s1.py sweep 4 && python3 run_s1.py finalize",
     "supersedes": [], "superseded_by": None,
     "reopens_if": "a warm-up, another stream start or another reduction is given a reason; or a covered-class plant is shown to fail"},
    {"id": "R44-S2-BLIND-GLIBC-CLOCK", "lane": "S2-blind-glibc-clock", "round": "44/S2", "date": DATE, "status": STATUS(r2["verdict"]),
     "hypothesis": "The LP2 keystream is glibc rand() after srand(t), t a unix second between 2011-12-01 and 2014-04-03 UTC or an "
                   "integer below 2^24, reduced as rand() % 29 or as floor(29 * rand() / 2^31).",
     "threshold": "as R44-S1-BLIND-PERL-2E32 (S2 PREREG sections 2 and 4)",
     "threshold_fixed_in_advance": True, "positive_control": "passed" if c2["passed"] else "FAILED",
     "control_detail": f"{c2['flagged']}/{c2['of']} planted seeds flagged in their true mode (keystream from the system C library "
                       f"itself), {c2['other_seeds_flagged']} other seeds flagged in 16 windows of 2^18 seeds.",
     "result": {"keystreams_evaluated": r2["keystreams_evaluated"], "complete": r2["complete"],
                "per_reduction": {g: {"seeds": v["seeds_evaluated"], "stage3_records": v["stage3_records"], "flagged": v["flagged"],
                                      "max_ioc_x29_L262": v["max_ioc_x29_L262"]} for g, v in r2["generators"].items()},
                "best_panel_pmax_among_top_rows": r2.get("best_panel_pmax_among_top_rows"), "verdict": r2["verdict"]},
     "coverage": "Seeds [0, 2^24) and [1322697600, 1396483200) (both server timestamps 1389478032 and 1396427599 inside), two "
                 "reductions; " + COND + " [plants: English letter-wise, English multigraph, Latin]",
     "not_covered": "seeds outside the two ranges (time ^ pid, microseconds, the rest of 2^32); other C libraries; " + NOTCOV,
     "null": "the sweep itself", "declares_sweep": True, "sweep_store": S2 + "sweep_rows_top.jsonl",
     "evidence": [S2 + "PREREG.md", S2 + "RESULTS.md", S2 + "results.json", S2 + "hist.json", S2 + "control.json"],
     "reproduce": "cd " + S2 + " && python3 run_s2.py sweep 4 && python3 run_s2.py finalize",
     "supersedes": [], "superseded_by": None,
     "reopens_if": "the full 2^32 is run (about ten core-hours with this kernel) and a pair clears; or a reason for a seed outside the ranges"},
]
json.dump(rows, open(os.path.join(HERE, "ledger_rows.json"), "w"), indent=1, ensure_ascii=False)
led_path = os.path.join(cm.lp2.LP, "LEDGER.json")
led = json.load(open(led_path, encoding="utf-8"))
ids = {r["id"] for r in rows}
led["entries"] = [e for e in led["entries"] if e["id"] not in ids] + rows
c = collections.Counter(e["status"] for e in led["entries"])
led["counts"] = {"total": len(led["entries"]), "by_status": dict(sorted(c.items()))}
with open(led_path, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(led, indent=1, ensure_ascii=False) + "\n")
print("ledger:", led["counts"])
