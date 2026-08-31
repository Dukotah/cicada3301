# Round 22 — Lane C — RESULTS: the four literal imperatives (X1 + X3 + X4)

_Run 2026-08-29. Pre-registration frozen in [`PREREG.md`](PREREG.md) before any LP2 scoring.
Recognizer = the Round-19/20 instrument stack (never −5.5). Machine record: [`ledger.json`](ledger.json)._

## Trust anchor

`python3 tests/validate.py` → **ALL VALIDATIONS PASSED** (reproduces every solved page). The
lane touched no instrument; the anchor is unaffected.

## Headline

**NEGATIVE across all three sub-lanes, all four Phase-0 positive controls PASSED, 0 survivors.**
185 enumerated operations over LP2 0–54 (12,956 runes); every one adjudicated by the repaired
9-register panel-max bar, keyed operations additionally gated by the recovery-gated `is_hit`.
The size-matched seed-3301 null produced **0 bar-clears and 0 hits** too — the real stream is
statistically indistinguishable from its histogram-preserving shuffle under every operation.

## Phase 0 — plant-and-recover (each operation validated before it was trusted; doctrine Q1/mech 2)

| control | operation proven | recovery | verdict |
|---|---|---|---|
| X1 de-interleave | 4-braid a known English text, X1c de-interleave must reconstruct it | **1.000** | PASS |
| X3a reversal | reverse + re-encipher forward (shift 7); X3a decrypt-the-reversal recovers it | **1.000** | PASS |
| X3b running-key | solved-plaintext as a genuine running key over a known target → `is_hit` | **1.000** (held-out 1.000) | PASS (`is_hit`=True) |
| X4 number-keystream | encipher a known text with a totient(φ) keystream; matching X4 config → `is_hit` | **1.000** (held-out 1.000) | PASS (`is_hit`=True) |

The recognizer itself was independently re-verified live at lane build time (the HITFN guard):
it **REJECTS** the EN_NOVOWEL hallucinating decode (recovery 0.44 strict / 0.83 held-out, pmax
clears on score) and **ACCEPTS** the genuine decode (recovery 1.00, pmax 26.4). So a null from
it is a real negative (doctrine mechanic 2).

## Phase 1 — LP2 0–54 sweep

### Coverage × the best statistic seen (doctrine R2: value = coverage × power)

| sub-lane | operations | best pmax | bar | best recovery | survivors |
|---|---:|---:|---:|---:|---:|
| **X1** (decimation ×4 phases + cipher ladder, iterate ×N, 4-way interleave/de-interleave) | 138 | 1.53 | ~5.09 | — (structural) | 0 |
| **X3a** (reversal re-enciphered forward, cipher ladder) | 31 | 0.57 | ~4.66 | — (structural) | 0 |
| **X3b** (solved-plaintext running key over unsolved, both signs, exact+drift) | 4 | 2.64 (7.35 drift) | 6.39 (11.97 drift) | 0.914 | 0 |
| **X4** (prime/prime-index/totient value as keystream over letters, ±sign, ±atbash) | 12 | 2.97 | 6.39 | 0.974 | 0 |
| **total** | **185** | | | | **0** |

Every X1/X3a decimated or reversed substream keeps IoC·N ≈ 1.00 and min-distinct-32 ≈ 13–14 —
i.e. flat, exactly like the parent stream: a structural rearrangement of a flat mod-29 stream is
still a flat mod-29 stream, and the panel-max never rises above ~1.5 (bar ~5). Nothing near a hit.

### The instructive part: the recovery gate caught the exact hazard it was built for

Four keyed rows recovered **above the 0.90 recovery bar** and were still correctly **rejected**:

| op | recovery | held-out | pmax | bar | failing clause |
|---|---:|---:|---:|---:|---|
| `X4_v_prime_none_sign-1` | 0.974 | 0.974 | 2.39 | 6.39 | clause 1 (panel-max) |
| `X4_v_prime_index_none_sign1` | 0.971 | 0.971 | 2.69 | 6.39 | clause 1 |
| `X4_v_totient_atbash_pre_sign1` | 0.925 | 0.925 | 2.88 | 6.39 | clause 1 |
| `X3b_solvedkey_running_sign-1` | 0.914 | 0.914 | 2.64 | 6.39 | clause 1 |

