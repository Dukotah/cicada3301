# R46-P1 — Pre-registered tests of the two Round-45 leads — RESULTS

_2026-11-24. PREREG: `PREREG.md` (sha256 `fd9fa758…94425285`, stamped as line 1 of `run.log` before any
script ran; unchanged at close, no addenda). Machine record: `results.json`. Ledger rows: `ledger_rows.json`.
Reproduce: `python p1_lead_i.py && python p1_lead_ii.py && python assemble.py` (about 4 + 5 min, stdlib).
The LP2 values were already seen in R45 (see PREREG §0). What is new here is the fresh reference panel, the
held-out splits and the tests that tell the explanations apart._

## Lead (i): the 2-rune-word deficit

| test | result | control | verdict |
|---|---|---|---|
| **T1** fresh English (30 corpora not used in R45, 6,000 windows of 2,896 words) | LP2 15.47 % is below **all 6,000** windows (pooled min 16.06 %, 1st pct 17.65 %) | thinning plant power 0.96 ✔; leave-one-corpus-out size **0.033 > 0.03 ✘** | **uninformative** (by the registered rule) |
| **T2** held-out halves / chapters | H1 15.3 %, H2 15.6 %, odd `$`-sections 15.4 %, even 15.6 %; all p ≤ 0.0006 | power ≥ 0.995 per part | **replicates in every part** |
| T2 section heterogeneity | per-section 12.5–17.7 %, G p = 0.80 | plant power 0.98 | **homogeneous**: the whole text carries it, not one chapter |
| PC1 probe: English minus THE/A/AN | median 20.3 %; 2.8 % of windows ≤ 15.5 % | — | removing articles alone rarely gets there |
| **T4** line-merge ceiling (split every line-spanning word) | 18.73 % vs fresh-English 1st pct 17.97 % (p = 0.022) | — | the ceiling **reaches** the bottom of English, so T4 **does not** rule out dropped separators |

