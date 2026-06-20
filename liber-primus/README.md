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
pytest tests/test_rig.py -q
```

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
- `analysis/` — statistical, structural, vision, stego, and transcription probes
- `data/` — committed: transcription + quadgram model; `fetch_sources.py` pulls the
  gitignored third-party transcriptions on demand
- `dataset/` — the canonical JSON corpus
- `attack.py` — vigenere/runningkey/keystream attack CLI (`selftest` re-finds DIVINITY)

See `research/06-liber-primus-status.md` for the long-form status writeup.
