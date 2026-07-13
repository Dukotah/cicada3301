"""RED TEAM front #1: is the plaintext LATIN, not English?

Every prior attack scored with an English model, so a Latin plaintext under a
running key/autokey (which flattens IoC identically) would have been invisible.
Build a Latin quadgram model from Caesar + Newton's Principia and re-run the
strongest attack families Latin-scored:
  1. monoalphabetic + short-Vigenere (key len 1-3) brute, per page
  2. plaintext-feedback autokey over the prime/totient family
  3. crib-drag with LATIN openers (consistency-based; language-independent)

A Latin break scores near the Latin reference; noise sits far below.
Reproduce: PYTHONUTF8=1 python analysis/latin/latin_redteam.py
"""
import os, sys, re, math
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp

N = 29
P = gp.PRIMES
TOT = [p - 1 for p in P]

def norm(t):
    t = t.upper().replace("J", "I").replace("V", "U")
    return re.sub("[^A-Z]", "", t)

# ---- build Latin quadgram model ----
def strip_gutenberg(t):
    a = re.split(r"\*\*\* ?START.*?\*\*\*", t, flags=re.S)
    t = a[1] if len(a) > 1 else t
    t = re.split(r"\*\*\* ?END", t, flags=re.S)[0]
    return t

corpus = ""
for fn in os.listdir(HERE):
    if fn.startswith("latin_") and fn.endswith(".txt"):
        corpus += strip_gutenberg(open(os.path.join(HERE, fn), encoding="utf-8", errors="ignore").read())
C = norm(corpus)
QG = {}
for i in range(len(C) - 3):
    q = C[i:i+4]
    QG[q] = QG.get(q, 0) + 1
tot = sum(QG.values())
logtot = math.log10(tot)
for q in QG:
    QG[q] = math.log10(QG[q]) - logtot
FLOOR = math.log10(0.01) - logtot
print(f"Latin model: {len(C)} chars, {len(QG)} distinct quadgrams")

def lscore(text):
    t = norm(text)
    n = len(t) - 3
    if n <= 0:
        return -99.0
    return sum(QG.get(t[i:i+4], FLOOR) for i in range(n)) / n

LAT_REF = lscore("GALLIA EST OMNIS DIUISA IN PARTES TRES QUARUM UNAM INCOLUNT BELGAE")
print(f"Latin reference score = {lscore('GALLIAESTOMNISDIUISAINPARTESTRES'):.3f}  "
      f"(sentence {LAT_REF:.3f}); noise ~ -4.5\n")

def pages():
    segs = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read().split("%")
    out = [gp.runes_to_indices(s) for s in segs if gp.runes_to_indices(s)]
    return out[:-2]

def tr(ix):
    return gp.indices_to_translit(ix)

PG = pages()
best = (-99, None)

# 1. mono + short Vigenere (len 1..3)
print("1. mono + short-Vigenere (Latin-scored)...")
import itertools
for pi, pg in enumerate(PG):
    for atb in (False, True):
        cc = [(N-1-x) if atb else x for x in pg]
        for klen in (1, 2, 3):
            # greedy per-position best would overfit; do full brute only for 1-2, sampled for 3
            ranges = [range(N)] * klen
            it = itertools.product(*ranges) if klen <= 2 else (
                (a, b, c) for a in range(N) for b in range(0, N, 2) for c in range(0, N, 2))
            for key in it:
                pt = [(cc[i] - key[i % klen]) % N for i in range(len(cc))]
                s = lscore(tr(pt))
                if s > best[0]:
                    best = (s, dict(attack=f"vig{klen}", page=pi, atb=atb, key=key,
                                    head=tr(pt)[:60]))

# 2. autokey prime/totient family (Latin-scored)
print("2. plaintext-feedback autokey (Latin-scored)...")
FUNCS = {"ident": lambda j: j, "prime": lambda j: P[j] % N,
         "totient": lambda j: TOT[j] % N}
for pi, pg in enumerate(PG):
    for atb in (False, True):
        cc = [(N-1-x) if atb else x for x in pg]
        for fn, F in FUNCS.items():
            for sign in (-1, 1):
                for seed in range(N):
                    out, prev = [], seed
                    for c in cc:
                        p = (c - sign * F(prev)) % N
                        out.append(p); prev = p
                    s = lscore(tr(out))
                    if s > best[0]:
                        best = (s, dict(attack=f"autokey-{fn}", page=pi, atb=atb,
                                        sign=sign, seed=seed, head=tr(out)[:60]))

# 3. crib-drag with Latin openers
print("3. crib-drag with Latin cribs...")
LAT_CRIBS = ["LIBER", "PRIMUS", "PARABOLA", "UERITAS", "SACER", "DEUS", "MORS",
             "FINIS", "INITIUM", "SAPIENTIA", "LUX", "UNUS", "OMNIA", "MUNDUS",
             "CIRCULUS", "NUMERUS", "SANCTUS", "UIA", "AUDI", "CAUE"]
for pi, pg in enumerate(PG):
    for atb in (False, True):
        cc = [(N-1-x) if atb else x for x in pg]
        for w in LAT_CRIBS:
            crib = gp.keyword_to_indices(w)
            if len(crib) < 4 or len(crib) > len(cc):
                continue
            K, contra = {}, 0
            for i in range(1, len(crib)):
                prev = crib[i-1]; kv = (cc[i] - crib[i]) % N
                if prev in K and K[prev] != kv:
                    contra = 1; break
                K[prev] = kv
            if contra or len(K) < 4:
                continue
            pt = list(crib)
            for i in range(len(crib), len(cc)):
                if pt[i-1] not in K:
                    break
                pt.append((cc[i] - K[pt[i-1]]) % N)
            if len(pt) >= len(crib) + 6:
                s = lscore(tr(pt))
                if s > best[0]:
                    best = (s, dict(attack=f"crib-{w}", page=pi, atb=atb, head=tr(pt)[:60]))

print("\n" + "="*55)
print(f"BEST Latin-scored decode: {best[0]:.3f}  (Latin ref {LAT_REF:.2f}, noise ~ -4.5)")
print("  ", best[1])
if best[0] > -3.6:
    print("\n  *** ABOVE NOISE — LATIN LEAD, VERIFY ***")
else:
    print("\n  Null: no Latin plaintext under mono/Vigenere/autokey/crib. The")
    print("  English-scored nulls were not hiding a Latin break.")
