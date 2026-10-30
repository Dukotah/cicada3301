#!/usr/bin/env python3
"""Round 37 X1: apply audited lane ledger rows/patches to LEDGER.json.
Idempotent: always rebuilds from LEDGER.pre-x1.json (pre-edit copy)."""
import json, os, re, copy, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R37 = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(R37, "..", ".."))
PRE = os.path.join(HERE, "LEDGER.pre-x1.json"); OUT = os.path.join(LP, "LEDGER.json")
doc = json.load(open(PRE, encoding="utf-8")); E = doc["entries"]; byid = {e["id"]: e for e in E}
N0 = len(E)
PFX = "liber-primus/analysis/round37/"


def jl(p):
    d = json.load(open(os.path.join(R37, p), encoding="utf-8"))
    return d["entries"] if isinstance(d, dict) and "entries" in d else (d if isinstance(d, list) else [d])


def fullpath(p, lanedir):
    if re.match(r"(liber-primus/|analysis/|tests/|\.\./)", p):
        return p
    return PFX + lanedir + "/" + p


def norm(e, lanedir):
    e = copy.deepcopy(e); e["round"] = 37
    ev = e.pop("artifacts", None) or e.get("evidence") or []
    e["evidence"] = [fullpath(p, lanedir) for p in ev]
    if isinstance(e.get("not_covered"), list):
        e["not_covered"] = "; ".join(e["not_covered"])
    if "conditionals" in e and "three_conditionals" not in e:
        c = e.pop("conditionals"); lab = [re.sub(r"^[a-z ]+:\s*", "", s) for s in c]
        e["three_conditionals"] = {"key_space": lab[0], "transition_model": lab[1], "adjudicator_register": lab[2]}
    if e.get("threshold_fixed_in_advance") is None:
        e["threshold_fixed_in_advance"] = True
    e.setdefault("lane_dir", lanedir)
    return e


def add(e):
    assert e["id"] not in byid, e["id"]
    E.append(e); byid[e["id"]] = e


# ---------------- C1
c1 = "C1-composed-clue-readings"
X1_C1 = ("X1/R37: (i) candidates.json holds 5 of the 7 clauses of the signed 2016 message (C-2016-1..5); C-2016-6 'Seek and you will be found' and "
         "C-2016-7 'Beware false paths. Verify OpenPGP 7A35090F' (O4 clues.json) are in neither stratum, so the U1 claim '2016 clauses' is 5/7 (the two were run only as legacy Vigenere keywords, R10b B1). "
         "(ii) the U3 composition labelled 'literal' (map = LP1 word list, road = position/rune offset/length, direction = LP1-entry number) is C1's operationalization, not the only literal reading: "
         "'its words' may be LP2's own words; a cipher-word gematria pointer (lagged one word, so well-formed) and the O4 untried.md U3 seed orders/value types (6 orders, 4 v, atbash, '&' '$' boundaries) were not run. "
         "(ii-b) U2's 'line' sequences come from the koans file, which matches the printed lines (data/scream314_lp.md, used by C2-U4) only on A WARNING (05/06/03/14/73 differ); the literal printed-line sums were not run, contrary to C1's 'not otherwise recorded'. "
         "(iii) re-runs: fresh-seed U1 plants (direct/ks2, sha256ctr/ks1) rank 1 of 83/76; U3 rho1-A3 ks1/ks2 and rho3-A2 plants recovered 1.000; sweep_rows.jsonl = header + 17,392 rows, stock validate_store ok.")
for e in jl(c1 + "/ledger.json"):
    e = norm(e, c1); e["x1_r37"] = X1_C1
    if e["id"].endswith("U3-COMPOSED-MAP-ROAD-DIRECTION"):
        e["three_conditionals"]["key_space"] += " [X1: 'most literal composition' means C1's most direct operationalization; other literal readings of 'its words'/'meaning'/'numbers' were not run]"
    add(e)
p1 = json.load(open(os.path.join(R37, c1, "ledger_patches.json"), encoding="utf-8"))
c3p = {p["id"]: p for p in json.load(open(os.path.join(R37, "C3-rescore-reopened", "ledger_patches.json"), encoding="utf-8"))["patches"]}
for nr in p1["new_rows"]:
    nr = copy.deepcopy(nr); nr["lane_dir"] = "round10/" + nr.get("lane", ""); add(nr)
