"""ROUND 19 / LANE G2 -- the pre-registered positive control ARTIFACT.

PREREG.md Q1 commits, in advance and before any sweep, to a specific planted
hit so that I1's driftbeam and I2's adjudicator can run G2-GATE-Q1 without
designing the control after seeing results.  This script builds that artifact.
It does NOT score anything -- Phase 0 is not finished and doctrine forbids
scoring with the current instrument.

THE PLANT, fixed in PREREG.md sec.Q1 and not changed here:

    seed       = 1389657600      (2014-01-14, inside the LP2 posting window)
    reduction  = r29             int(rand(29)), perlfunc's own idiom
    sign       = -1
    atbash     = off
    direction  = forward
    offset     = 0

Emits `plant.json` with, for each construction and each register:
  * the plaintext rune indices
  * the ciphertext rune indices
  * the true keystream
  * the skip trace (where the key desynchronises, and by how much)

WHAT I1 / I2 MUST DO WITH IT (G2-GATE-Q1)
-----------------------------------------
Recover the plant.  Specifically: run the drift-tolerant decoder on each
ciphertext under the TRUE keystream and report

  (a) score under I3's threshold, (b) rune-recovery fraction,
  (c) the margin over a deliberately WRONG seed's keystream,

for every construction x register cell.  Round 18 L7-A/L7-B measured the current
instrument at power 0.33 (Latin) / 0.00 (no-vowel English), and -6.90 at 25.8 %
recovery on `skip_by_two`.  If those numbers do not improve here, G2's sweep
output is INCONCLUSIVE, not NEGATIVE, and PREREG.md sec.Q5 KILL-2 fires.

CONSTRUCTIONS
-------------
  keyskip     `campaign18_skip.encipher_keyskip(supp=0.83)` -- the repo's pinned
              model, exact for the beam's transition relation
  skip_by_two the L7-B variant: the rejection loop burns TWO key draws instead of
              one.  A one-character change to a plausible 2013 loop; reproduces
              LP2's doublet rate (0.84 % vs 0.664 % observed); the current beam
              scores the CORRECT key at -6.90 / 25.8 % recovery on it.
  nodrift     no filter at all -- the trivial control.  If the instrument cannot
              recover THIS, nothing else in the panel means anything.

REGISTERS
---------
The panel is I2's, not G2's; this file plants the four that L7-A measured
directly (EN, Latin, half-vowel EN, no-vowel EN) plus LP1 orthography, so that
the control exercises the axis that made ~10^10 prior decodes English-only.
More registers are I2's to add.

Run:  python3 plant.py
"""
from __future__ import annotations

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import skipdecode as sk      # noqa: E402
import gen_perl as G         # noqa: E402

N = 29

# --- locked by PREREG.md sec.Q1 -------------------------------------------
PLANT_SEED = 1389657600
PLANT_RED = "r29"
PLANT_SIGN = -1
PLANT_ATBASH = False
PLANT_DIR = "forward"
PLANT_OFFSET = 0
WRONG_SEED = 1389657601          # the adjacent second: a maximally fair foil
SUPP = 0.83
FILTER_RNG_SEED = 3301           # matches encipher_keyskip's default

# --- registers -------------------------------------------------------------
_EN = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
       "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
       "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN")

_LP1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE "
        "TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT "
        "EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN")

_LATIN = ("OMNIA MUTANTUR NIHIL INTERIT NUMERUS PRIMUS SACER EST ET FUNCTIO "
          "TOTIENS SACRA EST OMNIA ENCRYPTA ESSE DEBENT COGNOSCE HOC UMBRAE "
          "VITAE MORTIS QUE CIRCULUS EST")


def _drop_vowels(s, keep_every=0):
    """keep_every=0 -> drop every vowel; 2 -> keep every 2nd (the half-vowel
    register L7-A measured at 0.00 and 0.33 power respectively)."""
    out, seen = [], 0
    for ch in s:
        if ch in "AEIOU":
            seen += 1
            if keep_every and seen % keep_every == 0:
                out.append(ch)
            continue
        out.append(ch)
    return "".join(out)


REGISTERS = {
    "EN": _EN,
    "LP1_ORTHOGRAPHY": _LP1,
    "LATIN": _LATIN,
    "EN_HALF_VOWEL": _drop_vowels(_EN, keep_every=2),
    "EN_NO_VOWEL": _drop_vowels(_EN, keep_every=0),
}


