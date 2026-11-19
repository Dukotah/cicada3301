# Challenges — bounded problems with a finish line you can check yourself

**Nobody has solved Liber Primus 2**, and this page doesn't pretend you will this weekend.
What it offers instead is seven problems that each have a **checker you can run**, a
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
seed. 351 ledger rows record what has been tried.

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

## Rules that apply to every challenge

- **Check the ledgers first.** Ours (`liber-primus/LEDGER.json`) and njloof's
  ([`docs/LEDGER.md`](https://github.com/njloof/cicada-lp2-sweeps/blob/main/docs/LEDGER.md));
  [`docs/CROSS-LEDGER.md`](docs/CROSS-LEDGER.md) maps one onto the other.
- **Don't tune to the checker's fixed inputs.** C2 and C5 are re-run on inputs you haven't
  seen before we credit them.
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
