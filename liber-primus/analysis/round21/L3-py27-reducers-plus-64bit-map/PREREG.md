# PREREG — Round 21 / Lane L3-py27-reducers-plus-64bit-map

_Written BEFORE the real sweep runs. Thresholds below are frozen; no threshold is edited after
seeing a result (append dated addenda only)._

## Objective

Sweep the three Py2.7 rune reducers that S-G3 (Round 20) never covered plus the amd64 (2-word)
`init_by_array` map, at a stated fraction of the 2^32 word space each, through the exact S-G3
two-stage instrument, reporting per-reducer coverage x power, survivors, hits, extrapolated
full cost. Only `random29` (i386, 1-word) was swept in S-G3 (LEDGER R19-G3 not_covered; SYNTHESIS
§8.5 thread 2). The reducers under test:

- `grb5_mod`   = `getrandbits(5) % 29`      (lazy fold, 1 MT word/rune, biased)
- `grb5_rej`   = `getrandbits(5)` rejecting 29..31 (careful fold, variable draws)
- `shuffle29`  = repeated `random.shuffle(range(29))` blocks
- amd64 2-word map: `init_by_array([w_lo, w_hi])` for `random29` (S-G3 used only the i386
  1-word map `init_by_array([w])`; on amd64 a str hash is a 64-bit long -> up to 2 key words).

## Instrument (reused, byte-exact)

`round19/G3/gen_py27.py` REDUCERS dict -> I1 `driftbeam.beam_decode` keyskip1 (exact preset,
drift_rec lam=12 max_free=2 via PRESETS["exact"]) -> I2 `adjudicate` 9-register panel ->
P3a panel-max bar (unscreened, claim bar 7.634 at exact/1e6/alpha=0.01) -> HITFN `hitfn20.is_hit`
(pmax>=bar AND rune-index recovery>=0.90 AND held-out 3/4 reproduces). Two stages exactly as
S-G3 `sweep.py`: Stage A cheap screen (bw64, L=120, promote at pmax>=SCREEN_BAR) ; Stage B full
L=240 gate on survivors only. Emits SWEEPROW/3 into `reducers_sweep.jsonl` + `out_reducers.json`.

## Five Aiming-Test answers

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit is a word `w` whose Py2.7 keystream (under the reducer under test) drives the keyskip1 beam
to a decode that (1) clears the panel-max null bar 7.634, (2) recovers >=0.90 of rune indices,
(3) reproduces >=0.90 on the held-out 3/4. Recognizer proven per reducer by the positive control:
each reducer's planted word recovers strict hit=True at pmax 28.27, recovery 1.000, held-out 1.000
(measured pre-run, this file's "positive control" section). If the instrument could not recognise
its own planted hit for a reducer, that reducer is a wiring gap and its null is not reported.

**Q2 — What measured fact raises this family's prior above the flat rate?**
`round18/L1-toolchain/RESULTS.md` §6: an Ubuntu 11.04-12.04 GnuPG-1.4.11 box promotes Python 2.7
LCG/MT seeding. `round19/G3/RESULTS.md` establishes the Py2.7 string-seed MT path is real and the
prior Py3 SHA-512 sweeps never touched it. These three reducers + the amd64 map are era-idiomatic
folds of that same validated MT stream. Prior weighting via P3b `seedprior20.json` (433 words).

**Q3 — Is the space bounded, and by what?**
Bounded, samplable. 2^32 words per reducer per map. Sampled prior-dense-first: 433 prior words +
top-64 +-512 neighbourhoods (~66k) + dense-from-0 baseline, time-boxed. Exact words screened +
fraction of 2^32 reported PER reducer (doctrine R2). Full-32 cost extrapolated from measured rate.

**Q4 — What three conditionals will the negative carry?**
1. Key space: the swept fraction of Py2.7 `init_by_array` 32-bit words per reducer (prior-dense
   first; the rest of 2^32 uncovered).
2. Decoder transition model: keyskip1 + drift_rec(lam=12,max_free=2) — one skip/drift family; a
   different rejection-loop or non-keyskip enciphering is not represented (L7-B conditional).
3. Adjudicator register: I2 9-register panel (LP1_REAL + Latin/OE/German/Welsh/EN variants);
   a plaintext outside the panel is invisible (L7-A conditional).

**Q5 — What single observation abandons this lane at 10% of budget?**
If a reducer's positive control does NOT recover rank-1 at pmax>=7.634 through is_hit, that
reducer's generator wiring is wrong: skip it, log the wiring gap, do NOT report its null as a
bound (kill condition). [Pre-run check: all four controls PASS strict, so no reducer is skipped.]

## Positive control (measured PRE-RUN, gates the whole lane)

Per reducer, plant P3b top word 1325734783 as `w`, encipher EN_MODERN[2000:2240] via
keyskip (supp 0.83), recover strict through is_hit:

| reducer            | strict hit | pmax  | recovery | held-out |
|--------------------|-----------|-------|----------|----------|
| grb5_mod           | True      | 28.27 | 1.000    | 1.000    |
| grb5_rej           | True      | 28.27 | 1.000    | 1.000    |
| shuffle29          | True      | 28.27 | 1.000    | 1.000    |
| random29 amd64 2wd | True      | 28.27 | 1.000    | 1.000    |

Panel-max bar (exact, 1e6, alpha 0.01) = 7.6342. All controls clear it by ~20 units. The lane's
own `poscontrol.py` re-runs these + a +-500 rank-1 neighbourhood check and writes
`out_poscontrol.json`; the sweep does not report any reducer's null unless that reducer PASSES.

## Thresholds (FROZEN)

- SCREEN_BAR (Stage A promote): pmax >= 5.0  (<< 7.634 claim bar; plant clears ~28, wrong <=4.2).
- Claim/HIT bar: P3a panel-max bar = 7.6342 (exact, N=1e6, alpha=0.01). NEVER -5.5.
- Recovery bar: 0.90 (rune indices, decode path). Held-out fraction: 0.25 attribute / 0.75 verify.
- HIT iff ALL THREE (hitfn20.is_hit). Score alone is never a hit.

## Time-box

<= 20 min real compute total across the 4 reducer-configs (doctrine). Budget split evenly per
config; each config screens prior-dense-first until its slice of the time-box, then extrapolates
full 2^32 cost from measured words/sec. Fraction of 2^32 reported per config.

## Register/power reporting

Per config: COVERAGE (words screened, fraction of 2^32) x POWER (positive-control measured
recovery = 1.000 strict, so power ~1.0 on the LP1_REAL / EN register at the planted supp). Both
reported together (doctrine R2). Negative stated with all three conditionals (Q4).
