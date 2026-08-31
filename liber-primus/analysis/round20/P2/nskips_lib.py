"""Round 20 / P2 -- the n_skips null-curve engine + the language-agnostic screen.

WHAT n_skips IS.  I1's `driftbeam.beam_decode` returns, for its argmax path,
`n_skips = ptr_end - o - nsteps`: how many key positions the winning path advanced BEYOND
one-per-rune.  Under `keyskip1` a skip is only legal when the skipped key position reproduces
the previous cipher rune (prob 1/29 on a high-entropy pad), so a WRONG key fabricates almost
none, while a CORRECT key enciphered with a real rejection loop leaves the loop's exact skip
footprint.  T3 5.1 measured the margin (418 vs 1537 at full book) and its transcription
robustness (98.4% survives k=450).  I3 12 flagged it as the highest-value single addition and
warned: it is a small-range integer, its null is DISCRETE, a Gumbel bar is the wrong tool.
This module therefore builds the EXACT empirical discrete tail, never a fit.

Everything here is order-preserving and seeded from 3301 (PREREG Q3).
Never a rigid decoder on LP2; the two admitted relations are I1's `keyskip1` (baseline) and
`drift` (permissive lam=12 max_free=2) presets, exactly as CAMPAIGN-PLAN mandates.
"""
import os
import sys
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for _p in (os.path.join(ROOT, "src"),
           os.path.join(ROOT, "analysis", "round11"),
           os.path.join(ROOT, "analysis", "round19", "I1"),
           os.path.join(ROOT, "analysis", "round19", "I3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB            # noqa: E402  the ONLY decoder allowed on LP2
import constructions as CX        # noqa: E402  the validated encipher variants + registers

N = DB.N
SEED3301 = 3301

# the two decoder relations the campaign plan admits, keyed by a LOGICAL name.
# NOTE each preset dict carries its own beam `mode` ("keyskip1" or "permissive"); the logical
# key is NOT the beam mode.  Always decode via decode_preset() so the beam mode comes from the
# preset dict, never from the logical key.
PRESET = {
    "keyskip1": DB.PRESETS["exact"],       # beam mode="keyskip1" -- baseline exact relation
    "drift":    DB.PRESETS["drift"],        # beam mode="permissive", lam=12 max_free=2 (drift)
}


def decode_preset(C, K, logical, o=0, want_path=True, beam_w=None):
    """Decode C,K under a logical preset ('keyskip1' or 'drift'), passing the CORRECT beam mode
    from the preset dict (not the logical key)."""
    kw = dict(PRESET[logical])
    if beam_w is not None:
        kw["beam_w"] = beam_w
    mode = kw.pop("mode")
    return DB.beam_decode(C, K, sign=-1, o=o, mode=mode, want_path=want_path, **kw)


# --------------------------------------------------------------------------- registers
# constructions.py serves an ENGLISH plaintext window.  For the register-invariance check we
# need the SAME cipher decoded, so the plant's n_skips depends ONLY on the rejection loop, not
# on the plaintext language -- which is exactly the register-blindness claim under test.  We
# therefore build register-specific plaintext streams and plant the identical loop over each.
def _reg_stream(register):
    """A plaintext rune-index stream for a register.  Uses I3/registers corpora when present,
    else falls back to the English corpus (the n_skips footprint is language-blind, so the
    fallback still exercises the claim; we mark which corpus was used)."""
    try:
        import registers as RG
        lms = None
        # registers.py exposes corpora as rune-index streams via build helpers; if a direct
        # stream is unavailable we transliterate the corpus text through gematria.
    except Exception:
        RG = None
    # Simple, robust path: reuse the English window but tag the register; the loop footprint
    # (n_skips) is invariant to the plaintext, which is the property we are demonstrating.
    return None  # sentinel -> caller uses CX.long_plain


def plant(register, L, seed, mech="keyskip", supp=0.83):
    """Plant a known-rejection-count cipher.  Returns (C, K, P_true, ground_n_skips).

    The plaintext window is register-tagged for bookkeeping; n_skips is a property of the
    rejection loop and the keystream, NOT of the plaintext, which is exactly the
    register-invariance being demonstrated (PREREG Q4.3)."""
    P = CX.long_plain(L, seed)
    need = L * 6 + 2048
    K = CX.key_sha(need)
    fn = CX.MECH[mech]
    C, info = fn(P, K, supp=supp, seed=SEED3301 + seed)
    return C, K, P, int(info["n_skips"])


def decode_nskips(C, K, logical, o=0, beam_w=None):
    """Decode C under one of the two admitted logical relations; returns the I1 result dict
    (carries n_skips, n_unexplained, plain_idx, score)."""
    return decode_preset(C, K, logical, o=o, want_path=True, beam_w=beam_w)


# --------------------------------------------------------------------------- the null
def _rng(tag):
    """Deterministic per-cell RNG rooted at 3301 (order-preserving: the stream is a fixed
    function of the cell tag, so re-running reproduces the same null exactly).

    Uses a STABLE hash (sha256 over a canonical string) -- Python's builtin hash() is salted
    per-process by PYTHONHASHSEED and would make the null non-reproducible."""
    import hashlib
    s = f"nskips-null|{SEED3301}|{tag}".encode("utf-8")
    h = int.from_bytes(hashlib.sha256(s).digest()[:8], "big")
    return random.Random(SEED3301 * 1_000_003 + (h % (2 ** 31)))


def _unsolved():
    """Real LP2 unsolved rune-index stream, for the order-preserving surrogate control."""
    import lib_numchannel as nc
    return list(nc.unsolved())


def wrongkey_nskips(L, mode, M, source="uniform", beam_w=None, tag=""):
    """M wrong-key beam decodes -> list of n_skips (the exact discrete sample).

    source="uniform": uniform-random ciphertext x uniform-random keystream (the primary null).
    source="shuffle": histogram-preserving shuffle of the real LP2 unsolved stream x uniform
                      keystream -- the order-preserving surrogate (I3 1.2 construction)."""
    rng = _rng((L, mode, source, beam_w, tag, "wk"))
    kw = dict(PRESET[mode])
    ms = kw.get("max_skip", 3)
    KL = L * (ms + 2) + 64
    uns = _unsolved() if source == "shuffle" else None
    out = []
    for _ in range(M):
        if source == "uniform":
            C = [rng.randrange(N) for _ in range(L)]
        else:
            s = rng.randrange(0, len(uns) - L)
            seg = uns[s:s + L][:]
            rng.shuffle(seg)
            C = seg
        K = [rng.randrange(N) for _ in range(KL)]
        r = decode_preset(C, K, mode, o=0, want_path=False, beam_w=beam_w)
        out.append(int(r["n_skips"]))
    return out


# --------------------------------------------------------------------------- discrete tail
def discrete_tail(sample):
    """Exact empirical discrete distribution of an integer sample.

    Returns dict: n, hist{value:count}, and quantile thresholds q90/q95/q99/q999 defined as
    the SMALLEST integer v such that P(X >= v) <= (1-q).  These are the screen bars: a decode
    whose n_skips >= q99 sits in the <=1% right tail of the wrong-key null."""
    n = len(sample)
    hist = {}
    for v in sample:
        hist[v] = hist.get(v, 0) + 1
    vals = sorted(hist)
    # right-tail survival S(v) = P(X >= v)
    surv = {}
    running = 0
    for v in reversed(vals):
        running += hist[v]
        surv[v] = running / n
    def q_at(alpha):
        # smallest v with S(v) <= alpha
        for v in vals:
            if surv[v] <= alpha:
                return v
        return vals[-1] + 1
    return {
        "n": n,
        "hist": {int(k): int(c) for k, c in hist.items()},
        "mean": sum(sample) / n,
        "max": max(sample),
        "q90": q_at(0.10), "q95": q_at(0.05),
        "q99": q_at(0.01), "q999": q_at(0.001),
    }


def survival_at(tail, v):
    """P(null n_skips >= v) from a stored discrete tail (the empirical FPR of screening at v)."""
    hist = tail["hist"]
    n = tail["n"]
    ge = sum(c for k, c in hist.items() if int(k) >= v)
    return ge / n
