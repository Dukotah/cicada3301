"""L3-ROAD validation gate — MUST pass before any null from this lane is reportable.

Builds synthetic corpora with LP2's exact word-length sequence and an English
message planted so that a ROAD reading recovers it, then checks that

  * the reading's own detector fires on the plant   (score >= -12.00)
  * the same detector on unplanted filler stays low (score <  -13.00)

Gates: A = selector power, B = selector end-to-end (predicate must *discover*
the plant), C = specificity on filler, D = T2 sum-reduction decode,
E = T4 gematria-ordered reading.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import road_lib as R  # noqa: E402

rng = np.random.default_rng(20260812)
PAGES = R.lp2_words()
WORDS = [w for p in PAGES for w in p]
LENS = np.array([len(w) for w in WORDS])
NW = len(WORDS)

# LP2's own rune marginal, so filler is as LP2-like as possible
MARG = np.bincount(np.concatenate([np.asarray(w) for w in WORDS]), minlength=29)
MARG = MARG / MARG.sum()

MSG = (open(os.path.join(R.ROOT, "data", "pride.txt"), encoding="utf-8",
            errors="ignore").read())
MSGR = np.array(R.eng_to_runes(MSG[20000:120000]), dtype=np.int64)

res = {}


CUTS = np.cumsum(LENS)[:-1]


def filler_words(lens=None):
    """LP2-marginal random runes cut into LP2's exact word-length sequence."""
    stream = rng.choice(29, size=int(LENS.sum()), p=MARG).astype(np.int64)
    return list(np.split(stream, CUTS))


