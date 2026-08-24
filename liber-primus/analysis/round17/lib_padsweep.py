"""Round 16 - the PUBLIC-PAD instrument.

Why this file exists
--------------------
Every external-pad sweep in this repo (A1's CicadaOS binaries, the keytext lanes) walked a
*coarse offset ladder* - A1 used eight offsets per keystream variant. For a blob of B bytes
the honest offset coverage of that design is 8/B. On the 118 MB `560.13` pad that is 7e-8 of
the offset space. The published verdict is still correct as a verdict on *those eight
offsets*; it is not a bound on the pad.

This instrument replaces the ladder with a **dense offset scan**: score EVERY offset with a
cheap vectorised rune-index trigram model over a short head window, then beam-decode only the
survivors. That is the difference between "we tried 8 places in the pad" and "we tried all of
them".

Why a short head window is legitimate under the anti-repeat filter: the filter makes the key
pointer drift, but the expected number of skips in the first L runes is L * (1/29) * supp,
so for L = 24 it is ~0.7 - a meaningful fraction of true offsets survive a rigid read of the
head, and the beam then repairs the rest. `control()` MEASURES that survival rate instead of
assuming it.

API
---
    ks   = build_keystreams(blob)               # {variant_name: np.int16 array}
    hits = dense_scan(K, C_head, sign=-1)       # [(trigram_score, offset)] best-first
    res  = escalate(hits, K, C_head, sign=-1)   # beam scores on the survivors
    bar  = hit_bar(null_max)                    # the pre-registered HIT threshold

Beam settings, score scale and null are A1's, unchanged, so results are directly comparable
to `analysis/round12/A1/results_560_13.json`.
"""
import os, sys, json, random, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))          # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))

from lp import gematria as gp            # noqa: E402
import lib_numchannel as nc              # noqa: E402
import skipdecode as sk                  # noqa: E402

N = gp.N
BEAM_W, MAX_SKIP, HEAD = 120, 3, 400     # A1's settings, unchanged, for comparability
PREFILTER_LEN = 24                       # head window for the dense scan
DATA = os.path.join(ROOT, "data")


# --------------------------------------------------------------- keystream builders
def _u8(b):
    return np.frombuffer(b, dtype=np.uint8)


def ks_mod29(b):
    return (_u8(b).astype(np.int16) % N)


def ks_hi_nibble(b):
    return ((_u8(b).astype(np.int16) >> 4) % N)


def ks_lo_nibble(b):
    return ((_u8(b).astype(np.int16) & 0xF) % N)


