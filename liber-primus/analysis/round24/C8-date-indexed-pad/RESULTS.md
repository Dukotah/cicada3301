# C8 — date-indexed public pad via PGP signature timestamps — RESULTS

**Primary verdict: UNAVAILABLE (premise fails at Step 0).** The join key the lane rests on —
per-page PGP signature timestamp → offset into a dated public pad — **does not exist for the
decrypt target.** The unsolved LP2 runic ciphertext pages carry no PGP signature at all. The
pipeline was nonetheless built and **control-validated** (right-date recovery 1.000, wrong-date
/ wrong-source 0.03), and the fullest defensible steelman probe the artifacts permit returned a
**clean, control-validated null** (630 tests, 0 survivors). C8 is closed for its stated purpose.

Trust anchor: `python3 tests/validate.py` = **5/5 PASS** (re-run at lane close).

---

## STEP 0 — the two premises (the crux; this is most of the result)

### Premise 1 — usable timestamps: FAIL for the decrypt target
`step0_timestamps.py` enumerates every PGP-signed Cicada artifact in `data/scream314_lp.md`
(the canonical LP corpus) and parses each armored v4 signature packet's `sig-creation-time`.
**Exactly 8 clearsigned blocks exist**, all under key `7A35090F`, all GnuPG v1.4.11:

| blk | section | sig-creation (UTC) | what is signed |
|----:|---|---|---|
| 0 | 00.jpg "Liber Primus" | 2014-01-07T03:16:41Z | JPEG-hex of an OutGuess clue image |
| 1 | 01/02 intro | 2014-01-07T03:16:44Z | intro prose |
| 2 | 02.jpg "Intus" | 2014-01-07T03:16:48Z | intro prose |
| 3 | 03.jpg | 2014-01-10T05:42:54Z | "Let the text guide you" + JPEG-hex of a clue image |
| 4 | 10.jpg index.1 | 2014-01-19T07:39:57Z | index/instruction prose (magic-square task) |
| 5 | 11.jpg index.2 | 2014-01-19T07:39:42Z | index/instruction prose |
| 6 | 12.jpg index.3 | 2014-01-19T07:39:50Z | index/instruction prose |
| 7 | 13.jpg index.4 | 2014-01-19T07:39:57Z | index/instruction prose |

**The mapping is explicit and it fails the join.** All 8 signatures cover *cleartext /
known-plaintext prose or JPEG-hash wrappers* on the intro and index pages. The decrypt target
— **LP2 / onion7 pages 0–54** (`data/krisyotam_runes.txt`, 57 %-delimited pages) — is a set of
**runic ciphertext images distributed as a book/PDF with no per-page PGP signatures.** The
signatures are integrity metadata on the *distribution wrapper*, not per-page keys for the
encrypted runes. There is **no per-page timestamp to index a dated pad by.**

This is the whole finding: R17-PUBLIC-PAD's `not_covered` ("non-contiguous selections") stays
uncovered *as a matter of practice* not because it is hard, but because **the join key the C8
hypothesis needs is not present in the artifacts.** We did NOT fabricate a timestamp→page
mapping to have something to sweep (that would manufacture a plausible-but-wrong result).

### Premise 2 — pad source covers the dates: PASS (but moot)
All 8 sig-creation times are **Jan 2014**, after the NIST Beacon v1 genesis (2013-09-05T15:39Z);
Bitcoin (genesis 2009-01) covers them a fortiori. So dates are covered — but this is moot
because Premise 1 removes any target page to index. The **NIST Beacon v1 legacy REST endpoint**
(`https://beacon.nist.gov/rest/record/<unix_seconds>`) **is reachable and serves the real 2014
records** (needs a User-Agent). The v2 API clamps to chain-1-pulse-1 = 2018 (the R17 caveat),
so v1-legacy is the correct source; it was used.

### Premise 3 — causal direction + spoofability (noted, not ignored)
Correct index would be the pulse **at-or-immediately-before** the signature time (a public pad
is unpredictable, so the page is generated at/after the pulse). And PGP sig-creation-time is
**author-settable** (`--faked-system-time`, wrong clock), so even a hit would be *suggestive*,
never proof. Both further weaken the lane even in the steelman.

---

