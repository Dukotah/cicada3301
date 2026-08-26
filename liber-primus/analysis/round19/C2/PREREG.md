# Round 19 / C2 — CLOSEOUT of Round 18 lane L6 (OFFSET & MARSAGLIA) — PRE-REGISTRATION

_Written 2026-08-26 **before any scoring code of this lane ran**. The hash re-verification of
the Marsaglia bytes (§5) was launched before this file was finished; verification is a gate on
data, not a test of a hypothesis, and no offset was scored before this file was complete._

Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md).
Inherited, unedited: [`round18/L6-offset-marsaglia/PREREG.md`](../../round18/L6-offset-marsaglia/PREREG.md).

Trust anchor, **before** this lane:

```
python3 liber-primus/tests/validate.py         -> ALL VALIDATIONS PASSED (5/5)
python3 -m pytest liber-primus/benchmark/ -q   -> 8 passed in 13.99s
```

---

## 0. What C2 inherited

Round 18's L6 was **written, launched and abandoned mid-run**. On disk:

| artefact | state |
|---|---|
| `PREREG.md` | complete, 17.5 kB, thresholds fixed |
| `data/` (1.2 GB, gitignored) | ISO + 110 extracted inner files + `MANIFEST.json` claiming 110/110 |
| `out/control_offset.json` | **CONTROL A: PASS** — recovery 40/40, survival 26/40 = 0.650 |
| `out/control_marsaglia.json` | **CONTROL B: PASS** — recovery 16/16 at ms=8 and 16/16 at ms=3 |
| `out/results_A1.json` | sub-lane A stage A1 **COMPLETE** — 220 units, 230,686,720 offsets, best −6.8093 |
| `out/ckpt_A2/` | 81 of 3,024 units (2.7 %) |
| `out/ckpt_M/` | **12 of 756 units (1.6 %)** — the Marsaglia sweep barely started |
| `RESULTS.md` | **does not exist** |

So the Marsaglia sweep is ~98 % unrun, and nothing in L6 has ever been written up.

## 1. The Aiming Test (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it?

Two different answers, and the difference **is** this lane's decision.

- **B-02 offset accounting.** A "hit" here is not a decode. It is an arithmetic statement:
  *how much of the offset axis the repository's published coverage actually touches.* The
  recognizer is a spreadsheet over `LEDGER.json` and the originating lanes' own result JSON.
  There is no instrument to be blind, and the answer cannot be a false negative. **Runs.**

- **Marsaglia sweep.** A hit is a 400-rune beam decode of Marsaglia bytes clearing L6's §4 bar.
  L6's own controls answer Q1 **for an English plant only**: Control B recovers 16/16 planted
  English texts at 100 % of runes on the real, hash-verified pad. But Round 18's **L7-A.7**
  states in terms that R17's pipeline — the identical pipeline L6 imports — filters on English
  **twice** (`dense_scan`'s rune-index trigram model trained on kjv/moby/pride/war selects which
  offsets reach the beam; the English quadgram `score_norm` adjudicates what arrives), and that
  *"no non-English survival rate was ever measured, so R17's coverage discount does not apply to
  a non-English plaintext at all."* Q1 is therefore **unanswered for every register except
  English**, and answering it is cheaper than the sweep it would qualify.

### Q2 — What measured fact raises this family's prior above the flat rate?

- **B-02:** `research/ROUND-8-RESULTS.md:127-129` — the sweep *"assumes key index 0 aligns with
  the first rune of LP2 page 0"*, in Round 8's own words, as a named residue. `handoff/PARKED.md`
  P-10 scores the axis at ×8,192 for a modest range and notes it **multiplies every generator**.
  This is a measured property of the repository's own coverage, not a hypothesis about 3301.
- **Marsaglia:** `round17/SYNTHESIS.md` — a published, dated (1995), hash-manifested archive of
  physical randomness that a 2012–14 author with a cryptography habit plausibly knew; R17 named
  it *"the cheapest live item in this branch"* and `R17-PUBLIC-PAD.not_covered` lists it first.
  Honest weight: this is **prior-by-availability**, not prior-by-evidence in L1's sense. It is
  nearer to doctrine §3's *completeness ritual* than to a high-prior bounded lane, and is
  labelled as such below.
- **The instrument measurement this lane substitutes (§3):** `round18/L7-redteam/RESULTS.md`
  §A.7 names the missing number explicitly. That is an evidence-derived gap in **our own
  instrument**, which doctrine R1 ranks above any key-space item.

