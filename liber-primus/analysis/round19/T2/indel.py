"""T2 -- the INDEL PROBE.  Bounds insertion/deletion and segmentation errors in canon.

T3's stated largest gap: "every model here is substitution-only and preserves
n=12,956.  Insertions/deletions and segmentation errors are not bounded at all."
This is the instrument that bounds them, and it needs no new machinery: a forced
alignment already knows how many tokens the ink will accept.

  deletion probe   cost_del[j] = min_x alpha[j][x] + beta[j+1][x]
                   (token j removed and its columns skipped)
                   delta_del[j] = C_canon - cost_del[j]
                   > 0  =>  the line is CHEAPER without canon's token j
                            =>  canon may carry an EXTRA rune there

  insertion probe  cost_ins[j] = min_{r,x} alpha[j][x] + m_r[x] + 6 + beta[j][x+w_r]
                   delta_ins[j] = C_canon - cost_ins[j]
                   > 0  =>  the line is CHEAPER with one MORE rune before slot j
                            =>  canon may be MISSING a rune there

PLANTS (PREREG section 2 discipline; these simulate a CANON error, not an image
error, so no ink surgery is involved and the plant is exactly the thing hunted):

  plant DEL  canon token j is dropped from the forced sequence -- i.e. canon is
             pretending to be missing a rune that IS in the ink.  The insertion
             probe must fire at position j and name the dropped rune.
  plant INS  a random rune is inserted into the forced sequence at position j --
             canon pretending to carry a rune the ink does not have.  The deletion
             probe must fire at position j.

usage: python3 indel.py
"""
import os, json, time, collections
import numpy as np
import t2lib as T
from probe import band_of
from lp.gematria import IDX_TO_TRANS

rng = np.random.default_rng(1337)
ALT = list(range(29))


def stratum(seg):
    if seg in (55, 56):
        return 'solved-LP2'
    if 45 <= seg <= 54:
        return 'dense-45-54'
    return 'pages-0-44'


def del_deltas(alpha, beta, C, L):
    """delta_del[j] for j in 0..L-1"""
    out = np.empty(L)
    for j in range(L):
        out[j] = C - float(np.min(alpha[j] + beta[j + 1]))
    return out


def ins_deltas(alpha, beta, C, L, cc, W):
    """(delta_ins[j], best rune r) for insertion BEFORE slot j, j in 0..L"""
    best = np.full(L + 1, -np.inf)
    who = np.zeros(L + 1, np.int64)
    for j in range(L + 1):
        a = alpha[j]
        b = beta[j]
        lo = np.inf
        arg = 0
        for r in ALT:
            if r not in cc:
                continue
            m, tw = cc[r]
            n = min(len(m), W - tw + 1)
            if n <= 0:
                continue
            v = a[:n] + m[:n] + T.GLYPH_PRIOR + b[tw:tw + n]
            mv = float(v.min())
            if mv < lo:
                lo, arg = mv, r
        best[j] = C - lo
        who[j] = arg
    return best, who


def main():
    lm = json.load(open(os.path.join(T.HERE, 'out_linemap.json')))['map']
    canon = T.canon_lines()
    tmpl = T.load_templates()
    rows, plants = [], []
    t0 = time.time()
    for k, rec in enumerate(lm):
        line = canon[rec['gline']]
        keys = list(line['runes'])
        if rec.get('initial') and keys:
            keys = keys[1:]
        band, bx, by = band_of(rec)
        W = band.shape[1]
        if W < 40 or not keys:
            continue
        cc = T.cost_curves(band, tmpl)
        if any(r not in cc for r in keys):
            continue
        skip = band.sum(0) * T.SKIP_A + T.SKIP_B
        S = np.concatenate([[0.0], np.cumsum(skip)])

        def run(kk):
            a = T.forward(band, kk, cc, skip, S)
            b = T.backward(band, kk, cc, skip, S)
            return a, b, float(a[len(kk)][W])

        L = len(keys)
        a, b, C = run(keys)
        dd = del_deltas(a, b, C, L)
        di, dw = ins_deltas(a, b, C, L, cc, W)
        rows.append(dict(gline=rec['gline'], seg=rec['seg'], num=rec['num'],
                         stratum=stratum(rec['seg']), L=L, C=round(C, 1),
                         max_del=round(float(dd.max()), 1),
                         arg_del=int(dd.argmax()),
                         max_ins=round(float(di.max()), 1),
                         arg_ins=int(di.argmax()),
                         ins_rune=int(dw[di.argmax()])))

        # ---- plant DEL: canon missing a rune that is in the ink
        j = int(rng.integers(0, L))
        kk = keys[:j] + keys[j + 1:]
        a2, b2, C2 = run(kk)
        di2, dw2 = ins_deltas(a2, b2, C2, len(kk), cc, W)
        plants.append(dict(kind='canon_missing_rune', stratum=stratum(rec['seg']),
                           gline=rec['gline'], pos=j, truth=keys[j],
                           fired=int(di2.max() > 0.0),
                           loc=int(int(di2.argmax()) == j),
                           rune=int(int(dw2[di2.argmax()]) == keys[j]),
                           delta=round(float(di2.max()), 1)))

        # ---- plant INS: canon carrying a rune the ink does not have
        j = int(rng.integers(0, L + 1))
        r = int(rng.integers(0, 29))
        kk = keys[:j] + [r] + keys[j:]
        if all(q in cc for q in kk):
            a3, b3, C3 = run(kk)
            dd3 = del_deltas(a3, b3, C3, len(kk))
            plants.append(dict(kind='canon_extra_rune', stratum=stratum(rec['seg']),
                               gline=rec['gline'], pos=j, truth=r,
                               fired=int(dd3.max() > 0.0),
                               loc=int(int(dd3.argmax()) == j),
                               rune=None,
                               delta=round(float(dd3.max()), 1)))
        if (k + 1) % 50 == 0:
            print('  %d/%d  %.0fs' % (k + 1, len(lm), time.time() - t0), flush=True)

    json.dump(dict(rows=rows, plants=plants),
              open(os.path.join(T.HERE, 'out_indel.json'), 'w'))
    print('wrote out_indel.json  (%d lines, %d plants)' % (len(rows), len(plants)))


if __name__ == '__main__':
    main()
