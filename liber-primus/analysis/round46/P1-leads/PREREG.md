# R46-P1 — Pre-registered tests of the two Round-45 leads — PREREG

_Dated 2026-11-24. Written before any P1 script was run or any P1 output existed. The sha256 of this file
(as frozen at first run) is written as the first line of `run.log`. Any later change is an appended,
dated, hash-stamped addendum; no threshold below is edited after a result is seen._

## 0. Honesty statement: what was already seen, and what is confirmatory here

Both leads were **found on LP2** post-hoc (R45-W1 `q2b_posthoc.json`, R45-X1 `AUDIT.md` §1):

- (i) 2-rune printed words are 15.5 % of LP2's 2,896 words; all 480 R45 English windows (8 corpora:
  kjv, moby, pride, war, king_in_yellow, mabinogion, self_reliance, book_of_the_law) were >= 19.7 %;
  solved Cicada printed words 24.1 %.
- (ii) 420 / 593 LP2 line breaks fall inside printed words (71 %; chance ~78 %); LP1 78 / 146 (53 %;
  chance ~75 %).
- Also already seen: splitting every line-spanning LP2 word at the line break gives 3,316 words, 2-rune
  share 18.7 %, mean 3.91 (X1 table).

LP2's own numbers cannot be "re-discovered". **Nothing here re-tests the existence of the LP2 values.**
What can be genuinely confirmatory, and is the only thing this lane claims as such:

1. **Fresh reference corpora (lead i).** Whether the English reference range that made 15.5 % look
   extreme survives on corpora R45 never used: archaic English, translated English, other original
   registers and verse (panel FE, §2), none of the 8 R45 corpora nor any KJV subset. If English in some
   register routinely reaches 15.5 %, lead (i) was an artefact of R45's reference choice.
2. **Split-half / held-out-chapter replication inside LP2 (both leads).** Whether the effect is carried by
   the whole text or by one part. Not independent of the original observation (same object), but it is
   a homogeneity test whose outcome was not seen.
3. **Explanation discrimination (both leads).** Tests whose LP2 outcome has not been computed: the
   length-profile goodness-of-fit against each competing generator (T3), the line-merge ceiling against
   fresh English (T4), the line-length signature of word-aware wrapping (U2), and the dropped-separator
   mixture fit (U3).

## 1. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?** For (i): LP2's 2-rune share
below the 1st percentile of a fresh English window panel, with a planted deficit of LP2's size detected
at power >= 0.8 and a leave-one-corpus-out size <= 0.03. For the explanations: LP2's 9-class length
profile admitted by a generator's own window null, with a confusion matrix showing which generators the
test can tell apart. For (ii): LP2's word-boundary preference below LP1's in every held-out part, with a
simulated typesetting plant at LP2's preference detected at power >= 0.8. All recognisers are planted in
§4 before LP2 is read.

**Q2 — What measured fact raises the prior?** `analysis/round45/W1-spaces/q2b_posthoc.json`
(2-rune class 15.5 % vs English min 19.7 %), `analysis/round45/W1-spaces/RESULTS.md` Q2 (multiset is
English-shaped but sits at the top of the mean-length range), `analysis/round45/X1-redteam/AUDIT.md` §1
(line breaks 71 % vs 53 %). Two post-hoc cells; this lane exists to price them.

**Q3 — Is the space bounded?** Yes, enumerable and finite: 2,896 printed lengths, ~593 LP2 line breaks,
~146 LP1 line breaks, a fixed list of 30 fresh English corpora + 4 non-English corpora already in-repo,
and a fixed set of 9 generator references. No key space; no network.

**Q4 — The three conditionals every negative here carries.**
1. *Key space:* none — no decode is run. Every statement is about printed word lengths and line layout.
2. *Decoder transition model / generator model:* the represented length generators are exactly T3's
   list (§3) and the represented layout models are exactly U1–U3's (blind fixed-width cut; word-aware
   mixture wrap with slack 6; blind cut with line-final separator drops). Not represented: hyphenation
   rules, glyph-width-aware justification, keyed or plaintext-driven layouts, "lengths borrowed from a
   specific other text" (unidentifiable from a multiset — see §3).
