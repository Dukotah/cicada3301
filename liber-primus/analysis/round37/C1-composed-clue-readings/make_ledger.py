#!/usr/bin/env python3
"""C1: build ledger.json (3 rows) and ledger_patches.json from control.json / sweep_summary_final.json / O4 readings.json. Writes both files only."""
import os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "sweep_summary_final.json"))); C = json.load(open(os.path.join(HERE, "control.json")))
SW = json.load(open(os.path.join(HERE, "sweep_summary.json")))
RD = {r["id"]: r for r in json.load(open(os.path.join(LP, "analysis", "round36", "O4-clue-coverage", "readings.json")))}
PANEL = "a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c"
today = time.strftime("%Y-%m-%d")


def best(sub):
    e = S["subfamilies"][sub]
    return "; ".join("%s N=%d best %.3f (%s, %s) vs bar_v3 %.3f actual-N / %.3f N=1e6 (bar12 %.3f / %.3f)" % (
        rel, v["N"], v["best_pmax"], v["best_cell"], v["best_register"], v["bar_v3_actualN"], v["bar_v3_N1e6"], v["bar12_actualN"], v["bar12_N1e6"]) for rel, v in e.items())


ev_common = ["analysis/round37/C1-composed-clue-readings/PREREG.md", "analysis/round37/C1-composed-clue-readings/RESULTS.md", "analysis/round37/C1-composed-clue-readings/control.json",
             "analysis/round37/C1-composed-clue-readings/sweep_summary_final.json", "analysis/round37/C1-composed-clue-readings/sweep_rows.jsonl"]
common = {"round": 37, "lane": "C1", "date": today, "threshold_fixed_in_advance": True, "positive_control": "passed", "sweep_store": "analysis/round37/C1-composed-clue-readings/sweep_rows.jsonl",
          "source_register": "round36/P1-panel-r36 panel12 " + PANEL, "evidence": ev_common,
          "threshold": "bars_v3 (alpha 0.01, family lp2) at actual N and N=1e6, L=120 screen / L=240 gate, cross-checked with bar12 from round36/B1 null12.json; fixed in PREREG.md before any output. Clearer -> L=240 -> flagged-for-oracle."}
