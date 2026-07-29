# Final draft — CicadaSolvers / r/codes / r/cicada

_Post under your own name. Tone: humble, skeptical, negative-results-first — this
audience is expert and rightly allergic to overclaiming. Do NOT claim a solve.
Supersedes the earlier COMMUNITY-POST.md (adds the assumption-stack red-team and
the label-free transcription audit)._

---

**Title:** LP2: a complete, reproducible map of what's ruled out — plus a
transcription check that's independent of the transcription itself

I'm **not** claiming a solve — the opposite. After a long, systematic run at the
unsolved Liber Primus pages (LP2, onion7 `0`–`55`) I want to hand the community
two things I think are genuinely useful and save people from re-running dead ends.
Everything is code you can check. Please poke holes in it.

**Repo:** https://github.com/Dukotah/cicada3301 →
`liber-primus/ELIMINATION-LEDGER.md` and `liber-primus/analysis/independent-read/`

## 1. A complete elimination ledger (the main gift)

`ELIMINATION-LEDGER.md` is a single reproducible record of everything tried and
*why each was eliminated*, so nobody re-runs a decade of dead ends. It now
includes a red-team of the **assumptions** the whole effort rests on, not just
the ciphertext. Eight load-bearing premises, each attacked directly, each held:

- key-guessing / running keys (112+ named keytexts, incl. thematic esoterica)
- reading order (reversed / per-page / boustrophedon)
- hidden subsequence / acrostic (first/last of line, word, page; prime positions)
- 1-bit-per-rune channel (parity / value threshold)
- transcription integrity (see #2)
- fixed-function autokey (crib-drag that *recovers* the function from an opener)
- **plaintext language** — Latin tested with a Caesar+Newton model; null, and
  note the two load-bearing exclusions (flat IoC, the doublet deficit) are
  **language-independent**, so "maybe it's Latin/other" can't rescue a solve.
- **book cipher** — runes as pointers into Cicada's known books (KJV, Mabinogion,
  Paradise Lost, Blake); every natural pointer scheme yields word-salad, not prose.

**Prior art, credited:** the doublet *observation* (unsolved pages run well below
the ~3.45% random doublet rate) is already on the Uncovering Cicada wiki, read
there as "points to autokey." What I'm adding is the *mechanistic* consequence —
any plaintext-independent additive keystream (English, non-English, numeric pad)
injects those doublets, so the whole "guess the running key" family is excluded,
not merely unlucky — plus the corpus-wide/period and combiner/homophonic closures.

## 2. A transcription check independent of the labels (the novel method)

Everyone knows the community transcriptions share one origin (rtkd/iddqd), so
"they all agree" proves consensus, not correctness — and whole-page AI vision
hallucinates, so it can't produce an independent read. A glyph classifier can,
but the usual one is *trained on the canonical labels*, so agreeing with it is
circular.

So I did it label-free: cluster ~10.7k segmented glyph bitmaps **by shape alone,
canon never shown**, then compare the emergent partition to canon. Result: canon
**is** the natural visual partition (ARI 0.75, homogeneity rising to 0.98 as
clusters grow) — the first confirmation independent of the labels. The only
visually fragile family is `ᚩ/ᚪ/ᚫ` (the historic page-24:172 dispute), and it's
10.7% of the corpus and cryptographically inert (even a worst-case whole-family
mislabel can't move IoC toward English). Code + figures in
`analysis/independent-read/`.

## The honest bottom line

I could not break LP2, and the map above is why: on the published ciphertext the
internal attack surface appears closed. What survives is unbounded (multi-rune
feedback; a book outside Cicada's known refs) or external (the lost AN-END onion
preimage; a future release). If any of this is already documented somewhere I
missed, or you can break one of the "sealed" fronts, please say so — I'd rather
be corrected here than be wrong quietly.
