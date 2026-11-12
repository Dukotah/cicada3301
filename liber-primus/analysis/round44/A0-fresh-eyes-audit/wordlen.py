"""Fresh-eyes audit, part 4: the cleartext word lengths say the plaintext is spelled one rune per letter.

Word boundaries pass through the cipher. For each committed English text, each word is spelled two
ways - letter-wise (THE = 3 runes) and in the solved pages' multigraph orthography (TH, EO, NG/ING,
OE, AE, IA/IO, EA as single runes; THE = 2 runes) - and the two word-length histograms are compared
with LP2's. Licence text is avoided by using the middle 70 % of each file. Output: wordlen.json.
"""
import collections
import glob
import json
import math
import os
import re

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
W = lp2.words(lp2.unsolved()); n_lp = len(W)
lp_c = collections.Counter(min(len(w), 12) for w in W)
H = [lp_c.get(k, 0) / n_lp for k in range(1, 13)]


def mg_len(w):
    i = n = 0
    while i < len(w):
        i += 3 if w.startswith("ING", i) else 2 if w[i:i + 2] in ("TH", "EO", "NG", "OE", "AE", "IA", "IO", "EA") else 1
        n += 1
    return n


def ks(h):
    a = b = m = 0.0
    for x, y in zip(h, H):
        a += x; b += y; m = max(m, abs(a - b))
    return m


def chi(h):
    return sum((lp_c.get(k, 0) - n_lp * h[k - 1]) ** 2 / (n_lp * h[k - 1]) for k in range(1, 13) if h[k - 1] > 0)


rows = []
keys = os.path.join(lp2.LP, "data", "keys")
for f in sorted(glob.glob(os.path.join(keys, "armada18", "*.txt")) + glob.glob(os.path.join(keys, "armada19", "*.txt"))):
    name = os.path.basename(f)[:-4]
    if "latin" in name:
        continue
    t = open(f, encoding="utf-8", errors="ignore").read()
    ws = re.findall(r"[A-Z]+", t[int(len(t) * 0.15):int(len(t) * 0.85)].upper())
    if len(ws) < 20000:
        continue
    cl = collections.Counter(min(len(w), 12) for w in ws); cm = collections.Counter(min(mg_len(w), 12) for w in ws)
    hl = [cl.get(k, 0) / len(ws) for k in range(1, 13)]; hm = [cm.get(k, 0) / len(ws) for k in range(1, 13)]
    rows.append({"text": name, "words": len(ws), "ks_letterwise": ks(hl), "chi2_letterwise": chi(hl),
                 "ks_multigraph": ks(hm), "chi2_multigraph": chi(hm), "two_rune_letterwise": hl[1],
                 "two_rune_multigraph": hm[1], "mean_letterwise": sum(map(len, ws)) / len(ws),
                 "mean_multigraph": sum(map(mg_len, ws)) / len(ws)})
rows.sort(key=lambda r: r["ks_letterwise"])
out = {"lp2": {"words": n_lp, "mean": sum(map(len, W)) / n_lp, "one_rune_words": lp_c[1],
               "hist_pct_len1to8": [round(100 * x, 1) for x in H[:8]]},
       "ks_critical_05": 1.36 / math.sqrt(n_lp), "texts": rows,
       "letterwise_fits_better_by_ks": sum(r["ks_letterwise"] < r["ks_multigraph"] for r in rows),
       "letterwise_fits_better_by_chi2": sum(r["chi2_letterwise"] < r["chi2_multigraph"] for r in rows),
       "n_texts": len(rows), "best_multigraph_ks": min(r["ks_multigraph"] for r in rows),
       "best_multigraph_chi2": min(r["chi2_multigraph"] for r in rows)}
json.dump(out, open(os.path.join(HERE, "wordlen.json"), "w"), indent=1)
print("LP2:", out["lp2"], " KS critical %.4f" % out["ks_critical_05"])
print(f"letter-wise fits better in {out['letterwise_fits_better_by_ks']}/{len(rows)} texts (KS), {out['letterwise_fits_better_by_chi2']}/{len(rows)} (chi2)")
for r in rows[:5]:
    print(f"  {r['text']:36s} letter-wise KS {r['ks_letterwise']:.4f} chi2 {r['chi2_letterwise']:6.1f} | multigraph KS {r['ks_multigraph']:.4f} chi2 {r['chi2_multigraph']:6.1f} | 2-rune words {100 * r['two_rune_letterwise']:.1f}% vs {100 * r['two_rune_multigraph']:.1f}%")
print("best multigraph fit of any text: KS %.4f, chi2 %.1f" % (out["best_multigraph_ks"], out["best_multigraph_chi2"]))