u1c = C["U1"]; u2c = C["U2"]; u3c = C["U3"]
rows = [
    dict(common, id="R37-C1-U1-CLUE-STRINGS", status="negative",
         hypothesis="The LP2 keystream is derived from a 2016-message clause, a short noun phrase of it, or an LP1 imperative, via the direct text key, SHA-256-CTR(string) (B-04 code) or PBKDF2-SHA256(string,'3301',10000) (R16 K2 config).",
         control_detail="Plant under ONE candidate per route and relation (6 plants: direct U1-001, sha256ctr U1-002, pbkdf2 U1-003; EN_MODERN held-out L=240; real enc_exact/enc_pair): planted string ranked #1 in the full route grid in 6/6 (of 83/76/117 keys), L=120 pmax %.1f-%.1f vs bar_v3(1e6) 9.03-9.24, L=240 recovery >= 0.99, runner-up pmax 5.2-6.6." % (min(e["planted_pmax120_in_grid"] for l in u1c.values() for e in l), max(e["planted_pmax120_in_grid"] for l in u1c.values() for e in l)),
         coverage="42 new + 41 B04-covered clue strings (candidates.json); strata N all 3 routes (hash routes x {UPPER, as-written}), stratum R direct+PBKDF2 only; x rel{ks1,ks2} x sign +-1 x offset 0..7 on LP2[:120]; 8,832 decodes (4,416 per relation); " + best("U1") + ". 0 clear the actual-N bar, 0 gate runs, 0 flagged, 0 near-miss.",
         result="negative (bounded): best %.3f/%.3f, bars 7.18/7.06 at actual N; the 2016 clauses specifically: best 5.078 (U1-001 'ITS WORDS ARE THE MAP' direct, LP1_REAL)." % (S["subfamilies"]["U1"]["keyskip1"]["best_pmax"], S["subfamilies"]["U1"]["keyskip2"]["best_pmax"]),
         three_conditionals={"key_space": "83 clue-derived strings (see candidates.json) x routes direct / sha256_ctr mod29 (B-04) / PBKDF2-SHA256-10000 salt '3301' mod29 (R16 K2); forms UPPER + as-written; offsets 0..7; sign +-1",
                             "transition_model": "keyskip1 + keyskip2 under beam_v3 panel_max (beam_w 400, lam_u 4), L120 screen / L240 gate; no free relation; no atbash; no pf_v4 screen (full grid decoded)",
                             "adjudicator_register": "panel-R36 12 registers; planted control is EN_MODERN only (power for the other registers under these specific constructions not re-measured; R36 B1 measured v3 recovery for GREEK/HEBREW/NORSE with other keys)"},
         not_covered="lower-case and despaced hash forms; other KDFs/iterations/salts (only pbkdf2_sha256_10000 salt '3301'); rej29/other reductions; other hashes/CTR byte orders; atbash; offsets > 7; strings not derived from the 2016 clauses/LP1 imperatives (other signed texts, 2012-14 clues); SHA-CTR route for the 41 covered strings (B04 legacy English-only beam is its only coverage); heads with >2 skips in 24 runes; free relation; L=31.",
         reopens_if="a clue-derived string beyond candidates.json is proposed with a stated reading; or the key is shown to be a hash/KDF output of a string whose form is not UPPER/as-written.",
         notes="Correction to O4 untried.md U1: 38 of 41 LP1-imperative/clue strings were already in round13/B04 lp_line/lp_word seeds (SHA/legacy route); only round26/C and the R16 core list lacked them."),
    dict(common, id="R37-C1-U2-LP1-NUMBER-SCHEDULES", status="negative",
         hypothesis="LP2 is enciphered with a key schedule built from LP1's own Gematria sums (per word / line / sentence / running cumulative; prime or index channel; mod 29 or 28), as an additive keystream or as pointer jumps through the LP1 rune stream at ciphertext word boundaries.",
         control_detail="32/32 planted variants (16 variants x mode a/b; EN_MODERN held-out L=240, real keyskip encipherers, random offset): min L=120 pmax %.1f, min L=240 pmax %.1f (bars 9.0-9.5), min recovery240 %.3f." % (min(e["pmax120"] for e in u2c), min(e["pmax240"] for e in u2c), min(e["recovery240"] for e in u2c)),
         coverage="16 variants x {additive a, pointer-jump b} x rel{ks1,ks2} x sign +-1 x offset 0..7 x page heads {0,1,2} (key restarts per page) = 3,072 decodes (1,536 per relation); " + best("U2") + ". 0 clear, 0 flagged, 0 near-miss.",
         result="negative (bounded); best 4.793 / 4.548 vs bars 6.78 / 6.67 at actual N.",
         three_conditionals={"key_space": "LP1 sequences from the 94 clues.json LP1 sentences (726 words; line sums from armada18 text lines = convenient, not the printed lines); 2 channels x 4 sequences x 2 moduli x 2 modes; offsets 0..7; page heads 0-2",
                             "transition_model": "keyskip1 + keyskip2 under beam_v3 panel_max; schedule K' indexed by cipher-rune position (skips do not re-time the word-boundary jumps); no free relation",
                             "adjudicator_register": "panel-R36 12 registers; control EN_MODERN only"},
         not_covered="phi(p)/prime-index channels; atbash; schedules applied per ciphertext line or per page; jump direction minus; base keys other than the LP1 rune stream (b); starting sequence index other than 0 with offset only 0..7 in the sequence; pages > 2 as separate restarts; per-word constant (non-stream) application is U3 A1; LP1 printed line breaks; heads with >2 skips; free relation.",
         reopens_if="a stated reading fixes the base key / sequence start for (b), or the printed LP1 line layout is recovered and per-line sums differ from the text lines used here."),
    dict(common, id="R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION", status="negative",
         hypothesis="'Its words are the map, their meaning is the road, their numbers are the direction': LP1's word list is a codebook; each unsolved word reaches an entry by position k / rune offset / length; the entry's Gematria value (mod 29 or 28) is the signed advance applied at each cleartext word boundary (per-word shift A1, cumulative shift A2, or key-pointer advance through the LP1 rune stream A3).",
         control_detail="24/24 planted cells (rho x M x {A1,A2,A3-ks1,A3-ks2}; independent encipherer; EN_MODERN held-out L=240 on page-0 word structure; random start s and sign): min L=120 pmax %.1f (bar 9.0-9.2), recovery240 >= %.3f. A1/A2 are beam-free exact inversions (recovery trivial, power shown by pmax)." % (min(e["pmax120"] for e in u3c), min(e["recovery240"] for e in u3c)),
         coverage="rho{position, rune offset, word length} x M{29,28} x start s 0..28 x sigma +-1 x modes {A1,A2,A3 rel1,rel2} x page heads {0,1,2} (k restarts per page) = 4,176 decodes (2,088 direct, 1,044 ks1, 1,044 ks2); " + best("U3") + ". The literal composition (rho1 x A3, M29, s=0) best 3.035. 0 clear, 0 flagged, 0 near-miss.",
         result="negative (bounded); best 5.085 (direct A2) vs keyskip1 bar 6.90 at actual N.",
         three_conditionals={"key_space": "the composed rule family as written in PREREG section 3 (3 roads x 2 moduli x 29 starts x 2 signs x 3 modes x 3 pages); pointer from the ciphertext word's own gematria sum EXCLUDED (not a well-formed cipher)",
                             "transition_model": "A1/A2 direct (no key stream, no skip relation); A3 under keyskip1/keyskip2 beam_v3 panel_max with K' indexed by cipher position; the rule itself is a new relation and was planted",
                             "adjudicator_register": "panel-R36 12 registers; A1/A2 judged against the keyskip1 beam bar (conservative); control EN_MODERN only"},
         not_covered="semantic (dictionary-meaning) indexing of ciphertext words; pointer from word gematria; alternative codebooks (LP1 sentences/lines, other books); rule applied across page boundaries with k not restarting beyond page-0 head; atbash; start index beyond 28; M other than 29/28; detail of how a real author would handle interrupters inside words; composition orders other than road-then-direction; pages > 2 as heads; free relation.",
         reopens_if="a reading of 'meaning' that yields a determinate per-word index (not position/length) is stated; or the LP1 codebook order is shown to differ from document order."),
]
json.dump({"$comment": "Round 37 C1: three rows; statuses negative are bounded and construction-conditional, never solved/closed/exhausted. Not merged into LEDGER.json by the lane.", "lane": "C1", "date": today, "entries": rows},
          open(os.path.join(HERE, "ledger.json"), "w"), indent=1)

