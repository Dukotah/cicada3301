# Round 18 / L6 — OFFSET & MARSAGLIA — RESULTS

_Pre-registration: [`PREREG.md`](PREREG.md), written before any offset was scored. Machine-readable
record: [`out/digest.json`](out/digest.json), [`ledger.json`](ledger.json),
[`data/MANIFEST.json`](data/MANIFEST.json)._

_Trust anchor, run for this lane: `python3 liber-primus/tests/validate.py` -> **ALL VALIDATIONS
PASSED - rig reproduces known solves** (`out/validate.log`)._

**Two named, live, never-swept gaps, both now measured.** Neither returned a hit. What follows is
coverage, not a conclusion (AGENTS.md §7).

---

## 0. The headline numbers

| | sub-lane A — OFFSET (B-02 / B-08) | sub-lane B — MARSAGLIA CDROM |
|---|---|---|
| offsets densely scored | **`497,025,024`** | **`1,539,996,304`** |
| best `score_norm` | **`-6.7702`** | **`-6.7387`** |
| bar — `threshold_for(N)` at the **true** trial count | **`-5.4664`** | **`-5.3844`** |
| bar — this lane's own ms=8 shuffle null, `null_max + 0.5` | `-6.4847` | `-6.4847` |
| distance below the binding bar | `1.304` | `1.354` |
| positive control, **on the real pad family** | **`PASS — 40/40 = 1.0`** | **`PASS — 16/16 = 1.0 (ms=8)`** |
| verdict | NEGATIVE for the coverage in §3 | NEGATIVE for the coverage in §4 |

Nothing here uses the habitual fixed −5.5 as its bar (Round 18 rule 4). `threshold_for()` is
evaluated at each sub-lane's own trial count and reported above; it carries −5.5 only as a floor,
so it is never looser than the habitual bar.

---

## 1. Why these two gaps were worth a lane

**Offset ≠ 0 multiplies every derived-key sweep this project has run.**
`research/ROUND-8-RESULTS.md` says its sweep *"assumes key index 0 aligns with the first rune of
LP2 page 0"*. That is not a detail; it is a dimension that was fixed at a single value:

| sweep | decodes | offsets covered |
|---|---|---|
| Round 8 seeded-PRNG | 2.52 × 10⁹ | **offset 0 only** |
| Round 13 B-04 stage A | 1,385,600 | **offset 0 only** |
| Round 13 B-04 stage B | 1,290,240 | 10: {1,4,16,29,64,128,256,512,1024,3301} |
| Round 13 B-04 stage C | 3,548,160 | 55 per-page restarts, all keyed from index 0 |
| Round 16 KDF | 692,064 | **offset 0 only** |
| Round 16 PRNG family | 52,556 | **offset 0 only** |

`PARKED.md` P-10 scores the omission at **×8,192 for even a modest range, and notes it multiplies
*every* generator**. B-04's own PREREG §6 lists "offsets beyond 3301" as explicitly not covered.

Round 17 fixed precisely this defect **for external pads** — `round17/lib_padsweep.py` replaced
A1's eight-offset ladder with a dense scan that scores *every* offset — and the **derived/seeded**
branch never received the same instrument. This lane applies it there.

**The Marsaglia CDROM was named, found, and left alone.** `round17/SYNTHESIS.md` §"corrections"
and P2's own source table record it as the single live, reachable, unswept public-pad item —
*"the cheapest live item in this branch"* — 634,124,288 bytes of published physical randomness
from 1995, with published SHA-256s, and a verified HTTP 206 from archive.org. Lane P2 wrote down
its identifier and moved on. **Nobody had ever fed it to the decoder.** Now someone has.

---

## 2. Instrument — what was audited before anything was swept

`scripts/audit_builders.py`, run first, all checks PASS ([`out/audit.json`](out/audit.json)):

1. **The `ks_hexchars` defect, re-derived rather than cited.** On a 4,096-byte blob the hex string
   is 8,192 characters and `ks_hexchars` keeps **2,944 (35.9 %)**. It is excluded from this lane
   and `ks_nibbles` — the true hex reading, length-conserving — used instead.
   > **A second, smaller defect found here and not recorded in Round 17.** Beyond dropping the
   > digits 0–9, `eng_to_idx` also **collapses the runic digraphs `AE` and `EA`**, so `hexchars`
   > keeps **128 fewer** symbols than even the A–F subsequence (3,072 A–F characters → 2,944
   > symbols on this sample). The published characterisation "the A–F subsequence" is therefore
   > slightly optimistic: it is the A–F subsequence *with AE/EA merged*. It does not change any
   > Round-17 verdict — that builder returned noise — but the next person reading
   > `lib_padsweep.ks_hexchars`'s docstring should know its stated limitation is incomplete.
