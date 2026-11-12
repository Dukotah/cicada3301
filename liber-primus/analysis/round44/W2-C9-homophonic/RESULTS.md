# W2-C9 — D-03 homophonic-downward screen — RESULTS

_Dated 2026-11-11. PREREG.md frozen 2026-11-09 (sha256 stamped in run.log before first
execution); one dated addendum appended after the plant phase and BEFORE any real-stream
run (re-stamped 16:10:42). X1 ruled the addendum **acceptable-as-narrowed** (REPORT-WAVE2.md
§C9) with a binding condition honored in `ledger_rows.json` (see §5)._

## 0. Headline

**NEGATIVE, detection-conditioned, clean.** All 49 pre-registered cells (22 annealed
k=5..26 + 27 natural partitions) × full 2,001-replicate envelope (1 real + 1,000 family-A
shuffles + 1,000 family-B doublet-matched filtered-uniform): **0 crossers** at the fixed
bar (T_real > 999th order statistic of BOTH families). The real LP2 stream shows no
held-out class-bigram structure under any surjective 29→k partition this instrument can
reach, while the planted homophonic shapes light up at ≈ +0.30–0.37 bits/bigram —
roughly 170× further above the null than the best real cell gets.

## 1. Verdict mechanism and plant gate (the narrowed claim)

Per the dated addendum (PREREG §ADDENDUM) and X1's ruling: the verdict mechanism is the
**envelope test on T (detection)**, not partition reconstruction.

| plant | shape | k | T | env100_max | margin (bits/bigram) | ARI | clauses |
|---|---|---|---|---|---|---|---|
| PC1 | EN uniform-homophone | 15 | 0.3047 | −0.0196 | +0.324 (≈16× null spread) | 0.326 | detection PASS, recovery FAIL (<0.5) |
| PC2 | EN repeat-avoiding (the LP2-matched shape) | 15 | 0.3270 | −0.0193 | +0.346 | 0.513 | BOTH PASS |
| PC3 | LATIN uniform-homophone | 12 | 0.2976 | −0.0106 | +0.308 | 0.761 | BOTH PASS |
| PC4 (supplementary, addendum plant, thresholds untouched) | flat-IoC LP2-matched | 19 | 0.3709 | −0.0360 | +0.407 | 0.711 | detection PASS |

Detection-level power ≈ 1 for every planted shape, including PC2 — the repeat-avoiding
construction that matches ALL measured LP2 statistics at once (IoC·N ≈ 1, lag-1-only
doublet deficit) and is the actual shape hunted. **Partition-RECOVERY power at
k15-uniform is NOT established (ARI 0.326)**; that limitation is carried verbatim in
`not_covered` per X1's binding condition. The negative claimed below is therefore: no
partition in the searched space produces DETECTABLE held-out bigram structure — not a
claim that the optimizer would have reconstructed the exact partition.

## 2. Envelope numbers vs null

2,001/2,001 replicate rows complete (`results/rows.jsonl`, one JSON row per replicate,
doctrine-R3 stats persisted; verdicts in `results/screen.json`). n_A = n_B = 1,000 at
every cell. s_keep (family-B doublet calibration) = 0.1933 against the real doublet
rate 0.006666.

- **Real T range**: annealed −0.0702 .. −0.0017 (best = k=5, T = −0.0017, train MI
  0.0096, R3: ioc_k 1.1135 / mds32 4 / zlib 0.358); natural −0.0488 .. +0.0018
  (best = prime_mod_9 and idx_mod_3 at +0.0018).
- **Closest approaches to the conjunction bar** (gap = max(bar_A, bar_B) − T_real):
  prime_mod_2 gap 0.0012; idx_mod_3 gap 0.0015; idx_mod_2 gap 0.0022; prime_mod_4
  gap 0.0027; vowel_consonant gap 0.0028. All other cells ≥ 0.0028; widest gap 0.0142
  (anneal_k26).
- **Single-family exceedances, disclosed**: 9 cells sit above ONE family's p999 bar but
  below the other's (largest: idx_mod_3 at +0.0018 vs bar_A +0.0008, under bar_B
  +0.0033; anneal_k10 at −0.0023 vs bar_A −0.0062, under bar_B +0.0027). Expected false
  single-family exceedances over 49 cells × 2 families at p999 ≈ 0.1; observing 9
  reflects the families' different spreads (family B's bar is the binding one in 8 of
  9), and none survives the pre-registered both-families conjunction. No cell crosses.
