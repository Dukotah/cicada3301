# Analysis — map of the work

Every attack, probe and sweep run against the Liber Primus lives here: **183 scripts**
across 22 investigation folders, each paired with the findings doc it produced. Nothing in
this tree is a sketch — every negative result below was produced by code you can re-run.

> **Looking for the answer, not the archive?**
> → [`../ELIMINATION-LEDGER.md`](../ELIMINATION-LEDGER.md) — everything tried and why it's dead.
> → [`../FINAL-SYNTHESIS.md`](../FINAL-SYNTHESIS.md) — the terminal verdict.
> This file is the **navigational map**: which folder holds which campaign.

---

## Folder → campaign → what it settled

| Folder | Campaign | What it settled |
|---|---|---|
| [`foundation/`](foundation/) | III | Transcription integrity: all public transcriptions trace to one origin (rtkd/iddqd); esoterica keys null. [`CAMPAIGN-III-FINDINGS.md`](foundation/CAMPAIGN-III-FINDINGS.md) |
| [`structure/`](structure/) | IV | Doublet deficit = a uniform **soft no-repeat rule**; keystream is continuous across page joins. [`CAMPAIGN-IV-FINDINGS.md`](structure/CAMPAIGN-IV-FINDINGS.md) |
| [`stones/`](stones/) | V | Glyph classifier 99.2% → transcription verified; multiplicative gematria excluded. [`CAMPAIGN-V-FINDINGS.md`](stones/CAMPAIGN-V-FINDINGS.md) |
| [`osint/`](osint/) | VI | The 2017 PGP message carries no key; reopened pp49–51 as the one unexamined object. [`CAMPAIGN-VI-OSINT-FINDINGS.md`](osint/CAMPAIGN-VI-OSINT-FINDINGS.md) |
| [`pp49_51/`](pp49_51/) | VII, IX, XX | The base-60 table payload: 2048-bit high-entropy blob — not prime, RSA, key or text; 4×64 / AN-END-hash / XOR leads all null; external-cipher pass null. |
| [`attribution/`](attribution/) | VIII, XIX | No named author is attributable on surviving evidence; full winner/insider roster enumerated and none holds key material. [`CAMPAIGN-XIX-WITNESSES.md`](attribution/CAMPAIGN-XIX-WITNESSES.md) |
| [`armada/`](armada/), [`armada20/`](armada20/) | Armada / 20-front | Exhaustive key + keystream assault (36+ agents), 0 breaks. Eliminated the memoryless-keystream family, differencing, page-keying, stego. [`ARMADA-20-FINDINGS.md`](ARMADA-20-FINDINGS.md) |
| [`campaign12/`](campaign12/) | XII | Payload burn-down + 15 verified thematic keytexts, all null (best −6.048). [`CAMPAIGN-XII-FINDINGS.md`](CAMPAIGN-XII-FINDINGS.md) |
| [`campaign13/`](campaign13/) | XIII | +82 never-tested keytexts across 10 lanes, null (best −5.809); CT-log avenue closed. [`CAMPAIGN-XIII-FINDINGS.md`](CAMPAIGN-XIII-FINDINGS.md) |
| [`campaign14/`](campaign14/) | XIV | Fresh-eyes red-team caught 4 over-claims; all closed by measurement. [`CAMPAIGN-XIV-FINDINGS.md`](CAMPAIGN-XIV-FINDINGS.md) |
| [`independent-read/`](independent-read/) | XV | **Label-free transcription audit** — glyphs clustered by shape with the canon never shown; the canon *is* the natural visual partition (ARI 0.75). First confirmation independent of the labels. [`FINDINGS.md`](independent-read/FINDINGS.md) |
| [`stylometry/`](stylometry/) | XVI | Cicada's connected prose totals 359 words — below any attribution floor, so authorship is **un-attributable**, not merely unknown. [`FINDINGS.md`](stylometry/FINDINGS.md) |
| [`latin/`](latin/), [`bookcipher/`](bookcipher/) | XVII | Latin plaintext sealed; book-cipher pointer schemes into Cicada's known books yield only word-salad. [`CAMPAIGN-XVII-FINDINGS.md`](CAMPAIGN-XVII-FINDINGS.md) |
| [`campaign18_skip/`](campaign18_skip/) | XVIII | **Skip-tolerant decoder** that tracks the desync the doublet filter induces, then re-ran every alignment-sensitive family under it — ~200 texts, autokey, ~620 Vigenère keywords: all unconditionally null. [`CAMPAIGN-XVIII-FINDINGS.md`](campaign18_skip/CAMPAIGN-XVIII-FINDINGS.md) · [`COVERAGE-MATRIX.md`](campaign18_skip/armada2/COVERAGE-MATRIX.md) |
| [`armada_osint/`](armada_osint/) | OSINT 2026-07-27 | Pulled the onion images/HTML never held locally from community mirrors and re-extracted → no new key. [`OSINT-SWEEP-2026-07-27.md`](OSINT-SWEEP-2026-07-27.md) |
| [`recon/`](recon/) | Auditor loop 2026-07-28/29 | LP1 method dossier + LP2 structure dossier + the 11-iteration rotating-critic loop (`i2_`–`i11_` folders, one per iteration). [`RECON-SUMMARY-2026-07-28.md`](recon/RECON-SUMMARY-2026-07-28.md) |
| [`stego/`](stego/) | — | Image-stego verdict + the provenance table proving the circulating images are byte-identical to the onion7 release. [`STEGO-VERDICT.md`](stego/STEGO-VERDICT.md) · [`provenance.json`](stego/provenance.json) |
| [`transcription/`](transcription/) | — | Cross-diff of every transcription lineage: rune-identical. [`TRANSCRIPTION-VERDICT.md`](transcription/TRANSCRIPTION-VERDICT.md) |
| [`vision/`](vision/), [`vision-rerun/`](vision-rerun/) | — | AI-vision re-transcription tried as an independent read; verdict unchanged. [`AVENUE-1-VISION-VERDICT.md`](vision/AVENUE-1-VISION-VERDICT.md) |

