"""C1 shared setup: panel-R36 beam_v3, planted encipherers' common bits. Writes nothing."""
import os, sys, json, time, math, random, hashlib, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
AN = lambda *a: os.path.join(LP, "analysis", *a)
import numpy as np
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m
sys.path.insert(0, AN("round32", "B1-bash-random"))
C1 = _load("b1common", AN("round32", "B1-bash-random", "common.py"))
sys.path.insert(0, AN("round33", "I1-register-aware-beam"))
import beam_v3 as V
PANEL_PATH = os.path.join(LP, "data", "panels", "panel-r36.npz")
PANEL_SHA = hashlib.sha256(open(PANEL_PATH, "rb").read()).hexdigest()
assert PANEL_SHA == "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
V.set_panel(PANEL_PATH)
AD = C1.AD
PAN = AD.Panel(PANEL_PATH); AD._PANEL = PAN; V._PAN = PAN
assert len(PAN.registers) == 12
sys.path.insert(0, AN("round34", "I1-v3-null"))
from bars_v3 import bar_v3
sk = C1.sk; B2 = V.B2
U = list(C1.U)
ADV = {"keyskip1": 1, "keyskip2": 2}; RELS = ("keyskip1", "keyskip2")

def v3dec(C, K, rel, sign=-1, o=0):
    d = V.beam_decode_v3(list(C), K, ADV[rel], "panel_max", sign=sign, o=o, tau=0.0, lam_u=4.0)
    return d, AD.adjudicate(d["plain_idx"])

def free_gb():
    import subprocess
    try:
        return float(subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB"], capture_output=True, text=True, timeout=30).stdout.strip())
    except Exception:
        return 9.9

def wait_mem(minq=0.4, maxwait=1800):
    t = time.time()
    while True:
        g = free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        time.sleep(60)
sys.path.insert(0, AN("round10", "L2-map"))
