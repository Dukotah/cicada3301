"""Round 13 / B-05 -- Parts 1 and 2.

PART 1  the pp49-51 256-byte payload expanded as a PRF SEED into a full runic keystream
        over the 12,956 unsolved LP2 runes, decoded with BOTH the rigid decoder and the
        MANDATORY skip-aware beam.  Grid pinned in PREREG.md.

PART 2  the 6 contested bytes (RECON-A A-04) as a sensitivity dimension:
        2a  all 2^6 = 64 combinations of the two adjudicated candidate values
        2b  a single-position 256-value sweep at each contested index (bounds the
            "both witnesses share one OCR error" case)

Run:  PYTHONUTF8=1 python3 analysis/round13/B05/sweep.py
Writes sweep_results.json next to this file.
"""
import os
import sys
import json
import time
import random
import itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))
sys.path.insert(0, HERE)

import skipdecode as sk            # noqa: E402
import lib_numchannel as nc        # noqa: E402
import prf                          # noqa: E402

# ------------------------------------------------------------------ pinned grid
HEAD = 400
BEAM_W = 120
MAX_SKIP = 3
OFFSETS = [0, 1, 2, 3, 5, 8, 13, 29, 64, 128, 256, 512, 1024, 3301]
REDUCTIONS = ["mod", "reject"]
SIGNS = [-1, +1]
DIRECTIONS = ["fwd", "rev"]
ATBASH = [False, True]

UNS = nc.unsolved()
HEADSEQ = UNS[:HEAD]
FULL_LEN = len(UNS)
# key material a full-page worst-case beam could consume, plus the largest offset
TOTAL_KS = FULL_LEN * (MAX_SKIP + 1) + max(OFFSETS) + 64
HEAD_KS = HEAD * (MAX_SKIP + 1) + max(OFFSETS) + 64

HIT_SCORE = -5.5


def log(msg):
    print(msg, flush=True)


# ------------------------------------------------------------------ null band
def null_band(n=200, seed0=3301):
    """Size-matched shuffle null: order-destroying, histogram-preserving surrogates of the
    real ciphertext HEAD, beam-decoded under a REAL payload-derived keystream at rotating
    offsets.  This is the false-positive ceiling the HIT bar must beat."""
    maj, _ = prf.load_payloads()
    K = prf.keystream(maj, "sha256_ctr", "mod", HEAD_KS)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(HEADSEQ)
        r.shuffle(s)
        bd = sk.beam_decode(s, K, sign=-1, o=(k * 37) % 2000, beam_w=BEAM_W, max_skip=MAX_SKIP)
        vals.append(bd["score"])
    return sum(vals) / len(vals), max(vals), vals


# ------------------------------------------------------------------ part 1
def part1(bar):
    reps = prf.representations()
    gens = list(prf.GENERATORS)
    results = []
    best_per_gen = {}
    t0 = time.time()
    ndone = 0

    for rname in sorted(reps):
        seed = reps[rname]
        for gname in gens:
            for red in REDUCTIONS:
                base = prf.keystream(seed, gname, red, TOTAL_KS)
                for direction in DIRECTIONS:
                    Kd = base if direction == "fwd" else base[::-1]
                    for atb in ATBASH:
                        K = prf.atbash(Kd) if atb else Kd
                        for sign in SIGNS:
                            for o in OFFSETS:
                                bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=o,
                                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                                ndone += 1
                                sc = bd["score"]
                                rec = {"part": 1, "rep": rname, "gen": gname, "red": red,
                                       "dir": direction, "atbash": atb, "sign": sign,
                                       "o": o, "score": sc, "head": bd["translit"][:48]}
                                results.append(rec)
                                if sc > best_per_gen.get(gname, (-99, None))[0]:
                                    best_per_gen[gname] = (sc, rec)
            log(f"  [part1] {rname:16s} {gname:18s} cum={ndone:6d} "
                f"{time.time()-t0:6.0f}s  best={max(r['score'] for r in results):.3f}")

    results.sort(key=lambda x: x["score"], reverse=True)
    hits = [r for r in results if r["score"] >= bar]
    return results, hits, {g: v[1] for g, v in best_per_gen.items()}, time.time() - t0


# ------------------------------------------------------------------ part 2
def _variant(maj, dec, mask):
    """mask is a 6-bit int: bit i set => take the DECIMAL value at contested index i."""
    b = bytearray(maj)
    for i, idx in enumerate(prf.CONTESTED):
        if mask >> i & 1:
            b[idx] = dec[idx]
    return bytes(b)


