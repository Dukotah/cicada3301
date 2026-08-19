"""ROUND 13 / B-04 — the sweep engine.

One worker = one chunk of seeds. For each seed it builds the derived keystream once per
(generator, reduction, direction) and then walks the sign / atbash / offset / segment
cross-product through the project's own SKIP-AWARE BEAM decoder (`sk.beam_decode`).

Only aggregates come back from a worker (top-K rows, a score histogram, per-axis bests,
a decode counter) so a multi-million-decode stage stays inside memory.

Sign convention: `score_norm` is negative, HIGHER = more English.
English ~ -4.2 | threshold -5.2 | noise ~ -7.4.
"""
import os, sys, time, math, heapq
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import skipdecode as sk        # noqa: E402
import lib_numchannel as nc    # noqa: E402
import ks                      # noqa: E402

N = 29
HEAD_L = 120        # PREREG s3.6 stage A/B segment length
PAGE_L = 100        # PREREG s3.6 stage C per-page segment length
BEAM_W = 400        # PREREG s3.6, matches round12/D3
MAX_SKIP = 3

# histogram bins for the sweep's own empirical (best-of-N) null
HIST_LO, HIST_HI, HIST_W = -12.0, -2.0, 0.05
HIST_NB = int((HIST_HI - HIST_LO) / HIST_W) + 1


def atbash(C):
    return [(N - 1) - c for c in C]


def make_segment(name, C):
    """(name, ciphertext, atbash(ciphertext))."""
    return (name, list(C), atbash(C))


def head_segment(L=HEAD_L):
    return make_segment("unsolved_head", nc.unsolved()[:L])


def page_segments(L=PAGE_L):
    out = []
    for i, pg in enumerate(nc.segments()[:-2]):        # 55 unsolved pages
        out.append(make_segment(f"page{i:02d}", pg[:min(L, len(pg))]))
    return out


def full_page0():
    return make_segment("page0_full", nc.segments()[0])


def full_unsolved():
    return make_segment("unsolved_full", nc.unsolved())


# ------------------------------------------------------------------ worker
_G = {}


def _init(seg_list, gens, reds, signs, atbs, dirs, offs, topk):
    _G.update(segs=seg_list, gens=gens, reds=reds, signs=signs, atbs=atbs,
              dirs=dirs, offs=offs, topk=topk)
    _G["maxlen"] = max(len(s[1]) for s in seg_list)
    _G["nsym"] = max(offs) + _G["maxlen"] * (MAX_SKIP + 2) + 128


def _work(chunk):
    segs, gens, reds = _G["segs"], _G["gens"], _G["reds"]
    signs, atbs, dirs, offs = _G["signs"], _G["atbs"], _G["dirs"], _G["offs"]
    topk, nsym = _G["topk"], _G["nsym"]
    heap = []
    hist = [0] * HIST_NB
    axis_best = {}
    ndec = 0
    for label, seed in chunk:
        for g in gens:
            raw = ks.make_bytes(g, seed, int(nsym * 1.35) + 256)
            for rd in reds:
                base = ks.make_ks(g, rd, seed, nsym, raw=raw)
                for dr in dirs:
                    K = base if dr == "fwd" else base[::-1]
                    for (sname, C0, C1) in segs:
                        for ab in atbs:
                            C = C0 if ab == 0 else C1
                            for sg in signs:
                                for off in offs:
                                    bd = sk.beam_decode(C, K, sign=sg, o=off,
                                                        beam_w=BEAM_W,
                                                        max_skip=MAX_SKIP)
                                    s = bd["score"]
                                    ndec += 1
                                    b = int((s - HIST_LO) / HIST_W)
                                    if 0 <= b < HIST_NB:
                                        hist[b] += 1
                                    ak = (g, rd)
                                    if s > axis_best.get(ak, -99):
                                        axis_best[ak] = s
                                    row = (s, label, seed, g, rd, sg, ab, dr,
                                           off, sname, bd["translit"][:64])
                                    if len(heap) < topk:
                                        heapq.heappush(heap, row)
                                    elif s > heap[0][0]:
                                        heapq.heapreplace(heap, row)
    return heap, hist, axis_best, ndec


