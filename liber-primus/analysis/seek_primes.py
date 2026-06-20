"""ANSWER-SEEKING probe: history-dependent prime-value transforms.

Motivation: the unsolved pages' fingerprint is a *history-dependent* no-repeat
rule (doublet deficit + delta=0 hole), NOT a memoryless keystream — and the
solved pages literally say "THE PRIMES ARE SACRED" while the 2016 Cicada message
says "their numbers are the direction." Prior work tested *memoryless* prime/
totient keystreams (excluded by the doublet deficit). This tests transforms that
are BOTH prime-based AND history-dependent (shift each rune by a function of the
PREVIOUS rune's Gematria prime) — exactly the class consistent with the fingerprint.

Honest expectation: most likely flat (OTP-class). Any decode whose IoC jumps
toward English (~1.7) would be a real lead. Reproduce: python analysis/seek_primes.py
"""
import os, sys

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
from lp import gematria as gp                  # noqa: E402
from lp.stats import ioc_norm                  # noqa: E402

N = 29
P = gp.PRIMES  # prime value per rune index 0..28


def load_unsolved():
    segs = open(os.path.join(ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read().split("%")
    pages = [gp.runes_to_indices(s) for s in segs if gp.runes_to_indices(s)]
    return pages[:-2]  # drop solved AN END / PARABLE


def main():
    pages = load_unsolved()
    pooled = [i for p in pages for i in p]
    n = len(pooled)
    print(f"history-dependent prime-value probes on {n} unsolved runes")
    print("IoC_norm: flat=1.00, English-class ~1.70\n")

    results = {}
    # 1) shift each rune by the PREVIOUS rune's prime value (history-dependent), both signs
    for sign in (-1, +1):
        out = [pooled[0]] + [(pooled[i] + sign * P[pooled[i-1]]) % N for i in range(1, n)]
        results[f"c[i] {'-' if sign<0 else '+'} prime(c[i-1])"] = ioc_norm(out)
    # 2) shift by the prime value's index-mod (prime mod 29 of previous)
    for sign in (-1, +1):
        out = [pooled[0]] + [(pooled[i] + sign * (P[pooled[i-1]] % N)) % N for i in range(1, n)]
        results[f"c[i] {'-' if sign<0 else '+'} (prime(c[i-1]) mod 29)"] = ioc_norm(out)
    # 3) running cumulative prime sum of the plaintext-so-far proxy (history accum)
    for sign in (-1, +1):
        out, acc = [], 0
        for i in range(n):
            out.append((pooled[i] + sign * (acc % N)) % N)
            acc += P[pooled[i]]
        results[f"c[i] {'-' if sign<0 else '+'} cumsum(prime(c[<i])) mod 29"] = ioc_norm(out)
    # 4) shift by prime-INDEX of previous (i.e. previous index itself) — Gronsfeld-on-history
    for sign in (-1, +1):
        out = [pooled[0]] + [(pooled[i] + sign * pooled[i-1]) % N for i in range(1, n)]
        results[f"c[i] {'-' if sign<0 else '+'} c[i-1] (history Gronsfeld)"] = ioc_norm(out)

    best = None
    for k, v in sorted(results.items(), key=lambda kv: -kv[1]):
        flag = "  <-- LANGUAGE SIGNAL — verify!" if v > 1.30 else ""
        print(f"  {k:<42}: {v:.4f}{flag}")
        if best is None:
            best = (k, v)
    print(f"\n  raw ciphertext IoC_norm = {ioc_norm(pooled):.4f}")
    print(f"  best: {best[0]} @ {best[1]:.4f} — "
          f"{'LEAD' if best[1] > 1.30 else 'no break (consistent with OTP-class)'}")


if __name__ == "__main__":
    main()
