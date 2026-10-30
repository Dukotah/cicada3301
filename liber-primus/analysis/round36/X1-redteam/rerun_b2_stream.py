"""X1: is R36-B2 tier b a subset of R32-B2 / R34-B1 tier b? Same numpy call pattern -> first 3 blocks compared + arithmetic."""
import numpy as np, json, hashlib
BLK = 1 << 17
def blocks(n):
    rng = np.random.default_rng(3301)
    return [rng.integers(0, 1 << 32, size=BLK, dtype=np.uint64) for _ in range(n)]
a = blocks(3); b = blocks(3)   # R32 sweep.py:95,186-190 and R36 sweep.py:259-263 both call rng.integers(0, 1<<32, size=BLK, dtype=np.uint64)
out = {"first3_blocks_equal": all((x == y).all() for x, y in zip(a, b)),
       "sha_block0": hashlib.sha256(a[0].tobytes()).hexdigest(),
       "r32_blocks": 41680896 // BLK, "r36_blocks": 26083328 // BLK, "r34_blocks": 2621440 // BLK,
       "r32_frac": 41680896 / 2**32, "r36_frac": 199 * BLK / 2**32, "r34_frac": 2621440 / 2**32,
       "r36_subset_of_r32": 199 <= 41680896 // BLK, "r34_subset_of_r36": 2621440 // BLK <= 199,
       "r32_blocks_beyond_r36": 41680896 // BLK - 199}
print(out); json.dump(out, open("rerun_b2_stream.json", "w"), indent=1)
