"""R44 / W2-C1 PC2 + PC3 — read-instrument plants (PREREG section 6), run BEFORE any
real read is adjudicated.

PC2 : 250-rune held-out English window, encrypted shift k*=7, planted count 7 ->
      MY generator harness must decode it and clear the matched-L null bar.
PC3i: planted monotone count stream fires S2; planted periodic type sequence fires S3
      (thresholds p < 0.01/6).
PC3ii: 56-rune held-out English window through MY stream->grid path == shortnull direct.
"""
import json
import os

import numpy as np

import reads_lib as R
import shortnull as SN
import battery as BT

OUT = os.path.join(R.CELL, "results")
rng = np.random.default_rng(R.SEED)
pan = R.panel()
res = {}

# ---------- PC2: generator plant ----------
win = SN.english_windows(250, 1, rng)[0]          # held-out EN window, rune indices
k_star = 7
cipher_idx = [(c + k_star) % R.N for c in win]    # encrypt: C = P + k
import lp.gematria as gp
cipher_text = gp.indices_to_runes(np.asarray(cipher_idx))
null = R.generator_null_bar(250, pan, np.random.default_rng(R.SEED + 1), n_surr=500)
fam = R.family_pmax(cipher_text, k_star, [7, 0, 0, 0, 0, 0, 0, 0], pan)
best = max(fam, key=lambda d: d["pmax"])
# the decrypting variant is shift sign=-1 with k=7 (interrupters=True differs from the
# plant's plain encryption only at F runes; English windows contain F -> the decode is
# exact except planted-F cells; panel tolerance covers it)
res["PC2"] = dict(bar=null["bar"], null=null, best=best,
                  passed=bool(best["pmax"] >= null["bar"]))
print("PC2 generator plant: best pmax %.3f (%s) vs bar %.3f -> %s" %
      (best["pmax"], best["variant"], null["bar"], res["PC2"]["passed"]))

# ---------- PC3 i: battery plants ----------
v_plant = [i // 8 for i in range(56)]
p2 = BT.S2_spearman_count(v_plant, rng=np.random.default_rng(R.SEED + 2))
t_plant = (["cross", "tree", "insect"] * 32)[:95]
p3 = BT.S3_zlib_type(t_plant, rng=np.random.default_rng(R.SEED + 3))
thr = 0.01 / 6
res["PC3i"] = dict(S2_p=p2, S3_p=p3, threshold=thr,
                   passed=bool(p2 < thr and p3 < thr))
print("PC3i battery plants: S2 p=%.2e S3 p=%.2e thr=%.2e -> %s" %
      (p2, p3, thr, res["PC3i"]["passed"]))

# ---------- PC3 ii: grid-path equivalence ----------
w56 = SN.english_windows(56, 1, np.random.default_rng(R.SEED + 4))[0]
pm_mine, meta, _ = R.stream_pmax([int(v) for v in w56], pan)
pm_ref = float(np.max(SN.grid_pmax(np.asarray(w56, dtype=np.int64), pan)[0]))
res["PC3ii"] = dict(mine=pm_mine, ref=pm_ref, passed=bool(abs(pm_mine - pm_ref) < 1e-9))
print("PC3ii grid equivalence: %.6f vs %.6f -> %s" % (pm_mine, pm_ref, res["PC3ii"]["passed"]))

res["all_passed"] = bool(res["PC2"]["passed"] and res["PC3i"]["passed"] and res["PC3ii"]["passed"])
json.dump(res, open(os.path.join(OUT, "plant_reads.json"), "w"), indent=1)
print("ALL READ PLANTS PASSED:", res["all_passed"])
