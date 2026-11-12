# RESULTS — R44 W2-B1: hash-block 20-byte-stride parse / per-page digest match

**Verdict: NEGATIVE (structural, measured).** 0 window↔digest matches across all three signed
991-byte blocks against the full preregistered candidate grid. Positive control passed.
PREREG sha256 `587f087f6861311195b3cd0d1d5a7f976e85c9b1385373bc68026b4b64e30034` stamped in
`run.log` before first execution.

## Artifact identity (pinned — the premise gate, PASSED)

Three distinct 7A35090F-signed 991-byte blocks (not one): the "1005-byte" community figure is
the wrapped hex text (33×60+2 = 1982 hex chars); the binary is 991 bytes. Each .asc armor
declares `Hash: SHA1`, GnuPG v1.4.11; issuer key-id `181F01E57A35090F` asserted inside each
signature packet by this cell's own parser, and all three are `VALID` in
`corpus/A-primary-artifacts/_logs/verify_sigs_run{2,3}.log` (class A, CORPUS-G-02).

| block | sha256 |
|---|---|
| `signed-payloads/2014-01-liber-primus-hash-block.bin` | `f8fa59ec…64fc530` |
| `…-outguess-01.bin` | `6600c94b…8b20f318` |
| `…-outguess-02.bin` | `07d660d7…77c9e07d` |

991 is prime: no stride width tiles any block exactly (991 = 49·20+11 = 30·32+31 = 61·16+15 =
15·64+31), so the scan ran at EVERY byte offset — a strict superset of every aligned stride parse.

## Positive control (plant, run through identical glue BEFORE real targets)

Copy of the main block with sha1(seg00 runes-only utf8) injected at ALIGNED offset 140 (7×20)
and md5(`data/relikd/p0.jpg` bytes) at UNALIGNED offset 333. Both recovered with correct
candidate, algo, width, offset and alignment attribution; 0 spurious hits outside the injection
zones. `plant.bin` persisted.

## Numbers vs bar

- Grid: 354 candidate byte-strings (57 canon segments × 5 encodings {raw utf8, runes-only utf8,
  comma-joined index csv, translit-upper, translit-lower} + 5 solved-page plaintexts × 2 cases +
  57 relikd page-image byte streams + 2 whole-stream extras) × {MD5, SHA-1, SHA-256, SHA-512} ×
  {fwd, byte-reversed} = 2,832 digests, matched at widths 16/20/32/64 by exact length or prefix
  truncation (entries per width: 2832/2124/1416/708).
- Scan: 3 blocks × 3,836 windows = **11,508 windows**; **matches = 0** (bar: ≥1 exact match ⇒
  FLAGGED-FOR-ORACLE; E[FP | uniform null] = 2.4×10⁻³², so any match would have been decisive).
  Neither the unsolved-page direction nor the solved-page/plaintext positive-control direction
  fired — no recipe in the grid is the author's.
- Side stats (descriptive): entropy 7.791/7.811/7.791 bits/byte; chi² (255 df) 267.3/252.8/272.5
  (all within ~0.8σ of uniform); **zero duplicate 20-byte windows** within or across blocks.
  The blocks are statistically indistinguishable from uniform random — consistent with a list of
  distinct digests (of unheld preimages) OR with encrypted/random filler; this cell cannot
  separate those.

## Coverage

All 3 signed 991-byte blocks; every contiguous window at widths 16/20/32/64 at every byte
offset; against MD5/SHA-1/SHA-256/SHA-512 (both byte orders, prefix truncation) of the 354-string
grid above. R3 note: no decode stream exists; the persisted statistics are the per-block
entropy/chi²/duplicate-census in `results.json`.

## not_covered

HMAC/keyed, salted or iterated hashes; non-prefix truncation; other algorithms (RIPEMD-160,
Whirlpool, Tiger, SHA-3); digests of hex-ASCII window text rather than binary; digests of image
masters other than relikd bytes (other mirrors' JPEGs differ byte-wise); per-page plaintexts
nobody holds — if the block is a verification oracle for FUTURE decrypts, its preimages are
unmatchable by construction and this negative says nothing about that reading; cross-block
concatenated windows; widths ∉ {16,20,32,64}.

## Reopens if

Any unsolved LP2 page is ever decrypted: hash the new plaintext (all 4 algos, both orders,
all 5 encodings) against `results.json`'s pinned blocks — minutes of compute, and the strongest
use of this artifact. Also reopens if a fourth signed block or the original outguess carrier
with different bytes surfaces.

## Files

`PREREG.md`, `parse_block.py`, `results.json`, `plant.bin`, `run.log`, `ledger_rows.json`.
Reproduce: `python3 liber-primus/analysis/round44/W2-B1-hash-stride/parse_block.py`.
