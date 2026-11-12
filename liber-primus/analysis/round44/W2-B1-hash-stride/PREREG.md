# PREREG — R44 WAVE-2 CELL B1: hash-block 20-byte-stride parse / per-page digest match

Date: 2026-11-09. Cell dir: `liber-primus/analysis/round44/W2-B1-hash-stride/`.
Charter: R43 X0 ADJUDICATION item 29 (NEW-lite half) = X0 NEW priority item 5
(`analysis/round43/X0-firewall/ADJUDICATION.md` lines 52, 65); R44 CAMPAIGN-PLAN P5 row
("hash-block 20-byte-stride parse (after pinning the artifact identity)").

## Hypothesis

The PGP-signed "liber-primus-hash-block" (community: "1005-byte"; in-repo binary: 991 bytes)
is a concatenation of per-page digests — a verification oracle for claimed decrypts — parseable
as 20-byte (SHA-1), 32-byte (SHA-256), 16-byte (MD5) or 64-byte (SHA-512) strides, some of
which equal digests of Liber Primus pages under an enumerable set of encoding recipes.

## Artifact identity (pinned BEFORE any run — the premise gate)

Three distinct 991-byte signed hex blocks exist in `corpus/A-primary-artifacts/`:

| file (signed-payloads/) | sha256 | source .asc (pgp/messages/) |
|---|---|---|
| `2014-01-liber-primus-hash-block.bin` | `f8fa59ec133168d8aaf9c67d13152286eebcec191c5668f7f143a2c7764fc530` | `2014-01-liber-primus-hash-block.asc` (sha1 `2a883f32...`, byte-identical to `ky_` copy) |
| `2014-01-liber-primus-hash-block-outguess-01.bin` | `6600c94b199f30c70c58f5800ccf80537b335122bd66768b6049241d8b20f318` | `...-outguess-01.asc` |
| `2014-01-liber-primus-hash-block-outguess-02.bin` | `07d660d76e24dac92dc0350881ed7771263905a4a64f66c68f7f88ef77c9e07d` | `...-outguess-02.asc` |

Provenance class A: all three .asc report `VALID` in
`corpus/A-primary-artifacts/_logs/verify_sigs_run2.log` + `verify_sigs_run3.log` (lines 21-23, 51, 133),
and ledger row **CORPUS-G-02** pins "every canon message verifies against 7A35090F; exactly one
signing key". As an independent in-cell check, `parse_block.py` decodes the armored signature
packet of each .asc and asserts the issuer key-ID is `181F01E57A35090F`. The armor header is
`Hash: SHA1`, GnuPG v1.4.11 — a measured, held fact raising the SHA-1-stride prior.
"1005/991": the message body is 33×60+2 = 1982 hex chars = 991 bytes; the 1005 figure is the
community's description of the wrapped text, not the binary. The binary identity used here is
991 bytes per block. 991 is prime, so NO stride width tiles the block exactly; a digest-list
reading necessarily has a remainder (991 = 49·20+11 = 30·32+31 = 61·16+15 = 15·64+31), which is
why the scan is run at EVERY byte offset, not only aligned offsets.

KILL GATE (premise): if any .bin had been absent, not 991 bytes, or its .asc not VALID-against-
7A35090F, report INSTRUMENT-INCOMPLETE and stop. (Gate passed — table above.)

## Cited ledger rows (anti-re-run check, verified wording)

- **R43-F6-PAGE56-HASH-AS-KEY** (negative): covers the *page-56 512-bit hash* as mod-29
  keystream / XOR key ONLY. Its coverage field names keystream geometry; nothing about parsing
  the 2014 signed block into strides. Different artifact, different question.
- **CORPUS-G-02** (measured): the provenance anchor used above.
- **R17 P1_blockchain** (`analysis/round17/P1_blockchain/`): hashed *blockchain* candidate bins,
  not this block; no per-page digest matching against the 991-byte blocks.
