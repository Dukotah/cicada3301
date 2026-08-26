"""I2 / G-SPEED — microseconds per decode, and the component breakdown.

Phase 2 calls `adjudicate()` tens of millions of times, so the gate is:
adjudicating one 240-rune decode must cost no more than 3x the legacy `score_norm`.

    python3 speed.py     -> out_speed.json
"""
import json
import os
import sys
import timeit

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import adjudicate as AJ                       # noqa: E402

N = 29
# Sibling lanes share this box.  Short bursts (number=500 ~ 15 ms) taken min-of-15 are far
# more likely to catch an uncontended scheduling window than a few long ones, and the
# load average at measurement time is recorded so a contended run is visible, not silent.
REPS = 500
BEST_OF = 15


def bench(fn, reps=REPS, best_of=BEST_OF):
    t = min(timeit.repeat(fn, number=reps, repeat=best_of))
    return t / reps * 1e6                     # microseconds/call


def main():
    pan = AJ.panel()
    q = AJ.quad()
    rng = np.random.default_rng(19)
    out = {"lane": "round19/I2/speed", "reps": REPS, "best_of": BEST_OF,
           "machine": {"python": sys.version.split()[0], "numpy": np.__version__,
                       "loadavg_at_start": list(os.getloadavg()),
                       "cpu_count": os.cpu_count()},
           "lengths": {}}

    TRIALS = 5
    for L in (120, 240, 400):
        X = rng.integers(0, N, size=(64, L))
        xs = [X[i] for i in range(64)]
        ts = [AJ.idx_to_trans(x) for x in xs]
        c = {"i": 0}

        def nxt():
            c["i"] = (c["i"] + 1) & 63
            return c["i"]

        # Sibling lanes share this machine.  Repeat the whole (score_norm, adjudicate) pair
        # TRIALS times and keep the trial with the smallest score_norm, i.e. the least
        # contended window.  Both halves of the ratio come from the SAME trial, so a
        # contended trial cannot flatter or penalise the ratio.
        trials = []
        for _ in range(TRIALS):
            a = bench(lambda: q.score_norm(ts[nxt()]))
            b = bench(lambda: AJ.adjudicate(xs[nxt()]))
            trials.append((a, b))
        trials.sort(key=lambda ab: ab[0])
        ratios = sorted(b / a for a, b in trials)
        t_score, t_full = trials[0]
        t_trans = bench(lambda: AJ.idx_to_trans(xs[nxt()]))
        t_legacy = t_score + t_trans
        t_nolegacy = bench(lambda: AJ.adjudicate(xs[nxt()], translit=ts[nxt()]))
        parts = {
            "panel_raw": bench(lambda: pan.raw(xs[nxt()])),
            "ioc": bench(lambda: AJ.ioc_n(xs[nxt()])),
            "min_distinct": bench(lambda: AJ.min_distinct(xs[nxt()])),
            "h2": bench(lambda: AJ.h2_cond(xs[nxt()])),
            "zlib_ratio": bench(lambda: AJ.zlib_ratio(xs[nxt()])),
            "cal_lookup": bench(lambda: pan.cal(L)),
            "idx_to_trans": t_trans,
            "score_norm": t_score,
        }
        XB = rng.integers(0, N, size=(2048, L))
        t_batch = min(timeit.repeat(lambda: AJ.adjudicate_batch(XB),
                                    number=1, repeat=5)) / 2048 * 1e6

        out["lengths"][str(L)] = {
            "us_score_norm_only": t_score,
            "us_legacy_pipeline_incl_translit": t_legacy,
            "us_adjudicate_full": t_full,
            "us_adjudicate_translit_supplied": t_nolegacy,
            "us_adjudicate_batch_panel_only_per_row": t_batch,
            "ratio_vs_score_norm": t_full / t_score,
            "ratio_trials_sorted": ratios,
            "ratio_median_over_trials": ratios[len(ratios) // 2],
            "ratio_min_over_trials": ratios[0],
            "n_trials": TRIALS,
            "ratio_vs_legacy_pipeline": t_full / t_legacy,
            "components_us": parts,
            "decodes_per_second_single": 1e6 / t_full,
            "decodes_per_second_batch_panel_only": 1e6 / t_batch,
        }
        r = out["lengths"][str(L)]
        print(f"L={L:3d}  score_norm {t_score:7.1f} us   adjudicate {t_full:7.1f} us   "
              f"ratio {r['ratio_vs_score_norm']:5.2f}x  (trial ratios "
              + " ".join(f"{v:.2f}" for v in ratios) + ")"
              f"   batch(panel only) {t_batch:6.1f} us")
        for k, v in sorted(parts.items(), key=lambda kv: -kv[1]):
            print(f"        {k:16s} {v:7.1f} us")

    out["machine"]["loadavg_at_end"] = list(os.getloadavg())
    r240 = out["lengths"]["240"]
    out["gate_G_SPEED"] = {
        "rule": "adjudicate(240 runes) <= 3 x score_norm(240 runes)",
        "us_adjudicate": r240["us_adjudicate_full"],
        "us_score_norm": r240["us_score_norm_only"],
        "ratio": r240["ratio_vs_score_norm"],
        "ratio_min_over_trials": r240["ratio_min_over_trials"],
        "ratio_median_over_trials": r240["ratio_median_over_trials"],
        "us_adjudicate_minus_legacy": (r240["us_adjudicate_full"]
                                       - r240["us_legacy_pipeline_incl_translit"]),
        "context_us_beam_decode_240": 134300.0,
        "context_note": ("one beam_decode(beam_w=400, max_skip=3) at L=240 costs ~134,300 us "
                         "on this machine, so the adjudicator is ~0.1 % of the decode it "
                         "adjudicates. The gate compares against score_norm alone and is "
                         "reported as pre-registered; see RESULTS.md s6 for why that "
                         "comparison turns out to measure the wrong quantity."),
        "verdict": "PASSED" if r240["ratio_vs_score_norm"] <= 3.0 else "FAILED",
    }
    print("\nG-SPEED:", out["gate_G_SPEED"]["verdict"],
          f"({out['gate_G_SPEED']['ratio']:.2f}x, limit 3.00x)")
    json.dump(out, open(os.path.join(HERE, "out_speed.json"), "w"), indent=1)
    print("wrote out_speed.json")


if __name__ == "__main__":
    main()
