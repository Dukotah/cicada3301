# Round 33 — SYNTHESIS (THE REGISTER-AWARE BEAM)

_Run 2026-10-29 on the owner's laptop (~7 GB RAM, < 1 GB free, no C toolchain). Plan of record:
[`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md).
Seven lanes + one PREREG-only lane, eight Sonnet agents, ~5 h wall. Every lane ran a positive control before its null
counted. `LEDGER.json`: 188 rows, 0 errors, 0 unsound negatives; `tests/validate.py` passes; `pytest tests/ benchmark/`
24 passed; no document drift._

## 1. Verdict in one paragraph

No survivor. The flagship landed: a beam whose search is register-aware (`beam_v3.py`, panel-max design) recovers
vowel-dropped English at **1.000** under every relation where the Round 19 beam managed 0.72, with no other register
losing more than 0.012 and at 1.4–2.3× the cost (I1). Re-decoding every stored survivor row of the repo's two
best-instrumented negatives through it flagged nothing (B3, 404,284 rows, coverage 1.00 of stored survivors). The
construction axis beyond {1, 2, free} was planted and priced: the doublet-rate prior that promoted `skip_by_two` in
Round 18 does not replicate at full length and discriminates nothing (I2, confirmed by X1), so no new relation was
merged. The corrected payload bytes change nothing in three of four re-fed rows (B1). An outside contributor's
transcription correction was landed and GitHub issue #12 closed; p27:93 resolves to U; the LP1 read-gate failure is
image coverage, not substitution (B2). The red-team found the Round 32 C-engine patch could never have compiled (X1).

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | **VALID** (design 1 of 3) | planted key, 54/54 cells recovered (driftbeam 48/54) | instrument | EN_NOVOWEL 0.72 → 1.000 (all 6 cells); worst Δ vs driftbeam −0.012; design 3 (no LM at all) also recovers NOVOWEL → the defect was the English-quadgram search bias. hitfn20 bars do not transfer to v3. |
| I2 | measured; kill rule did not fire (because nothing discriminates) | 20 plants/cell | instrument | doublet rate at full length ≈0.60 % for every construction incl. keyskip1 (LP2: 0.664 %). skip_by_3 covered by `free`; skip_by_4/5, reset_per_page/line unrepresented (best 0.83 / 0.74 / 0.51 / 0.21). Relation patch filed as a **queued completeness ritual**, not merged (R4). |
| B1 | NEGATIVE unchanged ×3; R17 not re-runnable | original harnesses, controls passed | B-04 7 payload-derived seeds, 76,160 decodes | corrected bytes (idx 45/50/246) flip nothing: B-04 best 5.11 vs 7.38; E-01 0 HIT (vacuous: payload ≥ modulus); E-02 Spearman shifts in the 3rd–4th decimal. R17's trigram prefilter needs three gitignored corpora → `not_covered`. |
| B2 | data correction landed; p27:93 = U; LP1 gate diagnosed | validators byte-identical before/after | finite objects | issue #12 two-gap fix applied (`.` 183 → 181); p27:93 6 px from a mislabelled U exemplar, ~2,900 px from every real B; LP1 94.60 % reproduces — 75 of 97 misses are one SOME WISDOM block absent from the vendored images (98.72 % without it). |
| B3 | NEGATIVE, bounded (survivors only) | 120/120 plants incl. 60 EN_NOVOWEL | 404,284 of 404,284 stored rows (1.00); v3 power 30/30 per register | best 7.068 (keyskip2, bash seed 1354603465 — the same Round 32 near-miss) vs bar 8.373; 6.856 vs 8.546 keyskip1. Bars are a POT fit extrapolated ~10× past a 12k-draw null (modelled, slightly lenient). Prefilter-dropped orbits not re-decoded; NOVOWEL reach still capped by the 0.47 prefilter. |
| O1 | PREREG-only (no build box) | — | — | queued; Q5 kill test = gs 9.04 vs 9.14 render of page 0. |
| X1 | FOUND-ERROR ×4 real/minor | two re-runs | — | see §4. |

## 3. What the instrument now says that it did not say yesterday

1. **"Would the true key have survived our sweeps if the plaintext were vowel-dropped English?"** Under every
   pre-Round-33 beam: no (0.72 recovery with the correct key, and the search steers away from it). Under v3: yes
   (1.000), at the survivor level of R32-B1/B2. At the *orbit* level the answer is still "≈0.47 × prefilter", because
   the prefilter was never register-aware. That is Round 34's compute.
2. **The `skip_by_two` prior was an artefact.** Round 18's 0.84 % was 2 doublets in 239 pairs. At full length every
   rejection-loop construction, keyskip1 included, sits at ≈0.60 % against LP2's 0.664 %. The relation stays (it is
   cheap and representable); the *prior* for it over keyskip1 is withdrawn, marked superseded in the nav docs.
3. **v3 needs its own null.** Because the search now optimises the statistic the adjudicator reads, v3's shuffle-null
   maximum rises (free/L=400: 8.60 → 13.03 at N=100). The hitfn20 bars, fitted on driftbeam decodes, are not v3's
   bars. B3 used a modelled bar; Round 34 I1 observes one.
4. **The transcription is in better shape than the gate said.** The 99 % LP1 read gate fails on image coverage (a
   75-rune block the vendored images do not contain), not on glyph substitution; p27:93 is settled; two separator
   categories are corrected with outside provenance.
5. **Auto-certification is still off.** D5c holds at L=240 on a third clean key (0.971 catch, 0/16 NOVOWEL genuine
   rejected) and fails at L=120 (rejects 53/53 NOVOWEL genuine). SEAL_PASS=false.

## 4. Red-team findings (X1)

| # | target | verdict |
|---|---|---|
| 1 | Round 32 B2 (PHP mt_rand), never audited | numbers reproduce; control is prefilter-conditional (end-to-end recall 0.75); with-replacement sampling → unique coverage ≈0.9658 %; PHP-5 reference 1244335972 reproduced from source structure, unverifiable without a binary |
| 2 | D5c replication | holds at L=240, fails at L=120 (above) |
| 3 | C-engine patch | **FOUND-ERROR (real):** raw newline inside a string literal in both files — could never have compiled. Fixed; still unbuilt. S2 stays do-not-resume. |
| 4 | `not_covered` hygiene | 9 drafted texts confirmed (tags dropped); R30-A1/A2/B1/B2/C1 filled; validator now warns on `null` for negatives from R19 (0 fire) |
| 5 | this round's lanes | I1 all 54 cells recomputed, 0 mismatches; I2 doublet finding confirmed; B1 missed five readers of `canon_256.bin` (R16-KDF via B-04 seeds, R30-B1, R30-B2, recon `h1_index`, campaign18 scripts) + the capsule manifest; B2's two-character diff confirmed by sha round-trip |
| — | B3 | audited by the coordinator (X1 closed first): summary, control and row count consistent with RESULTS |

## 5. Owner-only items (recorded, not blocking)

1. **`payload_resolved.bin` promotion is deferred to Round 34 P1.** Option A stands, but five more readers and the
   capsule manifest must be re-fed/regenerated first; the rename is reversible and happens after Round 34 X1.
2. **S2 resume** waits for the fixed engine to be built and tested on a real compiler (Round 34 S1).
3. The 13 `verify_capsule.py` INTACT-FAIL items look like CRLF checkout noise and were not confirmed (Round 34 X1).
4. Four stale PRs (#7–#10) predate the 2026-08-11 merge; closing them is the owner's call.

## 6. Round 34 — seeded from X1's critic list (plan: [`../round34/CAMPAIGN-PLAN.md`](../round34/CAMPAIGN-PLAN.md))

1. Re-feed the unfed readers, regenerate the capsule, promote the payload (P1).
2. v3 null of record — observed, register-matched, Gumbel over four lengths (I1) — then the two orbits under a
   NOVOWEL-aware prefilter + v3 (I2 → B1): the one place the repaired instrument has not yet looked.
3. D5c `m_NV(L)` on ≥4 lengths (I3).
4. A Linux sandbox to build the C engine, a PHP 5 reference, and the O1 kill test (S1).

No new key space. A survivor would be extraordinary; the round succeeds without one.
