# Round 44, lane A0 — the fresh-eyes audit of Rounds 1-43 and the whole repository

_Run 2026-11-12 at the owner's request ("a full sweep of all 43 rounds and the repo as a whole; see if
anything was left over; a fresh set of eyes to move the ball"). Doctrine: `../../../ARMADA-DOCTRINE.md`
R1 and R6. This lane audits closures, instruments, inputs and the tracking layer. It opened no new key
space. One small pre-registered lane came out of it (`../D1-depth-28-42/`)._

## How it was done

Thirteen readers each took one partition of the record (campaign era x2, Rounds 1-10b, 11-17, 18,
19, 20-24, 25-30, 32-35, 36-38, 39-43, the primary-artifact layer, the ledger and test layer) under
one brief (`readers/BRIEF.md`): report only what is untracked, mis-tracked, wider than its
measurement, or a defect; cite file and line; try to kill each finding before reporting it. Their
full notes are in `readers/`, their exploratory probes in `readers/probes/`.

The coordinator recomputed the foundation statistics from the raw transcription with a loader that
does not import the rig (`lp2.py`, hash-checked against `PROBLEM.json`), then re-verified the
readers' strongest claims in code or by measurement. Every finding below carries a status:

- **[V]** verified by the coordinator, with a script in this folder.
- **[R]** reported by a reader with citations and (usually) a probe; not independently re-run.

Nothing here is a solve. Pages 0-54 are not decrypted.

---

## 1. Seven findings that change what should be done next

### 1.1 The cleartext says the plaintext is English spelled one rune per letter [V]

Word boundaries pass through the cipher, and the shape of the word-length histogram has never been
used (only its mean was, and that closure was contaminated, see 3.6). LP2 has 2,928 words, mean
4.425 runes, 99 one-rune words; by length 1..8: 3.4, 15.9, 24.8, 17.6, 10.9, 8.6, 7.3, 5.4 %.

- Against 61 committed English texts, each spelled both ways, the **letter-wise** spelling (THE = 3
  runes) fits LP2 better than the solved pages' multigraph spelling (THE = 2 runes) in 60 of 61 texts
  by KS and 61 of 61 by chi-square. Best letter-wise fit: KS 0.0075, chi2 21.1 on 11 df (below the
  0.0251 critical value: statistically indistinguishable). Best multigraph fit of any text: KS 0.0586,
  chi2 117. (`wordlen.py`, `wordlen.json`)
- The discriminator is the two-rune class: 15.9 % in LP2; 15-22 % for letter-wise English; 21-32 %
  for multigraph English; 24.3 % on the author's own solved pages (z = 4.9, reader B). Reader I, over
  82 texts and 21,698 LP2-sized windows, found only 2 windows that low under the solved-page spelling.
- One-rune words are 3.4 % (English: A and I). Latin gives 0.6 %, Welsh 19.5 % (reader I).

Consequences, in order of weight:

1. **The plaintext is English.** The register axis that Round 18 opened (Latin, Welsh, Greek, Hebrew,
   Norse) is answered by the cleartext for the purposes of prioritising; panel breadth costs bar
   height and buys little.
2. **The unsolved pages were prepared differently from the solved ones.** The same release spells
   THE with two runes on pages 56-57. A script that maps Latin letters to runes one at a time would
   produce exactly this, which sits well with the machine-applied filter (ledger D-01).
3. **The instrument is not blind to it.** Measured, correct key handed in, through the oracle's own
   encipherer: letter-wise plants score pmax 13.5-18.8 at L=120 and 20.5-26.7 at L=240 (24/24 clear
   each; recovery 0.999), against 15.8-20.6 and 23.2-29.1 for the multigraph control
   (`instrument_power_letterwise.py`). **No sweep negative is retro-invalidated.**
4. A correct decode would use at most 22 of the 29 runes (the seven digraph runes never appear).
   That is a language-free recognizer. R3 already persists `mds`, but only for rows that survive a
   language-model screen.
5. The Round 8 skeleton scan, Round 9's length closure and Campaign XVIII item 2b all used folded
   lengths, so they are conditional on the wrong orthography. Ledger row `B-19` has been open with
   null fields since Round 10 and is in no tracking document.

