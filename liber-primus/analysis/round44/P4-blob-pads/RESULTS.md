# R44 / P4 — RESULTS: onion pre-page 256-byte blobs as per-page mod-29 pads

Ran 2026-11-09 per `PREREG.md` (written first; one pre-data grid-arithmetic correction is
documented inside the PREREG itself — the combined arm was mis-multiplied 36,864 → 55,296
and the bars renamed at the correct N = 92,160 before anything executed).
Runner: `extract_and_run.py` → `p4_results.json`. Instrument: the standing panel-R36
adjudicator (`analysis/round19/I2/adjudicate.py`, `data/panels/panel-r36.npz`) + the
standing free-null bars (`analysis/round34/I1-v3-null/bars_v3.py`), same wiring as
R43-F6(c)/R43-F5bT; harness construction = R43-F5bT's runner with key material swapped.

## Headline

**NEGATIVE. 0 / 5,068,800 decodes cross; observed global best pmax 5.881 vs its bar
14.034 (8.2z below), no near-miss on any page.** The F3-J6 join — X0 (R43) item 31, the
one blob cell never in any grid — is now measured and closed at this resolution.

## Extraction (own glue, cross-checked)

Blobs re-extracted by this lane's own regex-over-HTML glue (single ≥512-hex run per
pre-page file, asserted); sha256 digest-matched the R43-F6 record exactly:
`05acf0d8…` (761), `d8c0f83c…` (1033), `4f1cef87…` (3301); canon_256 `3b9b07d9…`,
canon_256_decpref `f42b7caa…`. All shas persisted in `p4_results.json["objects_sha256"]`.

## Positive controls — 3/3 PASSED (gate, before any page was swept)

Known English-register plaintexts enciphered through this lane's own derived keystreams
(R42 X1 rule) and recovered by the identical 92,160-cell sweep loop:

| plant | planted cell | grid-best = planted cell | recovery | pmax | bar |
|---|---|---|---|---|---|
| P1 | blob1033:div9 fwd vigm rot77 L240 | yes | exact | 38.321 | 18.8261 |
| P2 | comb:decpref:blob761:xor rev beau rot201 L200 | yes | exact | 33.398 | 14.0340 |
| P3 | blob3301:nib fwd vigp_atb rot500 L240 | yes | exact | 32.322 | 18.8261 |

All non-degenerate. The pipeline recognises the hunted shape in all three key arms
(div9 single, joined-stream, nibble) and both cipher geometries incl. atbash composition.

## The sweep

- Family (fixed in PREREG): 27 keystreams — 3 blobs × {mod29, div9, nib} + 18 joins
  ({canon, decpref} × 3 blobs × {XOR, ADD, SUB} mod 256, reduced mod 29) — × {fwd, rev}
  × 6 configs (vig± / Beaufort, each ± atbash) × all rotations (256; 512 for nib)
  = **92,160 decodes/page × 55 pages = 5,068,800**.
- Key distinctness: **0 mod-29 collisions** among the 27 derived streams (family size
  exact, no dedup needed).
- Bars of record (named in PREREG before running): **14.0340** (L_cap 120, pages 66–239),
  **18.8261** (L_cap 240, pages 240–277), from `bar_v3(92160, L_cap, "free")`, alpha 0.01.
- Crossers: **0.** Per-page best pmax range **4.48 – 5.88** (a wrong-key free-max
  population exactly where the null expects it at this N).
- Observed global best (full R3 stats in `p4_results.json`): pmax **5.881**, page 14
  (L=137), blob3301:nib fwd vigp_atb rot337, preg EN_HALFVOWEL, en −7.28, ioc·N 1.027,
  mds 16, h2 0.180, zl 0.796, non-degenerate — vs bar 14.034.
- Runners-up: 5.855 (p45, comb:canon:blob1033:sub vigp), 5.795 (p38,
  comb:canon:blob761:xor vigm) — same null band.
- Wall time 73.2 s.

## Numbers vs bar

Best 5.881 vs bar 14.034 → **gap 8.15** in panel-z; against the L_cap-240 pages the best
was further below its 18.8261 bar. Nothing within 8z of either bar. By the standing
hit rule (non-degenerate full-adjudicate pmax ≥ bar) the family is a clean negative.

## Coverage

All 3 pre-page blobs under 3 byte→mod-29 reductions + all 18 canon-payload byte joins
under mod-29; both directions; every whole-period rotation; 6 periodic substitution
configs; all 55 unsolved pages; panel-max over the 12 panel-R36 registers. R3 statistics
persisted for every per-page best and (had there been any) every crosser.

Ledger rows cited (queried before running; none re-run): R43-F6-ONION-BLOB-STRUCTURE,
R43-F6-PAYLOAD-VS-ONION-BLOBS (its coverage field confirms the joined streams were only
ever screened as payload candidates, never run as keystreams — hence the joined arm
here), R43-F6-PAGE56-HASH-AS-KEY (harness precedent), R28-L2-CONTESTED-BYTES (covers
canon-alone-as-key — deliberately NOT re-swept), R30-B1-BLOB-CRYPTO, H-03,
R12-A1 / B-02 / B-08 / R17-PUBLIC-PAD, R43-F5BT-TIMING-KEYSTREAM.

## Not covered (the three conditionals + residue)

- **key_space**: only the three pre-registered reductions; joins only under mod29 and
  only canon−blob SUB; no blob×blob joins, no hash/PRF/KDF expansion of the blobs, no
  use as offset/permutation tables or autokey seeds.
- **transition_model**: periodic constant-phase substitution only — no per-line/per-page
  resets (R44 lane R1's axis), no skips/rejection rules, no one-shot alignment, no
  transposition.
- **adjudicator_register**: the 12 panel-R36 registers (R37 caveat: the free control at
  L=240 fails for OE and EN_HALFVOWEL).
- Context: F3 §4's aggregate 17σ doublet-rate exclusion of ALL blind additive keystreams
  independently bounds this family; this lane adds the direct, per-page, measured-power
  negative for the one named candidate object the ledger had never run.

## Verdict

**NEGATIVE** (status `negative`; draft row `R44-P4-ONION-BLOB-PADS` in
`ledger_rows.json`, not applied — the coordinator applies rows). No crosser, so nothing
is flagged for the oracle. X0 item 31 (NEW-lite) and F3-J6 are discharged at this
resolution; reopens_if is stated in the draft row.
