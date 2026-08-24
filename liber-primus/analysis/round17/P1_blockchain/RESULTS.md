# Round 16 lane P1 — THE BLOCKCHAIN

_Bitcoin block hashes, merkle roots, nonces and timestamps, in height order, swept as a
one-time pad against LP2 pages 0–54 (12,956 runes). Pre-registration:
`liber-primus/analysis/round16/PREREG.md`. Instrument: `round16/lib_padsweep.py`._

## Verdict

**NEGATIVE over the coverage stated below.** No configuration reached the pre-registered
HIT bar. Best over the whole lane: **−6.802** against a bar of **−5.500**; the shuffle
null's own maximum under these keystreams is −6.838, and the scale-corrected expectation
for the best of this many *wrong* answers is **−6.500**. The lane's best score is therefore
*below where pure noise is expected to land* — it is not a near miss, and there was nothing
to escalate. `python liber-primus/verify_solution.py --selftest` was run and **PASSES**, so
the oracle that would have adjudicated a hit is healthy; it was never invoked on a
candidate because none qualified.

This is a bound on the pads and readings listed under **Coverage**. It is **not** a verdict
on "the blockchain" as a family — see **What this does not exclude**.

## Why this lane exists

The repo's seed census (`round10/L5-seed32/CENSUS.md:87-94`, repeated in `PARKED.md` and
`ELIMINATION-LEDGER.md`) files `random.org` and friends under "no seed at all … and nothing
can [touch it]". That merges *leaves no seed* with *leaves no public record*. The Bitcoin
blockchain separates them cleanly: it is full-entropy, seedless, permanently public,
timestamped, ordered, and byte-exact retrievable today. Block hashes are the canonical
"randomness nobody can forge and everybody can verify later", and a 2013–14 crypto-literate
author had every cultural reason to reach for them. Nothing in this repo had ever scored a
single blockchain byte.

Lane **P4** independently reports that the anti-repeat filter is **machine-applied** — flat,
unscoped, single-lag, supp = 0.813 — not hand-applied. A pad that came out of a program or a
file rather than a person is exactly the shape this lane assumed, so P4 *raises* the prior on
an imported public byte stream even though this particular stream came back negative.

## Data — what was fetched and how it was verified

Source: Blockchair's public per-day block dumps, one TSV row per block —
`https://gz.blockchair.com/bitcoin/blocks/blockchair_bitcoin_blocks_YYYYMMDD.tsv.gz`,
1,971 daily files covering **2009-01-03 → 2014-06-01**. Regenerate with
`python liber-primus/analysis/round16/P1_blockchain/fetch.py`.

| | |
|---|---|
| blocks | **303,727** — heights **0 … 303,726**, verified contiguous, no gaps, no conflicting duplicates |
| era covered | genesis through 2014-06-01. LP2 was posted 2014-01-05 at height ≈ 277,000, so every block the author could possibly have had is inside this range, with ~26,700 blocks of headroom past it |
| known-value checks | block **0**, **1**, **170**, **100000**, **210000** hashes asserted byte-exact against independently known values; genesis merkle root `4a5e1e4b…` and genesis nonce `2083236893` also asserted |
| second-source check | 11 heights (the 5 above + 6 drawn at random, seed 3301) re-fetched from **Blockstream Esplora** — hash, merkle root, nonce and timestamp agreed **11/11** |
| arithmetic check | for heights 100000 and 250000 the 80-byte header was reassembled from Esplora fields and double-SHA256'd; the recomputed hash equals the stored hash |
| digests | every emitted pad's SHA-256 is in `data/MANIFEST.json` |

`data/` is gitignored; `.gitignore` names the campaign and the exact regeneration command.

### Pads emitted

