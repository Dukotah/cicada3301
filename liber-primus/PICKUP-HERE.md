# PICKUP-HERE — where the work left off, and what is still open

_Refreshed **2026-08-31** at the close of Round 26 (originally opened 2026-08-29 at the close of
Round 22). Read this first, then [`ELIMINATION-LEDGER.md`](ELIMINATION-LEDGER.md) and query
[`LEDGER.json`](LEDGER.json) `coverage`/`not_covered` (never the bare `status`)._

Binding: [`liber-primus/ARMADA-DOCTRINE.md`](ARMADA-DOCTRINE.md). For a NEW solver deciding
where to spend effort (rather than picking up this project's own threads), read
[`handoff/SOLVER-STRATEGY-2026.md`](handoff/SOLVER-STRATEGY-2026.md). Trust anchor:
`python liber-primus/tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5), passing through
Round 25 and re-verified 2026-08-31 (`pytest -m "not network"` 85 passed).
`validate_ledger.py` Unsound-negatives = **0**. `LEDGER.json` now holds **156 entries**
(R22-A/B/C/D/R, R23-A2, R24 ×5, R25 merged, the ten Round-20 lanes filed 2026-08-31, and now
**Round 26 ×4**: R26-A-GEN-SWEEP-FIRST-FIRE [partially-run], R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE
[partially-run], R26-C-SEMANTIC-SEED-ZOO [negative], R26-D-REDTEAM [audit]).

**The Round 23 seed at the bottom of
[`analysis/NEXT-ARMADA-ROADMAP.md`](analysis/NEXT-ARMADA-ROADMAP.md) ("ROUND 23 SEED") has been
RUN.** Its one scoped task — the printed-line-geometry acrostic — came back a clean,
control-validated NULL (Round 23), and the seed's own decision line therefore stands: **the
active work sits at a natural stopping point at the tested resolution.** Rounds 24 and 25 then
did the two things that judgment leaves open — Round 24 discharged the L7-A/L7-B instrument
conditionals (the negatives hold under the corrected scorers and the skip-aware decoder), and
Round 25 began the owner-elected grind of the last runnable branch (the Py2.7-MT 2³² tail),
**parked at 0.5015 % coverage, 0 hits, fully resumable**.

> **Round 26 is CLOSED (2026-08-31).** Merged, validated (Unsound-negatives = 0), trust anchor
> 5/5. Four lanes under `analysis/round26/` (SYNTHESIS: [`analysis/round26/SYNTHESIS.md`](analysis/round26/SYNTHESIS.md)):
> **A** fired the built-but-never-swept R19 generators — first-ever scored decodes for **Perl** (G2,
> was zero seeds) and **TeX** (G4, was zero decodes), plus the Py2.7 reducers on the **distinct
> amd64-w64 / non-zero-offset / `skip_by_two`** axis R21-L3 never ran; all control-validated at
> 1.000 recovery, 0 clears over the prior-dense front (dense-from-0 baseline tail still running at
> close-out → row is **partially-run**/interim). **B** executed R12-C2's staged-but-never-run
> 33-keytext running-key sweep skip-aware: **0/1,562** clears, 3 of 9 pages complete at 4 offsets,
> large pages honestly capped into `not_covered` (**partially-run**). **C** enumerated a bounded
> **323-value corpus-semantic seed set × 7 generators × 2 decoders = 4,274 rows at 100 % coverage**
> (incl. the page-56 totient/prime ladder), control min recovery 0.9917, best screen −6.578
> (flat-random), **0 escalated** (**negative**). **D** red-team: **NO-ERROR-FOUND**, coverage×power
> reproduced from raw rows, no silent re-run, no FP-inflation, two MINOR hygiene defects noted.
> **0 oracle flags, no stop-and-alert. OTP-class verdict UNCHANGED — hardened along three
> previously un-swept axes, not overturned.** One loose thread: Lane A's dense-from-0 baseline
> sweep (`analysis/round26/A/sweep.py`) is still running in the background; it only extends the
> same null and finalizes `control.json` on completion.

---

## The one-paragraph state of the board

The standing verdict is unchanged: **LP2 0–54 is OTP-class** — statistically indistinguishable
from a one-time pad under every tested class, with a soft anti-repeat rewrite (~83% suppression)
acting on the ciphertext output. Rounds 18–25 did not move that; they moved the *instrument*, the
*measured status of branches inside it*, and **which of the signed-hint channels have actually
been read.** Round 18 proved the old magnet was broken; Round 19 rebuilt it (drift-tolerant
decoder, nine-register adjudicator, recalibrated nulls — no verdict flips); Round 20 found the sieve
that would make the enumerable-PRNG sweeps affordable **infeasible**; Round 21 found the no-oracle
seal **provably leaky** (best fold 0.80 vs a 0.90 bar → **HIT auto-certification WITHHELD; survivors
flagged-for-oracle**), swept one more Py2.7 slice clean, and measured the `n_skips` window at
**≥ ~6000 runes**. **Round 22 turned away from the letter-stream PRNG branch and, for the first
time, read every channel the signed hints point at** — the hidden message *inside the already-solved
plaintext* (X2, Lane A), the *numbers-as-direction* turtle render (G1, Lane B), the
*koans-as-operations* (X1/X3/X4, Lane C), and the *art-as-data* drop-cap channel (S3, Lane D) — and
**all four came back clean, control-validated NEGATIVES**, with the red-team lane (R) returning
**NO-ERROR-FOUND**. Combined with Round 11 (N1–N5, S1–S2), **every roadmap lens the hints name has
now been read at least once at the tested resolution.** The "we never even looked at the hinted
channels" objection is now **largely closed.** The two branches that could still hide the true pad
are untouched by any of this and remain exactly where they were: the **PRNG/seed tail** (built
byte-exact, unswept, **bounded — not closed**) and the **`/dev/urandom` branch** (untouchable by
construction). The completeness-critic's verdict that round: **the sharpest surviving reopener is
Lane A's printed-line-geometry acrostic — the one representation R22-A could not build — and after
that single cheap task the honest prior on the remaining reopeners is low.**

**Since then (2026-08-30/31):** **Round 23** ran exactly that task — the printed-line acrostic at
the true page-image line breaks, geometry from the same transcription `validate.py` trusts — and
it is a **clean, control-validated NULL** (48 reads, Phase-0 recovery 2/2 = 1.000, 0 family-wise
survivors). Every roadmap-named lens is now read. **Round 24** killed 5 of 8 candidate lanes at
its planning gate and ran the three survivors: the strongest prior B-04 slice re-adjudicated
under **matched-runic + genuinely language-aware scorers** (L7-A axis — clean NULL, 20,480
decodes ×2 lanes), the **`skip_by_two`-capable decoder** re-decode plus its broadening across 7
generator axes (L7-B axis — 245,975 + 113,432 keys, 0 hits, no beam-based negative reopens), and
the date-indexed-pad lane (**premise fails at Step 0**: the unsolved runic pages carry no PGP
signature). **The two conditionals hanging over every historic negative since Round 18 are now
measured through, and the negatives hold.** **Round 25** is the owner-elected compute grind of
the one runnable branch left — the Py2.7-MT 2³² seed tail under the skip-aware decoder —
**PARKED 2026-08-31 at 0.5015 % of 2³² (21,539,647 words), 0 hits, best pmax 6.826 vs bar
7.384**, resumable per-worker from the committed `progress_w{0..5}.json` checkpoints
(`analysis/round25/compute-tail/RESULTS-parked.md`).

---

## What Rounds 23–25 shipped (details)

| round | verdict | one line |
|---|---|---|
| **23** A2 printed-line acrostic | **CLEAN NULL, control-validated** | The last roadmap-named reopener, read at true resolution: 48 reads ({line,word} × {first,last} × {fwd,rev} × {5 pages + concat}) over the validated geometry; family bar −3.597, best real read −6.22; the single per-cell crosser is below the expected-FP count and gibberish. [`analysis/round23/SYNTHESIS.md`](analysis/round23/SYNTHESIS.md) |
| **24** C1 + C1-EXT register axis | **NULL — negatives HOLD** | Matched-runic scorer + language-aware Latin/Greek/OE-poetic/Enochian panels (each proven to beat the English scorer on its own planted language) over the strongest B-04 slice: 0 survivors. The English-only negatives were not hiding a non-English plaintext there. [`analysis/round24/SYNTHESIS.md`](analysis/round24/SYNTHESIS.md) |
| **24** C2 + C2-EXT relation axis | **NULL — no negative reopens** | The `pair`/`keyskip2` decoder (100% plant recovery on `skip_by_two` where the beam gets 25.8%, own bar 7.384) over the top-prior slice + bash/perl/tex/sha-keytexts/offsets/drift-cousin: 359,407 keys total, 0 hits, 8/8 + all controls validated. |
| **24** C8 date-indexed pad | **UNAVAILABLE at Step 0** | The unsolved runic pages carry **no PGP signature**, so the timestamp→offset join key does not exist; steelman probe (630 tests vs the NIST beacon) null anyway. |
| **25** compute-tail | **PARKED, 0 hits at 0.5015 %** | Owner-elected checkpointed grind of the Py2.7-MT 2³² tail; planted-seed control passes every invocation; a live drill proved the HIT path stops all 6 workers. ~25–32 wall-days remain at CPython speed; a GPU/C port does it in hours. [`analysis/round25/SYNTHESIS.md`](analysis/round25/SYNTHESIS.md) |

---

## What Round 22 shipped

| lane | roadmap | verdict | one line |
|---|---|---|---|
| **A** self-embedded read | X2 | **NULL, control-validated** | 3,508 selection functions (every-k / reversed / diagonal folds) over the 5 rig-solved pages' DECRYPTED plaintext; Phase-0 planted-acrostic recovery **1.000**; **0 family-wise survivors** (6 per-cell FPs vs 3.5 by chance = noise). "Seek within" as an acrostic-of-the-solution is clean-negative. **Sharpest reopener:** first-rune-of-each-PRINTED-LINE acrostic using real page-image line geometry (this lane had only the concatenated transliteration). `sweep_results.json`. |
| **B** turtle + spatial | G1, G3 | **CLEAN NULL, 0 flagged-for-oracle** | The value / π(p) / φ(p) stream drawn as a turtle path across **72 render combos**; Phase-0 planted square fires 5/6 geometry stats; 6 shape-stat p<0.01 candidates all fail Bonferroni (2.3e-5) as multiple-comparisons noise; G3 base32/onion/lat-long **POINTER_FOUND=False**. Already merged R22-B + R22-C into `LEDGER.json`. **Reopeners:** G2 non-turtle 2D/columnar reads, other moduli/step-fns, 3D lifts. `g3_results.json`. |
| **C** literal imperatives | X1, X3, X4 | **NEGATIVE, 0 survivors** | **185 enumerated operations** (decimation, cipher-iterate, interleave, reversal, running-key, prime-value/index/totient keystreams) under the 9-register panel-max bar; all 4 Phase-0 controls recover 1.000 (X3b/X4 held-out 1.000). 4 keyed decodes cleared 0.90 recovery but were **correctly rejected at panel-max** — the exact hallucination the recovery gate exists to catch. **X4-totient re-adjudicates Round-11 N5 under the repaired instrument, re-confirms NEGATIVE.** `ledger.json`. |
| **D** illustration / drop-cap | S3 | **NEGATIVE (min p=0.18); RUNNABLE** | First LP2 drop-cap catalog (15/58 illuminated, runes `SLXHXFUMDSFAINGP`); presence/order/gap/centroid/identity clear no p<0.01 Bonferroni bar; controls 4/4 + page0=S. **NOT blocked on assets — page scans are in-repo.** **Reopener:** figural-motif channel (crosses/trees/shrouded-corpse/mayflies) not yet coded as data. `features.json`. |
| **R** red-team | R6 | **NO-ERROR-FOUND** | Independently reconfirmed B's family-wise 0-survivor (P(≥6)=0.072, noise; the 4.7σ 'components' candidate is a discrete-stat z-tail artifact). No lane silently re-reads a Round-11 negative; all nulls seed-3301; no −5.5 relapse; no lane on an unvalidated instrument. One low-severity non-blocking disclosure gap (B's G3 coord-pair ~ Round-11 N2 route (d)) — **fix applied** (B now cites N2). `RESULTS.md`. |

Standing OTP-class verdict unchanged. All five lanes' positive controls fired first; `validate.py`
5/5 before and after; `validate_ledger.py` Unsound-negatives = 0. Merged as `LEDGER.json` entries
**R22-A-SELFEMBEDDED-READ / R22-B-TURTLE-SPATIAL-RENDER / R22-C-LITERAL-IMPERATIVES /
R22-D-ILLUSTRATION-DROPCAP / R22-R-REDTEAM** (130 → 135).

---

## What Round 21 shipped

| lane | verdict | one line |
|---|---|---|
| **L1** seal (real-mode no-oracle proxy) | **KILL — gate provably leaky** | The disjoint-fold proxy lifts correct-key EN_NOVOWEL catch from the single-cut **0.33 → 0.80** (genuine-safe, k=5/min) / **0.87** ceiling (genuine-unsafe), but **no cell reaches the pre-registered 0.90** and the winning cell's false-reject drifts **0.00 → 0.167** on a fresh held-out surrogate. Positive controls fired first (45/45 hallucination reproduction, 15/45 single-cut baseline, 20/20 genuine panel). **Consequence: Round 21 HIT auto-certification WITHHELD — bar-clearing survivors are flagged-for-oracle.** Seal open to a *non-fold* family. `catch_surface.json`. |
| **L3** Py2.7 reducers + amd64 map | **CLEAN NEGATIVE** | **884,000 words**, 0 hits, across `grb5_mod`/`grb5_rej`/`shuffle29` (i386) + `random29` (amd64 2-word init) — the reducer axis + 64-bit ABI map S-G3 left open. **4/4 positive controls recover 1.000 (pmax 28.3, rank-1)**; best decode **pmax 6.248 vs the 7.634 bar** (1.39 below). All 45,975 prior-dense words covered per config. **Bounded, not closed** (>99.99% flat-prior tail ≈61 core-days + 2⁶⁴ amd64 image + inherited S-G3 gaps). `reducers_sweep.jsonl`. |
| **L2** `n_skips` crossover length | **MEASURED — L\*=6000** | On the exact `keyskip1` relation, `n_skips` crosses from non-separating to separating at **L\*=6000** (bracket (3600,6000], holds at 9000/12956); correct-key overtakes the wrong-key *mean* at L≈1000 but clears the 1% right *tail* only at 6000. **Any whole-book / concatenated-page n_skips adjudication needs a window ≥ ~6000 runes.** `drift` "separation" is a LEFT-tail artifact; `skip_by_two` is beam-unrepresentable (crossover None). Plant recovery ≥0.998 at every L; R20 endpoints reproduced. `nskips_crossover.json`. |
| **L5** red-team | **MIXED** | Confirms the **L1 KILL** independently; **NO-ERROR-FOUND** on (b) no silent re-run of foreclosed lanes, (c) the 2.5×10⁶ sieve × panel-max FP inflation is **not** re-introduced (fold machinery FP-neutral, sweeps unscreened), (d) the row gate is honest (score alone can never be a HIT). FP-inflation conditional stands exactly as R left it in Round 20, binding on any FUTURE screened sieve only. |

Standing OTP-class verdict unchanged. All four lanes' positive controls fired first and passed;
`tests/validate.py` 5/5 before and after; `validate_ledger.py` Unsound-negatives = 0. Merged as
`LEDGER.json` entries **R21-L1-SEAL / R21-L2-NSKIPS-CROSSOVER-LENGTH / R21-L3-PY27-REDUCERS /
R21-L5-REDTEAM-SEAL** (126 → 130).

---

## What Round 20 shipped

| lane | verdict | one line |
|---|---|---|
| **P1** sieve | **INFEASIBLE** | Best simultaneous survival at ≥100× reduction on CY + half-vowel English = **0.667** (Wilson95 UB 0.85 < 0.90 bar). The multi-register lever *works* — it lifts vowel-dropped English **0.000→0.800**, half-vowel **0.067→0.667**, Welsh **0.300→0.733** off the English-only floor — but cannot reach 0.90 on a 24–32-rune decrypt head. `survival_surface.json` published. |
| **P2** `n_skips` null | **2 of 3 PASS** | `nskips_null.json` built (seed 3301, order-preserving) + `SWEEPROW/2` wired; the positive control does **not** separate at page-window lengths (separation appears only at full-book scale). |
| **P3** null/seed/drift | **PASS ×3** | Panel-max direct null `panelmax20.json` (correct-key power **1.00** / wrong-key 0.00 on LP1_REAL/LATIN/OE/half-vowel); seed prior `seedprior20.json` (**433** candidates, rank 1 = **1325734783**); drift re-baseline confirms OE `pmax` shortfall (13.543 vs 13.842) and the fragile-decode-channel bound. |
| **R** red-team | **NO-ERROR-FOUND / FOUND-ERROR (latent)** | No power leak on a structured wrong-key null (survival 0.000). **But** sieve × panel-max FP interaction inflates the survivor FP to **0.025/decode** vs the nominal **1e-8** — a 2.5×10⁶ inflation any future sieve must correct. |
| **N1** PDF/font hunt | **NEGATIVE** | No surviving LP PDF/PostScript with a runic text-layer or embedded font subset in 195 local PDFs or across the 4 named mirrors; the S-TEX `allrunes` promotion trigger did **not** fire. |
| **N2** haplography | **NO-ERROR-FOUND** | ~20 doublet-site merges do **not** reopen autokey; the positive refutation is hardened. |
| **C** closeout | **DONE** | L1-prior corrections propagated to source; nav docs + this file. |

Because Phase S was hard-gated on **P1∧P2∧P3 all PASS** and P1 failed, **no S-lane scored a single
decode.** The PRNG sweeps are exactly where Round 19 left them.

---

## What is still OPEN (ranked after Round 22; per-item updates through Round 25 marked inline)

> **Completeness-critic finding (this round's roadmap Phase-6 pass).** The six untouched roadmap
> lenses that justified Round 22 — **S3, X1–X4, G1-turtle** — are **now all read** (Round 22 lanes
> A/B/C/D), each a control-validated NEGATIVE. Combined with Round 11 (N1–N5, S1–S2), **every roadmap
> lens the signed hints name has been read at least once at the tested resolution.** The
> high-prior novel-channel budget is therefore mostly spent — what remains are **resolution gaps
> inside those reads**, not new channels. The doctrine's optimism clause (§5) is real, but all three
> of this project's past reopenings came from **auditing an instrument or a closure**, never from one
> more framing of an already-read channel — and two of the three Round-23 threads (D2, B2) are the
> latter. **The one thread worth running is A2** (item 0): a first-rune-of-each-PRINTED-LINE acrostic
> using the real page-image line geometry, the single representation R22-A could not build and the
> most conventional hiding spot for a self-embedded message. It is cheap (a transcription task + a
> re-run of R22-A's validated sweep) — **an afternoon, not an armada.** See
> `analysis/NEXT-ARMADA-ROADMAP.md` → "ROUND 23 SEED" for the honest-prior judgment.

0. ~~**[highest surviving novelty × prior] A2 — printed-line-geometry acrostic (from R22-A
   `not_covered`).**~~ **RUN — Round 23 closed it: CLEAN NULL, control-validated**
   (`analysis/round23/A2-line-acrostic/`, ledger `R23-A2-LINE-ACROSTIC`). The original text is
   kept below because its reasoning still ranks D2/B2 correctly (both remain un-run and
   low-expectation). R22-A read every-k / diagonal / substring selections of the concatenated solved
   plaintext and returned a control-validated NULL, but it could **not** reach the one representation
   a human calligrapher's message would most likely use: **the first rune of each PRINTED LINE (and
   per-word) acrostic, using the true page-image line breaks + word spacing.** R22-A had only the
   concatenated transliteration; the physical layout is unreconstructed. This reuses R22-A's
   validated acrostic recognizer (recovery 1.000) — only the input geometry changes — so it needs
   just a line-break transcription of the 5 solved pages plus a re-pointed Phase-0 control. **The
   single place a self-embedded read could still hide.** Then D2 (figural-motif channel, gated on
   building a control-validated motif extractor first) and B2 (non-turtle 2D/columnar reads at true
   line width, Lane G2) are cheap-to-run but **low-expectation** — see the Round 23 seed.

1. **~~S-G3 Python 2.7 `random.seed(<string>)`~~ — the reducer + amd64-map axis is now SWEPT
   (Round 21 L3, CLEAN NEGATIVE).** 884,000 words across `grb5_mod`/`grb5_rej`/`shuffle29` (i386) +
   `random29` (amd64 2-word init), 0 hits, best pmax 6.248 vs 7.634. **What remains is a
   stated-fraction negative that is bounded, not closed:** >99.99% of each config's 2³² flat-prior
   tail (~61 core-days for all four full enumerations), the full 2⁶⁴ amd64 hash image, and the
   inherited S-G3 family gaps — other decoder relations (`skip_by_two`/`keyskip2`), non-panel
   registers, PYTHONHASHSEED/`-R` randomized hash, WichmannHill, float/jumpahead seeds, Python
   2.6/2.5. `random29/i386-1word` was already S-G3-covered (round20) and was deliberately **not**
   re-run. Reopens the moment someone spends the core-days or validates a new Py2.x seed family.
   Measured in `analysis/round21/L3-py27-reducers-plus-64bit-map/`.
   _Update (Rounds 24–25):_ the `skip_by_two`/`keyskip2` relation gap named here is now covered
   for the prior-dense slices (R24 C2 + C2-EXT, 359,407 keys, 0 hits), and the `random29` flat
   tail is being ground directly — Round 25 parked at **0.5015 % of 2³²**, resumable
   (`analysis/round25/compute-tail/`).

2. **The no-oracle held-out SEAL is provably leaky — HIT auto-certification is WITHHELD (Round 21
   L1, KILL).** No disjoint-fold cell in the swept grid reaches ≥0.90 catch at ≤0.10 false-reject on
   held-out data (best 0.80 genuine-safe / 0.87 ceiling; held-out false-reject 0.167). **Until a
   no-oracle gate that clears 0.90 exists, any bar-clearing real-mode survivor from any sweep is
   flagged-for-oracle, never auto-certified as a solve.** The fold family alone is bounded at
   ~0.82–0.87; the seal is **still open to a NON-fold proxy** — a longer decrypt head than the 24–32
   rune head that capped R20 P1, a per-register fold bar, or a learned self-consistency gate. A
   `keyskip1`-relation hallucination population (the exact-preset overfits used here do not populate
   the relation axis) would also extend the surface. Measured in
   `analysis/round21/L1-seal-realmode-proxy/` (`catch_surface.json`).

3. **Fix the sieve × panel-max FP inflation (R's Round-20 FOUND-ERROR) before trusting any screened
   sweep.** Screened survivors carry a **2.5×10⁶ FP inflation** against the nominal panel-max bar.
   Any future P1-style sieve must either re-derive the null *on the screened population* or apply the
   measured correction. Until then, sweep **unscreened** (as R21 L3 did) or carry the inflation as an
   explicit conditional. **Round 21 L5 confirmed this item is NOT re-introduced** — R21's sweeps are
   unscreened and the fold machinery is FP-neutral (exactly one pmax evaluation per decode) — so it
   stands exactly as R left it, binding on any FUTURE screened sieve only.

4. **The sieve itself — is 0.90-at-100× the right bar?** P1 is infeasible *for that gate*. A future
   round could (a) lower the reduction target (e.g. 30× instead of 100×) if compute allows, (b) use a
   longer decrypt head than 24–32 runes (the signal ceiling that capped the hard registers), or
   (c) accept a per-register sieve with published leakage. `round20/P1/survival_surface.json` has the
   full surface to decide with numbers.

5. **P2's `n_skips` separation appears only at full-book scale — Round 21 L2 measured the
   crossover length: L\* = 6000 (≈11–12 pages) on the exact `keyskip1` relation.** At page-window
   lengths the statistic does not separate planted from wrong-key; it first clears the FPR=0.01
   two-sided bar at **L=6000** (bracket (3600, 6000], holds at 9000/12956), while the correct-key
   footprint overtakes the wrong-key *mean* already at L≈1000 but does not clear the 1% right *tail*
   until 6000. So any concatenated-page / whole-book `n_skips` adjudication must use a window of
   **≥ ~6000 runes** before `n_skips` **alone** is valid; below that, combine with the P3a panel-max
   score or enlarge the window. **Two channels do NOT give this crossover honestly and must not be
   read as page-scale discriminators:** the `drift` permissive beam fabricates huge wrong-key skip
   counts so the correct key sits in a LEFT-tail artifact at every L; and `skip_by_two` (R18 L7-B)
   the beam cannot represent, recovering 0 skips. Measured in
   `analysis/round21/L2-nskips-crossover-length/` (`nskips_crossover.json`, RESULTS.md); plant
   recovery ≥0.998 at every L; R20 endpoints (L=400 no-sep, L=12956 sep@0.999) reproduced.

6. **The remaining enumerable families stay sieve-gated and unswept:** bash `$RANDOM` (77.6M
   auto-seeded orbit, ~28 min), Perl 5.14 (2³², ~34 h full or a stated-fraction sample), TeX LCG
   one-cycle (~18 h), Marsaglia held units (679 units, ~21 CPU-h). None is closed. Each reopens the
   moment a sieve reaches the target *or* the coordinator accepts an unscreened stated-fraction sweep.
   *(Note: the doctrine and the completeness-critic both counsel against leading Round 22 with these —
   they are more of the same letter-stream sweep at a flat prior; queue them behind item 0.)*
   _Update (2026-08-31):_ their **prior-dense fronts** were swept clean under the skip-aware
   decoder in R24 C2-EXT (bash/perl/tex axes, 0 hits); the full tails remain compute-only.
   Two housekeeping sub-items surfaced by the Round-21 synthesis (filed late) also live here:
   **(a)** Round 21's planned **L4** never ran — the glibc `gen=0` full-32 row
   (`LEDGER.json:R19-G3-CORRECTION`) is still the one open row, and `gen=7`/`gen=8` are still
   un-re-adjudicated through I1+I2; **(b)** Round 21's planned **L6** never ran — the sieve
   reopening decision from `round20/P1/survival_surface.json` (carry Perl/TeX/Marsaglia as
   stated-fraction unscreened samples, or name the lowered feasible operating point) costs no
   compute and has now been deferred twice.

7. **The `/dev/urandom` branch is untouched and untouchable.** If the pad was a CSPRNG or hardware
   draw, nothing in any round recovers it. A clean negative on the enumerable families does **not**
   touch this branch — it only shrinks the "cheap seeded PRNG" hypothesis. This branch is real and may
   be the true one (doctrine §5); leave it untouched.

---

## Open governance item the coordinator must decide (C-canon)

**Should the 3 changed payload bytes (idx 45, 50, 246 → `payload_resolved.bin`) become canonical?**
Round 19 C1 corrected them and re-ran B-05 clean, but **B-04 / R16-KDF / R17 are input-sensitive
downstream** of the payload bytes. Lane C **flags but does not decide** this. If promoted to canon,
those three lanes must be re-checked against the new input and their `LEDGER.json` coverage restated.
Tracked as `LEDGER.json:C-CANON-PAYLOAD-3BYTES` (status `open`).

---

## One transcription candidate flagged for a human (C-eyeball)

**T1 p27:93, U→B, margin 5.** This is the single weakest transcription disagreement Round 19's T1
audit surfaced (canon upheld 450/450 overall, but this cell's margin is thin). It wants a human eye
on the actual glyph, not another automated pass. Not load-bearing for any current verdict, but worth
resolving before the next transcription-dependent sweep.

---

## Do NOT re-run (foreclosed — `ELIMINATION-LEDGER.md:328–384`)

Published-keytext/running-key (doublet-excluded by mechanism); the number channel (Round 11, 7 lenses
NULL); OSINT/AN-END retrieval (unreachable by construction); attribution-to-a-name (359-word corpus
< floor); stego/LSB/OutGuess/red-rune re-runs; autokey/ciphertext-feedback (positively refuted — the
one live reopener, A-03 haplography, was checked NEGATIVE by Round 20 N2); any ciphertext-only sweep
under a flat prior, a rigid decoder, or an English-only scorer. Before opening any lane, query
`LEDGER.json` `coverage`/`not_covered`, not `status`.
