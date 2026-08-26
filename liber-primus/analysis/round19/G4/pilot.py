"""ROUND 19 / G4 — PILOT.  NOT A RESULT.

Exactly 10 000 decodes of the pgf DEFAULT-SEED space through I1's drift-tolerant beam and
I2's nine-register adjudicator, written as a `SWEEPROW/1` store and validated with I2's
own `validate_store`.

WHAT THIS IS FOR: plumbing and timing, so `READY.md`'s Phase-2 cost figures are measured
rather than guessed, and so S1 inherits a store that I2's validator already accepts. The
10 000 are split across all three I1 presets because the presets differ in cost by more
than two orders of magnitude, and Phase 2's budget is decided by that ratio.

WHAT THIS IS NOT: a search. Round 19's hold says no G-lane adjudicates anything until
I1/I2/I3 have all PASSED their gates, and at the time of writing this lane had not seen
those verdicts. Every score below is therefore recorded and **explicitly not
interpreted**; no candidate is escalated from it, and it establishes no bound on
anything. The header carries `pilot: true` and `interpretable: false` so a later lane
reading the store cannot mistake it for coverage.

    python3 pilot.py
"""
from __future__ import annotations

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, os.path.join(R19, "I1"))
sys.path.insert(0, os.path.join(R19, "I2"))
sys.path.insert(0, HERE)

import lib_numchannel as nc            # noqa: E402
import driftbeam as db                 # noqa: E402
import adjudicate as adj               # noqa: E402
import gen_tex as gt                   # noqa: E402

N = 29
L = 120                                # B-04 stage-A segment length
YEAR = 2013
# (preset, n_seeds) -> n_seeds x sign(2) x atbash(2) x direction(2) decodes
CELLS = [("exact", 1000), ("pair", 125), ("drift", 125)]


def main():
    C0 = list(nc.unsolved()[:L])
    C1 = [(N - 1) - c for c in C0]

    store = os.path.join(HERE, "pilot_sweeprows.jsonl")
    hdr = adj.header(
        "round19/G4/PILOT-pgf-default-seed",
        pilot=True, interpretable=False,
        key_space=("pgf \\pgfmathrandominteger{}{0}{28}; seed = \\time x \\year with "
                   "year=%d; sign in {-1,+1}; atbash in {0,1}; direction in {fwd,rev}; "
                   "offset 0 (offsets are absorbed into the phase for a single-cycle "
                   "Lehmer generator — see G4/PREREG.md Q3)" % YEAR),
        decoder="round19/I1 driftbeam, presets %s" % {k: db.PRESETS[k] for k, _ in CELLS},
        adjudicator="round19/I2 adjudicate() nine-register panel",
        generator_validation="round19/G4/validation.json — V1 PASS, byte-exact vs real pdflatex",
        segment="unsolved_head L=%d" % L,
        notes=("PILOT ONLY. Round 19's Phase-0 gates had not been read as PASS when this "
               "ran; scores are recorded and NOT interpreted. Proof of plumbing and a "
               "throughput measurement, not coverage."),
    )

    keytable, timing = [], {}
    n = 0
    t_all = time.time()
    with open(store, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(hdr) + "\n")
        for preset, nseed in CELLS:
            kw = dict(db.PRESETS[preset])
            t0, n0 = time.time(), n
            for t in range(nseed):
                seed = t * YEAR
                base = gt.make_ks("pgf_mod29", seed, L * (kw["max_skip"] + 2) + 256)
                for direction in ("fwd", "rev"):
                    K = base if direction == "fwd" else base[::-1]
                    for ab in (0, 1):
                        C = C0 if ab == 0 else C1
                        for sign in (-1, 1):
                            bd = db.beam_decode(C, K, sign=sign, o=0, beam_w=400, **kw)
                            res = adj.adjudicate(bd["plain_idx"], translit=bd["translit"])
                            keytable.append([preset, seed, direction, ab, sign,
                                             bd["n_skips"], bd["n_unexplained"]])
                            fh.write(json.dumps(adj.to_row(res, n)) + "\n")
                            n += 1
            dt = time.time() - t0
            timing[preset] = {"decodes": n - n0, "elapsed_s": round(dt, 1),
                              "s_per_decode": round(dt / max(1, n - n0), 5),
                              "decodes_per_s": round((n - n0) / dt, 1),
                              "kwargs": kw}
            print(preset, timing[preset], flush=True)
    dt_all = time.time() - t_all

    json.dump({"fields": ["preset", "seed", "direction", "atbash", "sign",
                          "n_skips", "n_unexplained"], "rows": keytable},
              open(os.path.join(HERE, "pilot_keytable.json"), "w", encoding="utf-8"))

    ok, err = True, None
    try:
        adj.validate_store(store)
    except Exception as e:                                  # noqa: BLE001
        ok, err = False, f"{type(e).__name__}: {e}"

    ex, dr = timing["exact"]["s_per_decode"], timing["drift"]["s_per_decode"]
    out = {
        "lane": "round19/G4", "label": "PILOT — NOT A RESULT",
        "decodes": n, "elapsed_s": round(dt_all, 1), "segment_len": L,
        "per_preset": timing,
        "drift_over_exact_cost_ratio": round(dr / ex, 1) if ex else None,
        "store": os.path.basename(store),
        "store_validates_against_I2": ok, "validator_error": err,
        "interpretation": ("NONE. Scores in the store are not interpreted and no candidate "
                           "is escalated. Phase 2 (S1) adjudicates, after I1/I2/I3 PASS."),
    }
    json.dump(out, open(os.path.join(HERE, "pilot_results.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
