"""Round 44 lane S2 driver (glibc rand, clock-second band). See PREREG.md.

    python3 run_s2.py control | sweep [W] | finalize
"""
import glob
import json
import os
import random
import struct
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "S1-blind-perl"))
import common as cm        # noqa: E402
import run_s1 as s1        # noqa: E402

L1, T1, L2, T2, L3, T3 = s1.L1, s1.T1, s1.L2, s1.T2, s1.L3, s1.T3
RANGES = [(0, 1 << 24), (1322697600, 1396483200)]
GENS = ["glibcmod", "glibcscale"]
STEP = 1 << 22
CH = os.path.join(HERE, "chunks")
LIBC_SRC = r'''
#include <stdio.h>
#include <stdlib.h>
int main(int c, char **v){ unsigned s = strtoul(v[1],0,10); int how = atoi(v[2]); int n = atoi(v[3]); srand(s);
  for (int t=0;t<n;t++){ int r = rand(); printf("%d ", how ? (int)(29.0 * r / (RAND_MAX + 1.0)) : r % 29);} return 0; }
'''


def build():
    """Compile the shared kernel source into THIS lane's folder (lane S1's binary may be in use)."""
    cm.BLIND = os.path.join(HERE, "blind")
    subprocess.check_call(["gcc", "-O3", "-march=native", "-o", cm.BLIND, os.path.join(HERE, "..", "S1-blind-perl", "blind.c")])
    if not os.path.exists(cm.PAGE0):
        open(cm.PAGE0, "w").write(" ".join(map(str, cm.lp2.idx(cm.lp2.unsolved())[0])) + "\n")


def libc_stream(binpath, seed, how, n):
    r = subprocess.run([binpath, str(seed), str(how), str(n)], capture_output=True, text=True, check=True)
    return [int(x) for x in r.stdout.split()]


