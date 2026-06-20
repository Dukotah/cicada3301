# Liber Primus — Solvers' Dossier

A consolidated, reproducible contribution to the community effort on the
**unsolved Liber Primus pages (LP2, onion7 `0.jpg`–`55.jpg`; `56`=AN END and
`57`=PARABLE are solved)**. Everything here is backed by code in this repo and
written so others **do not re-run the dead ends**. Run `tests/validate.py` first —
it confirms the rig reproduces every known solved page, which is the trust anchor
for all the negative results below.

> Honest headline: from the **ciphertext alone**, the unsolved pages are
> **one-time-pad-class** — a full-length keystream with a deliberate no-repeat
> rule — and are information-theoretically unsolvable **without the key**. The
> transcription is *not* the blocker (verified). The realistic path to a solve is
> **external**: the key, most plausibly via the AN END deep-web page.

---

## 1. Verified provenance of the page images (new — please reuse)

Stego and any pixel/byte analysis only survive in byte-exact originals. We
hash-verified the circulating image set against the archived onion dump:

- The widely-used relikd/LiberPrayground images are **byte-identical to the
  original onion7 release**: **56/56 SHA1 match** the values published in the
  Internet Archive item `ky2khlqdf7qdznac.onion` (the archived 7th hidden service
  Cicada used to dump LP2 in May 2014). Table: `analysis/stego/provenance.json`.
- Fingerprint of an authentic original: 2400×3600 JPEG, JFIF **400 DPI**, with a
  uniform 2576-byte **"Artifex Software 2011" sRGB ICC profile** (the Ghostscript
  production artifact). The same fingerprint appears across relikd, rtkd/iddqd,
  krisyotam and archive.org — i.e. these are Cicada's rendered output.
- **Do NOT analyze Imgur/re-saved copies** for stego: re-encoding destroys it.

## 2. Statistical profile (reproduce: `analysis/run_stats.py`)
Over 12,956 unsolved runes:
- **IoC·N = 1.000** — at the random floor (perfectly flat).
- **Doublet rate 0.66%** vs 3.45% random — a ~5× *deficit*.
- **Consecutive differences** `c[i]−c[i−1] mod 29` flat-random **except a hole at 0**
  (adjacent runes are almost never equal).
- Shannon entropy ≈ 4.857 / 4.858 bits (max for 29 symbols ≈ 4.858).

## 3. Ruled out — with the reason and the reproduce command
| Attack | Verdict | Why / where |
|---|---|---|
| Every periodic key, len 1–40 (Friedman/column freq, both dirs, +Atbash) | dead | gibberish (best −5.8); `attack.py vigauto` |
| Running keys from the referenced texts + solved plaintext | dead | `attack.py runningkey` |
| Number-theoretic keystreams (primes, φ, iterated φ, gaps, cumsums, page-seeded, Fibonacci) | dead | `attack.py keystream`, `analysis/doublet_probe.py` |
| Plaintext & ciphertext **autokey** | dead | differences flat-random; `src/lp/autokey.py` |
| First-difference / **integral** inversion | dead | integrating normalizes doublets but stream stays flat; `analysis/armada/FOLLOWUP-TESTS.md` |
| **Page-on-page** key reuse / in-depth | dead | no shared-keystream signal |
| **Fractionation** (bifid/Polybius) | dead | can't reach flat IoC 1.0 or the deficit (`analysis/OPEN-AVENUES.md`) |
| Substitution / homophonic | dead | preserves IoC; can't turn flat→English |
| **Transposition-only** | dead | doublet-transparent; falsified by the *suppressed* doublet rate |
| **Block / permutation / Lehmer decode** (F-delimited) | dead | F-run lengths have no peak (modal share 0.055); `analysis/crypto_rigor.py` A |
| **No-repeat / collision inversion** decodes (delta≠0 family) | dead | IoC stays flat (≤1.04); `analysis/crypto_rigor.py` C |
| **Independent AI-vision re-transcription** | not viable | mean alignment 0.145 — vision can't read dense rune pages; `analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| **Image steganography** (appended/EXIF/LSB/carve/color/OutGuess) | none | `analysis/stego/STEGO-VERDICT.md` |

