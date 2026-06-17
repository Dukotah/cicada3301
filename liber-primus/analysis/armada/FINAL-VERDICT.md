# FINAL VERDICT: Liber Primus (LP2 pp.0–55) Multi-Agent Assault

## 1. BLUF

We threw a broad, automated cryptanalytic assault at the unsolved Liber Primus pages (LP2 0–55): running-key attacks against six external/internal source texts (Mabinogion, Emerson's *Self-Reliance*, *The King in Yellow*, Crowley's *Liber AL*, Gibson's *Agrippa*, and the solved-page plaintext), plus Vigenère and math-keystream (Fibonacci/prime) sweeps. **Nothing decrypted.** Zero candidates crossed the English threshold; the best score anywhere was **−6.23**, sitting much closer to gibberish (≈−7.4) than to real English (≈−4.2). This is not a near-miss — it is a clean, expected negative that corroborates the community consensus: these pages are **not** a memoryless keystream cipher you can crack by guessing the key. The genuine accomplishment here is not a solve (there isn't one) but a disciplined elimination of an entire family of hypotheses, plus a sharpened, fingerprint-driven shortlist of what is actually worth running next.

## 2. What was run + headline numbers

| Attack | Key / source | Best score | Hits >−5.2 |
|---|---|---|---|
| Running-key | Mabinogion (Guest) | −6.307 | 0 |
| Running-key | Emerson, *Self-Reliance* | −6.228 | 0 |
| Running-key | *The King in Yellow* | −6.357 | 0 |
| Running-key | Crowley, *Liber AL vel Legis* | −6.361 | 0 |
| Running-key | Gibson, *Agrippa* | −6.384 | 0 |
| Running-key | Solved-page plaintext | −6.397 | 0 |
| Vigenère | keyword sweep | −6.33 | 0 |
| Keystream | Fibonacci / prime variants | −6.369 | 0 |

- **Total hits above the English threshold (−5.2): 0.**
- **Best score seen anywhere: −6.23** (reference points: real English ≈ −4.0 to −4.4; pure gibberish ≈ −7.4).
- **Adversarial verdicts on hits: none required — there were no hits to contest.**
- Operational note: every orchestration command initially referenced non-existent verbose key filenames (e.g. `data/keys/The Mabinogion (Lady Charlotte Guest translation).txt`) and threw `FileNotFoundError`. Each job was re-run against the correct on-disk path (`mabinogion.txt`, `self_reliance.txt`, etc.) with the requested labels preserved, so the numbers above are real, not error artifacts.

## 3. Did anything decrypt? (honest read of the best score)

**No.** Read the −6.23 honestly: it is roughly **two-thirds of the way from gibberish to English**, and it falls short of even the lenient −5.2 hit threshold by a full point. The top candidates were inspected directly and are letter salad — e.g. p49 under the solved-plaintext key reads `TMOFNGOEDAWEFBEABYEOEOINTHTHSATHETHE...`, and the best Vigenère candidate (`WITHIN`, p49) shows teasing fragments (`...DSDIAEANRLINIATHTING...`) but no coherent words. Those English-like clusters are exactly the statistical mirage you expect from a 29-symbol alphabet scored by an English model — they are noise wearing a costume, not signal. There is no partial plaintext, no recoverable crib, no page that "almost" worked. The correct interpretation is a uniform null result, not a lead.

## 4. What the negative result means cryptographically

The null is informative because of *what* it rules out and *why*, and that reasoning is anchored in the community's hard statistical fingerprint of the unsolved corpus:

- **Index of Coincidence ≈ 0.037**, essentially at the 1/29 ≈ 0.0345 random floor → monoalphabetic structure is excluded; the cipher flattens single-symbol frequencies.
- **Doublets are *suppressed*** — adjacent-equal runes occur at ~0.66% vs the ~3.45% chance floor.
- Equivalently in difference space: `c[i] − c[i−1] mod 29` is uniform **except it almost never hits 0**.

This is the load-bearing fact, and it is what our negative result confirms from the other direction. **A memoryless additive/substitution keystream — running key, autokey, Vigenère, prime/totient — cannot drive the doublet rate *below* chance.** Such streams scramble the plaintext's own doublet rate toward chance; they never produce a sub-chance deficit. So a sub-chance doublet deficit plus a structural delta=0 hole is the signature of a **history-dependent generative rule that (nearly) forbids `c[i] == c[i−1]`** — not a key you can supply. Our six running keys, the Vigenère sweep, and the math-keystreams are *precisely* the memoryless family that the fingerprint predicts will fail. They failed, uniformly, exactly as predicted. That coherence between theory and result is the real epistemic payoff: we did not just "not find the key," we added direct evidence that **no key of this kind exists**, and that future effort spent enumerating more books/keywords/sequences has a near-zero prior. Stop widening the keystream search.

## 5. Genuinely-remaining untested angles, ranked