3. *Adjudicator register:* English GP under rule R-A (30 fresh corpora in 4 groups); Latin, German,
   Welsh, Old English under the §2 fold; solved-Cicada printed lengths. Greek / Hebrew / Norse (R36)
   corpora are not on disk and are **not covered**.

**Q5 — Kill at 10 %.** First checkpoint (`p1_lead_i.py` stage 1, before LP2 is compared): (a) if
>= 5 % of pooled FE windows have 2-rune share <= 0.155, lead (i) is dead as an "extreme" claim, stated
as such; (b) if the leave-one-corpus-out size > 0.03 or the LP2-size plant power < 0.8, T1 is
**uninformative** and is reported so. For (ii): if LP1 itself does not show π > 0 under the §3
definitions (sanity), the definitions are wrong and lead (ii) stops.

## 2. Data, parsing, transliteration (frozen)

- LP2 = first 12,956 runes of `data/krisyotam_runes.txt`; LP1 = `data/sources/rtkd_master.txt` before
  the LP2 start; solved Cicada = LP1 + AN END/PARABLE printed words (739). Word parsing is R45-W1's
  `w1lib.parse` (imported read-only): `- . & $ §` and digits break words; `/` and `%` do not.
- Words in corpora: R45 regex `[A-Za-z]+(?:'[A-Za-z]+)*`, apostrophes removed, R-A greedy GP
  transliteration (`w1lib.to_runes`). `w1lib.clean_text` for boilerplate.
- Non-English fold (applied before the regex): þ ð Þ Ð → TH; æ Æ → AE; ø œ ö → OE; ä → AE; ü → UE;
  ß → SS; then NFD and drop combining marks. Files are read as UTF-8, falling back to Latin-1 if more
  than 1 % of characters are replacement characters.
  - **LA** Latin: `data/keys/armada19/virgil_aeneid_latin.txt`, `analysis/latin/latin_218.txt`
    (Caesar). `latin_28233` (Newton; geometric labels) and `latin_12472` (French content) excluded.
  - **DE** German: `analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt`, `de_2.txt`.
  - **CY** Welsh: `data/keys/welsh/welsh_mabinogion.txt`.
  - **OE** Old English: `.../B6-non-english-plaintext/corpora/oe_beowulf.txt`, lines containing þ ð æ
    only (R18/B6 rule).
- **FE panel (fresh English, 30 corpora, none used in R45).** Paths under `data/keys/`:
  - *archaic (6):* armada19/tyndale_new_testament, armada19/bible_douay_rheims, armada18/shakespeare_hamlet,
    armada18/agrippa_occult_philosophy_book1_1651jf, armada19/bunyan_pilgrims_progress,
    campaign13/englishcanon_paradise_lost
  - *translated (11):* armada18/homer_odyssey_butler, armada18/plato_republic_jowett,
    armada18/dante_inferno_longfellow, armada19/cervantes_don_quixote_ormsby, armada19/herodotus_histories,
    armada19/tao_te_ching_legge, armada19/goethe_faust_taylor, armada19/arabian_nights_lane,
    armada19/kant_critique_pure_reason, armada19/upanishads_hume, campaign13/cypherpunk_kafka_trial
  - *original modern prose (12):* armada18/emerson_essays_first_series, armada18/poe_tales_vol2,
    armada18/lovecraft_charles_dexter_ward, armada19/mill_on_liberty, armada19/paine_age_of_reason,
    armada19/shelley_frankenstein, armada19/stoker_dracula, campaign13/mathscience_abbott_flatland,
    campaign13/philosophy_hume_enquiry, campaign12/walden, armada19/carroll_sylvie_and_bruno,
    armada18/crowley_book_of_lies_clean
  - *verse (1):* campaign12/leaves_of_grass
  A corpus yielding fewer than 3 × 2,896 words is dropped and listed (decided now, not after a look).
- Windows: per corpus 200 windows of n consecutive words, uniform random start; pooled with **equal
  weight per corpus**. Seeds fixed in code.

## 3. Tests and thresholds (fixed now)

### Lead (i) — the 2-rune deficit

