"""M0 spot-checks: reproduce the ORIGINAL-SIDE statistics the imported FlareZ123 studies rest on,
from our own canonical stream (sha-pinned by fable52/load.py). Controls (their English donors) are
NOT re-run here; only the ciphertext-side numbers are checked.

Needs fable52/load.py + load2.py; load2 reads word/line structure from the external clone's
lp2-transcription.txt (rune-identical to our dataset, see fable52/OUTPUTS.txt reconcile).
Run: python -I verify_imports.py
"""
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'fable52'))
import load, load2

c = [x['v'] for x in load.stream()]; N = len(c)
print('canonical unsolved runes', N)

def M(q):  # same-phase equal pairs, book-global clock (allperiod-secret-phase gate)
    cnt = collections.Counter((i % q, v) for i, v in enumerate(c))
    return sum(n * (n - 1) // 2 for n in cnt.values())
print('M(840) =', M(840), '(FlareZ: 3277)   M(3301) =', M(3301), '(FlareZ: 634)')

out, _ = load2.stream(); S = out[:N]
words, cur = [], []
for x in S:
    sep = x['sep']
    for ch in '/\n% ':
        sep = sep.replace(ch, '')
    if sep and cur:
        words.append(cur); cur = []
    cur.append(x['v'])
words.append(cur)
print('printed words', len(words), '(FlareZ: 2896)')
w8 = collections.Counter(tuple(w[-4:]) for w in words if len(w) >= 8)
w7 = collections.Counter(tuple(w[-3:]) for w in words if len(w) >= 7)
print('words>=8 sharing last-4 ct runes: pairs =', sum(n*(n-1)//2 for n in w8.values()), '(FlareZ: 0)')
print('words>=7 sharing last-3 ct runes: pairs =', sum(n*(n-1)//2 for n in w7.values()), '(FlareZ: 4)')

pos = [i for i in range(1, N) if c[i] == c[i - 1]]
g = [b - a for a, b in zip(pos, pos[1:])]
print('doublets', len(pos), '; longest single gap', max(g))
i = max(range(len(g) - 2), key=lambda k: g[k] + g[k+1] + g[k+2])
print('largest 3-gap sum', g[i] + g[i+1] + g[i+2], '=', g[i:i+3], 'sites (first rune, 0-based)', [p - 1 for p in pos[i:i+4]])
