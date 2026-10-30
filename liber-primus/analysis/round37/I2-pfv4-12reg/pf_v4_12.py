"""R37 I2 pf_v4_12 -- pf_v4 skip-tolerant Viterbi head statistic with the final lse over the TWELVE panel-R36 LMs.
Same prefilter_mask signature as round35 pf_v4. Frozen point read from frozen_op12.json."""
import os, sys, json, hashlib
import numpy as np
sys.dont_write_bytecode = True
import importlib.util as _u
_d = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(_d, "..", "..", ".."))
_s = _u.spec_from_file_location("pf_v4_r35", os.path.join(LP, "analysis", "round35", "I1-skip-tolerant-screen", "pf_v4.py"))
pf_v4 = _u.module_from_spec(_s); _s.loader.exec_module(pf_v4)
heads, LN10, LN29 = pf_v4.heads, pf_v4.LN10, pf_v4.LN29
PANEL_PATH = os.path.join(LP, "data", "panels", "panel-r36.npz")
PANEL_SHA = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
assert hashlib.sha256(open(PANEL_PATH, "rb").read()).hexdigest() == PANEL_SHA
_z = np.load(PANEL_PATH, allow_pickle=False)
REGS = [str(s) for s in _z["registers"]]; assert len(REGS) == 12
LMT = np.ascontiguousarray(_z["LM"].reshape(12, -1).astype(np.float32).T)      # (29^3, 12)


def dp_regs(Chead, K, k, a, pen, ms=(24,), chunk=16384):
    return pf_v4.dp_regs(Chead, K, LMT, k, a, pen, ms, chunk)


lse_from_regs = pf_v4.lse_from_regs


def dp_cols(Cc, K, k, a, pen, m=24):
    """Per-column ciphertext head Cc (m,B), keystream K (>=m+a*k, B) -> (B,) lse over 12 registers (plants)."""
    pl = pen / LN10
    st = [(b, c) for b in range(k + 1) for c in range(b, k + 1)]
    D = [[((Cc[t].astype(np.int32) - K[t + a * s].astype(np.int32)) % 29) for s in range(k + 1)] for t in range(m)]
    V = {(b, c): LMT[D[0][0] * 841 + D[1][b] * 29 + D[2][c]] - np.float32(pl * c) for (b, c) in st}
    for t in range(1, m - 2):
        Vn = {}
        for (b, c) in st:
            best = None
            for a_ in range(b + 1):
                x = V[(a_, b)] + LMT[D[t][a_] * 841 + D[t + 1][b] * 29 + D[t + 2][c]]
                best = x if best is None else np.maximum(best, x)
            Vn[(b, c)] = best - np.float32(pl * (c - b))
        V = Vn
    f = None
    for v in V.values(): f = v if f is None else np.maximum(f, v)
    return lse_from_regs(f.astype(np.float64), m)


_fp = os.path.join(_d, "frozen_op12.json")
FROZEN = json.load(open(_fp)) if os.path.exists(_fp) else {}


def prefilter_mask(seeds, variant, Chead, m=None, rel=None):
    m = m or FROZEN["m"]; rel = rel or FROZEN.get("rel", "both"); k = FROZEN["k"]
    K = heads(seeds, m + 2 * k, variant)
    mask = np.zeros(len(seeds), bool)
    for a in ((1, 2) if rel == "both" else ((1,) if rel == "keyskip1" else (2,))):
        R = dp_regs(Chead, K[:m + a * k], k, a, FROZEN["pen_a%d" % a], ms=(m,))
        mask |= lse_from_regs(R[m], m) > FROZEN["thr"]["a%d" % a]
    return mask
