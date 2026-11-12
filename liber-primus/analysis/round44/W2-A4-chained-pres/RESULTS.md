# R44 / WAVE-2 CELL A4 — chained (ciphertext-feedback) constructions parameterized by presentation channels — RESULTS

_2026-11-09. PREREG.md hash-stamped in `run.log` before first execution
(sha256 a88cf917… original, re-stamped after the pre-run wording Addendum 0)._

## Verdict

**NEGATIVE** (measured, panel-R36), **0 crossers** in 34,336 adjudicated cells vs bars fixed
in advance at N_bar = 50,000. No FLAGGED-FOR-ORACLE items.

| tier | cells | best pmax | bar of record | margin |
|---|---:|---:|---:|---|
| A — page-local complete cover (16 variants × 29 offsets × 55 pages) | 25,520 | **5.774** (page 40, L 231, s1=+1, s2=−1, k=2, continuous, o=24, preg 2) | 13.7082 (L_cap 120) / 18.3740 (L_cap 240) | ~8 units below the lowest bar |
| B — book-wide joint constructions on head-729 (= pages 0+1+2) | 8,816 unique of 13,920 nominal θ | **3.782** (s1=−1, s2=−1, k=2, page-scope, offsets 16/15/13; preg 11) | 22.6951 | ~19 below |

Doctrine-R3 statistics persisted for every page-best row and the tier-B best
(`results.json`: pmax, preg, pmax_ne, ioc, mds, h2, zl, en, degenerate).

## What was run (exactly the PREREG family)

Decode `p_i = (σ1·c_i + σ2·c_{i−k} + o_p) mod 29`, k ∈ {1,2}, scope ∈ {page-restart,
book-continuous}, forward, skip-free exact; per-page offset `o_p = (σ3·f(ch_p)+s) mod 29`,
ch ∈ {red count r_p (P1 census), sep3 count, sep-all count (P3 glue), page index, red-head
section index}, f ∈ {identity, mod29(≡identity, deduped), prime-index, cumulative}, σ3 ∈ ±1,
s ∈ 0..28. The **collapse lemma** (PREREG Q3, asserted at runtime) makes tier A a COMPLETE
page-granularity cover of the family: every offset any (ch,f,σ3,s) can give a page is one of
the 29 swept; tier B then tests joint cross-page consistency of every named θ on the head.
(Tier A carries 232 structural duplicate rows — page 0's scope twins — kept for enumeration
simplicity; tier B's 13,920 θ dedup to 8,816 distinct decoded streams, all adjudicated.)

## Positive controls (own glue, gated BEFORE the sweep — `plant_results.json`, `gate.json`)

- **G1 (tier A):** F5b-T control English enciphered with θ* = (+1,−1,k=1,page; o from s3 ×
  prime-index × σ3=−1, s=17) onto pages 10 and 20 of a corpus copy, pushed through the
  IDENTICAL 464-row page grid: planted cell = grid max on both pages, recovery **1.0/1.0**,
  pmax **39.75 / 39.78** ≥ bar 18.374, non-degenerate. Differentials: wrong offset → recovery
  0.0, pmax 3.4–4.8; wrong feedback sign → recovery 0.03–0.04, pmax 1.8–1.9.
- **G2 (tier B):** control English enciphered with θ** = (−1,+1,k=2,continuous; o from r ×
  cumulative, σ3=+1, s=5) onto pages 0–2, pushed through the IDENTICAL 13,920-θ enumeration:
  argmax = the planted key class exactly, recovery **1.0**, pmax **62.33** ≥ 22.6951.
- **GATE PASSED** (both clauses); Q5 did not fire.

## Coverage

All 55 unsolved canon pages × the complete per-page offset space of the family × 16
(σ1,σ2,k,scope) variants (tier A, measured power 1.0 via G1's end-to-end plant), plus all
13,920 named book-wide constructions on head-729 (tier B, power via G2). Discharges the
"chained/output-aware constructions taking red as input / parameterised by red" not_covered
of `R44-P1-RED-SELECTION` / `R44-P1-RED-KEYPARAM` for THIS bounded family, and puts the first
panel-R36 (12-register) negative on ciphertext-feedback constructions at k ∈ {1,2} (R12-C1's
ct-feedback negatives were English-quadgram-only, k=2..6, constant seeds).

## Not covered (the three conditionals, restated)

1. **Key space:** offsets beyond the per-page-additive form (per-LINE or per-WORD offsets,
   offsets varying within a page, channel ALGEBRA beyond the named f-set — differences,
   products, exclusive-cumulative); channels not censused per page (dot-block counts exist on
   only 3 pages and were not formed into a channel); reversed reading direction.
2. **Transition model:** multiplicative feedback coefficients a ∉ {±1} (D-04's open ground —
   2026-07 gate ran 3 pages, English-only), k ≥ 3, plaintext-feedback (R37-C3-U6A-N1-PT
   covers its N1 configs skip-free only), mixed pt/ct sources, hybrid keystream+feedback
   constructions with a rejection loop (not representable by this exact decoder).
3. **Adjudicator register:** panel-R36's 12 registers only; plaintexts outside them invisible.
   Tier-B head scoring covers pages 0–2 jointly; joint consistency over OTHER page subsets is
   implied only via tier A's per-page completeness, not scored as windows.

## Files

`PREREG.md` (hash-stamped), `chained.py`, `plant_gate.py` → `gate.json` + `plant_results.json`,
`run_sweep.py` → `results.json`, `run.log`, `ledger_rows.json` (draft — LEDGER.json not
modified).

Reproduce: `cd liber-primus/analysis/round44/W2-A4-chained-pres && python3 plant_gate.py && python3 run_sweep.py`
