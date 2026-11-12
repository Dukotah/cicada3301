# PREREG — R44 WAVE-2 CELL B3: the 86-doublet-site read (channel + D-01 falsifier)

Date: 2026-11-09. Cell dir: `liber-primus/analysis/round44/W2-B3-doublet-sites/`.
Charter: R43 X0 ADJUDICATION item 21 (`analysis/round43/X0-firewall/ADJUDICATION.md` line 44,
NEW list item 7 line 67); R44 CAMPAIGN-PLAN P5 row ("86-doublet-site read (D-01 falsifier
framing)"). Pure python3 + numpy, no network. Canon: `data/krisyotam_runes.txt`.
No outcome here is a "solved/closed/exhausted" claim.

## Hypothesis (two-headed, as chartered)

**H-channel** (low prior, A2-H2): the surviving doublet sites of the unsolved LP2 stream are a
deliberate low-rate channel — readable as (a) the doubled rune values in site order, (b) the
site positions as numbers (gaps / positions mod 29, mod 60), (c) per-page site counts.

**H-falsifier** (the real payoff): D-01's measured model says the sites are the machine
filter's own Bernoulli leakage — uniform, unscoped, structureless. Test that uniformity
properly, with a planted-structured-sites positive control (the power measurement D-01's own
coverage field says its placement tests lacked: "underpowered at n=12,956 (0.075-0.195)").
If uniform at measured power, D-01 hardens; if structured, flag loudly.

## The object (premise census, pinned before any pipeline run)

Site = adjacent equal pair `x[i]==x[i+1]` in the concatenated rune stream; site position
p_j = global 0-based index of the FIRST rune; doubled value v_j = x[p_j]; gaps
g_j = p_{j+1} − p_j; per-page counts c_p.

- Primary site-set **U86**: the 12,956-rune unsolved stream (canon split on `%`, segments
  [0..54], the exact D-01 / `round17/P4_filter/fingerprint.py::load_structure` object):
  **86 sites**, 0 cross-page, 85 gaps, 28 distinct doubled values (B never doubles),
  per-page counts max 5 (pages 19/24/27/29/44 are the top five).
- Secondary site-set **C89**: the full 13,136-rune canon (all 57 segments incl. AN END +
  PARABLE): **89 sites** — pinned because A-06 says "89 residual doublets" and the R43 blind
  agents counted 88 on pages 0-55; the count differences are segment-inclusion, not
  transcription drift. Registered as a variant so the read does not hinge on the cut.

KILL GATE (premise): if the census had not reproduced 86/89 from canon, report
INSTRUMENT-INCOMPLETE and stop. (Gate passed — numbers above measured from canon.)

## Cited ledger rows (anti-re-run check, wording verified)

- **D-01** (negative, round 16/P4): machine filter, flat/unscoped/single-lag, supp 0.8075.
  Its placement stats (pos-in-line/page KS, gap dispersion, line/page-cross, interrupter
  distance, per-page dispersion) EXIST but its coverage field discloses the per-page/drift
  family as underpowered (0.075–0.195) and its `not_covered` is the human-hand question only.
  **No channel read of the site tuple anywhere in the row.** This cell does not re-claim
  D-01's statistics; it adds the never-run channel reads + a power-controlled uniformity
  battery.
- **A-06** (measured): H6 = 12 ornament pointers landing on the 89 residual doublets
  (binom p=1.0). Covers pointers→sites, NOT sites-as-stream. Stays untouched.
- **E-02** (negative): part B = the 85 inter-doublet gaps rank-correlated against PAYLOAD
  byte-reads (null). Covers gaps-vs-payload only; its `not_covered` names other
  meta-parameter readings. This cell reads gaps as a channel in their own right — no payload
  correlation is re-run.
- X0 ADJUDICATION item 21: "No row reads the site 86-tuple as symbols/positions." Open ground
  confirmed; this cell stays inside it.

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
(channel) A hit = one of the channel streams scoring panel-R36 pmax above a POT bar refit on
nulls matched to this exact construction. PLANTS through this cell's OWN glue (raw rune stream
→ site extraction → channel streams → 116-map grid → panel), run BEFORE any real target:
PLANT-V (doubled values = held-out English rune window, L=86), PLANT-G (gaps = English window
+ offset, recoverable by the grid's shift maps), PLANT-P (positions mod 29 = English window via
constructed gaps), PLANT-C (per-page counts = English window, L=55). Each plant class is
replicated 40× for a measured power figure; a channel verdict requires EN power ≥ 0.5 at its L
(the W2-A1 POWER_FLOOR, adopted). (falsifier) A hit = any battery statistic beyond its
empirical-null band; PLANT-G/P double as the battery's positive control (clustered positions
must fire the KS test) — its firing fraction is the battery's measured power.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Honestly: the prior is LOW and the charter says so (X0 item 21: "D-01's measured model already
predicts these sites as Bernoulli filter slips... a falsifier of D-01's residue, not a likely
channel"). The measured facts that make it worth its (small) budget: (i) the sites are a
finite, human-checkable 86-tuple (doctrine R5 class 1); (ii) D-01's own coverage field
discloses its placement battery as underpowered with no planted positive control — the
falsifier half repairs a disclosed instrument gap; (iii) one R43 blind agent (A2-H2)
independently nominated the channel, and blind convergence onto uncovered ground is the X0
PREREG criterion. This is a bounded-object audit + instrument repair, not a sweep.

