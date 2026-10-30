"""X1/R36: apply audited lane rows + patches to LEDGER.json (idempotent). Run from liber-primus/."""
import json, os, collections
R36 = "analysis/round36"
EV = lambda lane, *fs: [f"liber-primus/{R36}/{lane}/{f}" for f in fs]
D = json.load(open("LEDGER.json", encoding="utf-8")); E = D["entries"]; ids = {e["id"]: e for e in E}


def lane_row(lane):
    d = json.load(open(f"{R36}/{lane}/ledger.json", encoding="utf-8"))
    for k in ("entries", "rows"):
        if k in d:
            return d[k][0]
    return d


new = []
# ---- I1
r = lane_row("I1-new-registers"); r["round"] = 36; r["lane"] = "round36/I1"
r["x1_r36"] = ("X1/R36: re-ran GREEK and NORSE L=120 plants under panel-R36 (8 lane reps reproduce bit-for-bit; 8 fresh reps 8/8 each; X1-redteam/rerun_i1_gate.json); "
               "EN_NOVOWEL/EN_HALFVOWEL/CY re-run 22/24, 24/24, 24/24 (rerun_nine.json); nine existing registers did not move. FOUND-ERROR (minor): "
               "the RESULTS 'Reproducibility' section and mappings.md present the build as deterministic, but hebrew_to_ascii iterates python sets of combining marks "
               "(mappings_r36.py:88,98,102): PYTHONHASHSEED 1/2/3 give three different HEBREW streams (rerun_hebrew_seed.txt), so I1's models/panel12.npz (sha ea8ef0fd..) "
               "is not run-to-run reproducible and its nine registers are the drifted Round 32 carry; the recorded gate is panel-R36 (R36-P1). The 15/384,147 affected clusters did not change the gate outcome.")
if isinstance(r.get("not_covered"), str):
    r["not_covered"] += "; I1's own models/panel12.npz is hash-seed dependent for HEBREW (superseded by panel-R36)"
new.append(r)
# ---- I2
r = lane_row("I2-pfv4-keystreams"); r["id"] = "R36-I2-PFV4-KEYSTREAMS"; r["lane"] = "round36/I2"; r["round"] = 36
r["threshold_fixed_in_advance"] = True
r["evidence"] = EV("I2-pfv4-keystreams", "PREREG.md", "RESULTS.md", "power_by_generator.json", "fpr_by_generator.json", "run.log")
tc = r["three_conditionals"]; r["three_conditionals"] = {"transition_model": tc[0], "key_space": tc[1], "adjudicator_register": tc[2]}
r["x1_r36"] = "X1/R36: PREREG precedes run.py by 20 ms and the first output by 1.4 s (same batch; thresholds are the frozen R35 values, so not a threshold-fitting risk). Results consumed by R36-B2 as its quoted reach."
new.append(r)
# ---- I3
r = lane_row("I3-d5c-two-margin"); r["id"] = "R36-I3-D5C-TWO-MARGIN"; r["lane"] = "round36/I3"; r["round"] = 36; r["date"] = "2026-10-30"
r["threshold_fixed_in_advance"] = True
r["evidence"] = [e if e.startswith("liber-primus/") else "liber-primus/" + e for e in r["evidence"]]
new.append(r)
# ---- P1
r = lane_row("P1-panel-r36"); r["round"] = 36
r["x1_r36"] = ("X1/R36: third build (PYTHONHASHSEED=7) into a scratch dir reproduces panel12.npz a0682f0c.. and testhalves12.npz cdd55adac.. byte for byte; "
               "inputs_r36.json 53/53 sha256 match on disk (X1 recomputed independently); GATE-CHANGE.md sec. 5 states the re-gate as a NEW measurement. "
               "FOUND-ERROR (minor): build_twice.json records no evidence of the seeds actually used (the PYTHONHASHSEED=1/2 claim is protocol prose; compare_builds.py compares files only) and its out_build12.json "
               "'identical:false' is the wall-clock fields; 5 Norse input paths in inputs_r36.json (Egils, Fostbraedra, Gisla, Hrafnkels, Volsunga) do not resolve as written because the on-disk names carry replacement characters (hashes match by basename).")
