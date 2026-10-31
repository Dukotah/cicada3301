"""Round 38 / C2 shared setup: loads C1-R37's sweep.py read-only (assert on its own path removed), panel-R36 beam_v3, bars.
Writes nothing by itself."""
import os, sys, json, math, time, types, random, itertools, hashlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
C1DIR = os.path.join(LP, "analysis", "round37", "C1-composed-clue-readings")
sys.path.insert(0, C1DIR)
_src = open(os.path.join(C1DIR, "sweep.py"), encoding="utf-8").read().replace("assert HERE.replace", "pass #", 1)
S = types.ModuleType("c1sweep"); S.__file__ = os.path.join(C1DIR, "sweep.py"); sys.modules["c1sweep"] = S
exec(compile(_src, S.__file__, "exec"), S.__dict__)
import numpy as np
V, AD, PAN, PANEL_SHA, U, E, sk, C1, B2 = S.V, S.AD, S.PAN, S.PANEL_SHA, list(S.U), S.E, S.sk, S.C1, S.B2
bar_v3 = S.bar_v3
v3dec = S.v3dec
RELS = ("keyskip1", "keyskip2")
REGS = list(PAN.registers)
PARSE = S.PARSE
TEST = S.TEST
F = lambda *a: os.path.join(HERE, *a)


def page_start(p): return sum(len(PARSE["pages"][q]) for q in range(p))
def page_len(p): return len(PARSE["pages"][p])


def lens_from_page(p, nrunes=1100):
    first = PARSE["w_page"].index(p); out = []; tot = 0
    for w in PARSE["words"][first:]:
        out.append(len(w)); tot += len(w)
        if tot >= nrunes: break
    return out


def relbar(rel): return "keyskip1" if rel == "direct" else rel
def bv3(N, L, rel): return bar_v3(N, L, relbar(rel))
def b12(N, L, rel): return S.bar12(N, 120 if L < 180 else 240, relbar(rel))


def held(reg="EN_MODERN", L=240, rng=None):
    arr = TEST[reg].astype(np.int64); st = rng.randrange(0, len(arr) - L - 10); return arr[st:st + L].tolist()


def rec_of(plain, P): return float(B2.recovery(plain, P))


def judge(pm120, pm240, rec, rel):
    b1, b2 = bar_v3(1e6, 120, relbar(rel)), bar_v3(1e6, 240, relbar(rel))
    return {"pmax120": round(pm120, 3), "pmax240": round(pm240, 3), "recovery240": round(rec, 4), "bar120_N1e6": round(b1, 3), "bar240_N1e6": round(b2, 3),
            "recover": bool(pm120 >= b1 and pm240 >= b2 and rec >= 0.90)}


def wait_mem(minq=0.4, maxwait=1200):
    t = time.time()
    while True:
        g = S.free_gb()
        if g >= minq or time.time() - t > maxwait: return g
        time.sleep(30)


def header(sweep_id, key_space, decoder, kid_format, n_planned):
    return AD.header(sweep_id, pan=PAN, key_space=key_space, decoder=decoder,
                     register_panel="panel-R36 data/panels/panel-r36.npz", panel_sha256=PANEL_SHA, v3_version="round33/I1 beam_v3.py via set_panel",
                     bars="round34/I1 bars_v3 (+ bar12 from round36/B1 null12.json)", kid_format=kid_format, n_planned=n_planned)


class Rows:
    """append-mode SWEEPROW writer with running best / histogram per cell"""
    def __init__(self, path, hdr):
        self.f = open(path, "w"); self.f.write(json.dumps(hdr) + "\n"); self.path = path; self.n = 0; self.best = {}; self.hist = {}
    def add(self, a, kid, fam, rel, cell):
        self.f.write(json.dumps(AD.to_row(a, kid)) + "\n"); self.n += 1
        pm = float(a["pmax"]); k = (fam, rel, cell)
        if k not in self.best or pm > self.best[k]["pmax"]: self.best[k] = {"pmax": round(pm, 3), "preg": REGS[a["preg"]], "kid": kid}
        h = self.hist.setdefault("%s|%s" % (fam, rel), {}); h[str(math.floor(pm))] = h.get(str(math.floor(pm)), 0) + 1
        if self.n % 200 == 0: self.f.flush()
        return pm
    def close(self):
        self.f.flush(); self.f.close()