### Q3 — Is the space bounded, and by what?

| object | size | class |
|---|---|---|
| B-02 offset accounting | 62 ledger entries, 9 sweeps with recoverable per-offset detail | **enumerable** (done in full) |
| Marsaglia offset space | 63 verified 10 MB pads (+ the 634,124,288 B ISO) × 6 builders × 2 byte-orders × 2 signs, every offset | **enumerable: ≈1.76 × 10¹⁰ offsets on the pads alone** (§4) |
| this lane's prefilter register panel | 10 registers × 30 plants × 1 real pad | **enumerable** |

The Marsaglia space is enumerable and *finite* — the rare good case. The cost is not the
obstacle; §4 measures it at ≈ 10 CPU-hours. The obstacle is Q1.

### Q4 — What are the three conditionals the negative will carry?

1. **Key space** — Marsaglia CDROM bytes only; 6 builders; both byte orders; both signs; every
   offset; `hexchars` excluded (L6 §2.1). Nothing outside the 63 hash-verified pads.
2. **Decoder transition model** — `skipdecode.beam_decode`, whose transition relation is exact
   for `encipher_keyskip` and, per **L7-B**, misses `skip_by_two` at −6.90 / 25.8 % recovery,
   unchanged by beam width 1000 or `max_skip` 8.
3. **Adjudicator register** — English, twice: an English rune-index trigram prefilter selecting
   the offsets, an English quadgram `score_norm` scoring them. Measured power (L7-A, L = 120):
   1.00 LP1-register / modern English, **0.33 Latin**, 0.33 half-vowel English, 0.00 Welsh,
   **0.00 vowel-dropped English**.

### Q5 — What single observation would make you abandon this lane at 10 % of budget?

