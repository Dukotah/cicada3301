# Round 21 — SYNTHESIS (bounds, not a verdict)

_Written 2026-08-31 by the coordinator, from the four lane `RESULTS.md` files as they were
filed on 2026-08-29. Doctrine [`ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) R7: this document
states what was measured and what would reopen each thread. It contains no "exhausted / closed /
unsolvable." Trust anchor `python tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)**; test
suite `python -m pytest -q -m "not network"` → **85 passed**; `validate_ledger.py` Unsound
negatives = **0**._

> **Filed late.** Round 21's lanes wrote their results in August 2026 but the round never got an
> exit document, so its two load-bearing facts — the KILL on the no-oracle seal, and the fact that
> two of its six planned lanes never ran — lived only inside lane folders. This file closes that
> gap. It reports no measurement that was not already in a lane `RESULTS.md`.

---

## 0. The one-line result

Round 21 set out to **seal the no-oracle hit gate and then spend compute on the named, enumerable
cells the ledger itself called un-measured at power.** The seal **failed at its own frozen bar**
— so HIT auto-certification is withheld and every bar-clearing survivor from this round onward is
*flagged-for-oracle*, never auto-certified. The compute lanes that did run came back **clean at a
stated fraction with power 1.00**, and one instrument lane produced the single number two previous
rounds had asked for (`n_skips` crossover **L\* = 6000**).

**There is no HIT.** No decode in this round cleared the three-clause gate; the best decode over
884,000 words reached pmax **6.248** against a **7.634** bar.

---

## 1. What ran, and what did not

| lane | planned | ran | verdict |
|---|---|---|---|
| **L1** seal the real-mode held-out proxy | yes | **yes** | **KILL** — the no-oracle gate is provably leaky |
| **L2** `n_skips` power-crossover length | yes | **yes** | **MEASURED** — L\* = 6000 |
| **L3** the three unswept Py2.7 reducers + the amd64 2-word map | yes | **yes** | **CLEAN NEGATIVE** at a stated fraction |
| **L4** the open glibc `gen=0` full-32 row + re-adjudicate `gen=7`/`gen=8` | yes | **NO — never run** | no result; the row stays open |
| **L5** red-team the seal and the not-a-re-run justification | yes | **yes** | **MIXED** — 1 FOUND-ERROR-class, 3 NO-ERROR-FOUND |
| **L6** sieve-survival reopening decision + closeout | yes | **NO — never run** | the R20 P1 reopening decision is still un-made |

**Two of six lanes never ran, and this is the first document to say so.** Their absence is not a
negative and must not be read as one:

- **L4 — the one open glibc row.** `LEDGER.json:R19-G3-CORRECTION` `not_covered` still reads
  "still absent, still the one open row" for `gen=0` (`random()%29`) over the full 2³², and
  `gen=7`/`gen=8` were still never re-adjudicated through I1+I2. Round 21 planned to close this to
  a stated-fraction bound and did not. **Coverage of that cell after Round 21 is exactly what it
  was after Round 19: zero at power.**
- **L6 — the sieve reopening decision.** R20's `survival_surface.json` was published so a
  coordinator could decide, with numbers and no new compute, whether to (a) carry Perl/TeX/Marsaglia
  as stated-fraction *unscreened* samples or (b) name the lowered operating point at which ≥0.90
  survival is reachable. **That decision was never recorded.** It costs no compute and is still
  the cheapest open item in the project.

---

## 2. L1 — the no-oracle seal: KILL (this is the round's load-bearing result)

Round 20 shipped `hitfn20.is_hit`, whose clause 3 asks whether a key attributed on ¼ of a page
reproduces on the held-out ¾. In **strict** mode (a plaintext oracle available) it catches 45/45
planted EN_NOVOWEL hallucinations. In **real** mode — the only mode a genuine LP2 candidate can
ever be judged in — R20's own S-RESCOPE audit measured the catch at **15/45 (33 %)**. L1's job was
to lift that to ≥0.90 using multiple disjoint held-out folds.

**It could not.** The fold family improves the catch enormously and still misses the bar:

| k | rule | catch | false-reject | ≥0.90 catch? | FR ≤0.10? |
|---|---|---:|---:|---|---|
| 2 | min / mean / frac | 0.422 | 0.05 | no | yes |
| 3 | min | 0.667 | 0.25 | no | **no** |
| 4 | min / frac_pass | 0.756 | 0.15 | no | **no** |
| **5** | **min** | **0.800** | **0.00** | **no** | yes ← best genuine-safe cell |

`SEAL_PASS = false` (`tuning_pass=false`, `heldout_surrogate_pass=false`). The best genuine-safe
cell also **fails to generalise**: on a fresh order-preserving surrogate population its
false-reject drifts to **0.167**, over the 0.10 cap.

