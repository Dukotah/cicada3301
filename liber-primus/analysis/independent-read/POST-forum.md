# Forum draft — r/codes / CicadaSolvers (peer-credit, humble, prior-art-aware)

**Title:** LP2: a label-free transcription audit + a mechanistic tightening of the doublet result (negative results, reproducible)

---

Not a solve. Posting to (a) contribute one method I haven't seen done here and (b) save people effort by documenting what a large automated sweep ruled out. Code and an elimination ledger are public [link]; corrections welcome — I'd rather be shown wrong here than be wrong quietly.

**Starting from what's already known.** The wiki's frequency analysis already notes the unsolved pages run a doublet rate well below the ~3.45% you'd expect from random, and reads it as pointing toward an autokey/autoclave. I'm building on that, not claiming it.

**1. Tightening the doublet result.** Rather than "suggests autokey," I characterized the deficit directly: it's ~0.66% vs ~3.45% expected, uniform across all 29 runes, diagonal-only, memoryless, with no off-diagonal, periodic, or inter-page structure. The consequence is stronger than "probably autokey" — *any* plaintext-independent keystream added to the text (an English book, a non-English text, a raw numeric pad, prime digits) injects ~3.45% doublets by construction. They're absent. So the entire "guess the running key" family isn't unlucky, it's mechanically excluded. Corpus-wide coincidence scans (all lags to 6478) and long-period column IoC (periods to 2000) are flat; additive autokey and many-to-few homophonic were simulated and don't reproduce the flat IoC either. What survives is OTP-class / non-additive feedback — no internal purchase from the ciphertext alone.

**2. The part I think is actually new: a label-free transcription audit.** We all know independent verification of the runes is hard, and that whole-page AI vision fails badly (it hallucinates rune counts). Both true — I reproduced the vision failure (0.145 alignment, useless). But there's a subtler issue: a glyph classifier people reach for to "verify" the transcription is typically *trained on that transcription's labels*, so agreeing with it is circular.

So I did it without labels. Take ~10,700 segmented glyph bitmaps, cluster them by shape alone (canon never shown), then compare the emergent partition to the canonical transcription:
- K=29 unsupervised vs canon: ARI 0.745, homogeneity 0.879 → 0.983 as K grows. Canon's partition *is* the natural visual partition — no gross swap or merge.
- Every near-identical family is self-consistent (R/W, M/D, N/I, B/E all ARI 0.98–0.99) *except one*: the ᚩ/ᚪ/ᚫ (O/A/AE) branch-family — the same family behind long-running individual-glyph disputes. Its class means are genuinely distinct (branch angle), so canon is self-consistent, but it's the one visually fragile locus.
- Cryptographic bound: that family is 10.7% of the corpus, and even a worst-case *whole-family* mislabel only moves IoC·29 1.00→1.14 and doublet 0.68%→1.46% — nowhere near English (1.73 / 3.4%). So it's a transcription-confidence matter, not a hidden decryption.

**Net:** this is the first transcription check I know of that's independent of the labels themselves, and it says the canonical read is sound off the one branch-family, which can't be hiding the answer regardless. It doesn't move us toward a solve — it removes "maybe we're all attacking a typo" as an excuse and points the remaining fragility at a specific, bounded place.

Everything's reproducible [link to `analysis/independent-read/`]. If any of this is already documented somewhere I missed, tell me and I'll cite it.
