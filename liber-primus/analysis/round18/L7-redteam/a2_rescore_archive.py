"""L7 / sub-attack A-iii,A-iv — re-score every archived sweep candidate under non-English
models, AND measure whether that exercise has any power at all.

`campaign14/REDTEAM-PROPOSALS.md` (~line 155) queued "language-agnostic and non-English
re-scoring of all sweep bests" and it was never run for the post-Round-10b sweeps. Round 10b
lane B6 ran it over the 75 candidate strings that existed then, and recorded a HANDOFF
REQUIREMENT: future harnesses must persist a language-agnostic statistic at sweep time. This
script (1) checks whether the sweeps that ran afterwards complied, (2) does the re-scoring on
whatever they did keep, and (3) computes the POWER of that re-scoring from A1's measured
per-register score distributions and each sweep's own recorded score histogram.

    python3 a2_rescore_archive.py     # writes out_a2.json
"""
import os, sys, json, glob, math, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
B6 = os.path.join(LP, "analysis", "round10b", "B6-non-english-plaintext")
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"), B6):
    sys.path.insert(0, p)

import numpy as np                              # noqa: E402
from lp import gematria as gp                   # noqa: E402
from lp import score as _score                  # noqa: E402
import skipdecode as sk                         # noqa: E402
import detectors as D                           # noqa: E402
from a1_scorer_language import build_panels     # noqa: E402

N = gp.N
Q = _score.default()
RNG = np.random.default_rng(3301)

# ------------------------------------------------------------------ the LMs
LM_PANELS = ["EN_MODERN", "LATIN", "OE", "DE", "CY", "LP1_REAL"]


def build_lms():
    panels = build_panels()
    lms = {}
    for k in LM_PANELS:
        lms[k] = D.build_trigram(np.array(panels[k], dtype=np.int64))
    return lms, {k: len(panels[k]) for k in LM_PANELS}


def score_lm(lm, r):
    if len(r) < 3:
        return -9.9
    return float(lm[r[:-2], r[1:-1], r[2:]].mean())


def ioc_n(r):
    if len(r) < 2:
        return 0.0
    c = np.bincount(r, minlength=N).astype(float)
    n = len(r)
    return float(N * (c * (c - 1)).sum() / (n * (n - 1)))


# --------------------------------------------------- harvest archived candidates
def harvest():
    """Every stored candidate decode string in the post-B6 sweeps, plus what
    non-English statistic (if any) each sweep persisted alongside it."""
    cands, provenance = [], []

    def add(src, rows, key, extra=None):
        n = 0
        for r in rows:
            h = r.get(key)
            if isinstance(h, str) and len(h) >= 20:
                cands.append({"source": src, "text": h, "score": r.get("score"),
                              "meta": {k: r[k] for k in (extra or []) if k in r}})
                n += 1
        return n

    reg = []
    for f, key, field in [
        ("analysis/round13/B04/results_A.json", "top50", "head"),
        ("analysis/round13/B04/results_B.json", "top50", "head"),
        ("analysis/round13/B04/results_C.json", "top50", "head"),
        ("analysis/round13/B04/results_D.json", "top50", "head"),
        ("analysis/round16/KDF/results_A.json", "top50", "head"),
        ("analysis/round16/prng/results.json", "top20", "head"),
        ("analysis/round17/P0_dense/results_big.json", "top20", "head"),
        ("analysis/round17/P0_dense/results_small.json", "top20", "head"),
        ("analysis/round17/P0_dense/results_big_ms8.json", "top20", "head"),
        ("analysis/round17/P0_dense/results_small_ms8.json", "top20", "head"),
        ("analysis/round17/P0_dense/results_all_nib.json", "top20", "head"),
        ("analysis/round17/P1_blockchain/results.json", "top20", "head"),
        ("analysis/round17/P2_beacons/results.json", "top20", "head"),
        ("analysis/round17/P3_tables/results.json", "top20", "head"),
        ("analysis/round17/P3_tables/results_ms8.json", "top20", "head"),
    ]:
        path = os.path.join(LP, f)
        if not os.path.exists(path):
            reg.append({"file": f, "present": False})
            continue
        d = json.load(open(path, encoding="utf-8"))
        if isinstance(d, list):
            rows = d
        else:
            rows = d.get(key) or []
        if isinstance(rows, dict):
            rows = list(rows.values())
        rows = [r for r in rows if isinstance(r, dict)]
        n = add(f, rows, field, extra=["seed", "gen", "red", "offset", "pad", "variant"])
        # did this sweep persist ANY language-agnostic statistic per candidate?
        keys = set()
        for r in rows[:5]:
            if isinstance(r, dict):
                keys |= set(r)
        agnostic = sorted(k for k in keys
                          if any(t in k.lower() for t in ("ioc", "lang", "lm_", "entropy",
                                                          "distinct", "agnostic")))
        reg.append({"file": f, "present": True, "n_rows": len(rows),
                    "n_candidates_ge20": n, "row_keys": sorted(keys),
                    "language_agnostic_fields": agnostic,
                    "b6_handoff_complied": bool(agnostic)})
    return cands, reg


