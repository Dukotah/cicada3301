#!/usr/bin/env python3
"""Round 38 X1: apply audited lane rows/patches to LEDGER.json. Idempotent: rebuilds from LEDGER.pre-x1.json."""
import json, os, re, copy, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R38 = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(R38, "..", ".."))
doc = json.load(open(os.path.join(HERE, "LEDGER.pre-x1.json"), encoding="utf-8")); E = doc["entries"]; byid = {e["id"]: e for e in E}; N0 = len(E)
PFX = "liber-primus/analysis/round38/"


def jl(p):
    d = json.load(open(os.path.join(R38, p), encoding="utf-8"))
    if isinstance(d, dict):
        return d.get("entries") or d.get("rows") or [d]
    return d


def add(e):
    assert e["id"] not in byid, e["id"]
    E.append(e); byid[e["id"]] = e


CFG = json.load(open(os.path.join(HERE, "x1_cfg.json"), encoding="utf-8"))

# ---------------- S1
raw = jl("S1-s2-windows/ledger.json")[0]
s1 = {"id": "R38-S1-S2-WINDOWS", "round": 38, "lane": "S1", "lane_dir": "S1-s2-windows", "date": "2026-10-31", "status": "measured",
      "raw_status": raw["status"],
      "hypothesis": "The Round 27 S2 (exact / keyskip1) lane, resumed under panel-R36, recovers an independently generated exact-relation plant and then advances; no seed crosses the claim bar.",
      "positive_control": "passed",
      "control_detail": "3/3 independently generated exact-relation plants (seeds 777, 1234567891, 3000000017) ranked first in a 4096-seed band through the engine's run_lane path, pmax 17.93/19.81/20.80 vs claim bar 7.6342 (control_exact.json, gen_control.py); stdlib-MT keystream equal to the engine's ks128; X1 regenerated the first 64 keystream values for all 3 seeds (rerun_s1.json). GRIND27_S2_CONTROL_OK is only a lane guard and is not the evidence.",
      "threshold": "claim bar 7.6341931878728095 (round27 panelmax_bar exact N=1e6; NOT recalibrated for 12 registers), candidate bar 5.0", "threshold_fixed_in_advance": True,
      "result": "Window 1 (panel-R36): 108,611,578 seeds, 0 claim-bar crossers, 0 near-misses (best pmax 7.3007 @ 3905907872). Window 2 was launched but its end state is UNRECOVERED (snapshot snap_ff0SWU76EW32OqbWJvp00fnORypR, Vercel 402 until 2026-11-01 UTC): no coverage, crosser or near-miss statement is made for it. Round 19 top-1024 re-scored under panel-R36: only 35563892 (7.6707) crosses (known R27 noise-crosser; 7.511 at L=240).",
      "coverage": "panel-R36 S2: 163,579,124 seeds = 3.809 pp of 2^32 (R36 window 54,967,546 + R38 window 1 108,611,578); window 2 NOT counted. Round 19-gated 44.138 % unchanged and not re-scored. Engine cursor sum 2,059,308,008 = 47.947 % is mixed-instrument.",
      "not_covered": "S2 window 2 (unrecovered); remaining ~52 % of the cursor space under panel-R36 and the 44.138 % under panel-R36 re-scoring; claim bars not recalibrated for 12 registers; the full hitfn20 3-clause gate on the control plants; full candidate/histogram lists (partial export, snapshots expire ~2026-11-06/07).",
      "three_conditionals": {"key_space": "Py2.7 MT19937 init_by_array([w]) w in uint32, random29 reducer, offset 0", "transition_model": "keyskip1 'exact' (one-draw rejection), relation exact only", "adjudicator_register": "panel-R36 12 registers, stage-A screen, claim bars from the Round 19 panel"},
      "reopens_if": "recover window 2 from snap_ff0SWU76EW32OqbWJvp00fnORypR after 2026-11-01 00:00 UTC and before ~2026-11-07; or continue S2 windows with persistent sessions.",
      "evidence": [PFX + "S1-s2-windows/" + x for x in ("RESULTS.md", "PREREG.md", "control_exact.json", "gen_control.py", "control_inputs.json", "top_rescored.json", "rescreen_l240.json", "state_after_1/STATUS_summary.json", "exported/R36_snapshot_summary.json")],
      "lane_ledger_raw": raw, "x1_r38": CFG["s1"]}
