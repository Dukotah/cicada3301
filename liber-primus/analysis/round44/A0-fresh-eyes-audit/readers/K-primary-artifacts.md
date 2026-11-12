# K-primary-artifacts — fresh-eyes audit notes (fork K, 2026-11-12)

Partition: corpus/, sources/, puzzles/, ciphers/, research/00-06, identity/ (skim), PROVENANCE/KNOWLEDGE/INDEX/PAPER/AGENTS (grep-level),
archive/branches-2026, liber-primus/docs/SOLVED-PAGES-AND-INTERRUPTERS.md, SOLVED-PAGES.json, data/scream314_lp.md.
Read-only on the repo. All my scripts: scratchpad `audit/K_work/*.py` (run with `PYTHONPATH=<scratchpad> python3 audit/K_work/<x>.py`).
Everything computed here is EXPLORATORY (no PREREG) unless it is a pure byte/identity check.

---------------------------------------------------------------------------------------------------------
## F1. [DROPPED-LEAD / new anomaly, exploratory] Segments 28 and 42 are position-aligned-related (possible depth pair)

Object: krisyotam %-segments 28 and 42 (= relikd 28.jpg / 42.jpg = scream314 45.jpg / 59.jpg; flat start 6761 and 10144, flat lag 3383;
lengths 269 / 272; second page of $-section 6 and third page of $-section 8; neither is a section start).
Statistic: d_i = (seg28[i] - seg42[i]) mod 29 over the 269 common positions (rune index within page, line breaks ignored).

| test | value | null p | family-wise |
|---|---|---|---|
| chi2 of d over 29 bins (pre-chosen, exact multinomial approx) | 74.1 on 28 df (IoC*29 = 1.172, z=6.2) | 4.8e-6 | 0.015 over 3,192 pair x sign tests at offset 0 (0.0077 differences only; ~0.5 if the 117,040 triple tests I ran in the same batch are counted) |
| share of that chi2 in the SYMMETRIC subspace (d vs -d folded) | 65.2 of 74.2 (antisymmetric part 9.0 on 14 df) | ~3e-4 (Beta(7,7) tail; independent of the first test under H0) | - |
| folded-|d| chi2, 14 df (post-hoc statistic) | 65.2 | 1.4e-8 | 1.9e-5 over 1,326 offset-0 pairs; **0.0047 over all 331,908 pair x relative-offset cells** (overlap >= 120) - it is the single top cell of the whole scan, at offset 0 |
| kappa (d = 0) | 21 / 269 (exp 9.3), z = 3.92 | - | top of 1,326 pairs but equal to the expected maximum (3.8): kappa alone cannot see it |
| |d| in {0,2,3,5,6} | 138 / 269 (exp 83.5), z = 7.2 | in-sample | - |

Histogram of d (0..28): [21,6,15,16,5,17,14,9,6,7,8,9,12,5,5,4,5,4,7,12,4,5,9,18,12,3,15,10,6].
Folded |d| 0..14: [21,12,25,31,8,29,32,18,11,11,20,16,16,10,9] (exp 9.3 for 0, 18.6 each otherwise).

What I checked trying to kill it:
- Not monogram bias: each page's own monogram chi2 is ordinary (23.5, 24.0 on 28 df), their monogram vectors correlate 0.11; shuffling seg 42's positions
  (monograms preserved) gives chi2 mean 28.0 sd 7.4 and 0/20,000 >= 74.1.
- Page-local: at the same flat lag (3383) the 234 runes before (seg 27 tail) give z = -0.09, seg 29 gives +1.04, seg 30 +0.05; a sliding 269-window peaks
  exactly on the page (lo = 6750-6770). Not a flat-stream periodicity; the (k, k+14) page family is null (z = 0.69).
- Rigid page-index alignment: every one of the nine 30-rune blocks is elevated (15,13,16,12,18,17,16,19,12 in-set vs 9.3 expected); line-left and
  line-right alignment destroy it (folded chi2 6.7 / 15.1). Relative offsets -15..+15 other than 0 are ordinary (16-51).