### 1.2 The oracle returned FAIL on a correct continuous key [V] — fixed in this commit

`verify_solution.py` decoded every page from `K[0]` (key restarts at each page) and its self-test
planted only that. Every seeded-generator sweep assumes the opposite: one stream from rune 0 of page
0. A correct key of the swept kind cleared page 0, failed page 1, and got `VERDICT: FAIL` because two
pages are required. Two readers found this independently (H, L) and each demonstrated it with a plant.

Fix: `judge_continuous()` decodes page 1 from where the stream had reached, over a window of key
offsets, with the bar taken at N = window size; the self-test now plants both page models in four
registers and prints that the old judge alone fails the continuous plant;
`tests/test_verify_solution.py` gained `test_continuous_key_passes_where_restart_judge_fails`.
Self-test: 8/8 plants recovered, 8/8 wrong keys rejected.

### 1.3 Natural-language running keys are excluded at the family level, key-free [V]

For C = P +- K with P and K both English, the ciphertext monogram distribution is the convolution of
two English distributions. Predicted monogram chi2 at N = 12,956: **772** (letter-wise) or **604**
(multigraph), against **26.4** observed on 28 df. This holds at any offset, any skip relation, either
sign. The key's own monogram distribution has to be uniform to within about a 15 % admixture
(`running_key_gate.py`). Round 43 F3 recorded the same gate (`TOOLKIT.md:86,105,123`) and then ranked
natural-language keys at the top of its localisation table; it never reached X0 or the ledger
(readers J, L).

This discharges, without a decode: ledger `R12-C2`, the remainder of `R26-B-KEYTEXT-RUNNINGKEY-
SKIPAWARE`, and the Round 42 "10-keytext refetch". **Drop them from the queue.**

### 1.4 The one long repeat is mis-recorded three ways, and it is not a 13 % event [V]

The only repeat of six or more runes in the unsolved stream is the two-word phrase **ᛞᛄᚢ-ᛒᛖᛁ**
(D J U - B E I): page 27 runes 28-33 and page 54 runes 70-75. The second site is **the last two
words of the unsolved book**, closing a sentence, a paragraph mark and a section mark. The first site
is 28 runes into the section that begins on page 27. Both have the same 3+3 word division.

- `ARMADA-20-FINDINGS.md:81` calls it chance, "Poisson P ~ 13 %". That is the chance of *any*
  repeated 6-gram and ignores the word alignment.
- `round43/F3-hand-feasibility/KEY-LOCALIZATION.md:107` calls it "the 7-gram ᛉᛚᛒᚱᛋᚳᛋ ... p ~ 0.5 %".
  That rune string occurs **zero** times in the data. The "7th rune" is the first rune of the solved
  page AN END, which happens to equal the rune after site 1 (both AE); F3 counted 13,041 runes with
  AN END included. The same file's "3.51 runes/word, 536 one-rune words" comes from treating line
  wraps as word breaks (true: 4.425 and 99). X0, X1 and the Round 44 plan repeat "7-gram".
- Calibrated with the cleartext skeleton fixed and runes uniform (`repeats.py`): expected count of any
  repeated 6-gram 0.141; of one with an identical boundary pattern 0.0059; of a **closed whole-word
  repeat of six or more runes 9.2e-5** (Monte Carlo: 0 of 3,000). It is the only repeated closed word
  sequence of four or more runes among 2,928 words.

So it is a 1e-4 to 6e-3 anomaly depending on how generously the statistic is chosen after the fact,
not noise-level and not a free crib either: the two sites sit at different offsets from every visible
boundary (page 28 vs 70, line 8 vs 2, section 28 vs 3310, sentence 9 vs about 290), so **no reset at a
visible boundary makes them the same key position**, and the rigid lag-6395 coincidence count is
unremarkable (z = -1.84). Round 44 lane R1 was about to anchor on it as "a free alignment anchor".
It anchors nothing as specified. A fresh keystream that never repeats cannot produce it except by
chance; any generator hypothesis that reaches both sites can be checked against it for free.

### 1.5 Pages 28 and 42 are related position by position, and plain depth is now excluded [V]

Reader K ran the classical depth test with a length-normalised statistic for the first time (earlier
runs used an un-normalised IoC threshold or kappa only). Recomputed in `depth_pairs.py`:

