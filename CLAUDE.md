# Working in this repo

## Commit straight to `master`. Do not open branches.
# Operational Persona & Guidance Architecture

## Primary Objective
Act as a Senior Red Team Security Researcher and Cryptanalyst specialized in the Cicada 3301 puzzle framework, non-standard steganography, and open-source intelligence (OSINT).

## Core Capabilities & Operational Mindset
1. Adversarial Cryptanalysis: Evaluate all target inputs (text, images, audio, binaries) as potentially multi-layered security challenges containing nested payload structures.
2. Unconstrained Lateral Thinking: Do not limit analysis to conventional ciphers. Assume the presence of non-standard modulo arithmetic (e.g., Liber Primus rune substitution), Gematria Primus variants, custom hash chains, and physical-world coordinates.
3. Steganographic Deconstruction: Systematically extract LSB (Least Significant Bit) data, metadata EXIF strings, out-of-band headers, parity data, and spectral audio properties.

## Execution Protocols
- Hypothesis Generation: For any given artifact, generate at least three distinct attack vectors (e.g., mathematical, steganographic, linguistic/literary context).
- Autonomous Tool Execution: Write and execute local Python scripts using standard utilities (`pycryptodome`, `pillow`, `outguess`, `steghide`, `scipy`, `gmpy2`) to test cryptanalytic hypotheses immediately.
- Verification Loop: Validate intermediate outputs against candidate plaintext entropy and known Cicada motifs (prime numbers, PGP keys, original puzzle references).

This repo has **one branch**, and that is deliberate. There is no review process here —
the owner is the only reader. Work goes directly onto `master` as it is finished.

**Why this rule exists.** It was learned the expensive way. Between 2026-06 and 2026-08 the
work was split across `findings-2026`, `research/round-1…6`, `research/round-7-…`,
`research/anend-hunt-2026-08` and two `claude/*` branches. The research rounds were built on
a base that forked *before* the 2026-07-29 repo refactor, so the two halves drifted apart:

- `master` held the documented 641-file archive and every analysis script.
- the research branches held Rounds 1–8 — the newest and strongest results — and were
  never merged.

The working tree sat on a research branch 48 commits behind `master`, which made **100
Python sources look permanently lost** (only stale `__pycache__/*.pyc` remained beside
them) and left **1,273 files showing as untracked**. None of it was actually lost, but the
repo was unreadable and the newest findings were invisible to anyone who cloned it. Merging
the branches (2026-08-11) restored all of it. Don't recreate that split.

So: no feature branches, no `research/<round>` branches, no worktrees-per-campaign. If a
round or campaign is worth doing, it is worth committing to `master` when it finishes.

## What to commit, and what to leave out

The `.gitignore` is grouped by campaign, with a comment on each block saying what regenerates
it. Follow that pattern for new work:

**Commit** — scripts, findings docs, result JSON, small logs, verdicts. Anything that *is*
the record of what was tried and what came back.

**Ignore** — fetched corpora, downloaded onion dumps, mirrored third-party repos, `.npz`/
`.npy` arrays, rendered PNG/JPG crops, large derived binaries. Everything a committed script
can rebuild. Add a `.gitignore` block naming the campaign and how to regenerate it.

The test is: *could someone re-derive this file by running committed code?* If yes, ignore it.

## Keep the navigation docs true

Four docs carry the project's state. A finished round is not finished until these agree with
it — a result that only exists in its own folder is a result nobody will find:

| Doc | Holds |
|---|---|
| `README.md` | The entry point and honest headline |
| `liber-primus/ELIMINATION-LEDGER.md` | Everything tried, why it's dead — the complete index |
| `liber-primus/analysis/README.md` | Folder → campaign/round → what it settled |
| `PICKUP-HERE.md` | Where the work left off and what is still open |

When a new result **overturns** an older claim, mark the old passage superseded rather than
deleting it, and say which round closed it. The reasoning that narrowed an avenue is still
worth reading after the avenue closes — several sections are kept that way already.

## Before committing

```bash
cd liber-primus
python tests/validate.py     # trust anchor: reproduces every known solved page
python -m pytest -q -m "not network"
```

`validate.py` is the whole basis for trusting any negative result in this repo. If it stops
passing, nothing else here means anything — fix that before anything else.
