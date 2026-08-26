"""Round 18 / L2 -- a FAST, BIT-IDENTICAL re-implementation of the repo's skip-aware beam.

Why this exists.  `campaign18_skip.skipdecode.beam_decode` carries the whole plaintext
transliteration *string* inside every beam hypothesis and rebuilds it with `tl + add` at
every node expansion.  That is O(L) per node, so a full-book decode is O(L^2 * W) character
copies: B-04's Stage D measured **68 s per 12,956-rune decode** (10,192 s / 150).  At that
rate the length-power test this lane needs (B.3) and the drift-corrected ladder (B.4) are
not affordable.

This module keeps only the last 3 characters of each hypothesis (all a quadgram model can
see) plus a back-pointer, which makes it O(L * W * (max_skip+1)) with no string copying.

It is a re-implementation, not an improvement: `gate_F0()` proves it returns scores
identical to `sk.beam_decode` to < 1e-9 and the same plaintext index vector, on random
(ciphertext, keystream) pairs at three lengths.  Per PREREG section 3 (gate F0) it may not
be used for anything unless that gate passes.

Run:  python3 fastbeam.py          # runs gate F0
"""
import os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round13", "B04")):
    sys.path.insert(0, os.path.join(ROOT, p))

from lp import gematria as gp          # noqa: E402
from lp import score as _score         # noqa: E402

N = gp.N
Q = _score.default()
TRANS = [gp.IDX_TO_TRANS[i] for i in range(N)]
TLEN = [len(t) for t in TRANS]


def beam_decode(C, K, sign=-1, o=0, beam_w=400, max_skip=3, want_path=True):
    """Numerically identical to skipdecode.beam_decode, without the O(L) string copy.

    Returns dict(score, beam_score, plain_idx, ptr_end, translit, n_skips, nchars).
    `n_skips` = ptr_end - o - (len(C)-1) = total keystream draws the winning path says the
    rejection sampler consumed.  That quantity is not exposed by the original decoder and
    is used in this lane as a second, English-independent ranking channel (PREREG 3.B.4).
    """
    d, floor = Q.d, Q.floor
    if o + len(C) + max_skip * len(C) >= len(K):
        Kx = list(K) + [0] * (len(C) * (max_skip + 1) + 8)
    else:
        Kx = K
    nK = len(Kx)

    p0 = (C[0] + sign * Kx[o]) % N
    t0 = TRANS[p0]
    # hypothesis = (cum, acc_key_idx, tail(<=3 chars), nchars, c_prev, node_id)
    beams = [(0.0, o, t0, len(t0), C[0], 0)]
    # back-pointer tables, one row per step
    bp_parent = [[-1]]
    bp_rune = [[p0]]

    for i in range(1, len(C)):
        ci = C[i]
        nxt = []
        par_row = []
        rune_row = []
        for bidx, (sc, pa, tail, L1, cprev, _nid) in enumerate(beams):
            off = L1 - len(tail)
            for dsk in range(0, max_skip + 1):
                acc = pa + 1 + dsk
                if acc >= nK:
                    break
                p = (ci + sign * Kx[acc]) % N
                ok = True
                for m in range(pa + 1, acc):
                    if (p - sign * Kx[m]) % N != cprev:
                        ok = False
                        break
                if not ok:
                    continue
                add = TRANS[p]
                # quadgrams newly completed by appending `add`
                s = tail + add
                tot = 0.0
                e0 = 4 if L1 < 3 else L1 + 1
                for e in range(e0, L1 + len(add) + 1):
                    a = e - 4 - off
                    if a < 0:
                        continue
                    tot += d.get(s[a:e - off], floor)
                nsc = sc + tot
                ntail = s[-3:]
                nxt.append((nsc, acc, ntail, L1 + len(add), ci, len(par_row)))
                par_row.append(_nid)          # parent's node-id, NOT its rank in `beams`
                rune_row.append(p)
        if not nxt:
            break
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
        bp_parent.append(par_row)
        bp_rune.append(rune_row)

    best = beams[0] if beams else None
    cum, ptr_end, tail, nchars, _cp, nid = best
    score = cum / (nchars - 3) if nchars > 3 else -999.0
    out = {"score": score, "beam_score": cum, "ptr_end": ptr_end,
           "nchars": nchars, "n_skips": ptr_end - o - (len(bp_parent) - 1)}
    if want_path:
        idx = []
        node = nid
        for step in range(len(bp_parent) - 1, -1, -1):
            idx.append(bp_rune[step][node])
            node = bp_parent[step][node]
        idx.reverse()
        out["plain_idx"] = idx
        out["translit"] = "".join(TRANS[j] for j in idx)
    return out


# ------------------------------------------------------------------ gate F0
def gate_F0(reps=8, lengths=(60, 120, 400), seed=20260825, verbose=True):
    """PREREG 3.B.3 gate F0 -- blocking. Fast decoder == repo decoder, or it is not used."""
    import skipdecode as sk
    rng = random.Random(seed)
    n_cases = 0
    worst_ds = 0.0
    path_mismatch = 0
    for L in lengths:
        for _ in range(reps):
            C = [rng.randrange(N) for _ in range(L)]
            K = [rng.randrange(N) for _ in range(L * 5 + 64)]
            sign = rng.choice((-1, 1))
            o = rng.randrange(0, 8)
            a = sk.beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3)
            b = beam_decode(C, K, sign=sign, o=o, beam_w=400, max_skip=3)
            ds = abs(a["score"] - b["score"])
            worst_ds = max(worst_ds, ds)
            if a["plain_idx"] != b["plain_idx"]:
                path_mismatch += 1
            n_cases += 1
    ok = (worst_ds < 1e-9 and path_mismatch == 0 and n_cases >= 20)
    if verbose:
        print(f"GATE F0: {n_cases} cases, lengths {lengths}")
        print(f"  max |score delta| vs skipdecode.beam_decode : {worst_ds:.3e}")
        print(f"  plaintext-path mismatches                   : {path_mismatch}")
        print(f"  -> {'PASS' if ok else 'FAIL'}")
    return {"cases": n_cases, "max_score_delta": worst_ds,
            "path_mismatches": path_mismatch, "pass": ok}


if __name__ == "__main__":
    import json, time
    t = time.time()
    r = gate_F0()
    r["elapsed_s"] = round(time.time() - t, 1)
    json.dump(r, open(os.path.join(HERE, "gate_F0.json"), "w"), indent=1)
