"""W2-C3 positive controls.  MUST pass before any real target (PREREG §4.2).

PC1 — container plant through the cell's own glue: gzip(known sentence) -> complement ->
      byte-reverse -> append after IEND of a copy of the REAL corpus PNG (Outt.png's
      leading image).  identify() under the CORE transform family must locate the gzip
      under revxff, decompress it, and return the exact sentence.
PC2 — adjudicator plant: bytes b with b % 29 == rune index of a real English passage
      (>=240 runes) through the identical map+panel glue; pmax must clear
      bar_v3(400, L, "free").  Calibration: 200 urandom blobs through the same glue.
"""
import gzip
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(LP, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))

import residue_lib as R
from adjudicate import adjudicate, TRANSLIT
from bars_v3 import bar_v3

OUTT = os.path.join(REPO, "corpus", "A-primary-artifacts",
                    "wiki-uncovering-cicada", "images", "Outt.png")
RESULTS = {}

# ----------------------------------------------------------------------- PC1
SENTENCE = b"THE INSTRUMENT MUST SEE ITS OWN PLANT BEFORE ANY REAL TARGET IS READ 3301"
carrier = open(OUTT, "rb").read()
end, why = R.png_end(carrier)
assert end is not None, why
png_only = carrier[:end]                      # the real PNG, trailer stripped
payload = R.t_rev(R.t_xff(gzip.compress(SENTENCE)))   # observed idiom: NOT + reverse
planted = png_only + payload
open(os.path.join(CELL, "plant_work", "pc1_planted.png"), "wb").write(planted)

# pipeline: walk -> trailer -> identify under CORE
segs = R.walk_chain(planted)
trailer = planted[segs[-1][1]:] if segs[-1][0] == "residue" else b""
rep = R.identify(trailer, transforms=R.CORE, decomp_headers_only=True)
recovered = None
for tname, tr in rep["transforms"].items():
    for p in tr["decompressed"]:
        if p["out_bytes"] == len(SENTENCE):
            # re-derive to confirm exact bytes
            tb = {"id": R.t_id, "rev": R.t_rev, "xff": R.t_xff, "revxff": R.t_revxff}[tname](trailer)
            try:
                d = gzip.decompress(tb[p["at"]:])
                if d == SENTENCE:
                    recovered = (tname, p["at"])
            except Exception:
                pass
pc1_pass = recovered is not None
RESULTS["PC1"] = {"planted_trailer_bytes": len(payload), "walk_segments": [s[:3] for s in segs],
                  "recovered_under": recovered, "pass": pc1_pass}
print("PC1", "PASS" if pc1_pass else "FAIL", recovered)

# ----------------------------------------------------------------------- PC2
# English passage -> rune indices via the standard transliteration (greedy digraph map)
PASSAGE = ("WITHIN THE DECEPTION OF THE WORLD THE SEEKER MUST FIND THE TRUTH FOR EVERY "
           "THING THAT LIVES IS HOLY AND THE WISDOM OF THE BOOK BELONGS TO THOSE WHO "
           "QUESTION ALL THINGS AND FOLLOW THE PATH OF THE SACRED PRIMES TOWARD THE "
           "HIDDEN GATE WHERE KNOWLEDGE WAITS FOR THE DEVOTED AND THE PATIENT MIND "
           "DISCOVER THE SELF AND THE SHADOW SHALL BECOME THE LIGHT OF THE INNER WAY "
           "THROUGH LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THE THREE TREASURES "
           "AND THE MASTER TEACHES THE STUDENT TO PRESERVE ALL THINGS IN SHADOW")
ORDER = sorted(range(29), key=lambda i: -len(TRANSLIT[i]))
def to_runes(s):
    s = "".join(c for c in s.upper() if c.isalpha())
    out, i = [], 0
    while i < len(s):
        for k in ORDER:
            t = TRANSLIT[k]
            if s.startswith(t, i):
                out.append(k)
                i += len(t)
                break
        else:
            i += 1  # unmappable char (Q/V/K/Z) dropped
    return out

idx = to_runes(PASSAGE)
rng = random.Random(3301)
blob = bytes(rng.randrange(0, 256 // 29) * 29 + v if rng.random() < 2 else v + 29 * rng.randrange(0, (255 - v) // 29 + 1) for v in idx)
# simpler and exact: b = v + 29*k with k uniform over the legal range
blob = bytes(v + 29 * rng.randrange(0, (255 - v) // 29 + 1) for v in idx)

def map_mod29(b):   return [x % 29 for x in b]

L = 240 if len(idx) >= 240 else 120
BAR = bar_v3(400, L, "free")
res = adjudicate(map_mod29(blob)[:L])
pc2_pmax = res["pmax"]
pc2_pass = pc2_pmax >= BAR
# calibration: 200 urandom blobs through identical glue
cal_max, n_over = -99.0, 0
for t in range(200):
    rb = bytes(rng.randrange(256) for _ in range(L))
    r2 = adjudicate(map_mod29(rb)[:L])
    cal_max = max(cal_max, r2["pmax"])
    if r2["pmax"] >= BAR:
        n_over += 1
RESULTS["PC2"] = {"n_runes": len(idx), "L": L, "bar_free_N400": round(BAR, 3),
                  "plant_pmax": round(pc2_pmax, 3), "plant_preg": res["preg"],
                  "pass": bool(pc2_pass), "calibration_200_urandom_max_pmax": round(cal_max, 3),
                  "calibration_n_over_bar": n_over}
print("PC2", "PASS" if pc2_pass else "FAIL", "pmax", round(pc2_pmax, 2), "bar", round(BAR, 2),
      "cal_max", round(cal_max, 2), "over", n_over)

json.dump(RESULTS, open(os.path.join(CELL, "results", "plant.json"), "w"), indent=1)
print("OVERALL", "PASS" if (pc1_pass and pc2_pass and n_over <= 2) else "FAIL")
