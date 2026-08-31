"""Round 20 / P1 -- THE skip-aware, multi-register PREFILTER SIEVE.

WHY THIS LANE EXISTS.  R1 (round19) named the sieve's absence "the finding" (D-ii): the only
affordable prefilter, round17/lib_padsweep.dense_scan, is RIGID (fixed one-key-per-rune
alignment) and ENGLISH-ONLY.  C2 measured its true-key survival on real Marsaglia bytes:
LP1 0.767, LATIN 0.70, OE 0.60, CY 0.30, EN_HALFVOWEL 0.067, EN_NOVOWEL 0.000 -- it throws the
true key away, unevenly by register, before I1xI2 ever sees it.  So every Phase-2 negative that
runs behind it is register-blind by construction.

WHAT THIS MODULE DOES.  A two-stage sieve.

  Stage A (cheap, vectorized numpy, rigid alignment over a head window W):
      score the decrypt head under ALL 9 register trigram LMs and take the MAX OVER REGISTERS
      per offset.  This is the one lever dense_scan's English-only trigram lacks; it directly
      recovers the LATIN/OE/CY/half-vowel register loss.  Optionally union with the C2 §4.5
      free language-agnostic screens (ioc, distinct).  Keeps a top fraction fA.

  Stage B (skip-aware, I1 driftbeam at reduced beam width):
      re-score ONLY the Stage-A survivors with the beam so the keyskip1 / drift skip relations
      are admitted, not rigid alignment.  Scores each survivor's decode head under the 9-register
      panel (max over registers).  Keeps a top fraction fB.

  reduction = 1/(fA*fB);  survival = per-register product of the two stages' true-key retention.

Everything is seed-3301 rooted and order-preserving.  NEVER a rigid decoder is used to ADJUDICATE
LP2 -- Stage A is a numpy SCREEN over a rigid decrypt (the only affordable first pass); the actual
skip-aware decode is I1's driftbeam in Stage B, and the survivors it retains are what the expensive
I1xI2 adjudicator finally sees.  Stage A rigidity is a SCREEN cost (measured, published), not an
adjudication.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for _p in (os.path.join(ROOT, "src"),
           os.path.join(ROOT, "benchmark"),
           os.path.join(ROOT, "analysis", "round19", "I1"),
           os.path.join(ROOT, "analysis", "round10b", "B6-non-english-plaintext"),
           os.path.join(ROOT, "analysis", "round18", "L7-redteam"),
           os.path.join(ROOT, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

N = 29
SEED3301 = 3301

# The 9 registers of the I2 panel (RAND is the negative-control floor, kept separate).
PANEL = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
         "EN_HALFVOWEL", "EN_NOVOWEL"]

_LMS = None


def register_lms():
    """The 9 register (29,29,29) log10 conditional trigram LMs, cached as .npz.

    Built from round18/L7-redteam.a1_scorer_language.build_panels() -- the SAME corpora
    L7-A/C2 measured against, via round10b detectors.build_trigram (alpha=0.5)."""
    global _LMS
    if _LMS is not None:
        return _LMS
    path = os.path.join(HERE, "_p1_lms.npz")
    if os.path.exists(path):
        z = np.load(path)
        _LMS = {k: z[k] for k in z.files}
        return _LMS
    import detectors as D
    import a1_scorer_language as A1
    panels = A1.build_panels()
    lms = {r: D.build_trigram(np.asarray(panels[r], dtype=np.int64)) for r in PANEL}
    np.savez_compressed(path, **lms)
    _LMS = lms
    return lms


# --------------------------------------------------------------------- Stage A
def _head_trigram_scores(P, lms, registers):
    """(m, W) decrypt-head rune indices -> {register: (m,) mean-trigram-logprob}."""
    W = P.shape[1]
    out = {}
    for r in registers:
        T = lms[r]
        sc = np.zeros(P.shape[0], dtype=np.float64)
        for j in range(2, W):
            sc += T[P[:, j - 2], P[:, j - 1], P[:, j]]
        sc /= (W - 2)
        out[r] = sc
    return out


def stageA_scores(K, C, sign=-1, W=32, registers=None, want_langagnostic=False):
    """The cheap, vectorized, rigid-alignment Stage-A screen over EVERY offset of a pad.

    For each offset o, decrypt the W-rune head  P = (C[:W] + sign*K[o:o+W]) % N,  score it under
    each register's trigram LM, and return the MAX OVER REGISTERS (plus, if asked, the C2 §4.5
    language-agnostic ioc / distinct screens computed from the same P matrix for free).

    Returns dict of (n_off,) arrays: {"multireg": max-over-register, ["ioc","ndist"], and each
    per-register score under key f"reg_{r}"}.  n_off = len(K) - W.
    """
    lms = register_lms()
    registers = registers or PANEL
    K = np.ascontiguousarray(np.asarray(K, dtype=np.int64))
    C = np.asarray(C[:W], dtype=np.int64)
    n_off = len(K) - W
    if n_off <= 0:
        return {}, 0
    out = {"multireg": np.full(n_off, -1e30, dtype=np.float64)}  # RAW max (diagnostic)
    per = {r: np.empty(n_off, dtype=np.float64) for r in registers}
    if want_langagnostic:
        out["ioc"] = np.empty(n_off, dtype=np.float64)
        out["ndist"] = np.empty(n_off, dtype=np.float64)
    denom = W * (W - 1)
    chunk = 1 << 18
    for start in range(0, n_off, chunk):
        stop = min(start + chunk, n_off)
        m = stop - start
        Kw = np.lib.stride_tricks.sliding_window_view(K[start:stop + W], W)[:m]
        P = (C[None, :] + sign * Kw) % N
        sc = _head_trigram_scores(P, lms, registers)
        best = np.full(m, -1e30, dtype=np.float64)
        for r in registers:
            per[r][start:stop] = sc[r]
            np.maximum(best, sc[r], out=best)
        out["multireg"][start:stop] = best
        if want_langagnostic:
            flat = (P + N * np.arange(m, dtype=np.int64)[:, None]).ravel()
            cnt = np.bincount(flat, minlength=N * m).reshape(m, N)
            out["ioc"][start:stop] = (cnt * (cnt - 1)).sum(1) * (N / denom)
            out["ndist"][start:stop] = -(cnt > 0).sum(1)
        del P
    for r in registers:
        out[f"reg_{r}"] = per[r]
    # The SCREEN statistic: per-register z-standardisation (each register's offset population
    # is standardised to its own mean/std over this pad) then MAX over registers.  This is the
    # cheap population analogue of I2's panel-max z: without it the tiny LP1_REAL LM (1768 runes,
    # sparse) produces spuriously high RAW scores at wrong offsets and dominates the raw max.
    zbest = np.full(n_off, -1e30, dtype=np.float64)
    for r in registers:
        v = per[r]
        z = (v - v.mean()) / (v.std() + 1e-12)
        np.maximum(zbest, z, out=zbest)
    out["zmax"] = zbest
    return out, n_off


def top_offsets(scores, keep):
    """Return the offsets (indices into the score array) of the top-`keep` by score, best-first."""
    n = len(scores)
    keep = min(keep, n)
    top = np.argpartition(-scores, keep - 1)[:keep]
    return top[np.argsort(-scores[top])]


# --------------------------------------------------------------------- Stage B
# logical Stage-B relation name -> I1 driftbeam PRESET key
STAGEB_PRESET = {"keyskip1": "exact", "drift": "drift", "pair": "pair"}


def stageB_rescore(C, K, offsets, sign=-1, W=32, beam_w=16, preset="keyskip1"):
    """Skip-aware re-score of Stage-A survivor OFFSETS with I1's driftbeam.

    For each candidate offset, decode the W-rune head with the beam (keyskip1 baseline or drift
    permissive) and score the decoded head under the 9-register panel (max over registers).  The
    beam admits key skips -- so a true offset whose loop burned skips, which rigid Stage A ranks
    lower, gets re-ranked correctly here.  Returns (m,) array of multireg beam-head scores aligned
    to `offsets`.
    """
    import driftbeam as DB
    lms = register_lms()
    kw = dict(DB.PRESETS[STAGEB_PRESET[preset]])
    mode = kw.pop("mode")
    kw["beam_w"] = beam_w
    Cw = list(C[:W])
    out = np.empty(len(offsets), dtype=np.float64)
    for i, o in enumerate(offsets):
        r = DB.beam_decode(Cw, K, sign=sign, o=int(o), mode=mode, want_path=True, **kw)
        idx = r["plain_idx"][:W]
        if len(idx) < 3:
            out[i] = -1e30
            continue
        a = np.asarray(idx, dtype=np.int64)
        best = -1e30
        for reg in PANEL:
            T = lms[reg]
            s = float(T[a[:-2], a[1:-1], a[2:]].mean())
            if s > best:
                best = s
        out[i] = best
    return out


# --------------------------------------------------------------------- the sieve
def sieve(C, K, o_true=None, sign=-1, W=32, fA=1e-3, fB=0.1, beam_w=16,
          stageB_preset="keyskip1", want_langagnostic=False):
    """Run the full two-stage sieve on one (pad K, cipher-head C).

    Returns a dict.  If o_true is given, reports whether the true offset SURVIVES each stage and
    its rank.  reduction = n_off / n_final.  This is the object the survival surface is built from.
    """
    a_scores, n_off = stageA_scores(K, C, sign=sign, W=W,
                                    want_langagnostic=want_langagnostic)
    keepA = max(1, int(round(n_off * fA)))
    survA = top_offsets(a_scores["zmax"], keepA)
    if want_langagnostic:
        # C2 §4.5 union: also admit the top-keepA by ioc and by ndist (free recovery in the
        # registers where the trigram is blind).
        ua = set(int(x) for x in survA)
        ua |= set(int(x) for x in top_offsets(a_scores["ioc"], keepA))
        ua |= set(int(x) for x in top_offsets(a_scores["ndist"], keepA))
        survA = np.array(sorted(ua), dtype=np.int64)
    b_scores = stageB_rescore(C, K, survA, sign=sign, W=W, beam_w=beam_w,
                              preset=stageB_preset)
    keepB = max(1, int(round(len(survA) * fB)))
    ordB = np.argsort(-b_scores)[:keepB]
    survB = survA[ordB]
    res = {"n_off": int(n_off), "keepA": int(keepA), "n_survA": int(len(survA)),
           "keepB": int(keepB), "n_final": int(len(survB)),
           "reduction": float(n_off / max(1, len(survB)))}
    if o_true is not None:
        o_true = int(o_true)
        # Stage-A rank of the true offset by the zmax screen
        rankA = int(np.where(top_offsets(a_scores["zmax"], n_off) == o_true)[0][0]) \
            if o_true < n_off else -1
        inA = o_true in set(int(x) for x in survA)
        inB = o_true in set(int(x) for x in survB)
        res.update({"o_true": o_true, "survivesA": bool(inA), "survivesB": bool(inB),
                    "rankA": rankA})
    return res


if __name__ == "__main__":
    # smoke: build the LMs and time a single-pad Stage-A pass.
    import time
    lms = register_lms()
    print("registers:", list(lms.keys()))
    rng = np.random.default_rng(3301)
    K = rng.integers(0, N, size=2_000_000).tolist()
    C = rng.integers(0, N, size=64).tolist()
    t0 = time.time()
    sc, n_off = stageA_scores(K, C, W=32)
    print(f"stageA over {n_off:,} offsets x 9 regs: {time.time()-t0:.1f}s "
          f"({n_off/(time.time()-t0):.2e}/s)")
