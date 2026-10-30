import os, sys, json, time, math, random, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AN = os.path.join(LP, "analysis"); R = lambda n: os.path.join(AN, "round%d" % n)
import numpy as np
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m
sys.path.insert(0, os.path.join(R(32), "B1-bash-random"))
C1 = _load("b1common", os.path.join(R(32), "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R(33), "I1-register-aware-beam"))
import beam_v3 as V
AD = C1.AD; B2 = V.B2; U = list(C1.U); NC = C1.nc
P12_PATH = os.path.join(R(36), "P1-panel-r36", "build1", "panel12.npz")
TH12_PATH = os.path.join(R(36), "P1-panel-r36", "build1", "testhalves12.npz")
PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN; V.PANEL_PATH = P12_PATH
REGS = list(PAN.registers); assert len(REGS) == 12
TEST = np.load(TH12_PATH)
NULL12 = json.load(open(os.path.join(R(36), "B1-orbit-12reg", "null12.json")))["cells"]
RELS = ("keyskip1", "keyskip2"); ADV = {"keyskip1": 1, "keyskip2": 2}; N = 29
F = lambda *a: os.path.join(HERE, *a)
def bar12(Nn, L, rel, alpha=0.01):
    c = NULL12["L%d|%s" % (L, rel)]; return c["mu"] + c["beta"] * math.log(float(Nn) / -math.log1p(-alpha))
SEGS = NC.segments()[:-2]
PAGE_START = [0]
for _s in SEGS: PAGE_START.append(PAGE_START[-1] + len(_s))
STARTS = [PAGE_START[p] for p in (0, 10, 20, 30, 40, 50)]
DOUBLET_TARGET = 86
def dfshuffle(seq, rng, target=DOUBLET_TARGET):
    x = list(seq); rng.shuffle(x); n = len(x)
    bad = [i for i in range(n - 1) if x[i] == x[i + 1]]; cnt = len(bad)
    for i in bad:
        if cnt <= target: break
        if x[i] != x[i + 1]: continue
        for _ in range(40):
            j = rng.randrange(2, n - 2)
            if abs(j - i) < 3: continue
            a, b = x[i + 1], x[j]
            if b != x[i] and b != x[i + 2] and a != x[j - 1] and a != x[j + 1] and a != b:
                x[i + 1], x[j] = b, a; cnt -= 1; break
    return x
TF = (("v_prime", NC.v_prime), ("v_prime_index", NC.v_prime_index), ("v_totient", NC.v_totient))
def x4_cfgs(S):
    """the family's derivation: K = f(stream) mod 29 per letter; letters = stream or atbash(stream); sign -1/+1"""
    out = []
    for tn, tf in TF:
        ks = [v % N for v in tf(S)]
        for vn, letters in (("none", list(S)), ("atbash_pre", [(N - 1 - c) % N for c in S])):
            for sg in (-1, 1): out.append(("X4_%s_%s_sign%+d" % (tn, vn, sg), letters, ks, sg))
    return out
def dec(Cw, Kw, rel, sg):
    return V.beam_decode_v3(list(Cw), list(Kw), ADV[rel], "panel_max", tau=0.0, lam_u=4.0, sign=sg)
def window(C, K, s, L):
    Kw = K[s:s + 1024] if len(K) >= s + 1024 else list(K[s:]) + [0] * (s + 1024 - len(K))
    return C[s:s + L], Kw