**T1 (primary, fresh reference).** s = share of length-2 words. p_FE = equal-weight fraction of FE
windows (n = 2,896) with s <= s_LP2. **Lead (i) replicates on fresh reference iff p_FE <= 0.01.**
Reported also per group and per corpus (min window share).
- *Size control S1:* for each FE corpus, the fraction of its windows below the 1st percentile of the
  other 29 corpora pooled; mean over corpora must be <= 0.03, else T1 uninformative.
- *Power PC2 (validity gate):* per FE corpus, thin its 2-rune words at random with probability chosen so
  the expected share is 0.155 (LP2's size); power = fraction of thinned windows (2,896 words after
  thinning) <= the intact-FE 1st percentile. T1 informative iff power >= 0.8.
- *Probe PC1 (an explanation, not a gate):* delete THE / A / AN tokens; report the share distribution and
  the fraction of windows <= s_LP2.

**T2 (split-half / held-out chapters).** Parts: H1 = words 1–1,448, H2 = 1,449–2,896; S_odd / S_even =
words in odd / even `$`-sections (section index from `w1lib.parse`). p_part = equal-weight fraction of FE
windows of the part's size with s <= s_part. **Replicates within LP2 iff all four p_part <= 0.05.**
Each part needs PC2-type power >= 0.8 at its size (at the 0.05 bar), else that part is uninformative.
*Section heterogeneity:* G of a 2 × (number of sections) table (2-rune vs other), null = permute LP2's
lengths over word positions (10,000); heterogeneous iff p <= 0.01. Plant: FE window cut to LP2's section
sizes, deficit (to an overall share of 0.155) confined to the sections making up the first half of the
words; power reported.

**T3 (which explanation survives — length-profile goodness-of-fit).** 9 classes (1..8, 9+). For each
reference R: q_R = pooled class distribution of the **first halves** of R's corpora (+0.5 smoothing);
null = G of 300 windows of 2,896 words drawn from the **second halves** (equal weight per corpus) against
q_R. LP2 is **admitted by R iff G_LP2 <= 99th percentile of R's null.** References:
- EN-FE (fresh English), EN-noART (FE minus THE/A/AN), EN-merge10 and EN-merge20 (FE with 10 % / 20 % of
  word boundaries removed at random — a "missing separators" generator), LA, DE, CY, OE,
- SOLVED (739 printed words; null = resample the 739 with replacement, then a multinomial of 2,896 from
  the resample, G against q_SOLVED; 300 draws).
*Control (confusion matrix):* 100 second-half windows of each R tested against every R'. Diagonal must be
>= 0.95 or R is uninformative. R and R' are **distinguishable** iff both off-diagonal admit rates <= 0.2.
An explanation **survives** iff LP2 is admitted by its reference; a survivor is "discriminated" from
another survivor only where distinguishable. **"Lengths borrowed from another text"** is not a
reference: any admitted reference is consistent with it, and a multiset cannot tell plaintext lengths
from borrowed lengths. Stated now as unidentifiable by this lane.

**T4 (line-merge ceiling).** Split every LP2 word that contains a line break (`/` with no word-break
character in the gap) at that break → s_max. If s_max is <= the 1st percentile of FE windows at the new
word count, **dropped line-final separators cannot by themselves explain lead (i).**

### Lead (ii) — line breaks inside words

Definitions. A *line gap* is a `/` between two runes. *Running* = the gap contains none of `& $ § %`
(paragraph / section / page ends excluded). *Inside* = the gap contains no word-break character
(`- . & $ §`, digits). c = fraction of all rune-to-rune gaps (within page) that are inside words in the
same text part. f_in = inside fraction of running line gaps. **π = 1 − f_in / c** (word-boundary
preference; 0 = layout blind to the spaces). X1's all-line-break definition is also reported.

