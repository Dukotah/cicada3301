# Round 44 / WAVE-2 CELL C3 — MIRROR BYTE RESIDUE — PREREG

_Dated 2026-11-09, written and hash-stamped into `run.log` BEFORE any plant, inventory or
read output existed (R44 X1 hygiene fix). Cell dir: `analysis/round44/W2-C3-mirror-residue/`.
Pure python3 (numpy/PIL available), no network. Corpus root for residue objects:
`corpus/A-primary-artifacts/` (+ `TRAILING-DATA.json` there, 13 trailing + 9 unparseable);
masters: `liber-primus/data/relikd/`; opaque blobs: `analysis/armada_osint/extracts/T2.bin`
(sha256 35d31e61…, the R35-B2 statistically-pinned copy), `analysis/armada_osint/artifacts/
folly.bin` (= T3, md5 0c7d18e8…, matches the recorded identity), `analysis/pp49_51/
canon_256.bin` (the R35-B2 promoted canon)._

## 1. Hypothesis

The corpus's **byte-residue channel** (bytes after EOI/IEND, unparseable image files, and
the two true-opaque blobs) still contains unidentified machine-readable objects. The
attested author idiom family (R43-F6: byte-reversal, bytewise complement/XOR-0xFF,
appended-file chains; 2012: plaintext trailer) is the prior transform family. Specific
named objects with no ledger row (R43 blind agents, `round43/F1-blind/hypothesis_lists.json`
lines 12, 157, 170, 362): **Outt.png** 13,592-B post-IEND trailer (palindromic, repeating
15-byte/120-bit unit — claims to verify), **Huh2.jpg** 175,159-B trailer starting `d9ff`
(reversed-JPEG shape, truncated?), the **9 unparseable** files, and the **0_wisdom.jpg /
05.jpg** 336,713-B trailer (reversed JPEG of the wisdom page + ASCII block — one blind
agent instead reports a "72,700-B truncated reversed JPEG": the discrepancy and the full
byte accounting of that trailer, i.e. "what is in the truncation gap", is a target).

## 2. Cited ledger rows (not_covered wording verified on 2026-11-09 before freezing)

- **B-09** (status `open`, raw `scope-limited`): "OSINT residue — T2/T3 blobs, items 6–9"
  (`round10/RECON-B/REGISTER.md` → `OSINT-SWEEP-2026-07-27.md` §items). T2/T3 are "still
  open (low prior)". Items 6–9 themselves (per-onion HTTP/port anomalies, whitespace
  re-audit at scale, 2012 "7 images" endpoint, Columbus GA Shamir onion) **require network
  → UNAVAILABLE-BY-PREMISE for this cell**; only the blob half of B-09 is in scope.
- **R29-L2** (via `round29/L2-blob-cross/FINDINGS.md`; ledgered inside R30-B1's coverage):
  T2_2jpg / T3-folly / canon_256 are "true opaque". COVERED there: cross-XOR all pairs,
  OTP-pad over known plaintexts, autocorrelation, repeated-8-block, and a **header hunt
  under raw / reverse / xor-0xFF / rotate(1,2,3,4,7) / base64** (header-position hunt, not
  an all-offset decompression sweep; no nibble/bit-level transforms, no delta/cumsum/
  xor-index, no direct symbol-mapped read). I do NOT re-run any of that list.
- **R30-B1-BLOB-CRYPTO** (negative, patched R34-P1/R35-B2): COVERED: ~7 cipher families ×
  ~37–40 Cicada-derivable keys, pairwise XOR, gpg trap. not_covered: keys beyond that set,
  AEAD/KDF. I run **no keyed-cipher battery** here (stays closed).
- **R43-F6-T4-BLOBS-IDENTIFIED** (measured): the T4 .htaccess blobs are identified
  (NOT-gzip-JPEG / NOT-JPEG chain); its result row records "no T2*/T3*.bin in artifacts/
  (absent)" — they are in fact present at the paths above (extracts/T2.bin,
  artifacts/folly.bin); noted as a correction, not a contradiction (F6 looked in
  `artifacts/` only, T2 lives in `extracts/`). F6's magic/decompression battery is the
  technique family this cell extends to the NON-T4 residue objects. F6's `reopens_if`
  (blob2-vs-blob3 diff region) is image-content work — NOT taken up here (out of scope).
