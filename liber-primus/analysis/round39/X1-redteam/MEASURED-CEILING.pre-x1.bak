# MEASURED-CEILING — what this repository's instrument generation excludes, at what power, and what re-opens it

_Round 39, lane P1. Written 2026-10-31 against `LEDGER.json` (256 rows). Binding doctrine:
[`ARMADA-DOCTRINE.md`](ARMADA-DOCTRINE.md) R2 (coverage times power, or nothing) and R7 (no foreclosure labels).
Every claim below is a table line with double-bracketed ledger row-id citations into `LEDGER.json`; `analysis/round39/P1-measured-ceiling/check_ceiling.py`
resolves each citation, refuses a strong verdict that cites a row without a passed positive control and a coverage
statement, and refuses the foreclosure vocabulary. CI runs it. If it fails, distrust this page._

**The position, in one paragraph.** Liber Primus pages 0-54 (12,956 runes) are not decrypted. Rounds 32-38 built one
instrument generation (call it **panel-R36**: a 12-register adjudicator, a register-aware skip-tolerant beam, a
skip-tolerant head screen, observed wrong-key nulls per relation and length, and a register-aware oracle) and pointed it
at every enumerable key family the ledger names and every clue reading the clue matrix found untried. Within its
reach (stated per row below) the answer is negative, with a planted control behind each negative. That is a
**bound set by this instrument generation, not a verdict about the puzzle**: every row carries the key space it
swept, the transition model of the decoder and the registers of the scorer, and everything outside those three is
listed in section 3 as *not excluded*. Section 2 gives, for each family, the one observation that re-opens it.

**Vocabulary used here.** `excluded at power p`: a swept key space, a planted control recovered at power p under the stated
decoder and registers, and no survivor above the pre-registered bar. `measured negative`: same, with the coverage or power
stated in the row. `partial`: some of the space or plan was measured. `unmeasured`: no instrument exists, or none ran.
`inconclusive`: an instrument ran and its own control failed or its evidence is absent. `not excluded`: outside every
swept space.

---

## 1. The instrument generation (panel-R36) — measured power and measured limits

| Component | Measured power | Measured limits | Rows |
|---|---|---|---|
| **Panel-R36** — 12 registers: EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE (Old English), DE, CY (modern-Welsh substitute), EN_HALFVOWEL, EN_NOVOWEL, GREEK, HEBREW, NORSE; panel sha256 `a0682f0c...` | 24 planted replicates per register at L=120 and L=240; all 12 registers at or above 0.90 power at both lengths; build run twice, byte-identical | 24/24 has a Wilson lower bound of 0.86; Greek/Hebrew/Norse use a fixed romanisation (unpointed Hebrew and other orthographies not covered); CY is a substitute because the original Welsh corpus is unrecoverable; the Round 19 panel (sha `14a23d36...`) is retired and its 44.138 % of the Py2.7-MT `exact` sweep was never re-scored; claim bars 7.3835 / 7.6342 are Round 19 quantities, not recalibrated for 12 registers | [[R36-P1-PANEL-R36-GATE]] [[R36-I1-NEW-REGISTERS]] [[R35-P1-R19-PANEL-RESTORE]] [[R36-S1-S2-WINDOW]] |
| **beam_v3 `panel_max`** under three transition relations: `keyskip1` (one-draw rejection), `keyskip2` (`skip_by_two`), `free` (up to 2 skips) | Correct-key recovery 1.00 pooled on the planted controls (81 cells x 20 plants); the L7-B defect (a decoder exact for one rejection loop only) is repaired | Recovery is *assumed* 1.00 for seven registers at orbit level (pooled control, not per-register); constructions outside the three relations (skip_by_4, skip_by_5, reset per page, reset per line, combined axes) are unrepresented; `lam_u=4`, beam width 400 only | [[R34-I1-V3-NULL-OF-RECORD]] [[R33-I1-REGISTER-AWARE-BEAM]] [[R32-I1-SKIPBYTWO-ENVELOPE]] [[R33-I2-CONSTRUCTION-AXIS]] [[R37-I2-PFV4-12REG-ORBIT]] |
| **Observed wrong-key nulls** per relation and length (`keyskip1`, `keyskip2` at L=120 and 240; `free` at L=240, 400, 729) | 12-register bars from 25,000 (L=120) and 4,000 (L=240) real-LP2 wrong-key decodes at actual N and at N=1e6; `free` licensed at L=240 for 10 registers and at L=400 and 729 for all 12 | OE and EN_HALFVOWEL are out of `free` at L=240; `free` nulls are 701 / 1,335 / 726 / 562 draws (target 2,000 unmet); N=1e6 bars are far-tail extrapolations (+-1); no real-LP2-structure null for `free`; ciphertext-derived key families need the bespoke key-matched null (transferred bars were 1.3-1.9 too low) with 121 analysed draws at L=240 | [[R36-B1-ORBIT-12REG]] [[R37-I1-FREE-NULL-LMATCHED]] [[R38-I2-X4-NULL]] |
| **pf_v4_12 head screen** (Viterbi over key advance 1 or 2, k up to 2 skips, log-sum-exp over the 12 registers, 24-rune head) | Natural-rate screen power 0.952 (EN_HALFVOWEL) to 0.994 (LP1_REAL), Greek 0.985, Hebrew 0.982, Norse 0.981; held-out FPR 8.9e-4; on the earlier nine-register calibration Hebrew/Norse reach was only 0.68/0.64 | Heads with 3 or more skips in 24 runes are not screened (estimated near 3 % of true-key mass by a Poisson argument on the measured 49-50 % with-skip rate, an estimate not a measurement); thresholds are calibrated to the real C[:24] head at offset 0; plants use the bash LP64 keystream; the PHP-cell FPR under the 12-register point is log-observed only (pooled 8.58e-4, 450/524288) and was never persisted | [[R37-I2-PFV4-12REG-ORBIT]] [[R35-I1-PFV4-SKIP-TOLERANT-SCREEN]] [[R36-I2-PFV4-KEYSTREAMS]] [[R38-S2-PHP-SANDBOX]] [[R36-B1-ORBIT-12REG]] |
| **Legacy (pre-Round-19) negatives** — what the old English-only scorer and one-rejection beam could see | English / archaic-English / LP1 register: power 1.00; Latin 0.33-0.50; half-vowel English 0.25-0.33; Welsh 0.00; vowel-dropped English 0.00 (correct key ranks below a wrong one) | Every negative from that era is an English-register negative on a one-symbol-per-rejection decoder; only stored survivor heads were re-scored under the later panels, not the swept spaces | [[B-04]] [[L7-A-SCORER-ENGLISH-ONLY]] [[L7-B-BEAM-ENVELOPE]] [[R24-C2-SKIP-BY-TWO-DECODER]] |
| **The S2 engine** (C port of Py2.7 `init_by_array`, `exact` relation) | Exact-relation planted control recovered 3/3 independently of the engine flag; window arithmetic re-derived | Cursor sums mix two instruments (Round 19 gate and panel-R36); only 3.809 pp of 2^32 carries panel-R36 pmax; window 2 is unrecovered and uncounted | [[R38-S1-S2-WINDOWS]] [[R36-S1-S2-WINDOW]] [[R27-CPORT-MT32-FULLSWEEP]] |
| **The oracle** — `verify_solution.py`: decodes under three relations, adjudicates with panel-R36, needs two pages under one relation, emits the `HUMAN-ORACLE.md` bundle | `--selftest` plants a key in English, Latin, vowel-dropped and Greek text and requires accept-good / reject-wrong | The no-oracle auto-certification seal fails: `SEAL_PASS=false` (fold family 36/45 catch at best; the non-fold family fails its pre-registered cells; the two-margin D5c rule fails at L=150; the linear D5c rule is retired); so no script may declare a solution and a human reads every crosser | [[R21-L1-SEAL]] [[R32-I4-NONFOLD-SEAL]] [[R35-I3-D5C-LINEAR-RULE]] [[R36-I3-D5C-TWO-MARGIN]] [[R36-X1-REDTEAM]] |

