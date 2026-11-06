# ROUND 43 — X1 RED-TEAM REPORT

## 1. BLINDNESS AUDIT — all six agents: **BLIND-CLEAN**

**Workspace forensics** (`/tmp/lp_blind/material`):
- Contents are exactly three objects: `krisyotam_runes.txt` (canon data), `page-images/` = byte-identical copy of `liber-primus/data/relikd/` (diff: zero differences, includes the p*.txt per-section transcriptions the agents cite), and `released-artifacts/` = byte-tree copy of `corpus/A-primary-artifacts/` **minus** `CONFLICTS-A.md`, `GAPS-A.md`, `MANIFEST.json`, `PROGRESS.md`.
- **No `*.md` above the data layer**: the only file at material root is `krisyotam_runes.txt`. The 10 `.md` files present are all inside `released-artifacts/` and are corpus content (2012/2013 puzzle walkthroughs, mirror READMEs) plus `REPORT-A.md`.
- Nothing from `liber-primus/analysis/` is present. Hard grep for `LEDGER.json | OTP-class | elimination-ledger | PREREG | ARMADA | MEASURED-CEILING | PICKUP-HERE | round 10–43`: **zero hits** (only "armada" matches are fandom image filenames `Cicada_armada*.png` — community content).

**Per-agent list scan** (markers: round numbers, ledger row ids, repo analysis docs, "OTP-class", elimination campaigns, analysis/-only facts):

| Agent | Verdict | Notes |
|---|---|---|
| A1 cryptanalyst | **BLIND-CLEAN** | "OTP-like flatness" is natural terminology, not the ledger's OTP-class label. All cited objects (TRAILING-DATA.json, 2015-1033/, signed-payloads/*.bin) verified present in material. |
| A2 forensic examiner | **BLIND-CLEAN** | REPORT-A.md citations (137/140, imgur strip) are in-material. |
| A3 puzzle designer | **BLIND-CLEAN** | All cited paths verified on disk (2012-01-key-in-front-of-you.asc, Fibbonachi.gif, Stacked Pages/, 2016-01-liber-primus.asc at `pgp/messages/`). |
| A4 hand-cipher historian | **BLIND-CLEAN** (caveat below) | "Background: solved pages used shift/Atbash/Vigenère/prime-totient+interrupter". |
| A5 data archaeologist | **BLIND-CLEAN** (caveat below) | "per the allowed background"; its "REPORT-A.md C-02" = CONFLICTS-A item C-02, a coincidental id collision with ledger row C-02, not leakage. |
| A6 adversarial reframer | **BLIND-CLEAN** | "index/ledger" is the object-class noun, not the repo LEDGER. |

**Two flags, neither a leak:**
1. **"The allowed background" (A4, A5).** The phrase implies the blind prompts carried a sanctioned background blurb; the prompts themselves are not on disk, so I cannot audit their text. Content-level screening: every background fact stated (solved-page cipher curriculum, totient stream, interrupter) is independently derivable from in-material corpus docs (verified: `cijhho123/2014/additional docs/Titanpads from time of solving/The complete story of onion 6.txt` contains the totient method; the 2012/2013 WALKTHROUGH.md puzzle docs are in material). No analysis/-only fact appears in any list.
2. **REPORT-A.md retained in the data layer.** It is project-compiled (2026-08-20) but is pure corpus provenance (signatures, trailing bytes, mirror conflicts); grep confirms zero cipher-analysis terms, zero round/ledger references. Defensible inclusion; record it as a deliberate data-layer decision for Round 44's blind lanes.

## 2. F5bT VERIFICATION — **NO-ERROR-FOUND**

