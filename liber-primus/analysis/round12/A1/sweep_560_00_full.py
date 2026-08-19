"""FRONT A1, completion run 2 — the AUTHORITATIVE `DATA/_560.00`.

## The defect this closes

Round 12's A1 swept a copy of `_560.00` obtained from the cicada-solvers mirror:
**2,412,544 bytes**. The copy inside archive.org's `3301.iso` is **3,992,970 bytes**.

They are not two different files. The mirror copy is an **exact byte PREFIX** of the ISO copy
(verified: `iso[:len(mirror)] == mirror`), so the mirror copy is **truncated at 60.4%** — the
remaining 1,580,426 bytes were never fed to any decoder. `560.17` from the same mirror is
byte-perfect, so this is a defect specific to this file, not a bad mirror in general.

## What that does and does not invalidate

- **The A1 `_560.00` sweep covers only the first 60.4% of the blob.** That is a genuine
  coverage gap, and A1's headline should read "four of six pads fully swept, one partially"
  until this run closes it.
- **A1's positive control and null ceiling remain sound.** Both use `_560.00` bytes as a
  keystream (`null_ceiling()` calls `PADS["_560.00"]`), but the control plants and recovers
  with the *same* keystream, and the null decodes shuffled ciphertext under a real keystream.
  Truncation changes *which* keystream, not whether the instrument works — and 2.4 MB is far
  more than the 400-rune window needs. So the gap is coverage, not validity. Stating this
  precisely matters: an overstated retraction is as unhelpful as the original overstatement.

Same machinery as A1 throughout — same builders, beam settings, HEAD window, null and HIT bar —
so the result is directly comparable. The offset ladder is extended to use the recovered tail,
and that extension is declared rather than applied silently.

    python3 sweep_560_00_full.py
"""
import hashlib, json, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from harness import load_bytes, BUILDERS, ks_mod29, PADDIR, nc, sk

TRUNCATED = os.path.join(PADDIR, "DATA__560.00")
AUTHORITATIVE = os.path.join(PADDIR, "DATA__560.00.iso-authoritative")

HEAD, BEAM_W, MAX_SKIP = 400, 120, 3
LOG = os.path.join(HERE, "sweep_560_00_full.log")


def log(m):
    print(m, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(m + "\n")


def prove_truncation():
    """Re-verify the prefix relation here, so the claim is reproducible from this script
    alone and does not rest on a note in a results file."""
    if not os.path.exists(AUTHORITATIVE):
        log(f"FATAL: {AUTHORITATIVE} missing. Fetch the ISO copy of DATA/_560.00 from\n"
            f"  https://archive.org/download/3301.iso/3301.iso/  (inner-file listing)")
        sys.exit(2)
    a = open(TRUNCATED, "rb").read()
    b = open(AUTHORITATIVE, "rb").read()
    is_prefix = b[:len(a)] == a
    log(f"truncated (mirror, swept by A1): {len(a):,} bytes  "
        f"sha256 {hashlib.sha256(a).hexdigest()}")
    log(f"authoritative (3301.iso)       : {len(b):,} bytes  "
        f"sha256 {hashlib.sha256(b).hexdigest()}")
    log(f"mirror is an exact byte PREFIX of iso: {is_prefix}")
    log(f"A1 coverage of this pad: {100 * len(a) / len(b):.1f}%  "
        f"({len(b) - len(a):,} bytes never decoded)")
    if not is_prefix:
        log("NOTE: not a prefix - these are DIFFERENT files, not a truncation. "
            "Treat the ISO copy as a separate pad, and do not describe A1 as partial.")
    return len(a), len(b), is_prefix


def null_ceiling(seq_len, K, n=200, seed0=3301):
    UNS = nc.unsolved()
    vals, base = [], UNS[:seq_len]
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, K, sign=-1, o=(k * 37) % 10000,
                                   beam_w=BEAM_W, max_skip=MAX_SKIP)["score"])
    return sum(vals) / len(vals), max(vals)


