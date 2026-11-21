# PREREG — R44 WAVE-2 CELL C4: KEYED STEGO ON THE 56 CANONICAL ONION-7 PAGE JPEGS

**Date: 2026-11-09, written BEFORE first adjudicated execution.** Cell dir:
`analysis/round44/W2-C4-keyed-stego/`.

**Disclosure (R44 X1 hygiene):** before this file was written, three un-adjudicated *plumbing
probes* were run to time the binaries (keyless `outguess -r` on `p5.jpg`, `outguess -k test` on a
/tmp copy, `steghide extract -p test` on the same). Their outputs were garbage-length reports and a
clean steghide refusal; none was scored, kept, or used. No real-target adjudication preceded this
PREREG. This file is sha256-stamped into `runlog.txt` before the first scripted run.

## Hypothesis

H: at least one of the 56 canonical onion-7 LP2 page JPEGs carries an OutGuess- or
steghide-embedded payload under a **page-derived passphrase** (the page's own opening word, its
red-channel text, its gematria sum, its page-number variants) or under a key from the
**4,013-key Cicada-native list** (`analysis/round29/L1-onion3-crack/keys_big.txt`) — key families
never pointed at the page JPEGs.

## Cited ledger rows (not_covered wording verified in LEDGER.json before running)

- **R29-L1-ONION-STEGO** (negative): 4,013 keys x **3 onion images** (onion1/2/3) x outguess 0.4 +
  steghide. `not_covered` names "Keys outside the 4,013-key Cicada-native dictionary" and the tool
  caveats — the LP **page** JPEGs are not in its coverage at all.
- **R8 narrative** (per R29-L1 `keys_provenance.txt` family `G:prior-59` and the ELIMINATION-LEDGER
  stego section): the LP page JPEGs were swept **keyless + a 59-key list** only. Page-derived
  passphrases and the 4,013-key list were never run against them.
- **R36-O2-SOURCE-ARTIFACT-HUNT** (partially-run): the source-artifact hunt is open; the F3-J4
  observation stands that the author demonstrably shipped every prior key inside released bytes.
- **R43-F6-T4-BLOBS-IDENTIFIED** (measured): its coverage note defers steg-inside-JPEGs to
  "R8/R29/R30 stego verdicts" — which, for keyed attacks on the page JPEGs, cover only the
  keyless+59-key sweep. CONFIRMED OPEN for this key space.
- NOT re-run here: LSB/F5/append/carve channels (R8, R30-A1/A2), onion images (R29-L1),
  blob crypto (R30-B1/B2).

## Inputs (identity pinned)

- Targets: `liber-primus/data/relikd/p0.jpg … p55.jpg` — **verified this cell** (runlog):
  sha1(relikd pN.jpg) == `dataset/liber_primus.json` pages[N].image.published_sha1 for all N 0..55,
  i.e. byte-identical to the archive.org copy of the ky2khlqdf7qdznac.onion ("onion-7") LP2 dump.
- Canon text: `data/krisyotam_runes.txt` (57 `%`-segments; segment N rune-count == dataset page N
  `n_runes` for all N — verified in runlog). Segments 0..55 pair 1:1 with the 56 jpegs; segment 56
  (PARABLE) has no master here.
- Red channel: `analysis/round44/P1-red-ink/channel.json` (`full.idx` + `page_starts`).
- Global key list: `analysis/round29/L1-onion3-crack/keys_big.txt` (4,013 lines, as-is).
- Tools: `/usr/local/bin/outguess` (OutGuess 0.4, default retrieve mode), `/usr/bin/steghide`
  (0.5.1). Pure local, no network.

## Key-derivation rules (FIXED; builder = `scripts/derive_keys.py`, output `results/keys_per_page.json`)

Gematria Primus transliteration (dataset `gematria` table). For page n (0..55), seg_n = canon
segment n, W1/W2 = its first/second maximal rune runs:

- **A opening word**: translit(W1).upper(), .lower(), .capitalize(), and W1 as UTF-8 runes.
- **B opening bigram**: translit(W1+W2).upper(), .lower() (concatenated, no separator).
- **C red text**: for m in {n-1, n, n+1} ∩ [0,56] with a non-empty red slice (channel `full.idx`
  positions in [page_starts[m], page_starts[m+1])): slice translit .upper(), .lower(), and the
  slice as UTF-8 runes. (The ±1 window immunises against the one-page census/channel index
  ambiguity observed at the book tail; documented in runlog.)
- **D gematria sums**: decimal string of the prime-sum of all page-n runes; decimal string of the
  prime-sum of W1.
- **E page numbers**: str(n), f"{n:02d}", "p{n}", "page{n}", str(n+1), f"{n+1:02d}", "p{n+1}",
  "page{n+1}", "{n}.jpg".
- Dedupe within page, order preserved. Expected ~17–35 keys/page.
- **Keyless outguess** per page is run but recorded as **REPLICATION** of R8 (not new coverage).

## Arms

- **ARM-D**: derived keys x 56 pages x {outguess, steghide}.
- **ARM-G**: all 4,013 `keys_big.txt` keys x 56 pages x {outguess, steghide} (~449k runs).

