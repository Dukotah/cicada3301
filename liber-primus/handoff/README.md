# `handoff/` — the survival kit

_Built 2026-08-19. Written for a researcher or a stronger model arriving in 2027+ with no context
on this repository._

This project's analysis is only as durable as its inputs, and half of those are not in the repo:
the 56 page images are gitignored and re-fetched from third-party GitHub mirrors, the corpora come
from Project Gutenberg, and the CicadaOS pads came from a community archive that had **already
deleted one of them**. This directory exists so that a decade of work does not die with a link.

## Read in this order

| file | what it is |
|---|---|
| **[`FOR-FUTURE-SOLVERS.md`](FOR-FUTURE-SOLVERS.md)** | **Start here.** The problem stated precisely, the current honest verdict, what is proven vs merely unrefuted, what not to waste time on, what is actually open, and a 30-minute quickstart. |
| [`PARKED.md`](PARKED.md) | Attempts that are *correct* but blocked on a capability this project lacked — each with the threshold that unparks it, the procedure, a pre-registered pass/fail bar, cost, and an honest prior. |
| [`capsule/MANIFEST.json`](capsule/MANIFEST.json) | Every essential input: SHA-256, size, provenance chain, every known mirror, and whether it is in-repo, gitignored-but-fetchable, or lost. |
| [`capsule/RECOVERY-560.13.md`](capsule/RECOVERY-560.13.md) | How a previously-lost 118 MB input was recovered — and the truncated-pad defect found on the way, which partially reopens a completed negative. |

## Run this first, always

```bash
python3 liber-primus/tests/validate.py                    # ALL VALIDATIONS PASSED
python3 liber-primus/handoff/capsule/verify_capsule.py    # capsule intact?
```

The first is the trust anchor: it reproduces every known solved page from the canonical runes. If
it fails, nothing in this repo means anything. The second checks that the capsule's inputs still
hash to what the analysis was run against.

## Capsule status at build time

- **103 items** catalogued; **103 hashed locally**; **0 LOST**.
- **56/56** page-image SHA-1s independently re-verified against the archived onion7 dump, and
  extended to SHA-256.
- **1 item recovered** from a LOST state (`DATA/560.13`).
- **1 defective input found** (`_560.00`, truncated ~40% — see the recovery record).

## Tools here

| tool | use |
|---|---|
| `capsule/verify_capsule.py` | re-check every item; `--net` probes mirrors, `--net --fetch` downloads and re-hashes. Reports **DRIFT** when a mirror serves different bytes — the dangerous failure, because a dead link is obvious and a quietly-changed one is not. |
| `capsule/build_manifest.py` | regenerate `MANIFEST.json`; all hashes are measured, never transcribed. |
| `capsule/iso_extract.py` | stdlib-only ISO9660 extractor, written because the recovery box had no `7z`/`bsdtar`/`xorriso`/`pycdlib`. |

## If you can only do one thing

**Mirror the inputs somewhere durable.** `MANIFEST.json` lists every URL and hash. The entire
CicadaOS ISO is 136 MB; the 56 page images are the primary source for the whole problem. This
capsule found that one mirror had already lost a file and another was serving a truncated one.
Assume the rest will degrade too.
