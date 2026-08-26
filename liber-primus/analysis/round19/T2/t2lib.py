"""T2 shared library — line geometry, templates, forced alignment, LOO probe.

Everything here reuses already-validated pieces:
  * templates + class->rune bijection : analysis/retranscribe/{templates.npz,diff_report.json}
  * per-column mismatch + DP constants: analysis/retranscribe/read.py (verbatim)
  * ornament/rune/dot height bands    : analysis/round12/frontB (measured)
  * glyph-width prior                 : analysis/round18/L4-forcing (validated corr .879)

The NEW thing is the forced alignment: canon supplies the token SEQUENCE, the ink
chooses the cut points. See PREREG.md §1.
"""
import os
import sys
import json
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.signal import fftconvolve

HERE = os.path.dirname(os.path.abspath(__file__))
LP = HERE
while LP != os.path.dirname(LP) and os.path.basename(LP) != 'liber-primus':
    LP = os.path.dirname(LP)
ROOT = os.path.normpath(os.path.join(LP, '..'))
RT = os.path.join(LP, 'analysis', 'retranscribe')
RELIKD = os.path.join(LP, 'data', 'relikd')
VENDOR = os.path.join(ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')
sys.path.insert(0, os.path.join(LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS      # noqa: E402

PAD_H, PAD_W = 128, 136
MINCLASS = 100

# measured in round12/frontB: runes ~95-132 px tall, ornaments ~41-91, dots ~7-10
RUNE_H = (95, 132)
SEP_H = (4, 34)

# ---------------------------------------------------------------- canon


def canon_lines():
    """604 canon lines as token lists.

    Token is (kind, value): ('r', rune_index) | ('s', '-') | ('s', '.')
    Returns list of dicts: seg, line_in_seg, tokens, runes.
    """
    txt = open(os.path.join(LP, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
    out = []
    for si, seg in enumerate(txt.split('%')):
        li = 0
        for ln in seg.split('/'):
            toks = []
            for c in ln:
                if c in RUNE_TO_IDX:
                    toks.append(('r', RUNE_TO_IDX[c]))
                elif c == '-':
                    toks.append(('s', '-'))
                elif c == '.':
                    toks.append(('s', '.'))
            if not any(t[0] == 'r' for t in toks):
                continue
            out.append(dict(seg=si, line_in_seg=li, tokens=toks,
                            runes=[t[1] for t in toks if t[0] == 'r']))
            li += 1
    return out


# ---------------------------------------------------------------- images

_ink_cache = {}


def page_ink(path):
    if path not in _ink_cache:
        a = np.asarray(Image.open(path).convert('L'))
        _ink_cache[path] = (a < 128).astype(np.float32)
        if len(_ink_cache) > 4:
            for k in list(_ink_cache):
                if k != path:
                    del _ink_cache[k]
                    break
    return _ink_cache[path]


_mask_cache = {}


def text_mask(path, xlo=330, xhi=2070, hmin=40, hmax=140, wmax=200):
    """Page ink with everything that is not body-text ink removed.

    Dropped: the ~9x10 px separator dots and the dotted `.` lozenge (h < 40), the
    margin floral ornaments and folio marks (out of column), and the large
    decorative drop-caps (h up to 608 px -- these sit INSIDE the text column and
    are the reason a naive band read slips on a page's first line).
    Kept: split rune strokes (h 41-94) and merged rune pairs (w up to 200).
    Height classes are the ones measured in round12/frontB.
    """
    key = (path, xlo, xhi, hmin, hmax, wmax)
    if key in _mask_cache:
        return _mask_cache[key]
    ink = page_ink(path)
    lbl, n = ndimage.label(ink > 0)
    objs = ndimage.find_objects(lbl)
    keep = np.zeros(n + 1, bool)
    for i, sl in enumerate(objs):
        ys, xs = sl
        h = ys.stop - ys.start
        w = xs.stop - xs.start
        xc = (xs.start + xs.stop) / 2
        if hmin <= h <= hmax and w <= wmax and xlo < xc < xhi:
            keep[i + 1] = True
    out = np.where(keep[lbl], ink, 0.0).astype(np.float32)
    _mask_cache.clear()
    _mask_cache[key] = out
    return out


def components(ink):
    lbl, n = ndimage.label(ink > 0)
    objs = ndimage.find_objects(lbl)
    comps = []
    for sl in objs:
        ys, xs = sl
        comps.append(dict(y0=ys.start, y1=ys.stop, x0=xs.start, x1=xs.stop,
                          h=ys.stop - ys.start, w=xs.stop - xs.start))
    return comps


def text_rows(path, xlo=330, xhi=2070):
    """Split a page into text rows using RUNE-HEIGHT components in the text column.

    Ornament swirls (h 41-91) and edge dots (h 7-10) at the margins are excluded by
    the height filter and the column window, which is the ornament-stripping pass
    frontB verified visually.
    Returns [(y0, y1, x0, x1, n_rune_comps)] top to bottom.
    """
    ink = page_ink(path)
    comps = [c for c in components(ink)
             if RUNE_H[0] <= c['h'] <= RUNE_H[1] and 6 <= c['w'] <= 110
             and xlo < (c['x0'] + c['x1']) / 2 < xhi]
    if not comps:
        return []
    comps.sort(key=lambda c: (c['y0'] + c['y1']) / 2)
    rows, cur = [], [comps[0]]
    for c in comps[1:]:
        med = np.median([(d['y0'] + d['y1']) / 2 for d in cur])
        if (c['y0'] + c['y1']) / 2 - med > 55:
            rows.append(cur)
            cur = []
        cur.append(c)
    rows.append(cur)
    out = []
    for R in rows:
        y0 = min(c['y0'] for c in R)
        y1 = max(c['y1'] for c in R)
        x0 = min(c['x0'] for c in R)
        x1 = max(c['x1'] for c in R)
        out.append((int(y0), int(y1), int(x0), int(x1), len(R)))
    return out


# ---------------------------------------------------------------- templates


def load_templates():
    """[(rune_index, bitmap)] for the 29 runes, via the stored R9 bijection."""
    t = np.load(os.path.join(RT, 'templates.npz'))
    X, label, sizes, centres = t['X'], t['label'], t['sizes'], t['centres']
    kh, kw = t['keys_h'], t['keys_w']
    cover = np.bincount(label, weights=sizes, minlength=label.max() + 1)
    mapping = {int(k): int(v) for k, v in
               json.load(open(os.path.join(RT, 'diff_report.json')))['mapping'].items()}
    out = {}
    for c in range(len(cover)):
        if cover[c] < MINCLASS or c not in mapping:
            continue
        i = centres[c]
        h, w = int(kh[i]), int(kw[i])
        canvas = X[i].reshape(PAD_H, PAD_W).astype(np.float32)
        top = (PAD_H - h) // 2
        left = (PAD_W - w) // 2
        out[mapping[c]] = canvas[top:top + h, left:left + w]
    return out


def build_separator_templates(pages, n=400):
    """Median bitmap of the '-' and '.' separator components.

    Both render as small marks; they are collected by height and split by the
    bimodal width/height signature, then represented as a single averaged mask
    each. Built from the image only -- no canon input.
    """
    crops = []
    for p in pages:
        ink = page_ink(p)
        for c in components(ink):
            if SEP_H[0] <= c['h'] <= SEP_H[1] and 4 <= c['w'] <= 34 \
                    and 330 < (c['x0'] + c['x1']) / 2 < 2070:
                crops.append((c['h'], c['w'],
                              ink[c['y0']:c['y1'], c['x0']:c['x1']].copy()))
            if len(crops) >= n:
                break
        if len(crops) >= n:
            break
    if not crops:
        return {}
    hs = np.array([c[0] for c in crops])
    ws = np.array([c[1] for c in crops])
    return dict(n=len(crops), h_med=float(np.median(hs)), w_med=float(np.median(ws)),
                h_hist=np.bincount(hs).tolist(), w_hist=np.bincount(ws).tolist())


# ---------------------------------------------------------------- alignment

DY = (-3, -1, 0, 1, 3)
GLYPH_PRIOR = 6.0
SKIP_A = 3.0
SKIP_B = 0.5
INF = 1e18


def cost_curves(band, tmpl):
    """{token_key: (cost_vector, width)} for every template over every column."""
    bh = band.shape[0]
    W = band.shape[1]
    out = {}
    for key, T in tmpl.items():
        th, tw = T.shape
        if tw >= W or th > bh:
            continue
        best = None
        Ts = float(T.sum())
        for dy in DY:
            top = (bh - th) // 2 + dy
            if top < 0 or top + th > bh:
                continue
            sub = band[top:top + th]
            corr = fftconvolve(sub, T[::-1, ::-1], mode='valid')[0]
            box = np.convolve(sub.sum(0), np.ones(tw), mode='valid')
            mism = Ts + box - 2.0 * corr
            best = mism if best is None else np.minimum(best, mism)
        if best is not None:
            out[key] = (np.asarray(best, np.float64), tw)
    return out


def _skipcost(band):
    colink = band.sum(0)
    return colink * SKIP_A + SKIP_B


def _relax_fwd(v, S):
    """v[x] <- min_{y<=x} (v[y] + S[x] - S[y]); S = prefix sums of skip cost."""
    return S + np.minimum.accumulate(v - S)


def _relax_bwd(v, S):
    """v[x] <- min_{y>=x} (v[y] + S[y] - S[x])."""
    return np.minimum.accumulate((v + S)[::-1])[::-1] - S


def forward(band, keys, cc, skip, S=None):
    """alpha[j][x] = min cost of placing tokens 0..j-1 so that token j starts at x.

    Free leading/trailing blank columns are paid at skip cost, so the alignment is
    not forced to start at column 0.
    """
    W = band.shape[1]
    L = len(keys)
    if S is None:
        S = np.concatenate([[0.0], np.cumsum(skip)])
    alpha = np.full((L + 1, W + 1), INF)
    alpha[0] = S.copy()
    for j in range(L):
        m, tw = cc[keys[j]]
        prev = alpha[j]
        nxt = np.full(W + 1, INF)
        n = min(len(m), W - tw + 1)
        if n > 0:
            nxt[tw:tw + n] = prev[:n] + m[:n] + GLYPH_PRIOR
        alpha[j + 1] = _relax_fwd(nxt, S)
    return alpha


def backward(band, keys, cc, skip, S=None):
    """beta[j][x] = min cost of placing tokens j..L-1 given they start at or after x."""
    W = band.shape[1]
    L = len(keys)
    if S is None:
        S = np.concatenate([[0.0], np.cumsum(skip)])
    beta = np.full((L + 1, W + 1), INF)
    beta[L] = S[W] - S
    for j in range(L - 1, -1, -1):
        m, tw = cc[keys[j]]
        nxt = beta[j + 1]
        cur = np.full(W + 1, INF)
        n = min(len(m), W - tw + 1)
        if n > 0:
            cur[:n] = m[:n] + GLYPH_PRIOR + nxt[tw:tw + n]
        beta[j] = _relax_bwd(cur, S)
    return beta


def align_cost(band, keys, cc, skip, S=None):
    a = forward(band, keys, cc, skip, S)
    return float(a[len(keys)][band.shape[1]]), a


def loo_probe(band, keys, cc, skip, alt_keys, S=None):
    """Per-slot leave-one-out substitution.

    Returns (total_cost, alpha, beta, table) where table[j] is an array over
    `alt_keys` of the best total line cost with token j replaced by that key, and
    argmin_x of the placement for the canon token.
    """
    W = band.shape[1]
    L = len(keys)
    if S is None:
        S = np.concatenate([[0.0], np.cumsum(skip)])
    alpha = forward(band, keys, cc, skip, S)
    beta = backward(band, keys, cc, skip, S)
    total = float(alpha[L][W])
    table = np.full((L, len(alt_keys)), INF)
    xpos = np.zeros(L, np.int64)
    for j in range(L):
        a = alpha[j]
        b = beta[j + 1]
        for ki, r in enumerate(alt_keys):
            if r not in cc:
                continue
            m, tw = cc[r]
            n = min(len(m), W - tw + 1)
            if n <= 0:
                continue
            v = a[:n] + m[:n] + GLYPH_PRIOR + b[tw:tw + n]
            table[j, ki] = v.min()
            if r == keys[j]:
                xpos[j] = int(v.argmin())
    return total, alpha, beta, table, xpos
