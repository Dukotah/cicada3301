"""Round 19 / I1 -- the encipherment constructions the decoder is measured against.

Every construction in round18/L7-redteam/b1_power_envelope.py is reproduced here VERBATIM
(same code, same seeds, same plaintext window selection, same key family) so that I1's
numbers are directly comparable to `round18/L7-redteam/out_b1.json` row for row.  Two are
added:

  coin_from_key   the suppression coin is itself drawn from the keystream, so a doublet
                  event burns an extra draw whether or not it is suppressed.  An independent
                  "two draws per rejection" variant, structurally different from skip_by_two
                  (its extra draw lands AFTER the accepted symbol, not before).
  keyskip         (baseline) imported from campaign18_skip.skipdecode, unchanged.

Nothing about the cipher is re-implemented; this module only composes validated pieces.
"""
import os
import sys
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for _p in ("src", "benchmark", "analysis",
           os.path.join("analysis", "campaign18_skip"),
           os.path.join("analysis", "round11")):
    _q = os.path.join(ROOT, _p)
    if _q not in sys.path:
        sys.path.insert(0, _q)

from lp import gematria as gp          # noqa: E402
import skipdecode as sk                # noqa: E402
import plant as PL                     # noqa: E402

N = gp.N
LP2_DOUBLET_PCT = 0.6638


# ------------------------------------------------------------------ plaintext
def _english_stream():
    p = os.path.join(ROOT, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        t = f.read()
    return sk.eng_to_idx(t)[5000:]


ENG = _english_stream()


def take_plain(L, seed):
    """Identical window selection to round18/L7-redteam/b1_power_envelope.take_plain."""
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - L - 1)
    return ENG[s:s + L]


def long_plain(L, seed=0):
    """A contiguous English plaintext of ANY length, tiling the corpus if needed
    (used for the L = 12,956 full-book control)."""
    if L + 1 < len(ENG):
        return take_plain(L, seed)
    reps = L // len(ENG) + 2
    big = ENG * reps
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG))
    return big[s:s + L]


# ---------------------------------------------------------------- key material
def key_sha(n, seed=b"CICADA3301"):
    return PL.make_key("sha256_ctr", length=n, seed=seed)


def key_runs(n, run, seed=b"CICADA3301"):
    """Low-entropy pad: constant runs of length `run` (round17/P1's regime)."""
    base = PL.make_key("sha256_ctr", length=n // max(1, run) + 8, seed=seed)
    out = []
    for v in base:
        out.extend([v] * run)
        if len(out) >= n:
            break
    return out[:n]


# ------------------------------------------------------------ encipher variants
def enc_keyskip(P, K, supp=0.83, seed=3301, **_):
    """BASELINE. The construction the repo decoder is exact for."""
    C, skips, _u = sk.encipher_keyskip(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_skips": int(sum(skips))}


def enc_keyskip_varying(P, K, mode="ramp", seed=3301, **_):
    rng = random.Random(seed)
    n = len(P)

    def supp_at(i):
        if mode == "ramp":
            return i / max(1, n - 1)
        if mode == "blocks":
            return 0.60 if (i // 60) % 2 == 0 else 0.98
        if mode == "burst":
            return 1.0 if n // 3 <= i < 2 * n // 3 else 0.30
        raise ValueError(mode)

    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        s = supp_at(i)
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < s:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk}


def enc_free_drift(P, K, supp=0.83, q=0.01, seed=3301, **_):
    """Pinned filter PLUS an extra key advance with probability q for an unrelated reason
    (interrupter, line break, discarded draw)."""
    rng = random.Random(seed)
    C, j, c_prev, nsk, ndrift = [], 0, None, 0, 0
    for p in P:
        if rng.random() < q:
            j += 1
            ndrift += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": ndrift}


def enc_drift_at(P, K, supp=0.83, ndrift=1, seed=3301, **_):
    """Pinned filter plus EXACTLY `ndrift` extra key advances at evenly spaced positions."""
    rng = random.Random(seed)
    n = len(P)
    pos = {int((i + 1) * n / (ndrift + 1)) for i in range(ndrift)} if ndrift else set()
    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        if i in pos:
            j += 1
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_drift": len(pos)}


def enc_jump_at(P, K, supp=0.83, jump=5, njump=1, seed=3301, **_):
    """The pinned filter plus `njump` key-pointer JUMPS of `jump` positions each, all at
    ONE rune (a page break, a reset, a block of discarded draws).  Distinguished from
    `drift_at`, where the same total number of extra advances is SPREAD one per rune:
    a permissive decoder with `max_free = f` covers a spread of f per rune and does NOT
    cover a single jump larger than f."""
    rng = random.Random(seed)
    n = len(P)
    pos = {int((i + 1) * n / (njump + 1)) for i in range(njump)} if njump else set()
    C, j, c_prev, nsk = [], 0, None, 0
    for i, p in enumerate(P):
        if i in pos:
            j += jump
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 1
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_jumps": len(pos), "jump": jump}


def enc_skip_by_two(P, K, supp=0.83, seed=3301, **_):
    """REJECTION CONSUMES TWO DRAWS (L7-B's sharp case, and the same object the campaign
    plan calls "two-draws-per-rejection"): the rejected symbol plus a fresh one."""
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk}


def enc_coin_from_key(P, K, supp=0.83, seed=3301, **_):
    """The suppression COIN is drawn from the keystream, not from a separate RNG.  Every
    doublet event therefore burns one extra draw whether or not it is suppressed, and the
    extra draw lands AFTER the symbol that was accepted.  A genuinely independent
    two-draws-per-rejection variant."""
    thresh = int(round(supp * N))
    C, j, c_prev, nsk, nacc = [], 0, None, 0, 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev:
                if K[j + 1] < thresh:
                    j += 2                      # burn rejected symbol + coin, retry
                    nsk += 1
                    continue
                j += 1                          # coin consumed, doublet accepted
                nacc += 1
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, {"n_skips": nsk, "n_accepted_doublets": nacc,
               "effective_supp": thresh / N}


def enc_rewrite(P, K, supp=0.83, seed=3301, **_):
    C, info = PL.encipher_rewrite(P, K, sign=-1, supp=supp, seed=seed)
    return C, {"n_rewrites": info["n_rewrites"]}


MECH = {
    "keyskip": enc_keyskip,
    "keyskip_varying": enc_keyskip_varying,
    "free_drift": enc_free_drift,
    "drift_at": enc_drift_at,
    "skip_by_two": enc_skip_by_two,
    "two_draws_per_rejection": enc_skip_by_two,     # explicit alias, same object
    "coin_from_key": enc_coin_from_key,
    "jump_at": enc_jump_at,
    "rewrite": enc_rewrite,
}


def doublet_pct(C):
    if len(C) < 2:
        return 0.0
    return 100.0 * sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)


def build(mech, L, seed, mkw=None, key="sha", key_kw=None, headroom=6):
    """Return (C, K, P_true, info). `headroom` = key symbols per rune to allocate."""
    mkw = dict(mkw or {})
    key_kw = dict(key_kw or {})
    P = long_plain(L, seed)
    need = L * headroom + 2048
    K = key_runs(need, **key_kw) if key == "runs" else key_sha(need)
    C, info = MECH[mech](P, K, seed=3301 + seed, **mkw)
    return C, K, P, info
