# exec'd by build_deliverables.py (shares its namespace: S, FAM, table, F, json)
D = "2026-10-31"
EV = ["liber-primus/analysis/round40/C1-rescore-46/PREREG.md", "liber-primus/analysis/round40/C1-rescore-46/RESULTS.md", "liber-primus/analysis/round40/C1-rescore-46/rescore_summary.json"]
STORE = "analysis/round40/C1-rescore-46/rescore_rows.jsonl"


def bsum(fn):
    e = FAM[fn]; k = e["bar_key"]
    return "best non-degenerate %.3f (ks1) / %.3f (ks2) vs 12-reg bars actual-N %.3f / %.3f, declared-N %.3f / %.3f; %s heads screened, %s survivors decoded (%d / %d rows per rel), %d / %d degenerate rows" % (
        e["best_nondegenerate"]["keyskip1"]["pmax"], e["best_nondegenerate"]["keyskip2"]["pmax"], e["bars"]["keyskip1"][k], e["bars"]["keyskip2"][k],
        e["bars"]["keyskip1"]["declared_1e6"], e["bars"]["keyskip2"]["declared_1e6"], e.get("heads_screened", "n/a"), e.get("survivors", "n/a"),
        e["rows"]["keyskip1"], e["rows"]["keyskip2"], e["n_degenerate_rows"]["keyskip1"], e["n_degenerate_rows"]["keyskip2"])


def bsum_plain(fn):
    e = FAM[fn]; k = e["bar_key"]
    return "best non-degenerate %.3f / %.3f vs 12-reg bars actual-N %.3f / %.3f (declared-N %.3f / %.3f); %d / %d rows per rel; %d / %d degenerate rows" % (
        e["best_nondegenerate"]["keyskip1"]["pmax"], e["best_nondegenerate"]["keyskip2"]["pmax"], e["bars"]["keyskip1"][k], e["bars"]["keyskip2"][k],
        e["bars"]["keyskip1"]["declared_1e6"], e["bars"]["keyskip2"]["declared_1e6"], e["rows"]["keyskip1"], e["rows"]["keyskip2"], e["n_degenerate_rows"]["keyskip1"], e["n_degenerate_rows"]["keyskip2"])


def dsum(fn):
    e = FAM[fn]
    return "%d scorable streams, D=%d null draws: best %s pmax %.2f, Z %.2f, p(Z)=%.4f, raw-best p=%.4f, n_degenerate=%s" % (
        e["n_streams"], e["D"], e["best_stream"], e["best_pmax"], e["best_Z"], e["p_family"], e.get("raw_best", {}).get("p", float("nan")), e.get("n_degenerate_streams"))


CTL_BEAM = "controls/<family>.json: plants (EN_MODERN/LATIN/GREEK, real enc_exact/enc_pair, the family's own keys) recovered 6/6 per relation (gate >= 4/6); recovered = pf_v4_12 head screen passes (screened families) AND L=120 pmax >= declared-N bar AND L=240 pmax >= bar AND recovery240 >= 0.90"
CTL_DIRECT = "direct_control: held-out EN_MODERN/LATIN/GREEK text at the family's stream length beats the family-null max-Z q99 by > 1 in all three registers"


def row(id_, hyp, status, cov, res, tc, nc_, ctl, ctl_detail, reopens=None):
    r = {"round": 40, "lane": "C1", "date": D, "threshold_fixed_in_advance": True, "evidence": EV,
         "reproduce": "cd liber-primus/analysis/round40/C1-rescore-46; see RESULTS.md 'Files' (run_screened.py / run_beam.py / direct.py stages, then final.py, build_deliverables.py)",
         "sweep_store": STORE, "id": id_, "hypothesis": hyp, "status": status, "coverage": cov, "result": res, "three_conditionals": tc, "not_covered": nc_,
         "threshold": "beam rows: 12-register POT bar (round36/B1-orbit-12reg/null12.json) at actual N (heads screened / rows per relation) and declared N=1e6; direct rows: per-stream-Z family p < 0.01 AND raw best-of-family p < 0.01",
         "positive_control": ctl, "control_detail": ctl_detail}
    if reopens: r["reopens_if"] = reopens
    return r


