This is a cryptanalysis reasoning task. No tools or skills apply. Here is my critical assessment.

---

# Completeness critique: what genuinely remains untested on LP2 pp.0–55

First, the honest framing. Your null result (0 hits, best −6.23 vs English ~−4.2) across running-key, Vigenere-with-solved-vocab, and the prime/totient/Fibonacci keystream families is strong evidence for one thing: **the unsolved pages are not a memoryless polyalphabetic stream over a keystream you can guess.** That is exactly what the community consensus says too. So the question is not "which key did I miss" — it's "which *structural* modality have I not modeled at all." Sorting by that:

---

## RULED OUT by the doublet/flatness evidence (do not run)

These are dead on arrival given your own stated fingerprint (flat monographics, uniform IoC, sub-chance doublet deficit, uniform first-differences with a single near-zero hole at delta=0):

1. **Any additional memoryless keystream (more primes, more thematic Vigenere keys, more running-key books).** The doublet deficit cannot be produced by a memoryless additive/substitution stream — such streams reproduce the *plaintext's* doublet rate scrambled to roughly chance, never *below* chance. You have already burned enormous compute here; the marginal book or keyword has near-zero prior. Stop adding running-key sources. This is the clearest case of diminishing returns in your whole program.

2. **Plain columnar / single transposition as the ONLY layer.** Pure transposition is transparent to monographic stats — it would leave the doublet rate at the plaintext's natural ~3.45%, not 0.66%. Since your doublet rate is *suppressed*, a transposition-only hypothesis is falsified directly. (This matters: it means transposition can only be present *underneath/around* a doublet-avoidant layer, never alone — see below.)

3. **Plaintext/ciphertext autokey** — you already refuted it, and it's also doublet-agnostic, so no reason to revisit.

The unifying point: the delta=0 hole says the generator (nearly) forbids `c[i] == c[i-1]`. That is a **non-additive, history-dependent encoding rule**, and it is the single most diagnostic fact you have. Every worthwhile remaining attack must either exploit it or be consistent with it.

---

## GENUINELY UNTESTED and worth running (ranked by prior)

### A. Doublet-avoidant decoding (the "delta≠0" inversion) — HIGHEST PRIORITY
This is the one your synthesis correctly identified and it is the biggest real gap. If the construction rule is "emit a rune, but never equal to the previous rune," the natural cipher families are:
- **Homophonic/skip encoding**: when an additive step would produce a repeat, the encoder skips by +1 (or by a fixed nudge), introducing a deterministic perturbation. The inverse is a *Viterbi/DP decode*: search the rune sequence that (i) is high-probability English under a rune-level n-gram model AND (ii) is consistent with a "+1-on-collision" forward rule. This is a constrained-decoding problem, not a key search — you have never run it.
- **Variant: the skip rule is keyed** (skip amount depends on a short period key). Co-search short keys (period 2–12) jointly with the DP decode.

Worth running: **yes, first.** It is the only attack whose hypothesis *predicts* your observed delta=0 hole rather than being agnostic to it. If the pages are solvable by classical means, the prior mass is concentrated here.

### B. Rune-as-key / pages-keying-each-other (running key from the corpus itself) — MEDIUM-HIGH
You ran running keys against *external* books and the solved plaintext, but not the **unsolved ciphertext pages keying each other** (page i runes as the keystream for page j), nor **self-keying with an offset** (the page shifted against itself). Two cautions:
- A naive additive page-on-page is still memoryless → would NOT produce the doublet deficit, so as a *standalone additive* it's ruled out for the same reason as A1.
- BUT it is worth running in the **delta domain**: if two pages share a keystream, `c1[i] − c2[i]` collapses to `p1[i] − p2[i]`, removing the keystream entirely. Scanning all page-pair alignments (and offsets) for a difference sequence whose statistics look like English-minus-English (a sharp, non-flat difference distribution) is cheap and you have not done it. This is the classic **in-depth / Kerckhoffs superimposition** attack and it is a real hole. Worth running: **yes** — it's cheap and the depth attack is method-agnostic to the doublet rule.