# --- constructions ---------------------------------------------------------

def enc_nodrift(P, K, sign=PLANT_SIGN):
    C = [(p - sign * K[i]) % N for i, p in enumerate(P)]
    return C, [0] * len(P), list(range(len(P)))


def enc_skip_by_two(P, K, sign=PLANT_SIGN, supp=SUPP, seed=FILTER_RNG_SEED):
    """L7-B's variant: the rejection loop burns TWO key draws per rejection.

    Identical to `encipher_keyskip` except for `j += 2` in the reject branch --
    a one-character change to a plausible 2013 loop, and the construction the
    current beam misses at -6.90 / 25.8 % recovery.
    """
    rng = random.Random(seed)
    C, skips, used = [], [], []
    j, c_prev = 0, None
    for p in P:
        nsk = 0
        while True:
            c = (p - sign * K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2                      # <-- the whole difference
                nsk += 2
                continue
            break
        C.append(c)
        skips.append(nsk)
        used.append(j)
        j += 1
        c_prev = c
    return C, skips, used


CONSTRUCTIONS = {
    "nodrift": enc_nodrift,
    "keyskip": lambda P, K: sk.encipher_keyskip(P, K, sign=PLANT_SIGN,
                                                supp=SUPP, seed=FILTER_RNG_SEED),
    "skip_by_two": enc_skip_by_two,
}


def main():
    doc = {
        "lane": "round19/G2",
        "artifact": "pre-registered positive control for G2-GATE-Q1",
        "locked_in": "round19/G2/PREREG.md sec.Q1 and sec.6",
        "plant": {"seed": PLANT_SEED, "reduction": PLANT_RED, "sign": PLANT_SIGN,
                  "atbash": PLANT_ATBASH, "direction": PLANT_DIR,
                  "offset": PLANT_OFFSET, "filter_supp": SUPP,
                  "filter_rng_seed": FILTER_RNG_SEED,
                  "perl_line": G.REDUCTIONS[PLANT_RED][3]},
        "wrong_seed_foil": WRONG_SEED,
        "generator_validated_by": "round19/G2/validation.json (gates A/B/C all PASS)",
        "instruction_to_I1_I2": (
            "Decode each ciphertext with the drift-tolerant decoder under keystream_true "
            "and under keystream_wrong. Report score, rune-recovery fraction and the "
            "true-minus-wrong margin per (construction x register) cell, at I3's "
            "threshold. Round 18 baselines to beat: L7-A power 0.33 Latin / 0.00 "
            "no-vowel EN; L7-B -6.90 at 25.8% recovery on skip_by_two."
        ),
        "cells": [],
    }

    for rname, text in REGISTERS.items():
        P = sk.eng_to_idx(text)
        nk = len(P) * 6 + 64                      # slack for worst-case skipping
        K_true = G.make_ks(PLANT_RED, PLANT_SEED, nk)
        K_wrong = G.make_ks(PLANT_RED, WRONG_SEED, nk)
        for cname, fn in CONSTRUCTIONS.items():
            C, skips, used = fn(P, K_true)
            doc["cells"].append({
                "register": rname,
                "construction": cname,
                "n_runes": len(P),
                "plaintext_translit": sk.idx_to_trans(P),
                "plain_idx": P,
                "cipher_idx": C,
                "keystream_true": K_true[:len(P) * 4 + 16],
                "keystream_wrong": K_wrong[:len(P) * 4 + 16],
                "skip_trace": skips,
                "key_index_used": used,
                "n_desync_events": sum(1 for s in skips if s),
                "total_key_advance_beyond_1to1": used[-1] - (len(P) - 1) if used else 0,
            })
            print(f"  {rname:16s} {cname:12s} n={len(P):3d} "
                  f"desync_events={sum(1 for s in skips if s):2d} "
                  f"final_key_drift={used[-1] - (len(P)-1) if used else 0}")

    with open(os.path.join(HERE, "plant.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print(f"\nwrote plant.json  ({len(doc['cells'])} cells: "
          f"{len(REGISTERS)} registers x {len(CONSTRUCTIONS)} constructions)")
    print("NOTE: nothing here was scored. Scoring is I1/I2/I3's, after Phase 0 gates PASS.")


if __name__ == "__main__":
    main()
