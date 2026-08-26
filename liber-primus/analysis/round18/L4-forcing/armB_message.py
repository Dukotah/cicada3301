"""Round 18 / L4-FORCING — Arm B: read the positional subsets AS A MESSAGE.

Arm A asks "is this subset distributionally odd". Arm B asks the stronger, more
specific question the original C-02 proposal never posed: does the subset SAY
anything. Six families, each swept over the full Gematria-Primus variant set and
adjudicated against a max-statistic null so that multiplicity inside a family is
handled exactly rather than by a Bonferroni fudge.

Variant set per read (232):
    direction  forward / reversed
    involution identity / Atbash (i -> 28-i)
    shift      29 Caesar shifts on rune indices
    nulls      keep / drop the F rune (the LP interrupter convention; this is the
               keyless analogue of the skip-aware beam, which is a KEYED instrument
               and therefore not applicable to a keyless acrostic read)

Scoring is on rune indices mapped through the Gematria Primus, never on a re-parsed
transliteration string (AGENTS.md §5 — 7 of 29 runes are two characters).

Gate (pre-registered, three-part conjunction):
    observed family max must (i) exceed ALL null replicate maxima,
    (ii) exceed the Gumbel bar fitted to those null maxima at alpha = 4.762e-5,
    (iii) be reported against benchmark/null.py: threshold_for(n_variants).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "benchmark"))
from lp import gematria as gp, score as sc  # noqa: E402
from parse_structure import Geometry  # noqa: E402

N = 29
ALPHA_TEST = 0.001 / 21
Q = sc.default()
TR = [gp.IDX_TO_TRANS[i] for i in range(N)]
F = gp.RUNE_TO_IDX[gp.INTERRUPTER]


def variants(seq):
    """Yield (label, translit) for all 232 Gematria-Primus reads of one rune list."""
    if len(seq) < 4:
        return
    a = np.asarray(seq, dtype=np.int16)
    for dlab, d in (("fwd", a), ("rev", a[::-1])):
        for ilab, inv in (("id", d), ("atb", (28 - d) % N)):
            for drop in (False, True):
                b = inv[inv != F] if drop else inv
                if len(b) < 4:
                    continue
                for k in range(N):
                    c = (b + k) % N
                    yield (f"{dlab}/{ilab}/{'dropF' if drop else 'keepF'}/+{k}",
                           "".join(TR[v] for v in c))


def family_max(reads):
    best = (-999.0, None, None)
    nvar = 0
    for ri, seq in enumerate(reads):
        for lab, t in variants(seq):
            nvar += 1
            s = Q.score_norm(t)
            if s > best[0]:
                best = (s, ri, lab)
    return best, nvar


# ------------------------------------------------------------------ families
def build_families(g):
    x = g.runes
    sub = g.subsets()
    pl = g.pages_lines()
    fam = {}

    fam["B1_line_initial_sequence"] = [[x[i] for i in sub["A1_line_initial"]]]

    fam["B2_per_page_acrostic"] = [[L[0] for L in page] for page in pl]

    diag = []
    for page in pl:
        diag.append([L[k] for k, L in enumerate(page) if k < len(L)])
        diag.append([L[len(L) - 1 - k] for k, L in enumerate(page) if k < len(L)])
    fam["B3_diagonals"] = [d for d in diag if len(d) >= 4]

    ini = [x[i] for i in sub["A1_line_initial"]]
    every = []
    for M in range(2, 13):
        for ph in range(M):
            every.append(ini[ph::M])
    fam["B4_every_Nth_line_initial"] = [e for e in every if len(e) >= 4]

    fam["B5_page_initial_and_final"] = [[x[i] for i in sub["A5_page_initial"]],
                                        [x[i] for i in sub["A6_page_final"]]]
    fam["B6_word_initial_and_final"] = [[x[i] for i in sub["A3_word_initial"]],
                                        [x[i] for i in sub["A4_word_final"]]]
    return fam


def gumbel_bar(nullmax, alpha):
    m = float(np.mean(nullmax)); s = float(np.std(nullmax))
    beta = s * math.sqrt(6) / math.pi
    mu = m - beta * 0.5772156649015329
    return mu + beta * (-math.log(-math.log(1 - alpha))), mu, beta


def run(nnull=2000, seed=3301, only=None):
    from null import threshold_for
    g = Geometry()
    x = np.array(g.runes)
    rng = np.random.default_rng(seed)
    fams = build_families(g)
    ckpt = os.path.join(HERE, "results_armB.json")
    out = {}
    if os.path.exists(ckpt):
        try:
            out = json.load(open(ckpt)).get("families", {})
        except Exception:
            out = {}
    for name, reads in fams.items():
        if only and name not in only:
            continue
        if name in out:
            print(f"{name:30s} [checkpointed, skipping]")
            continue
        (best, ri, lab), nvar = family_max(reads)
        nn = nnull if len(reads) * max(len(r) for r in reads) < 5000 else max(400, nnull // 2)
        nulls = np.empty(nn)
        lens = [len(r) for r in reads]
        for i in range(nn):
            fake = [x[rng.choice(len(x), L, replace=False)].tolist() for L in lens]
            nulls[i] = family_max(fake)[0][0]
        bar, mu, beta = gumbel_bar(nulls, ALPHA_TEST)
        tf = threshold_for(nvar)
        passes = (best > nulls.max()) and (best > bar)
        out[name] = {
            "n_reads": len(reads), "n_variants": nvar,
            "best_score_norm": best, "best_read_index": ri, "best_variant": lab,
            "best_translit_head": "".join(
                TR[v] for v in reads[ri][:40]) if ri is not None else None,
            "null_replicates": int(nn),
            "null_max_mean": float(nulls.mean()), "null_max_sd": float(nulls.std()),
            "null_max_max": float(nulls.max()),
            "gumbel_bar_alpha_prereg": bar,
            "benchmark_threshold_for_nvariants": tf,
            "verdict": "HIT" if passes else "NEGATIVE",
        }
        print(f"{name:30s} nvar={nvar:6d}  best={best:7.3f} [{lab}]  "
              f"null max={nulls.max():7.3f} mean={nulls.mean():7.3f}  "
              f"bar={bar:7.3f}  -> {out[name]['verdict']}", flush=True)
        json.dump({"alpha_test": ALPHA_TEST, "families": out}, open(ckpt, "w"), indent=2)
    return out


def control():
    """Instrument gate: plant real English in a 594-rune acrostic and confirm the
    family-max pipeline recovers it above the same bar."""
    g = Geometry()
    x = np.array(g.runes)
    rng = np.random.default_rng(11)
    txt = ("THEPRIMESARESACREDTOTALLYWITHINTHEDEEPWEBTHEREEXISTSAMAPTHATISNOTAMAP"
           "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATISNOTAPAGEBELIEVENOTHING")
    msg = gp.keyword_to_indices(txt)
    while len(msg) < 594:
        msg = msg + msg
    msg = msg[:594]
    from null import threshold_for
    rows = []
    for shift in (0, 7):
        seq = [(v + shift) % N for v in msg]
        (best, ri, lab), nvar = family_max([seq])
        nulls = np.array([family_max([x[rng.choice(len(x), 594, replace=False)].tolist()])[0][0]
                          for _ in range(300)])
        bar, _, _ = gumbel_bar(nulls, ALPHA_TEST)
        rows.append({"shift": shift, "best": best, "variant": lab,
                     "null_max": float(nulls.max()), "bar": bar,
                     "recovered": bool(best > nulls.max() and best > bar),
                     "threshold_for": threshold_for(nvar)})
        print(f"  control shift={shift}: best={best:.3f} [{lab}]  "
              f"null max={nulls.max():.3f}  bar={bar:.3f}  "
              f"recovered={rows[-1]['recovered']}")
    return rows


if __name__ == "__main__":
    nnull = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    print(f"Arm B — subsets read as a message   alpha_test={ALPHA_TEST:.4g}")
    print("POSITIVE CONTROL (planted English acrostic):")
    ctl = control()
    json.dump({"alpha_test": ALPHA_TEST, "control": ctl, "families": {}},
              open(os.path.join(HERE, "results_armB_control.json"), "w"), indent=2)
    print()
    res = run(nnull=nnull)
    json.dump({"alpha_test": ALPHA_TEST, "control": ctl, "families": res},
              open(os.path.join(HERE, "results_armB.json"), "w"), indent=2)
    print("wrote results_armB.json")
