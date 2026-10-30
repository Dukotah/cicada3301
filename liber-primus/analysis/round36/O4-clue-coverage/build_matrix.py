# O4: readings.json + matrix.md + counts. Tiny; no heavy compute.
import json, collections
A = "liber-primus/analysis/"
FAM = {"F1": "literal instruction executed", "F2": "number channel", "F3": "gematria/arith on words",
       "F4": "word-as-key / keytext", "F5": "semantic (meaning) -> operation", "F6": "positional (page/line/rune idx) -> key",
       "F7": "cross-page / cross-document join", "F8": "physical / geometric", "F9": "temporal (dates -> seeds)",
       "F10": "acrostic / stego in text", "F11": "AN-END structure"}
ROWS = {
 "H1": ("2016: Liber Primus is the way", "F1 F5 F7 F8"),
 "H2": ("2016: Its words are the map", "F1 F3 F4 F5 F6 F7 F10"),
 "H3": ("2016: their meaning is the road", "F1 F3 F4 F5 F7"),
 "H4": ("2016: their numbers are the direction", "F1 F2 F3 F5 F6 F7 F8"),
 "H5": ("2016: The path lies empty; epiphany seeks the devoted", "F1 F4 F5 F10"),
 "H6": ("2016/2017: Seek and you will be found; Beware false paths, verify 7A35090F", "F1 F2 F4"),
 "H7": ("2013: The key is all around you (@1231507051321)", "F2 F4 F9"),
 "H8": ("2012: The key has always been right in front of your eyes", "F1 F4 F5 F10"),
 "H9": ("2013: You already have everything you need; knock on the sky and listen", "F1 F5 F8 F10"),
 "H10": ("2014: Let the text guide you / produce from within", "F1 F5 F10"),
 "H11": ("2014 ciphertexts: IDGTK..., fallen-behind pairs, rune-table-morse", "F7 F10"),
 "H12": ("2012-13 pointers: dates, P.S. number, coords, book codes", "F2 F6 F7 F9"),
 "L1": ("A WARNING: believe nothing... test the knowledge, find your truth", "F1 F5 F7"),
 "L2": ("A WARNING: either the words or their numbers, for all is sacred", "F1 F2 F3 F4 F5"),
 "L3": ("A WARNING: do not edit or change this book or the message within", "F1 F10 F11"),
 "L4": ("SOME WISDOM: the primes / the totient function are sacred", "F1 F2 F3 F4 F5"),
 "L5": ("SOME WISDOM: all things should be encrypted", "F1 F2 F5"),
 "L7": ("INSTRUCTION: command your own self (+WISDOM lines)", "F1 F4 F5"),
 "L8": ("INSTRUCTION: do four unreasonable things each day", "F1 F5 F6 F9"),
 "L9": ("INSTRUCTION: program your mind / program reality", "F1 F5"),
 "L10": ("INSTRUCTION: question all things; discover truth inside yourself", "F1 F5 F7 F10"),
 "L11": ("WELCOME: journey deep within; like the instar, go within to emerge", "F1 F5 F10"),
 "L12": ("KOAN: master and student (who are you)", "F4 F5 F7"),
 "L13": ("KOAN: the I is the voice of the circumference", "F4 F5 F7 F8"),
 "L14": ("LOSS OF DIVINITY / wisdom: consumption, preservation, adherence; primality", "F2 F5"),
 "L15": ("KNOW THIS: the three magic squares (numbers + words)", "F2 F3 F6 F7"),
 "L16": ("Gematria-sum structure: prime line sums, 761, PARABLE product", "F2 F3 F11"),
 "L17": ("AN END: a page hashes to H; seek it out", "F3 F7 F11"),
 "L18": ("PARABLE: like the instar... shed circumferences", "F1 F5 F10"),
 "S1": ("Solved-page ladder + thematic page keys (DIVINITY, FIRFUMFERENFE)", "F1 F4 F5 F7 F11"),
 "S2": ("LP2 structure: 55 pages, 14 red heads, interrupter rule, word counts", "F1 F6 F7 F10"),
 "S3": ("pp49-51 base-60 256-byte payload", "F2 F6 F7"),
 "S4": ("Physical: ornaments, drop-caps, render/line geometry", "F8 F10"),
 "S5": ("Signature timestamps / dates", "F9"),
}
T, TE, TL, P, TN = "TRIED", "TRIED-ENGLISH-ONLY", "TRIED-LEGACY-BEAM", "PARTIAL", "TRIED-NO-CONTROL"
R = []
def r(id, name, rows, fam, rnd, ledger, dec, adj, ks, verdict, status, nc, cite):
    R.append(dict(id=id, name=name, rows=rows.split(), families=fam.split(), round=rnd, ledger_row=ledger, decoder=dec, adjudicator=adj,
                  conditionals=dict(key_space=ks, decoder_transition=dec, adjudicator_register=adj), verdict=verdict, status_class=status,
                  not_covered=nc, cite=cite))
