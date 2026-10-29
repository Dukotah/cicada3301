# R32 / B1 RESULTS - bash 4.2 `$RANDOM` auto-seeded orbit (prefilter + beam, both relations, both ABIs)

_2026-10-28. Pre-registered in `PREREG.md` (control run first, sweep second). No git. `LEDGER.json` untouched._

**Verdict: `negative (bounded: prefilter-lossy, construction-conditional)`.** 0 flagged, 0 hitfn20 gate-3 crossers. Not "closed".

## 1. Real cost (the "28 min" figure)
`round20/CAMPAIGN-PLAN.md` S-BASH: 28 min was **16 cores with the P-gate sieve assumed**; P1 was INFEASIBLE so the sieve never existed.
On this laptop pair 64 + exact 142 decodes/s: 77,594,624 seeds x 2 ABIs x 2 relations = 6.2e8 decodes = ~70 days. Unprefiltered is infeasible; hence a prefilter.

## 2. Construction swept
bash 4.2 `seedrand()`: `sbrand(tv_sec ^ tv_usec ^ pid)`, seed = state; `round19/G1/gen_bash.py` (verbatim `brand`, anti-repeat loop, `last_random_value=0`),
`$RANDOM % 29`, sign -1, offset 0. Seed set = 74 prefixes x 2^20 = **77,594,624** (tv_sec 2012-01-01..2014-06-01). ABIs: `bash4.2` LP64 (L1-validated against a real 4.2.0 binary)
and `bash4.2_i32` (L4 only). Relations: keyskip2 (`pair`) and keyskip1 (`exact`). Panel: **round32/I2 nine-register panel**; corpora SHA-256 are in the SWEEPROW header
(`corpora_sha256`; e.g. EN_MODERN self_reliance b2f3dbd3.., mabinogion e177d7c2.., EN_KJV 0204adae.., LP1_REAL 855eed73.., LATIN 84ac8411../cc3f9845.., CY 624ffc97..).

## 3. Prefilter and its measured power (`control.json`, `prefilter_power_trigram.json`)
Relation-agnostic (both relations decode identically before the first skip): first 16 decoded runes, max over 9 registers of z(sum trigram log10), null = 2^19 seeded-3301 in-set seeds vs the real LP2 head, threshold = null 1-6e-4 quantile (4.106 LP64 / 4.101 ILP32).
Realised survivor rate 6.11e-4 (47,449) / 6.26e-4 (48,584). Vectorised heads equal the exact generator on 2000/2000 seeds per ABI (0 mismatches).
An IoC-only head prefilter was tried first and **rejected** (power 2-23 % at FPR 1e-3).

| register planted (250 plants x 2 ABIs x 2 relations) | prefilter power at FPR 6e-4 (mean; range over the 4 cells) |
|---|---|
| EN_MODERN | 0.744 (0.736-0.752) |
| LATIN | 0.700 (0.688-0.708) |
| DE | 0.738 (0.716-0.760) |
| EN_NOVOWEL | 0.473 (0.432-0.508) |

Not measured in this lane: EN_KJV, OE, CY, EN_HALFVOWEL, LP1_REAL as planted registers; free-drift plants. **The prefilter is lossy: 25-55 % of planted keys are dropped before decode.**

## 4. Positive control (before the sweep; Q5) - `control.json`, `all_pass: true`
Planted EN_MODERN/LATIN through the real `chunk()` path (planted seed inside a 2^16-seed chunk): 10 plants per (ABI x relation) cell.

| cell | prefilter pass | recovered + HIT (pmax>bar, recovery>=0.90, held-out) |
|---|---|---|
| LP64 keyskip2 | 5/10 | 5/5 |
| LP64 keyskip1 | 6/10 | 6/6 |
| ILP32 keyskip2 | 7/10 | 6/7 (the miss has recovery 1.000 and stage-B pmax 25.7 > bar 7.38; it failed another hitfn20 clause - reported, not hidden) |
| ILP32 keyskip1 | 8/10 | 8/8 |

25/26 prefilter-passers recovered end-to-end (>=3 per cell in every cell). Passer screen pmax ~17-20, stage-B ~24-28, bars 7.3835 / 7.6342. Two plant texts (EN/LATIN), same decode functions as the sweep.

