"""I3 / Round 19 — a numpy-vectorised, MODE-PARAMETERISED re-implementation of the repo's
skip-aware beam decoder, batched across trials.

WHY THIS EXISTS.  `skipdecode.beam_decode` runs at ~25 decodes/s at L=120 on one core.
G-CAL requires >= 1e6 null decodes per published cell. 1e6/25 = 11 CPU-hours per cell, and
this lane must publish ~30 cells. Batching the beam across trials makes the same computation
~25x cheaper without changing it.

THE CONTRACT (PREREG Q5, the lane's kill condition).  This module is worthless unless it
reproduces the reference decoder *exactly*. `selftest_exact()` decodes 200 independent
random (C, K) pairs at each of L in {31, 120, 240} with both implementations and requires
the returned `score` to agree to 1e-9 on 200/200. If it does not, the fast path is abandoned
and the lane falls back to reference-instrument sampling at reduced n.

TWO REPRESENTATIONS, chosen by the transition relation, because the relation decides the
shape of the work:

  * SPARSE relations (`keyskip1`, `skip_by_two`) admit a key skip only when every skipped
    key position would have reproduced the previous cipher rune -- probability 1/29 each.
    The beam therefore grows like 1.034^i and is *ragged* across trials. A rectangular
    (T, beam_w) array is then ~85 % padding, which is exactly why the first cut of this
    module was no faster than the reference. The sparse path keeps one FLAT state vector
    with a trial-id column and only pays for states that exist.
  * PERMISSIVE relations (`drift*`, `union<lam>`) admit every advance, so every trial holds
    exactly beam_w states and a rectangular (T, beam_w) array is optimal.

Plaintext is recovered by BACKPOINTER TRACEBACK, not by carrying an (M, L) plaintext array
through every step; carrying it costs more memory traffic than the whole decode.

MODES -- the transition relation, which is the thing Round 18 L7-B found to be the real hole:

    union(lam)   advances 1..1+max_skip; a doublet-consistent advance is free, an
                 inconsistent one costs `lam` in score.
                 lam = inf  ->  EXACTLY the repo's beam_decode           (mode 'keyskip1')
                 lam = 0    ->  free drift, no constraint at all         (mode 'drift<k>')
                 0 < lam < inf -> a drift-TOLERANT decoder of the kind I1 is building
    skip_by_two  the L7-B construction: rejection burns two key draws, so an advance is
                 1 + 2*nrej and only the first draw of each rejected pair is constrained.

`lam` is this lane's scalar PERMISSIVENESS knob, and the null curve as a function of `lam`
is what tells Phase 2 what permissiveness it can afford.

SCORERS
    'quad_translit'  the repo's lp.score.Quadgram.score_norm over the transliteration.
                     This is the legacy statistic; its null cell must stay comparable to
                     every published number in the ledger.
    'tri_rune'       a rune-space trigram LM (detectors.build_trigram) for the non-English
                     registers of I2's panel. Mean log10 over L-2 trigrams.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (os.path.join(LP, "src"),
           os.path.join(LP, "benchmark"),
           os.path.join(LP, "analysis", "campaign18_skip"),
           os.path.join(LP, "analysis", "round11"),
           os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from lp import gematria as gp          # noqa: E402
from lp import score as _score         # noqa: E402

N = gp.N                                # 29
NULLCH = 26                             # padding symbol in the 3-char translit state
S3 = 27 ** 3                            # 19683 translit states
EMPTY3 = NULLCH * 729 + NULLCH * 27 + NULLCH
Q = _score.default()

_TR = [gp.IDX_TO_TRANS[i] for i in range(N)]
RLEN = np.array([len(t) for t in _TR], dtype=np.int64)
RC0 = np.array([ord(t[0]) - 65 for t in _TR], dtype=np.int64)
RC1 = np.array([(ord(t[1]) - 65) if len(t) > 1 else 0 for t in _TR], dtype=np.int64)

_QTAB = None


def qtab():
    """(27^3, 26): delta of the quadgram completed by appending char c to 3-char state s3.

    A state containing the padding symbol contributes 0, reproducing `_quad_delta`'s
    `e in range(max(4, L1+1), L2+1)` guard exactly -- no complete quadgram exists yet.
    """
    global _QTAB
    if _QTAB is not None:
        return _QTAB
    cache = os.path.join(HERE, "_qtab.npy")
    if os.path.exists(cache):
        _QTAB = np.load(cache)
        return _QTAB
    t = np.zeros((S3, 26), dtype=np.float64)
    a, b, c = np.meshgrid(np.arange(26), np.arange(26), np.arange(26), indexing="ij")
    t[(a * 729 + b * 27 + c).ravel(), :] = Q.floor
    for quad, val in Q.d.items():
        o = [ord(x) - 65 for x in quad]
        if min(o) < 0 or max(o) > 25:
            continue
        t[o[0] * 729 + o[1] * 27 + o[2], o[3]] = val
    np.save(cache, t)
    _QTAB = t
    return t


# --------------------------------------------------------------------------- mode registry
def mode_spec(mode, max_skip=3):
    """A dict describing one transition relation."""
    if mode == "keyskip1":
        return {"kind": "union", "max_skip": max_skip, "lam": float("inf"),
                "label": "keyskip1", "sparse": True}
    if mode == "skip_by_two":
        return {"kind": "by_two", "max_skip": max_skip, "lam": float("inf"),
                "label": "skip_by_two", "sparse": True}
    if mode.startswith("drift"):
        k = int(mode[5:])
        return {"kind": "union", "max_skip": k, "lam": 0.0, "label": mode, "sparse": False}
    if mode.startswith("union"):
        lam = float(mode[5:].replace("_", "."))
        return {"kind": "union", "max_skip": max_skip, "lam": lam,
                "label": mode, "sparse": False}
    raise ValueError(f"unknown mode {mode!r}")


def branching(mode, max_skip=3):
    """Nominal admissible transitions per position -- the permissiveness scale.

    keyskip1: 1 + sum_j (1/29)^j over the j-skip advances (a skip needs every skipped key
    position to reproduce the previous cipher rune, probability 1/29 each).
    """
    s = mode_spec(mode, max_skip)
    if s["lam"] == 0.0:
        return 1.0 + s["max_skip"]
    if s["lam"] == float("inf"):
        step = 2 if s["kind"] == "by_two" else 1
        return 1.0 + sum((1.0 / N) ** (j if s["kind"] != "by_two" else j)
                         for j in range(1, s["max_skip"] + 1))
    # finite penalty: every advance is admissible, but an inconsistent one is discounted.
    # Effective branching is reported empirically by run_calibration; this is the bound.
    return 1.0 + s["max_skip"]


# --------------------------------------------------------------------------- state pushes
def _push_translit(st, p, QT):
    c0 = RC0[p]
    d = QT[st, c0]
    s1 = (st % 729) * 27 + c0
    two = RLEN[p] == 2
    c1 = RC1[p]
    d2 = np.where(two, QT[s1, c1], 0.0)
    s2 = np.where(two, (s1 % 729) * 27 + c1, s1)
    return s2, d + d2


def _push_tri(st, p, TT):
    """2-rune state. 0..N*N-1 = two real runes (a*N+b); N*N + r = only one rune so far."""
    real = st < N * N
    d = np.where(real, TT[np.where(real, st, 0), p], 0.0)
    ns = np.where(real, (st % N) * N + p, (st - N * N) * N + p)
    return ns, d


# --------------------------------------------------------------------------- the batch beam
def batch_decode(C, K, scorer="quad_translit", tri=None, sign=-1, beam_w=400,
                 max_skip=3, mode="keyskip1", want_plain=False):
    """Decode T ciphertexts under T keystreams at once.

    C   (T, L)  int   ciphertext rune indices
    K   (T, KL) int   keystreams; KL must cover the worst-case advance
    tri (29,29,29)    required when scorer='tri_rune'

    Returns dict(score=(T,), cum=(T,), tlen=(T,), beam_states=(T,),
                 plain=(T,L) if want_plain).
    """
    spec = mode_spec(mode, max_skip)
    C = np.ascontiguousarray(C, dtype=np.int64)
    K = np.ascontiguousarray(K, dtype=np.int64)
    if spec["sparse"]:
        return _decode_sparse(C, K, spec, scorer, tri, sign, beam_w, want_plain)
    return _decode_dense(C, K, spec, scorer, tri, sign, beam_w, want_plain)


def _init(C, K, scorer, tri, sign):
    T, L = C.shape
    p0 = (C[:, 0] + sign * K[:, 0]) % N
    if scorer == "quad_translit":
        st = np.full(T, EMPTY3, dtype=np.int64)
        st, _ = _push_translit(st, p0, qtab())
        tlen = RLEN[p0].copy()
    else:
        st = p0 + N * N
        tlen = np.ones(T, dtype=np.int64)
    return p0, st, tlen


def _finish(scorer, cum, tlen, L):
    if scorer == "quad_translit":
        denom = np.maximum(tlen - 3, 1)
        return np.where(tlen - 3 <= 0, -999.0, cum / denom)
    return cum / max(1, L - 2)


def _trace(par_hist, rune_hist, idx, p0, T, L):
    plain = np.zeros((T, L), dtype=np.int64)
    cur = idx.copy()
    for i in range(L - 1, 0, -1):
        plain[:, i] = rune_hist[i - 1][cur]
        cur = par_hist[i - 1][cur]
    plain[:, 0] = p0[cur]
    return plain


def _decode_sparse(C, K, spec, scorer, tri, sign, beam_w, want_plain):
    """Ragged/flat path for relations whose admissible advances are rare (keyskip1, by_two)."""
    T, L = C.shape
    QT = qtab() if scorer == "quad_translit" else None
    TT = (np.ascontiguousarray(tri, dtype=np.float64).reshape(N * N, N)
          if scorer == "tri_rune" else None)
    ms = spec["max_skip"]
    by_two = spec["kind"] == "by_two"
    adv = (1 + 2 * np.arange(ms + 1)) if by_two else (1 + np.arange(ms + 1))
    A = len(adv)
    KLmax = K.shape[1] - 1

    p0, st, tlen = _init(C, K, scorer, tri, sign)
    sc = np.zeros(T)
    pa = np.zeros(T, dtype=np.int64)
    tid = np.arange(T, dtype=np.int64)
    par_hist, rune_hist = [], []
    peak = 0

    for i in range(1, L):
        M = len(sc)
        acc = np.minimum(pa[:, None] + adv[None, :], KLmax)          # (M, A)
        kg = K[tid[:, None], acc]
        ci = C[tid, i][:, None]
        cprev = C[tid, i - 1][:, None]
        p = (ci + sign * kg) % N
        ok = np.ones((M, A), dtype=bool)
        for j, a in enumerate(adv):
            if a == 1:
                continue
            nchk = (a - 1) // 2 if by_two else (a - 1)
            good = np.ones(M, dtype=bool)
            for q in range(nchk):
                m = np.minimum(pa + 1 + (2 * q if by_two else q), KLmax)
                good &= (((p[:, j] - sign * K[tid, m]) % N) == cprev[:, 0])
            ok[:, j] = good
        if scorer == "quad_translit":
            nst, d = _push_translit(st[:, None], p, QT)
            ntl = tlen[:, None] + RLEN[p]
        else:
            nst, d = _push_tri(st[:, None], p, TT)
            ntl = tlen[:, None] + 1
        nsc = sc[:, None] + d
        par = np.broadcast_to(np.arange(M)[:, None], (M, A))

        keep = ok.ravel()
        sc2 = nsc.ravel()[keep]
        st2 = nst.ravel()[keep]
        tl2 = ntl.ravel()[keep]
        pa2 = acc.ravel()[keep]
        p2 = p.ravel()[keep]
        par2 = par.ravel()[keep]
        tid2 = tid[par2]

        cnt = np.bincount(tid2, minlength=T)
        peak = max(peak, int(cnt.max()))
        if cnt.max() > beam_w:
            order = np.lexsort((-sc2, tid2))
            tids = tid2[order]
            cs = np.bincount(tids, minlength=T)
            starts = np.concatenate(([0], np.cumsum(cs)[:-1]))
            rank = np.arange(len(tids)) - np.repeat(starts, cs)
            order = order[rank < beam_w]
            sc2, st2, tl2, pa2, p2, par2, tid2 = (sc2[order], st2[order], tl2[order],
                                                  pa2[order], p2[order], par2[order],
                                                  tid2[order])
        sc, st, tlen, pa, tid = sc2, st2, tl2, pa2, tid2
        if want_plain:
            par_hist.append(par2.astype(np.int32))
            rune_hist.append(p2.astype(np.int8))

    order = np.lexsort((-sc, tid))
    cs = np.bincount(tid[order], minlength=T)
    starts = np.concatenate(([0], np.cumsum(cs)[:-1]))
    best = order[starts]
    cum, tl = sc[best], tlen[best]
    out = {"score": _finish(scorer, cum, tl, L), "cum": cum, "tlen": tl,
           "beam_states": np.full(T, peak), "ptr_end": pa[best],
           "drift": (pa[best] - (L - 1)) / max(1, L - 1)}
    if want_plain:
        out["plain"] = _trace(par_hist, rune_hist, best, p0, T, L)
    return out


def _decode_dense(C, K, spec, scorer, tri, sign, beam_w, want_plain):
    """Rectangular path for permissive relations: every trial holds exactly beam_w states."""
    T, L = C.shape
    QT = qtab() if scorer == "quad_translit" else None
    TT = (np.ascontiguousarray(tri, dtype=np.float64).reshape(N * N, N)
          if scorer == "tri_rune" else None)
    ms = spec["max_skip"]
    lam = spec["lam"]
    by_two = spec["kind"] == "by_two"
    adv = (1 + 2 * np.arange(ms + 1)) if by_two else (1 + np.arange(ms + 1))
    A = len(adv)
    KLmax = K.shape[1] - 1

    p0, st0, tl0 = _init(C, K, scorer, tri, sign)
    B = 1
    sc = np.zeros((T, 1))
    pa = np.zeros((T, 1), dtype=np.int64)
    st = st0[:, None].copy()
    tlen = tl0[:, None].copy()
    par_hist, rune_hist = [], []

    for i in range(1, L):
        acc = np.minimum(pa[:, :, None] + adv[None, None, :], KLmax)     # (T,B,A)
        kg = np.take_along_axis(K[:, None, :], acc, axis=2)
        ci = C[:, i][:, None, None]
        cprev = C[:, i - 1][:, None, None]
        p = (ci + sign * kg) % N
        pen = np.zeros((T, B, A))
        if lam != 0.0:
            for j, a in enumerate(adv):
                if a == 1:
                    continue
                nchk = (a - 1) // 2 if by_two else (a - 1)
                good = np.ones((T, B), dtype=bool)
                for q in range(nchk):
                    m = np.minimum(pa + 1 + (2 * q if by_two else q), KLmax)
                    km = np.take_along_axis(K, m, axis=1)
                    good &= (((p[:, :, j] - sign * km) % N) == cprev[:, :, 0])
                pen[:, :, j] = np.where(good, 0.0, lam)
        if scorer == "quad_translit":
            nst, d = _push_translit(st[:, :, None], p, QT)
            ntl = tlen[:, :, None] + RLEN[p]
        else:
            nst, d = _push_tri(st[:, :, None], p, TT)
            ntl = tlen[:, :, None] + 1
        with np.errstate(invalid="ignore"):
            nsc = sc[:, :, None] + d - pen
        nsc = np.where(np.isfinite(nsc), nsc, -np.inf)
        par = np.broadcast_to(np.arange(B)[None, :, None], (T, B, A))

        NSC = nsc.reshape(T, B * A)
        cw = B * A
        nb = min(beam_w, cw)
        if nb < cw:
            idx = np.argpartition(-NSC, nb - 1, axis=1)[:, :nb]
        else:
            idx = np.broadcast_to(np.arange(cw), (T, cw))
        sc = np.take_along_axis(NSC, idx, axis=1)
        st = np.take_along_axis(nst.reshape(T, cw), idx, axis=1)
        tlen = np.take_along_axis(ntl.reshape(T, cw), idx, axis=1)
        pa = np.take_along_axis(acc.reshape(T, cw), idx, axis=1)
        if want_plain:
            par_hist.append(np.take_along_axis(par.reshape(T, cw), idx, axis=1).astype(np.int32))
            rune_hist.append(np.take_along_axis(p.reshape(T, cw), idx, axis=1).astype(np.int8))
        B = nb

    best = np.argmax(sc, axis=1)
    ar = np.arange(T)
    cum, tl = sc[ar, best], tlen[ar, best]
    out = {"score": _finish(scorer, cum, tl, L), "cum": cum, "tlen": tl,
           "beam_states": np.full(T, B), "ptr_end": pa[ar, best],
           "drift": (pa[ar, best] - (L - 1)) / max(1, L - 1)}
    if want_plain:
        plain = np.zeros((T, L), dtype=np.int64)
        cur = best.copy()
        for i in range(L - 1, 0, -1):
            plain[:, i] = rune_hist[i - 1][ar, cur]
            cur = par_hist[i - 1][ar, cur]
        plain[:, 0] = p0
        out["plain"] = plain
    return out


# --------------------------------------------------------------------------- PREREG Q5 test
def selftest_exact(n=200, lengths=(31, 120, 240), beam_w=400, max_skip=3, seed=90210,
                   verbose=True, check_plain=True):
    """PREREG Q5. 200 independent random (C, K) per length; `score` must agree to 1e-9.

    `plain` agreement is recorded for information only (PREREG addendum 1): the reference
    defines no tie-break order over equal-scoring beam states, so only `score` gates.
    """
    import skipdecode as sk
    rng = np.random.default_rng(seed)
    rows = []
    for L in lengths:
        KL = L * (max_skip + 1) + 64
        C = rng.integers(0, N, size=(n, L))
        K = rng.integers(0, N, size=(n, KL))
        got = batch_decode(C, K, beam_w=beam_w, max_skip=max_skip, mode="keyskip1",
                           want_plain=check_plain)
        ref = [sk.beam_decode(list(map(int, C[t])), list(map(int, K[t])), sign=-1, o=0,
                              beam_w=beam_w, max_skip=max_skip) for t in range(n)]
        dif = np.abs(got["score"] - np.array([r["score"] for r in ref]))
        pl_ok = None
        if check_plain:
            pl_ok = int(sum(1 for t in range(n)
                            if list(map(int, got["plain"][t])) == list(ref[t]["plain_idx"])))
        rows.append({"L": L, "n": n, "max_abs_diff": float(dif.max()),
                     "n_exact": int((dif <= 1e-9).sum()),
                     "n_plain_identical": pl_ok,
                     "passed": bool((dif <= 1e-9).all())})
        if verbose:
            r = rows[-1]
            print(f"  L={L:4d}  score {r['n_exact']}/{n} exact  max|diff|={r['max_abs_diff']:.3e}"
                  f"  plain {r['n_plain_identical']}/{n}   {'PASS' if r['passed'] else 'FAIL'}")
    return rows


def throughput(T=2048, L=120, mode="keyskip1", beam_w=400, max_skip=3, seed=1, scorer="quad_translit", tri=None):
    import time
    rng = np.random.default_rng(seed)
    KL = L * (2 * max_skip + 2) + 64
    C = rng.integers(0, N, size=(T, L))
    K = rng.integers(0, N, size=(T, KL))
    t = time.time()
    r = batch_decode(C, K, beam_w=beam_w, max_skip=max_skip, mode=mode,
                     scorer=scorer, tri=tri)
    el = time.time() - t
    return {"mode": mode, "L": L, "T": T, "seconds": el, "per_s": T / el,
            "mean": float(r["score"].mean()), "max": float(r["score"].max()),
            "peak_beam": int(r["beam_states"].max())}


if __name__ == "__main__":
    if "--bench" in sys.argv:
        for L, T, m in ((31, 8192, "keyskip1"), (120, 4096, "keyskip1"),
                        (240, 1024, "keyskip1"), (120, 2048, "skip_by_two"),
                        (120, 512, "drift3"), (120, 512, "union0_5")):
            r = throughput(T=T, L=L, mode=m)
            print(f"{r['mode']:12s} L={r['L']:3d} T={r['T']:5d} {r['seconds']:6.2f}s "
                  f"{r['per_s']:8.1f} dec/s  peakbeam={r['peak_beam']:4d} "
                  f"mean={r['mean']:.3f} max={r['max']:.3f}")
    else:
        print("PREREG Q5 - vectorised engine vs skipdecode.beam_decode")
        rs = selftest_exact()
        print("ALL PASS" if all(r["passed"] for r in rs) else "KILL CONDITION MET")
