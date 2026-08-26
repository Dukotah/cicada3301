# I1 — DRIFT-TOLERANT DECODER — PRE-REGISTRATION

_Round 19, Phase 0, BLOCKING lane. Written **before any measurement**._
_Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

Trust anchor recorded at the top of `RESULTS.md`, run before and after.

---

## 0. The defect this lane exists to repair

`campaign18_skip/skipdecode.beam_decode` admits a key skip only if **every** skipped key
position would have reproduced the previous cipher rune. That validity test is exact for
`encipher_keyskip` and for nothing else. `round18/L7-redteam/RESULTS.md` §B measured the
consequence: handed the **correct key**, the beam scores

| construction | correct-key score | recovery |
|---|---|---|
| `skip_by_two` (rejection burns two draws), every `supp` | -5.90 … -6.90 | 25.8 % |
| free drift q = 0.05 | -6.88 | — |
| 5 unrepresentable key advances / 240 runes | -6.67 | 25.8 % |
| low-entropy pad, constant run r = 16 / 32, `supp` = 1.0, `ms` = 8 | -6.50 / -7.05 | — |

and raising `beam_w` 400 -> 1000 and `max_skip` 3 -> 8 changes those by **exactly 0.000**.
It is not a search-depth failure: the true path is outside the decoder's transition relation.

---

## 1. The Aiming Test (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it?

A hit for this lane is **a decoder that emits the true plaintext runes when handed the correct
key over a ciphertext produced by a rejection loop it was not built for.**

The recognizer is written before the search and is the same plant-and-recover harness L7-B
used, unchanged: plant a known held-out English plaintext under a known `sha256_ctr` keystream
through each construction, decode with the **correct key**, and read
`(lp.score.default().score_norm, rune-index recovery)`. The planted object *is* the shape being
hunted — a correct key whose pointer has drifted — not a friendly analogue. Because the harness,
plaintext source, key family, seeds and bar are all L7-B's, every number produced here is
directly comparable to `round18/L7-redteam/out_b1.json`, and the *old* decoder run through the
same harness is the built-in negative control that proves the recognizer can fail.

Second recognizer, for the fix's own failure mode: a wrong-key null of >= 2,000 keys per
permissiveness setting. If the recognizer only ever says "found", it is not a recognizer.

### Q2 — What measured fact raises this family's prior above the flat rate?

`round18/L7-redteam/RESULTS.md` §B.2–B.3, with raw rows in `out_b1.json`:

- **`skip_by_two` reproduces LP2's own ciphertext doublet rate** — 0.84 % median against the
  observed 0.664 %, inside the ±0.3 pp band — while being missed at -6.90 / 25.8 % recovery.
  It is a one-character change to a plausible 2013 rejection loop and appears in **no**
  `not_covered` field in `LEDGER.json`.
- The same table **excludes** key-side and plaintext-side filter placement (3.77 % / 3.80 %
  doublet), so the filter demonstrably acted on the *output* — which is precisely the family
  where the draw-count ambiguity lives.
- `round18/L2-filter-leak/RESULTS.md` §B.3 supplies the full-book positive control this lane
  must not regress: -4.098 / 0.9997 at L = 12,956, wrong key -7.305.

So the drift family is not a completeness ritual: one member of it matches the only surface
statistic the real ciphertext offers *and* is invisible to the instrument that produced every
negative in this repository.

### Q3 — Is the space bounded, and by what?

This lane sweeps **no key space**. It sweeps a *decoder-configuration* space, which is
**enumerable and small**: `mode in {keyskip1, keyskip2, permissive}` x `max_free in {0,1,2,3}` x
`lam in {0,2,4,6,8,12,16,24}` x `max_skip in {3,8,40}` — under 300 configurations, enumerated
exhaustively rather than sampled.

The **construction axis** it claims coverage over is *unbounded* (the set of all rejection
loops a 2013 author could have written) and I say so plainly. I cover the ten constructions
L7-B measured as failures, plus two constructed here. The permissive mode's entire claim is
that it does not have to enumerate the construction space — that it admits any key advance of
<= `max_skip` positions per rune of which <= `max_free` are not doublet-consistent, whatever
caused them. That claim is tested on 12 named constructions and asserted, not proved, beyond
them. The negative it can support is therefore of the form "not representable by <= `max_free`
unexplained advances per rune", never "any loop".

### Q4 — The three conditionals every negative from this lane will carry

1. **Key space** — none swept. The key is always either supplied correct (power arm) or drawn
   from an explicit wrong-key null (`sha256_ctr` with random seeds; plus the real 12,956-rune
   LP2 stream for the operational null).
