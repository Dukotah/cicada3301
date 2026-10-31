#!/usr/bin/env python3
"""Round 38 X1: nav-doc edits (idempotent; each edit guarded by a marker)."""
import json, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOT = os.path.dirname(LP)
total = json.load(open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))["counts"]["total"]


def rw(path, fn):
    t = open(path, encoding="utf-8").read(); n = fn(t)
    if n != t:
        open(path, "w", encoding="utf-8", newline="").write(n); print("edited", path)
    else:
        print("unchanged", path)


SUMMARY = ("Round 38 filed and X1-audited: S1 exact-lane control independently validated 3/3 and S2 window 1 under panel-R36 (108,611,578 seeds, 0 crossers; panel-R36 coverage 3.809 pp; window 2 launched but UNRECOVERED, not counted); "
           "S2 PHP sandbox never-run (zero coverage); C1 semantic road (WordNet first-synset offset and frequency rank, 28,224 decodes, all below bars); C2 never-cells (clauses 6/7, printed-line sums, lagged pointers, 7 O4 cells run, 34 closed as no-operation-stated, N5/N4 at L=240 flagged-for-oracle but inside a matched null); "
           "I1 glyph recognizer inconclusive (FPR 0.16, control failed); I2 X4 bespoke null (transferred bars too low; 0 of 120 rows clear). X1 found 12 bounded errors, none flipping a verdict, in `liber-primus/analysis/round38/X1-redteam/RESULTS.md`.")

def f_readme(t):
    if "Round 38 filed and X1-audited" in t:
        return t
    key = "*Status current as of 2026-10-30 (**Round 37 filed and X1-audited"
    assert key in t
    return t.replace(key, "*Status current as of 2026-10-31 (**" + SUMMARY + "** Earlier: **Round 37 filed and X1-audited", 1)
rw(os.path.join(ROOT, "README.md"), f_readme)


def f_elim(t):
    if "## Round 38 " in t:
        return t
    sec = ("## Round 38 — THE SANDBOX WINDOWS, THE SEMANTIC ROAD AND THE NEVER CELLS (2026-10-31)\n\n"
           "Rows `R38-*` in `LEDGER.json` (S1, S2 never-run, C1 x2, C2 x5, I1, I2, X1); `R27-CPORT-MT32-FULLSWEEP` carries S2 coverage per instrument; `R32-B2-PHP-MT-RAND` records zero added seeds; `F-02` stays partially-run; `R36-O4-CLUE-COVERAGE` carries the recount. "
           "Full write-up `analysis/round38/X1-redteam/RESULTS.md`; every verdict is conditional on key space x transition model x register panel.\n"
           "- **R38-S1** the S2 (exact) lane's planted control is now independently generated and recovered 3/3 (pmax 17.9-20.8 vs claim bar 7.634); window 1 under panel-R36 advanced 108,611,578 seeds, 0 claim-bar crossers, 0 near-misses (best 7.3007); panel-R36 coverage 3.809 pp of 2^32 (Round 19-gated 44.138 % unchanged). Window 2 was launched but its end state is unrecovered (snapshot `snap_ff0SWU76EW32OqbWJvp00fnORypR`, Vercel quota until 2026-11-01 UTC) and is NOT counted.\n"
           "- **R38-S2** PHP mt_rand tier (b) on the sandbox: never-run (no retained rows); zero seeds added; log-observed FPR/control numbers are not evidence.\n"
           "- **R38-C1** \"their meaning is the road\" as WordNet 3.1 first-synset FILE OFFSET (an identifier, not sense content) and Norvig frequency rank (not a meaning): 28,224 decodes, best 4.62 / 5.296 vs actual-N bars 6.90 / 7.85; negative, definition-conditional. O4 H3xF5 NEVER -> PARTIAL.\n"
           "- **R38-C2** C1-R37 gaps closed (clauses 6/7, printed-line sums, lag-1 pointers: all below bars); seven O4 NEVER cells run (4 TRIED, 3 PARTIAL); 34 closed as \"no operation stated\" (a reopen condition, not a verdict); N5/N4 top-50 at L=240: N5 7.446, N4 8.572, above the screen-N bar, below the N=1e6 bar, inside a cipher-derived-key matched null (p 0.74 / 0.16), non-language: flagged-for-oracle bundle pending the owner.\n"
           "- **R38-I1** stroke-aware glyph recognizer: planted-glyph detection 1.0 but FPR 0.16 (V2 29/50): control failed, inconclusive; the D2 run is not the pre-registered D2; the variant-limited re-score is diagnostic only (three PNGs viewed: nothing to escalate).\n"
           "- **R38-I2** bespoke X4 null: transferred bars undercut it (6.994 vs 5.69 at L=120); 0 of 120 non-degenerate X4 rows clear; the degenerate filter removes only constant decodes (raw 8.70 / 12.40 = recognizer failure).\n"
           "- **R38-X1** FOUND-ERROR x12 (all bounded) and O4 recount: NEVER 60 -> 18; TRIED 35; PARTIAL 7; NO-OPERATION-STATED 34.\n\n")
    key = "## Round 37 — THE UNTRIED READINGS AND THE 12-REGISTER TOOLING (2026-10-30)"
    assert key in t
    return t.replace(key, sec + key, 1)
