# Round 41 — SYNTHESIS (THE BAR OF RECORD)

_Lanes run 2026-10-31 on the owner's laptop; closeout and X1 part B 2026-11-02. Plan of record:
[`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md). Doctrine: [`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md).
Four lanes closed (I1, C1, B2-filed, X1 parts A+B); **S1/S2/S3 (sandbox) never launched — they roll to
Round 42 carrying a deadline** (the S2 snapshot expires ~2026-11-06). `LEDGER.json` 299 rows, 0 errors,
0 unsound negatives; `tests/validate.py` passes; full non-network pytest 110 passed / 5 skipped;
`check_ceiling.py` PASS (125 rows, 110 pins); no document drift._

## 1. Verdict in one paragraph

No survivor. The round did what it pre-registered: **the bars every sweep is judged against are now fitted
on the population they are applied to.** I1 refit the twelve-register null on real sweep survivors (wrong-key
heads that pass `pf_v4_12`, decoded by beam_v3) — the bar of record is `bars_v3(family="survivor12")`, max of
the refit and the pooled real-sweep POT line: ≈9.34–9.44 at actual N, 10.4645/10.4856 at N=1e6, stated as an
upper bracket (true 1 % level between ≈7.1 and 10.5). All 34 best rows of Rounds 36–40 were re-judged under
it: 0 cross, the stored best (7.10) sits ≥2.3 below, and the withdrawn KDF flag stays withdrawn (6.528 vs
7.438 at N=591). B2 (bash 4.2 key offsets/sign) filed from X1's corrected text: four LP64 cells swept
(77,594,624 seeds each; offset 3 half), 0 flagged, best 6.831 vs 9.344 — and the misaligned-control finding
is real but relation-specific (offset 1 under keyskip1 10/15 recovered, under keyskip2 0/15), so the offset-0
negatives partly reach offsets 1–2 already. C1 re-scored the two archive-blocked English-only families from
the recovered campaign7 code (the archived bests -6.897 and -6.873 reproduced exactly, every per-variant/per-matrix best included):
R14 and R15 are **negative** under matched block-permutation nulls with 120/120 and 144/144 plants recognised;
three matrix cells move to TRIED. The round's own red-team then found the round's blind spot: C1's five
"artefact absent" verifications were made **in a fresh clone where gitignored corpora do not exist** — four of
them are present in the canonical tree (R35 keytexts, R36 dated pads, the 43-B1 OSINT raw, the R44 expand
books), so those cells are not blocked, they are **runnable and waiting**.

## 2. Lane scoreboard

| lane | verdict | control | coverage × power | headline |
|---|---|---|---|---|
| I1 | instrument refit LANDED | 470/480 screen-passers clear both bars, min pmax120 12.35 | ≥40k draws L=120 + ≥5k L=240 per relation; KS vs real survivors p 0.49–0.67 on 131,786 rows | bar of record 9.34–9.44 actual-N / 10.46–10.49 at 1e6 (upper bracket); 34 rows re-judged, 0 cross; null12 retired from actual-N claims. |
| C1 | R14 NEGATIVE, R15 NEGATIVE; cells H4×F3, L2×F3, L15×F2 → TRIED; R44 partially-run (control kill 0.743–0.815 < 0.90); R31/R35/R36/43-B1 inconclusive | 120/120 + 144/144 recognised (plants 28.0+ vs null max 5.81) | R14 1,120 units / R15 1,344 units × 3 block sizes × D=1000, decision p ≥ 0.37 everywhere | faithful to the archived code (exact best reproduction); no crosser; the five "blocked" verifications are clone-scoped — see X1-B. |
| B2 | filed: partially-run (4 of a 116-cell axis = 4.7 %) | 40 natural-rate plants/cell, 39–40/40; X1 re-plants 9/10 + 5/5 | (0,+1), (1,-1), (2,-1) full + (3,-1) half, LP64; 65k survivors/cell both relations | 0 flagged, best 6.831 vs bar of record 9.344; relation-specific partial reach at offsets 1–2 from the offset-0 sweeps. |
| S1/S2/S3 | **NOT RUN** | — | — | the S2 window-2 snapshot (`snap_ff0SWU76EW32OqbWJvp00fnORypR`) expires ~2026-11-06; S3 is ~10 min; all three head Round 42. |
| X1-A | FOUND-ERROR ×9, all bounded, no verdict flips | independent re-plants, refits, recounts | — | Q5 fired-and-overridden must be said plainly; KDF pin 7.435→7.438; six stale lenient null12 bars on the ceiling page (now patched); B2's bar/denominator/control-scope corrected before filing; WATCH-band policy proposed. |
| X1-B | FOUND-ERROR ×5 (B-1, B-2 systemic, B-3, B-9 ×2), no verdict flips | 112 independent checks green | — | 21 exact null ties dropped by float32 at R14-b1000/P (p 0.854 vs 0.833; decision 0.893 either way); four clone-scoped absence claims corrected (artefacts present here); the documented full gate had been red since Round 32 (repaired). |

