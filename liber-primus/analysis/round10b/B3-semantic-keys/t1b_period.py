"""T1b -- crib readout -> EXACT PERIOD detection.  Zero-false-positive structural test.

T1 showed the language scorer has no power on a 5-9 rune key readout (positive control put the
true DIUINIT readout at rank 53/176).  So replace the scorer with STRUCTURE:

  If the page key is a repeating word of length L, then a crib of length m > L placed at the
  right offset yields a readout k with k[j] == k[j+L] for every j.  For a wrong crib the readout
  is uniform noise, so the chance of an exact period L over m-L constraint positions is
  29^-(m-L).  For m=20, L=8 that is 29^-12 ~= 2e-18.  ANY exact hit is unambiguous.

This recovers the key WITHOUT the key being in any word list -- the crib does the work.

POSITIVE CONTROL: crib 'WELCOMEWELCOMEPILGRIM' at offset 0 of 03.jpg must expose exact period 8
(= DIVINITY).  If it does not, the instrument is void.

Interrupters: the F rune may be a null that carries no plaintext.  Every subset of the F runes
inside the crib window is tried (windows are short, so this is a handful of combinations).

Run: PYTHONUTF8=1 python3 t1b_period.py
"""
import itertools
import json
import random
import sys

import b3lib
from b3lib import gp
from run_stats import english_baseline

N = gp.N
MIN_CRIB = 12
MIN_REPEAT = 4          # need at least this many constraint positions to call a period


# ------------------------------------------------------------------ cribs
CRIB_PHRASES = [
    # the two demonstrated solved openings, and their LP2-style analogues
    "WELCOMEWELCOMEPILGRIM", "WELCOMEPILGRIMTOTHE", "AKOANDURINGALESSON",
    "SOMEWISDOMTHEPRIMESARESACRED", "THEPRIMESARESACRED",
    "ALLTHINGSSHOULDBEENCRYPTED", "THETOTIENTFUNCTIONISSACRED",
    "PARABLELIKETHEINSTAR", "LIKETHEINSTARTUNNELING",
    "WEMUSTSHEDOUROWNCIRCUMFERENCES", "FINDTHEDIVINITYWITHIN",
    "ANINSTRUCTIONCOMMAND", "AWARNINGBELIEUENOTHING",
    "THELOSSOFDIVINITY", "ANENDTHEPRIMES",
    # plausible LP2 openings built from the author's own vocabulary
    "THEINSTAREMERGES", "SHEDYOURCIRCUMFERENCE", "SEEKTHETRUTHWITHIN",
    "THEDIUINITYWITHIN", "KNOWTHYSELFANDEMERGE", "THEPILGRIMSJOURNEY",
    "THEENDOFALLTHINGS", "ANINSTARWITHINTHESELF", "THEMASTEREXPLAINED",
    "THESTUDENTASKEDTHEMASTER", "DURINGALESSONTHEMASTER",
    "COMMANDONEADHERE", "COMMANDTWOPRESERVE", "COMMANDTHREECONSUME",
    "THESHADOWSONTHECAUE", "REALITYISANILLUSION",
]


def crib_keys():
    out, seen = [], []
    s = set()
    for p in CRIB_PHRASES:
        for t in b3lib.orbit(p):
            if len(t) >= MIN_CRIB and t not in s:
                s.add(t)
                out.append((p, t))
    return out


def readout(ct, start, crib, sign, skips=()):
    """keystream implied by crib at ct[start:], with `skips` = ciphertext offsets (relative to
    start) treated as interrupter nulls that carry no plaintext."""
    k, ci = [], 0
    j = start
    while ci < len(crib) and j < len(ct):
        if (j - start) in skips:
            j += 1
            continue
        k.append((sign * (ct[j] - crib[ci])) % N)
        ci += 1
        j += 1
    return k if ci == len(crib) else None


def exact_periods(k):
    """All L with k[j]==k[j+L] for all valid j and at least MIN_REPEAT constraints."""
    m = len(k)
    out = []
    for L in range(2, m - MIN_REPEAT + 1):
        nc = m - L
        if nc < MIN_REPEAT:
            continue
        if all(k[j] == k[j + L] for j in range(nc)):
            out.append((L, nc))
    return out


def best_partial(k):
    """max over L of (fraction of satisfied constraints, L, n_constraints) -- for the null dist."""
    m = len(k)
    best = (0.0, 0, 0)
    for L in range(2, m - MIN_REPEAT + 1):
        nc = m - L
        if nc < MIN_REPEAT:
            continue
        f = sum(1 for j in range(nc) if k[j] == k[j + L]) / nc
        if f > best[0]:
            best = (f, L, nc)
    return best


