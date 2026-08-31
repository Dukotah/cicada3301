"""P3c -- re-measure T3's section-5 decode-DERAIL curve and I3's drift-on-OE pmax shortfall
under the REPAIRED drift_rec beam.

Both were measured on the OLD keyskip1 beam:
  - T3 S5 (out_decode_L*.json): fastbeam.beam_decode (keyskip1, max_skip=3) -> K-REC k=450,
    derail 0.17 @k=200, 0.50 @k=450, 1.00 @k=900 at full-book length. T3 S7 conditional 2
    EXPLICITLY asks for this to be re-run under drift_rec: "whose larger skip budget may be
    either more robust (it can absorb a spurious advance) or less (it can absorb a WRONG one).
    This lane does not know which, and says so."
  - I3 S7.2 (out_plants.json): the drift preset's OE median pmax = 13.40 vs the drift pmax bar
    13.842 (N=1e6, a=0.01) -- shortfall 0.44, G-RECOVER FAILED on OE.

This lane closes both by measuring them on driftbeam PRESETS["drift"] (max_skip=40, max_free=2,
lam=12, start_slack=2 -- the repaired preset). Design mirrors T3.t3_decode.cell exactly, but
swaps the decoder:
  plaintext (LP1_REAL / KJV) -> encipher_keyskip(supp=0.83) -> corrupt k runes ->
  decode with the CORRECT key through driftbeam(drift)  (vs T3's fastbeam keyskip1)
and records rune-INDEX recovery, derail vs the rigid-true-key-index reference, and n_skips error.

k=0 control (PREREG P3c): recovery >= 0.99 and correct/wrong separation under BOTH beams,
proving the re-baseline instrument is wired right before its derail curve is trusted.

Run:
  python3 p3c_drift_rebaseline.py derail [L] [REPS]   # the derail curve, both beams
  python3 p3c_drift_rebaseline.py oe [nrep]            # OE pmax shortfall re-measure
  python3 p3c_drift_rebaseline.py all
"""
import hashlib
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R19 = os.path.join(LP, "analysis", "round19")
for _p in (os.path.join(R19, "I1"), os.path.join(R19, "I2"),
           os.path.join(R19, "I3"), os.path.join(R19, "T3"),
           os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round18", "L2-filter-leak"),
           os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext"),
           os.path.join(LP, "analysis", "round18", "L7-redteam")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import skipdecode as sk            # noqa: E402
import fastbeam                    # noqa: E402
import driftbeam as DB             # noqa: E402
from lp import gematria as gp      # noqa: E402

SUPP = 0.83
BEAM_W = 400
N = 29


def keystream(seed, n):
    out, ctr = [], 0
    while len(out) < n:
        h = hashlib.sha256(f"{seed}:{ctr}".encode()).digest()
        out.extend(b % 29 for b in h)
        ctr += 1
    return out[:n]


def _txt_to_idx(up, limit=None):
    two = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 2}
    one = {t: i for i, t in gp.IDX_TO_TRANS.items() if len(t) == 1}
    idxs, i = [], 0
    while i < len(up) and (limit is None or len(idxs) < limit):
        if up[i:i + 2] in two:
            idxs.append(two[up[i:i + 2]]); i += 2
        elif up[i] in one:
            idxs.append(one[up[i]]); i += 1
        else:
            i += 1
    return idxs


def kjv_plaintext(n):
    txt = open(os.path.join(LP, "data", "kjv.txt"), encoding="utf-8", errors="ignore").read()
    up = "".join(ch for ch in txt.upper() if ch.isalpha())
    up = up.replace("K", "C").replace("V", "U").replace("Q", "C").replace("Z", "S")
    return _txt_to_idx(up, n)


def band(v):
    v = sorted(v)
    n = len(v)
    return {"median": statistics.median(v), "mean": statistics.fmean(v),
            "p05": v[max(0, int(0.05 * n) - 1)], "p95": v[min(n - 1, int(0.95 * n))]}


def _decode(beam, Cn, K):
    """Decode Cn with key K under `beam` in {'keyskip1','drift'}; return (plain_idx, n_skips)."""
    if beam == "keyskip1":
        r = fastbeam.beam_decode(Cn, K, sign=-1, beam_w=BEAM_W, max_skip=3)
        return r["plain_idx"], r.get("n_skips")
    else:
        r = DB.beam_decode(Cn, K, sign=-1, o=0, beam_w=BEAM_W, **DB.PRESETS["drift"])
        return r["plain_idx"], r.get("n_skips")


