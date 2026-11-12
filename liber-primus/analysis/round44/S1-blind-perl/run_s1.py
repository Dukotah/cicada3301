"""Round 44 lane S1 driver. See PREREG.md.

    python3 run_s1.py control     # the 24 Perl-seed plants through the sweep binary (go / no-go)
    python3 run_s1.py sweep [W]   # all 2^32 seeds in 256 resumable chunks, W worker processes (default 4)
    python3 run_s1.py finalize    # merge, verdict, SWEEPROW store of the best rows, results.json
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

import common as cm

L1, T1, L2, T2, L3, T3 = 64, 247, 120, 828, 262, 3564          # PREREG section 3
CHUNK = 1 << 24
NCHUNK = 1 << 8
CH = os.path.join(cm.HERE, "chunks")


def control():
    cm.build()
    rng = random.Random(4403)
    T = cm.plant_texts()
    names = list(T)
    rows = []
    with tempfile.TemporaryDirectory() as td:
        cf = os.path.join(td, "c.txt")
        for k in range(24):
            seed = rng.getrandbits(32)
            tname = names[k % 3]; variant = cm.VARIANTS[k % 4]
            cons = cm.CONSTRUCTIONS[(k // 4) % 3]; sign = +1 if (k // 12) % 2 == 0 else -1
            K = cm.perl_real(seed, 420)                      # the perl binary, not this lane's generator
            assert K == cm.perl_stream(seed, 420)
            C, info = cm.make_plant(rng, T[tname], variant, cons, K, L=L3, sign=sign)
            open(cf, "w").write(" ".join(map(str, C)))
            lo = max(0, min((1 << 32) - (1 << 18), seed - rng.randrange(1 << 18)))
            recs, _ = cm.run_kernel("perl", lo, lo + (1 << 18), cf, L1, T1, L2, T2, L3)
            mode = (0 if sign == +1 else 2) + (0 if cons == "keyskip1" else 1)
            flagged = [(r[0], r[1]) for r in recs if r[4] >= T3]
            hit = (seed, mode) in flagged
            others = [f for f in flagged if f[0] != seed]
            best = max((r[4] for r in recs if r[0] == seed), default=0)
            rows.append({"plant": k, "text": tname, "variant": variant, "construction": cons, "sign": sign,
                         "seed_window": [lo, lo + (1 << 18)], "planted_seed_flagged_in_true_mode": hit,
                         "other_seeds_flagged": len(others), "stage3_records_in_window": len(recs),
                         "ioc_x29_L262_planted": cm.ioc29(best, L3) if best else None, **info})
            print(f"plant {k:2d} {tname:20s} {variant:22s} {cons:14s} s={sign:+d}  flagged={hit}  others={len(others)}  "
                  f"IoCx29@262={cm.ioc29(best, L3) if best else float('nan'):.3f}", flush=True)
    ok = sum(r["planted_seed_flagged_in_true_mode"] for r in rows); oth = sum(r["other_seeds_flagged"] for r in rows)
    res = {"plants": rows, "flagged": ok, "of": len(rows), "other_seeds_flagged": oth, "passed": ok >= 23 and oth == 0}
    json.dump(res, open(os.path.join(cm.HERE, "control.json"), "w"), indent=1)
    print(f"CONTROL: {ok}/24 planted seeds flagged, {oth} other seeds flagged -> {'PASS' if res['passed'] else 'FAIL'}")
    return res["passed"]


def one_chunk(c):
    out = os.path.join(CH, f"c_{c:03d}.bin"); h = os.path.join(CH, f"h_{c:03d}.bin"); done = os.path.join(CH, f"d_{c:03d}")
    if os.path.exists(done):
        return c, 0.0
    t0 = time.time()
    lo = c * CHUNK
    subprocess.run([cm.BLIND, "perl", str(lo), str(lo + CHUNK), cm.PAGE0, str(L1), str(T1), str(L2), str(T2), str(L3),
                    out + ".tmp", h + ".tmp"], check=True, stderr=subprocess.DEVNULL)
    os.replace(out + ".tmp", out); os.replace(h + ".tmp", h); open(done, "w").write(f"{time.time() - t0:.1f}\n")
    return c, time.time() - t0


def sweep(workers=4):
    cm.build()
    os.makedirs(CH, exist_ok=True)
    todo = [c for c in range(NCHUNK) if not os.path.exists(os.path.join(CH, f"d_{c:03d}"))]
    print(f"{NCHUNK - len(todo)} chunks done, {len(todo)} to run, {workers} workers", flush=True)
    t0 = time.time()
    with Pool(workers) as pool:
        for n, (c, dt) in enumerate(pool.imap_unordered(one_chunk, todo), 1):
            print(f"chunk {c:3d} done in {dt:6.1f}s   ({n}/{len(todo)}, elapsed {time.time() - t0:7.0f}s)", flush=True)
            if n == 4:                      # PREREG Q5 kill condition, checked on the first chunks finished
                recs = sum(os.path.getsize(f) // 20 for f in glob.glob(os.path.join(CH, "c_*.bin")))
                rate = recs / (4 * CHUNK * 4)
                print(f"kill check: stage-3 rate {rate:.2e} per (seed, mode) (limit 1e-3)", flush=True)
                if rate > 1e-3:
                    pool.terminate(); print("KILL: calibration did not transfer"); return
    open(os.path.join(cm.HERE, "SWEEP_DONE"), "w").write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")


def best_path(C, K, s, q, L, maxsk):
    """Python twin of the kernel's search, returning (sum of squares, decoded symbols of the best path)."""
    N = cm.N
    best = (-1, None)
    stack = [(0, 0, 0, [0] * N, 0, [])]
    while stack:
        i, j, used, cnt, ssq, dec = stack.pop()
        cnt = cnt[:]; dec = dec[:]
        while i < L:
            if i > 0 and used < maxsk:
                r = 1
                while r <= 3:
                    jj = j + r * q
                    if (s * (K[jj] - K[j]) - (C[i] - C[i - 1])) % N == 0:
                        stack.append((i, jj, used + r, cnt[:], ssq, dec[:]))
                    if K[jj] != K[j]:
                        break
                    r += 1
            d = (C[i] - s * K[j]) % N
            ssq += 2 * cnt[d] + 1; cnt[d] += 1; dec.append(d)
            i += 1; j += 1
            if q == 2 and i - 1 > 0 and C[i - 1] == C[i - 2]:
                stack.append((i, j + 1, used, cnt[:], ssq, dec[:]))
        if ssq > best[0]:
            best = (ssq, dec)
    return best