- Calibration of the scan: p-value fractions over the 1,326 pairs are nominal (p<0.05: 5.7%, p<0.01: 1.3%, p<0.001: 0.15%); next-best pair p = 5e-4.
  Sums (a+b) as a control family: best p = 6.8e-5 (Bonferroni 0.09). No third page shares the shape at offsets -3..3.
- Imaginary Fourier coefficients of the d distribution are all within noise (sum Im^2 0.017 vs 0.026 expected) = symmetric; real ones: k=1 (+4.1 sd),
  5 (+2.8), 9 (+2.2), 10 (+3.3), 11 (+3.3), 12 (+2.7), one negative k=7 (-2.4 sd; an autocorrelation must be >= 0, so this is a mild strain on pure depth).

What it is NOT: English-minus-English in Gematria index order. From Cicada's own solved plaintext (2,059 runes) the predicted difference distribution has
IoC*29 = 1.058 with peaks at 0 and +-14/15 (E-O, E-R); the matched filter gives (28,42) only z = 1.67 (rank 59/1326), and the observed histogram has a
TROUGH at +-14/15 (9 vs 18.6). The observed non-uniformity is ~3x the English prediction (excess chi2 51 vs 15.6, +3.7 sd). Affine re-labelings (d -> m*d)
fit weakly (best m = 4, r = 0.53/0.57). So if this is depth, either the plaintext alphabet is not in index order (C = pi(P) + K, a mixed-alphabet additive
cipher - a free pi reaches unigram LLR 20.6 nats vs 2.5 +- 2.6 on 10 control pairs, but that mostly re-expresses the non-uniformity) or the plaintext
symbol distribution is much more peaked than Cicada's prose (implied IoC*29 ~ 2.4), or the relation is something other than a shared additive key.