## 3. What the instrument now says that it did not say yesterday

1. **There is one bar, and it is fitted on the right population.** `bars_v3(N, L, rel, family="survivor12")`
   supersedes every null12 "actual-N" number in rows and on the ceiling page (patched, pinned, checker green).
   Quote it as an upper bracket; the exponential tail overstates the 1 % level by ≈2.7–3.5 against the observed
   survivor tail (endpoint ≈7.1).
2. **The gate has a known insensitivity, with a named fix on the table.** Plants that pass the screen score
   12.35+, so the 9.4–10.5 gate loses nothing for in-model keys — but a partially-decoded true key outside the
   transition model would land at 7–9 and die silently. X1's proposed WATCH band (any row above the largest
   stored survivor, 7.10 → one L=240 decode + a human look, no oracle bundle) is an owner decision for Round 42.
3. **Four "blocked" cells are not blocked.** The artefacts C1 reported absent exist in the canonical tree
   (33 keytexts; 523 MB of dated-pad data; all six OSINT year files; every expand book) — three of the four need
   zero network. They are doctrine-R5 finite objects and the cheapest honest coverage on offer.
4. **Page-level matched nulls need page-scale blocks.** At b1000 the blockperm preserves whole pages (21/1000
   draws reproduced the observed best page exactly); b100/b250 carry the constraint. One line for every future
   direct-family PREREG.
5. **The full documented gate is green again** — `pytest -m "not network"` had been failing since Round 32 on a
   backcompat test whose contract Round 32 itself changed, and nobody runs the full gate because CI runs a
   subset. Repaired and pinned in both directions (X1-B B-9).

## 4. Red-team findings

Part A (I1, B2): `X1-redteam/RESULTS-A.md` — the Q5 kill fired and was overridden (the row must say so; it now
does), the bar-of-record pins corrected and placed on the page lines, six ceiling rows still quoting null12
patched, B2 filed from corrected text (bars of record, 116-cell denominator, relation-split misaligned
control), and the pooled real sample's non-independence noted. Part B (C1, S, gate): `X1-redteam/RESULTS-B.md`
— the float32 tie recount, the clone-scoped absence claims (with the two artefact-search rules proposed for
the doctrine), the b1000-only parenthetical, the never-applied C1 patch superseded with corrected text, and
the two-test repair of the documented gate. All patches applied and verified token-by-token
(`ledger_patches_a.json`, `ledger_b2_corrected.json`, `ledger_patches_b.json`).

## 5. Owner decisions pending (carried to Round 42)

1. **WATCH band** (X1-A #12): adopt pmax > 7.10 → L=240 decode + human look? Recommended before the next mass sweep.
2. **R13 DIRECTION**: move `open` → `negative` on the structure-matched null (Round 40 X1)?
3. **KDF noise-crosser**: coordinator adjudicated, X1 concurs — owner sign-off closes it.
4. **`with_degenerate` as SWEEPROW default** (Round 39 T1) and the **N5/N4 L=240 bundle read** (Round 38) — both still open.

## 6. Next

`analysis/round42/CAMPAIGN-PLAN.md` — THE WASTING ASSET AND THE OPEN CELLS: S1/S2 sandbox windows before the
snapshot dies (~2026-11-06), S3 in the same session, the four unblocked artefact cells (R35 keytexts, R36
dated pads, 43-B1 auto keys, R44-expand under a redesigned control), the B2 remainder behind a widened screen
(offset ≥3 needs >2 head skips), and the WATCH band wired into the sweep harness if adopted.