2. **Builder equivalence.** This lane's shardable builders are asserted **bit-identical** to
   `lib_padsweep`'s whole-blob builders on all six (mod29, hi_nibble, lo_nibble, byte_scaled,
   prime_to_idx, nibbles).
3. **Sharding loses no offset.** `sharded_scan` reproduces the whole-blob `dense_scan` top-50
   exactly, on two builders, with 0 mismatches — which is what licenses sweeping a 634 MB pad in
   32 MiB pieces.
4. **The beam, never rigid** (AGENTS.md §4 lesson 2): a planted key recovers at **−4.176 / 1.000
   rune match** at ms = 8.
5. **The bar is stricter than −5.5 at this lane's N**: `threshold_for(1.8 × 10⁹) = −5.3731`,
   `threshold_for(1.8 × 10¹⁰) = −5.2062`.

**`max_skip = 8` everywhere**, per Round 17/P1 (its strict control *failed on its real pad* at
ms = 3, 6/8; 60/60 at ms = 8). Both of this lane's controls are planted in the **real** pad
family, not a synthetic one, and sub-lane B runs the ms = 3 diagnostic alongside so the
constant-run question is *measured on Marsaglia* rather than assumed in either direction.

**No ×0.625 survival constant is used anywhere.** Round 17 measured 0.375–0.875, non-monotone in
pad size. This lane measured its own, per sub-lane, and reports it as the coverage discount.

### 2.1 A note on `threshold_for`'s segment-length argument

`benchmark/null.py: threshold_for(n_trials, segment_len=...)` **accepts `segment_len` and does not
use it.** Its Gumbel constants (μ = −7.2517, β = 0.0725) are tail-calibrated on L ≈ 120 windows —
the file's own CALIBRATION block says so — while this lane adjudicates on a **400-rune** window.
`scripts/nulls_l6.py` therefore measures this lane's null at **both** lengths on the real keystream
families, to establish the direction of that mismatch empirically rather than by assertion:

| keystream family | null mean (L=400) | null max (L=400) | null max (L=120) |
|---|---|---|---|
| `derived:sha512_ctr|mod29` | -7.3139 | -7.0024 | -6.7164 |
| `derived:iter_sha256_100000|rej29` | -7.2979 | -6.9947 | -6.5846 |
| `marsaglia:BITS.01|mod29` | -7.2670 | -6.9847 | -6.6709 |

> threshold_for()'s Gumbel constants are tail-calibrated on L~120 windows and the function ignores its segment_len argument. This lane adjudicates on L=400. The measured L=400 null max is LOWER than the L=120 null max, so applying the L~120-calibrated bar to L=400 scores is CONSERVATIVE - it can only make a hit harder to claim, never easier.

This also explains why scores here look *lower* than the originating lanes' published maxima
(B-04 stage A best −6.185, R16-KDF −6.259, R16-PRNG −6.347): those were best-of-N on a **120**-rune
window, this lane adjudicates on a **400**-rune window, and a longer window has a lower null. The
two numbers are not comparable, and the bar used here is the one measured here.

---

## 3. Sub-lane A — OFFSET

### 3.1 The offset range, and the argument for its bound

Not "as far as we could afford" — the bound is past the largest artifact any named mechanism
could produce:

| mechanism that displaces key index 0 | offset implied |
|---|---|
| the author enciphered the earlier Liber Primus pages first (this repo holds 1,796 solved runes; the circulating book is ≈14.7 k) | 1,796 … ≈14,752 |
| a file header or fixed skip in a generated pad file | 512 · 1,024 · 4,096 · 8,192 · 65,536 |
| hash/cipher block alignment (16/20/32/64/128 B digests × a round count) | multiples of 16…128 |
| page/section restarts and lore constants — the 57 cumulative segment starts, 3301·k | ≤ 12,956 |
| **a 1 MB generated pad file consumed from the middle** — the modal artifact of a "make me a pad" script | ≤ 1,048,576 |

