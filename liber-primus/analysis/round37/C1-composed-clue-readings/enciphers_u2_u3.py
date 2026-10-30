#!/usr/bin/env python3
"""Round 37 / C1: LP1 data (codebook, GP-sum sequences) and the INDEPENDENT encipherers for U2 and U3.

These work forward from plaintext words (their lengths = the cipher word lengths); the decoders in sweep.py work
from the ciphertext and are written separately (different code path), so a control that passes is a real
round-trip, not a shared function.   Writes nothing.
"""
import os, re, sys, json, random
sys.dont_write_bytecode = True
from c1lib import *            # noqa: F401,F403  (LP, AN, sk, C1, U ...)
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp

PRIMES = gp.PRIMES

# ------------------------------------------------------------------ LP1 data
CLUES = {c["id"]: c for c in json.load(open(AN("round36", "O4-clue-coverage", "clues.json"), encoding="utf-8"))}
LP1_IDS = sorted([k for k in CLUES if k.startswith("LP1-0.")], key=lambda s: [int(x) for x in s[4:].split(".")])
LINES_SRC = os.path.join(LP, "data", "keys", "armada18", "cicada_koans_and_lp_sections.txt")


def toks(text):
    return [w.replace("'", "") for w in re.findall(r"[A-Z']+", text.upper()) if w.replace("'", "")]


def runes(word):
    """word -> rune indices (K->C, V->U via eng_to_idx; ING -> NG so published line sums reproduce)."""
    return sk.eng_to_idx(word.upper().replace("ING", "NG"))


def vsum(rs, ch):
    return sum(PRIMES[i] for i in rs) if ch == "prime" else sum(rs)


SENTS = [toks(CLUES[i]["text"]) for i in LP1_IDS]
W = [w for s in SENTS for w in s]                                  # the codebook (document order)
WR = [runes(w) for w in W]
K0 = [r for rs in WR for r in rs]                                  # the map as a rune stream
LINES = [toks(l) for l in open(LINES_SRC, encoding="utf-8").read().split("\n") if toks(l)]


def sequences(ch):
    """{name: [ints]} for channel ch in {prime,index}."""
    word = [vsum(r, ch) for r in WR]
    sent = [sum(vsum(runes(w), ch) for w in s) for s in SENTS]
    line = [sum(vsum(runes(w), ch) for w in l) for l in LINES]
    cum, t = [], 0
    for v in word:
        t += v; cum.append(t)
    return {"word": word, "line": line, "sentence": sent, "cumul": cum}


SEQS = {ch: sequences(ch) for ch in ("prime", "index")}
VAL = {ch: [vsum(r, ch) for r in WR] for ch in ("prime", "index")}   # per codebook entry
VARIANTS = [(ch, nm, m) for ch in ("prime", "index") for nm in ("word", "line", "sentence", "cumul") for m in (29, 28)]


# ------------------------------------------------------------------ cipher-side word structure
def word_lens_from(page, nrunes=1100):
    """FULL ciphertext word lengths from the start of `page` (continuing through later pages) covering >= nrunes."""
    import mapcommon as M
    P = word_lens_from._P if hasattr(word_lens_from, "_P") else M.parse()
    word_lens_from._P = P
    first = P["w_page"].index(page)
    out, tot = [], 0
    for w in P["words"][first:]:
        out.append(len(w)); tot += len(w)
        if tot >= nrunes: break
    return out


# ------------------------------------------------------------------ U2 encipherers
def u2a_key(ch, nm, m, o, n):
    S = SEQS[ch][nm]
    return [S[(j + o) % len(S)] % m for j in range(n)]


def u2b_key(ch, nm, m, o, lens, n):
    """K'[i] = K0[(o + i + sum_{j<=k(i)} S[j] mod m) mod |K0|]  (jump applied at the START of word k, incl. k=0)."""
    S = SEQS[ch][nm]; out = []; J = 0; i = 0
    for k, l in enumerate(lens):
        J += S[k % len(S)] % m
        for t in range(l):
            out.append(K0[(o + i + J) % len(K0)]); i += 1
            if i >= n: return out
    return out


def encipher_with_key(P, K, rel, seed):
    enc = C1.enc_exact if rel == "keyskip1" else C1.enc_pair
    return enc(list(P), list(K), seed=seed)


def enc_u2a(P, ch, nm, m, o, rel, seed):
    K = u2a_key(ch, nm, m, o, 4 * len(P) + 64)
    return encipher_with_key(P, K, rel, seed)


def enc_u2b(P, ch, nm, m, o, lens, rel, seed):
    K = u2b_key(ch, nm, m, o, lens, 4 * len(P) + 64)
    return encipher_with_key(P, K, rel, seed)


# ------------------------------------------------------------------ U3 encipherer
def u3_d(lens, rho, M, s):
    """per-word number d_k = v(W[(s+p_k) mod n]) mod M, from the word-length structure (cipher-side observables only)."""
    n = len(W); out = []; r = 0
    for k, l in enumerate(lens):
        p = k if rho == 1 else (r if rho == 2 else l)
        out.append(VAL["prime"][(s + p) % n] % M); r += l
    return out


def enc_u3(P, lens, rho, M, s, sigma, mode, rel=None, seed=1):
    """P plaintext rune indices (len L); word k = next lens[k] runes. mode in A1 (shift), A2 (cumulative), A3 (key advance in K0)."""
    d = u3_d(lens, rho, M, s)
    if mode in ("A1", "A2"):
        C, i, D = [], 0, 0
        for k, l in enumerate(lens):
            D += d[k]
            sh = d[k] if mode == "A1" else D
            for t in range(l):
                if i >= len(P): return C
                C.append((P[i] + sigma * sh) % 29); i += 1
        return C
    # A3
    K = []; r = 0; J = 0
    for k, l in enumerate(lens):
        J += sigma * d[k]
        for t in range(l):
            K.append(K0[(r + J + t) % len(K0)])
        r += l
    return encipher_with_key(P, K, rel, seed)