**Positive controls fired first and passed** — the 45-case hallucination population reproduces
bit-identically, the single-cut baseline reproduces the exact 15/45 leak this lane targeted, the
20/20 genuine panel recovers at ≥0.971, and `panelmax_bar` returns the same 7.634. So the KILL is a
measured bound from a validated instrument, not silence from a dead one.

**Consequence, and it binds every later round:** per the frozen Q5 kill clause, **HIT
auto-certification is WITHHELD.** A bar-clearing survivor is reported as *flagged-for-oracle*.
High-prior lanes still run — coverage × power bounds are unaffected — only the act of calling
something a solve without an oracle is withheld.

**Not covered / reopening.** The fold *family* is bounded here at roughly 0.82–0.87 catch. The seal
remains open to a **non-fold** proxy: a decrypt head longer than the 24–32 runes that capped R20's
P1, a per-register fold bar, or a learned self-consistency gate. The hallucination population used
is `exact`-preset EN_NOVOWEL only; a `keyskip1`-relation population would extend the surface. Not
measured: k=6, the `frac_pass` rule, the `drift_rec` relation, registers other than EN_NOVOWEL,
screened sweeps.

---

## 3. L2 — `n_skips` crossover length: L\* = 6000

R20's P2 proved `n_skips` has **zero** page-window (L ≤ 400) power and 0.999 full-book (L = 12956)
power, and named the crossover length as the one number a future adjudication needs. Both R20 §7
and §8.5 listed it top-3. L2 measured it.

| L | correct | null mean | null q99 | two-sided p | recovery | separates at FPR 0.01? |
|---:|---:|---:|---:|---:|---:|:--|
| 400 | 6 | 8.87 | 19 | 0.520 | 1.000 | No _(reproduces R20)_ |
| 1200 | 34 | 27.56 | 46 | 0.400 | 1.000 | No |
| 3600 | 94 | 82.12 | 107 | 0.267 | 0.999 | No |
| **6000** | **198** | **139.36** | **176** | **0.000** | **0.999** | **Yes ← crossover** |
| 12956 | 418 | 296.99 | 350 | 0.000 | 0.999 | Yes _(reproduces R20)_ |

The Q1 gate passed first — both R20 endpoints re-derived from the same machinery before any
intermediate L was trusted — and plant recovery is ≥0.998 at every ladder point.

**The usable bound:** any concatenated-page or whole-book `n_skips` adjudication must use a window
of **≥ ~6000 runes (about 11–12 pages)** before `n_skips` **alone** is a valid discriminator under
the exact decoder. Below that it is not. The correct key overtakes the wrong-key *mean* around
L ≈ 1000–1200 but does not clear the 1 % right *tail* until 6000.

**Two channels must not be read as page-scale discriminators.** The `drift` permissive beam
fabricates large wrong-key skip counts, so the correct key sits in a **left-tail artifact** at
every L — that is not separation. And `skip_by_two` is beam-unrepresentable, so it recovers no
skips and has no crossover at all.

**Not covered:** rejection loops other than keyskip / skip_by_two (each has its own curve); Ls
between ladder points (the crossover is bracketed to (3600, 6000], not pinned to the rune); null
sizes beyond M=300.

---

## 4. L3 — the three unswept Py2.7 reducers + the amd64 map: CLEAN NEGATIVE

S-G3 (Round 20) swept only the `random29` reducer on the i386 1-word map. L3 finished the axis.

| config | reducer | map | words screened | fraction of 2³² | survivors | **hits** | max pmax | full-2³² cost |
|---|---|---|---:|---:|---:|---:|---:|---:|
| grb5_mod_i386 | `getrandbits(5) % 29` | i386 1-word | 288,000 | 0.006706 % | 21 | **0** | 6.089 | 10.9 core-days |
| grb5_rej_i386 | `getrandbits(5)` reject 29–31 | i386 1-word | 216,000 | 0.005029 % | 25 | **0** | 5.260 | 14.3 core-days |
| shuffle29_i386 | repeated `shuffle(range(29))` | i386 1-word | 186,000 | 0.004331 % | 24 | **0** | 6.248 | 18.4 core-days |
| random29_amd64 | `int(random()*29)` | **amd64 2-word** | 194,000 | 0.004517 % | 25 | **0** | 5.341 | 18.0 core-days |
| **TOTAL** | | | **884,000** | — | **95** | **0** | **6.248** | ~61 core-days |