- Ledger grep over all 322 entries for `991 | digest | sha-1 | sha1`: no row parses this block
  or matches per-page digests (matches X0 item 29's NEW-lite finding). This cell stays inside
  that open ground.

## The five Aiming-Test answers

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit = a contiguous w-byte window of a block byte-equal to a candidate digest (w ∈ {16,20,32,64}).
The recognizer is exact byte comparison via hash-table lookup over every window of every block.
PLANT (run through the identical glue BEFORE any real target): a copy of the main block with
(a) sha1(runes-only utf8 of canon segment 0) written at ALIGNED offset 140 (=7×20) and
(b) md5(raw bytes of `data/relikd/p0.jpg`) written at UNALIGNED offset 333. The pipeline must
report both, with correct candidate attribution, width, offset and alignment flag, and must
report zero injected artifacts when re-run on the untouched blocks. No verdict without this.

**Q2 — What measured fact raises this family's prior above the flat rate?**
(i) The artifact is 7A35090F-signed (class A; CORPUS-G-02 + verify_sigs_run3.log) — it is one of
the very few author-signed binary payloads in existence, delivered in January 2014 alongside LP.
(ii) Its own armor declares `Hash: SHA1` and 991 ≈ 49.55 × 20 — the SHA-1-width stride reading
is the R43 blind-lane convergence-2 hypothesis (A4-H7, A6-H8; `round43/F1-blind/hypothesis_lists.json`
"verification oracle... ~50 20-byte SHA-1 digests"). (iii) X0 adjudication ranked it NEW
priority 5 with testability HIGH. This is a bounded-object audit (doctrine R5 class 1), not a sweep.

**Q3 — Is the space bounded, and by what?**
Enumerable and tiny. Windows: 3 blocks × Σ_w(991−w+1) = 3 × 3836 = **11,508** window lookups.
Candidates: 57 canon segments (`data/krisyotam_runes.txt`, split on `%`: [0..54]=unsolved LP2,
[55]=AN END, [56]=PARABLE) × 5 encodings {raw-segment utf8, runes-only utf8, comma-joined index
string (the `hash_runes.py`/PROBLEM.json identity), transliteration-upper, transliteration-lower}
+ 5 solved-page plaintext transliterations (SOLVED-PAGES.json) × {as-stored, lowercase}
+ 57 page-image byte streams (`data/relikd/p0..p55.jpg`, `0_wisdom.jpg`)
+ 2 whole-stream extras (full canon file bytes; flattened 12,956-rune unsolved index csv)
= **354 byte-strings** × 4 algos {MD5, SHA-1, SHA-256, SHA-512} × 2 byte-orders {as-is, reversed}
= 2,832 digests, matched at each width by exact length or prefix truncation.
Expected false positives under a uniform-block null at the WORST width (16):
2,928 windows × ≤2,832 entries / 2^128 ≈ 2.4×10⁻³² — exact match is self-adjudicating.

**Q4 — The three conditionals this negative will carry.**
1. *Key space*: the candidate grid above — these 354 byte-strings, these 4 digest algos, these
   2 byte-orders, prefix-truncation only. NOT covered: HMAC/keyed hashes, salted or iterated
   hashes, non-prefix truncation, RIPEMD-160/Whirlpool/Tiger, digests of OTHER image masters
   (only relikd bytes hashed), digests of hex-ASCII rather than binary windows, digests of
   future/unreleased plaintexts (the oracle's whole point may be preimages nobody holds —
   an unmatchable-by-construction branch, stated honestly).
2. *Decoder transition model*: N/A — no decode is performed; the construction axis here is the
   digest-recipe grid of (1).
3. *Adjudicator register*: N/A — adjudication is byte equality, register-free. The panel-R36
   adjudicator (`analysis/round19/I2/adjudicate.py`) and `bars_v3.py` bars are NOT engaged
   because no plaintext stream is produced; per CAMPAIGN-PLAN P5 this cell is pure structural.

**Q5 — Kill condition at 10% of budget?**
(a) Premise gate above (artifact unpinnable) → INSTRUMENT-INCOMPLETE, stop. (b) Plant not
recovered by the glue → stop, no verdict. (c) Both pass → the full scan is seconds of compute;
no further checkpoint needed.

## Fixed thresholds / decision rule (in advance)

- Decision statistic: count of exact window↔digest matches on the three REAL blocks.
- **≥1 match on an unsolved-page candidate → FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md` (never
  self-certified), with the full (block, offset, width, recipe) tuple published.
- **≥1 match on a solved-page candidate → the recipe is the author's; FLAGGED-FOR-ORACLE** and
  every unsolved page is re-queued under that exact recipe in RESULTS.md.
- **0 matches → NEGATIVE (structural, measured)** over exactly the Q3/Q4 grid.
- `bars_v3.py` (standing instrument, `analysis/round34/I1-v3-null/bars_v3.py`) not engaged — no
  language scoring occurs; thresholds here are exact-equality with the 2.4×10⁻³² FP bound above.
- Descriptive side-measurements (verdict-neutral, persisted): per-block byte entropy, chi-square
  vs uniform, duplicate-window census at w=20 within/across blocks, remainder arithmetic.

## Coverage statement to be reported

Covered: all 3 signed 991-byte blocks, every contiguous window at widths 16/20/32/64 at every
byte offset (superset of every aligned stride parse), against the full Q3 candidate grid.
Not covered: the Q4-1 list; cross-block concatenation-boundary windows; width ≠ {16,20,32,64}.

## Outputs

`parse_block.py` (artifact pin + plant + scan), `results.json`, `RESULTS.md`,
`ledger_rows.json` (draft), `run.log` (with PREREG sha256 stamp before first execution).