add(s1)
r = byid["R27-CPORT-MT32-FULLSWEEP"]
r["r38_s1"] = ("Round 38 S1 (2026-10-30/31; X1-audited): S2 (exact) coverage BY INSTRUMENT: Round 19 panel 44.138 % (cursor 1,895,728,884, unchanged, not re-scored); panel-R36 3.809 pp (163,579,124 seeds = R36 54,967,546 + R38 window 1 108,611,578), "
               "0 claim-bar crossers, 0 near-misses (best 7.3007 @ 3905907872). Engine cursor sum 2,059,308,008 = 47.947 % is mixed-instrument, not a single-instrument fraction. Window 2 was launched but is NOT counted (end state unrecovered, snap_ff0SWU76EW32OqbWJvp00fnORypR). "
               "The S2 exact-relation control is now independently validated (3/3, control_exact.json); this discharges the 'S2 null does not count until its own planted control passes' clause for the exact-lane stage-A control only (the full hitfn20 gate was not re-run).")
r["coverage_by_instrument"] = {"round19_panel_fraction": 0.441383776, "panel_R36_fraction": 0.038086, "panel_R36_seeds": 163579124, "engine_cursor_sum_mixed": 0.479470009, "window_2": "unrecovered, not counted"}
r["evidence"] = list(r.get("evidence") or []) + [PFX + "S1-s2-windows/RESULTS.md"]

# ---------------- S2
raw = jl("S2-php-sandbox/ledger.json")[0]
e = copy.deepcopy(raw); e.pop("sweep_store", None); e["round"] = 38; e["lane_dir"] = "S2-php-sandbox"
e["evidence"] = [PFX + "S2-php-sandbox/" + os.path.basename(p) for p in e["evidence"]]
e["positive_control"] = "not-persisted"
e["x1_r38"] = CFG["s2"]
add(e)
r = byid["R32-B2-PHP-MT-RAND"]
r["r38_s2"] = ("Round 38 S2 (X1-audited): tier (b) coverage added = ZERO seeds. The sandbox sessions were lost with no retained rows, control or FPR file; the log-observed numbers (12-register FPR 8.58e-4, 240 plants, throughput) are NOT evidence. "
               "R32 tier-b 0.970 % per twist and R36's 0.607 % per cell are unchanged. See R38-S2-PHP-SANDBOX (never-run).")

# ---------------- C1
for e in jl("C1-semantic-road/ledger.json"):
    e = copy.deepcopy(e); e["round"] = 38; e["lane_dir"] = "C1-semantic-road"; e["positive_control"] = "passed"
    e["control_detail"] = ("36/36 plants, 18/18 cells (6 variants x A1/A2/A3, 2 plants each, sigma +-1): recovery 0.996-1.0, pmax120 ~16-21 vs 9.235, pmax240 ~21-31 vs 9.514. "
                           "X1 re-ran 2 cells with a fresh seed (A-R29/A3, B-R28/A1; 4 plants, recovered 1.0, wrong-s decodes 0-5.1; rerun_c1_controls.json).")
    e["evidence"] = list(dict.fromkeys([PFX + "C1-semantic-road/" + os.path.basename(p) for p in e["evidence"]] + [PFX + "C1-semantic-road/PREREG.md"]))
    e["sweep_store"] = PFX + "C1-semantic-road/sweep_rows.jsonl"
    e["three_conditionals"] = {"key_space": "WordNet 3.1 first-synset offset (A) or Norvig rank (B) of LP1 codebook words, 3 reductions, rho=1, pages 0-2, start s",
                               "transition_model": "keyskip1 only (A3); A1/A2 direct shifts judged vs keyskip1 bar", "adjudicator_register": "panel-R36 12 registers; plants EN_MODERN only"}
    e["x1_r38"] = CFG["c1_wn"] if e["id"].endswith("WORDNET") else CFG["c1_fr"]
    add(e)