- Every margin above is ~2 orders of magnitude smaller than the plant detection margins
  (+0.31 to +0.41).

## 3. Coverage

Covered: the D-03-specified annealing search at the pre-registered bounded budget
(2 restarts × 2,500 proposals, identical on every replicate), surjective 29→k for
k = 5..26; the 27 frozen natural partitions (aetts, vowel/consonant, idx mod 2–13,
prime-value mod 2–13, confusable-glyph merge); both control families at N=1,000 each;
cross-validated train/test page split (even/odd), bigrams within pages only;
detection-level power measured ≈ 1 on three (plus one supplementary) planted shapes
spanning EN/LATIN registers and uniform / repeat-avoiding / flat-IoC homophone
selection.

Not covered (restating PREREG §8 + the addendum): EM optimizer arm; k outside 5..26;
variable-rate encodings; non-stationary (per-page/per-section) partitions;
keystream-driven homophone selection; plaintexts with no order-2 structure; trigram+
objectives; optimizer-unreachable partitions beyond the plant-measured power envelope;
**partition-recovery power NOT established at k15-uniform (ARI 0.33)**.

## 4. Deviations and incidents (full disclosure)

1. **PC1 recovery-clause failure → dated addendum → X1 ruling.** PC1 failed the ARI ≥ 0.5
   recovery clause (0.326) while passing detection at ≈16× the null spread. The addendum
   narrowing the claim to detection-conditioned was appended BEFORE the real screen,
   explicitly submitted itself to X1, and X1 ruled it acceptable-as-narrowed with the
   binding not_covered condition (honored verbatim). Bars, budgets and §5 thresholds were
   never touched.
2. **Mid-run death + resume.** The original fork-context Pool died at ~300/2,001 rows
   (leaked-semaphore interpreter shutdown, 2026-11-09 16:13). Resumed via
   `scripts/resume_screen.py`: spawn-context Pool, maxtasksperchild=40, per-row flush,
   driven in foreground slices with heartbeats to run.log. Resume is exact, not
   approximate: every null stream is generated from its own per-tag seed
   (A_i ← SEED_A+i, B_i ← SEED_B+i), independent of execution order, and completed tags
   are skipped by tag identity. No statistic, seed, budget or bar changed. The host
   additionally slept ~2 days mid-slice (16:59 2026-11-09 → 21:14 2026-11-11); rows
   persisted and the run completed 21:34:00 2026-11-11.
3. The wall-clock gap means the dates on PREREG (11-09) and RESULTS (11-11) straddle the
   sleep; chronology of stamps in run.log is intact and monotone.

## 5. Ledger row

One negative row drafted in `ledger_rows.json` (coordinator applies; this cell does NOT
modify LEDGER.json). Per X1's binding condition, its not_covered carries verbatim:
"partition-recovery power NOT established at k15-uniform (ARI 0.33)". No crossers, so
nothing is flagged-for-oracle; had any cell crossed, it would have been
FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, never certified here.

## 6. What this discharges

LEDGER.json **D-03** (open, `declared-closed-but-thin`): the search its text says "was
never coded" — anneal the partition, validate on synthetic homophonic ciphertext, score
against a 1,000-shuffle envelope, check generalisation to held-out pages, natural
partitions first — has now been coded and run exactly as specified, plus the D-02-lesson
second control family. The thin bigram-flatness inference (Campaign XIV P4, +0.81σ) is
replaced by a measured, plant-validated, detection-conditioned negative.

## Files

- `PREREG.md` (+ dated addendum), hash-stamped in `run.log` (opening, addendum, closing)
- `scripts/homophonic.py` — frozen glue (plants + screen)
- `scripts/resume_screen.py` — resume runner + finalizer (no statistic changes)
- `scripts/pc4_flat.py`, `results/pc4_flat.json` — supplementary plant
- `results/plants.json` — PC1/PC2/PC3 gate
- `results/rows.jsonl` — 2,001 replicate rows (R3 persistence)
- `results/screen.json` — 49-cell verdicts + real-stream per-k partitions/R3 stats
- `ledger_rows.json` — draft row for the coordinator
