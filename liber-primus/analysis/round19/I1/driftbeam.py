"""Round 19 / I1 -- DRIFT-TOLERANT BEAM DECODER.

WHAT IS BROKEN.  `campaign18_skip/skipdecode.beam_decode` admits a key skip only if EVERY
skipped key position would have reproduced the previous cipher rune.  That validity test is
exact for `encipher_keyskip` and for nothing else.  round18/L7-redteam/RESULTS.md B measured
the price: handed the CORRECT key, `skip_by_two` (a rejection loop that burns two draws
instead of one, and which reproduces LP2's observed doublet rate) scores -6.90 at 25.8 %
rune recovery, and raising beam width 400->1000 / max_skip 3->8 changes that by EXACTLY 0.000.
The true path is outside the decoder's transition relation, not beyond its search depth.

WHAT THIS MODULE DOES.  It parameterises the transition relation:

    mode="keyskip1"    the repo's current relation, exact for `encipher_keyskip`.
                       Bit-identical to skipdecode.beam_decode (gate G-EQ).
    mode="keyskip2"    exact for `skip_by_two`: skipped positions come in PAIRS; the first
                       of each pair must reproduce c_prev, the second is unconstrained.
    mode="permissive"  agnostic: ANY key advance of <= max_skip positions per rune is
                       admitted, of which at most `max_free` need not be doublet-consistent,
                       at a beam-score penalty `lam` per unexplained advance.

THE ALGEBRA THAT MAKES IT FAST.  For an accepted key index `acc` at rune i, the repo's
validity condition on a skipped position m is

    (p - sign*K[m]) % N == c_prev  with  p = (c_i + sign*K[acc]) % N
      <=>  K[m] == (K[acc] - sign*(c_prev - c_i)) % N  =:  v(acc)

i.e. every skipped position must hold ONE value v(acc), fixed by K[acc].  So the number of
*unexplained* skips is  dsk - cnt[v(acc)]  where cnt is a 29-bin histogram of the skipped
window maintained in O(1) as acc advances, and the whole dsk loop can break as soon as
`dsk - max(cnt) > max_free` (that quantity is monotone non-decreasing in dsk).

Consequences:
  * max_free = 0 reproduces the repo's relation exactly, and *faster* than the naive loop;
  * on a high-entropy pad the loop breaks after ~max_free+1 branches, so `max_skip` may be
    set to 40 without paying for it -- which is what fixes the low-entropy-pad (constant key
    run) failures at r = 16 and r = 32, where dsk legitimately reaches r.

The fastbeam optimisation is preserved: each hypothesis carries only the last 3 characters of
its transliteration plus a back-pointer, so there is no O(L) string copy per node.

The `lam` penalty steers the SEARCH only.  The reported `score` is the unpenalised quadgram
`score_norm` of the path the penalised search chose, so it stays on the project's canonical
scale (English ~ -4.1, threshold -5.5, noise ~ -7.3) and is comparable to every ledger number.

Run:  python3 driftbeam.py          # self-gates (G-EQ + the mode-exactness checks)
"""
import os
import sys
import random
from operator import itemgetter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for _p in ("src", "benchmark", "analysis",
           os.path.join("analysis", "campaign18_skip"),
           os.path.join("analysis", "round11"),
           os.path.join("analysis", "round18", "L2-filter-leak")):
    _q = os.path.join(ROOT, _p)
    if _q not in sys.path:
        sys.path.insert(0, _q)

from lp import gematria as gp          # noqa: E402
from lp import score as _score         # noqa: E402

N = gp.N
Q = _score.default()
TRANS = [gp.IDX_TO_TRANS[i] for i in range(N)]

MODES = ("keyskip1", "keyskip2", "permissive")