def f_positions(ct, start, span):
    return [i for i in range(span) if start + i < len(ct) and ct[start + i] == 0]


def scan(pages, positions, cribs, max_skip=2):
    hits, partials = [], []
    for si, off, kind in positions:
        ct = pages[si]
        for lat, t in cribs:
            span = len(t) + max_skip
            fps = f_positions(ct, off, span)
            skipsets = [()]
            for r in range(1, max_skip + 1):
                skipsets += list(itertools.combinations(fps, r))
            for sign in (-1, +1):
                for sk in skipsets:
                    k = readout(ct, off, t, sign, set(sk))
                    if k is None:
                        continue
                    ep = exact_periods(k)
                    if ep:
                        hits.append((si, off, kind, lat, gp.indices_to_translit(t), sign,
                                     sk, ep, gp.indices_to_translit(k)))
                    partials.append(best_partial(k)[0])
    return hits, partials


def positive_control(cribs):
    print("== T1b POSITIVE CONTROL ==")
    idxs, _ = b3lib.solved_page("03.jpg")
    ok = False
    for lat, t in cribs:
        if lat != "WELCOMEWELCOMEPILGRIM":
            continue
        for sign in (-1, +1):
            k = readout(idxs, 0, t, sign)
            if k is None:
                continue
            ep = exact_periods(k)
            if ep:
                print(f"  03.jpg crib {gp.indices_to_translit(t)} sign{sign:+d}: "
                      f"exact periods {ep}  readout {gp.indices_to_translit(k)}")
                if any(L == 8 for L, _ in ep):
                    print("        -> period 8 = DIUINITY  PASS")
                    ok = True
    idxs14, _ = b3lib.solved_page("14.jpg")
    for lat, t in cribs:
        if lat != "AKOANDURINGALESSON":
            continue
        for sign in (-1, +1):
            for sk in [()] + [(i,) for i in f_positions(idxs14, 0, len(t) + 2)]:
                k = readout(idxs14, 0, t, sign, set(sk))
                if k is None:
                    continue
                ep = exact_periods(k)
                if ep:
                    print(f"  14.jpg crib {gp.indices_to_translit(t)} sign{sign:+d} skips{sk}: "
                          f"exact periods {ep}  readout {gp.indices_to_translit(k)}")
    print(f"  POSITIVE CONTROL: {'PASS' if ok else 'FAIL'}\n")
    return ok


def main():
    rng = random.Random(3301)
    cribs = crib_keys()
    print(f"crib variants (>= {MIN_CRIB} runes): {len(cribs)} "
          f"from {len(CRIB_PHRASES)} semantic phrases")
    if not positive_control(cribs):
        print("ABORT: positive control failed, instrument void")
        return 1

    import t1_titlecrib as t1
    positions = [p for p in t1.crib_positions() if p[0] < 55]
    pages = b3lib.lp2_segments()[:55]
    print(f"positions: {len(positions)}   "
          f"total readouts ~ {len(positions)*len(cribs)*2*4}")

    hits, partials = scan(pages, positions, cribs)
    print(f"\nREAL: exact-period hits = {len(hits)}")
    for h in hits[:20]:
        print("   ", h)

    # NULL A: pseudo-cribs of matched lengths from the English generator
    eng = english_baseline()
    lens = [len(t) for _, t in cribs]
    ncribs = []
    for L in lens:
        s = rng.randrange(0, len(eng) - L - 1)
        ncribs.append(("<null>", tuple(eng[s:s + L])))
    nhits, npartials = scan(pages, positions, ncribs)
    print(f"NULL-A (pseudo-cribs): exact-period hits = {len(nhits)}")

    # NULL B: real cribs vs shuffled ciphertext
    shuf = []
    for ct in pages:
        c = list(ct)
        rng.shuffle(c)
        shuf.append(c)
    bhits, bpartials = scan(shuf, positions, cribs)
    print(f"NULL-B (shuffled ct):  exact-period hits = {len(bhits)}")

    import statistics
    for nm, v in (("REAL", partials), ("NULL-A", npartials), ("NULL-B", bpartials)):
        print(f"  {nm:<7s} best-partial-period fraction: n={len(v)} "
              f"max={max(v):.3f} mean={statistics.mean(v):.4f} "
              f"sd={statistics.pstdev(v):.4f}")

    json.dump({
        "n_cribs": len(cribs), "n_positions": len(positions),
        "real_hits": len(hits), "nullA_hits": len(nhits), "nullB_hits": len(bhits),
        "real_hit_detail": [list(map(str, h)) for h in hits[:50]],
        "real_max_partial": max(partials), "nullA_max_partial": max(npartials),
        "nullB_max_partial": max(bpartials),
    }, open("T1B-RESULTS.json", "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
