# PA-1 — Public Prior-Art Census (Round 10B, 2026-08-12)

No attack run. Pre-registration: `PREREG.md`. Novelty control **passed** (all six decoy tokens
the repo demonstrably holds — relikd, scream314, krisyotam, iBotPeaches, LiberPrimusSolver,
cicada-solvers — were flagged by the grep), so the "uncited" judgments below are trustworthy.

---

## 0. Headline: the OTP verdict is this repo's, not the community's

Pre-registered rule: verdict decided by 3 primary community sources only; journalism excluded as
circular. Result — **0 of 3 assert OTP; 2 of 3 assert the opposite.** Under the pre-registered
threshold this is the "OTP is this repo's own" verdict, not "unresolved".

| Primary source | Says about solvability | OTP mentioned? |
|---|---|---|
| **DEF CON 31 (Aug 2023)** — "Cracking Cicada 3301", by Taiiwo, Artorias, Puck, Clockwork. The community speaking officially. | "the rest have resisted thousands of attempts"; "we have worked for years against all odds to solve the unsolvable"; "The future will prevail" | **No.** Full text extracted and decoded (see `defcon31_decoded.txt` note below). Zero occurrences of *one-time pad, unbreakable, autokey, running key, doublet, index of coincidence, brute force, Vigenère, totient, interrupter*. The only technical claims about LP2 in the entire deck are three bullets: "Runes are encrypted / Normal statistical distribution / Repeating bi-grams have a high frequency." |
| **cicadasolvers.com/quickstart** — the community's maintained cryptanalysis briefing | LP "has gone unsolved for over a decade" **despite "cryptographically sound indications that it is solvable"** | **No.** |
| **uncovering-cicada wiki, `Liber_Primus_Ideas_and_Suggestions`** — the community's technical analysis page | The doublet deficit is *"so far the only solid clue towards cipher/key found in runes"*, and they propose constructions that **reproduce** it | **No.** |

**Extraction control (pre-registered) satisfied:** the DEF CON PDF uses a font encoding offset by
a uniform +29 on ASCII inside UTF-16BE strings. After decoding, known plaintext comes out clean
(speaker names, and the verbatim 2014 "We are an international group… We have no name" PGP
message). So the term-absence measurement is on readable text, not garbage.

