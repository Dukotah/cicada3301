"""Round 41 I1: the standing POSITION-STRUCTURE-MATCHED null for direct (non-key) families.

Round 40 X1 showed the R13 DIRECTION near-miss's family p moved 0.004 -> 0.018 -> 0.070 as the null kept more of the
text's regional composition (global doublet-matched shuffle 0.004; block-permuted LP2 at 100 / 250 / 1000 runes
0.004 / 0.018 / 0.070, 500 draws each; round40/X1-redteam/rerun_r13_matched.py).  A walk of ~5,000 positions samples
page- and region-scale composition; a global shuffle destroys it and understates the spread.

    matched_shuffle(stream, block, rng, mode="blockperm", interrupter=0)
    bar_matched(stream, block_sizes=(100, 250, 1000), draws=500, stat_fn=..., alpha=0.01, seed_base=60000)

mode="blockperm" (X1's recipe, the standing default): cut `stream` into contiguous blocks of `block` runes, permute the
ORDER of the blocks with `random.Random(seed_base + j)`; local order inside a block, and every interrupter (rune 0 =
the F rune that acts as a pass-through null) that sits inside it, travel with the block.
mode="within": shuffle the NON-interrupter runes inside each block, interrupters fixed at their positions.

`stat_fn(shuffled_stream) -> float` is the family statistic (the family-wide Z or the family-best raw pmax).
Returns {block: {"stats": [...], "bar": empirical (1-alpha) quantile, "mean", "sd"}}; p_matched(obs, stats) is the
add-one empirical p.  No decoding machinery is imported: stat_fn carries it.

>>> import random
>>> s = list(range(12))
>>> matched_shuffle(s, 4, random.Random(0)) == matched_shuffle(s, 4, random.Random(0))
True
>>> sorted(matched_shuffle(s, 4, random.Random(1))) == s
True
>>> t = [0, 5, 0, 7, 9, 0, 2, 3]
>>> u = matched_shuffle(t, 4, random.Random(2), mode="within")
>>> [i for i, x in enumerate(u) if x == 0] == [0, 2, 5]
True
>>> r = bar_matched(list(range(300)), (100,), 20, stat_fn=lambda x: float(x[0]))
>>> sorted(r) == [100] and len(r[100]["stats"]) == 20
True
"""
import math, random
import numpy as np

SEED_BASE = 60000          # X1's rerun_r13_matched.py: random.Random(60000 + j)


def matched_shuffle(stream, block, rng, mode="blockperm", interrupter=0):
    x = list(stream); n = len(x)
    if mode == "blockperm":
        blocks = [x[i:i + block] for i in range(0, n, block)]
        rng.shuffle(blocks)
        return [v for b in blocks for v in b]
    if mode == "within":
        out = list(x)
        for i in range(0, n, block):
            idx = [k for k in range(i, min(i + block, n)) if x[k] != interrupter]
            vals = [x[k] for k in idx]; rng.shuffle(vals)
            for k, v in zip(idx, vals): out[k] = v
        return out
    raise ValueError(mode)


def p_matched(obs, stats):
    s = np.asarray(stats, float)
    return float((1 + (s >= obs).sum()) / (len(s) + 1))


def bar_matched(stream, block_sizes=(100, 250, 1000), draws=500, stat_fn=None, alpha=0.01, seed_base=SEED_BASE,
                mode="blockperm", interrupter=0):
    if stat_fn is None:
        raise ValueError("stat_fn is required")
    res = {}
    for bs in block_sizes:
        stats = [float(stat_fn(matched_shuffle(stream, bs, random.Random(seed_base + j), mode, interrupter))) for j in range(draws)]
        a = np.asarray(stats)
        res[bs] = {"stats": stats, "bar": float(np.quantile(a, 1 - alpha)), "mean": float(a.mean()),
                   "sd": float(a.std(ddof=1)) if len(a) > 1 else 0.0, "draws": draws}
    return res


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
