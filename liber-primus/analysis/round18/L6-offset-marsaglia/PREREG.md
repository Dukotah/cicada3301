# Round 18 / L6 — OFFSET & MARSAGLIA — PRE-REGISTRATION

_Written 2026-08-25 **before any scoring code ran**. Nothing below is edited after seeing a
score; corrections, if any, are appended as dated addenda at the bottom with the reason._

Trust anchor to be recorded in `RESULTS.md`: `python3 liber-primus/tests/validate.py`
(ALL VALIDATIONS PASSED) and `python3 -m pytest liber-primus/benchmark/ -q`.

Data acquisition (the 634 MB archive.org download of sub-lane B's pad) was started before this
file was finished. **No offset was scored before this file was complete.** Acquisition is not a
test; the hash verification in §B.2 is a gate that runs after this file, not before it.

---

## 0. The two gaps, and why they are live

**B-02 / B-08 — OFFSET ≠ 0.** `research/ROUND-8-RESULTS.md` states that its sweep *"assumes key
index 0 aligns with the first rune of LP2 page 0"*. That assumption multiplies every derived-key
sweep this project has run:

| sweep | decodes | offset coverage |
|---|---|---|
| Round 8 seeded-PRNG | 2.52 × 10⁹ | **offset 0 only** |
| Round 13 B-04 stage A | 1,385,600 | **offset 0 only** |
| Round 13 B-04 stage B | 1,290,240 | 10 offsets: {1,4,16,29,64,128,256,512,1024,3301} |
| Round 13 B-04 stage C | 3,548,160 | 55 per-page restarts, all keyed from index 0 |
| Round 16 KDF | 692,064 | **offset 0 only** (`KDF/PREREG.md`: "Offset 0 only (Stage A)") |
| Round 16 PRNG family | 52,556 | **offset 0 only** |

`handoff/PARKED.md` P-10 scores this at **×8,192 for a modest range, and notes it multiplies
every generator**. B-04's own PREREG §6 declares "offsets beyond 3301" explicitly **not covered**.

Round 17 fixed exactly this defect for the *external-pad* branch — `round17/lib_padsweep.py`
replaced A1's eight-offset ladder with a dense scan that scores **every** offset — and the
**derived/seeded** branch never received the same treatment. This lane applies the Round-17
instrument to the Round-13/16 generators.

**Marsaglia.** `round17/SYNTHESIS.md` names the **Marsaglia Random Number CDROM (1995)** as the
single live, reachable, unswept public-pad item — *"the cheapest live item in this branch"* —
634,124,288 bytes of published physical randomness with published SHA-256s, dated 1995, exactly
the kind of object a 2012–14 author with a cryptography habit would have known about. Found by
lane P2, deliberately left alone, **never fed to the decoder**.

---

## 1. Hypotheses

- **H-A1.** A generator/seed already at the top of B-04 / R16-KDF / R16-PRNG produces the LP2
  keystream, but starting at some key index *o* > 0 that those sweeps never scored.
- **H-A2.** A seed in B-04's 504-entry core dictionary, under one of the six highest-prior
  keystream constructions, produces the LP2 keystream at some key index *o* > 0.
- **H-B.** The LP2 keystream is a window of the published Marsaglia CDROM bytes, under one of
  Round 17's byte→Z₂₉ reductions, in either byte order, at some offset.

Each is tested by the same adjudication: does any decode clear the pre-registered bar in §4?

---

## 2. Instrument

`analysis/round17/lib_padsweep.py`, unmodified, imported (not copied):

- `dense_scan(K, C, sign)` — scores **every** key offset by rigid-reading a 24-rune head window
  under a trigram model trained on **rune indices** (AGENTS.md §4 lesson 4), returns the best
  `keep` offsets.
- `beam_decode` from `analysis/campaign18_skip/skipdecode.py` — the skip-aware beam. Rigid
  decoding is **never** used for adjudication (AGENTS.md §4 lesson 2).
- `benchmark/null.py: threshold_for(n_trials, segment_len)` — the scale-corrected bar. The
  habitual fixed −5.5 is **not** the bar for this lane; it is the floor inside `threshold_for`.

### 2.1 Instrument defects inherited from Round 17, and what this lane does about them

| defect | Round 17's finding | this lane |
|---|---|---|
| `max_skip=3` underpowered on pads with constant byte runs | P1's control **failed on its real pad**, 6/8; at ms=8, 60/60 | **ms = 8 everywhere.** Both controls are run on the **real** pad/keystream family, not a synthetic one, and the sub-lane B control is run at ms=3 **and** ms=8 so the effect is measured on Marsaglia rather than assumed |
| `ks_hexchars` silently drops digits 0–9 (`eng_to_idx` discards non-letters) — it sweeps the A–F subsequence | found by P1 after it had already been used on the highest-prior variants | **Audited by assertion before use** (`audit_builders.py`): every text→keystream converter is checked for length conservation. `hexchars` is **excluded**; `ks_nibbles` (the true hex reading) is used in its place, and the exclusion is recorded, not silent |
| ×0.625 prefilter-survival discount treated as a constant | measured 0.375–0.875 across pads, **non-monotone** in size | **No constant is used.** Survival is measured per sub-lane by this lane's own control and reported as that sub-lane's coverage discount |

### 2.2 Beam settings

Tier 1 (screening escalation): `head=400`, `beam_w=120`, `max_skip=8`, both signs.
Tier 2 (adjudication): anything scoring ≥ **−6.00** at tier 1 is re-decoded at `beam_w=400`,
`max_skip=8` on (a) the 400-rune head, (b) full page 0 (262 runes), (c) the full 12,956-rune
stream. A correct key **improves** with more text; a lucky one decays. Both directions are
recorded. Round 13 Stage D is the precedent and its logic is adopted unchanged.

---

## 3. Sub-lane A — OFFSET

### A.1 The offset range, and the argument for its bound

This is not "as far as we could afford". The bound is chosen to be past the largest artifact any
named mechanism could produce.

| mechanism that puts key index 0 somewhere other than LP2 rune 0 | offset it implies |
|---|---|
| **The author enciphered the earlier Liber Primus pages first.** This repo's own `SOLVED-PAGES.json` holds 1,796 solved runes (184+157+742+394+319); the full circulating book is ≈14.7 k runes | 1,796 … ≈14,752 |
| **A file header or fixed skip** — the author generated a pad file and skipped a header, or the script wrote a preamble | 512, 1024, 4096, 8192, 65,536 |
| **Hash/cipher block alignment** — 16/20/32/64/128-byte digests × a round count | any multiple of 16…128 |
| **Page/section restarts and lore constants** — the 57 cumulative segment starts (max 12,956), 3301 and its multiples | ≤ 12,956; 3301·k |
| **A generated pad file consumed from the middle** — the modal artifact of a "make me a one-time pad" script is a 1 MB file | ≤ 1,048,576 |

**OFF_MAX = 2²⁰ = 1,048,576, scanned DENSELY (every integer offset).** That subsumes every row
above by construction — it is 71× the entire Liber Primus and the full length of a 1 MB pad file.
Coverage relative to the offset-0 assumption: **×1,048,576**, against PARKED P-10's "×8,192 for a
modest range".

For the fresh grid (A.3), where the config count is ~6,000× larger, **OFF_MAX = 2¹⁸ = 262,144**,
which still subsumes rows 1–4 and 17.8× the whole book.

### A.2 Stage A1 — dense offset re-sweep of the mined survivors

Configs are **mined from existing results JSON; no prior sweep is re-run** (Round 18 rule 7):

- `round13/B04/results_{A,B,C}.json` → `top50` of each (150 rows)
- `round16/KDF/results_A.json` → `top50`
- `round16/prng/results.json` → `top20`

deduplicated on the full config tuple. Each config's keystream is rebuilt with the **original
lane's own code** (`round13/B04/ks.py`, the KDF lane's KDF list, `round16/prng/prng_sweep.py`),
extended to `OFF_MAX + 400·9 + 8` symbols, and `dense_scan`'d over every offset in [0, 2²⁰).
`keep = 1000`; the top **200** dense survivors per (config, sign) go to tier-1 beam.

