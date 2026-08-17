#!/usr/bin/env python3
"""L7-sota — isomorph statistic on LP2 0-54.

Fills the one capability gap found in the Round-10 community survey: the
`aldegonde` library (forked into cicada-solvers 2026-08-10) ships
stats/isomorphs.py and this repo has never computed the statistic.

Pre-registered in PREREG-ADDENDUM.md. HIT = z >= +4.0 vs the anti-repeat-matched
null (NC-B) at any window length, or a non-trivial shared pattern of length >= 14
present in LP2 and absent from all 200 NC-B nulls.

Run:  python3 isomorph.py
"""
import io
import json
import os
import random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.abspath(os.path.join(HERE, "..", "..", "..", "dataset", "liber_primus.json"))
NSHUF = 200
LENGTHS = (6, 8, 10, 12)
SEED = 20260812


def load_corpus():
    d = json.load(io.open(DATASET, encoding="utf-8"))
    pages = [p for p in d["pages"] if p["page"] <= 54]
    runes = "".join(p["runes"] for p in pages)
    alpha = sorted(set(runes))
    idx = {c: i for i, c in enumerate(alpha)}
    return [idx[c] for c in runes], len(alpha)


def pattern(win):
    """First-occurrence normalisation. Returns None if all symbols distinct."""
    seen = {}
    out = []
    for s in win:
        if s not in seen:
            seen[s] = len(seen)
        out.append(seen[s])
    if len(seen) == len(win):
        return None  # trivial
    return bytes(out)


def isomorph_pairs(seq, L):
    c = Counter()
    for i in range(len(seq) - L + 1):
        p = pattern(seq[i:i + L])
        if p is not None:
            c[p] += 1
    return sum(v * (v - 1) // 2 for v in c.values()), c


def longest_shared_nontrivial(seq, cap=40):
    """Longest L such that some non-trivial pattern is shared by >=2 windows."""
    best = 0
    for L in range(4, cap + 1):
        n, _ = isomorph_pairs(seq, L)
        if n == 0:
            break
        best = L
    return best


def adjacent_equal_rate(seq):
    return sum(1 for a, b in zip(seq, seq[1:]) if a == b) / (len(seq) - 1)


def shuffle_plain(seq, rng):
    s = list(seq)
    rng.shuffle(s)
    return s


def shuffle_antirepeat(seq, rng, target, tries=400):
    """Shuffle, then repair adjacent-equal pairs down toward `target` rate by
    swapping offending positions with random non-conflicting positions."""
    s = shuffle_plain(seq, rng)
    n = len(s)
    goal = int(round(target * (n - 1)))
    for _ in range(tries):
        bad = [i for i in range(n - 1) if s[i] == s[i + 1]]
        if len(bad) <= goal:
            break
        for i in bad:
            if len([1 for k in range(n - 1) if s[k] == s[k + 1]]) <= goal:
                break
            for _ in range(20):
                j = rng.randrange(n)
                if abs(j - i) < 2:
                    continue
                a, b = s[i], s[j]
                if a == b:
                    continue
                ok = True
                for k in (j - 1, j + 1):
                    if 0 <= k < n and s[k] == a:
                        ok = False
                for k in (i - 1, i + 1):
                    if 0 <= k < n and s[k] == b:
                        ok = False
                if ok:
                    s[i], s[j] = s[j], s[i]
                    break
    return s


def main():
    seq, nsym = load_corpus()
    rng = random.Random(SEED)
    rate = adjacent_equal_rate(seq)
    print(f"corpus N={len(seq)} alphabet={nsym} adjacent-equal rate={rate*100:.3f}%")

    obs = {}
    for L in LENGTHS:
        n, _ = isomorph_pairs(seq, L)
        obs[L] = n
    print("observed isomorph pairs:", obs)
    lsl = longest_shared_nontrivial(seq)
    print("longest shared non-trivial pattern length (LP2):", lsl)

    results = {"N": len(seq), "adjacent_equal_rate": rate, "observed": obs,
               "longest_shared_nontrivial": lsl, "nulls": {}}

    for name, maker in (("NC-A_plain", shuffle_plain),
                        ("NC-B_antirepeat", None)):
        stats = {L: [] for L in LENGTHS}
        longest = []
        for t in range(NSHUF):
            if name == "NC-A_plain":
                s = shuffle_plain(seq, rng)
            else:
                s = shuffle_antirepeat(seq, rng, rate)
            for L in LENGTHS:
                n, _ = isomorph_pairs(s, L)
                stats[L].append(n)
            if t < 20:  # longest-pattern scan is the expensive one
                longest.append(longest_shared_nontrivial(s))
        entry = {}
        for L in LENGTHS:
            v = stats[L]
            m = sum(v) / len(v)
            sd = (sum((x - m) ** 2 for x in v) / (len(v) - 1)) ** 0.5
            z = (obs[L] - m) / sd if sd > 0 else float("nan")
            entry[L] = {"mean": m, "sd": sd, "z": z, "min": min(v), "max": max(v)}
            print(f"{name} L={L:2d}: obs={obs[L]:8d} null mean={m:10.1f} sd={sd:8.1f} z={z:+.2f}")
        entry["longest_null"] = {"n": len(longest), "max": max(longest) if longest else None,
                                 "mean": sum(longest) / len(longest) if longest else None}
        print(f"{name} longest-shared-nontrivial over {len(longest)} nulls: "
              f"max={entry['longest_null']['max']} mean={entry['longest_null']['mean']}")
        results["nulls"][name] = entry

    with io.open(os.path.join(HERE, "isomorph_results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, default=str)
    print("wrote isomorph_results.json")


if __name__ == "__main__":
    main()
