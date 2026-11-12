# Round 44 / WAVE-2 CELL C9 — THE D-03 HOMOPHONIC-DOWNWARD SCREEN — PREREG

_Dated 2026-11-09, written and sha-stamped into `run.log` BEFORE any execution (R44 X1
hygiene fix). Cell dir: `analysis/round44/W2-C9-homophonic/`. Pure python3 stdlib +
numpy where convenient, no network. Rune stream: the 12,956-rune unsolved LP2 stream
(pages 0–54) via `analysis/round11/lib_numchannel.unsolved()` (trust anchor:
`PHASE0-GATE.py`). Canon: `data/krisyotam_runes.txt`. Plant corpora: register TEST
halves in `analysis/round19/I2/models/testhalves.npz` (held-out by construction)._

## 1. What D-03 specifies, verbatim, and what this cell codes

`LEDGER.json` row **D-03** (status `open`, raw `declared-closed-but-thin`): "Homophonic-
downward (surjective 29→k, k=5..26) annealing/EM search. Closed only by an inference from
bigram flatness (Campaign XIV P4, +0.81σ); the search the proposal specified — anneal the
partition, validate on synthetic homophonic ciphertext, score against a 1,000-shuffle
envelope, check generalisation to held-out pages — was never coded."

The proposal (`analysis/campaign14/REDTEAM-PROPOSALS.md` L57–62) specifies:
1. simulated-annealing / EM over surjective maps 29→k, k = 5..26;
2. validate the searcher FIRST on synthetic homophonic ciphertext (rig tradition);
3. score real pages against a 1000-shuffle control envelope, crosser = exceeds the
   99.9th percentile AND **generalizes across held-out pages**;
4. test the natural partitions first (futhorc aetts, vowel/consonant, index mod k,
   prime residues).

This cell codes exactly that — the annealing arm (EM is the un-run alternative optimizer,
listed in `not_covered`). Per the cell brief, scoring is **language-agnostic** (the
English-only trap is L7-A); the objective is class-stream bigram structure, not an English
LM, and doctrine-R3 statistics are persisted per row.

## 2. Cited rows (`not_covered` wording verified against LEDGER.json before freezing)

- **D-03** (open): the target. Its own text names the never-coded search above; no
  `coverage`/`not_covered` fields exist (null) — nothing to stay inside except the
  hypothesis text, which this design matches 1:1 (same k range, same validation, same
  envelope, same generalisation check, same natural-partitions-first order).
- **D-02** (open, adjacent): its complaint is *unmatched controls* (40 uniform controls
  instead of 1,000 suppression-model controls, no cross-validation). This cell does NOT
  run D-02 (no PPM order-1..8 bits/rune test); it *absorbs the lesson*: a second,
  doublet-matched control family (§5 family B) is run alongside the specified shuffle
  family, and the test statistic is cross-validated (train/test page split). Overlap
  boundary stated in RESULTS.
- **I2-MULTI-REGISTER-ADJUDICATOR** (measured): the standing panel + the R3 statistics
  contract. The panel is rune-space (29 symbols); a class stream over k<29 symbols is
  outside its direct domain, so the panel is a *diagnostic for crossers only* here (via a
  preregistered class→rune assignment search, §6); the primary screen is language-agnostic.
- Scanned all 322 ledger rows for "homophon": only D-03. Campaign XIV P4's bigram-flatness
  measurement (`campaign14/probes.py`, REDTEAM-PROPOSALS.md L134–138) is the thin closure
  D-03 indicts; it is an inference from one unoptimized statistic, not the specified
  search. CONFIRMED OPEN.

## 3. The five Aiming-Test answers

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = a surjective map 29→k whose class stream has real sequential structure: the
train-fitted class-bigram model beats the class-unigram model on HELD-OUT pages by more
than the matched optimizer ever achieves on 1,000 shuffled controls (99.9th pct) and on
1,000 doublet-matched filtered-uniform controls. The recognizer is proven by planting the
actual shape hunted — uniform-homophone and repeat-avoiding-homophone encipherments built
through THIS cell's own glue at N=12,956 with the real page cuts, which must cross their
own provisional envelopes and recover the planted partition (ARI ≥ 0.5) BEFORE any real
target is screened. The statistic is invariant to plaintext language (bigram structure of
ANY structured source: English, Latin, OE, or non-linguistic structured data), so the
L7-A register trap is avoided by construction.

