"""PATCH PROPOSAL (not applied): relation 'keyskipk' and segment-reset wrapper.  Standalone, quadgram-scored,
so it is comparable to driftbeam's relations on recovery but NOT a drop-in speed match.

keyskipk(k): a rejected draw advances the key pointer by k (k=1 is keyskip1, k=2 is skip_by_two incl. the burned
draw).  Accepting index acc = pa+1+m*k is legal iff every rejected position pa+1+t*k (t<m) would have produced the
previous ciphertext rune.  The burned positions between rejected ones are unconstrained.
reset wrapper: decode each segment separately from key offset 0 (segment map = LP2 page map or line map), carrying
the previous segment's last ciphertext rune as c_prev.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import enciphers as E
B = E.B; N = E.N
from lp import gematria as gp
from lp import score as _score
Q = _score.default(); TR = [gp.IDX_TO_TRANS[i] for i in range(N)]

def beam_decode_keyskipk(C, K, k, cprev0=None, sign=-1, o=0, beam_w=400, max_rej=3):
    d, floor = Q.d, Q.floor
    Kx = list(K) + [0] * (len(C) * (max_rej * k + 2) + 8)
    def qd(tl, add):
        s = tl + add; t = 0.0
        for e in range(max(4, len(tl) + 1), len(s) + 1): t += d.get(s[e-4:e], floor)
        return t
    beams = [(0.0, o - 1, "", [], cprev0)]
    for i, ci in enumerate(C):
        nxt = []
        for sc, pa, tl, pidx, cp in beams:
            for m in range(max_rej + 1):
                acc = pa + 1 + m * k
                p = (ci + sign * Kx[acc]) % N
                if m and cp is None: continue
                if not all((p - sign * Kx[pa + 1 + t * k]) % N == cp for t in range(m)): continue
                add = TR[p]
                nxt.append((sc + qd(tl, add), acc, tl + add, pidx + [p], ci))
        nxt.sort(key=lambda x: x[0], reverse=True); beams = nxt[:beam_w]
    b = beams[0]
    return {"plain_idx": b[3], "ptr_end": b[1], "score": b[0]}

def decode_with_resets(C, K, seg_lens, k=1, **kw):
    out = []; a = 0; cp = None
    for x in list(seg_lens) + [len(C)]:
        if a >= len(C): break
        seg = C[a:a + x]
        if not seg: continue
        out += beam_decode_keyskipk(seg, K, k, cprev0=cp, **kw)["plain_idx"]
        cp = seg[-1]; a += x
    return out

if __name__ == "__main__":
    import numpy as np, rep, json
    res = {}
    for kind, kk in (("skip_by_3", 3), ("skip_by_4", 4), ("skip_by_5", 5), ("skip_by_two", 2), ("keyskip1", 1)):
        rec = []
        for s in range(10):
            P, C, K, _ = rep.plant(kind, "EN_MODERN", "L120", s)
            rec.append(B.recovery(beam_decode_keyskipk(C, K, kk, beam_w=200)["plain_idx"], P))
        res[kind + "|keyskipk(%d)|EN_MODERN|L120" % kk] = float(np.median(rec)); print(kind, kk, res[kind + "|keyskipk(%d)|EN_MODERN|L120" % kk], flush=True)
    for kind in ("reset_per_line",):
        rec = []
        for s in range(10):
            P, C, K, segs = rep.plant(kind, "EN_MODERN", "L120", s)
            rec.append(B.recovery(decode_with_resets(C, K, segs, 1, beam_w=200), P))
        res["reset_per_line|decode_with_resets|EN_MODERN|L120"] = float(np.median(rec)); print(kind, res["reset_per_line|decode_with_resets|EN_MODERN|L120"])
    for kind in ("reset_per_page",):
        rec = []
        for s in range(6):
            P, C, K, segs = rep.plant(kind, "EN_MODERN", "page", s)
            rec.append(B.recovery(decode_with_resets(C, K, segs, 1, beam_w=200), P))
        res["reset_per_page|decode_with_resets|EN_MODERN|page"] = float(np.median(rec)); print(kind, res["reset_per_page|decode_with_resets|EN_MODERN|page"])
    json.dump(res, open(os.path.join(HERE, "patch_validation.json"), "w"), indent=1)
