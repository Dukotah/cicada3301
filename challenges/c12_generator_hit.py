"""C12 checker: did a generator reproduce a run of LP2's printed runes exactly? (CHALLENGES.md, C12)

    python challenges/c12_generator_hit.py --self-test
    python challenges/c12_generator_hit.py emitted.txt --log2-search 53.6

emitted.txt holds the rune indices (0-28, whitespace-separated; gematria order, F = 0) that YOUR program emitted
for the seed you claim. The checker finds the longest run that matches the 12,956-rune unsolved stream exactly,
forward or in Atbash order (28 - x), starting at the first emitted rune.

A hit needs no language model, so the only question is chance. If you tried 2^B (seed x variant) streams, each
against every position and both orders, a run of length R turns up by chance about 2^B * 25,912 / 29^R times.
--log2-search B is that B (count everything you tried, not only the stream you submit). The finish line is the
smallest R that keeps the chance count below 0.001, and never less than 14.

Round 48 / M1 covered B = 39.6 (8 generators x 2^32 seeds x 24 picker variants): 0 hits, longest run 11.
Exit 0 = the run is long enough. Credit also needs your program and seed, which we re-run.
"""
import argparse
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402

FLOOR, CHANCE = 14, 1e-3


def need(log2_search):
    return max(FLOOR, math.ceil((log2_search * math.log(2) + math.log(2 * 12956 / CHANCE)) / math.log(29)))


def best_run(E, T):
    best = (0, -1, 0)
    for atb in (0, 1):
        for p in range(len(T)):
            k = 0
            while k < len(E) and p + k < len(T) and (28 - T[p + k] if atb else T[p + k]) == E[k]:
                k += 1
            if k > best[0]:
                best = (k, p, atb)
    return best


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("emitted", nargs="?")
    ap.add_argument("--log2-search", type=float, default=39.6, help="log2 of the number of streams you tried")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    T = H.lp2_stream()
    if a.self_test or not a.emitted:
        rng = random.Random(4812)
        r1 = best_run(T[5000:5040], T)
        r2 = best_run([28 - x for x in T[700:730]], T)
        r3 = best_run([rng.randrange(29) for _ in range(40)], T)
        ok = r1 == (40, 5000, 0) and r2[0] == 30 and r2[2] == 1 and r3[0] < FLOOR and need(39.6) == 14 and need(64) > 14
        print(f"planted forward run {r1}; planted Atbash run {r2}; random stream {r3}; "
              f"required run at B=39.6: {need(39.6)}, at B=53.6: {need(53.6)}, at B=64: {need(64)}")
        print("SELF-TEST " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)
    E = [int(x) for x in open(a.emitted).read().split()]
    if any(not 0 <= x < 29 for x in E):
        sys.exit("rune indices must be 0-28")
    R, pos, atb = best_run(E, T)
    req = need(a.log2_search)
    print(f"longest exact run from your first rune: {R} runes at stream position {pos} ({'Atbash' if atb else 'gematria'} order)")
    print(f"search size 2^{a.log2_search}: required run {req} (chance count < {CHANCE})")
    done = R >= req
    print("FINISH LINE MET, pending a re-run of your program and seed" if done else "not yet")
    sys.exit(0 if done else 1)


if __name__ == "__main__":
    main()
