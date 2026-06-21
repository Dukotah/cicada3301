import sys, json
sys.path.insert(0, "src")
from lp import gematria as gp, score as _score
SC = _score.default()

N = gp.N

def load_pages():
    raw = open("data/krisyotam_runes.txt", encoding="utf-8").read()
    pages = []
    for blk in raw.split("%"):
        idxs = gp.runes_to_indices(blk) if hasattr(gp, "runes_to_indices") else None
        if idxs is None:
            idxs = []
            for ch in blk:
                for (i, r, t, p) in gp.GEMATRIA:
                    if ch == r:
                        idxs.append(i); break
        if idxs:
            pages.append(idxs)
    return pages

# Magic square numbers from the KNOW THIS page
sq = [434,1311,312,278,966,204,812,934,280,1071,626,620,809,620,626,1071,280,934,812,204,966,278,312,1311,434]
# also the WELCOME page magic square (Lo Shu derived numbers) - the 272/110... border
# and the digit stream of all squares concatenated
digitstream = [int(d) for n in sq for d in str(n)]

candidates = {
    "sq_mod29": [n % N for n in sq],
    "sq_digits_mod29": [d % N for d in digitstream],
    "sq_repeat": [n % N for n in sq],  # cyclic over page
}

pages = load_pages()
best_overall = (-99, None)
for name, base in candidates.items():
    for pi, idxs in enumerate(pages):
        L = len(idxs)
        stream = [base[j % len(base)] for j in range(L)]
        for sign in (-1, 1):
            for atb in (False, True):
                p = [(((N-1-c) if atb else c) + sign*stream[j]) % N for j,c in enumerate(idxs)]
                s = SC.score_norm(gp.indices_to_translit(p))
                if s > best_overall[0]:
                    best_overall = (s, (name, pi, sign, atb, gp.indices_to_translit(p)[:80]))

print("BEST:", round(best_overall[0],3))
print(best_overall[1])