**Stage A1 scans every integer offset in [0, 2²⁰).** That subsumes every row by construction:
71× the entire Liber Primus, and the full length of a 1 MB pad file. Relative to the offset-0
assumption this is **×1,048,576** coverage, against PARKED P-10's "×8,192 for a modest range".
Stage A2, with ~6,000× more configs, scans [0, 2¹⁸) — still 17.8× the whole book.

### 3.2 Stage A1 — the mined survivors, re-swept densely — **COMPLETE**

No prior sweep was re-run (Round 18 rule 7). The **220 distinct configs** were *read* from the
published results JSON of the three lanes that fixed this axis at 0 — B-04 `results_{A,B,C}.json`
top-50 each, R16-KDF `results_A.json` top-50, R16-PRNG `results.json` top-20 — and each config's
keystream was rebuilt **with the originating lane's own code**, extended, and scanned at every
offset.

| | |
|---|---|
| configs | **220** (B-04 ×150 rows dedup, R16-KDF ×50, R16-PRNG ×20) |
| offsets scored | **230,686,720** |
| escalation | top 40 dense survivors per config, beam `head=400 / w=120 / ms=8` |
| best | **−6.8093**, offset **45,081**, `pbkdf2_sha1_10000 | rej29`, seed label `thematic` |
| `threshold_for(230,686,720)` | **−5.5000** (the floor still binds at this N) |
| over bar | **0** |

The top of the distribution is flat and structureless — the eight best sit in −6.81 … −6.86,
spread across three different originating lanes (KDF, B-04, PRNG) and three generator families.
That is the shape of a best-of-N order statistic, not of a signal with a preferred offset.

**Every one of the 220 configs got *worse* than its published offset-0 score**, which is exactly
right and is worth stating plainly: the published scores were maxima over a 120-rune window, these
are maxima over a 400-rune window, and adding text is precisely what a lucky key cannot survive.

### 3.3 Stage A2 — a fresh seed × offset grid on the highest-prior constructions

504-entry B-04 core dictionary × 6 highest-prior generators (`sha256_ctr`, `sha512_ctr`,
`sha1_ctr`, `md5_ctr`, `sha256_chain`, `hmac_sha256_ctr`) × `mod29` × both signs, dense over
[0, 2¹⁸), escalating the top 12 dense survivors per (seed, generator, sign).

