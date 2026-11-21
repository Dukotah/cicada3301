"""R44 / W2-C1 — ADDED specificity control for the S1/S3 battery crossers (the R22-D
H7/H8 move: a registered bar-crosser is tested against the reference class it actually
lives in before the oracle reads it; the registered result is NOT altered).

Question: do S1 (presence-gap variance) and S3 (type-sequence compressibility) fire on
ANY 'sectioned book' whose illustration plates change per chapter — i.e., do they detect
hidden signal, or just overt sectioning?

Control model (independent of the catalog): the canon's own section structure.
krisyotam_runes.txt marks sections with '&' / '$' inside page segments. We map each page
(relikd image) to its canon section index, then build 10,000 control books: each section
independently assigned a random plate = (motif type t_s, per-page count c_s) with
P(no art)=p0 matched to the observed fraction of artless sections; S1/S3 computed on each
control book against the SAME uniform/permutation nulls used for the real reads
(statistic-level p via the same code path, 2,000 inner draws for tractability).
Output: fraction of control books whose S1/S3 p-values are as small as the real ones.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))

import battery as BT
from lp import gematria as gp

OUT = os.path.join(CELL, "results")
streams = json.load(open(os.path.join(OUT, "streams.json")))

# ---- canon sections per page ----
txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
segs = txt.split("%")
IMG2SEG = {p: p for p in range(50)}
IMG2SEG.update({50: None, 51: 50, 52: 51, 53: 52, 54: 53, 55: 54})
sec = 0
page_section = {}
for i, s in enumerate(segs):
    # a '&'/'$' in a segment closes a section at that page
    for p, g in IMG2SEG.items():
        if g == i:
            page_section[p] = sec
    sec += s.count("&") + s.count("$")
page_section[50] = page_section.get(49, 0)  # runeless page inherits its neighbour's section
sections = sorted(set(page_section.values()))
n_sec = len(sections)
sec_pages = {s: [p for p in range(56) if page_section[p] == s] for s in sections}

# observed stats (same code paths, smaller inner draws for the outer loop)
BT.NDRAW = 2000
rng = np.random.default_rng(3301 + 77)
obs_S1 = BT.S1_presence_gaps(streams["motif_pages"], rng=np.random.default_rng(7))
obs_S3 = BT.S3_zlib_type(streams["T1"], rng=np.random.default_rng(8))

TYPES = ["cross", "tree", "insect", "other_figural", "corpse_figure"]
p0 = 18 / 56  # observed artless-page fraction (16-21, 23, 28-31, 33-39)

N_BOOKS = 300
hits1 = hits3 = 0
S1s, S3s = [], []
for b in range(N_BOOKS):
    present, T1 = [], []
    for s in sections:
        if rng.random() < p0:
            continue
        t = TYPES[rng.integers(0, len(TYPES))]
        c = int(rng.integers(1, 5))
        for p in sec_pages[s]:
            present.append(p)
            T1 += [t] * c
    if len(present) < 4 or len(set(T1)) < 2:
        continue
    s1 = BT.S1_presence_gaps(present, rng=np.random.default_rng(1000 + b))
    s3 = BT.S3_zlib_type(T1, rng=np.random.default_rng(2000 + b))
    S1s.append(s1); S3s.append(s3)
    if s1 <= obs_S1:
        hits1 += 1
    if s3 <= obs_S3:
        hits3 += 1

res = dict(n_sections=n_sec, obs_S1=obs_S1, obs_S3=obs_S3, n_control_books=len(S1s),
           frac_S1_as_small=hits1 / len(S1s), frac_S3_as_small=hits3 / len(S3s),
           median_S1=float(np.median(S1s)), median_S3=float(np.median(S3s)),
           frac_S1_below_bar=float(np.mean(np.asarray(S1s) < 0.01 / 6)),
           frac_S3_below_bar=float(np.mean(np.asarray(S3s) < 0.01 / 6)),
           page_section={str(k): v for k, v in page_section.items()})
json.dump(res, open(os.path.join(OUT, "control_specificity.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "page_section"}, indent=1))