new.append(r)
# ---- S1
new.append({"id": "R36-S1-S2-WINDOW", "lane": "round36/S1", "round": 36, "date": "2026-10-30", "status": "measured",
 "hypothesis": "The Round 27 C engine, re-gated to panel-R36 (12 registers), passes its self-test (V1 64/64, V2 17.931158509762) and a capped sandbox window advances S2 (exact relation, random29, offset 0) from the 44.138 % change-point cursors with no claim-bar crosser.",
 "result": "negative: 0 claim-bar crossers (>= 7.6342), 0 near-misses (>= 7.5342); best pmax 7.1256 (seed 325254043); 6,280 candidates >= 5.0. Self-test PASS (V1 64/64 exact, V2 17.931158509762); resume tests a/a2/b/c PASS. Window 54,967,546 seeds in 2100 s (26,174.5 seeds/s on 2 vCPU).",
 "coverage": "S2 cursor coverage 1,950,696,430 / 2^32 = 45.418 % (was 44.138 %, +1.2798 pp). MIXED INSTRUMENT: the 44.138 % was scored under the Round 19 gate and never re-scored (28/64 V1 pmax move -0.66..+1.34 under panel-R36); only the 54,967,546-seed window carries panel-R36 pmax. The panel-R36-gated S2 coverage is therefore 1.28 %, not 45.4 %.",
 "threshold": "claim bars 7.3835 / 7.6342 (Round 19-panel quantities, not recalibrated for 12 registers); near-miss = claim bar - 0.10; fixed in PREREG before the sandbox existed",
 "threshold_fixed_in_advance": True, "positive_control": "passed",
 "control_detail": "engine --self-test V1 64/64 exact + V2 17.931158509762 (|d| 0); resume tests incl. planted hit; S2 itself still requires GRIND27_S2_CONTROL_OK=1 and the lane's own exact-relation planted control is not independently validated (V2 validates only the screen).",
 "three_conditionals": {"key_space": "S2 exact relation (keyskip1), random29, offset 0, 54,967,546 new seeds of 2^32 under panel-R36", "transition_model": "C screen at L=120 beam 64 (engine); not re-measured at the engine's own beam under panel-R36", "adjudicator_register": "panel-R36, 12 registers, CY a modern-Welsh substitute; claim bars not recalibrated"},
 "not_covered": ["the first 44.138 % of S2 was not re-scored under panel-R36", "top-1024 list / histogram / candidates.jsonl of the window exist only in sandbox snapshot snap_fWma12lA4k5RXsR6LHPwhV2p0DnN (expires ~2026-11-06)", "S2 remaining 54.58 % (~42.6 more windows at this rate)", "npz hash (a0682f0c..) not checked on the sandbox; engine blob hash e46d4bb7.. was", "S2 exact-relation planted control not independently validated"],
 "reopens_if": "the snapshot is lost before the window lists are exported, or S2 resumes (cursors in state_after/STATUS.json)",
 "evidence": EV("S1-s2-window", "PREREG.md", "RESULTS.md", "selftest.json", "engine_tests.json", "resume_window.json", "state_before/STATUS.json", "state_after/STATUS.json"),
 "x1_r36": "X1/R36: NO-ERROR-FOUND on window arithmetic (cursor sums, 54,967,546 seeds, +1.2798 pp, 42.6 windows), live run/ untouched (STATUS/top_S2/HIT byte-identical to state_before/, mtime 2026-10-28), after-state cursors in band and resumable (grind27.c:906-922 tolerates missing hist/top); FOUND-ERROR (wording): coverage 45.418 % mixes two instruments (corrected above)."})
# ---- B2
r = lane_row("B2-php-awake"); r["lane"] = "round36/B2"
r["coverage"] += (" X1/R36: tier-b seeds are the FIRST 199 blocks of the same numpy default_rng(3301) stream (blocks of 2^17) that R32-B2 drew 318 blocks from (round32/B2-php-mtrand/sweep.py:186-190, BLK=2^17; R36 sweep.py:259-263) "
                  "and R34-B1 drew 20 blocks from: the R36 tier-b seed set is a SUBSET of R32-B2's 41,680,896 seeds (0.9705 %), not new key space. What R36 adds is screen power on those 199 blocks (pf_v4 0.94-0.99 vs R32's 0.47-0.74), v3 on every survivor, and 263,906 persisted rows.")