def finalize():
    done = len(glob.glob(os.path.join(CH, "d_*")))
    recs = []
    for f in sorted(glob.glob(os.path.join(CH, "c_*.bin"))):
        raw = open(f, "rb").read()
        recs += [struct.unpack_from("<5I", raw, o) for o in range(0, len(raw), 20)]
    hist = [[0] * 2048 for _ in range(4)]
    for f in sorted(glob.glob(os.path.join(CH, "h_*.bin"))):
        hb = open(f, "rb").read()
        for m in range(4):
            for v, x in enumerate(struct.unpack_from("<2048Q", hb, m * 2048 * 8)):
                hist[m][v] += x
    with open(os.path.join(cm.HERE, "survivors.bin"), "wb") as fh:
        for r in recs:
            fh.write(struct.pack("<5I", *r))
    json.dump({"L1": L1, "modes": cm.MODES, "sum_of_squares_histogram": [{str(v): x for v, x in enumerate(h) if x} for h in hist]},
              open(os.path.join(cm.HERE, "hist.json"), "w"))
    seeds = sum(hist[0])
    flagged = sorted((r for r in recs if r[4] >= T3), key=lambda r: -r[4])
    top = sorted(recs, key=lambda r: -r[4])
    ctrl = json.load(open(os.path.join(cm.HERE, "control.json")))
    res = {"prereg": "PREREG.md", "thresholds": {"L1": L1, "T1": T1, "L2": L2, "T2": T2, "L3": L3, "T3": T3},
           "chunks_done": done, "of_chunks": NCHUNK, "seeds_evaluated": seeds, "complete": seeds == 1 << 32,
           "pairs_evaluated": 4 * seeds,
           "stage1_pass_by_mode": [sum(x for v, x in enumerate(h) if v >= T1) for h in hist],
           "stage3_records": len(recs), "stage3_rate_per_pair": len(recs) / max(1, 4 * seeds),
           "flagged": [{"seed": r[0], "mode": cm.MODES[r[1]], "ioc_x29_L64": cm.ioc29(r[2], L1), "ioc_x29_L120": cm.ioc29(r[3], L2),
                        "ioc_x29_L262": cm.ioc29(r[4], L3)} for r in flagged],
           "best_null_rows": [{"seed": r[0], "mode": cm.MODES[r[1]], "ioc_x29_L120": cm.ioc29(r[3], L2), "ioc_x29_L262": cm.ioc29(r[4], L3)}
                              for r in top[:10]],
           "max_ioc_x29_L262": cm.ioc29(top[0][4], L3) if top else None,
           "control_passed": ctrl["passed"], "control": f"{ctrl['flagged']}/{ctrl['of']} planted seeds flagged, {ctrl['other_seeds_flagged']} others"}
    res["verdict"] = ("INCONCLUSIVE (control failed)" if not ctrl["passed"] else
                      "INCONCLUSIVE (sweep incomplete)" if not res["complete"] else
                      "INCONCLUSIVE (more than 20 flagged: threshold mis-set)" if len(flagged) > 20 else
                      "FLAGGED-FOR-ORACLE" if flagged else "NEGATIVE")
    # SWEEPROW/1 store of the best rows, adjudicated by panel-R36 on the L=120 decode of the best path
    try:
        sys.path.insert(0, cm.lp2.LP)
        import verify_solution as vs
        V, _, pan = vs.load_instruments(quiet=True)
        A = V.A
        C = cm.lp2.idx(cm.lp2.unsolved())[0]
        path = os.path.join(cm.HERE, "sweep_rows_top.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(A.header("round44/S1-blind-perl", pan=pan, generator="perl int(rand(29)) srand(seed)",
                                         statistic="best admissible path by IoC, decoded at L=120 as C - s*K (Gematria order)",
                                         rows="the 2,000 (seed, mode) pairs with the largest full-page IoC")) + "\n")
            for r in top[:2000]:
                s = +1 if r[1] < 2 else -1; q = 1 + (r[1] % 2)
                _, dec = best_path(C[:L2], cm.perl_stream(r[0], 420), s, q, L2, 12)
                fh.write(json.dumps(A.to_row(A.adjudicate(dec, pan=pan), kid=f"perl:seed={r[0]}:{cm.MODES[r[1]]}")) + "\n")
        A.validate_store(path)
        res["sweep_store"] = "sweep_rows_top.jsonl"
        rows = [json.loads(x) for x in open(path, encoding="utf-8").read().splitlines()[1:]]
        ip = A.ROW_FIELDS.index("pmax")
        res["best_panel_pmax_among_top_rows"] = max(x[ip] for x in rows) if rows else None
        for fl in res["flagged"]:
            s = +1 if fl["mode"].startswith("s=+1") else -1; q = int(fl["mode"][-1])
            _, dec = best_path(C, cm.perl_stream(fl["seed"], 420), s, q, L3, 24)
            fl["decode_gematria_order"] = "".join(cm.lp2.TR[d] for d in dec)
    except Exception as ex:                                    # the panel fixtures are needed for this part only
        res["sweep_store_error"] = repr(ex)
    json.dump(res, open(os.path.join(cm.HERE, "results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("best_null_rows",)}, indent=1)[:3000])


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