## 1. Positive control — PASS (pipeline validated independent of the failed premise)
`run_c8.py::positive_control`. Cicada-register English enciphered with a **real beacon-derived
pad** (mod29 builder over concatenated consecutive v1 `outputValue`s from the signing minute),
**under the anti-repeat key-skip filter** (`skipdecode.encipher_keyskip`, supp=0.83 — the R17
control model, the construction the driftbeam is built to invert), planted at a **deep offset
o=137**, decoded through `hitfn20` (driftbeam + 9-register panel-max + recovery≥0.90 +
held-out-3/4).

| index | recovery | held-out | pmax | bar | hit |
|---|---|---|---|---|---|
| **RIGHT date** (2014-01-07 pulse) | **1.000** | **1.000** | 29.44 | 4.87 | **True** |
| WRONG date (2014-01-19 real pulse) | 0.032 | — | — | — | False |
| WRONG source (seed-3301 pad) | 0.032 | — | — | — | False |

The decoder recovers the beacon-enciphered page **only** at the right date/source and fails at
both wrong ones. Pipeline validated. **Debugging note (kept honestly):** the first control
version enciphered plain-additive (no filter) and the beam desynced to recovery 0.28–0.50,
because it inserts phantom anti-repeat skips a filterless ciphertext does not contain; a second
version tiled a single 512-bit pulse and desynced across the tile boundary. Both were pipeline
bugs, caught by the mandatory control before any verdict — enciphering under the filter with a
consecutive-pulse pad is the correct, R17-matched control.

## 2. Steelman probe (non-primary, labelled) — CLEAN NULL
The only runic pages with a real timestamp neighbourhood are the *solved* pages. As the fullest
defensible application of the timestamp index the artifacts permit, each of the 15 solved rune
pages (`data/campaign14/`) was treated as ciphertext and decoded with the beacon pad indexed by
each of the 8 real signature timestamps × 6 R17 builders, capped at one pulse's rune length
(no tiling). This can only reconfirm solved pages or return null; it cannot solve LP2.

| quantity | value |
|---|---|
| tests run (page × timestamp × builder) | **630** (15 × 7 distinct ts × 6 builders) |
| survivors flagged-for-oracle | **0** |
| expected FP @ α=0.01 | 6.3 |
| best row | page_08 / nibbles / ts 2014-01-19 — pmax **3.79** vs bar **7.63**, recovery **0.594** |

Every row fails the three-clause `hitfn20` gate (max recovery 0.59 < 0.90; max pmax 3.79 far
below the per-row panel-max bar 7.63). Clean, control-validated negative.

## 3. Null / FP ceiling
Wrong-date and wrong-source (seed-3301) controls both recover 0.03 (§1). Over the 630 probe
tests the family-wise expectation is 6.3 chance clears at α=0.01; **0 observed** — under the
null band. No survivor to flag.

---

## Decision-relevant bottom line
- **Does the timestamp-indexed public pad reopen anything? No.** The join key (per-page sig
  timestamp) does not exist for the decrypt-target pages. R17-PUBLIC-PAD's `not_covered`
  "non-contiguous / dated selection" stays uncovered because **the artifacts provide no index**,
  not because a sweep was skipped. Manufacturing a mapping would be a plausible-but-wrong result.
- **Residual sub-lane?** The only conceivable follow-up would need an *external* per-page
  timestamp for the LP2 rune pages that this repo does not hold (e.g., original upload
  timestamps of the individual onion7 page images, if they were ever posted separately with
  verifiable dates). That is an OSINT-provenance question, not a cryptanalytic one, and current
  evidence (`ARMADA-20-FINDINGS.md` #21) is that the rune pages were distributed as a single
  book/PDF, not individually dated artifacts. **No in-repo residual.**
- **C8 is closed.** With C1/C2 already returning clean, and C8 UNAVAILABLE-by-premise, the
  external-input axis is dry at the tested resolution. The standing verdict is unchanged: LP2
  0–54 remains OTP-class; the only technically-live branches remain the PRNG core-day tail and
  `/dev/urandom` (both out of scope for an in-session lane).

## Files
| file | what it is |
|---|---|
| `PREREG.md` | pre-registration incl. the five Aiming-Test answers and the Step-0 premise plan |
| `step0_timestamps.py` | enumerates + parses all 8 PGP signature creation times; maps to target |
| `run_c8.py` | bounded beacon fetch + positive control + steelman probe |
| `cache/timestamps.json` | the Step-0 output (8 signed blocks, premise verdicts) |
| `cache/beacon_v1_*.xml` | the fetched NIST Beacon v1 records (bounded; ≤16 records) |
| `results.json` | machine-readable control + probe results |
| `ledger.json` | this lane's ledger row |
