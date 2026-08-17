"""GATE for lane B3.  Both gates must pass before any negative may be reported.

GATE-1  the expanded-orbit key search must re-find the ground-truth keys:
        03.jpg -> DIVINITY (rank 1, > -5.0, plaintext has WELCOME + PILGRIM)
        14.jpg -> a CIRCUMFERENCE-orbit key (rank 1, > -5.0, plaintext has KOAN/LESSON/CIRCU..)
GATE-2  the crib instrument must read the key out of the ciphertext:
        crib WELCOME at offset 0 of 03.jpg  -> keystream translit exactly 'DIUINIT'
        crib AKOAN   at offset 0 of 14.jpg  -> keystream translit exactly 'FIRFU'

Run: PYTHONUTF8=1 python3 gate.py
"""
import re
import sys

import b3lib
import screen
from b3lib import gp
from lp import solve

SC = b3lib.scorer()


def canon(s):
    s = re.sub(r"[^A-Z]", "", s.upper())
    for a, b in (("K", "C"), ("V", "U"), ("Z", "S"), ("Q", "C")):
        s = s.replace(a, b)
    return s


def rigid(idxs, key, sign, atbash):
    out = []
    for j, c in enumerate(idxs):
        base = (gp.N - 1 - c) if atbash else c
        out.append((base + sign * key[j % len(key)]) % gp.N)
    return out


def search_page(idxs, keys, beam=True, runes_text=None, topn=8):
    """Screen every candidate with the phase-flexible decoder, then re-rank the
    survivors with the repo's own interrupter beam.
    Returns sorted [(score, latin, translit_key, sign, atbash, plaintext, tuple)]."""
    segs = screen.segments_of(idxs)
    res = []
    for lat, grp, k in keys:
        for sign in (-1, +1):
            for atb in (False, True):
                s, _, _ = screen.phase_flexible_score(idxs, k, sign, atb, SC, segs)
                res.append((s, lat, gp.indices_to_translit(k), sign, atb, "", k))
    res.sort(key=lambda r: -r[0])
    if beam and runes_text is not None:
        refined = []
        for s, lat, kt, sign, atb, _, tup in res[:topn]:
            stream = [tup[j % len(tup)] for j in range(len(idxs))]
            r = solve.find_interrupters(runes_text, stream, sign=sign, atbash=atb,
                                        beam_width=300)
            refined.append((r["score_norm"], lat, kt, sign, atb, r["plaintext"], tup))
        refined.sort(key=lambda r: -r[0])
        return refined + res[topn:]
    return res


def crib_readout(idxs, crib_key, sign):
    """Given plaintext crib (rune indices) at offset 0, recover the keystream prefix."""
    return [(sign * (idxs[j] - crib_key[j])) % gp.N for j in range(len(crib_key))]


def main():
    keys = b3lib.expanded_keys()
    print(f"expanded candidate keys: {len(keys)}")
    ok = True

    # ---------------------------------------------------------------- GATE-1
    print("\n== GATE-1  key search re-finds ground truth ==")
    for label, want_latin, must in (("03.jpg", "DIVINITY", ["WELCOME", "PILGRIM"]),
                                    ("14.jpg", "CIRCUMFERENCE",
                                     ["KOAN", "LESSON", "CIRCUMFERENCE"])):
        idxs, page = b3lib.solved_page(label)
        res = search_page(idxs, keys, beam=True, runes_text=page["runes"])
        s, lat, kt, sign, atb, txt = res[0][:6]
        c = canon(txt)
        hits = [m for m in must if canon(m) in c]
        good = (lat == want_latin and s > -5.0 and len(hits) >= 2)
        print(f"  {label}: rank1 = {lat} spelled {kt}  sign{sign:+d} atb{atb} "
              f"score {s:.3f}  words {hits}")
        print(f"        plaintext: {txt[:90]}")
        print(f"        -> {'PASS' if good else 'FAIL'}")
        ok &= good
        # show where the ground-truth spelling ranks
        for rank, r in enumerate(res):
            if r[1] == want_latin:
                print(f"        first {want_latin} variant at rank {rank}: {r[2]} {r[0]:.3f}")
                break

    # ---------------------------------------------------------------- GATE-2
    print("\n== GATE-2  crib instrument reads out the key ==")
    for label, crib, want in (("03.jpg", "WELCOME", "DIUINIT"),
                              ("14.jpg", "AKOAN", "FIRFU")):
        idxs, page = b3lib.solved_page(label)
        ck = gp.keyword_to_indices(crib)
        found = None
        for sign in (-1, +1):
            ro = gp.indices_to_translit(crib_readout(idxs, ck, sign))
            print(f"  {label} crib {crib!r} sign{sign:+d} -> {ro}")
            if ro == want:
                found = sign
        good = found is not None
        print(f"        want {want!r} -> {'PASS' if good else 'FAIL'}")
        ok &= good

    print("\nGATE OVERALL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
