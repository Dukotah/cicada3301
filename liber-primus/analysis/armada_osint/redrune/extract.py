"""RED-RUNE extraction + cryptanalytic test for the relikd Liber Primus renders.

Established (verified): the relikd page JPEGs carry genuine saturated red ink
(mean RGB ~ (187,2,3)) on select glyphs. The transliteration carries NO colour,
so the red runes as a *selection* have never been cryptanalysed.

PAGE<->CANON ALIGNMENT (STEP 2):
  Count-signature matching per this session's own attempt proved UNRELIABLE: the
  stones segmenter under-/over-counts by +-2-3 glyphs/line, so per-line cost
  exceeds between-page discrimination (only 1/56 pages confidently matched).
  We therefore reuse the ALREADY-SOLVED image<->canon alignment baked into the
  stones pipeline (`analysis/stones/build_dataset.py` + `alignment.json`), whose
  premise is verified in that module: relikd LINE order == krisyotam LINE order
  exactly (594 identical lines), even though relikd *page numbers* differ from
  krisyotam page numbers. `dataset.npz` stores, for every one of 12,764
  segmented glyphs: its source image, its glyph box, and its aligned canon rune
  (10,774 glyphs on exact-count-match lines) OR a fallback classifier prediction
  (`all_pred.npy`, mean conf 0.96) for the rest.

We overlay the verified RED rule on each glyph box -> a red flag per canonically
placed rune. This is the confident extraction the count-signature path could not
deliver.

STEP 3  red-fraction per box (red_px / ink_px), classify red glyphs.
STEP 4  red rune subsequence (canon order) + Latin transliteration.
STEP 5  DECORATION-vs-DATA: is each page's red run the page's own opening/
        section-initial words, or a scattered independent selection?
STEP 6  cryptanalysis: red string direct/atbash/shift; red as add/Beaufort/atbash
        KEY over the black runes (calibrated scorer, English~-4, floor~-7.49).

Run:  PYTHONUTF8=1 python analysis/armada_osint/redrune/extract.py
"""
import os, sys, json
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "stones"))

from lp import gematria as gp, ciphers, score as _score

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

N = gp.N
SC = _score.default()
THRESHOLD = -5.2
RED_THR = 0.30
INK_THR = 128
RELIKD = os.path.join(ROOT, "data", "relikd")
STONES = os.path.join(ROOT, "analysis", "stones")


def red_mask(rgb):
    """Verified rule: R-(G+B)/2>40 & R>120 & G<80."""
    R = rgb[:, :, 0].astype(np.int16)
    G = rgb[:, :, 1].astype(np.int16)
    B = rgb[:, :, 2].astype(np.int16)
    return (R - (G + B) / 2 > 40) & (R > 120) & (G < 80)


def box_red_fraction(rgb, redimg, x0, x1, y0, y1):
    sub = rgb[y0:y1, x0:x1]
    subred = redimg[y0:y1, x0:x1]
    ink = (sub.mean(2) < INK_THR) | subred
    nink = int(ink.sum())
    if nink == 0:
        return 0.0
    return int(subred.sum()) / nink


def load_aligned_glyphs():
    """Return list of dicts, one per segmented glyph, in global reading order:
       {img, line, gi, gli, rune, matched, box=(x0,x1,y0,y1)}
    rune = canon rune if the line count-matched, else classifier prediction."""
    d = np.load(os.path.join(STONES, "dataset.npz"), allow_pickle=True)
    provall = d['provall']            # (img,line,glyph,gli,canon_rune_or_None,match)
    boxesall = d['boxesall']          # (img,x0,x1,y0,y1)
    pred = np.load(os.path.join(STONES, "all_pred.npy"), allow_pickle=True)
    conf = np.load(os.path.join(STONES, "all_conf.npy"))
    glyphs = []
    for i in range(len(provall)):
        img, line, gi, gli, canon, match = provall[i]
        _, x0, x1, y0, y1 = boxesall[i]
        rune = canon if canon is not None else pred[i]
        glyphs.append({'img': int(img), 'line': int(line), 'gi': int(gi),
                       'gli': int(gli), 'rune': str(rune),
                       'matched': bool(match), 'conf': float(conf[i]),
                       'box': (int(x0), int(x1), int(y0), int(y1))})
    return glyphs


