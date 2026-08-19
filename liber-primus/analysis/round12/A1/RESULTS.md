# FRONT A1 — the author's own never-fed binary pads under the skip-aware decoder

_Round 12, "honest best shot". Ran 2026-08-17. Verdict: **NEGATIVE**._

## What was tested

The hypothesis (PA-3): Cicada shipped authored binary key material in the 2013
CicadaOS (`DATA/_560.00`, `DATA/560.13`, `DATA/560.17`) plus the `761.mp3`/twitter
pair, and this material was **only byte-XOR'd** by the community, **never fed as a
mod-29 keystream under the skip-aware (anti-repeat) beam decoder** — the only decoder
that survives the doublet filter proven on LP2 0–54.

## Pads obtained (local + fetched)

| pad | bytes | source | note |
|---|---|---|---|
| `_560.00` | 2,412,544 | cicada-solvers archive (fetched) | real binary |
| `560.17` | 1,183,811 | cicada-solvers archive (fetched) | real binary |
| `folly` / `wisdom` | 3,368 | local `armada_osint/artifacts` == archive `tmp/folly` | identical MD5 `0c7d18…`, one pad |
| `prime_echo` | 12,248 | archive `usr_local_bin/prime_echo` (fetched) | the binary that *consumes* the DATA pads |
| `761.mp3` | 4,010,732 | local `puzzles/2013/artifacts` | audio bytes |
| `560.13` | **UNRECOVERABLE** | Git-LFS pointer only | see below |

**`DATA/560.13` could not be fetched.** In both the cicada-solvers and krisyotam
mirrors it is a 134-byte Git-LFS pointer (real object: sha256 `db79072c…`, 118,818,811
bytes). The LFS batch API returns `404 Object does not exist on the server` on both
remotes. Logged and continued with the five real pads above (the archive.org 3301.iso
was not attempted this run; noted as the only remaining fetch avenue for 560.13).

## Machinery (all reused, validated)

- decoder: `campaign18_skip/skipdecode.py` `beam_decode` / `rigid_decode`
- data + null + scorer: `round11/lib_numchannel.py` (`nc.unsolved()` = 12,956 runes,
  `nc.segments()`, `nc.shuffled` seed 3301)
- keystream builders per pad, tried literally: `mod29`, `prime_to_idx`
  (gematria PRIME→rune-index where in range else b%29), `hi_nibble`, `lo_nibble`,
  `byte_scaled` (0..255→0..28), each also on the **reversed** byte stream.
- sign ±1; key offsets 0/1000/5000/20000 (head sweep); whole-stream and **per-page**.

## POSITIVE CONTROL — PASS

Encrypted PARABLE-like plaintext with the real `_560.00` pad (`mod29`, anti-repeat
key-skip filtered, offset 5000) and recovered it:

- beam decode: **score −4.211, rune-match 100%** (English band ~−4.4)
- rigid decode of same: **−6.668** (fails — the desync trap, as designed)
- wrong pad (`560.17`) beam: **−7.049** (stays noise)

The instrument recovers a planted signal *made from an author pad*, and rejects the
wrong pad. Gate satisfied — a real hit would have been visible.

## RESULT — no signal

**Head sweep** (first 400 runes, 340 pad×variant×sign×offset configs):

- best config **−6.883** (`560.17` byte_scaled s+1 o20000) — gibberish
- null (n=200 shuffles, matched length): mean −7.291, **max −6.995**
- HIT bar = max(−5.5, null_max+0.5) = **−5.5**. Best is 1.38 below the bar and only
  0.11 above null_max. Everything sits in the noise band.

**Per-page sweep** (55 pages × pads × 12 variants × 2 signs, offset 0 per page):

- best per-page **−6.517** (`560.17` prime_to_idx_rev, page 54) — gibberish
- per-page null (n=200, median page len): mean −7.308, **max −6.877**
- HIT bar −5.5. Best is 1.02 below the bar, 0.36 above null_max. Noise.

**Full-page beam** on the best head config (all 12,956 runes): **−7.298** — pure noise,
confirming nothing lifts over the whole stream.

## Verdict

**NEGATIVE.** None of the author's five recoverable never-fed pads — under any of
mod-29 / prime-index / nibble / bit-scaled reductions, forward or reversed, either
sign, any tested offset, whole-stream or per-page — decodes the LP2 unsolved runes to
English through the doublet-surviving beam decoder. Positive control passed, so the
null result is trustworthy. Best observed score (−6.517) falls 1.0–1.4 below the HIT
bar and within ~0.1–0.4 of the shuffle ceiling.

