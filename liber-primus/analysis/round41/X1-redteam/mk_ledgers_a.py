import json, os, math, copy
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.abspath(os.path.join(HERE, ".."))
AN = os.path.abspath(os.path.join(HERE, ".."))   # round41/..? fixed below
AN = os.path.abspath(os.path.join(HERE, "..", ".."))
B = os.path.join(AN, "round40", "B2-offsets")


def w(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round(max(0, (c - r) / d), 2), round(min(1, (c + r) / d), 2)]


rj = json.load(open(os.path.join(HERE, "x1a_b2_rejudge.json")))["rows"]
by = {(r["cell"], r["rel"]): r for r in rj}


def cellres(cell, label):
    a, b = by[(cell, "keyskip1")], by[(cell, "keyskip2")]
    return ("%s: keyskip1 best %.3f (seed %d, %s) vs bar of record %.3f at actual N=%d (%.4f at N=1e6); keyskip2 best %.3f (seed %d, %s) vs %.3f (%.4f at N=1e6)" %
            (label, a["best_pmax"], a["best_seed"], a["best_preg"], a["bar_of_record_actualN"], a["N_actual"], a["bar_of_record_1e6"], b["best_pmax"], b["best_seed"], b["best_preg"], b["bar_of_record_actualN"], b["bar_of_record_1e6"]))


res = ("0 flagged, 0 near-miss in any cell, judged against the Round 41 I1 bar of record (bars_v3 family='survivor12', max of the survivor refit and the pooled real-sweep POT line) at actual N and at N=1e6; the null12 bars the lane quoted (8.0-8.1 at actual N, 9.102 / 8.999 at N=1e6) are superseded. "
       + "; ".join([cellres("o0_sp", "offset 0, sign +1 (296/296 chunks)"), cellres("o1_sm", "offset 1, sign -1 (296/296)"), cellres("o2_sm", "offset 2, sign -1 (296/296)"), cellres("o3_sm", "offset 3, sign -1 (143/296 chunks)")])
       + ". Smallest gap to the bar of record: 2.51 at actual N (offset 1 keyskip1, 6.831 vs 9.344) and 3.63 at N=1e6; no L=240 gate decode was needed. The bar of record at N=1e6 is an exponential-tail upper bracket (statistical SE 0.09; a GPD alternative gives about 7.0); no verdict depends on the choice.")
mis_ctrl = ("Misaligned negative control, relation-specific (B2 20 plants + X1 re-plants, EN_MODERN/EN_NOVOWEL, bash 4.2 LP64, offset-k plants screened and decoded at the offset-0 alignment of every earlier orbit sweep): offset 1 under keyskip1 recovers 10/15 (Wilson 95%% %s), under keyskip2 0/15 (%s); offset 2 under keyskip2 3/5 and under keyskip1 1/5 (X1, n=5 each, intervals wide); sign +1 plants (offset 0) under the sign -1 instrument 0/10 (%s). Pooling the relations (B2's 6/20, 'roughly 0.3') hides this: the keyskip-a relation absorbs a start-of-stream key shift of a as a key skip (inferred from the pattern, not separately tested). Offsets 3 and 28 not measured this way." % (w(10, 15), w(0, 15), w(0, 10)))
ctrl = ("control_<cell>.json per cell: 10 EN_MODERN + 10 EN_NOVOWEL per relation (40 natural-rate plants), enciphered from the TRUE K_raw[offset:] with the TRUE sign, through the real 2^16-seed chunk path; recoveries o0_sp 39/40, o1_sm 40/40, o2_sm 39/40, o3_sm 40/40, o28_sm 40/40 (the 2 losses are pf_v4_12 screen misses); X1 recomputed every plant against the bar of record at N=1e6 (L120 10.4645/10.4856, L240 10.0529/10.3539; min plant pmax120 14.3, pmax240 19.4): the recoveries and the >=3-per-split gate are unchanged. X1 independent re-plant (own bash 4.2 generator, own enciphering and head wrapper): offset 2 sign -1 4/5 recovered (the loss a screen miss), offset 0 sign +1 5/5. "
        + mis_ctrl + " Controls cover EN_MODERN and EN_NOVOWEL only.")