These are the **hallucination pattern**: the beam wanders into an EN/OE-register basin and
self-reproduces (so recovery-vs-self is high), but the panel-max adjudicator scores the result
noise (pmax 2.4–2.9, far below the 6.39 bar). Had this lane certified on recovery-alone — or on
the retired −5.5 score bar — it would have announced a false discovery. The three-clause `is_hit`
(panel-max AND recovery AND held-out) rejects all four at clause 1. This is doctrine R1 in action:
the instrument was measured, not reasoned about, and it earned its keep on the first real sweep.

The `_drift` X3b rows show the opposite failure: higher raw pmax (7.0–7.35) but their bar rises
with drift-permissiveness to 11.97, and their recovery collapses to 0.20–0.44 — rejected at the
recovery clause. Neither route reaches a hit.

### Null (size-matched, seed 3301)

The seed-3301 order-destroying shuffle, run through the identical operations, produced
**0 bar-clears (X1, X3a) and 0 `is_hit` (X3b, X4)** — the null is empty, so the real-stream
negative is a negative against a calibrated empty null, not against a bar nobody measured.

## The three conditionals this negative carries (doctrine Q4)

1. **Key space / operations swept:** the 185 enumerated literal-"four"/"question"/"or" operations
   above — decimation (4 phases × cipher ladder), iterate ×{2,3,4}, 4-way (de)interleave, full
   reversal × cipher ladder, solved-plaintext running key (±sign), and the 3 number transforms
   as keystreams (±sign, ±atbash). Bounded and enumerable, not a fog.
2. **Decoder transition model:** driftbeam `exact` (keyskip1) for keyed rows, plus `drift` for
   X3b; structural rows are adjudicated directly (no decoder). A construction the beam cannot
   represent (e.g. `skip_by_2`, J≥8 pointer jumps) is out of scope, as everywhere in this repo.
3. **Adjudicator register:** the full 9-register panel (EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY
   EN_HALFVOWEL EN_NOVOWEL), each row's argmax `preg` persisted. This is *not* an English-only
   negative — every register was in the panel and none cleared.

## Red-team / non-overlap honesty note (doctrine R6)

- **X1 and X3 are genuinely new operations.** No prior round performed decimation, cipher
  iteration, 4-way interleave/de-interleave, whole-stream reversal-as-encryption, or the
  solved↔unsolved role inversion. These are the untouched literal-imperative executions the
  ELIMINATION-LEDGER and Round-22 seed flagged OPEN.
- **X4 partially overlaps Round 11, and this is reported honestly, not claimed as untouched.**
  Round 11 **N5** already used **φ(prime)=totient as a keystream** (its positive control
  reproduced AN END that way) and scored the LP2 stream NEGATIVE; Round 11 **N4** used digit
  planes as mod-N keystreams. So `X4_v_totient_none_sign-1` is a **re-adjudication of the N5
  totient-keystream lens under the REPAIRED instrument** (9-register panel-max + recovery gate),
  not a virgin lens — and it comes back NEGATIVE again (recovery 0.49, pmax 2.69). The
  genuinely-new X4 members are the **raw prime-value** and **prime-index** keystreams and the
  sign/atbash variants, none previously run as keystreams-over-letters. Value of the overlap: it
  confirms N5's negative survives the instrument repair that voided so many other English-only
  bars — the totient-keystream lens was *not* a victim of the broken magnet.

## Verdict and what remains

**FLAGGED-FOR-ORACLE survivors: none.** All three sub-lanes are control-validated NEGATIVE at the
pre-registered panel-max bar, carrying the three conditionals above. Per the roadmap R21-L1 seal
note, had any survivor appeared it would be flagged, not auto-certified; none did.

**Not covered (bounds, not a verdict — doctrine R7):**
- Non-zero key offsets for the X3b/X4 keyed lanes (all run at o=0).
- Interleave widths other than 4, decimation steps other than 4 (the imperative is literally
  "four", so this is the correct scope, but other-k is untouched).
- Cipher-iterate counts beyond {2,3,4} and cipher families beyond {atbash, shift}.
- Decoder constructions outside driftbeam exact/drift (skip_by_2, J≥8 pointer jumps).
- X4 keystreams from φ(φ(p)), λ(p) (Round 11 N5 covered these as *number-theoretic ladder*, not
  re-adjudicated here) and digit-plane keystreams (Round 11 N4).

The literal execution of "do four unreasonable things", "question all things / test the knowledge",
and "the words OR their numbers" does not, in any of the 185 bounded readings enumerated here,
produce a decode the repaired recognizer accepts.