r["x1_r36"] = ("X1/R36: NO-ERROR-FOUND on the sweep_rows.jsonl header + append logic (sweep.py:186-202: 'w' only on an absent/empty store, resume opens 'a'), 263,906 data rows (66,088/66,036/65,904/65,878 per cell = 2 x (decodes) as reported), "
               "control split 35+45 / 37+43 = 160, tier (a) 487+9,280 = 9,767 = 20.33 % / 38,269 pf_v4 = 79.67 %, tier (b) 199 x 2^17 / 2^32 = 0.6073 %, best 6.608 < bar 7.941. "
               "FOUND-ERROR: the lane's ledger patches (a) target id R32-B2-PHP-MTRAND which does not exist (real id R32-B2-PHP-MT-RAND) and (b) describe tier b as new coverage that 'replaces' R34's; it is a subset of R32's draw (see coverage).")
new.append(r)
# ---- O2
r = lane_row("O2-source-artifact-hunt"); r["lane"] = "round36/O2"
r["status"] = "partially-run"
r["hypothesis"] = "A non-JPEG source artifact (PDF/PS/DjVu/SVG/TIFF/PNG), a mirror with producer metadata, or a named original rune face for Liber Primus survives on the public web."
r["result"] = "NOT-FOUND within the covered space: 0 new artifacts. Coordinator addendum: gh code search for pdf/ps = 0 results; four large community repos contain no alternate-format source. Wayback CDX returned 'Temporarily Offline' - UNSEARCHED, not empty."
r["not_covered"] = ["Wayback snapshots of onion mirrors / uncovering-cicada / reddit 2014 (service offline)", "fandom wiki (HTTP 402)", "mirror JPEG EXIF/XMP diff vs R18-L1 fingerprint", "reddit", "GitHub code search by the 58 SHA-256s", "generic web search does not index file bytes"]
r["threshold"] = "n/a - search lane; recognizer in PREREG.md"; r["threshold_fixed_in_advance"] = True
r["reopens_if"] = "a tool that can query web.archive.org CDX, or a krisyotam/cicada3301 copy, becomes available"
r["evidence"] = EV("O2-source-artifact-hunt", "PREREG.md", "RESULTS.md", "search_log.json", "candidates.json")
r["x1_r36"] = "X1/R36: status 'negative' in the lane file would be an unsound negative (no positive control exists for a search); filed as partially-run. Not re-run."
new.append(r)
# ---- O3
r = lane_row("O3-nearmiss-1354603465"); r["lane"] = "round36/O3"
r["result"] += (" free relation: pmax rises with L for every seed (null medians 5.16/7.47/11.24 at L 120/262/729); not usable as evidence without an L-matched null (bars_v3 has free at L=120 only); "
                "one ILP32 free L=729 cell (15.15) exceeds an n=100 null max (14.33) - a larger free null is a coordinator decision.")
r["x1_r36"] = ("X1/R36: PREREG's 'wrong-key pmax is L-independent' was wrong (disclosed by the lane); the corrected argument (excess over size-matched null 4.85 -> 3.58 -> 1.08, plants rise 13.8-27.5 -> 36-71) holds, and the selection-free test is the held-out windows. "
               "Re-ran Verifier B windows 0 and 1 of the L=729 decode and the chained windows 0/1: 7.0681 LP1_REAL / 2.4157 EN_KJV; chained 7.0681 / 2.5463 EN_NOVOWEL, equal to the lane to 15 digits (rerun_o3_verifB.json). "
               "NO-ERROR-FOUND. Minor: O3's 12-register panel is I1's models/panel12.npz (ea8ef0fd..), not panel-R36 (pmax12 = pmax9 to 1e-7 either way).")
