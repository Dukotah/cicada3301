"""Build ledger.json and ledger_patches.json for R40-B2 from stored results (no heavy compute)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "sweep_summary.json")))["cells"]
P = json.load(open(os.path.join(HERE, "sweep_progress.json")))["cells"]
EV = "analysis/round40/B2-offsets/"
cells = ["o0_sp", "o1_sm", "o2_sm", "o3_sm"]
desc = {"o0_sp": "offset 0, sign +1", "o1_sm": "offset 1, sign -1", "o2_sm": "offset 2, sign -1", "o3_sm": "offset 3, sign -1"}
cov, res = [], []
for c in cells:
    p = P[c]; k1, k2 = S[c + "|keyskip1"], S[c + "|keyskip2"]
    cov.append("%s: %d/296 chunks (%d seeds, %.1f%% of the orbit), %d survivors, each decoded under both relations" % (desc[c], len(p["done_chunks"]), p["seeds_screened"], 100 * len(p["done_chunks"]) / 296, p["survivors"]))
    res.append("%s: keyskip1 best %.3f (seed %d, %s) vs 12-register bar %.3f at actual N=%d (%.3f at N=1e6); keyskip2 best %.3f (seed %d, %s) vs %.3f (%.3f at N=1e6)" % (
        desc[c], k1["best_pmax"], k1["best_seed"], k1["best_preg"], k1["bar120_actualN"], k1["N_actual"], k1["bar120_declN"], k2["best_pmax"], k2["best_seed"], k2["best_preg"], k2["bar120_actualN"], k2["bar120_declN"]))
ctl = []
for c in cells + ["o28_sm"]:
    d = json.load(open(os.path.join(HERE, "control_%s.json" % c)))
    ctl.append("%s %d/%d recovered (prefilter %d)" % (c, d["recover_total"], d["n_plants"], d["prefilter_total"]))
e = {"id": "R40-B2-BASH42-OFFSETS-SIGN", "round": 40, "lane": "B2", "date": "2026-10-31", "status": "partially-run", "positive_control": "passed",
     "control_detail": "control_<cell>.json per cell: 10 EN_MODERN + 10 EN_NOVOWEL per relation (40 natural-rate plants), enciphered from the TRUE K_raw[offset:] with the TRUE sign, through the real 2^16-seed chunk path (pf_v4_12 -> v3 L120 both rels -> L240 -> panel-R36), >= 3 recoveries in every register x skip split pooled; " + "; ".join(ctl) + ". Misaligned negative control (offset-1 plants screened at offset 0): 16/20 pass the prefilter, 6/20 recover (0/7 with-skip heads), so the offset-0 instrument had only partial reach at offset 1.",
     "hypothesis": "The LP2 key is the bash 4.2 LP64 auto-seed $RANDOM%29 stream with the first k draws discarded (k = 1, 2, 3 swept; 28 not run) and/or with the decode sign +1 (offset 0), <= 2 key skips in the first 24 runes, plaintext in one of the 12 panel-R36 registers.",
     "coverage": "Cells run in the pre-registered prior-weighted order. " + "; ".join(cov) + ". Offset 28 (sign -1) was NOT run (cap). Of the 58-cell offset x sign axis: 1 cell done by R37-I2 (offset 0, sign -1), 3 full + 0.48 of a cell here, 53 cells untouched (91.4%). Cells here: 3.48 of 58 = 6.0% of the axis (4.48/58 = 7.7% with R37-I2). LP64 only; ILP32 not run at any offset.",
     "result": "0 flagged, 0 near-miss in any cell. " + ". ".join(res) + ".",
     "threshold": "12-register POT bars from round36/B1 null12.json at actual N and N=1e6; pf_v4_12 frozen point unchanged", "threshold_fixed_in_advance": True,
     "three_conditionals": {"key_space": "bash 4.2 LP64 auto-seed orbit (74 x 2^20 seeds), %29, at the cells (0,+1), (1,-1), (2,-1), (3,-1 half); ciphertext C[0] paired with K_raw[offset]; effective key K_raw[k:] (sign -1) or 29-K_raw[k:] (sign +1)",
                            "transition_model": "keyskip1+keyskip2 under beam_v3 panel_max, L120 screen / L240 gate; heads with <= 2 skips in 24 runes; not free, not L31",
                            "adjudicator_register": "panel-R36, 12 registers; pf_v4_12 reach 0.952-0.994 per register x v3 recovery (this lane's controls: 198/200 end-to-end over EN_MODERN and EN_NOVOWEL only)"},
     "not_covered": "Offset 28 (sign -1) and the second half of offset 3; offsets 4-27 at sign -1; offsets 1-28 at sign +1; ILP32 at every offset; offsets > 28; heads with >= 3 skips; free relation; L=31; registers outside the twelve; control plants cover EN_MODERN and EN_NOVOWEL only; a nondeterministic offset (k depends on shell activity).",
     "reopens_if": "the oracle flags a row; a stated offset or sign is hypothesised with evidence; the remaining cells (28; 4-27; sign +1 offsets) or ILP32 are run.",
     "evidence": [EV + f for f in ("RESULTS.md", "PREREG.md", "sweep.py", "sweep_summary.json", "sweep_progress.json", "wrapcheck.json", "control_gates.json", "run.log", "sweep_rows.jsonl")] + [EV + "control_%s.json" % c for c in cells + ["o28_sm"]],
     "sweep_store": EV + "sweep_rows.jsonl", "declares_sweep": True,
     "per_cell_coverage": {c: {"offset": P[c]["offset"], "sign": P[c]["sign"], "chunks_done": len(P[c]["done_chunks"]), "chunks_total": 296, "survivors": P[c]["survivors"], "best": P[c]["best"]} for c in cells}}
e["per_cell_coverage"]["o28_sm"] = {"offset": 28, "sign": -1, "chunks_done": 0, "chunks_total": 296, "note": "control passed (40/40); sweep not run (cap)"}
json.dump({"$comment": "written by R40 B2 lane agent", "entries": [e]}, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)
line = ("| Other bash versions and seedings; other PHP variants; offsets other than 0; sign +1 on most rows | (as R40-B1 audit line) and, for the bash 4.2 LP64 orbit, key offsets 4-28 at sign -1 (offset 3 half done), offsets 1-28 at sign +1, and ILP32 at every offset; offsets and signs measured: (0,+1), (1,-1), (2,-1) full and (3,-1) 143/296 chunks, best 6.831 vs bar 8.109 | partial | "
        "[[R40-B2-BASH42-OFFSETS-SIGN]] (added to the cell's existing refs) | a stated offset or sign, the remaining cells, or ILP32 at an offset |")
pins = ["<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 77,594,624 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 6.831 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 143/296 -->"]
json.dump({"$comment": "R40 B2 (not applied by lane). The MEASURED-CEILING section-3 line at row 107 ('Other bash versions and seedings; ... non-zero key offsets (a Round 40 offset lane was still running ...)') should have its 'non-zero key offsets' clause replaced by the clause below; the bash 4.2 orbit row (row 51) gets the offsets note. Pins must sit next to the lines.",
           "measured_ceiling_row107_replace_clause": "non-zero key offsets (a Round 40 offset lane was still running at the audit and is not audited here)",
           "measured_ceiling_row107_new_clause": "key offsets and sign on the bash 4.2 LP64 orbit: R40-B2 measured (offset 0, sign +1), (1,-1), (2,-1) in full and (3,-1) at 143/296 chunks, 0 flagged / 0 near-miss, best 6.831 vs bar 8.109; NOT covered: offset 28, offsets 4-27 (sign -1), offsets 1-28 at sign +1, ILP32 at any offset (4 of 58 offset x sign cells fully measured counting R37-I2's (0,-1), plus (3,-1) half; 53 cells, 91.4 %, untouched)",
           "measured_ceiling_row51_append": "Round 40 B2 extends the orbit to (offset, sign) cells (0,+1), (1,-1), (2,-1) full and (3,-1) 48 % under the same instrument: see [[R40-B2-BASH42-OFFSETS-SIGN]]",
           "measured_ceiling_new_line_if_whole_row_replaced": line, "pins_to_add": pins,
           "patches": [{"id": "R35-B1-BASH-ORBIT-PFV4", "coverage_add": "R40-B2: offsets 0(+1),1,2,3(half) under the same instrument: 0 flagged."},
                       {"id": "R37-I2-PFV4-12REG-ORBIT", "coverage_add": "R40-B2: offset / sign extension (0,+1), (1,-1), (2,-1), (3,-1 half): 0 flagged; misaligned-control finding: an offset-1 plant screened at offset 0 passes pf_v4_12 16/20 and recovers 6/20."}]},
          open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)
print("ok")
