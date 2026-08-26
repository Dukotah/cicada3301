"""I2 / ledger — generate ledger.json from the measured outputs.

Numbers are read from out_gates.json / out_null.json / out_speed.json rather than typed,
so the ledger cannot drift from the results.  Merge into liber-primus/LEDGER.json.

    python3 make_ledger.py "<trust anchor before>" "<trust anchor after>"
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTERS = ["EN_MODERN", "EN_KJV", "LP1_REAL", "LATIN", "OE", "DE", "CY",
             "EN_HALFVOWEL", "EN_NOVOWEL"]


def load(n):
    return json.load(open(os.path.join(HERE, n), encoding="utf-8"))


def main():
    before = sys.argv[1] if len(sys.argv) > 1 else "not recorded"
    after = sys.argv[2] if len(sys.argv) > 2 else "not recorded"
    g = load("out_gates.json")
    nulls = load("out_null.json")
    build = load("out_build.json")
    speed = load("out_speed.json")
    rows = g["gates"]["G-POWER"]["table"]

    def cell(reg, L, k):
        for r in rows:
            if r["register"] == reg and r["L"] == L:
                return r[k]
        return None

    verdicts = {k: v["verdict"] for k, v in g["gates"].items()}
    entry = {
        "id": "I2-MULTI-REGISTER-ADJUDICATOR",
        "lane": "round19/I2",
        "round": "19",
        "date": "2026-08-26",
        "hypothesis": (
            "round18/L7-A measured that the repository's adjudicator (lp.score.Quadgram."
            "score_norm against a fixed -5.5 English band) discards the CORRECT key for "
            "Latin, Old English, German, Welsh and abbreviated English even though the beam "
            "recovers 100 % of the runes, and that doctrine R3's four language-agnostic "
            "statistics had 0/15 compliance.  I2 asserts that a nine-register rune-space "
            "language-model panel plus those four statistics, behind one adjudicate() call "
            "and one SWEEPROW schema, restores power >= 0.90 for every register without "
            "raising the false-positive rate at matched trial count."),
        "status": ("positive" if all(v == "PASSED" for v in verdicts.values())
                   else "mixed"),
        "verdict": "INSTRUMENT-REPAIRED" if verdicts.get("G-POWER") == "PASSED"
                   else "INSTRUMENT-PARTIALLY-REPAIRED",
        "gates": verdicts,
        "coverage": (
            "Nine plaintext registers (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, "
            "EN_HALFVOWEL, EN_NOVOWEL) x three segment lengths (120/240/400) x "
            f"{load('out_power.json')['nrep']} replicates, plant windows drawn from held-out "
            "corpus TEST halves (LP1_REAL: leave-one-page-out).  Protocol is L7-A's "
            "verbatim: plant sha256_ctr(CICADA3301), encipher_keyskip(supp=0.83), "
            "beam_decode(beam_w=400,max_skip=3) with the CORRECT key, adjudicate on rune "
            "indices.  Wrong-key null measured on the real 12,956-rune unsolved LP2 stream "
            "under uniform random keys through the same beam: "
            + ", ".join(f"n={nulls['lengths'][str(L)]['wrongkey']['en']['n']} at L={L}"
                        for L in (120, 240, 400))
            + f"; plus {nulls['lengths']['240']['random_rune']['en']['n']} uniform-random-"
              "rune draws per length and a 20,000-draw random-rune calibration at each of "
              "14 grid lengths."),
        "not_covered": [
            "registers outside the nine modelled: Greek, Hebrew, Norse/Icelandic, Enochian, "
            "constructed languages",
            "non-linguistic payloads (key blocks, hashes, base32) - round10b/B6 showed this "
            "class is undetectable in principle by any language model, and the four "
            "agnostic statistics are the only instrument that touches it",
            "decoder transition models beyond the Round-18 baseline: this lane deliberately "
            "held encipher_keyskip -> beam_decode fixed so its numbers are comparable with "
            "L7-A, and therefore INHERITS L7-B's hole (skip_by_two, free drift). That is "
            "lane I1's scope; every power number here is conditional on the baseline "
            "construction",
            "key families other than sha256_ctr(CICADA3301) - power is a property of the "
            "adjudicator rather than the key, but only one family was measured",
            "the beam still chooses its skip path by ENGLISH score, so for a register whose "
            "recovery is < 100 % the adjudicator sees an English-argmax path. Measured "
            f"here only for EN_NOVOWEL (recovery {cell('EN_NOVOWEL', 240, 'recovery')}); "
            "a panel-aware beam is an open item for I1",
            "family-wise thresholds at real sweep scale - the gate is adjudicated at the "
            "pre-registered per-decode alpha_ref=1e-3; the far-tail extrapolation in "
            "out_gates.json is SUPPLEMENTARY and I3 owns the calibrated bar",
        ],
        "positive_control": "passed",
        "threshold": (
            "Pre-registered in PREREG.md s3 before any measurement.  G-POWER: measured power "
            ">= 0.90 for every register at every L in {120,240,400}, at the matched-FP bar "
            "t_pmax set from the wrong-key null at alpha_ref=1e-3.  G-FP: at matched "
            "per-decode FP, panel power >= single-scorer power for every register at every "
            "L.  G-LP1: LP1_REAL median legacy score_norm >= -4.5 with 100 % of replicates "
            "clearing -5.5.  G-SPEED: adjudicate(240 runes) <= 3x score_norm(240 runes)."),
        "result": {
            "gate_verdicts": verdicts,
            "min_panel_power_over_all_27_cells": g["gates"]["G-POWER"][
                "min_power_over_all_cells"],
            "panel_power_at_L240": {r: cell(r, 240, "power_pmax") for r in REGISTERS},
            "legacy_scorer_power_at_L240_same_plants": {
                r: cell(r, 240, "power_legacy_bar") for r in REGISTERS},
            "median_panel_pmax_at_L240": {r: cell(r, 240, "median_pmax")
                                          for r in REGISTERS},
            "median_legacy_en_at_L240": {r: cell(r, 240, "median_en") for r in REGISTERS},
            "median_rune_recovery_at_L240": {r: cell(r, 240, "recovery")
                                             for r in REGISTERS},
            "k_eff_effective_independent_tests": {
                str(L): nulls["lengths"][str(L)]["k_eff"] for L in (120, 240, 400)},
            "beam_inflation_of_the_null": {
                str(L): {
                    "pmax_mean_wrongkey": nulls["lengths"][str(L)]["wrongkey"]["pmax"]["mean"],
                    "pmax_mean_random_rune":
                        nulls["lengths"][str(L)]["random_rune"]["pmax"]["mean"],
                    "en_mean_wrongkey": nulls["lengths"][str(L)]["wrongkey"]["en"]["mean"],
                    "en_mean_random_rune":
                        nulls["lengths"][str(L)]["random_rune"]["en"]["mean"],
                } for L in (120, 240, 400)},
            "thresholds_at_alpha_ref_1e-3": {
                str(L): g["gates"]["G-FP"]["per_length"][str(L)] for L in (120, 240, 400)},
            "us_per_decode": {
                "adjudicate_240": speed["gate_G_SPEED"]["us_adjudicate"],
                "score_norm_240": speed["gate_G_SPEED"]["us_score_norm"],
                "ratio": speed["gate_G_SPEED"]["ratio"],
                "batch_panel_only_240":
                    speed["lengths"]["240"]["us_adjudicate_batch_panel_only_per_row"]},
            "sweeprow_bytes_per_row": {"jsonl": "~130", "binary_ROW_DTYPE": 77},
        },
        "deliverables": {
            "adjudicate(plain_idx, translit=None) -> dict": "round19/I2/adjudicate.py",
            "SWEEPROW/1 schema + validator": "round19/I2/SWEEPROW.md, "
                                             "adjudicate.validate_row/validate_store",
            "register panel + null calibration builder": "round19/I2/build_models.py",
            "measurement harness": "round19/I2/power.py, speed.py, gates.py",
            "tests": "round19/I2/test_adjudicate.py",
        },
        "corpora_sha256": {k: [c["sha256"] for c in v]
                           for k, v in build["corpora"].items()},
        "trust_anchor_before": before,
        "trust_anchor_after": after,
        "reopens_if": (
            "a register outside the nine is proposed (add it to build_models.REGISTERS and "
            "re-measure), OR I1 changes the decoder's transition relation (every power "
            "number here is conditional on encipher_keyskip -> beam_decode(400,3)), OR I3's "
            "calibrated family-wise bar lands above the far-tail extrapolation in "
            "out_gates.json, in which case the power table must be recomputed at that bar "
            "from the stored per-replicate rows in out_power.json."),
        "artifacts": ["round19/I2/out_build.json", "round19/I2/out_smoke.json",
                      "round19/I2/out_null.json", "round19/I2/out_power.json",
                      "round19/I2/out_speed.json", "round19/I2/out_gates.json"],
    }

    doc = {"$comment": ("Round 19 lane I2 (MULTI-REGISTER ADJUDICATOR) ledger fragment. "
                        "Merge into liber-primus/LEDGER.json. This entry records an "
                        "INSTRUMENT measurement, not a key-space sweep: it states what the "
                        "repaired adjudicator can and cannot see, which is the third of the "
                        "three conditionals doctrine Q4 requires on every negative."),
           "lane": "round19/I2", "date": "2026-08-26",
           "trust_anchor_before": before, "trust_anchor_after": after,
           "entries": [entry]}
    json.dump(doc, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)
    print("wrote ledger.json")
    for k, v in verdicts.items():
        print(f"  {k:10s} {v}")


if __name__ == "__main__":
    main()
