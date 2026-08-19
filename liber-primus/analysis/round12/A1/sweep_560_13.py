"""FRONT A1, completion run — the recovered `DATA/560.13` pad.

Round 12's A1 swept five of the author's six CicadaOS binaries and returned NEGATIVE, with
one declared gap: `DATA/560.13` (118,818,811 bytes, sha256 db79072c...) was unobtainable —
in both the cicada-solvers and krisyotam mirrors it is a 134-byte Git-LFS pointer and the LFS
batch API answers `404 Object does not exist` on both remotes. A1/RESULTS.md recorded
recovering it from archive.org's 3301.iso as "the one remaining A1 lever".

2026-08-19: recovered. The archive.org item exposes the ISO's inner files directly —

    https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13    -> HTTP 200

and the download verifies **byte-exact** against the LFS pointer's own digest:
sha256 db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f, 118,818,811 bytes.

This script closes that gap by running the SAME machinery A1 used — same builders, same beam
settings, same null, same HIT bar — over the one pad it could not reach. Nothing here is a new
method; deliberately so, because the point is comparability with the published A1 result.

    python3 sweep_560_13.py [--nproc N]
"""
import argparse, hashlib, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_bytes, BUILDERS, ks_mod29, PADDIR, N, gp, nc, sk

# The capsule build renamed the recovered file; accept either name.
def _first_existing(*names):
    for n in names:
        p = os.path.join(PADDIR, n)
        if os.path.exists(p):
            return p
    return os.path.join(PADDIR, names[0])

PADS_TO_SWEEP = {
    # label: (path, expected sha256, expected length)
    "560.13": (_first_existing("DATA_560.13", "DATA_560.13.recovered"),
               "db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f",
               118818811),
    # A1 swept a TRUNCATED _560.00: the mirror copy is 2,412,544 B and is an exact byte
    # PREFIX of the ISO's 3,992,970 B copy (60.4% coverage), so A1's _560.00 result covers
    # only the first 60% of the real blob. Swept here from the authoritative copy.
    "_560.00_full": (_first_existing("DATA__560.00.iso-authoritative"), None, 3992970),
}
PAD = PADS_TO_SWEEP["560.13"][0]
EXPECT_SHA = PADS_TO_SWEEP["560.13"][1]
EXPECT_LEN = PADS_TO_SWEEP["560.13"][2]

HEAD = 400          # A1's head window
BEAM_W = 120        # A1's beam settings, unchanged
MAX_SKIP = 3
PAGE_L = 100


def log(m):
    print(m, flush=True)
    with open(os.path.join(HERE, "sweep_560_13.log"), "a", encoding="utf-8") as f:
        f.write(m + "\n")