**Why T1 failed its own control.** One corpus did it: *Paradise Lost*. 99 % of its windows fall below the
other 29 corpora's 1st percentile, and its minimum (16.06 %) is the only fresh window close to LP2. The
next-lowest corpus minimums are 19.2 % (*Leaves of Grass*), 19.4 % (Tyndale) and 19.8 % (*Faust*, translated
by Taylor). So the honest statement is narrower than "below all English": **LP2 is below all 6,000
fresh windows, but one fresh register (Milton's blank verse, minimum 16.06 %) comes within 0.6 points, and that
single corpus is what fails the size control.** Whether the R45 panel caused the lead is therefore not settled
by T1; the panel's lower edge depends on register.

**T3: which explanation survives** (9-class length profile, G against each reference's own window null):

| reference | G / 99 % bar | verdict |
|---|---|---|
| EN-FE fresh English | 234 / 688 | admitted |
| EN-noART (no THE/A/AN) | 99 / 712 | admitted (best fit) |
| EN-merge10 (10 % of separators missing) | 152 / 537 | admitted |
| EN-merge20 | 244 / 391 | admitted |
| Latin | 1,159 / 897 | **rejected** |
| German | 378 / 121 | **rejected** |
| Welsh | 1,396 / 681 | **rejected** |
| Old English | 384 / 137 | **rejected** |
| solved Cicada pages | 193 / 91 | **rejected** |

Confusion control: every diagonal is ≥ 0.95. The four English-family references admit each other's windows at
rates of 0.56–1.00, so **this test cannot tell "fewer articles", "another English register" and "missing
separators" apart.** Latin and
Welsh are separable from English (off-diagonals ≤ 0.18). German is separable from fresh English, but 70 % of German
windows are admitted by EN-noART. Old English is **not** distinguishable from fresh English by the registered rule
(100 % of OE windows are admitted by EN-FE); its rejection of LP2 reflects a narrow single-text (Beowulf) bar. The
pooled-English bars are wide because English varies a lot between corpora, so being admitted is weak evidence.
Being rejected is the informative outcome.

**Which explanations survive (lead i):** fewer articles / another English register (survives), missing
separators (survives; T3 and T4 can't exclude it), and lengths borrowed from another text (unidentifiable from
a multiset, as the PREREG said in advance). **Ruled out by the GOF test:** another language among
Latin/German/Welsh/Old English under the §2 fold, and "same register as the solved Cicada pages". LP2's profile
is not a resample of the 739 solved words (G 193 vs bar 91), but that bar has no between-text variance and
rejects 67 % of fresh-English windows too, so this is weak evidence about register.

## Lead (ii): line breaks inside words

Running line breaks (paragraph, section and page ends excluded). LP1: 126 lines, c = 0.755, f_in = 0.587,
**π = 0.22**. LP2: 532 lines, c = 0.777, f_in = 0.729, **π = 0.062**. Under X1's definition (all breaks):
LP1 53.4 %, LP2 70.8 %, which reproduces X1.

| test | LP2 result | control | verdict |
|---|---|---|---|
| **U1b** π_part < π_LP1, all 4 parts | P1 p = 0.038, P2 0.0014, S_odd 0.011, S_even 0.0046 (2 of 4 pass) | typesetting-plant power **0.46–0.62 ✘**, size 0.00 | **uninformative**: LP1's 126 lines limit the power |
| U1b on full LP2 (descriptive) | p = 0.0051 | — | not registered; computed on the R45-X1 discovery data, so no confirmatory weight |
| U1a π > 0 | full p = 0.005; P1 0.002, S_odd 0.009 pass; P2 0.25, S_even 0.15 fail | plant power ≤ 0.26 ✘ | parts **uninformative**; LP2 shows a small boundary preference overall |
| **U2** word-aware-wrapping signature (boundary-ending lines shorter) | D = +0.27 runes, p = 0.084 | LP1 real D = +2.86, p = 0.0003 ✔; plant power 0.27 ✘; size 0.005 | null **uninformative** |
| **U3** dropped line-final separators (merged pairs in spanning words) | ŵ = 0.00, LR = 0.00 (bar 1.85), n = 388 | power 0.55 (d = 1), 0.25 (d = 0.5) ✘; LP1 ŵ = 0 | **uninformative**. The point estimate is exactly zero merges |

**Which explanations survive (lead ii):** every one. None of the registered discriminators reached power 0.8.
The full-data contrast (LP2 boundary preference about a quarter of LP1's, p = 0.005) stands as a
**descriptive** fact. It is the R45-X1 observation itself re-expressed as a p-value (same 126 + 532 lines),
not a test of it. LP1's own layout carries a strong word-aware-wrapping signature (U2 p = 0.0003), which
validates the instrument on real pages. LP2's signature is weak (+0.27 vs +2.86 runes) and not significant.
U3's ŵ = 0 tilts against "line-final dots dropped", but the test is underpowered.

## What this means (plain)

1. **Lead (i) covers the whole text (T2 homogeneity, section G p = 0.80); whether it is extreme for English is
register-dependent (T1 uninformative: Paradise Lost windows reach 16.1 %).** Both halves
   and both sets of chapters show it, and no chapter stands out. Only archaic verse (Milton) gets close.
2. **LP2's length profile fits English, or English with fewer articles, and does not fit Latin, German, Welsh,
   Old English, or the solved Cicada pages.** Removing articles moves English toward LP2 but usually not
   far enough (median 20.3 %). This test cannot separate "fewer articles" from "missing separators".
3. **Lead (ii) can't be confirmed with held-out parts**, because LP1 is the only word-aware reference and it has
   just 126 running lines. The full-data difference stands, but as a description, not a replicated finding.
4. Nothing here touches the key. The OTP-class verdict is unchanged.

## Conditionals (doctrine Q4)

1. **Key space:** none. No decode was run.
2. **Generator / layout models represented:** the length generators are T3's 9 references, plus article
   deletion and random separator merging. The layout models are a blind fixed-width cut, a word-aware mixture
   wrap (slack 6), and a blind cut with line-final separator drops. **Not represented:** lengths borrowed from a
   specific text, glyph-width justification, hyphenation, and keyed layouts. Lead-(ii) plants are simulated inside
   layout(), not parsed through struct()/summ(), so lead-(ii) power is measured on the layout model, not on the
   lane's parsing glue.
3. **Register:** English GP under rule R-A, using 30 fresh corpora in four groups. Latin, German, Welsh and Old
   English use the §2 fold. Solved-Cicada printed lengths are included. **Not covered:** Greek, Hebrew and Norse
   (corpora not on disk), and any other language.

## Closing stamp

R46-P1 closed 2026-11-24. PREREG sha256 `fd9fa7581caed9d40bd190cecb0382dab0c1bc5e9da83004dff6baef94425285`, with
no addenda and no thresholds edited. Verdicts:

- **T1:** uninformative (size 0.033; Paradise Lost).
- **T2:** replicates in all four parts, and the text is homogeneous.
- **T3:** LA, DE, CY, OE and SOLVED rejected; the English family is admitted but cannot be told apart.
- **T4:** dropped separators are not excluded.
- **U1b, U1a parts, U2 null, U3:** uninformative (power 0.17–0.62).

Rows: `ledger_rows.json` (R46-P1-TWO-RUNE-DEFICIT-REPLICATION, R46-P1-TWO-RUNE-EXPLANATIONS,
R46-P1-LINEBREAK-INSIDE-WORDS). Files written only inside `analysis/round46/P1-leads/`. LEDGER.json not edited.
Nothing committed.

## X1 corrections applied

_Applied by the Round 46 coordinator from `../X1-redteam/AUDIT.md` (2026-11-24); PREREG untouched._ §1.6 items 1–7: T1 wording no longer claims the R45 panel was not the cause (T1 is uninformative); "not an artefact of R45's corpus choice" withdrawn; Old English is **not** distinguishable from fresh English by the registered rule (OE→EN-FE 1.00); Latin/Welsh separable at ≤ 0.18, not ≤ 0.07; the solved-pages rejection is weak evidence about register; lead-(ii) full-LP2 p = 0.005 is unregistered, on the R45-X1 discovery data, and carries no confirmatory weight; lead-(ii) plants are measured on the layout model, not the parsing glue. Same edits in `ledger_rows.json`.