**U1 (primary, held-out replication + LP1 contrast).** LP2 parts: P1 = first half of LP2 pages, P2 =
second half; S_odd / S_even sections. For each part: (a) π > 0: one-sided binomial of boundary count vs
(1 − c)·n, p <= 0.01; (b) π_part < π_LP1: one-sided permutation test (10,000) of the excess indicator
e = 1[boundary] − (1 − c_text) between LP1's running line gaps and the part's, p <= 0.01.
**Lead (ii) replicates within LP2 iff (b) passes in all four parts.**
- *Plants (justified-typesetting simulation):* English FE word stream laid into lines with the part's own
  sequence of running-line rune counts as target widths. Layout model: each line with probability ρ is
  word-aware (break at the last word boundary at or before the width if it lies within 6 runes of it,
  else cut at the width), otherwise cut exactly at the width. ρ_LP2 and ρ_LP1 are calibrated on plants so
  the plant's mean π equals the full-LP2 π and LP1's π respectively. Power(b) = fraction of ρ_LP2 plants
  passing (b) against real LP1; size(b) = fraction of ρ_LP1 plants passing (b), must be <= 0.02.
  Power(a) = fraction of ρ_LP2 plants passing (a). (b) informative iff power >= 0.8 and size <= 0.02.

**U2 (typesetting discriminator: is the residual preference word-aware wrapping?).** Running lines
within page; r = rune count − median rune count of the page's running lines. D = mean r(lines ending
inside a word) − mean r(lines ending at a boundary). Word-aware wrapping predicts D > 0 (lines broken
early at a boundary are short). Null: shuffle end-type labels within page, 10,000. **Signature present
iff p <= 0.01.** Controls: real LP1 must show it (p <= 0.01) — else U2 is uninformative; plant power at
ρ_LP2 on LP2's widths (U1 simulation) >= 0.8 to call an LP2 null informative; size on blind plants
(ρ = 0) <= 0.02.

**U3 (dropped line-final separators: are line-spanning "words" merged pairs?).** Lengths L of running
spanning words. Model P(L) = (1 − w)·SB(L) + w·CV(L), SB(L) ∝ (L − 1)·g(L), CV(L) = Σ_a g(a) g(L − a),
g = LP2's printed length distribution. ŵ by ML on a 0.00–1.00 grid (step 0.01); LR = 2[ℓ(ŵ) − ℓ(0)].
Bar = 99th percentile of LR over 1,000 plants (500 blind ρ = 0, 500 word-aware ρ_LP2; English FE
lengths, LP2's widths). **Merged pairs present iff LR > bar.** Power plants: blind layout with every
line-final boundary separator dropped (d = 1.0) and half of them (d = 0.5); power reported for each,
U3 informative iff power(d = 1.0) >= 0.8. LP1 reported as a real-world check (expected ŵ ≈ 0).

### Competing explanations and which test discriminates them

| explanation | lead (i) prediction | lead (ii) prediction | discriminating test |
|---|---|---|---|
| fewer articles / another English register | admitted by EN-noART or a FE group; FE windows reach 15.5 % | none | T1 (per group), T3 |
| another language | admitted by LA/DE/CY/OE, rejected by EN-FE | none | T3 |
| lengths borrowed from another text | any admitted profile | π ≈ 0, D ≈ 0 if spaces post-date layout | unidentifiable for (i); U1(a), U2 for (ii) |
| missing separators (typesetting/transcription) | admitted by EN-merge; T4 ceiling reaches English | ŵ > 0 in U3 | T3, T4, U3 |
| layout artefact (word-aware wrapping used rarely) | none | U2 D > 0; π > 0 | U1(a), U2 |
| one chapter carries it | T2 halves disagree; section G heterogeneous | U1 parts disagree | T2, U1 |

## 4. Order of execution

1. Write this file; record its sha256 in `run.log` line 1.
2. `p1_lead_i.py`: stage 1 builds FE/references and all controls (S1, PC2, PC1, confusion matrix,
   T2 plant) and writes them **before** LP2 is compared; stage 2 computes T1–T4 on LP2.
3. `p1_lead_ii.py`: stage 1 plants (calibration, U1/U2/U3 power and size, LP1 controls); stage 2 LP2.
4. `assemble.py` → `results.json`, `ledger_rows.json`; `RESULTS.md` with closing stamp.

Family: lead (i) T1 is its primary test at 0.01; lead (ii) U1(b) is its primary at 0.01 per part. All
other tests are reported with their own fixed bars and are secondary. A failed control = "uninformative".
Stdlib Python; total < 10 min; heartbeat file `heartbeat.txt` updated by each stage.
