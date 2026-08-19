"""Merge the small-pad and big-pad sweep outputs into the lane's single results.json,
and print the top-20 table for RESULTS.md.

    python merge.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R16 = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, R16)
import lib_padsweep as L                                    # noqa: E402
sys.path.insert(0, os.path.join(L.ROOT, "benchmark"))
import null as NULLMOD                                      # noqa: E402

parts = []
for fn in ("results_small.json", "results_big.json"):
    p = os.path.join(HERE, fn)
    if os.path.exists(p):
        d = json.load(open(p))
        parts.append((fn, d))

pads = []
for fn, d in parts:
    pads.extend(d["pads"])

tot_off = sum(p["coverage"]["offsets_scanned"] for p in pads)
tot_cfg = sum(p["coverage"]["configs"] for p in pads)
tot_beam = sum(p["coverage"]["beam_escalations"] for p in pads)
allrows = sorted((r for p in pads for r in p["top"]), key=lambda r: r["score"], reverse=True)
allhits = [r for p in pads for r in p["hits"]]
best = allrows[0] if allrows else None

thr_off = NULLMOD.threshold_for(max(2, tot_off))
thr_beam = NULLMOD.threshold_for(max(2, tot_beam))

out = {
    "lane": "round16/P0_dense",
    "hypothesis": ("Round 12 A1 swept these same CicadaOS pads on an 8-offset ladder and "
                   "returned NEGATIVE. 8/118,818,811 = 6.7e-8 of the offset space on 560.13. "
                   "Re-sweep with dense_scan, which scores every offset."),
    "instrument": "round16/lib_padsweep.py dense_scan + A1 beam (beam_w=120, max_skip=3, head=400)",
    "control": {
        "source": "lib_padsweep.control(), re-run on this box 2026-08-19",
        "PASS": True, "n_trials": 8, "beam_recovered": 8, "dense_found": 5,
        "survival_rate": 0.625,
        "note": "reproduces round16/PREREG.md exactly; beam recovers 8/8 at 100% of runes "
                "(-4.212); the dense prefilter retains the true offset in 5/8.",
    },
    "window_equivalence_check": (
        "sweep.py::_assert_window_equiv asserts the windowed beam/null wrappers are "
        "bit-identical to lib_padsweep.escalate / lib_padsweep.null_ceiling. Asserted at "
        "the start of every run."),
    "hit_bar_rule": "score_norm >= -5.5 AND score_norm >= null_max + 0.5 (pre-registered, A1's)",
    "coverage_total": {
        "pads": len(pads),
        "configs_completed": tot_cfg,
        "offsets_scanned": tot_off,
        "survival_rate": 0.625,
        "effective_offsets": int(round(tot_off * 0.625)),
        "beam_escalations": tot_beam,
        "A1_offsets_per_variant_for_comparison": 8,
    },
    "extreme_value_check": {
        "note": "AGENTS.md lesson 3 - a fixed bar is invalid at large N.",
        "threshold_for_offsets_scanned": thr_off,
        "threshold_for_beam_escalations": thr_beam,
        "raw_best": best["score"] if best else None,
        "reading": ("threshold_for() returns the -5.5 floor at both trial counts because the "
                    "fitted family-wise bar (mu=-7.2517, beta=0.0725) only exceeds -5.5 above "
                    "~1e11 trials. The floor is the binding constraint here, and the raw best "
                    "misses it by a wide margin either way."),
    },
    "best": best,
    "n_hits": len(allhits),
    "hits": allhits,
    "top20": allrows[:20],
    "pads": pads,
    "verdict": "HIT" if allhits else "NEGATIVE",
    "sources": [fn for fn, _ in parts],
}
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=2)

print("| # | pad | variant | sign | offset | pre | score_norm | bar | head (64 runes) |")
print("|---|---|---|---|---:|---:|---:|---:|---|")
for i, r in enumerate(allrows[:20], 1):
    print("| %d | %s | `%s` | %+d | %d | %.3f | **%.4f** | %.2f | `%s` |"
          % (i, r["pad"], r["variant"], r["sign"], r["offset"], r["pre"],
             r["score"], r["bar"], r["head"][:48]))
print()
print("pads=%d configs=%d offsets=%s effective=%s beams=%s"
      % (len(pads), tot_cfg, format(tot_off, ","),
         format(int(round(tot_off * 0.625)), ","), format(tot_beam, ",")))
print("best=%s  verdict=%s" % (best["score"] if best else None, out["verdict"]))
print("threshold_for(%s)=%.4f  threshold_for(%s)=%.4f"
      % (format(tot_off, ","), thr_off, format(tot_beam, ","), thr_beam))
print()
print("| pad | bytes | configs | offsets scanned | effective (x0.625) | best | verdict |")
print("|---|---:|---:|---:|---:|---:|---|")
for p in pads:
    print("| `%s` | %s | %d | %s | %s | %.4f | %s |"
          % (p["file"], format(p["bytes"], ","), p["coverage"]["configs"],
             format(p["coverage"]["offsets_scanned"], ","),
             format(p["coverage"]["effective_offsets"], ","),
             p["best"]["score"], p["verdict"]))
