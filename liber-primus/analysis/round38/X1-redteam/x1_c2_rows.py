# exec'd inside apply_ledger.py (namespace: jl, add, byid, PFX, CFG, copy, os, R38)
HYP = {
 "R38-C2-G1-CLAUSES-6-7": "The 2016 clauses 'Seek and you will be found.' and 'Beware false paths. Verify OpenPGP 7A35090F.' (omitted from R37 C1 U1's candidate list), as direct / SHA-256-CTR / PBKDF2 keys, are the LP2 key.",
 "R38-C2-G2-PRINTED-LINE-SUMS": "R37 C1 U2's LP1 number schedule, rebuilt from the PRINTED lines (60 physical rune lines of six solved pages, data/scream314_lp.md) instead of the koans-file lines, is the LP2 key schedule (additive or pointer).",
 "R38-C2-G3-LAGGED-POINTERS": "A pointer from the gematria/index of the PREVIOUS cipher word (cw) or decoded word (dw), lag 1, in the R37 C1 U3 composed map-road-direction rule, is the LP2 key.",
 "R38-C2-N5N4-L240": "The top-50 R37 C3 N5 / N4-keystream rows, re-run at L=240, separate from a cipher-derived-key matched null.",
 "R38-C2-NEVER-CELLS-RUN": "Seven O4 NEVER cells with a literal operation (H5xF1, H6xF2, L8xF6, L15xF6/F7, L17xF7, L4xF3) are run once under a bounded recognizer with a planted control.",
}
STORE = {"R38-C2-G1-CLAUSES-6-7": "C2-never-cells/gaps/sweep_rows.jsonl", "R38-C2-G2-PRINTED-LINE-SUMS": "C2-never-cells/gaps/sweep_rows.jsonl", "R38-C2-G3-LAGGED-POINTERS": "C2-never-cells/gaps/sweep_rows.jsonl", "R38-C2-N5N4-L240": "C2-never-cells/n5n4/rows_L240.jsonl"}
for e in jl("C2-never-cells/ledger.json"):
    e = copy.deepcopy(e); e["round"] = 38; e["lane_dir"] = "C2-never-cells"; e["hypothesis"] = HYP[e["id"]]
    e["evidence"] = [PFX + "C2-never-cells/" + x for x in ("RESULTS.md", "PREREG.md", "closed_no_operation.md")]
    if e["id"] in STORE: e["sweep_store"] = PFX + STORE[e["id"]]
    e["x1_r38"] = CFG["c2"][e["id"]]
    if e["id"] == "R38-C2-N5N4-L240":
        e["raw_status"] = e["status"]; e["status"] = "measured"
        e["flagged_for_oracle"] = "bundle C2-never-cells/n5n4/oracle/bundle.json: PENDING OWNER (HUMAN-ORACLE.md); lane + X1 expectation NOISE-CROSSER (matched null p 0.16 N4 / 0.74-0.78 N5; non-language decode); status not moved by this ledger"
    if e["id"] == "R38-C2-G3-LAGGED-POINTERS":
        e["three_conditionals"]["transition_model"] += "; the A3/cw plant is skip-free while the search relations are keyskip1/2 (power under skips unmeasured)"
    add(e)
for pid, txt in (("R37-C1-U1-CLUE-STRINGS", "clauses 6/7 now run (R38-C2-G1-CLAUSES-6-7, 384 decodes, best 4.26/4.32 vs 5.99/5.91); the '2016 clauses' conditional is now 7/7 for the three routes (direct, SHA-256-CTR, PBKDF2)"),
                 ("R37-C1-U2-LP1-NUMBER-SCHEDULES", "printed-line sums now run (R38-C2-G2-PRINTED-LINE-SUMS, 768 decodes, best 4.57/4.54 vs 6.25/6.16); X1 re-checked that the position array is aligned with the physical line lengths on all six pages (rerun_g2_align.json; the R37 U4 misalignment class is absent)"),
                 ("R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION", "lag-1 cipher-word / decoded-word pointers now run (R38-C2-G3-LAGGED-POINTERS, 576 decodes, best 4.91 vs 5.73); not run: dw inside the beam, lag > 1, s > 0")):
    r = byid[pid]; r["r38_c2"] = txt; r["related"] = list(r.get("related") or []) + [{"R37-C1-U1-CLUE-STRINGS": "R38-C2-G1-CLAUSES-6-7", "R37-C1-U2-LP1-NUMBER-SCHEDULES": "R38-C2-G2-PRINTED-LINE-SUMS", "R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION": "R38-C2-G3-LAGGED-POINTERS"}[pid]]
for pid in ("R37-C3-U6A-N5", "R37-C3-U6A-N4", "R11-N5-NUMBER-CHANNEL", "R11-N4-NUMBER-CHANNEL"):
    byid[pid]["r38_c2"] = ("R38 C2 n5n4: top-50 rows re-run at L=240 (L=120 reproduction 200/200 exact): best N5 7.446 (LATIN; screen-N bar 7.376), N4 8.553/8.572 (EN_HALFVOWEL; screen-N bar 6.45); below the N=1e6 bars (9.51/9.15); inside a cipher-derived-key matched null "
                           "(fixed-config, D=22/30: p 0.74-0.78 / 0.16; X1 recomputed from null_N4/N5.jsonl); decodes are non-language. Flagged-for-oracle bundle pending owner. Verdict unchanged (negative, conditional).")
for pid in ("R22-C-LITERAL-IMPERATIVES", "R37-C3-U6B-R22C"):
    pass  # R22-C X4 restatement comes from I2 (x1_i2_rows.py)
