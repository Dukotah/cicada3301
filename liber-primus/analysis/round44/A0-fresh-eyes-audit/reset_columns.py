"""Fresh-eyes audit, part 11: identical key restarts at visible boundaries are excluded without a key.

If the key restarted in the same state at every page (or section, sentence, line), the runes at the
same offset from each restart would share a key value, so pairs of them would coincide at the
plaintext rate (about 6.5 %) instead of 1/29. They do not. (Line columns 0-1 are skipped: the
glyph-width line-break bias of round18/L4 lives there.) A restart to a DIFFERENT key state is not
tested by this and stays open.
"""
import collections
import json
import math
import os

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
P = lp2.unsolved(); PI = lp2.idx(P)
out = {}


def col_test(units, ncol, label):
    eq = tot = 0
    for t in range(ncol):
        col = [u[t] for u in units if len(u) > t]
        c = collections.Counter(col); n = len(col)
        eq += sum(v * (v - 1) // 2 for v in c.values()); tot += n * (n - 1) // 2
    sd = math.sqrt(tot * (1 / 29) * (28 / 29))
    z = (eq - tot / 29) / sd
    zexp = (0.0655 - 1 / 29) * tot / sd
    out[label] = {"units": len(units), "columns": ncol, "equal_pairs": eq, "pairs": tot, "kappa_x29": 29 * eq / tot, "z": z,
                  "z_expected_if_same_key_english": zexp}
    print(f"{label:28s} {eq}/{tot} equal pairs  kappa x 29 = {29 * eq / tot:.3f}  z = {z:+.2f}   (same key, English: z about {zexp:+.0f})")


col_test(PI, 10, "page heads, columns 0-9")
txt = open(lp2.KRIS, encoding="utf-8").read(); secs, cur = [], []
for ch in txt:
    if ch in lp2.R2I:
        cur.append(lp2.R2I[ch])
    elif ch in "$§":
        secs.append(cur); cur = []
col_test([s for s in secs if s][:8], 40, "section heads, columns 0-39")
sents, cur = [], []
for p in P:
    for r in p:
        if "." in r["pre"] and cur:
            sents.append(cur); cur = []
        cur.append(r["i"])
sents.append(cur)
col_test(sents, 8, "sentence heads, columns 0-7")
lines = []
for p in P:
    cur = []
    for k, r in enumerate(p):
        if k > 0 and "/" in r["pre"]:
            lines.append(cur); cur = []
        cur.append(r["i"])
    lines.append(cur)
col_test([l[2:] for l in lines], 8, "line columns 2-9")
json.dump(out, open(os.path.join(HERE, "reset_columns.json"), "w"), indent=1)
