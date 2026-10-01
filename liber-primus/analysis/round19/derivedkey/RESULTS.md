# Round 19 — LANE 2 — DERIVED-KEY DICTIONARY — RESULTS

_Run 2026-10-01. Doctrine `liber-primus/ARMADA-DOCTRINE.md`. PREREG: `PREREG.md` (this folder).
Cites Lane 1's power envelope (`analysis/round19/instrument/POWER-ENVELOPE.md`) for coverage × power._

Trust anchor confirmed this run: `python3 tests/validate.py` → `=== ALL VALIDATIONS PASSED ===`
(5/5 known solves). Every statement below rests on it.

---

## 0. Headline — the finding is NEGATIVE-BY-PRIOR-COVERAGE, and it is a doctrine finding, not a sweep

The PREREG hypothesis was that the pad is a short-seed-DERIVED keystream (finite, enumerable):
`$RANDOM`/glibc `rand`, a TeX/LaTeX LCG, Py2.7 `random` from small seeds, and PBKDF2/scrypt over
Cicada-published seeds (3301, prime sequences, `7A35090F`, the page-56 hash). The lane's first
mandated step (doctrine mechanics 6: *query LEDGER.json first, read each entry's coverage /
not_covered, do NOT re-run measured ground*) was to check what of this is already measured.

**It is almost entirely already measured, across rounds R16–R30**, with measured power and — in the
rounds that post-date the R3 mandate — persisted R3 statistics. The README's self-description that
"the derived-key dictionary lane is untested; only running it settles which" is **STALE**: it was
written before R16-KDF/R20/R21/R24/R25/R26/R27/R28 ran. Re-running this class would be exactly the
mis-aimed-decode failure Round 19 exists to prevent. The honest result of this lane is therefore a
**coverage map of an already-swept family**, two freshly-run instrument anchors that make the
standing null trustworthy, and the mandatory AN-END blind holdout — not a new key-space sweep.

---

## 1. What the ledger already covers (the hypothesis class, cell by cell)

| PREREG member | Already measured by | Coverage | Register axis |
|---|---|---|---|
| PBKDF2 / scrypt / S2K over published seeds | `R16-KDF` | 692,064 KDF configs, NEGATIVE | English-only at run time… |
| …its non-English re-adjudication | `R24-C1-EXT-NONENGLISH-READJUDICATION` | B-04/KDF prior-dense slice re-scored over {EN,LA,GR,OE,Enochian} matched LMs + R3 persisted | **closed** on the modelable registers |
| `$RANDOM` / bash / glibc `rand` | `R26-A-GEN-SWEEP-FIRST-FIRE`, `B-01`, `F-01`, `R28-L4` (queued) | Perl/glibc first-fire + prior-dense; flat 2^32 tail parked | panel + R3 |
| TeX / LaTeX LCG | `G4-TEX-RNG`, `R26-A` (first scored TeX decodes) | prior-dense; flat 2^31 tail parked | panel |
| Py2.7 `random` small seeds | `R20-SG3`, `R21-L3`, `R25`, `R27-CPORT-MT32-FULLSWEEP` | S1 (pair decoder) **coverage 1.00 of [0,2^32)**, power 1.00; S2 in-flight | win-condition registers |
| Published-constant seeds (3301, `7A35090F` fragments, page hashes, primes/totients) | `R26-C-SEMANTIC-SEED-ZOO` | 323/323 semantic seeds × 7 generators × 2 decoders, offset 0, FULLY swept | panel + R3 |
| skip_by_two construction over these generators | `R24-C2-EXT-SKIP-GENERATORS` | 113,432 keys, control-validated pair decoder | matched panel |

Every one returned NEGATIVE / no-crosser. See each entry's `not_covered` for its exact bound;
they are copied forward into §4 so this lane's negative EXTENDS rather than overwrites them.

## 2. COVERAGE × POWER (doctrine R1/R2), citing Lane 1's envelope

Lane 1 (`instrument/power_summary.json`, 198 cells) measured the instrument the whole class uses.
Reading its power into this lane's null:

- **Register axis.** At 100 % rune recovery (keyskip/L=240) the English-quadgram scorer — the bar
  every pre-R24 derived-key null used — has power EN 1.00 / LP1 1.00 / LA 0.29 / OE 0.71 / DE 0.71 /
  CY 0.00 / EN_NOVOWEL 0.00. So the pre-R24 KDF/PRNG negatives are informative ONLY on EN/LP1.
  The **matched per-register LM** restores power 1.00 on LA/OE/DE/CY/EN_NOVOWEL (correct-vs-wrong-key
  margin +0.50..+0.83). R24-C1-EXT already re-adjudicated the KDF/B-04 slice under that matched
  panel, so the register-axis gap my PREREG worried about is **closed on the modelable registers**;
  it remains open ONLY on registers no in-repo corpus can model (native Old Norse, romanized Hebrew,
  Welsh/vowel-dropped where even the matched LM has power ~0 — permanent blind spot inherited from L7-A).
