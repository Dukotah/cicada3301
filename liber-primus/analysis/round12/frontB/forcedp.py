"""Forced-COUNT template DP (the honest forced segmentation).

R9's read.py used an UNCONSTRAINED template DP -- it chose however many glyphs
minimised cost, which over/under-segments dense lines. Here we add a hard count
dimension: f[x][g] = min cost to explain columns [0,x) with EXACTLY g glyphs.
We then read out the path that ends at (W, n_runes). This forces the known rune
count per line while letting the DP place the cuts where templates actually fit
-- the joint optimisation R9 lacked. Separator dots are removed from the ink
first (they have no template), so g counts runes only.

Cost of placing template t starting at column x uses the R9 formula
    mism(t,x) = T.sum() + box_ink(x..x+w) - 2*corr(T, ink at x)
minimised over a small vertical offset, exactly as read.py.
"""
import numpy as np
from scipy.signal import fftconvolve


def glyph_costs(ink, tmpl):
    """For each template, cost array over start columns x (len Wl-tw+1..)."""
    band_h, Wl = ink.shape
    costs = {}
    for cid, T in tmpl:
        th, tw = T.shape
        if tw >= Wl:
            continue
        best = None
        for dy in (-3, -1, 0, 1, 3):
            top = (band_h - th) // 2 + dy
            if top < 0 or top + th > band_h:
                continue
            sub = ink[top:top + th]
            corr = fftconvolve(sub, T[::-1, ::-1], mode='valid')[0]
            box = np.convolve(sub.sum(0), np.ones(tw), mode='valid')
            mism = T.sum() + box - 2.0 * corr
            best = mism if best is None else np.minimum(best, mism)
        if best is not None:
            costs[cid] = (best, tw)
    return costs


def forced_count_decode(ink, tmpl, n_glyph, glyph_prior=6.0,
                        skip_cost=3.0, blank=0.5):
    """DP with an exact glyph-count constraint. Returns list of (cid, x, cost)
    of length n_glyph (or best achievable if infeasible)."""
    Wl = ink.shape[1]
    colink = ink.sum(0)
    costs = glyph_costs(ink, tmpl)
    INF = 1e18
    G = n_glyph
    f = np.full((Wl + 1, G + 1), INF)
    bk = [[None] * (G + 1) for _ in range(Wl + 1)]
    f[0, 0] = 0.0
    for x in range(Wl):
        for g in range(G + 1):
            if f[x, g] == INF:
                continue
            base = f[x, g]
            # blank column: skip, no glyph added
            nc = base + colink[x] * skip_cost + blank
            if nc < f[x + 1, g]:
                f[x + 1, g] = nc
                bk[x + 1][g] = ('skip', x, g)
            if g < G:
                for cid, (m, tw) in costs.items():
                    if x + tw > Wl or x >= len(m):
                        continue
                    nc = base + m[x] + glyph_prior
                    if nc < f[x + tw, g + 1]:
                        f[x + tw, g + 1] = nc
                        bk[x + tw][g + 1] = ('g', x, g, cid, float(m[x]))
    # backtrack from (Wl, G); if INF, relax to nearest reachable count
    endg = G
    if f[Wl, G] >= INF:
        reach = [g for g in range(G + 1) if f[Wl, g] < INF]
        if not reach:
            return []
        endg = min(reach, key=lambda g: abs(g - G))
    out = []
    x, g = Wl, endg
    while x > 0 and bk[x][g] is not None:
        b = bk[x][g]
        if b[0] == 'g':
            out.append((b[3], b[1], b[4]))
            x, g = b[1], b[2]
        else:
            x, g = b[1], b[2]
    out.reverse()
    return out
