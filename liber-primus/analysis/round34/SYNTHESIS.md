# Round 34 — SYNTHESIS (CLOSE THE LOOP)

_Run 2026-10-29/30 on the owner's laptop plus one Vercel Linux sandbox. Plan of record:
[`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md). Seven lanes,
eight Sonnet agents, ~14 h wall including an overnight sleep. Every lane ran a positive control before its null
counted. `LEDGER.json` 195 rows, 0 errors, 0 unsound negatives; `tests/validate.py` passes; `pytest tests/ benchmark/`
24 passed; capsule `verify_capsule.py` INTACT-FAIL 13 → 2 (both expected substitute corpora)._

## 1. Verdict in one paragraph

No survivor. The repaired instrument was run where its holes were: the full bash `$RANDOM` auto-seed orbit (both ABIs)
and the PHP `mt_rand` prior-dense tier were screened with a register-aware head prefilter and decoded with the
register-aware beam under an observed null, and nothing cleared any bar (B1). The payload canon is promoted with every
re-runnable reader re-fed first (P1 + coordinator). The seal candidate D5c calibrates at four lengths (I3) but stays
unadopted. The sandbox lane built the fixed C engine and proved its resume path on copies, pinned the PHP 5 reference
value, and tightened the Ghostscript band to 9.05–9.14 by rendering rather than by file-in-tree (S1). The red-team
overturned two of this round's own claims: the prefilter's 0.998 vowel-drop power was an artefact of skip-free plants
(operative ≈0.66), and the v3 null's kill-rule alarm was a like-for-like error (X1). The honest residue is one
number: **≈30–35 % of true-key mass in those orbits sits in heads that contain a key skip, and no head screen yet
passes those.**

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | observed v3 null; Q5 alarm withdrawn by X1 | 20/20 at L=120/240/400 all nine registers; **fails L=31 and `free`** | instrument | 40k draws at L=31/120; β exponent −0.11 to −0.14 (like-for-like prediction ≈−0.05: fine); Gumbel conservative at L≤240; bars 9.24/9.03 (L120, N=1e6). B3's modelled bars were 0.08–0.28 low, immaterial. |
| I2 | prefilter met its bar on skip-free heads; **operative power ≈0.66** | 2,000 plants/register | instrument | lse m=20, FPR 1.0e-3, 1.31× slower; X1: 37–51 % of real heads contain a skip and pass at 0.19–0.34 → R32-B1's 0.47 stands; the claimed artefact was not one. |
| I3 | D5c calibrates at L=120/180/240/400 (recipe 1); SEAL_PASS=false | frozen tuning key | instrument | m_NV 6.95/10.45/13.58/20.21 (≈0.055·L, not pre-registered); L=400 passed only after a disclosed sample extension (3/100, Wilson upper 0.085); EN_HALFVOWEL hallucinations unprotected. |
| S1 | three measured outcomes | — | build box | engine compiles clean, 4/4 resume tests on copies; **S2 still blocked**: its self-test is gated on `round19/I2/models/panel.npz` (sha 14a23d36…), absent everywhere; PHP 5.6.40 `mt_srand(1); mt_rand()` = 1244335972, 40/40 match; gs 9.04 ships the ICC file but does not embed it, 9.05–9.14 do → band 9.05–9.14. |
| P1 | nothing changes; GO | every reader's control + canon comparator | 5 readers + 3 campaign18 scripts + hash_hunt | R30-B1 canon-as-key over T2/folly and R30-B2 folly/2.jpg legs unmeasured (inputs absent). Capsule settled: 9 CRLF, validate.py = R19 AN-END guard, kjv/mabinogion = R32 substitutes. |
| B1 | **NEGATIVE, bounded** | 120/120 (skip-free by construction — decode path only) | bash orbit 1.000 × ≈0.65–0.70 reach; PHP prior-dense 1.000; PHP uniform 0.00061 | 12 cells, best 7.068 (the Round 32 near-miss seed again) vs 8.118 actual-N / 9.034 declared-N; 0 flagged, 0 near-miss. |
| X1 | FOUND-ERROR ×2 substantive + minors | re-runs | — | §4. R33-I2 "earned" relations struck. GS band applied to nav docs. Manifest decision written. |

## 3. What the instrument now says that it did not say yesterday

1. **The register-aware beam has an observed null** (`round34/I1-v3-null/bars_v3.py`). Every future v3 negative's bar
   is read off measured draws at its L and N, Gumbel-fitted, conservative at L≤240. Not for L=31 or `free`.
2. **The bash orbit is a register-aware negative at ≈0.65–0.70 reach**, up from ≈0.47 for vowel-dropped English.
   The prefilter, not the decoder, is now the binding instrument: heads with a key skip in the first 20 runes pass at
   0.19–0.34. A skip-tolerant head screen (DP over advance 1/2) is bounded and is Round 35's flagship.
3. **The payload canon is one file again.** `canon_256.bin` = R19-C1's resolved bytes; every re-runnable reader
   was re-fed first and none moved; the superseded bytes are kept; the capsule manifest and verifier agree with the
   tree except for the two substitute corpora, which are labelled as such.
4. **S2 can be resumed only once the Round 19 panel is restored byte-exact.** The engine is proven; the gate is a
   panel built from the *original* corpus downloads (sha 14a23d36…), which this checkout does not have. Restoring it
   is a bounded fetch-and-rebuild job (Round 35).
5. **The toolchain band is 9.05–9.14**, by what Ghostscript writes rather than what it ships.
6. **Auto-certification stays off.** D5c now calibrates across four lengths, but its L=400 pass is marginal and its
   `m_NV(L)` rule is post-hoc; EN_HALFVOWEL hallucinations are unprotected.

## 4. Red-team findings (X1)

| target | verdict |
|---|---|
| R34 I2 skip-free-head claim | **FOUND-ERROR (substantive).** Skips fire on the candidate rune; 37–51 % of real heads contain one; operative power ≈0.66 NOVOWEL / 0.71 EN. R32-B1/B2 unchanged. |
| R34 I1 Q5 ("not Gumbel") | **FOUND-ERROR (framing).** z-scored vs raw exponent; like-for-like Δ is 1.4–2.1 SE. "Gumbel conservative" not shown at L=400. |
| R33 I2 "earned" relations | **STRUCK.** The 2× gate cannot fail when every ratio is 0.88–1.00. |
| R33 B3 | row counts reproduce (994 duplicate B2 kids → 403,290 unique); bars 0.08–0.28 low vs observed, immaterial. |
| R34 I3 / S1 / P1 | main claims hold; wording fixes; PREREG mtimes post-date outputs where addenda rewrote the file (disclosed). |
| capsule INTACT-FAIL ×13 | settled (`manifest_decision.md`) and applied by the coordinator. |
| B1 | audited by the coordinator from on-disk artifacts (agent stalled after the sweep finished); control is skip-free by construction. |

## 5. Owner-only items (recorded, not blocking)

1. A stopped Vercel sandbox record and a 1.28 GB snapshot (`snap_84wyROyjgjBX7veiBuxb8bqgyJYU`, auto-expires
   ~2026-11-05) remain; delete from the dashboard unless the O1 bisect on a real page source is wanted.
2. Four stale PRs (#7–#10) predate the 2026-08-11 merge.
3. The original KJV and Mabinogion downloads recorded in the capsule are absent on this checkout; the Round 32
   substitutes are labelled. Re-fetching the originals is Round 35 P1's job and also unblocks S2.

## 6. Round 35 — seeded from X1's critic list (plan: [`../round35/CAMPAIGN-PLAN.md`](../round35/CAMPAIGN-PLAN.md))

1. Skip-tolerant head prefilter (DP over advance 1/2 on the first 20–24 runes) with a measured envelope, then the
   bash orbit re-screened with it — the one measured hole left in the two best negatives.
2. Restore the Round 19 panel byte-exact (fetch the original corpora, rebuild, match sha 14a23d36…); if it matches,
   resume S2 for a stated window on the build box.
3. D5c pre-registered validation of `m_NV ≈ 0.055·L` on new keys and intermediate lengths; cover EN_HALFVOWEL.
4. The R30-B1/B2 T2/folly/2.jpg legs, if the inputs can be regenerated from committed code.

No new key space. A survivor would be extraordinary; the round succeeds without one.