def run_stage(segs, entries, gens=None, reds=None, signs=(-1, 1), atbs=(0, 1),
              dirs=("fwd", "rev"), offs=(0,), topk=300, nproc=None,
              chunk_seeds=16, label=""):
    """Run one stage. Returns dict(rows, hist, axis_best, n_decodes, elapsed_s)."""
    gens = list(gens or ks.GEN_NAMES)
    reds = list(reds or ks.RED_NAMES)
    nproc = nproc or max(1, (os.cpu_count() or 2) - 1)
    chunks = [entries[i:i + chunk_seeds]
              for i in range(0, len(entries), chunk_seeds)]
    per_seed = (len(gens) * len(reds) * len(dirs) * len(segs) * len(atbs)
                * len(signs) * len(offs))
    total = per_seed * len(entries)
    print(f"[{label}] seeds={len(entries)} gens={len(gens)} reds={len(reds)} "
          f"segs={len(segs)} signs={len(signs)} atbash={len(atbs)} "
          f"dirs={len(dirs)} offs={len(offs)}  -> {total:,} decodes "
          f"on {nproc} procs", flush=True)

    heap, hist, axis_best, ndec = [], [0] * HIST_NB, {}, 0
    t0 = time.time()
    with Pool(nproc, initializer=_init,
              initargs=(segs, gens, reds, signs, atbs, dirs, offs, topk)) as pool:
        done = 0
        for h, hh, ab, nd in pool.imap_unordered(_work, chunks):
            for row in h:
                if len(heap) < topk:
                    heapq.heappush(heap, row)
                elif row[0] > heap[0][0]:
                    heapq.heapreplace(heap, row)
            for i, v in enumerate(hh):
                hist[i] += v
            for k, v in ab.items():
                if v > axis_best.get(k, -99):
                    axis_best[k] = v
            ndec += nd
            done += 1
            if done % 20 == 0 or done == len(chunks):
                el = time.time() - t0
                print(f"    [{label}] {done}/{len(chunks)} chunks  "
                      f"{ndec:,} decodes  {el:.0f}s  "
                      f"({ndec/max(el,1e-9):,.0f}/s)  best={max(r[0] for r in heap):.3f}",
                      flush=True)
    rows = sorted(heap, key=lambda r: -r[0])
    return {
        "rows": [_row_dict(r) for r in rows],
        "hist": hist, "axis_best": {f"{a}|{b}": v for (a, b), v in axis_best.items()},
        "n_decodes": ndec, "elapsed_s": time.time() - t0,
    }


def _row_dict(r):
    (s, label, seed, g, rd, sg, ab, dr, off, sname, head) = r
    return {"score": s, "label": label,
            "seed": seed.decode("utf-8", "replace")[:64],
            "seed_hex": seed.hex(), "seed_len": len(seed),
            "gen": g, "red": rd, "sign": sg, "atbash": ab, "dir": dr,
            "offset": off, "segment": sname, "head": head}


def hist_stats(hist):
    """Empirical best-of-N ceiling from the sweep's own score distribution."""
    tot = sum(hist)
    if not tot:
        return {}
    cum, out = 0, {}
    marks = {"p50": 0.50, "p90": 0.90, "p99": 0.99, "p999": 0.999,
             "p9999": 0.9999, "p99999": 0.99999}
    keys = sorted(marks.items(), key=lambda x: x[1])
    ki = 0
    for i, v in enumerate(hist):
        cum += v
        while ki < len(keys) and cum / tot >= keys[ki][1]:
            out[keys[ki][0]] = HIST_LO + i * HIST_W
            ki += 1
    hi = max(i for i, v in enumerate(hist) if v)
    lo = min(i for i, v in enumerate(hist) if v)
    mean = sum((HIST_LO + i * HIST_W + HIST_W / 2) * v
               for i, v in enumerate(hist)) / tot
    var = sum(((HIST_LO + i * HIST_W + HIST_W / 2) - mean) ** 2 * v
              for i, v in enumerate(hist)) / tot
    out.update(n=tot, mean=mean, sd=math.sqrt(var),
               max_bin=HIST_LO + hi * HIST_W, min_bin=HIST_LO + lo * HIST_W)
    return out


# ------------------------------------------- flat-config API used by control.py
def stage_a_configs(entries):
    """(kept for readability of the control) — the Stage-A axis bundle."""
    return {"gens": list(ks.GEN_NAMES), "reds": list(ks.RED_NAMES),
            "signs": (-1, 1), "atbs": (0, 1), "dirs": ("fwd", "rev"),
            "offs": (0,), "entries": entries}


def run_configs(C, bundle, nproc=None, topk=300):
    """Run the Stage-A bundle against an explicit ciphertext (used by the G2 gate)."""
    segs = [make_segment("plant", C)]
    r = run_stage(segs, bundle["entries"], gens=bundle["gens"], reds=bundle["reds"],
                  signs=bundle["signs"], atbs=bundle["atbs"], dirs=bundle["dirs"],
                  offs=bundle["offs"], topk=topk, nproc=nproc, label="G2")
    for row in r["rows"]:
        row["seed_bytes"] = bytes.fromhex(row["seed_hex"])
    r["_rows"] = r["rows"]
    return r


if __name__ == "__main__":
    seg = head_segment()
    print("segment:", seg[0], len(seg[1]), "runes")
    print("generators:", len(ks.GEN_NAMES), "reductions:", len(ks.RED_NAMES))