| | |
|---|---|
| units run | **508 / 3,024** (16.8% of the planned grid — bounded by this lane's compute budget; the sweep is checkpointed per unit and resumes without recomputing) |
| offsets scored | **266,338,304** |
| escalation | top 12 dense survivors per (seed, generator, sign), beam `head=400 / w=120 / ms=8` |
| best | **-6.7702**, offset 253,446, `sha256_chain`, seed label `slogan`, sign 1 |
| `threshold_for(266,338,304)` | **-5.5000** |
| over bar | **0** |

### 3.4 Sub-lane A positive control — **PASS**, on the real keystream family

`scripts/control_offset.py`, [`out/control_offset.json`](out/control_offset.json). Cicada-register
English (335 runes) enciphered under the anti-repeat filter at supp = 0.83, planted at a uniformly
random offset in [1000, 2²⁰) inside a **real** derived keystream — a real B-04 dictionary seed, a
real generator, a real reduction, **8 distinct configs** — and pushed through the *identical*
`dense_scan → beam` pipeline at ms = 8.

| quantity | value | what it is |
|---|---|---|
| **recovery** | **40/40 = 1.000** | the gate. The beam recovers >95 % of **rune indices** at the true offset, every time, at beam scores ≈ **−4.28** (deep in the English band, against a noise mean near −7.3) |
| **survival**, keep = 1000 | 26/40 = **0.650** | fraction of true offsets the dense prefilter retains at all |
| **survival**, escalation depth 40 | 21/40 = **0.525** | stage A1's effective offset discount |
| **survival**, escalation depth 12 | 21/40 = **0.525** | stage A2's — *identical*: when a true offset survives the prefilter at all, it is essentially always inside the top 12, so A2's shallower escalation costs nothing |

**Read the two rows together.** Recovery 1.000 means the adjudicator is sound: if a true offset
reaches the beam, the beam finds it and says so loudly. Survival 0.525 means the *prefilter* is
where the power is lost: roughly **47 % of true offsets would never reach the beam**. That is a
power bound on this sub-lane, not a soundness one, and it is the honest discount on the coverage
claim: **230.7 M offsets scanned ≈ 121 M effective** in stage A1. No ×0.625 constant was used;
this number was measured.

---

## 4. Sub-lane B — THE MARSAGLIA RANDOM NUMBER CDROM (1995)

### 4.1 Acquisition and verification — **ALL GATES PASS**

This repository has twice swept the wrong bytes (`_560.00` arrived as a silent 60.4 % prefix;
`DATA/560.13` arrived as a 134-byte Git-LFS pointer). So nothing was scored before the hashes
matched. [`data/MANIFEST.json`](data/MANIFEST.json) carries all of it.

| object | value |
|---|---|
| archive.org item | `marsaglia-cdrom` (creator: George Marsaglia) |
| `MARSAGLIA_CDROM.iso` size | **634,124,288 bytes** — exactly the published size |
| md5 | `f127d50c2bd80e7c23f28184423a2d94` — **matches** archive.org item metadata |
| sha1 | `ca116df4940eb4b7538942ea6fbe454556b1bac2` — **matches** archive.org item metadata |
| **sha256 (computed here; archive.org publishes only md5+sha1)** | **`6d124080f942a88afade2d6cd2da4b9f092e0e376ee5a9d4af9f7224523f9d28`** |
| `checksums.sha256.txt` — the CDROM's own published per-file manifest | 110 lines; its own sha256 `e0e4daa152c093fe6651ec63352b27a7a247a839af6a757cb62f26fb1fa7f82f` |
| inner files verified against those published SHA-256s | **110 / 110 matched** |
| random-data pads recovered | **63 files, 630,000,000 bytes**, every one hash-verified: `BITS.01`…`BITS.60`, `CALIF.BIT`, `CANADA.BIT`, `GERMANY.BIT` |

**The Marsaglia verdict on provenance: clean.** The bytes we swept are the published bytes, and
the sha256 above is recorded here because the archive publishes only md5 and sha1 for the ISO —
the next person can now check against a SHA-256 as well.

### 4.2 What was swept

| | |
|---|---|
| pads swept | **63** of the 63 hash-verified random-data files |
| units run | **77 / 756** (pad x builder x byte-order), builder-major order |
| builders actually completed | **`mod29_fwd` (63/63 pads), `mod29_rev` (14/63 pads)** |
| builders queued but not reached inside the compute cap | `byte_scaled_fwd`, `byte_scaled_rev`, `hi_nibble_fwd`, `hi_nibble_rev`, `lo_nibble_fwd`, `lo_nibble_rev`, `nibbles_fwd`, `nibbles_rev`, `prime_to_idx_fwd`, `prime_to_idx_rev` |
| offsets scored | **1,539,996,304** |
| best | **-6.7387** — `BITS.22` / `mod29`, sign +1, offset 7,710,875 |
| `threshold_for(1,539,996,304)` | **-5.3844** |
| over bar | **0** |

**Configured** builders: `mod29`, `hi_nibble`, `lo_nibble`, `byte_scaled`, `prime_to_idx`,
`nibbles` — Round 17's set with `hexchars` **excluded** (§2, and the exclusion is stated rather
than silent) and `nibbles` used in its place. Both byte orders, both signs, every offset,
`max_skip = 8`, escalation top 40 per (pad, builder, byte-order, sign). **The table above says
which of them actually completed inside this lane's compute cap; the rest are queued, not done,
and are listed in §5.3.** Job order is deliberately **builder-major** precisely so that a budget
cut leaves a clean statement — *"`mod29` forward is complete across all 63 pads"* — rather than a
ragged sample, and so that resuming picks up whole builders.

### 4.3 Sub-lane B positive control — **PASS, on the real Marsaglia bytes**

`scripts/control_marsaglia.py`, [`out/control_marsaglia.json`](out/control_marsaglia.json).

| quantity | ms = 8 | ms = 3 (diagnostic) |
|---|---|---|
| **recovery** (>95 % of rune indices, real pads) | **16/16 = 1.000** | `16/16 = 1.0` |
| survival, keep = 1000 | 9/16 = **0.5625** | — |
| survival, escalation depth 40 | 9/16 = **0.5625** | — |

