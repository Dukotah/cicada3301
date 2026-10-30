#!/usr/bin/env python3
"""Builds control.json, ledger.json, ledger_patches.json from rescore_summary.json + parts/*.done (no decoding)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); F = lambda *a: os.path.join(H, *a)
S = json.load(open(F("rescore_summary.json"))); Fm = S["families"]
dctl = {k: v["control"] for k, v in Fm.items() if v["kind"] == "direct"}
ctl = {"date": "2026-10-30", "panel_sha256": S["panel_sha256"], "beam": json.load(open(F("control_beam.json"))), "direct": dctl}
ctl["direct_all_pass"] = {k: bool(v.get("all_pass", False)) if "all_pass" in v else None for k, v in dctl.items()}
ctl["all_pass"] = bool(ctl["beam"]["all_beam_pass"] and all(bool(v["all_pass"]) for v in dctl.values()))
json.dump(ctl, open(F("control.json"), "w"), indent=1)


def d(f):
    v = Fm[f]
    rb = ("%.3f" % v["raw_best"]["p"]) if "raw_best" in v else "n/a"
    return "%s: best %s pmax %.2f, Z %.2f, family p(Z)=%.3f, raw-best p=%s" % (f, v["best_stream"], v["best_pmax"], v["best_Z"], v["p_family"], rb)


def b(f):
    v = Fm[f]; n = v["best_nondegenerate"]
    return ("%s: best non-degenerate pmax %.2f (ks1) / %.2f (ks2) vs 12-reg bars actual-N %.2f/%.2f, declared-N %.2f/%.2f (%d rows/rel, %d degenerate rows/rel)"
            % (f, n["keyskip1"]["pmax"], n["keyskip2"]["pmax"], v["bars"]["keyskip1"]["actualN"], v["bars"]["keyskip2"]["actualN"],
               v["bars"]["keyskip1"]["declared_1e6"], v["bars"]["keyskip2"]["declared_1e6"], v["rows"]["keyskip1"], v["n_degenerate_rows"]["keyskip1"]))


TC = lambda ks, tm, ad: {"key_space": ks, "transition_model": tm, "adjudicator_register": ad}
ADJ = "panel-R36 12 registers (sha a0682f0c); self-calibrating shuffle null for direct streams, 12-register POT bars (null12.json) for beam rows"
BEAMTM = "keyskip1+keyskip2 under beam_v3 panel_max, L=120 (U6b also L=240); wrong-key bars transferred from the bash-orbit null (data-dependent keys: degenerate decodes filtered by IoC/mds)"
common = {"round": 37, "lane": "C3", "date": "2026-10-30", "threshold_fixed_in_advance": True,
          "evidence": ["liber-primus/analysis/round37/C3-rescore-reopened/PREREG.md", "liber-primus/analysis/round37/C3-rescore-reopened/RESULTS.md",
                       "liber-primus/analysis/round37/C3-rescore-reopened/rescore_summary.json"],
          "reproduce": "cd liber-primus/analysis/round37/C3-rescore-reopened; python rescore.py control; python rescore.py u6a; python rescore.py u6b; python rescore.py u5; python rescore.py final; python build_deliverables.py",
          "sweep_store": "analysis/round37/C3-rescore-reopened/rescore_rows.jsonl"}
rows = []


def row(id_, hyp, cov, res, tc, notc, thr, pc="passed", status="negative", reopens=None, detail=None):
    r = dict(common)
    r.update({"id": id_, "hypothesis": hyp, "status": status, "coverage": cov, "result": res, "three_conditionals": tc, "not_covered": notc,
              "threshold": thr, "positive_control": pc})
    if reopens: r["reopens_if"] = reopens
    if detail: r["control_detail"] = detail
    rows.append(r)


z = Fm["U5_L2_M1_pooled"]
l2 = " | ".join(d(f) for f in ("U5_L2_M1_pooled", "U5_L2_M1_pooled_dfnull", "U5_L2_M1_perpage", "U5_L2_M2", "U5_L2_M5", "U5_L2_M9"))
row("R37-C3-U5-L2-MAP", "Round 10 L2-map cleartext streams (M1/M2/M5/M9) re-scored outside English: the z=6.94 first-of-word near-flag and its family.",
    "REGENERATED (no stored streams): M1 pooled 464 readings (2000 null_A + 2000 doublet-matched draws), M1 per-page 21,808 short streams (200 draws), M2 348, M9 290 (300 draws), M5 1,486 paths (100 draws); 12-register panel-R36 direct pmax per stream. NOT covered: M3/M4/M6/M7/M8 (bits, LP1 pointers, counts, analytic, run pattern).",
    "NEGATIVE. The original z=6.94 reading (first-of-word/noF atbash/rev/+28) has panel pmax %.2f (EN_MODERN) = Z %.2f within its family (p(Z)=%.3f, raw best-of-464 p=%.3f; Wilson 95%% on exceedance rate %s). The English-gated flag was an artefact of the retired scorer. "
    % (z["original_reading_pmax"], z["original_reading_Z_vs_family"], z["p_family"], z["raw_best"]["p"], [round(x, 3) for x in z["raw_best"]["wilson95_exceed_rate"]]) + l2,
    TC("regenerated streams: 464 pooled M1 readings, per-page M1, M2 348, M9 290, M5 1,486", "none: cleartext-layer reads of the ciphertext's word/line/page structure (key-free)", ADJ),
    "M3/M4/M6/M7/M8 (not rune streams or analytic; LP1-pointer text reads stay English-only); the decoded (keyed) layer; the lane's own null kept alongside a doublet-matched null for M1 pooled only",
    "family-wise exceedance of per-stream standardised pmax vs same-draw family max of >=200 size-matched nulls (alpha 0.01), raw best-of-family pmax reported beside it",
    detail="control.json direct: planted EN_MODERN/LATIN/GREEK text at the family's n beats the family-null q99 by >1 Z for every L2 family",
    reopens="a stream whose panel pmax and standardised Z both clear the family-wise null with non-degenerate IoC/mds")
row("R37-C3-U5-L3-ROAD", "Round 10 L3-road word-sum cleartext streams (T2/T3/T4/T5) re-scored in 12 registers.",
    "REGENERATED by exec of road.py::readings (208 T2/T3/T4 streams, 300 lane-null draws) and T5 book-code streams (15 usable, 60 draws); direct panel-R36 pmax. NOT covered: T1 count tests (no stream).",
    "NEGATIVE. " + d("U5_L3_T234") + " | " + d("U5_L3_T5"),
    TC("208 T2-T4 readings + 15 T5 streams (road.py code unchanged)", "none: key-free reads", ADJ),
    "T1a/T1b count tests (no adjudicator); T5 with 60 null draws only; decoded layer", "as U5-L2", detail="control.json direct", reopens="as U5-L2")
row("R37-C3-U6A-N1-CT", "R11-N1 cumulative-gematria CT-feedback autokey under beam_v3 keyskip1+2 on panel-R36.",
    "24 CT-feedback configs REGENERATED (no top-N stored) x 10 windows x 2 relations = 480 decodes, L=120.", "NEGATIVE. " + b("U6a_N1_ct"),
    TC("24 N1 CT-feedback key configs, sign +/-, fwd/rev, continuous/per-segment", BEAMTM, ADJ), "PT-feedback under skip relations; windows beyond the 10; offsets",
    "12-register POT bar at actual N (240/rel) and 1e6", detail="control.json beam N1ct 12/12 (3 registers x 2 relations x 2 plants)",
    reopens="a window clearing the actual-N bar then L=240")
row("R37-C3-U6A-N1-PT", "R11-N1 plaintext-feedback (self-keying) autokey under the 12-register panel.",
    "24 PT-feedback configs regenerated; skip-free direct decode of the 12,956 stream scored on panel-R36. The key depends on recovered plaintext so the fixed-K keyskip beam cannot represent it.",
    "NEGATIVE on a skip-free transition model only. " + d("U6a_N1_pt") + ". The Z=78 is a null-variance artefact: raw pmax 2.7 is noise level and raw best-of-24 p=0.50.",
    TC("24 N1 PT-feedback configs", "skip-free (legacy) exact decode only", ADJ), "PT-feedback under any skip relation (not representable)", "Z and raw statistics both required",
    detail="control.json direct U6a_N1_pt")
row("R37-C3-U6A-N2", "R11-N2 prime gap/index streams read as data under 12 registers.",
    "12 streams (4 x mod29, base29-2, base29-3), derived-stream null from doublet-matched shuffled LP2 sources (200 draws); ASCII/coordinate routes not rune streams.",
    "NEGATIVE. " + d("U6a_N2"), TC("4 integer streams x 3 interpretations", "none: data read", ADJ), "ASCII printable and coordinate-structure routes; other bases",
    "family-wise vs derived-source null", detail="control.json direct U6a_N2")
row("R37-C3-U6A-N3", "R11-N3 whole-book integer structure (primality/factors).", "Not re-scored: N3 never used an adjudicator or decoder.",
    "NOT RE-SCORED. The English-only conditional never applied to N3; its original structural result stands.", TC("55 segments + full number", "n/a", "n/a: no scorer"),
    "everything adjudicator-related", "n/a", pc="n/a", status="inconclusive", detail="no control: nothing to re-score")
row("R37-C3-U6A-N4", "R11-N4 digit planes: as keystream (beam_v3) and as read symbol streams (direct).",
    "Keystream: 28 (14 planes x 2 signs) x 6 windows x 2 relations = 336 decodes at L=120 (regenerated; no top-N stored). Read: 14 plane streams, derived-source null.",
    "NEGATIVE. " + b("U6a_N4_ks") + " | " + d("U6a_N4_read"), TC("bases 3,5,7,10, all digit places, both signs", BEAMTM, ADJ), "base 29/other bases; plane combinations",
    "POT bars + family-wise Z", detail="control.json beam N4ks 12/12; direct U6a_N4_read")
row("R37-C3-U6A-N5", "R11-N5 totient-ladder keystreams (464) under beam_v3 keyskip1+2 on panel-R36.",
    "8 generators x 2 signs x 29 offsets = 464 keystreams (continuous windows 0/4800/9600 + per-segment restart on pages 18 and 36) x 2 relations = 4,640 decodes at L=120. AN END (real keyed page) decoded with phi(prime): recovery 1.00/0.93.",
    "NEGATIVE. " + b("U6a_N5"), TC("464 totient-ladder keystreams (regenerated from n5.py)", BEAMTM, ADJ), "5 windows per keystream; offsets beyond additive; generators beyond the 8",
    "POT bars actual N (2,320/rel) and 1e6", detail="control.json beam N5 12/12 + AN END real artifact (recovery 1.00/0.93; pmax 8.93/9.00 at n=85 < L=120)",
    reopens="a window clearing the actual-N bar then L=240")
row("R37-C3-U6A-S1", "R11-S1 interrupter-position gaps under 12 registers.",
    "8 rune-valued routes of the F-gap stream (mod29, base29-2, mod n); count-preserving random position null (300 draws); raw-best not computed for S1 (family p(Z)>0.4).",
    "NEGATIVE. " + d("U6a_S1"), TC("gaps mod29, base29-2/3, mod n in {2,3,4,5,8}", "none", ADJ), "ASCII/bit/indicator byte routes", "family-wise Z", detail="control.json direct U6a_S1")
row("R37-C3-U6A-S2", "R11-S2 separator run-lengths mod 29 under 12 registers.", "1 stream (run lengths mod29), shuffle null 1000 draws; raw-best not computed.",
    "NEGATIVE. " + d("U6a_S2"), TC("run lengths between - / .", "none", ADJ), "binary/ternary separator-byte routes (bytes/text, not rune space)", "family-wise Z",
    detail="control.json direct U6a_S2")
row("R37-C3-U6B-R22C", "R22-C: 185 operations under the 12-register panel: 169 structural (direct) + 14 keyed op-configs x keyskip1/2.",
    "169 structural streams (X1 138, X3a 31; ops regenerated with R22-C's code; 300 doublet-matched source-null draws); 14 keyed op-configs (X3b 2 signs, X4 12) x 6 page-start windows x 2 relations = 168 decodes at L=120 and 168 at L=240. The plan's '185 x keyskip1/2' does not apply to the keyless structural ops. Degenerate constant decodes (e.g. X4 prime_index atbash_pre sign+1: constant stream, pmax 12.4 in OE, IoC*N=29, mds=1) are filtered by the IoC/mds rule.",
    "NEGATIVE. " + d("U6b_R22C_structural") + " | " + b("U6b_R22C_keyed_L120") + " | L=240: " + b("U6b_R22C_keyed_L240"),
    TC("the same 185 operations (not widened)", BEAMTM + "; structural ops skip-free", ADJ), "non-zero offsets, width!=4 interleave/decimation, phi(phi)/lambda keystreams beyond N4/N5",
    "POT bars + family-wise Z", detail="control.json: inverse-op plants (decimation, deinterleave, reversal+shift) for X1/X3a; beam plants for X3b/X4 12/12",
    reopens="as R22-C: width!=4, non-zero offsets, drift constructions beyond keyskip")
json.dump({"$comment": "R37 C3 ledger rows (not applied to LEDGER.json by the lane)", "entries": rows}, open(F("ledger.json"), "w"), indent=1)

pat = []


def mk(i, txt, nc_):
    pat.append({"id": i, "coverage_add": "R37-C3 (2026-10-30): " + txt, "not_covered_add": nc_,
                "status_note": "English-only/legacy-beam conditional replaced by the 12-register conditional; remains negative"})


n1 = Fm["U6a_N1_ct"]
mk("R11-N1-NUMBER-CHANNEL", "CT-feedback 24 configs x 10 windows x keyskip1/2 L=120 under beam_v3 + panel-R36 (best non-degenerate %.2f/%.2f vs actual-N bars %.2f/%.2f); PT-feedback 24 configs skip-free direct (raw p 0.50)."
   % (n1["best_nondegenerate"]["keyskip1"]["pmax"], n1["best_nondegenerate"]["keyskip2"]["pmax"], n1["bars"]["keyskip1"]["actualN"], n1["bars"]["keyskip2"]["actualN"]), "PT-feedback under skip relations; windows beyond 10")
mk("R11-N2-NUMBER-CHANNEL", d("U6a_N2"), "ASCII/coordinate routes")
mk("R11-N3-NUMBER-CHANNEL", "not re-scored: no adjudicator involved", "")
mk("R11-N4-NUMBER-CHANNEL", b("U6a_N4_ks") + "; " + d("U6a_N4_read"), "other bases")
mk("R11-N5-NUMBER-CHANNEL", b("U6a_N5"), "5 windows per keystream")
mk("R11-S1-NUMBER-CHANNEL", d("U6a_S1"), "ASCII/bit/indicator routes")
mk("R11-S2-NUMBER-CHANNEL", d("U6a_S2"), "binary/ternary byte routes")
mk("R22-C-LITERAL-IMPERATIVES", d("U6b_R22C_structural") + "; keyed " + b("U6b_R22C_keyed_L240"), "keyless structural ops have no keyskip axis; non-zero offsets; width!=4")
mk("R10-L2-MAP", "streams regenerated and re-scored under panel-R36: z=6.94 reading pmax %.2f, family p(Z)=%.2f (U5-L2)." % (z["original_reading_pmax"], z["p_family"]), "M3/M4/M6/M7/M8")
mk("R10-L3-ROAD", d("U5_L3_T234"), "T1 count tests; T5 60 null draws")
json.dump({"$comment": "R37 C3 patches (not applied by the lane); R10-L2-MAP / R10-L3-ROAD are C1's proposed rows", "patches": pat}, open(F("ledger_patches.json"), "w"), indent=1)
print("ok", len(rows), len(pat), ctl["all_pass"], ctl["direct_all_pass"])
