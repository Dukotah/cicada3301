#!/usr/bin/env python3
"""Round 27 — ORACLE adjudication driver for S1 claim-bar crossers (parameterized).

Adapted verbatim from oracle_35563892.py (the adjudicated-of-record driver for the
first crosser); identical protocol (MONITORING.md "If HIT-CANDIDATE.json appears"):
  1. Re-score the seed with the Python R25 reference (runner.stage_a via pyref) and
     require C-vs-Python pmax agreement <= 1e-6 (else K4: PARITY-VOID).
  2. Run the hitfn20 3-clause gate (panel-max-null-clear AND recovery >= 0.90 AND
     held-out 3/4 reproduction >= 0.90), adjudicate.py as adjudicator of record.
  3. Print the decoded text (first ~200 transliterated chars) + firing panel register.

Read-only w.r.t. the running sweep; writes nothing but stdout JSON.
Run:  nice -n 15 python3 oracle_crosser.py <seed> <c_pmax>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P2 = os.path.join(HERE, "P2-harness")
if P2 not in sys.path:
    sys.path.insert(0, P2)

import pyref                       # noqa: E402  imports the R25 pipeline VERBATIM
from pyref import runner, AD, H    # noqa: E402

CLAIM_BAR_S1 = 7.3835202943286884
PARITY_TOL = 1e-6


def main(seed, c_pmax):
    out = {"seed": seed, "lane": "S1", "c_pmax": c_pmax, "claim_bar": CLAIM_BAR_S1}

    # ---- 1. Python reference stage_a (L=120 screen) — parity vs the C engine
    a = pyref.stage_a_full(seed)
    py_pmax = a["pmax"]
    delta = abs(py_pmax - c_pmax)
    out["py_stage_a_pmax"] = repr(py_pmax)
    out["parity_abs_delta"] = repr(delta)
    out["parity_ok"] = delta <= PARITY_TOL
    if not out["parity_ok"]:
        out["verdict"] = "PARITY-VOID"   # K4: halt, parity is void
        print(json.dumps(out, indent=1))
        return 4

    # stage-A adjudication record (adjudicator of record = round19/I2 adjudicate.py)
    adj_a = AD.adjudicate(a["plain_idx"])
    out["stage_a"] = {
        "n": adj_a["n"], "pmax": adj_a["pmax"],
        "preg": adj_a["preg"], "preg_name": AD.panel().registers[adj_a["preg"]],
        "en": adj_a["en"], "ioc": adj_a["ioc"], "mds": adj_a["mds"],
        "h2": adj_a["h2"], "zl": adj_a["zl"], "z": [round(v, 3) for v in adj_a["z"]],
        "translit_full": AD.idx_to_trans(a["plain_idx"]),
    }

    # ---- 2. hitfn20 3-clause gate on the L=240 hit window (exactly runner.stage_b)
    K = runner.word_stream(seed, runner.L_HIT * 6 + 64)
    dec = H.HitDecode(C=runner.C_HIT, K=K, o=0, preset=runner.PRESET,
                      n_round_adjudicated=10 ** 6)
    v = H.evaluate(dec)
    d = dec._decoded
    adj_b = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    out["stage_b"] = {
        "hit": bool(v.hit), "reason": v.reason,
        "clause1_pmax": v.pmax, "clause1_bar": v.bar, "clause1_clears_null": bool(v.clears_null),
        "clause2_recovery": v.recovery, "clause2_ok": bool(v.recovery_ok),
        "clause2_source": v.recovery_source,
        "clause3_heldout": v.heldout_recovery, "clause3_ok": bool(v.heldout_ok),
        "preg": v.preg, "preg_name": v.preg_name,
        "beam_score": v.score, "n": v.n,
        "ioc": adj_b["ioc"], "mds": adj_b["mds"], "h2": adj_b["h2"], "zl": adj_b["zl"],
        "z": [round(x, 3) for x in adj_b["z"]],
    }

    # ---- 3. decoded "plaintext" sample (first ~200 transliterated chars)
    translit = AD.idx_to_trans(d["plain_idx"])
    out["decoded_sample_240win_first200"] = translit[:200]

    out["verdict"] = "HIT-TRUE-FLAGGED-FOR-ORACLE" if v.hit else "NOISE-CROSSER"
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), float(sys.argv[2])))
