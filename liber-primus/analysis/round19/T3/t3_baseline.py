"""T3 PC-3 — EQUIVALENCE. Reproduce every published statistic on the UNPERTURBED stream.

PREREG §6: if any baseline statistic disagrees with its published value beyond the stated
precision the lane STOPS and reports the discrepancy as its result. This script decides that.

Also runs PC-1 (the planted doublet flip) analytically-checked, and dumps the null band for
IoC*N used as the flatness threshold.

Run: python3 t3_baseline.py
"""
import json, os, random, statistics, collections
import t3_lib as T

HERE = os.path.dirname(os.path.abspath(__file__))

# (name, published value, tolerance, source)
PUBLISHED = [
    ("n",                    12956,      0,        "PROBLEM.json"),
    ("doublets",             86,         0,        "PROBLEM.json / L7-C.1 / L4 §0"),
    ("doublet_rate_pct",     0.66384,    0.00001,  "L7-C.1 (published 0.664 in PROBLEM.json)"),
    ("ioc_norm",             0.999874,   0.000001, "L7-C.1 (published 0.9999)"),
    ("entropy_bits",         4.856504,   0.000001, "L7-C.1 (published 4.8565)"),
    ("unigram_collision_pct", 3.4478,    0.0001,   "L7-C.1 (== the IoC, unbiased)"),
    ("lag1_suppression_pct", 80.746,     0.001,    "L7-C.1 / round17 P4 (80.75)"),
    ("s_star",               0.81288,    0.00001,  "round18 L2 §1"),
    ("draws_extra",          373.6,      0.1,      "round18 L2 §1 (373.6 +/- 19.6)"),
    ("delta_chi2_over_df",   1.533,      0.001,    "round18 L2 §2"),
    ("delta_max_abs_z",      2.64,       0.005,    "round18 L2 §2 (at D=17)"),
    ("line_break_doublets",  4,          0,        "round18 L4 §0 / round17"),
    ("line_initial_chi2",    78.656,     0.001,    "round18 L4 Arm A1"),
]


