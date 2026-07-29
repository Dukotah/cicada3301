"""i9 CONTRARIAN-SKEPTIC — DOUBT THE UNIT OF ANALYSIS (inventory cardinality).

Premise (b'): the 29-rune INVENTORY cardinality is never tested by the alphabet
ORDER attack (relabeling 29 fixed symbols cannot detect that the TRUE inventory
is 28 or 30). If two visually/phonetically confusable ciphertext glyphs are in
fact ONE underlying symbol (scribal variant), their genuine doublets get
MISCOUNTED as non-doublets -> producing exactly the observed 0.66% deficit.
So the inventory error and the anomaly may be the same thing.

HEADLINE TEST:
  MERGE  each of the ~6 confusable Gematria-Primus pairs to one symbol; re-measure
         (i) adjacent-equal doublet rate and (ii) the validated i7 oracle P
         (fraction of adjacent pairs in the PARABLE-learned LEGAL bigram set).
  SPLIT  the 2-3 highest-freq runes into two context classes (position parity /
         preceding-rune class); re-measure doublet rate + P.
CONTROLS: 20 RANDOM-pair merges and random-binary splits -> null bands.

A real inventory error surfaces as EXACTLY ONE operation shifting the 0.66%
doublet rate TOWARD the 3.45% baseline OR lifting P off its ~0.09 floor, BEATING
the random-operation control percentile.

deficit_explained=true ONLY if one confusable merge normalizes the deficit past
the random-merge control band. Honest null = the 29-inventory is correct and the
deficit is intrinsic.

Run: PYTHONUTF8=1 python analysis/recon/i9_inventory/inventory_attack.py
"""
import os
import sys
import json
import random
from collections import Counter

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa

N = gp.N
KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")

# ---------------------------------------------------------------- load corpus
def load_pages_idx():
    segs = open(KRIS, encoding="utf-8").read().split("%")
    pages = [gp.runes_to_indices(s) for s in segs]
    pages = [p for p in pages if p]
    return pages

PAGES = load_pages_idx()
UNSOLVED = [p for p in PAGES[:55]]           # per-page (keep boundaries)
CORPUS = [i for p in UNSOLVED for i in p]    # flat 0-54
PARABLE = PAGES[56]                          # English-in-runes ground truth

# LEGAL bigram set from PARABLE only (identical to i7 oracle)
LEGAL = {(a, b) for a, b in zip(PARABLE, PARABLE[1:])}

# --------------------------------------------------------------- metrics
def doublet_pct(pages):
    """Adjacent-equal rate as %, computed WITHIN each page (no cross-page pairs)."""
    d = 0
    tot = 0
    for p in pages:
        for a, b in zip(p, p[1:]):
            tot += 1
            if a == b:
                d += 1
    return 100.0 * d / tot if tot else 0.0

def oracle_P(pages, legal):
    hit = 0
    tot = 0
    for p in pages:
        for a, b in zip(p, p[1:]):
            tot += 1
            if (a, b) in legal:
                hit += 1
    return hit / tot if tot else 0.0

# --------------------------------------------------------------- MERGE
def apply_merge(pages, keep, drop):
    """Relabel every `drop` index to `keep` (they become one symbol)."""
    return [[keep if x == drop else x for x in p] for p in pages]

def remap_legal_merge(legal, keep, drop):
    """Project the LEGAL bigram set through the same merge so P is measured on a
    consistent alphabet (drop -> keep on both sides of every legal pair)."""
    m = lambda x: keep if x == drop else x
    return {(m(a), m(b)) for (a, b) in legal}

# --------------------------------------------------------------- SPLIT
def apply_split_parity(pages, target):
    """Split `target` into two labels by absolute position parity within page.
    New label uses index N + something; we relabel to fresh ints to keep them
    distinct from all existing symbols."""
    A, B = target, N + target   # even-position keeps target, odd -> N+target
    out = []
    for p in pages:
        row = []
        for pos, x in enumerate(p):
            if x == target:
                row.append(A if pos % 2 == 0 else B)
            else:
                row.append(x)
        out.append(row)
    return out

def apply_split_prevclass(pages, target):
    """Split `target` by parity of the PRECEDING rune's index (context class).
    Position 0 defaults to the even class."""
    A, B = target, N + target
    out = []
    for p in pages:
        row = []
        prev = None
        for x in p:
            if x == target:
                cls = 0 if (prev is None or prev % 2 == 0) else 1
                row.append(A if cls == 0 else B)
            else:
                row.append(x)
            prev = x
        out.append(row)
    return out

# --------------------------------------------------------------- confusable pairs
# (keep_idx, drop_idx, label) — the ~6 visually/phonetically confusable GP pairs.
def T(name):
    for i, _, t, _ in gp.GEMATRIA:
        if t == name:
            return i
    raise KeyError(name)

CONFUSABLE = [
    ("os/ac (O ~ A)",        T("O"),  T("A")),
    ("eoh/ior (EO ~ IA)",    T("EO"), T("IA")),
    ("ior/ear (IA ~ EA)",    T("IA"), T("EA")),
    ("wynn/peordh (W ~ P)",  T("W"),  T("P")),
    ("is/eoh (I ~ EO)",      T("I"),  T("EO")),
    ("ing/daeg (NG ~ D)",    T("NG"), T("D")),
    ("ac/aesc (A ~ AE)",     T("A"),  T("AE")),
]