def part2a(bar):
    """All 2^6 = 64 combinations of the two adjudicated candidate values."""
    maj, dec = prf.load_payloads()
    gens = list(prf.GENERATORS)
    need = HEAD * (MAX_SKIP + 1) + 64
    results = []
    t0 = time.time()
    for mask in range(64):
        seed = _variant(maj, dec, mask)
        for gname in gens:
            for red in REDUCTIONS:
                K = prf.keystream(seed, gname, red, need)
                for sign in SIGNS:
                    bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=0,
                                        beam_w=BEAM_W, max_skip=MAX_SKIP)
                    results.append({"part": "2a", "mask": mask, "gen": gname, "red": red,
                                    "sign": sign, "score": bd["score"],
                                    "head": bd["translit"][:40]})
        if mask % 16 == 15:
            log(f"  [part2a] mask {mask+1}/64  {time.time()-t0:5.0f}s")
    results.sort(key=lambda x: x["score"], reverse=True)
    return results, [r for r in results if r["score"] >= bar], time.time() - t0


def part2b(bar):
    """Single-position 256-value sweep: hold 5 contested bytes at the majority value and
    sweep the sixth over all 256 byte values.  Bounds the single-unknown-error case."""
    maj, _ = prf.load_payloads()
    gens = list(prf.GENERATORS)
    need = HEAD * (MAX_SKIP + 1) + 64
    results = []
    t0 = time.time()
    for idx in prf.CONTESTED:
        for val in range(256):
            b = bytearray(maj)
            b[idx] = val
            seed = bytes(b)
            for gname in gens:
                K = prf.keystream(seed, gname, "mod", need)
                bd = sk.beam_decode(HEADSEQ, K, sign=-1, o=0,
                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                results.append({"part": "2b", "idx": idx, "val": val, "gen": gname,
                                "score": bd["score"]})
        log(f"  [part2b] idx {idx} done  {time.time()-t0:5.0f}s  "
            f"best={max(r['score'] for r in results):.3f}")
    results.sort(key=lambda x: x["score"], reverse=True)
    return results, [r for r in results if r["score"] >= bar], time.time() - t0


# ---------------------------------------------------- secondary constant-shift pass
def part1_shift(bar):
    """The main grid has no additive constant.  Sweep s in 0..28 on the two canonical
    representations (equivalent to adding a constant to the keystream)."""
    maj, dec = prf.load_payloads()
    need = HEAD * (MAX_SKIP + 1) + 64
    results = []
    t0 = time.time()
    for rname, seed in (("maj.raw", maj), ("dec.raw", dec)):
        for gname in prf.GENERATORS:
            for red in REDUCTIONS:
                base = prf.keystream(seed, gname, red, need)
                for s in range(29):
                    K = [(k + s) % 29 for k in base]
                    for sign in SIGNS:
                        bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=0,
                                            beam_w=BEAM_W, max_skip=MAX_SKIP)
                        results.append({"part": "1shift", "rep": rname, "gen": gname,
                                        "red": red, "shift": s, "sign": sign,
                                        "score": bd["score"]})
        log(f"  [shift] {rname} done  {time.time()-t0:5.0f}s")
    results.sort(key=lambda x: x["score"], reverse=True)
    return results, [r for r in results if r["score"] >= bar], time.time() - t0


# ------------------------------------------------------------------ rigid control channel
def rigid_channel():
    """Report what the RIGID decoder returns on the same grid corner, to document that the
    beam is doing the work (D3's point: rigid is blind to this family even when correct)."""
    reps = prf.representations()
    out = []
    for rname in sorted(reps):
        for gname in prf.GENERATORS:
            K = prf.keystream(reps[rname], gname, "mod", HEAD + 64)
            rd = sk.rigid_decode(HEADSEQ, K, sign=-1, o=0)
            out.append({"rep": rname, "gen": gname, "score": rd["score"]})
    out.sort(key=lambda x: x["score"], reverse=True)
    return out


# ------------------------------------------------------------------ full-page rerun
def full_page(rec):
    reps = prf.representations()
    seed = reps[rec["rep"]]
    base = prf.keystream(seed, rec["gen"], rec["red"], TOTAL_KS)
    K = base if rec["dir"] == "fwd" else base[::-1]
    if rec["atbash"]:
        K = prf.atbash(K)
    bd = sk.beam_decode(UNS, K, sign=rec["sign"], o=rec["o"], beam_w=400, max_skip=MAX_SKIP)
    return {"config": rec, "full_score": bd["score"], "head": bd["translit"][:120]}


