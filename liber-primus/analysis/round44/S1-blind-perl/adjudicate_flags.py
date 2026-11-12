"""Lane S1, adjudication of the weak flags (POST-DATA; see RESULTS.md).

The sweep left 19 seed-mode pairs with full-page IoC x 29 between 1.40 and 1.433: weak flags by the
PREREG addendum. Fourteen of them are not "null-consistent" by the addendum's crude decay rule, so
they are owed an oracle step. This script does three things, each with a control, and says so
plainly that they were chosen after the flags were seen:

  A. tail shape   - how many pairs sit at each level of the full-page statistic, here and in lane S2.
                    A true key is an isolated point near the plants (>= 1.61); the tail of the null
                    is a smooth geometric decay.
  B. back half    - IoC of runes 120..261 of the decode alone, along the best full-page path. A true
                    key decodes the back half as well as the front; a head fluke does not.
  C. reading      - the decode is solved as a simple substitution of English (the adjudicator is blind
                    to how the plaintext is labelled, so "reading" a flag means exactly this). Controls:
                    relabelled English plants decoded by the same path search, and wrong-key decodes.

Output: flags_adjudication.json.
"""
import collections
import json
import math
import os
import random
import struct
import sys

import common as cm
import run_s1 as s1

N = cm.N
HERE = cm.HERE
L1, L2, L3 = s1.L1, s1.L2, s1.L3
C = cm.lp2.idx(cm.lp2.unsolved())[0]
res = json.load(open(os.path.join(HERE, "results.json")))
out = {"post_data": True}


def ioc(x):
    c = collections.Counter(x); n = len(x)
    return N * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


# ---- A. tail shape
def tail(path, fmt, idx):
    raw = open(path, "rb").read(); sz = struct.calcsize(fmt)
    v = [cm.ioc29(struct.unpack_from(fmt, raw, o)[idx], L3) for o in range(0, len(raw), sz)]
    return {f"{t:.2f}": sum(x >= t for x in v) for t in (1.30, 1.32, 1.34, 1.36, 1.38, 1.40, 1.42, 1.44, 1.50, 1.60)}


out["tail_counts_S1_perl"] = tail(os.path.join(HERE, "survivors.bin"), "<5I", 4)
p2 = os.path.join(HERE, "..", "S2-blind-glibc-clock", "survivors.bin")
if os.path.exists(p2):
    out["tail_counts_S2_glibc"] = tail(p2, "<B5I", 5)
    out["pairs"] = {"S1": res["pairs_evaluated"], "S2": 4 * 181125632}
print("pairs at or above each level of the full-page statistic:")
print("  S1 (1.72e10 pairs):", out["tail_counts_S1_perl"])
print("  S2 (7.2e8 pairs):  ", out.get("tail_counts_S2_glibc"))

# ---- quadgram model for C
qg = {}
tot = 0
for line in open(os.path.join(cm.lp2.LP, "data", "english_quadgrams.txt")):
    q, c = line.split(); qg[q] = int(c); tot += int(c)
FLOOR = math.log10(0.01 / tot)
LOGQ = {q: math.log10(c / tot) for q, c in qg.items()}
LET = "ETAOINSHRDLCUMWFGYPBVKJXQZ"


def solve(dec, rng, restarts=10, iters=4000):
    """Solve the decode as a simple substitution of English: an INJECTIVE map from the 26 most frequent
    decode symbols to the 26 letters (any rarer symbols share X), hill-climbed by swaps on quadgram score.
    Returns (mean log10 quadgram probability, text)."""
    syms = sorted(set(dec), key=lambda s: -dec.count(s))
    main, rest = syms[:26], syms[26:]

    def text(perm):
        m = {s: perm[k] for k, s in enumerate(main)}
        m.update({s: "X" for s in rest})
        return "".join(m[d] for d in dec)

    def score(perm):
        t = text(perm)
        return sum(LOGQ.get(t[i:i + 4], FLOOR) for i in range(len(t) - 3)) / (len(t) - 3)

    best = (-99, "")
    for r in range(restarts):
        perm = list(LET)
        if r:
            for _k in range(8):
                a, b = rng.sample(range(26), 2); perm[a], perm[b] = perm[b], perm[a]
        cur = score(perm)
        for _i in range(iters):
            a, b = rng.sample(range(26), 2)
            perm[a], perm[b] = perm[b], perm[a]
            sc = score(perm)
            if sc >= cur:
                cur = sc
            else:
                perm[a], perm[b] = perm[b], perm[a]
        if cur > best[0]:
            best = (cur, text(perm))
    return best