| file | bytes | what it is |
|---|---:|---|
| `hash_display.bin` | 9,719,264 | block hashes, 32 B each, **display order** (big-endian hex, as every explorer shows it) |
| `hash_internal.bin` | 9,719,264 | the same hashes **byte-reversed** (little-endian, as stored on the wire) — a different pad |
| `merkle_display.bin` | 9,719,264 | merkle roots, display order |
| `merkle_internal.bin` | 9,719,264 | merkle roots, internal order |
| `nonce_le.bin` | 1,214,908 | 4-byte nonces, header (little-endian) order |
| `time_le.bin` | 1,214,908 | 4-byte block timestamps, header order |
| `hash_display_2013.bin` | 2,029,856 | **2013 blocks only** (63,433 of them), display order |
| `hash_internal_2013.bin` | 2,029,856 | 2013 blocks only, internal order |

The 2013-only pads exist because a date-filtered selection is a *different byte stream*, not
a substring of the full pad. Every other subset the lane brief names — "genesis onward",
"blocks near LP2-relevant dates" — **is** a contiguous run of the full pad and is therefore
already covered by scanning every offset of it.

## Control status — and the one deliberate departure from A1's settings

The round-level gate in `PREREG.md` passed on a synthetic stand-in pad (8/8 recovered, dense
survival 0.625). Re-running that same gate on the **real** blockchain pad is what this lane
did first, and it initially **FAILED**: 6/8 recovered (`control.json`).

Diagnosis (`control_ext.py` → `control_ext.json`; `control_ms.py` → `control_ms.json`):

* `hash_display.bin` is **18.4 % zero bytes**. Every block hash in display order opens with
  exactly 4+ zero bytes (mean leading-zero run = 4.00), so the pad carries a 4-byte
  **constant run every 32 bytes**. `merkle_display.bin`, by contrast, is 0.39 % zeros — full
  entropy.
* Under the anti-repeat filter a constant key run makes the key pointer advance *without
  changing the key symbol*, so suppressed doublets consume more skips. Measured: failed
  trials averaged **12 skips**, successful ones 8, and the synthetic pad 6.
* A1's `max_skip=3` is therefore too small **on this pad family specifically**. Widening the
  beam does nothing — it is a skip-budget limit, not a search-width limit:

| plant-and-recover, 60 plants, beam_w=500 | recovered @0.95 | beam score ≥ −5.5 at true offset |
|---|---:|---:|
| `hash_display`, max_skip=3 (A1's setting) | 0.650 | 0.867 |
| `hash_display`, max_skip=3, beam_w=**1500** | 0.650 | 0.867 |
| `hash_display`, max_skip=**5** | 0.967 | 1.000 |
| `hash_display`, max_skip=**8** | **1.000** | **1.000** |
| `merkle_display` (full entropy), max_skip=3 | 1.000 | 1.000 |

**The fix, and why it was needed.** Every dense-scan survivor is escalated **twice** — once
at `max_skip=3` (A1's setting, so the numbers stay directly comparable to
`round12/A1/results_560_13.json`) and once at `max_skip=8` (power restored on the zero-run
pads) — and each is judged against **its own** shuffle null (n=200) computed at the same
decoder setting. Without this, the block-hash pads would have been swept at ~65 % recovery
and a NEGATIVE would have been reported off an instrument that could miss a third of true
plants on precisely the pad this lane was built to test. This is lesson 1 of `AGENTS.md` §4
firing in the field: the null of an under-powered instrument is not a negative.

Re-running the strict gate at the corrected budget (`control_pass.py` → `control_pass.json`,
12 plants each):

| pad | beam recovered | dense survival | strict gate |
|---|---:|---:|---|
| `hash_display.bin` @ max_skip=8 | **12/12** | 9/12 | **PASS** |
| `merkle_display.bin` @ max_skip=8 | **12/12** | 5/12 | **PASS** |

**Lane control: PASS at the setting the headline numbers use.** The residual loss is entirely
the *dense prefilter*, not the decoder: in the end-to-end control every trial whose offset the
prefilter retained also cleared the −5.5 bar under the beam (`control_ms.json`: detection power
== dense survival, 0.542 on `hash_display`, 0.792 on `merkle_display`). That is a power limit,
exactly as PREREG anticipated.

Pooled dense-prefilter survival over all **104** plants this lane ran on real blockchain pads:
**66/104 = 0.635** (95 % CI 0.542–0.727) — consistent with PREREG's measured 0.625, which is
the figure used for the coverage discount below.

## A second instrument gap this lane found: `ks_hexchars` drops the digits

The lane brief asks for "the hex STRING reading, not just the bytes", and points at
`lib_padsweep.ks_hexchars`. That builder runs `blob.hex().upper()` through
`skipdecode.eng_to_idx`, which is documented as *lenient*: it silently **drops every character
it cannot map, and digits are unmappable**. So `hexchars` over `hash_display.bin` sees
5,732,786 of the 19,438,528 hex characters — it is really *"the A–F subsequence of the hex
text"*. That is a legitimate reading (a letters-only running key) but it is not the reading
that was asked for, and it is not what a 2013 author pasting a hash off a block explorer would
have had.

The faithful arithmetic reading of hex text is the **nibble stream** — each hex character as a
value 0–15, hi then lo for every byte — and it is *not* covered by `hi_nibble` or `lo_nibble`,
which each take every **other** nibble. A lane-local builder `ks_nibbles` was added and every
pad was swept a second time under it (`sweep.py --extra`, results in `results_extra_*.json`).
Both readings are in the coverage table and both came back negative.

## Coverage

12 keystream builders per pad in the main pass (6 `lib_padsweep` builders × forward/reverse)
plus 2 in the nibble pass, × 2 signs, × **every** offset, escalated at 2 skip budgets.

### coverage

| pad | bytes | builders | variants (builders x fwd/rev) | offsets scored (all variants x 2 signs) | best score |
|---|---:|---|---:|---:|---:|
| `hash_display.bin` | 9,719,264 | nibbles (hex text) | 2 | 77,754,016 | -6.915 |
| `hash_display_2013.bin` | 2,029,856 | nibbles (hex text) | 2 | 16,238,752 | -6.879 |
| `hash_internal.bin` | 9,719,264 | nibbles (hex text) | 2 | 77,754,016 | -6.882 |
| `hash_internal_2013.bin` | 2,029,856 | nibbles (hex text) | 2 | 16,238,752 | -6.882 |
| `merkle_display.bin` | 9,719,264 | nibbles (hex text) | 2 | 77,754,016 | -6.955 |
| `merkle_internal.bin` | 9,719,264 | nibbles (hex text) | 2 | 77,754,016 | -6.854 |
| `nonce_le.bin` | 1,214,908 | nibbles (hex text) | 2 | 9,719,168 | -6.862 |
| `time_le.bin` | 1,214,908 | nibbles (hex text) | 2 | 9,719,168 | -6.967 |
| `hash_display.bin` | 9,719,264 | 6 lib_padsweep builders | 12 | 217,317,732 | -6.802 |
| `hash_display_2013.bin` | 2,029,856 | 6 lib_padsweep builders | 12 | 45,189,560 | -6.834 |
| `hash_internal.bin` | 9,719,264 | 6 lib_padsweep builders | 12 | 217,317,732 | -6.802 |
| `hash_internal_2013.bin` | 2,029,856 | 6 lib_padsweep builders | 12 | 45,189,560 | -6.802 |
| `merkle_display.bin` | 9,719,264 | 6 lib_padsweep builders | 12 | 222,964,704 | -6.826 |
| `merkle_internal.bin` | 9,719,264 | 6 lib_padsweep builders | 12 | 222,964,850 | -6.857 |
| `nonce_le.bin` | 1,214,908 | 6 lib_padsweep builders | 12 | 27,631,086 | -6.849 |
| `time_le.bin` | 1,214,908 | 6 lib_padsweep builders | 12 | 27,674,888 | -6.833 |

total offsets scored: **1,389,182,016**

### top 20 (all pads, all builders, both signs, both skip budgets)

| # | pad | builder | sign | max_skip | offset | score_norm | bar | beam head |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | `hash_display.bin` | hexchars | +1 | 3 | 3,552,344 | **-6.802** | -5.500 | `NTHELFASDISPTOETHCAUEFOEYXTH` |
| 2 | `hash_display.bin` | hexchars | +1 | 8 | 3,552,344 | **-6.802** | -5.500 | `NTHELFASDISPTOETHCAUEFOEYXTH` |
| 3 | `hash_internal.bin` | hexchars_rev | -1 | 3 | 1,342,827 | **-6.802** | -5.500 | `IAHPIAEOAEIAEOSTHATIODBLATOE` |
| 4 | `hash_internal.bin` | hexchars_rev | -1 | 8 | 1,342,827 | **-6.802** | -5.500 | `IAHPIAEOAEIAEOSTHATIODBLATOE` |
| 5 | `hash_internal_2013.bin` | hexchars_rev | -1 | 3 | 892,664 | **-6.802** | -5.500 | `IAHPIAEOAEIAEOSTHATIODBLATOE` |
| 6 | `hash_internal_2013.bin` | hexchars_rev | -1 | 8 | 892,664 | **-6.802** | -5.500 | `IAHPIAEOAEIAEOSTHATIODBLATOE` |
| 7 | `merkle_display.bin` | hexchars | +1 | 3 | 6,305,924 | **-6.826** | -5.500 | `STHELDWOEALTHENEATHEAJXEATIO` |
| 8 | `merkle_display.bin` | hexchars | +1 | 8 | 6,305,924 | **-6.826** | -5.500 | `STHELDWOEALTHENEATHEAJXEATIO` |
| 9 | `hash_internal.bin` | hexchars | +1 | 3 | 5,301,349 | **-6.832** | -5.500 | `OTHWOUMSASSEIRLEAAPECTOYLOGE` |
| 10 | `hash_internal.bin` | hexchars | +1 | 8 | 5,301,349 | **-6.832** | -5.500 | `OTHWOUMSASSEIRLEAAPECTOYLOGE` |
| 11 | `time_le.bin` | mod29 | +1 | 3 | 325,334 | **-6.833** | -5.500 | `AYRIASHEYASEEXLTOCEOLEOIAPHI` |
| 12 | `time_le.bin` | mod29 | +1 | 8 | 325,334 | **-6.833** | -5.500 | `AYRIASHEYASEEXLTOCEOLEOIAPHI` |
| 13 | `hash_display_2013.bin` | mod29 | -1 | 3 | 913,508 | **-6.834** | -5.500 | `SHELDEALACIANNINRUISASTATHWO` |
| 14 | `hash_internal.bin` | byte_scaled_rev | -1 | 3 | 7,321,738 | **-6.837** | -5.500 | `RNARYSIMENIMHAMETLEALENTHNEW` |
| 15 | `hash_internal.bin` | byte_scaled_rev | -1 | 8 | 7,321,738 | **-6.837** | -5.500 | `RNARYSIMENIMHAMETLEALENTHNEW` |
| 16 | `merkle_display.bin` | prime_to_idx | -1 | 3 | 2,339,541 | **-6.849** | -5.500 | `OEAEPAEAEXCLENSASCEFBASEATHY` |
| 17 | `merkle_display.bin` | prime_to_idx | -1 | 8 | 2,339,541 | **-6.849** | -5.500 | `OEAEPAEAEXCLENSASCEFBASEATHY` |
| 18 | `nonce_le.bin` | byte_scaled | +1 | 3 | 502,559 | **-6.849** | -5.500 | `XFTDTHEMBEOPITELTELAUINGCLLA` |
| 19 | `nonce_le.bin` | byte_scaled | +1 | 8 | 502,559 | **-6.849** | -5.500 | `XFTDTHEMBEOPITELTELAUINGCLLA` |
| 20 | `hash_display.bin` | byte_scaled | +1 | 8 | 8,824,293 | **-6.850** | -5.500 | `SHENTRUSTIATYEADMYBEABROIMTH` |

## Limits — what this does and does not exclude

**Excluded, subject to the 0.625 prefilter discount:** that LP2's keystream is a contiguous
run taken from any of the eight byte streams above — Bitcoin block hashes or merkle roots
(both byte orders), nonces, or timestamps, for **heights 0–303,726 (genesis through
2014-06-01)**, read forward or reversed, through any of `mod29`, `hi_nibble`, `lo_nibble`,
`byte_scaled`, `prime_to_idx`, `hexchars` (letters-only hex text) or `nibbles` (full hex
text), at either sign, at **any** starting offset. That is **1,389,182,016** scored offsets,
≈ **868 million effective** after the measured survival discount. Nothing came within 1.3 of
the bar and nothing came within 0.3 of the noise ceiling.

**Not excluded, and worth saying plainly:**

1. **Any non-contiguous or transformed selection.** Every-Nth block, difficulty-retarget
   blocks only, blocks whose height is prime, hashes concatenated with their heights, hashes
   XORed together, the hash of a hash, hashes with the leading zeros stripped (which is what a
   human copying "the interesting part" would produce) — none of these is a contiguous run of
   any pad here and none was scored.
2. **Other blockchain fields and other chains.** Transaction IDs, coinbase scriptSigs,
   difficulty/bits/chainwork, block sizes, addresses, and every non-Bitcoin chain (Litecoin,
   Namecoin, Dogecoin — all live and popular in 2013) are untouched.
3. **Any keystream builder outside the seven tested.** The mapping from bytes to a 0–28 rune
   index is a free parameter and only seven readings were tried. A base-29 conversion of the
   256-bit hash as an integer, or a per-block rather than per-byte reading, would be a
   different keystream over the same public data.
4. **The prefilter's 37 % blind spot.** The dense scan is rigid over a 24-rune head window;
   a true offset whose first 24 runes happen to carry several filter skips is dropped before
   the beam ever sees it. Measured at 0.635 survival here. A brute-force beam over all 1.39e9
   offsets — ~2 CPU-years at this beam width — would close it, and is the obvious unpark item
   if the blockchain prior ever rises again.
5. **The transcription.** Every number here inherits `PROBLEM.json`'s rune stream, which has
   never had an independent from-scratch re-read (`PARKED.md`).

**"Bitcoin is dead" is not what this says.** What it says is: *block hashes, merkle roots,
nonces and timestamps for heights 0–303,726, under 12 (+2) keystream builders × 2 signs × all
1.39e9 offsets × 0.635 measured survival, escalated at two skip budgets, best −6.802 against a
−5.500 bar and a −6.500 noise expectation.*

## Reproduce

```bash
cd liber-primus/analysis/round16/P1_blockchain
python fetch.py                     # re-download, re-verify, re-emit data/ (~35 min)
python control_ext.py               # the zero-run diagnosis
python control_ms.py                # skip-budget sweep + end-to-end detection power
python control_pass.py              # strict gate at max_skip=8   -> both pads PASS
python sweep.py --subsets
for p in hash_display hash_internal merkle_display merkle_internal \
         nonce_le time_le hash_display_2013 hash_internal_2013; do
  python sweep.py --pad $p.bin              # 12 builders x 2 signs x all offsets
  python sweep.py --extra --pad $p.bin      # faithful hex-text (nibble) reading
done
python sweep.py --merge             # -> results.json
python report.py                    # -> the tables above
python ../../../verify_solution.py --selftest
```

## Files

| file | what |
|---|---|
| `fetch.py` | downloads + verifies the blockchain data, emits the pads and `data/MANIFEST.json` |
| `sweep.py` | the dense sweep; `--pad`, `--extra`, `--control`, `--subsets`, `--merge` |
| `control_ext.py` / `control_ms.py` / `control_pass.py` | the three control stages described above |
| `report.py` | renders the coverage and top-20 tables from `results.json` |
| `results.json` | merged lane result: verdict, controls, per-pad bests, bars, top-20 |
| `results_*.json` | per-pad detail incl. the full top-20 per builder × sign × skip budget |
| `control*.json` | raw control output |
| `logs/` | stdout of every run |
| `.gitignore` | excludes `data/`, with the regeneration command |
