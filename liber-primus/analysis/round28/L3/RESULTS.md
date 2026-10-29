# R28-L3 RESULTS (write-up, Round 32 lane B3) — string-seed Py2.7 amd64 dictionary

_Written 2026-10-28 by R32-B3 strictly from artifacts on disk in this directory. No sweep was re-run._
_Verdict: **`inconclusive`** (bounded-negative evidence is on disk; bulk artifacts are missing — see §7)._

## 1. What ran (from `progress28.json`, `PREREG.md` + amendments A1–A6)

11 items, all `status: complete`, `stopped: all-items-complete`, `elapsed_s` 7,828.7, `flagged_survivors: []`.
Decoder: Py2.7 `random.seed(str)` amd64 (64-bit hash) -> 2-word `init_by_array`, wordsize 64, offset 0. Stage A =
driftbeam (`pair`|`exact`), beam_w 64, L=120, scored by the I2 nine-register panel (`pmax`). Stage B = hitfn20
three-clause gate for pmax >= 5.0.

| item | reducer x relation | tier | decodes | skipped (R26-C image) | best pmax | best seed | stage-B (pmax>=5.0) |
|---|---|---|---:|---:|---:|---|---:|
| r29_pair_t0 | random29 x pair | 0 corpus | 32,298 | 31 | 5.315 | `204 966 278` | 7 |
| r29_exact_t0 | random29 x exact | 0 | 32,298 | 31 | 4.9988 | `25 AUGUST 2012` | 0 |
| grbmod_pair_t0 | grb5_mod x pair | 0 | 32,298 | 31 | 5.2915 | `BIBLE-DOUAY-RHEIMS` | 4 |
| grbrej_pair_t0 | grb5_rej x pair | 0 | 32,298 | 31 | 5.2081 | `4397` | 2 |
| shuf_pair_t0 | shuffle29 x pair | 0 | 32,329 | 0 | 5.3251 | `APOEMOFFADINGDEATHNAMEDFORAKING` | 2 |
| r29_pair_t1 | random29 x pair | 1 wordlist | 389,789 | 0 | 6.0952 | `sestole` | 37 |
| r29_exact_t1 | random29 x exact | 1 | 389,789 | 0 | 5.7037 | `actaeonidae` | 34 |
| r29_pair_t1b | random29 x pair | 1b UPPER | 389,782 | 0 | 5.7584 | `UNDERLOOKER` | 36 |
| r29_exact_t1b | random29 x exact | 1b | 389,782 | 0 | 5.7581 | `IMPLORATORY` | 22 |
| r29_pair_t1c | random29 x pair | 1c Title | 389,772 | 0 | 5.9478 | `Galvanoplastic` | 40 |
| r29_exact_t1c | random29 x exact | 1c | 389,772 | 0 | **6.3148** | `Graplin` | 42 |

Sum of `done` = **2,500,207** decodes (items x seeds; 11 items, not 2.5M distinct strings). Internal consistency
re-checked here: per-item histogram mass == `done` for all 11 items; histogram mass at pmax >= 5.0 == `n_stage_b`
for all 11 items; top histogram bin consistent with `best_pmax`. Dictionary: `dict_meta.json`
deduplicated_total 1,201,672 (tier0 32,329; wordlist 389,789 / UPPER 389,782 / Title 389,772) after dropping
11,878 hash-image collisions.

## 2. Threshold actually used vs the contract bar

