"""Round 34 / I1 shared setup (imports only; writes nothing outside this directory)."""
import os, sys, re, json, time, random, importlib.util
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R32 = os.path.join(LP, "analysis", "round32")
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
import beam_v3 as V                      # noqa: E402
AD = C1.AD
B2 = V.B2
PAN = V.panel()
TEST = np.load(os.path.join(R32, "I2-multiregister-readjudication", "models", "testhalves.npz"))
FAMS = [("B1", "bash4.2"), ("B1", "bash4.2_i32")] + [("B2", c) for c in ("mt_scale", "mt_mod", "php_scale", "php_mod")]
OUT = lambda f: os.path.join(HERE, f)


def keystream(store, fam, seed, n):
    if store == "B1":
        return C1.ks(seed, fam, n)
    tw, rd = fam.split("_")
    return C2.ks(seed, (tw, rd), n)


def survivor_seeds():
    """keyskip1 survivor seeds per (store, family), same universe as B3 readjud.load_universe (kid = store:family:seed:rel)."""
    by = {}
    pat = re.compile(r'^\["([^"]+)"')
    for store, d in (("B1", "B1-bash-random"), ("B2", "B2-php-mtrand")):
        with open(os.path.join(R32, d, "sweep_rows.jsonl"), encoding="utf-8") as f:
            f.readline()
            for line in f:
                m = pat.search(line[:200])
                if not m:
                    continue
                p = m.group(1).split(":")
                if p[3] == "keyskip1":
                    by.setdefault((store, p[1]), []).append(int(p[2]))
    return by


def keylen(L):
    return max(1024, 6 * L + 64)
