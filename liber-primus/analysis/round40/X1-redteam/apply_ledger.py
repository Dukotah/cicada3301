#!/usr/bin/env python3
"""Round 40 X1: file the audited lane rows and patches into LEDGER.json. Idempotent: always rebuilds from LEDGER.pre-x1.json."""
import json, os, copy, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R40 = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(R40, "..", ".."))
doc = json.load(open(os.path.join(HERE, "LEDGER.pre-x1.json"), encoding="utf-8")); E = doc["entries"]; byid = {e["id"]: e for e in E}
PFX = "liber-primus/analysis/round40/"
jl = lambda p: json.load(open(os.path.join(R40, p), encoding="utf-8"))
rows_of = lambda p: (lambda d: d["entries"] if isinstance(d, dict) and "entries" in d else d)(jl(p))
rj = lambda f: json.load(open(os.path.join(HERE, f), encoding="utf-8"))


def add(e):
    assert e["id"] not in byid, e["id"]
    E.append(e); byid[e["id"]] = e


def norm_ev(ev, lane):
    out = []
    for x in ev or []:
        x = str(x)
        out.append(x if x.startswith("liber-primus/") else ("liber-primus/" + x if x.startswith("analysis/") else PFX + lane + "/" + x))
    return out


def lane_rows(lane):
    out = []
    for r in rows_of(lane + "/ledger.json"):
        r = copy.deepcopy(r); r["lane_dir"] = lane; r["evidence"] = norm_ev(r.get("evidence"), lane)
        if r.get("sweep_store") and not str(r["sweep_store"]).startswith("liber-primus/"):
            r["sweep_store"] = "liber-primus/" + r["sweep_store"] if str(r["sweep_store"]).startswith("analysis/") else r["sweep_store"]
        out.append(r)
    return out


def append_cov(e, marker, text):
    c = e.get("coverage")
    if isinstance(c, str):
        if marker not in c: e["coverage"] = c + " | " + text
    elif c is None:
        e["coverage"] = text
    else:
        e.setdefault("r40_coverage_ext", []);
        if text not in e["r40_coverage_ext"]: e["r40_coverage_ext"].append(text)


# ------------------------------------------------------------------ B1
gen = rj("rerun_generators.json"); rep = rj("rerun_replication.json")
b1x = {
 "R40-B1-BASH41-RANDOM-AUTOSEED": ("X1/R40: NO-ERROR-FOUND on the generator and the identity claim. From the downloaded GNU tarballs (sha256 equal to verification.json) X1 read variables.c: the 4.0 and 4.1 RANDOM blocks are textually identical (empty diff), and differ from 4.2 only in the zero branch (seedrand() vs 123459876). "
   "RANDOM=1 first 20 values re-derived by independent code (rerun_generators.py, LP64 and ILP32): equal to verification.json. X1 re-ran 2 of the 8 replication chunks (1329/786432 and 1306/262144): 423 survivors, 846 rows, identical keys to R37-I2 4.2 rows, max pmax diff 0.0005 (rerun_replication.json). "
   "Limits: no 4.1 binary; the planted controls use the same generator (they validate the pipeline, not the generator); the 8 replication chunks are the first 8 of the Random(3301)-shuffled order, not a fresh random draw."),
 "R40-B1-BASH40-RANDOM-AUTOSEED": "X1/R40: NO-ERROR-FOUND; same audit as R40-B1-BASH41-RANDOM-AUTOSEED (4.0 and 4.1 RANDOM blocks diff empty; read from bash-4.0 variables.c l.1207-1257). No 4.0 binary; covered by identity.",
 "R40-B1-BASH32-RANDOM-AUTOSEED": ("X1/R40: NO-ERROR-FOUND on the arithmetic (76,237,568 = 76,204,800 + 32,768; 291 chunks of 2^18). X1 read bash-3.2 variables.c independently (brand l.1156-1159: rseed*1103515245+12345, (rseed>>16)&32767; init l.498 sbrand(dollar_dollar_pid + shell_start_time); shell_start_time set at shell.c:424 and dollar_dollar_pid at variables.c:376, both before initialize_shell_variables) and re-derived RANDOM=1 -> 16838 5758 10113 17515 31051 ... "
   "Still no 3.2 binary: stays partially-run. The ceiling patch as filed said only 'pid_max > 32768' remained for 3.2; the generator being source-derived and the subshell reseed are also not excluded (page line corrected)."),
 "R40-B1-BASH51-RANDOM-AUTOSEED": ("X1/R40: NO-ERROR-FOUND. X1 read bash-5.1 lib/sh/random.c (intrand32 Schrage with +0x7fffffff correction, brand fold (r>>16)^(r&65535) when compat > 50, genseed = tv_sec^tv_usec^pid^ppid^uid^(u32)&seedrand) and re-derived 20 values; the live bash 5.3.9 binary matches the model on 7 seeds incl. 2147483646, 3000000000, 4000000000 (a 5.3 binary, not 5.1: the RANDOM=s stream is equal, the 5.1 auto-seed is source-read only). "
   "88 prefixes confirmed (74 base 1263..1336 XOR {0..7}); 92,274,688 / 2^31 = 4.297 %. Filed negative only for the non-PIE family: ~95.7 % of the PIE/ASLR orbit is not covered."),
}
for r in lane_rows("B1-bash-versions"):
    r["x1_r40"] = b1x[r["id"]]
    r["evidence"] = r["evidence"] + [PFX + "X1-redteam/RESULTS.md", PFX + "X1-redteam/rerun_generators.json", PFX + "X1-redteam/rerun_replication.json"]
    add(r)