new.append(r)
# ---- O4
r = lane_row("O4-clue-coverage"); r["round"] = 36; r["lane"] = "round36/O4"; r["threshold_fixed_in_advance"] = True
r["x1_r36"] = ("X1/R36: counts reproduce (68+24+29+3+16 = 140 applicable of 374; 154 clue entries incl. 7 clause entries; 132 mapped); pgp/messages holds 58 files = 37 covered + 21 'ky_*' duplicates (bodies already in clues.json; the gap is undocumented but not a coverage hole). "
               "FOUND-ERROR (classification): matrix cells H7 x F2 and H12 x F2 are NEVER, but the 2012 P.S. digit string and the 2013 handle 1231507051321 were run as numeric additive keystreams in R10b B1 (b1_keys.py:138, 'NUMER' keys, row R30) and, skip-aware, in campaign18 numeric2_skip.py:170-205, and the P.S. digits as seeds in R26-C; "
               "these are F4 in O4's scheme but are number-as-key readings, so NEVER count is overstated by >= 2 (66). Not re-run.")
new.append(r)
# ---- X1
new.append({"id": "R36-X1-REDTEAM", "lane": "round36/X1", "round": 36, "date": "2026-10-30", "status": "audit",
 "hypothesis": "Round 36 lanes I1/P1/S1/B2/O3/O4, the audit edits and verify_solution.py contain errors that survive refute-by-default review.",
 "result": "FOUND-ERROR (mostly minor): I1 reproducibility claim (hash-seed-dependent Hebrew mapper); P1 build_twice records no seeds, 5 Norse paths unresolvable as written; S1 coverage 45.418 % mixes two instruments; B2 patch id wrong and tier-b seeds are a subset of R32-B2's draw; O4 H7/H12 x F2 mis-marked NEVER; O3 PREREG error (self-disclosed) holds up. NO-ERROR-FOUND on I1 GREEK/NORSE gate cells (re-run 8/8 each, lane reps bit-identical), S1 arithmetic and live-state integrity, B2 store/control/tier arithmetic, O3 Verifier B windows, O4 counts and message coverage, verify_solution.py (selftest PASS, wrong key FAIL with conditionals text, >=2 pages under one relation, panel sha a0682f0c.., tests/validate.py 6/6), AUDIT-applied edits (strikethrough, no deleted reasoning). B1 not available at audit time.",
 "coverage": "see round36/X1-redteam/RESULTS.md",
 "not_covered": ["B1-orbit-12reg (RESULTS.md absent at audit time)", "C --self-test and engine behaviour beyond what S1 logged (no compiler here)", "I2 and I3 numerics (only PREREG order checked)", "O2 search results (not re-run)"],
 "threshold": "n/a - audit (no null, no threshold)", "threshold_fixed_in_advance": True,
 "positive_control": "n/a - audit; recomputations reproduce lane numbers where stated",
 "evidence": EV("X1-redteam", "RESULTS.md", "rerun_i1_gate.json", "rerun_nine.json", "rerun_o3_verifB.json", "rerun_hebrew_seed.txt", "rerun_verify_rk11.json"),
 "reopens_if": "a corrected claim is re-asserted without new evidence."})
for r in new:
    if r["id"] in ids:
        continue
    E.append(r); ids[r["id"]] = r


def app(e, k, s):
    e[k] = (e[k] + " " + s) if isinstance(e.get(k), str) else s


# ---- patches to existing rows (idempotent: keyed fields overwritten)
e = ids["R27-CPORT-MT32-FULLSWEEP"]
e["r36_p1"] = ("Round 36 P1 (2026-10-30): the Round 19 panel gate (panel_lm.f32 sha 14a23d36..) is unrebuildable (Welsh corpus lost). The 44.14 % S2 coverage and the completed S1 lane were produced under that gate and remain recorded as such, not re-scored. "
               "Any S2 work after the re-gate is adjudicated by panel-R36 (12 registers, panel12.npz a0682f0c.., engine blob e46d4bb7..) and is a NEW measurement, not a continuation of the Round 19-gated rows; pmax values are not comparable across the change (28/64 V1 vectors move). Claim bars 7.3835 / 7.6342 are Round 19-panel quantities, not recalibrated. See round36/P1-panel-r36/GATE-CHANGE.md.")