2. **Decoder transition model** — `keyskip1` (exact, = the repo's current relation),
   `keyskip2` (skipped positions in pairs, first of each pair doublet-consistent), or
   `permissive` (<= `max_skip` advance per rune, <= `max_free` of them not doublet-consistent,
   penalty `lam` each). **Not covered by any mode:** an advance > `max_skip` at a single rune,
   a key pointer that *retreats* (the beam can insert draws, never remove them), a
   non-monotone key pointer, or a key value stream that is itself a function of the plaintext.
3. **Adjudicator register** — English quadgram `lp.score.default().score_norm` throughout.
   I1 deliberately **pins the register axis at English** so that every loss it measures is the
   decoder's. The register axis is I2's lane; nothing here extends to a non-English plaintext.

### Q5 — What single observation abandons this lane at 10 % of budget?

**Kill condition A.** At the *most permissive* setting reachable (`permissive`, `max_free = 2`,
`lam = 0`, `max_skip = 8`) the correct key on `skip_by_two supp = 0.83`, L = 240, 7 seeds, does
**not** reach median score >= -5.5 **and** median recovery >= 0.90. If the loosest transition
relation still cannot hold the true path, the transition relation was not the binding
constraint, and no value of `lam` will help. I stop, and report **G-FIX FAIL** with that
number, rather than sweeping `lam`.

**Kill condition B.** If every `lam` that satisfies Kill-A also lifts the wrong-key median
above **-6.0** (i.e. there is no `lam` window in which the correct key is recovered *and* the
null stays in its measured noise band), the fix buys recovery at the price of the separation it
exists to protect. I report that plainly as **G-FP FAIL** with the full tradeoff curve, and
recommend Phase 2 sweep in `keyskip1` (unchanged) with the drift family explicitly listed in
`not_covered`.

**Checkpoint:** both are evaluated immediately after the equivalence gate G-EQ, before any of
the wide sweeps are launched.

---

## 2. Instrument

`round19/I1/driftbeam.py`, built on `round18/L2-filter-leak/fastbeam.py` (gate F0: bit-identical
to `skipdecode.beam_decode`, max |dscore| 7.99e-15, 9x faster, last-3-chars + back-pointer, no
per-hypothesis string growth). The fastbeam optimisation is preserved; the only change is the
transition relation.

**The algebra the fix rests on.** For a candidate accepted key index `acc` at rune `i`, the
repo's validity test requires, for every skipped `m` in `(pa, acc)`:

```
(p - sign*K[m]) % N == c_prev,   p = (c_i + sign*K[acc]) % N
  <=>  K[m] == (K[acc] - sign*(c_prev - c_i)) % N  ==  v(acc)
```

i.e. **every skipped key position must hold one single value `v(acc)`, determined by `K[acc]`**.
So the number of *unexplained* skips is `dsk - cnt[v(acc)]` where `cnt` is a 29-bin histogram of
the skipped window, maintained in O(1) as `acc` advances. That makes:

- `max_free = 0` exactly the repo's relation (asserted by gate G-EQ, not assumed);
- an early break at `dsk - max(cnt) > max_free`, which costs O(max_free) branches on a
  high-entropy pad and only opens up inside a constant key run — which is exactly where the
  low-entropy-pad failures live. `max_skip` can therefore be 40 without paying for it.

Modes:

| mode | transition relation |
|---|---|
| `keyskip1` | `dsk` skipped positions, all doublet-consistent. Exact for `encipher_keyskip`. |
| `keyskip2` | `dsk` even; positions at even offsets doublet-consistent, odd offsets free. Exact for `skip_by_two`. |
| `permissive` | any `dsk <= max_skip`, of which at most `max_free` are not doublet-consistent, at a beam-score penalty `lam` each. |

The penalty steers the search only; the **reported score is the unpenalised
`Q.score_norm(translit)` of the recovered plaintext**, so it stays on the project's canonical
scale and comparable to every ledger number.

## 3. Positive control, null, and pass/fail thresholds

All scores are `score_norm`; all recoveries are on **rune indices**, not the transliteration
string. 7 seeds minimum per construction; medians reported with min/max.

### G-EQ — equivalence (blocking, runs first)
`driftbeam(mode="keyskip1", max_free=0)` must equal `skipdecode.beam_decode` to
`|dscore| < 1e-9` with an identical plaintext-index vector, over >= 20 random
(ciphertext, keystream) cases at L in {60, 120, 400}, both signs. **A fail here voids the lane.**

### G-BASE — no regression
On the baseline `encipher_keyskip` construction, `driftbeam` must match the existing beam's
correct-key score within **0.15** and its rune recovery within **2 points**. Replicated at
`supp in {0.0, 0.4, 0.83, 1.0}`, L in {240, 400}. Plus L2's full-book control replicated:
**score >= -5.5 and recovery >= 0.90 at L = 12,956.**

### G-FIX — the point of the lane
With the **correct key** supplied, `driftbeam` must reach **score >= -5.5 AND rune recovery
>= 0.90** on every construction in L7-B's failure table, at L = 240 and L = 400, >= 7 seeds each:

| # | construction |
|---|---|
| 1–3 | `skip_by_two`, `supp in {0.5, 0.83, 1.0}` |
| 4–5 | `free_drift`, `q in {0.05, 0.10}` |
| 6–7 | `drift_at`, `n in {5, 10}` unrepresentable advances per 240 runes |
| 8 | two-draws-per-rejection (L7-B's `skip_by_two`; reported as its own row, plus a second, independent two-draws variant `coin_from_key` built here) |
| 9–10 | low-entropy pad, constant run `r in {16, 32}`, `supp = 1.0` |

PASS requires **all ten**. Any construction below either bar is reported as a FAIL row and the
gate verdict is FAIL. I will not move the bar after seeing the numbers; a bar change may only
appear as a dated addendum below, with its reason.

### G-FP — the failure mode of the fix itself
A **wrong key must stay in the noise band** under the most permissive mode. At each
permissiveness setting, >= **2,000** wrong keys are decoded and the full score distribution
(mean, median, sd, p99, max) reported, against the same statistic under `keyskip1`. Two nulls:

- **N-synth** — wrong `sha256_ctr` keys against a synthetic `encipher_keyskip` plant, L = 240.
- **N-real** — wrong `sha256_ctr` keys against segments of the **real 12,956-rune LP2 stream**
  (`round11/lib_numchannel.unsolved()`), L = 240. This is the null Phase 2 will actually face.

The published statistic is the **separation** `correct-key score - wrong-key p99` at each
setting, and the family-wise bar from `benchmark/null.threshold_for(n_trials)` recomputed for
the shifted null. If permissiveness lifts the wrong-key distribution into the English band, I
say so plainly and publish the tradeoff curve (permissiveness vs separation) instead of a fix.

### G-COST — the price, as a number
The score and recovery `permissive` loses relative to `keyskip1` **on the baseline
`encipher_keyskip` construction**, and the shift it causes in the wrong-key p99 — one number
each, published, because Phase 2 pays them on every decode.

### Speed
A full-book L = 12,956 decode must stay in single-digit seconds in `keyskip1` mode; the
permissive-mode figure is measured and published whatever it is.

---

## 4. What this lane will NOT claim

- It will not claim to cover "any rejection loop". It covers what `max_free` and `max_skip` say
  it covers, on 12 named constructions, with English pinned.
- It will not restate a decoder pass as evidence about LP2. Recovering a *planted* key says
  nothing about whether any real key exists.
- It will not report coverage without power (doctrine R2), and every row it writes carries the
  three conditionals of §Q4.
- No "exhausted", "closed" or "unsolvable" (doctrine R7). Bounds and reopening conditions only.

## 5. Outputs

`driftbeam.py` (+ self-tests), `test_driftbeam.py`, `RESULTS.md`, `out_eq.json`, `out_base.json`,
`out_fix.json`, `out_fp.json`, `out_cost.json`, `ledger.json`. Files written; **no `git commit`**
(the coordinator commits). Nothing outside `round19/I1/` is edited.

---

## Addendum, 2026-08-26 (a) — Kill condition A was evaluated first, as written, and did **not** stop the lane

Kill-A names `permissive, max_free = 2, lam = 0, max_skip = 8` as "the most permissive setting
reachable" and stops the lane if the correct key on `skip_by_two supp = 0.83` fails there. It was
evaluated before anything else was launched. Measured (L = 240, 7 seeds): median score
**-4.730**, comfortably over the -5.5 bar, median rune recovery **13.3 %**. The literal
conjunction therefore fails.

**The lane did not stop, and the reason is a measurement rather than a preference:** the same
`lam = 0` setting also fails on the **baseline** construction, `encipher_keyskip` at
`supp = 0.0` — a ciphertext containing *no key skips at all* — which decodes at
**-4.617 / 17.1 % recovery**. A control that fails on the one construction the relation
represents *exactly* is not measuring the transition relation; it is measuring the absence of
regularisation. At `lam = 0` the beam is handed a free key advance at every rune and spends it
buying quadgram score, which is exactly the G-FP failure mode this document anticipates — at
`lam = 0` that failure is total, which is why the score stays high while recovery collapses.

Kill-A as written therefore asks "is the relation expressive enough?" with an instrument that
cannot answer it. The expressiveness question is answered instead by `mode="keyskip2"`, which is
*exact* for `skip_by_two` and which recovers it at **-4.285 / 100.0 %**. That is the intended
content of Kill-A and it says GO.

**No gate threshold is changed by this addendum.** G-EQ, G-BASE, G-FIX, G-FP and G-COST stand
exactly as pre-registered above, and every `lam = 0` row is reported in full in `RESULTS.md` as
measured — it is one of the lane's more useful findings, not an embarrassment to be hidden.
