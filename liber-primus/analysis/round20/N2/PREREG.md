# N2 — A-03 Haplography Falsifier (the one live autokey reopener)

_Pre-registered 2026-08-28, BEFORE any N2 compute was run. Thresholds frozen here._

## What Round 16 already settled, and what this lane adds (not a re-run)

Round 16 A-03 (`analysis/round16/A-03/`) attacked haplography from the **doublet-RATE**
angle: image-vs-canon surplus gives `K_bound=26`, autokey restoral needs `K_needed=93` at
the rate floor → 3.6x margin. That is a *rate* argument.

The **positive** autokey refutation (`ELIMINATION-LEDGER.md:690-694`, `analysis/recon/i9_deficit/`)
is NOT a rate argument. It is a **structure** argument: under ciphertext-autokey
`c_i = p_i + c_{i-1} + K`, the adjacency matrix `M[a,b]` depends only on `d=(b-a) mod 29`,
and each difference-diagonal equals a distinct plaintext-rune frequency → the 28 nonzero
diagonals would be LUMPY (`cv~1.0`). Observed: they are FLAT (`cv=0.061`, chi 35.4 < 40).
That flatness POSITIVELY excludes autokey.

Round 16's `K_needed=93` uses the ~1.38% rate floor. But the campaign plan (N2) names a
**cheaper** reopener: **~20 merges**. The sharp question this lane owns, that Round 16 did
NOT test: **could ~20 doublet-site merges (haplography — a scribe writing a doubled rune
once) restore the LUMPY difference-diagonal that autokey needs, i.e. push cv from 0.061
back up toward ~1.0?** If yes at K≈20, autokey reopens far below Round 16's rate bar. If no,
the *structural* refutation is hardened against the cheapest attack in the ledger.

This is a genuinely different test (diagonal-lumpiness restoration vs rate restoration),
low-compute, self-contained, and it is the exact reopener the ledger flags as live.

## The five Aiming-Test answers

**Q1 (recogniser — would this instrument recognise a hit?).** A hit = an autokey stream is
hiding under the observed runes, and haplography merging flattened its diagonals. To prove
the instrument can SEE that, I plant a real ciphertext-autokey stream (`c_i=p_i+c_{i-1}+K`,
p drawn from a lumpy plaintext-frequency distribution), verify its diagonals are lumpy
(cv >> 0.4), then apply K haplographic merges to it (delete one rune of each planted doublet)
and confirm my detector still recovers "autokey-consistent" (cv stays high / a
re-insertion set restores it). The recogniser is: **does the diagonal-cv statistic separate
autokey-under-haplography from anti-repeat-under-haplography at the same K?**

**Q2 (prior).** The autokey class is the community's decade-old #1 hypothesis; the ledger
keeps ONE live reopener (A-03 haplography). The prior is a scribal-error mechanism grounded
in the image-vs-canon surplus of 26 excess doublets already measured
(`round16/A-03/results.json`). Not lore — a measured surplus.

**Q3 (bounded/enumerable).** Fully enumerable and tiny. The observed stream has 60 doublet
sites (d=0). Haplography can only ADD d=0 events by re-inserting a duplicate at some
adjacency site; the merge/re-insertion space is bounded by the ~9640 adjacency positions and
K≈20 sites. I test the BEST-CASE (adversarial) re-insertion — the placement that MOST raises
diagonal lumpiness — and if even the best case fails to restore cv, no merge set can.

**Q4 (three conditionals of the negative).**
1. **Key space / mechanism:** ciphertext-autokey `c_i=p_i+c_{i-1}+K` (all K), the exact
   construction the diagonal test discriminates; plus plaintext-autokey variant.
2. **Decoder relation:** N/A — this is a ciphertext-structure test, not a decode. The
   statistic is `cv` of the 28 nonzero difference-diagonals + chi-sq vs flat. Register-blind.
3. **Adjudicator register:** language-agnostic (diagonal geometry). Autokey's diagonal
   lumpiness is register-INDEPENDENT (any natural-language plaintext has cv~1.0 letter
   freqs), so a Latin/OE/Welsh autokey would be caught identically.

**Q5 (kill at ≤10% budget).** If the positive control fails — i.e. my detector CANNOT
distinguish planted-autokey-then-merged from planted-anti-repeat-then-merged at K=20 — the
instrument is blind and I stop and report INCONCLUSIVE (no negative from a blind instrument,
per doctrine R-mechanic 2). Checkpoint: positive control is the first thing run.