def derail(L=400, REPS=40, beams=("keyskip1", "drift")):
    """The T3 S5 derail curve, both beams, so drift_rec is directly comparable to keyskip1."""
    PT = kjv_plaintext(L * (REPS + 2) + 6000)
    KBOOK = [0, 50, 100, 200, 450, 900]
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "L": L, "reps": REPS, "supp": SUPP, "beam_w": BEAM_W,
           "register": "EN_KJV (L7-A power 1.00)",
           "keyskip1_ref": "T3/out_decode -- fastbeam max_skip=3",
           "drift_kw": DB.PRESETS["drift"], "by_beam": {}}
    for beam in beams:
        rows = []
        for kb in KBOOK:
            kc = round(kb * L / 12956)
            rc_all, derail_all, dsk_all, sep_c, sep_w = [], [], [], [], []
            t0 = time.time()
            for t in range(REPS):
                st = 7 + t * (L + 13)
                P = PT[st % (len(PT) - L): st % (len(PT) - L) + L]
                rng = random.Random(90000 + t)
                K = keystream(f"CICADA3301-{t}", L * 42 + 128)
                KW = keystream(f"WRONGKEY-{t}", L * 42 + 128)
                C, skips, used = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=90000 + t)
                Cn = list(C)
                if kc:
                    for i in rng.sample(range(len(Cn)), min(kc, len(Cn))):
                        Cn[i] = rng.choice([v for v in range(N) if v != Cn[i]])
                pc, ns = _decode(beam, Cn, K)
                pw, _ = _decode(beam, Cn, KW)
                recc = sum(1 for a, b in zip(pc, P) if a == b) / len(P)
                recw = sum(1 for a, b in zip(pw, P) if a == b) / len(P)
                rigid = sum(1 for i, u in enumerate(used)
                            if (Cn[i] - K[u]) % N == P[i]) / len(P)
                rc_all.append(recc)
                sep_c.append(recc); sep_w.append(recw)
                derail_all.append(1.0 if recc < rigid - 0.10 else 0.0)
                ts = sum(skips)
                dsk_all.append(abs((ns if ns is not None else ts) - ts))
            rows.append({
                "k_book": kb, "k_cell": kc, "eps": kb / 12956,
                "recovery_correct": band(rc_all),
                "derail_fraction": sum(derail_all) / len(derail_all),
                "graceful_recovery_expected": 1.0 - kc / L,
                "n_skips_error": band(dsk_all),
                "recovery_wrong_median": statistics.median(sep_w),
                "separated": bool(band(sep_c)["p05"] > statistics.median(sep_w)),
                "secs": round(time.time() - t0, 1)})
            print(f"  [{beam:9s}] k_book={kb:4d} kc={kc:3d}  rec_med={rows[-1]['recovery_correct']['median']:.3f} "
                  f"derail={rows[-1]['derail_fraction']:.2f} nskips_err_p95={rows[-1]['n_skips_error']['p95']:.0f} "
                  f"({rows[-1]['secs']}s)", flush=True)
        krec = next((r["k_book"] for r in rows if r["recovery_correct"]["median"] < 0.90), None)
        out["by_beam"][beam] = {"rows": rows, "K_REC_k_book": krec}
        print(f"  [{beam}] K-REC (median recovery<0.90) at k_book={krec}")
    json.dump(out, open(os.path.join(HERE, f"out_derail_L{L}.json"), "w"), indent=1, default=float)
    print(f"wrote out_derail_L{L}.json")
    return out


def oe_shortfall(nrep=12):
    """Re-measure I3 S7.2's drift-on-OE pmax shortfall under the repaired drift preset.

    I3 measured drift-OE median pmax = 13.40 vs the drift pmax bar 13.842 (shortfall 0.44),
    which is why G-RECOVER FAILED on OE. That was on I3's drift preset -- which IS this repaired
    one (PRESETS['drift'] lam=12,max_free=2). So this re-measures the SAME cell with fresh
    replicates to confirm the shortfall is real and stable, and reports it against the panelmax20
    bar. If the shortfall persists, the fragile-decode-channel bound is confirmed: the drift
    channel cannot lift OE over its own panel-max bar, so OE decodes in Phase S must be ranked
    (n_skips / recovery), not thresholded on pmax."""
    import plants as PL
    sys.path.insert(0, os.path.join(HERE))
    import nullcurve19 as NC
    import panelmax20 as PM
    rows = PL.p3_recover(L=120, nrep=nrep, presets=("drift", "exact"))
    import numpy as np
    out = {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "nrep": nrep, "by_preset": {}}
    for preset in ("drift", "exact"):
        bar = PM.panelmax_bar(preset=preset, n_round_adjudicated=10 ** 6, alpha=0.01)
        tbl = {}
        for reg in sorted({r["register"] for r in rows}):
            cor = [r for r in rows if r["preset"] == preset and r["register"] == reg
                   and r["arm"] == "correct"]
            if not cor:
                continue
            pv = np.array([r["pmax"] for r in cor])
            tbl[reg] = {"median_pmax": float(np.median(pv)),
                        "pmax_bar_1e6": bar,
                        "shortfall": float(bar - np.median(pv)),
                        "power_at_bar": float((pv >= bar).mean()),
                        "median_recovery": float(np.median([r["recovery"] for r in cor]))}
        out["by_preset"][preset] = {"pmax_bar_1e6": bar, "by_register": tbl}
    json.dump(out, open(os.path.join(HERE, "out_oe_shortfall.json"), "w"), indent=1, default=float)
    d = out["by_preset"]["drift"]["by_register"].get("OE", {})
    print(f"wrote out_oe_shortfall.json")
    print(f"  drift OE: median_pmax={d.get('median_pmax'):.3f} bar={d.get('pmax_bar_1e6'):.3f} "
          f"shortfall={d.get('shortfall'):.3f} power={d.get('power_at_bar'):.2f} "
          f"(I3 ref: 13.40 vs 13.842, shortfall 0.44)")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "derail":
        L = int(sys.argv[2]) if len(sys.argv) > 2 else 400
        REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        derail(L=L, REPS=REPS)
    elif cmd == "oe":
        oe_shortfall(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    elif cmd == "all":
        derail(L=400, REPS=40)
        oe_shortfall(12)
    else:
        raise SystemExit(cmd)