EN4 = "rune 4-gram trained on English-in-futhorc + English score_norm (English-only)"
L2P = A + "round10/L2-map/PREREG.md"
r("R01", "R10 L2 M1/G1 word/line/page-initial & final acrostic streams", "H2", "F10", "10", "NONE (round10 not in LEDGER.json)", "none (cleartext layer, key-free)", EN4,
  "ciphertext word/line boundary positions, 29 shifts x atbash x reverse", "NEGATIVE; G1 fired on line-initial (z=6.35) and was adjudicated as width-greedy typesetting (r=0.72)", T if False else TE, "words of the DECODED plaintext; non-English registers; acrostic over word-numbers", L2P + ":59-76; round10/L2-map/results.json G1,M1; diag_lineinit.json D1")
r("R02", "R10 L2 M2 word gematria sums -> symbol stream", "H2 H3", "F3", "10", "NONE", "none", EN4, "2,928 word sums mod 29/26", "NEGATIVE (z=-0.12)", TE, "non-English; sums as keystream (not symbol stream)", L2P + ":77-83")
r("R03", "R10 L2 M3 word-length bits (ASCII/Baconian)", "H2", "F10", "10", "NONE", "none", "ASCII printability + English score_norm", "4 predicates x polarity x offsets", "NEGATIVE", TE, "multi-bit predicates; non-English", L2P + ":84-90")
r("R04", "R10 L2 M4 LP2 word numbers as pointers into the solved LP1 English word list ('its words are the map', 'meaning = LP1')", "H2 H3", "F7", "10", "NONE", "none", "English score_norm of retrieved LP1 words (repeating words inflate the score; flagged artefact)", "6 pointer families, ~750-word target", "NEGATIVE (best -4.05 is repeated-word artefact)", TE, "target = LP1 only; no gematria-sum-of-LP1 as pointer INTO LP2; no Latin/other target", L2P + ":91-100; results.json M4")
r("R05", "R10 L2 M5 word-level walk w <- w +/- f(word)", "H2 H4", "F6", "10", "NONE", "none", EN4, "6 f x 32 starts x 2 dirs", "NEGATIVE (z=-0.03)", TE, "no positive control recorded for the walk family (inherits R9)", L2P + ":102-108")
r("R06", "R10 L2 M6 structural counts (words/line, per page) as message", "H2", "F6", "10", "NONE", "none", EN4 + " letters mod 26", "5 sequences", "NEGATIVE", TE, "counts used as KEY SCHEDULE for decode (not as message)", L2P + ":109-114")
r("R07", "R10 L2 M7 word-level transposition (IoC*N=1.0000)", "H2", "F10", "10", "NONE", "analytic", "IoC", "n/a", "EXCLUDED analytically", T, "", L2P + ":115-120")
r("R08", "R10 L2 M8 LP1 English word-length skeleton vs LP2 word lengths", "H2 H3", "F7", "10", "NONE (C-01 open: skeleton corpus extension)", "none", "longest exact word-length run", "LP1+AN END+PARABLE ~752 words", "NEGATIVE (7 vs null max 8)", TE, "only English LP1 register as skeleton", L2P + ":121-130")
r("R09", "R10 L2 M9 word numbers as direct addresses into the rune stream", "H2 H4", "F6", "10", "NONE", "none", EN4, "10 families x 29 shifts", "NEGATIVE (z=0.32)", TE, "", A + "round10/L2-map/PREREG-ADDENDUM-E.md:23-35")
r("R10", "R10 L3 T1 word/sentence/line/page gematria sums marked (prime/emirp/phi-shaped/Cicada constants)", "H3 L16", "F3", "10", "NONE", "none", "counts vs permutation null (language-free)", "all LP2 CIPHERTEXT word sums", "NEGATIVE", T, "applies to ciphertext words only; never to DECODED lines (LP1 line sums are all prime - designed property)", A + "round10/L3-road/PREREG.md:116-124; road_results.json T1a/T1b")
r("R11", "R10 L3 T2-T4 sum -> symbol / word selection by predicate / reorder by sum", "H3", "F3", "10", "NONE", "none", EN4, "5 readings", "NEGATIVE; validation gate oracle z=79.7", TE, "", A + "round10/L3-road/PREREG.md:116-125")
r("R12", "R10 L3 T5 sum as pointer into a key text", "H3", "F4", "10", "NONE", "none", EN4, "high-prior key texts", "NEGATIVE (confirmatory only)", TE, "texts predate B-16 correction", A + "round10/L3-road/PREREG.md:124")
r("R13", "R9 DIRECTION: 2,670 rune-level positional walks/sieves", "H4", "F6", "9", "NONE (F-02 open row is stale)", "none (positional reads of ciphertext)", EN4, "walk p <- p +/- f(c[p]), 7 f, 64 starts", "NEGATIVE z=-0.40; PA-2: NO positive control", TN, "word-level and key-schedule uses of the numbers; no control", "research/ROUND-9-RESULTS.md:65-124")
r("R14", "campaign7 wordsum_selfkey: word gematria sums drive next-word shift", "H4 L2", "F3", "campaign7", "NONE", "rigid/legacy", "English quadgram", "5 variants per page", "NEGATIVE (-6.897)", TE, "legacy decoder, English only", "corpus/H-branch-recovery/recovered/claude_master-roadmap-libra-qk527u/liber-primus/analysis/campaign7/CAMPAIGN-VII-FINDINGS.md:25")
r("R15", "campaign7 hill5_magic: the three book matrices as Hill keys (M, M^T, inv)", "L15", "F2", "campaign7", "NONE", "Hill, rigid", "English quadgram", "6 matrices x 4 forms", "NEGATIVE (-6.873)", TE, "matrices as column/row key schedules, as permutations, or via word-number fills", "campaign7 CAMPAIGN-VII-FINDINGS.md:24")
r("R16", "R11 N1 cumulative-gematria feedback autokey", "L2 L4 H4", "F2", "11", "R11-N1-NUMBER-CHANNEL", "legacy skip beam", "English quadgram (lib_numchannel)", "48 configs", "NEGATIVE, control validated; ledger 'measured'", TE, "beam_v3/pf_v4/12 registers (reopen is cheap per ledger)", "ELIMINATION-LEDGER.md:935-960")
r("R17", "R11 N2 prime-gap / prime-index as data", "L4", "F2", "11", "R11-N2-NUMBER-CHANNEL", "legacy", "English quadgram", "route (d) coordinate pairs too", "NEGATIVE", TE, "same reopen", "ELIMINATION-LEDGER.md:935-960")
r("R18", "R11 N3 whole-book/segments as number-theoretic objects", "L4 L14", "F2", "11", "R11-N3-NUMBER-CHANNEL", "none", "number-theory counts vs null", "55 segments + prime-concat", "NEGATIVE, ANTI-special", T, "", "ELIMINATION-LEDGER.md:935-960")
r("R19", "R11 N4 digit planes (bases 3/5/7/10)", "L4", "F2", "11", "R11-N4-NUMBER-CHANNEL", "legacy", "English quadgram", "4 bases", "NEGATIVE", TE, "same reopen", "ELIMINATION-LEDGER.md:935-960")
r("R20", "R11 N5 totient ladder (phi(phi(p)), Carmichael, totient of running sum)", "L4 S1", "F2", "11", "R11-N5-NUMBER-CHANNEL", "legacy", "English quadgram", "ladder", "NEGATIVE; control reproduced AN END via phi(prime)", TE, "same reopen", "ELIMINATION-LEDGER.md:935-960")
r("R21", "R11 S1 interrupter-position gap channel", "S2", "F10", "11", "R11-S1-NUMBER-CHANNEL", "legacy", "English quadgram", "457 gaps", "NEGATIVE, plant recovered", TE, "", "ELIMINATION-LEDGER.md:935-960")
r("R22", "R11 S2 separators = typography", "S4", "F8", "11", "R11-S2-NUMBER-CHANNEL", "none", "run-length stats", "", "NEGATIVE", T, "19 disagreements (A-05)", "ELIMINATION-LEDGER.md:935-960")
r("R23", "R22-C X1 'do four unreasonable things' (every-4th x4 phases, cipher x{2,3,4}, 4-way interleave)", "L8", "F1", "22", "R22-C-LITERAL-IMPERATIVES", "driftbeam exact/drift (legacy)", "R19/R20 nine-register panel-max + recovery gate", "185 ops total; width 4 only", "NEGATIVE (best pmax 1.53 vs bar ~5.1)", TL, "widths != 4; 'each day' / temporal; four as 4 DIFFERENT keys; beam_v3/pf_v4/12 reg", "LEDGER.json R22-C-LITERAL-IMPERATIVES")
r("R24", "R22-C X3 reversal re-enciphered forward; solved plaintext as running key (+/-)", "L1 L10 H3", "F7", "22", "R22-C-LITERAL-IMPERATIVES", "driftbeam (legacy)", "nine-register panel-max", "both signs; zero offset only", "NEGATIVE (pmax 2.6)", TL, "non-zero offsets; per-page solved text as per-page key; map/road/direction composition", "LEDGER.json R22-C-LITERAL-IMPERATIVES")
r("R25", "R22-C X4 'words OR numbers': prime/index/totient value as keystream over letters (+/-, atbash)", "L2 L4", "F2", "22", "R22-C-LITERAL-IMPERATIVES", "driftbeam (legacy)", "nine-register panel-max", "value/pi/phi x signs", "NEGATIVE (4 decodes >0.90 recovery rejected at panel clause)", TL, "phi(phi), lambda, digit planes; offsets", "LEDGER.json R22-C-LITERAL-IMPERATIVES")
r("R26", "R22-B turtle/spatial render of value, pi(p), phi(p) streams (+G3 pointer decoders)", "H4", "F8", "22", "R22-B-TURTLE-SPATIAL-RENDER", "geometry (decoder-independent)", "shape statistics vs seed-3301 shuffle null; eye", "72 combos, moduli {4,6,8,12,29,360}", "CLEAN NULL", T, "per-page renders; other step functions; L-systems; interrupter-gated pen-up; English-along-path", "LEDGER.json R22-B")
r("R27", "R22-A self-embedded selection (every-k, diagonals) of solved plaintext", "L10 L11 H10", "F10", "22", "R22-A-SELFEMBEDDED-READ", "identity (selection axis)", "English quadgram score_norm vs per-length null (+agnostic secondary stats)", "3,508 selection functions over 5 rig-solved pages", "CLEAN NULL", TE, "AN END/PARABLE/community-solved LP1 pages (only 5 pages used); keyword-cued selections; k>40", "LEDGER.json R22-A")
r("R28", "R23 A2 printed-line / word acrostics of solved pages at true geometry", "L10 L11 H10 H8", "F10", "23", "R23-A2-LINE-ACROSTIC", "identity", "English quadgram score_norm + agnostic stats", "48 reads, 5 pages", "CLEAN NULL", TE, "cue-word selections; k-th rune per line; the other community-solved pages", "LEDGER.json R23-A2")
r("R29", "R22-D drop-cap channel (presence/order/gap/identity)", "S4", "F8", "22", "R22-D-ILLUSTRATION-DROPCAP", "none", "permutation null, Bonferroni over 5", "15 illuminated of 58 scans", "NEGATIVE (min p 0.18)", P, "figural motifs (crosses/trees/corpse/mayflies) never coded", "LEDGER.json R22-D")
r("R30", "R10b B1 artifact-derived keys (168 alpha incl. all 2016 clauses, BEWAREFALSEPATHS; 16 numeric) rigid + interrupter beam", "H1 H2 H3 H4 H5 H6 H7 H8", "F4", "10b", "NONE (round10b; see RESULTS.md)", "rigid additive + legacy interrupter beam", "English quadgram (break bar -5.2)", "168+16 keys x 55 pages x signs x phases", "NEGATIVE; real scored below shuffled null", TL, "keys as seeds (hash/PRNG); sentence-level compositions; non-English register; skip_by_two", A + "round10b/B1-overlooked-artifact/RESULTS.md; b1_keys.py:85-91")
r("R31", "R10b B3 page-local semantic keys, orthography-expanded (crib readouts)", "S1 L12 L13", "F5", "10b", "NONE", "crib readout", "English", "168k readouts; recovered DIVINITY and FIRFUMFERENFE from scratch", "NEGATIVE", TE, "keys from LP1 words only", A + "round10b/SYNTHESIS (B3 row in round10/SYNTHESIS.md)")
r("R32", "R13 B-04 + R16 KDF: SLOGAN list (LP1 lines, 'THEIR NUMBERS ARE THE DIRECTION', 'BEWARE FALSE PATHS', ...) as hash-chain / KDF secrets", "L1 L2 L4 L5 L7 L8 H4 H6 L17 L18 L11", "F4", "13/16", "B-04, R16-KDF (restated RESTATE-*; R32-I2 re-scored survivors)", "legacy beam (English-ranked heads only stored)", "English quadgram; 9-register re-score of stored survivors only", "692k+ decodes", "NEGATIVE; English-only conditional recorded", TE, "map/road/way/epiphany/seek sentences absent from SLOGANS (round13/B04/seeds.py:71-111); non-stored heads", A + "round13/B04/seeds.py:71-111; LEDGER.json B-04, R16-KDF")
r("R33", "R26 C semantic-seed zoo: 323 corpus values (primes, totients, Cicada ints, dates, coords, 16 sums + 31 solved/koan phrases) x 7 generators x {keyskip1,pair}", "L4 L5 L2 L12 L13 L8 S5 H12 L16", "F4 F9", "26", "R26-C-SEMANTIC-SEED-ZOO", "legacy keyskip1 + pair beam, hitfn20", "R19/20 panel-max recovery-gated", "4,274 rows, 100% of enumerated set, offset 0", "NEGATIVE (best -6.578)", TL, "seeds absent: 2016 sentences (verified: no THE MAP/ROAD/WAY/EPIPHANY in seeds.json); offsets; v3/pf_v4/12 reg", A + "round26/C/RESULTS.md; seeds.json")
r("R34", "R26 A page-56 ladders (ladder_prime/totient/prime_totient) as generator zoo", "L17 S1", "F11", "26", "R26-A-GEN-SWEEP-FIRST-FIRE (partially-run)", "legacy", "panel", "ladder generators", "partial", P, "full sweep; v3", "LEDGER.json R26-A")
r("R35", "R12-C2 / R26 B keytext running keys (33 curated texts), skip-aware", "H7 H8", "F4", "12/26", "R12-C2 (never-run), R26-B (partially-run), B-16 (eliminated=unsound)", "legacy skip beam", "English", "33 texts", "partial", P, "most of R12-C2; R7 'keytext killed by mechanism' was unsound (B-16)", "LEDGER.json R12-C2, R26-B, B-16")
r("R36", "R17 public pad + R24 C8 date-indexed pad (NIST beacon, block headers)", "H7 H12 S5", "F9", "17/24", "R17-PUBLIC-PAD (+restatement), R24-C8-DATE-INDEXED-PAD", "legacy", "English quadgram (R17); measured (C8)", "dated public sources", "NEGATIVE/measured", TE, "R17 not re-runnable post payload promotion; non-English", "LEDGER.json R17-PUBLIC-PAD, R24-C8")
r("R37", "bash 4.2 $RANDOM auto-seed orbit (2012-2014 timestamp seeds) under beam_v3 + pf_v4; glibc gen0 prior-dense; PHP", "S5 H12", "F9", "32-35", "R32-B1, R32-B3, R34-B1, R35-B1-BASH-ORBIT-PFV4", "beam_v3 + pf_v4", "nine-register panel + observed null", "77.6M x 2 ABIs (fraction 1.000)", "NEGATIVE (best 7.068 vs bar 8.06)", T, "re-score under 12 registers (R36 B1); other generators; non-signature dates", "LEDGER.json R35-B1-BASH-ORBIT-PFV4")
r("R38", "R8 SEED unix-second sweep 2011-2015 x 10 generators", "S5 H12", "F9", "8", "B-21 (partially-run; restated)", "rigid, legacy", "English", "2.52e9 decodes", "NEGATIVE", TE, "non-English; skip_by_two", "LEDGER.json B-21, RESTATE-B-21-ROUND8-BAR")
r("R39", "G-09 / R18-L8 timestamp seed prior (signed-message times as ranked seeds)", "S5 H12", "F9", "18", "G-09 (measured)", "none (prior only)", "n/a", "ranked tiers A-D", "prior built; no decode of tier A under current instrument stated", P, "tier-A seconds under v3/pf_v4/12 reg", A + "round18/L8-provenance/TIMESTAMP-SEED-CANDIDATES.json; LEDGER.json G-09")
r("R40", "Ornaments, line geometry, glyph variants, sub-pixel, render forensics", "S4", "F8", "8/19/30", "A-06, B-12, R19-FINITE-ORNAMENT-REGISTER, R30-A1, R30-A2, R30-A3", "none", "agnostic stats / nulls", "47+74 bands, 58 pages", "NEGATIVE/measured", T, "figural motifs; 30 small bands content", "LEDGER.json (ids listed)")
r("R41", "pp49-51 payload family: RSA ct (E-01), meta-params (E-02), PRF seed (B-05), per-section index (LP2-H1), micro (R28-L5), as pad (R30-B1/B2, R35-B2)", "S3", "F2 F6", "13-35", "E-01,E-02,B-05,R28-L2,R28-L5,R30-B1,R30-B2,R35-B2", "mixed", "mixed", "256 B + contested bytes", "NEGATIVE", T, "payload as schedule of the SOLVED-page ladder; payload x clue strings", "LEDGER.json (ids listed); ELIMINATION-LEDGER.md:551-569")
r("R42", "AN END hash hunt (2,706 corpus hash tests; archive/Tor crawl; B-07 never-run archive)", "L17", "F11", "anend", "B-07 (never-run), F-01", "none", "SHA-512 match", "held blobs + corpora", "NULL (sourced)", P, "archived-object recovery (not computable)", A + "anend_hunt/FINDINGS.md; ELIMINATION-LEDGER.md:623-664")
r("R43", "R10b B5 composed keys W (word) xor G (gematria stream) with start offset", "S1 L2", "F4", "10b", "NONE", "legacy", "English", "6/55 pages", "NEGATIVE", P, "49 pages; v3", A + "round10/SYNTHESIS.md (B5 row)")
r("R44", "campaign XVII / bookcipher: LP numbers as pointers into Cicada's known books", "H12 H2", "F7", "XVII", "NONE", "pointer", "English word-salad test", "known 2012-14 books", "word salad", TE, "books from H12 book-code puzzles as targets for LP1-sum pointers; non-English books", A + "CAMPAIGN-XVII-FINDINGS.md; bookcipher/")
r("R45", "LP2-H2 red-join continuity / per-section reset (14 red heads)", "S2", "F6", "recon", "NONE (ELIMINATION-LEDGER section)", "permutation stat", "doublet statistic", "14 heads", "NEGATIVE (p=1.0)", T, "", "ELIMINATION-LEDGER.md:551-569")
r("R46", "Solved-page skip rule as decoder transition model (rejection loop, skip_by_two, beams)", "S1 S2", "F1", "18-35", "R18-L2-*, I1-*, R24-C2*, R32-I1, R33-I2", "keyskip1/2, free (beam_v3)", "9-12 register panel", "construction axis measured", "instrument measured; applied via B/I lanes", T, "per-page key reset, skip_by_k (R33-I2 struck as unearned)", "LEDGER.json R32-I1, R33-I2")
r("R47", "LP2-as-pad inversion / all-pairs page XOR / canon as key", "S2", "F7", "16/30", "F-01, R30-B1", "XOR/sub", "English", "12,956-run pad", "NEGATIVE", TE, "internal pad under beam_v3 with solved-page offsets", "LEDGER.json F-01, R30-B1")
r("R48", "Non-cipher framings (image/DSP/message-existence)", "S4", "F8", "recon", "NONE", "none", "image/DSP stats", "", "NULL; message existence undecidable", T, "", "ELIMINATION-LEDGER.md:570-590")
r("R49", "Onion-image stego with large dictionaries; OutGuess hash blocks", "H10 H11", "F10", "29", "R29-L1-ONION-STEGO", "stego extractors", "agnostic", "24,078 extractions", "NEGATIVE", T, "", "LEDGER.json R29-L1")
json.dump(R, open("readings.json", "w"), indent=1)

