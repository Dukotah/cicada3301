#!/usr/bin/env python3
"""Round 38 / C2 sub-lane B follow-up: matched null for the cipher-DERIVED keys (N4 digit planes of the stream's own prime magnitudes; N5 generators of the stream).
Each draw: doublet-matched shuffle of LP2 -> re-derive every config's key from the shuffled stream (the same code path as the real build) -> decode the SAME 50 (config, window)
rows per family at L=240 -> family max per relation.  Fixed-config null (anti-conservative: the 50 were selected on the real L=120 scores).
python run_null.py <N4|N5> <D> <max_seconds>"""
import os, sys
sys.dont_write_bytecode = True
HERE0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE0)
import run_b as B          # reuses its imports, build(), top_rows(), dec()
from run_b import *        # noqa

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


LENS = [len(s) for s in B.SEGS]


def build_null(fam, cfg_w, Un, segs_n, gens, planes_n):
    cfg, w = cfg_w.rsplit(":w", 1); w = int(w)
    if fam == "U6a_N4_ks":
        m = re.match(r"^b(\d+)_p(\d+)_ks([+-]\d)$", cfg); return list(Un), planes_n[(int(m.group(1)), int(m.group(2)))], int(m.group(3)), w
    m = re.match(r"^(.*)_s([+-]\d)_o(\d+)(?:_seg(\d+))?$", cfg); gname, sg, off, pg = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
    if pg is None:
        if ("c", gname) not in gens: gens[("c", gname)] = B.gen_stream(gname, Un)
        return list(Un), [(k + off) % 29 for k in gens[("c", gname)]], sg, w
    key = ("s", gname, int(pg))
    if key not in gens: gens[key] = B.gen_stream(gname, segs_n[int(pg)])
    return list(segs_n[int(pg)]), [(k + off) % 29 for k in gens[key]], sg, w


def planes_of(Un):
    vals = NC.v_prime(Un); out = {}
    for base in (3, 5, 7, 10):
        mx = max(vals); pl = 0; v = mx
        while v > 0: pl += 1; v //= base
        for place in range(max(pl, 1)): out[(base, place)] = [int(x) for x in NC.digit_plane(vals, base=base, place=place)]
    return out


def main():
    which, D, tmax = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    fam = {"N4": "U6a_N4_ks", "N5": "U6a_N5"}[which]; wait_mem(); t0 = time.time()
    rows, _ = B.top_rows(fam); cfgs = [r[0] for r in rows]
    outp = B.BF("null_%s.jsonl" % which); done = [json.loads(l) for l in open(outp)] if os.path.exists(outp) else []
    f = open(outp, "a")
    for dd in range(len(done), D):
        if time.time() - t0 > tmax: break
        rng = random.Random(38200 + dd + (0 if which == "N4" else 100000)); Un = dfshuffle(U, rng)
        segs_n = []; i = 0
        for l in LENS: segs_n.append(Un[i:i + l]); i += l
        gens = {}; planes_n = planes_of(Un) if which == "N4" else None; mx = {r: -9.0 for r in RELS}; arg = {}
        for cfg_w in cfgs:
            C, K, sg, s = build_null(fam, cfg_w, Un, segs_n, gens, planes_n); L = min(240, len(C) - s); Cw, Kw = B.window(C, K, s, L)
            for rel in RELS:
                d, a = B.dec(Cw, Kw, rel, sg); pm = float(a["pmax"])
                if pm > mx[rel]: mx[rel] = pm; arg[rel] = [cfg_w, REGS[a["preg"]]]
        f.write(json.dumps({"draw": dd, "max": mx, "arg": arg, "elapsed": round(time.time() - t0, 1)}) + "\n"); f.flush()
        if dd % 5 == 0: print(which, dd, mx, "%.0fs" % (time.time() - t0), flush=True)
        if dd % 10 == 0: wait_mem()
    print("DONE", which, "%.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