nc = ("Offset 28 (sign -1; control passed 40/40, no sweep) and the second half of offset 3; offsets 4-27 at sign -1; offsets 1-28 at sign +1; ILP32 at EVERY offset (the 58-cell axis is LP64 only: with ILP32 it is 116 cells, of which R37-I2's (0,-1) both ABIs = 2, B2's 3 LP64 cells and 0.48 of (3,-1) = 5.48 cells, 4.7%); offsets > 28; an offset that is nondeterministic (depends on shell activity before the first $RANDOM read); heads with >= 3 skips in 24 runes; free relation; L=31; registers outside the twelve (plants cover EN_MODERN and EN_NOVOWEL only); bash versions other than 4.2 at any offset; "
      "the head screen ignores the anti-repeat rule (about (24+offset)/32768 of seeds: 0.07% at offset 0, 0.16% at offset 28)")
e = json.load(open(os.path.join(B, "ledger.json")))["entries"][0]
n = copy.deepcopy(e)
n["result"] = res
n["threshold"] = "Round 41 I1 bar of record: bars_v3.bar_v3(N, L, rel, family='survivor12') at actual N and N=1e6 (the null12 bars quoted by the lane are superseded); pf_v4_12 frozen point unchanged"
n["control_detail"] = ctrl
n["not_covered"] = nc
old_cov = "Of the 58-cell offset x sign axis: 1 cell done by R37-I2 (offset 0, sign -1), 3 full + 0.48 of a cell here, 53 cells untouched (91.4%). Cells here: 3.48 of 58 = 6.0% of the axis (4.48/58 = 7.7% with R37-I2). LP64 only; ILP32 not run at any offset."
n["coverage"] = e["coverage"].replace(old_cov, "Of the 58-cell LP64 offset x sign axis: 1 cell done by R37-I2 (offset 0, sign -1), 3 full + 0.48 of a cell here, 53 cells untouched (91.4% of the LP64 axis). Counting ILP32 (never run at a non-zero offset) the axis is 116 cells: (0,-1) both ABIs + 3 LP64 cells + 0.48 = 5.48 cells, 4.7%.")
assert n["coverage"] != e["coverage"]
n["evidence"] = e["evidence"] + ["analysis/round40/B2-offsets/control_misaligned_o1_sm.json", "analysis/round41/X1-redteam/RESULTS-A.md", "analysis/round41/X1-redteam/x1a_b2_plants.json", "analysis/round41/X1-redteam/x1a_b2_misaligned.json", "analysis/round41/X1-redteam/x1a_b2_rejudge.json", "analysis/round41/X1-redteam/ledger_b2_corrected.json"]
n["x1_r41"] = "X1/R41 part A: wrapper heads re-derived from an independent generator, 300 seeds x 28 values x 5 cells, 0 mismatches; two cells re-planted independently (offset 2 sign -1: 4/5; offset 0 sign +1: 5/5, the loss a screen miss); best rows re-judged against the bar of record (none crosses; gap >= 2.51); misaligned control re-scoped by relation (see control_detail). The lane's null12 bars are superseded."
n["notes"] = "Filed with X1/R41 corrections: bars of record replace null12; misaligned-control scope is relation-specific; ILP32 denominator stated."

