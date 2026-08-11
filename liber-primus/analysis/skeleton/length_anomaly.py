"""Direct attack on the LP2 word-length excess.

LP2 (unsolved, 55 pages) has mean rune-word length 4.425. English-in-futhorc is
4.10-4.15 and all 458 interrupters supply only +0.156 runes/word, leaving a ~+0.17
residue. Round 8 left this open. Here it is attacked directly.

Ground truth first: the solved LP2 page PARABLE is *unenciphered plaintext*, so it
pins the author's transliteration convention exactly. The greedy-multigraph encoder
used throughout this repo reproduces all 20 of its word lengths (THE=2 via the TH
rune, TUNNELING=7 via ING, CIRCUMFERENCES=14, DIVINITY=8 with U for V). So the
encoder is not the source of the excess.

Hypotheses tested here:
  H1 REGISTER  -- 4.425 is inside the natural spread of English *passages* of the
                  same size. The KS test compared LP2 to an aggregate corpus; a
                  single 2,928-word passage has its own sampling variance, and
                  formal/archaic registers run longer than novels. Tested by
                  sliding a 2,928-word window over every corpus text.
  H2 NULLS     -- more nulls than the 458 F runes. Reports how many inserted runes
                  would be needed, and what that implies.
  H3 CICADA    -- the author's own prose is simply long-worded. The two solved LP2
                  pages give 3.40 (AN END) and 4.75 (PARABLE) -- tiny samples, but
                  they bracket the observation.
"""
import os, sys, re, math, json, collections, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS

MULTI = ('ING', 'EA', 'IA', 'IO', 'AE', 'OE', 'NG', 'EO', 'TH')


def enc(w):
    w = w.upper(); i = n = 0
    while i < len(w):
        for m in MULTI:
            if w.startswith(m, i):
                i += len(m); n += 1
                break
        else:
            if 'A' <= w[i] <= 'Z':
                n += 1
            i += 1
    return n


def words_of(seg_indices):
    txt = open(os.path.join(ROOT, 'data', 'krisyotam_runes.txt'),
               encoding='utf-8').read()
    segs = txt.split('%')
    out, F = [], 0
    for i in seg_indices:
        cur, cf = 0, 0
        for ch in segs[i]:
            if ch in RUNE_TO_IDX:
                cur += 1
                if ch == 'ᚠ':
                    cf += 1
            elif ch in '-.':                 # '/' is a line wrap
                if cur:
                    out.append(cur); F += cf
                cur = cf = 0
        if cur:
            out.append(cur); F += cf
    return np.array(out), F


PARABLE_EN = ("PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR "
              "OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE").split()
PARABLE_RUNES = [7, 4, 2, 6, 7, 2, 2, 7, 2, 4, 4, 3, 3, 14, 4, 2, 8, 5, 3, 6]


