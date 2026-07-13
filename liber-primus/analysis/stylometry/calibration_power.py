"""Does stylometry have ANY power at Cicada's text length?

Before trusting stylometry to name Cicada's author, prove the method can identify
KNOWN authors at ~360 words. Burrows's Delta, closed-set, leave-one-WORK-out
(train on an author's other works, attribute a held-out work -> tests STYLE not
topic). Sweep the test-sample length down through Cicada's size and watch
accuracy vs chance.

Candidate pool = every labeled author available locally (literary + cypherpunk).
Test targets = the two authors with >=2 distinct works (Carroll, Blake), so a
held-out work never shares a book with its training profile.
"""
import re, os, glob, json, statistics
import numpy as np

D = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'keys', 'campaign13')

# author -> list of work files (only authors we can build a topic-clean profile for)
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

def load_words(fn):
    t = open(os.path.join(D, fn), encoding='utf-8', errors='ignore').read().lower()
    return re.findall(r"[a-z']+", t)

def fvec(words):
    n = max(1, len(words))
    from collections import Counter
    c = Counter(words)
    return np.array([c[w] / n for w in FUNC])

# build per-work vectors
work_vecs = {}   # (author, idx) -> (vec, wordcount, words)
for a, fns in WORKS.items():
    for i, fn in enumerate(fns):
        w = load_words(fn)
        if len(w) >= 100:
            work_vecs[(a, i)] = (fvec(w), len(w), w)

# corpus-wide mean/std per function word for Delta z-scoring
allv = np.array([v for v, _, _ in work_vecs.values()])
mu, sd = allv.mean(0), allv.std(0) + 1e-9

def delta_profile(vecs):
    return ((np.mean(vecs, 0) - mu) / sd)

def attribute(sample_words, exclude_author):
    """Delta-nearest author, using profiles built from all works EXCEPT the held-out
    author's own held-out work (that author's OTHER works still allowed)."""
    sv = (fvec(sample_words) - mu) / sd
    best, bd = None, 1e9
    for a in WORKS:
        vs = [v for (aa, i), (v, _, _) in work_vecs.items() if aa == a]
        if not vs:
            continue
        d = np.abs(sv - delta_profile(vs)).sum()   # Burrows's Delta = mean |z| diff
        if d < bd:
            bd, best = d, a
    return best

LENGTHS = [4000, 2000, 1000, 500, 359, 200, 100]
targets = [a for a, fns in WORKS.items() if len([1 for i in range(len(fns))
           if (a, i) in work_vecs]) >= 2]
n_authors = len(WORKS)
print(f'candidate pool: {n_authors} authors  (chance = {100/n_authors:.0f}%)')
print(f'test targets (>=2 works): {targets}\n')
print(f'{"len":>6} | ' + ' '.join(f'{a:>8}' for a in targets) + '   overall')

results = {}
rng = np.random.RandomState(0)
for L in LENGTHS:
    per_author_acc = {}
    all_correct, all_total = 0, 0
    for a in targets:
        # hold out each of this author's works in turn; chunk it to length L
        correct = total = 0
        idxs = [i for i in range(len(WORKS[a])) if (a, i) in work_vecs]
        for held in idxs:
            _, wc, words = work_vecs[(a, held)]
            # temporarily drop the held-out work from that author's profile pool
            saved = work_vecs.pop((a, held))
            for start in range(0, max(1, len(words) - L), L):
                chunk = words[start:start + L]
                if len(chunk) < min(L, 80):
                    continue
                total += 1
                if attribute(chunk, a) == a:
                    correct += 1
            work_vecs[(a, held)] = saved
        per_author_acc[a] = correct / total if total else float('nan')
        all_correct += correct; all_total += total
    results[L] = {'overall': all_correct / all_total, 'per_author': per_author_acc}
    print(f'{L:>6} | ' + ' '.join(f'{per_author_acc[a]*100:7.0f}%' for a in targets) +
          f'   {100*all_correct/all_total:5.0f}%')

json.dump({'chance_pct': 100/n_authors, 'targets': targets,
           'accuracy_by_length': {str(L): results[L]['overall'] for L in LENGTHS}},
          open(os.path.join(os.path.dirname(__file__), 'calibration.json'), 'w'), indent=2)
print(f'\nCicada connected-prose total = 359 words (in ONE aggregate, not per doc).')
print('Read the 359 / 200 / 100 rows: that is the regime any Cicada attribution lives in.')
