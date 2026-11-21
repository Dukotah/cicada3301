"""R44 / W2-C1 — REAL READS (after PC1/PC2/PC3 all passed; see run.log).

(a) six-statistic battery vs seed-3301 nulls (battery.py), survivor iff p < 0.01/6
(b) V-stream panel reads through the 116-map grid; matched L=56 PERM/DRAW POT bars
    (bar of record = max), built by this cell; EN/LATIN power at L=56; degenerate
    (<5 distinct) streams are MEASURED-ONLY per PREREG
(c) generator-family keyed decodes on every motif page with canon runes; matched-L
    POT null bars (500 surrogates x 12 random-key decodes, shuffled canon windows)
"""
import json
import os
import time

import numpy as np

import battery as BT
import reads_lib as R
import shortnull as SN

OUT = os.path.join(R.CELL, "results")
t0 = time.time()
pan = R.panel()
streams = json.load(open(os.path.join(OUT, "streams.json")))
V1 = streams["V1"]
V2 = streams["V2"]
results = {"N_CAP": R.N_CAP, "alpha": R.ALPHA}

# ---------------- (a) battery ----------------
rng = np.random.default_rng(R.SEED)
bat = dict(
    S1_presence_gaps=BT.S1_presence_gaps(streams["motif_pages"]),
    S2_spearman_V1=BT.S2_spearman_count(V1),
    S3_zlib_T1=BT.S3_zlib_type(streams["T1"]),
    S4_zlib_O1=BT.S4_zlib_orient(streams["O1"]),
    S5_primes_V1=BT.S5_prime_counts(V1),
    S6_centroid_y=BT.S6_centroid_y(streams["centroid_y"]),
)
thr = 0.01 / 6
bat_min = min(bat.values())
results["battery"] = dict(p_values=bat, threshold=thr, min_p=bat_min,
                          survivor=bool(bat_min < thr))
print("battery:", {k: round(v, 5) for k, v in bat.items()}, "min", bat_min,
      "thr %.5f survivor" % thr, results["battery"]["survivor"])

# ---------------- (b) V-stream panel reads ----------------
vres = {}
pw = None
for name, vals in [("V1", V1)] + [("V2_%s" % k, v) for k, v in V2.items()]:
    nd = len(set(int(x) % R.N for x in vals))
    null = R.stream_null_bar(vals, pan, np.random.default_rng(R.SEED + 10))
    pm, meta, _ = R.stream_pmax(vals, pan)
    row = dict(n_distinct=nd, degenerate=bool(nd < 5), pmax=pm, argmax=meta,
               bar_of_record=null["bar_of_record"], null=null,
               crosses=bool(pm >= null["bar_of_record"]))
    if name == "V1" and nd >= 5:
        # power at L=56 through THIS path (held-out plant windows)
        pws = {}
        for lab, latin in (("EN", False), ("LATIN", True)):
            wins = SN.english_windows(56, 300, np.random.default_rng(R.SEED + 20), latin=latin)
            hits = sum(1 for w in wins
                       if R.stream_pmax([int(v) for v in w], pan)[0] >= null["bar_of_record"])
            pws[lab] = hits / len(wins)
        row["power"] = pws
        row["verdict_capable"] = bool(pws["EN"] >= 0.5)
        pw = pws
    vres[name] = row
    print("%s: pmax %.3f vs bar %.3f distinct=%d %s" %
          (name, pm, null["bar_of_record"], nd,
           "CROSSES" if row["crosses"] else ("measured-only" if row["degenerate"] else "neg")))
    if "power" in row:
        print("   power:", row["power"])
results["v_streams"] = vres

# ---------------- (c) generator-family keyed decodes ----------------
cat = json.load(open(os.path.join(OUT, "catalog.json")))
READ_CLASSES = sorted(["cross", "tree", "corpse_figure", "insect", "emblem_circle",
                       "grid_square", "humanoid_other", "other_figural"])
per_page = {}
for m in cat["motifs"]:
    per_page.setdefault(m["page"], {c: 0 for c in READ_CLASSES})
    per_page[m["page"]][m["cls"]] += 1

bars = {}
gres = []
n_dec = 0
for p in sorted(per_page):
    text = R.page_text(p)
    L = R.page_len(p)
    if text is None or L is None or L < 31:
        gres.append(dict(page=p, skipped="no canon runes (p50) or L<31", L=L))
        continue
    if L not in bars:
        bars[L] = R.generator_null_bar(L, pan, np.random.default_rng(R.SEED + 100 + L))
        print("null bar built L=%d bar=%.3f (%.0fs)" % (L, bars[L]["bar"], time.time() - t0))
    k = sum(per_page[p].values())
    vec = [per_page[p][c] for c in READ_CLASSES]
    fam = R.family_pmax(text, k, vec, pan)
    n_dec += len(fam)
    best = max(fam, key=lambda d: d["pmax"])
    gres.append(dict(page=p, L=L, k=k, vec=vec, bar=bars[L]["bar"], best=best,
                     decodes=fam, crosses=bool(best["pmax"] >= bars[L]["bar"])))
    print("p%d L=%d k=%d best %.3f (%s) vs bar %.3f %s" %
          (p, L, k, best["pmax"], best["variant"], bars[L]["bar"],
       "CROSSES" if gres[-1]["crosses"] else ""))
results["generator"] = dict(pages=gres, bars={str(k): v for k, v in bars.items()},
                            n_decodes=n_dec)

# ---------------- totals ----------------
n_panel = 116 * (1 + len(V2)) + n_dec
results["n_adjudicated_total"] = n_panel
results["any_crosser"] = bool(
    results["battery"]["survivor"]
    or any(v["crosses"] for v in vres.values())
    or any(g.get("crosses") for g in gres))
json.dump(results, open(os.path.join(OUT, "reads.json"), "w"), indent=1)
print("TOTAL adjudicated decodes: %d (cap %d) | any crosser: %s | %.0fs" %
      (n_panel, R.N_CAP, results["any_crosser"], time.time() - t0))
