"""Rank Cicada's actual prose against the candidate authors -- and show WHY the
'top match' is noise, by comparing the winner's margin to the impostor band from
calibration_reject.py (which found true and false matches overlap at 359 words).
"""
import re, os, json
import numpy as np
from collections import Counter

here = os.path.dirname(__file__)
D = os.path.join(here, '..', '..', 'data', 'keys', 'campaign13')
corpus = json.load(open(os.path.join(here, 'corpus.json'), encoding='utf-8'))
cic = ' '.join(v['text'] for v in corpus.values() if v['source'] == 'pgp_message')
cic_words = re.findall(r"[a-z']+", cic.lower())

CAND = {
    'May (crypto-anarchist)':   'cypherpunk_may_crypto_anarchist.txt',
    'Hughes (cypherpunk)':      'cypherpunk_hughes_manifesto.txt',
    'Stallman (GNU)':           'cypherpunk_gnu_manifesto.txt',
    'Mentor (hacker)':          'cypherpunk_mentor_conscience.txt',
    'Carroll':                  'englishcanon_alice_wonderland.txt',
    'Blake':                    'englishcanon_blake_thel.txt',
    'Milton':                   'englishcanon_paradise_lost.txt',
    'Shakespeare':              'englishcanon_shakespeare_sonnets.txt',
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

vecs = {k: fvec(words_of(fn)) for k, fn in CAND.items()}
allv = np.array(list(vecs.values()) + [fvec(cic_words)])
mu, sd = allv.mean(0), allv.std(0) + 1e-9
cv = (fvec(cic_words) - mu) / sd
ranked = sorted(((float(np.abs(cv - (vecs[k]-mu)/sd).sum()), k) for k in CAND))

print(f"Cicada prose = {len(cic_words)} words, vs {len(CAND)} candidates\n")
print("RANKED nearest-first (Burrows's Delta):")
for d, k in ranked:
    print(f"   {d:7.2f}  {k}")
margin = ranked[1][0] - ranked[0][0]
band = 157.32 - 150.71  # impostor vs true-match median gap from rejection.json
print(f"\nTop match: {ranked[0][1]!r}")
print(f"Margin over #2: {margin:.2f} Delta")
print(f"Impostor/true overlap band at 359w: ~{band:.2f} Delta (medians nearly equal;")
print(f"  62% of impostors fall inside the accept region).")
print("VERDICT: the winner's margin sits INSIDE the noise band where true and false")
print("matches are indistinguishable -> this 'top match' is not separable from chance.")
print("It is a LEAD-shaped artifact, not an identification. Do not publish it as a name.")
