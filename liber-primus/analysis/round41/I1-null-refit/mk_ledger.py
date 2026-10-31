"""R41 I1: build ledger.json (lane row), ledger_patches.json (bar-of-record notes) and measured_ceiling_replacement.md from the lane outputs.  python mk_ledger.py"""
import json, os, math, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
fit, ctl, rej = J("fit.json"), J("control.json"), J("rejudged_rounds36_40.json")
fx = J("fixture_r13.json") if os.path.exists(os.path.join(HERE, "fixture_r13.json")) else {}
REC = fit["bar_of_record"]; C = fit["cells"]
f4 = lambda x: ("%.4f" % x)
rec = lambda L, rel, N: REC["L%d|%s" % (L, rel)]["N=%s" % N]["record"]
ID = "R41-I1-NULL-REFIT-SURVIVOR12"
rows = rej["rows"]
worst = max(rows, key=lambda r: r["margin_to_refit_actualN"])
q1a = fit["Q1a"]

result = {
    "population": "wrong-key seeds uniform over six generator families (bash 4.2 LP64, bash 4.2 ILP32, PHP mt_scale, mt_mod, php_scale, php_mod), real LP2 head, passed through pf_v4_12 at the frozen point, survivors decoded by beam_v3 panel_max under panel-R36",
    "heads_screened": 6 * 8126464, "survivor_draws_raw": fit["n_survivor_draws_raw"], "distinct_survivors_L120": fit["n_survivors"], "per_family_distinct": fit["per_family_survivors"],
    "L240_distinct_survivors": C["L240|keyskip1"]["n"],
    "survivor_median_pmax_L120": {"keyskip1": round(C["L120|keyskip1"]["median_pmax"], 3), "keyskip2": round(C["L120|keyskip2"]["median_pmax"], 3), "null12": 2.334},
    "fit_L120": {rel: {"mu": round(C["L120|" + rel]["mu"], 4), "beta": round(C["L120|" + rel]["beta"], 4), "beta_se": round(C["L120|" + rel]["beta_se"], 4), "k_tail": C["L120|" + rel]["k"]} for rel in ("keyskip1", "keyskip2")},
    "fit_L240": {rel: {"mu": round(C["L240|" + rel]["mu"], 4), "beta": round(C["L240|" + rel]["beta"], 4), "beta_se": round(C["L240|" + rel]["beta_se"], 4), "k_tail": C["L240|" + rel]["k"]} for rel in ("keyskip1", "keyskip2")},
    "bar_of_record_L120": {rel: {"N=131786": rec(120, rel, "131786"), "N=1e+05": rec(120, rel, "100000"), "N=1e+06": rec(120, rel, "1e+06"), "N=1e+09": rec(120, rel, "1e+09")} for rel in ("keyskip1", "keyskip2")},
    "bar_of_record_L240": {rel: {"N=131786": rec(240, rel, "131786"), "N=1e+06": rec(240, rel, "1e+06"), "N=1e+09": rec(240, rel, "1e+09")} for rel in ("keyskip1", "keyskip2")},
    "null12_bars_for_comparison": {"L120_N1e6": {"keyskip1": 9.102, "keyskip2": 8.999}, "L120_survivorN_69k": {"keyskip1": 8.130, "keyskip2": 8.044}, "L120_N131786": {"keyskip1": round(C["L120|keyskip1"]["null12"]["bar_N131786"], 3), "keyskip2": round(C["L120|keyskip2"]["null12"]["bar_N131786"], 3)}},
    "Q1a": {rel: {"refit_gumbel_bar_N131786": q1a[rel]["refit_bar_N131786"], "pooled_real_sweep_POT_bar_N131786": q1a[rel]["target_pooled_real_POT_bar_N131786"], "strict_pass": q1a[rel]["PASS_pooled"]} for rel in ("keyskip1", "keyskip2")},
    "Q1b": {"n_plants": ctl["n_plants"], "prefilter_pass": ctl["prefilter_pass_total"], "clear_both_bars_given_prefilter": ctl["pooled_clear_L120_given_prefilter"], "cells_below_19_of_20": ctl["cells_below_19"], "gate": ctl["gate_ge19_of_20_every_cell_both_L_path"]},
    "Q5": "fired in the conservative direction: observed real-sweep maxima sit 0.7-2.8 SE BELOW the Gumbel-implied location (11 of 12 store x relation cells negative; R37-I2 keyskip1 -2.78, R40-B1 keyskip2 -2.80), and the null's own tail counts are 2-4 SE below exponential expectation at q99.9 / q99.97 (xi_gpd about -0.13): the exponential tail over-predicts; the GPD sensitivity bar (about 6.8-7.0) is crossed by the real stores' own maxima (7.065, 7.098), so it cannot be the bar. Bar of record = the higher of the Gumbel refit and the pooled real-sweep POT line at L=120; Gumbel refit at L=240.",
    "rejudge": {"rows": rej["n_rows"], "cross_actualN": len(rej["any_cross_actualN"]), "cross_1e6": len(rej["any_cross_1e6"]), "smallest_margin_to_bar_at_actualN": {"row": "%s %s %s" % (worst["lane"], worst["cell"], worst["rel"]), "best_pmax": worst["best_pmax"], "refit_bar_actualN": worst["refit_bar_actualN"], "margin": worst["margin_to_refit_actualN"]},
                "kdf_flag_withdrawn": "R40-B3 KDF keyskip2 6.528 vs refit bar 7.435 at N=591 (stored null12 bar 6.342 had flagged it)"},
    "matched_null_fixture_R13": fx,
}
row = {
    "id": ID, "round": 41, "lane": "I1", "lane_dir": "I1-null-refit", "date": "2026-10-31", "status": "measured",
    "hypothesis": "A bar fitted on the population it is applied to (wrong-key seeds from the six generator families that pass pf_v4_12 on the real LP2 head and are decoded by beam_v3 panel_max under panel-R36) reproduces the survivors the real sweeps produce, and every Round 36-40 best row stays below it.",
    "positive_control": "failed",
    "control_detail": "480 plants (20 x 12 registers x 2 relations) through the real chunk path: 470/480 passed the pf_v4_12 screen; every one of the 470 cleared the bar of record at N=1e6 at BOTH L=120 and L=240 (min pmax120 12.35, min pmax240 17.71 against 10.46/10.49 and 10.05/10.35). The pre-registered gate (>=19/20 in every register x relation cell) fails in two cells, LATIN keyskip1 and OE keyskip2 (18/20 each), solely through screen misses (10 plants lost to the screen: EN_KJV 1, LP1_REAL 1, LATIN 2, OE 2, CY 1, EN_HALFVOWEL 1, GREEK 1, HEBREW 1; 7 of the 10 have a skip inside the 24-rune head).",
    "threshold": "Gumbel/POT bar of record at N=1e6 and at actual N (alpha 0.01); fixed in PREREG.md before the first draw",
    "threshold_fixed_in_advance": True,
    "result": result,
    "coverage": "48,758,784 wrong-key heads screened (8,126,464 per family x 6); 41,149 survivor draws, 40,482 distinct (key, family) decoded at L=120 under both relations and 5,194 distinct at L=240 (floors 40,000 / 5,000 met on distinct keys); 480 plants through the real chunk path; the three real-sweep survivor stores (R37-I2 131,786, R40-B1 142,283, R40-B3 33,308 rows per relation) used as the empirical comparison; 34 best rows re-judged (R36-B1, R37-I2, R40-B1, R40-B3, R40-C1 screened families).",
    "three_conditionals": {
        "key_space": "wrong keys drawn uniformly from six generator families (bash 4.2 LP64/ILP32 orbit prefixes, PHP mt_rand four cells over 2^32 seeds); a bar for survivors of the six-family mixture, not for any generator outside them and not for the unscreened (no-prefilter) or direct-stream populations",
        "transition_model": "beam_v3 panel_max keyskip1 and keyskip2 only, beam_w 400, lam_u 4, after pf_v4_12 (frozen point m=24, k=2, rel both); not the free relation",
        "adjudicator_register": "panel-R36 12 registers, pmax; L=120 and L=240 on LP2[:120] / LP2[:240] (nodes only at these two lengths; no extrapolation in L)",
    },
    "not_covered": "L other than 120 and 240; the free relation; direct (non-key) families (see benchmark/bars_matched.py); unscreened populations (null12 still describes shuffled-LP2 wrong keys with no prefilter, and its bars are not made stricter by this refit); draws are with replacement (1.6 % repeat keys, deduplicated for the fit); L=240 has no real-sweep survivor rows to compare, so its bar is the Gumbel refit alone (n about 5,194, bar SE about 0.2); bars at N>=1e6 are tail extrapolations (the observed tail is lighter than exponential, so they are conservative); the 1 % family-wise level at N~1.3e5 cannot be measured empirically (it would need ~100 independent sweeps of that size).",
    "reopens_if": "a sweep's survivor median or q99 departs from 2.80 / 4.76 (the population changed); a family beyond the six (for example Perl, Python MT, PHP with another seed range) is screened; the pf_v4_12 frozen point is changed; or a real sweep produces a survivor row above 9.0 at L=120 (re-decode at L=240 and re-judge against these bars).",
    "evidence": [
        "liber-primus/analysis/round41/I1-null-refit/PREREG.md", "liber-primus/analysis/round41/I1-null-refit/RESULTS.md",
        "liber-primus/analysis/round41/I1-null-refit/null_survivor12.json", "liber-primus/analysis/round41/I1-null-refit/fit.json",
        "liber-primus/analysis/round41/I1-null-refit/control.json", "liber-primus/analysis/round41/I1-null-refit/rejudged_rounds36_40.json",
        "liber-primus/analysis/round41/I1-null-refit/null_stream.jsonl", "liber-primus/analysis/round41/I1-null-refit/null_stream240.jsonl",
        "liber-primus/analysis/round34/I1-v3-null/bars_v3.py", "liber-primus/benchmark/bars_matched.py", "liber-primus/tests/test_null_refit.py"],
}
json.dump({"$comment": "R41 I1 lane row; the coordinator files it in LEDGER.json", "entries": [row]}, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)

