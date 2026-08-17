"""L3-ROAD step 0 - CALIBRATION on control data only.

Purpose: fix the numeric pass/fail thresholds BEFORE the ROAD tests touch LP2.
Nothing here reads the unsolved ciphertext.

Measures, for the seed-sweep rune 4-gram scorer:
  * English-in-futhorc score at each length a ROAD reading can produce
  * uniform-random rune score at the same lengths
  * the score of the two solved LP2 pages (author's own prose; PARABLE is
    unenciphered plaintext, AN END is keystream gibberish) as sanity anchors
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import road_lib as R  # noqa: E402

rng = np.random.default_rng(3301)
LENS = [2928, 1500, 700, 300, 120, 48]

# ------------------------------------------------------------------ English
texts = []
for f in ("kjv.txt", "moby.txt", "pride.txt", "war.txt"):
    p = os.path.join(R.ROOT, "data", f)
    if os.path.exists(p):
        texts.append((f, open(p, encoding="utf-8", errors="ignore").read()))
enc = {nm: np.array(R.eng_to_runes(t), dtype=np.int64) for nm, t in texts}

out = {"english": {}, "uniform": {}, "note": "stream-scale 4-gram (seed sweep)"}
for L in LENS:
    sc = []
    for nm, a in enc.items():
        if a.size <= L + 10:
            continue
        for _ in range(300):
            i = int(rng.integers(0, a.size - L))
            sc.append(R.score(a[i:i + L]))
    sc = np.array(sc)
    out["english"][L] = dict(n=len(sc), mean=float(sc.mean()), sd=float(sc.std()),
                             p01=float(np.percentile(sc, 1)),
                             p001=float(np.percentile(sc, 0.1)),
                             min=float(sc.min()), max=float(sc.max()))
    u = np.array([R.score(rng.integers(0, 29, L)) for _ in range(300)])
    out["uniform"][L] = dict(mean=float(u.mean()), sd=float(u.std()),
                             max=float(u.max()), min=float(u.min()))

# ------------------------------------------------ solved LP2 pages as anchors
anend, parable = R.lp2_solved()
out["anchors"] = {
    "PARABLE_plaintext": dict(runes=int(sum(len(w) for w in parable)),
                              score=R.score([r for w in parable for r in w])),
    "AN_END_ciphertext": dict(runes=int(sum(len(w) for w in anend)),
                              score=R.score([r for w in anend for r in w])),
}

json.dump(out, open(os.path.join(HERE, "calib.json"), "w"), indent=1)

print("length |  English mean   sd    p1     p0.1  |  uniform mean   max")
for L in LENS:
    e, u = out["english"][L], out["uniform"][L]
    print(f"{L:6d} | {e['mean']:8.3f} {e['sd']:6.3f} {e['p01']:7.3f} {e['p001']:7.3f} "
          f"| {u['mean']:9.3f} {u['max']:8.3f}")
print()
for k, v in out["anchors"].items():
    print(f"{k:22s} n={v['runes']:5d}  score={v['score']:.4f}")
