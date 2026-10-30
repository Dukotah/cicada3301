"""R35 I1 pf_v4 -- skip-tolerant head screen. Same prefilter_mask signature as round34 pf_v3 (extra optional rel=)."""
import os, sys
import numpy as np
sys.dont_write_bytecode = True
import importlib.util as _u
_d = os.path.dirname(os.path.abspath(__file__))
_p = os.path.join(_d, "..", "..", "round34", "I2-novowel-prefilter", "pf_v3.py")
_s = _u.spec_from_file_location("pf_v3_r34", _p); pf_v3 = _u.module_from_spec(_s); _s.loader.exec_module(pf_v3)
heads = pf_v3.heads
LN10 = np.log(10.0); LN29 = np.log(29.0)

def dp_regs(Chead, K, LMT, k, a, pen, ms=(20, 24), chunk=16384):
    """Per-register Viterbi. Chead (>=max(ms),), K (L,B) int8 keystream heads, L >= max(ms)+a*k.
    Returns {m: (B,9) float64 best-path trigram log10 sum (penalty pen nats/skip applied)}."""
    C = np.asarray(Chead, dtype=np.int32); mmax = max(ms); B = K.shape[1]
    pl = pen / LN10
    st = [(b, c) for b in range(k + 1) for c in range(b, k + 1)]
    out = {m: np.empty((B, LMT.shape[1]), np.float64) for m in ms}
    for i0 in range(0, B, chunk):
        Kc = K[:, i0:i0 + chunk].astype(np.int32)
        D = [[(C[t] - Kc[t + a * s]) % 29 for s in range(k + 1)] for t in range(mmax)]
        V = {}
        for (b, c) in st:
            V[(b, c)] = LMT[D[0][0] * 841 + D[1][b] * 29 + D[2][c]] - np.float32(pl * c)
        for t in range(1, mmax - 2):
            # state after trigram t-1 is (s_t, s_t+1); now add trigram t
            Vn = {}
            for (b, c) in st:
                best = None
                for a_ in range(b + 1):
                    x = V[(a_, b)] + LMT[D[t][a_] * 841 + D[t + 1][b] * 29 + D[t + 2][c]]
                    best = x if best is None else np.maximum(best, x)
                Vn[(b, c)] = best - np.float32(pl * (c - b))
            V = Vn
            m_here = t + 3
            if m_here in ms:
                f = None
                for v in V.values(): f = v if f is None else np.maximum(f, v)
                out[m_here][i0:i0 + chunk] = f
    return out

def lse_from_regs(R, m):
    llr = R * LN10 + (m - 2) * LN29
    mx = llr.max(1)
    return mx + np.log(np.exp(llr - mx[:, None]).sum(1))

def lse_v4(Chead, K, LMT, k, a, pen, ms=(20, 24)):
    R = dp_regs(Chead, K, LMT, k, a, pen, ms)
    return {m: lse_from_regs(R[m], m) for m in ms}

# ---- frozen operating point: filled in by run.py (frozen_op.json) ----
import json
_fp = os.path.join(_d, "frozen_op.json")
FROZEN = json.load(open(_fp)) if os.path.exists(_fp) else {}
M_DEFAULT = FROZEN.get("m", 20)

def prefilter_mask(seeds, variant, Chead, LMT, m=None, rel=None):
    """Drop-in for pf_v3.prefilter_mask. seeds -> boolean survivor mask. rel in {'keyskip1','keyskip2','both'}."""
    m = m or FROZEN["m"]; rel = rel or FROZEN.get("rel", "both")
    k, pen = FROZEN["k"], FROZEN["pen"]
    K = heads(seeds, m + 2 * k, variant)
    mask = np.zeros(len(seeds), bool)
    for a in ((1, 2) if rel == "both" else ((1,) if rel == "keyskip1" else (2,))):
        thr = FROZEN["thr"]["a%d" % a]
        L = m + a * k
        s = lse_v4(Chead, K[:L], LMT, k, a, FROZEN["pen_a%d" % a], ms=(m,))[m]
        mask |= s > thr
    return mask