**Q3 — Is the space bounded, and by what?**
Enumerable and tiny. 8 channel streams (4 per site-set: dblvals L=86/89, gapsmod29 L=85/88,
posmod29 L=86/89, pagecounts L=55/57) × the FIXED W2-A1 116-map grid ({fwd,rev} × a∈{1,28} ×
s∈0..28) = **928 real readings**, bars fixed at N=928. Falsifier battery = 7 fixed statistics
on U86. Nothing is selected after seeing a score.

**Q4 — The three conditionals this negative will carry.**
1. *Key space*: identity/affine/reversal readings of these 8 streams only. NOT covered: keyed
   or derived readings of the channel streams, interleavings/joins across channels,
   positional-selector readings into other channels, site-sets under any other doublet
   definition (e.g. ≥triplets, lag-2 pairs), gap encodings outside mod-29 shift reach (e.g.
   base-29 multi-digit), and any use of the sites as cribs gating key sweeps.
2. *Decoder transition model*: memoryless monoalphabetic on the channel stream — no chained or
   output-aware construction of the channel itself is represented.
3. *Adjudicator register*: panel-R36's 12 registers at the power measured by THIS cell's
   plants at L∈{55,85,86} (reported in RESULTS). The per-page-counts channel is expected
   DEGENERATE by construction on the real data (counts occupy ≤6 symbols; R38 guard
   mds≤6) — if so it is measured-only, exactly the W2-A1 dotvals30 precedent, and the plant
   (which uses the full alphabet) only validates the glue path. Non-panel registers (numeric,
   schema) not covered.
Falsifier conditionals: uniformity is tested against D-01's flat-Bernoulli model as
instantiated by the dfshuffle surrogate (histogram-preserving, doublet-count-matched); 7
statistics only; power measured for position-clustering plants, not for every conceivable
structure.

**Q5 — Kill condition at 10% of budget?**
(a) Premise census fails → INSTRUMENT-INCOMPLETE, stop (passed). (b) Any plant class not
recovered by the glue (extraction returns ≠ planted sites, or glue crashes) → stop, fix or
report INSTRUMENT-INCOMPLETE; no real read without all four plant classes recovered
mechanically. (c) All channel plants below 0.5 power AND battery plant power < 0.5 →
the cell is honestly UNDERPOWERED; report measured-only, no negative. Checkpoint = end of
plant stage, before any real read.

## Instrument + fixed thresholds (in advance)

- Adjudicator: the standing panel-R36 (`analysis/round19/I2/adjudicate.py` +
  `data/panels/panel-r36.npz`, sha256 a0682f0c…) via the W2-A1 `shortnull.py` glue pattern
  (116-map grid, `adjudicate_batch`, R38 degenerate guard mds≤6 / IoC·N≥4.24).
