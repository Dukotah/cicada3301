#!/usr/bin/env python3
"""LANE B POSITIVE CONTROL (mandatory, pre-registered).

Plant: take ONE of the R12-C2 keytexts, map it to rune indices, and use it as a
RUNNING KEY K over an English plaintext P. Encipher with the SAME key-skip filter
the decoder inverts:
  - keyskip1 plant  <- inverted by preset 'exact'  (skipdecode.encipher_keyskip)
  - skip_by_two plant <- inverted by preset 'pair' (enc_skip_by_two, j+=2)

We must show the skip-aware gate RECOVERS the plant at >=0.90 rune-index recovery
BEFORE any sweep null counts. If it does not, Lane B STOPS.

This is the control that R12-C2 staged-but-never-ran. Structure mirrors
analysis/round24/C2-skip-by-two/control.py (L=240, English held-out plaintext,
RECOVERY_BAR=0.90) but the KEY is a real keytext, not sha256_ctr, because a running
key is exactly what this lane sweeps.

Run: python3 control.py            # writes control.json
"""
import os, sys, json, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "benchmark",
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round19", "I1"),
          os.path.join("analysis", "round20", "HITFN")):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp          # noqa
import skipdecode as sk                # noqa  (eng_to_idx, encipher_keyskip)
import driftbeam as DB                 # noqa  (keyskip1/keyskip2)

N = gp.N
L = 240
NSEED = 7
RECOVERY_BAR = 0.90

TEXTDIR = os.path.join(LP, "analysis", "round12", "C2", "texts")
# a representative keytext for the control (Latin/Greek philosophy, dense letters)
CONTROL_TEXT = "plotinus_enneads_mackenna.txt"


def english_stream():
    p = os.path.join(LP, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sk.eng_to_idx(f.read())[5000:]


ENG = english_stream()


def keytext_idx(fname):
    p = os.path.join(TEXTDIR, fname)
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sk.eng_to_idx(f.read())


KT = keytext_idx(CONTROL_TEXT)


def take_plain(Ln, seed):
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - Ln - 1)
    return ENG[s:s + Ln]


def enc_skip_by_two(P, K, o, supp=0.83, seed=3301):
    """Rejection CONSUMES TWO draws (j += 2) -- the pair-decoder target.
    Decode relation p = (c + sign*k) % N with sign=-1, so encipher c = (p + k)."""
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], o, None, 0
    while len(C) < len(P):
        p = P[len(C)]
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c); j += 1; c_prev = c
    return C, nsk


def rec(plain_idx, truth):
    return sum(1 for a, b in zip(plain_idx, truth) if a == b) / max(1, len(truth))


def run():
    out = {"lane": "round26/B/control",
           "control_text": CONTROL_TEXT,
           "plant": "keytext running key over English self_reliance L=240; keyskip1 + skip_by_two",
           "recovery_bar": RECOVERY_BAR, "n_seeds": NSEED, "keytext_len": len(KT),
           "rows": []}
    ks1_recs, pair_recs = [], []
    for s in range(NSEED):
        P = take_plain(L, s)
        # random offset into the keytext for the running key
        r = random.Random(4000 + s)
        o = r.randrange(0, len(KT) - L * 12 - 8)
        # --- keyskip1 plant (skipdecode.encipher_keyskip uses key starting at index 0;
        #     shift K by o so the running-key offset is exercised)
        Ko = KT[o:]
        C1, sk1, used1 = sk.encipher_keyskip(P, Ko, sign=-1, supp=0.83, seed=3301 + s)
        d1 = DB.beam_decode(C1, Ko, sign=-1, o=0, beam_w=400, mode="keyskip1", max_skip=8)
        r1 = rec(d1["plain_idx"], P)
        # --- skip_by_two plant
        C2, nsk2 = enc_skip_by_two(P, KT, o, supp=0.83, seed=3301 + s)
        d2 = DB.beam_decode(C2, KT, sign=-1, o=o, beam_w=400, mode="keyskip2", max_skip=8)
        r2 = rec(d2["plain_idx"], P)
        ks1_recs.append(r1); pair_recs.append(r2)
        out["rows"].append({"seed": 3301 + s, "offset": o,
                            "keyskip1_rec": r1, "keyskip1_score": d1["score"],
                            "pair_rec": r2, "pair_score": d2["score"]})
    out["keyskip1_median_rec"] = statistics.median(ks1_recs)
    out["keyskip1_min_rec"] = min(ks1_recs)
    out["pair_median_rec"] = statistics.median(pair_recs)
    out["pair_min_rec"] = min(pair_recs)
    out["keyskip1_pass"] = out["keyskip1_min_rec"] >= RECOVERY_BAR
    out["pair_pass"] = out["pair_min_rec"] >= RECOVERY_BAR
    out["control_passed"] = out["keyskip1_pass"] and out["pair_pass"]
    return out


def main():
    out = run()
    with open(os.path.join(HERE, "control.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("keytext running-key control:", CONTROL_TEXT)
    print("keyskip1 median/min rec: %.3f / %.3f  pass=%s" %
          (out["keyskip1_median_rec"], out["keyskip1_min_rec"], out["keyskip1_pass"]))
    print("pair     median/min rec: %.3f / %.3f  pass=%s" %
          (out["pair_median_rec"], out["pair_min_rec"], out["pair_pass"]))
    print("CONTROL_PASSED:", out["control_passed"])


if __name__ == "__main__":
    main()
