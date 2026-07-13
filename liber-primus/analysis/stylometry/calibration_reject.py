"""The ethical gate: can closed-set attribution be TRUSTED to name someone at
Cicada's text length? A matcher always returns a nearest author -- even when the
true author is absent, it fingers an innocent. To name responsibly you need a
Delta threshold that separates a REAL match from a FORCED FALSE one. This tests
whether such a threshold even exists at 359 words.

For held-out works (Carroll, Blake) chunked to L words:
  IN-SET   : true author present -> winning Delta of the CORRECT attribution.
  IMPOSTOR : true author removed  -> winning Delta of the forced WRONG attribution.
If these two Delta distributions overlap, no threshold can tell "found them" from
"wrongly accused someone" -> naming is indefensible at this length.
"""
import re, os, glob, json
import numpy as np
from collections import Counter

D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'keys', 'campaign13')
WORKS = {
    'Carroll':    ['englishcanon_alice_wonderland.txt', 'englishcanon_looking_glass.txt',
                   'englishcanon_hunting_snark.txt'],
    'Blake':      ['englishcanon_blake_thel.txt', 'englishcanon_book_urizen.txt',
                   'englishcanon_songs_innocence_experience.txt'],
    'Milton':     ['englishcanon_paradise_lost.txt'],
    'Shakespeare':['englishcanon_shakespeare_sonnets.txt'],
    'Coleridge':  ['englishcanon_coleridge_poems.txt'],
    'May':        ['cypherpunk_may_crypto_anarchist.txt'],
    'Hughes':     ['cypherpunk_hughes_manifesto.txt'],
    'Stallman':   ['cypherpunk_gnu_manifesto.txt'],
    'Mentor':     ['cypherpunk_mentor_conscience.txt'],
}
FUNC = ("the of and to a in that it is was for on are as with his they at be this have from or "
        "had by but not what all were we when there can an your which their said if do will each "
        "about how up out them then she many some so these would other into has more her two like "
        "him no could than first been who its now my over such our down only may after little "
        "very just where most know while should through both those before shall").split()

def words_of(fn):
    return re.findall(r"[a-z']+", open(os.path.join(D, fn), encoding='utf-8', errors='ignore').read().lower())
def fvec(w):
    n = max(1, len(w)); c = Counter(w)
    return np.array([c[t]/n for t in FUNC])

wv = {}
for a, fns in WORKS.items():
    for i, fn in enumerate(fns):
        w = words_of(fn)
        if len(w) >= 100:
            wv[(a, i)] = (fvec(w), w)
allv = np.array([v for v, _ in wv.values()])
mu, sd = allv.mean(0), allv.std(0) + 1e-9

def profile(a, drop=None):
    vs = [v for (aa, i), (v, _) in wv.items() if aa == a and (aa, i) != drop]
    return None if not vs else (np.mean(vs, 0) - mu) / sd

def rank(sample, pool_authors, drop=None):
    sv = (fvec(sample) - mu) / sd
    ds = []
    for a in pool_authors:
        p = profile(a, drop)
        if p is not None:
            ds.append((np.abs(sv - p).sum(), a))
    ds.sort()
    return ds  # [(delta, author), ...] nearest first

L = 359
targets = ['Carroll', 'Blake']
allA = list(WORKS)
inset, impostor = [], []
for a in targets:
    for i in range(len(WORKS[a])):
        if (a, i) not in wv:
            continue
        _, words = wv[(a, i)]
        for s in range(0, max(1, len(words) - L), L):
            chunk = words[s:s+L]
            if len(chunk) < 200:
                continue
            r_in = rank(chunk, allA, drop=(a, i))          # true author present
            if r_in[0][1] == a:
                inset.append(r_in[0][0])
            r_out = rank(chunk, [x for x in allA if x != a], drop=(a, i))  # author removed
            impostor.append(r_out[0][0])                    # forced-wrong winner's Delta

inset, impostor = np.array(inset), np.array(impostor)
print(f'sample length = {L} words, pool = {len(allA)} authors\n')
print(f'IN-SET correct-match Delta   : median {np.median(inset):.2f}  '
      f'[{np.percentile(inset,10):.2f}-{np.percentile(inset,90):.2f}]  n={len(inset)}')
print(f'IMPOSTOR forced-wrong Delta  : median {np.median(impostor):.2f}  '
      f'[{np.percentile(impostor,10):.2f}-{np.percentile(impostor,90):.2f}]  n={len(impostor)}')
# overlap: at the threshold that accepts 80% of true matches, what % of impostors sneak through?
thr = np.percentile(inset, 80)
fpr = float((impostor <= thr).mean())
print(f'\nThreshold accepting 80% of TRUE matches (Delta<= {thr:.2f}) also ACCEPTS '
      f'{100*fpr:.0f}% of IMPOSTORS')
print('=> A confident-looking match is a WRONG name that often.' if fpr > 0.2 else
      '=> Impostors are separable; naming could be defensible here.')
json.dump({'L': L, 'inset_median': float(np.median(inset)),
           'impostor_median': float(np.median(impostor)),
           'impostor_acceptance_at_80pct_recall': fpr},
          open(os.path.join(os.path.dirname(__file__), 'rejection.json'), 'w'), indent=2)