## Adjudicator (FIXED thresholds, calibrated BEFORE the sweep; `scripts/adjudicate.py`)

An outguess retrieval row FLAGS iff payload non-empty AND any of:
- **F1 magic**: payload starts with a listed magic (gzip, zlib 78 01/9C/DA, PK, 7z, xz, bz2, PNG,
  JPEG, GIF, PDF, RAR, Salted__, OpenPGP armor) OR contains `-----BEGIN PGP` in the first 1024 B.
- **F2 printable**: declared length ≥ 32 and printable ratio ≥ 0.95 over the first 8 KiB.
- **F3 strict OpenPGP binary parse**: packet chain consuming ≥ 95% of the payload, 1..8 packets,
  tags in {1,2,3,4,6,8,9,11,14,18}, lengths consistent. **ARMED only if** its false-fire rate on
  10,000 random blobs (log-uniform sizes 16 B–85 KB) is < 0.5%; otherwise advisory-only. The naive
  weak-tag detector (R43-F6 measured 32.8% on noise) is recorded for comparison but NEVER flags.

A steghide row FLAGS iff exit status 0 and a non-empty file is extracted (steghide
self-authenticates; calibration-free).

Any flag on a real target is inspected; a survivor is **FLAGGED-FOR-ORACLE** per
`HUMAN-ORACLE.md` — never certified here. If any extraction yields a rune/rune-index stream of
N ≥ 60, it is additionally adjudicated under the standing panel
(`analysis/round19/I2/adjudicate.py`) against `analysis/round34/I1-v3-null/bars_v3.py`
`bar_v3(N_actual, 10000 nulls)` at that exact N — threshold computed before scoring that stream.

**R3 stats persisted per row** (`results/sweep_stats.tsv.gz`): tool, page, key_class, key,
og_seed, og_declared_len, out_len, byte entropy, printable_ratio, F1/F2/F3/naive flags.

## Positive controls (PLANTED THROUGH THIS CELL'S OWN GLUE, before any real target)

- **PC1 (real author positive)**: `analysis/armada_osint/artifacts/dl_1033.jpg` keyless through
  the sweep driver → must FLAG (known PGP "Welcome", seed 102, len 1498; R29-L1 FINDINGS).
- **PC2 (keyed outguess, the shape we hunt)**: embed an ASCII-armored PGP-style message into a
  copy of p12.jpg with `outguess -k` = page-12's A1 key; the driver over page-12's full keylist
  must FLAG at exactly that key via F1.
- **PC3 (steghide)**: `steghide embed` a text payload into a copy of p33.jpg with its D1
  gematria-sum key; driver must FLAG at exactly that key.
- No verdict is issued unless PC1–PC3 all pass.

## Aiming Test

**Q1 — what does a hit look like; does the instrument see it?** A steghide extraction success, or
an outguess payload with magic/armor/printable structure — the exact shape the author used on
onion3/1033.jpg (ASCII-armored PGP). PC1 is the author's own artifact through this driver; PC2/PC3
plant the keyed shape. A payload of structureless high-entropy bytes is NOT recognizable
(indistinguishable from wrong-key garbage) — stated as a register conditional, not hidden.

**Q2 — measured fact raising the prior?** `analysis/round29/L1-onion3-crack/FINDINGS.md`: the
author *demonstrably used OutGuess on this release channel* — 1033.jpg from the onion carries a
keyless OutGuess PGP payload. And F3-J4/R36-O2 residue: every prior key was shipped inside
released bytes. The page JPEGs are the largest released byte mass never keyed-attacked; the
page-derived families are exactly how the author keyed prior material (DIVINITY, FIRFUMFERENFE =
opening/first-line words of their own pages).

**Q3 — bounded?** ENUMERABLE: ≤ (35 derived + 4013 global) keys x 56 pages x 2 tools ≈ 4.6 x 10^5
extractions, all run. If the ARM-G projection at the 10% checkpoint exceeds 5 h wall, truncate to
the first K file-order keys fitting 5 h and report the exact fraction as coverage.

**Q4 — the three conditionals of a negative.**
1. *Key space*: the derivation rules above + keys_big.txt, verbatim — nothing else.
2. *Construction*: OutGuess 0.4 default retrieve + steghide 0.5.1 extract only. NOT: outguess
   legacy `-t`/0.13 mode, F5, jsteg, LSB, EOF-append (measured elsewhere), other stego tools.
3. *Recognizer register*: F1/F2/F3 structure classes (+ panel path for rune streams). A payload
   deliberately shaped as uniform random bytes is invisible to this cell.

**Q5 — kill condition.** PC1 fails through the driver → INSTRUMENT-INCOMPLETE, stop, no verdict.
10% checkpoint on ARM-G for the 5 h truncation rule. If `%`-segment/page pairing had failed
verification (it did not — runlog), the derived arm would have been UNAVAILABLE-BY-PREMISE.

## Verdict vocabulary

negative / flagged-for-oracle / INSTRUMENT-INCOMPLETE, with coverage x power and not_covered per
doctrine R7. Ledger rows drafted in `ledger_rows.json`; LEDGER.json never modified.