# F-02 (X1 override: partially-run, not measured: the semantic reading is untested)
f2 = byid["F-02"]; pt = p1["patches"][0]
f2["restated_from"] = {"status": f2["status"], "raw_status": f2.get("raw_status"), "coverage": f2.get("coverage"), "not_covered": f2.get("not_covered")}
f2["status"] = "partially-run"
f2["raw_status"] = pt["set"]["raw_status"]; f2["coverage"] = pt["set"]["coverage"]; f2["not_covered"] = pt["set"]["not_covered"]
f2["related"] = pt["set"]["superseded_by"]
f2["reopens_if"] = ("a bounded, non-lore definition of the semantic ('dictionary meaning') reading of 'their meaning is the road' is specified; or a pointer from the cipher word's "
                    "own gematria (lagged) / the O4 U3 seed orders is run under beam_v3 + panel-R36.")
f2["x1_r37"] = ("X1/R37: C1's patch set status=measured; X1 sets partially-run because the semantic reading of 'meaning' and several literal alternatives of the composed rule "
                "are untested (R7: bounds, not verdicts).")
f2["evidence"] = list(f2.get("evidence") or []) + [PFX + c1 + "/RESULTS.md"]

# ---------------- C2
c2 = "C2-recognizer-index-readings"
U4_FIX = ("X1/R37 CORRECTION: measure.py builds plaintext line boundaries from plaintext-rune counts (plens) but sums over the position array that still holds zero-valued interrupter slots, "
          "so lines are misaligned on pages with interrupters (03: 7, 14: 2, 73: 1). Re-aligned (rerun_u4.py): 03 = 3/8 (not 4/8), p(shuffle) 0.09-0.13 (not 0.025); pooled 21/60 (not 22/60), p 5e-4; "
          "pages p<0.05 = 1 (01 only), not 2. Pages 01/05/06 have no interrupters and are unchanged. Verdict NO-SEPARATION unchanged (stronger).")
for sub in ("U4-prime-line-sums", "U7-book-code", "U8-geometry"):
    for e in jl("%s/%s/ledger.json" % (c2, sub)):
        e = norm(e, c2 + "/" + sub)
        if e["id"] == "R37-C2-U4-PRIME-LINE-SUMS":
            e["three_conditionals"] = {"key_space": "six solved pages, all physical rune lines incl. titles; Gematria Primus line sums",
                                       "transition_model": "none (measured on decoded plaintext and on ciphertext; no decoder)",
                                       "adjudicator_register": "language-free statistic (primality of line sums); n/a register"}
            e["not_covered"] = "LP2 pages (no decode exists); title-excluded variants as primary; sentence/word sums; unsolved pages"
            e["x1_r37"] = U4_FIX
            e["result"] += " [X1 correction: 03 = 3/8 and pooled 21/60 after re-alignment; pages p<0.05 = 1; verdict unchanged]"
        if e["id"] == "R37-C2-U7-BOOK-CODE":
            e["three_conditionals"] = {
                "key_space": "exactly the 240 R/F-word/F-line selections (3 strings x pair/triple/single/whole x LP1/UNS x 0/1-based x fwd/rev)",
                "transition_model": "verbatim index->letter retrieval with mod wrap (no cipher/decoder); page:line:char, other books, sliding windows missed",
                "adjudicator_register": "panel-R36 pmax_ne trigram z, powered only n>=~40 (controls A,C at n=56-60); 96 of 240 cells (S2, whole-number) are n<30 and unpowered"}
            e["not_covered"] = e["not_covered"] + "; 96 short-selection cells unpowered"
            e["x1_r37"] = ("X1/R37: random-index null over the scheme's own digit alphabet is the right null for a book code (the real indices can only address that range; the order-shuffle null is the second); "
                           "control B failure explanation reproduced (rerun_u7_controlB.json: random bags of LP1 words mean pmax_ne 12.16, real sentence 14.53, 1.25 % of bags >= real; uniform random runes 1.26). "
                           "threshold_fixed_in_advance stays true: Addendum 1 corrected the null after run 1 but 0 selections were flagged in either run.")
        if e["id"] == "R37-C2-U7-BOOK-CODE-W":
            e["three_conditionals"] = {"key_space": "80 W-readout (whole indexed word) selections", "transition_model": "verbatim retrieval",
                                       "adjudicator_register": "panel-R36 pmax_ne: UNPOWERED for LP1 words (control B failed)"}
            e["x1_r37"] = "X1/R37: control B failure reproduced (rerun_u7_controlB.json); inconclusive is the right label."
        if e["id"] == "R37-C2-U8-GEOMETRY":
            e["three_conditionals"] = {"key_space": "4 turtle rules x 58 pages", "transition_model": "deterministic turtle; F = pen-up",
                                       "adjudicator_register": "glyph-template NCC/z: UNPOWERED (5/5 planted glyphs missed under two recognizers)"}
            e["x1_r37"] = ("X1/R37: inconclusive is right (planted 24-30 step glyphs not separable from shuffled strokes); the 232-render sweep is diagnostic only "
                           "and is labelled so in RESULTS and in this row (result/coverage).")
        add(e)

