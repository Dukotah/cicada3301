# Lane B — PROGRESS

Resume file. Updated continuously. Branch `corpus-sweep`.

## State
- [x] Read INVENTORY §2, PROBLEM.json, SOLVED-PAGES.json, gematria.py, validate.py,
      lib_numchannel.py, corpus.py, run_stats.load_pages, dataset/build_dataset.py
- [x] Established the page-numbering reconciliation (see CONFLICTS-B.md C-01)
- [ ] PAGES.json built + validated (13,136 / 12,956)
- [ ] analysis/reproduce/ scripts (5) written and passing
- [ ] External hunt: independent transcriptions / text-layer PDF
- [ ] MANIFEST.json, GAPS-B.md, CONFLICTS-B.md, REPORT-B.md

## Key structural facts established by running code (2026-08-19)
- `run_stats.load_pages()` splits `liber-primus/data/krisyotam_runes.txt` on `%`
  -> **57 non-empty segments, 13,136 runes**. Segments 0..54 = 12,956 unsolved.
  Segment 55 = AN END (85 runes, solved). Segment 56 = PARABLE (95 runes, solved).
- `liber-primus/data/sources/relikd_*.txt` independently re-splits the SAME 13,136 runes
  into **58 onion7 page slots 0..57**, of which **page 50 carries no runes at all**
  (verified by eye: p50.jpg is a 13x8 grid of two-character tokens, no runic text).
- Therefore segment index != page number above 49:
  `seg 0..49 -> page 0..49` · `page 50 = runeless` · `seg 50..54 -> page 51..55`
  · `seg 55 -> page 56 (AN END)` · `seg 56 -> page 57 (PARABLE)`.
  Independently corroborated in-repo by `liber-primus/analysis/seed_sweep/prep.py:11`.

## Done (2026-08-19)
- [x] `corpus/B-liber-primus/build_pages.py` + `PAGES.json` — 58 LP2 page records
      (0-57) + 5 LP1 solved-page records. Hard gates all pass:
      13,136 total / 12,956 unsolved / 57 krisyotam segments / relikd == krisyotam
      rune-for-rune on all 57 / unsolved-index SHA-256 == the PROBLEM.json pin
      `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`
      / 56/56 images attached and SHA-1-verified against the archived onion7 dump.
- [x] `analysis/reproduce/` — 7 standalone scripts + `run_all.py` + `README.md`.
      **7/7 PASS in 0.8 s.** The 5 mandated LP1 solves plus LP2 56 (AN END) and
      57 (PARABLE). Each is an independent re-implementation (inlines its own
      gematria/ciphers/scorer/beam search, imports nothing from liber-primus/src).
- [x] Finding: AN END needs 1 interrupter for a full decode; the in-repo gate only
      asserted a prefix and never saw the truncated tail. -> CONFLICTS-B C-05.

## Remaining
- [ ] External hunt: independent transcriptions / text-layer PDF (GAPS.md G-03)
- [ ] MANIFEST.json, GAPS-B.md, CONFLICTS-B.md, REPORT-B.md

## External hunt — LIVE FINDINGS (2026-08-19)
Tooling: `corpus/B-liber-primus/hunt_transcriptions.py` (fetch + rune-for-rune diff,
checkpoints `hunt_results.json` after every repo) and `align_henkman.py`.

1. **henkman/liberprimus (repo created 2016-08-14, PRE-DATES the 2017 rtkd root)**
   — 13,072 runes, own page markers `----- N -----`, own codepoint convention.
   Agrees with canon on **49/58 pages exactly**; **DIVERGES on 9** (pages
   0, 3, 6, 19, 26, 33, 35, 39, 56), 13 edit blocks. Full edit script in
   `CONFLICT-henkman-2016.json`. Page 56 (AN END) conflict ADJUDICATED
   mechanically in canon's favour (canon "THERE EXISTS", henkman "HERE EXISTS").
2. **aautcsh/idkfa (2016-01-17)** `assets/liber-primus-translation.txt`, 15,938 runes
   (whole book, LP1+LP2). 9 edit blocks vs `rtkd_master.txt`. One adjudicated:
   PARABLE reads DIUINITY in canon, DIUINITE in the candidate -> canon right.
3. **>>> AN ERROR IN THIS REPOSITORY'S OWN DATA <<<**
   `data/scream314_lp.md` page 06.jpg reads **ᚹᛋ (W,S)** at rune offsets 142 and 279
   where `data/sources/rtkd_master.txt` reads a single **ᛠ (EA)**. Decrypting
   (atbash + shift 3) settles it: EA gives the koan's actual refrain
   "THAT IS NOT **WHO** YOU ARE" / "THAT IS WHAT YOU DO NOT **WHO** YOU ARE";
   WS gives the self-contradictory "NOT WHAT YOU ARE". **rtkd_master is right,
   scream314 is wrong**, and the error propagates into SOLVED-PAGES.json and
   tests/validate.py. LP1 only - the 12,956-rune unsolved stream is unaffected.
4. **dude123124144/Liber-Primus-Runes-OCR (2017-03)** `misc_scripts/transcriptions.rne`
   — 13,136 runes, **0 divergences** after normalising U+16C2 -> U+16C4. Perfect
   agreement over 13,136 glyphs is itself evidence of derivation, not independence.
5. Codepoint conflict: three sources write the GER/J rune as **U+16C2 ᛂ**, canon uses
   **U+16C4 ᛄ**. A join trap; 453 runes affected.
6. archive.org item `liber-primus` = a 9,086,651-byte ZIP of images. **No text layer.**