for pid, txt in (("R32-B1-BASH42-RANDOM-AUTOSEED", "R40-B1: bash 4.0/4.1 share the 4.2 LP64/ILP32 stream except the zero-state branch (covered by identity with R37-I2); bash 3.2 (76,237,568 seeds, generator source-derived) and bash 5.1 non-PIE (92,274,688 seeds, 4.3 % of the PIE orbit) swept in full under pf_v4_12 + beam_v3 + panel-R36: 0 flagged, 0 near-miss."),
                 ("R37-I2-PFV4-12REG-ORBIT", "R40-B1: 8/296 chunks re-executed through the bash 4.1 generator by the lane and 2 of them again by X1: identical survivor and decode sets, pmax equal at 3 dp.")):
    append_cov(byid[pid], "R40-B1", txt)

# ------------------------------------------------------------------ B3
bars = rj("rerun_bars.json"); noise = rj("rerun_noise.json"); cell = rj("rerun_noise_cell.json"); cal = rj("rerun_r37_calibration.json")
kd = bars["KDF"]["keyskip2"]
b3x_common = ("X1/R40: bars recomputed from null12.json at actual N / N=1e6 / screened N: equal to the stored values (max diff < 6e-4, rerun_bars.json). SURVIVOR-POPULATION MISMATCH (FOUND-ERROR): the stored survivors' L=120 pmax is shifted up against the null12 cells (median 2.74-2.86 vs 2.33; q99 4.7 vs 4.06) in every B3 grid, in the B1 sweeps and in R37-I2 (131,786 rows: median 2.81, q99 4.76), so the 'actual-N' bar is not a 1 % family-wise bar (empirical POT bar at N=131,786: 9.62-9.64 vs the stored 8.27-8.37). "
   "No verdict flips (nothing within 1.5 of any bar except the KDF cell below); the N=1e6 bar is the effective one. Planted controls re-counted from control_*.json: 80/80, 78/80, 78/80 per register (Wilson lower bounds 0.954, 0.913, 0.913).")