# ---------------- C3
c3 = "C3-rescore-reopened"
POSTHOC = {"R37-C3-U6A-N1-PT", "R37-C3-U6A-N2", "R37-C3-U6A-N4", "R37-C3-U6B-R22C"}
X1_C3 = ("X1/R37: the doublet-matched null (and, for N1-PT, the two-statistic rule) replaced the first-pass plain-shuffle null AFTER the first-pass real-data results existed "
         "(superseded_plain_shuffle_null/: p(Z) 0.0066 N1-PT, 0.0050 N2, 0.0033 N4-read, all < 0.01, became 0.41-0.50 under the final null). The replacement is mechanically justified "
         "(LP2 has 86 adjacent equal pairs; a plain shuffle gives ~447) and moves toward fewer hits, but it is a post-data change to the test, so threshold_fixed_in_advance is false for this row "
         "and the verdict rests on the final null being right. The raw-pmax statistic has marginal planted power in N2 (LATIN plant 111.31 vs null q99 111.12).")
for e in jl(c3 + "/ledger.json"):
    e = norm(e, c3)
    ar = e["three_conditionals"].get("adjudicator_register", "")
    e["three_conditionals"]["adjudicator_register"] = ar + "; positive controls planted EN_MODERN/LATIN/GREEK only (not CY/HEBREW/NORSE/EN_NOVOWEL) for these key families"
    if e["id"] in POSTHOC:
        e["threshold_fixed_in_advance"] = False; e["x1_r37"] = X1_C3
    if e["id"] == "R37-C3-U6B-R22C":
        e["x1_r37"] += (" Degenerate-decode filter (mds<=6 or IoC*N>=4.24, decided after the keyed pass) removed only constant-output decodes "
                        "(X4 prime_index atbash_pre/none, mds=1, IoC*N 27-29; 12 rows/rel/L): audited, no non-constant row removed.")
    if e["id"] == "R37-C3-U6A-N5":
        e["x1_r37"] = ("X1/R37: best 6.304 (CY) vs actual-N bar 6.897 recomputed from null12.json; under the transferred GPD tail P(max of 2,320 >= 6.304) ~ 0.05, and the next row "
                       "(6.244, same generator phi_phi_prime_RI s-1, window 9600) is similar: the closest row is not noise-level by construction. Neither went to L=240 "
                       "(rule: only actual-N clearers do). An L=240 follow-up on the top-5 is cheap.")
    if e["id"] == "R37-C3-U5-L2-MAP":
        e["x1_r37"] = ("X1/R37: the z=6.94 reading re-scored independently: pmax 3.942 (EN_MODERN) under panel-R36; single-reading p 0.073 (plain shuffle) / 0.070 (doublet-matched), "
                       "300 draws each (rerun_z694.json). The near-flag was an English-gated artefact.")
    add(e)
