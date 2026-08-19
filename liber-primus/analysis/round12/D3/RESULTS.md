# FRONT D3 — Red-team: scope-overreach audit

**Verdict: FOUND-ERROR.** A narrow, ciphertext-statistics negative ("the ciphertext is
indistinguishable from an external pad") has been promoted, in the load-bearing top-line
verdict, into an unconditional information-theoretic closure ("information-theoretically
unsolvable / no compute recovers it / unsolvable-by-design"). That promotion foreclosed a
concrete, tractable, **never-run** lane — the SHA/AES/HMAC-counter **derived-key dictionary**
(RECON-A item **B-04/B-05**) — which the repo's own B4/G5 result proves the ciphertext
*cannot* exclude and which is therefore settled ONLY by running the dictionary, not by any
statistics closure.

Trust anchor: `python3 tests/validate.py` = ALL PASS (rig reproduces known solves).

---

## Positive control (mandatory gate) — PASS

`pc_derivedkey.py`. Planted a **SHA-256 counter-mode derived keystream** (seed
`b"CICADA3301"`, the exact B-04/G5 family) over English-in-runes, enciphered under the repo's
**pinned soft anti-repeat filter** (`encipher_keyskip`, supp=0.83). Result reproduces the LP2
anomaly and is recovered through the project's own validated machinery:

| channel | score_norm | note |
|---|---|---|
| English plaintext target (`nc.eng_norm`) | **-4.170** | the English band |
| ciphertext doublet rate | **0.0000** | matches LP2's suppressed-doublet anomaly |
| RIGID decode, correct seed | -6.835 | noise — what every prior seed/keytext test used |
| **BEAM (skip-aware) decode, correct seed** | **-4.170** | recovered; **98.9% char-recovery** |
| BEAM decode, WRONG seed | -7.349 | noise |
| null (shuffled P, N=200, seed 3301) | mean -6.478, **max -6.044** |

Gate: beam recovers the correct short seed, jumps noise (~-7.5) → English (-4.170), beats the
wrong seed by 3.18 and beats null_max by 1.87. **PASS.** This proves the derived-key dictionary
lane is a *real, powered* test — the correct short seed is recoverable by compute — so
"no compute recovers it" is false over this lane.

---

## The three biggest promoted closures (claim vs actual coverage)

### 1. "Information-theoretically unsolvable / no compute recovers it / unsolvable-by-design"
- **Claim** (`ELIMINATION-LEDGER.md:21`, `CAMPAIGN-PLAN.md:12-13`, README/PICKUP-HERE, Round 11
  SYNTHESIS:52): LP2 is a full-length keystream against an EXTERNAL pad ⇒ the plaintext is
  "information-theoretically not present in the ciphertext … no compute recovers it."
- **Actual evidence** (`round10b/B4-otp-steelman/b4_results.json`, G4/G5): the ciphertext is a
  member of an **indistinguishability class**. A SHA-256 counter-mode keystream **derived from a
  short seed** + the same filter is statistically inseparable from a true pad (G5 `separated:false`,
  max |z| = 1.60 across the 6-stat battery). Round 10 SYNTHESIS states this correction verbatim
  ("OTP-*class*, not a unique external pad"). A short-seed-derived keystream lives in a **finite,
  enumerable keyspace — it is NOT information-theoretically closed and IS brute-forceable.**
- **Overreach:** one member (true OTP) of the class is promoted to a property of the whole class.
  The B4 correction lives only in Round 10's SYNTHESIS and PICKUP-HERE; the top-line verdict lines
  in ELIMINATION-LEDGER, CAMPAIGN-PLAN, README, and Round 11 SYNTHESIS still assert the
  unconditional information-theoretic closure.
- **Live lane it hides — B-04/B-05, marked `never-run` in `round10/RECON-A/REGISTER.md:51-52`:**
  cryptographic keystreams (MD5/SHA-1/SHA-256/SHA-512 chain & counter, HMAC-DRBG, AES-CTR, RC4)
  from a Cicada seed dictionary, reduced mod 29, under the filter-aware beam; and pp49-51's
  256-byte payload as a PRF seed. The L5 CENSUS.md (§C) independently marks this "out of scope for
  a seed sweep … a different lane" and Round 8's "2.52e9 decodes" covered **only hobbyist PRNGs**.
  RECON-A explicitly notes the iter-6 MDL "incompressible ⇒ not algorithmically generated" kill has
  **no power** here (hash keystreams are incompressible by construction).
- **Cheapest settling test:** run B-04 = a dictionary of ~10²–10⁴ Cicada strings/constants
  (3301, primes, "DIVINITY"/"CIRCUMFERENCE"/"INSTAR", AN-END hex, canon_256, PGP fingerprint
  7A35090F, onion names) × {SHA-256, SHA-512, HMAC-DRBG, AES-CTR, RC4} counter-mode × ±/atbash ×
  offset, each reduced mod 29 and fed through the **existing** Campaign XVIII skip-aware beam with
  the plant-recover gate this control just passed. Minutes-to-hours of compute; not a revival of a
  dead family (Round 8 swept integer-seeded PRNGs, never keyed hash/stream-cipher keystreams).

### 2. "seeded-PRNG pads … DO NOT re-run" (Round 8 SEED, 2.52e9 decodes, 0 hits)
- **Claim** (`ELIMINATION-LEDGER.md:272-273`): flat "do not re-run — seeded-PRNG pads."
- **Actual coverage** (`round10/L5-seed32/CENSUS.md`): Round 8 covered 10 integer-seeded
  generators over ~3% of each seed space (2 fully). The census itself lists as **UNCOVERED and
  named-plausible:** PHP `mt_rand` (**highest-prior open generator**), .NET `System.Random`, BBS
  as a real seed space, ISAAC, LFSR/Geffe/Gollmann, plus >2³² / millisecond / offset≠0 seed spaces.
- **Overreach:** "10 generators, 3% each" written up as "seeded-PRNG pads, closed." RECON-B/B-21
  (Round 10) already flagged "Round 8 SEED residue … dropped by every nav doc" — **the flag was
  never actioned; the ledger line is unchanged.**
- **Cheapest settling test:** add PHP `mt_rand` (validate against a `php` binary) to the sweep
  harness and run its 32-bit space — the census says this is the single highest-prior named gap.

### 3. "keytexts dead BY MECHANISM, independent of which text" (Round 7)
- **Claim** (`ELIMINATION-LEDGER.md:34,174,272`): the keytext class is closed by mechanism
  (doublet-excluded rigidly + un-anchorable skip-aware), so exhaustion no longer matters.
- **Actual evidence** (RECON-B/B-16, `round10/RECON-B/REGISTER.md`): under the repo's OWN pinned
  soft-rewrite construction (p_keep≈0.18 applied to the OUTPUT), the doublet deficit is set by the
  filter, not the key — so it has **no discriminating power over key type**, and "dead rigidly
  (doublet-excluded)" does no work. What actually survives is the ~200-text **exhaustion** sweep
  (best -5.75…-5.88), under an **unverified robustness assumption**: Campaign XVIII's validated
  gate covers key **skip** (desync), NOT value **rewrite** — `armada2/COVERAGE-MATRIX.md` has no
  rewrite row (verified: 0 rewrite rows in the matrix).
- **Overreach:** "closed by exhaustion under an unverified assumption" is stated as "closed by
  mechanism, independent of text." Flagged by RECON-B/B-16 (Round 10); **not actioned** — the
  ledger still reads "dead by mechanism."
- **Cheapest settling test:** the B-16 afternoon test — plant a known key, encipher known English,
  apply the **value-rewrite** filter at p_keep=0.18 (distinct from the key-skip form this control
  used), run the existing Campaign XVIII beam. If the correct key still scores English, add a
  rewrite row and reword "by mechanism" → "by exhaustion"; if not, every keytext null needs
  re-running rewrite-tolerant.

---

## Secondary: RECON-A holds 16 `never-run` items the "internal attack surface is closed" line
(`ELIMINATION-LEDGER.md:211`) papers over. Highest-prior beyond B-04/B-05: A-03 (haplography
count-audit of the 86 doublet sites — the cheap falsifier of the whole engineered-filter edifice;
"~20 confirmed merges would put autokey back on the table"), D-01 (generator-fingerprint suite
Campaign IV skipped), F-01 (LP2-as-pad inversion against other Cicada objects). These are not all
high-prior, but "closed" is the wrong word for a surface with 16 named, never-run entries.

## Bottom line
Three load-bearing closures (information-theoretic unsolvability, seeded-PRNG, keytext-by-mechanism)
each state MORE than their evidence supports, and the single biggest one hides a genuinely-open,
tractable, control-detectable lane (**B-04 derived-key dictionary**) that the repo's own B4/G5
proof shows can ONLY be settled by running it. Two of the three were already caught by Round 10's
RECON-B (B-16, B-21) and never actioned. The correct top-line wording is: *"OTP-**class** — the
ciphertext is indistinguishable between a true external pad (information-theoretically closed) and
a short-seed **derived** keystream (finite keyspace, brute-forceable). The derived-key dictionary
lane is untested; only running it settles which."*
