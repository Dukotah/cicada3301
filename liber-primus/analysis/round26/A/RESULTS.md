# Round 26 — Lane A RESULTS: fire the built-but-never-swept derived-key generators

Lane: round26/A | Date: 2026-08-31 | Prior: LOW | Framing: HARDENS the derived-key branch.
Real LP2 target: unsolved page idx 19 ('23.jpg, 24.jpg', 333 runes), 0-54 OTP-class band.

## INSTRUMENT POWER (measured before the sweep — doctrine R1 / control gate)

Each of the three generators passed a plant-and-recover control BEFORE its null counts. A
keystream was drawn FROM THAT EXACT GENERATOR, used to encipher held-out English
(self_reliance.txt, L=240) under the repo keyskip1 relation, and driven through hitfn20 with
`truth_idx`. hitfn20 must return HIT=True (recovery>=0.90 + panel-max + held-out 3/4).

| Generator (control seed)          | median recovery | HIT on plant | control pmax vs bar |
|-----------------------------------|-----------------|--------------|---------------------|
| Perl  make_ks('r29', 3301)        | **1.000**       | True         | 24.90 vs 7.63       |
| TeX   make_ks('pgf_rnd29', 3301)  | **1.000**       | True         | (clears, HIT)       |
| Py2.7 keystream('CICADA3301','grb5_mod', wordsize=64) | **1.000** | True | (clears, HIT)  |

**control_min_recovery = 1.000 >= 0.90 bar → all three controls VALIDATED**
(control.json: `all_controls_validated: true`). Power ~1.0 on the win-condition registers for
all three generators; the instrument certifies these keystreams where they exist. A null from
this lane is therefore a real negative, not an unvalidated-instrument artifact.

## COVERAGE (swept fraction — doctrine R2/R7, never "closed")

Prior-dense FIRST (doctrine R5): a 347-seed corpus-derived dictionary D (Cicada/3301 motifs,
first-200 primes, era dates 2011-2015 day-epochs, gematria prime-sums of 35 solved-LP thematic
words, and those words as Python-2 string seeds), swept in FULL before any dense-from-0 baseline.
Then a small stated dense baseline of 400 seeds (0..399).

Axes crossed:
- Perl: 8 Perl-reachable reductions x (D + baseline) int seeds x {keyskip1, keyskip2}.
- TeX:  4 generators (pgf_rnd29, lcg_mod29, randomtex_div29, pdftex_u29) x (D + baseline) x 2 presets.
- Py2.7: 3 reducers (grb5_mod/grb5_rej/shuffle29) x (D + baseline) x **wordsize=64** x
  **offset ladder {0,1,2,3,5,7,13}** x 2 presets — the DISTINCT axis vs R21-L3.

Planned decodes: **49,302**. Swept fraction of each 2^32 int-seed space (prior-dense + baseline):
747 / 2^32 = **1.74e-7** per generator/reduction — a bounded prior-dense slice, NOT the tail.
The flat-prior tail of 2^32 (Perl/TeX) and 2^64 (Py2.7 amd64 2-word image) is NOT swept.

## RESULT (interim — sweep in progress at report time)

The single clean sweep process was validated and launched after the controls passed. As of this
report it had scored **>1,000 decodes** of the 49,302 planned with **0 clearing the panel-max
bar** (best pmax 4.49 vs bar 7.38 on the LP1_REAL register; earlier interim best 5.44 vs 7.63 on
py27:grb5_rej/CY). This matches the Q5 checkpoint prediction: the prior-dense front shows no
decode even approaching the bar. Every row persists R3 language-agnostic stats (pmax, bar,
recovery, held-out, IoC*N, min-distinct-over-32-window, distinct-count, argmax register) in
`sweep.jsonl` so nothing is retro-fit. **HITs: 0. Flagged-for-oracle: 0.** Final counts write to
`control.json` (`decodes_run`, `best_pmax_row`, `n_clears_bar`, `hits`) on sweep completion.

No survivor cleared the bar → no oracle flag. A hit here would be a SOLVE; none appeared in the
prior-dense front.

## REPRODUCE

```
cd liber-primus && python3 tests/validate.py
cd analysis/round26/A && python3 sweep.py    # controls gate, then sweep -> sweep.jsonl + control.json
```