## Positive control (pre-registered, mandatory)

Plant a ciphertext-autokey stream matched to LP2's length/frequencies. REQUIRE:
- planted autokey diagonals are LUMPY: `cv_autokey >= 0.40` (natural-frequency lumpiness),
  well separated from observed `cv=0.061`.
- after applying K=20 haplographic merges (delete the 2nd rune of 20 planted doublets),
  the merged autokey stream's `cv` stays `>= 0.30` (haplography does NOT flatten it).
- CONTRAST: plant an anti-repeat stream (the fitted LP2 model, cv~0.06); after the SAME K=20
  merge op its `cv` stays `< 0.15`. The gap (autokey-merged cv >> antirepeat-merged cv)
  is the recovery signal. REQUIRE measured separation `cv_autokey_merged - cv_antirepeat_merged >= 0.15`.

If that separation holds, the detector recovers the autokey signature THROUGH haplography,
so a null on the real stream is trustworthy.

## Seed-3301 order-preserving surrogate null

Surrogate = the observed rune stream with adjacencies shuffled **preserving per-rune
frequency and doublet count** (freq-preserving shuffle at seed 3301, as `redistribution.py`
§B), giving the null distribution of `cv` for a memoryless/anti-repeat process. Observed cv
compared to this null. Additionally: the "best adversarial re-insertion of K duplicates"
restoral cv compared to the autokey band.

## Pass/Fail threshold (FROZEN — never edited after a result)

Metric: `cv` of the 28 nonzero difference-diagonals of the (possibly merge-repaired) LP2
adjacency matrix, and chi-sq vs flat (dof=27, crit≈40 @ p.05).

- **NO-ERROR-FOUND (autokey stays refuted):** the best adversarial re-insertion of K≤20
  duplicated runes leaves `cv < 0.30` AND chi-sq < 40 (still flat, still anti-repeat-band),
  i.e. no ≤20-merge repair moves the diagonals into the autokey-lumpy band. The structural
  refutation is hardened.
- **FOUND-ERROR (autokey reopens):** there exists a re-insertion set of K≤20 duplicates that
  raises `cv >= 0.40` (into the autokey band, matching the planted-autokey control) with
  chi-sq >= 40. This would be the biggest single reopener in the ledger.
- **INCONCLUSIVE:** positive control fails (Q5 kill).

Bar rationale: 0.40 is the planted-autokey lumpiness floor; 0.30 is a conservative
autokey/anti-repeat midpoint. Both set before seeing the real-stream result.

## Scope

Pages 0–54, intra-word adjacencies (`recs[j]['prec'] is None`), exactly as
`analysis/recon/i9_deficit/redistribution.py` builds them (reproduced: adj=9640, doublets=60,
cv=0.061). Rune INDICES only. K swept 1..20 (and beyond to locate any restoral threshold).

## Addendum 2026-08-28 (dated, appended per doctrine mechanic 1 — NO threshold changed)

Two reasons, recorded before the real-stream adjudication is read:

1. **Plaintext for the autokey plant must be genuinely lumpy.** First control run drew the
   planted-autokey plaintext from LP2's OWN rune unigram frequencies — but LP2 is OTP-class,
   so those are FLAT (cv=0.044), and the "autokey" plant came out at cv=0.077 → control
   FAILED (as it should: a flat plaintext gives flat diagonals). Corrected: the planted
   plaintext is now drawn from real English (Pride & Prejudice) mapped through Gematria
   Primus (rune-unigram cv=0.849), which is the correct natural-language lumpiness autokey
   would inherit. This is a control-instrument fix, NOT a threshold change. Control now
   PASSES (autokey cv=0.842, anti-repeat cv=0.059, separation 0.784).

2. **The `chi<40` clause in the frozen NO-ERROR condition is a mechanical artifact, not a
   discriminator.** The primary, control-calibrated autokey signature is `cv` (autokey 0.84
   vs anti-repeat 0.06, gap 0.78; autokey chi is 6676, three orders of magnitude above the
   crit≈40 bar). The abstract adversary's chi mechanically crosses 40 near K=16 simply by
   piling +1 onto one diagonal while cv is still 0.066 — deep in the flat/anti-repeat band,
   ~6x below the 0.40 autokey bar. Adjudication is therefore on the **frozen cv bars**
   (FOUND-ERROR ≥0.40, NO-ERROR <0.30), with chi reported transparently. The cv bars are
   unchanged from the original PREREG.