cells = collections.defaultdict(list)
for x in R:
    for rw in x["rows"]:
        for f in x["families"]:
            cells[(rw, f)].append(x)
def status(rw, f):
    rs = cells.get((rw, f), [])
    if not rs:
        return "NEVER" if f in ROWS[rw][1].split() else "."
    cl = [x["status_class"] for x in rs]
    if T in cl: return "TRIED"
    for k in (TL, TE, TN, P):
        if k in cl: return k
    return cl[0]
short = {"NEVER": "NEVER", ".": ".", "TRIED": "T", "TRIED-ENGLISH-ONLY": "T-EN", "TRIED-LEGACY-BEAM": "T-LEG", "PARTIAL": "PART", "TRIED-NO-CONTROL": "T-NOCTL"}
cnt = collections.Counter()
lines = ["# O4 matrix - clue row x reading family", "",
         "Cell codes: T = TRIED (instrument-independent or current instrument, controls stated); T-EN = TRIED-ENGLISH-ONLY; T-LEG = TRIED-LEGACY-BEAM (pre-beam_v3 decoder, 9-register or English panel); PART = PARTIAL; T-NOCTL = tried, no positive control; NEVER = applicable cell with no reading; '.' = family not applicable to that clue. Reading ids (R01..R49) are listed in each cell and defined in readings.json.", "",
         "Families: " + "; ".join("%s=%s" % (k, v) for k, v in FAM.items()), ""]
