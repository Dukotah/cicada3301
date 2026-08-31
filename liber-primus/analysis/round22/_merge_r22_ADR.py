"""Round 22 coordinator merge: append lane A / D / R entries into the central
liber-primus/LEDGER.json, add the red-team's N2 citation to the already-merged R22-B
coverage note, recompute counts, and append an R22 merge note.

The central LEDGER.json is hand-edited for round entries (build_ledger.py's HAND list
does NOT contain R20/R21/R22, so rebuilding would DROP them). Lane B already merged
R22-B and R22-C directly into the JSON; this script does the same for A/D/R.

Run:  python3 analysis/round22/_merge_r22_ADR.py
Then: python3 analysis/handoff/validate_ledger.py   (Unsound negatives must be 0)
"""
import json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", ".."))          # liber-primus/
LEDGER = os.path.join(LP, "LEDGER.json")

KEYS = ["id", "lane", "hypothesis", "status", "round", "date", "threshold",
        "threshold_fixed_in_advance", "positive_control", "control_detail", "null",
        "result", "coverage", "not_covered", "evidence", "reproduce", "supersedes",
        "superseded_by", "reopens_if", "priority", "source_register", "raw_status",
        "notes", "evidence_missing"]

A = {
    "id": "R22-A-SELFEMBEDDED-READ",
    "lane": "22/A-selfembedded-read",
    "hypothesis": "Roadmap X2 read literally: the hidden message is a SELECTION (acrostic / "
        "every-k-th rune / diagonal fold read) OF THE ALREADY-SOLVED PLAINTEXT, not of the "
        "ciphertext -- 'discover the truth inside yourself / seek within' + 'test the knowledge' "
        "as an instruction to look INSIDE the pages already decrypted. Distinct from Round 11 "
        "(N1-N5/S1-S2 worked the CIPHERTEXT number/value/separator channels); this works the "
        "DECRYPTED English plaintext of the 5 rig-reproduced pages.",
    "status": "negative",
    "round": "22/A",
    "date": "2026-08-29",
    "threshold": "Pre-registered before any candidate scored. Recognizer: src/lp/score.py "
        "score_norm (KJV-weighted English quadgram). SURVIVOR iff score_norm > candidate's OWN "
        "size-matched null bar at FPR=0.001 (per selection LENGTH, 1000 order-shuffles of the "
        "source, seed 3301) AND it clears the FAMILY-WISE bar (max null score over all lengths). "
        "No fixed score bar; the retired -5.5 bar is not used. Phase-0 positive control required "
        "planted-acrostic recovery >= 1.0 before the real sweep was trusted (Q5 kill gate).",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": "PHASE0-GATE.py planted a known English message at (a) every-7th and "
        "(b) width-13-diagonal positions inside an i.i.d. length-matched control (1887 letters, "
        "seed 3301) and ran the FULL sweep. Both plants RECOVERED as the top selection ranked by "
        "excess over their own size-matched null bar (every-k7 excess +2.088; diag w13 excess "
        "+2.105). Measured recovery = 2/2 = 1.000 -> GATE PASS. The instrument provably sees a "
        "self-embedded acrostic when one is present, so the real-data null is a genuine bound.",
    "null": "Per selection LENGTH: distribution of score_norm over random contiguous slices of "
        "that length from 1000 order-shuffles of the source symbols (histogram-preserving, "
        "destroys order, seed 3301). FPR=0.001 -> 99.9th percentile per-cell bar. Family-wise "
        "bar = max over all null draws across all lengths. Controls for 'English letters leak "
        "through any selection of English text'.",
    "result": {
        "overall": "NEGATIVE / CLEAN NULL",
        "selection_functions": 3508,
        "family_survivors": 0,
        "per_cell_survivors_fpr001": "4 (letters) + 2 (runes) = 6 vs 3.5 expected by chance over "
            "3508 tests -- statistically indistinguishable from zero; each clears by a trivial "
            "margin (excess 0.01-0.21) and is unreadable gibberish (best -5.37/-5.25 vs real "
            "English ~-2.2)",
        "note": "'seek within / test the knowledge' as a self-embedded acrostic/every-k/diagonal "
            "read of the rig-solved pages is CLEAN NEGATIVE. Instrument finding: width-w main "
            "diagonal == every-(w+1) at offset 0, so diagonals are subsumed by the every-k family. "
            "Language-agnostic secondary stats (IoC*N, min-distinct-32, base32 frac, gzip ratio) "
            "show no structured outlier either.",
    },
    "coverage": "Selection-FUNCTION coverage (NOT key space; the transform is identity on "
        "already-decrypted runes, so the selection IS the swept axis). 3508 selection functions = "
        "1754 per representation x 2 {letter stream 1887, greedy rune-index stream 1769}: "
        "every-k for k in [2,40] over all offsets (~780) + reversed every-k (~780) + "
        "diagonal/anti-diagonal folds w in [2,60] (~118). Search space = the 5 solved pages "
        "validate.py reproduces (A WARNING, SOME WISDOM, two KOANs, WELCOME), concatenated in "
        "book order. Power = Phase-0 recovery 1.000 on planted acrostics of the same shape.",
    "not_covered": [
        "Printed-line/word acrostics using true page-image line-break + word-spacing geometry "
        "(only the concatenated transliteration was available; physical layout unreconstructed) "
        "-- THE SHARPEST REOPENER, the one place a self-embedded read could still hide",
        "The wider community-solved LP corpus beyond the 5 rig-reproduced pages (AN END / parable "
        "material not in SOLVED-PAGES.json)",
        "Keyword-cued and two-stage/recursive selections (every rune after a cue word)",
        "Every-k for k>40 and fold widths w>60",
        "Non-English target registers beyond the base32/IoC/gzip secondary screen",
        "The /dev/urandom pad branch (a selection-of-plaintext null says nothing about it)",
    ],
    "evidence": [
        "liber-primus/analysis/round22/A-selfembedded-read/PREREG.md",
        "liber-primus/analysis/round22/A-selfembedded-read/RESULTS.md",
        "liber-primus/analysis/round22/A-selfembedded-read/ledger.json",
        "liber-primus/analysis/round22/A-selfembedded-read/sweep_results.json",
        "liber-primus/analysis/round22/A-selfembedded-read/PHASE0-GATE.py",
        "liber-primus/analysis/round22/A-selfembedded-read/run_sweep.py",
        "liber-primus/analysis/round22/A-selfembedded-read/lib_selfread.py",
    ],
    "reproduce": "cd liber-primus && python3 tests/validate.py (5/5) && "
        "cd analysis/round22/A-selfembedded-read && python3 PHASE0-GATE.py (recovery 1.000 PASS) "
        "&& python3 run_sweep.py (0 family survivors -> NULL).",
    "supersedes": "",
    "superseded_by": None,
    "reopens_if": "A first-rune-of-each-PRINTED-LINE acrostic using the real page-image line "
        "geometry (not the concatenated transliteration this lane had) -- the sharpest reopener; "
        "OR a self-embedded read over the WIDER community-solved LP corpus; OR keyword-cued / "
        "two-stage selections; OR a non-English target register with its own LM.",
    "priority": "high-prior-bounded-novel",
    "source_register": "English quadgram (KJV-weighted) primary + language-agnostic secondary "
        "panel (IoC*N, min-distinct-32, base32 fraction, gzip ratio)",
    "raw_status": "NULL, control-validated. 3508 selection functions over the 5 solved pages, "
        "pos-control recovery 1.000, 0 family-wise survivors.",
    "notes": "Roadmap lens X2, NEVER run before this round. Doctrine R2 coverage x power reported "
        "together; R3 language-agnostic stats persisted per candidate at run time; R7 this is a "
        "BOUND over the enumerated selection set on the rig-solved 5 pages, not 'X2 closed'. "
        "Seal note (R21 L1) moot: no survivor to certify; any bar-clearer would be "
        "FLAGGED-FOR-ORACLE. Red-team (R22-R) confirmed no silent re-read of a Round-11 lens.",
}

