# Round 18 · Lane L5 — PAYLOAD CLOSURE · PRE-REGISTRATION

_Written 2026-08-25, **before** any crop was rendered, any cell was read, or any modulus was
fetched. Thresholds below are fixed and are not to be edited after seeing a result._

Lane scope: **A-04** (the 6 contested bytes of the pp49–51 256-byte payload) and **E-01**
(payload as an RSA signature/ciphertext under 3301's published moduli — the named Round 16
coverage gap: "the 7A35090F RSA-4096 primary and subkey moduli were not fetched").

---

## Part A — A-04: read the 6 contested bytes

### A.0 What is actually contested (established fact, not a hypothesis)

`analysis/pp49_51/canonicalize.py` adjudicates three witnesses — (A) relikd token tables,
(B) scream314 token tables, (C) scream314's own decimal column — over 256 base-60 tokens.
Eleven cells disagree; six are "both tokens agree, only the derived decimal differs", i.e.
the two token transcriptions share one lineage and the decimal column is the only independent
vote. Re-running `canonicalize.py` reproduces exactly:

| idx | page | row,col (in-page) | relikd tok | scream tok | scream decimal | maj | the ambiguity |
|---|---|---|---|---|---|---|---|
| 25  | p49 | r3,c1   | `3I` = 198 | `3I` = 198 | 224 (= `3i`) | 198 | **I vs i** |
| 175 | p50 | r11,c7  | `0I` = 18  | `0I` = 18  | 44  (= `0i`) | 18  | **I vs i** |
| 182 | p50 | r12,c6  | `2l` = 167 | `2l` = 167 | 141 (= `2L`) | 167 | **l vs L** |
| 199 | p51 | r1,c7   | `0l` = 47  | `0l` = 47  | 21  (= `0L`) | 47  | **l vs L** |
| 215 | p51 | r3,c7   | `1O` = 84  | `1O` = 84  | 5   (= `05`) | 84  | **both digits differ** |
| 237 | p51 | r6,c5   | `0W` = 32  | `0W` = 32  | 58  (= `0w`) | 32  | **W vs w** |

Index→page split is 80 / 104 / 72 = p49 / p50 / p51; rows are 8 cells wide.

Five of six are pure **letter-case** discriminations in the base-60 alphabet
(`A–Z` → 10–35, `a–x` → 36–59), so a byte flips by exactly 26 when the case is wrong. One
(idx 215) differs in both positions and is the hardest.

### A.1 Hypothesis

The master 400-DPI page images (`liber-primus/data/relikd/p49.jpg`, `p50.jpg`, `p51.jpg`;
2400×3600) render these glyphs at sufficient resolution that a careful reader can adjudicate
each contested cell against the two candidate tokens. **H1:** at least one contested cell is
resolvable to a single token at ≥3-pass concordance. **H0:** the glyphs are ambiguous at this
resolution and every cell stays contested.

### A.2 Instrument

1. Verify the three images against `handoff/capsule/MANIFEST.json` via
   `handoff/capsule/verify_capsule.py` **before** any pixel is read. If any image is not
   `OK`, the lane stops.
2. Build a per-page cell grid by projection profiling (column/row ink profiles of the
   binarised table region), not by hand-typed coordinates. Validate the grid by cell count:
   p49 must yield 10×8 = 80 cells, p50 13×8 = 104, p51 9×8 = 72. A page whose grid does not
   yield the exact expected count is regridded, not fudged.
3. Crop each cell with padding, upscale ≥6× (LANCZOS), and render to PNG for direct visual
   reading. Both an OCR pass (`pytesseract` if available; otherwise template/feature
   matching against glyphs cut from the same pages) **and** direct visual reading are used.
   Where they disagree, the visual reading of the maximum-zoom crop is authoritative and the
   disagreement is recorded.

### A.3 Positive control — **the gate**

Before any contested cell is adjudicated, read a **blind calibration sample of 40
uncontested cells**, drawn by a fixed rule (`random.Random(3301).sample()` over the 245
indices that are not one of the 11 conflict cells) and read **without** the canonical value
in view. Score exact-token agreement against `canon_256.bin`.

- **GATE: ≥ 38/40 (95%) exact-token agreement.** Below that the instrument is declared unable
  to adjudicate letter-case at this resolution, the contested cells stay contested, and the
  measured accuracy is reported as the result.
- The calibration sample must include at least 6 cells whose true token contains one of the
  case-ambiguous glyph classes `{I, i, l, L, O, 0, W, w, S, s}`; if the seeded draw does not,
  it is topped up with the next such indices in ascending order, and that top-up is reported.
  Case-class accuracy is reported **separately** from overall accuracy, because overall
  accuracy on unambiguous glyphs would flatter the instrument.

### A.4 Decision rule per contested cell

- **RESOLVED** iff ≥3 *independent* passes (different crop padding, different upscale factor,
  and a differently-ordered presentation so the reads are not primed by each other) all return
  the **same** token, **and** the calibration gate passed.
- Otherwise **STILL-CONTESTED**, reported with the shortlist of candidate values.
- A resolution that contradicts *both* prior witnesses is reported as such, loudly, and
  requires a 4th pass.

### A.5 Propagation (runs regardless of how many cells resolve)

With the resolved payload — or, if cells remain contested, with the full Cartesian product of
their candidates (bounded: ≤ 2^6 = 64 variants, trivially enumerable) — re-run every
payload-consuming test that was run on the holed byte string:

- `analysis/pp49_51/characterize.py` (entropy / primality / modulus / printability),
- `analysis/pp49_51/hash_hunt.py` (the hash/checksum probes),
- `analysis/round16/zeroFP/zerofp_tests.py` E-02A / E-02B / H-03,
- B-05's generator family (payload-as-PRF-seed) over each variant.

**Threshold for the propagation:** any test with a pre-existing pre-registered bar keeps that
bar. Where a bar is a scored one (B-05: HIT iff score ≥ −5.5 AND score > null_max), the
family-wise bar is raised for the variant count per Rule 4 / PARKED P-7 — with `V` variants
the effective trial count is `V ×` the original, and the bar is recomputed with
`benchmark/null.py: threshold_for(n_trials, segment_len)` rather than reusing B-05's
single-payload bar. Note B-05 already swept all 256 values at each of the 6 positions
*singly* plus 64 all-position masks (LEDGER B-05 `notes`), so the genuinely new coverage here
is **joint** corruption — which is exactly B-05's stated `reopens_if`.

---

## Part B — E-01: payload as RSA signature/ciphertext under 3301 moduli

### B.1 Hypothesis

The 256-byte payload is 2048 bits — but it is also exactly the right *shape* to be a raw
RSA block. **H1:** for some published 3301 modulus `n` and public exponent `e`,
`pow(s, e, n)` (with `s` = the payload read big-endian **or** little-endian, and also the
payload zero-extended into a 4096-bit block) yields a byte string with **PKCS#1 v1.5**
(`00 01 FF… 00 <DigestInfo>` or `00 02 <nonzero pad> 00 <msg>`) or **PSS** (`…BC` trailer,
recoverable `01` delimiter in the DB after MGF1 unmasking) structure. **H0:** no structure.

This is a **zero-false-positive** test: the match is a structural predicate, not a score.
The probability that a random 256- or 512-byte block satisfies the v1.5 predicate (leading
`00 01`, then ≥8 bytes of `FF`, then `00`) is ≈ 2⁻¹⁶ × 2⁻⁰ … ≈ 10⁻⁵ at the very loosest and
~2⁻⁸⁰ for the full DigestInfo form; PSS with a valid MGF1-recovered `01` delimiter is ~2⁻⁶⁴.
There is no threshold to tune. **HIT = structure match. No structure = null.**

### B.2 The named coverage gap being closed

Round 16 (`round16/SYNTHESIS.md` §zeroFP) ran E-01 partially and recorded the exact reason it
is incomplete: only the 2013 **432-bit** modulus was on disk (too small to hold a 2048-bit
payload), and *"the 7A35090F RSA-4096 moduli (the correct size) were not on disk and not
fetched."* This lane fetches them.

**Moduli to be covered:** every RSA modulus recoverable from 3301's canonical public key
`0x7A35090F` (primary key **and** every subkey), plus the 2013 puzzle modulus already on
disk, plus any other published 3301 modulus found in `corpus/` or the round10 L6 archive.
Fetch order: local `corpus/` and `analysis/round10/L6-archives/fetched/**/*.asc` first,
then keyservers (`keys.openpgp.org`, `keyserver.ubuntu.com`, `pgp.mit.edu`), then community
mirrors. **The fingerprint must be verified** (`gpg --fingerprint`) and recorded in RESULTS
before any modulus is used; an unverified key is reported as unverified and its result is
labelled accordingly.

### B.3 Instrument

Extend `analysis/round16/zeroFP/zerofp_tests.py` — which already accepts additional moduli —
rather than rewriting it. Cover, for each modulus `n` of bit-length `L`:

- `s` = payload big-endian, `s` = payload little-endian (= byte-reversed);
- `s` = payload left-aligned into an `L`-bit block (zero-padded low) and right-aligned
  (zero-padded high), for `L > 2048`;
- `e` ∈ {65537, 3, 17} (the exponents actually published on 3301 keys, plus the classic
  small ones);
- also `pow(s, e, n)` on the **decimal-preferred** variant and on each resolved/candidate
  payload variant from Part A.

### B.4 Positive control — **mandatory**

Generate an RSA key locally, sign a message with genuine PKCS#1 v1.5 and with PSS, and
confirm the matcher **fires** on both, and does **not** fire on 10,000 random blocks of the
same length. Both numbers are reported. If the v1.5 matcher does not fire on a genuine
signature, or the false-positive count on random blocks is non-zero, the E-01 result is not
trusted and is reported as instrument failure.

### B.5 Decision rule

HIT iff a structural match. Anything else is a null, reported with the explicit list of
moduli, exponents and encodings covered, and what is not covered.

---

## Part C — E-02

E-02 is recorded **negative / complete** in Round 16 (`LEDGER.json` E-02: E-02A 201 windows
exhaustive, zero permutations; E-02B max |Spearman r| < 0.05). Its `not_covered` is `null`.
Per Rule 7 this lane does **not** re-run E-02 as specified. The only extension taken is the
free one: re-running the *existing* E-02 script over the corrected/variant payloads from
Part A, which is a coverage extension of Part A's propagation, not a new E-02 sweep.

---

## Registered nulls / what would falsify

- A-04 null: the calibration gate fails (<38/40), or the 6 cells fail 3-pass concordance.
- E-01 null: no structural match on any (modulus, exponent, encoding, payload-variant) tuple
  while the positive control fires on genuine signatures.

## Deliverables

`PREREG.md` (this file), scripts, `payload_resolved.json` (per-byte value + confidence),
`RESULTS.md`, `ledger.json`.

_No `git commit` from this lane (Rule 8)._