# ------------------------------------------------------------------ main
def main():
    log("=" * 78)
    log("ROUND 13 / B-05 -- pp49-51 payload as a PRF SEED expanded into a runic keystream")
    log("=" * 78)
    log(f"unsolved runes: {FULL_LEN}   HEAD={HEAD}  beam_w={BEAM_W}  max_skip={MAX_SKIP}")

    t0 = time.time()
    nmean, nmax, nall = null_band(n=200)
    bar = max(HIT_SCORE, nmax)
    log(f"\nnull (shuffled ciphertext HEAD, n=200): mean {nmean:.3f}  max {nmax:.3f}")
    log(f"HIT bar: score >= -5.5 AND score > null_max  ->  bar = {bar:.3f}\n")

    log("--- PART 1: pinned grid ---")
    p1, p1hits, p1best, p1t = part1(bar)
    log(f"\nPART 1 done: {len(p1)} decodes in {p1t:.0f}s  best={p1[0]['score']:.3f}")
    for r in p1[:10]:
        log(f"  {r['score']:.3f}  {r['rep']:14s} {r['gen']:18s} {r['red']:6s} "
            f"{r['dir']} atb={int(r['atbash'])} s{r['sign']:+d} o{r['o']:<5d} {r['head'][:36]}")

    log("\n--- PART 1b: constant-shift pass ---")
    ps, pshits, pst = part1_shift(bar)
    log(f"PART 1b done: {len(ps)} decodes in {pst:.0f}s  best={ps[0]['score']:.3f}")

    log("\n--- PART 2a: all 64 contested-byte combinations ---")
    p2a, p2ahits, p2at = part2a(bar)
    log(f"PART 2a done: {len(p2a)} decodes in {p2at:.0f}s  best={p2a[0]['score']:.3f}")

    log("\n--- PART 2b: single-position 256-value sweep ---")
    p2b, p2bhits, p2bt = part2b(bar)
    log(f"PART 2b done: {len(p2b)} decodes in {p2bt:.0f}s  best={p2b[0]['score']:.3f}")

    log("\n--- rigid control channel (documents that the beam carries the test) ---")
    rig = rigid_channel()
    log(f"  rigid best over {len(rig)} corners: {rig[0]['score']:.3f} "
        f"({rig[0]['rep']} / {rig[0]['gen']})")

    # full-page rerun of the top-5 configs regardless of bar, for the record
    log("\n--- full-page rerun of top-5 Part-1 configs ---")
    fp = []
    for r in p1[:5]:
        f = full_page(r)
        fp.append(f)
        log(f"  full {f['full_score']:.3f}  (head was {r['score']:.3f})  "
            f"{r['rep']}/{r['gen']}/{r['red']}/{r['dir']}/atb{int(r['atbash'])}/s{r['sign']}/o{r['o']}")

    total_decodes = len(p1) + len(ps) + len(p2a) + len(p2b)
    allhits = p1hits + pshits + p2ahits + p2bhits
    log(f"\n{'='*78}")
    log(f"TOTAL beam decodes: {total_decodes}   HITS at bar {bar:.3f}: {len(allhits)}")
    log(f"VERDICT: {'CANDIDATES FOUND' if allhits else 'NEGATIVE'}")
    log(f"{'='*78}")

    out = {
        "unsolved_len": FULL_LEN, "head": HEAD, "beam_w": BEAM_W, "max_skip": MAX_SKIP,
        "null_mean": nmean, "null_max": nmax, "hit_bar": bar, "null_n": 200,
        "grid": {"reps": sorted(prf.representations()), "gens": list(prf.GENERATORS),
                 "reductions": REDUCTIONS, "signs": SIGNS, "dirs": DIRECTIONS,
                 "atbash": ATBASH, "offsets": OFFSETS},
        "part1": {"n": len(p1), "best": p1[0], "top20": p1[:20], "hits": p1hits,
                  "best_per_generator": p1best, "seconds": p1t},
        "part1_shift": {"n": len(ps), "best": ps[0], "top10": ps[:10], "hits": pshits,
                        "seconds": pst},
        "part2a": {"n": len(p2a), "best": p2a[0], "top20": p2a[:20], "hits": p2ahits,
                   "seconds": p2at,
                   "best_per_mask": _best_by(p2a, "mask")},
        "part2b": {"n": len(p2b), "best": p2b[0], "top20": p2b[:20], "hits": p2bhits,
                   "seconds": p2bt, "best_per_idx": _best_by(p2b, "idx")},
        "rigid_channel": {"n": len(rig), "best": rig[0], "top10": rig[:10]},
        "full_page_top5": fp,
        "total_decodes": total_decodes,
        "n_hits": len(allhits),
        "verdict": "CANDIDATES" if allhits else "NEGATIVE",
        "elapsed_s": time.time() - t0,
    }
    with open(os.path.join(HERE, "sweep_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    log(f"wrote sweep_results.json  ({time.time()-t0:.0f}s total)")


def _best_by(rows, key):
    best = {}
    for r in rows:
        k = r[key]
        if r["score"] > best.get(k, {"score": -99})["score"]:
            best[k] = r
    return {str(k): v for k, v in sorted(best.items())}


if __name__ == "__main__":
    main()