Ranked by prior probability and by *consistency with the doublet/flatness fingerprint* (an attack that contradicts the fingerprint is not worth running):

1. **Doublet-avoidant constrained decode (delta≠0 inversion) — run first.** Model the rule "emit a rune, never equal to the previous one" (collision-skip / rank code). Invert it as a Viterbi/DP decode that maximizes rune-level n-gram English likelihood subject to the forward collision rule, optionally co-searching a short skip-key (period 2–12). This is the *only* hypothesis that **predicts** the observed delta=0 hole rather than being agnostic to it. If these pages are classically solvable, the prior mass is here. Parameter-light — a few hundred trials.

2. **First-difference / integral test — run today, it's nearly free.** If the plaintext was differenced (or the cipher emits `c[i]=c[i−1]+g(p[i])` with a permutation `g` whose range omits 0), then taking the cumulative sum `q[i]=Σc[j] mod 29` inverts it. Test `q` (and `q+k` for all 29 offsets, and `−q`) for language. A single operation that, if correct, *reverses all four anomalies at once*. Falsifiable tell: after integration, the doublet rate should rise back toward ~3.45% and the delta-flatness should break.

3. **Fractionation family (bifid / trifid / Polybius over the 29-rune set) — run second.** Sub-chance doublets + flat monographics is *also* the classic signature of a fractionating cipher, which our keystream tests cannot touch because it is not a keystream. Cheap, untouched, and fingerprint-consistent. Sweep periods 3–25, score after de-fractionation.

4. **In-depth / page-on-page difference attack — cheap, assumption-light.** We ran external books and the solved plaintext as keys, but never the *unsolved pages keying each other*. If two pages share a keystream, `c1[i]−c2[i]` cancels it to `p1−p2`. Scan all page-pair alignments and offsets for a non-flat (English-minus-English) difference distribution. Method-agnostic to the doublet rule.

5. **Transposition layered with a doublet-avoidant substitution — run after #1, and as a validity check.** Transposition *alone* is falsified (it is doublet-transparent and would leave ~3.45%). But transposition *outside* the substitution would mean our delta-space diagnostics are reading non-native order. Invert candidate transpositions (columnar all widths, route, rail) and **re-measure the doublet/delta statistics** — if a width *sharpens* the delta=0 hole, that is the native order; if some transposition *erases* it, the entire "history-dependent generator" conclusion must be re-derived in that order. This doubles as a sanity check on our own evidence.

6. **Interrupter (ᚠ/F) co-searched with running keys — marginal, refinement only.** The solved pages used an F-skip interrupter; the interrupt-mask space is 2^(#F), infeasible by brute force, and skips alone cannot manufacture a *global* sub-chance doublet deficit. Worth co-running only to rescue a specific near-miss, not as a fresh broad sweep. Diminishing returns.

**Explicitly do not run again:** more running-key source texts, more thematic Vigenère keywords, more math keystreams, plaintext/ciphertext autokey, or transposition-only. All are memoryless or doublet-transparent and are contradicted by the fingerprint. Continuing them is the clearest diminishing-returns trap in the whole program.

## 6. Can AI + unlimited tokens solve the Liber Primus?

**Honest answer: not by itself, and "unlimited tokens" is the wrong resource.** Tokens buy generation, not insight, and this problem is not token-bound — it is *hypothesis-bound*. The bottleneck is identifying the correct **structural model** of the cipher (the generative rule behind the doublet deficit), after which the actual decode is cheap. No amount of LLM text generation discovers that model; LLMs are weak at exactly the novel symbolic/combinatorial reasoning required, and the 2024 GPT-4 attempts confirmed this — they handled trivial lookups and failed at both the OCR and any genuine cryptanalytic advance ("it only knows what is a quick search away").

Where AI *does* contribute, and meaningfully:
- **As a fast, tireless scoring and search engine** — neural/n-gram English models as the fitness function inside DP/Viterbi/hillclimb/annealing decoders. This is real leverage and it is the right way to deploy compute on angles #1–#5 above.
- **As a hypothesis generator and critic** — the value this very assault produced was not a solve but a *rigorous elimination* of the memoryless-keystream family and a fingerprint-driven reprioritization. That is genuine, creditable progress: the search space is now provably narrower and correctly aimed.

But two hard limits remain that no token budget removes: (1) a likely **OCR/transcription** problem at the source (variable rune box sizes) means some pipelines may be attacking subtly wrong ciphertext; and (2) **there may simply be no plaintext to find** for some pages, or the key may be external information never published — in which case the puzzle is not *hard*, it is *underdetermined*, and unsolvable by any amount of analysis.

**Bottom line:** AI is a force-multiplier on the search and scoring, and it sharpened the problem here — but the Liber Primus will be cracked, if at all, by a correct human (or AI-assisted) *structural insight* into the doublet-avoidant construction, not by brute generation. Unlimited tokens spent on the wrong model produce −6.23 forever. We did not solve it; we did, honestly, narrow it and aim it.