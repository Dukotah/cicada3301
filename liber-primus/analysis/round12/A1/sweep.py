"""FRONT A1 sweep — decode 12,956 unsolved runes against every author pad / config.

For efficiency the full-page beam decode is expensive; we sweep configs on a
representative HEAD window (first 400 runes) to find any config that lifts score
toward English, then re-run the full page on any survivor. This mirrors the
skip-model's own behavior: if a real key exists it produces English from rune 0.
"""
import os, sys, json, time, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import (load_bytes, BUILDERS, ks_mod29, PADDIR, N, gp, nc, sk)

# ------------------------------------------------------------------ data
UNS = nc.unsolved()                 # 12,956 rune indices
print(f"unsolved runes: {len(UNS)}")

PADS = {
    "_560.00":   os.path.join(PADDIR, "DATA__560.00"),
    "560.17":    os.path.join(PADDIR, "DATA_560.17"),
    "folly":     os.path.join(PADDIR, "tmp_folly"),
    "prime_echo":os.path.join(PADDIR, "usr_local_bin_prime_echo"),
    "761mp3":    os.path.abspath(os.path.join(HERE, "..", "..", "..", "..",
                    "puzzles", "2013", "artifacts", "761_The-Instar-Emergence.mp3")),
}

def null_ceiling(seq_len, n=200, seed0=3301):
    """False-positive ceiling: beam-decode a shuffled unsolved head under a fixed
    real keystream, n draws. Returns (mean,max)."""
    b = load_bytes(PADS["_560.00"])
    K = ks_mod29(b)
    vals = []
    base = UNS[:seq_len]
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base); r.shuffle(s)
        bd = sk.beam_decode(s, K, sign=-1, o=(k * 37) % 10000, beam_w=120, max_skip=3)
        vals.append(bd["score"])
    return sum(vals)/len(vals), max(vals), vals

# ------------------------------------------------------------------ head sweep
HEAD = 400
head = UNS[:HEAD]
results = []
t0 = time.time()

for padname, path in PADS.items():
    b = load_bytes(path)
    variants = {name: fn(b) for name, fn in BUILDERS.items()}
    variants_rev = {name + "_rev": fn(b[::-1]) for name, fn in BUILDERS.items()}
    allv = {**variants, **variants_rev}
    for vname, K in allv.items():
        if len(K) < HEAD + 50:
            continue
        for sign in (-1, +1):
            for o in (0, 1000, 5000, 20000):
                if o + HEAD * 4 + 8 >= len(K) and o != 0:
                    # allow o=0 always; skip offsets beyond pad
                    if o >= len(K):
                        continue
                bd = sk.beam_decode(head, K, sign=sign, o=o, beam_w=120, max_skip=3)
                results.append({
                    "pad": padname, "variant": vname, "sign": sign, "o": o,
                    "score": bd["score"], "head": bd["translit"][:48],
                })
    print(f"  {padname}: cum {len(results)} configs, {time.time()-t0:.0f}s")

results.sort(key=lambda x: x["score"], reverse=True)
print("\n=== TOP 15 head configs ===")
for r in results[:15]:
    print(f"{r['score']:.3f}  {r['pad']:9s} {r['variant']:14s} s{r['sign']:+d} o{r['o']:<6d} {r['head']}")

# null ceiling at HEAD length
nmean, nmax, _ = null_ceiling(HEAD, n=200)
print(f"\nnull(HEAD={HEAD}, n=200): mean={nmean:.3f} max={nmax:.3f}")
hit_bar = max(-5.5, nmax + 0.5)
print(f"HIT bar: score >= {hit_bar:.3f}  (>= -5.5 AND >= null_max+0.5)")

best = results[0]
print(f"\nbest head score = {best['score']:.3f}  -> "
      f"{'CANDIDATE' if best['score'] >= hit_bar else 'below bar (NEGATIVE)'}")

out = {
    "unsolved_len": len(UNS), "head": HEAD, "n_configs": len(results),
    "null_mean": nmean, "null_max": nmax, "hit_bar": hit_bar,
    "top": results[:20], "best": best,
    "elapsed_s": time.time()-t0,
}
with open(os.path.join(HERE, "sweep_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\nwrote sweep_results.json  ({time.time()-t0:.0f}s total)")