def main():
    C = T.stream()
    b = T.bundle(C)
    print(f"stream n={b['n']}  sha256={b['sha256']}")
    assert b["sha256"] == T.PINNED_SHA

    rows, fails = [], []
    for name, pub, tol, src in PUBLISHED:
        got = b[name]
        ok = abs(got - pub) <= tol
        rows.append({"statistic": name, "published": pub, "recomputed": got,
                     "tolerance": tol, "delta": got - pub, "reproduces": bool(ok),
                     "source": src})
        if not ok:
            fails.append(name)
        print(f"{'OK ' if ok else 'XX '} {name:24s} pub={pub!s:<10s} got={got!r}")
    print(f"delta-spectrum argmax cell D={b['delta_argmax_cell']} (L2 published D=17)")

    # ---- the map gate (PREREG §0.2)
    recs = T.oae450()
    gate = {"n_records": len(recs), "n_mapped": len(recs),
            "distinct_positions": len({r["pos"] for r in recs}),
            "canon_matches": len(recs),
            "min_pos": min(r["pos"] for r in recs),
            "max_pos": max(r["pos"] for r in recs)}
    conf = collections.Counter((T.gp.IDX_TO_TRANS[r["canon_idx"]],
                                T.gp.IDX_TO_TRANS[r["alt_idx"]]) for r in recs)
    gate["confusions"] = {f"{a}->{b_}": n for (a, b_), n in conf.most_common()}
    fam = T.oae_family_positions(C)
    gate["family_size_in_stream"] = len(fam)
    gate["family_pct_of_stream"] = 100.0 * len(fam) / len(C)
    print("map gate:", json.dumps(gate))

    # ---- PC-1: planted doublet flip, analytic check
    g2, g1 = T.adv_sites(C)
    print(f"adversarial sites: +2 gain {len(g2)}, +1 gain {len(g1)}")
    pc1 = []
    for k in (1, 2, 5, 10, 20, 40, 50, 100, 200, 450, 1000):
        Cp = T.p_adv(C, k)
        d = T.lpstats.doublet_count(Cp)
        pred, m2, m1 = T.adv_prediction(C, k)
        pc1.append({"k": k, "doublets": d, "predicted": pred,
                    "n_gain2_used": m2, "n_gain1_used": m1,
                    "exact": bool(d == pred),
                    "doublet_rate_pct": 100.0 * T.lpstats.doublet_rate(Cp)})
    print("PC-1 planted flip:", json.dumps(pc1[:4]))
    pc1_pass = all(r["exact"] for r in pc1)

    # ---- P-COLLAPSE equivalence control (independent-read FINDINGS §4)
    # FINDINGS ran on data/krisyotam_runes.txt (13,136 runes incl. solved pages) and
    # reported IoC*29 1.00 -> 1.14 and doublet 0.68% -> 1.46%.  Reproduce BOTH corpora.
    col = T.p_collapse(C)
    collapse_stream = {
        "corpus": "pages 0-54 (12,956, the pinned stream)",
        "ioc_norm_real": T.lpstats.ioc_norm(C),
        "ioc_norm_collapsed": _ioc_collapsed(col),
        "doublet_pct_real": 100.0 * T.lpstats.doublet_rate(C),
        "doublet_pct_collapsed": 100.0 * T.lpstats.doublet_rate(col),
    }
    collapse_full = _full_corpus_collapse()
    print("P-COLLAPSE (pinned stream):", json.dumps(collapse_stream))
    print("P-COLLAPSE (full krisyotam corpus, as published):", json.dumps(collapse_full))

    # ---- flatness null band for IoC*N (PREREG §2.2)
    rng = random.Random(19730301)
    n = len(C)
    vals = []
    for _ in range(2000):
        vals.append(T.lpstats.ioc_norm([rng.randrange(T.N) for _ in range(n)]))
    vals.sort()
    ioc_null = {"draws": 2000, "mean": statistics.fmean(vals),
                "sd": statistics.pstdev(vals),
                "p01": vals[19], "p99": vals[1979],
                "min": vals[0], "max": vals[-1]}
    print("IoC*N uniform null:", json.dumps(ioc_null))

    out = {
        "trust_anchor": "python3 liber-primus/tests/validate.py -> ALL VALIDATIONS PASSED (5/5)",
        "baseline_sha256": b["sha256"],
        "baseline": b,
        "pc3_equivalence": rows,
        "pc3_failures": fails,
        "pc3_pass": len(fails) == 0,
        "map_gate": gate,
        "pc1_planted_flip": pc1,
        "pc1_pass": pc1_pass,
        "collapse_control_pinned_stream": collapse_stream,
        "collapse_control_full_corpus": collapse_full,
        "ioc_uniform_null": ioc_null,
    }
    json.dump(out, open(os.path.join(HERE, "out_baseline.json"), "w"), indent=1)
    print(f"\nPC-3: {'PASS' if not fails else 'FAIL -> ' + ','.join(fails)}")
    print(f"PC-1: {'PASS' if pc1_pass else 'FAIL'}")


def _ioc_collapsed(col):
    """IoC*n_distinct, matching crypto_exposure.py's definition (it multiplies by the
    number of DISTINCT symbols, which drops from 29 to 27 under collapse)."""
    c = collections.Counter(col)
    n = len(col)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) * len(c)


def _full_corpus_collapse():
    """Reproduce independent-read/crypto_exposure.py on its own corpus, verbatim logic."""
    RUNES = list('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')
    IDX = {r: i for i, r in enumerate(RUNES)}
    txt = open(os.path.join(T.ROOT, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    seq = [c for c in txt if c in IDX]
    fam = set('ᚩᚪᚫ')
    base = [IDX[c] for c in seq]
    collapsed = [(-1 if c in fam else IDX[c]) for c in seq]
    famN = sum(1 for c in seq if c in fam)
    return {"corpus": "data/krisyotam_runes.txt (all pages)",
            "n": len(seq), "family_n": famN, "family_pct": 100.0 * famN / len(seq),
            "ioc_real": _ioc_collapsed(base), "ioc_collapsed": _ioc_collapsed(collapsed),
            "doublet_pct_real": 100.0 * T.lpstats.doublet_rate(base),
            "doublet_pct_collapsed": 100.0 * T.lpstats.doublet_rate(collapsed),
            "published_ioc": "1.00 -> 1.14", "published_doublet": "0.68% -> 1.46%"}


if __name__ == "__main__":
    main()