def TC(ks, tm):
    return {"key_space": ks, "transition_model": tm, "adjudicator_register": "panel-R36 12 registers (sha a0682f0c); 12-register POT bars (null12.json) for beam rows, self-calibrating shuffle null for direct streams; 14-field rows with degenerate flag"}


SCR = "keyskip1 + keyskip2 under beam_v3 panel_max after the pf_v4_12 head screen (frozen point, per-relation FPR 5e-4, min power over the 12 registers 0.952, so up to ~5% of true-key heads could be dropped by the screen)"
ent = []
ent.append(row("R40-C1-R30-B1-ARTIFACT-KEYS", "Round 10b B1 artifact-derived Vigenere keys (125 curated alpha + 16 numeric streams) re-scored under panel-R36 + beam_v3 (+ pf_v4_12 head screen) at every page start.", "negative",
    "REGENERATED (b1_keys.build; the 43 auto-extracted alpha keys need the uncommitted armada_osint raw archive and are absent): 3,258 (key, phase<=12, sign) entries x 104 page-start windows (52 pages >= 120 runes, atbash 0/1) at L=120. " + bsum("R30_B1_artifact_keys"),
    "NEGATIVE. Best non-degenerate pmax is below the actual-N bar in both relations; 0 flagged, 0 near-miss.", TC("125 alpha + 16 numeric key strings x <=12 phases x sign x atbash x 52 page starts (L=120)", SCR),
    "43 auto-extracted alpha keys (raw archive not committed); the interrupter-beam arm (F-rune interrupters inside the beam); pages < 120 runes; windows beyond the page-start head; phases beyond 12 for alpha keys", "passed", CTL_BEAM))
ent.append(row("R40-C1-C18-NUMERIC-PS-TWEET-MAYAN", "R10b/campaign18 numeric keystreams (end-of-puzzle P.S. digit string, @1231507051321 handle, Mayan rotation list; single/pairs/disjoint pairs/reversed) re-scored with ALL phases.", "negative",
    "REGENERATED (digit strings and Mayan list copied from campaign18_skip/armada2/numeric2_skip.py): 1,338 (stream, phase, sign) entries x 104 page-start windows at L=120. " + bsum("C18_numeric_PS_tweet_mayan"),
    "NEGATIVE; 0 flagged, 0 near-miss.", TC("P.S. digits, tweet-handle digits (5 readings each, all phases), Mayan list and reverse, sign x atbash x 52 page starts", SCR),
    "other digit readings (base-N, digit sums); other pointer constants; windows beyond the page-start head", "passed", CTL_BEAM))
ent.append(row("R40-C1-R32-B04-SLOGAN-SEEDS", "Round 13 B-04 SLOGAN seeds (139 text forms) as hash-chain/KDF secrets under the 16 B04 generators x 5 reductions x dir x sign x atbash, stage A + stage C per-page restarts, re-scored under panel-R36 + beam_v3.", "negative",
    "REGENERATED (round13/B04 seeds.py/ks.py/harness constants unchanged; nsym=728): 44,480 keystreams x 104 windows (52 pages incl. the page-0 head, atbash 0/1). " + bsum("R32_B04_slogan_seeds"),
    "NEGATIVE; 0 flagged, 0 near-miss. R37 C1 U1 had already re-scored the 41 B04-covered clue strings on 3 routes; this extends to the whole SLOGAN seed set over all B04 generators.",
    TC("139 SLOGAN seed byte-strings x 16 generators x 5 reductions x fwd/rev x sign (44,480 keystreams), offset 0", SCR),
    "stage B offset ladder (10 offsets); core seeds other than slogan/lp (thematic, solvedkey, num_, primes_, onion, lore); pages < 120 runes; stage D escalation", "passed", CTL_BEAM))