### C. Transposition *combined with* a doublet-avoidant layer — MEDIUM
Transposition alone is ruled out (above), but **transposition layered with the delta≠0 substitution** is not, and it would *defeat your difference-based diagnostics*: the uniform-first-difference / delta=0-hole signature is only visible if adjacency is preserved. If there's a columnar/route transposition *outside* the substitution, your "adjacent runes" are not actually adjacent in the cipher's native order, and the delta=0 hole you measured would be a *coincidence of reading order* or would survive only partially. Test: attempt **transposition inversion (columnar, all plausible widths; route; rail) and re-measure the doublet/delta statistics after each candidate de-transposition** — if some width *sharpens* the delta=0 hole or restores a doublet structure, that's the native order. Worth running: **yes, but after A**, and mainly as a preprocessor that you then feed into A. Honest caveat: the search multiplies (widths × A's DP), so bound widths by IoC-after-transposition.

### D. Per-page interrupter co-search jointly with running keys — LOW-MEDIUM
You ran interrupters with thematic Vigenere, and running keys without interrupters, but **not interrupters jointly with running keys**. The solved pages did use interrupter/skip rules (the F-skip), so the prior is non-trivial. However: this is still fundamentally a memoryless-stream-plus-skips model, and skips alone don't manufacture a *global* sub-chance doublet deficit (they perturb locally). So it can rescue a near-miss running key but it cannot explain the fingerprint by itself. Worth running: **only as a refinement on your best running-key near-misses (the −6.2 region), not as a fresh broad sweep.** Diminishing returns are real here.

### E. Two-symbol / bigram-level encoding (the doublet deficit as a tell of non-monographic units) — MEDIUM, under-considered
You have been assuming the rune is the unit. A sub-chance doublet rate plus flat monographics is *also* the signature of an encoding where **the meaningful unit is a pair/fractionated symbol** (e.g., a Polybius/bifid/ADFGX-style fractionation over the 29-rune alphabet, or a taptcode-like coordinate scheme). Fractionation flattens monographics, can suppress same-symbol adjacency, and survives your keystream tests because it isn't a keystream. Worth running: **yes** — bifid/trifid/Polybius with the 29→(near-square) mapping, periods 3–25, scored by rune-n-gram English after de-fractionation. This is a clean, cheap family you have not touched and it is *consistent with* the fingerprint rather than contradicted by it. I'd rank this second after A.

---

## Quick verdict table

| Modality | Run it? | Why / fingerprint consistency |
|---|---|---|
| More keystreams (primes/books/keywords) | **No** | Memoryless; can't make sub-chance doublets. Pure diminishing returns. |
| Transposition alone | **No** | Doublet-transparent; falsified by suppressed doublet rate. |
| Plaintext/ciphertext autokey | No | Already refuted; also doublet-agnostic. |
| **A. Doublet-avoidant constrained DP decode (delta≠0)** | **Yes — first** | Only hypothesis that *predicts* the delta=0 hole. |
| **E. Fractionation (bifid/trifid/Polybius)** | **Yes — second** | Flattens monographics + suppresses adjacency; fingerprint-consistent; untouched. |
| **B. In-depth / page-on-page difference attack** | **Yes** | Cheap; cancels keystream; method-agnostic; genuinely untested. |
| **C. Transposition + doublet-avoidant layer** | Yes, after A | Only transposition variant not falsified; also tests whether your diagnostics are even reading native order. |
| D. Interrupter × running-key co-search | Marginal | Only to rescue −6.2 near-misses; can't explain fingerprint alone. |

---

## The one uncomfortable honesty note

There is a real possibility your difference-space diagnostics (the delta=0 hole, the uniform first-differences) are **artifacts of reading order** — i.e. they only hold because you're measuring runes in file order, and the true cipher applies transposition first. If so, idea A is being fed mis-ordered data and will also fail. That is why **C is not optional cleanup but a validity check on your entire fingerprint**: before trusting the delta=0 hole as a generative rule, confirm it isn't destroyed/created by plausible transpositions. If the hole survives all transposition hypotheses, it's structural and A/E are well-founded. If some transposition erases it, your "memory-dependent generator" conclusion — and the whole prioritization above — has to be re-derived in that order.

Net: stop spending on keystream breadth (A1/D); spend on **A (constrained doublet-avoidant decode)** and **E (fractionation)** as the two fingerprint-consistent families you never modeled, run **B** because it's cheap and assumption-light, and treat **C** as the experiment that tells you whether your own evidence means what you think it means.