hdr = "| row | clue | " + " | ".join(FAM) + " |"
lines += [hdr, "|" + "---|" * (len(FAM) + 2)]
never = []
for rw, (title, ap) in ROWS.items():
    cs = []
    for f in FAM:
        s = status(rw, f)
        cnt[s] += 1
        ids = ",".join(x["id"] for x in cells.get((rw, f), []))
        cs.append(short[s] + (" " + ids if ids else ""))
        if s == "NEVER": never.append((rw, f))
    lines.append("| %s | %s | %s |" % (rw, title, " | ".join(cs)))
lines += ["", "## Counts (applicable cells only)", ""]
for k, v in cnt.items():
    if k != ".": lines.append("- %s: %d" % (k, v))
lines += ["", "## NEVER cells", "", ", ".join("%s x %s" % (a, b) for a, b in never), ""]
open("matrix.md", "w").write("\n".join(lines))
cl = json.load(open("clues.json"))
summary = dict(clue_entries=len(cl), clue_entries_in_matrix=sum(1 for c in cl if c["row"]), matrix_rows=len(ROWS), readings=len(R), cells=dict(cnt),
               applicable=sum(v for k, v in cnt.items() if k != "."), never=len(never))
json.dump(summary, open("counts.json", "w"), indent=1)
print(json.dumps(summary))
print(never)