def main():
    rep = {}

    # ---- 0. encoder ground truth against the unenciphered solved page
    pred = [enc(w) for w in PARABLE_EN]
    ok = sum(1 for a, b in zip(pred, PARABLE_RUNES) if a == b)
    print('encoder check vs PARABLE (unenciphered plaintext): %d/%d word lengths exact'
          % (ok, len(pred)))
    if ok != len(pred):
        for w, a, b in zip(PARABLE_EN, pred, PARABLE_RUNES):
            if a != b:
                print('   %-16s predicted %d actual %d' % (w, a, b))
    rep['encoder_exact'] = [ok, len(pred)]

    lp, F = words_of(range(55))
    n = len(lp)
    print('\nLP2 unsolved: %d words, mean %.4f, %d F runes (+%.3f runes/word if all null)'
          % (n, lp.mean(), F, F/n))
    rep['lp2'] = dict(n=int(n), mean=float(lp.mean()), F=int(F))

    an, _ = words_of([55])
    pa, _ = words_of([56])
    print('Cicada solved LP2 pages: AN END %.3f (n=%d), PARABLE %.3f (n=%d), pooled %.3f'
          % (an.mean(), len(an), pa.mean(), len(pa),
             np.concatenate([an, pa]).mean()))
    rep['cicada_solved'] = dict(anend=float(an.mean()), parable=float(pa.mean()),
                                pooled=float(np.concatenate([an, pa]).mean()))

    # ---- H1: is 4.425 inside the spread of English PASSAGES of the same size?
    texts = {}
    for p in glob.glob(os.path.join(HERE, 'corpus', '*.txt')):
        texts['g/' + os.path.basename(p)[:-4]] = p
    for f in ('moby.txt', 'pride.txt', 'kjv.txt', 'war.txt'):
        q = os.path.join(ROOT, 'data', f)
        if os.path.exists(q):
            texts[f[:-4]] = q
    for p in glob.glob(os.path.join(ROOT, 'data', 'keys', '*.txt')):
        texts['k/' + os.path.basename(p)[:-4]] = p

    rng = np.random.default_rng(3301)
    obs_mean = lp.mean()
    # subtract the interrupter contribution so we compare like with like: the
    # plaintext behind LP2 is at most obs_mean and at least obs_mean - F/n
    lo_mean = obs_mean - F/n
    print('\nLP2 plaintext mean word length lies in [%.4f, %.4f]' % (lo_mean, obs_mean))
    print('(upper = no F is a null, lower = all 458 F are nulls)\n')

    rows = []
    for name, path in sorted(texts.items()):
        t = open(path, encoding='utf-8', errors='ignore').read()
        v = np.array([x for x in (enc(w) for w in re.findall(r"[A-Za-z']+", t)) if x])
        if len(v) < n * 2:
            continue
        # sliding-window means of the same size as LP2
        cs = np.concatenate([[0], np.cumsum(v)])
        idx = np.arange(0, len(v) - n, max(1, (len(v)-n)//4000))
        wm = (cs[idx + n] - cs[idx]) / n
        pct_above = float((wm >= lo_mean).mean())
        rows.append((name, len(v), float(v.mean()), float(wm.min()), float(wm.max()),
                     pct_above))
    rows.sort(key=lambda r: -r[4])
    print('%-34s %8s %7s %16s %9s' %
          ('text', 'words', 'mean', 'passage-mean range', 'pct>=%.2f' % lo_mean))
    for r in rows[:18]:
        print('%-34s %8d %7.3f   %6.3f .. %-6.3f %8.1f%%'
              % (r[0], r[1], r[2], r[3], r[4], 100*r[5]))
    any_reach = [r for r in rows if r[4] >= lo_mean]
    print('\ntexts with ANY %d-word passage reaching the LP2 lower bound %.3f: %d / %d'
          % (n, lo_mean, len(any_reach), len(rows)))
    if any_reach:
        print('   e.g. ' + ', '.join('%s (max %.3f)' % (r[0], r[4])
                                     for r in any_reach[:6]))
    rep['h1'] = dict(lo=lo_mean, hi=float(obs_mean), n_texts=len(rows),
                     n_reaching=len(any_reach),
                     top=[dict(text=r[0], mean=r[2], max_passage=r[4]) for r in rows[:10]])

    # ---- H2: how many nulls would be needed to bring LP2 onto the English mean?
    eng_mean = np.mean([r[2] for r in rows])
    need = (obs_mean - eng_mean) * n
    print('\nH2: to land on the %.3f cross-corpus mean, LP2 would need %.0f inserted'
          ' runes; it has %d F runes (%.1fx).' % (eng_mean, need, F, need/F))
    rep['h2'] = dict(eng_mean=float(eng_mean), need=float(need), F=int(F),
                     ratio=float(need/F))

    json.dump(rep, open(os.path.join(HERE, 'length_anomaly.json'), 'w'), indent=1)
    print('\nwrote length_anomaly.json')


if __name__ == '__main__':
    main()
