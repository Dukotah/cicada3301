# Round 19 — "FIX THE MAGNET, THEN SWEEP THE SMALL HAYSTACK"

_Opened 2026-08-26. Thirteen lanes in four phases. Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md)._

## The thesis

Round 18 found that this project has been searching with a broken magnet:

- **L7-A** — handed the **correct key**, the beam recovers 100 % of runes for Latin, Old
  English, German, Welsh and abbreviated English, and the English quadgram adjudicator then
  calls the result noise. Measured power: **0.33** Latin, **0.00** vowel-dropped English (where
  the correct key scores *below* a deliberately wrong one). ~10¹⁰ decodes of published coverage
  are **English-only** coverage, and Round 10b's language-agnostic-statistic requirement had
  **0/15 compliance**, so none of it can be retro-fitted.
- **L7-B** — the beam admits a key skip only if every skipped position would have reproduced the
  previous cipher rune. That is exact for `encipher_keyskip` and **nothing else**.
  `skip_by_two` — the rejection sampler burning two draws instead of one, a one-character change
  to a plausible 2013 loop — **reproduces LP2's doublet rate** (0.84 % vs 0.664 % observed) and
  the correct key scores **−6.90 at 25.8 % recovery**. Beam width 1000 and `max_skip` 8 change
  that by *exactly* 0.000, because it is not a search-depth failure.

Put together: **if the true key were already inside the swept set, the sweep would probably have
thrown it away.** Meanwhile **L1** produced this project's first evidence-derived prior — an
Ubuntu 11.04–12.04 workstation, GnuPG 1.4.11 unchanged for three years, ImageMagick over
Ghostscript, a 6×9-inch typeset PDF — which promotes four generator families that have **never
been swept**, two of which are **fully enumerable**.

So Round 19 is not a bigger sweep. It is: **repair the decoder, repair the adjudicator,
recalibrate the nulls, and then run the small, high-prior, enumerable spaces through the
repaired instrument.** Per doctrine §3 the budget is ~30 % instrument, ~40 % high-prior lanes,
~20 % red-team, ~10 % closeout.

This is the most optimistic round since Round 12, and the reason is concrete: for the first time
the project has (a) an instrument whose blind spots are *measured*, (b) a prior derived from
physical evidence rather than lore, and (c) target spaces small enough to **enumerate rather
than sample**.

## The hard dependency

**No Phase 2 lane scores anything until all three Phase 0 gates PASS.** Sweeping with the
current instrument is precisely the mistake this round exists to correct. Phase 1 lanes build
and validate their generators concurrently and **hold at the scoring boundary**.

```
 PHASE 0  instrument   I1 driftbeam ──┐
                       I2 adjudicator ─┼── gates PASS ──> PHASE 2  S1 sweep / S2 re-adjudicate
                       I3 thresholds ──┘                     ^
 PHASE 1  generators   G1 G2 G3 G4  ── keystreams + validation ┘   (concurrent, no scoring)
 PHASE 3  red-team + closeout  R1 C1 C2 C3                          (concurrent, independent)
```

## Lanes

### Phase 0 — INSTRUMENT (blocking)

| id | name | the gap it closes |
|---|---|---|
| **I1** | DRIFT-TOLERANT DECODER | L7-B. Generalise the beam's transition relation to cover `skip_by_two`, free drift, and unrepresentable key advances — without losing power on the baseline construction or admitting wrong keys |
| **I2** | MULTI-REGISTER ADJUDICATOR | L7-A. A register panel (EN / LP1-orthography / Latin / OE / DE / CY / half-vowel / no-vowel) plus the four language-agnostic statistics doctrine R3 makes mandatory, behind one `adjudicate()` call and one `SWEEPROW` schema |
| **I3** | NULLS & THRESHOLDS | `threshold_for()` is calibrated for the English quadgram scorer alone. A 9-way max-over-panel statistic inflates the null; without recalibration I2 converts a power problem into a false-positive problem |

### Phase 1 — GENERATORS (concurrent; validation only)

Every generator must **reproduce the real library byte-exactly** before it may produce a
keystream — the standard Round 8 set. All four are named in `round18/L1-toolchain/RESULTS.md`
§6.2 as ranked *above* families already swept.