Why the repo never saw it (LOGIC-GAP in three standing closures):
- `analysis/armada/FOLLOWUP-TESTS.md:23-35` (#4): thresholded raw IoC*N > 1.12 with no length normalisation, named only the short-page top
  (29&54, n=76), and concluded "no credible shared-keystream signal". Its own reference (E-E IoC*N = 1.033; I get 1.058) shows the test is weak;
  no plant. (28,42) at 1.172 on n=269 was inside its ">1.12" list of 31 and not singled out.
- `analysis/round43/F3-hand-feasibility/KEY-LOCALIZATION.md:50,105`: "mean cross-page kappa exactly 1/29; max pair consistent with noise over 1,540
  trials. The process never rewound - 13k fresh key values." Kappa uses 1 of 29 bins; per-pair depth power at L=269 is ~z 3.9 even with the ideal
  matched filter for English, i.e. about the null maximum.
- `liber-primus/ELIMINATION-LEDGER.md:131` ("Page-on-page key reuse / in-depth - dead"), `SOLVERS-DOSSIER.md:49` and `:107-111`,
  `handoff/FOR-FUTURE-SOLVERS.md:330` ("killed by structural gates") state this as closed. No ledger row carries a per-pair power figure.
Checked not tracked: X0 #11 (REOPEN) is "all-pairs page XOR ... not run / kappa at offset 0 flat"; nothing names (28,42); grep for "28.*42" in armada/F3 docs: none.

Why it matters for solving: it would be the first positional structure beyond lag 1 in LP2. If real: (a) key material was reused between two pages
with rigid, skip-free alignment over 269 runes (so on these pages the anti-doublet mechanism did not desynchronise a running key - against
key-skip implementations, for per-page position-locked keys); (b) one collision among 55 pages suggests per-page keys drawn from a small space
(birthday-style: order 10^3, very wide interval); (c) any keystream hypothesis with per-page reset (R44 lane R1) gains a two-page joint crib;
(d) a depth-2 solve (two-time pad) is a bounded, human-checkable object (doctrine R5 #1).
Cost: 1 h to pre-register the statistic and re-run from committed code + plant a depth pair through the same glue; 5 min to confirm on the page
images that both pages read as transcribed; then a days-scale depth-2 decode lane (12 registers, free plaintext alphabet).
Scripts: K_work/share_test.py, pair_detail.py, pair_detail2.py, depth_llr.py, folded_scan.py, replicate.py, alloffsets.py, spectrum.py, linealign.py,
alphamap.py. Caveat on replicate.py: split-half correlation (0.80) is NOT independent of the full-page chi2 - do not cite it as replication.

---------------------------------------------------------------------------------------------------------
## F2. [CONTRADICTION, verified byte-exact] The three signed 991-byte "liber-primus-hash-block" blobs are XOR shares of a solved 2014 message

`corpus/A-primary-artifacts/signed-payloads/2014-01-liber-primus-hash-block.bin` XOR `...-outguess-01.bin` XOR `...-outguess-02.bin`
== `corpus/A-primary-artifacts/pgp/messages/2014-01-signed-ciphertext.asc` (991/991 bytes, sha256 81139c4d7e025878...): the PGP-signed
"IDGTK UMLOO ARWOE RTHIS ..." columnar-transposition message (which contains the letters of an onion address). They are the 2014 chain's
three-share XOR step, not hash blocks, not commitments to LP, not "never-decrypted payloads". 991 is simply that message's length.
Consequences:
- `analysis/round44/CAMPAIGN-PLAN.md:23` P5 "hash-block 20-byte-stride parse (after pinning the artifact identity)" and
  `round43/X0-firewall/ADJUDICATION.md:52,65` (item 29 NEW-lite) are moot: identity is pinned; a share is uniform by construction.
- Blind-agent premises in `round43/F1-blind/hypothesis_lists.json:14,63,152,181-183,311` ("three still-opaque ciphertext blocks", "authors commit to
  hashes", "LP2 is the pad for the 991-byte blobs" - X0 item 10, 3 agents) rest on a false description. X0 stamped item 10 CITED without noticing.
- Lane A's file naming (`REPORT-A.md`, `PAYLOADS.json`: "detected_type: unidentified") is the source of the misreading.
- Root cause: there is no artifact-verified step-by-step chain. `puzzles/README.md` promises `2012.md`, `2013.md`, `2014.md`; none exists;
  `research/03-puzzle-2014-liber-primus.md` never mentions the XOR step or the transposition. Solved-chain residue (these shares, the 05.jpg reversed
  trailer, onion-2/onion-6 concatenated and reversed JPEGs = `Huh2.jpg`, `ONION_2_JPG.jpg`, `10.jpg`) keeps being listed as open objects (X0 #16).
Cost: 0 (done). Suggest a one-page "solved-chain residue registry" (2 h) so future blind lanes and X0 can separate residue from open objects.

## F3. [CONTRADICTION] Two of Round 43's NEW stamps have prior art inside the repo
- p15 4x4 grid (X0 item 18: "No row contains the 16 numbers ... zero representation in the solver input"; X1 upheld by grepping LEDGER.json for 3258/4516).
  The grid is `M3_4x4` in `archive/.../campaign7/hill5_magic.py:38-39` and in `analysis/round41/C1-r14-r15/PREREG.md:13` / `RESULTS.md:14-15`
  (ledger row R41-C1-R15-HILL5-MAGIC, panel-R36: best 2.443 whole-book and 4.094 on p36, both for M3_4x4.M). It also sits in
  `analysis/round18/L3-ornaments/nonrunic.json` and `data/scream314_lp.md`. So the Hill-key reading of the grid is already a measured negative;
  R44-P2 should cite it and keep only the schedule / offset-table / page-index readings.
- Cuneiform clusters (X0 item 20: "No row ... zero representation anywhere"). Campaign VI/VII read them as base-60 numerals 17,13,55,1 -> 1033 and 3301
  and ran them as keys: `archive/.../campaign7/c2_cuneiform.py` (docstring) and `CAMPAIGN-VII-FINDINGS.md:22` (rigid, English-only, best -6.725).
  A community paper `Larger cuneiform numbers.pdf` is held in corpus/F (`BIBLIOGRAPHY-GENERATED.md:421`) and unread (GAPS-F F-G-10: "nothing in this
  lane was read"). LEDGER.json has zero occurrences of "cuneiform". R44-P5's census should start from the numeral reading.

## F4. [SHARED-PREMISE, now measured] LP2 0-54 does not use the solved pages' F-interrupter convention
- Rule on solved cipher pages, verified on the data with the repo's own solver: every plaintext F is written as a clear F and freezes the key; no plaintext
  F is ever enciphered (03.jpg: 16 ciphertext F = 7 clear + 9 enciphered non-F; 14.jpg: 5 = 2 + 3; 73.jpg: 5 = 1 + 4; enciphered plaintext F: 0/0/0).
  scream314 says so verbatim (`data/scream314_lp.md:267,851,1382,1990`: "Every clear text F is an F, and needs to be skipped"), whereas
  `docs/SOLVED-PAGES-AND-INTERRUPTERS.md` and `src/lp/solve.py` describe "a per-page subset the solver must discover" and R43 F3 TOOLKIT.md:33
  calls it "one bit of discretion per F". There is no discretion: it is deterministic on the plaintext side.
- Cicada's own plaintext F-rate (2,059 runes of direct/Atbash pages) = 1.65 %. Under the same rule LP2 would hold ~653 F; it holds 458
  (uniform expectation 446.8, sd 20.8): 9.4 sd short. Number of clear-F interrupters in LP2: 11.6 +- 21.5, <= 47 at 95 % one-sided.
- No other rune can be a clear pass-through either: per-rune counts are flat (chi2 26.4 / 28 df; max excess OE +45).
- Consequences: (i) the Round 19 FOUND-ERROR "the sweep beam reads an interrupter page at 14 %" is bounded to <= ~47 events book-wide, i.e. < 0.5 per
  120-rune decode - but `MEASURED-CEILING.md` never mentions interrupters at all (0 hits) among the unrepresented constructions; add the bound.
  (ii) "AN-END system continued book-wide" readings (X0 item 7, F3 J2) need F-free plaintext or a changed convention. (iii) Together with F5 this is a
  second, independent signature separating pp0-54 from every solved cipher page.
Checked: no ledger row, ELIMINATION-LEDGER line or STRUCTURE-FINDINGS passage draws this inference (they list the F counts and test F positions as a
channel: R11-S1, R37-C3-U6A-S1). Cost: 10 min to file.

## F5. [answer to pointed Q2] Solved cipher pages show NORMAL doublet rates
Polyalphabetic cipher pages (03, 04, 14, 73): 919 runes, 27 doublets (31.6 expected at 1/29; ~6 under LP2-style 0.19 suppression).
Monoalphabetic cipher pages (01, 06, 09): 964 runes, 19. Plaintext pages: 1,095 runes, 29. Cicada's plaintext rune-doublet rate ~2.3 %.
p56 (AN END, inside the onion-7 release): 2 in 85. The suppression is specific to pp0-54. No lead, but it localises the filter.

## F6. [LOGIC-GAP] "The keystream is one continuous stream; it does not reset per page" is not supported by its evidence
`analysis/STRUCTURE-FINDINGS.md` section 2 and `SOLVERS-DOSSIER.md:107-111` infer it from 0/54 page-join doublets (P = 0.155 with no suppression at
all) and from the filter looking back across boundaries, which says nothing about where the key restarts. The solved record says the opposite: the
only solved LP2 cipher page (p56) starts its phi(prime) stream at the page top; LP1 keys restart per section and continue across pages
(`scream314_lp.md:849` "Continuation of key"). Every screen is calibrated on the page-0 head at offset 0 (MEASURED-CEILING section 1). R44-R1 tracks
resets (so not new), but the three stale closure sentences stand uncorrected, and F1 is direct evidence of page-locked alignment.

## F7. [UNDISCHARGED] Recovered Campaign VII / XV probes without ledger rows
Lane H recovered them (2026-08-19); R40/R41-C1 ledgered only R14 (wordsum), R15 (hill5), R44 and C18 (Mayan/tweet numerics). No row for:
`c2_cuneiform`, `false_holes` (spaces-advance-keystream, first-rune shift, segment key-reset, OutGuess relocation), `reading_direction`,
`b3_hints` (telnet missing primes and gaps, trailing-space sequences 2012-2015), `c1_skipkey`, `b2_onion_xor`. All were rigid, English-only decodes
(best -6.6 to -6.9), i.e. not negatives under the doctrine. Either ledger them as English-era/rigid or queue the two cheap ones (segment key-reset,
trailing-space sequences) behind R44-R1. Cost: 1 h to ledger; hours to re-run.

## F8. [UNEXAMINED-INPUT, low] Secret sharing is a recurring 3301 technique with no LP2 analogue lane
2013: three signed `ssss-03/09/10` Shamir shares (`ibotpeaches/messages/2013`, REPORT-A section 2). 2014: the three-share XOR (F2).
I ran the simplest analogue (all 1,596 pairs x 2 signs and 29,260 triples x 4 signs of the 57 segments at offset 0, IoC of the combination, plant
recovered at z = 10.4 on a 95-rune page): null apart from F1 (z mean 0.003, sd 1.007). Not run: byte-level shares, shares at other alignments.

## Tail (tidiness or low prior)
- `corpus/B-liber-primus/CONFLICTS-B.md` C-02 / GAPS-B G-09: the scream314 `WS` vs `EA` error on LP1 page 06 is still live (SOLVED-PAGES.json still
  reads "THATISNOTWHATYOUARE"); LP1 only. G-04/C-05 (validate.py prefix) is fixed (R19 guard) though still marked OPEN in CONFLICTS-B.
- `TRAILING-DATA.json` "unparseable" list includes an onion-7 mirror page (`Hadyn_cicada/2014/ky2khlqdf7qdznac.onion/54.jpg`) and wiki `53.jpg`;
  X0 #16 tracks it as REOPEN with no lane; a diff against the SHA-pinned relikd p53/p54 settles it in 5 minutes (files are not in this checkout).
- `Outt.png` trailer (13,592 B after IEND, X0 #16 "palindrome"): its first 16 bytes (df7d35d37df4d74d f7d35d37df4d74df) are the base64-decoding of the
  repeating text "33010330103301033..." (period 5, i.e. 3301 / 1033 with a separator). Looks like padding, not payload. Full file not on disk here.
- `corpus/A/2014/signed_interconnectedness_decoded.bin` (6.65 MB, signer-attested 2014 audio) is in the checkout; no lane has reduced it (X0 #25 REOPEN).
- G-forensics G-G-07: 761.mp3 never had a spectrogram pass. GAPS-A A-04 (QR), A-05 (cross-hash 2013/2014/2016 entry images), A-09 (315 key
  certifications) are open but do not bear on LP2. GAPS-F F-G-10: the cipher-literature corpus was retrieved and never read.
- corpus/D D-G-04: `5fpp2orjc2ejd2g7.onion` (Portuguese) unauthenticated; not LP2.
- Side check (outside partition): per-page rune counts are under-dispersed vs iid (contingency chi2 1350.8 vs 1512, z = -2.9) but only z ~ -1.5 once the
  no-repeat Markov structure is accounted for (expected ~1427). Not an anomaly.

---------------------------------------------------------------------------------------------------------
## Pointed question 1 - 3301's own techniques vs an LP2 analogue under the repaired instrument
| technique (where used) | LP2 analogue tested? | rows | status |
|---|---|---|---|
| Caesar / Atbash / affine (2012 Caesar-4; LP1 pp01, 06-09) | excluded structurally: monograms flat (chi2 26.4/28), language-free | structural gates | covered, any register |
| Vigenere short key + F-skip (2012 reddit Mayan key; LP1 DIVINITY, FIRFUMFERENFE) | periodic IoC flat to m=40 (F3 C8, language-free); ~620 keywords English-era; artifact keys under panel-R36 | campaign XVIII; R40-C1-R30-B1; R42-C3; R40-C1-C18 | covered for finite lists; keyword mass English-era only; F-skip variant unrepresented by beam_v3 but bounded by F4 |
| phi(prime) stream + F-skip, page-top start (p56) | book-continuous and gridded starts | R11-N2/N5, R37-C3-U6A-N2/N5, R22-C, R26-C | covered as a continuous stream; per-page/section restart under the modern beam = R33-I2 "unrepresented" (R44-R1) |
| direct transliteration | n/a | - | - |
| book codes (Mabinogion, Gibson's Agrippa, Liber AL, Self-Reliance) | as running keys rigid + skip-aware; as index codes | attack.py runningkey; campaign XVIII `RUN-referenced.log`; R26-B (partial); R42-C1; R37-C2-U7 | covered English-era; texts held (data/keys/armada18); 12-register coverage of exactly these four not confirmed |
| file XOR / secret sharing (2013 ISO-segment XOR, ssss; 2014 three-share XOR) | pages as shares: kappa only (F3); IoC threshold (armada #4) | X0 #11 REOPEN | effectively untested until this audit (F1, F8) |
| columnar transposition (2014 IDGTK) | transposition-only excluded by flat IoC; transposition x stream product not run under panel-R36 | campaign XVII; R22-C (185 ops) | partial |
| RSA / factoring (2014) | payload as RSA | E-01, R30-B2 | covered (n/a to runes) |
| OutGuess (all years) | LP2 pages give default-key garbage; 60-key and 26x3 sweeps; 24,078 extractions on onion images | R29-L1, B-10, G-G-06 | bounded; keyed payload invisible (G-G-08); X0 #15 REOPEN |
| appended / reversed data after EOI (2012 1CcV1; 2014 05.jpg, onion 2/6) | 0 bytes after EOI on the 56 LP2 pages | R8 stego narrative | covered |
| magic squares (1033, 3301, p15 4x4) | Hill keys and numeric streams under panel-R36 | R41-C1-R15, R40-C1 | covered (see F3) |
| gematria sums / number-to-rune | sums as symbols, keys, selection | R10-L3, R37-C1-U2/U3, R37-C2-U4, R41-C1-R14 | covered |
| audio (761.mp3; Interconnectedness) | byte pad, sparse offsets | R12-A1, R40-B3 | partial; X0 #25 REOPEN |
| telnet primes / trailing whitespace / tweets | rigid English only | campaign7 b3 (no row), R40-C1-C18, H-02 partial | partial (F7) |
| timing channel (onion 2) | as keystream | R43-F5BT | covered at ~44 % |
| PGP timestamps as seeds | 433 ranked seeds | R18-L8, R20-P3 | covered |

## Pointed question 3 - corpus GAPS / CONFLICTS and whether picked up
corpus G-02 (PGP table): closed R18-L8. G-03 (independent transcription): closed at stated power (A-01, T1-05, T2-INDEL). G-09: closed for message
signatures. G-11: recovered, partly ledgered (F7). G-05/G-06 (IRC, archives): partly closed by R36-O2, R43-F5a/F5b. G-08 (cipher literature):
retrieved, unread. GAPS-A A-07 (stego toolchain): closed by Lane G / R29. GAPS-B G-03 (page 50 grid): covered by the pp49-51 rows. C-02: still live.
CONFLICTS-A C-02/C-05 (imgur and Fandom strip bytes): recorded; no LP2 consequence because LP2 pages are SHA-pinned to the onion dump.

## Pointed question 4 - archive/ and H-branch-recovery content not in LEDGER.json
See F3 and F7. Also `PAGE-MAP.md` (three numbering schemes) exists only in archive/ and corpus/H; master has no equivalent single table.

---------------------------------------------------------------------------------------------------------
## PRIMARY-MATERIAL x EXAMINED matrix
"held" = in this checkout unless marked (ign) = gitignored / fetch-on-demand per Lane A manifests.

| year | artifact / channel | held (path) | analysed by | lossy? / note |
|---|---|---|---|---|
| 2012 | entry image 1CcV1.jpg, 3 byte-streams, TIBERIVS trailer | (ign) corpus/A cijhho123, krisyotam, wiki | Lane A C-02, trailing scan | Wayback copy lacks the payload; 4chan bytes never held (A-01) |
| 2012 | 7 other chain images | (ign) | Lane A cross-hash (7/7 identical x3), Lane G battery | - |
| 2012 | reddit Vigenere + Mayan numeral key | text only | campaign7 b1 (rigid), R40-C1-C18 | - |
| 2012 | book-code texts (Mabinogion, Gibson Agrippa) | data/keys/armada18, capsule | running-key lanes | English-era |
| 2012 | posters, QR, 845145127.com, phone message | 6 photos (ign); no 2012 site capture | none | QR never decoded (A-04); not LP2-bearing |
| 2012-17 | 56 distinct PGP signatures, one key | corpus/A/pgp/messages (58), ibotpeaches (57) | Lane A, R18-L8 | timestamps used as seed prior |
| 2012 | key certifications (315) | corpus/A/pgp/keys | none (A-09) | not LP2-bearing |
| 2013 | entry image, second image | (ign) | visual only (A-05) | not cross-hashed |
| 2013 | 761.mp3 | (ign) puzzles/2013/artifacts | R12-A1, G-G-07 | byte pad at sparse offsets; no spectrogram |
| 2013 | CicadaOS ISO files (560.00/.13/.17, prime_echo, folly, wisdom) | (ign), byte-verified | R12-A1, R28-L1 | offsets 0.006 % |
| 2013 | ssss shares, coordinates, tcp-server, telnet, rune-table-morse messages | ibotpeaches/messages/2013 | verified; as seed strings (B-04 dictionary) | never read as a technique precedent (F8) |
| 2013 | Twitter stream / XOR image / Gematria table image | not held as originals (C-G-03); wiki image (ign) | mapping only | - |
| 2014 | entry image; "work of a private man" book code | (ign); .asc held | chain only | - |
| 2014 | LP1 pages 00-16 (images + outguess payloads) | images (ign); payloads in scream314_lp.md and corpus/A | validate.py; F5 above | - |
| 2014 | three signed 991-byte blobs | corpus/A/signed-payloads | **this audit: XOR shares of the IDGTK message (F2)** | previously "unidentified" |
| 2014 | IDGTK transposition, fallen-behind note, magic-square upload form, RSA-OAEP challenge | .asc held | R30-B2 (RSA); F3 (squares) | solved-chain residue |
| 2014 | 05.jpg trailer (reversed JPEG, hex, 1033 square); onion 2 / 6 concatenated JPEGs; Huh2.jpg | (ign) | Lane A scan; R43-F6 (T4 = JPEGs) | solved-chain residue; X0 #16 |
| 2014 | "let the text guide you" JPEG; onion-5 signed JPEG (second JPEG after EOI) | (ign) / .asc held | Lane A | signer-attested |
| 2014 | Interconnectedness audio | corpus/A/2014/signed_interconnectedness_decoded.bin | none as a reduction (X0 #25) | held, unexamined |
| 2014 | onion 1-7 HTML, 256-byte hex blobs, onion-2 timing | armada_osint (ign), R43-F5b | R43-F6, R43-F5BT, R29-L1 | HTTP headers not held (G-07) |
| 2014 | onion-7 LP2 pages 0-57 (58 JPEG) | (ign) data/relikd, 56/56 SHA-1 | everything | rune loader drops all non-rune marks (R43-F2) |
| 2014 | LP2 non-rune marks: red ink, dot clusters, cuneiform numerals, p15 grid, quotes, punctuation identity, inline digits 1-5 and 7, & $ section marks | images (ign); grid in L3 nonrunic.json | R18-L3, R19 ornaments, R43-F2; campaign7 (cuneiform as key), R41-C1-R15 (grid as Hill key) | R44 P1-P3/P5 (see F3 for prior art) |
| 2014 | pp49-51 base-60 table (256-byte payload) | canon + payload_resolved.bin | A-04, B-05, R28-L2, R28-L5, R43-F6 | most-covered object |
| 2014 | page-56 hash | text | anend_hunt, campaign7 b4, R43-F6 | preimage unreachable |
| 2015 | Planned Parenthood denial | .asc | verified | - |
| 2016 | 4gq25.jpg + outguess message ("words are the map ...") | (ign); micheloosterhof stage01 outguess held | R36-O4 matrix, R37/R38 clause readings | not cross-hashed (A-05) |
| 2017 | "Beware false paths" (SHA512 header) | .asc, pastebin copy | verified | - |
| any | IRC logs, non-English communities, YouTube | mostly absent (C-G-05/08/09) | R43-F5b partial | - |

## Checked and clean
- PGP record: one key, 54-56 distinct signatures, the 2 INVALID rows are one armor-damaged mirror copy (Lane A C-01; R18-L8 agrees).
- validate.py reproduces all six solved cipher/plain pages in this checkout.
- Book-code source texts, including Gibson's Agrippa (not only Cornelius Agrippa), were held and run (armada FINAL-VERDICT.md:15; campaign XVIII matrix line 54).
- Pair/triple additive-share scan: null apart from F1.
- Affine/identity alphabets for (28,42) do not give an English depth reading (matched filter z = 1.67).