ent.append(row("R40-C1-R32-B04-LP-SEEDS-STAGE-A", "Round 13 B-04 LP-line/word seeds (1,256 'lp' labels) under the 16 generators x 5 reductions x dir x sign, stage A (LP2 head, atbash 0/1) re-scored under panel-R36 + beam_v3.", "negative",
    "REGENERATED: 401,920 keystreams x 2 windows. " + bsum("R32_B04_lp_seeds_stageA"), "NEGATIVE; 0 flagged, 0 near-miss.", TC("1,256 lp seed byte-strings x 16 x 5 x 2 x 2, offset 0, LP2 head", SCR),
    "per-page restarts and offsets for lp seeds; the other label groups (lore, onion, num, ...)", "passed", CTL_BEAM))
ent.append(row("R40-C1-R33-SEMANTIC-SEED-ZOO", "Round 26 C semantic-seed zoo (323 corpus values x 7 generators) re-scored under panel-R36 + beam_v3 keyskip1/keyskip2, L=120 window 0.", "negative",
    "REGENERATED from seeds.json + sweep.ZOO: 2,137 keystreams (= the original 4,274 rows over 2 presets), window 0, L=120, keyskip1+2. " + bsum_plain("R33_R26C_semantic_seed_zoo"),
    "NEGATIVE; 0 flagged, 0 near-miss.", TC("323 corpus values + phrases x 7 generators (str seeds only on the py27 generators), offset 0", "keyskip1 + keyskip2 under beam_v3 panel_max, no head screen (direct decode of all 2,137)"),
    "offsets != 0; semantic seeds outside the 323-value enumeration; other generators", "passed", CTL_BEAM))
ent.append(row("R40-C1-R43-B5-COMPOSED-KEYS", "Round 10b B5 composed keys K = cw*W + cg*G (44 words x 3 generators x 8 coefficient pairs x all wphases x goff 0..63 = 289,344 configs) re-scored with pf_v4_12 + beam_v3 on pages 0,1,2,5,20.", "negative",
    "REGENERATED (composed_key.py logic; 289,344 configs, equal to the original tier-1 count): 5 pages x 289,344. " + bsum("R43_B5_composed_keys"), "NEGATIVE; 0 flagged, 0 near-miss.",
    TC("289,344 composed configs x 5 pages (L=120), sign +1 (the 8 coefficient pairs cover -1)", SCR), "page 54 (76 runes < 120); the other 49 pages; atbash arm; goff > 63", "passed", CTL_BEAM))
ent.append(row("R40-C1-R47-F01-LP2-AS-PAD", "Round 16 F-01 LP2 (fwd/rev/atbash/neg) x sign as a running key over Cicada target objects re-scored under panel-R36 + beam_v3.", "negative",
    "REGENERATED (F-01 loaders unchanged): T1 2012-13 texts, T2 solved LP1, T3 PGP bodies (500 runes each; L=120 windows at 0,120,240,360), T6 LP2 head 200 (windows 0,80). " + bsum_plain("R47_F01_LP2_as_pad") + " (the degenerate rows are T6 self-key: constant output, top degenerate pmax 8.70)",
    "NEGATIVE; 0 flagged, 0 near-miss.", TC("4 LP2 key variants x 2 signs x 4 targets x windows", "keyskip1 + keyskip2 under beam_v3 panel_max"),
    "T4 AN-END hash (63 values < L=120) and T5 payload (absent); all-pairs page XOR and canon-as-key parts of the reading; other target objects; windows beyond 500 runes", "passed", CTL_BEAM))
