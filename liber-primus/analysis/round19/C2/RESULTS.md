# Round 19 / C2 — CLOSEOUT of Round 18 lane L6 (OFFSET & MARSAGLIA) — RESULTS

_Ran 2026-08-26. Pre-registered in [`PREREG.md`](PREREG.md) before any scoring code of this
lane executed. Inherited thresholds: [`round18/L6-offset-marsaglia/PREREG.md`](../../round18/L6-offset-marsaglia/PREREG.md),
**not edited**. Binding: [`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Trust anchor, before and after this lane — both PASS, unchanged:**

| | before | after |
|---|---|---|
| `python3 liber-primus/tests/validate.py` | ALL VALIDATIONS PASSED (5/5) | ALL VALIDATIONS PASSED (5/5) |
| `python3 -m pytest liber-primus/benchmark/ -q` | 8 passed | 8 passed |

---

## 0. Headline

1. **B-02 is quantified for the first time.** Across the derived-key branch, **0.054 %** of
   2,531,663,008 published decodes were ever run at a nonzero key offset, and **16 distinct
   offsets** have ever been tested — largest 3,301 — which is **1.5 × 10⁻⁵** of the
   mechanism-bounded offset axis. Round 18/L6's sub-lane A1 is the first dense coverage the
   branch has ever had, and it is dense for **220 configs**, not for the branch.
2. **The Marsaglia CDROM is real and intact.** Recomputed from the bytes on disk against the
   published digests, ignoring the lane's own manifest: **112 PASS, 0 DRIFT, 0 ABSENT**;
   110/110 inner files match their published SHA-256; 63 hash-verified 10 MB random-data pads.
3. **DECISION: staged hold** — B-02 accounting, data gate, space quantification and one
   instrument measurement run now; the 17.6 × 10⁹-offset Marsaglia sweep and the fresh A2 grid
   **held** for Round 19 Phase 0 (I1/I2).
4. **The measurement that justifies the hold — and it is stronger than the inference was.**
   L7-A.7 said no non-English prefilter survival had ever been measured. It has now, on these
   very pads: the English trigram prefilter retains an **English** true offset **0.767–0.800**
   of the time and a **vowel-dropped-English** one **0.000** (0/30), half-vowel English
   **0.067**, Welsh **0.300**. Composite pipeline power (prefilter × L7-A adjudicator) for
   vowel-dropped English is **0.000 × 0.00**; for Latin **0.23**; for the register the Liber
   Primus actually uses, **0.77**. Pre-registered verdict: **FOUND-GAP**.
5. **A measured way to recover some of it, for free.** In the one register where the trigram
   prefilter is completely blind (`EN_NOVOWEL`, 0.000), a language-agnostic screen on the *same
   24-rune window* retains **0.133** — 1,300 × the chance rate. The screens cost nothing: they
   come out of the plaintext matrix `dense_scan` already builds.

Nothing in this lane cleared any bar. Every negative below carries its three conditionals (§6).

---

## 1. What was inherited, and what C2 did with it

Round 18's L6 was written, launched and abandoned with **no `RESULTS.md`**. It has one now:
[`../../round18/L6-offset-marsaglia/RESULTS.md`](../../round18/L6-offset-marsaglia/RESULTS.md),
written by a concurrent continuation of the L6 lane itself during C2's window (see the
disclosure below). C2 did **not** overwrite it — it appended **§8, a closeout addendum**
carrying this lane's four results. Round 18's record is complete either way.

| item | C2's action |
|---|---|
| B-02 / B-08 offset accounting | **RAN IN FULL** (§2) — instrument-independent arithmetic |
| Marsaglia hash verification | **RE-RAN INDEPENDENTLY** (§3) — did not trust the lane's own manifest |
| Marsaglia offset space + cost | **QUANTIFIED** (§5) |
| prefilter register power | **MEASURED** (§4) — new; the number L7-A.7 named and nobody had taken |
| sub-lane A1 (complete) | **REPORTED AS-RUN** (§5.1), not re-run |
| sub-lane A2 (partial), sub-lane B (partial) | **HELD** for I1/I2; state reported, not extended (§5.2) |

> **Disclosure.** During C2's window a **concurrent continuation of L6's own sweeps**
> (`sweep_marsaglia.py --nproc 3 --budget 2700`, `sweep_offset.py --stage A2`) was running in
> this worktree, started by another process. C2 neither launched nor extended it, and did not
> kill it. All sub-lane A2 / B counts below are **frozen at C2 collection time** (both
> processes had exited); that continuation also produced `out/nulls.json`,
> `out/langagnostic.json`, `out/digest.json`, the L6 `ledger.json` and L6's own `RESULTS.md`,
> which are cited where they bear on the result. One finding of theirs is worth surfacing here
> because it sharpens a Round 17 correction: `eng_to_idx` does not only drop the digits 0–9 in
> `ks_hexchars`, it also **collapses the runic digraphs `AE` and `EA`**, so that builder swept
> the A–F subsequence *with AE/EA merged* — 35.9 % of the hex string, not the 36.8 % Round 17
> published. No verdict moves; the docstring's stated limitation is incomplete.

---

## 2. B-02 — the offset-coverage accounting

**Method.** Pure arithmetic over committed artefacts — no decoder, no scorer, no threshold, so
it cannot be a false negative and Phase 0 cannot invalidate it. Every offset count is read from
the originating lane's own result JSON or from the line of its own sweep source that fixes the
offsets. Nothing is taken from prose.
Script: [`scripts/offset_coverage.py`](scripts/offset_coverage.py) → [`out_offset_coverage.json`](out_offset_coverage.json).

**The denominator.** For a derived key the offset axis is countably infinite (you can always
generate more keystream), so the honest denominator is a *mechanism bound*. L6 PREREG §A.1
argues **2²⁰ = 1,048,576** subsumes every named mechanism: the author enciphering LP1 first
(≤ 14,752), a file header or fixed skip (≤ 65,536), digest-block alignment, 3301·k, and a 1 MB
generated pad file consumed from the middle. A 2³² sensitivity column is given below. For an
external pad the axis is exact: the pad's length in symbols.

### 2.1 The table

| sweep | decodes | distinct key offsets | fraction of the 2²⁰ axis |
|---|---:|---:|---:|
| Round 8 SEED — time-seeded PRNG, 10 gens × 2011–2015 | 2,524,608,000 | **1** `{0}` | 9.54 × 10⁻⁷ |
| Round 8 SEED — non-integer / lore seeds | 15,408 | **1** `{0}` | 9.54 × 10⁻⁷ |
| Round 13 B-04 stage A — broad screen | 1,385,600 | **1** `{0}` | 9.54 × 10⁻⁷ |
| Round 13 B-04 stage B — **the offset stage** | 1,290,240 | **10** `{1,4,16,29,64,128,256,512,1024,3301}` | 9.54 × 10⁻⁶ |
| Round 13 B-04 stage C — per-page restarts | 3,548,160 | **1** `{0}` † | 9.54 × 10⁻⁷ |
| Round 13 B-04 stage D — escalation | 300 | inherits its rows' offsets | — |
| Round 13 B-05 — payload as PRF seed | 70,680 | **14** `{0,1,2,3,5,8,13,29,64,128,256,512,1024,3301}` | 1.34 × 10⁻⁵ |
| Round 16 KDF — key stretching | 692,064 | **1** `{0}` | 9.54 × 10⁻⁷ |
| Round 16 PRNG — 7 census generators | 52,556 | **1** `{0}` | 9.54 × 10⁻⁷ |
| **Round 18 L6 A1 — dense re-sweep, 220 mined configs** | 230,686,720 offsets | **1,048,576** — every offset | **1.000** (per config) |
| Round 18 L6 A2 — fresh 504-seed × 6-gen grid, 508/3,024 units | 266,338,304 offsets | 262,144 — every offset in [0, 2¹⁸) | 0.250 (per config run) |
| — *external-pad branch* — | | | |
| Round 12 A1 — CicadaOS author pads (original) | — | **8** (a ladder) | 6.7 × 10⁻⁸ ‡ |
| Round 12 A1 — `560.13` completion | — | extended ladder "to 5 × 10⁷" — still a ladder | — |
| Round 17 P0–P3 — the public-pad round | 14,522,916,046 offsets | **every offset on every pad** | 1.000 (per pad) |
| Round 18 L6 B — Marsaglia, 77/756 units | 1,539,996,304 offsets | every offset on the units run | 0.0873 of the pad space |

† Stage C varies where the **ciphertext** starts (55 page segments), not where the key starts.
The key restarts at index 0 for every segment. It is not offset coverage.
‡ Against the 118,818,811-byte `560.13` pad's own offset axis.

### 2.2 The aggregate — what B-02 actually costs

| statement | value |
|---|---|
| total published decodes in the derived/seeded branch | **2,531,663,008** |
| …run at key offset 0 **only** | **2,530,301,788** |
| …run at **any nonzero** key offset | **1,355,871** |
| fraction of derived decodes ever run off offset 0 | **0.054 %** |
| distinct key offsets ever tested before Round 18 | **16** |
| largest key offset ever tested before Round 18 | **3,301** |
| fraction of the 2²⁰ axis those 16 points cover | **1.53 × 10⁻⁵** |
| fraction of a 2³² axis | 3.7 × 10⁻⁹ |
| joint (config × offset) space at the 2²⁰ axis | 2.65 × 10¹⁵ |
| …covered before Round 18 | 2.53 × 10⁹ = **9.5 × 10⁻⁷** |
| …added by Round 18/L6 A1 | 2.31 × 10⁸ = **8.7 × 10⁻⁸** |

**How to read this, honestly, in both directions.**

- *Against the repo's published coverage:* an author who started the keystream anywhere other
  than index 0 defeats 99.95 % of every derived-key decode this project has run. B-04's
  Stage B — ten points, the largest 3,301 — is the entire offset coverage of the branch, and
  `handoff/PARKED.md` P-10's "×8,192 for a modest range" understates the axis by 128×.
- *Against panic:* offset 0 is **not** one point among 2²⁰ equally likely ones. Generating a
  pad and using it from its first byte is the modal behaviour of the modal script, so the
  offset-0 slice carries far more prior mass than 1/2²⁰. The correct statement is conditional:
  **conditional on offset = 0 the published coverage stands as written; conditional on
  offset ∈ (0, 2²⁰] the pre-Round-18 coverage is 15 points out of 1,048,575.**
- *And against volume-thinking:* L6's A1 makes the axis **complete out to 2²⁰ for the 220
  highest-prior configs** while adding under 10⁻⁷ of the joint volume. Under a non-flat prior
  over configs, completeness along an axis for the top configs is worth more than its share of
  the volume. This is doctrine R4 in arithmetic: prior beats volume.
- **The offset axis is *not* the residual gap in the external-pad branch.** Round 17 made it
  dense. That branch's residual gap is which pads, which builders, and — §4 — which register.

**B-02 / B-08 status after this lane:** still **open**, now with numbers. What is covered is
tabulated above; what is not covered is everything outside it, and the reopening conditions are
L6 PREREG §7 plus §7 below.

---

## 3. The Marsaglia data gate — PASS, recomputed independently

Round 12 was burned twice by files that were not what they claimed: `_560.00` arrived as a
silent 60.4 % prefix, and `DATA/560.13` arrived as a 134-byte Git-LFS pointer.
`handoff/capsule/verify_capsule.py` exists because of that, and reports DRIFT separately from
ABSENT. L6 wrote its own `data/MANIFEST.json` claiming 110/110 — but that manifest was written
by the process that fetched the bytes, so it is not independent evidence about them.

[`scripts/verify_marsaglia_independent.py`](scripts/verify_marsaglia_independent.py)
**does not read that manifest.** It recomputes from disk and compares against the two
*published* sources.

| gate | object | compared against | verdict |
|---|---|---|---|
| 0 | `checksums.sha256.txt` (11,247 B) | archive.org item metadata: md5 `cc8cf878…`, sha1 `9b3b921a…`, size | **PASS** |
| 1 | `MARSAGLIA_CDROM.iso` (634,124,288 B) | archive.org item metadata: md5 `f127d50c2bd80e7c23f28184423a2d94`, sha1 `ca116df4940eb4b7538942ea6fbe454556b1bac2`, size | **PASS** |
| 2 | all 110 inner files | each file's own published SHA-256 line | **110 / 110 PASS** |

**Totals: 112 PASS · 0 DRIFT · 0 ABSENT.** Wall 134 s. Recorded sha256 of the ISO (archive.org
publishes only md5/sha1/crc32 for it, so this is recorded, not compared):
`6d124080f942a88afade2d6cd2da4b9f092e0e376ee5a9d4af9f7224523f9d28`.

**63 of the 110 inner files are 10,000,000-byte random-data pads** — `BITS.01`–`BITS.60`,
`CALIF.BIT`, `CANADA.BIT`, `GERMANY.BIT` = **630,000,000 bytes** of hash-verified published
physical randomness, dated 1995-12-09 (`BITS.31`: 1996-01-30). Per-file table:
[`out_verify.json`](out_verify.json). The 1.2 GB itself stays gitignored — hashes are the
record, not the bytes.

**No pad that is not PASS was swept.** There are none.

---

## 4. THE MEASUREMENT — the prefilter's register power, on the real Marsaglia bytes

### 4.1 Why this and not the sweep

`round18/L7-redteam/RESULTS.md` §A.7, on the ≈1.45 × 10¹⁰ offsets Round 17 scored and the
2.3 × 10⁸ Round 18/L6 scored:

> R17's own measured prefilter survival (0.375–0.875, non-monotone in pad size) is a survival
> rate **for English plants only**; no non-English survival rate was ever measured, so R17's
> coverage discount does not apply to a non-English plaintext at all.

L7-A measured the **adjudicator's** register power. Nobody measured the **prefilter's** — and
the prefilter runs first, so a register it discards never reaches the beam and L7-A's numbers
never apply to it. That is the missing half of the pipeline's power envelope, and it costs
about 1 % of the sweep it qualifies.

### 4.2 Design

Paired: the same 30 (pad, true-offset) pairs for every register, so the contrast is not
confounded with pad statistics or offset. For each register, a plaintext of **L = 120** rune
indices is drawn from L7-A's own panel (`a1_scorer_language.build_panels()`, imported), planted
into a **real hash-verified Marsaglia pad** at a uniformly random offset, enciphered with
`skipdecode.encipher_keyskip(supp = 0.83)`, and the whole pad is `dense_scan`-ed
(`plen = 24`, `keep = 1000`, sign −1, builder `mod29`).
**N = 9,999,976 offsets per scan; chance survival = 1000/N = 1.00 × 10⁻⁴.**
Script: [`scripts/prefilter_register_power.py`](scripts/prefilter_register_power.py) →
[`out_prefilter_register_power.json`](out_prefilter_register_power.json). Wall 2,732 s, 6 procs.

**Instrument identity is asserted, not assumed.** `--selftest` proves the scan's trigram half is
bit-identical to `lib_padsweep.dense_scan`: same 50 offsets in the same order,
`max |Δscore| = 0.000e+00`. The three language-agnostic screens are computed from the plaintext
matrix `dense_scan` already materialises, so they are free.

### 4.3 The result

Survival of the **true** offset in the top-1000, n = 30 per register (Wilson 95 % CI on the
trigram column):

| register | **trigram prefilter** (the R17/L6 filter) | 95 % CI | IoC·N | max-unigram | distinct-symbols | **any language-agnostic** |
|---|---:|---|---:|---:|---:|---:|
| `EN_KJV` (in the model's training set — ceiling) | **0.800** | 0.63–0.91 | 0.100 | 0.067 | 0.033 | 0.100 |
| `EN_MODERN` (held out) | **0.767** | 0.59–0.88 | 0.000 | 0.000 | 0.000 | 0.000 |
| **`LP1_REAL`** (the register the book actually uses) | **0.767** | 0.59–0.88 | 0.000 | 0.000 | 0.067 | 0.067 |
| `LATIN` | **0.700** | 0.52–0.83 | 0.067 | 0.000 | 0.067 | 0.100 |
| `DE` | **0.633** | 0.46–0.78 | 0.000 | 0.000 | 0.000 | 0.000 |
| `OE` | **0.600** | 0.42–0.75 | 0.000 | 0.000 | 0.000 | 0.000 |
| `CY` (Welsh) | **0.300** | 0.17–0.48 | 0.000 | 0.033 | 0.067 | 0.100 |
| **`EN_HALFVOWEL`** | **0.067** | 0.02–0.21 | 0.000 | 0.000 | 0.000 | 0.000 |
| **`EN_NOVOWEL`** | **0.000** (0/30) | 0.00–0.11 | **0.100** | 0.000 | **0.133** | **0.133** |
| `RAND` (uniform runes — floor) | **0.000** (0/30) | 0.00–0.11 | 0.000 | 0.000 | 0.000 | 0.000 |

**Panel controls, both pre-registered, both hold:** `EN_KJV` is the highest (0.800) and `RAND`
is joint-lowest (0.000). The English arm reproduces L6 Control A's 0.650 within the
pre-registered window [0.47, 0.81]. **Verdict: FOUND-GAP** — pre-registered as
"some non-English register ≤ 0.20 while an English arm ≥ 0.50"; `EN_HALFVOWEL` 0.067 and
`EN_NOVOWEL` 0.000 against `EN_KJV` 0.800.

### 4.4 What it means — the first end-to-end power envelope for a pad sweep in this repo

Composite pipeline power = **prefilter survival × adjudicator power**, the second factor from
L7-A's measured table at L = 120:

| register | prefilter (C2, measured here) | adjudicator (L7-A) | **composite** | relative to English |
|---|---:|---:|---:|---:|
| `LP1_REAL` / `EN_MODERN` | 0.767 | 1.00 | **0.77** | 1.00 |
| `LATIN` | 0.700 | 0.33 | **0.23** | 0.30 |
| `DE` | 0.633 | 0.42–0.83 | 0.27–0.53 | 0.35–0.69 |
| `OE` | 0.600 | 0.42–0.83 | 0.25–0.50 | 0.33–0.65 |
| `CY` | 0.300 | 0.00 | **0.00** | 0 |
| `EN_HALFVOWEL` | 0.067 | 0.33 | **0.022** | **1/35** |
| `EN_NOVOWEL` | 0.000 | 0.00 | **0.00** | 0 |

Applied to the published offset counts (doctrine R2 — coverage × power, never coverage alone):

| sweep | offsets scored | effective for LP1-register / English | for Latin | for vowel-dropped English |
|---|---:|---:|---:|---:|
| Round 17 P0–P3 | 14,522,916,046 | ≈ 1.11 × 10¹⁰ | ≈ 3.4 × 10⁹ | **0** |
| Round 18 L6 A1 | 230,686,720 | ≈ 1.8 × 10⁸ | ≈ 5.3 × 10⁷ | **0** |
| Round 18 L6 B (77/756 units) | 1,539,996,304 | ≈ 1.2 × 10⁹ | ≈ 3.6 × 10⁸ | **0** |

*Caveat, stated rather than buried:* the survival factors were measured on Marsaglia `mod29`
pads with L = 120 plants. R17's pads and builders differ, and R17's own English survival ranged
0.375–0.875 non-monotonically. The **ratios between registers** are the transferable quantity;
the absolute effective counts above are order-of-magnitude.

Two consequences worth stating plainly:

- **`EN_HALFVOWEL` is the new worst case, and it was not visible before.** L7-A had it at
  adjudicator power 0.33 — recoverable. With the prefilter's 0.067 in front of it, the pipeline
  composite is **0.022**: an abbreviated-English plaintext is ~35× less findable than English,
  and 97.8 % of that loss happens *before the beam ever runs*.
- **Welsh flips the diagnosis.** L7-A's adjudicator power for `CY` is 0.00, so its offsets never
  mattered — but the prefilter still passes 0.300 of them. The `CY` failure is purely an
  adjudicator failure, which means **I2 alone fixes Welsh, while `EN_HALFVOWEL` needs I2 *and*
  a prefilter change.** That is an actionable split Phase 0 did not have.

### 4.5 The free recovery — language-agnostic screens

In `EN_NOVOWEL`, where the trigram prefilter retains **0/30**, the IoC screen retains **3/30**
and the distinct-symbols screen **4/30**; their union is **0.133**, i.e. **1,300 × the chance
rate of 1.0 × 10⁻⁴**. In `LATIN`, `CY` and `EN_KJV` the union adds 0.033–0.100 on top of the
trigram survivors.

These screens are weak — a 24-rune window is too short for IoC to separate much — and on six of
ten registers they contribute nothing. But they are **free** (they fall out of the plaintext
matrix `dense_scan` already builds), they are **the four statistics doctrine R3 makes
mandatory**, and they are non-zero **exactly in the register where the English filter is
totally blind**. Recommendation to **I2/S1**: keep the union of `top-K(trigram)` and
`top-K(IoC)` and `top-K(distinct)`, and persist all four statistics per retained offset. Cost:
one bincount per chunk. Numbers: [`out_prefilter_union.json`](out_prefilter_union.json).

---

## 5. The sweeps: what exists, and what is held

### 5.1 Sub-lane A1 — COMPLETE — NEGATIVE for an English-register plaintext

The first dense offset coverage the derived/seeded branch has ever had. 220 configs mined from
`round13/B04/results_{A,B,C}.json` + `round16/KDF/results_A.json` + `round16/prng/results.json`
(no prior sweep re-run), keystreams rebuilt with each originating lane's own code, `dense_scan`
over **every** offset in [0, 2²⁰).

| | |
|---|---|
| units | **220 / 220 complete** |
| offsets | **230,686,720** |
| best | **−6.8093** — `pbkdf2_sha1_10000 \| rej29`, seed `thematic`, sign −1, **offset 45,081** |
| bar | `threshold_for(230,686,720)` = **−5.5000** (floor binds) |
| per-unit best distribution | max −6.809, mean −6.982, sd 0.075, min −7.501 (n = 220) |
| hits | **0** |

The campaign maximum is 2.3 sd above the mean of 220 per-unit maxima — where a best-of-N order
statistic belongs — and 1.31 below the bar. It is also below B-04's own Stage-A p99.999 of
−6.35. The L6 continuation's measured shuffle null (`out/nulls.json`, n = 200, ms = 8) puts
`null_max` at **−6.9847** at L = 400 and −6.5846 at L = 120, so the `null_max + 0.5` half of the
L6 §4 bar is −6.48/−6.08 and the `threshold_for` floor of −5.5 binds either way.

**Sub-lane A as a whole**, with A2's partial units folded in (L6 `RESULTS.md` §0): 497,025,024
offsets, best **−6.7702**, bar `threshold_for(497,025,024)` = **−5.4664**, distance below the
binding bar **1.304**. A1's own best (−6.8093) is *lower* than A2's because A2 covers many more
configs; both are ≈ 1.3 below their bar. A useful caution from the same file: these scores are
adjudicated on a **400-rune** window while B-04 / R16's published maxima (−6.185, −6.259, −6.347)
were best-of-N on a **120**-rune window, and the measured null is lower at L = 400. **The two
sets of numbers are not comparable**, and `threshold_for`'s Gumbel constants are calibrated at
L ≈ 120 while the function ignores its `segment_len` argument — a bias that makes the bar used
here conservative, never loose. That is Round 19 **I3**'s problem, and it is now measured.

**Positive control (L6 Control A, `out/control_offset.json`):** 8 real mined configs, real
dictionary seeds, Cicada-register English planted at a random offset in [1000, 2²⁰),
**recovery 40/40 = 1.000** (gate ≥ 0.95) → PASS. Dense-prefilter **survival 0.650**, reported as
this sub-lane's coverage discount. No ×0.625 constant was used anywhere.

### 5.2 Sub-lane B (Marsaglia) and sub-lane A2 — HELD

| | sub-lane B (Marsaglia) | sub-lane A2 |
|---|---|---|
| planned | 756 units = **17,639,963,712** offsets on the 63 pads (+ 17,755,479,488 for the whole ISO as one pad) | 3,024 units ≈ 1.59 × 10⁹ offsets |
| done at C2 collection | **77 / 756 (10.2 %)** = 1,539,996,304 offsets — `mod29` **forward complete on all 63 pads**, `mod29` reversed on 14 | 508 / 3,024 (16.8 %) = 266,338,304 offsets |
| best | **−6.7387** `BITS.22` / `mod29` / fwd / sign +1 / offset 7,710,875 | −6.7702, `sha256_chain\|mod29`, seed `slogan`, offset 253,446 |
| bar | `threshold_for(1,539,996,304)` = **−5.3844** (stricter than −5.5) | `threshold_for(266,338,304)` = −5.5000 |
| hits | **0** | **0** |
| tier-2 escalation | not triggered — nothing reached the −6.00 gate | not triggered |

**Positive control (L6 Control B, `out/control_marsaglia.json`)** — planted in the **real
hash-verified CDROM bytes**: **recovery 16/16 at ms = 8** → PASS; survival 9/16 = 0.563. The
ms = 3 diagnostic also recovered 16/16, so **R17/P1's constant-run defect does not bite on
Marsaglia**: the 10 MB random-data files are 0.36–0.48 % zero bytes with a longest constant run
of 3–4 bytes in 10 MB. The ISO does carry filesystem padding (longest constant run 32,768 in its
first 16 MiB), which is why the whole-ISO view is a separate set of units.

**One flagged row, reported because R3 exists to preserve exactly this.** The L6 continuation's
`out/langagnostic.json` re-scored the top-20 survivors of each stage against 8 register LMs and
three language-free statistics and found **one** (statistic, survivor) pair outside its matched
null band: the sub-lane B best row (`BITS.22`, offset 7,710,875) at **IoC·N = 1.0873** against a
null of 1.0082 ± 0.0197, i.e. **+4.0 sd**. Its English score is −6.7387 — noise — and its
register-LM scores are all inside the band. Across ~220 (statistic, survivor) comparisons a
+4.0 sd one-sided event has family-wise p ≈ 0.7 % *if* the null band were exact, and at n = 60
it is not. Recorded as **INSPECT**, not as a signal. It is named here so that it is not
rediscovered as a surprise.

### 5.3 The cost of finishing — measured, not estimated

[`out_marsaglia_space.json`](out_marsaglia_space.json), from realised checkpoint throughput:

| | |
|---|---|
| offsets, 63 verified pads × 6 builders × 2 byte-orders × 2 signs | **17,639,963,712** |
| offsets, whole ISO as one pad | 17,755,479,488 |
| units (pads only) | 756 |
| observed | 33.9 s wall/unit at nproc = 3 → **≈ 100 CPU-s per unit** |
| **cost to finish the 63 pads** | **≈ 21 CPU-hours** |
| cost including the whole-ISO view | ≈ 43 CPU-hours |

The Marsaglia pads alone are **1.21 ×** the entire Round 17 public-pad round. C2's PREREG §2
guessed ~10 CPU-hours before measuring; the measurement says 21, and the measurement is what is
reported.

Resumable, never recomputes a finished unit:

```bash
cd liber-primus/analysis/round18/L6-offset-marsaglia/scripts
python3 sweep_marsaglia.py --nproc 6 --budget <seconds>    # checkpoints in out/ckpt_M
python3 sweep_offset.py --stage A2 --nproc 6 --budget <seconds>
```

### 5.4 The decision, restated against the measurement

PREREG §2 held the remainder on the *inference* that a Marsaglia sweep through the unrepaired
instrument would be an English-only negative. §4 replaces the inference with a measurement, and
the measurement is worse than the inference:

- For a **vowel-dropped-English** plaintext the remaining 15.5 × 10⁹ offsets have composite power
  **0.000 × 0.00**. Doctrine R2: 1.55 × 10¹⁰ × 0 = **0**.
- For **half-vowel English**, composite 0.022 — the 21 CPU-hours would buy the equivalent of
  3.4 × 10⁸ effective offsets, ~2 % of their face value.
- The harness stores `(offset, sign, pre, score, head)` — `(parameters, English score, 64-char
  head)`, the exact shape that made 10¹⁰ decodes permanently un-reinterpretable (doctrine R3,
  Round 10b's 0/15 compliance). **Running it now does not reduce Phase 2's work; it duplicates
  it.** Every offset scored today must be scored again by `S1` under I2's `SWEEPROW`.
- **I1** is still pending: the beam's transition relation is exact for `encipher_keyskip` and
  misses `skip_by_two` at −6.90 / 25.8 % recovery (L7-B).

So the hold stands, and the release condition is concrete and near: **I1 and I2 PASS**, then
`S1` runs the 679 remaining units under `SWEEPROW` with the union prefilter of §4.5. That is
21 CPU-hours of *re-adjudicable* coverage instead of 21 CPU-hours of a fourth English null.

---

## 6. The three conditionals — on every negative in §5

Doctrine R2 / Aiming-Test Q4. A negative missing one of these is not a result.

1. **Key space.**
   *A1:* the 220 mined configs, dense over [0, 2²⁰). Not: seeds outside B-04's dictionary,
   generators outside the swept 16 + 27 + 7, offsets > 2²⁰, reductions outside each row's own,
   non-integer or per-line offset schedules, filters other than supp = 0.83.
   *B:* Marsaglia bytes only; `mod29` forward on 63/63 pads and reversed on 14/63; the other
   five builders (`hi_nibble`, `lo_nibble`, `byte_scaled`, `prime_to_idx`, `nibbles`) **not yet
   run on any pad**; the whole-ISO view **not run**; `hexchars` excluded by L6 §2.1 and named
   here rather than left silent.
2. **Decoder transition model.** `skipdecode.beam_decode`. Its transition relation admits a key
   skip only if every skipped position would have reproduced the previous cipher rune — exact
   for `encipher_keyskip` and **nothing else**. L7-B: `skip_by_two`, a one-character change to a
   plausible 2013 rejection loop that reproduces LP2's observed doublet rate, scores the
   **correct** key at −6.90 with 25.8 % recovery, and beam width 1000 / `max_skip` 8 change that
   by exactly 0.000. Round 19 **I1** is the fix.
3. **Adjudicator register.** English, **twice**, and now with both factors measured:
   prefilter survival (§4.3) × adjudicator power (L7-A) = composite (§4.4). For the register the
   Liber Primus demonstrably uses, 0.77. For Latin, 0.23. For Welsh and vowel-dropped English,
   **0.00** — these negatives say nothing at all about those registers. Round 19 **I2** is the
   fix for the adjudicator half; §4.5 is a measured, free start on the prefilter half.

---

## 7. Bounds, and what reopens each item

Doctrine R7. No verdicts here; the words "exhausted", "closed" and "unsolvable" appear nowhere
above as conclusions.

- **B-02 / B-08** — remains **open**, now quantified. Reopens/extends on: any derived-key sweep
  proposing seeds or generators outside the swept sets *together with* an offset axis; offsets
  beyond 2²⁰, for which the only new argument needed is a mechanism producing a pad file larger
  than 1 MB; and non-integer, per-line or per-page offset schedules, which nothing has tested.
  The dense axis out to 2²⁰ must **not** be re-run for L6's 220 configs.
- **Marsaglia** — **verified, quantified, costed, 10.2 % swept, live.** Reopens by simply being
  finished: 679 units, ≈ 21 CPU-hours, resumable, and it should be finished under I2's
  `SWEEPROW`, not before.
- **Sub-lane A2** — 508/3,024 units, live, held on the same condition.
- **The §4 panel** — one builder (`mod29`), one pad family, one plaintext length (L = 120), one
  filter (supp = 0.83), n = 30. It **bounds** the prefilter; it does not characterise it.
  Reopens for other builders, other pads, other lengths, and for I1's repaired decoder. The
  cheapest extension is L = 400, where the trigram window is unchanged but the survival
  competition is identical — it would cost the same 45 minutes.
- **The one INSPECT row** (§5.2) reopens if `BITS.22` offset 7,710,875 clears its own bar under
  I1 + I2, or if the language-agnostic null band is re-derived at n ≫ 60 and the +4.0 sd holds.

---

## 8. Reproduce

```bash
cd /path/to/cicada3301
python3 liber-primus/tests/validate.py                                     # 5/5
python3 -m pytest liber-primus/benchmark/ -q                               # 8 gates

python3 liber-primus/analysis/round19/C2/scripts/verify_marsaglia_independent.py
python3 liber-primus/analysis/round19/C2/scripts/offset_coverage.py
python3 liber-primus/analysis/round19/C2/scripts/marsaglia_space.py
python3 liber-primus/analysis/round19/C2/scripts/prefilter_register_power.py --selftest
python3 liber-primus/analysis/round19/C2/scripts/prefilter_register_power.py --nproc 6
```

Outputs: [`out_verify.json`](out_verify.json), [`out_offset_coverage.json`](out_offset_coverage.json),
[`out_marsaglia_space.json`](out_marsaglia_space.json),
[`out_prefilter_register_power.json`](out_prefilter_register_power.json),
[`out_prefilter_union.json`](out_prefilter_union.json), [`ledger.json`](ledger.json).
The 1.2 GB of Marsaglia bytes stays gitignored; §3's hashes are the record.

## 9. Handoff — the three things Round 19 should take from C2

1. **I2/I3:** the composite power table (§4.4) is the first end-to-end power envelope for a pad
   sweep in this repository. Use it to set the recalibration target, and note the split: Welsh
   needs only the adjudicator; half-vowel English needs the **prefilter** too.
2. **S1:** the union prefilter of §4.5 costs one `np.bincount` per chunk and recovers survival in
   the register where the English filter is at 0.000. Persist all four statistics per retained
   offset — that is doctrine R3, and it is what makes 21 CPU-hours of Marsaglia worth spending
   once rather than twice.
3. **The coordinator:** `LEDGER.json`'s **B-02** entry currently has every field except
   `hypothesis` set to `null`. [`ledger.json`](ledger.json) here fills `coverage`,
   `not_covered` and `reopens_if` for it, and adds entries for L6's two sub-lanes and this
   lane's measurement. `README.md`, `ELIMINATION-LEDGER.md`, `analysis/README.md` and
   `PICKUP-HERE.md` are outside C2's write scope and still need this round's line.