---

## 2. The exclusion table

Read every row as `excluded within (key space) x (transition model) x (register)`. The *Re-opens if* column is the single
observation (or the short list) that puts the family back on the table; it is copied from the ledger rows' `reopens_if`.

### 2a. Key families (generators, KDFs, pads, keytexts)

| Family / construction / reading | Swept (coverage) | Measured power | Three conditionals: key space / transition model / register | Rows | Verdict | Re-opens if |
|---|---|---|---|---|---|---|
| bash 4.2 `$RANDOM` auto-seed orbit (`%29`, offset 0, sign -1) | Full orbit, both ABIs: 77,594,624 seeds each; 65,815 (LP64) + 65,971 (ILP32) screen survivors all decoded (263,572 rows); earlier screens re-run three times (R34, R35, R36) | Screen reach per register 0.952-0.994 x v3 recovery 1.00 (assumed for seven registers); best 7.065 vs 12-register bar 8.027 at actual N (8.999 at N=1e6) | bash 4.2 auto-seed set, LP64+ILP32, offset 0 / `keyskip1`+`keyskip2`, heads with at most 2 skips in 24 runes (not `free`, not L=31) / panel-R36, 12 registers | [[R37-I2-PFV4-12REG-ORBIT]] [[R36-B1-ORBIT-12REG]] [[R35-B1-BASH-ORBIT-PFV4]] | **excluded at power 0.95-0.99** (per register, at most 2 skips in the head) | the oracle flags a row; a true-key head with more than 2 skips in 24 runes is shown; a register outside the twelve is added; another bash version or seeding is hypothesised |
| The recurring near-miss: bash seed 1354603465 (LP64 `keyskip2`, pmax 7.068) | Reproduced exactly; 2,383 of 2,972 grid cells (both ABIs, three relations, both signs, L 120-729, key and cipher offsets 0-28 one axis at a time); nulls of 400-2,000 draws | Family-wise P(best of 69,017 >= 7.068) = 0.20 (ILP32 0.56); excess over a size-matched null falls 4.85 to 1.08 as L grows; decode has no word structure while plants read verbatim | this seed only / `keyskip1`/`keyskip2`/`free` beam_v3 / 9- and 12-register panels | [[R36-O3-NEARMISS-1354603465]] | **measured negative** (noise, p=0.20) | an L-matched `free` null larger than n=100 at L=729 contradicts it (one ILP32 `free` L=729 cell, 15.15, exceeded an n=100 null max of 14.33 and was later placed at family-wise p near 0.95 by [[R37-I1-FREE-NULL-LMATCHED]]) |
| PHP `mt_rand`, prior-dense tier (4 cells: mt/php twist x scale29/mod29) | 48,036 seeds per cell: 487 core + 9,280 dense decoded unfiltered; 38,269 dense through pf_v4; 263,906 persisted rows | Screen power 0.94-0.99 x v3 recovery 1.00 (control, Wilson lower bound near 0.91); tier overall reach about 0.98-0.99; best 6.608 vs bar 7.941 at actual N | prior-dense PHP list (primes, dates, PGP times, ints), offset 0 / `keyskip1`+`keyskip2`, at most 2 skips in the head / nine-register panel (Greek, Hebrew, Norse not applied to PHP) | [[R36-B2-PHP-AWAKE-PFV4]] [[R32-B2-PHP-MT-RAND]] | **excluded at power 0.98** (nine registers) | the oracle flags a row; a true-key head with more than 2 skips; PHP variants or offsets other than 0; Greek/Hebrew/Norse applied to the PHP rows |
| PHP `mt_rand`, uniform tier (first ~1 % of 2^32 per twist) | 41,680,896 seeds drawn (0.9705 % of 2^32, 0.9658 % unique); R36 added screen power and persisted rows on a 0.607 % subset of the same stream, no new key space | R32 screen power 0.47-0.74; R36 pf_v4 screen power 0.94-0.99 on the 0.607 % subset; best 6.856 vs 6.991 at actual N | uniform sample of 2^32, offset 0 / `keyskip1`+`keyskip2`, at most 2 skips / nine registers | [[R36-B2-PHP-AWAKE-PFV4]] [[R32-B2-PHP-MT-RAND]] | **measured negative** (about 1 % of the space only) | the remaining tier is funded (resumable in append mode); see the 99 % line in section 3 |
| Py2.7 `random.seed(w)` Mersenne Twister, `pair` relation (`keyskip2`, `random29`) | **Full 2^32**: 4,294,967,296 seeds scored exactly once (histogram sums to 2^32); 392,131 flags at the 5.0 candidate bar (1.31 x the Gumbel prediction); three claim-bar crossers (35563892 and two others), all adjudicated noise | Power 1.00 at the tested resolution (plant margin 12.93, false-reject 0 observed, K4 parity 0.0 across 10,971 re-scores) | Py2.7 `init_by_array([w])`, w uint32, offset 0 / `keyskip2` (`skip_by_two`-exact) / Round 19 nine-register panel, claim bar 7.3835 (not re-scored under panel-R36) | [[R27-CPORT-MT32-FULLSWEEP]] | **excluded at power 1.00** (Round 19 panel) | a K4 parity disagreement above 1e-6 (parity void); per-cell controls (S3) are built; or the mass is re-scored under panel-R36 and a row crosses |
| Py2.7 MT, `exact` relation (`keyskip1`), cumulative | **47.95 % of 2^32** (cursor 2,059,308,008): 44.138 % under the Round 19 panel + 3.809 pp under panel-R36 (163,579,124 seeds: R36 window 54,967,546 + R38 window 108,611,578); window 2 launched but unrecovered, not counted | Exact-relation control 3/3 independent of the engine flag; panel-R36 windows: 0 crossers, 0 near-misses, best 7.3007 vs claim bar 7.6342; Round 19 top-1024 re-scored under panel-R36: only 35563892 (7.6707) crosses, a known noise-crosser | Py2.7 `init_by_array`, `random29`, offset 0 / `keyskip1` only / mixed: Round 19 panel for 44.138 %, panel-R36 for 3.809 pp; claim bar not recalibrated for 12 registers | [[R38-S1-S2-WINDOWS]] [[R36-S1-S2-WINDOW]] [[R27-CPORT-MT32-FULLSWEEP]] | **measured negative** (47.95 % cumulative, mixed instrument) | window 2 is recovered from its snapshot and a row crosses; or S2 continues over the remaining cursor space (section 3) and one crosses |
| Py2.7 other reducers (`grb5_mod`, `grb5_rej`, `shuffle29`), amd64 2-word `init_by_array`, integer seeds | Prior-dense words first (45,975 prior words fully covered), then dense-from-0 slices: 884,000 words screened (0.0043-0.0067 % of each config); 2,458,000 for `random29` i386 (0.057 %) | Positive control rank-1 at pmax 28.268 on all four configs (power about 1.0 on the win-condition registers) | Py2.7 word space per config, offset 0 / `keyskip1` / Round 19 nine-register panel | [[R21-L3-PY27-REDUCERS]] [[R20-SG3-PY27-RANDOM29]] | **measured negative** (under 0.1 % of each space) | the full enumeration of a config (about 10.9-18.4 core-days each) or the 2^64 image is run; a Py2.x seed family is validated |
| Py2.7 string-seed dictionary (amd64 hash image) | 1,201,672 distinct strings, 11 items, 2,500,207 decodes (about 1.4e-13 of the 2^64 image) | Best stage-A pmax 6.3148 vs 7.3835 / 7.6342, but the 226 stage-B rows, dictionary and bulk store are absent from the checkout | dictionary amd64 hash image, offset 0 / `keyskip1`+`keyskip2` / Round 19 nine-register panel | [[R28-L3-PY27-STR-AMD64-DICT]] | **inconclusive** (not citable as an exclusion) | `candidates28.jsonl` and `dictionary.jsonl` are recovered (it then upgrades to a bounded negative with no re-sweep), or any tier outside coverage is run |
| SHA-256-CTR / HMAC-DRBG / AES-CTR / RC4 / ChaCha20 seed lists; PBKDF2 and the 27 tested KDF configs; payload-as-seed | B-04: 6,224,300 decodes; B-05: payload representations x expanders; R16-KDF: 27 configs; offsets scanned 497,025,024 (B-02); stored survivors re-scored through the Latin/OE/DE/half-vowel adjudicator | English / archaic-English / LP1 register power 1.00; Latin 0.33-0.50; half-vowel 0.25-0.33; Welsh 0.00; vowel-dropped 0.00 on the original sweep; stored top-50 and 48 KDF survivor heads re-scored through the nine-register panel (min L=120 power 0.92), best pmax 3.97 vs escalate bar 6.05 | Cicada-flavoured short seeds, the listed expanders and KDF grid / one-symbol-per-rejection beam, with `skip_by_two` discharged in R24 for the top-prior slice / English register in the sweep; other registers on stored survivors only | [[B-04]] [[B-05]] [[R16-KDF]] [[B-02]] [[R24-C2-SKIP-BY-TWO-DECODER]] [[R24-C1-EXT-NONENGLISH-READJUDICATION]] | **excluded at power 1.00** (English register); **measured negative** (other registers, stored survivors only) | a KDF config outside the 27, or a salt or secret outside the covered ranges; joint corruption of two or more contested payload bytes; a stretching or salting construction not tested; a seed dictionary or generator outside the swept sets together with an offset sweep |
| glibc `srandom(seed); random() % 29`, gen=0, prior-dense | 48,036 distinct seeds (1.12e-5 of 2^32) x {pair, exact} = 96,072 decodes; best pmax pair 5.74 / exact 5.393 vs 7.3835 / 7.6342 | Plant-and-recover control passed on the Round 19 nine-register panel sibling (lane-local rebuild) | prior-dense glibc seeds (PGP times, dates, B-04 ints), offset 0, sign -1 / `keyskip1`+`keyskip2` / nine-register panel (lane rebuild) | [[R32-B3-GLIBC-GEN0-PRIORDENSE]] | **measured negative** (prior-dense only; 99.9989 % of gen=0 is in section 3) | the full 2^32 gen=0 completes; any listed-out axis (offsets, sign +1, other reductions, timestamp jitter) is run |
| Corpus-semantic seed zoo (323 seeds: primes, totients, 3301, 0x7A35090F fragments, dates, coordinates, gematria sums, clue phrases) x 7 generators | 323 of 323 deduplicated seeds x (Py2.7 `random29`/`grb5_mod`/`grb5_rej`, glibc `g_r29`, prime / totient / prime-totient ladders) x 2 decoders | Plants recovered for the generators under test | the 323 seeds, offset 0 / two decoders / the then-current panel | [[R26-C-SEMANTIC-SEED-ZOO]] | **measured negative** | a semantic seed source beyond the 323-value enumeration; offsets other than 0 for the set |
| Perl `rand`, TeX `\pgfmathrandom` and Py2.7 amd64 generators, first scored sweeps | 347 corpus-derived prior-dense seeds fully swept (empty); about 7,194 of 49,302 planned dense decodes at close-out | Planted control recovered at 1.000 for all three generators | prior-dense seeds plus a dense-from-0 slice (about 747 seeds / 2^32) / `keyskip1` / nine-register panel | [[R26-A-GEN-SWEEP-FIRST-FIRE]] | **partial** (interim; flat tails unmeasured) | a GPU or C port finishes the flat 2^32 or 2^64 tails; a new corpus-derived seed family or generator is identified |
| Keytexts as running keys (33 mysticism / philosophy texts) | 1,562 decodes: pages 19, 26, 28 complete at 4 offsets per text; page 23 at 86 %; page 20 a thin slice; 991 of 2,184 planned (45.4 %) | Planted-running-key control recovered 1.000 at L=240 (control present; its ledger field is a prose description, not the word `passed`) | 33 texts, 4 offsets per text, sign -1 / `keyskip1`+`keyskip2` / nine-register panel | [[R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE]] [[B-16]] | **partial** (45.4 % of the plan; the earlier keytext nulls were unsound and are retracted) | pages 20, 22, 25, 27, 29 are run at 4 or more offsets per text; a keytext outside the 33 is proposed |
| The author's own CicadaOS pads and literal pad files as byte-to-symbol reductions | 2 authoritative pads x 5 reductions x fwd/rev x both signs x 2 relations: 24,080 rows (100 % of plan); 6 pads, offsets to 5e7 (R12-A1) | Planted control passed | the pad files, mod29 / prime-index / nibble / scaled reductions, offsets on a stride grid / `keyskip1`+`keyskip2` / English-leaning panel of that round | [[R28-L1-CICADAOS-PADS-DENSE-PAIR]] [[R12-A1]] | **measured negative** (as literal reductions only) | a construction or register outside the three conditionals gains a measured prior; the pads are used as a PRF seed or salt (that is the B-04/B-05 lane) |
| Public randomness: blockchain, beacon, archives (English plaintext) and a date-indexed pad | Offsets selected by an English trigram prefilter and the top 40 per sign escalated (R17); NIST beacon v1 date-indexed with right/wrong-date plants (R24-C8) | English plaintext only; the date-indexed join key (a per-page timestamp) is absent for pages 0-54 | public archives named in the source table / English beam / English register | [[R17-PUBLIC-PAD]] [[R24-C8-DATE-INDEXED-PAD]] | **measured negative** (English plaintext only) | the Marsaglia CDROM sweep or any pre-2014-01 dated archive scores at or above its null max + 0.5; an external per-page timestamp for the LP2 pages is found |