Beam scores at the true offset were **−4.352** on every trial. The measured survival **0.5625** on
10 MB pads is this sub-lane's coverage discount — again measured, not the ×0.625 constant.

**And a measured answer to Round 17's open instrument question, for this pad.** P1 found ms = 3
fails on pads with constant byte runs; P0 found it does not bite on high-entropy ISO-carved blobs.
Marsaglia's random-data files are firmly in P0's regime — `BITS.01` is **0.390 % zero bytes with a
longest constant run of 3 bytes in 10 MB**, `GERMANY.BIT` 0.478 % / run 4 — so the *validity test*
inside `beam_decode` binds, not the skip budget. The **ISO as a whole is not**: its first 16 MiB
contain a **32,768-byte constant run** (filesystem padding), which is exactly P1's failure regime.
`**Measured here: ms = 3 does NOT bite on the Marsaglia random-data files** — recovery was 16/16 at both skip budgets, reproducing P0's finding on a new pad family and confirming its explanation (on a high-entropy pad the beam's skip *validity* test binds, not the budget).` This is why ms = 8 was pre-registered for everything and why the whole-ISO view is
tracked separately from the 63 random-data pads.

---

## 5. Coverage — read this, not the verdict

### 5.1 What sub-lane A measured

- **220 mined configs** — every surviving top-50 row of B-04 stages A/B/C, every top-50 row of
  R16-KDF, every top-20 row of R16-PRNG — each scanned at **every integer offset in [0, 2²⁰)**.
  For these configs the offset axis is now dense and **should not be re-run**.
- Stage A2: 508 of 3,024 planned (seed x generator) units, 266,338,304 offsets, every integer offset in [0, 2^18) for each unit run. The remaining 2,516 units are checkpointed-resumable and are listed as not-covered below.
- Effective coverage after this lane's **own measured** prefilter survival (0.525 at escalation
  depth): `497,025,024 scanned -> approximately 260,938,137 effective`.
- The adjudicator's power is established: planted English recovers at 40/40 with beam ≈ −4.28
  against a null mean ≈ −7.3.

### 5.2 What sub-lane B measured

- The object is **provenance-clean**: 110/110 published SHA-256s verified, ISO md5+sha1 matching archive.org, size exact. That result stands on its own and does not depend on how much of the sweep completed.
- **1,539,996,304 offsets** densely scored across **63 pads** and 77/756 (pad x builder x byte-order) units, both signs, max_skip=8.
- Effective coverage after this sub-lane's own measured prefilter survival (0.5625): approximately 866,247,921 offsets.
- The adjudicator's power on THIS pad is established: 16/16 planted recoveries at beam -4.352 against a null mean near -7.3.

### 5.3 What is NOT covered — declared in PREREG §6, restated with the numbers

**Sub-lane A**
- **Offsets beyond 2²⁰** (A1) / **2¹⁸** (A2). A pad file *larger than 1 MB*, consumed past its
  first megabyte, is untouched. Reopening this needs only one new argument: a mechanism that
  generates a pad file bigger than 1 MB.
- **Offset *schedules*.** Only a single constant offset into one keystream was tested — not
  per-line, per-page or non-integer restart schedules, and not a keystream that is restarted with
  a different offset per page.
- Seeds outside B-04's 2,165-entry dictionary (A1) and its 504-entry core (A2); generators outside
  the 16 in `round13/B04/ks.py`, the 27 KDF configs of R16-KDF and the 7 of R16-PRNG; reductions
  other than `mod29` in stage A2; filters other than the pinned soft key-skip at supp = 0.83;
  composite plaintext transforms.
- **A ~47 % prefilter blind spot on offsets.** Measured, not assumed. This is *power*, not
  soundness: beam recovery was 100 % on every plant. The cheap fix is a wider `keep` window and a
  deeper escalation — it costs beam time and nothing else.
- `dir=rev` rows from the mined set were swept as **new coverage** of the "author generated an
  L-byte pad file and read it backwards" hypothesis at L = 2²⁰ + slack, *not* as an extension of
  the original row: reversing a longer generated stream is a different keystream, and that was
  declared in PREREG §3.2 before the run.