## 4. Verified POSITIVE (so you can trust these inputs)
- **Transcription is correct.** Every community lineage — krisyotam, relikd
  (different delimiters, independently "double-checked"), and the rtkd/iddqd 2017
  root — is **rune-for-rune identical (13136/13136, 0 divergences)**;
  `analysis/transcription/crossdiff.py`. The rtkd baseline was image-error-corrected
  via PRs (2017–21); we spot-verified sample lines by eye against the authentic
  images (`analysis/transcription/linecrop.py`). Caveat: all lineages share the one
  2017 root, so this is consensus+audit, not a from-scratch independent re-read.
- **The no-repeat rule is structural, not a reading-order artifact.** File order is
  the unique doublet-suppression minimum; every transposition restores doublets
  toward random (`analysis/crypto_rigor.py` B).
- **The rig reproduces all solved pages** (atbash / shift / Vigenère DIVINITY /
  Vigenère FIRFUMFERENFE / totient): `tests/validate.py`.

## 5. The load-bearing conclusion
Perfect IoC flatness (1.00) is reachable only by a **full-length keystream**
(one-time-pad-class); fractionation/substitution top out ~1.4–1.5. Add the
deliberate no-repeat constraint (the doublet deficit + structural delta=0 hole)
and the exhaustive key-search failure, and the pages are
**information-theoretically underdetermined without the key** — for any chosen
plaintext a valid structureless key exists (`analysis/SOLVE-ATTEMPT-FINAL.md`).
They are not "hard"; absent the key they are unsolvable by ciphertext-only analysis.

## 6. Genuinely open (where help is worth it)
1. **The AN END deep-web page** (hash `36367763…c2a8b4`) — the one place a key may
   physically exist. Never found; "hash-as-ed25519-onion" tested and FAILED; Tor v2
   deprecated Oct 2021. Status + leads: `analysis/DEEPWEB-HASH-OSINT.md`,
   `analysis/KEY-HINT-RESEARCH.md`.
2. **A from-scratch independent re-transcription.** All machine-readable
   transcriptions descend from the one 2017 root; AI vision can't produce an
   independent one. A careful human re-read from the authentic images is the only
   way to fully exclude a shared-root error (low prior — it would have to survive
   the solved-page decryptions).
3. **OutGuess control run** (Linux): confirm the LP2 OutGuess "garbage" blobs
   (shared 1417-byte prefix) are a default-key/blank-margin artifact, not a
   passphrase-locked payload. See `analysis/stego/STEGO-VERDICT.md`.

## 6b. The keystream is one continuous stream over the whole book
The no-repeat suppression holds across **every** boundary — word, clause, line,
and even page joins (page-boundary doublet rate = 0.0000). So the keystream does
**not** reset per page/paragraph; it spans the entire concatenated book. There is
no boundary where it restarts, so per-page/in-depth-at-boundary attacks don't
apply. Also: the ᚠ-interrupter carries no hidden ASCII/sequence, and **no page is
a non-flat outlier**. Details + the F-count sequence (for OEIS-checking):
`analysis/STRUCTURE-FINDINGS.md` (reproduce: `analysis/structure_analysis.py`).

## 7. Tools & data in this repo (build on these)
- **`dataset/liber_primus.json`** — one machine-readable corpus: gematria, per-page
  runes + transliteration + indices, **verified image hashes**, solved-page keys,
  ruled-out registry, stats. (`dataset/build_dataset.py`)
- **`lp_try.py`** (`pip install -e .` → `lp-try`) — test any key/method against all
  pages with quadgram scoring + a built-in sanity gate. `python lp_try.py --selftest`.
- `attack.py` (vigenere/runningkey/keystream, self-validating) · `tests/validate.py`
  · `analysis/run_stats.py` · `analysis/crypto_rigor.py` · `analysis/structure_analysis.py`
  · `analysis/vision/` · `analysis/stego/stego_scan.py` ·
  `analysis/transcription/crossdiff.py` + `linecrop.py`. Core lib in `src/lp/`.

*Shared in the spirit of the puzzle: verify, don't trust. PGP-authenticate any
claimed key against Cicada's key 7A35090F.*
