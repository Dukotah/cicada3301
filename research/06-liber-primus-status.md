I have everything needed. The frequency analysis page 403'd but the earlier search snippet gave me the key numbers. I have enough to write the report.

# The Current State of the Liber Primus (Cicada 3301)

## Executive summary

The Liber Primus ("First Book") is the central, still-largely-unsolved artifact of the Cicada 3301 puzzle saga. It is a book written in a 29-symbol runic alphabet (the Gematria Primus). A minority of its pages have been decrypted and yield short philosophical/mystical passages; the large majority — roughly 50+ pages of the later release — remain unsolved as of 2026. The puzzle's last verified author activity was an OpenPGP-signed message in **April 2017**, and there has been no confirmed new 3301 material or solution since. A serious, widely-held theory is that the remaining pages may be effectively unsolvable (a key that was never published, or the group walked away), which is why no amount of community or computational effort has cracked them. This is consistent with the cryptographic evidence, not just defeatism.

---

## 1. Structure

- The book is written entirely in **Gematria Primus**, an alphabet of 29 runes drawn from the Anglo-Saxon Futhorc. Each rune maps to (a) an English letter or letter-cluster and (b) a **prime number** — the "gematria" value. This dual mapping (letters + primes) is itself thematically central. [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [scream314 GitHub](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)
- The material is usually split by solvers into two batches:
  - **LP1** — an early set (2014) of which roughly **17 pages are solved**.
  - **LP2** — a larger later set of **~58 pages, of which only ~2 are solved**, leaving on the order of **56 pages unsolved**. [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus)
- **Built-in rune ambiguities** make even a correct decryption hard to read and hard to validate automatically: U/V, C/K, S/Z, NG/ING, and IA/IO are not distinguished by separate runes and must be inferred from context. This creates exponential branching when a computer tries to score candidate plaintext. [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/)

---

## 2. What has been solved (with decoded English where documented)

### "A Warning" — Page 01
**Method:** Atbash (the Gematria Primus alphabet reversed) — a simple substitution. [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md), [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus)

Decoded:
> "BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE. TEST THE KNOWLEDGE. FIND YOUR TRUTH. EXPERIENCE YOUR DEATH. DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN, EITHER THE WORDS OR THEIR NUMBERS, FOR ALL IS SACRED." [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### "Some Wisdom" — Page 05
**Method:** Direct Gematria Primus → Latin transliteration (no cipher beyond the runic mapping). [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus)

Decoded (opening):
> "THE PRIMES ARE SACRED. THE TOTIENT FUNCTION IS SACRED. ALL THINGS SHOULD BE ENCRYPTED." (followed by guidance such as to amass wealth but never become attached to it). [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [search result corroboration]

### "Welcome" — Pages 03–04
**Method:** Vigenère with the key **DIVINITY** (ᛞᛁᚢᛁᚾᛁᛏᚣ), plus the **"F-skip" rule** — the key position is *not* advanced when the ciphertext rune is ᚠ (F). This F-skip trick recurs across several puzzles. [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

Decoded:
> "WELCOME, PILGRIM, TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS. IT IS NOT AN EASY TRIP, BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE. ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING, YOUR INNOCENCE, YOUR ILLUSIONS, YOUR CERTAINTY, AND YOUR REALITY. ULTIMATELY, YOU WILL DISCOVER AN END TO SELF." [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### Koan / "I AM" parable — Pages 06–09
**Method:** Shift-by-3 over a reversed Gematria alphabet. [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

A master interrogates a student's identity; every label (name, profession, "human," "conscious") is rejected until the student can only answer "**I AM**," and the master replies "**THEN YOU ARE WELCOME TO COME STUDY**," followed by the instruction "**DO FOUR UNREASONABLE THINGS EACH DAY**." [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### "The Loss of Divinity" — Pages 10–13
**Method:** Default Gematria (direct transliteration). [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

Names three behaviors that cause loss of divinity — **consumption** (belief in scarcity), **preservation** (fear of weakness), and **adherence** (following dogma to belong) — concluding "**THERE IS NOTHING TO BE RIGHT ABOUT. TO BELONG IS DEATH.**" [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### "The Circumference" koan — Pages 14–15
**Method:** Vigenère with key **CIRCUMFERENCE** (rendered FIRFUMFERENFE because of the F-substitution/skip quirk). [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### Closing instruction — Page 16
**Method:** Default Gematria. Reads: "**QUESTION ALL THINGS. DISCOVER TRUTH INSIDE YOURSELF. FOLLOW YOUR TRUTH. IMPOSE NOTHING ON OTHERS.**" [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### "An End" — Page 56/73
**Method:** A **totient/prime keystream** — for each prime, use φ(prime) = prime − 1, applied **mod 29**, again with the F-skip rule. This is the most mathematically elaborate of the *solved* pages. [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

Decoded:
> "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO [a 128-hex-char SHA-512 value]… IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE." The hash begins `36367763ab73783c…`. (No one has publicly found a page matching that hash — itself an open thread.) [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus), [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md)

### The Parable / "Instar Emergence"
This predates the book proper (it appeared in 2013 in the ID3 tag of the file 761.mp3) but is part of the same corpus and thematically frames the whole project:
> "Like the instar, tunneling to the surface, we must shed our own circumferences; find the divinity within and emerge." [Uncovering Cicada Wiki — Instar emergence](https://uncovering-cicada.fandom.com/wiki/Instar_emergence_(mp3_and_hidden_poem))

It is tagged "Parable 1,595,277,641," a number equal to the product of the per-line gematria sums (1259 × 1031 × 1229), illustrating the "words are also numbers" design. [Uncovering Cicada Wiki — Instar emergence](https://uncovering-cicada.fandom.com/wiki/Instar_emergence_(mp3_and_hidden_poem))

**Pattern of the solved pages:** they progress from trivial (direct transliteration) → simple substitution (Atbash) → keyed polyalphabetic (Vigenère with a *guessable, thematic* key) → math-keystream (totient mod 29). The crucial enabler in every keyed case was that the **key was a recoverable crib** — a word from the puzzle's own vocabulary (DIVINITY, CIRCUMFERENCE) or a derivable mathematical rule (φ, primes). [How the solved pages were solved](https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved)

---

## 3. What is NOT solved, and why

The bulk of LP2 — roughly pages 17 onward (solver source files mark these with key "?") — has resisted every attempt. The reasons are both evidential and structural:

**a) No recoverable key / no crib.** The solved pages cracked because the key was guessable from the puzzle's own themes or was a clean mathematical rule. The unsolved pages give solvers nothing analogous. If 3301 used a **long key, a running key (e.g., keying off another text), or an autokey**, and that key/seed text was never published, the pages are cryptographically a one-time-pad-like dead end. [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/), [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus)

**b) The statistics rule out the easy ciphers.** Community cryptanalysis found the ciphertext is *not* a simple short-key Vigenère or monoalphabetic cipher. Rune frequencies are nearly flat (≈1–3% on unsolved pages, occasionally up to ~6% on a single page) — i.e., close to uniform, which is what you expect from a strong polyalphabetic/stream cipher. [Frequency Analysis search result], [Uncovering Cicada Wiki — Frequency Analysis](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_(Liber_Primus))

**c) The one real anomaly — the doublet deficit.** The single most-cited clue is a **strange shortage of "doubled" runes**: only about **86 same-rune 2-grams in ~13,000 runes**, far fewer than chance would produce under a normal stream cipher. A low doublet count classically points toward an **autokey/autoclave cipher** (where the plaintext or ciphertext itself feeds the key), or a custom 3301-designed cipher, possibly autokey combined with something else. This is described as essentially the *only* solid structural clue found, and so far no one has turned it into a working attack. [search result — Frequency Analysis Unsolved Pages], [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages)

**d) Manual position-based exceptions.** Even on solved pages the cipher had hand-placed irregularities (the F-skip; key resets observed at specific indices like 59, 95, 108). Such index-specific exceptions are hostile to automated solvers because they break the regularity that cryptanalysis algorithms exploit. [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/)

**e) The validation problem.** Because of the U/V, C/K, S/Z, NG/ING ambiguities, even a *correct* decryption emerges as something like `TRBX[NG|ING]H BYF PAR[NG|ING]RAEG` and must be disambiguated; conversely, near-miss garbage can look superficially word-like. This makes it hard for a brute-force/scoring approach to recognize a true solution. [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/)

> **Flagged as theory, not fact:** A widely repeated and plausible hypothesis is that 3301 **deliberately made the remaining pages unsolvable** — using a never-published key — to "end the puzzle while preserving the air of mystery." This is speculation, but it fits the evidence (flat stats, no crib, silence since 2017). It is *not* a confirmed statement from 3301. [uatrav](https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html)

---

## 4. The community effort

- **Uncovering Cicada Wiki (Fandom)** — the most thorough public archive of solved/unsolved pages, methods, transliterations, and frequency analysis. [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved)
- **CicadaSolvers** — the principal active community, a **Discord server with 10,000+ members**, with admins who have worked the puzzles since 2013. Reddit (r/codes, r/cicada) historically fed it. [uatrav](https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html)
- **Open-source solvers/playgrounds** exist on GitHub (e.g., `r4nd0mD3v3l0p3r/LiberPrimusSolver`, `relikd/LiberPrayground`, `scream314/cicada3301`) — tooling for transliteration, Vigenère/Atbash/totient trials, IoC and n-gram statistics. These confirm the solved pages and provide infrastructure, but none has cracked an unsolved page. [scream314](https://github.com/scream314/cicada3301/blob/master/liber_primus.md), [LiberPrimusSolver](https://github.com/r4nd0mD3v3l0p3r/LiberPrimusSolver), [LiberPrayground](https://github.com/relikd/LiberPrayground)
- **Last verified 3301 activity:** an **OpenPGP-signed message on 4 April 2017** ("Beware false paths"), warning that fakes were circulating. No authenticated 3301 communication or new puzzle has been confirmed since. (Note: no credible verified "IamA" from the real 3301 exists; purported AMAs should be treated as unverified.) [Wikipedia — Cicada 3301](https://en.wikipedia.org/wiki/Cicada_3301), [uatrav](https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html)

---

## 5. Honest assessment: can modern AI/LLMs or computation solve the rest?

**Realistically, no — not with current methods, and an LLM in particular adds little.** Here is the unhyped reasoning:

- **What's been tried computationally:** Solvers have run the standard arsenal — index of coincidence, frequency and n-gram analysis, automated Vigenère/affine key-shift detection, brute-forcing thematic keys, and autokey hypotheses. These are exactly the right tools, and they're what *revealed* the problem (flat frequencies, the doublet deficit). They have not produced a break. [Uncovering Cicada Wiki — Frequency Analysis](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_(Liber_Primus)), [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/)

- **The fundamental obstacle is information-theoretic, not computational power.** If the cipher is an autokey or running-key system whose seed/key text was never released, then for a short message there can be *multiple* grammatically plausible decryptions and **no way to know which is intended** — i.e., the ciphertext may not uniquely determine the plaintext. More compute does not fix a missing key; it just enumerates more equally-plausible candidates. This is the same wall that makes a true one-time pad unbreakable. [connortumbleson](https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/), [Boxentriq](https://www.boxentriq.com/guides/cicada-3301-liber-primus)

- **Where an LLM could *help* (modestly):** as a *plaintext scorer*. The hardest part of any candidate decryption here is judging whether ambiguous output (`[C|K]`, `[NG|ING]`, archaic/koan-like English) is "real text." An LLM is genuinely better than a simple dictionary/quadgram model at recognizing 3301's stylized English and disambiguating runic clusters, which could raise the signal-to-noise of an automated search. That's a real but incremental benefit.

- **Where an LLM does *not* help:** it does not invent the missing key, does not divine a custom cipher's internal rule, and cannot brute-force a large keyspace better than purpose-built code. LLMs hallucinate plausible-looking "solutions," which is actively dangerous in a domain already drowning in hoaxes. Treat any "AI solved the Liber Primus" claim with strong skepticism — none is documented. [uatrav](https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html)

- **The plausible win condition is not cryptanalysis at all.** The realistic paths to solving the rest are (1) the correct *key/method* being identified — most likely by a human insight about what text or rule 3301 used as the running key, possibly seeded by the doublet anomaly pointing at autokey; or (2) 3301 (or a knowledgeable insider) publishing the key. Absent one of those, the pages may stay permanently unsolved — which several long-time solvers now consider the most likely outcome. [uatrav](https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html), [Uncovering Cicada Wiki](https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages)

**Bottom line:** The solved pages were solved because their keys were *recoverable*. The unsolved pages show every statistical sign of a strong cipher (likely autokey/running-key) with **no recoverable crib**, the activity record went silent in 2017, and there's a credible theory the book was intentionally left unsolvable. Computers and even good LLM-assisted scoring can sharpen the search, but they cannot manufacture a missing key. The honest status is: **mostly unsolved, possibly unsolvable, and unlikely to fall to "AI" absent a human or insider revealing the method.**

---

## Sources
- https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved
- https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_(Liber_Primus)
- https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages
- https://uncovering-cicada.fandom.com/wiki/Instar_emergence_(mp3_and_hidden_poem)
- https://www.boxentriq.com/guides/cicada-3301-liber-primus
- https://github.com/scream314/cicada3301/blob/master/liber_primus.md
- https://en.wikipedia.org/wiki/Cicada_3301
- https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/
- https://www.uatrav.com/lifestyles/a-flyer-linked-the-uofa-to-one-of-the-internet-s-deepest-mysteries-14-years/article_28497ecb-e80d-4f33-abcd-3af8755a871b.html
- https://github.com/r4nd0mD3v3l0p3r/LiberPrimusSolver
- https://github.com/relikd/LiberPrayground

*Note: The Uncovering Cicada Wiki frequency-analysis pages returned HTTP 403 to automated fetch; the doublet figure (~86 in ~13,000 runes), the 1–3% frequency range, and the autokey inference are drawn from the indexed search excerpts of those wiki pages and should be treated as community analysis (well-established within the solver community) rather than a 3301 primary statement. The SHA-512 hash on "An End," the "Beware false paths" 2017 PGP message, and all decoded passages above are documented in the cited primary/secondary sources.*
