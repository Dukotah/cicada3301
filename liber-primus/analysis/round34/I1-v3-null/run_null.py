"""Round 34 / I1 null runner.  One process.  python run_null.py [total_budget_s]
Streams rows to null_stream.jsonl ({"cell":..., "pm":[...]}) every 200 draws."""
import sys
from common34 import *

BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 4300.0
T0 = time.time()
LOGF = open(OUT("run_null.log"), "a")
def log(*a):
    s = "[%6.0fs] " % (time.time() - T0) + " ".join(str(x) for x in a)
    print(s, flush=True); LOGF.write(s + "\n"); LOGF.flush()

U = list(C1.U)
REG4 = ["EN_NOVOWEL", "LATIN", "OE", "DE"]
ADV = {"keyskip1": 1, "keyskip2": 2, "free": "free"}
# (family, source, L, relations, draws target, wall allotment s)
PLAN = [
    ("lp2", None, 120, ("keyskip1", "keyskip2"), 40000, 900),
    ("lp2", None, 240, ("keyskip1", "keyskip2"), 6000, 800),
    ("lp2", None, 400, ("keyskip1", "keyskip2"), 1200, 520),
    ("lp2", None, 120, ("free",), 1000, 420),
] + [("register", r, L, ("keyskip1", "keyskip2"), n, w) for (L, n, w) in ((120, 3000, 130), (240, 500, 85), (400, 200, 90), (31, 3000, 50)) for r in REG4] \
  + [("lp2", None, 31, ("keyskip1", "keyskip2"), 40000, 450)]
# per-register allotments sum: 4*(130+85+90+50)=1420 -> total plan ~4900 > cap; global deadline trims the tail
OUTF = open(OUT("null_stream.jsonl"), "a")


def draw_C(fam, src, L, k):
    if fam == "lp2":
        s = U[:]
        random.Random(3301 + k).shuffle(s)
        return s[:L]
    a = TEST[src].astype(np.int64)
    return a[np.random.default_rng(3301 + k).choice(len(a), L, replace=False)].tolist()


def adj_batch(rows):
    X = np.asarray(rows, dtype=np.int64)
    return AD.adjudicate_batch(X)["pmax"].tolist()


def main():
    by = survivor_seeds()
    log("seeds", {k: len(v) for k, v in by.items()})
    # equality check batch vs full adjudicate
    chk = [random.Random(i).sample(range(29), 29) * 4 for i in range(3)]
    chk = [c[:120] for c in chk]
    full = [float(AD.adjudicate(c)["pmax"]) for c in chk]
    bat = adj_batch(chk)
    assert max(abs(a - b) for a, b in zip(full, bat)) < 1e-3, (full, bat)
    summary = {}
    for (fam, src, L, rels, ntarget, allot) in PLAN:
        name = "%s|%s|L%d|%s" % (fam, src or "LP2", L, "+".join(rels))
        t0 = time.time()
        remaining = BUDGET - (t0 - T0)
        if remaining < 20:
            log("SKIP (global budget)", name); continue
        allot = min(allot, remaining)
        rng = random.Random(3301 + L * 7 + (hash(src) % 1000 if False else (sum(map(ord, src)) if src else 0)))
        n = keylen(L)
        buf = {r: [] for r in rels}
        outs = {r: [] for r in rels}
        done = 0
        k0 = 0 if src is None else 1000000 * (1 + REG4.index(src))
        while done < ntarget and time.time() - t0 < allot:
            C = draw_C(fam, src, L, k0 + done)
            st, fm = FAMS[done % len(FAMS)]
            K = keystream(st, fm, rng.choice(by[(st, fm)]), n)
            for r in rels:
                d = V.beam_decode_v3(C, K, ADV[r], "panel_max", tau=0.0, lam_u=4.0)
                buf[r].append(d["plain_idx"])
            done += 1
            if done % 200 == 0 or done == ntarget:
                for r in rels:
                    ls = {}
                    for i, x in enumerate(buf[r]):
                        ls.setdefault(len(x), []).append(i)
                    pm = [None] * len(buf[r])
                    for ln, ii in ls.items():
                        for i, v in zip(ii, adj_batch([buf[r][i] for i in ii])):
                            pm[i] = round(float(v), 4)
                    outs[r].extend(pm)
                    OUTF.write(json.dumps({"cell": name, "rel": r, "L": L, "family": fam, "source": src or "LP2", "i0": done - len(pm), "pm": pm}) + "\n")
                    buf[r] = []
                OUTF.flush()
        if done % 200:   # flush the tail of an allotment-stopped cell
            for r in rels:
                if buf[r]:
                    pm = []
                    ls = {}
                    for i, x in enumerate(buf[r]):
                        ls.setdefault(len(x), []).append(i)
                    pm = [None] * len(buf[r])
                    for ln, ii in ls.items():
                        for i, v in zip(ii, adj_batch([buf[r][i] for i in ii])):
                            pm[i] = round(float(v), 4)
                    OUTF.write(json.dumps({"cell": name, "rel": r, "L": L, "family": fam, "source": src or "LP2", "i0": done - len(pm), "pm": pm}) + "\n")
                    outs[r].extend(pm)
            OUTF.flush()
        sec = time.time() - t0
        summary[name] = {r: {"n": len(outs[r]), "max": max(outs[r]) if outs[r] else None} for r in rels}
        summary[name]["seconds"] = round(sec, 1)
        log("cell", name, "draws", done, "of", ntarget, "%.0fs" % sec, {r: summary[name][r] for r in rels})
    log("DONE", json.dumps(summary))

main()
