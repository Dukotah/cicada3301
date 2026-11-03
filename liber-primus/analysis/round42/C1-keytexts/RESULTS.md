# Round 42 / C1 — R35 keytexts (H7xF4, H8xF4) under panel-R36: RESULTS

2026-11-02. `PREREG.md` first. panel-R36, standing free-null bar of record.

## Result: NEGATIVE (measured, 12 registers) — and a data-integrity finding

X1-B/R41 (B-2) showed `round12/C2/texts/` is present (C1's "absent" was a clone-scoped search).
Running the cell revealed a second problem the clone-scoped view hid:

- **Data integrity: 10 of the 33 "keytexts" are corrupt.** They are globalgrey
  "Page Not Found" HTML error pages (8,674 B each), not the intended esoteric texts:
  `achad_qbl, alghazali_alchemy_happiness, dee_hieroglyphic_monad, emerald_tablet_hermetic,
  iamblichus_mysteries, meister_eckhart_pfeiffer, porphyry_life_plotinus, sepher_yetzirah_westcott,
  theologia_germanica, waite_holy_kabbalah`. These were classified out before scoring, so the
  negative is not manufactured by feeding garbage. (The R35 corpus was a stale fetch; the 10 would
  need a fresh, hash-pinned re-download to be tested.)
- **23 real texts swept** as running keys over the 55 unsolved pages: each transliterated to rune
  indices, windowed from ~150 stride-sampled start offsets, both signs, both atbash, every decode
  adjudicated under panel-R36 (panel-max over 12 registers incl. LATIN/OE/GREEK/HEBREW for the
  Latin/Greek/Hebrew source texts). Grid ~13,800.
- **Verdict.** Global best **pmax 5.479** (`boehme_aurora.txt`, page 26, L=265, start 100800,
  sign-1 atb1, register LP1_REAL) vs free bar of record **17.42**. **0 crossers**, no near-miss.

H7xF4 / H8xF4 move from **T-LEG (legacy/English-only)** to **TRIED (panel-R36)**: a measured
negative at full 12-register power over the 23 intact texts, with 10 corrupt captures recorded as
not-covered-pending-refetch.

## Scope / not covered
The 10 corrupt 404 captures (need a fresh hash-pinned re-download); running-key offsets beyond the
~150 stride-sample per text; texts not in this 33-file corpus; the free bar is the standing null,
not a fresh per-shuffle null.

## Ledger
Adds `R42-C1-R35-KEYTEXTS-RUN` (negative); patches `R41-C1-R35-KEYTEXTS-VERIFIED` (the clone-scoped
stub) with the run result + the corrupt-corpus finding.

## Files
`PREREG.md`, `RESULTS.md`, `run_c1.py`, `c1_results.json`, `ledger_patches.json`, `apply_ledger.py`.