- `D_i = (p28_i - p42_i) mod 29` over 269 runes: chi2 **74.1** on 28 df (p = 4.8e-6), the top of 1,326
  aligned page pairs (next: 59.2). The chi-square splits 65.2 symmetric / 8.9 antisymmetric, which is
  what a difference of two draws from one distribution looks like; the mean over all pairs is 14.1 /
  13.9. Offsets +-1..4 are flat. The excess is present in every 45-rune block. kappa = 21/269.
- Family-wise on the statistic fixed in advance: about 0.006. The reader scanned 331,908 pair x offset
  cells in the same batch, where 1.6 cells this extreme are expected on the unfolded statistic, so
  this is suggestive, not established.
- The two pages have different word skeletons, so different plaintexts.

The natural reading (same key on both pages, two English plaintexts) was tested the same day under a
pre-registration, with a joint two-plaintext decoder that recovers 70-94 % of planted pairs:
**negative in all three encodings, real pair indistinguishable from 40 nulls** (`../D1-depth-28-42/
RESULTS.md`). The histogram itself is also too structured for English depth under any standard
numbering (monogram-level LLR +1.5 nats against +6.9 expected for Gematria-order text).

Status: an unexplained measured anomaly with its obvious explanation removed. If it is real it
contradicts "13k fresh key values, never rewound" (`round43/F3`, `ELIMINATION-LEDGER.md:131`).

### 1.6 The loader several lanes used drops the book's head and tail [V] — fixed in this commit

`src/lp/corpus.py parse()` reads `data/scream314_lp.md`. It is the right loader for the solved pages
and the wrong one for LP2, in three ways (`loader_map.py`):

1. It took the note "Outguessing the image yields 58,2kB garbage output" for a plaintext, so three
   unsolved sections were flagged **solved**: canonical pages 0-2, the first 119 runes of page 3, and
   pages 53-54. Only 11,107 of the 12,956 unsolved runes were flagged unsolved.