- Stage-A candidate bar: `SCREEN_BAR = 5.0` (frozen R27 constant).
- Claim bars: pair 7.3835, exact 7.6342, "at N=1e6 ceiling" (PREREG Bars). Every cell's N is <= 389,789, so
  these are conservative per cell. The round19/I3 panel-max bar at N=1e6 is 7.634 (I3 RESULTS, "NEW pmax bar
  (7.634)"), equal to the exact-cell bar used. I did not re-derive I3.
- Best pmax over all 2,500,207 decodes: **6.3148**, 1.32 below the exact bar and 1.07 below the pair bar (best
  pair pmax 6.0952). No decode reached any claim bar, so the A6 mitigation ("flag every row >= claim bar
  regardless of clauses 2/3") flagged nothing.

## 3. Control recovery (stored)

- `controls.json` (2026-09-08T11:45:09, before the first sweep row): one planted `THE PRIMES ARE SACRED`
  through the real stage-B path in each cell. random29 x pair pmax 25.36, recovery 0.9917; random29 x exact
  25.239 / 1.000; grb5_mod x pair 25.239 / 1.000; grb5_rej x pair 25.239 / 1.000; shuffle29 x pair 25.239 /
  1.000; `all_pass: true`.
- `control_e2e.json` (10 plants x 5 cells, screen + 3-clause gate): end-to-end recovery random29xpair 1.0,
  grb5_rejxpair 1.0, shuffle29xpair 1.0, random29xexact **0.9 (9/10)**, grb5_modxpair **0.8 (8/10, cell
  `pass:false`)**. PREREG A6 attributes every miss to clause 3 only, with rune recovery 1.000. Stage-A
  sensitivity: 50/50 plants cleared the 5.0 screen, min stage-A pmax 17.931 (17.748 for shuffle29), i.e. 12.7+
  above the screen bar. So the measured loss is in the auto-HIT label, not in the screen.
- `hash_gate.json`: 1,500/1,500 strings equal real CPython 2.7.18 amd64 `hash()`. `subsumption.json`: 200/200
  i386 string seeds equal `init_by_array([hash32])` (i386 half inherited from R27-S1/S2, not re-swept).
- The control is a planted English plaintext (`self_reliance.txt` idx 5000..) at one offset under the
  skip_by_two / keyskip1 model, run through the decoder separately. It was NOT injected into the real-ciphertext
  sweep stream.

## 4. Null

No separate null run exists. The null is the sweep's own per-item pmax histogram (`progress28.json hist`, 0.1
bins): bulk 1.0–2.5, tail decaying to a few rows per ~390k at 5.0–6.3. No excess near the claim bars. The
Gumbel-null reference curve is I3's, not re-fit here.

## 5. Coverage x power

- Coverage: the dictionary's amd64 image under random29 x {pair, exact} (tiers 0, 1, 1b, 1c) and grb5_mod /
  grb5_rej / shuffle29 x pair (tier 0 only), offset 0. 2,500,207 decodes against a 2^64 image: visited
  fraction of the image ~1.4e-13.
- Power: screen-level planted recovery 50/50 (Wilson 95% lower bound ~0.93) at plant pmax 17.9 vs bar 5.0, on
  ONE plant text / length / offset and ONE skip model per relation. End-to-end 0.8 (grb5_mod x pair) and 0.9
  (random29 x exact).
- not_covered: strings outside this dictionary; the wordlist tiers for grb5_mod / grb5_rej / shuffle29;
  offsets != 0; other word sizes except the subsumed i386; PYTHONHASHSEED / -R; Python != 2.7; relations other
  than pair / exact (free drift); beam_w > 64; L != 120 screen.

## 6. The three doctrine conditionals (Q4)

1. **Key space:** dictionary strings' amd64 Py2.7 hash image, offset 0, cells as tabled.
2. **Transition model:** keyskip1 (`exact`) and keyskip2 (`pair`) only.
3. **Adjudicator register:** I2 nine-register panel pmax (English, KJV, LP1_REAL, Latin, OE, DE, CY, half- and
   no-vowel English) — not English-only. EN_NOVOWEL is detection-only (R21-L3). Non-linguistic payloads are not
   covered. **No SWEEPROW/1 bulk store was persisted** (only the stage-A histogram, a top-32 list and stage-B
   rows to `candidates28.jsonl`), so R3 language-agnostic stats exist only for the stage-B crossers, and those
   rows are not on this checkout.

## 7. Verdict and what is missing

**`inconclusive`**, not negative, by the lane's kill rule (artifacts incomplete). Absent from this checkout
(gitignored, `.gitignore` ~lines 371–376; they lived on the originating machine):
- `candidates28.jsonl` — the 226 stage-B rows (7+0+4+2+2+37+34+36+22+40+42). Unverifiable here; every one had
  pmax < a claim bar per `best_pmax`.
- `dictionary.jsonl` — rebuildable by `build_dict.py` but needs the 390,306-word list
  `corpus/E-tooling/vendor/cicada-solvers__libergo/words.txt` (sha256 `0ae20e66…c1a9`), also absent, so the
  coverage count cannot be independently recounted; it rests on `dict_meta.json` and `progress28.json`.
- `sweep28.pid` and any SWEEPROW bulk store (never written).

On disk and consistent: complete progress for all 11 items, pre-sweep controls with stored recovery (5/5 pass),
hash gate, subsumption, and a self-consistent histogram null with best pmax 6.3148 against bars 7.38 / 7.63.

**Upgrade path to `negative (bounded)`:** recover `candidates28.jsonl` and `dictionary.jsonl` (or rebuild with
the pinned wordlist) from the originating machine and confirm all 226 stage-B rows have pmax below their bar.
No re-sweep needed. Until then do not cite it as an exclusion. It is not "closed" or "exhausted": ~1.4e-13 of
the 2^64 amd64 image was visited.