b3x = {
 "R40-B3-B04-REDECODE": b3x_common,
 "R40-B3-R16KDF-REDECODE": (b3x_common + " FLAGGED CELL (KDF|03000000:iter_md5_1000:self:mod29:rev, keyskip2, 6.528): X1 re-decoded it at L=120 and L=174 under both relations (rerun_noise_cell.json): keyskip2 6.528 (EN_MODERN) -> 5.531 (EN_HALFVOWEL), keyskip1 4.520 -> 4.483; transliteration has digraph flavour and no words (e.g. FICNIFGEWWIAOORSNCENSUWENCLACOY...); the forward twin scores 1.957. "
   "Pooled empirical bar from 32,717 other-grid survivor decodes per relation (POT refit, N=591): 7.37 / 7.38 and P(max of 591 >= 6.528) = 0.075 / 0.078 (stored fit: 0.6 %), 0 of 32,717 other-grid rows and 1 of 142,283 B1 rows reach 6.528. X1 verdict: NOISE-CROSSER, concurring independently with the coordinator. "
   "The coordinator's policy note that the screened-configuration bar is primary is not supported: the null12 cells are fitted on screen survivors, so survivor N is the matching count; screened N (8.87) happens to land near the empirical bar only because the null12 location is too low."),
 "R40-B3-R17-PUBLIC-PAD-REDECODE": (b3x_common + " P3 regeneration: 25 of 28 pads sha-equal; the 3 mismatches (canon_256, cicada_all_pub, cicada_all_rev) are one cause: round34/SYNTHESIS.md:41 replaced canon_256.bin with R19-C1's resolved bytes and build_pads.py:248 concatenates canon_256 into cicada_all_*, so R17's original sweep covers the old bytes of those three pads. Offset fractions 7,506,611 / 1,577,174,689 = 0.4760 % re-derived from counts_pads.json (PREREG quoted a 5.76e9 dense space; the 1.577e9 figure is the builder x direction count actually used)."),
 "R40-B3-COSPAD-REDECODE": (b3x_common + " Offset fraction 10,006,340 / 1,280,055,240 = 0.7817 % re-derived."),
}
for r in lane_rows("B3-english-era-grids"):
    r["x1_r40"] = b3x[r["id"]]
    r["evidence"] = r["evidence"] + [PFX + "X1-redteam/RESULTS.md", PFX + "X1-redteam/rerun_bars.json", PFX + "X1-redteam/rerun_noise.json", PFX + "X1-redteam/rerun_noise_cell.json", PFX + "X1-redteam/rerun_r37_calibration.json"]
    if r["id"] == "R40-B3-R16KDF-REDECODE":
        r["oracle_adjudication"] = ("coordinator 2026-10-31 (owner's delegated authority): NOISE-CROSSER; X1 independent re-decode and pooled-null check concur (not the owner's read). "
                                    "Cleared actual-N 6.342 but not N=1e6 8.999 nor screened-N 8.868; no L=240 gate exists for rev keys. Status stays partially-run; the flagged cell is closed as a noise-crosser unless the owner overrules.")
    add(r)
