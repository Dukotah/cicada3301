I have comprehensive coverage. Final synthesis below.

---

# Cicada 3301 / Liber Primus (LP2 pp.0–55): What the Solver Community Has Already Exhausted

**Scope/skeptic note:** No reputable, reproducible solution to any unsolved page has appeared since the last verified solves (the prime/totient page, "56.jpg", solved early 2015). Everything below LP1 is consensus among the CicadaSolvers community; treat any "I solved a page" claim that doesn't produce a *reproducible method + coherent English plaintext + the expected Gematria/prime validation* as a hoax. Many circulate.

## 1. Ciphers and keys explicitly ruled out

The classical-cipher search space is essentially exhausted on the unsolved pages:

- **Plain monoalphabetic substitution / Atbash / fixed Caesar shifts** — these cracked the *easy* solved pages (e.g. 01.jpg = Atbash; several = simple shifts via Gematria Primus) but produce gibberish on pp.0–55.
- **Vigenère and Beaufort with all the "obvious" thematic keys** — tested and failed, including SOPHIA, VOID, INSTABILITY, PRIMES, CIRCUMFERENCE, DIVINITY, etc. Kasiski examination and IoC-by-period scans found no stable key length.
- **Re-using the solved-page methods** — the **prime/totient stream cipher** (the method that solved the last hard page: shift each rune by `prime − 1 mod 29`, with the F-skip rule) was re-implemented and run against the unsolved pages with many stream/offset variants → gibberish. Whatever keys/schedules they used were not reused.
- **Hill cipher, affine, XOR, reverse-Gematria** — built into the main solver toolkits (LiberPrayground, LiberPrimusSolver) and swept automatically; no hits.
- **OEIS sequence sweeps** — automated checking of the shift stream against thousands of integer sequences (LiberPrayground's OEIS checker) found no recognizable generating sequence.

Sources: [Boxentriq LP guide](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [How the solved pages were solved](https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved), [scream314/cicada3301 liber_primus.md](https://github.com/scream314/cicada3301/blob/master/liber_primus.md), [relikd/LiberPrayground](https://github.com/relikd/LiberPrayground), [r4nd0mD3v3l0p3r/LiberPrimusSolver](https://github.com/r4nd0mD3v3l0p3r/LiberPrimusSolver).

## 2. The statistical consensus (doublets + IoC)

This is the most important and most agreed-upon finding, and it constrains everything:

- **Index of Coincidence ≈ 0.0376–0.0385** on the unsolved corpus — essentially flat/random, very close to the 1/29 ≈ 0.0345 floor for a 29-symbol alphabet. This is *polyalphabetic-or-stronger* territory; anything monoalphabetic (IoC would be ~0.05+) is excluded.
- **Doublets are suppressed** — fewer adjacent repeated runes than random chance would predict. In classical cryptanalysis, *suppressed* doublets are the signature of an **autokey / running-key (autoclave)** construction, where the keystream itself shifts the plaintext and breaks up natural repeats. A plain periodic Vigenère would *not* suppress doublets this way.
- **Consensus interpretation:** the unsolved pages are an **autokey or running-key polyalphabetic**, or a custom stream cipher (possibly autokey layered with prime/totient streams), rather than any keyword Vigenère. This is *why* keyword sweeps were abandoned.

Sources: [Frequency Analysis – Unsolved Pages (wiki)](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages), [scream314 liber_primus.md](https://github.com/scream314/cicada3301/blob/master/liber_primus.md).

## 3. The doublet/interrupter (F-rune) behaviour

- The first rune **ᚠ (F)** functions as an **interrupter**: on solved pages, *some* cleartext F's are "escaped" — copied through unchanged and **not consuming** a shift from the prime/totient stream — while others are encrypted normally. This shifts the entire downstream alignment of the keystream.
- The unsolved problem: you don't know *which* F's are interrupts, and brute-forcing all subsets is **2^(number of F's)** — combinatorially infeasible by naive search.
- Community response: dedicated **interrupt-detector** tooling (LiberPrayground's `InterruptSearch.py` uses sequential + genetic/heuristic search instead of exhaustive enumeration, scored by IoC/English-likeness). It has recovered the interrupt patterns on *solved* pages but has **not** yielded the unsolved ones — implying either a different interrupter rune/rule, or that the underlying cipher is wrong so no interrupt pattern can score well.

Source: [LiberPrayground](https://github.com/relikd/LiberPrayground), [scream314 liber_primus.md](https://github.com/scream314/cicada3301/blob/master/liber_primus.md).

## 4. Claims of partial progress since ~2017

- **None reputable / reproducible.** The verified solve count has been static (LP1 ~17–18 pages; LP2 effectively stuck at "2 of 58") for years. Multiple secondary write-ups state plainly that solving "stalled significantly."
- The only repeatedly cited *foothold* is structural, not a decryption: the **6-gram "DJUBEI" appears twice** across the unsolved corpus (a rare long repeat / dis legomenon) — flagged as a possible crib/attack point but never converted into plaintext.
- **AI/LLM attempts (2024)** were unproductive: GPT-4 handled the trivial parts (magic square, rune lookup) but **failed at the actual OCR/transcription** (variable rune box sizes) and offered no cryptanalytic advance — "it only knows what is a quick search away." A real bottleneck is reliable image→rune OCR, which one researcher is still refining.
- **2025 "OutGuess" note** (community wiki, unverified): assertion that all LP pages carry encrypted or concealed OutGuess steganographic data. No confirmed extraction; treat as speculation.

Sources: [Cicada 3301 (Wikipedia)](https://en.wikipedia.org/wiki/Cicada_3301), [AI & Cicada 3301 (Tumbleson, 2024)](https://connortumbleson.com/2024/01/29/ai-cicada-3301/), [CicadaSolvers quickstart briefing](https://www.cicadasolvers.com/quickstart/), [Liber Primus Updates 2025 (wiki)](https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Updates_2025).

## 5. Notably UNDER-explored attack modalities

Given the autokey/running-key consensus and the obsessive sweeping of substitution-family ciphers, the gaps are:

1. **Transposition (and substitution+transposition composites).** Almost all community effort assumes shift/substitution preserving rune order. Pure or partial **transposition / route / columnar** attacks are thin. The flat IoC is also exactly what transposition would leave (it preserves single-symbol frequencies but kills bigram structure) — yet this is rarely pursued seriously.
2. **OutGuess-driven re-ordering as a cipher step.** A specifically named "untried" idea: use the steganographic OutGuess payload to **relocate the runes** before shifting — i.e., the stego data *is* the transposition/keying key. Essentially unexplored.
3. **True running-key against an external text.** If the keystream is a *running key* drawn from a specific book/text (rather than a math sequence), no one has systematically tried plausible source texts (Cicada's own solved-page English, sacred/gnostic texts, the Mabinogion/Agrippa lineage the puzzle references). Crib-dragging a running key is labor-intensive and under-done.
4. **Homophonic / multi-variant rune mapping.** Single runes can map to multiple values (A/I/O, TH, NG/ING). A genuine **homophonic substitution** model (multiple ciphertext runes per plaintext letter to flatten frequencies) is consistent with the flat IoC but barely modeled.
5. **Joint interrupt + cipher optimization at scale.** Interrupt search and cipher-key search are mostly done *separately*. A combined modern search (e.g., simulated annealing / hillclimbing over {cipher params × interrupt mask} scored by an n-gram/neural English model) is the obvious unexploited compute play — current tools hillclimb one axis at a time.

Sources: [60out summary](https://www.60out.com/blog/unsolved-mystery-cicada-3301-cypher), [CicadaSolvers briefing](https://www.cicadasolvers.com/quickstart/), [LiberPrayground](https://github.com/relikd/LiberPrayground), [Frequency Analysis – Unsolved Pages](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages).

## Bottom line
- **Exhausted:** monoalphabetic/Atbash/Caesar, keyword Vigenère/Beaufort (all thematic keys), re-use of the prime/totient method, Hill/affine/XOR, OEIS sequence sweeps.
- **Consensus:** unsolved pages are **autokey / running-key polyalphabetic (or a custom stream cipher)** — driven by flat **IoC ≈ 0.037** and **suppressed doublets**; the **ᚠ interrupter** scrambles keystream alignment and the interrupt-mask space is exponential.
- **Progress since 2017:** effectively none verified; AI/OCR efforts stalled; "DJUBEI" repeat is the only live crib.
- **Under-explored:** transposition/composite ciphers, OutGuess-as-transposition-key, external running-key source texts, homophonic models, and joint interrupt+key optimization with modern search/scoring.

**Caveat:** the strongest primary source (the `uncovering-cicada.fandom.com` Frequency Analysis pages) blocks automated fetch, so the exact IoC/doublet figures here are corroborated via search excerpts and the scream314 mirror rather than the page text directly — worth eyeballing manually before relying on the precise numbers.