ent.append(row("R40-C1-R04-M4-LP1-POINTER", "Round 10 L2 M4 LP2 word numbers as pointers into the solved LP1 English word list, re-scored under panel-R36.", "negative",
    "REGENERATED 16 pointer streams (~12k runes each). " + dsum("R04_M4_LP1_pointer") + ". The Z statistic is a null defect: the 'len' and 'len-1' pointer families depend only on word lengths, which null_A holds fixed, so their null sd is 0 (Z 5784); the raw best-of-family statistic (obs 224.98 vs null best mean 226.1) is the valid one. The stream is English by construction (words copied from the book), which is why pmax is ~225 regardless of LP2.",
    "NEGATIVE on the valid statistic (raw p 0.72); the Z statistic is invalid for this family and is not used.", TC("16 pointer streams into the solved English word list", "none (cleartext layer)"),
    "decoded-word pointers; lags; pointers from other sources", "passed", CTL_DIRECT))
ent.append(row("R40-C1-R06-M6-STRUCTURAL-COUNTS", "Round 10 L2 M6 structural counts as a message, re-scored under panel-R36.", "negative",
    "REGENERATED 5 sequences x (29 shifts x id/atbash + 26 letter shifts). " + dsum("R06_M6_structural_counts") + " (168 of 420 streams degenerate: small-count mod 29 streams)", "NEGATIVE.",
    TC("5 count sequences x 84 transforms", "none"), "other count sequences (F-count/page etc.); bases other than mod 26/29", "passed", CTL_DIRECT))
ent.append(row("R40-C1-R13-R9-DIRECTION-WALKS", "Round 9 DIRECTION: 2,670 positional walks/sieves of the LP2 ciphertext re-scored under panel-R36 (direction.py unchanged).", "open",
    "REGENERATED 2,670 reads (2,274 scorable >= 32 runes). Three null runs (doublet-matched shuffled LP2, different seeds): D=150 p(Z)=0.0066 raw 0.0066; D=800 p(Z)=0.0062 raw 0.0062; D=500 p(Z)=0.0040 raw 0.0040. Best A:idx:s60/s61:b1:f1 (backward self-indexing walk, step = rune index, F skipped; both starts reach the same 400-rune path), pmax 4.733, non-degenerate (IoC*N 1.01, mds 16).",
    "NEAR-MISS (both statistics < 0.01, replicated on independent null seeds). Amplitude is noise-level in absolute terms (a readable 400-rune stream in a panel register scores pmax in the tens; planted controls Z 11-18), the stream's transliteration reads as noise, and contiguous 400-windows of LP2 sit at pmax 1.3 (max 2.99). Not flagged: no beam row, no key, nothing to run through the L=240/oracle path. Coordinator decides whether a human read is wanted.",
    TC("2,670 fixed positional reads of the LP2 ciphertext", "none (key-free reads)"), "walk families beyond direction.py's parameter grid; reads of the keyed (decoded) layer", "passed", CTL_DIRECT,
    reopens="a replication of the excess under a null that also matches the positional/selection structure of the walk, or a human read judging the stream as language"))
ent.append(row("R40-C1-R27-R22A-SELFEMBEDDED", "Round 22 A self-embedded selections (every-k / diagonal / anti-diagonal / reverse of the solved plaintext) re-scored under panel-R36.", "negative",
    "REGENERATED selections of the solved-plaintext rune-index stream (lib_selfread.enumerate_selections unchanged). " + dsum("R27_R22A_selfembedded"), "NEGATIVE.", TC("every-k / diagonal / anti-diagonal / reverse selections of the solved rune-index stream", "none"),
    "printed-line geometry is covered by R28; keyword-cued selections; the wider community-solved corpus", "passed", CTL_DIRECT))
ent.append(row("R40-C1-R28-R23A2-LINE-ACROSTIC", "Round 23 A2 printed-line / word acrostics of the solved pages re-scored under panel-R36.", "negative",
    "REGENERATED 48 reads, 24 scorable (>= 32 runes). Lane null (order-shuffled letter pool): p(Z) 0.0033, raw 0.0033 (best 06|word_last|rev pmax 13.46; CONCAT|word_last|rev 17.1). Matched null (each read's own letters shuffled): p(Z) 0.0066, raw 0.103. Natural-English baseline (a2_natural_baseline.json): word-final-letter streams of running English score at the same level (CONCAT|word_last|rev obs 17.1 vs natural windows mean 17.4, 67% of windows >= obs; 06|word_last|rev obs 13.46 vs 12 natural windows max 13.09).",
    "NEGATIVE. The lane-null excess is the natural English first/last-letter skew and suffix structure, not a message; listed for the red team (06 word_last/rev is 0.4 above the max of 12 natural windows).",
    TC("24 scorable acrostic reads of 5 solved pages", "none"), "24 of 48 reads are below the panel floor (< 32 runes); wider solved corpus; keyword-cued selections", "passed", CTL_DIRECT))
