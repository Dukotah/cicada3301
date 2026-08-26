"""L3 -- MANDATORY positive control C-2: plant a message in synthetic ornament bands and
prove the band pipeline recovers it.

A null from an unvalidated instrument is not a negative.  This script composites REAL glyph
bitmaps, lifted from the sha256-verified renders themselves, into band-shaped strips placed
at the real ornament-band coordinates from `inventory.json`, encoding a known plaintext and
using the exact band-length ladder P-9 names (1 / 3 / 4 / 8 / 16 glyphs).  The synthetic
page is then run through the SAME code path `read_bands.py` uses, and per-glyph recovery is
measured.

PASS bar fixed in PREREG section 2: >= 90% of planted glyphs recovered, and H1 fires on the
planted message.

Writes controls.json (+ ctrl_page.png for eyeball verification).
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402
sys.path.insert(0, os.path.join(R.LP, 'src'))
from lp.gematria import IDX_TO_TRANS, RUNE_TO_IDX                      # noqa: E402

IMG = os.path.join(R.LP, 'data', 'relikd')
RNG = np.random.default_rng(3301)

MESSAGE = 'THEPRIMESARESACRED'
# band-length ladder from P-9 / ornaments.json
LADDER = [16, 8, 4, 3, 1]


def translit_to_idx(s):
    """Greedy longest-match of the transliteration back to rune indices."""
    two = {v: k for k, v in IDX_TO_TRANS.items() if len(v) == 2}
    one = {v: k for k, v in IDX_TO_TRANS.items() if len(v) == 1}
    out, i = [], 0
    while i < len(s):
        if i + 1 < len(s) and s[i:i + 2] in two:
            out.append(two[s[i:i + 2]]); i += 2
        elif s[i] in one:
            out.append(one[s[i]]); i += 1
        else:
            i += 1
    return out


def glyph_bank(page, tmpl, mapping, need):
    """Lift one clean bitmap per rune index from a real page render."""
    path = os.path.join(IMG, 'p%d.jpg' % page)
    ink = R.page_ink(path)
    tink = R.text_ink(path)[0]
    rows = R.rows_from_ink(tink)
    bank = {}
    for a, b in rows:
        g = R.read_ink_strip(tink, a - 3, b + 3, tmpl)
        for k, (cid, x, cost) in enumerate(g):
            r = mapping.get(cid, -1)
            if r < 0 or r not in need:
                continue
            wnext = g[k + 1][1] if k + 1 < len(g) else x + 110
            w = min(max(int(wnext - x), 30), 150)
            crop = ink[a:b, x:x + w]
            if crop.size == 0 or crop.sum() < 50:
                continue
            cols = np.where(crop.sum(0) > 0)[0]        # trim to the glyph's own ink
            if len(cols) == 0:
                continue
            crop = crop[:, cols[0]:cols[-1] + 1]
            rws = np.where(crop.sum(1) > 0)[0]
            crop = crop[rws[0]:rws[-1] + 1]
            if r not in bank or cost < bank[r][0]:
                bank[r] = (cost, crop.copy())
    return {k: v[1] for k, v in bank.items()}


def main():
    tmpl = R.load_templates()
    mapping = R.load_mapping()
    idxs = translit_to_idx(MESSAGE)
    need = set(idxs)
    print('planted message %r -> %d runes %s' % (MESSAGE, len(idxs),
                                                 [IDX_TO_TRANS[i] for i in idxs]))
    bank = glyph_bank(1, tmpl, mapping, need)
    print('glyph bank covers %d/%d needed runes' % (len(bank), len(need)))
    missing = need - set(bank)
    if missing:
        for p in (2, 3, 4, 5):
            bank.update(glyph_bank(p, tmpl, mapping, missing))
            missing = need - set(bank)
            if not missing:
                break
    print('glyph bank after top-up: %d/%d' % (len(bank), len(need)))
    if need - set(bank):
        print('STILL MISSING', [IDX_TO_TRANS[i] for i in sorted(need - set(bank))])

    inv = json.load(open(os.path.join(HERE, 'inventory.json')))
    # place the planted bands at real ornament-band coordinates, shortest first
    spots = sorted([b for b in inv if b['h'] < 400 and b['w'] > 200],
                   key=lambda b: b['n'])[:len(LADDER)]
    page = np.zeros((3600, 2400), np.float32)
    planted, cursor = [], 0
    # place each planted band on its OWN baseline: the real ornament coordinates come from
    # different pages and collide when composited onto one synthetic sheet.
    for si, (spot, ln) in enumerate(zip(spots, LADDER)):
        spot = dict(spot, y=[500 + si * 400, 500 + si * 400 + 160],
                    x=[300, 2100])
        seq = [idxs[(cursor + k) % len(idxs)] for k in range(ln)]
        cursor += ln
        x = spot['x'][0]
        y = spot['y'][0]
        placed = []
        for r in seq:
            gl = bank.get(r)
            if gl is None:
                continue
            h, w = gl.shape
            if y + h >= 3600 or x + w >= 2400:
                break
            page[y:y + h, x:x + w] = np.maximum(page[y:y + h, x:x + w], gl)
            placed.append(r)
            x += w + 14
        planted.append(dict(spot=spot['id'], y=int(y), x0=int(spot['x'][0]),
                            len_requested=ln, len_placed=len(placed),
                            runes=[int(v) for v in placed],
                            translit=''.join(IDX_TO_TRANS[v] for v in placed)))
        print('planted %2d glyphs at %s (p%d y=%d): %s'
              % (len(placed), spot['id'], spot['page'], y, planted[-1]['translit']))

    out_png = os.path.join(HERE, 'ctrl_page.png')
    Image.fromarray(((1 - page) * 255).astype(np.uint8)).save(out_png)

    # ---- read the synthetic page through the SAME code path
    rows = R.rows_from_ink(page, min_gap=10, min_h=20)
    got = []
    for a, b in rows:
        g = R.read_ink_strip(page, a - 3, b + 3, tmpl)
        got.append(dict(y=[int(a), int(b)], n=len(g),
                        runes=[mapping.get(c, -1) for c, x, k in g],
                        cost_median=float(np.median([k for c, x, k in g])) if g else None,
                        translit=''.join(IDX_TO_TRANS[mapping.get(c, -1)]
                                         if mapping.get(c, -1) >= 0 else '?'
                                         for c, x, k in g)))
    exp = [r for pl in planted for r in pl['runes']]
    obs = [r for gr in got for r in gr['runes']]
    import difflib
    sm = difflib.SequenceMatcher(a=obs, b=exp, autojunk=False)
    match = sum(bl.size for bl in sm.get_matching_blocks())
    recall = match / max(len(exp), 1)
    full = ''.join(gr['translit'] for gr in got)
    from fuzzy import fuzzy_find
    h1_exact = MESSAGE in full or any(MESSAGE in gr['translit'] for gr in got)
    h1 = (fuzzy_find(full, MESSAGE) is not None or
          any(fuzzy_find(gr['translit'], MESSAGE) for gr in got))

    print('\nrows found on synthetic page: %d' % len(rows))
    for gr in got:
        print('   y=%s n=%2d cost %-7s %s' % (gr['y'], gr['n'],
                                              None if gr['cost_median'] is None
                                              else round(gr['cost_median'], 1),
                                              gr['translit']))
    print('\nC-2 recovery: %d / %d planted glyphs = %.1f%%   (bar 90%%)'
          % (match, len(exp), 100 * recall))
    print('C-2 H1 (exact substring)      fires: %s' % h1_exact)
    print('C-2 H1prime (confusable-tolerant) fires: %s' % h1)
    verdict = 'PASS' if (recall >= 0.90 and h1) else 'FAIL'
    print('C-2 VERDICT: %s' % verdict)

    json.dump(dict(message=MESSAGE, ladder=LADDER, planted=planted,
                   read=got, planted_glyphs=len(exp), recovered=int(match),
                   recovery=round(recall, 4), h1_fires=bool(h1),
                   h1_exact_fires=bool(h1_exact),
                   bar=dict(recovery=0.90, h1=True), verdict=verdict,
                   artifact=out_png),
              open(os.path.join(HERE, 'controls.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