f2 = byid["F-02"]
f2["coverage"] = (f2.get("coverage") or "") + " | Round 38 C1: 'meaning' operationalized as WordNet 3.1 first-synset FILE OFFSET (arbitrary address, not sense similarity) and as Norvig frequency rank (not a meaning at all), 3 reductions x 3 modes x pages 0-2, 28,224 decodes, all below bars (best 5.30 vs 7.85)."
f2["x1_r38"] = CFG["f02"]
f2["related"] = list(f2.get("related") or []) + ["R38-C1-SEMANTIC-WORDNET", "R38-C1-SEMANTIC-FREQRANK"]
byid["R36-O4-CLUE-COVERAGE"]["x1_r38_cell_moves"] = CFG["o4"]

# ---------------- I1
raw = jl("I1-glyph-recognizer/ledger.json")[0]
e = copy.deepcopy(raw); e["lane_dir"] = "I1-glyph-recognizer"
e["evidence"] = list(dict.fromkeys([PFX + "I1-glyph-recognizer/" + os.path.basename(p.rstrip("/")) for p in e.pop("artifacts")]))
e["evidence"] = [p if not p.endswith("oracle") else p for p in e["evidence"]]
e["coverage"] = ("power test only (5 glyphs x 40 trials x D1 and D2, 400 null renders). The U8 232-render re-score was NOT run under the kill rule; a coordinator-licensed variant-limited diagnostic "
                 "(V1/V3/V4, 3 x 58 = 174 renders, D2, 100-draw nulls) was run afterwards and is NOT evidence (control failed).")
e["result"] = ("inconclusive: planted-glyph detection 1.0 (D2) but realised FPR 0.16 (V2 29/50, V3 3/50) vs <=0.05, so the control FAILED. The D2 actually run (min 8 steps + real-text window null) is NOT the D2 pre-registered "
               "(reweight + turning-function term; weights unchanged, tf=0.0 in both runs), so U8 is not retired by the kill rule's pre-registered revision. The three variant-limited above-null-max PNGs were viewed by the coordinator and by X1: nothing to escalate.")
e["status"] = "inconclusive"; e["positive_control"] = "failed"; e["round"] = 38
e["three_conditionals"] = {"key_space": "five U8 planted glyphs (octagon, 29-gon, T, L, 12-gon) in 4 turtle rules x 58 pages", "transition_model": "deterministic turtle render; templates identical to the planted polylines",
                           "adjudicator_register": "recognizer D2 (corner count, closure, turning histogram, Hu 1-4) vs real-text window null; FPR gate failed"}
e["x1_r38"] = CFG["i1"]
add(e)

# ---------------- C2 / I2 hooks (extra rows supplied by x1_c2_rows.py / x1_i2_rows.py, written only after those lanes' RESULTS.md exist and are audited)
for key in ("c2", "i2"):
    p = os.path.join(HERE, "x1_%s_rows.py" % key)
    if os.path.exists(p):
        exec(open(p, encoding="utf-8").read())

# ---------------- X1 row + counts
add(json.load(open(os.path.join(HERE, "x1_row.json"), encoding="utf-8")))
rec = {}
for e in E:
    rec[e["status"]] = rec.get(e["status"], 0) + 1
doc["counts"]["total"] = len(E); doc["counts"]["by_status"] = rec
doc["counts"]["note"] += (" | Round 38 X1 merged 2026-10-31: lanes S1 (window 1 only; window 2 unrecovered, not counted; coverage per instrument on R27-CPORT-MT32-FULLSWEEP), S2 (never-run, zero coverage on R32-B2), "
                          "C1 (2 rows; F-02 stays partially-run; O4 H3xF5 NEVER -> PARTIAL), I1 (inconclusive, control failed; D2 not the pre-registered D2) filed after refute-by-default audit%s (+%d rows incl. X1)."
                          % (CFG.get("c2i2_note", ""), len(E) - N0))
json.dump(doc, open(os.path.join(LP, "LEDGER.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("entries", len(E), rec)