D = {
    "id": "R22-D-ILLUSTRATION-DROPCAP",
    "lane": "22/D-illustration-dropcap",
    "hypothesis": "Roadmap S3: the illumination / drop-cap channel carries data -- the presence, "
        "page-position, ordering, gap structure, centroid, and rune-identity of the large red "
        "illuminated drop-caps across the 58 committed LP2 page scans encode a hidden integer/"
        "letter sequence.",
    "status": "negative",
    "round": "22/D",
    "date": "2026-08-29",
    "threshold": "Survivor iff p < 0.01 Bonferroni over 5 order/identity statistics vs a "
        "seed-3301 null (10000 shuffles / random-alphabet draws, size-matched). No score bar.",
    "threshold_fixed_in_advance": True,
    "positive_control": "passed",
    "control_detail": "P0.2-style hand-count on 4 pages (0/8/15 present, 9 absent) + page-0 "
        "illuminated-rune identity 'S' from canonical_pages.json all reproduced (4/4 + page0=S). "
        "The colour-separable red drop-cap needs no OCR (unlike the unreliable dense-rune OCR "
        "floor 0.145), so extraction is control-validated.",
    "null": "seed 3301, 10000 shuffles / random-alphabet draws; size-matched.",
    "result": {
        "overall": "NEGATIVE (drop-cap channel)",
        "n_pages": 58,
        "n_illuminated": 15,
        "n_illuminated_is_prime": False,
        "n_illuminated_is_29": False,
        "illuminated_runes_read": "SLXHXFUMDSFAINGP",
        "min_p": 0.1795,
        "survivor": False,
        "note": "presence/order/gap/centroid/illuminated-rune-identity all clear no Bonferroni "
            "p<0.01 bar (min p=0.18). First LP2 drop-cap catalog built (features.json). NOT a "
            "verdict on figural motifs (crosses/trees/shrouded-corpse/mayflies), which remain "
            "un-coded as data.",
    },
    "coverage": "Full drop-cap presence/position/identity channel over all 58 committed page "
        "scans (corpus/E-tooling/.../LP/0..57.jpg, 2400x3600; duplicate henkman set). First LP2 "
        "drop-cap catalog (features.json). RUNNABLE -- page scans are in-repo, this lane was NOT "
        "blocked on assets.",
    "not_covered": [
        "Figural-motif catalog (type/count/orientation of crosses, trees, shrouded-corpse figure, "
        "mayflies) per page -- THE REOPENER; needs hand-annotation or a black-channel shape pass "
        "entangled with the dense-rune OCR floor. Documented, not executed.",
        "Page 57's illuminated rune absent from canonical_pages.json (1-page identity gap).",
    ],
    "evidence": [
        "liber-primus/analysis/round22/D-illustration-dropcap/PREREG.md",
        "liber-primus/analysis/round22/D-illustration-dropcap/RESULTS.md",
        "liber-primus/analysis/round22/D-illustration-dropcap/ledger.json",
        "liber-primus/analysis/round22/D-illustration-dropcap/extract_illustration.py",
        "liber-primus/analysis/round22/D-illustration-dropcap/features.json",
        "liber-primus/analysis/round22/D-illustration-dropcap/order_results.json",
        "liber-primus/analysis/round22/D-illustration-dropcap/illuminated_rune_results.json",
    ],
    "reproduce": "cd liber-primus && python3 tests/validate.py (5/5) && "
        "cd analysis/round22/D-illustration-dropcap && python3 extract_illustration.py && "
        "python3 test_order.py && python3 test_illuminated_runes.py (min p=0.18, survivor=False).",
    "supersedes": "",
    "superseded_by": None,
    "reopens_if": "A per-page figural-motif integer sequence (type/count/orientation of crosses, "
        "trees, shrouded-corpse figure, mayflies) is catalogued and tested against the same "
        "seed-3301 null.",
    "priority": "high-prior-bounded-novel",
    "source_register": "language-agnostic order/identity statistics (gap-variance, presence "
        "compressibility, centroid rank-correlation, illuminated-rune entropy); no English scorer",
    "raw_status": "NEGATIVE on the drop-cap channel (min p=0.18), control-validated. RUNNABLE, "
        "not blocked on assets. Figural-motif channel not yet coded.",
    "notes": "Roadmap lens S3, NEVER run before this round -- first LP2 drop-cap catalog. Distinct "
        "from Round-11 S2 (inline separator glyphs, not page-scan illustrations; red-team R22-R "
        "confirmed no overlap). Doctrine R7: BOUND on the drop-cap channel, not 'S3 closed' -- the "
        "figural-motif channel is the live reopener.",
}

