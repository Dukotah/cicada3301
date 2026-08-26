"""R1 red-team — INDEPENDENT instrument.

Written from primitives so that nothing in Round 19's I1/I2/I3 lanes is validated with its
own harness (doctrine R6 / this lane's PREREG §1.1).

What is re-implemented here, from scratch:
  * the quadgram log-prob table loader (reads data/english_quadgrams.txt directly)
  * a beam decoder with an EXPLICIT, PARAMETERISED transition relation
  * the three encipherment constructions (keyskip / skip_by_two / free drift)
  * rune-space n-gram language models for a register panel
  * a two-point Gumbel extrapolation from a measured null

What is borrowed (data, not instrument):
  * the Gematria table (29 runes -> transliteration)      src/lp/gematria.py
  * the pinned 12,956-rune unsolved stream                analysis/round11/lib_numchannel.py
  * corpus text files under data/ and analysis/
"""
import math
import os
import random
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))     # liber-primus/
for _p in (os.path.join(LP, "src"),
           os.path.join(LP, "analysis"),
           os.path.join(LP, "analysis", "round11")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lp import gematria as gp                                  # noqa: E402  (data table)

N = 29
IDX_TO_TRANS = [gp.IDX_TO_TRANS[i] for i in range(N)]
_TRANS_SORTED = gp._TRANS_SORTED
_ALIAS = {"V": 1, "K": 5, "Z": 15, "Q": 5}
EULER_GAMMA = 0.5772156649015329


# ----------------------------------------------------------------- quadgram (mine)
class QG:
    """Independent loader of the same count file. Log10 probs, floor for unseen."""

    def __init__(self, path=None):
        path = path or os.path.join(LP, "data", "english_quadgrams.txt")
        d = {}
        tot = 0
        with open(path, encoding="ascii") as f:
            for line in f:
                q, c = line.split()
                c = int(c)
                d[q] = c
                tot += c
        lt = math.log10(tot)
        self.d = {q: math.log10(c) - lt for q, c in d.items()}
        self.floor = math.log10(0.01) - lt
        self.total = tot

    def total_score(self, text):
        t = re.sub(r"[^A-Z]", "", text.upper())
        if len(t) < 4:
            return -999.0, 0
        g, s = self.d.get, 0.0
        fl = self.floor
        for i in range(len(t) - 3):
            s += g(t[i:i + 4], fl)
        return s, len(t) - 3

    def score_norm(self, text):
        s, n = self.total_score(text)
        return -999.0 if n <= 0 else s / n


_QG = None


def qg():
    global _QG
    if _QG is None:
        _QG = QG()
    return _QG


# ----------------------------------------------------------------- text <-> runes
def eng_to_idx(text):
    """Greedy longest-match transliteration -> rune indices. Independent re-write."""
    s = text.upper()
    out, i, n = [], 0, len(s)
    while i < n:
        for t, idx in _TRANS_SORTED:
            if s.startswith(t, i):
                out.append(idx)
                i += len(t)
                break
        else:
            a = _ALIAS.get(s[i])
            if a is not None:
                out.append(a)
            i += 1
    return out


def idx_to_trans(idxs):
    return "".join(IDX_TO_TRANS[i % N] for i in idxs)


def unsolved():
    """The pinned 12,956-rune LP2 stream (data, not instrument)."""
    import lib_numchannel as nc
    return nc.unsolved()


# ----------------------------------------------------------------- constructions
def encipher_keyskip(P, K, sign=-1, supp=0.83, seed=3301):
    """Baseline: on rejection the key advances by ONE. (Matches the repo's pinned model.)"""
    rng = random.Random(seed)
    C, used = [], []
    j, cp = 0, None
    for p in P:
        while True:
            c = (p - sign * K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 1
                continue
            break
        C.append(c)
        used.append(j)
        j += 1
        cp = c
    return C, used


def encipher_skip2(P, K, sign=-1, supp=0.83, seed=3301):
    """L7-B's hole: the rejection sampler burns TWO draws per rejection."""
    rng = random.Random(seed)
    C, used = [], []
    j, cp = 0, None
    for p in P:
        while True:
            c = (p - sign * K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 2
                continue
            break
        C.append(c)
        used.append(j)
        j += 1
        cp = c
    return C, used


def encipher_drift(P, K, sign=-1, supp=0.83, q=0.05, seed=3301):
    """Baseline keyskip PLUS an independent source of key drift at rate q per symbol."""
    rng = random.Random(seed)
    C, used = [], []
    j, cp = 0, None
    for p in P:
        while True:
            c = (p - sign * K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 1
                continue
            break
        C.append(c)
        used.append(j)
        j += 1
        if rng.random() < q:
            j += 1                      # unrepresentable advance
        cp = c
    return C, used


def doublet_rate(C):
    return sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)


# ----------------------------------------------------------------- transitions
def transition_deltas(model, max_skip):
    """Return [(d, constraint_kind)] for accepted key index pa+1+d.

    constraint_kind:
        'all'  every skipped position must have produced c_prev
        'alt'  positions at even offset from pa+1 must have produced c_prev; rest free
        'none' no constraint (pure drift tolerance)
    """
    if model == "exact":
        return [(d, "all") for d in range(0, max_skip + 1)]
    if model == "by2":
        return [(2 * m, "alt") for m in range(0, max_skip + 1)]
    if model == "union":
        seen, out = set(), []
        for d in range(0, max_skip + 1):
            out.append((d, "all"))
            seen.add(d)
        for m in range(1, max_skip + 1):
            d = 2 * m
            if d not in seen:
                out.append((d, "alt"))
        return out
    if model == "union2":
        # CORRECTED union: every even advance is admissible under EITHER constraint.
        out = [(d, "all") for d in range(0, max_skip + 1)]
        out += [(2 * m, "alt") for m in range(1, max_skip + 1)]
        return out
    if model in ("free", "freepen"):
        return [(d, "none") for d in range(0, max_skip + 1)]
    raise ValueError(model)


def mean_branching(model, max_skip):
    """Expected admissible transitions per position under a random key (permissiveness scalar).

    'all'  with k skipped positions: probability (1/29)^k that all reproduce c_prev.
    'alt'  with d=2m: m constrained positions -> (1/29)^m.
    'none': always admissible.
    """
    tot = 0.0
    for d, kind in transition_deltas(model, max_skip):
        if kind == "none":
            tot += 1.0
        elif kind == "all":
            tot += (1.0 / N) ** d
        else:                                     # alt, d = 2m
            tot += (1.0 / N) ** (d // 2)
    return tot


def branching_report(models=("exact", "by2", "union2", "free"), skips=(1, 2, 3, 4, 6, 8)):
    return {f"{m}/ms{s}": mean_branching(m, s) for m in models for s in skips}


# ----------------------------------------------------------------- the beam (mine)
def beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3, model="exact", lam=0.0):
    """Independent skip/drift-tolerant beam.

    States are kept in flat parallel arrays with backpointers (no string concatenation and no
    list copying), so the cost is O(L * beam_w * |transitions|).

    Returns dict(score=score_norm, plain_idx, n_drift, nchars).
    """
    d_tab, floor = qg().d, qg().floor
    L = len(C)
    need = o + L * (max_skip + 1) + 8
    if len(K) < need:
        K = list(K) + [0] * (need - len(K))
    deltas = transition_deltas(model, max_skip)

    # state arrays for the current step
    p0 = (C[0] + sign * K[o]) % N
    t0 = IDX_TO_TRANS[p0]
    cur_sc = [0.0]
    cur_pa = [o]
    cur_tail = [t0[-3:]]
    cur_nch = [len(t0)]
    cur_cp = [C[0]]
    cur_dr = [0]
    cur_par = [-1]
    cur_p = [p0]
    hist = [(cur_par, cur_p)]

    for i in range(1, L):
        ci = C[i]
        n_sc, n_pa, n_tail, n_nch, n_cp, n_dr, n_par, n_p = [], [], [], [], [], [], [], []
        for b in range(len(cur_sc)):
            sc = cur_sc[b]
            pa = cur_pa[b]
            tail = cur_tail[b]
            nch = cur_nch[b]
            cp = cur_cp[b]
            dr = cur_dr[b]
            for (dd, kind) in deltas:
                acc = pa + 1 + dd
                if acc >= len(K):
                    continue
                p = (ci + sign * K[acc]) % N
                if kind != "none" and dd:
                    ok = True
                    if kind == "all":
                        for m in range(pa + 1, acc):
                            if (p - sign * K[m]) % N != cp:
                                ok = False
                                break
                    else:                                  # 'alt'
                        for m in range(pa + 1, acc, 2):
                            if (p - sign * K[m]) % N != cp:
                                ok = False
                                break
                    if not ok:
                        continue
                add = IDX_TO_TRANS[p]
                s = tail + add
                delta = 0.0
                # quadgrams newly completed
                start = max(4, len(tail) + 1)
                for e in range(start, len(s) + 1):
                    delta += d_tab.get(s[e - 4:e], floor)
                pen = lam * dd if (model == "freepen") else 0.0
                n_sc.append(sc + delta - pen)
                n_pa.append(acc)
                n_tail.append(s[-3:])
                n_nch.append(nch + len(add))
                n_cp.append(ci)
                n_dr.append(dr + dd)
                n_par.append(b)
                n_p.append(p)
        if not n_sc:
            break
        if len(n_sc) > beam_w:
            order = sorted(range(len(n_sc)), key=lambda k: n_sc[k], reverse=True)[:beam_w]
            n_sc = [n_sc[k] for k in order]
            n_pa = [n_pa[k] for k in order]
            n_tail = [n_tail[k] for k in order]
            n_nch = [n_nch[k] for k in order]
            n_cp = [n_cp[k] for k in order]
            n_dr = [n_dr[k] for k in order]
            n_par = [n_par[k] for k in order]
            n_p = [n_p[k] for k in order]
        cur_sc, cur_pa, cur_tail, cur_nch, cur_cp, cur_dr = n_sc, n_pa, n_tail, n_nch, n_cp, n_dr
        cur_par, cur_p = n_par, n_p
        hist.append((cur_par, cur_p))

    best = max(range(len(cur_sc)), key=lambda k: cur_sc[k])
    # backtrace
    out = []
    b = best
    for step in range(len(hist) - 1, -1, -1):
        par, pp = hist[step]
        out.append(pp[b])
        b = par[b]
    out.reverse()
    nch = cur_nch[best]
    denom = nch - 3
    return {"score": (cur_sc[best] / denom) if denom > 0 else -999.0,
            "raw": cur_sc[best], "plain_idx": out, "n_drift": cur_dr[best], "nchars": nch}


def recovery(plain_idx, P):
    n = min(len(plain_idx), len(P))
    if n == 0:
        return 0.0
    return sum(1 for a, b in zip(plain_idx[:n], P[:n]) if a == b) / len(P)


# ----------------------------------------------------------------- keys / nulls
def sha_key(seed, length):
    import hashlib
    out, ctr = [], 0
    while len(out) < length:
        h = hashlib.sha256(seed + ctr.to_bytes(8, "big")).digest()
        for byte in h:
            if byte < 232:               # rejection-sample to mod 29 without bias
                out.append(byte % N)
        ctr += 1
    return out[:length]


def random_key(rng, length):
    return [rng.randrange(N) for _ in range(length)]


def gumbel_fit(values):
    """Tail-calibrated two-point Gumbel from order statistics of the sample.

    Uses the 1-of-n and (n/8)-of-n order statistics rather than the bulk sd, because the
    beam score distribution is left-skewed and its bulk spread mis-states the upper tail
    (the trap benchmark/null.py documents). Returns (mu, beta).
    """
    v = sorted(values)
    n = len(v)
    if n < 16:
        return None, None
    # expected reduced variate for the k-th largest of n:  -ln(-ln((n-k+0.5)/n))
    def red(k):
        return -math.log(-math.log((n - k + 0.5) / n))
    k1, k2 = 1, max(2, n // 8)
    y1, y2 = red(k1), red(k2)
    x1, x2 = v[n - k1], v[n - k2]
    beta = (x1 - x2) / (y1 - y2)
    mu = x1 - beta * y1
    return mu, beta


def bar_at(nt, mu, beta, alpha=0.01):
    if nt < 2:
        return mu
    return mu + beta * (math.log(nt) - math.log(-math.log(1 - alpha)))


def expected_max(nt, mu, beta):
    return mu + beta * (math.log(nt) + EULER_GAMMA)


# ----------------------------------------------------------------- register panel
def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def _mid(t):
    return t[len(t) // 8: -len(t) // 8] if len(t) > 40000 else t


def _drop_vowels(text, frac=1.0, seed=7):
    r = random.Random(seed)
    out = []
    for ch in text.upper():
        if ch in "AEIOUY" and (frac >= 1.0 or r.random() < frac):
            continue
        out.append(ch)
    return "".join(out)


_FOLD = {
    "EN": {}, "LA": {"J": "I", "K": "C", "W": "U", "Y": "I"},
    "OE": {"Þ": "TH", "Ð": "TH", "Æ": "AE", "þ": "TH", "ð": "TH", "æ": "AE"},
    "DE": {"Ä": "AE", "Ö": "OE", "Ü": "UE", "ß": "SS"},
    "CY": {"Ŵ": "W", "Ŷ": "Y", "Â": "A", "Ê": "E", "Î": "I", "Ô": "O", "Û": "U"},
}


def text_to_runes(text, lang="EN"):
    t = text.upper()
    for a, b in _FOLD.get(lang, {}).items():
        t = t.replace(a.upper(), b)
    t = re.sub(r"[^A-Z]", "", t)
    return eng_to_idx(t)


def build_registers():
    """Nine plaintext registers as rune-index streams. Built by me from repo corpora."""
    B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
    import json
    P = {}
    en_held = _mid(_read(os.path.join(LP, "data", "keys", "self_reliance.txt"))) + \
        _mid(_read(os.path.join(LP, "data", "keys", "king_in_yellow.txt")))
    P["EN"] = text_to_runes(en_held, "EN")
    P["EN_KJV"] = text_to_runes(_mid(_read(os.path.join(LP, "data", "kjv.txt")))[:600000], "EN")
    sp = json.load(open(os.path.join(LP, "SOLVED-PAGES.json"), encoding="utf-8"))
    P["LP1"] = eng_to_idx("".join(p["plaintext_transliteration"] for p in sp["pages"]))
    la = _mid(_read(os.path.join(LP, "analysis", "latin", "latin_218.txt"))) + \
        _mid(_read(os.path.join(LP, "analysis", "latin", "latin_28233.txt")))
    P["LA"] = text_to_runes(la, "LA")
    oe_raw = _read(os.path.join(B6, "corpora", "oe_beowulf.txt"))
    oe = "\n".join(l for l in oe_raw.split("\n") if re.search(r"[þðæÞÐÆ]", l))
    oe += _read(os.path.join(LP, "data", "keys", "runepoem_oe.txt"))
    P["OE"] = text_to_runes(oe, "OE")
    de = _mid(_read(os.path.join(B6, "corpora", "de_faust.txt"))) + \
        _mid(_read(os.path.join(B6, "corpora", "de_2.txt")))
    P["DE"] = text_to_runes(de, "DE")
    P["CY"] = text_to_runes(
        _mid(_read(os.path.join(LP, "data", "keys", "welsh", "welsh_mabinogion.txt"))), "CY")
    P["EN_HALF"] = text_to_runes(_drop_vowels(en_held, 0.5), "EN")
    P["EN_NOVOW"] = text_to_runes(_drop_vowels(en_held, 1.0), "EN")
    return P


class RuneLM:
    """Order-3 (trigram) rune-index LM with add-k smoothing, in nats per symbol."""

    def __init__(self, stream, k=0.5, order=3):
        self.order = order
        self.k = k
        ctx = {}
        for i in range(order, len(stream)):
            key = tuple(stream[i - order:i])
            row = ctx.get(key)
            if row is None:
                row = ctx[key] = [0] * N
            row[stream[i]] += 1
        self.ctx = {c: (r, sum(r)) for c, r in ctx.items()}
        # backoff: unigram
        uni = [0] * N
        for s in stream:
            uni[s] += 1
        tu = sum(uni)
        self.uni = [math.log((c + k) / (tu + k * N)) for c in uni]
        self.logN = math.log(1.0 / N)

    def score(self, stream):
        """Mean log-prob per symbol (nats)."""
        o, k = self.order, self.k
        tot, n = 0.0, 0
        for i in range(o, len(stream)):
            row = self.ctx.get(tuple(stream[i - o:i]))
            if row is None:
                tot += self.uni[stream[i]]
            else:
                r, s = row
                tot += math.log((r[stream[i]] + k) / (s + k * N))
            n += 1
        return tot / n if n else -99.0


# ------------------------------------------------------- language-agnostic stats (R3)
def ioc_times_n(stream):
    c = [0] * N
    for s in stream:
        c[s] += 1
    n = len(stream)
    if n < 2:
        return 0.0
    return N * sum(x * (x - 1) for x in c) / (n * (n - 1))


def min_distinct_32(stream):
    if len(stream) < 32:
        return len(set(stream))
    return min(len(set(stream[i:i + 32])) for i in range(len(stream) - 31))


def compressibility(stream):
    b = bytes(stream)
    return len(zlib.compress(b, 9)) / max(1, len(b))
