# P4 — Doublet Forensics (Campaign XV)

- **probe_id:** P4-doublet-forensics
- **verdict:** null-closed
- **headline_number:** 86 tolerated doublets; every distribution test p ≥ 0.24 (min over all 10 structure tests = 0.0116, a mild prime-position *deficit*, ≫ the 0.001 gate); best decode score_norm = −6.45 (gate −5.2).
- **falsifiable_signal:** distribution test p < 0.001 (positions/values/gaps non-uniform) = HIDDEN STRUCTURE, OR any decode score_norm > −5.2 = SIDE-CHANNEL MESSAGE.
- **signal_fired:** false
- **synthetic_validation:** n/a — pure measurement (no decode succeeded; scorer itself is the validated trust anchor via `tests/validate.py`, which reproduces every known solve).
- **method:** Isolated the 86 survivor doublets (positions where `stream[i]==stream[i-1]`) from the 12,956-rune LP2 body stream. (a) KS of positions vs Uniform(0,1) and of the 85 inter-doublet gaps vs a MLE-fit Geometric, plus binned χ² of gaps vs geometric. (b) χ² of the 86 doubled values vs uniform over 29 runes. (c) binomial enrichment of doublet positions at word-starts, line-starts, F-rune(interrupter) as/adjacent-to the doubled value, and χ² of doublets-per-page vs page sizes. (d) gaps/positions/values mod {29,26,24,13,5,7} read as rune indices, quadgram-scored. (e) the 86 doubled runes read in order through identity / Atbash / all 29 Caesar shifts / 29 reflections, quadgram-scored. (f) doublet positions vs primes (binomial) and gaps rank-correlated (Spearman) with the pp49-51 256-byte payload and its first-differences. scipy 1.17.1 for KS/χ²/binomtest/spearman.
- **script_path:** analysis/campaign15/P4-doublet-forensics.py
- **reproduce_cmd:** `PYTHONUTF8=1 python analysis/campaign15/P4-doublet-forensics.py`

## one_paragraph

The soft no-repeat filter tolerates exactly **86 doublets** (0.664%, reproducing the ledger's 0.66%), and those survivors carry **no structure whatsoever**. Their positions are uniform (KS D=0.109, p=0.24); the 85 inter-doublet gaps are textbook geometric (KS p=0.67, binned χ² p=0.96, mean 150.8 ≈ 1/p̂ for p̂=0.0066); the 86 doubled values are uniform over the 29 runes (χ²=25.95, df=28, p=0.58); and doublets are not enriched at word boundaries (p=0.32), line starts (p=0.80), on the F-interrupter (4/86, p=0.54), adjacent to F (p=0.83), or on any page beyond its size (χ² p=0.31). Reading gaps/positions/values as rune indices (best −6.45) or the 86 doubled runes as an 86-char string through identity/Atbash/all shifts/reflections (best −6.85) yields only noise — both far below the −5.2 side-channel threshold and even below the ~−6.0 random floor. Correlation with the pp49-51 payload as a gap table is null (Spearman ρ=+0.043, p=0.70). The single sub-0.05 result — doublet positions landing on primes 3/86 vs 10.2 expected (p=0.012) — is a *deficit*, is nowhere near the 0.001 gate, and is unremarkable as the extreme of 10 tests. **The gate does not fire.** Positions uniform, values uniform, gaps geometric, no decode: the survivors are i.i.d. accidents, which pins the filter as **memoryless rejection-sampling** — a quantitative refinement of Campaign XI. The doublets are not a fingerprint or a hidden channel; they are exactly the tail the Campaign-XI ~83%-suppression model predicts, and they carry zero information about the plaintext.

## ledger_row

| Attack | Verdict | Why | Where |
|---|---|---|---|
| **Doublet survivors as fingerprint / side-channel** (positions, values, gaps, boundary/F/page/prime cross-refs, mod-reads, value-string decode, payload gap-table) | ❌ dead | 86 survivors are i.i.d.: positions uniform (KS p=0.24), gaps geometric (KS p=0.67 / χ² p=0.96), values uniform (χ² p=0.58), no boundary/F/prime enrichment (all p≥0.01, none <0.001), all decodes ≤ −6.45 (gate −5.2). Filter = memoryless rejection-sampling, refining Campaign XI | Campaign XV P4 `analysis/campaign15/P4-doublet-forensics.py` |
