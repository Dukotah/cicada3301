"""FRONT A1 sweep 2 — per-page decode + full-page on top candidate + wider offsets.

Per-page: the pads may sync per LP2 page (each page reset). Decode each page's
runes under each pad/config, score, compare to per-length null.
Also: run full 12,956-rune beam on the single best head config to confirm it does
not lift over the whole stream.
"""
import os, sys, json, time, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_bytes, BUILDERS, ks_mod29, PADDIR, N, gp, nc, sk

SEGS = nc.segments()[:-2]            # 55 unsolved page-segments
UNS = nc.unsolved()
print(f"pages: {len(SEGS)}  total runes: {len(UNS)}")

PADS = {
    "_560.00":   os.path.join(PADDIR, "DATA__560.00"),
    "560.17":    os.path.join(PADDIR, "DATA_560.17"),
    "folly":     os.path.join(PADDIR, "tmp_folly"),
    "prime_echo":os.path.join(PADDIR, "usr_local_bin_prime_echo"),
    "761mp3":    os.path.abspath(os.path.join(HERE, "..", "..", "..", "..",
                    "puzzles", "2013", "artifacts", "761_The-Instar-Emergence.mp3")),
}

t0 = time.time()

# ---- per-page sweep (offset 0 only, per page reset) ----
best_pp = []
for padname, path in PADS.items():
    b = load_bytes(path)
    allv = {n: fn(b) for n, fn in BUILDERS.items()}
    allv.update({n + "_rev": fn(b[::-1]) for n, fn in BUILDERS.items()})
    for vname, K in allv.items():
        if len(K) < 2500:
            continue
        for sign in (-1, +1):
            for pi, seg in enumerate(SEGS):
                if len(seg) < 30:
                    continue
                bd = sk.beam_decode(seg, K, sign=sign, o=0, beam_w=80, max_skip=3)
                best_pp.append((bd["score"], padname, vname, sign, pi, len(seg),
                                bd["translit"][:40]))
    print(f"  {padname}: {len(best_pp)} page-configs, {time.time()-t0:.0f}s")

best_pp.sort(reverse=True)
print("\n=== TOP 15 per-page configs ===")
for s, pad, v, sg, pi, ln, h in best_pp[:15]:
    print(f"{s:.3f}  {pad:9s} {v:14s} s{sg:+d} pg{pi:<2d} n{ln:<4d} {h}")

# per-page null ceiling at median page length
med_len = sorted(len(s) for s in SEGS)[len(SEGS)//2]
b = ks_mod29(load_bytes(PADS["_560.00"]))
pp_null = []
base = UNS[:med_len]
for k in range(200):
    r = random.Random(3301 + k); s = list(base); r.shuffle(s)
    bd = sk.beam_decode(s, b, sign=-1, o=(k*37) % 10000, beam_w=80, max_skip=3)
    pp_null.append(bd["score"])
nmean, nmax = sum(pp_null)/len(pp_null), max(pp_null)
print(f"\nper-page null (len={med_len}, n=200): mean={nmean:.3f} max={nmax:.3f}")
bar = max(-5.5, nmax + 0.5)
print(f"HIT bar: {bar:.3f}")
best = best_pp[0]
print(f"best per-page = {best[0]:.3f} -> {'CANDIDATE' if best[0]>=bar else 'NEGATIVE'}")

# ---- full-page beam on the best head config (from sweep_results.json) ----
full = None
try:
    with open(os.path.join(HERE, "sweep_results.json")) as f:
        sw = json.load(f)
    bc = sw["best"]
    b = load_bytes(PADS[bc["pad"]])
    fn = BUILDERS[bc["variant"].replace("_rev", "")]
    K = fn(b[::-1]) if bc["variant"].endswith("_rev") else fn(b)
    print(f"\n=== full 12,956-rune beam on best head config: {bc['pad']} {bc['variant']} s{bc['sign']:+d} o{bc['o']} ===")
    bd = sk.beam_decode(UNS, K, sign=bc["sign"], o=bc["o"], beam_w=200, max_skip=3)
    print(f"full score = {bd['score']:.3f}")
    print(f"head: {bd['translit'][:80]}")
    full = {"config": bc, "full_score": bd["score"], "head": bd["translit"][:120]}
except Exception as e:
    print("full-page step error:", e)

out = {
    "per_page_null_mean": nmean, "per_page_null_max": nmax, "hit_bar": bar,
    "top_per_page": [list(x) for x in best_pp[:20]],
    "best_per_page": list(best),
    "full_page_best_config": full,
    "elapsed_s": time.time()-t0,
}
with open(os.path.join(HERE, "sweep2_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\nwrote sweep2_results.json  ({time.time()-t0:.0f}s)")
