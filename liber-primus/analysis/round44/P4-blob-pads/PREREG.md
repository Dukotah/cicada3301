# R44 / P4 — PREREG: onion pre-page 256-byte blobs as per-page mod-29 pads

_Written 2026-11-09, BEFORE any data output of this lane. Plan of record:
`../CAMPAIGN-PLAN.md` lane P4 (X0 NEW #4, item 31 "NEW-lite"). Doctrine:
`../../../ARMADA-DOCTRINE.md`. Construction is the R43-F6 / R28-L2 / R43-F5bT
keystream harness verbatim with the key material swapped; instrument is the standing
panel-R36 adjudicator + bars_v3 free bars. No threshold in this file moves after data._

## Hypothesis

One (or more) of the three onion pre-page 256-byte hex blobs — the high-entropy objects
embedded in the pre-pages of `avowyfgl5lkzfj3n.onion` (marker `<!--3301-->`),
`cu343l33nqaekrnw.onion` (`<!--761-->`), `fv7lyucmeozzd5j4.onion` (`<!--1033-->`) — is,
after a byte→mod-29 reduction, a repeating keystream for one or more of the 55 unsolved
LP2 pages under a periodic additive / Beaufort / atbash-composed Vigenère geometry.
Secondary: the blob joined byte-wise with the pp49–51 payload (canon_256 /
canon_256_decpref × {XOR, ADD, SUB mod 256}) is that keystream.

## Objects and extraction (own glue)

- Blobs are extracted BY THIS LANE's own code from
  `analysis/armada_osint/onions_ibotpeaches/onions__{avowyfgl5lkzfj3n,cu343l33nqaekrnw,fv7lyucmeozzd5j4}.onion__pre__index.html`:
  the single run of ≥512 hex chars per file (assert exactly one), `bytes.fromhex`,
  256 bytes each. Cross-check (not dependence): sha256 must equal the R43-F6 recorded
  values `4f1cef87…` (3301), `05acf0d8…` (761), `d8c0f83c…` (1033); mismatch = hard stop.
- `analysis/pp49_51/canon_256.bin` (sha `3b9b07d9…`) and `canon_256_decpref.bin`
  (sha `f42b7caa…`), asserted at load.
- Pages: `load_pages()[:-2]` from `analysis/run_stats.py` — the same 55 unsolved pages as
  R42-C3 / R43-F6 / R43-F5bT (lengths 66–277, 12,956 runes).

## The Aiming Test

**Q1 — what would a hit look like, and would this instrument recognise it?**
A page whose decode under some (stream, reduction, direction, config, rotation) cell is
natural language in one of the 12 panel-R36 registers: full-`adjudicate` pmax ≥ the
pre-named bars_v3 free bar at the page's L_cap, non-degenerate. Three positive controls
(below) are enciphered through THIS lane's own derived keystreams and decoded by the same
sweep loop (R42 X1 rule: not a borrowed control); each must be found at its exact planted
cell with exact plaintext recovery and a bar-crossing pmax, or the lane hard-stops.

**Q2 — what measured fact raises this family's prior above the flat rate?**
(a) `round43/F3-hand-feasibility/KEY-LOCALIZATION.md` J6/C7: F3's hand-feasibility
localization names the three published, page-adjacent, exactly-256-byte high-entropy
blobs as a candidate pad location, and R43-F6 measured them to be *neither RSA moduli
nor mutually related* (R43-F6-ONION-BLOB-STRUCTURE) — 768 bytes of deliberate,
unexplained, pre-page material of exactly pad-like shape. (b) `round43/X0-firewall/
ADJUDICATION.md` item 31: the blob-as-mod-29-keystream cell was never in any grid, while
the exactly analogous construction for the payload (R28-L2) and for the page-56 hash
(R43-F6 part c) both exist — a measured ledger GAP, not lore.
**Honesty clause (stated in advance):** F3 §4 *lowers* the prior for the whole family —
any blind plaintext-independent additive keystream is excluded in AGGREGATE at 17σ by the
book-wide doublet rate (0.0068 vs floor 0.0186). This lane runs anyway because (i) that
exclusion is aggregate-statistical and assumes natural-language doublet statistics on all
pages — a per-page direct test at measured power is a different and per-cell stronger
kind of evidence; (ii) plaintexts that are themselves doublet-suppressed escape the
floor; (iii) X0 ranked the cell and the cost is minutes. This is close to a completeness
ritual and is labelled as such; it queues exactly where the campaign plan put it (P4).

**Q3 — is the space bounded, and by what?**
Enumerable and exact. Per page: singles 3 blobs × {mod29, div9} × 2 dir × 6 cfg × 256
rot = 18,432; nibble 3 × 2 × 6 × 512 = 18,432; combined 18 streams × mod29 × 2 × 6 ×
256 = 55,296. **N_grid = 92,160 decodes/page; total = 55 × 92,160 = 5,068,800.**
(Correction before any run: the first draft of this file mis-multiplied the combined arm
as 36,864 and named bars at N = 73,728; fixed here, pre-data, with bars recomputed at
N = 92,160. Nothing had been executed against the wrong N.)

**Q4 — the three conditionals this negative will carry** (`three_conditionals`):
- `key_space`: the 3 onion pre-page 256-byte blobs under 3 fixed reductions (byte mod 29;
  byte div 9; interleaved hi/lo nibbles) + the 18 canon-payload-joined streams
  ({canon_256, canon_256_decpref} × 3 blobs × {XOR, ADD, SUB(canon−blob) mod 256}, byte
  mod 29 only) × {fwd, rev} × all rotations. NOT: other reductions, blob−canon SUB,
  nibble/div9 reductions of the joined streams, cross-blob joins, hashes/PRF expansions
  of the blobs.
- `transition_model`: periodic (repeating) keystream, constant phase per page, additive
  ±, Beaufort, each with optional atbash pre-map — 6 configs, the R43-F5bT `decode()`
  verbatim. NOT: autokey, per-line/per-page resets, skips/rejection rules, one-shot
  (non-wrapping) alignment, transposition, non-mod-29 geometries.
- `adjudicator_register`: panel-R36 (12 registers: EN_MODERN, EN_KJV, LP1_REAL, LATIN,
  OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL, GREEK, HEBREW, NORSE), with the R37 caveat that
  the free control at L=240 fails for OE and EN_HALFVOWEL. Languages outside the panel
  are not seen.

**Q5 — kill condition at ≤10% of budget.** Hard stop if ANY of the three plants fails
(wrong cell, imperfect recovery, degenerate, or pmax < bar). Checkpoint after the plants
+ first 6 pages: if projected wall time exceeds 4 hours, stop and re-scope (benchmark
says ~1 minute, so this should never fire).

## Fixed thresholds (standing instrument)

- Adjudicator: `analysis/round19/I2/adjudicate.py` `adjudicate`/`adjudicate_batch` with
  `Panel(data/panels/panel-r36.npz)` — the exact wiring of R43-F6 keystream part (c) and
  R43-F5bT.
- Bar: `analysis/round34/I1-v3-null/bars_v3.py` `bar_v3(N_grid, L_cap, "free")` at
  N_grid = 92,160, L_cap = max tabulated length in {120, 240, 400, 729} ≤ page length
  (pages shorter than 120 use 120) — the same rule as R43-F6/F5bT. **Named values at
  this lane's N: L_cap 120 → bar 14.0340; L_cap 240 → bar 18.8261** (max unsolved page
  length is 277, so no other node is reachable; for the record 400 → 20.0418,
  729 → 23.1380).
