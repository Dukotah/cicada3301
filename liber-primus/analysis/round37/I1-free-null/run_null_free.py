"""Round 37 / I1 -- free-relation null + control under panel-R36.  One process.
usage: python run_null_free.py time | control L nseeds | null L ndraws allot_s | o3 | fit
Streams to null_free_stream.jsonl / control_free_stream.jsonl.  See PREREG.md."""
import sys, os, json, time, random, math, ctypes
sys.dont_write_bytecode = True
LANE = os.path.dirname(os.path.abspath(__file__))
HERE = LANE
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R34 = os.path.join(LP, "analysis", "round34", "I1-v3-null")
sys.path.insert(0, R34)
from common34 import *            # imports beam_v3 as V, AD, B2, C1, TEST (R32 testhalves) ...
HERE = LANE
PANEL_R36 = os.path.join(LP, "data", "panels", "panel-r36.npz")
V.PANEL_PATH = PANEL_R36
V._PAN = None
PAN = V.panel()
assert len(PAN.registers) == 12, PAN.registers
TH = np.load(os.path.join(LP, "data", "panels", "testhalves-r36.npz"))
U = list(C1.U)
F = lambda n: os.path.join(LANE, n)
kl = lambda L: 41 * L + 64


class MS(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("ml", ctypes.c_ulong), ("tp", ctypes.c_ulonglong), ("ap", ctypes.c_ulonglong),
                ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong), ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ae", ctypes.c_ulonglong)]
def freegb():
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return m.ap / 2 ** 30
def memwait():
    t = time.time()
    while freegb() < 0.4:
        if time.time() - t > 1200: raise SystemExit("mem wait >20min")
        time.sleep(30)

def pm_of(xs):
    """pmax under panel-R36 for a list of decodes (grouped by equal length)."""
    out = [None] * len(xs); ls = {}
    for i, x in enumerate(xs): ls.setdefault(len(x), []).append(i)
    for ln, ii in ls.items():
        r = AD.adjudicate_batch(np.asarray([xs[i] for i in ii], dtype=np.int64), pan=PAN)["pmax"]
        for i, v in zip(ii, r.tolist()): out[i] = round(float(v), 4)
    return out

def draw_C(L, k):
    s = U[:]; random.Random(3301 + k).shuffle(s); return s[:L]

def null(L, ndraws, allot, start=0, tag="null"):
    by = survivor_seeds(); rng = random.Random(3301 + L * 7 + start)
    out = open(F("null_free_stream.jsonl"), "a"); t0 = time.time(); buf = []; done = 0; i0 = start
    def flush():
        nonlocal buf, i0
        if buf:
            pm = pm_of(buf); out.write(json.dumps({"L": L, "i0": i0, "pm": pm}) + "\n"); out.flush(); i0 += len(buf); buf = []
    while done < ndraws and time.time() - t0 < allot:
        if done % 50 == 0: memwait()
        C = draw_C(L, start + done); st, fm = FAMS[(start + done) % len(FAMS)]
        K = keystream(st, fm, rng.choice(by[(st, fm)]), kl(L))
        d = V.beam_decode_v3(C, K, "free", "panel_max", tau=0.0, lam_u=4.0)
        buf.append(d["plain_idx"]); done += 1
        if len(buf) >= 100: flush()
    flush()
    print("null L=%d draws %d in %.0fs (%.2f/s)" % (L, done, time.time() - t0, done / max(1e-9, time.time() - t0)), flush=True)

def control(L, nseeds, regs=None, tag=""):
    K = B2.sha_ctr_key(kl(L)); out = open(F("control_free_stream.jsonl"), "a"); t0 = time.time()
    for reg in (regs or list(PAN.registers)):
        a = TH[reg].astype(np.int64)
        for s in range(nseeds):
            memwait() if s % 10 == 0 else None
            r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1); P = a[st:st + L].tolist()
            C, info = B2.ENCIPHER["free_q05"](P, K, 0.83, 3301 + s)
            d = V.beam_decode_v3(C, K, "free", "panel_max", tau=0.0, lam_u=4.0)
            x = d["plain_idx"]; pm = pm_of([x])[0]
            out.write(json.dumps({"L": L, "register": reg, "seed": s, "pmax": pm, "rec": round(float(B2.recovery(x, P)), 4), "len": len(x)}) + "\n")
        out.flush()
        print("control L=%d %s %.0fs" % (L, reg, time.time() - t0), flush=True)

if __name__ == "__main__":
    m = sys.argv[1]
    if m == "time":
        for L in (240, 400, 729):
            t = time.time(); null(L, 50, 1e9); print("   cost L=%d: %.2f s/draw" % (L, (time.time() - t) / 50), flush=True)
    elif m == "null":
        null(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), start=int(sys.argv[5]) if len(sys.argv) > 5 else 0)
    elif m == "control":
        control(int(sys.argv[2]), int(sys.argv[3]))