e["r36_s1"] = ("Round 36 S1 (2026-10-30): S2 cursor coverage advanced 44.138 % -> 45.418 % (1,895,728,884 -> 1,950,696,430 of 2^32) by a 35-min sandbox window; 54,967,546 seeds, 0 claim-bar crossers, 0 near-misses (best pmax 7.1256). "
               "MIXED-INSTRUMENT (X1): only the 1.2798 pp window is adjudicated by panel-R36; the 44.138 % stays Round 19-gated and unre-scored, so the panel-R36 coverage is 1.28 %. Histogram/top list reset; claim bars uncalibrated. State: STATUS cursors in round36/S1-s2-window/state_after/; lists only in sandbox snapshot snap_fWma12lA4k5RXsR6LHPwhV2p0DnN. See R36-S1-S2-WINDOW.")
nc = e.get("not_covered")
adds = ["S2 rows after the re-gate use a 12-register panel with a modern-Welsh CY substitute; claim bars not recalibrated for 12 registers; the S2 histogram/top list before the change point is Round 19-gated.",
        "S2 panel-R36-gated coverage is 1.28 % (one window); the other 44.138 % has no panel-R36 score."]
if isinstance(nc, list):
    for s in adds:
        if s not in nc:
            nc.append(s)
else:
    e["not_covered"] = (nc or "") + " " + " ".join(adds)
ev = e.setdefault("evidence", [])
for x in ("liber-primus/analysis/round36/P1-panel-r36/GATE-CHANGE.md", "liber-primus/analysis/round36/S1-s2-window/RESULTS.md"):
    if x not in ev:
        ev.append(x)
ids["R32-B2-PHP-MT-RAND"]["r36_b2"] = ("R36-B2 (2026-10-30, X1-audited): re-ran the four PHP cells awake under pf_v4 + v3 on tier a (48,036: 9,767 unfiltered, 38,269 via pf_v4) and tier b = the first 199 blocks (26,083,328 seeds, 0.6073 % of 2^32) of the SAME default_rng(3301) stream this row drew 318 blocks from. "
               "So R36 adds no new seeds beyond this row's 0.9705 %; it raises screen power on 62.6 % of them (pf_v4 0.94-0.99 vs 0.47-0.74), v3-decodes every survivor and persists 263,906 validated rows. 0 flagged, best 6.608 vs bar 7.941 (actual N). The other 119 blocks of this row's draw keep the R32 prefilter power. See R36-B2-PHP-AWAKE-PFV4.")
ids["R34-B1-ORBITS-V3-PFV3"]["r36_b2"] = ("R36-B2 (2026-10-30, X1-audited): the PHP tiers were re-run awake. R34's tier-b 2,621,440 seeds are the first 20 blocks of the stream R36 now covers to block 199 (26,083,328 seeds = 0.6073 % per cell, a superset), "
               "so the sleep-truncated 0.061 % is subsumed and its lost PHP-side rows are replaced by R36-B2's 263,906 persisted rows; tier a is no longer prefilter-only (9,767 of 48,036 unfiltered, the rest pf_v4). "
               "R36 tier-b seeds are NOT new relative to R32-B2 (same stream). The bash-side per-seed rows (324,798 decodes) are still not persisted by this row. The uniform remainder (99.39 % per cell) stays not_covered.")
# ---- counts
cnt = collections.Counter(x["status"] for x in E)
bs = {k: cnt[k] for k in D["counts"]["by_status"]}
bs.update({k: v for k, v in cnt.items() if k not in bs})
D["counts"]["total"] = len(E); D["counts"]["by_status"] = bs
MARK = " | Round 36 X1 merged 2026-10-30:"
if MARK not in D["counts"]["note"]:
    D["counts"]["note"] += (MARK + " lane rows I1/I2/I3/P1/S1/B2/O2/O3/O4 + X1 filed (B1 not available at audit time); S1 coverage recorded as mixed-instrument (44.138 % Round 19-gated + 1.28 % panel-R36); "
                            "B2 patches applied to the real ids R32-B2-PHP-MT-RAND / R34-B1-ORBITS-V3-PFV3 with the shared-stream correction (R36 tier b is a subset of R32-B2's draw); O2 filed partially-run (a search has no positive control); I1 hash-seed finding recorded.")
open("LEDGER.json", "w", encoding="utf-8").write(json.dumps(D, indent=2, ensure_ascii=False))
print(len(E), dict(cnt))
