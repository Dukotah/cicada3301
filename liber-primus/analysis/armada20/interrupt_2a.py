import sys, re, json
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus')
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
import numpy as np
from src.lp import gematria as gp, score as _score, solve
import attack

N = gp.N
text = open('data/keys/runepoem_translit.txt', encoding='utf-8').read()
letters = re.sub(r'[^A-Za-z]', '', text)
key = np.array(gp.keyword_to_indices(letters))
scorer = _score.default()
pages = attack.unsolved_pages()

def idxs_to_runes(idxs):
    return ''.join(gp.IDX_TO_RUNE[i] for i in idxs)

results = []
for pi, idxs in enumerate(pages):
    c = np.array(idxs)
    L = len(c)
    best = (-99, None)
    for sign in (+1, -1):
        for atb in (False, True):
            cc = (N-1)-c if atb else c
            noff = len(key) - L
            for o in range(noff):
                p = (cc - sign*key[o:o+L]) % N
                s = scorer.score_norm(gp.indices_to_translit(p.tolist()))
                if s > best[0]:
                    best = (s, (sign, atb, o))
    results.append((pi, best[0], best[1], L))

results.sort(key=lambda r: -r[1])
print('TOP 10 plain (no interrupter) page configs:')
for pi, s, cfg, L in results[:10]:
    print(f'  p{pi} score={s:.3f} cfg={cfg} L={L}')

# interrupter beam on top 8 configs
print('\\nINTERRUPTER BEAM on top configs:')
best_overall = (-99, None)
for pi, s, cfg, L in results[:8]:
    sign, atb, o = cfg
    runes = idxs_to_runes(pages[pi])
    stream = key[o:o+L+200].tolist()  # extra room since interrupters skip
    sg = -1 if sign == -1 else 1
    r = solve.find_interrupters(runes, stream, sign=sg, atbash=atb,
                                beam_width=200, scorer=scorer)
    sc = scorer.score_norm(r['plaintext'])
    nint = r['n_interrupters']
    pt = r['plaintext'][:60]
    print('  p%d cfg=%s interrupt_score=%.3f n_int=%d pt=%s' % (pi, cfg, sc, nint, pt))
    if sc > best_overall[0]:
        best_overall = (sc, (pi, cfg, r['plaintext'][:80]))

print('\\nBEST OVERALL interrupter:', best_overall)