- Hit rule: a cell crosses iff its FULL `adjudicate` pmax ≥ the page's bar AND the decode
  is non-degenerate under the standing guard (mds ≤ 6 or IoC·N ≥ 4.24 ⇒ degenerate,
  R38 I2). Batch pmax is the screen; full adjudicate is the decision.
- Any crosser: **FLAGGED-FOR-ORACLE per `liber-primus/HUMAN-ORACLE.md`, never
  self-certified.**
- Alpha: 0.01 family-wise per page family (bars_v3 default).

## Reductions (justification fixed in advance)

- `mod29`: b % 29 — the repo-standard byte→rune surjection (R12-A1, R43-F6, R28-L2).
- `div9`: b // 9, values 0..28 (255//9 = 28). Distribution 9/256 for symbols 0..27 and
  4/256 for symbol 28 — uniform to within +2% except symbol 28 (EA) at −56%. Justified
  as the natural complementary surjection: mod29 keys off low-order byte structure,
  div9 off high-order bits; both near-uniform, mutually independent maps. The symbol-28
  deficit biases *key* composition, not the adjudicator (decodes remain full-alphabet).
- `nib`: interleaved (hi, lo) nibbles → length-512 stream of values 0..15 ⊂ 0..28
  (16-symbol key alphabet; stated restriction, mirrors R43-F6's nibble arm).
- Direction `rev` = the derived keystream reversed (per-element maps commute with
  reversal, so this equals reducing the reversed byte stream).
- Joined streams: op applied byte-wise on the 256-byte objects (a = canon variant,
  b = blob): XOR a^b; ADD (a+b)%256; SUB (a−b)%256. Then mod29 only.
- Distinctness: all derived mod-29 key tuples are checked pairwise within each length
  class; any collision is reported (family size then conservative), not silently deduped.

## Positive controls (planted through this lane's own extraction + decode glue)

Plaintexts = the three solved-LP paraphrase texts used by R43-F5bT (PT1/PT2/PT3,
rune-indexed via `gp.keyword_to_indices`). Encipherment is the exact inverse of the
sweep's `decode()` at one named cell each; the full 73,728-cell per-page grid must
return the planted cell as grid-best, with exact plaintext recovery, non-degenerate,
pmax ≥ bar:

- **P1**: stream blob1033 single, reduction div9, dir fwd, cfg vigm, rot 77, L = 240.
- **P2**: stream canon_256_decpref XOR blob761 (joined, mod29), dir rev, cfg beau,
  rot 201, L = 200.
- **P3**: stream blob3301, reduction nib, dir fwd, cfg vigp_atb, rot 500, L = 240.

All three pass or no verdict is issued (`control gate`, R42 X1 rule satisfied: the keys
are this lane's own derived streams, the embedding is through the same decode relation
the sweep inverts, and the recognizer is the same batch→full adjudicate path).

## Coverage query (run before this lane; rows cited, none re-run)

- **R43-F6-ONION-BLOB-STRUCTURE** (negative): blobs not moduli, mutually unrelated —
  structure only; explicitly does NOT cover keystream use. Motivates, doesn't cover.
- **R43-F6-PAYLOAD-VS-ONION-BLOBS** (negative): canon × blob × {XOR,ADD,SUB} × 2 orders
  as PAYLOAD candidates (structure detectors + D6 mod-29 screen of the 256-byte output
  itself). Coverage field: "Does NOT cover: keyed/rolling combinations…" — the joined
  stream *as a keystream over the 55 pages* was not in that grid. Not re-run: the 36
  combined outputs are not re-screened as payloads here; they are only used as keys.
- **R43-F6-PAGE56-HASH-AS-KEY** (negative): the exactly analogous construction with the
  page-56 hash as key (0/55, best 4.596 vs bar 11.27). Different key material; cited as
  the harness precedent.
- **R28-L2-CONTESTED-BYTES** (negative): canon payload variants as DIRECT keys over the
  same 55 pages + corpus (fwd/rev × sign × atbash × beaufort × offsets 0..255, 21.6M
  decodes). This is why canon_256 ALONE is not swept here — covered. The canon⊕blob
  joins are not in its coverage.
- **R30-B1-BLOB-CRYPTO** (negative): keyed symmetric ciphers over T2/folly/canon blobs —
  different family (those are the T2/folly blobs, and the construction is block-cipher
  decrypt, not mod-29 keystream).
- **H-03** (negative): 2013 cookies XOR'd against 256-byte blobs, 80%-ASCII gate —
  different operand, different recognizer, 64 trials; does not cover this grid.
- **R12-A1 / B-02 / B-08 / R17-PUBLIC-PAD** (negative/partially-run): other pads as
  byte→mod-29 keystreams — same construction family, disjoint key material.
- **R43-F5BT-TIMING-KEYSTREAM** (negative): the harness this lane reuses, with the
  timing channel as key. Disjoint key material.

No eliminated cell is re-run: the three blobs × mod-29-keystream × 55 pages has no row.

## Outputs

`extract_and_run.py` (one runner: extraction, plants, sweep), `p4_results.json`
(controls, per-page best with full SWEEPROW statistics, crossers, bars, verdict),
`RESULTS.md`, `ledger_rows.json` (drafts only; LEDGER.json untouched). R3 statistics
(ioc, mds, h2, zl, en, full z-panel) persisted for every per-page best row and every
crosser via full `adjudicate`.
