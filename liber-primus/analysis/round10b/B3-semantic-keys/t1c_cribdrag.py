"""T1c -- exhaustive crib DRAG with the exact-period detector, vectorised.

T1b only cribbed at 219 semantically-chosen positions.  This removes the position guess
entirely: it asks whether ANY semantic opening phrase sits at ANY offset in ANY unsolved page
under a repeating key of ANY length.

The identity that makes it cheap and sign-free:

    key period L  <=>  k[j] == k[j+L]  for all j
                  <=>  (ct[o+j] - ct[o+j+L]) == (t[j] - t[j+L])   (mod 29)

so define  D_L[i] = ct[i]-ct[i+L]  and  E_L[j] = t[j]-t[j+L]  and the test is a plain pattern
search of E_L inside D_L.  The sign of the cipher cancels; atbash also cancels (it negates both
sides equally).  One numpy pass per (crib, L).

Scope limit stated up front: this assumes no interrupter NULL falls inside the crib window.
With the observed F density that leaves roughly half of all windows clean, which is ample when
dragging over 12,956 offsets.

POSITIVE CONTROL: the drag must find WELCOMEWELCOMEPILGRIM at offset 0 of 03.jpg with L=8.

Run: PYTHONUTF8=1 python3 t1c_cribdrag.py
"""
import json
import random
import sys

import numpy as np

import b3lib
import t1b_period as t1b
from b3lib import gp
from run_stats import english_baseline

N = gp.N
MIN_CONSTRAINTS = 6      # need k[j]==k[j+L] to hold at >= 6 positions to call a hit


def drag(ct, cribs, min_c=MIN_CONSTRAINTS):
    """Return list of (offset, L, crib_latin, crib_spelled, n_constraints)."""
    ct = np.asarray(ct, dtype=np.int64)
    n = len(ct)
    hits = []
    Dcache = {}
    for lat, t in cribs:
        ta = np.asarray(t, dtype=np.int64)
        m = len(ta)
        for L in range(2, m - min_c + 1):
            E = (ta[:m - L] - ta[L:]) % N            # length m-L
            if len(E) < min_c:
                continue
            if L not in Dcache:
                Dcache[L] = (ct[:n - L] - ct[L:]) % N
            D = Dcache[L]
            w = len(E)
            if len(D) < w:
                continue
            # sliding-window exact match of E inside D
            sw = np.lib.stride_tricks.sliding_window_view(D, w)
            eq = (sw == E[None, :]).all(axis=1)
            for o in np.flatnonzero(eq):
                hits.append((int(o), L, lat, gp.indices_to_translit(t), w))
    return hits


def positive_control(cribs):
    print("== T1c POSITIVE CONTROL ==")
    idxs, _ = b3lib.solved_page("03.jpg")
    sel = [(l, t) for l, t in cribs if l == "WELCOMEWELCOMEPILGRIM"]
    hits = drag(idxs, sel)
    good = any(o == 0 and L == 8 for o, L, _, _, _ in hits)
    for h in hits[:6]:
        print("   hit", h)
    print(f"  offset 0 / L=8 found: {'PASS' if good else 'FAIL'}\n")
    return good


def main():
    rng = random.Random(3301)
    cribs = t1b.crib_keys()
    print(f"crib variants: {len(cribs)}  (>= {t1b.MIN_CRIB} runes)")
    if not positive_control(cribs):
        print("ABORT: positive control failed")
        return 1

    pages = b3lib.lp2_segments()[:55]
    stream = [c for p in pages for c in p]
    print(f"LP2 unsolved stream: {len(stream)} runes; dragging every offset")

    real = drag(stream, cribs)
    print(f"REAL exact-period hits (>= {MIN_CONSTRAINTS} constraints): {len(real)}")
    for h in real[:20]:
        print("   ", h)

    # NULL A: pseudo-cribs, matched lengths
    eng = english_baseline()
    ncribs = []
    for _, t in cribs:
        L = len(t)
        s = rng.randrange(0, len(eng) - L - 1)
        ncribs.append(("<null>", tuple(eng[s:s + L])))
    nA = drag(stream, ncribs)
    print(f"NULL-A pseudo-crib hits: {len(nA)}")

    # NULL B: real cribs vs shuffled stream
    sh = list(stream)
    rng.shuffle(sh)
    nB = drag(sh, cribs)
    print(f"NULL-B shuffled-stream hits: {len(nB)}")

    # expected-by-chance estimate
    exp = 0.0
    for _, t in cribs:
        m = len(t)
        for L in range(2, m - MIN_CONSTRAINTS + 1):
            w = m - L
            if w >= MIN_CONSTRAINTS:
                exp += len(stream) * (1.0 / N) ** w
    print(f"expected hits by chance over the whole drag: {exp:.4g}")

    json.dump({"n_cribs": len(cribs), "stream_len": len(stream),
               "real_hits": len(real), "nullA_hits": len(nA), "nullB_hits": len(nB),
               "expected_by_chance": exp,
               "real_detail": [list(map(str, h)) for h in real[:100]]},
              open("T1C-RESULTS.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