Consistent with the standing OTP verdict: if these were the pad and the alignment were
recoverable by literal byte→symbol reductions, the beam would have shown English from
rune 0 (as it did in the positive control). It did not.

**Residual (not closed by this run):** `DATA/560.13` (118 MB) remains unfetched — the
LFS object is deleted from both GitHub mirrors. Recovering it from `archive.org/details/3301.iso`
and re-running this exact harness is the one remaining A1 lever.

---

# COMPLETION RUN — `DATA/560.13` recovered and swept (2026-08-19)

**A1's one declared gap is now closed by measurement. Verdict unchanged: NEGATIVE.**

## The recovery

The section above recorded `DATA/560.13` as **UNRECOVERABLE**: in both the cicada-solvers and
krisyotam mirrors it is a 134-byte Git-LFS pointer, and the LFS batch API returns
`404 Object does not exist on the server` on both remotes. `archive.org/details/3301.iso` was
named as "the only remaining fetch avenue" and was not attempted in that run.

It works. The archive.org item exposes the ISO's **inner files** directly:

```
https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13     # HTTP 200
```

and the download verifies **byte-exact against the LFS pointer's own digest** — the strongest
available provenance check, since the digest was published by the mirror that no longer holds
the object:

| | value |
|---|---|
| size | **118,818,811 bytes** (expected 118,818,811) |
| sha256 | **`db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f`** (expected identical) |

`sweep_560_13.py` re-verifies this hash on every run and **refuses to proceed on a mismatch** —
a pad that is not byte-exact is a different experiment.

## Method — deliberately identical to A1

Same builders (`mod29`, `prime_to_idx`, `hi_nibble`, `lo_nibble`, `byte_scaled`, each forward
and reversed), same beam settings (`beam_w=120`, `max_skip=3`), same HEAD=400 window, same
shuffle null (n=200), same HIT bar. Nothing new was introduced, so the result is directly
comparable with the five-pad negative above.

**One declared extension.** This pad is ~100× longer than the others, so it supports offsets A1
could not sweep. The ladder was extended from `(0, 1e3, 5e3, 2e4)` to
`(0, 1e3, 5e3, 2e4, 1e5, 1e6, 1e7, 5e7)`. Declared here rather than silently widening A1's
stated bound.

## Result

160 configurations. Best and null:

| quantity | value |
|---|---|
| best head score | **−6.965** (`prime_to_idx_rev`, sign −1, offset 1,000) |
| null (HEAD=400, n=200) | mean −7.291, **max −7.037** |
| HIT bar | −5.500 |

The best configuration sits **1.47 below the bar and only 0.07 above the null maximum** — inside
the noise band, not near it. No configuration was escalated, because none crossed the bar.

Top decodes read as expected for noise (`AEWOEOSIMOCNGEANGTHYEHDUPAPWDTHAJAEUWNSOETHDDWIA`),
with no word structure at any offset, sign, reduction or direction.

## Verdict

**NEGATIVE** for `560.13`.

> **⚠️ Correction (same day).** An earlier version of this line said "A1 is now **complete**:
> all six of the author's CicadaOS binaries have been fed…". **That was wrong**, and the error
> was caught by the capsule build a few hours later — see the next section. `_560.00` was swept
> from a **truncated** copy, so recovering `560.13` closed one gap while a second, undeclared
> one was still open. The honest statement at this point was "five of six pads fully swept, one
> partially".

This matters beyond its own null. `DATA/560.13` was the single largest piece of period-correct,
author-authored key material known to exist, and PA-3 ranked this family as the **highest-prior
untested input** remaining in the whole project. That family is now exhausted rather than merely
unreached, and the "we never actually looked" caveat attached to A1 is retired.

**Residual.** The pad was tested as a *literal byte→symbol reduction*. It was not tested as a
**PRF seed** (hash/stream-cipher expansion), which is a distinct lane — that construction is
RECON-A **B-05**, and lane **B-04** covers the same expansion family over short seeds. A 118 MB
file is an implausible short seed, but it could be a *salt* or a keyed input, and neither is
covered here.

Artifacts: `sweep_560_13.py`, `results_560_13.json`, `sweep_560_13.log`.
The pad itself is gitignored; the script's docstring carries the exact re-fetch command.


---

# COMPLETION RUN 2 — the truncated `_560.00` (2026-08-19)

**A second, previously-undeclared coverage gap, found while building the provenance capsule.**

## The defect

