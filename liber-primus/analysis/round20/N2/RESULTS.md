# N2 — A-03 Haplography Falsifier — RESULTS

**Verdict: NO-ERROR-FOUND.** ~20 doublet-site haplographic merges do NOT reopen autokey.
The positive difference-diagonal refutation (`cv=0.061`) is hardened against its cheapest
ledger reopener.

## The question (the one live autokey reopener)

Autokey is *positively* refuted, not merely null: under ciphertext-autokey
`c_i = p_i + c_{i-1} + K`, the adjacency matrix `M[a,b]` depends only on `d=(b-a) mod 29`,
so each nonzero difference-diagonal equals a distinct plaintext-rune frequency → the 28
nonzero diagonals would be LUMPY (`cv~1.0`). Observed LP2: they are FLAT
(`cv=0.061`, chi 35.4 < crit≈40). That flatness excludes autokey.

Round 16 A-03 checked the *rate* channel (`K_bound=26 < K_needed=93`). This lane checks the
sharper *structure* channel the campaign plan named: could ~20 merges restore the diagonal
lumpiness itself? Different test, not a re-run.

## Positive control (instrument validated — silence is trustworthy)

Planted a real ciphertext-autokey stream with plaintext drawn from English (Pride &
Prejudice) via Gematria Primus (rune-unigram cv=0.849, genuinely lumpy):

| stream | cv (28 nonzero diagonals) |
|---|---|
| planted AUTOKEY | **0.842** (lumpy, chi=6676) |
| autokey after K=20 merges | **0.842** |
| planted ANTI-REPEAT (fitted LP2 model) | 0.059 (flat, chi=33) |
| anti-repeat after K=20 merges | 0.059 |
| **separation (autokey−antirepeat, merged)** | **0.784** (need ≥0.15) |

The cv statistic cleanly separates autokey from anti-repeat *through* K=20 haplography.
**POSITIVE CONTROL PASSES.** (First control run used LP2's own flat unigrams as plaintext
and failed correctly at cv=0.077 — see PREREG addendum; corrected to real lumpy plaintext.)

## The decisive structural fact

A physical haplography reversal = re-inserting a duplicated rune (`...a,x,b...` →
`...a,x,x,b...`). Its diagonal deltas are: the `x→b` edge is removed (−1 on d=b−x) and
re-added after the 2nd x (+1 on d=b−x) → net zero on every nonzero diagonal; the only net
change is **+1 on d=0**. Therefore **every physical merge touches ONLY the d=0 diagonal; the
28 nonzero diagonals that carry the autokey signature are literally invariant.** The
diagnostic `cv` cannot move at all: physical cv stays 0.0608 for all K.

## Adversarial upper bound (super-physical)

To bound even non-physical scenarios, a greedy adversary allowed to add +1 to *any* diagonal
it chooses (strictly stronger than physical re-insertion) reaches only:

- **cv = 0.066 at K=20** (autokey band bar = 0.40 → **6.1× below**), never reaching 0.40
  through K=40.
- (The abstract adversary's chi crosses 40 near K=16 as a mechanical +1-piling artifact
  while cv stays 0.066; autokey chi is 6676. Adjudication is on the control-calibrated cv
  bars — see PREREG addendum. This changes no frozen threshold.)

## The three conditionals of this negative

1. **Key space / mechanism:** ciphertext-autokey `c_i=p_i+c_{i-1}+K` (all K) and its
   plaintext-autokey variant — the exact construction the diagonal test discriminates.
2. **Decoder relation:** N/A — this is a ciphertext-structure test (cv of difference
   diagonals), not a decode; register-blind.
3. **Adjudicator register:** language-agnostic. Autokey diagonal lumpiness is register-
   independent (any natural-language plaintext has lumpy letter freqs), so a Latin/OE/Welsh
   autokey would be caught identically.

## Coverage / power

- **Coverage:** the full physical haplography-merge space (K = 1..20 and beyond) is covered
  by a closed-form invariance proof, not a sample — 100% of the physical scenario. The
  super-physical adversary (free diagonal choice) is covered K=1..40.
- **Power:** measured 1.00 — positive control recovers autokey through K=20 merges with cv
  separation 0.784 (bar 0.15); the cv statistic distinguishes autokey (0.84) from
  anti-repeat (0.06) at zero overlap.

## Reopening condition (doctrine R7 — bounds, not verdicts)

This closes the *cv/diagonal-lumpiness* haplography channel. It would reopen only if a merge
mechanism existed that alters the 28 nonzero diagonals (not just d=0) — e.g. correlated
multi-rune transcription errors that systematically re-route adjacencies onto specific
diagonals. No such mechanism is proposed in the ledger, and it would contradict the
image-vs-canon audit (Round 16: the surplus is d=0 doublets, z=1.83, not off-diagonal
re-routing).

Files: `PREREG.md`, `n2_haplography_falsifier.py`, `results.json`, `RESULTS.md`.
