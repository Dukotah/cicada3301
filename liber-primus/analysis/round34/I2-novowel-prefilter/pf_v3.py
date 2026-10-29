"""R34 I2 pf_v3 -- drop-in for round32/B1 pf.py (same heads/ioc_stat/tri_stat signatures) plus lse_stat/screen."""
import os, sys
import numpy as np
sys.dont_write_bytecode = True
import importlib.util as _u
_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "round32", "B1-bash-random", "pf.py")
_s = _u.spec_from_file_location("pf_r32", _p)
_m = _u.module_from_spec(_s); _s.loader.exec_module(_m)
heads, ioc_stat, tri_stat = _m.heads, _m.ioc_stat, _m.tri_stat
LN10 = np.log(10.0)

def lse_stat(P, LMT):
    """P (m,B) int8 plaintext idx -> (B,) log-sum-exp over the nine registers of the head LLR vs uniform (nats)."""
    m = P.shape[0]
    acc = tri_stat(P, LMT)
    llr = acc.astype(np.float64) * LN10 + (m - 2) * np.log(29.0)
    mx = llr.max(1)
    return mx + np.log(np.exp(llr - mx[:, None]).sum(1))

def screen(P, LMT, thr):
    """Boolean pass mask for plaintext heads P (m,B) (m = P.shape[0]); thr from frozen_op.json for that m."""
    return lse_stat(P, LMT) > thr

# ---- frozen operating point (roc.json, stat=lse, FPR target 1e-3, pooled over bash LP64/ILP32 + 4 PHP cells) ----
FROZEN = {16: 5.597248442103894, 20: 3.9053751767817753}   # lse threshold (nats) per head length
M_DEFAULT = 20

def prefilter_mask(seeds, variant, Chead, LMT, m=M_DEFAULT):
    """Drop-in for B1 prefilter_scores: bash seeds -> boolean survivor mask. Chead = real ciphertext head (>= m runes)."""
    K = heads(seeds, m, variant)
    P = (np.asarray(Chead[:m], dtype=np.int8)[:, None] - K) % 29
    return screen(P, LMT, FROZEN[m])