def main():
    t0 = time.time()
    log("=" * 74)
    log("FRONT A1 completion 2 — authoritative DATA/_560.00 (A1 swept a 60.4% truncation)")
    log("=" * 74)
    n_trunc, n_full, is_prefix = prove_truncation()

    UNS = nc.unsolved()
    head = UNS[:HEAD]
    b = load_bytes(AUTHORITATIVE)
    allv = {**{k: fn(b) for k, fn in BUILDERS.items()},
            **{k + "_rev": fn(b[::-1]) for k, fn in BUILDERS.items()}}

    # A1's ladder was (0, 1e3, 5e3, 2e4). Extended so the recovered tail is actually
    # exercised: the truncation began at byte 2,412,544, so offsets beyond that index are
    # the ones A1 could not have reached at all.
    OFFSETS = (0, 1000, 5000, 20000, 100_000, 500_000, 1_000_000,
               2_000_000, 2_412_544, 3_000_000, 3_500_000)

    results = []
    for vname, K in allv.items():
        if len(K) < HEAD + 50:
            continue
        for sign in (-1, +1):
            for o in OFFSETS:
                if o and o + HEAD * 4 + 8 >= len(K):
                    continue
                bd = sk.beam_decode(head, K, sign=sign, o=o,
                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                results.append({"pad": "_560.00_authoritative", "variant": vname,
                                "sign": sign, "o": o, "score": bd["score"],
                                "in_recovered_tail": bool(o >= n_trunc),
                                "head": bd["translit"][:48]})
        log(f"  {vname}: cum {len(results)} configs, {time.time() - t0:.0f}s")

    results.sort(key=lambda x: x["score"], reverse=True)
    log("\n=== TOP 15 head configs ===")
    for r in results[:15]:
        tail = " [TAIL]" if r["in_recovered_tail"] else ""
        log(f"{r['score']:.3f}  {r['variant']:16s} s{r['sign']:+d} "
            f"o{r['o']:<9d}{tail} {r['head']}")

    nmean, nmax = null_ceiling(HEAD, ks_mod29(b), n=200)
    hit_bar = max(-5.5, nmax + 0.5)
    log(f"\nnull(HEAD={HEAD}, n=200): mean={nmean:.3f} max={nmax:.3f}")
    log(f"HIT bar: score >= {hit_bar:.3f}")

    best = results[0]
    tail_only = [r for r in results if r["in_recovered_tail"]]
    best_tail = max(tail_only, key=lambda r: r["score"]) if tail_only else None
    hit = best["score"] >= hit_bar

    log(f"\nbest overall      = {best['score']:.3f} "
        f"-> {'CANDIDATE' if hit else 'below bar (NEGATIVE)'}")
    if best_tail:
        log(f"best in the 40% A1 never saw = {best_tail['score']:.3f} "
            f"({best_tail['variant']} o{best_tail['o']})")

    escalated = []
    if hit:
        for r in results:
            if r["score"] < hit_bar:
                break
            bd = sk.beam_decode(UNS, allv[r["variant"]], sign=r["sign"], o=r["o"],
                                beam_w=BEAM_W, max_skip=MAX_SKIP)
            escalated.append({**r, "full_score": bd["score"],
                              "full_head": bd["translit"][:120]})
            log(f"  ESCALATE {r['variant']} o{r['o']} -> full {bd['score']:.3f}")

    out = {
        "pad": "DATA/_560.00 (authoritative, from 3301.iso)",
        "truncated_bytes_swept_by_A1": n_trunc,
        "authoritative_bytes": n_full,
        "mirror_is_exact_prefix": is_prefix,
        "a1_coverage_pct": round(100 * n_trunc / n_full, 1),
        "bytes_never_previously_decoded": n_full - n_trunc,
        "n_configs": len(results), "offsets": list(OFFSETS),
        "null_mean": nmean, "null_max": nmax, "hit_bar": hit_bar,
        "best": best, "best_in_recovered_tail": best_tail,
        "hit": hit, "escalated": escalated, "top": results[:20],
        "verdict": "HIT" if escalated and any(
            e["full_score"] >= hit_bar for e in escalated) else "NEGATIVE",
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(HERE, "results_560_00_full.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    log(f"\nVERDICT: {out['verdict']}   wrote results_560_00_full.json "
        f"({out['elapsed_s']:.0f}s)")


if __name__ == "__main__":
    main()
