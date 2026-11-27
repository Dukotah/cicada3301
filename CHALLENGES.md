# Challenges — bounded problems with a finish line you can check yourself

**Nobody has solved Liber Primus 2**, and this page doesn't pretend you will this weekend.
What it offers instead is twelve problems (C10 is retired for now) that each have a **checker you can run**, a
**finish line written down in advance**, and **credit** in the ledger when you cross it.

This is different from [`docs/OPEN-LANES.md`](docs/OPEN-LANES.md). A lane is a research
direction: you decide when you're done. A challenge is a problem where a script tells you
whether you're done, so you (or the AI agent you point at this page) can iterate without
waiting on us.

If you're an agent: every checker below runs from the repo root with plain `python`, needs
no network after `python liber-primus/data/fetch_sources.py`, and exits `0` on success.
Read [`AGENTS.md`](AGENTS.md) §1 first so you know what has already been ruled out.

## At a glance

| | challenge | for | effort | checker | finish line | current best |
|---|---|---|---|---|---|---|
| **C0** | Decode an LP2 page | anyone | unbounded | `liber-primus/verify_solution.py` | the oracle's verdict + human review | unsolved |
| **C1** | Restore relikd's page map | first-time contributors | ~1 hour | `challenges/c1_crossdiff_test.py` | 4/4 tests pass | open |
| **C2** | Recognize plaintext in short windows | ML / stats people | days | `challenges/c2_short_recognizer.py` | +0.05 over baseline on a held-out text | baseline **0.408** |
| **C3** | Certify your decoder | anyone running sweeps | hours | `challenges/c3_decoder_gates.py` | 7/7 gates | reference beam |
| **C4** | Read a page independently | humans, vision models | ~1 hour per page | `challenges/c4_transcription.py` | a full read of a page nobody has re-read | **1/57** pages |
| **C5** | Explain the T7 anomaly | modelers | days to weeks | `challenges/c5_t7_mechanism.py` | fits all 7 statistics, evidence ratio ≥ 3 | flat filter: misfits T7 |
| **C6** | Break one of our closures | red-teamers | varies | your own reproduce command | a plant the row's own code misses | none yet |
| **C7** | Forge a reference corpus *(heavy lift)* | linguists, corpus builders | days | `challenges/c7_corpus_forge.py` | a validated corpus in a register nobody has covered | 6 language families covered |
| **C8** | Score a register the panel can't *(heavy lift)* | NLP / LM people | days to weeks | `challenges/c8_register_scorer.py` | power ≥ 0.80 at 1% FPR on LP2-page windows | panel-R36: 12 registers |
| **C9** | Recover through null insertion *(re-scoped R47-H2)* | search / decoding people | days | `challenges/c9_rejection_loops.py` | C3 7/7 + ≥ 0.80 of V-NULL plants recovered | both beams **0/40** (X1 probe 8/40) |
| ~~C10~~ | Attack under shuffled word lengths *(retired pending Round 48)* | — | — | `challenges/c10_shuffled_lengths.py` (instrument only) | none: crossed in-house twice (R47-X1 0.962 at known key; R47-H2 0.88 at unknown key) | not offered |
| **C11** | Decode the constructions the coin hides *(heavy lift)* | search / decoding people | days to weeks | `challenges/c11_alt_constructions.py` | ≥ 0.80 of V-DELETE and V-SILENT plants recovered | reference beam **0/40** on each |
| **C12** | Reproduce 14 runes with a generator *(heavy compute)* | anyone with GPUs or a cluster | 10²–10⁵ core-hours per target | `challenges/c12_generator_hit.py` | an exact run long enough for your search size (≥ 14) | 8 generators × 2³² seeds: 0 hits, longest run 11 |

## How it works

1. **Pick one** and read its section below.
2. **Claim it** if it'll take more than a day: open an issue with the *Challenge submission*
   template marked "claiming", or comment on the challenge's pinned issue. C4 is claimed per page.