# ---------------------------------------------------------------- patches
def rr(ids): return [RD[i] for i in ids]


l2 = rr(["R%02d" % i for i in range(1, 10)]); l3 = rr(["R10", "R11", "R12"])
def newrow(rid, lane, rs, hyp, extra):
    return {"id": rid, "round": 10, "lane": lane, "date": "2026-08 (round 10; documented by O4 2026-10-30)", "status": "measured", "kind": "retro-row written by C1 from O4 readings.json; code not re-run",
            "hypothesis": hyp, "result": " | ".join("%s: %s" % (r["id"], r["verdict"]) for r in rs),
            "coverage": "; ".join("%s %s" % (r["id"], r["name"]) for r in rs),
            "three_conditionals": {"key_space": "; ".join(r["conditionals"]["key_space"] for r in rs), "transition_model": "none: cleartext-layer / key-free reads of the CIPHERTEXT's word, line and page structure",
                                   "adjudicator_register": "ENGLISH ONLY: rune 4-gram trained on English-in-futhorc and English score_norm (no non-English register, no panel)"},
            "positive_control": "none for the Round 9/10 reads except the L3 T2-T4 validation gate (oracle z=79.7); round10/SYNTHESIS.md 'Instrument caveats'",
            "not_covered": "; ".join(sorted(set(r["not_covered"] for r in rs))) + "; the DECODED (keyed) plaintext layer; non-English registers; anything under beam_v3 / panel-R36 (R37 C1 re-reads the clue as keys/schedules, not these cleartext reads)",
            "evidence": sorted(set(r["cite"] for r in rs)), "notes": extra}
patch = {"$comment": "R37 C1 ledger patches (not applied by the lane). F-02 is stale: Round 10 L2-map and L3-road treated the clauses first-class but are absent from LEDGER.json.",
         "patches": [{"id": "F-02", "set": {"status": "measured", "raw_status": "stale: clauses 1-2 were attacked in Round 10 (L2-map M1-M9, L3-road T1-T5) and clause 3 in Round 9 DIRECTION; all English-only, cleartext-layer; composed/keyed readings run in R37 C1",
                                           "coverage": "Round 9 DIRECTION (2,670 readings, negative, no positive control); Round 10 L2-map M1-M9 and L3-road T1-T5 (English-only, cleartext layer of the ciphertext); Round 37 C1: clause strings as seeds/keys (8,832 decodes), LP1 numbers as key schedules (3,072), composed map-road-direction rule (4,176), all panel-R36 12 registers, controls passed, all below bars at actual N.",
                                           "not_covered": "meaning as dictionary semantics; reads of the clauses other than C1's operationalizations; non-English reads of the Round 10 cleartext streams (O4 U5)",
                                           "superseded_by": ["R37-C1-U1-CLUE-STRINGS", "R37-C1-U2-LP1-NUMBER-SCHEDULES", "R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION", "R10-L2-MAP", "R10-L3-ROAD"]}}],
         "new_rows": [newrow("R10-L2-MAP", "L2-map", l2, "'Its words are the map': the ciphertext's own word/line/page structure (initials, finals, word sums, lengths, pointers into LP1, walks, addresses) carries the message.", "M1 pooled best z=6.94 (first-of-word/noF atbash/rev/+28; absolute -16.51 vs English threshold -13.5) never re-scored outside English (O4 U5). G1 fired on line-initial (z=6.35), explained by width-greedy typesetting r=0.72."),
                      newrow("R10-L3-ROAD", "L3-road", l3, "'Their meaning is the road': word/sentence/line/page gematria sums marked, mapped to symbols, used for selection/reordering, or as pointers into key text.", "Sums were of the LP2 ciphertext's own words only (never LP1 plaintext numbers as a key schedule; that is R37 C1 U2).")]}
json.dump(patch, open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)
print("ok", [r["id"] for r in rows])