rw(os.path.join(LP, "ELIMINATION-LEDGER.md"), f_elim)


def f_an(t):
    if "round38/X1-redteam/" in t:
        return t
    key = "| [`round37/`](round37/) |"
    assert key in t
    row = ("| [`round38/`](round38/) | **Round 38 — SANDBOX WINDOWS, SEMANTIC ROAD, NEVER CELLS (S1, S2, C1, C2, I1, I2; X1) 2026-10-31** | "
           "**S1** exact-lane control 3/3 independent; window 1 0 crossers, panel-R36 coverage 3.809 pp; window 2 unrecovered. **S2** PHP sandbox never-run. **C1** WordNet offset / frequency rank readings of \"meaning\", 28,224 decodes, negative. "
           "**C2** C1-R37 gaps + 7 O4 cells run + 34 no-operation-stated; N5/N4 L=240 flagged-for-oracle (inside matched null). **I1** glyph recognizer inconclusive (FPR 0.16). **I2** X4 bespoke null: 0/120 clear. "
           "**X1** FOUND-ERROR x12, none flipping a verdict. | [`CAMPAIGN-PLAN.md`](round38/CAMPAIGN-PLAN.md), [`X1-redteam/RESULTS.md`](round38/X1-redteam/RESULTS.md), [`S1-s2-windows/RESULTS.md`](round38/S1-s2-windows/RESULTS.md) |\n")
    return t.replace(key, row + key, 1)
rw(os.path.join(LP, "analysis", "README.md"), f_an)


def f_pick(t):
    if "Round 38 X1" in t:
        return t
    key = "> **Round 37 X1 (red-team, 2026-10-30):**"
    assert key in t
    blk = ("> **Round 38 X1 (red-team, 2026-10-31):** S1/S2/C1/C2/I1/I2 are filed; no survivor; `LEDGER.json` now holds **" + str(total) + " entries**. X1 FOUND-ERROR x12 (all bounded) -> `analysis/round38/X1-redteam/RESULTS.md`. "
           "**Time-critical:** recover S2 window 2 from snapshot `snap_ff0SWU76EW32OqbWJvp00fnORypR` after the Vercel quota resets (2026-11-01 00:00 UTC) and before ~2026-11-07, and export the R36/after-window-1 lists (snapshots expire ~2026-11-06). "
           "**Owner decision pending:** the N5/N4 L=240 oracle bundle (`round38/C2-never-cells/n5n4/oracle/bundle.json`; expected NOISE-CROSSER, matched-null p 0.16 / 0.74). "
           "**Still open:** 18 NEVER F5 (semantic) cells and sense-similarity readings of \"meaning\" (C1 tested only the first-synset file offset); 34 O4 cells closed only as \"no operation stated\"; a page-matched null for the V2 geometry render; the pre-registered I1 D2 never run; "
           "O4 `matrix.md` table bodies still say NEVER 68 (true after Round 38: 18).\n\n")
    t = t.replace(key, blk + key, 1)
    t = re.sub(r"\(244 rows as of the R37 X1 merge, 2026-10-30; was 220 at R36 X1", "(%d rows as of the R38 X1 merge, 2026-10-31; was 244 at R37 X1, 220 at R36 X1" % total, t)
    t = re.sub(r"\*\*244 entries\*\* \(R37 X1-merge count; was 220 at R36 X1", "**%d entries** (R38 X1-merge count; was 244 at R37 X1, 220 at R36 X1" % total, t)
    return t
rw(os.path.join(LP, "PICKUP-HERE.md"), f_pick)


def f_paper(t):
    return t.replace("244 ledger entries", "%d ledger entries" % total).replace("All 244 entries", "All %d entries" % total)
rw(os.path.join(ROOT, "PAPER.md"), f_paper)