- **Construction axis.** `skip_by_two` collapses beam recovery to 10–41 % in every register, and the
  matched LM cannot rescue what the decoder never recovered (power dips to 0.71). R24-C2 built the
  control-validated pair decoder and swept 113,432 derived-key skip_by_two keys → no crosser. Any
  construction with Lane-1 recovery < 0.85 (free_drift q>0.02, multi-interrupter pages, page-boundary
  resets) is NOT covered and needs its own decoder before a null under it means anything.

**Value statement:** the derived-key class has been swept at power ~1.0 on the EN/LP1/LA/OE/DE/CY +
EN_NOVOWEL registers (matched LM) under the keyskip and skip_by_two constructions, for the finite
published-seed set and the full Py2.7-MT [0,2^32) pair-decoder space, plus prior-dense slices of the
flat generator tails. The flat 2^32/2^64 generator tails and the un-modelable registers are the
residual, carried honestly as not_covered.

## 3. Instrument anchors run THIS lane (so the standing null is trustworthy) — `dk_confirm.json`

Doctrine: *a null from an unvalidated instrument is not a negative.* Two anchors, run fresh:

- **DK-PC2 (plant-and-recover through the live beam).** Planted a PBKDF2-HMAC-SHA256 keystream
  derived from each published seed {3301, 7A35090F, page56_hash, prime_seq}, enciphered a held
  English / Latin / Old-English plaintext under the pinned keyskip construction, decoded with the
  CORRECT key via `skipdecode.beam_decode(400,3)`. **Median recovery 100 %**; correct-key EN-quad
  **−4.79** vs wrong-seed **−7.31**; matched-LM correct **−4.74**. 12 rows, all four R3 columns
  (IoC·N, min-distinct-32, best-non-English LM + register, gzip compressibility) persisted per row
  in Lane 1's exact schema. → The instrument demonstrably emits a planted derived-key hit, so the
  prior nulls are real negatives on the cells where Lane 1 shows power ≥ ~0.8.

- **AN-END BLIND HOLDOUT (mandatory PREREG gate).** Built the AN-END-class ciphertext forward
  (totient shift-down + F-interrupters), then handed the solver ONLY the ciphertext + its stated
  external input (the prime sequence), NOT the key. Rediscovering `φ(prime)=(p−1) mod 29` shift-down
  from the primes reproduced the true keystream bit-for-bit and the interrupter-aware solver returned
  the known plaintext. **Outcome: RECOVERED.** Caveat (Lane-1 FOUND-ERROR): the keyskip BEAM alone
  recovers only ~14 % of this interrupter page; rediscovery required the interrupter-aware solver.
  Any derived-key candidate implying an interrupter page MUST be run through that solver, not the beam.

## 4. NOT COVERED (doctrine R7 — bounds, not verdicts; copied forward from prior entries)

- Flat generator tails: `$RANDOM`/glibc/Perl/TeX **2^32** and Py2.7-amd64 **2^64** seed images
  beyond the prior-dense slices + the Py2.7 pair-decoder [0,2^32). (`R26-A`, `R21-L3` NC-1/NC-2,
  `R25`, `R28-L4`.) Reopens: a GPU/C port finishes a flat tail, or a crosser is flagged for oracle.
- KDF params outside R16-KDF's grid: Argon2, bcrypt, salts outside the 3 Stage-A set (onion-/pp49-51-/
  per-page), iteration counts outside the tested set, KDF offset ≠ 0, secrets outside the 534-list.
- Offsets ≠ 0 for the semantic-seed zoo and most generators (only o=0 swept broadly).
- Un-modelable registers: native Old Norse, romanized Hebrew (no in-repo corpus), Welsh and
  vowel-dropped English (even the matched LM has power ~0 — permanent L7-A blind spot).
- Constructions beyond keyskip1/keyskip2/skip_by_two + permissive-drift: free_drift q>0.02,
  multi-interrupter pages, page-boundary key resets (Lane-1 recovery < 0.85 — need a decoder first).
- The `/dev/urandom` branch: unrecoverable by construction; the honest live possibility.

## 5. AN-END holdout outcome

**RECOVERED** (blind, from the stated prime input, via the interrupter-aware solver). A derived-key
pipeline that cannot represent interrupter pages (the keyskip beam) would miss an AN-END-class target
at ~14 % recovery; this is the standing FOUND-ERROR constraint on every derived-key sweep in the repo.

## 6. Reproduce

```
cd liber-primus/analysis/round19/derivedkey
PYTHONUTF8=1 python3 dk_confirm.py      # DK-PC2 anchor + AN-END blind holdout -> dk_confirm.json
```
Artifacts: `dk_confirm.json` (12 PC2 rows w/ R3 + holdout), this `RESULTS.md`, `PREREG.md`.