# ------------------------------------------------------------------- nulls
def null_table(lms, lengths, n=400):
    """z-null for each (LM, length): random rune strings."""
    out = {}
    for L in lengths:
        draws = RNG.integers(0, N, size=(n, L))
        for name, lm in lms.items():
            v = np.array([score_lm(lm, draws[i]) for i in range(n)])
            out[(name, L)] = (float(v.mean()), float(v.std()), float(v.max()))
        v = np.array([ioc_n(draws[i]) for i in range(n)])
        out[("IOC", L)] = (float(v.mean()), float(v.std()), float(v.max()))
    return out


# ------------------------------------------------------- power of the re-scoring
def rescoring_power(a1, sweeps):
    """For each register A1 measured, where would the CORRECT key have landed in each
    sweep's own recorded English-score distribution, and would it have been stored?"""
    out = []
    for key, s in a1["summary"].items():
        if s["L"] != 120:
            continue
        for sw in sweeps:
            mu, sd, n = sw["mean"], sw["sd"], sw["n"]
            if sd <= 0:
                continue
            z = (s["median_score"] - mu) / sd
            # expected rank of that score among n draws of the sweep's own null
            p_exceed = 0.5 * math.erfc(z / math.sqrt(2))
            exp_rank = max(1.0, n * p_exceed)
            stored = sw.get("stored_top_n")
            cutoff = sw.get("stored_cutoff_score")
            out.append({
                "register": s["panel"], "L": s["L"],
                "correct_key_median_score": s["median_score"],
                "sweep": sw["name"], "sweep_mean": mu, "sweep_sd": sd, "sweep_n": n,
                "z_vs_sweep_null": z,
                "expected_rank_among_sweep_decodes": exp_rank,
                "stored_top_n": stored, "stored_cutoff_score": cutoff,
                "would_be_stored": (cutoff is not None
                                    and s["median_score"] >= cutoff),
                "clears_repo_bar_-5.5": s["median_score"] >= -5.5,
            })
    return out


