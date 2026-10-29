"""Shared setup for R32-B2. Uses the ROUND32 I2 nine-register panel (models/panel.npz of I2-multiregister-readjudication)."""
import os, sys, json, random, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
I2DIR = os.path.join(LP, "analysis", "round32", "I2-multiregister-readjudication")
for p in ("analysis/round19/G1", "analysis/round19/I1", "analysis/round20/P3", "analysis/round20/HITFN",
          "analysis/round11", "analysis/campaign18_skip", "src"):
    q = os.path.join(LP, p)
    if q not in sys.path: sys.path.insert(0, q)
sys.path.insert(0, I2DIR)           # round32 I2 adjudicate (panel.npz + out_build.json) shadows round19/I2
import adjudicate as AD
assert os.path.dirname(os.path.abspath(AD.__file__)) == os.path.abspath(I2DIR), AD.__file__
import driftbeam as DB, hitfn20 as H, skipdecode as sk, lib_numchannel as nc
assert H.AD is AD
sys.path.insert(0, os.path.join(LP, "benchmark"))
U = list(nc.unsolved())
L_SCREEN, L_HIT = 120, 240
C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]
NEED = L_HIT * 4 + 64
sys.path.insert(0, HERE)
import php_mt as PM_
import hitfn20 as H
PMB = H.PM           # panelmax_bar provider
U = list(nc.unsolved())
L_SCREEN, L_HIT = 120, 240
C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]
NEED = L_HIT * 4 + 64
CELLS = [(tw, rd) for tw in ("mt", "php") for rd in ("scale", "mod")]
def cname(c): return "%s_%s" % c

def ks(seed, cell, n=NEED):
    return PM_.ks(int(seed), cell[0], cell[1], n)

def enc_pair(P, K, supp=0.83, seed=777):
    rng = random.Random(seed); C, j, cp = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % 29
            if cp is not None and c == cp and rng.random() < supp: j += 2; continue
            break
        C.append(c); j += 1; cp = c
    return C

def enc_exact(P, K, seed=777):
    return list(sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=seed)[0])

def enc_exact(P, K, seed=777):
    return list(sk.encipher_keyskip(P, K, sign=-1, supp=0.83, seed=seed)[0])

def corpora():
    r = lambda p: open(os.path.join(LP, p), encoding="utf-8", errors="ignore").read()
    en = sk.eng_to_idx(r("data/keys/self_reliance.txt"))
    la = sk.eng_to_idx(r("analysis/latin/latin_28233.txt"))
    de = sk.eng_to_idx(r("analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt"))
    nov = sk.eng_to_idx("".join(ch for ch in r("data/keys/self_reliance.txt") if ch.upper() not in "AEIOU"))
    return {"EN_MODERN": en, "LATIN": la, "DE": de, "EN_NOVOWEL": nov}