# --------------------------------------------------------------------------- decoder
def beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3,
                mode="keyskip1", max_free=0, lam=0.0, lam_explained=0.0,
                start_slack=0, want_path=True):
    """Drift-tolerant skip-aware beam decode.

    Parameters
    ----------
    mode : "keyskip1" | "keyskip2" | "permissive"
    max_free : max key advances per rune that need NOT be doublet-consistent.
               Forced to 0 for mode="keyskip1".
    lam : beam-score penalty (log10 quadgram units) charged per unexplained advance.
    lam_explained : optional penalty per doublet-consistent advance (default 0, which is
               what keeps mode="keyskip1" bit-identical to the repo decoder).
    start_slack : allow the FIRST rune's key index to be o..o+start_slack (penalty lam each).
               Default 0 = the repo's behaviour.

    Returns dict(score, beam_score, quad_score, plain_idx, translit, ptr_end, nchars,
                 n_skips, n_unexplained).
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    if mode == "keyskip1":
        max_free = 0
    if mode == "permissive" and max_free < 1:
        raise ValueError("mode='permissive' with max_free=0 is just keyskip1; say so explicitly")

    d, floor = Q.d, Q.floor
    L = len(C)
    if L == 0:
        raise ValueError("empty ciphertext")
    if o + L + max_skip * L >= len(K):
        Kx = list(K) + [0] * (L * (max_skip + 1) + 8)
    else:
        Kx = K
    nK = len(Kx)
    pair = (mode == "keyskip2")

    # ---- initial hypotheses ------------------------------------------------
    bp_parent = [[]]
    bp_rune = [[]]
    beams = []
    for s in range(start_slack + 1):
        acc0 = o + s
        if acc0 >= nK:
            break
        p = (C[0] + sign * Kx[acc0]) % N
        t = TRANS[p]
        # (cum_penalised, cum_quadgram, acc, tail<=3, nchars, n_unexplained, node_id)
        beams.append((-lam * s, 0.0, acc0, t, len(t), s, len(bp_parent[0])))
        bp_parent[0].append(-1)
        bp_rune[0].append(p)
    if not beams:
        raise ValueError("key offset beyond end of keystream")

    cnt = [0] * N
    nn = N
    Tr = TRANS
    dget = d.get
    ms1 = max_skip + 1
    step_pair = 2 if pair else 1
    key0 = itemgetter(0)
    track = bool(want_path)

    for i in range(1, L):
        ci = C[i]
        sgn_delta = (sign * (C[i - 1] - ci)) % nn
        # per-step 29-entry lookups, indexed by the KEY VALUE at the accepted position:
        #   pmap[k] = plaintext rune,  tmap[k] = its transliteration,
        #   vmap[k] = the single key value every skipped position must hold.
        pmap = [(ci + sign * k) % nn for k in range(nn)]
        tmap = [Tr[p] for p in pmap]
        lmap = [len(t) for t in tmap]
        vmap = [(k - sgn_delta) % nn for k in range(nn)]
        nxt = []
        nxt_append = nxt.append
        par_row = []
        rune_row = []
        for (sc, qc, pa, tail, L1, nun_tot, nid) in beams:
            base = pa + 1
            hi = base
            maxcnt = 0
            long_form = L1 < 3
            off = 0 if long_form else L1 - 3
            for dsk in range(0, ms1):
                acc = base + dsk
                if acc >= nK:
                    break
                if dsk:
                    if not pair or (dsk & 1):
                        km = Kx[acc - 1]
                        c2 = cnt[km] + 1
                        cnt[km] = c2
                        if c2 > maxcnt:
                            maxcnt = c2
                    hi = acc
                    if pair:
                        if dsk & 1:
                            continue          # only even advances are representable
                        need = dsk >> 1
                    else:
                        need = dsk
                    if need - maxcnt > max_free:
                        break
                else:
                    need = 0
                kacc = Kx[acc]
                nun = need - cnt[vmap[kacc]]
                if nun > max_free:
                    continue
                la = lmap[kacc]
                s2 = tail + tmap[kacc]
                if long_form:
                    tot = 0.0
                    for e in range(4, L1 + la + 1):
                        a = e - 4 - off
                        if a < 0:
                            continue
                        tot += dget(s2[a:e - off], floor)
                elif la == 1:
                    tot = dget(s2, floor)             # s2 is exactly one quadgram
                else:
                    tot = dget(s2[:4], floor) + dget(s2[1:], floor)
                if nun:
                    nsc = sc + tot - lam * nun
                else:
                    nsc = sc + tot
                if lam_explained:
                    nsc -= lam_explained * (need - nun)
                if track:
                    nxt_append((nsc, qc + tot, acc, s2[-3:], L1 + la,
                                nun_tot + nun, len(par_row)))
                    par_row.append(nid)
                    rune_row.append(pmap[kacc])
                else:
                    nxt_append((nsc, qc + tot, acc, s2[-3:], L1 + la,
                                nun_tot + nun, 0))
            if hi > base:
                for m in range(base, hi, step_pair):
                    cnt[Kx[m]] = 0
        if not nxt:
            break
        nxt.sort(key=key0, reverse=True)
        beams = nxt[:beam_w]
        if track:
            bp_parent.append(par_row)
            bp_rune.append(rune_row)
        else:
            bp_parent.append(())

    cum, qcum, ptr_end, tail, nchars, nun_tot, nid = beams[0]
    score = qcum / (nchars - 3) if nchars > 3 else -999.0
    nsteps = len(bp_parent) - 1
    out = {"score": score, "beam_score": cum, "quad_score": qcum,
           "ptr_end": ptr_end, "nchars": nchars,
           "n_skips": ptr_end - o - nsteps, "n_unexplained": nun_tot,
           "mode": mode, "max_free": max_free, "lam": lam, "max_skip": max_skip}
    if want_path:
        idx = []
        node = nid
        for step in range(nsteps, -1, -1):
            idx.append(bp_rune[step][node])
            node = bp_parent[step][node]
        idx.reverse()
        out["plain_idx"] = idx
        out["translit"] = "".join(TRANS[j] for j in idx)
    return out


def recovery(plain_idx, truth_idx):
    """Rune-INDEX recovery (AGENTS.md 4: never score on the transliteration string --
    7 of the 29 runes are two characters long)."""
    if not truth_idx:
        return 0.0
    return sum(1 for a, b in zip(plain_idx, truth_idx) if a == b) / len(truth_idx)


# -------------------------------------------------------------- presets for Phase 2
PRESETS = {
    # the repo's current instrument, unchanged
    "exact":       dict(mode="keyskip1", max_skip=3,  max_free=0, lam=0.0, start_slack=0),
    "exact_ms8":   dict(mode="keyskip1", max_skip=8,  max_free=0, lam=0.0, start_slack=0),
    # exact for skip_by_two
    "pair":        dict(mode="keyskip2", max_skip=8,  max_free=0, lam=0.0, start_slack=0),
    # construction-agnostic -- THE RECOMMENDED PHASE-2 CONFIGURATION (RESULTS.md section 9).
    # lam = 12 is the joint optimum: it passes all 20 G-FIX cells AND leaves 0/4000 wrong
    # keys above -5.5, with 0.52-0.68 of margin over its own family-wise bar at 10^9 decodes.
    # lam <= 6 admits false positives (at lam = 4, 11.3 % of wrong keys clear -5.5); lam = 0
    # is a catastrophe that LOOKS like a success (score -4.7, rune recovery 13 %).
    # Prefer run_gates.suggest_max_skip(K, L) over the fixed 40 when the pad may be
    # low-entropy: max_skip must be able to cross the longest constant run in the keystream.
    "drift":       dict(mode="permissive", max_skip=40, max_free=2, lam=12.0, start_slack=2),
    # the lam = 8 point, kept because G-FIX and G-FP were both measured at it
    "drift_l8":    dict(mode="permissive", max_skip=40, max_free=2, lam=8.0, start_slack=2),
}


# ------------------------------------------------------------------- self-gates
def gate_EQ(reps=8, lengths=(60, 120, 400), seed=20260826, verbose=True):
    """G-EQ (blocking). mode='keyskip1' == skipdecode.beam_decode, or the lane is void."""
    import skipdecode as sk
    rng = random.Random(seed)
    n_cases = 0
    worst = 0.0
    mism = 0
    for L in lengths:
        for _ in range(reps):
            C = [rng.randrange(N) for _ in range(L)]
            K = [rng.randrange(N) for _ in range(L * 5 + 64)]
            sign = rng.choice((-1, 1))
            o = rng.randrange(0, 8)
            a = sk.beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3)
            b = beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3, mode="keyskip1")
            worst = max(worst, abs(a["score"] - b["score"]))
            if a["plain_idx"] != b["plain_idx"]:
                mism += 1
            n_cases += 1
    ok = (worst < 1e-9 and mism == 0 and n_cases >= 20)
    if verbose:
        print(f"GATE G-EQ: {n_cases} cases at lengths {lengths}")
        print(f"  max |score delta| vs skipdecode.beam_decode : {worst:.3e}")
        print(f"  plaintext-path mismatches                   : {mism}")
        print(f"  -> {'PASS' if ok else 'FAIL'}")
    return {"gate": "G-EQ", "cases": n_cases, "max_score_delta": worst,
            "path_mismatches": mism, "pass": ok}


def gate_EQ_fast(reps=6, lengths=(120, 400), seed=7, verbose=True):
    """Secondary equivalence: keyskip1 == round18/L2 fastbeam (the 9x reimplementation)."""
    import fastbeam as fb
    rng = random.Random(seed)
    worst, mism, n = 0.0, 0, 0
    for L in lengths:
        for _ in range(reps):
            C = [rng.randrange(N) for _ in range(L)]
            K = [rng.randrange(N) for _ in range(L * 5 + 64)]
            sign = rng.choice((-1, 1))
            o = rng.randrange(0, 8)
            a = fb.beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3)
            b = beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3, mode="keyskip1")
            worst = max(worst, abs(a["score"] - b["score"]))
            if a["plain_idx"] != b["plain_idx"]:
                mism += 1
            n += 1
    ok = worst < 1e-9 and mism == 0
    if verbose:
        print(f"GATE G-EQ2 (vs round18/L2 fastbeam): {n} cases, "
              f"max delta {worst:.3e}, mismatches {mism} -> {'PASS' if ok else 'FAIL'}")
    return {"gate": "G-EQ2", "cases": n, "max_score_delta": worst,
            "path_mismatches": mism, "pass": ok}


def _demo():
    """A visible plant-and-recover on skip_by_two: old relation vs the two new ones."""
    import constructions as cx
    P = cx.take_plain(240, 0)
    K = cx.key_sha(240 * 6 + 1024)
    C, info = cx.enc_skip_by_two(P, K, supp=0.83, seed=3301)
    print(f"\nplant: skip_by_two supp=0.83, L=240, {info['n_skips']} rejections")
    for name, kw in (("keyskip1 (repo)", PRESETS["exact"]),
                     ("keyskip1 ms=8", PRESETS["exact_ms8"]),
                     ("keyskip2 (exact)", PRESETS["pair"]),
                     ("permissive drift", PRESETS["drift"])):
        r = beam_decode(C, K, sign=-1, o=0, beam_w=400, **kw)
        print(f"  {name:20s} score {r['score']:7.3f}  recovery "
              f"{recovery(r['plain_idx'], P):6.1%}")


if __name__ == "__main__":
    import json
    import time
    t0 = time.time()
    res = {"gate_EQ": gate_EQ(), "gate_EQ2": gate_EQ_fast()}
    res["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(HERE, "out_eq.json"), "w"), indent=1)
    try:
        _demo()
    except Exception as exc:                                   # pragma: no cover
        print("demo skipped:", exc)