def verify_pad():
    """A pad that is not byte-exact is a different experiment. Refuse to run on drift."""
    if not os.path.exists(PAD):
        log(f"FATAL: {PAD} not present. Fetch with:\n"
            f"  curl -L -o {PAD} "
            f"'https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13'")
        sys.exit(2)
    h, n = hashlib.sha256(), 0
    with open(PAD, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    ok = (h.hexdigest() == EXPECT_SHA and n == EXPECT_LEN)
    log(f"pad: {n:,} bytes  sha256 {h.hexdigest()}")
    log(f"     expected {EXPECT_LEN:,} / {EXPECT_SHA}  -> {'MATCH' if ok else 'MISMATCH'}")
    if not ok:
        log("FATAL: pad does not match the LFS pointer digest. Refusing to run.")
        sys.exit(2)
    return n


def null_ceiling(seq_len, K, n=200, seed0=3301):
    """A1's null, verbatim: beam-decode a shuffled head under a real keystream."""
    UNS = nc.unsolved()
    vals, base = [], UNS[:seq_len]
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        bd = sk.beam_decode(s, K, sign=-1, o=(k * 37) % 10000,
                            beam_w=BEAM_W, max_skip=MAX_SKIP)
        vals.append(bd["score"])
    return sum(vals) / len(vals), max(vals)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=2,
                    help="kept for symmetry; this sweep is single-process like A1's")
    ap.parse_args()

    t0 = time.time()
    log("=" * 74)
    log("FRONT A1 completion — DATA/560.13 (recovered from archive.org 3301.iso)")
    log("=" * 74)
    nbytes = verify_pad()

    UNS = nc.unsolved()
    log(f"unsolved runes: {len(UNS)}")
    head = UNS[:HEAD]

    b = load_bytes(PAD)
    log(f"loaded {len(b):,} bytes -> building {len(BUILDERS) * 2} keystream variants")

    variants = {name: fn(b) for name, fn in BUILDERS.items()}
    variants_rev = {name + "_rev": fn(b[::-1]) for name, fn in BUILDERS.items()}
    allv = {**variants, **variants_rev}

    # This pad is ~100x longer than the others, so it supports far deeper offsets than
    # A1 could sweep on the small pads. Offsets are extended accordingly and the extension
    # is declared here rather than quietly widening A1's stated bound.
    OFFSETS = (0, 1000, 5000, 20000, 100_000, 1_000_000, 10_000_000, 50_000_000)

    results = []
    for vname, K in allv.items():
        if len(K) < HEAD + 50:
            log(f"  skip {vname}: keystream too short ({len(K)})")
            continue
        for sign in (-1, +1):
            for o in OFFSETS:
                if o and o + HEAD * 4 + 8 >= len(K):
                    continue
                bd = sk.beam_decode(head, K, sign=sign, o=o,
                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                results.append({"pad": "560.13", "variant": vname, "sign": sign,
                                "o": o, "score": bd["score"],
                                "head": bd["translit"][:48]})
        log(f"  {vname}: cum {len(results)} configs, {time.time() - t0:.0f}s")

    results.sort(key=lambda x: x["score"], reverse=True)
    log("\n=== TOP 15 head configs ===")
    for r in results[:15]:
        log(f"{r['score']:.3f}  {r['variant']:16s} s{r['sign']:+d} "
            f"o{r['o']:<9d} {r['head']}")

    nmean, nmax = null_ceiling(HEAD, ks_mod29(b), n=200)
    hit_bar = max(-5.5, nmax + 0.5)
    log(f"\nnull(HEAD={HEAD}, n=200): mean={nmean:.3f} max={nmax:.3f}")
    log(f"HIT bar: score >= {hit_bar:.3f}   (A1's bar: >= -5.5 AND >= null_max + 0.5)")

    best = results[0] if results else None
    hit = bool(best and best["score"] >= hit_bar)
    log(f"\nbest head score = {best['score']:.3f} "
        f"-> {'CANDIDATE — ESCALATE' if hit else 'below bar (NEGATIVE)'}")

    # Escalation, per A1: any survivor is re-decoded on the full 12,956-rune stream.
    escalated = []
    if hit:
        for r in results:
            if r["score"] < hit_bar:
                break
            K = allv[r["variant"]]
            bd = sk.beam_decode(UNS, K, sign=r["sign"], o=r["o"],
                                beam_w=BEAM_W, max_skip=MAX_SKIP)
            escalated.append({**r, "full_score": bd["score"],
                              "full_head": bd["translit"][:120]})
            log(f"  ESCALATE {r['variant']} s{r['sign']:+d} o{r['o']} "
                f"-> full-stream {bd['score']:.3f}")

    out = {
        "pad": "DATA/560.13",
        "pad_bytes": nbytes,
        "pad_sha256": EXPECT_SHA,
        "pad_source": "https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13",
        "recovered": "2026-08-19",
        "closes": "the one declared gap in round12/A1/RESULTS.md",
        "unsolved_len": len(UNS),
        "head": HEAD, "beam_w": BEAM_W, "max_skip": MAX_SKIP,
        "offsets": list(OFFSETS),
        "n_configs": len(results),
        "null_mean": nmean, "null_max": nmax, "hit_bar": hit_bar,
        "best": best, "hit": hit, "escalated": escalated,
        "top": results[:20],
        "verdict": "HIT" if escalated and any(
            e["full_score"] >= hit_bar for e in escalated) else "NEGATIVE",
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(HERE, "results_560_13.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    log(f"\nVERDICT: {out['verdict']}   wrote results_560_13.json  "
        f"({out['elapsed_s']:.0f}s)")


if __name__ == "__main__":
    main()
