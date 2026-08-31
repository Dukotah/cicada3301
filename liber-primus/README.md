# Liber Primus

[![CI](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml/badge.svg)](https://github.com/Dukotah/cicada3301/actions/workflows/ci.yml)

The runic "First Book" that the 2014 Cicada 3301 puzzle pointed to as the ongoing
challenge. ~58 pages in the **Gematria Primus** runic alphabet (each rune maps to
a letter *and* a prime). This folder holds the transcription, a validated
cryptanalysis rig, a provenance-verified dataset, and the consolidated findings.

> **Start here:** [`SOLVERS-DOSSIER.md`](SOLVERS-DOSSIER.md) — what's verified,
> what's ruled out (with reproduce commands), and the genuinely open threads.

## Quick status
- A minority of pages are decrypted (A Warning, Welcome, Some Wisdom, An End, Parable).
- The majority remain **unsolved** and are **one-time-pad-class** (full-length
  keystream + a no-repeat rule) — i.e. unsolvable from ciphertext alone without
  the key. Solved pages used Atbash / Vigenère (DIVINITY, FIRFUMFERENFE) / totient
  keystreams + the ᚠ interrupter rule.

## Latest rounds (2026-08)
- **Round 18** proved the project had been searching with a *broken magnet* — every prior
  negative is English-register-only, and the beam represented exactly one enciphering relation.
- **Round 19** *rebuilt* the magnet (a drift-tolerant decoder, a nine-register adjudicator,
  recalibrated nulls — the historical −5.5 bar was wrong in 14/14 sweeps, but **no verdict flips**),
  and found it could not yet affordably sweep. Canon upheld **450/450**; 3 payload bytes corrected.
- **Round 20** tried to build the missing *sieve* that would make the enumerable PRNG sweeps
  affordable. It is **infeasible** at the required ≥100×-reduction / 0.90-survival target
  (best 0.667) — but the round also shipped the **recovery-gated hit function** (`hitfn20`:
  a decode is a HIT only if it clears the calibrated null AND recovers ≥0.90 of rune indices
  AND reproduces on the held-out ¾), and its follow-up ran the project's **first power-1.00
  sweep** (Py2.7 `random29`, 0.057 % of 2³², 0 hits).
- **Round 21** found the **no-oracle mode of that gate provably leaky** (best fold 0.80 vs the
  0.90 bar) — so any bar-clearing survivor is *flagged-for-oracle*, never auto-certified —
  swept the three remaining Py2.7 reducers + the amd64 map clean (884,000 words, 0 hits), and
  measured the `n_skips` window: **≥ ~6000 runes** before that statistic alone discriminates.
- **Round 22** turned from the letter stream and **read every channel the signed hints point
  at, for the first time** — message-inside-the-solved-plaintext, numbers-as-direction turtle
  render, koans-as-operations, art-as-data drop-caps. All four: clean, control-validated
  negatives; red-team NO-ERROR-FOUND.
- **Round 23** read the one representation Round 22 could not — the **printed-line-geometry
  acrostic** at true page-image line breaks. Clean null. With it, every roadmap-named lens has
  been read at least once at the tested resolution.
- **Round 24** discharged the two instrument conditionals hanging over every negative since
  Round 18: re-adjudicated the strongest sweeps under **non-English / matched-runic scorers**
  (L7-A) and under a decoder that **can represent `skip_by_two`** (L7-B), across 7 generator
  axes. **The negatives hold under both corrections.**
- **Round 25** is the owner-elected compute grind of the last runnable branch — the Py2.7-MT
  2³² seed tail — **parked mid-sweep at 0.5015 % coverage, 0 hits**, fully resumable from
  committed checkpoints.
- **Round 26** fired the three *built-but-never-swept* instruments and one live reframe, each
  control-validated first: the **Perl `rand`** (R19-G2, previously **zero** seeds) and **TeX RNG**
  (G4-TEX, previously **zero** decodes) generators got their first-ever scored decodes; the Py2.7
  reducers were swept on the **distinct amd64-w64 / non-zero-offset / `skip_by_two`** axis R21-L3
  never touched (Lane A). **R12-C2's staged-but-never-run 33-keytext running-key sweep** finally ran,
  skip-aware (Lane B, 0/1,562 clears). And the **semantic-seed** reframe — *the puzzle must be
  solvable, so try each corpus value AS A SEED* through the generator zoo incl. the totient/prime
  ladder that solves page 05 — swept **100 % of a bounded 323-value set × 7 generators** (Lane C,
  flat-random, 0 escalated). All three **HARDEN** the branch along previously un-swept axes; red-team
  **NO-ERROR-FOUND**, **0 oracle flags, no stop-and-alert**.

The standing verdict through all of it: **LP2 0–54 is OTP-class**, with a soft anti-repeat
rewrite acting on the ciphertext output. → [`PICKUP-HERE.md`](PICKUP-HERE.md).

## Quickstart

```bash
cd liber-primus
pip install -e .            # installs the `lp` core library (gematria/ciphers/stats/...)
                            # (image tools also need: pip install numpy pillow)
                            # the solver CLI runs directly, no install needed:

# 1) prove the rig reproduces every known solved page
python tests/validate.py

# 2) test YOUR key/method hypothesis against all pages (with a sanity gate)
python lp_try.py --key DIVINITY            # vigenere, subtract, interrupters
python lp_try.py --keystream totient       # totient(prime) keystream
python lp_try.py --selftest                # prove the scorer separates English from ciphertext

# 3) run the analyses (auto-fetch third-party sources as needed)
python analysis/run_stats.py               # statistical profile
python analysis/crypto_rigor.py            # last structural attacks (all closed)
python analysis/structure_analysis.py      # interrupter / boundary / per-page probes
python analysis/transcription/crossdiff.py # all transcription lineages are rune-identical

# regression gate
pytest -m "not network"          # fast subset; `pytest` for the full gate
```

**Shortcut — `tasks.py` runner:** `python tasks.py <task>` wraps the common jobs:
`validate`, `test` (fast) / `test-full`, `analyze` (hardening probes),
`seek` (answer-seeking probes), `cross`, `dataset`, `fetch`, `all`, and
`evo` (dual-track: harden **and** seek in one go).

## The dataset
[`dataset/liber_primus.json`](dataset/liber_primus.json) — one machine-readable
corpus to build on:
- `gematria`: the 29-rune table (index, rune, transliteration, prime)
- `pages[]`: per page → `runes`, `translit`, `indices`, and `image` (sha1/md5 +
  `provenance_verified` against the archived onion7 release)
- `solved_pages_reference`, `ruled_out`, `open_threads`, `statistical_profile`

Rebuild: `python dataset/build_dataset.py`.

## Layout
- `src/lp/` — core library: `gematria`, `ciphers`, `stats`, `score`, `solve`
- `tests/` — `validate.py` (reproduces solved pages) + `test_rig.py` (pytest gate)
- [`analysis/`](analysis/README.md) — 183 scripts across 22 campaigns; the folder's
  README maps each one to the campaign and finding it produced
- `data/` — committed: transcription + quadgram model; `fetch_sources.py` pulls the
  gitignored third-party transcriptions on demand
- `dataset/` — the canonical JSON corpus
- [`docs/`](docs/README.md) — reference material + superseded snapshots
- [`outreach/`](outreach/README.md) — community post drafts
- `attack.py` — vigenere/runningkey/keystream attack CLI (`selftest` re-finds DIVINITY)

## The three canonical docs
| Doc | What it holds |
|---|---|
| [`ELIMINATION-LEDGER.md`](ELIMINATION-LEDGER.md) | Everything tried and why it's eliminated — read this before attacking LP2 |
| [`FINAL-SYNTHESIS.md`](FINAL-SYNTHESIS.md) | The terminal verdict on both goals: the solve and the attribution |
| [`SOLVERS-DOSSIER.md`](SOLVERS-DOSSIER.md) | The community-facing writeup, with a reproduce command per claim |

See [`../research/06-liber-primus-status.md`](../research/06-liber-primus-status.md) for
the long-form status writeup.