B3NC = "v3 re-decode of the source decodes (requires regenerating ciphertext/key per source)"
for pid, extra in (("B-04", "R40-B3: the 2,165-seed dictionary re-decoded under pf_v4_12 + beam_v3 keyskip1+keyskip2 on panel-R36 (6,998,144 configs): best 6.336 / 6.049 vs actual-N bars 7.244 / 7.173 (N=1e6 9.102 / 8.999), 0 flagged; planted controls EN_MODERN / EN_NOVOWEL / LATIN only."),
                   ("R16-KDF", "R40-B3: 534 secrets x 27 KDFs x 3 salts re-decoded under the same instrument (692,064 configs): best 5.150 / 6.528 vs actual-N bars 6.399 / 6.342 (N=1e6 9.102 / 8.999; screened-N 8.968 / 8.868); one rev-buffer cell flagged by protocol and adjudicated noise-crosser (coordinator; X1 concurs); planted controls EN_MODERN / EN_NOVOWEL / LATIN only."),
                   ("R17-PUBLIC-PAD", "R40-B3: the regenerated R17-P3 pad list (25 of 28 sha-equal; canon_256, cicada_all_pub/rev regenerated from the corrected canon) re-decoded at a stated sampled offset fraction (7,506,611 of 1,577,174,689 builder x direction columns, 0.476 %): 15,013,222 configs, best 5.745 / 5.846 vs actual-N bars 7.424 / 7.350, 0 flagged. P1/P2 not regenerated; planted controls EN_MODERN / EN_NOVOWEL / LATIN only.")):
    e = byid[pid]; append_cov(e, "R40-B3", extra)
    nc = e.get("not_covered")
    if isinstance(nc, str) and B3NC in nc:
        e["not_covered"] = nc.replace(B3NC, "v3 re-decode of the ORIGINAL source decode stores (the regenerated key lists were re-decoded by R40-B3 under keyskip1+keyskip2 and panel-R36 with plants in three registers; B-04 stage B/D, dense offsets and registers outside EN_MODERN / EN_NOVOWEL / LATIN remain)")
    e["r40_b3"] = "see R40-B3 rows and analysis/round40/B3-english-era-grids/ledger_patches.json (audited by X1: coverage extensions applied; the lane's not_covered_remove strings did not occur in the rows and were replaced by the narrowing above)"
for pid, extra in (("R12-A1", "R40-B3: the four ISO pads (560.00 auth, 560.13, 560.17, 761.mp3) re-decoded under keyskip1+keyskip2 on panel-R36 at a sampled offset fraction (10,006,340 of 1,280,055,240 columns, 0.782 %): 20,012,680 configs, best 6.066 / 5.967 vs actual-N bars 7.619 / 7.542, 0 flagged; the truncated _560.00, folly/wisdom and prime_echo pads were not regenerable."),
                   ("R28-L1-CICADAOS-PADS-DENSE-PAIR", "R40-B3: the R28 stride grids re-included in the sampled offset set and re-decoded under pf_v4_12 + beam_v3 on panel-R36 (same 20,012,680 configs): best 6.066 / 5.967 vs 7.619 / 7.542, 0 flagged; planted controls EN_MODERN / EN_NOVOWEL / LATIN only.")):
    append_cov(byid[pid], "R40-B3", extra); byid[pid]["r40_b3"] = "see R40-B3-COSPAD-REDECODE"

# ------------------------------------------------------------------ C1
r13 = rj("rerun_r13_matched_BS100.json"), rj("rerun_r13_matched_BS250.json"), rj("rerun_r13_matched_BS1000.json")
clu = rj("rerun_r13_clusters.json"); calr = rj("rerun_r13_calib.json"); sts = rj("rerun_r13_starts.json")
fam = lambda d: d["blockperm_family"]
R13NOTE = ("X1/R40 RE-JUDGEMENT of the R13 DIRECTION near-miss under positional-structure-matched nulls (rerun_r13_matched.py, _clusters, _calib, _starts). (1) The lane's null (a global doublet-matched shuffle) is mismatched: on real LP2 the A:idx:b1:f1 walks collapse to 923 distinct trajectories (merging walks) whose stream pmax has mean 2.18, sd 0.82, max 4.50, 34 of 923 >= 4.0, whereas the same walk on dfshuffle texts gives mean 1.0-1.2, sd 0.5-0.7, max 2.3-2.6, 0 >= 4.0. "
           "(2) Nulls that keep local and regional text structure: block-permuted LP2 (blocks of 100 / 250 / 1000 runes, 500 draws each, the whole 2,274-stream family): Z-statistic family p = %.4f / %.4f / %.4f, raw best-of-family p = %.4f / %.4f / %.4f. Only the 100-rune null (which destroys the regional structure that a 5,000-position walk samples) reproduces the lane's p<0.01; at page scale (250) and region scale (1000) the pre-registered two-statistic rule is not met. "
           "(3) Same rule, same text, all 12,956 start positions: the observed trajectory is the top of 923 (rep pmax 4.35, member max 4.73; 13 trajectories reach its representative), at z = 3.0 of the trajectory distribution (expected maximum of 923 draws is about 3.2 sd). (4) Order carries structure beyond the unigram histogram: 0 of 1,000 permutations of the 400-rune stream reach 4.73 (mean 2.00, max 3.77), and amplitude is still the noise scale (a readable 400-rune stream scores tens). "
           "Verdict: not a near-miss under the matched nulls; consistent with the real text's regional heterogeneity. The row's own reopen condition (a replication under a null matching the walk structure) is evaluated and not met; filed `open` as instructed, X1 recommends the coordinator move it to `negative`. "
           "The lane's null defect also affects every direct family judged by a global shuffle (R04, R06, R27, R28): a mismatched null can only make those negatives look stronger than they are, so none flips.") % (
           fam(r13[0])["p_family"], fam(r13[1])["p_family"], fam(r13[2])["p_family"], fam(r13[0])["raw_best"]["p"], fam(r13[1])["raw_best"]["p"], fam(r13[2])["raw_best"]["p"])