- **R12-A1 / R44-P4** (negative): blobs **as pads/keystreams over LP** are covered
  (CicadaOS pads; onion 256-B blobs as per-page mod-29 pads). This cell does not re-run
  pad legs; the direct **read-as-plaintext** of a blob (bytes symbol-mapped and
  adjudicated as a message in its own right) appears in no row — that is the open sliver.
- **R29-L1 / R8 / R30-A1/A2** (stego): pixel/DCT stego inside decoded images is covered
  and NOT re-run; this cell touches container bytes only.
- Checked wave-1 (P1–P5/R1/X1) and wave-2 siblings (A1–A4, B1–B4, C1): no cell reads the
  trailing-byte channel or the T2/T3 structural residue. W2-B1 is the hash-block stride
  (different artifact); no overlap.

## 3. The five Aiming-Test answers

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
Three hit shapes, each with its own recognizer, each proven by a plant through this cell's
own glue BEFORE any real target:
(i) *Hidden container*: a trailer/residue that under one of the attested transforms
(reverse, complement, reverse∘complement, or identity) contains a parseable object (JPEG/
PNG/gzip/zlib/bz2/xz/PGP/ASCII) at some offset. Recognizer = `residue_lib.identify()`
(all-offset magic scan + decompression + image walk under the transform family). Plant
PC1: gzip of a known sentence, complemented+byte-reversed, appended after IEND of a copy
of a real corpus PNG → pipeline must locate, invert, decompress and return the exact
sentence.
(ii) *Symbol-mapped message*: a residue stream whose bytes, under a registered symbol map,
score above the fixed panel bar. Recognizer = `adjudicate.py` (panel-R36, 12 registers) on
rune indices from the map. Plant PC2: a byte blob synthesized so bytes mod 29 = the rune
indices of a real English passage (≥ 240 runes), pushed through the identical map+panel
glue → pmax must clear the §5 bar; 200 urandom blobs through the same glue must stay
under it (reported as calibration).
(iii) *Structure bound*: for objects that remain opaque, the deliverable is a measured
bound (windowed entropy ≥ 7.9 throughout, no period, no transform hit) — F6's convention.