## 5. Sweep (`sweep.py sweep`, `sweep_rows.jsonl`, `sweep_summary.json`)
**Complete**: 74/74 prefixes, 2022.9 s wall (cap 2500). Seeds prefiltered 77,594,624 per ABI (**coverage of seeds 1.00 at the prefilter stage; the decode stage covers only prefilter survivors**).
**192,066 decodes** (47,449 + 48,584 survivors x 2 relations); 490 reached stage B (pmax >= 5.0). SWEEPROW rows persisted for every decode (not for prefilter-rejected seeds); `validate_store` passes 192,066 rows and
`handoff/validate_ledger.check_r3_store` returns `[]` (header carries `ioc, mds, pmax_ne, zl`).

Best screen pmax (L=120) vs bars:

| relation x ABI | best pmax | seed | claim bar, N=1e6 (declared) | claim bar at actual N=192,066 |
|---|---|---|---|---|
| keyskip2 LP64 | **7.068** | 1354603465 | 7.3835 | 6.939 |
| keyskip2 ILP32 | 6.762 | 1354603465 | 7.3835 | 6.939 |
| keyskip1 LP64 | 6.198 | 1398535392 | 7.6342 | 7.161 |
| keyskip1 ILP32 | 6.679 | 1375265595 | 7.6342 | 7.161 |

**Disclosure.** keyskip2 seed 1354603465 clears the actual-N screen bar (7.068 > 6.939) though not the declared-N bar. The decisive gate (hitfn20 at L=240) re-decoded it:
pmax 4.66 (recovery 0.61) LP64 and 6.09 (recovery 0.87) ILP32, both below the bars, so clause 1 fails; the L=120 text is `EAOEEAHEWASEDOROW...` (best register LP1_REAL). Treated as a single-draw extreme of the null and **not flagged**; recorded so the coordinator can overrule. The two ABIs' streams coincide early in this seed's orbit (identical until a negative Schrage residue), so those two rows are not independent.
I3's L-aware `threshold_for(n=192066, segment_len=120)` = **-5.5** (the floor binds at this N); it governs the legacy `en` statistic, so the pmax claim bar is hitfn20's `panelmax_bar`, shown above. `flagged: []`, `gate3_crossers: []`.

## 6. Coverage x power (not "swept")
| axis | coverage | power |
|---|---|---|
| seeds (auto-seeded set) | 1.00 prefiltered, both ABIs | prefilter 0.47 (NOVOWEL) - 0.74 (EN) |
| relation | keyskip1 + keyskip2 (not free-drift) | decoder 25/26 on passers (EN/LATIN) |
| register | panel adjudicates 9; plants measured for EN, LATIN, DE, NOVOWEL (prefilter) | end-to-end ~0.71 EN, ~0.67 LATIN, NOVOWEL prefilter 0.47 (NOVOWEL decoder power not re-measured here) |
| ABI | LP64 (L1) + ILP32 (L4) | same |

## 7. The three conditionals
1. **Key space:** bash 4.2 auto-seed set (74 x 2^20), `RANDOM % 29`, offset 0, sign -1, 2 ABIs.
2. **Transition model:** keyskip1 (`exact`) and keyskip2 (`pair`), beam_w 64, L=120 screen / L=240 gate.
3. **Adjudicator register:** round32/I2 nine-register panel; EN_NOVOWEL detection-only; pmax bars from hitfn20 (N=1e6 reference).

## 8. not_covered
bash 3.2 / 4.0 / 4.1 / 5.x maps; explicit `RANDOM=n` seeds outside the set; seeds outside the 2012-01-01..2014-06-01 window; subshell re-seeding; reductions other than `%29`; sign +1, reversed, atbash; free-drift and any relation beyond keyskip1/2;
the 25-55 % of planted keys the prefilter drops (a key whose first 16 decoded runes score below null q0.9994 is invisible: skips in the head, vowel-dropped text); anti-repeat collisions inside the 16-rune head (<=0.05 % of seeds); registers not planted (EN_KJV, OE, CY, HALFVOWEL);
LP2 beyond rune 120/240 (a pad that does not begin at rune 0); ILP32 only L4-validated; flat prior over the auto-seed set (NC-4).

## 9. Reopen
A higher-power skip-tolerant prefilter or a stated-fraction un-prefiltered sample to measure the lost fraction; a real 32-bit bash 4.2 (ILP32 to L1); other bash versions/reductions.