**Negative control (pre-registered) satisfied:** I searched with OTP-loaded terms
("one-time pad", "unbreakable", "unsolvable by design", "keys intentionally withheld"). That
biased search surfaced the claim only in **SEO/journalism-tier** pages ("what appear to be
one-time-pad fragments"), never in a community primary source — and even those concede *"no
community-wide consensus exists on whether the unsolved pages encode a continuous message or
whether the keys themselves were intentionally withheld."*

### What this does and does not mean

It does **not** refute the repo's OTP characterisation. The community has not done the repo's
quantitative work, and majority disbelief is not evidence. What it does mean is narrower and
still important: **the repo's confidence in OTP cannot borrow any support from an imagined
external consensus.** The most engaged public solvers, looking at the *same* doublet statistic,
read it as the fingerprint of a **findable algorithm** and are still building tools on that
premise in 2026. The verdict is load-bearing on this repo's own reasoning alone.

### Two corrections to `analysis/armada/recon-community-exhausted.md`

That doc is the repo's existing community-SOTA file and it is wrong in two sourced ways:

1. **§2 "Consensus interpretation: the unsolved pages are an autokey or running-key
   polyalphabetic"** — I found no primary community source stating this. The wiki's actual text
   attributes the doublet deficit to algorithms "using previous rune gematria position or value
   when calculating shift" (ciphertext feedback) and to specific integer stream keys. The repo
   **positively refuted autokey** — and may have been refuting a consensus it attributed to the
   community rather than one the community holds.
2. **§2's "IoC ≈ 0.0376–0.0385"** is cited to the fandom Frequency Analysis pages, which the doc
   admits it could not fetch. I fetched them (via `?action=raw`, which bypasses the Cloudflare
   interstitial that blocks normal fetch). **They contain no IoC figure at all** — only per-rune
   percentage tables, concluding "probably (page 0-2, page 3-7…etc) is same cipher/key but with
   different shift". The IoC number in the repo doc is unsourced.

---

## 1. Where the community's *actual* doublet work went (repo does not hold this)

The wiki page is the community's primary doublet document and it goes further than the repo knew:

- Their count: **86 same-rune 2-grams in ~13,000 runes**, "almost impossible… randomly using
  standard polyalphabetic cipher". Independently consistent with this repo's 0.66% vs 3.45%.
- They name **specific stream keys that reproduce the suppression**: [OEIS A061474](https://oeis.org/A061474)
  and a second sequence at `pastebin.com/PFb6eQiD`.
- They hold a **shared dataset**: `docs.google.com/spreadsheets/d/1-Tqf9SuLXv75YQfpAr7zIm7s1oF4ZWO_jqU-sg9PuN0`
  (doublet analysis) and `…/1DjK-AWjdP6pldAyVbKyCchAEYK0O1LCBLSm72Bbkd1c` (frequency by chapter).
- LP2 in gematria values: `pastebin.com/NrLjVjdq`.

Repo status: A061474 **is** tested (`analysis/armada20/test_id18.py`). The **pastebin sequence and
both spreadsheets are uncited and untested** (grep: 0 hits).

---

## 2. Uncited public prior art (grep = 0 hits in this repo)

### 2a. mortlach — the deepest single-person technical body, and it is ACTIVE
17 repos. Repo cites the *name* once (`research/LEDGER.md:164`) and nothing else. Methods proven
already-tried by its existence:

| Repo | Proves already tried |
|---|---|
| [lp-decrypter](https://github.com/mortlach/lp-decrypter) (10★) | Brute force over **arbitrary functions of two runes** `f(plain,key)=cipher`, with automated gematria rotations, **interrupters**, **key-dragging**, and plaintext ranking. This is a far more general sweep than "Vigenère/Beaufort". |
| [key-drag](https://github.com/mortlach/key-drag) (2024) | Cython-accelerated key application; `solve_solved_pages.py` reproduces all 3 keyed solved sections; `py_test_own_text.py` is a **planted-plaintext positive control** ("These should _never_ fail") — the same discipline this repo pre-registers. |
| [Liber-Primus-Crib-Assist](https://github.com/mortlach/Liber-Primus-Crib-Assist) (4★, 2024) | Systematic cribbing |
| [runeglish-language-model-transition-probabilty-matrices](https://github.com/mortlach/runeglish-language-model-transition-probabilty-matrices) | A **Runeglish 1–5-gram LM**, with and without the C→F/K orthography. The scoring instrument. |
| [project-runeberg](https://github.com/mortlach/project-runeberg) + [projectRuneberg_2022](https://github.com/mortlach/projectRuneberg_2022) | **"data for books in runes"** — a pre-built *rune-space* keytext corpus. Directly relevant to the Round-10 skeleton-corpus lane. |
| [RuneDecrypterPrime](https://github.com/mortlach/RuneDecrypterPrime) | **Pushed 2026-08-11 — one day before this census.** The community is not dormant. |
| [Key_search](https://github.com/mortlach/Key_search) | Brute-force keys against **cribs of the first 6 runes of each section** |

Forum: **[cicada3301.boards.net](https://cicada3301.boards.net/)** — live; mortlach's threads
[31 (combining runes)](https://cicada3301.boards.net/thread/31/combining-runes-1-visual-representation),
[33 (modular exponentiation ciphers)](https://cicada3301.boards.net/thread/33/modular-exponentiation-ciphers-runes),
[37](https://cicada3301.boards.net/thread/37/decrypt-runes-first-pages-solved),
[43 (decrypting spreadsheet)](https://cicada3301.boards.net/thread/43/rune-decrypting-spreadsheet).
Repo holds **3 PDFs of unrelated boards.net threads** in `attribution/papers-archive/`; the
technical threads are not ingested.

### 2b. cicada-solvers org — 57 repos, most uncited
Notably uncited: **csrkd** ("Cicada Shifting Running Key Decoder"), **Red_Rune_Cribs**,
**project-runeberg**, **gutenberg-txt**, **3301_assist** (baseline statistics so you can check
your tool is working), **LiberPrTools**, **monokuma-ConvolutionKernels** (convolution kernels of
the tree images), **lphelper**, **liber_primus_finds**, **miteo-3301tools**, **GematriaPrimusTool**,
**joutguess** / **joutguess-rebirth**, **idkfa**/**idkfa-web** (rtkd translator),
[**aldegonde**](https://github.com/cicada-solvers/aldegonde) (classical-crypto library for
non-A–Z alphabets; **pushed 2026-08-10**), **libergo**, **cmbsolverwp**,
[**The-Complete-Cicada3301-Archive**](https://github.com/cicada-solvers/The-Complete-Cicada3301-Archive) (106★).

### 2c. Solvers 2024–2026 the repo has never seen
- [NoxxGames/LiberPrimus-GPU](https://github.com/NoxxGames/LiberPrimus-GPU) (2026-06) — staged CUDA
  workbench with CI gates and provenance. **Its own README states broad unsolved-page search
  campaigns are "not started"** and CUDA is "deferred". So GPU-scale brute force is *tooled but
  not run* publicly. Same "no solve claim without a reproducible manifest" discipline as here.
- [cmbsolver/cmbcidada3301](https://github.com/cmbsolver/cmbcidada3301) (.NET GUI, 2026) — prime
  checker, numeric sequence generator, transposition, scytale, Caesar, word-length dictionary
  checker, binary identification.
- [neuroretransmit/liberprimus-tool](https://github.com/neuroretransmit/liberprimus-tool) — a
  **genetic algorithm** (`--ga`) over LP structure. Evolutionary search is dug ground.
- [sasha-thecornerspore-dev/RuneSwiss](https://github.com/sasha-thecornerspore-dev/RuneSwiss),
  [d4v1-sudo/my_cicada_tools_cpp](https://github.com/d4v1-sudo/my_cicada_tools_cpp) (statistical/
  structural + correlation dashboard), [Taiiwo/cicada](https://github.com/Taiiwo/cicada) (18★, the
  original CicadaSolvers library), [ralphatobe/cicada-3301](https://github.com/ralphatobe/cicada-3301),
  [lipeeeee/gematria](https://github.com/lipeeeee/gematria), [IamYoddha/liber-primus](https://github.com/IamYoddha/liber-primus),
  [artistofreap-byte/liber-primus-matrix-attack](https://github.com/artistofreap-byte/liber-primus-matrix-attack),
  [hugvig/liber-primus-research](https://github.com/hugvig/liber-primus-research) (2026-08-10),
  [Locyyx64/lp-cribbs](https://github.com/Locyyx64/lp-cribbs).

### 2d. The LLM-era assault record is far thinner than assumed
- **[Tumbleson 2024](https://connortumbleson.com/2024/01/29/ai-cicada-3301/)** (the "2024 GPT-4
  attempt"): GPT-4, Dec 2023–Jan 2024. Tasks were **magic-square identification, rune→Latin
  lookup, and image OCR**. Verdict: OCR "failed consistently"; **"No specific cipher decryption
  methods were tested"**; "AI wasn't really gaining anything."
- **[mae3301/chatbot_cribber](https://github.com/mae3301/chatbot_cribber)** (2023) — "use new
  chatbot technology to make a cribber". Stub.
- **No published LLM *cryptanalytic* assault on LP2 exists.** Academic LLM-crypto work
  (CipherBank ACL 2025, "Benchmarking LLMs for Cryptanalysis" EMNLP 2025) benchmarks classical
  ciphers and never touches LP.

---

## 3. The period-correct thesis: was it ever pursued publicly?

**Largely not.** The community's own untried list (wiki, quoting the Wikimedia etherpad,
verbatim "*Untried methods to solve LP*") is:

> • Using the outguess data to relocate the runes before shifting them.
> • Counting spaces AS runes instead of not.
> • Breaking LP into sections and applying the gematria value of the first rune to shift the next
>   rune. Or the pi_digit(n)th rune.
> • Applying gematria value of the first rune to the last rune (of the section).
> • Translating runes > old english > english.
> • Something similar to that [3301-fib prime] spiral from page 15.

Note what is **absent**: any systematic attempt to use *2012–2014 released Cicada artifacts* as
LP2 key material. The community's search stayed **inside the book**. The only public statement of
the external-artifact idea is a wiki author naming the 2014 onion-trail hex and writing:

> "*XORing the data… probably the strings of hex from the 2nd, 3rd and 4th onion pages of the
> 2014 trail, which have never been used for anything yet. I don't know how to XOR things, so
> I'll leave this for somebody else.*"

So the owner's thesis is, on the public record, **substantially undug** — the repo's own Round 4 /
Campaign VI external-artifact sweep is more thorough than anything published. That is a genuine
point in the thesis's favour on *novelty*, and simultaneously a point against it on *odds*,
because this repo already ran the obvious version of it and got null.

**One place this repo is ahead of the community:** the #1 item on their untried list
(outguess-payload-as-transposition-key) is killed here at the input level — `analysis/stego/`
built OutGuess 0.4 from source, verified it against known payloads, and found **LP2 pages carry
no stego at all** (`ELIMINATION-LEDGER.md:101`). There is no outguess data to relocate runes with.