2. It keeps the first rune block of each section only (15,241 of the file's 15,938 runes).
3. Its sections are not pages: index 19 is canonical page 6 rune 71 to page 7 rune 207.

Lanes built on it:

- `round26/A/sweep.py:129-131` decoded the Perl, TeX and Py2.7-reducer keystreams against section 19
  at key offset 0, a mid-book slice. `MEASURED-CEILING.md:64` records "347 prior-dense seeds fully
  swept". That sweep has no power for a stream that starts at the book head (reader G).
- `round26/B/sweep.py:48-53`: the keytext lane's "pages 19, 26, 28" are section indices, 545 runes in
  all; pages 0-5 and 53-54 were never targets; four offsets per text; ten of 33 files are HTML
  (reader G). Moot after 1.3, but X0's CITED stamp for "running key plus skip" rested on it.
- `r6_sieve_windows.py:61`, `round38/C2-never-cells/cells/run_cells.py:186`,
  `round10/L3-road/t6_source_control.py:36`.

Fix: OutGuess notes are classified as notes (`_is_stego_note`), the module docstring now says what
the loader is for, `tests/validate.py` still passes. The first-block-only behaviour is left as is
(the solved-page gate depends on it) and documented.

### 1.7 Every decode in the repository shares premises that one instrument could retire [V/R]

Readers working on different rounds converged on the same list of things no decoder represents. Each
was confirmed by handing the repo's own instrument a correct key (probes in `readers/probes/`):

| premise never tested | what a correct key does today | bound or note | readers |
|---|---|---|---|
| combiner is C = P + K with no constant | C = P+K+1, Beaufort, Atbash-then-add all score as noise (recovery 0.00-0.06) | Atbash and +3 are house style on solved pages; the Round 19 G1 plan had 48 combiner cells and one was swept | H, E, A1, C |
| draw t meets rune t, from rune 0 of page 0 | a key burned at word boundaries, a warm-up, or a start at a section head is noise | only `C[:24]` of page 0 ever screens a seed; the 8 section heads and 54 other page heads are unused | H, I, G, A2 |
| the key pointer never stalls | an F left in clear (the solved-page interrupter) desyncs every relation | LP2's F count (458 vs 446.8 +- 20.8 expected) bounds clear-F interrupters at about 47 book-wide; F sits at head positions 7 and 17 | E, A1, I, K, C, H |
| the rejected draw is tied to the current rune | a writer who *drops* the second rune of a would-be doublet: recovery >= 0.90 in 0/10 at L=120 under keyskip1/2; `free` gets 10/10 | every mass sweep's confirm stage is keyskip1+2 only | F |
| rejection consumes key | a value rewrite with no key draw has no measured power through pf_v4 / beam_v3 | Round 18 L2 said sweeps must cover both; the ceiling page never mentions it | D |
| the soft-filter coin is a separate RNG | in a one-generator script each kept doublet also costs a draw; L=120 heads of page 0 are safe (first doublets at 122 and 207), L=240 confirmation is not | 0.83 is fitted, never derived; RANDOM%5, RANDOM%6 and 24/29 all fit 86 | G, D, H, C, E |
| plaintext symbols are numbered in Gematria order | any relabelling of the plaintext is noise to a language model | a script that maps letters to numbers need not use Gematria order | A1, K |

**The unifying observation (coordinator; reader A1 reached it independently).** Under key-skip, a
rejection at cipher position i with key pointer j is only *possible* if
`K[j+1] - K[j] = C[i] - C[i-1] (mod 29)`. Skip sites are fixed by the key and the ciphertext alone, at
about one admissible site per 16 runes, half of them real. So a decoder needs no language model to
track the key: it can branch at admissible sites and score each path by a statistic that does not
care how the plaintext is labelled (index of coincidence, distinct-symbol count). Such a **blind
adjudicator** is invariant to language, orthography, plaintext numbering, a constant in the combiner,
Atbash and Beaufort, all at once, and its null is directly measurable.

**Measured on plants** (`blind_adjudicator_poc.py`, encipherer = the Campaign XVIII implementation,
decoder shares no code with it): at L = 120 the best-path IoC x 29 over 400 wrong keys is 1.14 +- 0.06
(max 1.41); **480 of 480 plants score above that maximum** (plant minimum 1.43, medians 1.71-2.16),
across English letter-wise, English multigraph and Latin, each as written, under a random relabelling
of the plaintext, with a +7 constant in the combiner, and as Beaufort. At L = 160: 479 of 480 above a
null maximum of 1.30. At L = 64 it is a usable first-stage screen only (z of the median +4 to +8). The
existing instrument returns noise for three of those four variants. This is the instrument lane the
Round 44 plan lacks; section 5 specifies how to use it.

---

## 2. Finite, high-prior key spaces that were never swept at power [R, partly V]

The doctrine ranks enumerable generator spaces second. Four are sitting unswept or mis-swept:

1. **The clock-second band.** `srand(time)` is the commonest seeding idiom there is. Under the
   repaired instrument, only bash 3.2 and Py2.7 integer seeds cover every second of 2012-2014. glibc
   (Round 18 L1's rank 1) has midnights and top-of-hour seconds only; PHP, Perl and TeX have a 1 %
   draw or less. Round 8's per-second sweep of ten generators used a rigid 48-rune English kernel,
   whose power against a key-skip seed is about 0.44 by arithmetic, and ledger row `R19-G1` says not
   to re-sweep the window. A six-month window is 1.6e7 seeds per generator. (readers B, L, D)
2. **Perl `rand`, all of it.** Perl is the only generator with signed first-party evidence: two
   signed messages (2012-01-15, 2014-01-06) carry `Crypt::RSA` armor and `Data::Dumper` output
   (`round19/C3/RESULTS.md` section 2c', [V] read). Its seed space is exactly 2^32 including the
   unseeded case. About 25,000 seeds have ever been decoded, and the one prior-dense run was aimed
   at the wrong page (1.6). `PICKUP-HERE.md` still files it as "sieve-gated, flat prior"; the sieve
   has existed since Round 35. (readers E, D, F)
3. **bash 4.2, the whole state cycle.** `round19/G1/RESULTS.md:29` [V] measured that seed and offset
   are the same thing: every seed is a point on one cycle of 2,147,483,646 states (LP64), and on
   ILP32 the cycle is only 343,896 long. The "full orbit" swept since is 77.6M seeds per ABI, 3.6 %
   of the LP64 cycle, and the offset ladder (offsets 0-28 at 77.6M each) costs more than one pass over
   the whole cycle, which would close every seed, every explicit `RANDOM=`, every date and every
   offset at once. (reader E)
4. **TeX default seeds.** pgf's `\time x \year` gives 8,627 seeds; the only run is a pilot marked
   `interpretable: false`. (reader E)

Two measured facts are missing from the seed prior: the onion-7 index page's
`Last-Modified: Wed, 02 Apr 2014 08:33:19 GMT` (1396427599) and the Jan-11 status page's
`Sat, 11 Jan 2014 22:07:12 GMT` (1389478032). Round 43 F5b recorded both
(`round43/F5-stored/RESULTS-irc.md:63,83`); neither integer occurs anywhere else in the repository
[V, grep], and ledger row `G-09` reopens on exactly this (reader L).

Also reported: `grb5_rej` is the Python >= 3.2 `randrange` stream for integer seeds and is queued as
a "Py2.7 completeness ritual" with about 0.005 % skip-aware coverage (reader G); there is no awk row
at all, though unseeded gawk `rand()` is one fixed stream (reader D).

---

## 3. Negatives that do not mean what their rows say

| # | claim on file | what was actually measured | status | reader |
|---|---|---|---|---|
| 3.1 | Round 42 C1-C3 and Round 43 F6 / F5b-T object-as-key rows read `negative`, control `passed` | a **rigid** position-wise decode judged against the **free-beam** bar, with no filter-shaped plant. With the repo's own constructions a correct key under key-skip scores pmax 3.9 at L=265 (0 of 12 plants over the bar); `round42/CAMPAIGN-PLAN.md:37-38` had specified beam_v3. `R28-L2` payload-as-key carries the same conditional, and Round 44 lane P4 plans to reuse that harness verbatim | [V] code read (`round42/C1-keytexts/run_c1.py:40-58`); plant numbers [R] | J, L |
| 3.2 | Round 11 number-channel rows say "legacy skip beam" | Round 11 used no beam and unfiltered plants. The only repaired-instrument run of the totient/prime streams has three aligned starts, two of which (flat 4800, 9600) are vacuous under key-skip drift. The solved page 56 method, generalised with the anti-repeat rule, is covered on 3 of 55 page starts | [R] | C |
| 3.3 | "Filter acts on the ciphertext, power 1.000" (Round 18 L2); "OTP-class" (Round 10b B4) | true inside the family `(p + k) mod 29` with an independent uniform key. All seven loci and all eight mechanisms tested are of that form; B4's battery is six first-order or lag-1 statistics comparing two additive-plus-filter models. Neither is a measurement against a non-additive or keyed-alphabet cipher | [R], consistent with [V] foundation recompute | D, B, C |
| 3.4 | "Keystream is continuous across the whole book" (`STRUCTURE-FINDINGS.md:17-35`, copied into `dataset/build_dataset.py:108` and the dossier) | 0 doublets at 54 page joins. With no suppression at joins that has probability 0.155; with suppression it shows filter memory, not key continuity. This is where the offset-0 premise comes from | [V] (0 of 54; expected 1.9) | A2, K, I, B |
| 3.5 | Same-key resets at page, line, sentence and word are "open" and head Round 44's R1 | already excluded key-free by depth columns: page columns 0-9 give z = +0.76 against +13 to +16 planted; line columns +0.9 against +95. Only resets to a *different* key state survive, which means "screen every page and section head", not "reset" | [V] `reset_columns.py`: page heads kappa x 29 = 1.033 (z +0.76; same key would give about +21), section heads 1.010, sentence heads 0.993, line columns 0.999; found by four readers independently | C, D, F, H |
| 3.6 | Round 9's word-length closure, "do not re-open" (`research/DEAD_ENDS.md:448-465`) | `analysis/skeleton/length_anomaly.py:106,125-126` never strips the Project Gutenberg licence; 22 of 22 Gutenberg files peak at the file tail; stripped, Dante falls from 4.771 to 3.973 | [R], reproduced by the reader on 34 texts | B |
| 3.7 | Long-period periodic keys killed "by doublet floor" (`round24/PLAN.md:83-93`) | that argument was retracted (`README.md` D1 note): the filter makes the deficit key-type-agnostic. No ledger row covers periodic key plus filter. Measured here instead: rigid all-lag scan flat (12,454 lags, sd 1.01, max 4.22 = chance); drift-smeared matched filter flat (max 3.37). Three readers built their own drift-aware detectors with plants: periods up to about 1,000-1,500 excluded at power, nothing above | [V] `foundation.py`; plant power [R] | A1, B, F |
| 3.8 | Round 10 L9 linear-complexity negative "eliminates finite-state generators" | its own gate shows an LCG mod 29 and a filtered LFSR both read n/2; it was run on ciphertext | [R] | B |
| 3.9 | "Autokey refuted by simulation" (`ELIMINATION-LEDGER.md:129`) | the simulation covers one offset. The valid refutation is the flat difference structure (lag-L difference and sum spectra flat for L = 2..400), which excludes ciphertext-autokey with any primer up to 400 in any language | [R] | A1 |
| 3.10 | Round 20's "a 24-32-rune head cannot carry enough signal" (`R20-P1-SIEVE-INFEASIBLE`, `superseded_by` empty) | pf_v4_12 later reached 0.952-0.994 on a 24-rune head. The cause was the rigid stage A | [R] | F |
| 3.11 | "17 CITED, zero letter-stream items missed" (Round 43 X0) | at least four of the 17 cite rows that are rigid, single-offset or mis-targeted (items 1, 7, 10, 12), and X1 delivered three of seven planned audits (F2, F3, F5, F6 were never red-teamed) | [R] | J |

---

## 4. Corrections to the Round 44 plan

| lane | as planned | correction | status |
|---|---|---|---|
| **P2** p15 grid as key schedule | "14/16 cells = 3301 - prime; red 3299 = F" | **all 16 cells equal `|3301 - p_F|`**, p_0 = 2, F over the Fibonacci numbers 0..987. The grid has no free information; the red cell marks the origin. It was also already run as a Hill key (`round41/C1-r14-r15`, `M3_4x4`) | [V] `p15_grid.py`; prior run [R] J, K |
| **P5** hash-block 20-byte-stride parse | three signed 991-byte blobs as an open object | they are XOR shares of the solved 2014 transposition message, byte-exact against `pgp/messages/2014-01-signed-ciphertext.asc`. The parse is moot | [V] `xor_shares.py` (found by reader K) |
| **P5** cuneiform clusters | "NEW" | read as 17, 13, 55, 1 and run as keys in the recovered `campaign7/c2_cuneiform.py`; `Larger cuneiform numbers.pdf` is held and unread | [R] K |
| **R1** per-page / per-line resets with the "7-gram" anchor | anchor on p27 / p54 | the anchor is a 6-rune two-word repeat at incompatible offsets (1.4); identical resets are already dead (3.5). Re-scope R1 to "screen every section and page head as a possible stream start" | [V] / [R] |
| **P4** onion blobs as per-page pads | "reuse the R28-L2 harness verbatim" | that harness is rigid and English-only with an unfiltered plant (3.1). Use a skip-aware one | [R] L, J |
| **P1** red-ink channel | inherits the Round 22 drop-cap catalog | that catalog joins image pages to transcription entries by raw index (off by one after page 49) and assumes the drop cap is the first rune of the page; about half its entries are wrong. The string `SLXHXFUMDSFAINGP` in `LEDGER.json` is unreliable | [R] F |
| P1, P3, R1, P4 | `%` segments are pages | they are not image pages: solver page 15 is 9+150 runes and page 33 is 91+123; `dataset/liber_primus.json` is wrong for pages 50-56 (image 50 is runeless) | [R] J, A2 |
| deferred: 10-keytext refetch, B2 remainder behind "running key" | queued | drop the keytext items (1.3) | [V] |
| owner decision: N5/N4 bundle read | pending since Round 38 | moot. Both keys are pointwise functions of the ciphertext rune, so the "decode" is a fixed many-to-one relabelling; a rigid relabel reproduces both bundle decodes 240/240. Noise by construction | [V] code read (`round38/C2-never-cells/n5n4/run_b.py:44-60`, `round11/N5/n5.py:128-147`: the keys are built from the ciphertext runes' own primes); the 240/240 reproduction is [R] I |
| owner decision: WATCH band | pending | five S2 seeds above 7.10 survive locally in `round42/S1-s2-recovery/state_recovered/candidates_summary.json`; the decision costs five decodes | [R] J |

---

## 5. Proposed queue, ranked by (chance it changes the picture) x (cheapness)

**Instrument first (doctrine R1).**

- **I1. The blind adjudicator.** A C kernel that walks a candidate keystream against `C[:L]` of a
  stream start, branches only at admissible skip sites (keyskip1: `s*(K[j+1]-K[j]) = dC[i]`;
  keyskip2: `s*(K[j+2]-K[j]) = dC[i]`; both signs s), and scores each path by IoC. Stage 1 at L = 64,
  stage 2 at L = 160, stage 3 the full page with a human read. Plant it in English (both spellings),
  one non-English register, a random relabelling of the plaintext, C = P+K+c, Beaufort and
  Atbash-then-add; measure the per-stage pass rate and the null from random keys before any real seed
  is touched. Estimated cost 2-4 microseconds per seed for all four modes, so a 2^32 space is about
  an hour on four cores. It retires rows 1, 2 (constant and reflection) and 7 of the table in 1.7 and
  the register conditional in one stroke, and it is the first adjudicator here whose null is exact.
- **I2. Power envelopes that do not exist:** value rewrite (M2), deletion-type avoidance, the F-stall,
  the in-stream coin at L=240. Each is a plant through pf_v4_12 and beam_v3 and a table. Hours.
- **I3. One shared skip-aware harness for object-as-key cells,** then re-run the five rows of 3.1 and
  R28-L2 through it. Hours.

**Then the finite spaces of section 2,** in this order: Perl 2^32; the clock-second band for glibc,
Perl and PHP with the two server timestamps at the centre of the prior; the bash 4.2 cycle (ILP32
first, it is 343,896 states); TeX's 8,627. Each through both the existing instrument and I1, each at
every section head as well as page 0 (R1 re-scoped).

**Then the cleartext, which has barely been used as data.**

- **C1.** Re-run the skeleton scan with letter-wise lengths, locally (sentence and quote-span sized
  windows, not whole-text correlation), against the largest corpus that can be assembled. Round 43 F2b
  already mapped seven quote spans (405 runes); reader J saved the positions
  (`readers/probes/J_token_channels.json`). A quotation identified by its word lengths is known
  plaintext, and known plaintext is key.
- **C2.** The structure the transcription already carries: eight `$` sections with title-like first
  sentences (lengths 8+5; 2+11+3; ...), 17 paragraph marks, the numbered list 1-5 on pages 36-38, the
  literal 7 on page 10. None of it is in any lane.
- **C3.** Image crops of both DJU-BEI sites and of pages 28 and 42 for a human look.

**Then the physical-page lanes of the existing plan, as corrected in section 4.**

Not recommended: more key space under the current page-0, constant-free, Gematria-order premises
before I1 exists; any keytext lane (1.3); P2 and the hash-block half of P5 as written.

---

## 6. Tracking layer and housekeeping

- **CI was red at HEAD** for two reasons unrelated to this audit: `PROBLEM.json` drifted from the
  ledger (299-row counts) and `check_consistency.py` failed on `PAPER.md`. Both are repaired in this
  commit (reader L).
- The ledger no longer held the current state: no rows for Round 43 F1, F2, F3, F5a, F5b or X0, none
  for the Round 44 queue, and at least ten stale rows (`A-02` and `B-13` still partially-run though
  Round 19 settled 450/450; `C-01` "never extended" though Round 10 ran 224 texts; `G-09` "no seed
  ever run" though eight lanes consumed the 433; `R20-P1` not superseded; `R25` "over 99 % unswept";
  `C-CANON-PAYLOAD-3BYTES` "promotion pending" though commit 26c4446 overwrote `canon_256.bin`). This
  commit adds rows for the audit's own measurements and leaves the stale rows listed here for the
  coordinator of the next round (readers L, B, G, D).
- `MEASURED-CEILING.md` is stale against Rounds 41-43 at lines 53, 58, 107 and 114 (47.95 % for the
  Py2.7 exact relation, bash 3.2 "unverified", R14/R15 "not run", p27:93 "unresolved").
  `check_ceiling.py` passes because it checks citations, not currency (reader L).
- Hand versus machine is held three ways at once: `README.md` says machine at >= 0.99 power; ledger
  `D-01` excludes only human-supplied randomness; Round 43 F3 rests on a 19 % human lapse rate and on
  a hand-drawn book, against the typeset Ghostscript render and identical glyph bitmaps (readers E, L).
- Round 31 has no folder, row or document. Its only trace is `._round31_stale_backup/` in the owner's
  home directory, which Round 35 P1 says may hold the lost Welsh corpus and Round 36's audit says to
  delete. Owner only (reader G).
- Unexamined inputs, each minutes to an hour: the 56.jpg and 57.jpg masters that Round 43 F5a
  recovered have had no stego or forensic pass, and the other 13 Jan-2014 carriers were not fetched;
  OutGuess's second-message channel (`-e`) was never tried anywhere; blob T2 is very likely a
  no-payload OutGuess artifact (header seed 38370 against real seeds 94-163) and is still carried as
  live by four rounds; the stego verdict's own "decisive next experiment" on pages 0/4/26 was never
  run (ledger `B-10` was marked superseded by a row that attacked different images); the 6.65 MB
  signer-attested audio decode is in-tree and never reduced; `R28-L3` is inconclusive only because two
  files were "absent from this checkout", a class of claim Round 41 X1-B proved clone-scoped
  (readers G, A2, K).
- The solved cipher pages show normal doublet rates (27 in 919 runes against 31.6 expected), so the
  filter is specific to pages 0-54, and LP2 does not follow the solved pages' interrupter rule: every
  plaintext F is clear on solved pages (10 of 10), which would predict about 653 F in LP2 against 458
  (reader K).

---

## 7. What was checked and found sound

The foundation statistics reproduce from an independent parse: 12,956 runes with the pinned hash;
86 doublets in 12,901 within-page pairs (0.667 %), none across a page join, none tripled; monogram
chi2 26.4 on 28 df; off-diagonal bigram chi2 z = +0.71; every lag from 2 to 12,454 flat. The doublets
are uniform by boundary class (keep ratio 0.18 inside words, 0.24 across word boundaries, 0.18 at
sentence ends), by page (chi2 58.5 on 54 df), by section (0.15-0.31), by position residue (no block
structure mod 2..40) and against prime positions; twelve of them are at word-initial pairs, so they
are not plaintext double letters. There is no vertical or diagonal avoidance. The line-initial rune
skew (chi2 81.4) is the glyph-width size bias Round 18 L4 already measured. (`foundation.py`)

Readers also found sound, at stated scope: the beam_v3 transition algebra and its independent plants;
the Round 27 full-2^32 histogram and its crosser adjudication; the Round 36 near-miss and KDF-crosser
adjudications; the transcription audits (0.9973 per-slot agreement, indel bound of one each way); the
payload canon; the PGP table; the keyless polygraphic, fractionation, transposition-only and
differencing exclusions; the Round 32 X1 corrections (all propagated but one line of
`KNOWLEDGE.json`).

---

## 8. Reproduce

```bash
cd liber-primus/analysis/round44/A0-fresh-eyes-audit
python3 lp2.py                 # the loader: 12,956 runes, 2,928 words, hash-checked
python3 foundation.py          # section 7, 3.7                -> foundation.json
python3 repeats.py             # 1.4                           -> repeats.json
python3 running_key_gate.py    # 1.3                           -> running_key_gate.json
python3 wordlen.py             # 1.1                           -> wordlen.json
python3 instrument_power_letterwise.py   # 1.1 item 3 (needs data/panels)
python3 depth_pairs.py         # 1.5                           -> depth_pairs.json
python3 reset_columns.py       # 3.5                           -> reset_columns.json
python3 blind_adjudicator_poc.py   # 1.7: the language-model-free adjudicator on plants -> blind_adjudicator_poc.json
python3 p15_grid.py            # section 4, P2
python3 xor_shares.py          # section 4, P5
python3 loader_map.py          # 1.6
cd ../D1-depth-28-42 && python3 run_d1.py   # the pre-registered depth lane
cd ../../.. && python3 verify_solution.py --selftest   # 1.2
```