def extract():
    glyphs = load_aligned_glyphs()
    # group by image so we open each JPEG once
    by_img = {}
    for g in glyphs:
        by_img.setdefault(g['img'], []).append(g)

    for img, gs in sorted(by_img.items()):
        path = os.path.join(RELIKD, f"p{img}.jpg")
        rgb = np.asarray(Image.open(path).convert('RGB'))
        redimg = red_mask(rgb)
        for g in gs:
            x0, x1, y0, y1 = g['box']
            g['frac'] = box_red_fraction(rgb, redimg, x0, x1, y0, y1)
            g['red'] = g['frac'] > RED_THR
    return glyphs


# ------------------------------------------------------- decoration test ------
def decoration_test(glyphs):
    """Per canon page (gli grouped), is the red run a contiguous prefix /
    section-initial run of that page's own text?  We use global-line index
    (gli) grouping since relikd page numbers are unreliable."""
    # group glyphs by canon PAGE. Map gli->page via alignment.json.
    align = json.load(open(os.path.join(STONES, "alignment.json")))
    gli_to_page = {}
    for pg, glis in align.items():
        for gl in glis:
            gli_to_page[gl] = int(pg)
    pages = {}
    for g in glyphs:
        pg = gli_to_page.get(g['gli'])
        pages.setdefault(pg, []).append(g)
    verdicts = {}
    for pg, gs in pages.items():
        gs = sorted(gs, key=lambda g: (g['gli'], g['gi']))
        reds = [i for i, g in enumerate(gs) if g['red']]
        if not reds:
            verdicts[pg] = ('no-red', 0, len(gs))
            continue
        if reds == list(range(len(reds))):
            kind = 'prefix'
        elif reds == list(range(reds[0], reds[0] + len(reds))):
            kind = 'contig-run'
        else:
            # single-line contiguous?
            lines_of = set(gs[i]['gli'] for i in reds)
            if len(lines_of) == 1:
                gidx = sorted(gs[i]['gi'] for i in reds)
                kind = 'line-run' if gidx == list(range(gidx[0], gidx[0] + len(gidx))) else 'scattered'
            else:
                kind = 'scattered'
        verdicts[pg] = (kind, len(reds), len(gs))
    return verdicts, pages


# --------------------------------------------------------- cryptanalysis ------
def translit(idxs):
    return gp.indices_to_translit(idxs)


def r2i(runes):
    return [gp.RUNE_TO_IDX[r] for r in runes if r in gp.RUNE_TO_IDX]


def keytest(red_idx, black_idx):
    out = []
    if red_idx:
        out.append(("RED direct", SC.score_norm(translit(red_idx)), translit(red_idx)[:90]))
        atb = ciphers.atbash_indices(red_idx)
        out.append(("RED atbash", SC.score_norm(translit(atb)), translit(atb)[:90]))
        bs = None
        for sh in range(1, N):
            p = [(c + sh) % N for c in red_idx]
            sc = SC.score_norm(translit(p))
            if bs is None or sc > bs[1]:
                bs = (sh, sc, translit(p)[:90])
        out.append((f"RED shift+{bs[0]}", bs[1], bs[2]))
    key_results = []
    if red_idx and black_idx:
        for kname, key in [("red", red_idx), ("red-rev", red_idx[::-1])]:
            L = len(black_idx)
            stream_fwd = [key[i % len(key)] for i in range(L)]
            for sign in (-1, +1):
                for atbash in (False, True):
                    for beaufort in (False, True):
                        if beaufort and sign == +1:
                            continue
                        src = ciphers.atbash_indices(black_idx) if atbash else black_idx
                        if beaufort:
                            p = [(stream_fwd[i] - c) % N for i, c in enumerate(src)]
                        else:
                            p = ciphers.apply_stream_to_indices(src, stream_fwd, sign=sign)
                        sc = SC.score_norm(translit(p))
                        mode = f"{kname} sign{sign:+d}{' atbash' if atbash else ''}{' beaufort' if beaufort else ''}"
                        key_results.append((sc, mode, translit(p)[:70]))
        key_results.sort(reverse=True)
    return out, key_results