def ks_byte_scaled(b):
    return ((_u8(b).astype(np.int32) * N) // 256).astype(np.int16)


def ks_prime_to_idx(b):
    p2i = np.full(256, -1, dtype=np.int16)
    for i, p in enumerate(gp.PRIMES):
        if p < 256:
            p2i[p] = i
    a = _u8(b)
    out = p2i[a].astype(np.int16)
    return np.where(out < 0, a.astype(np.int16) % N, out)


def ks_hexchars(b):
    """The blob READ AS ITS HEX STRING, through eng_to_idx.

    A 2013 author copy-pasting a block hash or a beacon value off a web page is handling
    the hex text, not the bytes. Byte-level builders cannot see that keystream at all.

    **KNOWN LIMITATION, found by lane P1 (2026-08-19).** `eng_to_idx` drops any character
    that is not a mappable letter, so it silently DISCARDS the digits 0-9: on a 19.4M-char
    hex string it kept 5.7M chars. This builder is therefore the **A-F subsequence** of the
    hex reading, not the hex reading. It is kept as-is because published lane results were
    measured with it, and it is a legitimate (if odd) keystream in its own right. For the
    actual hex-text reading use `ks_nibbles`.
    """
    return np.array(sk.eng_to_idx(b.hex().upper()), dtype=np.int16)


def ks_nibbles(b):
    """The true hex-text reading: each hex character as its value 0-15, in order.

    Added by lane P1 after `ks_hexchars` was found to drop digits. Not in `BUILDERS` —
    opt in explicitly — so that lane results measured against the original builder set
    stay comparable.
    """
    a = _u8(b).astype(np.int16)
    out = np.empty(a.size * 2, dtype=np.int16)
    out[0::2] = a >> 4
    out[1::2] = a & 0xF
    return out


BUILDERS = {
    "mod29": ks_mod29,
    "hi_nibble": ks_hi_nibble,
    "lo_nibble": ks_lo_nibble,
    "byte_scaled": ks_byte_scaled,
    "prime_to_idx": ks_prime_to_idx,
    "hexchars": ks_hexchars,
}


def build_keystreams(blob, reverse=True, only=None):
    out = {}
    for name, fn in BUILDERS.items():
        if only and name not in only:
            continue
        out[name] = fn(blob)
        if reverse:
            out[name + "_rev"] = fn(blob[::-1])
    return out


# --------------------------------------------------------------- index-space trigram model
_TRI = None


def trigram_model():
    """log10 P(c | a, b) over RUNE INDICES (not transliteration characters).

    Round 15's SCORER finding: the decoder emits runes, the quadgram scorer eats English
    characters, and 7 of 29 runes expand to two characters - training and scoring on
    different distributions costs power. This prefilter model is trained in the same space
    it scores. The final adjudication is still `score_norm`, unchanged, for comparability.
    """
    global _TRI
    if _TRI is not None:
        return _TRI
    cache = os.path.join(HERE, "trigram_idx.npy")
    if os.path.exists(cache):
        _TRI = np.load(cache)
        return _TRI
    counts = np.ones((N, N, N), dtype=np.float64)          # Laplace
    for fn in ("kjv.txt", "moby.txt", "pride.txt", "war.txt"):
        p = os.path.join(DATA, fn)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            idx = sk.eng_to_idx(f.read())
        a = np.array(idx, dtype=np.int64)
        np.add.at(counts, (a[:-2], a[1:-1], a[2:]), 1.0)
    _TRI = np.log10(counts / counts.sum(axis=2, keepdims=True)).astype(np.float32)
    np.save(cache, _TRI)
    return _TRI


# --------------------------------------------------------------- dense offset scan
def dense_scan(K, C, sign=-1, plen=PREFILTER_LEN, keep=400, chunk=1 << 21):
    """Score EVERY key offset by rigid-reading `plen` runes under the trigram model.

    Returns [(score_per_symbol, offset)] best-first, at most `keep` rows.
    Vectorised; peak memory bounded by `chunk` offsets at a time.
    """
    T = trigram_model()
    K = np.ascontiguousarray(np.asarray(K, dtype=np.int16))
    C = np.asarray(C[:plen], dtype=np.int16)
    n_off = len(K) - plen
    if n_off <= 0:
        return []
    best_s = np.full(0, -np.inf, dtype=np.float32)
    best_o = np.zeros(0, dtype=np.int64)
    for start in range(0, n_off, chunk):
        stop = min(start + chunk, n_off)
        m = stop - start
        Kw = np.lib.stride_tricks.sliding_window_view(K[start:stop + plen], plen)[:m]
        P = (C[None, :] + sign * Kw) % N
        sc = np.zeros(m, dtype=np.float32)
        for j in range(2, plen):
            sc += T[P[:, j - 2], P[:, j - 1], P[:, j]]
        sc /= (plen - 2)
        offs = np.arange(start, stop, dtype=np.int64)
        cat_s = np.concatenate([best_s, sc])
        cat_o = np.concatenate([best_o, offs])
        k = min(keep, len(cat_s))
        top = np.argpartition(-cat_s, k - 1)[:k]
        order = top[np.argsort(-cat_s[top])]
        best_s, best_o = cat_s[order], cat_o[order]
    return list(zip(best_s.tolist(), best_o.tolist()))


def escalate(hits, K, C, sign=-1, head=HEAD, top=40):
    """Beam-decode the dense scan's survivors on the real head window."""
    Kl = [int(x) for x in K]
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (MAX_SKIP + 1) + 8 >= len(Kl):
            continue
        bd = sk.beam_decode([int(x) for x in C[:head]], Kl, sign=sign, o=o,
                            beam_w=BEAM_W, max_skip=MAX_SKIP)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": bd["score"], "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


# --------------------------------------------------------------- null + bar
def null_ceiling(K, seq_len=HEAD, n=200, seed0=3301):
    """A1's null verbatim: beam-decode a SHUFFLED ciphertext under a real keystream."""
    Kl = [int(x) for x in K]
    base = nc.unsolved()[:seq_len]
    span = max(1, len(Kl) - seq_len * (MAX_SKIP + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, Kl, sign=-1, o=(k * 37) % span,
                                   beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    return float(np.mean(vals)), float(np.max(vals))


def hit_bar(null_max):
    """Pre-registered, A1's bar unchanged: score >= -5.5 AND >= null_max + 0.5."""
    return max(-5.5, null_max + 0.5)


# --------------------------------------------------------------- the gate
def control(blob=None, n_trials=8, seed=3301, verbose=True):
    """Plant an external-pad keystream at a RANDOM DEEP OFFSET in a real blob, encipher
    Cicada-register English under the anti-repeat filter, and require that

      (a) the dense scan ranks the true offset inside its `keep` window,
      (b) the beam recovers the plaintext there at >= 95% of runes.

    `survival_rate` is measured, not assumed: it is the fraction of planted offsets the
    dense prefilter retains, and it is the honest discount on this lane's coverage claim.
    A lane whose control fails reports INCONCLUSIVE, never NEGATIVE.
    """
    rng = random.Random(seed)
    if blob is None:                                    # deterministic stand-in pad
        blob = hashlib.sha512(b"ROUND16-CONTROL-PAD").digest()
        while len(blob) < (1 << 20):
            blob += hashlib.sha512(blob[-64:]).digest()
    plain_en = ("THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
                "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
                "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
                "SACRED GEOMETRY OF THE CIRCUMFERENCE")
    P = sk.eng_to_idx(plain_en)
    K = ks_mod29(blob)
    Kl = [int(x) for x in K]
    found = recovered = 0
    rows = []
    for t in range(n_trials):
        o_true = rng.randrange(1000, len(Kl) - len(P) * (MAX_SKIP + 2))
        C, skips, used = sk.encipher_keyskip(P, Kl[o_true:], sign=-1, supp=0.83)
        hits = dense_scan(K, C, sign=-1)
        rank = next((i for i, (s, o) in enumerate(hits) if int(o) == o_true), None)
        bd = sk.beam_decode(C, Kl, sign=-1, o=o_true, beam_w=500, max_skip=MAX_SKIP)
        match = sum(a == b for a, b in zip(bd["plain_idx"], P)) / len(P)
        found += (rank is not None)
        recovered += (match > 0.95)
        rows.append({"trial": t, "o_true": o_true, "rank": rank,
                     "beam_score": bd["score"], "match": match,
                     "skips": int(sum(skips))})
        if verbose:
            print(f"  trial {t}: o={o_true:>9d} dense-rank={rank} "
                  f"beam={bd['score']:.3f} match={match:.3f}", flush=True)
    res = {"n_trials": n_trials, "dense_found": found, "beam_recovered": recovered,
           "survival_rate": found / n_trials, "rows": rows}
    res["PASS"] = (found >= 1 and recovered == n_trials)
    return res


if __name__ == "__main__":
    r = control()
    print(json.dumps({k: v for k, v in r.items() if k != "rows"}, indent=2))
    print("CONTROL:", "PASS" if r["PASS"] else "FAIL")