R = {
    "id": "R22-R-REDTEAM",
    "lane": "22/R-redteam",
    "hypothesis": "Standing red-team audit (doctrine R6) of Round-22 lanes A/B/C/D: refute, don't "
        "confirm. Target = the repository's own current Round-22 claims. Reports FOUND-ERROR or "
        "NO-ERROR-FOUND, never 'confirmed'.",
    "status": "audit",
    "round": "22/R",
    "date": "2026-08-29",
    "threshold": "Would flag: a real geometric outlier B suppressed; an undisclosed re-read of a "
        "Round-11 negative; a retired -5.5-bar relapse or non-3301 null; a control with "
        "recovery<0.90. Reports FOUND-ERROR / NO-ERROR-FOUND.",
    "threshold_fixed_in_advance": True,
    "positive_control": "n/a-audit",
    "control_detail": "Re-read one positive control per lane for recovery>=0.90, bar provenance "
        "(no -5.5), seed-3301 nulls: A recovery 1.0; B phase-0 square fires 5/6 stats; C all "
        "controls 1.0 incl X3b/X4 HIT + held-out; D 4/4 + page0=S. No lane on an unvalidated "
        "instrument; retired -5.5 bar used nowhere.",
    "null": "n/a (audit lane; independently recomputed B's family-wise correction from raw "
        "ledger rows and cross-checked no-silent-reread vs all 7 Round-11 lenses).",
    "result": {
        "overall_verdict": "NO-ERROR-FOUND",
        "found_errors": 0,
        "b_familywise_reconfirmed": "6 shape-stat p<0.01 candidates, P(>=6)=0.072 (Poisson "
            "lambda 2.88) / 0.071 (binomial) -- consistent with multiple-comparisons noise; "
            "0 clear the Bonferroni flag bar; B's 0-flagged-for-oracle is SOUND, no combo reopens. "
            "The 'components' candidate proved a discrete-stat Gaussian-z artifact, not a "
            "suppressed hit.",
        "disclosure_gap": "ONE low-severity, non-blocking: B/g3 coord_pair_rate re-touches "
            "Round-11 N2 route (d) 'coordinate pairs' with a different statistic and did not cite "
            "it; both agree NEGATIVE, changes no verdict. Recommendation APPLIED this round: B's "
            "RESULTS.md and this LEDGER coverage note now cite N2.",
        "c_x4_n5": "C's X4-totient re-adjudication of Round-11 N5 under the repaired instrument is "
            "fully disclosed and exemplary; X4 raw-prime-value/index is new.",
    },
    "coverage": "All 4 Round-22 lanes (A/B/C/D) audited on 3 axes: (1) B's family-wise correction "
        "independently recomputed from raw ledger rows (hit counts match B's table, 0 mismatches); "
        "(2) no-silent-reread cross-checked vs all 7 Round-11 lenses (N1-N5,S1-S2) read from "
        "source; (3) one positive control per lane re-read for recovery>=0.90, bar provenance, "
        "seed-3301 nulls.",
    "not_covered": [
        "Re-execution of the 72-combo / 185-op sweeps from source (trusted committed ledger rows "
        "as faithful to code)",
        "Numerical correctness of B's self_intersections sampler and D's colour-mask extractor "
        "beyond their passing planted controls",
        "Regeneration of the .gitignore'd PNG renders",
    ],
    "evidence": [
        "liber-primus/analysis/round22/R-redteam/RESULTS.md",
        "liber-primus/analysis/round22/R-redteam/ledger.json",
    ],
    "reproduce": "Read RESULTS.md; recomputed statistics are inline (Poisson/binomial P>=6, "
        "per-candidate sigma, hit-count recomputation from B's g3_results.json / ledger rows).",
    "supersedes": "",
    "superseded_by": None,
    "reopens_if": "A future round re-executes the A/B/C/D sweeps from source and finds a ledger "
        "row that does not match committed code, OR a fifth Round-22 claim is added that this "
        "audit did not cover.",
    "priority": "red-team",
    "source_register": "n/a (audit of instruments/claims, not a decode)",
    "raw_status": "NO-ERROR-FOUND. Independently reconfirmed B's family-wise 0-survivor "
        "(P(>=6)=0.072, noise). One low-severity non-blocking disclosure gap (B G3 coord_pair ~ "
        "N2 route d) -- fix applied. No lane on an unvalidated instrument; no -5.5 relapse.",
    "notes": "Doctrine R6 standing red-team lane. Verdict NO-ERROR-FOUND. The single "
        "recommendation (B cite N2 route d for the coord-pair sub-detector) was APPLIED by the "
        "Round-22 coordinator to both B's RESULTS.md and R22-B's LEDGER coverage note.",
}