c1x_common = ("X1/R40: C1 'blocked' premise checked in part. R14 wordsum_selfkey and R15 hill5_magic: the lane says the code is not committed; analysis/campaign7/wordsum_selfkey.py and hill5_magic.py exist under archive/branches-2026/claude_master-roadmap-libra-qk527u/ and corpus/H-branch-recovery/recovered/..., so cells H4xF3, L2xF3, L15xF2 are re-scorable (not done here: Round 41 item). "
              "R35 round12/C2/texts is absent (only fetch.sh), as stated. The lane's patch file named four ids that are not in LEDGER.json (O4-matrix, R9-DIRECTION, R10b-B1-ARTIFACT-KEYS, R10b-B5-COMPOSED-KEYS); applied below to the real rows. "
              "Bar policy differs by lane: C1 uses heads screened as its 'actual N' (e.g. R32 slogan 9.66 > the 9.10 declared bar) where B1/B3 use survivors; the null12 cells fit screen survivors, so both are off (see R40-B3 rows).")
c1_notes = {"R40-C1-R13-R9-DIRECTION-WALKS": R13NOTE + " " + c1x_common}
for r in lane_rows("C1-rescore-46"):
    r["x1_r40"] = c1_notes.get(r["id"], c1x_common if r["id"] in ("R40-C1-INCONCLUSIVE-R14", "R40-C1-INCONCLUSIVE-R15") else "X1/R40: see R40-C1-R13-R9-DIRECTION-WALKS x1_r40 for the lane-level audit.")
    if r["id"] in ("R40-C1-INCONCLUSIVE-R14", "R40-C1-INCONCLUSIVE-R15"):
        r["reopens_if"] = "the archived code (archive/branches-2026/.../analysis/campaign7/wordsum_selfkey.py, hill5_magic.py) is re-scored under panel-R36 (it exists; the lane's 'not committed' premise is wrong)"
        r["coverage"] = r["coverage"] + " [X1/R40: the code IS present under archive/branches-2026 and corpus/H-branch-recovery; not re-scored here.]"
    if r["positive_control"] == "not applicable":
        r["positive_control"] = "n/a (no control run)"
    r["evidence"] = r["evidence"] + [PFX + "X1-redteam/RESULTS.md"]
    if r["id"] == "R40-C1-R13-R9-DIRECTION-WALKS":
        r["evidence"] += [PFX + "X1-redteam/" + f for f in ("rerun_r13_matched.py", "rerun_r13_matched_BS100.json", "rerun_r13_matched_BS250.json", "rerun_r13_matched_BS1000.json", "rerun_r13_clusters.json", "rerun_r13_calib.json", "rerun_r13_starts.json")]
    add(r)