Everything re-derived independently from the lane's own artifacts:
- **PREREG discipline**: `PREREG.md` mtime 16:14 precedes `merged_intervals.json`/`key_streams.json` (16:16), `f5bt_results.json` (16:18), `RESULTS.md` (16:19). Thresholds were fixed in PREREG and **re-derive exactly**: `bars_v3.bar_v3(34668, 120/240, "free")` = 13.5131 / 18.1033. Grid arithmetic re-derives: per-cfg 963 × 2 × 3 × 6 = **34,668** (S_A has no mode-O rows, correctly handled); 55 × 34,668 = 1,906,740 ✓, controls 3 × 34,668 = 104,004 ✓.
- **Merge honesty**: 112 exact cells (31 multi-witness, 81 single, exactly 9 unconfirmed = bytes 143–151; byte 152 is correctly multi-witness via the Cripion overlap), bounded pair {190,191} sum 30, `value_disagreements` empty, 3 findings with the single byte-168 clock-digit root cause — all match RESULTS.md. S_A (47) and S_B (65) rebuilt cell-by-cell from `merged_intervals.json` match `key_streams.json` and the RESULTS-printed S_A verbatim. **Raw-witness spot-check**: BotSottile log bytes 170–174 give intervals 10/35/10/5/10 → k = 2,7,2,1,2 = S_A idx 27–31 exactly.
- **Plant control through the same glue**: code-inspected — controls are scored by the identical `sweep_page()` the real pages use, run FIRST, gate kills the lane on failure. I rebuilt P1 from the PREREG spec independently: decode is byte-exact, pmax **38.3214** matches the stored result to 1e-6.
- **Headline re-score**: global best (page 30, S_B fwd, m2, beau+atbash, rot 36, L=263) independently re-decoded and re-adjudicated: pmax **5.363516**, non-degenerate — matches; 12.7 z below the 18.103 bar. 0 crossers confirmed across all 55 page-bests.
- **`ledger_rows.json` coverage honesty**: ~44% (112 exact + 2 bounded of 255) is stated, bytes 2–142 named as unattested and outside the key space, and the not_covered list (byte-values-as-key, transposition/selection readings, sub-runs, sub-60 one-shot, fresh per-shuffle null) matches PREREG's own exclusions. Draft row is safe to apply as-is.
- One cosmetic nit (not an error): PREREG says plants are "appended as synthetic pages"; the code scores them ahead of the pages through the same function. Functionally identical glue.

## 3. X0 SPOT-CHECK — stamps **UPHELD**; four text corrections needed

Ledger confirmed at **308 entries**; every cited row id resolves (full ids are suffixed, e.g. `R33-I2-CONSTRUCTION-AXIS`, `R28-L2-CONTESTED-BYTES`).

**CITED stamps checked (10 items, 20 rows) — all accurate:** item 1 (VERDICT-OTP-CLASS "separates, does not choose" ✓; R18-L2-A-LOCUS M3/M4 excluded at power 1.000, 17 z ✓; D-01 supp 0.8075, MACHINE ✓; R12-C1 23,520 configs ✓), item 2 (A-03 K_bound 26 vs 93, 3.6× ✓; R20-N2 K=40 ✓; T2-INDEL ≤1 ✓), item 3 (A-01 99.89%, 0 identity errors ✓; T1-05 99.6346%, p27:93 ✓), item 6 (R10-L3-ROAD T1–T5 ✓; R41-C1-R14 wordsum self-key negative panel-R36 ✓; U6A-N3 genuinely inconclusive ✓), item 12 (R28-L2 11/11 cells 100%, 21,628,416 decodes ✓), item 13 (HILL5-MAGIC negative ✓), item 14 (R30-A1-FONT 28/29 maxIoU 1.000, below-noise disclaimed ✓), item 26 (R22-C 185 ops ✓), item 32 (UNSOLVABLE-BY-DESIGN status superseded→OTP-CLASS ✓), item 33 (CORPUS-G-02 one key ✓; L1-F6 56 files / 54 timestamps ✓).