for pid, p in c3p.items():
    r = byid[pid]
    r["coverage"] = ((r.get("coverage") or "") + " | " + p["coverage_add"]).strip(" |")
    if p.get("not_covered_add"):
        nc = r.get("not_covered") or ""
        if isinstance(nc, list):
            r["not_covered"] = nc + [p["not_covered_add"]]
        else:
            r["not_covered"] = (nc + "; " if nc else "") + p["not_covered_add"]
    r["three_conditionals_r37_c3"] = {
        "key_space": "only what R37 C3 regenerated (see coverage); a keystream is covered only at the listed windows",
        "transition_model": "keyskip1 + keyskip2 under beam_v3 panel_max for beam families; skip-free for N1-PT PT-feedback and for all direct (key-free) streams",
        "adjudicator_register": "panel-R36, 12 registers; positive controls planted EN_MODERN/LATIN/GREEK only"}
    r["x1_r37"] = ("X1/R37: C3's patch text 'English-only/legacy-beam conditional replaced ... remains negative' is corrected: the ORIGINAL result stays an English-only/legacy-beam result "
                   "(kept above); R37 C3 ADDS a second, re-scored result under the 12-register conditional (three_conditionals_r37_c3, coverage); status unchanged (`%s`)." % r["status"])
    if pid in ("R11-N1-NUMBER-CHANNEL", "R11-N2-NUMBER-CHANNEL", "R11-N4-NUMBER-CHANNEL", "R22-C-LITERAL-IMPERATIVES"):
        r["x1_r37"] += " The R37 verdict for the data-dependent / derived-stream halves uses a doublet-matched null chosen after the first pass (see the R37-C3 rows)."

# ---------------- T1
for e in jl("T1-12reg-plumbing/ledger.json"):
    e = norm(e, "T1-12reg-plumbing")
    e["x1_r37"] = ("X1/R37: NO-ERROR-FOUND. Stock validate_store on the R35 B1 9-wide store (276,242 rows) and the R36 B1 12-wide store (276,242 rows) ok; check_r3_store [] on both; "
                   "derive_clusters(panel-R36) = 10 clusters, derive_clusters(R32 9-register panel) = the old 7; panelmax_bar/contract and hitfn20 refuse panel-R36 (rerun_t1.json); "
                   "ci.yml:53 runs tests/test_12reg_plumbing.py.")
    add(e)

# ---------------- I1 / I2 (only if the lane filed RESULTS.md and ledger.json)
I1D, I2D = "I1-free-null", "I2-pfv4-12reg"
if os.path.exists(os.path.join(R37, I1D, "RESULTS.md")) and os.path.exists(os.path.join(R37, I1D, "ledger.json")):
    raw = json.load(open(os.path.join(R37, I1D, "ledger.json"), encoding="utf-8"))
    e = {"id": "R37-I1-FREE-NULL-LMATCHED", "round": 37, "lane": "I1", "lane_dir": I1D, "date": raw["date"], "status": "measured",
         "hypothesis": "The `free` relation can be adjudicated as evidence at L=240/400/729 once an L-matched wrong-key null is fitted under panel-R36 and a planted-key control is passed per register.",
         "positive_control": "passed for 10 registers at L=240 (OE 3/20 and EN_HALFVOWEL 7/20 fail; CY 19/20); L=400: 12/12 registers >= 19/20 (OE 19/20); L=729: 12/12 20/20 (after the coordinator-ordered completion; see x1_r37)",
         "control_detail": raw["positive_control_detail"],
         "threshold": "Gumbel/POT bars of record at N=1e6 (alpha 0.01): 20.59 / 21.67 / 24.86 at L=240/400/729; GPD bars are sensitivity only", "threshold_fixed_in_advance": True,
         "result": "bar_v3(N,L,'free') now returns panel-R36 nodes for L in {240,400,729}; free usable at L=240 for 10 registers (not OE, EN_HALFVOWEL), at L=400 and L=729 for all 12; O3 ILP32 free L=729 cell re-decoded 15.157 (LP1_REAL) = NOISE (null max 15.54 of 562 draws; family-wise p ~0.95).",
         "coverage": "null draws 701 / 1335 / 726 / 562 at L=120/240/400/729 (target 2,000 not met; fitted from what ran), shuffled-LP2 wrong keys from the six B1/B2 survivor families; controls 20 free_q05 plants x 12 registers x 3 L (720 plants).",
         "three_conditionals": {"key_space": "free-relation null from the six B1/B2 survivor key families, key length 41L+64; plants use SHA-CTR keys",
                                "transition_model": "beam_v3 free (max_skip 40, max_free 2), beam_w 400, lam_u 4; free_q05 enciphering only",
                                "adjudicator_register": "panel-R36 12 registers (beam objective and pmax); not comparable with the 9-register R34 node"},
         "not_covered": "2,000 draws at any L; real-LP2-structure null; other free-like enciphering rates; other beam widths; L=120 12-register control; N=1e6 bars are far-tail extrapolations (+-1)",
         "reopens_if": "a (L, register) pair outside the licensed set is needed, or a real-structure null is drawn",
         "evidence": [PFX + I1D + "/" + x for x in ("RESULTS.md", "ADDENDUM-2026-10-30-b.md", "PREREG.md", "null_free.json", "fit_free.json", "control_free.json", "o3_cell_rejudged.json", "ledger.json")],
         "lane_ledger_raw": raw,
         "x1_r37": ("X1/R37: NO-ERROR-FOUND on the numbers: the fit (u, beta, mu, N=1e3/1e6 bars) reproduced from the raw null stream (rerun_i1_fit.json, equal to the table); control pass counts recomputed from control_free_stream.jsonl (720 plants); "
                    "bars_v3 returns 15.48/16.95/19.86 (N=1e3) and 20.59/21.67/24.86 (N=1e6) at L=240/400/729 and raises at other L. FOUND-ERROR (documentation, minor): RESULTS.md (14:54) still says 5/5 and 3/3 plants and 'no register is passed at L=400 and L=729'; "
                    "ADDENDUM-b, ledger.json and the stream (20 plants x 12 x 3) say all 12 pass at 400 (OE 19/20, at the threshold) and 729 -- the addendum is the claim of record. Also `bar_v3(..,120,'free')` still returns the R34 9-register node (17.43) while L>=240 returns 12-register nodes (L=120 12-register node needs panel='r36', 15.30).")}
    add(e)