for pid, extra in (("B-04", "R40-C1: SLOGAN seeds (139) x 16 gens x 5 reds x dir x sign x atbash, stage A + per-page restarts, and 1,256 lp seeds stage A, re-screened with pf_v4_12 and decoded with beam_v3 under panel-R36: slogan best 5.88 (ks1) vs bar 9.66 (heads-screened N), lp 5.75 (ks2) vs 8.92; plants EN_MODERN / LATIN / GREEK."),
                   ("R16-KDF", "R40-C1: see B-04 (slogan seed groups only)."),
                   ("R26-C-SEMANTIC-SEED-ZOO", "R40-C1: all 2,137 keystreams re-decoded with beam_v3 keyskip1+2 under panel-R36 at L=120 window 0: best 4.81 / 4.90 vs bars 6.87 / 6.80; plants EN_MODERN / LATIN / GREEK."),
                   ("R22-A-SELFEMBEDDED-READ", "R40-C1: rune-index selections re-scored under panel-R36 (direct): p(Z)=0.0945, raw p=0.87; global-shuffle null (see R40-C1-R13 x1_r40 on its calibration)."),
                   ("R23-A2-LINE-ACROSTIC", "R40-C1: 24 of 48 reads scorable under panel-R36; the lane-null excess is explained by the natural English first/last-letter baseline (a2_natural_baseline.json); 24 reads are below the 32-rune panel floor."),
                   ("F-01", "R40-C1: 8 (variant, sign) pairs x T1/T2/T3/T6 windows re-decoded with beam_v3 keyskip1+2 under panel-R36: best 4.18 / 4.46 vs bars 5.80 / 5.75; T4, T5, all-pairs page XOR, canon-as-key not run."),
                   ("R10-L2-MAP", "R40-C1: M4 (16 pointer streams) and M6 (420 count streams) re-scored under panel-R36; M4 Z statistic invalid (null sd 0 for length-pointer families; raw best-of-family p 0.72), M6 p(Z)=0.31.")):
    append_cov(byid[pid], "R40-C1", extra); byid[pid]["r40_c1"] = "see R40-C1 rows (C1 patch audited by X1: the ids O4-matrix, R9-DIRECTION, R10b-B1-ARTIFACT-KEYS, R10b-B5-COMPOSED-KEYS do not exist and were not applied)"
cp = jl("C1-rescore-46/ledger_patches.json")["patches"][0]["set"]
tried = [c for c in cp["cells_to_TRIED"] if c != "H4xF6"]
partial = cp["cells_to_PARTIAL"] + ["H4xF6"]
unch = cp["cells_unchanged_inconclusive"]
assert len(tried) + len(partial) + len(unch) == 46 and len(tried) == 34 and len(partial) == 4
byid["R36-O4-CLUE-COVERAGE"]["x1_r40_cell_moves"] = {
    "TRIED_EN_or_LEG_to_TRIED": tried, "TRIED_EN_or_LEG_to_PARTIAL": partial, "unchanged_TRIED_EN_or_LEG": unch,
    "reason": ("C1 re-scored the readings of 46 English-only / legacy-beam cells under panel-R36. X1 moves H4xF6 TRIED -> PARTIAL (the lane marked it TRIED with an R13 caveat; its R13 reading is filed `open`). "
               "Three of the 'unchanged' cells (H4xF3, L2xF3, L15xF2) are blocked by a false premise (R14/R15 code exists under archive/branches-2026); the other five (H7xF9 R36 data, H12xF7 R44 books, L12xF5, L13xF5, S1xF5 R31 sub-floor crib readouts) were not independently verified except R35's missing texts."),
    "counts_after_R40_C1": {"NEVER": 0, "TRIED": 69, "TRIED-ENGLISH-ONLY": 21 - 13, "TRIED-LEGACY-BEAM": 0, "TRIED-EN+LEG_total": 8, "PARTIAL": 29, "NO-OPERATION-STATED": 34, "sum": 140},
    "evidence": PFX + "X1-redteam/RESULTS.md"}