**If the English trigram prefilter's measured survival of a *non-English* true offset on the
real Marsaglia pad is at or near the chance rate (`keep`/N), the full Marsaglia sweep is
abandoned until I1/I2 land.** Because then the sweep's non-English coverage is not merely
"unmeasured" (L7-A.7's wording) — it is measured, and it is ≈ 0, and ~10 CPU-hours would buy
~10 CPU-hours of English-only null that Round 19 Phase 2's `S1`/`S2` would have to run again.

Checkpoint: after the §3 panel, before any `sweep_marsaglia.py` unit beyond the 12 already
checkpointed.

---

## 2. THE DECISION — run, hold, or stage. **Staged hold, and here is the defence.**

The brief offers three options. This lane takes the third, in this shape:

| | action | why |
|---|---|---|
| **RUN NOW, in full** | B-02 offset accounting | Instrument-independent. Pure coverage arithmetic over the ledger and the originating lanes' JSON. Cannot be invalidated by I1/I2. |
| **RUN NOW, in full** | Independent hash re-verification of the 1.2 GB | A data gate, not a test. Round 12 was burned twice; `MANIFEST.json` was written by the process that fetched the bytes and is not independent evidence about them. |
| **RUN NOW, in full** | Exact quantification of the Marsaglia offset space + measured throughput | Converts "sweep the CDROM" into a costed, schedulable Phase-2 unit with a checkpointed resume path. |
| **RUN NOW** | **The prefilter's register power on the real Marsaglia pad** (§3) | Doctrine R1. This is the number L7-A.7 named and did not measure. It is the gate on whether a Marsaglia negative means anything, it costs ~1 % of the sweep, and it is *reusable by I2/I3* — a property no offset of Marsaglia has. |
| **HOLD** | The 744 remaining `sweep_marsaglia.py` units (≈1.76 × 10¹⁰ offsets) | See below. |
| **HOLD** | The 2,943 remaining sub-lane A2 units (≈1.59 × 10⁹ offsets) | Same argument; A2 is a *fresh key-space grid*, which doctrine R1 forbids opening before the instrument's power envelope covers the hypothesis class. |
| **REPORT AS-RUN** | Sub-lane A1 (complete: 230,686,720 offsets, best −6.8093) | Already measured. Reported with all three conditionals, not re-run. |

**The defence of the hold.** Running Marsaglia now through the unrepaired instrument buys a
negative whose three conditionals are already known in advance, and it buys nothing else:

1. **It is an English-only negative by construction, and doubly so.** L7-A.7 established that
   R17's pipeline — the one L6 imports unmodified — is *English trigram prefilter → English
   quadgram beam*. A Latin or vowel-dropped-English true offset is discarded by the prefilter
   before the beam ever sees it. The measured adjudicator power against those registers is 0.33
   and 0.00. Doctrine R2: value = coverage × power; 1.76 × 10¹⁰ × 0.00 = 0.
2. **It is un-re-adjudicable.** `sweep_marsaglia.py` stores `(offset, sign, pre, score, head)`.
   That is `(parameters, English score, 64-char head)` — precisely the shape that made
   10¹⁰ decodes permanently un-reinterpretable (doctrine R3; Round 10b's 0/15 compliance). Every
   offset it scores today would have to be scored again by S1 tomorrow. Running it now does not
   even *reduce* Phase 2's work; it duplicates it.
3. **The construction axis is untouched by it.** L7-B: `skip_by_two` reproduces LP2's observed
   doublet rate and is missed at −6.90. I1 exists to fix that. Sweeping Marsaglia before I1
   lands means sweeping it against one of at least two live rejection-loop constructions.
4. **The cost is not trivial.** §4 measures ≈ 10 CPU-hours for the pads alone, ≈ 20 with the
   ISO — with six cores shared across a thirteen-lane armada whose Phase 0 is the critical path.

**And the defence of not simply holding everything.** Doctrine §3 allots ~10 % to closeout, and
the honest reading of "closeout" is *make the round's record true and hand Phase 2 a runnable
unit*, not *finish the sweep at any register*. The four RUN-NOW items above do that, and one of
them (§3) is an instrument measurement that Phase 0 needs and does not currently have.

**The completeness-ritual label (doctrine §3).** Sub-lane A1's result and this lane's
quantification of the Marsaglia space are reported as **closeout and completeness**, not as
high-prior lanes. Nothing here claims an evidence-derived prior on 3301's behaviour.

---

## 3. What this lane measures — the prefilter's register power

**Hypothesis (H-C2).** `round17/lib_padsweep.dense_scan`'s English rune-index trigram prefilter
retains a *non-English* true offset at a rate materially below the ≈ 0.65 it retains an English
one (L6 Control A, 26/40) and above the chance rate `keep / N_offsets`.

**Instrument.** Unmodified and imported, never copied:
`round17/lib_padsweep.dense_scan` (`plen = 24`, `keep = 1000`, both signs),
`campaign18_skip/skipdecode.encipher_keyskip(supp = 0.83)`,
`round18/L7-redteam/a1_scorer_language.build_panels()` for the register corpora — the identical
panel L7-A used, so the two numbers compose.

**Design.** For each register R in
{`EN_MODERN`, `EN_KJV`, `LP1_REAL`, `LATIN`, `OE`, `DE`, `CY`, `EN_HALFVOWEL`, `EN_NOVOWEL`,
`RAND`}: draw a plaintext of L = 120 rune indices from R's panel; pick a uniformly random true
offset `o*` inside a **real, hash-verified Marsaglia pad**; build the keystream with `mod29`
(the modal builder, and the one L6 sweeps first); encipher with `encipher_keyskip` at supp 0.83;
run `dense_scan` over the *whole* pad and record whether `o*` is in the top-`keep`, and its rank.
`n = 30` trials per register, the same 30 `(pad, o*)` pairs across registers (paired design, so
the register contrast is not confounded with pad or offset).

**Alongside, at no extra cost, three language-agnostic screens** on the identical offsets — the
statistics doctrine R3 makes mandatory and which no sweep in this repo has ever persisted:
`decrypt IoC·N`, `distinct symbols in the 24-rune prefilter window`, and
`max unigram count in that window` (a compressibility proxy at this window length). Each keeps
its own top-`keep`. Reported: survival of `o*` under each screen, per register.

**Pre-registered thresholds — fixed now, never edited after seeing a score.**

- `p_chance` = `keep / N_offsets` = 1000 / (10⁷ − 24) ≈ **1.00 × 10⁻⁴**.
- **FOUND-GAP** iff, for at least one non-English register, the trigram-prefilter survival is
  ≤ 0.20 while an English register's survival on the *same* 30 (pad, offset) pairs is ≥ 0.50.
- **NO-GAP** iff every register's survival is within a two-sided 95 % binomial interval of the
  English arm's.
- **INCONCLUSIVE** otherwise, or if the English arm itself fails to reproduce L6 Control A's
  0.650 ± binomial (i.e. English survival outside [0.47, 0.81] at n = 30) — in which case the
  panel has not reproduced the instrument and reports nothing about registers.
- Any language-agnostic screen whose survival for a register exceeds the trigram prefilter's for
  that register is reported as a **measured recovery of coverage** available to I2/S1; a screen
  at or below `p_chance` is reported as useless at this window length and named as such.

**Q5 kill applied to this panel's own result:** if FOUND-GAP, the Marsaglia sweep stays held for
I1/I2 and the reason becomes a measurement rather than an inference.

**Positive control on the panel itself:** the `RAND` register is the floor — uniform runes have
no register at all — and `EN_KJV` is the ceiling (it is *in* the trigram model's training set).
If `RAND` survival is not among the lowest and `EN_KJV` not among the highest, the panel is not
measuring what it claims and reports INCONCLUSIVE.

---

## 4. Inherited thresholds — L6 §4, verbatim, not edited

For each sub-lane, with `N` = the number of offsets that sub-lane dense-scanned:

```
HIT  iff  score_norm  >=  max( threshold_for(N, segment_len=400),  null_max + 0.5 )
```

`threshold_for` carries the historical −5.5 as a floor, so the bar can only be stricter.
L6's tier-2 escalation gate (−6.00), tier-1 beam (`head` 400, `beam_w` 120, `max_skip` 8, both
signs), tier-2 beam (`beam_w` 400, page 0 and the full 12,956-rune stream, must **improve** not
decay), the `hexchars` exclusion and the "no ×0.625 constant, measure survival per sub-lane"
rule are all inherited unchanged. **This lane does not edit a single L6 threshold.**

Reported at their true `N`: sub-lane A1's `threshold_for(230,686,720) = −5.5000` (floor binds);
sub-lane B's bar is reported at whatever `N` it has actually scanned, which is 12/756 units.

## 5. The data gate — re-run independently, not inherited

`scripts/verify_marsaglia_independent.py` deliberately does **not** read L6's `MANIFEST.json`.
It recomputes md5/sha1/sha256 from the bytes on disk and compares against the two **published**
sources: archive.org's item metadata for the ISO (`marsaglia-cdrom_files.xml`) and the CDROM's
own `checksums.sha256.txt` for all 110 inner files. Per file it reports **PASS / DRIFT / ABSENT**
— DRIFT separately from ABSENT, as `handoff/capsule/verify_capsule.py` does, because the two
failures Round 12 hit were one of each. **No pad that is not PASS is swept, and it is listed in
`not_covered` by name.**

## 6. What C2 will NOT cover — declared before the run

- The 744 unrun Marsaglia units and the 2,943 unrun A2 units. Explicitly **held**, not excluded;
  §7 states what releases them.
- Any register measurement of the **beam/adjudicator** — that is L7-A (done) and I2 (running).
- Offsets beyond L6's declared 2²⁰ (A1) / 2¹⁸ (A2) on derived keys, and everything else in
  L6 §6, which is inherited verbatim.
- The B-02 accounting covers only sweeps whose per-offset detail is recoverable from committed
  artefacts. A sweep whose offsets cannot be reconstructed is listed as **unrecoverable**, not
  as zero.
- The prefilter panel is one builder (`mod29`), one pad family (Marsaglia), one length
  (L = 120), one filter (supp 0.83). It bounds the prefilter; it does not characterise it.

## 7. Reopening / release conditions — stated in advance

- The held Marsaglia sweep **releases the moment Round 19's I1 and I2 gates PASS**, and should
  then be run under I2's `SWEEPROW` so it is re-adjudicable. Its 12 checkpointed units and this
  lane's costing make it a schedulable S1 unit, not a research question.
- It also releases, unchanged, if Round 19 decides to accept an English-only negative as
  closeout — in which case `python3 sweep_marsaglia.py --nproc 6 --budget <s>` resumes from
  `out/ckpt_M` and needs ≈ 10 CPU-hours for the 63 pads.
- Sub-lane A1's negative reopens per L6 §7: any seed dictionary wider than B-04's, any generator
  outside the swept 16 + 27 + 7, offsets > 2²⁰, or a score ≥ its own `null_max + 0.5` that
  improves under tier 2.
- The prefilter panel reopens for other builders, other pads, other plaintext lengths, and for
  the repaired I1 decoder.

## 8. Vocabulary

Doctrine R7. This lane reports **bounds**. The words "exhausted", "closed" and "unsolvable" do
not appear as verdicts anywhere in its `RESULTS.md`.
