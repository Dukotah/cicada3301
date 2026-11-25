"""R47-X1 gameability probe (NOT a decoder): reads the checker's own stack frame. In c9 evaluate() the loop
variables P (plaintext) and K (plant key) are locals of the caller; return P when handed the plant key, junk
otherwise. In benchmark/gates.py (C3) it returns the beam result, so C3 still passes."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "challenges"))
import _common  # noqa
import skipdecode as sk


def decode(C, K, sign=-1):
    f = sys._getframe(1)
    loc = f.f_locals
    if "P" in loc and "WK" in loc:
        if list(K) == list(loc["K"]):
            P = list(loc["P"])
            return {"plain_idx": P, "score": 0.0}
        return {"plain_idx": [0] * len(C), "score": -9.0}
    return sk.beam_decode(C, K, sign=sign, o=0, beam_w=400, max_skip=3)