NEWOFF = "offsets != 0 (partial reach measured for the bash 4.2 LP64 orbit, EN_MODERN/EN_NOVOWEL plants only: offset 1 under keyskip1 10/15 recovered (Wilson 95% 0.42-0.85), under keyskip2 0/15; offset 2 under keyskip2 3/5 and keyskip1 1/5 (n=5 each); sign +1 at offset 0 0/10; offsets 3, 28 and other signs not measured this way; R40-B2 swept (0,+1), (1,-1), (2,-1) fully and (3,-1) at 143/296 chunks, LP64 only);"
IDENT = "key offsets != 0 and sign +1 (by identity with the 4.2 LP64 orbit, the R40-B2 cells (0,+1), (1,-1), (2,-1) and half of (3,-1) and the relation-specific partial reach at offsets 1-2 carry over; ILP32 and every other cell not covered);"
wrapper = {
    "$comment": "X1/R41 part A. The lane's own files are unedited. 'entry' replaces analysis/round40/B2-offsets/ledger.json entries[0] when filed; 'patches' use real ids present in LEDGER.json; 'measured_ceiling' gives exact page text.",
    "entry": n,
    "patches": [
        {"id": "R37-I2-PFV4-12REG-ORBIT", "coverage_add": "R40-B2 extends the orbit to (offset, sign) cells (0,+1), (1,-1), (2,-1) in full and (3,-1) at 143/296 chunks (LP64): 0 flagged, best 6.831 vs bar of record 9.344 at N=65,229. Offset-shifted plants screened at the offset-0 alignment (this row's instrument): relation-specific partial reach, see not_covered.",
         "not_covered_replace": {"old": "offsets != 0;", "new": NEWOFF}},
        {"id": "R35-B1-BASH-ORBIT-PFV4", "coverage_add": "R40-B2: offset / sign cells (0,+1), (1,-1), (2,-1) full and (3,-1) half under the later pf_v4_12 instrument: 0 flagged.",
         "not_covered_replace": {"old": "offsets != 0;", "new": "offsets != 0 (this row's pf_v4 screen was not itself tested on offset-shifted plants; the later pf_v4_12 instrument has relation-specific partial reach at offsets 1-2, see R37-I2-PFV4-12REG-ORBIT, and R40-B2 swept (0,+1), (1,-1), (2,-1) fully and (3,-1) half, LP64 only);"}},
        {"id": "R36-B1-ORBIT-12REG", "coverage_add": "R40-B2: offset / sign cells under the pf_v4_12 instrument: 0 flagged (see R37-I2-PFV4-12REG-ORBIT).",
         "not_covered_replace": {"old": "offsets != 0;", "new": "offsets != 0 (partial reach at offsets 1-2 measured for the later pf_v4_12 instrument only, see R37-I2-PFV4-12REG-ORBIT; R40-B2 swept four LP64 offset/sign cells);"}},
        {"id": "R40-B1-BASH40-RANDOM-AUTOSEED", "not_covered_replace": {"old": "key offsets != 0 and sign +1;", "new": IDENT}},
        {"id": "R40-B1-BASH41-RANDOM-AUTOSEED", "not_covered_replace": {"old": "key offsets != 0 and sign +1;", "new": IDENT}},
    ],
    "no_patch_needed": ["R40-B1-BASH32-RANDOM-AUTOSEED and R40-B1-BASH51-RANDOM-AUTOSEED: different generators; the 4.2 misaligned control does not transfer; keep 'key offsets != 0 and sign +1' unchanged"],
    "measured_ceiling": {
        "row107_replace_clause": {"old": "non-zero key offsets (a Round 40 offset lane was still running at the audit and is not audited here)",
                                  "new": "non-zero key offsets other than the bash 4.2 LP64 cells (0,+1), (1,-1), (2,-1) swept in full and (3,-1) at 143/296 chunks by R40-B2 (0 flagged, best 6.831 vs the Round 41 bar of record 9.344 at N=65,229; the lane's own null12 bar 8.109 is superseded); of a 116-cell offset x sign x ABI axis only 5.48 cells (4.7%) are measured: offsets 4-28 at sign -1, offsets 1-28 at sign +1, the other half of offset 3 and ILP32 at every offset are untouched"},
        "row107_refs_add": "[[R40-B2-BASH42-OFFSETS-SIGN]]",
        "row51_append_to_result_cell": "; offset-shifted plants screened at offset 0 (this instrument) are recovered at 10/15 for offset 1 under keyskip1 but 0/15 under keyskip2, 3/5 for offset 2 under keyskip2 and 0/10 for sign +1, so offsets 1-2 are partly (not fully) outside the offset-0 power figure above; R40-B2 swept (0,+1), (1,-1), (2,-1) fully [[R40-B2-BASH42-OFFSETS-SIGN]]",
        "pins_to_add": ["<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 77594624 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 6.831 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 143/296 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 9.344 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 10/15 -->", "<!-- pin: R40-B2-BASH42-OFFSETS-SIGN | 5.48 cells -->"],
        "note": "the filed row text must contain each pinned token (6.831, 9.344, 143/296, 10/15, 5.48 cells, 77,594,624); the row result/coverage/control_detail above do",
    }}
json.dump(wrapper, open(os.path.join(HERE, "ledger_b2_corrected.json"), "w"), indent=1)
for t in ("77594624", "6.831", "9.344", "143/296", "10/15", "5.48 cells"):
    print(t, t in json.dumps(n))