**Sub-lane B**
- **679 of 756 (pad x builder x byte-order) units were not run** — this lane was capped on compute, not on method. Because the job order is builder-major, the shortfall is whole builders rather than a ragged sample; `out/results_M.json` names exactly which units are done. The whole-ISO view (as distinct from the 63 random-data files, and the only view that can see an offset straddling a file join or landing in the disc's non-random members) was **not swept** in this run. All of it is checkpointed-resumable: re-running `scripts/sweep_marsaglia.py` continues from where this stopped and recomputes nothing.
- Keystream constructions outside the six builders; window lengths other than the 400-rune head;
  the disc's code, documentation and PostScript members as pads in their own right (they were
  hash-verified, but only the 63 random-data files were swept, and only under the builders
  the table in §4.2 lists as completed).
- The measured **0.5625** prefilter survival on 10 MB pads: ~44 % of true offsets would not reach
  the beam. Power, not soundness.

### 5.4 The three conditionals this negative carries

Round 18's own lane L7 measured two things that qualify **every** negative in this repository,
including both of this lane's. They are stated here rather than left for a reader to discover:

1. **The key space swept** — §5.1 and §5.2. This is the only conditional the repo used to report.
2. **The decoder's transition model.** L7-B: the skip-aware beam's transition relation is exact
   for *one* rejection-loop implementation. `skip_by_two` — a one-character variant that
   reproduces LP2's observed doublet rate — is scored at −6.90 / 25.8 % recovery, and raising the
   beam width and skip budget changes that by **exactly 0.000**. Both sub-lanes here use that
   decoder, so both negatives are conditional on that construction.
3. **The adjudicator's register.** L7-A: handed the *correct* key, the beam recovers 100 % of
   runes for Latin, Old English, German, Welsh and abbreviated English — and the English quadgram
   adjudicator then scores the result as noise (power 0.33 for Latin, 0.00 for vowel-dropped
   English). **Every score in this file is an English score**, so both verdicts are English-only
   negatives.

Partial mitigation, measured rather than promised: `scripts/langagnostic.py` re-decodes each
stage's top survivors at their recorded offsets and re-scores them under an **8-register trigram
panel** — modern English, LP1's own solved plaintext, Latin, Old English, German, Welsh,
vowel-dropped and half-vowel-dropped English — plus three language-free statistics (decrypt
IoC·N, minimum distinct symbols over a 32-rune window, zlib ratio), each against a matched null
band built by pushing shuffled ciphertext through the same path.

**Result.** 1 survivor/statistic pairs outside the null band - INSPECT

| stage | survivors re-scored | best English | best register score (panel) | IoC*N | min distinct / 32 |
|---|---|---|---|---|---|
| A1 | 20 | -6.8093 | -1.4625 (`LP1_REAL`) | 0.975-1.056 | 14-17 |
| A2 | 20 | -6.7702 | -1.4619 (`LP1_REAL`) | 0.986-1.082 | 14-16 |
| M | 20 | -6.7387 | -1.4645 (`LP1_REAL`) | 0.987-1.087 | 14-16 |

Matched null band (n=60 shuffled-ciphertext decodes through the same path): ioc_times_n mean 1.008 sd 0.020; min_distinct_32 mean 15.467 sd 0.884; zlib_ratio mean 0.677 sd 0.004. Register null maxima: `CY` -1.6372, `DE` -1.6622, `EN_HALFVOWEL` -1.6438, `EN_MODERN` -1.7262, `EN_NOVOWEL` -1.6089, `LATIN` -1.7301, `LP1_REAL` -1.4629, `OE` -1.6672.

**One row tripped the wire, and is reported rather than quietly dropped.** `BITS.22` / `mod29`, offset 7,710,875, English score -6.7387, came in at **IoC*N = 1.0873** against a null band of mean 1.0082 / sd 0.0197 — 4.0 sigma, just past this lane's 4-sigma trip wire.

**It is a selection artifact, and the reference number says so immediately.** Real Liber Primus plaintext — the repo's own solved pages — has **IoC*N = 1.7570** over 1,768 runes; the ciphertext has 0.9999. The flagged row sits at 1.0873, i.e. essentially at the ciphertext's own value and nowhere near plaintext. The survivors re-scored here were not random draws: they were selected as the maximum English score over ~1.5e9 offsets, and English score and IoC are positively correlated, so a mildly elevated IoC on the single best row is what the selection produces on its own.