rng = random.Random(4405)
# ---- controls: plants (random relabelling, both spellings) and wrong-key decodes, through the same path search
T = cm.plant_texts()
ctrl_plant, ctrl_null = [], []
for k in range(10):
    tname = ["English letter-wise", "English multigraph"][k % 2]
    K = [rng.randrange(N) for _ in range(420)]
    Cp, _ = cm.make_plant(rng, T[tname], "random relabelling", cm.CONSTRUCTIONS[k % 3], K, L=L3, sign=+1)
    q = 1 if k % 3 == 0 else 2
    ssq, dec = s1.best_path(Cp, K, +1, q, L3, 24)
    sc, txt = solve(dec, rng)
    ctrl_plant.append({"text": tname, "ioc_x29_full": cm.ioc29(ssq, L3), "ioc_x29_front": ioc(dec[:120]), "ioc_x29_back": ioc(dec[120:]),
                       "solve_score": sc, "reading": txt[:80]})
    print(f"plant   {tname:20s} full {cm.ioc29(ssq, L3):.3f} front {ioc(dec[:120]):.3f} back {ioc(dec[120:]):.3f}  solve {sc:.3f}  {txt[:60]}", flush=True)
for k in range(10):
    K = [rng.randrange(N) for _ in range(420)]
    ssq, dec = s1.best_path(C, K, +1, 1 + k % 2, L3, 24)
    sc, txt = solve(dec, rng)
    ctrl_null.append({"ioc_x29_full": cm.ioc29(ssq, L3), "ioc_x29_back": ioc(dec[120:]), "solve_score": sc})
    print(f"wrong key                    full {cm.ioc29(ssq, L3):.3f} back {ioc(dec[120:]):.3f}  solve {sc:.3f}", flush=True)
out["controls"] = {"plants": ctrl_plant, "wrong_keys": ctrl_null}

# ---- the flags
flags = []
for f in res["flagged"]:
    s = +1 if f["mode"].startswith("s=+1") else -1; q = int(f["mode"][-1])
    ssq, dec = s1.best_path(C, cm.perl_stream(f["seed"], 420), s, q, L3, 24)
    sc, txt = solve(dec, rng)
    row = {"seed": f["seed"], "mode": f["mode"], "ioc_x29_full": cm.ioc29(ssq, L3), "ioc_x29_front": ioc(dec[:120]),
           "ioc_x29_back": ioc(dec[120:]), "decay_L120_to_L262": f["ioc_x29_L120"] - f["ioc_x29_L262"],
           "null_consistent_by_prereg_decay_rule": f["ioc_x29_L120"] - f["ioc_x29_L262"] > 0.15,
           "solve_score": sc, "best_english_reading_under_any_relabelling": txt[:120]}
    flags.append(row)
    print(f"FLAG {f['seed']:>10d} {f['mode']}  full {row['ioc_x29_full']:.3f} front {row['ioc_x29_front']:.3f} back {row['ioc_x29_back']:.3f}  "
          f"solve {sc:.3f}  {txt[:60]}", flush=True)
out["flags"] = flags
pb = [x["ioc_x29_back"] for x in ctrl_plant]; ps = [x["solve_score"] for x in ctrl_plant]
ns = [x["solve_score"] for x in ctrl_null]
out["summary"] = {"plants_back_half_min": min(pb), "flags_back_half_max": max(x["ioc_x29_back"] for x in flags),
                  "plants_solve_score_min": min(ps), "wrong_key_solve_score_max": max(ns),
                  "flags_solve_score_max": max(x["solve_score"] for x in flags),
                  "all_flags_below_plants_on_back_half": max(x["ioc_x29_back"] for x in flags) < min(pb),
                  "all_flags_below_plants_on_reading": max(x["solve_score"] for x in flags) < min(ps)}
json.dump(out, open(os.path.join(HERE, "flags_adjudication.json"), "w"), indent=1)
print(json.dumps(out["summary"], indent=1))
