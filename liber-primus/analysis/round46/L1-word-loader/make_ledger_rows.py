"""R46-L1: write ledger_rows.json (LEDGER.json entry schema) from results.json. Does not touch LEDGER.json."""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
D = "liber-primus/analysis/round46/L1-word-loader/"
EV = [D + "PREREG.md", D + "RESULTS.md", D + "results.json"]
C3 = lambda ks, tm: {"key_space": ks, "transition_model": tm,
                     "adjudicator_register": "panel-R36 12 registers (sha a0682f0c...); plants English only (data/pride.txt, B6 EN mapping); non-English shuffled-word power not measured"}
base = dict(lane="round46/L1-word-loader", round="46/L1", date="2026-11-24", threshold_fixed_in_advance=True)
r41 = R["r41_R14"]; p41 = r41["plants_W1_W4"]; real41 = r41["real"]
r37 = R["r37_U2b_U3"]; p37 = r37["plants"]
sk = R["skeleton_C01"]["plants"]; sev = R["sevengram_R44"]["shape_precision"]

rows = [
    dict(base, id="R46-L1-WORD-LOADER", status="measured",
         hypothesis="One loader yields LP2's printed words from the canonical stream, joining line- and page-wrapping words (W1 rule: break at - . & $ section-sign digits; not at / or %).",
         threshold="stream sha256 == PROBLEM.json AND LP2 words == 2,896 AND test_words.py all pass (PREREG s4)",
         positive_control="passed",
         control_detail="test_words.py 10/10: stream hash; 2,896 words; 420 wrapping words (388 line + 32 page); A WARNING decoded word-by-word (atbash) and PARABLE word-by-word match the reference; 739/739 solved words align; render->parse round trip on LP2's layout exact.",
         result="PASS: 2,896 LP2 words, stream sha 023312066d... = PROBLEM.json, page lengths = dataset. Reconciled: camp7 (R41) 3,316 = 2,896 + 420 extra cuts (388 at '/', 32 at '/%'); mapcommon (R37/R38/R39) and skeleton lp2_words 2,928 = 2,896 + 32 extra cuts at '/%'; no legacy loader misses a words.py boundary. LP1 694 words, solved tail 45.",
         coverage="LP2 pages 0-54 (12,956 runes), LP1 (rtkd_master), solved tail (AN END, PARABLE).",
         not_covered=["whether the printed spaces are the plaintext's (R45-W1); transcription separators taken as canon"],
         three_conditionals=C3("n/a (instrument)", "n/a"), evidence=EV + [D + "words.py", D + "test_words.py", D + "reconcile.json"]),
    dict(base, id="R46-L1-R41-R14-RERUN", status="negative",
         hypothesis="R41-C1 R14 wordsum_selfkey (campaign7 W1-W5 x sign x atbash, per-page key reset) decodes LP2 when the words are segmented correctly (words.py).",
         threshold="R41 rule: alpha 0.0025 per level (W whole stream, P pages); crosses iff family-Z p AND raw p <= alpha vs blockperm null 100/250/1000, D=400 each (probe-chosen per PREREG s4), re-cut to words.py each draw.",
         positive_control="passed",
         control_detail="English over LP2's real layout, 2 layouts x 20 variants per regime, through words.py: regime a (true spaces in order) W1-W4 pages recognised 1760/1760 (Wilson 0.998-1.0; exact recovery and pmax > P null max 5.591); regime b (words shuffled within sentence) 1760/1760. Same plants through R41's camp7 loader: 2/1760 (a), 1/1760 (b), mean page recovery 0.48. Regime b' (lengths permuted within sentence) 0/1760 either loader.",
         result="negative: W best pmax %.3f, decision p(Z)=%.3f p(raw)=%.3f; P best pmax %.3f (%s), decision p(Z)=%.3f p(raw)=%.3f. No crossing, nothing flagged. Same scorer on R41's split segmentation reproduces R41's recorded best page 3.642." % (
             real41["best_W"], real41["decision"]["W"]["decision_p_Z"], real41["decision"]["W"]["decision_p_raw"], real41["obs_top5_P"][0][0], real41["obs_top5_P"][0][1],
             real41["decision"]["P"]["decision_p_Z"], real41["decision"]["P"]["decision_p_raw"]),
         coverage="20 variants x 55 pages + 20 whole-stream decodes on the 2,896-word segmentation (page-wrap word belongs to the page it starts on).",
         not_covered=["page-wrap word assigned to the page it ends on, or no per-page reset (whole-stream key)", "non-English registers under shuffled words", "skip-aware variants"],
         three_conditionals=C3("R41's 20 campaign7 variants (no key)", "exact deterministic inverse, per-page reset, no skips"),
         evidence=EV + [D + "arm_r41.py", D + "r41_judge.json", D + "r41_plants.json"]),
    dict(base, id="R46-L1-R37-U2B-U3-RECHECK", status="negative",
         hypothesis="R37-C1 U2b/U3 (and the rho1 U3-form rows R38-WORDNET/FREQRANK, R39-SENSE) change under the corrected loader.",
         threshold="real: re-decode exactly the jobs whose decode changes; bars_v3 at actual N (ks1 6.632, ks2 6.529, direct 6.895). plants: R37 sweep.judge().",
         positive_control="passed",
         control_detail="plants on LP2 layout (page-0 head and page-1 head that opens mid-word), words.py lengths: U2b 64/64 and U3 48/48 recovered under a and b; b' 0/64, 0/48. mapcommon lengths: U2b 64/64, U3 45/48 (rho3 on the page-1 layout 5/8).",
         result="Decoded-head word boundaries of pages 0-2 are identical under both loaders. Only difference: pages 1 and 2 open mid-word (fragments 5 of 6 and 2 of 5 runes), which changes the rho3 length value d_0. Those 928 U3 rho3 decodes re-run with the full printed length: best ks1 4.352, ks2 3.843, direct 3.697, all below bars. Every other R37/R38/R39 real decode is identical by construction.",
         coverage="928 re-decodes (U3 rho3, pages 1-2, all valid cells, s, sigma, rel); equality proof for the rest.",
         not_covered=["a key that does not restart per page (whole-stream word index)", "R38-C2-G3 cw/dw lag pointers on pages 1,2,4,5 (open mid-word): not re-run"],
         three_conditionals=C3("R37 U2b/U3 frozen grids", "beam_v3 keyskip1/keyskip2; direct A1/A2"),
         evidence=EV + [D + "arm_r37.py", D + "r37_results.json"]),
    dict(base, id="R46-L1-SKELETON-RERUN", status="negative",
         hypothesis="C-01 SKELETON word-length plaintext identification, with correctly joined page-wrap words, finds the LP2 plaintext in the repo-resident corpus.",
         threshold="original wordlen_search statistic (best exact-match count vs shuffled-pattern best per text); plants: global argmax at planted offset AND > max of 5 shuffled scans (I1 rule).",
         positive_control="passed",
         control_detail="pride over LP2 layout from a random page start: words.py a: W120 20/20, W400 20/20; legacy lp2_words a: 10/20 and 5/20 (page-wrap splits shift the alignment); b (shuffled within sentence) 0/20 both W, both loaders; b' 0/20.",
         result="chance-level: words.py full window best 584/2,896 (20.2%%, mabinogion) vs shuffled max 579 (z 1.54); W400 25.0%%, W120 34.2%%; legacy reproduces the recorded 581/1,441 (KJV). A real plaintext match would be ~100%%. Nothing flagged.",
         coverage="%d texts, %d words (data/*.txt, data/keys/*.txt, skeleton/corpus/*.txt), windows full/400/120, slack 0/1." % (R["skeleton_C01"]["corpus_texts"], R["skeleton_C01"]["corpus_words"]),
         not_covered=["any text outside the resident corpus (the row's 'full Gutenberg' extension)", "plaintext with shuffled word order (power 0)", "non-English length mappings"],
         three_conditionals=C3("resident corpus only", "exact length match (slack 0) and +-1"),
         evidence=EV + [D + "arm_skeleton.py", D + "skeleton_real.json", D + "skeleton_plants.json"]),
    dict(base, id="R46-L1-REOPEN-VERDICTS", status="measured",
         hypothesis="Corrected verdicts for the ten R45-I1 reopened word-indexed rows, with power under (a) true spaces in order and (b) words shuffled within sentence (plus b' lengths permuted within sentence).",
         threshold="PREREG s4: power >= 0.90 holds; 0.50-0.90 weakened; < 0.50 conditional.",
         positive_control="passed",
         control_detail="see R46-L1-R41-R14-RERUN, R46-L1-R37-U2B-U3-RECHECK, R46-L1-SKELETON-RERUN; 7-gram shape precision a 1.000 / b 1.000 / b' %.3f (words.py)." % sev["bp|L"]["precision"],
         result="C-01: holds under a (now 1.0; legacy 0.25-0.50), CONDITIONAL under b (0.0). R37-U2 (U2b): holds a and b (1.0). R37-U3: holds a and b (1.0). R38-WORDNET, R38-FREQRANK, R39-SENSE: real decodes identical; holds a and b by inheritance (U3 rho1 plants 1.0), not separately planted. R38-C2-G3: pages 0,3 unchanged; pages 1,2,4,5 open mid-word, not re-run; CONDITIONAL. R41-R14: re-run negative; was uninformative before (legacy power 0.001), now holds a and b (1.0). R44-7GRAM: site shapes unchanged; holds a and b. R40-R31: not word-indexed (cribs at page/sentence/section starts); unchanged INCONCLUSIVE; I1 inclusion not supported. Every row is CONDITIONAL under b' (spaces not the plaintext's boundaries): power 0.",
         coverage="ten rows", not_covered=["non-English registers", "book-scope shuffles", "G3 pages opening mid-word"],
         three_conditionals=C3("each row's own frozen space", "each row's own"), evidence=EV),
]
json.dump(rows, open(os.path.join(HERE, "ledger_rows.json"), "w"), indent=1)
print(len(rows), "rows")