**And it was escalated anyway** (PREREG §2.2, Round 13 stage D's protocol), even though at -6.7387 it sits below the −6.00 tier-2 gate:

| window | runes | score | IoC*N |
|---|---|---|---|
| `head400` | 400 | -6.7387 | 1.0873 |
| `page0_full` | 262 | -6.7410 | 1.1077 |
| `full_stream` | 12,956 | -7.2720 | 1.0095 |

> no flagged row improves under escalation - every one decays toward the noise mean, which is the signature of a lucky draw, not a key. A correct key improves as text is added; this one does not.

This covers the **survivors**, not every row: the sweeps were launched before
`ARMADA-DOCTRINE.md` R3 existed and their discarded rows cannot be re-interpreted. That gap is
real and is recorded in PREREG Addendum B rather than papered over.

### 5.5 Round 17's residue — what this lane took and what it left

`round17/SYNTHESIS.md` names as unswept: the Marsaglia CDROM; non-contiguous blockchain selections;
the beacon past 2013-11-13; other chains, txids, coinbase scriptSigs, chainwork; keystream builders
outside the seven tested; and P3's 13 short pads.

- **Taken:** the Marsaglia CDROM (§4) — the one Round 17 called cheapest. And the *builder* residue,
  in the form of `nibbles` on every Marsaglia pad, which is new-coverage for a binary pad
  (`hi_nibble`/`lo_nibble` see the two nibble streams separately, never interleaved in order).
- **Left, with the reason:** non-contiguous blockchain selections and other chains (each needs a
  fresh multi-GB fetch — a lane of its own, not a residue item); the beacon past 2013-11-13 (same);
  P3's 13 short pads (their bound is a *window* bound, not an offset bound, so it is not this
  lane's gap). Round 17's gitignored corpora were not present in this working tree, so the
  opportunistic re-sweep declared in PREREG §5.5 R-2 did not run and is reported as not-covered
  rather than quietly dropped.

---

## 6. What would change these verdicts

- Any decode at or above its own `null_max + 0.5` **that also improves** when escalated to full
  page 0 and the full 12,956-rune stream. A correct key gets better with more text; a lucky one
  decays. Nothing in either sub-lane came within `1.304` of the bar.
- Sub-lane A: a mechanism producing a pad file larger than 1 MB; or a wider seed dictionary or a
  generator outside the swept sets, **proposed together with an offset sweep** — the offset axis is
  now dense for the configs listed here and re-running it for them is wasted compute.
- Sub-lane B: a byte order, reduction or window outside those in §4.2; or the units listed as not
  done in [`out/results_M.json`](out/results_M.json).

---

## 7. Artifacts and how to reproduce

```
PREREG.md  RESULTS.md  ledger.json
data/MANIFEST.json          110/110 published SHA-256s + the ISO's md5/sha1/sha256
out/audit.json              instrument audit (5 checks, all PASS)
out/nulls.json              this lane's own ms=8 null at L=400 and L=120
out/control_offset.json     sub-lane A control, 40 trials, real derived keystreams
out/control_marsaglia.json  sub-lane B control, 16 trials x2 skip budgets, real Marsaglia bytes
out/results_A1.json         220 configs x 2^20 offsets
out/results_A2.json         504 seeds x 6 generators x 2 signs x 2^18 offsets
out/results_M.json          Marsaglia, per pad x builder x byte order x sign
out/digest.json             the numbers in this file, machine-readable
scripts/                    lib_l6.py audit_builders.py nulls_l6.py fetch_marsaglia.sh
                            verify_marsaglia.py control_offset.py control_marsaglia.py
                            sweep_offset.py sweep_marsaglia.py assemble.py
```

```bash
cd liber-primus/analysis/round18/L6-offset-marsaglia
python3 scripts/audit_builders.py          # instrument gates, must PASS first
python3 scripts/control_offset.py          # sub-lane A control
python3 scripts/sweep_offset.py --stage A1 # resumable, checkpointed per config
python3 scripts/sweep_offset.py --stage A2
bash    scripts/fetch_marsaglia.sh         # 634 MB, resumable
python3 scripts/verify_marsaglia.py        # refuses to proceed unless hashes match
python3 scripts/control_marsaglia.py
python3 scripts/sweep_marsaglia.py         # resumable, checkpointed per pad x builder
python3 scripts/assemble.py                # regenerates ledger.json + out/digest.json
```

Every sweep is checkpointed per work unit and resumes without recomputing; `assemble.py` is
idempotent and can be re-run after any extension to update the coverage numbers.