A1 swept a copy of `_560.00` from the cicada-solvers mirror: **2,412,544 bytes**. The copy inside
archive.org's `3301.iso` is **3,992,970 bytes**.

These are not two different files. Verified directly (`sweep_560_00_full.py::prove_truncation`,
which re-checks it on every run so the claim never rests on a note):

```
iso[:len(mirror)] == mirror   ->   True
```

The mirror copy is an **exact byte prefix**. It is **truncated at 60.4%**, and **1,580,426 bytes
were never fed to any decoder**. `560.17` from the same mirror is byte-perfect, so this is a
defect specific to this file rather than a bad mirror.

## What this does and does not invalidate

Precision matters here, because an overstated retraction is as unhelpful as the original
overstatement.

| | |
|---|---|
| **Invalidated** | The A1 `_560.00` sweep covers only the first 60.4% of the blob. A1's headline should have read "five of six pads fully swept, one partially". |
| **NOT invalidated** | A1's **positive control** and **null ceiling**. Both use `_560.00` bytes as a keystream (`null_ceiling()` loads `PADS["_560.00"]`), but the control plants and recovers with the *same* keystream, and the null decodes shuffled ciphertext under a real keystream. Truncation changes *which* keystream, not whether the instrument works — and 2.4 MB is vastly more than the 400-rune window consumes. The gap is **coverage, not validity**. |
| **NOT invalidated** | Every other pad's result. `560.17`, `folly`/`wisdom`, `prime_echo`, `761.mp3` and `560.13` are all byte-verified. |

## The completion sweep

Same machinery again — A1's builders, `beam_w=120`, `max_skip=3`, HEAD=400, n=200 shuffle null,
same HIT bar. The offset ladder is extended so the recovered tail is genuinely exercised:
offsets at and beyond byte **2,412,544** are positions A1 could not have reached at any setting,
and each result is tagged `in_recovered_tail` so the newly-covered region can be read separately
from the re-covered one.

### Result

220 configurations.

| quantity | value |
|---|---|
| best overall | **−6.918** (`prime_to_idx_rev`, sign −1, offset 3,500,000) |
| best **inside the 40% A1 never saw** | **−6.918** — the same config; the top result does fall in the recovered tail |
| null (HEAD=400, n=200) | mean −7.291, **max −6.995** |
| HIT bar | −5.500 |

**NEGATIVE.** The best configuration is 1.42 below the bar and 0.08 above the null maximum —
noise. It is worth noting that the top-scoring config *does* live in the newly recovered tail,
which is exactly what one expects by chance when 40% more keystream is added: more draws, so a
slightly higher sample maximum, with no shift in the distribution. That is the null behaving
normally, not a weak signal.

Artifacts: `sweep_560_00_full.py`, `results_560_00_full.json`, `sweep_560_00_full.log`.

### A1 is now complete — for real this time

All six of the author's CicadaOS binaries have been fed as mod-29 keystreams under the
doublet-surviving beam decoder, from **byte-verified** copies:

| pad | bytes | status |
|---|---|---|
| `_560.00` | 3,992,970 | ✅ full (was 60.4% truncated) |
| `560.13` | 118,818,811 | ✅ full (was an unfetched LFS pointer) |
| `560.17` | 1,183,811 | ✅ byte-perfect from the mirror |
| `folly` / `wisdom` | 3,368 | ✅ |
| `prime_echo` | 12,248 | ✅ |
| `761.mp3` | 4,010,732 | ✅ |

**None decodes LP2 0–54 to English.** PA-3 ranked this family the *highest-prior untested input*
in the entire project; it is now exhausted rather than merely unreached, and both of the
"we never actually looked" caveats are retired.

**Residual, unchanged:** the pads were tested as **literal byte→symbol reductions**. They were
not tested as **PRF seeds**, salts, or keyed inputs — a distinct construction covered by lanes
B-04/B-05, not by A1.

## The wider lesson, worth more than either null

Both gaps had the same shape: **a file was accepted as the artifact it claimed to be, without
its size or digest being checked against an independent source.** One was visible (a 134-byte
LFS pointer standing in for a 118 MB blob, which A1 did catch and declare); one was invisible (a
silently truncated download, which it did not).

The fix is now structural rather than a matter of care: `handoff/capsule/MANIFEST.json` records a
measured SHA-256 and byte length for every input, and `verify_capsule.py` flags **DRIFT**
separately from absence — because a mirror quietly serving *different bytes* is far more
dangerous than one serving none. Any future campaign should verify against the manifest before
sweeping, not after.