**Q2 — Measured fact raising the prior above flat.** The residue channel has already paid
twice in this corpus, by measurement not lore: the 2012 TIBERIVS trailer (61 B after EOI =
the entire first puzzle step, `TRAILING-DATA.json` rows 1CcV1/Final.jpg) and the 05.jpg /
0_wisdom.jpg trailer (byte-reversed JPEG + the magic-square ASCII block — verified on
bytes by two independent R43 blind agents). The transform family is attested in-corpus
(R43-F6: T4 blobs are NOT(gzip(JPEG))/NOT(JPEG); `folly.rev` exists in the CicadaOS tree).
Outt.png's 13,592-B trailer and Huh2.jpg's 175,159-B trailer have **no identification
anywhere in the ledger** (B-09 is `open`; F1-blind calls Outt "an unexplained
machine-readable object"). Honest label: inventory+identification = high-prior bounded
object audit; the T2/T3 new-transform battery = completeness ritual on a bounded object
(R29-L2 already bounded them as random-by-every-test it ran).

**Q3 — Bounded space?** ENUMERABLE and small. Objects: 13 trailing entries (10 distinct
trailer sha256s) + 9 unparseable files + 3 true-opaque blobs + ≤ a handful of recursive
inner residues ≈ **≤ 30 objects**. Transforms: 4 attested (id, rev, xff, rev∘xff) on large
objects; + 9 extension transforms (rot5, rot6, nibble-swap, bitrev-per-byte, delta,
cumsum, xor-index, and rev/xff composites already counted) on the 3 small opaques only.
Magic scan is exact (bytes.find, all offsets). Panel decodes capped **N_CAP = 400**.

**Q4 — The three conditionals any negative carries.**
1. *Key space*: NONE swept (no keyed decryption at all). The swept space is the transform
   family above × all offsets × the symbol maps of §5(ii) — nothing else.
2. *Decoder transition model*: direct symbol maps only ({bytes mod 29, 5-bit groups
   skip-≥29, byte-pairs mod 29} × {id, rev, xff}); no cipher constructions, no resets, no
   autokey. A payload enciphered under any keyed construction is invisible here (R30-B1's
   negative plus its not_covered governs that branch).
3. *Adjudicator register*: panel-R36 (12 registers) + language-agnostic stats (ioc, mds,
   h2, zl, degenerate guard). A plaintext outside those registers, or a non-linguistic
   payload (keys, coordinates), scores as noise — identification legs (i)/(iii) partially
   compensate, linguistic leg does not.

**Q5 — Kill condition at 10% of budget.** (a) If PC1 fails and one dated repair addendum
does not fix it → INSTRUMENT-INCOMPLETE, stop, no real verdicts. (b) If PC2's positive
does not clear the bar or >2/200 urandom calibration blobs clear it → the adjudication leg
is reported INSTRUMENT-INCOMPLETE and only legs (i)/(iii) proceed. (c) If the premise
objects are absent on disk (trailer sha mismatch vs TRAILING-DATA.json) → that object is
UNAVAILABLE-BY-PREMISE, reported per-object, not silently skipped.

## 4. Procedure (order is binding)

1. Hash-stamp this PREREG into `run.log` (sha256 + date) — before any execution.
2. **PC1 + PC2 plants** (`scripts/run_plant.py`). No real target before both are decided.
3. **Inventory** (`scripts/run_inventory.py`): verify every TRAILING-DATA.json row on
   disk (sha256 of file + trailer); run `identify()` on each distinct trailer; walk
   appended-image chains recursively; byte-account the 05.jpg/0_wisdom trailer and the
   Huh2 trailer end-to-end (every byte assigned to a parsed segment or flagged residue);
   verify/refute Outt's palindrome + 15-byte-unit claims; parse the 9 unparseable files
   (walker failure point, classification, post-failure residue through `identify()`).
4. **T2/T3/canon battery** (`scripts/run_t2t3.py`): ONLY the uncovered transforms
   (§2 R29-L2 item): all-offset magic+decompression under id/rev/xff/rev∘xff (R29 was
   header-hunt only), plus rot5, rot6, nibble-swap, bitrev, delta, cumsum, xor-index;
   windowed entropy; repeating-unit/palindrome scan. NO cipher keys, NO pad legs.
5. **Adjudication** (`scripts/run_adjudicate.py`): every unexplained residue stream
   ≥ 120 mapped symbols + T2/T3/canon direct reads, under the §3-Q4 maps; panel-R36;
   compare to §5 bars. Streams < 120 symbols: stats recorded, no verdict (instrument
   floor), listed in not_covered.
6. RESULTS.md + results/*.json + ledger_rows.json. Any bar-crosser →
   **FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never certified here.

## 5. Fixed thresholds (before any run; bars_v3 at N_CAP=400, computed 2026-11-09)

- Identification legs: deterministic (valid decompression / valid image decode / exact
  inner-sha match). No stat bar.
- Panel bar of record: `bar_v3(400, L, "free")` from `analysis/round34/I1-v3-null/
  bars_v3.py`: **L=120: 11.136, L=240: 14.805, L=400: 16.327, L=729: 19.198** (pmax
  scale). Mapped streams are truncated to the largest node ≤ their length; actual N
  reported (must be ≤ 400 or an addendum logs the overrun before running it).
- Degenerate guard (standing, R38 I2): a decode with mds ≤ 6 or IoC·N ≥ 4.24 is a
  recognizer failure, never a candidate.
- Null-family caveat (stated now, part of the record): the "free" null is shuffled-LP2
  wrong-key free-decode pmax — the closest standing null for non-LP symbol streams; the
  200-urandom calibration run is reported alongside but does NOT move the bar.
- Random-bound leg: "statistically random residue" claim requires windowed entropy
  ≥ 7.9 bits/byte on every 4096-B window (window 4096, step 1024) for objects ≥ 8 KiB
  (F6 convention); smaller objects get global entropy + chi² only, no randomness claim.

## 6. Coverage / not_covered (drafted now, finalized in RESULTS.md)

Covers: identification of the 13 trailing rows + 9 unparseable files under the attested
transform family at all offsets; byte accounting of the 05/0_wisdom and Huh2 trailers;
Outt.png trailer structure; T2/T3/canon under the §4.4 extension transforms; direct
symbol-mapped reads of unexplained residues under 9 map combinations, panel-R36, N ≤ 400.
Does NOT cover: network OSINT (B-09 items 6–9); keyed ciphers (R30-B1 governs); pixel/DCT
stego inside decoded images (R8/R29-L1/R30 govern); pad/keystream legs (R12-A1/R28/R44-P4
govern); registers outside panel-R36; non-linguistic structured payloads; transforms
outside the enumerated family.