# ---------------------------------------------------------------- patches
b_note = lambda extra="": ("R41-I1 bar of record (survivor12): the 'actual-N' / N=1e6 bars quoted from null12 for this row were fitted on shuffled-LP2 wrong keys with no prefilter and are superseded. "
                           "On the pf_v4_12-survivor population the L=120 bars are %s / %s at N=131,786, %s / %s at N=1e6 (keyskip1 / keyskip2). %s See [R41-I1] rejudged_rounds36_40.json: no best row crosses at its actual N or at 1e6." %
                           (rec(120, "keyskip1", "131786"), rec(120, "keyskip2", "131786"), rec(120, "keyskip1", "1e+06"), rec(120, "keyskip2", "1e+06"), extra))
R = {(r["lane"], r["cell"], r["rel"]): r for r in rows}


def rowsfor(lane, cells=None):
    return [r for r in rows if r["lane"] == lane and (cells is None or r["cell"] in cells)]


def txt(rs):
    return "; ".join("%s %s best %.3f vs refit bar %.3f at N=%d (%.3f at 1e6)" % (r["cell"], r["rel"][-1:], r["best_pmax"], r["refit_bar_actualN"], r["N_actual"], r["refit_bar_1e6"]) for r in rs)


P = []
def patch(i, cov, note=None):
    P.append({"id": i, "coverage_add": cov, **({"bar_of_record_note": note} if note else {})})

