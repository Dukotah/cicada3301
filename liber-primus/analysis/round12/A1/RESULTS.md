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