if os.path.exists(os.path.join(R37, I2D, "RESULTS.md")) and os.path.exists(os.path.join(R37, I2D, "ledger.json")):
    for e in jl(I2D + "/ledger.json"):
        e = norm(e, I2D)
        e["x1_r37"] = ("X1/R37: NO-ERROR-FOUND. Recomputed from _null_scores.npz / _plant_scores.npz: thresholds 7.4155 / 7.4412 give FPR 8.81e-4 (calibration half) / 8.89e-4 (held-out) / per ABI 8.75e-4, 8.95e-4; "
                       "min plant power 0.952 (EN_HALFVOWEL), every register >= 0.952; sweep store validates (263,572 rows, 12 registers), check_r3_store []; survivors 65,815 + 65,971; "
                       "actual-N bars 8.113 / 8.027 recomputed from null12.json; best rows ks1 6.506 (ILP32), ks2 7.065 (LP64, seed 1354603465) equal the R36 B1 re-decode. "
                       "Limits kept: PHP FPR not re-measured; reach assumes v3 recovery 1.00 for seven registers; same orbit as R35/R36 B1 (no new seed coverage, new screen power).")
        add(e)

# ---------------- X1 row (written by build_x1_row.py)
add(json.load(open(os.path.join(HERE, "x1_row.json"), encoding="utf-8")))

# ---------------- counts + note
rec = {}
for e in E:
    rec[e["status"]] = rec.get(e["status"], 0) + 1
doc["counts"]["total"] = len(E); doc["counts"]["by_status"] = rec
doc["counts"]["note"] = doc["counts"]["note"] + (
    " | Round 37 X1 merged 2026-10-30: lanes T1/C1/C2(U4,U7,U8)/C3 filed after refute-by-default audit (+%d rows incl. retro-rows R10-L2-MAP, R10-L3-ROAD and X1; I1/I2 only if their RESULTS.md existed); "
    "F-02 -> partially-run; R11-*/R22-C/R10-* restated with an added 12-register result (original English-only result kept); U4 line-alignment error corrected; "
    "C3 post-data null swap recorded as threshold_fixed_in_advance=false on 4 rows." % (len(E) - N0))
json.dump(doc, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("entries", len(E), rec)
