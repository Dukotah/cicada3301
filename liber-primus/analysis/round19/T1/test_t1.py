"""Tests for the T1 per-rune reader.  Run:
    cd liber-primus/analysis/round19/T1 && PYTHONUTF8=1 python3 test_t1.py

These are the assertions that make the lane's numbers checkable rather than asserted.
They read the committed out_*.json / adjudication.json plus the rebuildable work/ cache.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T

HERE = T.HERE
ok = fail = 0


def check(name, cond, detail=''):
    global ok, fail
    if cond:
        ok += 1; print('  PASS  %s %s' % (name, detail))
    else:
        fail += 1; print('  FAIL  %s %s' % (name, detail))


# ---- 1. the speed refactor is exact: Matcher == t1_bank.pairwise_cross
def t_matcher():
    import t1_bank as B
    from t1_match import Matcher
    rng = np.random.default_rng(3301)
    X = (rng.random((7, 144, 100)) > 0.85).astype(np.float32)
    Y = (rng.random((11, 144, 100)) > 0.85).astype(np.float32)
    D1 = B.pairwise_cross(X, Y)
    D2 = Matcher(Y, np.arange(11)).distances(X)
    check('Matcher == pairwise_cross', np.allclose(D1, D2),
          '(max abs diff %.3g)' % np.abs(D1 - D2).max())


# ---- 2. the Y finding: exactly one rune is drawn as two components
def t_yglyph():
    path = T.relikd_path(0)
    ink = T.page_ink(path)
    comps = T.components(ink)
    cands = [dict(c) for c in comps if T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1]]
    others = [c for c in comps if not (T.RUNE_H[0] <= c['h'] <= T.RUNE_H[1])]
    for g in cands:
        g.setdefault('n_inner', 0)
    n = T.attach_inner(cands, others)
    canon = T.canon_pages()[0]
    from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS
    nY = sum(1 for c in canon if IDX_TO_TRANS[RUNE_TO_IDX[c]] == 'Y')
    check('p0: inner-stroke attachments == canon Y count', abs(n - nY) <= 1,
          '(attached %d, canon Y %d)' % (n, nY))


# ---- 3. G-READ on the solved LP2 control pages
def t_gread():
    d = json.load(open(os.path.join(HERE, 'out_gread_lp2.json')))
    r = {x['image']: x for x in d['lp2']['rows']}
    check('73.jpg read 85/85', r['73.jpg']['correct'] == 85 and r['73.jpg']['canon'] == 85,
          '(%d/%d)' % (r['73.jpg']['correct'], r['73.jpg']['canon']))
    check('74.jpg read 95/95', r['74.jpg']['correct'] == 95 and r['74.jpg']['canon'] == 95,
          '(%d/%d)' % (r['74.jpg']['correct'], r['74.jpg']['canon']))
    check('no spurious or missing glyphs on the control pages',
          d['lp2']['missing'] == 0 and d['lp2']['spurious'] == 0)
    check('G-READ-LP2 >= 99%%', d['lp2']['accuracy'] >= 99.0,
          '(%.4f%%)' % d['lp2']['accuracy'])


# ---- 4. G-OAE: no O/A/AE confusion under leave-one-bitmap-out
def t_oae():
    d = json.load(open(os.path.join(HERE, 'out_loo.json')))
    worst = max(v['rate'] for k, v in d['oae'].items() if '->' in k)
    check('G-OAE: every ordered O/A/AE confusion rate == 0', worst == 0.0,
          '(worst %.6f)' % worst)
    for a in ('O', 'A', 'AE'):
        v = d['oae']['recall_' + a]
        check('G-OAE recall %s == 100%%' % a, v['rate'] == 1.0,
              '(%d/%d)' % (v['n'], v['of']))


# ---- 5. the 450 locate, and the direction breakdown matches T3's independent map
def t_450():
    d = json.load(open(os.path.join(HERE, 'adjudication.json')))
    check('450 records present', d['n_records'] == 450, '(%d)' % d['n_records'])
    check('450/450 located', d['tally'].get('UNLOCATABLE', 0) == 0,
          '(%d unlocatable)' % d['tally'].get('UNLOCATABLE', 0))
    want = {'A->O': 306, 'O->A': 72, 'AE->A': 70, 'A->AE': 2}
    check('direction breakdown reproduces round19/T3 exactly', d['direction'] == want,
          '(%s)' % d['direction'])
    check('every located record adjudicated', sum(d['tally'].values()) == 450)
    check('canon call and T1 call agree at every AGREE row',
          all(r['t1_call'] == r['canon_call'] for r in d['rows']
              if r['verdict'] == 'AGREE'))


# ---- 6. plants: the reader is never blind to a substituted glyph
def t_plant():
    d = json.load(open(os.path.join(HERE, 'out_plant.json')))
    for k in ('P-1', 'P-2'):
        check('%s zero reader-blind misses' % k, d[k]['blind'] == 0,
              '(%d blind of %d planted)' % (d[k]['blind'], d[k]['k']))
        check('%s detection given alignment == 100%%' % k,
              d[k]['detection_given_aligned'] == 1.0,
              '(%.4f)' % d[k]['detection_given_aligned'])


# ---- 7. corpus agreement
def t_corpus():
    d = json.load(open(os.path.join(HERE, 'out_corpus_lp2.json')))
    check('LP2 corpus agreement >= 99%%', d['agreement'] >= 99.0,
          '(%d/%d = %.4f%%)' % (d['n_equal'], d['n_canon'], d['agreement']))


if __name__ == '__main__':
    for f in (t_matcher, t_yglyph, t_gread, t_oae, t_450, t_plant, t_corpus):
        print(f.__name__)
        f()
    print('\n%d passed, %d failed' % (ok, fail))
    sys.exit(1 if fail else 0)