patch("R36-B1-ORBIT-12REG", "R41-I1 re-judge: " + txt(rowsfor("R36-B1")) + ". The stored 12-register 'actual-N' bars (8.130 / 8.044) were null12 quantities and were lenient (survivor population median 2.81, not 2.33); bar of record is now round41/I1-null-refit (survivor12). No verdict moves.", b_note())
patch("R35-B1-BASH-ORBIT-PFV4", "R41-I1: the 12-register 'actual-N' bar quoted for this sweep's stored survivors (8.044) is superseded by the survivor12 bar of record (9.385 at N=69,017 for keyskip2, 9.367 for keyskip1); the stored best (7.065) is below it.")
patch("R37-I2-PFV4-12REG-ORBIT", "R41-I1 re-judge: " + txt(rowsfor("R37-I2")) + ". Stored actual-N bars were 8.113 / 8.027 (keyskip1 / keyskip2, LP64) and the N=1e6 declared 9.102 / 8.999; the bars of record are %s / %s at N=1e6 and ~9.35 at N=65,8xx." % (rec(120, "keyskip1", "1e+06"), rec(120, "keyskip2", "1e+06")), b_note())
for rid, cell in (("R40-B1-BASH32-RANDOM-AUTOSEED", "bash3.2"), ("R40-B1-BASH51-RANDOM-AUTOSEED", "bash5.1")):
    patch(rid, "R41-I1 re-judge: " + txt(rowsfor("R40-B1", [cell])) + ".", b_note())