| id | family | L1 rank / shift | status |
|---|---|---|---|
| **G1** | bash `$RANDOM`, glibc `rand()`/`random()`/`drand48` | rank 1 (×3) and rank 4 (×2) | `random()` ~3 % swept; `$RANDOM` **never swept, enumerable** |
| **G2** | Perl 5.14 `rand`/`srand` | rank 3 (×2.5) | **never swept** |
| **G3** | Python **2.7** `random.seed(<string>)` | rank 2 (×3) | silent coverage hole — Py2 and Py3 hash seed strings differently |
| **G4** | TeX/LaTeX-internal LCGs (`\pgfmathrandom`, `lcg`, `random.tex`) | rank 5 (×2) | **never swept, never considered; fully enumerable** |

### Phase 2 — THE SWEEP (gated on Phase 0)

| id | name | what |
|---|---|---|
| **S1** | ENUMERATE | G1–G4 keystreams through I1 + I2, writing the full `SWEEPROW` for every decode. Enumerate where enumerable; state the covered fraction where not |
| **S2** | RE-ADJUDICATE | The highest-prior slice of already-swept space (B-04 top seeds, R16-KDF top configs, R17 top offsets) re-run through the repaired instrument. The only route to recovering any value from 10¹⁰ discarded decodes |

### Phase 3 — RED-TEAM + CLOSEOUT (concurrent, independent)

| id | name | what |
|---|---|---|
| **R1** | RED-TEAM ROUND 19 | Doctrine R6. Target: **this round's own instrument**. The obvious failure mode of I1 is that a permissive transition relation lets *wrong* keys score as English; attack that, and attack I2's panel for register-shopping inflation. Verdict: FOUND-ERROR / NO-ERROR-FOUND |
| **C1** | CLOSEOUT L5 — PAYLOAD | A-04 (6 contested pp49–51 bytes) + E-01 (7A35090F moduli). Artifacts on disk; `RESULTS.md` is a TBD skeleton |
| **C2** | CLOSEOUT L6 — OFFSET & MARSAGLIA | B-02 (every sweep assumed key index 0 = rune 0) + the Marsaglia CDROM. 1.2 GB fetched, PREREG written, **no results** |
| **C3** | CLOSEOUT L3 + L8 | L3 ornament bands (109 records, 30 with n ≤ 16) reader; L8 PGP verification table has data and **no `RESULTS.md`** |

## Rules for every lane

1. **Read `liber-primus/ARMADA-DOCTRINE.md` first.** Answer the **Aiming Test** (five questions)
   in your `PREREG.md` before you measure anything. A lane that cannot answer all five does not run.
2. **Pre-register.** `round19/<LANE>/PREREG.md` — hypothesis, instrument, positive control, null,
   pass/fail threshold. Never edit a threshold after seeing a result; append a dated addendum.
3. **A null from an unvalidated instrument is not a negative.** Plant, prove recovery, then trust
   silence. State the control's measured recovery in `RESULTS.md`.
4. **Report all three conditionals** on any negative: key space, decoder transition model,
   adjudicator register. A negative missing one of the three is not a result.
5. **Report coverage × power, never coverage alone.**
6. **Store the `SWEEPROW`** (I2's schema) for every decode a sweep scores. Doctrine R3, CI-enforced.
7. **Never rigid-decode LP2.** `pytest liber-primus/benchmark/ -k rigid_scores_correct`.
8. **Score on rune indices, not the transliteration string** (7 of 29 runes are 2 chars).
9. **Do not re-run measured ground.** Query `LEDGER.json`; read `coverage`/`not_covered`, not `status`.
10. **Bounds, not verdicts.** No "exhausted", "closed", "unsolvable". End with what was measured,
    what was not covered, and the condition that reopens it.
11. **Write files; do not `git commit`.** Thirteen lanes share one worktree; the coordinator commits.
12. Append your ledger entry to `round19/<LANE>/ledger.json` for merge into `liber-primus/LEDGER.json`.

## Environment

Run Python through WSL: `wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/dukot/projects/cicada3301 && python3 ..."`
(Python 3.14, numpy/scipy present). Trust anchor before and after your lane:

```bash
python3 liber-primus/tests/validate.py        # ALL VALIDATIONS PASSED (5/5)
python3 -m pytest liber-primus/benchmark/ -q  # 8 gates
```