**REOPEN stamps — all 9 verified against the rows' own disclaimers, verbatim:** R33-I2 `unrepresented: [skip_by_4, skip_by_5, reset_per_page, reset_per_line]` ✓; R22-D "THE REOPENER… Documented, not executed" ✓; R40-C1-R47-F01 "all-pairs page XOR and canon-as-key… not run" ✓; R36-O2 partially-run (Wayback "Temporarily Offline — UNSEARCHED, not empty") ✓; B-09 open, hypothesis literally "OSINT residue — T2/T3 blobs, items 6–9" ✓ + G-01/H-02 partially-run ✓; R18-L2-A-LOCUS "power 0.075, i.e. underpowered" ✓; D-03/D-02/C-01 open by their own hand ✓; B-24/B-19/B-20 open ✓; R12-A1 ">99.99% of single-byte offsets remain unswept", literal-reductions-only ✓ + R40-B3 "Dense offsets" uncovered ✓. The p27/p54 7-gram: grepped — appears in **no** ledger row, as X0 claimed.

**NEW stamps — all 8 survive the hard grep:** red-ink channel (all "red/chroma" hits are JPEG-forensics or ink-repair contexts; A-06/B-12/R19/MEASURED-CEILING line 112 all disclaim colour verbatim) ✓; p15 grid (3258/4516/etc. appear in zero rows; only trace is B-12 reopens_if (iii) "p15 `3299` ink-tone marking", exactly as X0 quoted) ✓; quote/punctuation-identity (all "quote" hits are "bar quoted here" boilerplate; B-12 "separator SHAPE" uncovered) ✓; cuneiform/5-dot (zero rows) ✓; 86-doublet-site message (E-02B and R28-L5's E-02v cover gap-vs-payload correlations only, never the site tuple as symbols) ✓; hash-block stride parse (zero rows; R43-F6-PAGE56-HASH-AS-KEY is keystream/XOR only, confirmed in its coverage field) ✓; blurred tree ("blur/Gaussian" hits are statistics terms) ✓; onion blobs as per-page mod-29 pads (R43-F6 rows cover structure and blob×payload byte-ops only; H-03 is cookies×blobs ASCII-gated) ✓.

### Ledger/adjudication patches needed (text, not stamps)

1. **Headline arithmetic error**: "~24 of 34 deduplicated items stamp CITED" is wrong. The table itself stamps **17 CITED + 1 split (item 29) + 9 REOPEN + 7 NEW = 34**. Correct to "17 CITED (18 counting item 29's attestation half)". The qualitative headline (zero letter-stream items missed; all REOPENs are self-disclosed edges) survives.
2. **Item 9**: delete "R26-B/R42-C1 are skip-aware by construction". `R42-C1-R35-KEYTEXTS-RUN` is rigid-alignment running key (no skip axis anywhere in its coverage); skip-awareness rests on R26-B alone, which is partially-run with large pages capped. Stamp unchanged.
3. **Item 21**: "E-02B" is a sub-test of row **E-02**, not a standalone row id — cite as `E-02 (part B)`; add `R28-L5-PAYLOAD-MICRO` (its E-02v doublet-gap-varint leg) to the adjacent-row list.
4. **Item 1**: when R12-C1 is cited for the bare delta-tape decode negative, carry its own not_covered caveat (English-quadgram scorer, no register panel — an L7-A-class negative). The exclusion itself safely rests on R18-L2-A-LOCUS/D-01 at power 1.000, which are scorer-free.
5. **F5bT**: no patch; `ledger_rows.json` draft `R43-F5BT-TIMING-KEYSTREAM` is accurate and may be applied verbatim.

Files referenced: `/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/round43/F5bT-timing-keystream/{PREREG.md,RESULTS.md,run_f5bt.py,merged_intervals.json,key_streams.json,f5bt_results.json,ledger_rows.json}`, `/mnt/c/Users/dukot/projects/cicada3301/liber-primus/LEDGER.json`, `/mnt/c/Users/dukot/projects/cicada3301/corpus/A-primary-artifacts/REPORT-A.md`, `/tmp/lp_blind/material/`.