for rid in ("R40-B1-BASH41-RANDOM-AUTOSEED", "R40-B1-BASH40-RANDOM-AUTOSEED"):
    patch(rid, "R41-I1: carried by identity with the 4.2 orbit; the R37-I2 rows are re-judged against the survivor12 bar of record (no crossing).", b_note())
for rid, g in (("R40-B3-B04-REDECODE", "B04"), ("R40-B3-R16KDF-REDECODE", "KDF"), ("R40-B3-R17-PUBLIC-PAD-REDECODE", "R17PAD"), ("R40-B3-COSPAD-REDECODE", "COSPAD")):
    extra = ""
    if g == "KDF":
        extra = "The flagged KDF cell (6.528, keyskip2) is BELOW the bar of record at its actual N (7.435): the flag raised against the stored null12 bar (6.342) is withdrawn. "
    patch(rid, "R41-I1 re-judge: " + txt(rowsfor("R40-B3", [g])) + ".", b_note(extra))
for rid, fam in (("R40-C1-R30-B1-ARTIFACT-KEYS", "R30_B1_artifact_keys"), ("R40-C1-C18-NUMERIC-PS-TWEET-MAYAN", "C18_numeric_PS_tweet_mayan"), ("R40-C1-R32-B04-SLOGAN-SEEDS", "R32_B04_slogan_seeds"),
                 ("R40-C1-R32-B04-LP-SEEDS-STAGE-A", "R32_B04_lp_seeds_stageA"), ("R40-C1-R33-SEMANTIC-SEED-ZOO", "R33_R26C_semantic_seed_zoo"), ("R40-C1-R43-B5-COMPOSED-KEYS", "R43_B5_composed_keys"),
                 ("R40-C1-R47-F01-LP2-AS-PAD", "R47_F01_LP2_as_pad")):
    patch(rid, "R41-I1 re-judge (N = decodes in the family): " + txt(rowsfor("R40-C1", [fam])) + ". The lane's 'actual-N' / heads-screened bars were null12 quantities; the screened-N sensitivity is also below every best row (see rejudged_rounds36_40.json).", b_note())
patch("R40-C1-R13-R9-DIRECTION-WALKS", "R41-I1: the survivor12 bar does not apply (direct family). The standing page-/region-scale matched null benchmark/bars_matched.py reproduces the R13 family p at block sizes 100 / 250 / 1000 (fixture_r13.json: %s); the near-miss does not survive the matched nulls." % json.dumps({k: v.get("p_family") for k, v in fx.items()}))
for rid in ("B-04", "R16-KDF"):
    patch(rid, "R41-I1: the declared N=1e6 bars 9.102 / 8.999 quoted here are null12 quantities; the bar of record at N=1e6 on the pf_v4_12-survivor population is %s / %s (L=120, keyskip1 / keyskip2). The stored re-decode rows remain below it." % (rec(120, "keyskip1", "1e+06"), rec(120, "keyskip2", "1e+06")))
