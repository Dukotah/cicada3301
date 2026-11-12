"""Fresh-eyes audit, part 2: the one long repeat in LP2, calibrated against a word-aware null.

The repeat is the two-word phrase ᛞᛄᚢ-ᛒᛖᛁ (D J U - B E I): page 27 runes 28-33 and page 54 runes
70-75, the last two words of the unsolved book. Earlier records call it "chance, P ~ 13 %"
(ARMADA-20-FINDINGS) and "a 7-gram, p ~ 0.5 %" with the wrong runes (round43 F3). Output: repeats.json.
"""
import collections
import json
import os
import random

import lp2

HERE = os.path.dirname(os.path.abspath(__file__))
P = lp2.unsolved(); PI = lp2.idx(P)
U = [x for p in PI for x in p]; N = len(U)
ALL = lp2.idx(lp2.load_all())
pg = [k for k, p in enumerate(PI) for _ in p]
off = [j for p in PI for j in range(len(p))]
out = {}

# every repeated n-gram, n = 5..8
for n in (5, 6, 7, 8):
    d = collections.defaultdict(list)
    for i in range(N - n + 1):
        d[tuple(U[i:i + n])].append(i)
    rep = {k: v for k, v in d.items() if len(v) > 1}
    out[f"repeated_{n}grams"] = {"count": len(rep), "expected_uniform": N * (N - 1) / 2 / 29 ** n,
                                 "sites": [{"runes": " ".join(lp2.TR[x] for x in k),
                                            "at": [[pg[i], off[i]] for i in v]} for k, v in rep.items()] if n >= 6 else None}

# the repeat itself
a, b = 6555, 12950
assert U[a:a + 6] == U[b:b + 6] and b + 6 == N
out["the_repeat"] = {
    "runes": "ᛞᛄᚢ-ᛒᛖᛁ", "translit": "D J U - B E I", "site_1": {"page": pg[a], "offset": off[a], "flat": a},
    "site_2": {"page": pg[b], "offset": off[b], "flat": b, "note": "the last six runes of the unsolved stream"},
    "flat_distance": b - a, "factorisation": "5 x 1279",
    "seventh_rune": "site 1 is followed by AE; site 2 is followed by the first rune of the SOLVED page AN END, also AE "
                    "(a 1-in-29 coincidence across a cipher boundary, which is how a 13,041-rune count made it a '7-gram')",
    "next_after_site_1": lp2.TR[U[a + 6]], "first_rune_of_AN_END": lp2.TR[ALL[55][0]]}

# word-aware expectations with the cleartext skeleton held fixed
W = lp2.words(P); lens = [len(w) for w in W]
closed = collections.Counter()
for k in range(1, 7):
    pat = collections.Counter(tuple(lens[i:i + k]) for i in range(len(lens) - k + 1))
    for p_, c in pat.items():
        n = sum(p_)
        if n >= 5:
            closed[(k, min(n, 8))] += c * (c - 1) / 2 / 29 ** n
bflag = []
for w in W:
    bflag += [1] + [0] * (len(w) - 1)
bflag.append(1)
pat = collections.Counter(tuple(bflag[i:i + 7]) for i in range(N - 5))
out["expected_counts_under_uniform_runes"] = {
    "any_repeated_6gram": N * (N - 1) / 2 / 29 ** 6,
    "repeated_6gram_with_identical_word_boundary_pattern": sum(c * (c - 1) / 2 for c in pat.values()) / 29 ** 6,
    "closed_whole_word_repeat_ge6_runes": sum(v for (k, n), v in closed.items() if n >= 6),
    "closed_multiword_repeat_ge6_runes": sum(v for (k, n), v in closed.items() if n >= 6 and k >= 2)}

# what is actually observed among closed whole-word sequences
obs = []
for k in (1, 2, 3):
    d = collections.defaultdict(list)
    for i in range(len(W) - k + 1):
        key = tuple(tuple(w) for w in W[i:i + k])
        if sum(len(w) for w in key) >= 4:
            d[key].append(i)
    obs += [{"words": k, "runes": sum(len(w) for w in key), "word_index": v} for key, v in d.items() if len(v) > 1]
out["observed_closed_word_repeats_ge4_runes"] = obs
out["n_words"] = len(W)

# Monte Carlo cross-check: shuffle the runes, keep the skeleton
rng = random.Random(1); flat = U[:]; T = 3000; hit6 = hit5 = 0
for _ in range(T):
    rng.shuffle(flat)
    ws, j = [], 0
    for L in lens:
        ws.append(tuple(flat[j:j + L])); j += L
    m = 0
    for k in (1, 2):
        seen = set()
        for i in range(len(ws) - k + 1):
            key = ws[i:i + k]; n = sum(map(len, key))
            if n >= 5:
                key = tuple(key)
                if key in seen:
                    m = max(m, n)
                seen.add(key)
    hit6 += m >= 6; hit5 += m >= 5
out["monte_carlo"] = {"trials": T, "any_closed_repeat_ge6": hit6 / T, "any_closed_repeat_ge5": hit5 / T}

# does any reset at a visible boundary put both sites at the same key position? (it does not)
out["offsets_of_the_two_sites"] = {"page": [28, 70], "line": [8, 2], "section": [28, 3310], "sentence": [9, "~290"]}
json.dump(out, open(os.path.join(HERE, "repeats.json"), "w"), indent=1, ensure_ascii=False)
e = out["expected_counts_under_uniform_runes"]
print("repeated 6-grams:", out["repeated_6grams"]["count"], " 7-grams:", out["repeated_7grams"]["count"])
print("expected: any 6-gram %.3f | same boundary pattern %.4f | closed whole-word >=6 runes %.2e" %
      (e["any_repeated_6gram"], e["repeated_6gram_with_identical_word_boundary_pattern"], e["closed_whole_word_repeat_ge6_runes"]))
print("observed closed word repeats (>=4 runes):", obs, " MC:", out["monte_carlo"])
print("7th rune:", out["the_repeat"]["next_after_site_1"], "/ AN END starts with", out["the_repeat"]["first_rune_of_AN_END"])