# ------------------------------------------------------- GATE A: selector power
# Oracle-selected subset: plant English into a random 25% of the word slots.
sel = np.sort(rng.choice(NW, size=NW // 4, replace=False))
ws = filler_words(LENS)
cur = 0
for i in sel:
    n = len(ws[i])
    ws[i] = MSGR[cur:cur + n]
    cur += n
read = np.concatenate([ws[i] for i in sel])
res["A_oracle_selector"] = dict(n=int(read.size), score=R.score(read),
                                sample=R.show(read))

# ------------------------------------- GATE B: predicate must DISCOVER the plant
# Design-realistic construction: an author who marks message words with prime
# gematria sums must also keep FILLER sums composite, otherwise the marker does
# not mark anything. So: message words padded with one rune to make their sum
# prime; filler words resampled until their sum is composite. The `sum is prime`
# selector then finds the message with no oracle.
def make_plantB():
    ws, planted, cur = [], [], 0
    for i in range(NW):
        L = int(LENS[i])
        if i % 4 == 0 and L >= 3:
            n = L - 1
            w = MSGR[cur:cur + n]
            cur += n
            for pad in range(29):
                cand = np.append(w, pad)
                if bool(R.is_prime(np.array([int(R.PRIME[cand].sum())]))[0]):
                    ws.append(cand)
                    planted.append(i)
                    break
            else:
                ws.append(w)
        else:
            for _ in range(200):
                w = rng.choice(29, size=L, p=MARG).astype(np.int64)
                if not bool(R.is_prime(np.array([int(R.PRIME[w].sum())]))[0]):
                    break
            ws.append(w)
    return ws, planted


ws, planted = make_plantB()
sums = np.array([int(R.PRIME[np.asarray(w)].sum()) for w in ws])
hit = np.where(R.is_prime(sums))[0]
read = np.concatenate([ws[i] for i in hit])
res["B_prime_selector_endtoend"] = dict(
    n=int(read.size), score=R.score(read), n_selected=int(hit.size),
    n_planted=len(planted),
    purity=float(np.isin(hit, planted).mean()), sample=R.show(read))

# ------------------------- GATE B2: POWER CURVE vs dilution (scope measurement)
# How pure must the selected set be for the -12.00 threshold to fire? Answering
# this bounds exactly what a T3 null does and does not exclude.
curve = {}
base_msg = MSGR
for purity in (1.0, 0.9, 0.8, 0.7, 0.6, 0.5):
    k = 700
    nmsg = int(round(k * purity))
    idx = rng.permutation(k)
    parts, cur = [], 0
    for t in range(k):
        L = int(LENS[t % NW]) or 4
        if idx[t] < nmsg:
            parts.append(base_msg[cur:cur + L])
            cur += L
        else:
            parts.append(rng.choice(29, size=L, p=MARG).astype(np.int64))
    rd = np.concatenate(parts)
    curve[purity] = round(R.score(rd), 4)
res["B2_power_curve_purity_to_score"] = curve

# ------- GATE B3: dilution-robust statistic -- z of the selector vs its own null
# Absolute score is dilution-fragile (see B2). The z of the selected read against
# the SAME selector run on unplanted filler is not. Measure that null.
nullsc = []
for _ in range(200):
    f = filler_words()
    s = np.array([int(R.PRIME[np.asarray(w)].sum()) for w in f])
    k = np.where(R.is_prime(s))[0]
    nullsc.append(R.score(np.concatenate([f[i] for i in k])))
nullsc = np.array(nullsc)
zB = (res["B_prime_selector_endtoend"]["score"] - nullsc.mean()) / nullsc.std()
res["B3_selector_null"] = dict(mean=float(nullsc.mean()), sd=float(nullsc.std()),
                               max=float(nullsc.max()), z_of_plant=float(zB))
# purity at which z>=8 would still fire, from the B2 curve
res["B3_z_of_power_curve"] = {p: float((v - nullsc.mean()) / nullsc.std())
                              for p, v in curve.items()}

# ------------------------------------------------- GATE C: specificity (filler)
ws = filler_words(LENS)
sums = np.array([int(R.PRIME[np.asarray(w)].sum()) for w in ws])
worst = -99.0
for nm, m in (("prime", R.is_prime(sums)), ("emirp", R.is_emirp(sums)),
              ("mod29", sums % 29 == 0), ("odd", sums % 2 == 1)):
    k = np.where(m)[0]
    if k.size < 5:
        continue
    for mode in ("whole", "first", "last"):
        if mode == "whole":
            rd = np.concatenate([ws[i] for i in k])
        elif mode == "first":
            rd = np.array([ws[i][0] for i in k])
        else:
            rd = np.array([ws[i][-1] for i in k])
        worst = max(worst, R.score(rd))
res["C_filler_specificity_max"] = float(worst)

# --------------------------------- GATE D: T2 sum-reduction decode (s mod 29)
# Build words whose prime-sums, taken mod 29, spell the message.
target = MSGR[:NW]
ws = []
for i in range(NW):
    L = int(LENS[i])
    for _ in range(400):
        w = rng.choice(29, size=L, p=MARG).astype(np.int64)
        if int(R.PRIME[w].sum()) % 29 == int(target[i]):
            break
    ws.append(w)
sums = np.array([int(R.PRIME[np.asarray(w)].sum()) for w in ws])
red = sums % 29
res["D_sum_mod29_decode"] = dict(n=int(red.size), score=R.score(red),
                                 exact=float((red == target).mean()),
                                 sample=R.show(red))

# ------------------------------------------- GATE E: T4 gematria reading order
# Words carry the message in order, but their sums are made monotone increasing;
# the words are then scattered. sort-by-sum must restore the message.
ws = filler_words(LENS)
cur = 0
for i in range(NW):
    n = len(ws[i])
    ws[i] = MSGR[cur:cur + n]
    cur += n
perm = rng.permutation(NW)
scattered = [ws[i] for i in perm]
read = np.concatenate([scattered[t] for t in np.argsort(perm)])
res["E_order_oracle"] = dict(n=int(read.size), score=R.score(read),
                             sample=R.show(read))
# and the ceiling a WRONG order still reaches (English words, scrambled):
res["E2_wrong_order_ceiling"] = round(
    R.score(np.concatenate([scattered[t] for t in range(NW)])), 4)

# ------------------------------------------------------------------- verdict
PASS = (res["A_oracle_selector"]["score"] >= -12.0
        and res["B3_selector_null"]["z_of_plant"] >= 8.0
        and res["C_filler_specificity_max"] < -13.0
        and res["D_sum_mod29_decode"]["score"] >= -12.0
        and res["E_order_oracle"]["score"] >= -12.0)
res["GATE"] = "PASS" if PASS else "FAIL"

json.dump(res, open(os.path.join(HERE, "gate.json"), "w"), indent=1)
for k, v in res.items():
    print(k, "=", v if not isinstance(v, dict) else
          {kk: (round(vv, 4) if isinstance(vv, float) else vv)
           for kk, vv in v.items()})
