# Contributing — for people, and for the AI agents they point at this repo

Most outside contributions here have come from one person working with an AI agent
(Claude Code, ChatGPT, and others). That works well, and this page is written so your
agent can follow it without asking. If you are an agent, read [`AGENTS.md`](AGENTS.md) §1
first for the state of play, then come back here.

**Nobody has solved LP2.** Everything here is measured elimination plus a short list of
open anomalies. A contribution is valuable if it is **reproducible, powered, and checked
against what has already been tried**, whether it comes back positive or negative.

**Looking for something bounded?** [`CHALLENGES.md`](CHALLENGES.md) lists seven problems,
each with a checker you can run and a finish line written down in advance.

## What we want, in order of value

1. **Independent replication** of a live finding. Right now that is the T7 anomaly: the
   doublet slip rate is not stationary across the book (`LEDGER.json` row
   `R44-W2B3-D01-FALSIFIER`). It has one external replication so far (njloof, campaign #10).
2. **Data and transcription corrections** with image evidence. These have been the
   highest-yield outside contributions: #12 (separators) and #14 (page numbering from 50 on).
3. **Instrument audits.** Find a hole in a closure, a null, a decoder or an input. Every
   genuinely new result in this project came from one of those, not from a bigger sweep.
4. **Powered negatives** on a lane in [`docs/OPEN-LANES.md`](docs/OPEN-LANES.md) or in
   another ledger's `not_covered` list.

## The five rules (same ones we hold ourselves to)

1. **Check both ledgers before you start.** Ours is `liber-primus/LEDGER.json` (query
   `coverage` and `not_covered`). The other active one is
   [njloof/cicada-lp2-sweeps `docs/LEDGER.md`](https://github.com/njloof/cicada-lp2-sweeps/blob/main/docs/LEDGER.md).
   [`docs/CROSS-LEDGER.md`](docs/CROSS-LEDGER.md) maps one to the other.
2. **Pre-register.** Commit a `PREREG.md` (hypothesis, statistic, null, threshold, what
   counts as a hit) *before* the first output. Amendments before output are fine if dated.
3. **Plant a positive control.** Show your method finds a real signal of the shape you
   are looking for. A negative with no power number is not a result.
4. **Calibrate against a null of the max**, built by re-running the identical search on
   shuffled or surrogate inputs. Not a Bonferroni band. Nulls are family-specific; do not
   borrow another family's threshold.
5. **Stay language-agnostic at the decision level**, or say clearly that your negative is
   English-only. Every pre-Round-19 negative here was English-only, and that cost months.

The full doctrine is [`liber-primus/ARMADA-DOCTRINE.md`](liber-primus/ARMADA-DOCTRINE.md).

## Page numbering — read this before citing any page ≥ 50

Segment indices are book page minus one from 50 onward. Book page 50 has no runes. See
[`liber-primus/data/PAGE-NUMBERING.md`](liber-primus/data/PAGE-NUMBERING.md).

## How to submit

- **Claim a lane** before a long run, so two agents don't spend a week on the same space:
  open an issue with the *Claim a lane* template.
- **Report a result:** open an issue with the *Result* template, linking your repo or a
  PR. Fill in the ledger-row fields; that's what we copy into `LEDGER.json`.
- **Data correction:** use the *Data correction* template. Image evidence and pinned
  source commits, please.
- **Questions and loose ideas:** use Discussions, not issues.
- Say which AI tools you used. It's useful context, not a mark against you.

## Credit

Accepted contributions are credited by name in the commit, in the ledger row's `notes`,
and in the doc they change. If you run your own repo, we link it from `docs/CROSS-LEDGER.md`.

## Before a PR

```bash
cd liber-primus
python tests/validate.py            # must reproduce every solved page
python -m pytest -q -m "not network"
python analysis/handoff/validate_ledger.py
```

Content you contribute is under the repo's MIT `LICENSE`. Puzzle artefacts keep their
original attribution.
