# Round 22 — Lane R (red-team) — RESULTS

_Ran 2026-08-29. Standing red-team lane, doctrine R6. Target = the repository's own Round-22
claims (lanes A/B/C/D). Default posture: try to REFUTE, not confirm. Reports FOUND-ERROR or
NO-ERROR-FOUND, never "confirmed"._

## Trust anchor

`cd liber-primus && python3 tests/validate.py` → **ALL VALIDATIONS PASSED** — 5/5 known solves
reproduced (A WARNING, SOME WISDOM, two KOANs, WELCOME). The rig is honest; every negative below
rests on a passing anchor. Not stopped.

## Overall verdict: **NO-ERROR-FOUND** (one low-severity disclosure gap noted, non-blocking)

No Round-22 lane rests its negative on an unvalidated instrument, no lane silently re-reads a
Round-11 NEGATIVE lens as new, and Lane B's family-wise "0 flagged-for-oracle" conclusion is
**SOUND** — independently reconfirmed. One minor undisclosed partial overlap in Lane B's G3
sub-detector is documented below; it changes no verdict.

---

## 1. AUDIT of Lane B's family-wise correction (the sharpest target)

**Independently recomputed from `B/ledger.json` (not from B's summary).**

### 1a. Cross-check of the reported hit counts
Recomputing per-stat `p<0.01` counts directly from each row's stored `null_p` field, over all 72
combos, reproduces B's table **exactly**: `bbox_fill`=3, `symmetry`=2, `components`=1, and
`closure`/`self_intersections`/`caging`=0. 6 shape-stat `p<0.01` candidates total. Zero
mismatches between the recomputed counts and B's `hits_at_0.01` records. **B's counting is honest.**

### 1b. How many flags are EXPECTED under the seed-3301 null?
- Full detector family: **6 stats × 72 combos = 432 tests** at α=0.01 → **4.32** expected false
  `p<0.01` hits. B routes only the **4 shape stats** to the flag decision (caging/closure are the
  same net/path ratio and are recorded-not-refined) → shape family **N = 4×72 = 288** →
  **2.88** expected false hits.
- **Observed shape-stat hits = 6.** Under a pure null:
  - `P(≥6 | Poisson λ=2.88) = 0.072`
  - `P(≥6 | Binomial(n=288, p=0.01)) = 0.071`
- **Verdict:** 6 hits is **consistent with pure multiple-comparisons noise** (p ≈ 0.07, not
  significant at 0.05). No excess of hits demanding explanation.

### 1c. Is any single flag a real outlier B wrongly dismissed?
Converting each refined z-tail to a σ-equivalent and re-deriving the family-wise ceiling:

| combo / stat | emp_p (N=2000) | z-tail | σ-equiv | B flag | independent read |
|---|---|---|---|---|---|
| `value_M8_relative_value` / `components` | 0.012 (24/2000, **NOT floor**) | 2.17e-6 | 4.74σ | reject | **reject — correct** |
| `value_M8_relative_value` / `symmetry` | 0.000 (floor) | 4.2e-4 | 3.53σ | reject | **reject — correct** |
| `value_M8_relative_value` / `bbox_fill` | 0.002 | 1.1e-3 | 3.26σ | reject | reject — correct |
| `pi_M6_relative_unit` / `bbox_fill` | 0.012 | 8.8e-3 | ~2.4σ | reject | reject — correct |
| `value_M12_absolute_unit` / `bbox_fill` | 0.006 | 1.0e-2 | ~2.3σ | reject | reject — correct |
| `value_M6_absolute_unit` / `symmetry` | 0.002 | 0.127 | ~1.5σ | reject | reject — correct |

Bonferroni flag bar 2.31e-5 corresponds to a **4.23σ** threshold.

**The one candidate that superficially looks like a wrongly-dismissed outlier** is
`value_M8_relative_value / components`: its normal-approx z-tail (4.74σ) *exceeds* the 4.23σ bar.
But its **empirical p is 0.012 — 24 of 2000 shuffle surrogates matched or beat it.** A genuine
4.7σ outlier cannot have 24/2000 of the null exceed it; the two numbers are contradictory. The
resolution: `components` is a **discrete, highly-skewed integer count** (real=8 vs null mean 1.95),
so a Gaussian z-tail is invalid and inflates the tail. The honest number is the empirical 0.012,
which Bonferroni-adjusted across the family (×288) → 1.0. **This is exactly the discrete-stat
artifact B's double-gate (needs BOTH emp_p at floor AND z<bar) was built to reject. B rejected it
correctly.**

The only candidate whose **empirical p is genuinely at the floor** (`value_M8_relative_value /
symmetry`) sits at just **3.53σ** — well under the 4.23σ bar, Bonferroni-adjusted emp_p ≈ 0.14.
Not an outlier. For contrast, the Phase-0 planted square fired 5/6 stats at p=0 with
self-intersections ~170× the null mean (many tens of σ): a *real* made figure is not subtle. None
of the six LP2 candidates is within reach of that signature.

**B's "0 flagged-for-oracle" is SOUND. No combo reopens.** The family-wise ceiling holds at the
true N (432 full / 288 shape), the expected-vs-observed test is non-significant (p≈0.07), and the
single apparent outlier is a discrete-count normal-approximation artifact, not a suppressed hit.

### 1d. One methods caveat (not an error)
B's Bonferroni bar is derived over the **full 432-cell family** (6×72) but the flag decision only
ever runs on the **4 shape stats** (caging/closure never refined). Using the larger 432 divisor
makes the bar **more conservative** (harder to flag), not less — so it cannot produce a false
negative relative to a correctly-scoped 288-cell bar. The direction of the approximation is safe.

---

## 2. NO-SILENT-REREAD check (doctrine R6) — all four lanes

Round-11 NEGATIVE lenses, confirmed from their RESULTS.md: **N1** gematria-feedback autokey;
**N2** prime-gap/prime-index streams read as data (base-29 / mod-29 / ASCII / coordinate-pair);
**N3** whole-book-as-integer number theory; **N4** digit-plane keystreams (bases 3/5/7/10);
**N5** totient-ladder keystreams; **S1** interrupter-position channel; **S2** separator/ornament
(inline `-` `/` `.` glyph) channel.

| lane | channel | overlap with N1–N5 / S1–S2 | disclosed? | verdict |
|---|---|---|---|---|
| **A** self-embedded acrostic of the **decrypted solved plaintext** | selection functions on plaintext | **none** — Round 11 worked ciphertext/number channel, never the decrypted plaintext | yes (RESULTS ¶2, ledger `_note`) | clean |
| **B** turtle **geometry** render of value/π/φ streams | geometry adjudicator | headline (turtle path) **new**; G3 `coord_pair_rate` sub-detector partially re-touches **N2 route (d)** (value pairs as coordinates) with a *different* statistic | **partial gap** (see below) | minor |
| **C** literal imperatives X1/X3/X4 | keystream/structural | **X4-totient re-adjudicates N5**; X4 raw-prime-value & prime-index keystreams **new** (N4 used digit-*planes*, N2 read primes as *data* not keystream) | **yes, in full** (RESULTS §"non-overlap honesty note", ledger `redteam_overlap`) | clean, exemplary |
| **D** red drop-cap illustration channel | image/illumination | **none** — S2 was the inline-separator glyph channel, not page-scan illustrations; no drop-cap catalog existed before | yes (RESULTS ¶"Asset verdict") | clean |

### C's disclosure is complete and accurate — independently verified
- N5 used φ(prime) as a positional keystream; C's `X4_v_totient_none_sign-1` re-adjudicates that
  exact lens under the **repaired 9-register panel-max instrument** (N5 used the retired −5.5 bar),
  and re-confirms NEGATIVE (recovery 0.49, pmax 2.69). This is a legitimate *instrument-repair
  re-adjudication* (doctrine R1), not a silent duplicate, and C labels it so.
- N4 used digit-*planes* of prime magnitudes as keystreams — **not** the raw prime-value/index.
  N2 read prime-index/gap as *data* — **not** as a keystream over the letters. So X4's raw-value
  and prime-index keystream members are genuinely new. **C's overlap accounting checks out.**

### The one gap — Lane B / G3 (LOW severity, non-blocking)
`B/g3_coord_decode.py::digit_pairs_as_coords` reads consecutive stream values as lat/lon degree
pairs and counts plausible-range hits vs the seed-3301 null. This re-touches the *channel* of
**N2 route (d)** ("coordinate pairs → top-pair concentration"), which B does not cite. It is not a
silent re-read of a full lens presented as new: (i) the statistic differs (plausible-range count
vs top-pair concentration), (ii) B's *headline* G3 detectors — base32/onion-v3 pointer regex and
low-entropy base32 run — are genuinely new and never in N2, and (iii) both the new and the
overlapping sub-detectors return the same NEGATIVE, consistent with N2's coordinate route. Impact
on any verdict: **none.** Recommendation: B's G3 section should cite N2 route (d) for the
coord-pair sub-detector. Recorded as a disclosure gap, **not** a FOUND-ERROR.

---

## 3. Positive-control / instrument spot-check (one per lane)

| lane | control | recovery / firing | bar used | null | pass |
|---|---|---|---|---|---|
| **A** | planted every-7 + width-13-diagonal acrostic | recovery **1.000** (2/2, recovered as top-by-excess) | excess-over-null (no −5.5) | seed-3301, 1000 shuffles, FPR 1e-3 | ✓ |
| **B** | planted closed square / block-comb | square **fires 5/6** stats (p=0, self-int ~170× null); blockcomb fires symmetry+bbox_fill | geometry, Bonferroni 2.3e-5 | seed-3301, 200/combo + 2000 refine | ✓ |
| **C** | X1 de-interleave / X3a reversal / X3b runkey / X4 keystream | all recovery **1.000**, X3b/X4 `is_hit`=True held-out 1.000 | panel-max ~5–6.39 (never −5.5) | seed-3301 histogram-preserving | ✓ |
| **D** | 4 hand-read pages + page-0 rune identity | 4/4 has-cap + page-0 = S | p<0.01 Bonferroni | seed-3301, 10000 shuffles | ✓ |

- **No lane uses the retired −5.5 score bar as a live threshold** (grep confirms `-5.5` appears
  only in Round-11 files and in "5/5" validation counts; C's ledger explicitly records
  `recognizer_bar: NEVER -5.5`).
- **All nulls are seed-3301** and order-affecting (shuffle / histogram-preserving), as required.
- **No lane rests its negative on an unvalidated instrument.** Every recognizer separated a
  planted hit of its own shape from its own null before the real sweep ran.

---

## 4. Coverage × power of THIS audit (doctrine R2)

- **Coverage.** All four Round-22 lanes audited on three axes: (1) B's family-wise correction
  independently recomputed from raw ledger rows (432/288-cell ceiling, Poisson+binomial
  expected-vs-observed, per-candidate σ re-derivation); (2) no-silent-reread cross-checked against
  all seven Round-11 lenses (N1–N5, S1–S2) read from source; (3) one positive control per lane
  re-read for recovery≥0.90 gates, bar provenance (no −5.5), and seed-3301 nulls.
- **Power.** The audit *would* have flagged: a real geometric outlier B suppressed (it found the
  components candidate looked like one and proved it a discrete-stat artifact — i.e. the audit can
  tell a true 4.7σ outlier from a fake one); an undisclosed re-read (it found B's G3/N2 coord
  overlap that B did not cite); a −5.5-bar relapse or a non-3301 null (none present); a control
  with recovery <0.90 (none present). The audit did not re-run B's 72-combo sweep or C's 185
  operations from scratch — it audited their persisted per-row statistics for internal consistency
  and family-wise soundness, which is the R6 target (audit the claim, not re-run the space).
- **Not covered (reopeners for this audit).** Re-execution of the sweeps from source (trusted the
  committed ledger rows as faithful to the code); the specific numerical correctness of B's
  `self_intersections` sampler and D's colour-mask extractor (validated only via their passing
  planted controls); the PNG renders (`.gitignore`d, not regenerated here).

---

## FOUND-ERROR ledger

**NO-ERROR-FOUND.** One low-severity, non-blocking disclosure gap (Lane B G3 coord-pair
sub-detector should cite Round-11 N2 route (d)). No verdict changes. No combo reopens. No lane
rests on an unvalidated instrument. Lane B's family-wise 0-survivor conclusion is independently
reconfirmed SOUND.