> **Declared in advance:** for a config whose original row has `dir=rev`, reversing a *longer*
> generated stream is a **different keystream** from the one the original lane scored. Those rows
> are therefore reported as **new coverage of the "author generated an L-byte pad file and read
> it backwards" hypothesis at L = OFF_MAX + slack**, not as an extension of the original row.

### A.3 Stage A2 — fresh seed × offset grid on the highest-prior constructions

- **Seeds:** B-04's 504-entry `core` set (`seeds.py: core()` — slogan, thematic, solvedkey, num_*,
  primes_*, anend_*, canon256_*, pgp, onion).
- **Generators (6, the highest-prior):** `sha256_ctr`, `sha512_ctr`, `sha1_ctr`, `md5_ctr`,
  `sha256_chain`, `hmac_sha256_ctr`. Rationale: bare-hash counter/chain expansion of a memorable
  secret is the modal shape of a 2013 "make me a pad" script, and these six carry B-04's own
  top-of-distribution rows.
- **Reduction:** `mod29` (the modal reduction, and the one B-04's best rows used).
- **Signs:** both. **Direction:** `fwd` (the `rev` hypothesis is covered by A.2, where it is
  length-meaningful).
- **Offsets:** dense over [0, 2¹⁸).
- Tier-1 beam on the top **40** dense survivors per (seed, gen, sign).

Planned scale: 504 × 6 × 2 = 6,048 dense scans × 262,144 ≈ **1.585 × 10⁹ offsets**.

### A.4 Sub-lane A positive control — MANDATORY, on the real keystream family

`control_offset.py`: for each of **≥8 distinct real mined configs** (real dictionary seed, real
generator, real reduction — not a synthetic hash chain), plant Cicada-register English,
encipher it with `skipdecode.encipher_keyskip` under the anti-repeat filter at supp = 0.83 at a
uniformly random true offset in [1000, OFF_MAX), and push it through the **identical**
`dense_scan → tier-1 beam` pipeline at ms = 8.

- **n = 40 trials.**
- Recorded: `survival` = fraction of trials whose true offset is inside the `keep` window;
  `recovery` = fraction of trials where the beam at the true offset matches > 95 % of **rune
  indices**.
- **Gate: `recovery` must be ≥ 0.95 (38/40) for this sub-lane's null to be reported as a
  negative.** If it is not, the sub-lane reports **INCONCLUSIVE**, never NEGATIVE.
- `survival` is *not* a gate; it is this sub-lane's honest coverage discount, reported as a
  measured number with no ×0.625 constant anywhere.

---

## 4. The bar — fixed now

For each sub-lane, with `N` = the total number of offsets that sub-lane dense-scanned:

```
HIT  iff  score_norm  >=  max( threshold_for(N, segment_len=400),  null_max + 0.5 )
```

- `threshold_for` is `benchmark/null.py`'s scale-corrected family-wise bar at α = 0.01. It
  already carries the historical −5.5 as a floor, so this bar can only ever be **stricter** than
  the habitual −5.5, never looser. Its value at each sub-lane's true N is reported in `RESULTS.md`
  alongside the best score.
- `null_max` is this lane's **own** shuffle null — histogram-preserving, order-destroying,
  n = 200, measured **at ms = 8 on the same keystream family and the same 400-rune window**,
  because a larger skip budget gives the beam more freedom and raises the null.
- Anything crossing the bar must then survive tier 2 (§2.2) on full page 0 **and** the full
  12,956-rune stream, and must improve rather than decay. Anything crossing the bar and failing
  tier 2 is logged as an expected null event and named as such.

**Pre-registered prediction (so this lane can be wrong in public):** given B-04's measured Stage-A
null (mean −7.344, sd 0.231, p99.999 −6.35) and the Gumbel fit in `benchmark/null.py`
(μ = −7.2517, β = 0.0725), a **null** sub-lane A at N ≈ 1.8 × 10⁹ should return a best score near
**−7.2517 + 0.0725·(ln N + γ) ≈ −5.86**, and sub-lane B at N ≈ 1.8 × 10¹⁰ near **−5.69**. A best
score materially above those, at a score that also improves on longer text, is the interesting
outcome. A best score at or below them is the null behaving exactly as expected.

---

## 5. Sub-lane B — THE MARSAGLIA RANDOM NUMBER CDROM (1995)

### B.1 The object

archive.org item **`marsaglia-cdrom`** (creator: George Marsaglia), file
`MARSAGLIA_CDROM.iso`, **634,124,288 bytes**, plus the item's own
`checksums.sha256.txt` (11,247 B) — the CDROM's published per-file SHA-256 manifest, 110 files.

### B.2 Verification gate — nothing is swept before this passes

This repository has been burned twice by a mirror serving different bytes: `_560.00` arrived as a
silent **60.4 % prefix**, and `DATA/560.13` arrived as a 134-byte Git-LFS pointer. Therefore:

1. The downloaded ISO's **md5, sha1 and sha256** are computed and recorded.
2. md5 and sha1 must equal archive.org's published item metadata
   (`md5 f127d50c2bd80e7c23f28184423a2d94`, `sha1 ca116df4940eb4b7538942ea6fbe454556b1bac2`),
   and the size must be exactly 634,124,288.
3. The inner files are extracted and **each one is verified against its own line in
   `checksums.sha256.txt`**. The pass/fail count is reported.
4. All of the above go into `data/MANIFEST.json` in the shape of
   `handoff/capsule/MANIFEST.json`, and a capsule fragment is written for merge.
5. **A file that fails, or that cannot be verified, is not swept** — it is listed in
   `not_covered` by name.

### B.3 What is swept

- **Pads:** the whole ISO as one pad, **and** each verified inner random-data file as its own pad
  (the ISO's own filesystem headers and inter-file padding are long constant runs — precisely the
  regime where P1 found ms = 3 fails, so both the whole-ISO and per-file views are taken).
- **Builders (Round 17's set, with the audited substitution):** `mod29`, `hi_nibble`, `lo_nibble`,
  `byte_scaled`, `prime_to_idx`, and `nibbles`. **`hexchars` is excluded by §2.1** and the
  exclusion is stated in the results rather than left silent.
- **Byte order:** forward and reversed, for every builder.
- **Signs:** both.
- **Offsets:** **every** offset, via `dense_scan`, sharded so peak memory stays bounded; shard
  hit-lists are pooled before escalation so sharding does not change which offsets are adjudicated.
- **max_skip = 8**, per §2.1.

### B.4 Sub-lane B positive control — MANDATORY, on the real pad

`control_marsaglia.py`: `lib_padsweep.control()` run with `blob =` the **real, hash-verified
Marsaglia bytes**, at **ms = 3 and ms = 8**, n = 16 trials each.

- **Gate: beam recovery ≥ 0.95 of runes on 16/16 trials at ms = 8**, on the real pad. Below that
  the sub-lane reports **INCONCLUSIVE**.
- The ms = 3 run is diagnostic only: it measures whether the constant-run defect bites on *this*
  pad (P0 found it does not bite on high-entropy ISO-carved blobs; the Marsaglia ISO has both
  high-entropy regions and filesystem padding, so it is measured, not assumed).
- `survival` is reported per pad as the coverage discount. No constant.

### B.5 The residue items Round 17 named, and which of them this lane takes

`round17/SYNTHESIS.md` §"What this round did NOT exclude" names: the Marsaglia CDROM;
non-contiguous blockchain selections; the beacon beyond 2013-11-13; other chains, txids, coinbase
scriptSigs, chainwork; **keystream builders outside the seven tested**; and P3's 13 short pads.

Taken here, because they are cheap and need no new download:

- **R-1. `nibbles` on the Marsaglia pads** — new-coverage builder, folded into §B.3.
- **R-2. The builder-set residue on pads already on disk.** If `round17/P3_tables/data/pads/`
  and/or `P2_beacons/data/` survive in the working tree, the *builders outside the seven tested*
  are swept on those existing, already-hash-verified pads at ms = 8. No fetch, no new pad.
  Declared in advance as **opportunistic**: if the gitignored corpora are absent, this is reported
  as not-covered with the reason, and nothing is re-downloaded to chase it.

Not taken (and named, with the reason): non-contiguous blockchain selections and other chains
(needs a fresh multi-GB fetch — a lane of its own); the beacon past 2013-11-13 (same); P3's short
pads (their bound is a window bound, not an offset bound, so it is not this lane's gap).

---

## 6. What this lane will NOT cover — declared before the run

- Offsets beyond 2²⁰ (A.2) / 2¹⁸ (A.3). A pad file larger than 1 MB consumed past its first
  megabyte is **not** covered.
- **Non-integer, per-line and per-page offset schedules.** Only a single constant offset into one
  keystream is tested.
- Seeds outside B-04's 2,165-entry dictionary and its 504-entry core; generators outside the 16
  in `round13/B04/ks.py`, the 27 KDF configs of R16-KDF and the 7 of R16-PRNG.
- Reductions other than `mod29` in stage A.3.
- Filters other than the pinned soft key-skip at supp = 0.83.
- Composite plaintext transforms.
- The dense prefilter's own blind spot: whatever `1 − survival` measures in §A.4 / §B.4 is a
  **power** limit on offsets, not a soundness claim. It is reported as a number.
- Anything in §B.5 marked "not taken".

## 7. Reopening conditions — stated in advance

- Sub-lane A reopens if a *seed dictionary* wider than B-04's, or a generator outside the swept
  16 + 27 + 7, is proposed **together with** an offset sweep; the offset axis is now dense for the
  configs listed and must not be re-run for them.
- Sub-lane A also reopens for offsets > 2²⁰, for which the only new argument needed is a
  mechanism that generates a pad file larger than 1 MB.
- Sub-lane B reopens if any Marsaglia inner file fails hash verification and a byte-correct copy
  is later obtained, or if a builder outside §B.3 is proposed.
- Either sub-lane reopens on a score at or above its own `null_max + 0.5` that also **improves**
  under tier 2.

## 8. Vocabulary

Per Round 18 rule 6 and AGENTS.md §7, this lane's `RESULTS.md` will report **coverage and bounds**.
The words "exhausted", "closed" and "unsolvable" will not appear as verdicts.
