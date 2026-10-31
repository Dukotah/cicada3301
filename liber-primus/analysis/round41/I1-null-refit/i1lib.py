"""R41 I1 shared setup: the real chunk path (pf_v4_12 frozen + beam_v3 panel_max under panel-R36), six generator families."""
import os, sys, json, time, math, random, hashlib, importlib.util, subprocess
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AN = os.path.join(LP, "analysis")
R32, R33, R34, R35, R36, R37 = [os.path.join(AN, "round%d" % r) for r in (32, 33, 34, 35, 36, 37)]
import numpy as np


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


sys.path.insert(0, os.path.join(R32, "B1-bash-random"))
C1 = _load("b1common", os.path.join(R32, "B1-bash-random", "common.py"))
sys.path.insert(0, os.path.join(R33, "I1-register-aware-beam"))
import beam_v3 as V
sys.path.insert(0, os.path.join(R37, "I2-pfv4-12reg"))
import pf_v4_12 as PF
PM = _load("php_mt", os.path.join(R32, "B2-php-mtrand", "php_mt.py"))
P12_PATH = os.path.join(LP, "data", "panels", "panel-r36.npz"); P12_SHA = PF.PANEL_SHA
assert hashlib.sha256(open(P12_PATH, "rb").read()).hexdigest() == P12_SHA
AD = C1.AD; B2 = V.B2; U = list(C1.U)
V.set_panel(P12_PATH); PAN = AD.Panel(P12_PATH); AD._PANEL = PAN; V._PAN = PAN
assert V.A is AD and len(PAN.registers) == 12 and V.panel() is PAN
REGS = list(PAN.registers)
TEST = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip1", "keyskip2")
FAMILIES = ("bash4.2", "bash4.2_i32", "mt_scale", "mt_mod", "php_scale", "php_mod")
FR = PF.FROZEN; M_PF, K_PF = FR["m"], FR["k"]
SEC0, SEC1 = 1325376000, 1401580800
PREF = list(range(SEC0 >> 20, (SEC1 >> 20) + 1)); assert len(PREF) == 74
F = lambda n: os.path.join(HERE, n)
T0 = time.time()


def log(*a):
    s = "[%6.0fs] " % (time.time() - T0) + " ".join(str(x) for x in a); print(s, flush=True)
    with open(F("run.log"), "a") as f: f.write(s + "\n")


def free_gb():
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"], capture_output=True, text=True, timeout=30).stdout
        return float(o.strip())
    except Exception:
        return 9.9


def wait_mem(minq=0.4, maxwait=1200):
    t = time.time()
    while True:
        g = free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        log("RAM wait: free %.2f GB" % g); time.sleep(60)


def seeds_for(fam, rng, n):
    if fam.startswith("bash"):
        pre = np.asarray(PREF, dtype=np.uint64)[rng.integers(0, len(PREF), n)]
        return (pre << np.uint64(20)) | rng.integers(0, 1 << 20, n).astype(np.uint64)
    return rng.integers(0, 1 << 32, n, dtype=np.uint64)


def heads_K(seeds, fam, m):
    """(m, B) int8 keystream heads."""
    if fam.startswith("bash"): return PF.heads(seeds, m, fam)
    tw, rd = {"mt_scale": ("mt", "scale"), "mt_mod": ("mt", "mod"), "php_scale": ("php", "scale"), "php_mod": ("php", "mod")}[fam]
    return PM.reduce_heads(PM.heads_all(seeds, m)[tw], rd)


def pass_mask(seeds, fam, Chead=None):
    """pf_v4_12 frozen point, rel=both, any key family (same arithmetic as pf_v4_12.prefilter_mask)."""
    m, k = M_PF, K_PF
    Chead = np.array(U[:m] if Chead is None else Chead[:m], dtype=np.int8)
    K = heads_K(seeds, fam, m + 2 * k); mask = np.zeros(len(seeds), bool)
    for a in (1, 2):
        R = PF.dp_regs(Chead, K[:m + a * k], k, a, FR["pen_a%d" % a], ms=(m,))
        mask |= PF.lse_from_regs(R[m], m) > FR["thr"]["a%d" % a]
    return mask


def ks_full(fam, seed, n=1024):
    if fam.startswith("bash"): return C1.ks(int(seed), fam, n)
    tw, rd = {"mt_scale": ("mt", "scale"), "mt_mod": ("mt", "mod"), "php_scale": ("php", "scale"), "php_mod": ("php", "mod")}[fam]
    return PM.ks(int(seed), tw, rd, n)


def v3dec(C, K, rel):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])
