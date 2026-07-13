# Independent (label-free) transcription audit — FINDINGS

_2026-07-13. The first read of the LP2 runes that **never sees the canonical
transcription** — closing the one hole every prior "verification" left open.
Artifacts in `analysis/independent-read/`: `cluster_read.py`, `family_probe.py`,
`oae_deepdive.py`, `crypto_exposure.py` + JSON/PNG outputs. Reproduce:
`PYTHONUTF8=1 python cluster_read.py && python family_probe.py && python oae_deepdive.py && python crypto_exposure.py`._

## Why this pass exists

Every prior transcription check shared a fatal dependency on the very thing it
claimed to verify:

- The **whole-page vision armada** (56 agents) confabulated — 0.145 alignment.
  It couldn't read dense pages at all, so it verified nothing.
- The **Campaign-V glyph classifier** (SVC, 99.2% CV) was **trained on canon
  labels** (`build_dataset.py`: _"Label by position from canon"_). A classifier
  agreeing with its own training target is **circular** — it proves the labels
  are learnable, not that they are correct. This was over-claimed as
  "independent corroboration."

So the community's real worry — _a systematic mis-read baked into the single
2017 rtkd/iddqd root that every transcription descends from_ — had never
actually been tested by an independent read. This pass tests it.

## Method

Take the 10,774 segmented glyph bitmaps (56×40) from the Campaign-V pipeline and
**cluster them by shape alone — canon is never shown to the clustering.** Then
compare the emergent visual partition against canon. A systematic mis-read leaves
one of two fingerprints, each detectable:

- **SPLIT / MERGE** (canon tears one shape into two runes, or fuses two shapes):
  the cluster×rune table stops being block-diagonal. → clustering + K-sweep.
- **MISLABEL** (right partition, wrong rune name): invisible to clustering;
  caught by rendering each class's mean shape and reading it against the
  Gematria Primus chart.

## Results

**1. No gross systematic mis-read.** Unsupervised K=29 clustering vs canon:
ARI 0.745, homogeneity 0.879, completeness 0.900. As K grows, homogeneity climbs
0.879 → 0.935 → 0.964 → 0.983 (K=29→87): same-rune glyphs reliably co-locate.
If canon had swapped or merged two common runes wholesale, homogeneity would
collapse. It doesn't. **Canon's partition is the natural visual partition.**

**2. Every "look-alike" family except one is perfectly self-consistent.**
Re-clustering each near-identical pair on its own, canon's split matches the
visual split: R/W ari 0.977, M/D 0.978, N/I 0.989, B/E 0.995. Canon separates
these exactly along the visual grain.

**3. One fragile locus, and it is the historically-known one.** The `ᚩ/ᚪ/ᚫ`
triad (O / A / AE) — the exact family of the decade-old page-24:172 dispute —
is the only family where an unsupervised read diverges from canon. Its three
class **mean shapes are genuinely distinct** (branch-angle differs, verified by
eye — see `oae_meanshapes.png`), so canon *is* applying a consistent, reproducible
rule; but the distinction is subtle enough that crude clustering can't reproduce
it (the trained SVC can — that's what the extra features buy). Direct inspection
of every unsupervised-vs-canon disagreement (`oae_mismatch.png`) shows **no
blatant single-glyph error** — all disagreements are within the F/branch family,
plus a few known segmentation-artifact outliers.

**4. It cannot unlock the puzzle anyway.** The `ᚩ/ᚪ/ᚫ` family is 10.70% of the
corpus (1406 / 13136 runes). Even the maximum-damage hypothesis — the *entire*
family systematically mislabeled — moves the statistics only from IoC·29 1.00 →
1.14 and doublet 0.68% → 1.46%, nowhere near English (1.73 / 3.4%). The stream is
OTP-flat *off* this family and stays flat under family collapse. Resolving the
ambiguity is a **transcription-confidence refinement, not a decryption unlock.**

## Verdict

The canonical LP2 transcription now has its **first genuinely independent
confirmation**: a read that never saw canon reproduces canon's partition, with
divergence confined to a single subtle branch-angle family that (a) canon still
handles self-consistently and (b) is cryptographically incapable of hiding the
solution. The "systematic mis-read propagated from the 2017 root" hypothesis is
**effectively closed** — the strongest form of it (gross swap/merge) is refuted
outright; the weakest (a few borderline O/A/AE calls) is real but bounded and
inert.

**What is genuinely novel / publishable here:** the label-free audit method
itself (nobody in the community has separated the read from the labels), the
result that canon = the natural visual partition, and the exact localization +
cryptographic bounding of the one fragile family. This does not solve LP2 — but
it removes the last excuse that a transcription error was hiding the answer,
which sharpens the standing OTP verdict rather than weakening it.

## Honest limits

Clustering runs on the Campaign-V segmentation, which itself descends from the
relikd images (the hash-verified onion7 master) — so this is independent of the
canonical *labels* but not of the *segmentation geometry*. It cannot detect an
error that is simultaneously a segmentation error and a label error at the same
position. And it is a shape-statistics argument, not a runologist's reading; the
`ᚩ/ᚪ/ᚫ` individual calls remain, as ever, a matter for a human expert on the
crisp masters.