INC = [("R14", "campaign7 wordsum_selfkey (word gematria sums drive the next-word shift)", "campaign7 code not committed (only CAMPAIGN-VII-FINDINGS.md in a recovered corpus path); no wordsum_selfkey in any committed .py"),
       ("R15", "campaign7 hill5_magic (three book matrices as Hill keys)", "campaign7 code not committed; no hill5_magic in any committed .py"),
       ("R31", "Round 10b B3 page-local semantic keys / crib readouts", "readouts are 5-9 runes (< the 32-rune panel floor); T1 was already INCONCLUSIVE by its own weak control; no stored top-N full-page promotions"),
       ("R35", "R12-C2 / R26-B 33 keytexts as running keys", "round12/C2/texts (the 29-33 curated key texts, ~12 MB) are not in the repo and fetch.sh needs network; texts not hash-pinned"),
       ("R36", "R17 public pad + R24 C8 date-indexed pad (NIST beacon, Random.org, block headers)", "dated public-pad data not committed; round17/P*/fetch.py needs network"),
       ("R44", "campaign XVII bookcipher: LP numbers as pointers into Cicada's known books", "the 2012-14 book texts are not committed as inputs and the original adjudicator was an English word-salad test with no rune stream")]
for rid, name, why in INC:
    ent.append(row("R40-C1-INCONCLUSIVE-" + rid, name + " (not re-scorable under panel-R36 + beam_v3 from committed code).", "inconclusive",
                   "NOT re-scored: " + why + ". (R08, the M8 word-length run statistic, involves no adjudicator and is not affected by the English-only conditional.)",
                   "INCONCLUSIVE: the English-only/legacy conditional of this reading is unchanged.", TC("not regenerated", "n/a"), why, "not applicable", "no control run: no artefact to run it on",
                   reopens="the missing artefact (" + why + ") is supplied or committed"))
json.dump({"$comment": "R40 C1 ledger rows (not applied to LEDGER.json by the lane)", "entries": ent}, open(F("ledger.json"), "w"), indent=1)