def control():
    build()
    rng = random.Random(4404)
    T = cm.plant_texts(); names = list(T)
    rows = []
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "l.c"); lb = os.path.join(td, "l"); cf = os.path.join(td, "c.txt")
        open(src, "w").write(LIBC_SRC); subprocess.check_call(["gcc", "-O2", "-o", lb, src])
        for k in range(16):
            how = k % 2
            lo_r, hi_r = RANGES[1] if k % 4 < 3 else RANGES[0]
            seed = rng.randrange(lo_r, hi_r)
            tname = names[k % 3]; variant = cm.VARIANTS[(k // 2) % 4]
            cons = cm.CONSTRUCTIONS[k % 3]; sign = +1 if k < 8 else -1
            K = libc_stream(lb, seed, how, 420)              # the C library itself
            C, info = cm.make_plant(rng, T[tname], variant, cons, K, L=L3, sign=sign)
            open(cf, "w").write(" ".join(map(str, C)))
            lo = max(0, seed - rng.randrange(1 << 18))
            recs, _ = cm.run_kernel(GENS[how], lo, lo + (1 << 18), cf, L1, T1, L2, T2, L3)
            mode = (0 if sign == +1 else 2) + (0 if cons == "keyskip1" else 1)
            flagged = [(r[0], r[1]) for r in recs if r[4] >= T3]
            hit = (seed & 0xFFFFFFFF, mode) in flagged
            others = len([f for f in flagged if f[0] != seed])
            rows.append({"plant": k, "generator": GENS[how], "text": tname, "variant": variant, "construction": cons, "sign": sign,
                         "planted_seed_flagged_in_true_mode": hit, "other_seeds_flagged": others})
            print(f"plant {k:2d} {GENS[how]:10s} {tname:20s} {variant:22s} {cons:14s} s={sign:+d}  flagged={hit}  others={others}", flush=True)
    ok = sum(r["planted_seed_flagged_in_true_mode"] for r in rows); oth = sum(r["other_seeds_flagged"] for r in rows)
    res = {"plants": rows, "flagged": ok, "of": len(rows), "other_seeds_flagged": oth, "passed": ok >= 15 and oth == 0}
    json.dump(res, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print(f"CONTROL: {ok}/16 planted seeds flagged, {oth} other seeds flagged -> {'PASS' if res['passed'] else 'FAIL'}")
    return res["passed"]


def jobs():
    out = []
    for g in GENS:
        for lo_r, hi_r in RANGES:
            a = lo_r
            while a < hi_r:
                out.append((g, a, min(hi_r, a + STEP))); a += STEP
    return out


def one(job):
    g, lo, hi = job
    tag = f"{g}_{lo}"
    out = os.path.join(CH, f"c_{tag}.bin"); h = os.path.join(CH, f"h_{tag}.bin"); done = os.path.join(CH, f"d_{tag}")
    if os.path.exists(done):
        return tag, 0.0
    t0 = time.time()
    subprocess.run([cm.BLIND, g, str(lo), str(hi), cm.PAGE0, str(L1), str(T1), str(L2), str(T2), str(L3), out + ".tmp", h + ".tmp"],
                   check=True, stderr=subprocess.DEVNULL)
    os.replace(out + ".tmp", out); os.replace(h + ".tmp", h); open(done, "w").write(f"{hi - lo}\n")
    return tag, time.time() - t0


def sweep(workers=4):
    build(); os.makedirs(CH, exist_ok=True)
    todo = [j for j in jobs() if not os.path.exists(os.path.join(CH, f"d_{j[0]}_{j[1]}"))]
    print(f"{len(jobs()) - len(todo)} jobs done, {len(todo)} to run", flush=True)
    t0 = time.time()
    with Pool(workers) as pool:
        for n, (tag, dt) in enumerate(pool.imap_unordered(one, todo), 1):
            print(f"{tag} done in {dt:.1f}s ({n}/{len(todo)}, elapsed {time.time() - t0:.0f}s)", flush=True)
    open(os.path.join(HERE, "SWEEP_DONE"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")


def finalize():
    res = {"prereg": "PREREG.md", "thresholds": {"L1": L1, "T1": T1, "L2": L2, "T2": T2, "L3": L3, "T3": T3}, "generators": {}}
    allrecs = []
    total_planned = sum(hi - lo for lo, hi in RANGES)
    hists = {}
    for g in GENS:
        recs = []; seeds = 0
        hist = [[0] * 2048 for _ in range(4)]
        for j in jobs():
            if j[0] != g:
                continue
            tag = f"{g}_{j[1]}"
            if not os.path.exists(os.path.join(CH, f"d_{tag}")):
                continue
            seeds += j[2] - j[1]
            raw = open(os.path.join(CH, f"c_{tag}.bin"), "rb").read()
            recs += [struct.unpack_from("<5I", raw, o) for o in range(0, len(raw), 20)]
            hb = open(os.path.join(CH, f"h_{tag}.bin"), "rb").read()
            for m in range(4):
                for v, x in enumerate(struct.unpack_from("<2048Q", hb, m * 2048 * 8)):
                    hist[m][v] += x
        hists[g] = [{str(v): x for v, x in enumerate(h) if x} for h in hist]
        top = sorted(recs, key=lambda r: -r[4])
        res["generators"][g] = {
            "seeds_evaluated": seeds, "of": total_planned, "complete": seeds == total_planned, "stage3_records": len(recs),
            "flagged": [{"seed": r[0], "mode": cm.MODES[r[1]], "ioc_x29_L262": cm.ioc29(r[4], L3)} for r in top if r[4] >= T3],
            "max_ioc_x29_L262": cm.ioc29(top[0][4], L3) if top else None,
            "best_rows": [{"seed": r[0], "mode": cm.MODES[r[1]], "ioc_x29_L120": cm.ioc29(r[3], L2), "ioc_x29_L262": cm.ioc29(r[4], L3)} for r in top[:5]]}
        allrecs += [(g,) + r for r in recs]
    json.dump({"L1": L1, "modes": cm.MODES, "sum_of_squares_histogram": hists}, open(os.path.join(HERE, "hist.json"), "w"))
    with open(os.path.join(HERE, "survivors.bin"), "wb") as fh:
        for r in allrecs:
            fh.write(struct.pack("<B5I", GENS.index(r[0]), *r[1:]))
    ctrl = json.load(open(os.path.join(HERE, "control.json")))
    nflag = sum(len(v["flagged"]) for v in res["generators"].values())
    complete = all(v["complete"] for v in res["generators"].values())
    res.update({"control_passed": ctrl["passed"], "control": f"{ctrl['flagged']}/{ctrl['of']} planted seeds flagged, {ctrl['other_seeds_flagged']} others",
                "keystreams_evaluated": sum(v["seeds_evaluated"] for v in res["generators"].values()), "complete": complete,
                "verdict": ("INCONCLUSIVE (control failed)" if not ctrl["passed"] else "INCONCLUSIVE (sweep incomplete)" if not complete else
                            "INCONCLUSIVE (more than 20 flagged)" if nflag > 20 else "FLAGGED-FOR-ORACLE" if nflag else "NEGATIVE")})
    try:
        sys.path.insert(0, cm.lp2.LP)
        import verify_solution as vs
        V, _, pan = vs.load_instruments(quiet=True); A = V.A
        C = cm.lp2.idx(cm.lp2.unsolved())[0]
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "l.c"); lb = os.path.join(td, "l"); open(src, "w").write(LIBC_SRC)
            subprocess.check_call(["gcc", "-O2", "-o", lb, src])
            path = os.path.join(HERE, "sweep_rows_top.jsonl")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(A.header("round44/S2-blind-glibc-clock", pan=pan, generator="glibc srand(seed); rand()%29 | floor(29*rand()/2^31)",
                                             statistic="best admissible path by IoC, decoded at L=120 as C - s*K (Gematria order)",
                                             rows="the 1,000 (generator, seed, mode) rows with the largest full-page IoC")) + "\n")
                for r in sorted(allrecs, key=lambda r: -r[5])[:1000]:
                    g, seed, mode = r[0], r[1], r[2]
                    s = +1 if mode < 2 else -1; q = 1 + (mode % 2)
                    _, dec = s1.best_path(C[:L2], libc_stream(lb, seed, GENS.index(g), 420), s, q, L2, 12)
                    fh.write(json.dumps(A.to_row(A.adjudicate(dec, pan=pan), kid=f"{g}:seed={seed}:{cm.MODES[mode]}")) + "\n")
            A.validate_store(path)
            res["sweep_store"] = "sweep_rows_top.jsonl"
            rows = [json.loads(x) for x in open(path, encoding="utf-8").read().splitlines()[1:]]
            res["best_panel_pmax_among_top_rows"] = max(x[A.ROW_FIELDS.index("pmax")] for x in rows) if rows else None
    except Exception as ex:
        res["sweep_store_error"] = repr(ex)
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(json.dumps(res, indent=1)[:2500])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "control":
        sys.exit(0 if control() else 1)
    elif cmd == "sweep":
        sweep(int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    elif cmd == "finalize":
        finalize()
    else:
        print(__doc__)