with open(LEDGER, encoding="utf-8") as f:
    doc = json.load(f)

existing = {e["id"] for e in doc["entries"]}
NEW = [A, D, R]
for e in NEW:
    if e["id"] in existing:
        raise SystemExit(f"DUPLICATE: {e['id']} already present -- aborting, no double-merge.")
    for k in KEYS:
        e.setdefault(k, None)
    e["evidence"] = e.get("evidence") or []

# Apply red-team N2 citation to the already-merged R22-B coverage note.
for e in doc["entries"]:
    if e["id"] == "R22-B-TURTLE-SPATIAL-RENDER":
        cite = (" [R22-R red-team note: the G3 coord-pair sub-detector re-touches Round-11 "
                "N2 route (d) 'coordinate pairs' (analysis/round11/N2) with a different "
                "statistic; both NEGATIVE, distinct statistic not a silent re-read.]")
        if "N2 route (d)" not in (e.get("coverage") or ""):
            e["coverage"] = (e.get("coverage") or "") + cite

doc["entries"].extend(NEW)

# Recompute counts.
by_status = collections.Counter(e["status"] for e in doc["entries"])
doc["counts"]["total"] = len(doc["entries"])
doc["counts"]["by_status"] = dict(by_status)

# Append an R22 merge note.
note = doc["counts"].get("note", "")
r22note = (" Round 22 merged 2026-08-29 (coordinator): 5 lanes. Lane B pre-merged R22-B-TURTLE "
    "+ R22-C-LITERAL-IMPERATIVES (130->132); coordinator appended R22-A-SELFEMBEDDED-READ, "
    "R22-D-ILLUSTRATION-DROPCAP (both negative, control-validated) and R22-R-REDTEAM (audit, "
    "NO-ERROR-FOUND) -> 132->135. Round 22 read the four signed-hint channels for the first time: "
    "self-embedded plaintext acrostic (X2/A), numbers-as-direction (G1/B), koans-as-operations "
    "(X1/X3/X4/C), art-as-data (S3/D) -- all CLEAN control-validated NEGATIVES. Standing verdict "
    "unchanged: LP2 0-54 remains OTP-class. Sharpest surviving reopener = A's printed-line-geometry "
    "acrostic (real page-image line breaks). validate.py 5/5 and validate_ledger.py Unsound=0 "
    "before and after.")
if "Round 22 merged" not in note:
    doc["counts"]["note"] = note + r22note

with open(LEDGER, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1, ensure_ascii=False)

print(f"wrote LEDGER.json: {len(doc['entries'])} entries")
print("R22 ids:", sorted(x["id"] for x in doc["entries"] if "R22" in x["id"]))
print("by_status:", dict(by_status))
