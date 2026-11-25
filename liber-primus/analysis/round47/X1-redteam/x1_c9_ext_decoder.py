"""R47-X1: an extended-relation beam for C9 (probe of whether V-BACK / V-NULL are representational gaps).

Same design as skipdecode.beam_decode (position-synchronous over ciphertext, English quadgram score,
deterministic doublet-consistency constraints), with two extra transitions:
  BACK : p = c - K[j-1] (reuse the previous key symbol), allowed iff p + K[j] == c_prev (the forward try
         would have doubled); the pointer stays at j.
  NULL : emit nothing for this ciphertext rune, consume K[j], allowed iff the NEXT rune decoded with K[j+1]
         would have doubled under K[j] (p_next + K[j] == c_prev).
Each non-normal transition costs PEN (log10); NULL also pays the mean quadgram cost it skips.
Returns the better (by recomputed English score) of this beam and the C3 reference beam, so C3 behaviour is kept.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "challenges"))
import _heavy as H  # noqa: E402
import skipdecode as sk  # noqa: E402
from lp import gematria as gp  # noqa: E402

N = H.N
Q = H.Q
TR = [gp.IDX_TO_TRANS[i] for i in range(N)]
W = int(os.environ.get("X1_W", "200"))
PEN = float(os.environ.get("X1_PEN", "2.0"))
NULLCOST = float(os.environ.get("X1_NC", "4.2"))


def _delta(tail, add):
    t = tail + add
    s = 0.0
    for i in range(max(0, len(tail) - 3), len(t) - 3):
        s += Q.d.get(t[i:i + 4], Q.floor)
    return s, t[-3:]


def ext_beam(C, K, max_skip=3):
    Kx = list(K) + [0] * (len(C) * 5 + 8)
    p0 = (C[0] - Kx[0]) % N
    beams = [(0.0, 1, TR[p0][-3:], (p0,))]          # (score, next key index j, tail, out)
    for t in range(1, len(C)):
        c, cp = C[t], C[t - 1]
        nxt = []
        for sc, j, tail, out in beams:
            for s in range(0, max_skip + 1):         # normal (s=0) and keyskip s
                acc = j + s
                p = (c - Kx[acc]) % N
                if any((p + Kx[m]) % N != cp for m in range(j, acc)):
                    continue
                d, nt = _delta(tail, TR[p])
                nxt.append((sc + d - (PEN if s else 0), acc + 1, nt, out + (p,)))
            if j >= 1:                                # BACK
                p = (c - Kx[j - 1]) % N
                if (p + Kx[j]) % N == cp:
                    d, nt = _delta(tail, TR[p])
                    nxt.append((sc + d - PEN, j, nt, out + (p,)))
            if t + 1 < len(C):                        # NULL
                pn = (C[t + 1] - Kx[j + 1]) % N
                if (pn + Kx[j]) % N == cp:
                    nxt.append((sc - NULLCOST - PEN, j + 1, tail, out))
        nxt.sort(key=lambda x: -x[0])
        seen, beams = set(), []
        for st in nxt:
            k = (st[1], st[2], len(st[3]))
            if k in seen:
                continue
            seen.add(k)
            beams.append(st)
            if len(beams) >= W:
                break
    return list(max(beams, key=lambda x: x[0])[3])


def decode(C, K, sign=-1):
    assert sign == -1
    a = ext_beam(list(C), list(K))
    b = sk.beam_decode(list(C), list(K), sign=sign, o=0, beam_w=400, max_skip=3)["plain_idx"]
    best = a if H.english_score(a) >= H.english_score(b) else b
    return {"plain_idx": best, "score": H.english_score(best), "translit": sk.idx_to_trans(best)}