tried = [t["cell"] for t in table if t["new_status"] == "TRIED"]
part = [t["cell"] for t in table if t["new_status"] == "PARTIAL-RESCORED"]
unch = [t["cell"] for t in table if t["new_status"].startswith("UNCHANGED")]
patches = {"patches": [
    {"id": "O4-matrix", "set": {"cells_to_TRIED": tried, "cells_to_PARTIAL": part, "cells_unchanged_inconclusive": unch,
        "recount": {"before_R40_C1": {"T-EN": 21, "T-LEG": 25}, "TRIED_added": len(tried), "PARTIAL_added": len(part), "T-EN_T-LEG_remaining": len(unch)},
        "note": "TRIED = every re-scorable reading in the cell's record was re-scored here or in R37-C3 under panel-R36 (12 registers) + beam_v3 with a passed control (R08 has no adjudicator and is not counted against a cell); PARTIAL = at least one reading re-scored but another reading in the record is inconclusive (missing artefact); H4xF6 and any cell citing R13 carries the R13 near-miss caveat."}},
    {"id": "B-04", "coverage_add": "R40-C1 (2026-10-31): SLOGAN seeds (139) x 16 gens x 5 reds x dir x sign x atbash, stage A + per-page restarts, and 1,256 lp seeds stage A, re-screened with pf_v4_12 and decoded with beam_v3 under panel-R36: slogan best 5.88 (ks1) vs actual-N 9.66; lp 5.75 (ks2) vs 8.92.",
     "not_covered_add": "stage B offsets; non-slogan/lp core seeds", "status_note": "English-only/legacy-beam conditional replaced by the 12-register conditional for these seed groups; remains negative"},
    {"id": "R16-KDF", "coverage_add": "R40-C1: see B-04 (slogan seed groups only).", "not_covered_add": "", "status_note": "unchanged otherwise"},
    {"id": "R26-C-SEMANTIC-SEED-ZOO", "coverage_add": "R40-C1: all 2,137 keystreams re-decoded with beam_v3 keyskip1+2 under panel-R36 at L=120 window 0: best 4.81/4.90 vs actual-N 6.87/6.80.", "not_covered_add": "", "status_note": "English-only/legacy-beam conditional replaced by the 12-register conditional; remains negative"},
    {"id": "R22-A-SELFEMBEDDED-READ", "coverage_add": "R40-C1: rune-index selections re-scored under panel-R36: p(Z)=0.0945, raw p=0.87.", "not_covered_add": "", "status_note": "English-only conditional replaced by the 12-register conditional for the rune-index representation; remains negative"},
    {"id": "R23-A2-LINE-ACROSTIC", "coverage_add": "R40-C1: 24 of 48 reads scorable under panel-R36; the lane-null excess is explained by the natural English first/last-letter baseline (a2_natural_baseline.json).", "not_covered_add": "24 reads below the 32-rune panel floor", "status_note": "remains negative; 06 word_last/rev listed for the red team"},
    {"id": "F-01", "coverage_add": "R40-C1: 8 (variant, sign) pairs x T1/T2/T3/T6 windows re-decoded with beam_v3 keyskip1+2 under panel-R36: best 4.18/4.46 vs actual-N 5.80/5.75.", "not_covered_add": "T4 (63 values < L), T5; all-pairs page XOR; canon-as-key", "status_note": "English-only/legacy-beam conditional replaced by the 12-register conditional for the covered configs; remains negative"},
    {"id": "R10-L2-MAP", "coverage_add": "R40-C1: M4 (16 pointer streams) and M6 (420 count streams) re-scored under panel-R36; M4 Z invalid (null sd 0 for length pointers), raw p 0.72; M6 p(Z)=0.31.", "not_covered_remove": "M4, M6 (M3/M7/M8 remain; M8 has no adjudicator)", "status_note": "remains negative"},
    {"id": "R9-DIRECTION", "coverage_add": "R40-C1: 2,670 reads re-scored under panel-R36; best A:idx:s60/61 backward walk pmax 4.73, p 0.004-0.0066 on three null runs (both statistics): near-miss, noise-level amplitude, no readable text.", "not_covered_add": "", "status_note": "proposed status open pending coordinator decision on a human read; not flagged", "set_status": "open"},
    {"id": "R10b-B1-ARTIFACT-KEYS", "coverage_add": "R40-C1: 125 curated alpha + 16 numeric keys (+ c18 numeric: P.S. digits, tweet handle, Mayan, all phases) re-scored with pf_v4_12 + beam_v3 under panel-R36 at 52 page starts: best 5.31 vs actual-N 8.61; c18 5.01 vs 8.29.", "not_covered_add": "43 auto-extracted alpha keys (raw archive not committed)", "status_note": "English-only/legacy-beam conditional replaced by the 12-register conditional; remains negative"},
    {"id": "R10b-B5-COMPOSED-KEYS", "coverage_add": "R40-C1: 289,344 composed configs x pages 0,1,2,5,20 screened with pf_v4_12 and decoded with beam_v3 under panel-R36: best 5.96 vs actual-N 9.24.", "not_covered_add": "page 54 (<120 runes) and the other 49 pages", "status_note": "remains negative"}],
    "new_rows": "ledger.json"}
json.dump(patches, open(F("ledger_patches.json"), "w"), indent=1)
print("ledger rows", len(ent), "tried", len(tried), "part", len(part), "unch", len(unch))