## The 2026-07-28/29 auditor loop (`recon/`)

An 11-iteration loop in which a critic in a **fresh perspective** scored each round and
directed the next: contrarian → naïve-outsider → author-empathy → historian →
data-provenance → lateral-field → game-theorist → devil's-advocate believer, then recycling.

| Folder | Iteration | Result |
|---|---|---|
| `recon/i2_message/`, `i2_signal/`, `i2_image/` | 2 — naïve outsider | Non-cipher framings (message-existence, DSP/signal, image) all null |
| `recon/i6_mdl/`, `i6_wordlen/`, `i6_repeats/` | 6 — lateral field | MDL/compression (exactly incompressible), word-length typology, bioinformatics approximate-repeats — all null |
| `recon/i7_oracle/`, `i7_oracle_reset/`, `i7_constants/` | 7 — game theorist | Plaintext-blind doublet-restoration oracle: every numeric generator pushes the doubling rate *toward* random |
| `recon/i8_image/`, `i8_mapping/` | 8 — devil's-advocate believer | DCT-LSB / PNG-LSB / trailer clean against a working positive control; rune mapping falsifiably correct |
| `recon/i9_inventory/`, `i9_deficit/`, `i9_ocr/` | 9 — contrarian restart | Inventory = 29 confirmed correct; **autokey positively refuted** (difference-diagonal test, z=−17.25) |
| `recon/i11_smirnov/` | 11 — final pass | Smirnov/Carlitz deterministic rewrite gate-validated, pinned to its random control |
| `recon/lp1h_norepeat/`, `lp2h_index/` | LP1/LP2 recon | Three not-in-ledger hypotheses surfaced and tested clean null |

The loop **self-corrected three of its own false positives** (a word-length "language" signal
that turned out to be line-wrap typography; a "surviving English phonotactics" claim that was
95-rune sample noise; several claimed hits killed at the verify stage). That is the signal it
was doing real work rather than accumulating motion.

## Standalone probes (this folder)

| Script | What it does |
|---|---|
| [`run_stats.py`](run_stats.py) | The statistical profile every proposed mechanism must reproduce (IoC·N, doublets, entropy) |
| [`crypto_rigor.py`](crypto_rigor.py) | The last structural attacks — all closed |
| [`structure_analysis.py`](structure_analysis.py) | Interrupter / boundary / per-page probes |
| [`doublet_probe.py`](doublet_probe.py) | Doublet behaviour under candidate keystreams |
| [`red_team.py`](red_team.py) | Campaign XVII assumption-stack attacks |
| [`crib_autokey.py`](crib_autokey.py), [`seek_autokey.py`](seek_autokey.py) | Autokey crib-drag and search |
| [`seek_primes.py`](seek_primes.py) | Prime/totient keystream search |
| [`campaign10_otp_vs_autokey.py`](campaign10_otp_vs_autokey.py), [`campaign11_pin_the_filter.py`](campaign11_pin_the_filter.py) | The two positive results: autokey excluded, filter quantified at ~83% suppression |

## Running anything in here

All scripts resolve paths relative to their own location, so they run from any checkout:

```bash
cd liber-primus
python tests/validate.py              # trust anchor first — reproduces every solved page
python analysis/run_stats.py          # the statistical profile
python analysis/recon/i11_smirnov/smirnov_decode.py
```

Large corpora, downloaded onion dumps and mirrored third-party repos are **gitignored** —
the scripts that need them re-fetch on demand, so a fresh clone stays small and every
result stays reproducible.
