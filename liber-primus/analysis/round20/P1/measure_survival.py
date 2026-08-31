"""Round 20 / P1 -- plant skip_by_two keys over all 9 registers on REAL Marsaglia bytes and
measure per-register true-key survival through the sieve (the survival SURFACE, Q1/Q4).

Design is C2 §4's paired design, VERBATIM where possible:
  - plants go into REAL hash-verified Marsaglia pads (mod29), NOT synthetic sha256 -- the honest
    high-entropy control C2 used and where the English filter measured 0.000 on vowel-dropped EN.
  - the SAME (pad, true-offset) pairs are used for every register (paired -> register contrast
    is not confounded with pad statistics or offset).
  - plaintext windows come from L7-A's own register panels (a1_scorer_language.build_panels()).
  - the skip loop is skipdecode.encipher_keyskip (Q1: the construction keyskip1 is exact for) and
    encipher-skip_by_two (the L7-B hole; the campaign's motivating case) at supp=0.83.

Everything is seed-3301 rooted / order-preserving.
"""
import os
import sys
import json
import time
import argparse
import random

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for _p in (os.path.join(ROOT, "analysis", "campaign18_skip"),
           os.path.join(ROOT, "analysis", "round18", "L7-redteam"),
           os.path.join(ROOT, "analysis", "round19", "I1"),
           os.path.join(ROOT, "src"), os.path.join(ROOT, "benchmark")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import prefilter20 as PF          # noqa: E402
import skipdecode as sk           # noqa: E402
import constructions as CX        # noqa: E402

N = 29
PLANT_LEN = 120                    # C2/L7-A headline length (the window the plant occupies)
SUPP = 0.83
SEED0 = 33019                      # C2's SEED0, so the plant coins match C2 exactly
DATA = os.path.join(ROOT, "analysis", "round18", "L6-offset-marsaglia", "data", "iso")
REGISTERS = PF.PANEL + ["RAND"]    # 9 panel registers + RAND negative control


def _pad(name, cache={}):
    """A real Marsaglia pad as mod29 symbols (the modal builder C2 used)."""
    if name not in cache:
        a = np.fromfile(os.path.join(DATA, name), dtype=np.uint8)
        cache[name] = (a.astype(np.int64) % N)
    return cache[name]


def _verified_pads():
    v = json.load(open(os.path.join(ROOT, "analysis", "round19", "C2", "out_verify.json")))
    assert v["all_gates_pass"], "Marsaglia hash gates did not pass -- refusing to plant"
    return v["random_data_pads"]


def build_pairs(pad_names, n, minlen, span=10_000_000):
    """C2 build_pairs (paired: pad, true-offset, plaintext-start).  `span` bounds the offset
    range scanned per plant for compute; the true offset is placed inside [1000, span-...].
    span=10_000_000 reproduces C2's full-pad scan exactly."""
    rng = random.Random(SEED0)
    pairs = []
    for t in range(n):
        pn = pad_names[t % len(pad_names)]
        o = rng.randrange(1000, span - PLANT_LEN * 10 - 64)
        ps = rng.randrange(0, minlen - PLANT_LEN - 1)
        pairs.append((pn, o, ps))
    return pairs


def measure(registers, ntrials, W, fA, fB, beam_w, stageB_preset, mech,
            want_langagnostic, span=10_000_000, verbose=True):
    """Return per-register survival (A, B, combined) + reduction, for one frozen param point."""
    PF.register_lms()
    import a1_scorer_language as A1
    panels = A1.build_panels()
    pad_names = _verified_pads()
    minlen = min(len(panels[r]) for r in registers)
    pairs = build_pairs(pad_names, ntrials, minlen, span=span)

    per = {r: {"survA": 0, "survB": 0, "n": 0, "ranksA": [], "reductions": []}
           for r in registers}
    fn = CX.MECH[mech]
    t0 = time.time()
    ndone = 0
    total = len(registers) * ntrials
    for r in registers:
        panel = panels[r]
        for ti, (pn, o_true, ps) in enumerate(pairs):
            Kfull = _pad(pn)
            K = Kfull[:span]                       # bounded offset population
            P = [int(x) for x in panel[ps:ps + PLANT_LEN]]
            Kl = [int(x) for x in K[o_true:]]
            if mech == "keyskip":
                C, skips, _u = sk.encipher_keyskip(P, Kl, sign=-1, supp=SUPP,
                                                   seed=SEED0 + ti)
            else:
                C, info = fn(P, Kl, supp=SUPP, seed=SEED0 + ti)
            res = PF.sieve(C, K, o_true=o_true, sign=-1, W=W, fA=fA, fB=fB,
                           beam_w=beam_w, stageB_preset=stageB_preset,
                           want_langagnostic=want_langagnostic)
            d = per[r]
            d["n"] += 1
            d["survA"] += int(res["survivesA"])
            d["survB"] += int(res["survivesB"])
            d["ranksA"].append(res["rankA"])
            d["reductions"].append(res["reduction"])
            ndone += 1
            if verbose and ndone % 15 == 0:
                print(f"  [{ndone}/{total}] {time.time()-t0:.0f}s", flush=True)
    summ = {}
    for r in registers:
        d = per[r]
        summ[r] = {"n": d["n"],
                   "survivalA": d["survA"] / d["n"],
                   "survivalB": d["survB"] / d["n"],
                   "median_rankA": float(np.median([x for x in d["ranksA"] if x >= 0]))
                   if any(x >= 0 for x in d["ranksA"]) else None,
                   "median_reduction": float(np.median(d["reductions"]))}
    return summ, round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ntrials", type=int, default=15)
    ap.add_argument("--W", type=int, default=32)
    ap.add_argument("--fA", type=float, default=1e-3)
    ap.add_argument("--fB", type=float, default=0.1)
    ap.add_argument("--beam_w", type=int, default=16)
    ap.add_argument("--stageB", default="keyskip1")
    ap.add_argument("--mech", default="skip_by_two")
    ap.add_argument("--langagnostic", action="store_true")
    ap.add_argument("--span", type=int, default=10_000_000)
    ap.add_argument("--registers", default=",".join(REGISTERS))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    regs = [r for r in a.registers.split(",") if r in REGISTERS]
    print(f"[P1] measure: mech={a.mech} W={a.W} fA={a.fA} fB={a.fB} bw={a.beam_w} "
          f"stageB={a.stageB} langagnostic={a.langagnostic} ntrials={a.ntrials}", flush=True)
    summ, wall = measure(regs, a.ntrials, a.W, a.fA, a.fB, a.beam_w, a.stageB,
                         a.mech, a.langagnostic, span=a.span)
    out = {"lane": "round20/P1", "mech": a.mech, "W": a.W, "fA": a.fA, "fB": a.fB,
           "beam_w": a.beam_w, "stageB": a.stageB, "langagnostic": a.langagnostic,
           "ntrials": a.ntrials, "span": a.span, "plant_len": PLANT_LEN, "supp": SUPP,
           "builder": "mod29_marsaglia", "summary": summ, "wall_s": wall}
    print(f"\n  {'register':<14} {'survA':>7} {'survB':>7} {'med_rankA':>10} {'med_red':>9}")
    for r in regs:
        s = summ[r]
        mr = f"{s['median_rankA']:.0f}" if s['median_rankA'] is not None else "None"
        print(f"  {r:<14} {s['survivalA']:>7.3f} {s['survivalB']:>7.3f} {mr:>10} "
              f"{s['median_reduction']:>9.0f}")
    print(f"[P1] wall {wall}s")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)
        print(f"[P1] wrote {a.out}")
    return out


if __name__ == "__main__":
    main()