def run():
    glyphs = extract()
    n_matched = sum(1 for g in glyphs if g['matched'])
    print("=" * 74)
    print(f"aligned glyphs: {len(glyphs)}  (canon-valued {n_matched}, "
          f"classifier-fallback {len(glyphs)-n_matched})")
    print("=" * 74)

    # sensitivity
    print("\nRED sensitivity (glyphs with red-fraction > thr):")
    fr = np.array([g['frac'] for g in glyphs])
    for thr in (0.15, 0.30, 0.50, 0.70, 0.90):
        print(f"  thr={thr:.2f}: {(fr > thr).sum()} red glyphs")

    # decoration test + per-page
    verdicts, pages = decoration_test(glyphs)
    print("\n" + "=" * 74)
    print("STEP 5  DECORATION-vs-DATA (per canon page)")
    print("=" * 74)
    kinds = {}
    for pg in sorted(v for v in verdicts if v is not None):
        kind, nred, ntot = verdicts[pg]
        kinds[kind] = kinds.get(kind, 0) + 1
        if nred:
            gs = sorted(pages[pg], key=lambda g: (g['gli'], g['gi']))
            redrunes = ''.join(g['rune'] for g in gs if g['red'])
            print(f"  canon page {pg:2d}: {kind:11s} red={nred:3d}/{ntot:3d}  "
                  f"{redrunes}  ({translit(r2i(redrunes))})")
    print(f"\n  kind tally: {kinds}")
    data_pages = {k: v for k, v in kinds.items() if k in ('scattered',)}
    dec_pages = {k: v for k, v in kinds.items() if k in ('prefix', 'contig-run', 'line-run')}
    print(f"  DECORATION-like (prefix/contig/line-run): {sum(dec_pages.values())}")
    print(f"  DATA-like (scattered/independent):        {sum(data_pages.values())}")

    # global red string, canon reading order
    order = sorted(glyphs, key=lambda g: (g['gli'], g['gi']))
    global_red = [g['rune'] for g in order if g['red']]
    global_black = [g['rune'] for g in order if not g['red']]
    red_idx = r2i(global_red)
    black_idx = r2i(global_black)

    print("\n" + "=" * 74)
    print("STEP 4  GLOBAL RED-RUNE STRING (canon reading order)")
    print("=" * 74)
    print(f"  n red runes: {len(red_idx)}   n black runes: {len(black_idx)}")
    print(f"  runes: {''.join(global_red)}")
    print(f"  Latin: {translit(red_idx)}")

    print("\n" + "=" * 74)
    print("STEP 6  CRYPTANALYSIS")
    print("=" * 74)
    print(f"  calibration: english ~ -4.0, floor ~ -7.49, THRESHOLD {THRESHOLD}")
    direct, keyres = keytest(red_idx, black_idx)
    if direct:
        print("\n  (a) direct / atbash / best-shift of RED:")
        for name, sc, s in direct:
            flag = "  <-- ABOVE THRESHOLD" if sc > THRESHOLD else ""
            print(f"    {sc:7.3f}  {name:14s}  {s}{flag}")
    if keyres:
        print("\n  (b) RED as KEY over BLACK runes (top 12):")
        for sc, mode, s in keyres[:12]:
            flag = "  <-- ABOVE THRESHOLD" if sc > THRESHOLD else ""
            print(f"    {sc:7.3f}  {mode:28s}  {s}{flag}")

    best_direct = max((sc for _, sc, _ in direct), default=None)
    best_key = keyres[0][0] if keyres else None
    n_above = sum(1 for _, sc, _ in direct if sc > THRESHOLD) + \
              sum(1 for sc, _, _ in keyres if sc > THRESHOLD)
    print(f"\n  best_direct={best_direct}  best_key={best_key}")
    print(f"  configs above THRESHOLD({THRESHOLD}): {n_above}")

    result = {
        'aligned_glyphs': len(glyphs), 'canon_valued': n_matched,
        'red_threshold': RED_THR,
        'n_red': len(red_idx), 'n_black': len(black_idx),
        'global_red_runes': ''.join(global_red),
        'global_red_translit': translit(red_idx),
        'decoration_kinds': kinds,
        'best_direct': best_direct, 'best_key': best_key,
        'above_threshold': n_above, 'threshold': THRESHOLD,
        'per_page': {str(pg): {'kind': verdicts[pg][0], 'n_red': verdicts[pg][1],
                               'n_total': verdicts[pg][2],
                               'red_runes': ''.join(g['rune'] for g in
                                   sorted(pages[pg], key=lambda x: (x['gli'], x['gi'])) if g['red'])}
                     for pg in verdicts if pg is not None},
    }
    with open(os.path.join(HERE, "result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  wrote {os.path.join(HERE, 'result.json')}")
    return result


if __name__ == "__main__":
    run()
