"""R34 B1 shared setup (imports only; writes nothing outside this directory)."""
import os, sys, re, json, time, random, math, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32 = os.path.join(LP, "analysis", "round32")
R34 = os.path.join(LP, "analysis", "round34")
I1D = os.path.join(LP, "analysis", "round33", "I1-register-aware-beam")
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m
    sp.loader.exec_module(m)
    return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R32, "B2-php-mtrand"))
C2 = _load("b2common", os.path.join(R32, "B2-php-mtrand", "common.py"))
sys.path.insert(0, I1D)
import beam_v3 as V                                  # noqa: E402
sys.path.insert(0, os.path.join(R34, "I2-novowel-prefilter"))
import pf_v3                                         # noqa: E402
sys.path.insert(0, os.path.join(R34, "I1-v3-null"))
from bars_v3 import bar_v3                           # noqa: E402
AD = C1.AD
B2 = V.B2
PM = C2.PM_
PAN = V.panel()
LMT = PAN.LMT.astype(np.float32)
TEST = np.load(os.path.join(R32, "I2-multiregister-readjudication", "models", "testhalves.npz"))
U = C1.U
L_SCREEN, L_HIT = 120, 240
C_SCREEN, C_HIT = U[:L_SCREEN], U[:L_HIT]
NEED = 1024
ADV = {"keyskip1": 1, "keyskip2": 2}
RELS = ("keyskip2", "keyskip1")
M_PF = pf_v3.M_DEFAULT
THR = pf_v3.FROZEN[M_PF]
N_DECL = 10 ** 6
KEEP = 6.0
PHP_CELLS = [(tw, rd) for tw in ("mt", "php") for rd in ("scale", "mod")]
cname = lambda c: "%s_%s" % c


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    a = AD.adjudicate(d["plain_idx"])
    return d, a