# NB: split of the 8 remaining between TRIED-EN and TRIED-LEG: H4xF3,H7xF9,H12xF7,L2xF3,L12xF5,L13xF5,L15xF2,S1xF5 are all T-EN in cell_table.json
byid["R36-O4-CLUE-COVERAGE"]["x1_r40_cell_moves"]["counts_after_R40_C1"] = {"NEVER": 0, "TRIED": 69, "TRIED-ENGLISH-ONLY": 8, "TRIED-LEGACY-BEAM": 0, "PARTIAL": 29, "NO-OPERATION-STATED": 34, "sum": 140}

# ------------------------------------------------------------------ I1
i1 = lane_rows("I1-replant-controls")[0]
spot = {w: rj("rerun_i1_%s.json" % w) for w in ("u1", "g2", "n5")}; l2 = rj("rerun_i1_l2map.json")
i1["raw_positive_control"] = i1["positive_control"]
i1["positive_control"] = "passed"
i1["control_detail"] = ("Passed for 17 of 18 harness rows in all five registers (recovery 1.00; n 12-80 per register; Wilson 95 % lower bounds 0.72-0.95). NOT passed: R37-C3-U5-L2-MAP per-page M1 family (n=53 runes): EN_MODERN 8/10, EN_NOVOWEL 1/10 (X1 fresh seeds: 8/10 and 2/10). "
                        + i1["raw_positive_control"])
i1["x1_r40"] = ("X1/R40: spot re-run with fresh seeds, 5 plants each: R37-C1-U1 5/5 (LATIN, GREEK, HEBREW, 2x EN_NOVOWEL), R38-C2-G2 5/5, R37-C3-U6A-N5 5/5 (pmax120 15.1-20.7 vs bars ~9.1; pmax240 22.6-29.1). Line-80 claim re-checked with 10 fresh seeds (500-509): U5_L2_M1_perpage EN_MODERN %d/10, EN_NOVOWEL %d/10 (criterion Z > q99+1 = %.2f): weakness confirmed. "
                "Power words: the lane's 'power 1.00' is a point estimate on 10-80 plants (Wilson lower bounds 0.72-0.95), and U1/G1 test true-setting recovery, not the original rank-1 test. The tags cited the lane id as plain text because the row was not yet filed; the Rows cells now cite [[R40-I1-REPLANT-CONTROLS]]. "
                "Line 80 split: the seven passing rows carry their own five-register tag; U5-L2-MAP is its own `partial` line.") % (l2["EN_MODERN"]["recovered"], l2["EN_NOVOWEL"]["recovered"], l2["q99"] + 1)
i1["evidence"] = i1["evidence"] + [PFX + "X1-redteam/RESULTS.md"] + [PFX + "X1-redteam/rerun_i1_%s.json" % w for w in ("u1", "g2", "n5", "l2map")]
add(i1)
for p in jl("I1-replant-controls/ledger_patches.json")["patches"]:
    e = byid[p["id"]]
    for k, v in p["set"].items():
        if k.startswith("three_conditionals."):
            e["three_conditionals"][k.split(".", 1)[1]] = v
        else:
            e[k] = v
    e["r40_i1"] = "see R40-I1-REPLANT-CONTROLS"

# ------------------------------------------------------------------ B2 (not available at audit)
b2 = os.path.join(R40, "B2-offsets", "RESULTS.md")
B2_FILED = os.path.exists(b2)