- **Null families, D = 1,000 draws each, seed 3301:**
  - **F1 (matched channel null, binding):** `dfshuffle` (the standing doublet-matched
    shuffle, code copied from `analysis/round41/C1-r14-r15/lib.py::dfshuffle`) of the unsolved
    stream (target 86) and of the full canon (target 89); per draw, extract sites through the
    IDENTICAL glue, build the same 4 channels, run the same 116 maps; pool pmax per channel.
  - **F2 (SEL cross-check, conservatism):** sorted uniform position-selections from canon at
    each real L (W2-A1's SEL family, same code shape), 1,000 × 116 per L.
- **Bar of record per channel** = max(F1 POT bar, F2 POT bar) with the bars_v3 model refit
  (exponential POT above the empirical 90th pct — `pot_fit`/`pot_bar` as W2-A1), at
  **N = 928, α = 0.01**. bars_v3 itself has no free node below L=120 (verified by call); the
  refit-at-actual-L is the W2-A1 instrument this wave built for exactly this case, and
  `bar_v3(928, 120, "free")` is reported as a non-binding cross-check.
- **Channel decision rule:** a real reading with pmax ≥ bar_of_record AND non-degenerate →
  **FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never certified. 0 crossers + plant power ≥
  0.5 at that channel's L → NEGATIVE for that channel (within Q4). 0 crossers + power < 0.5 →
  measured-only.
- **Falsifier battery on U86** (empirical add-one p against the F1 unsolved-stream draws;
  family α = 0.01, Bonferroni over 7 → per-test **p ≤ 0.001428**; D=1000 makes 0.000999
  attainable):
  T1 KS of p_j/12956 vs uniform (one-sided, larger=structured);
  T2 gap CV² = var(g)/mean(g)² (two-sided);
  T3 χ² of p_j mod 29 over 29 cells (one-sided);
  T4 χ² of p_j mod 60 over 60 cells (one-sided);
  T5 χ² of doubled-value counts vs the F1-null mean count vector (one-sided);
  T6 per-page binomial dispersion index of c_p (two-sided; D-01's test-6 statistic, now with
  an empirical null + measured power rather than an asymptotic z);
  T7 lag-1 autocorrelation of the gap sequence (two-sided).
  Two-sided p = 2·min(add-one lower, add-one upper), capped at 1.
  **Any test ≤ 0.001428 → LOUD FLAG (D-01 residue structured; report to oracle queue).
  All > → D-01 HARDENS at the battery's measured power.**
- Specificity: 25 untouched F1 draws through the full pipeline; expected crossers ≈ 0.25
  (α·25) — reported, and >3 crossers voids the bars (refit forced, dated addendum).
- No threshold changes after seeing a result; later changes only as a dated addendum.

## Coverage statement to be reported

Covered: the 86-site and 89-site tuples as value/gap/position/count channels under 116
affine/reversal maps each, panel-R36, bars refit at actual L and N=928; the 7-statistic
uniformity battery vs the dfshuffle instantiation of D-01's model, with measured power.
Not covered: the Q4 list above.

## Outputs

`b3lib.py` (glue: census, channels, grid, nulls, battery), `plant_gate.py` → `plants.json`,
`run_real.py` → `results.json`, `RESULTS.md`, `ledger_rows.json` (draft), `run.log`
(PREREG sha256-stamped before first execution).

## Addendum 1 (dated 2026-11-09, BEFORE any null build, plant or real read)

Glue smoke-testing (run.log) measured a defect in the standing `dfshuffle` that makes it unfit
as THIS cell's F1 null: it repairs bad pairs in ARRAY ORDER and breaks when the count reaches
the target, so (a) its residual doublet sites cluster at the stream END (one-draw KS vs
uniform 0.844; per-page dispersion 6.29) and (b) the final site count undershoots the target
(56 observed vs 86 requested) because order-position swaps destroy unvisited bad pairs without
being counted. For its historical use (scoring decodes of the whole shuffled stream) this bias
is immaterial; for a null over SITE POSITIONS it is disqualifying — it would fake "structure"
in the real data. F1 is therefore built with `site_matched_shuffle` (this cell's b3lib):
full histogram-preserving shuffle (initial doublets uniformly placed), then repair of
UNIFORMLY-RANDOM-chosen bad pairs with full recount, until EXACTLY the target count remains
(exact 86/89 per draw — also removing the channel-L mismatch). No threshold, statistic,
channel, grid, alpha or decision rule changes. The dfshuffle defect is reported in RESULTS.md
as an incidental instrument observation for other lanes.

## Addendum 2 (dated 2026-11-09, after the real battery, before any verdict is written)

Adjudication exposed an attainability defect the PREREG mis-stated: with D=1000, the MINIMUM
attainable two-sided add-one p is 2×1/1001 = 0.001998 > the per-test bar 0.001428 — the three
two-sided tests (T2/T6/T7) could never formally fire. T7 (lag-1 gap autocorrelation) came back
AT that floor: observed +0.380 vs null mean −0.014, sd 0.105 — outside all 1,000 draws
(z ≈ +3.7). Resolution: the battery null (battery statistics ONLY — no panel scoring, no new
real readings, no new statistics) is extended to D = 10,000 fresh site_matched_shuffle draws
(seed block 3301+200000+j, disjoint from the original), and every battery p is recomputed on
the extended null. The per-test bar stays 0.001428 and the decision rule is unchanged; min
attainable two-sided p becomes 0.0002. Robust descriptive context (Spearman ac1, leave-one-
pair-out sensitivity) will be reported alongside T7 but is NOT a registered test.