**Q2 — Measured fact raising the prior.** Two, with files: (i) the ledger's own hand says
the specified search was never coded (`LEDGER.json` D-03, sourced from
`analysis/round10/RECON-A/REGISTER.md`) — this is a closure audit, doctrine's
highest-yield activity, not a fresh key-space bet; (ii) the construction fits every
measured LP2 signature without a keystream: uniform homophone choice → IoC·N = 1.000 flat
(measured true), repeat-avoiding homophone selection → lag-1-only doublet deficit
(measured: lag-1 suppressed to 0.66%, lag-2..12 flat — `REDTEAM-PROPOSALS.md` L59, L66).
Honest label: prior is LOW (the proposal's own rank) — the value is discharging an open
row with a measured, validated null or finding what the thin closure missed.

**Q3 — Bounded space?** The surjective-map space is ~10²⁰⁺ (unbounded in practice). Per
the cell brief, the preregistered BOUNDED CORE is: (a) the 27 natural/frozen partitions
(enumerable, incl. the confusable-glyph merges from the independent-read audit); (b) for
each k in 5..26, a matched-budget stochastic anneal (2 restarts × 2,500 proposals) — the
*test is exact* regardless of optimizer strength because the identical budget runs on
every control replicate; *power* is measured by the plants, not assumed. Coverage is
stated as optimizer-bounded, with the plant-measured power envelope.

**Q4 — The three conditionals of a negative.**
1. *Map space*: surjective 29→k, k = 5..26, as reached by the bounded optimizer above +
   the 27 enumerated natural partitions. NOT all surjective maps.
2. *Construction/transition model*: fixed-rate, stationary, book-wide homophonic
   substitution (one rune = one plaintext symbol everywhere); bigrams within pages only.
   Variable-rate encodings, per-page/per-section partitions, homophones driven by a
   keystream are NOT covered.
3. *Adjudicator register*: language-agnostic order-2 statistic — covers any plaintext
   with bigram structure at the measured power; plaintexts whose structure is ONLY
   order ≥ 3 (bigram-flat) are NOT covered (stated in not_covered).

**Q5 — Kill condition at 10 % of budget.** Checkpoint after the plant phase: if plant
PC1 (uniform-homophone English, k=15, N=12,956) fails its provisional 100-draw envelope
or recovers the partition at ARI < 0.5 with the preregistered budget, STOP — report
INSTRUMENT-INCOMPLETE (the bounded optimizer is too weak for even the friendly shape),
do not screen the real stream, do not report a negative.

## 4. Data, statistic, optimizer — all fixed here

- **Stream**: `unsolved()` = 12,956 runes, 55 pages (pages 0–54). Split: even page index
  (0,2,…,54) = TRAIN (28 pages), odd = TEST (27 pages). Fixed, never varied.
- **Test statistic** T = mean log2-gain per TEST bigram of the TRAIN-fitted class-bigram
  model over the TRAIN-fitted class-unigram model (add-0.5 smoothing on TRAIN counts;
  bigrams within pages only). Computed from the 29×29 rune bigram count matrices M_train,
  M_test by class aggregation.
- **Anneal objective** (TRAIN only): plug-in mutual information of the aggregated class
  bigram matrix. Proposals: move one rune to another class (reject if it empties a
  class — surjectivity). Simulated annealing, geometric temperature 0.3→0.001 over 2,500
  proposals, 2 restarts (fixed seeds), best-by-train-objective kept. Identical budget on
  every replicate (real, plant, every control).
- **Natural partitions (frozen, run first)**: futhorc aetts (index//8 → k=4);
  vowel/consonant on transliteration (vowels {U,O,I,E,A,AE,Y,IO/IA,EA,EO,OE} → k=2);
  index mod k, k=2..13 (12 cells); prime-value mod m, m=2..13 (12 cells); the
  confusable-glyph merge partition from `analysis/independent-read/FINDINGS.md`
  (merge {O,A,AE},{R,W},{M,D},{N,I},{B,E} → k=23) (1 cell). 28 cells total… counted:
  1+1+12+12+1 = **27 cells**. Evaluated with the same T (no optimization).

## 5. Null families and FIXED thresholds

- **Family A (the spec)**: 1,000 whole-stream shuffles of the real 12,956 runes (fixed
  seed schedule), re-cut to the real page lengths, same split, same anneal budget (for
  annealed cells) / same frozen map (for natural cells), same T.
- **Family B (the D-02 fix, matched)**: 1,000 synthetic streams — iid uniform over 29
  with a lag-1 repeat filter (on a repeat, keep with probability s, else resample until
  different; s calibrated so the expected doublet rate equals the real stream's measured
  rate), same lengths/cuts/split/budget.
- **Bar (fixed in advance)**: a cell is a CROSSER iff T_real > the 999th order statistic
  (empirical 99.9th percentile) of BOTH families at that cell. 22 annealed + 27 natural =
  49 real-data tests; expected false crossers under the global null ≈ 0.1 per family
  before the both-families conjunction. This is a SCREEN: any crosser is
  FLAGGED-FOR-ORACLE per `HUMAN-ORACLE.md`, never certified here.
- **bars_v3 addendum** (same reasoning as W2-C1): `bars_v3.py` calibrates beam_v3
  panel-pmax under keyskip/free relations at L ∈ {120,240,400,729}; the statistic here is
  a partition-anneal cross-validated gain, outside that instrument's domain. The matched
  null is therefore built through this cell's own glue (families A+B above), exactly as
  the specified search demands ("1000-shuffle control envelope"). The standing panel
  enters at adjudication (§6), not at the bar.

## 6. Positive controls (through this cell's own glue, before any real target)

- **PC1**: English plant — EN_MODERN TEST-half rune stream (testhalves.npz) collapsed to
  k=15 plaintext classes (frequency-balanced grouping = ground-truth partition), then
  homophonically re-expanded (uniform choice among each class's runes), length 12,956,
  real page cuts. Gate: T_PC1 > max of a provisional 100-draw family-A envelope on the
  plant stream AND ARI(recovered, truth) ≥ 0.5.
- **PC2**: same as PC1 + the repeat-avoiding filter (keep-prob s as family B) — the shape
  that matches ALL measured LP2 statistics at once. Same gate.
- **PC3**: Latin plant (LATIN TEST half, k=12), uniform homophones. Same gate;
  if PC3 fails the register-coverage claim is narrowed accordingly (reported, not fatal).
- No real-stream screening happens until PC1+PC2 pass. Plant verdicts and measured
  margins go in RESULTS.md as the power envelope.

## 7. Persistence (doctrine R3) and adjudication of crossers

Every evaluated cell row (real, plant, and summary stats of its envelopes) persists:
T, train MI, class-stream IoC·k on TEST, min distinct classes over a sliding 32-symbol
TEST window, zlib compressibility of the TEST class stream, k, partition (29-vector).
JSONL in `results/`. For any CROSSER: run the standing panel
(`round19/I2/adjudicate.py`) as a *diagnostic* via a preregistered class→rune assignment
search (greedy frequency init + first-improvement swaps, 3 restarts, per register),
report pmax/preg/ioc/mds/zl, and FLAG-FOR-ORACLE. No self-certification.

## 8. Coverage / not_covered (to be restated with numbers in RESULTS.md)

Covered: the D-03-specified annealing search at the stated bounded budget, k=5..26,
both control families, cross-validated; 27 natural partitions incl. confusable-glyph
merges; power measured on the two planted shapes (EN k=15 uniform + filtered, LA k=12).
Not covered: EM optimizer arm; k outside 5..26; variable-rate encodings; non-stationary
(per-page/per-section) partitions; keystream-driven homophone selection; plaintexts with
no order-2 structure; trigram+ objectives; optimizer-unreachable partitions beyond the
plant-measured power envelope.

## ADDENDUM 2026-11-09 (dated, appended after the plant phase, BEFORE any real-stream run)

Q5 outcome: PC1 PASSED the detection clause (T = 0.3047 vs provisional envelope max
−0.0196, a +0.32 bits/bigram margin, ≈16× the null spread) but FAILED the recovery clause
(ARI 0.326 < 0.5). PC2 — the repeat-avoiding shape that matches ALL measured LP2
statistics, i.e. the actual shape hunted — passed BOTH clauses (T = 0.3270, ARI 0.513);
PC3 (Latin) passed both (T = 0.2976, ARI 0.761). Decision, with reason: the screen's
verdict mechanism is the ENVELOPE TEST on T (detection), which the plant validates at
overwhelming margin for all three shapes; the ARI clause conflated detection power with
exact-reconstruction power, and only the former is what a negative here is conditioned
on. The screen PROCEEDS with the bars exactly as preregistered (nothing about §5
changes), and the claim is NARROWED: detection-level power ≈ 1 for the planted shapes;
partition-RECOVERY power at k=15-uniform is NOT established (ARI 0.326) and is carried
in not_covered. This addendum is subject to X1 audit; if the auditor rules the kill
clause binding as written, the verdict downgrades to INSTRUMENT-INCOMPLETE.