3. **Run the checker until it says you're done.** Every checker prints what's wrong.
4. **Submit** with the *Challenge submission* issue template: the checker's output, a link
   to your PR or repo, and which AI tools you used (that's useful context, never a mark against you).

We aim to answer every submission within a week. Accepted work is credited by name in the
commit, the ledger row, the doc it changes, and the [hall of fame](#hall-of-fame) below.

---

## C0 — Decode an LP2 page

The grand prize, and the one we least expect. The ciphertext is **OTP-class**: it cannot be
told apart from a one-time pad, and it also cannot rule out a keystream derived from a short
seed. 420 ledger rows (Round 47) record what has been tried.

**Check:** `python liber-primus/verify_solution.py --keystream your_key.txt` (or `--key-module`,
or `--plaintext`). The oracle replays your key through the same instrument the repo trusts
and compares it to a size-matched null. A crosser goes to human review per
[`liber-primus/HUMAN-ORACLE.md`](liber-primus/HUMAN-ORACLE.md); it is never auto-certified.

**Before you start:** search `liber-primus/LEDGER.json` for your idea. Asking an LLM to
"read the runes as English" is closed at measured power; so are cross-page pads, stego on
the page images, and the rest of the list at the bottom of `docs/OPEN-LANES.md`.

## C1 — Restore relikd's page map *(good first issue)*

`load_relikd()` in [`liber-primus/analysis/transcription/crossdiff.py`](liber-primus/analysis/transcription/crossdiff.py)
concatenates relikd's eleven chunk files into one flat list, throwing away the only
correct book-page map in the transcription lineage (njloof traced this in
[#14](https://github.com/Dukotah/cicada3301/issues/14)).

**Task:** add `load_relikd_chunks()` returning, for each chunk in order, a dict with
`chunk` (e.g. `"p40-53"`), `book_pages`, `segments` and `runes`. Book page 50 has no runes
and must not appear. Leave `load_relikd()` returning exactly what it does now.

**Check:** `python -m pytest challenges/c1_crossdiff_test.py -q` → 4 passed. It fails today
on purpose. (We verified it's solvable: every chunk's rune count equals the sum of its
canonical segments, 11/11.)

## C2 — Recognize plaintext in short windows

Our English scorer works on long text and falls apart below about 13 runes. That blocks
the 30-bit dot stream and every short enumeration in the ledger, which are stuck at
"measured only" ([`docs/OPEN-LANES.md`](docs/OPEN-LANES.md), Tier 2).

**Task:** write `score(idx) -> float` for a list of rune indices (0–28); higher means more
plaintext-like. The checker draws fresh windows of 6, 8, 10 and 12 runes each run: real
text as positives, and two kinds of negatives, uniform random runes (what a wrong key
decodes to) and the *same* positive windows shuffled. It reports TPR at 1% FPR.

```bash
python challenges/c2_short_recognizer.py                  # baseline: 0.408 (±0.01 across seeds)
python challenges/c2_short_recognizer.py my_scorer.py
```

| L | 6 | 8 | 10 | 12 |
|---|---|---|---|---|
| baseline TPR vs both negatives | 0.239 | 0.350 | 0.469 | 0.575 |

**Finish line:** a headline at least **0.05 above the baseline on a held-out text**. The dev
texts (`solved_plaintext.txt`, `self_reliance.txt`, `thematic.txt`) are public, so you can
overfit them; at review we run your scorer with `--text` on public-domain archaic English we
choose then and don't announce. The shuffled negatives are the honest part: a scorer that
only rewards letter frequency fails them.

**Note:** this is an English-register instrument. A negative that uses it is an
English-only negative and must say so (doctrine rule 5).

## C3 — Certify your decoder

Round 8 ran 2.52 × 10⁹ decodes through a decoder that could not have found the answer even
if the hypothesis had been right. The benchmark's seven gates exist so that never happens
again; each plants a known key family and checks both directions (plant recovered, wrong
key stays in noise).

**Task:** expose `decode(C, K, sign=-1) -> {"score", "translit", "plain_idx"}` as in
[`liber-primus/benchmark/README.md`](liber-primus/benchmark/README.md).

```bash
python challenges/c3_decoder_gates.py                                       # reference: 7/7
python challenges/c3_decoder_gates.py challenges/examples/rigid_decoder.py  # 4/7, NOT QUALIFIED
python challenges/c3_decoder_gates.py my_decoder.py
```

**Finish line:** 7/7. That is the entry ticket for filing any sweep you run as a negative.
A qualified decoder that's meaningfully faster or stronger than the reference beam (in
sweep throughput, or recovery at lengths the reference can't reach) is worth a ledger row of its own.

## C4 — Read a page independently

Every published transcription descends from **one 2017 root**. Unanimity among them is one
witness, not five. Independent reads are how [#12](https://github.com/Dukotah/cicada3301/issues/12)
and [#14](https://github.com/Dukotah/cicada3301/issues/14) found real errors.

**Task:** transcribe one **book** page from its image (`liber-primus/data/relikd/p<N>.jpg`,
or any scan you trust) **without looking at any transcription first**. Humans and vision
models are both welcome; say which.

```bash
python challenges/c4_transcription.py --page 23 my_p23.txt   # diff against the canonical stream
python challenges/c4_transcription.py --board                # which pages have been re-read
```

**Finish line:** a complete read of a page not yet on the board. Agreement and disagreement
are both results: a page you match exactly gains a second independent witness, and a
disagreement you confirm with a pixel crop is a data correction. Claim the page first so two
people don't read the same one. Page numbers are book pages: book p50 has no runes, see
[`liber-primus/data/PAGE-NUMBERING.md`](liber-primus/data/PAGE-NUMBERING.md).

## C5 — Explain the T7 anomaly

The live anomaly in both public ledgers: where doublets (adjacent repeated runes) occur in
the ciphertext, consecutive gaps between them are correlated (lag-1 autocorrelation +0.380,
p ≈ 0.001), and the effect is concentrated in three large gaps spanning stream positions
2739–4388. The old model, a flat anti-repeat filter, explains every other statistic and
misses this one. Ledger row `R44-W2B3-D01-FALSIFIER`.

**Task:** write `generate(rng, page)` returning a 12,956-rune stream from a mechanism you
can name: per-session filters, state resets, hand vs machine encipherment, anything with a
story. The checker runs the registered R44 battery on your draws and compares them to the
real stream.

```bash
python challenges/c5_t7_mechanism.py                          # flat filter: T7 misfit, p=0.007
python challenges/c5_t7_mechanism.py my_generator.py --draws 1000
```

**Finish line:** fits all seven statistics (each two-sided p ≥ 0.05) **and** an evidence
ratio of at least **3** against the flat filter, at `--draws 1000`, on two seeds. The ratio is
a kernel estimate of how densely your model lands on the real statistics, and it's there
because fitting is easy: a vague model that sprays its draws widely "fits" everything. A
throwaway random-session model we tried fits all seven and scores **0.03**.

**Rules:** at most 5 free parameters, named in your file. The generator may not read the LP2
stream, its doublet positions or its gaps. A winning mechanism becomes a constraint on the
key generator, which is the most direct path from an anomaly to the cipher.

## C6 — Break one of our closures

Every genuinely new result in this project came from auditing an instrument or a closure,
not from a bigger sweep (doctrine rule 1). So this is the challenge we most want lost.

**Task:** pick a row in `liber-primus/LEDGER.json` with status `negative` or `eliminated`.
Read its `coverage`. Build a planted signal that sits **inside** that coverage and show that
the row's own code fails to recover it.

**Finish line:** one reproduce command that plants, runs the row's code, and shows the miss.
The row gets reopened with your name on the correction. Our own audits have done this
before: `liber-primus/analysis/round36/AUDIT-inhibitors.md` is one, and the Round 43 ledger
diff found 9 closures that needed reopening (`liber-primus/analysis/round43/SYNTHESIS.md`).

---

## Heavy lifts — bring your own compute

C7 and C8 are questions this project can state precisely but can't afford to answer alone. Each one
sits on a measured gap in the repo's own instruments, so every negative in the ledger carries it as a
caveat until someone closes it. C9 is smaller and is no longer pitched as a heavy lift. C10 is retired until
Round 48. R47-X1's red-team and R47-H2's hardening are why; see each section.

- **C7, C8 — the register gap (L7-A).** Every negative here is an English-register negative unless it was
  re-adjudicated. Closing it needs corpora and language models for registers we don't have. That means
  sourcing texts, designing transliteration tables and training scorers, which is reading-heavy work.
- **C9 — null-insertion recovery (L7-B, recovery only).** The beams already *see* the correct key under
  V-NULL; they can't *read* it. The bigger construction gap, V-BACK (a key pointer that steps back), turned
  out to be closable in-house with one added beam relation (R47-X1, 32/40), so it is scheduled for Round 48
  rather than offered here.
- **C10 — the word-length gap (R46-L1).** If the printed spaces aren't the plaintext's own, every
  word-indexed attack in the ledger loses its recovery. A position-synchronous beam over each sentence's length
  multiset recovers U2b plants at known key (R47-X1); what remains open is the unknown-key sweep and the other
  constructions. R47-H2 then made the key unknown, and a cheap key screen plus that beam still recovered 0.88,
  so C10 is retired until Round 48 re-scopes it.

**Rough cost** (our guess, so you can budget, not a promise):

| | agent tokens to a serious attempt | CPU per checker run | what dominates |
|---|---|---|---|
| C7 | 0.5–2 M | seconds | finding a clean public-domain text, designing and justifying the table |
| C8 | 1–5 M | ~1 min per held-out text | building an LM that beats the shuffled-text null on short windows |
| C9 | 0.5–2 M | ~1 min at 12 plants, ~5 min at 40 | a transition that drops doublet-triggered nulls (not a heavy lift) |

**How sealing works.** Each checker draws **fresh plants** every run from `--seed`. With no seed it uses
64 random bits and prints them, so any run can be reproduced. You can iterate as much as you like, but
you can't tune to a fixed set. Credit is decided on a **sealed run**: we post `sha256(seed)` in your
submission issue, run the checker at that seed (C8 and C9 also on held-out text we choose then), and reveal
the seed with the verdict.

**Isolation.** C8 and C9 (and the retired C10's checker) run your file in a separate `python -I` process (`challenges/_sandbox.py`). It
receives only the inputs the challenge grants (a window; C and K; C and the print), one call at a time and in
a random order, and returns only a number or rune indices. It never sees the plaintext, the seed or the
checker's objects. (Before R47-H2, submissions ran in the checker's own process, and R47-X1 passed all four
checkers by reading their stack frames.) A hostile program can still inspect other processes through the
operating system, so credit also requires code review. C7's language label is checked by an automatic
profile gate and then by a human reading your source and table.

**What a crossing changes** is named under each challenge below. Every baseline is measured and recorded
in `liber-primus/analysis/round47/H1-heavy-lifts/` (`RESULTS.md`, ledger rows `R47-H1-…`).

### C7 — Forge a reference corpus

LP2's printed words are unusually short of 2-rune words (15.47 %). Round 46 placed that against English,
Latin, German, Welsh, Old English and the solved pages, and **nothing else**
(`R46-P1-TWO-RUNE-EXPLANATIONS`, `not_covered`: "Greek, Hebrew, Norse … and other languages"). The missing
piece is not a statistic. It's a corpus written in Gematria Primus runes.

**Task:** a directory with `manifest.json` (ISO 639-3 language, register, public-domain provenance with
the source's sha256, and a **transliteration table**: grapheme → GP tokens), `source.txt`, and
`corpus.txt`. `--build` writes `corpus.txt` from your table, so you don't need a transliterator of your
own. The table and the source are the contribution. Copy `challenges/examples/c7_latin_aeneid/` to start.

```bash
python challenges/c7_corpus_forge.py --self-test                      # worked example: Latin (Aeneid), covered
python challenges/c7_corpus_forge.py my_corpus/manifest.json --build
python challenges/c7_corpus_forge.py my_corpus/manifest.json          # validate + place LP2 against it
```

The checker re-derives a seeded sample of 500 sentences from your table and requires an exact match. It
also requires ≥ 20,000 words, and it prints a ready-to-add row: 2-rune share, 9-class length profile, LP2's
percentile among 1,000 windows of 2,896 words, and the R46-P1 T3 verdict (admitted or rejected). In the
worked example Latin sits at 8.4 % 2-rune words, LP2 is above all 1,000 windows, and Latin is rejected.

**Label gate.** The language field is not taken on trust. The checker compares your corpus's GP bigram profile
with the English reference and with every covered language except the one you claim (Jensen–Shannon
divergence). If it is within 0.06 of any of them, the corpus is rejected. In-repo English texts sit 0.014–0.049
from the English reference, and every pair of different languages is at least 0.079 apart. The worked example
(Latin) is 0.12 from English. English labelled as Old Norse (R47-X1's probe) is 0.024 and fails. The gate is a
sanity check, not a language ID: a close relative of English, such as Middle English, can trip it legitimately.
If yours does, say so in the submission. The maintainers review every source and table by hand either way.

**Finish line:** a valid corpus in a register **not already covered**. Covered: English (all registers),
classical Latin, German, Welsh, Old English, the solved pages. Wanted: Koine or Attic Greek, Biblical
Hebrew, Old Norse or Icelandic, Middle English, Vulgate or medieval Latin, Old Irish, Gothic. **Changes:**
R46-P1-TWO-RUNE-EXPLANATIONS gains a reference, and its "other languages" gap narrows by one.

### C8 — Score a register the panel can't

Panel-R36 adjudicates 12 registers: three Englishes, the LP1 register, Latin, Old English, German, Welsh,
two vowel-reduced Englishes, Greek, Hebrew and Norse. Anything else is invisible to every negative that
used it (`L7-A-SCORER-ENGLISH-ONLY`, `not_covered`: "languages not modelled").

**Task:** `REGISTER = "<name>"` and `score(idx) -> float` for one register outside the 12, plus held-out
text in it, given as a C7 manifest, a rune file or Latin-alphabet text.

**How it's scored:** windows of 236 runes (LP2's mean page), also 120 and 60. Each window is planted with
the repo's standard plant: keyskip encipher under a fresh SHA-256 key, then decoded with the correct key by
the reference beam. It is scored against **four nulls**: uniform runes, real LP2 windows, the same windows
shuffled, and beam decodes of LP2 under a wrong key. The threshold must hold FPR ≤ 0.01 against **every**
class.

```bash
python challenges/c8_register_scorer.py --self-test                               # English + panel baselines
python challenges/c8_register_scorer.py my_scorer.py --heldout my_text.json --direct   # fast iteration
python challenges/c8_register_scorer.py my_scorer.py --heldout my_text.json            # the real protocol
```

| held-out text, full protocol, L = 236 | English reference | panel-R36 |
|---|---|---|
| English (*Dracula*) | 1.00 | 1.00 |
| Latin (latin_218), German (de_2) | 1.00 | 1.00 |
| vowel-dropped English (a panel register) | **0.00** (L7-A, reproduced) | **0.33** (≥ 0.90 against the three wrong-key nulls) |
| reversed English (not a panel register) | 0.87 | **0.62** |

**Read this table carefully.** At 1% FPR the English scorer already sees Latin and German. The real gap is
in registers whose letter *sequence* is unlike anything the scorer was trained on, such as vowel-dropped or
reversed text, abbreviated scribal forms, or non-European orthographies. There, the **shuffled-text null**
is the one that bites, and it bites the panel too. Reversed English shows the English scorer can beat the
panel on an off-panel register, so the incumbent line is worth reading.

**Finish line:** power ≥ **0.80** at FPR 0.01, L = 236, against every null class, for a register outside the
12. We re-run it at review on our own held-out text of the same register. **Changes:** the panel's register
list and the register conditional of every re-adjudicated negative. If the panel already reaches 0.80 on
your windows (the checker tells you), it is filed as "already seen by panel-R36". That is still a measured
row, but it isn't an extension.

### C9 — Recover through null insertion *(re-scoped by R47-H2; not a heavy lift)*

Every beam in this repo assumes two things about the encipherer's rejection loop: the key pointer only
moves **forward**, and every cipher rune comes from **one** plaintext rune. beam_v3's three relations
(keyskip1, keyskip2, free) all make both assumptions. The checker's variants each break one:

- **V-NULL (scored):** on a would-be doublet it emits a **null** rune that uses no key, throws the rejected key
  symbol away and retries. Because the rejected key symbol is discarded, the key still advances once per cipher rune, so beams stay in sync; unlike
  the solved pages' interrupters it does not shift the key.
- **V-BACK (diagnostic, not scored):** on a would-be doublet the encipherer steps the key **back** one place
  (`j -= 1`, the one-character sibling of keyskip's `j += 1`) and retries. This reuses key symbols.
- V-DEFER (diagnostic, not scored): the rejected key symbol is used for the next rune.

All three reproduce LP2's doublet rate (0.66 %) and its lag-2 repeat rate (3.4 %). An earlier V-NULL
didn't, and failed that check, so it was replaced (PREREG Addendum 1).

**Task:** `decode(C, K, sign=-1) -> {"plain_idx": [...]}` as in C3, returning the plaintext **without** the
nulls. The checker computes the English score of your output itself. A plant passes if you recover ≥ 0.85 of
its runes and the output scores ≥ −5.2; the same ciphertext under a wrong key must stay ≤ −6.0.

```bash
python challenges/c9_rejection_loops.py --self-test --v3                          # both reference beams
python challenges/c9_rejection_loops.py my_decoder.py                             # C3 gates + 12 plants/variant
python challenges/c9_rejection_loops.py my_decoder.py --plants 40                 # the scored size
```

| 40 plants, L = 240 (plants ok · median score of the correct-key decode) | keyskip (control) | V-NULL | V-BACK (diag.) | V-DEFER (diag.) |
|---|---|---|---|---|
| C3 reference beam | 40/40 · −4.29 | **0/40** · −4.54 | 0/40 · −7.01 | 39/40 · −4.60 |
| beam_v3, best of 3 relations | 40/40 · −4.29 | **0/40** · −4.54 | 0/40 · −6.79 | 39/40 · −4.59 |
| R47-X1 beam + backstep + null relations (dev seed, penalties tuned on it) | 36/40 | 8/40 | 32/40 | — |

The failures are different in kind. V-BACK is the transition-model gap: no beam negative covers it, though a backstep relation closes it
(R47-X1, 32/40). V-NULL is a recovery gap only: beam negatives already score its correct key as English (−4.54).
For V-NULL the beams output a junk rune for every null, so positional recovery is 0.17: a sweep would still flag
the key, but nobody would read the plaintext correctly.

**Why V-BACK is not offered here.** It is real (both beams score its correct key as noise, so no beam negative
in the ledger covers it), but it is a representational gap that a ~20-line beam relation closes, and nothing
measured raises its prior for LP2. Closing it is in-house work: **Round 48** adds a backstep relation to the
beam and re-adjudicates the beam-based negatives with it. The checker still reports V-BACK so that work can
use it.

**Finish line:** C3 7/7 **and** ≥ 80 % of 40 sealed plants recovered on V-NULL, with wrong-key false positives
≤ 5 %, then code review. **Changes:** no detection negative (they already cover V-NULL's key). It adds a
qualified *recovery* decoder for doublet-triggered null insertion to `L7-B-BEAM-ENVELOPE`'s recovery
qualifier, which is what turning a flagged key into a reading would need. R47-X1's quick null relation got
8/40, so this may well close in-house too; treat it as a days-scale problem, not a heavy lift.

### C10 — Attack under shuffled word lengths *(retired pending Round 48)*

Round 46 asked what happens if LP2's printed word lengths are right per sentence but **in the wrong
order** (regime b′). Every word-indexed attack in the ledger dropped to ≤ 0.033 power. C10 asked for an attack
that still works. **It is not offered right now**, because both versions were crossed in-house:

- **v1 (R47-H1), key given.** R47-X1 crossed it with a 58-line beam over each sentence's length orderings (481/500
  and 488/500, null FP 0). So at known key the (b′) loss belongs to the printed-start decoder, not to the
  information in the print. That result stands as a finding (`R47-X1-C10-SEGMENTATION-BEAM-CROSSING`).
- **v2 (R47-H2), key unknown.** The key came from a stated family of 65,536 keys, which the repo's decoder
  searches exhaustively when the word spaces are true. The finish-line rule was fixed before any number
  (H1 PREREG Addendum 3): FINISH = max(0.80, best in-house attack + 0.20). If that came out above 0.95, C10
  would not be offered.

| seed 4710, 100 plants + 100 nulls | plants recovered | null FP | time per unit |
|---|---|---|---|
| (i) all 65,536 keys, TRUE lengths (ceiling) | 100/100 | 0.00 | ~7 s |
| (ii) all keys, jumps at the PRINTED starts (L1 rule) | 0/100 | 0.00 | ~7 s |
| (iii) X1's beam run per key | correct key wins against 1,024 sampled wrong keys, 16/16 units | — | ~0.2 s per key, ~3.7 h per unit |
| (iv) rank all keys by the printed-start decode, X1's beam on the top 64 | 78/100 | 0.00 | ~11 s |
| (iv) the same, top 512 | **88/100** | 0.00 | ~88 s (7 jobs in parallel) |

The obvious composition, a cheap key screen followed by the known-key beam, already reaches 0.88. So the rule gives
1.10, and C10 is retired rather than published with an easy line. The checker
(`challenges/c10_shuffled_lengths.py`) stays as an instrument. **Round 48** re-scopes it with a larger key family,
the doublet filter, or the other word-indexed constructions (R41 W1–W4, G3 lagged pointers, the lexicon rows).
The (iv) result is itself useful: an unknown-key sweep that survives (b′) for the U2b class costs about 11–88 s
per unit over a 2¹⁶-key family, so a (b′)-robust re-run of `R46-L1-R37-U2B-U3-RECHECK` is affordable in-house.

### C11 — Decode the constructions the coin hides *(heavy lift, opened by Round 48 / M1)*

LP2 has 86 doubled runes where chance gives 447. Every decoder here assumes one explanation: the encipherer
skipped a key symbol on a would-be doublet, with probability 0.813. Round 48 / M1 showed that this is one of
four constructions that produce **exactly the same statistics on the printed runes** (independent steps that
are zero with a small probability), so no test on the ciphertext can prefer it. As ciphers they are different,
and with the **correct key in hand** the reference beam reads none of the other three:

| variant | what the encipherer did | reference beam, correct key |
|---|---|---|
| KEYSKIP (control) | the construction every beam here is built for | 40/40 |
| **V-DELETE** *(scored)* | strict filter, then 18.7 % of the cipher runes were deleted | **0/40** (recovery 0.31, which is what two unrelated rune strings score; reads as noise) |
| **V-SILENT** *(scored)* | cipher works mod 36; 7 symbols print nothing; word space is a plaintext symbol | **0/40** (0.27) |
| V-TWOLAYER *(diagnostic)* | strict filter under a second shift that jumps every ≈ 5 runes; shift not given | 0/40 (0.30) |

**Task:** `decode(C, K, variant) -> {"plain_idx": [...]}`. You get the printed runes and a key that is either
right or wrong. A plant passes when you recover ≥ 0.85 of the recoverable plaintext (longest common
subsequence) and your right-key output scores above your wrong-key outputs.

**Finish line:** ≥ 80 % of plants on both scored variants at `--plants 40`, maintainers' seed, held-out text.

**What a crossing changes:** it is the instrument needed to re-run the ledger's beam negatives under
constructions that fit LP2 as well as the one they assumed. Until it exists, those negatives say nothing
about three quarters of the constructions consistent with the data. V-TWOLAYER is open in a stronger sense:
nobody has shown whether 240 runes carry enough redundancy to recover the unknown shift at all. A bound either
way is a ledger row.

**Rough cost:** 1–5 M agent tokens; the checker runs in under a minute with a fast decoder. V-DELETE is a
beam over (key pointer, deletions); V-SILENT needs a decoder that tracks unseen symbols and works mod 36.

```bash
python challenges/c11_alt_constructions.py --self-test          # the baseline above
python challenges/c11_alt_constructions.py my_decoder.py
```

### C12 — Reproduce 14 runes with a generator *(heavy compute, opened by Round 48 / M1)*

One reading of LP2 has no language model, no scorer and no judgement call: **the pages are the output of a
seeded pseudo-random generator**, either with no message at all or as a keystream somebody can regenerate. If
that is true, some (generator, seed) reproduces a run of the printed runes **exactly**, and a 14-rune match
cannot be argued with.

Round 48 / M1 ran the cheap part: Perl `drand48`, bash 4.2 `$RANDOM` (64- and 32-bit), glibc `rand`, CPython 2.7
`random`, MSVC `rand`, the ANSI C LCG and minstd, **every 32-bit seed**, a no-repeat picker over 29–40 symbols,
two reductions, two rune orders, every alignment: ≈ 8.2 × 10¹¹ streams, **0 hits**, longest chance run 11
(`liber-primus/analysis/round48/M1-leak-census/`, C source `repro.c`, ≈ 1–4 µs per seed per core).

What is left needs compute this project does not have. Each line is a separate claimable target:

| target | size | why it is plausible |
|---|---|---|
| `drand48` / Perl with the full 48-bit state | 2⁴⁸ | Perl seeds from more than 32 bits when it can; 65,536 × our run |
| Java `java.util.Random` | 2⁴⁸ | same LCG family, different output bits |
| MT19937 `init_genrand(seed)`: PHP `mt_rand`, C++ `std::mt19937`, NumPy `RandomState`, Ruby | 2³² each | we covered only CPython 2.7's `init_by_array` path |
| CPython 3 `random.seed(int)`; `randrange` / `choice` / `shuffle` instead of `random()` | 2³² each | library wrappers add their own rejection loops |
| TeX / pgf `\pgfmathrandom`, Lua `math.random`, awk `rand()` | ≤ 2³² each | the pages were typeset; see `round18/L1-toolchain` |
| other pickers: shuffled symbol table, a draw per word, `randint(1, 29)` with its own retry | × your choice | our picker is one guess at the program |

**Task:** adapt `repro.c` (or write your own), sweep a target, and feed any long run to the checker.
**Finish line:** an exact run of length R with 2^B · 25,912 / 29^R < 0.001, where 2^B counts every stream you
tried (R = 14 at our search size, 17 at 2⁵³·⁶, 19 at 2⁶⁴). Then we re-run your program and seed.

**A clean negative counts**, if it comes with a planted control (splice a known-seed run into the stream and
show your sweep finds it): it becomes a ledger row with your name and the exact coverage.

**What a crossing changes:** everything. It would be the first key material for LP2 ever recovered.
Stated prior, so nobody is misled: low, on the order of a percent across all targets.

```bash
python challenges/c12_generator_hit.py --self-test
python challenges/c12_generator_hit.py emitted.txt --log2-search 53.6
```

### Copy-paste prompts for your agent

Each block below is self-contained. Paste it into your agent from the repo root.

<details><summary><b>C7 prompt</b></summary>

```text
You are working in a clone of github.com/Dukotah/cicada3301. Goal: CHALLENGES.md challenge C7. Build a
Gematria Primus reference corpus in a register not yet covered: not English, not classical Latin, German,
Welsh or Old English. Good targets: Koine Greek, Biblical Hebrew, Old Norse, Middle English, Vulgate Latin.
1. Read CHALLENGES.md (C7), challenges/c7_corpus_forge.py (docstring) and the worked example
   challenges/examples/c7_latin_aeneid/manifest.json.
2. Find a PUBLIC-DOMAIN source text of >= 20,000 words. Record title, author, edition, URL and licence, and
   save it unchanged as source.txt. Put its sha256 in the manifest.
3. Design the transliteration table (source graphemes -> the 29 GP tokens). Justify every non-obvious
   choice in a "_comment" field: digraphs, letters with no GP equivalent, diacritics.
4. Run: python challenges/c7_corpus_forge.py <dir>/manifest.json --build. Fix every error it prints
   (unmapped letters, too small) until it exits 0.
5. Report the JSON row it prints, and whether crosses_finish_line is true. Do not edit the checker.
```
</details>

<details><summary><b>C8 prompt</b></summary>

```text
You are working in a clone of github.com/Dukotah/cicada3301. Goal: CHALLENGES.md challenge C8. Write a
scorer for ONE plaintext register that panel-R36 does not model. Panel-R36 has EN_MODERN, EN_KJV,
LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL, GREEK, HEBREW and NORSE.
1. Read CHALLENGES.md (C8) and challenges/c8_register_scorer.py. Run its --self-test and read the
   baseline table.
2. Pick the register. Get TRAINING text and separate HELD-OUT text, both public domain, with no overlap
   between them. Make them runes via a C7 manifest (challenges/c7_corpus_forge.py), or use Latin-alphabet
   text if the GP greedy fold is faithful for that language.
3. Write my_scorer.py with REGISTER = "<NAME>" and score(idx) -> float. Rune indices are 0-28. The model
   must be trained only on the training text.
4. Iterate with: python challenges/c8_register_scorer.py my_scorer.py --heldout <heldout> --direct
   Then confirm WITHOUT --direct. Target: power >= 0.80 at L=236 against every null class. The shuffled
   null is the hard one, so model sequence, not letter frequency.
5. Report the full output, including the incumbent (panel-R36) line. Never train on the held-out text.
```
</details>

<details><summary><b>C9 prompt</b></summary>

```text
You are working in a clone of github.com/Dukotah/cicada3301. Goal: CHALLENGES.md challenge C9. Write a
decoder that recovers plaintext under the rejection loop V-NULL (on a would-be doublet a null rune is
inserted and the rejected key symbol is discarded). It must still pass the C3 gates.
1. Read CHALLENGES.md (C3, C9), liber-primus/benchmark/README.md, challenges/c9_rejection_loops.py (the
   variant enciphers are the ground truth) and liber-primus/analysis/campaign18_skip/skipdecode.py
   (the reference beam). R47-X1's probe (liber-primus/analysis/round47/X1-redteam/x1_c9_ext_decoder.py)
   got 8/40 on V-NULL; start there if you like.
2. Run python challenges/c9_rejection_loops.py --self-test to see the baseline: both beams recover 0 V-NULL plants.
3. Write my_decoder.py with decode(C, K, sign=-1) -> {"plain_idx": [...]}. Return the plaintext WITHOUT
   nulls. It runs in an isolated child process and only gets (C, K, sign); the checker re-scores your output.
4. Iterate: python challenges/c9_rejection_loops.py my_decoder.py (C3 gates + 12 plants per variant).
   Then run --plants 40. Keep wrong-key false positives <= 5%: a decoder that turns every key into English
   fails. V-BACK is reported but not scored.
5. Report the output. Do not edit the checker or the variant enciphers.
```
</details>

<details><summary><b>C11 prompt</b></summary>

```text
You are working in a clone of github.com/Dukotah/cicada3301. Goal: CHALLENGES.md challenge C11. Write a
decoder that recovers English plaintext, key in hand, under V-DELETE (strict doublet filter, then 18.7 % of
cipher runes deleted) and V-SILENT (cipher mod 36, 7 silent symbols, word space = plaintext symbol 29).
1. Read CHALLENGES.md (C11), challenges/c11_alt_constructions.py (the enc_* functions are the ground truth),
   liber-primus/analysis/round48/M1-leak-census/RESULTS.md section 1, and the reference beam
   liber-primus/analysis/campaign18_skip/skipdecode.py.
2. Run python challenges/c11_alt_constructions.py --self-test to see the baseline (0 plants on every variant).
3. Write my_decoder.py with decode(C, K, variant) -> {"plain_idx": [...]}. It runs in an isolated child
   process and gets only (C, K, variant). K may be the wrong key: do not force English out of every key.
4. Iterate: python challenges/c11_alt_constructions.py my_decoder.py   then --plants 40.
5. Report the full table. Do not edit the checker. If you conclude a variant is unrecoverable, show the bound.
```
</details>

<details><summary><b>C12 prompt</b></summary>

```text
You are working in a clone of github.com/Dukotah/cicada3301. Goal: CHALLENGES.md challenge C12. Test whether
the 12,956-rune unsolved stream is reproduced exactly by ONE generator target from the C12 table.
1. Read CHALLENGES.md (C12) and liber-primus/analysis/round48/M1-leak-census/ (PREREG.md, RESULTS.md,
   repro.c, validate_gens.py, plants.py). Build: python common.py && gcc -O3 -march=native -fopenmp -o repro repro.c
2. Pick a target nobody has claimed (check the issues). Implement the generator in repro.c and validate its
   first outputs against the real library before sweeping anything.
3. Plant: splice a run from a known seed into the stream and show your sweep reports that seed.
4. Sweep. Log every run of 10 or more runes. State exactly which seeds, pickers and alignments you covered.
5. For any long run: write the emitted rune indices to a file and run
   python challenges/c12_generator_hit.py emitted.txt --log2-search <log2 of all streams you tried>
6. Report coverage, the plant result, the near-miss count against the chance count, and any hit.
```
</details>


---

## Rules that apply to every challenge

- **Check the ledgers first.** Ours (`liber-primus/LEDGER.json`) and njloof's
  ([`docs/LEDGER.md`](https://github.com/njloof/cicada-lp2-sweeps/blob/main/docs/LEDGER.md));
  [`docs/CROSS-LEDGER.md`](docs/CROSS-LEDGER.md) maps one onto the other.
- **Don't tune to the checker's fixed inputs.** C2 and C5 are re-run on inputs you haven't
  seen before we credit them; C8, C9 and C11 are re-run at a sealed seed on held-out text, and C7's
  register is checked by a human reading your source and table.
- **A clean negative counts.** If you work a challenge properly and it doesn't go, file what
  you tried; for C5 and C6 a documented failure is a ledger row.
- **Page numbers ≥ 50:** read [`liber-primus/data/PAGE-NUMBERING.md`](liber-primus/data/PAGE-NUMBERING.md).
- **Say what tools you used.** Most contributions here are a person plus an AI agent.

## Hall of fame

| who | what | where |
|---|---|---|
| **njloof** | p15 grid closed form: all 16 cells = \|3301 − prime(F+1)\|, Fibonacci F on a spiral from the red 3299 — first complete read of a printed LP2 object | [#14](https://github.com/Dukotah/cicada3301/issues/14), ledger `R45-COMM-P15GRID-CLOSEDFORM` |
| **njloof** | Page numbering from 50 on, traced to the runes-only extraction; book p51 read 92/92 | [#14](https://github.com/Dukotah/cicada3301/issues/14), `liber-primus/data/PAGE-NUMBERING.md` |
| **njloof** | Reproduced T7 with independent nulls; corrected our "doublet-free" mislabel | [#13](https://github.com/Dukotah/cicada3301/issues/13), [njloof/cicada-lp2-sweeps](https://github.com/njloof/cicada-lp2-sweeps) |
| **RETSAM3301** | Separator corrections on seg 8 and seg 40; first image-to-page mapping | [#12](https://github.com/Dukotah/cicada3301/issues/12) |

Your name goes here when a checker says you're done and we confirm it.