def main():
    print("building rune-space LMs ...")
    lms, sizes = build_lms()
    print("  corpus sizes:", sizes)

    cands, reg = harvest()
    print(f"harvested {len(cands)} archived candidate strings from "
          f"{sum(1 for r in reg if r.get('present'))} files")

    lengths = sorted({len(sk.eng_to_idx(c['text'])) for c in cands})
    lengths = sorted({min(lengths, key=lambda x: abs(x - L)) for L in lengths})
    print("  candidate rune lengths:", lengths[:20], "...")
    nulls = null_table(lms, lengths)

    flags = []
    for c in cands:
        r = np.array(sk.eng_to_idx(c["text"]), dtype=np.int64)
        L = len(r)
        Lk = min(lengths, key=lambda x: abs(x - L))
        row = {"source": c["source"], "text": c["text"][:64],
               "english_score": c["score"], "n_runes": L, "meta": c["meta"], "z": {}}
        for name, lm in lms.items():
            m, s, mx = nulls[(name, Lk)]
            v = score_lm(lm, r)
            row["z"][name] = {"val": v, "z": (v - m) / s if s else 0.0,
                              "above_null_max": v > mx}
        m, s, mx = nulls[("IOC", Lk)]
        v = ioc_n(r)
        row["z"]["IOC"] = {"val": v, "z": (v - m) / s if s else 0.0,
                           "above_null_max": v > mx}
        hit = [k for k, z in row["z"].items()
               if z["z"] >= 4.0 and z["above_null_max"]]
        if hit:
            row["flagged_by"] = hit
            flags.append(row)
        c["_row"] = row

    print(f"flags (z>=4.0 AND above null max): {len(flags)}")
    for f in flags[:20]:
        print("   ", f["source"], f["flagged_by"], f["text"][:40])

    # ---- language CONTRAST, against the archive's own empirical distribution.
    # A raw z against a random-rune null is confounded: every archived candidate is the
    # ENGLISH argmax of its sweep, so English-correlated models (OE, DE) light up by
    # selection alone. The question that matters is whether any candidate is MORE
    # Latin/OE/DE/Welsh-like than its own English-likeness already explains. Contrast
    # c_M = score_M - score_EN, standardised against the archive itself (which the repo's
    # own verdict says is 340 noise strings).
    contrast = {}
    for name in lms:
        if name == "EN_MODERN":
            continue
        vals = np.array([c["_row"]["z"][name]["val"] - c["_row"]["z"]["EN_MODERN"]["val"]
                         for c in cands])
        m, s = float(vals.mean()), float(vals.std())
        zc = (vals - m) / s if s else vals * 0
        order = np.argsort(-zc)[:5]
        contrast[name] = {
            "archive_mean": m, "archive_sd": s,
            "max_z_contrast": float(zc.max()),
            "top5": [{"source": cands[int(i)]["source"],
                      "text": cands[int(i)]["text"][:48],
                      "z_contrast": float(zc[int(i)])} for i in order],
            "n_over_3": int((zc >= 3.0).sum()), "n_over_4": int((zc >= 4.0).sum())}
        for c, z in zip(cands, zc):
            c["_row"]["z"].setdefault("_contrast", {})[name] = float(z)
    print("\nLANGUAGE CONTRAST vs the archive's own distribution (selection-corrected):")
    for k, v in contrast.items():
        print(f"  {k:10s} max z_contrast {v['max_z_contrast']:5.2f}  "
              f"n>=3: {v['n_over_3']}  n>=4: {v['n_over_4']}   best: "
              f"{v['top5'][0]['source'].split('/')[-2]} {v['top5'][0]['text'][:32]}")

    # ---- power of the exercise
    a1 = json.load(open(os.path.join(HERE, "out_a1.json"), encoding="utf-8"))
    sweeps = []

    d = json.load(open(os.path.join(LP, "analysis/round13/B04/results_A.json")))
    hs = d["hist_stats"]
    top = [r["score"] for r in d["top50"]]
    sweeps.append({"name": "B-04 stage A (round13)", "mean": hs["mean"], "sd": hs["sd"],
                   "n": hs["n"], "stored_top_n": len(top),
                   "stored_cutoff_score": min(top)})
    d = json.load(open(os.path.join(LP, "analysis/round16/KDF/results_A.json")))
    top = [r["score"] for r in d["top50"]]
    sweeps.append({"name": "R16-KDF stage A", "mean": d["sample_mean"], "sd": d["sample_sd"],
                   "n": d["n_decodes"], "stored_top_n": len(top),
                   "stored_cutoff_score": min(top)})
    d = json.load(open(os.path.join(LP, "analysis/round16/prng/results.json")))
    top = [r["score"] for r in d["top20"]]
    sweeps.append({"name": "R16-PRNG", "mean": d["null_mean"], "sd": 0.2305,
                   "n": d["total_decodes"], "stored_top_n": len(top),
                   "stored_cutoff_score": min(top),
                   "sd_note": "no per-decode sd stored; B-04 stage-A sd used"})

    power = rescoring_power(a1, sweeps)

    out = {"lane": "round18/L7-redteam/A2",
           "lm_corpus_sizes": sizes,
           "b6_handoff_compliance": reg,
           "n_candidates": len(cands),
           "flag_rule": "z >= 4.0 vs a length-matched 400-sample random-rune null AND above its max (B6's rule verbatim)",
           "flags": flags,
           "language_contrast": contrast,
           "all_candidates": [c["_row"] for c in cands],
           "rescoring_power": power,
           "sweeps_used": sweeps}
    json.dump(out, open(os.path.join(HERE, "out_a2.json"), "w"), indent=1)

    print("\nPOWER OF THE ARCHIVE RE-SCORING (would the correct key even be in the archive?)")
    print(f"{'register':14s} {'score':>7s} {'sweep':22s} {'z':>6s} {'exp.rank':>12s} {'stored?':>8s}")
    for p in power:
        if p["sweep"].startswith("B-04"):
            print(f"{p['register']:14s} {p['correct_key_median_score']:7.3f} "
                  f"{p['sweep']:22s} {p['z_vs_sweep_null']:6.2f} "
                  f"{p['expected_rank_among_sweep_decodes']:12.3g} "
                  f"{str(p['would_be_stored']):>8s}")
    print("\nwrote out_a2.json")


if __name__ == "__main__":
    main()
