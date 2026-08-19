# FRONT D2 — RED-TEAM the load-bearing measurement/counting. VERDICT: NO-ERROR-FOUND

Independent recomputation of every load-bearing LP2 statistic from the raw runes.
Positive control passed first (planted English recovered: score −4.34 vs shuffled
noise −6.60, jump +2.26; CONTROL_OK=True). Trust anchor `tests/validate.py` passes.

## Independent recomputation vs repo's claimed values

| statistic | repo claim | my independent recompute | match |
|---|---|---|---|
| unsolved rune count n | 12,956 | 12,956 | ✓ exact |
| doublet rate | 0.664% | 0.664% (flattened) | ✓ |
| IoC·N | 1.000 | 0.9999 | ✓ |
| Shannon entropy | 4.857 bits | 4.8565 bits | ✓ |
| doublet COUNT | (86) | 86 | ✓ |
| p* period bound | ≈400 | 400 (reproduced in B4 G2) | ✓ |
| G3 doublet floor min_d Pdp(d) | >0.664% (≈1.5%) | 1.38%–1.83% over 4 corpora | ✓ |

Every headline number reproduces from raw runes with independent code (not just the
repo's own functions). B4's identifiability battery (G1–G5) also re-runs clean.

## The four specific miscount hypotheses — all REFUTED

**1. Are page/segment JOINS double-counting or creating false doublets?**
NO. Doublet rate computed on the flattened stream (with cross-page adjacency) =
0.664% over 12,955 pairs. Recomputed PER-PAGE (no cross-page adjacency) = 0.667%
over 12,901 pairs. The 54 cross-page join pairs contain **0** doublets. The join
convention changes the rate by 0.003 pp — nil. Not an artifact.

**2. Are the F-rune INTERRUPTERS wrongly included/excluded?**
Interrupters ARE included in the stream (458 F-runes, 3.54%). Stripping them
per-page RAISES the doublet rate to 0.755% and IoC·N to 1.036 — the anomaly
persists and actually strengthens slightly. So the deficit is intrinsic, not an
interrupter-padding artifact (this independently re-confirms ledger H1). Whether
interrupters are in or out, the verdict stands.

**3. Are SOLVED pages leaking into the "unsolved" stream?**
NO. The stream is `pages[:-2]` = pages 0–54; pages 55–56 (AN END, PARABLE) are
excluded. Per-page IoC·N for ALL of 0–54 sits at ~0.92–1.10 (flat/ciphertext-like);
none shows English-plaintext IoC·N (~1.7). The excluded PARABLE page 56 correctly
reads IoC·N=1.819 (English). No solved plaintext page leaks in; scope is correct.

**4. Is the p*≈400 period bound wrong or misused?**
NO. p*≈400 is an EMPIRICALLY-CALIBRATED detection floor: the smallest periodic-key
period whose ciphertext IoC·N can no longer be reliably (>95% of trials)
distinguished from the flat null at N=12,956. Reproduced exactly (period 400 → 76.7%
detected, below the 95% bar). Its theory check IoC·N(k) ≈ 1 + 0.8147/k matches the
simulation. Crucially it is used CORRECTLY and CONSERVATIVELY: Round 10 already used
it to RETRACT the over-claim "flat IoC forces a full-length key" (p* is a lower bound
on undetectable period, not a proof of full length). No over-reach here.

## The G3 doublet-floor theorem — direction and normalisation are correct

The exclusion of the entire plaintext-INDEPENDENT-key class rests on
P(dbl) = Σ_d Pdp(d)·Pdk(−d) ≥ min_d Pdp(d). I verified: since Pdk is a probability
vector, the minimising key puts all difference-mass on argmin_d Pdp(d), giving the
floor = min_d Pdp(d) exactly. Direction is correct (independent key CANNOT go below
this). Least-favourable large-corpus floor = 1.38% (KJV), 2.08× the observed 0.664%.
To reach 0.664% via an independent key the PLAINTEXT itself must be pre-suppressed
(some consecutive difference ≤0.664% rare) — which no natural language is (floor
≈1.4–1.8%). That leaves only an output-aware filter OR a non-linguistic pre-suppressed
plaintext, both already inside the repo's stated ciphertext-indistinguishability
verdict class. No mis-normalisation.

## Bottom line

No statistic is wrong, mis-normalised, or computed on the wrong stream. The
interrupter-inclusion, page-join, solved-page-leakage, and period-bound concerns are
all measured and refuted. Unlike Round 10's B4 (which DID find a real over-claim in
the *interpretation* of flat IoC), this red-team finds the numbers AND their current
usage sound. No exclusion class is reopened by a corrected statistic.

**VERDICT: NO-ERROR-FOUND.**