json.dump({"$comment": "R41 I1 bar-of-record notes (NOT applied by the lane; the coordinator applies, then runs check_ceiling.py). Rows R37-C1/C3/N* , R38-C1, R39-C1 that quote bar12 at N=1e6 for UNSCREENED direct decodes are not patched: their population is the unscreened null12, which this refit does not change.", "patches": P}, open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)

# ---------------------------------------------------------------- page replacement (text only; the lane does not edit the page)
pin = lambda s: "<!-- pin: %s | %s -->" % (ID, s)
newlim = ("X1/Round 40 found that the 'actual-N' bars quoted from this null were fitted on shuffled-LP2 wrong keys with no prefilter, a population less English-like than the survivors the sweeps decode (L=120 median 2.33 vs 2.80). "
          "Round 41 I1 refit the bar on the population it is applied to (wrong-key seeds from six generator families, real LP2 head, pf_v4_12 survivors, beam_v3 panel_max under panel-R36; 40,482 distinct survivors at L=120, 5,194 at L=240): "
          "the survivor median is 2.809 / 2.828 (keyskip1 / keyskip2) against the real sweeps' 2.80 / 2.82, and the L=120 bar of record is %s / %s at N=131,786 and %s / %s at N=1e6 (stored null12: 8.365 / 8.275 at N=131,786 and 9.102 / 8.999 at N=1e6); at L=240 the N=1e6 bar of record is %s / %s. "
          "The Gumbel tail is conservative (the real sweeps' maxima lie 0.7-2.8 SE below it), the bar of record at L=120 is the higher of the refit and the pooled real-sweep survivor POT line, and the 1 %% family-wise level at N~1.3e5 is not empirically measurable. "
          "The planted-key gate (480 plants, bar of record at N=1e6) fails in two register x relation cells (LATIN keyskip1, OE keyskip2, 18/20) through the pf_v4_12 screen, not the bar (470/470 screen-passers clear it). "
          "All 34 best rows of Rounds 36-40 stay below the bar of record at their actual N and at N=1e6 (smallest gap 0.9, the withdrawn KDF flag); no stored verdict moves. "
          "Direct (non-key) families need the page-/region-scale matched null (benchmark/bars_matched.py), not this bar; N=1e6 bars are tail extrapolations. "
          % (rec(120, "keyskip1", "131786"), rec(120, "keyskip2", "131786"), rec(120, "keyskip1", "1e+06"), rec(120, "keyskip2", "1e+06"), rec(240, "keyskip1", "1e+06"), rec(240, "keyskip2", "1e+06")))
pins = ["9.6325", "9.6549", "10.4645", "10.4856", "10.0529", "10.3539", "40,482", "5,194", "2.809", "480 plants", "470/480", "7.435"]
pins = [p for p in pins if p.replace(",", "") in json.dumps(row) or p in json.dumps(row)]
with open(os.path.join(HERE, "measured_ceiling_replacement.md"), "w", encoding="utf-8") as f:
    f.write("# Replacement text for MEASURED-CEILING.md section 1 (NOT applied by the lane; coordinator applies, files the ledger row, then runs check_ceiling.py)\n\n")
    f.write("In the 'Observed wrong-key nulls' row of section 1, replace the Measured-limits cell's clause beginning `X1/Round 40: the stored survivors of the sweeps score higher ...` (through `... (mean 1.1, sd 0.5)`) with:\n\n")
    f.write("> " + newlim.strip() + "\n\n")
    f.write("and add `[[%s]]` to that row's Rows cell. Add these pins to the pin block at the bottom of the page (each is checked against the row JSON):\n\n" % ID)
    f.write("```\n" + "\n".join(pin(p) for p in pins) + "\n```\n\n")
    f.write("Row to file in LEDGER.json: `ledger.json` (id `%s`). Notes to apply: `ledger_patches.json`. The 'N=1e6 bar is the effective one' sentence is withdrawn: the bar of record at the sweep's actual N is now calibrated, and the N=1e6 bar of record is %s / %s.\n" % (ID, rec(120, "keyskip1", "1e+06"), rec(120, "keyskip2", "1e+06")))
print("wrote ledger.json, ledger_patches.json, measured_ceiling_replacement.md; pins:", pins)