All four positive controls recover their planted key at **recovery 1.000, rank 1, pmax 28.268**,
far above the 7.634 bar — a measured negative from a validated instrument. In every config the
**entire 45,975-word prior-dense front** (the 433 P3b seeds plus the top-64 ±512 neighbourhoods)
was screened *first and in full*, so the highest-prior region of each config is completely covered
and the uncovered remainder is the flat-prior tail.

Sweeps ran **unscreened** — no P1 sieve — which is why R20-R's ~2.5×10⁶ FP-inflation condition
does not apply to them.

**Bounded, not closed.** >99.99 % of each config's 2³² flat-prior tail remains (~61 core-days for
all four full enumerations), plus the full 2⁶⁴ amd64 image and every gap S-G3 already carried:
other decoder relations (`skip_by_two`), non-panel registers, `PYTHONHASHSEED`/`-R` randomized
hash, WichmannHill, float/jumpahead seeds, Python 2.6/2.5. `random29`/i386 was already S-G3-covered
and was deliberately **not** re-run.

---

## 5. L5 — red-team (doctrine R6): MIXED

The mandatory positive control passed first: the harness detects a known-leaky seal on fresh,
unseen data (single-cut proxy caught 0.289 of a fresh hallucination population, matching the 33 %
on-disk baseline). So every verdict below rests on a validated audit instrument.

| # | attack | verdict | finding |
|---|---|---|---|
| **(a)** | Is L1's fold seal overfit — does it seal at all? | **L1-KILL** | No fold cell reaches ≥0.90 catch without false-reject >0.10, **on its own tuning population**, before overfit is even reachable. Independently confirms L1. |
| **(b)** | Are the named L3/L4 cells genuinely un-measured *at power*? | **NO-ERROR-FOUND** | All 6 checked cells are named un-measured-at-power in `coverage`/`not_covered`; the prior sweep was a rigid −12.5 decoder = zero power. No silent re-run. |
| **(c)** | Does the fold machinery re-introduce the sieve × panel-max FP inflation? | **NO-ERROR-FOUND** | The fold proxy feeds clause 3 only and never touches `pmax` or screening; exactly one `AD.adjudicate` call per decode regardless of `k_folds`; sweeps run unscreened. The 2.5×10⁶ inflation is not re-introduced. |
| **(d)** | Can any row be a HIT on score alone (defect d re-opened)? | **NO-ERROR-FOUND** | Every row routes through `hitfn20.is_hit`, which requires `clears_null` ∧ `recovery ≥ 0.90` ∧ `heldout ≥ 0.90`; `validate_row_v3` raises on a lying HIT row. |

Note the shape of (b): it verified the cells **L3 and L4** would cover. L3 ran; **L4 did not**, so
that half of the clearance was never spent.

---

## 6. What Round 21 moved, and what it did not

**Moved.** The trustworthiness of the hit gate is now *measured* rather than assumed, and measured
unfavourably — which is worth more than an unexamined gate. One more named axis of the Py2.7 family
is swept clean at power 1.00 over its prior-dense front. The `n_skips` window question that two
rounds had deferred is answered with a number.

**Did not move.** The standing verdict — **LP2 0–54 is OTP-class**, statistically indistinguishable
from a one-time pad under every tested class, with a soft anti-repeat rewrite acting on the
ciphertext output — is unchanged, by construction: 884,000 words out of 2³² per config cannot move
it. The `/dev/urandom` branch is untouched and remains untouchable. The glibc `gen=0` row is still
open because L4 never ran. The sieve reopening decision is still un-made because L6 never ran.

---

## 7. Live threads leaving Round 21

1. **Make the L6 decision. It costs nothing.** `round20/P1/survival_surface.json` is published;
   decide in writing whether Perl/TeX/Marsaglia are carried as stated-fraction unscreened samples,
   or name the lowered operating point (30× reduction, or a longer decrypt head) at which ≥0.90
   survival is reachable. This is the cheapest open item in the project and it has now been
   deferred twice.
2. **Run L4, or restate the glibc row honestly.** `gen=0` (`random()%29`) full-32 is still the one
   open row, and `gen=7`/`gen=8` are still un-re-adjudicated through I1+I2. Either sweep a stated
   fraction through the current gate, or record in `LEDGER.json` that Round 21 planned it and did
   not run it — this document does the latter in the meantime.
3. **The seal needs a non-fold family.** The fold family is measured out at ~0.82–0.87. Until some
   no-oracle gate clears 0.90 at ≤0.10 false-reject, no sweep in this project may call a survivor a
   solve without an oracle.

_Standing condition, unchanged: do **not** re-enable a P1-style sieve without first re-fitting the
panel-max null on **screened** wrong keys (~2.5×10⁶ FP inflation otherwise). Round 21's sweeps were
unscreened, so this remains binding on future work only._
