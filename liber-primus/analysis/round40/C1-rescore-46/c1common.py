"""R40 C1 common: lib.py (= round37/C3 rescore.py machinery, repointed to this dir) + degenerate-flag rows + pf_v4_12 head screen engine."""
import os, sys, json, math, random, time, importlib.util
sys.dont_write_bytecode = True
HERE0 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE0)
import lib
from lib import *          # noqa
from lib import _load
import numpy as np
# ---- 14-field rows with the degenerate flag everywhere
_orig_to_row = AD.to_row
AD.to_row = lambda res, kid, with_degenerate=True: _orig_to_row(res, kid, with_degenerate=True)
_orig_header = AD.header
AD.header = lambda sweep_id, pan=None, with_degenerate=True, **kw: _orig_header(sweep_id, pan=pan, with_degenerate=True, **kw)
# ---- pf_v4_12 (round37/I2)
sys.path.insert(0, os.path.join(R(37), "I2-pfv4-12reg"))
import pf_v4_12 as PF
FR = PF.FROZEN
assert FR["m"] == 24 and FR["k"] == 2

def screen(Chead, Kx):
    """Chead (>=24,), Kx (>=28, B) int8 (plain = C - Kx). Returns bool mask: pf_v4_12 frozen point, rel both."""
    m = 24; K = np.ascontiguousarray(Kx[:m + 4]).astype(np.int8); mask = np.zeros(K.shape[1], bool)
    for a in (1, 2):
        R_ = PF.dp_regs(np.asarray(Chead[:m]), K[:m + a * 2], 2, a, FR["pen_a%d" % a], ms=(m,))
        mask |= PF.lse_from_regs(R_[m], m) > FR["thr"]["a%d" % a]
    return mask

def screen_rel(Chead, Kx):
    m = 24; K = np.ascontiguousarray(Kx[:m + 4]).astype(np.int8); out = {}
    for a in (1, 2):
        R_ = PF.dp_regs(np.asarray(Chead[:m]), K[:m + a * 2], 2, a, FR["pen_a%d" % a], ms=(m,))
        out["keyskip%d" % a] = PF.lse_from_regs(R_[m], m) > FR["thr"]["a%d" % a]
    return out

def deg_thr():
    return degenerate_thresholds()