# ------------------------------------------------------------------ X1 row
x1 = {"id": "R40-X1-REDTEAM", "round": 40, "lane": "X1", "lane_dir": "X1-redteam", "date": "2026-10-31", "status": "audit",
      "hypothesis": "Round 40's own claims (B1 generators, B3 grids and the KDF crosser, C1 re-scores and the R13 near-miss, I1 re-plants, the ceiling-page refreshes) survive a refute-by-default audit.",
      "result": ("FOUND-ERROR (none flips a stored negative). B1: NO-ERROR-FOUND on the four generators (20 values re-derived from the tarball sources, live bash 5.3.9 equal for 5.1-family streams, 4.0=4.1 diff empty, 2 of 8 replication chunks re-run identical, arithmetic 76,237,568 / 88 prefixes / 4.3 %); the ceiling patch understated the 3.2 caveat (generator unverified). "
                 "B3: the null12 bars are fitted on a survivor population that is less English-like than the sweeps' own (median 2.8 vs 2.33; empirical bar at N=131,786 is 9.6 vs the stored 8.3), so 'actual-N' is not a 1 % bar; the KDF cell (6.528) is a noise-crosser independently (pooled bar 7.37, P=0.075; score falls 6.528 -> 5.531; no words); the coordinator's 'screened-N is primary' note is unsupported; canon_256 cascade explains the P3 mismatch. "
                 "C1: the R14/R15 'code not committed' premise is false (archive/branches-2026); four patch ids do not exist; H4xF6 cannot be TRIED while its R13 reading is open; the R13 near-miss does not survive page- and region-scale matched nulls (Z-statistic p 0.018 / 0.070) and is the top of 923 trajectories at ~3 sd. "
                 "I1: 15/15 fresh re-plants recovered; L2-MAP weakness confirmed (EN_MODERN 8/10, EN_NOVOWEL 2/10); line 80 split; the cite form fixed; 'power 1.00' was a point estimate. B2 incomplete at audit time (not audited). S1/S2 (sandbox) not run this round."),
      "not_covered": "B2 (running, no RESULTS.md at audit); S1/S2 not run; the R14/R15 re-score; the five unverified blocked C1 cells; claims of cited rows were checked against row fields, not re-run, except where listed.",
      "reopens_if": "S2 window 2 is recovered (snap_ff0SWU76EW32OqbWJvp00fnORypR before about 2026-11-07); B2 files RESULTS.md (audit its offset alignment); the owner overrules the KDF noise-crosser or the R13 demotion.",
      "evidence": [PFX + "X1-redteam/RESULTS.md", PFX + "X1-redteam/apply_ledger.py", PFX + "X1-redteam/rerun_generators.json", PFX + "X1-redteam/rerun_bars.json", PFX + "X1-redteam/rerun_noise.json", PFX + "X1-redteam/rerun_r13_clusters.json", PFX + "X1-redteam/rerun_c1_cells.json", PFX + "X1-redteam/rerun_i1_l2map.json", "liber-primus/MEASURED-CEILING.md"]}
add(x1)
json.dump({"$comment": "R40 X1 lane row (also filed in LEDGER.json by apply_ledger.py)", "entries": [x1]}, open(os.path.join(HERE, "ledger.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ------------------------------------------------------------------ counts + note
rec = {}
for e in E: rec[e["status"]] = rec.get(e["status"], 0) + 1
doc["counts"]["total"] = len(E); doc["counts"]["by_status"] = rec
doc["counts"]["note"] = doc["counts"]["note"] + (" | Round 40 X1 merged 2026-10-31: lanes B1 (4 rows: bash 4.1/4.0 negative by identity, 3.2 partially-run, 5.1 non-PIE negative), B3 (4 re-decode rows; KDF flagged cell adjudicated noise-crosser), C1 (18 rows; R13 open; 35 cells re-scored: 34 -> TRIED, 4 -> PARTIAL incl. H4xF6; 8 unchanged), I1 (measured; 17 of 18 harness rows pass in 5 registers), "
                                                 "and X1 filed after refute-by-default audit; B2 not available at audit; sandbox lanes S1/S2 were not run.")
json.dump(doc, open(os.path.join(LP, "LEDGER.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(E), rec, "B2 filed:", B2_FILED)
