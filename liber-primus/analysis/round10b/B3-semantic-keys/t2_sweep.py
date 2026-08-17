"""T2 -- orthography-expanded SEMANTIC key sweep over all 55 unsolved LP2 segments.

Novelty axis (PREREG G-a): every candidate word is expanded into its full ORTHOGRAPHIC ORBIT
(C->F systematic substitution, C/K/Q rune sharing, every multigraph split) instead of the single
greedy gp.keyword_to_indices() parse that every prior sweep in this repo used.

Decoder: phase-flexible screen (screen.py) -- exact for a periodic key under any interrupter
mask -- vectorised with fastscore.  Survivors re-scored with the repo's own Latin-space quadgram
scorer and then the repo's interrupter beam.

GATE (runs first, aborts on failure): the vectorised screen must rank DIVINITY #1 on 03.jpg and
a CIRCUMFERENCE-orbit key #1 on 14.jpg.

NULL: identical sweep against per-page shuffled ciphertext.

Run: PYTHONUTF8=1 python3 t2_sweep.py
"""
import json
import random
import sys
import time

import numpy as np

import b3lib
import fastscore as fs
import screen
from b3lib import gp
from lp import solve

SCL = b3lib.scorer()
N = gp.N
MIN_SEG = 10


def segments_of(ct):
    fpos = [i for i, c in enumerate(ct) if c == 0]
    bounds = [0] + [p for p in fpos if p > 0] + [len(ct)]
    segs = [(a, b) for a, b in zip(bounds, bounds[1:]) if b - a >= MIN_SEG]
    return segs or [(0, len(ct))]


def screen_page(ct_np, segs, keys):
    """Return list of (score, latin, spelled, sign, atbash, key_tuple)."""
    out = []
    lens = np.array([b - a for a, b in segs], dtype=np.float64)
    wsum = lens.sum()
    for lat, grp, k in keys:
        for sign in (-1, +1):
            for atb in (False, True):
                D = fs.decode_all_rotations(ct_np, k, sign, atb)   # (L, n)
                tot = 0.0
                for (a, b), w in zip(segs, lens):
                    if b - a < 4:
                        continue
                    tot += fs.score_rows(D[:, a:b]).max() * w
                out.append((tot / wsum, lat, gp.indices_to_translit(k), sign, atb, k))
    out.sort(key=lambda r: -r[0])
    return out


def gate_fast(keys):
    print("== T2 GATE: vectorised screen must re-find the ground truth ==")
    ok = True
    for label, want in (("03.jpg", "DIVINITY"), ("14.jpg", "CIRCUMFERENCE")):
        idxs, page = b3lib.solved_page(label)
        ct = np.array(idxs, dtype=np.int64)
        res = screen_page(ct, segments_of(idxs), keys)
        r = res[0]
        rank = next(i for i, x in enumerate(res) if x[1] == want)
        print(f"  {label}: rank1 = {r[1]} ({r[2]}) sign{r[3]:+d} atb{r[4]} score {r[0]:.3f}"
              f" | true {want} at rank {rank}")
        ok &= (r[1] == want)
    print(f"  T2 GATE: {'PASS' if ok else 'FAIL'}\n")
    return ok


def main():
    t0 = time.time()
    keys = b3lib.expanded_keys()
    print(f"expanded semantic keys: {len(keys)}  "
          f"(from {len(b3lib.vocabulary())} Latin words)")
    if not gate_fast(keys):
        print("ABORT: gate failed")
        return 1

    segs_all = b3lib.lp2_segments()
    rng = random.Random(3301)

    def run(pages, tag):
        best_rows = []
        for pi, ct in enumerate(pages):
            ctn = np.array(ct, dtype=np.int64)
            res = screen_page(ctn, segments_of(ct), keys)
            best_rows.append((res[0][0], pi, res[0][1], res[0][2], res[0][3], res[0][4],
                              res[0][5]))
        best_rows.sort(key=lambda r: -r[0])
        print(f"{tag}: best screen {best_rows[0][0]:.3f} on seg{best_rows[0][1]} "
              f"key {best_rows[0][2]} ({best_rows[0][3]})")
        return best_rows

    unsolved = segs_all[:55]
    real = run(unsolved, "REAL   ")
    shuf = []
    for ct in unsolved:
        c = list(ct)
        rng.shuffle(c)
        shuf.append(c)
    null = run(shuf, "SHUFFLE")

    print(f"\nscreen scale calibration (rune-4gram, NOT the Latin scale):")
    for label in ("03.jpg", "14.jpg"):
        idxs, _ = b3lib.solved_page(label)
        ct = np.array(idxs, dtype=np.int64)
        r = screen_page(ct, segments_of(idxs), keys)[0]
        print(f"  solved {label} with true key: {r[0]:.3f}")

    # ------------------------------------------ promote to the repo's own instruments
    print("\n== promotion of the top 20 real screens to the repo interrupter beam ==")
    raws = b3lib.lp2_segments_raw()
    promoted = []
    for s, pi, lat, spelled, sign, atb, k in real[:20]:
        ct = unsolved[pi]
        stream = [k[j % len(k)] for j in range(len(ct))]
        r = solve.find_interrupters(raws[pi], stream, sign=sign, atbash=atb, beam_width=300)
        pf, _, _ = screen.phase_flexible_score(ct, k, sign, atb, SCL)
        promoted.append((max(r["score_norm"], pf), pi, lat, spelled, sign, atb,
                         r["plaintext"][:80]))
    promoted.sort(key=lambda x: -x[0])
    for p in promoted[:10]:
        print(f"  {p[0]:7.3f} seg{p[1]:<3d} {p[2]:<18s} {p[3]:<18s} sign{p[4]:+d} atb{p[5]}"
              f"  {p[6][:60]}")
    print(f"\nBEST LATIN-SCALE SCORE ON ANY UNSOLVED PAGE: {promoted[0][0]:.3f}"
          f"   (repo hit threshold -5.200; campaign-18 null-max -6.820; English -4.0..-4.4)")

    json.dump({
        "n_keys": len(keys), "n_words": len(b3lib.vocabulary()),
        "real_screen_top": [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in real[:30]],
        "null_screen_top": [[r[0], r[1], r[2], r[3], r[4], r[5]] for r in null[:10]],
        "real_screen_best": real[0][0], "null_screen_best": null[0][0],
        "promoted": [list(p) for p in promoted[:20]],
        "best_latin_scale": promoted[0][0],
        "seconds": round(time.time() - t0, 1),
    }, open("T2-RESULTS.json", "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