### 2b. Clue readings and structural channels

| Family / construction / reading | Swept (coverage) | Measured power | Three conditionals: key space / transition model / register | Rows | Verdict | Re-opens if |
|---|---|---|---|---|---|---|
| Composed clue: "words are the map, meaning is the road, numbers are the direction" (position / rune offset / word length x mod 29,28 x start x sign) | 4,176 decodes on page heads 0-2 (k restarts per page) | Planted controls recovered; best 4.484 (`keyskip1`) vs bar_v3 6.632 at actual N | rho x M x start x sigma grid, offset 0-28 / direct, `keyskip1`, `keyskip2` / panel-R36, 12 registers | [[R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION]] | **measured negative** | "meaning" yields a determinate per-word index (not position or length); the LP1 codebook order differs from document order |
| LP1 gematria sums as a key schedule (additive and pointer-jump; text lines and printed lines) | 3,072 decodes (16 variants, text lines) + 768 decodes (printed lines: additive + pointer, prime / index, mod 29/28) | Planted controls recovered; best 4.793 vs 6.778 (`keyskip1`); printed lines at least 1.3 below bar | 16 + printed variants, offsets 0-7, page heads 0-2 / `keyskip1`+`keyskip2` / panel-R36 | [[R37-C1-U2-LP1-NUMBER-SCHEDULES]] [[R38-C2-G2-PRINTED-LINE-SUMS]] | **measured negative** | a stated reading fixes the base key or sequence start for the pointer form; the printed LP1 line layout yields different per-line sums |
| Clue strings and all seven signed clauses as seeds, three derivation routes (direct, hash, PBKDF2; UPPER and as-written) | 8,832 decodes (83 strings) + 384 decodes (clauses 6 and 7) | Plants rank 1 (6/6, 32/32, 24/24 across variants); best 5.239 vs bar_v3 7.179 | clue strings x routes x offsets 0-7 x sign / `keyskip1`+`keyskip2` / panel-R36 | [[R37-C1-U1-CLUE-STRINGS]] [[R38-C2-G1-CLAUSES-6-7]] | **measured negative** | a clue-derived string beyond the candidate list with a stated reading; the key is a hash or KDF output of a string not in UPPER or as-written form |
| Signed numbers as book-code indices | 240 selections (144 powered at n >= 30), 320-cell family bar | Controls A and C passed; best p 0.027 over 320 cells | 3 strings x index forms x LP1 / unsolved register, 0/1-based, reversed / index-alphabet and order-shuffle nulls / panel-R36 pmax_ne | [[R37-C2-U7-BOOK-CODE]] | **measured negative** (powered cells only) | a held book-cipher source is identified |
| Book-code, whole-indexed-word variant | 96 short or unpowered selections | Control B failed (the LP1 register contains LP1 words) | whole-word retrieval / same / LP1 register | [[R37-C2-U7-BOOK-CODE-W]] | **inconclusive** (control failed) | a control that separates the LP1 register from LP1 words is built |
| Prime line sums as a recognizer | 6 decrypted pages, 60 physical lines, both sides, 10,000 shuffles + 10,000 random strings per page | Plant 60/60; pooled 21/60 and one page at p<0.05 (a flagged coincidence, no separation) | printed-line primality / none (recognizer) / n.a. | [[R37-C2-U4-PRIME-LINE-SUMS]] | **measured negative** (no separation) | a language-free recognizer separates real from shuffled lines on a page the rule was not fitted on |
| Semantic address: "meaning" as a frozen public lexical address (WordNet 3.1 first-synset offset; Norvig frequency rank) | 28,224 decodes per variant set, pages 0-2, `keyskip1`, L=120 | 36/36 planted variants recovered; best 5.296 vs 7.85 | 3 reductions x A1/A2/A3 x start x sign / `keyskip1` / panel-R36 (an offset is a file address, not a sense; the frequency-rank row is not a reading of "meaning") | [[R38-C1-SEMANTIC-WORDNET]] [[R38-C1-SEMANTIC-FREQRANK]] | **measured negative** (address-type readings only) | a determinate sense-level reading is stated (see section 3, sense similarity) |
| Lagged pointers (gematria or index of the previous cipher word or decoded word) | 576 decodes (cw A1/A2/A3, dw A1/A2) | Gap controls 80/80; the A3 control is skip-free | pointer forms / `keyskip1`+`keyskip2` / panel-R36 | [[R38-C2-G3-LAGGED-POINTERS]] | **measured negative** | a lag form outside cw/dw, or a control with skips for A3 |
| Matrix cells with a literal operation (7 NEVER cells) | about 1,730 decodes + 5,760 hashes + one word-primality measurement | Cell controls passed (three cells are PARTIAL, subfamily only) | per-cell / per-cell / panel-R36 | [[R38-C2-NEVER-CELLS-RUN]] | **measured negative** (7 cells; 3 of them partial) | a stated operation for any of the cells listed in section 3 |
| Round 10 map / road streams and the Round 11 number-channel lenses, re-scored outside English | M1 464 + 21,808 + M2 348 + M9 290 + M5 1,486 map streams; 208 road streams; N1 CT-feedback 24 configs; N2, N4, N5 (4,640 decodes), S1, S2 under 12 registers; the z=6.94 map stream is an ordinary member of its own family (family p 0.95) | Direct plants 14/14, beam plants 30/30; N5 AN END control 1.00 / 0.93 | regenerated streams and ledgered configs / direct and `keyskip1`+`keyskip2` / panel-R36 | [[R37-C3-U5-L2-MAP]] [[R37-C3-U5-L3-ROAD]] [[R37-C3-U6A-N1-CT]] [[R37-C3-U6A-N2]] [[R37-C3-U6A-N4]] [[R37-C3-U6A-N5]] [[R37-C3-U6A-S1]] [[R37-C3-U6A-S2]] | **measured negative** (N3 whole-book integer structure is inconclusive) | a stream whose panel pmax and standardised Z both clear the family-wise null with non-degenerate IoC and mds |
| Ciphertext-derived keys (N4 / N5 / X4) at L=240 under a key-matched null | Top-50 each at L=240; bespoke X4 null: 2,000 draws at L=120, 121 at L=240 | N5 7.446 and N4 8.57 above transferred bars, matched-null p 0.74 / 0.16; decodes are non-language; X4 bar 6.99 vs transferred 5.69 | the R37 N5/N4/X4 families / `keyskip1`+`keyskip2` / panel-R36 (oracle bundle kept; logged as a noise-crosser on the coordinator's reading) | [[R38-C2-N5N4-L240]] [[R38-I2-X4-NULL]] | **measured negative** (noise-crosser; human read pending) | the owner reads the bundle two pages deep and judges it language; or the L=240 null is extended to 2,000 draws and the verdict moves |
| Literal imperatives as operations (decimation, interleave, whole-stream reversal, running key, prime / totient keystreams) | 185 operations; structural re-score of 169 streams and 14 keyed configs x 6 windows x 2 relations | Size-matched seed-3301 null empty; keyed R22-C 5.46 vs 6.04 at L=240 | width-4 interleave, offset 0, prime / totient keystreams / direct and keyskip / panel-R36 | [[R22-C-LITERAL-IMPERATIVES]] [[R37-C3-U6B-R22C]] | **measured negative** | a width other than 4, a non-zero keyed offset, or a phi(phi) / lambda / digit-plane keystream clears the bar with recovery >= 0.90 and held-out >= 0.90 |
| Signed-hint channels read literally: self-embedded acrostic / every-k selections, printed-line acrostics, turtle / spatial render, drop-cap channel | 3,508 selection functions; 48 line and word acrostic reads; 72 render combos x 200 shuffles; drop-cap catalogue over all 58 page scans | Controls passed for each lane | selection functions and render classes as enumerated / identity transform / English target for the acrostics | [[R22-A-SELFEMBEDDED-READ]] [[R23-A2-LINE-ACROSTIC]] [[R22-B-TURTLE-SPATIAL-RENDER]] [[R22-D-ILLUSTRATION-DROPCAP]] | **measured negative** | a keyword-cued or two-stage selection; a render outside the enumerated turtle class; a per-page figural-motif sequence; a non-English acrostic target with its own model |
| Glyph-shape and sub-pixel channels in the rendered pages | Font variants over pp0-53; baseline / advance / kerning / jitter of repeated runes | Runes are a deterministic vector font (28/29 runes IoU 1.000); detection floor about 2 px on the 400 dpi JPEG | pp0-53 / n.a. / n.a. | [[R30-A1-FONT]] [[R30-A2-SUBPIXEL]] | **measured negative** (above the 2 px floor) | a lossless or higher-DPI render, or the original PDF with exact kerning arrays, appears |
| Geometry: "numbers are the direction" per-page turtle renders (V1 / V3 / V4 variants) | 232 renders (58 pages x 4 variants); 174-render variant-limited diagnostic; the three above-null renders were viewed and are random walks | Planted-glyph detection 1.0 (D2) but realised FPR 0.16 (V2 29/50, V3 3/50), so the control failed | per-page renders / n.a. / n.a. | [[R37-C2-U8-GEOMETRY]] [[R38-I1-GLYPH-RECOGNIZER]] | **inconclusive** (V1/V3/V4 at chance level as a diagnostic, not evidence; V2 unmeasured) | a page-matched null (shuffle within line and word, keeping interrupters) brings V2 FPR to 0.05 or below; the pre-registered D2 revision is run |
| Round 11 lens rows as originally filed (English-only legacy scorer) | few-hundred-decode scale; English quadgram only | no planted control recorded in the original rows | legacy / legacy beam / English | [[R11-N1-NUMBER-CHANNEL]] [[R10-L2-MAP]] [[R10-L3-ROAD]] | **unmeasured** in their own right (superseded by the re-scores above) | n.a.; the re-scores in this table replace them |

---

## 3. What is NOT excluded

Nothing in section 2 says anything about the following. Each has a size, a status, and the instrument it would need.

| Not excluded | Size / what it is | Status | Rows | What would measure it |
|---|---|---|---|---|
| Unbounded pads: a true external pad, a hardware or dice source, any pad not derived from a seed | Not enumerable | not excluded (the ciphertext cannot distinguish an external pad from a short-seed derivation) | [[VERDICT-OTP-CLASS]] [[R17-PUBLIC-PAD]] | the pad surfacing, or a dated public archive scoring above its own null max + 0.5 |
| Constructions outside {`keyskip1`, `keyskip2`, `free` with up to 2 skips} | skip_by_4, skip_by_5, reset to a nonzero offset, resets per page or per line, combined axes, heads with 3 or more skips (estimated near 3 % of mass) | unmeasured | [[R33-I2-CONSTRUCTION-AXIS]] [[R35-I1-PFV4-SKIP-TOLERANT-SCREEN]] | a screen beyond 24 runes at 3x cost or less; a source-code find that gives the construction an evidence prior |
| Registers outside the twelve | unpointed Hebrew, runic-inscription Norse, other languages and orthographies, a real Welsh register (CY is a substitute), non-linguistic payloads | not excluded | [[R36-I1-NEW-REGISTERS]] [[R35-P1-R19-PANEL-RESTORE]] [[R36-B1-ORBIT-12REG]] | add the register to the panel, re-measure power, and re-screen |
| About 52 % of the Py2.7-MT `exact` cursor space, and the Round 19-gated 44.138 % under panel-R36 | cursor sum 2,059,308,008 of 2^32 is 47.947 %; panel-R36 carries only 3.809 pp; about 11 sandbox-hours remain | partial | [[R38-S1-S2-WINDOWS]] [[R36-S1-S2-WINDOW]] | recover window 2 from its snapshot (after the quota reset, before about 2026-11-07), then persistent-session windows |
| About 99 % of the PHP `mt_rand` uniform tier | 99.39 % of 2^32 per cell beyond R36; the Round 38 sandbox lane persisted zero seeds | unmeasured | [[R38-S2-PHP-SANDBOX]] [[R36-B2-PHP-AWAKE-PFV4]] | the retry harness: control and FPR persisted first, then 3301 blocks 318 and up and the 3302 stream |
| The flat tails of the other generators | glibc gen=0 beyond the 48,036 prior-dense seeds (99.9989 %); Perl and TeX 2^32 tails; Py2.7 reducers and amd64 2^64 image (over 99.99 %) | unmeasured | [[R32-B3-GLIBC-GEN0-PRIORDENSE]] [[R26-A-GEN-SWEEP-FIRST-FIRE]] [[R21-L3-PY27-REDUCERS]] [[R28-L4-UNSWEPT-GENERATORS-QUEUE]] | a C or GPU port; about 10.9-18.4 core-days per Py2.7 config |
| Other bash versions and seedings; other PHP variants; offsets other than 0; sign +1 on most rows | bash 3.2 / 4.0 / 4.1 / 5.x, a real 32-bit bash 4.2, non-zero key offsets | not excluded | [[R32-B1-BASH42-RANDOM-AUTOSEED]] [[R36-B1-ORBIT-12REG]] | a stated version or offset with its own plant-and-recover control |
| The 18 sense-similarity cells (F5 column of the clue matrix): hypernym depth, synonym class, lemma-sense count, gloss length, all senses | 18 NEVER cells; the last matrix cells with a literal basis; Round 39 lane C1 is running and is not in the ledger at the time of writing | unmeasured | [[R38-X1-REDTEAM]] [[R36-O4-CLUE-COVERAGE]] | the Round 39 C1 sweep, frozen lexicon and planted controls per variant |
| The 34 matrix cells with no stated operation | clue entries for which the text gives no operation to run | not excluded (a stated operation re-opens each) | [[R38-X1-REDTEAM]] [[R36-O4-CLUE-COVERAGE]] | an operation stated in the source text or a hidden-operation hypothesis with a control |
| English-only and legacy-beam rows not yet re-scored under panel-R36 | about 21 TRIED-English and 25 TRIED-legacy matrix cells | partial | [[R36-O4-CLUE-COVERAGE]] [[R38-X1-REDTEAM]] | re-run each named reading under beam_v3 and the 12-register panel |
| The two unmeasured instruments: V2 geometry and the auto-certification seal | V2 render FPR 0.16; `SEAL_PASS=false` | unmeasured | [[R38-I1-GLYPH-RECOGNIZER]] [[R37-C2-U8-GEOMETRY]] [[R36-I3-D5C-TWO-MARGIN]] [[R21-L1-SEAL]] | a page-matched null for V2; a seal that reaches 0.90 catch at 0.10 false-reject on a held-out virgin key |
| Ciphertext-side channels the readers cannot see | sub-2 px placement, colour / chroma, ink outside the 109 band boxes, the original PDF's kerning arrays | not excluded | [[R30-A2-SUBPIXEL]] [[A-06]] [[B-12]] | the original PDF or a lossless render; a per-rune reader and a multi-register scorer on the bands |

---

## 4. If you have a candidate

1. Build the bundle exactly as [`HUMAN-ORACLE.md`](HUMAN-ORACLE.md) section 1 specifies and put it in `analysis/<round>/<lane>/ORACLE-<id>/`: provenance (generator, parameters, relation, offset, page, sign, one-command `reproduce:`), the decoded text of at least two independent pages (rune-index decode and transliteration; one page the key was not selected on), the three `hitfn20` verifier outputs verbatim (panel-max bar at stated N, rune recovery >= 0.90, held-out 3/4 reproduction), the panel argmax trace, the lane's planted-control recovery with the language-agnostic row (IoC, mds, pmax_ne, zl), and the commit hash.
2. Run `python verify_solution.py --keystream ...` as supporting evidence, open a GitHub issue titled `ORACLE: <lane> <id>` with label `oracle`, and stop running sweeps over that space. The repo owner (or a person named in writing) reads two pages as language; only `PASS` moves a ledger row to `positive`, and the community's acceptance test remains a PGP-signed claim (key 7A35090F).

## 5. How to rebuild and re-run

Run from `liber-primus/` (Python 3.12; `numpy` and `pytest` needed).

```bash
python data/fetch_sources.py                                                  # 1. fetch the gitignored transcription sources
python analysis/round36/I1-new-registers/fetch_r36.py && \
  python analysis/round36/P1-panel-r36/build_r36.py analysis/round36/P1-panel-r36/build1   # 2. build panel-R36 (npz sha256 a0682f0c...)
python -m pytest benchmark/ -q                                                # 3. the gate: plant-and-recover instrument gates, both directions
python verify_solution.py --selftest                                          # 4. the oracle accepts a good key in four registers, rejects a bad one
python tests/validate.py && python analysis/round39/P1-measured-ceiling/check_ceiling.py   # 5. validate: the rig reproduces every known decrypted page; every claim on this page resolves to a ledger row
```

A fresh clone carries a committed copy of the panel (`data/panels/panel-r36.npz`), so step 4 runs without step 2. If any
command fails, distrust this page and the repository.

---

<!-- pins: each line is "ROW-ID | substring that must occur in that row's JSON". check_ceiling.py fails if one is absent. -->
<!-- pin: R36-P1-PANEL-R36-GATE | a0682f0c -->
<!-- pin: R36-P1-PANEL-R36-GATE | 14a23d36 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 77,594,624 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 0.952 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 0.994 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 8.9e-4 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 263,572 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | 8.027 -->
<!-- pin: R37-I2-PFV4-12REG-ORBIT | assumed from pooled -->
<!-- pin: R35-I1-PFV4-SKIP-TOLERANT-SCREEN | 3+ skips -->
<!-- pin: R36-I2-PFV4-KEYSTREAMS | 0.940 -->
<!-- pin: R37-I1-FREE-NULL-LMATCHED | not OE, EN_HALFVOWEL -->
<!-- pin: R37-I1-FREE-NULL-LMATCHED | 701 / 1335 / 726 / 562 -->
<!-- pin: R38-S2-PHP-SANDBOX | 8.58e-4 -->
<!-- pin: R38-S2-PHP-SANDBOX | 450/524288 -->
<!-- pin: R36-O3-NEARMISS-1354603465 | 0.20 -->
<!-- pin: R36-O3-NEARMISS-1354603465 | 2,383/2,972 -->
<!-- pin: R36-B2-PHP-AWAKE-PFV4 | 48,036 -->
<!-- pin: R36-B2-PHP-AWAKE-PFV4 | 263,906 -->
<!-- pin: R36-B2-PHP-AWAKE-PFV4 | 6.608 -->
<!-- pin: R32-B2-PHP-MT-RAND | 41,680,896 -->
<!-- pin: R32-B2-PHP-MT-RAND | 0.9658 -->
<!-- pin: R27-CPORT-MT32-FULLSWEEP | 4,294,967,296 -->
<!-- pin: R27-CPORT-MT32-FULLSWEEP | 392,131 -->
<!-- pin: R27-CPORT-MT32-FULLSWEEP | 35563892 -->
<!-- pin: R27-CPORT-MT32-FULLSWEEP | 12.93 -->
<!-- pin: R38-S1-S2-WINDOWS | 163,579,124 -->
<!-- pin: R38-S1-S2-WINDOWS | 3.809 -->
<!-- pin: R38-S1-S2-WINDOWS | 44.138 -->
<!-- pin: R38-S1-S2-WINDOWS | 2,059,308,008 -->
<!-- pin: R38-S1-S2-WINDOWS | 7.3007 -->
<!-- pin: R38-S1-S2-WINDOWS | 7.6707 -->
<!-- pin: R21-L3-PY27-REDUCERS | 884,000 -->
<!-- pin: R21-L3-PY27-REDUCERS | 28.268 -->
<!-- pin: R20-SG3-PY27-RANDOM29 | 0.05723% -->
<!-- pin: R28-L3-PY27-STR-AMD64-DICT | 1,201,672 -->
<!-- pin: R28-L3-PY27-STR-AMD64-DICT | 2,500,207 -->
<!-- pin: R32-B3-GLIBC-GEN0-PRIORDENSE | 96,072 -->
<!-- pin: R32-B3-GLIBC-GEN0-PRIORDENSE | 99.9989% -->
<!-- pin: R26-C-SEMANTIC-SEED-ZOO | 323/323 -->
<!-- pin: R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE | 1,562 -->
<!-- pin: R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE | 991/2,184 -->
<!-- pin: R28-L1-CICADAOS-PADS-DENSE-PAIR | 24,080 -->
<!-- pin: R37-C1-U3-COMPOSED-MAP-ROAD-DIRECTION | 4,176 -->
<!-- pin: R37-C1-U2-LP1-NUMBER-SCHEDULES | 3,072 -->
<!-- pin: R38-C2-G2-PRINTED-LINE-SUMS | 768 -->
<!-- pin: R37-C1-U1-CLUE-STRINGS | 8,832 -->
<!-- pin: R38-C2-G1-CLAUSES-6-7 | 384 -->
<!-- pin: R38-C2-G3-LAGGED-POINTERS | 576 -->
<!-- pin: R37-C2-U7-BOOK-CODE | 240 R/F selections -->
<!-- pin: R38-C1-SEMANTIC-WORDNET | 28224 -->
<!-- pin: R38-I2-X4-NULL | 121 analysed -->
<!-- pin: R38-I1-GLYPH-RECOGNIZER | 29/50 -->
<!-- pin: R38-X1-REDTEAM | 18 remain NEVER -->
<!-- pin: R38-X1-REDTEAM | 34 no-operation -->
<!-- pin: R36-I3-D5C-TWO-MARGIN | SEAL_PASS=false -->
<!-- pin: R35-I3-D5C-LINEAR-RULE | rule retired -->
<!-- pin: R21-L1-SEAL | 36/45 -->
<!-- pin: R22-C-LITERAL-IMPERATIVES | 185 -->
<!-- pin: R37-C3-U6A-N5 | 4,640 -->
<!-- pin: B-04 | 6,224,300 -->
<!-- pin: B-02 | 497025024 -->
<!-- pin: R16-KDF | 3.97 -->