# --------------------------------------------------------------- run
def run():
    base_d = doublet_pct(UNSOLVED)
    base_P = oracle_P(UNSOLVED, LEGAL)
    random_d = 100.0 / N  # 3.448

    par_d = doublet_pct([PARABLE])
    par_P = oracle_P([PARABLE], LEGAL)

    report = {
        "baseline": {
            "doublet_pct": round(base_d, 4),
            "oracle_P": round(base_P, 4),
            "random_doublet_pct": round(random_d, 4),
            "parable_doublet_pct": round(par_d, 4),
            "parable_P": round(par_P, 4),
            "n_runes": len(CORPUS),
        },
        "confusable_merges": [],
        "splits": [],
        "controls": {},
    }

    # ---- CONFUSABLE MERGES
    for name, keep, drop in CONFUSABLE:
        merged = apply_merge(UNSOLVED, keep, drop)
        legalm = remap_legal_merge(LEGAL, keep, drop)
        d = doublet_pct(merged)
        P = oracle_P(merged, legalm)
        report["confusable_merges"].append({
            "pair": name, "keep": keep, "drop": drop,
            "doublet_pct": round(d, 4), "oracle_P": round(P, 4),
            "d_delta_vs_base": round(d - base_d, 4),
            "P_delta_vs_base": round(P - base_P, 4),
        })

    # ---- CONTROL: 20 random-pair merges -> null band for merge effect
    rng = random.Random(3301)
    ctrl_d = []
    ctrl_P = []
    for _ in range(20):
        a, b = rng.sample(range(N), 2)
        merged = apply_merge(UNSOLVED, a, b)
        legalm = remap_legal_merge(LEGAL, a, b)
        ctrl_d.append(doublet_pct(merged))
        ctrl_P.append(oracle_P(merged, legalm))
    ctrl_d.sort(); ctrl_P.sort()
    report["controls"]["random_merge"] = {
        "d_mean": round(sum(ctrl_d) / len(ctrl_d), 4),
        "d_min": round(ctrl_d[0], 4), "d_max": round(ctrl_d[-1], 4),
        "d_p95": round(ctrl_d[int(0.95 * len(ctrl_d))], 4),
        "P_mean": round(sum(ctrl_P) / len(ctrl_P), 4),
        "P_max": round(ctrl_P[-1], 4),
    }

    # percentile of each confusable merge vs the random-merge d distribution
    for row in report["confusable_merges"]:
        pct = 100.0 * sum(1 for x in ctrl_d if x <= row["doublet_pct"]) / len(ctrl_d)
        row["d_control_percentile"] = round(pct, 1)
        pctP = 100.0 * sum(1 for x in ctrl_P if x <= row["oracle_P"]) / len(ctrl_P)
        row["P_control_percentile"] = round(pctP, 1)

    # ---- SPLITS on top-3 highest-freq runes
    cnt = Counter(CORPUS)
    top3 = [i for i, _ in cnt.most_common(3)]
    for target in top3:
        for split_name, fn in (("parity", apply_split_parity),
                               ("prevclass", apply_split_prevclass)):
            sp = fn(UNSOLVED, target)
            d = doublet_pct(sp)
            P = oracle_P(sp, LEGAL)  # split introduces fresh symbols; legal unaffected
            report["splits"].append({
                "target": target, "trans": gp.IDX_TO_TRANS[target],
                "method": split_name,
                "doublet_pct": round(d, 4), "oracle_P": round(P, 4),
                "d_delta_vs_base": round(d - base_d, 4),
            })

    # ---- CONTROL: 20 random-binary splits of a random top rune
    ctrl_sd = []
    for _ in range(20):
        target = rng.choice(top3)
        # random binary label per occurrence
        out = []
        for p in UNSOLVED:
            row = []
            for x in p:
                if x == target and rng.random() < 0.5:
                    row.append(N + target)
                else:
                    row.append(x)
            out.append(row)
        ctrl_sd.append(doublet_pct(out))
    ctrl_sd.sort()
    report["controls"]["random_split"] = {
        "d_mean": round(sum(ctrl_sd) / len(ctrl_sd), 4),
        "d_min": round(ctrl_sd[0], 4), "d_max": round(ctrl_sd[-1], 4),
    }

    # ---- VERDICT
    # A confusable merge is a HIT if it pushes doublet% clearly above the random
    # -merge control band (toward 3.45) OR lifts P above the random-merge P band.
    d_ctrl_hi = report["controls"]["random_merge"]["d_max"]
    P_ctrl_hi = report["controls"]["random_merge"]["P_max"]
    hits = []
    for row in report["confusable_merges"]:
        d_hit = row["doublet_pct"] > d_ctrl_hi and row["doublet_pct"] > base_d + 0.5
        P_hit = row["oracle_P"] > P_ctrl_hi + 0.02
        if d_hit or P_hit:
            hits.append({"pair": row["pair"], "d_hit": d_hit, "P_hit": P_hit,
                         "doublet_pct": row["doublet_pct"], "oracle_P": row["oracle_P"]})
    report["verdict"] = {
        "d_control_max": round(d_ctrl_hi, 4),
        "P_control_max": round(P_ctrl_hi, 4),
        "hits": hits,
        "deficit_explained": len(hits) > 0,
        "note": ("A single confusable merge that beats the random-merge control "
                 "band would identify a scribal-variant inventory error AS the "
                 "doublet deficit. No such merge = 29-inventory is correct and "
                 "the deficit is intrinsic."),
    }
    return report


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, indent=2))
    out = os.path.join(HERE, "results.json")
    with open(out, "w") as f:
        json.dump(r, f, indent=2)
