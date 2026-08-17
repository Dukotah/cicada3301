"""Phase-flexible screening decoder for a PERIODIC key under an unknown interrupter mask.

Why this and not a rigid decode: on the solved keyed pages the F-rune interrupter is a NULL that
does not advance the key, so every skipped F shifts the key phase by exactly -1 for the whole
remainder of the page.  A rigid decode therefore scores the CORRECT key as noise (demonstrated:
gate run 1, DIVINITY ranked 53rd at -7.274 on 03.jpg).  Between two consecutive F runes the phase
is constant, so:

    split the page at F positions -> per segment, take the best key ROTATION -> length-weighted mean

is exact for a periodic key with any interrupter mask, and costs L full decodes instead of a beam.
It is deliberately permissive (each segment picks its own phase), so it is a SCREEN; the survivors
are re-ranked with the repo's own solve.find_interrupters beam.
"""
import b3lib
from b3lib import gp

N = gp.N
MIN_SEG = 10


def segments_of(idxs):
    fpos = [i for i, c in enumerate(idxs) if c == 0]
    bounds = [0] + [p for p in fpos if p > 0] + [len(idxs)]
    segs = []
    for a, b in zip(bounds, bounds[1:]):
        if b - a >= MIN_SEG:
            segs.append((a, b))
    if not segs:
        segs = [(0, len(idxs))]
    return segs


def phase_flexible_score(idxs, key, sign, atbash, scorer, segs=None):
    """Length-weighted mean of per-segment best-rotation score_norm."""
    L = len(key)
    if segs is None:
        segs = segments_of(idxs)
    # precompute decoded translit per rotation
    rots = []
    for r in range(L):
        out = []
        for j, c in enumerate(idxs):
            base = (N - 1 - c) if atbash else c
            out.append(gp.IDX_TO_TRANS[(base + sign * key[(j + r) % L]) % N])
        rots.append(out)
    tot, wt = 0.0, 0
    parts = []
    for a, b in segs:
        best = -99.0
        bi = 0
        for r in range(L):
            s = scorer.score_norm("".join(rots[r][a:b]))
            if s > best:
                best, bi = s, r
        tot += best * (b - a)
        wt += (b - a)
        parts.append((a, b, bi, best))
    return tot / max(wt, 1), parts, rots


def rigid_text(idxs, key, sign, atbash, rot=0):
    L = len(key)
    return "".join(gp.IDX_TO_TRANS[(((N - 1 - c) if atbash else c)
                                    + sign * key[(j + rot) % L]) % N]
                   for j, c in enumerate(idxs))
