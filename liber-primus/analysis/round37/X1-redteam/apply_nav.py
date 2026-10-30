#!/usr/bin/env python3
"""Round 37 X1: nav-doc edits (idempotent; each edit is guarded by a marker)."""
import json, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOT = os.path.dirname(LP)
total = json.load(open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))["counts"]["total"]
I12 = sys.argv[1] if len(sys.argv) > 1 else "I1 and I2 were still running at audit time (no RESULTS.md) and are not audited here."


def rw(path, fn):
    t = open(path, encoding="utf-8").read(); n = fn(t)
    if n != t:
        open(path, "w", encoding="utf-8", newline="").write(n); print("edited", path)
    else:
        print("unchanged", path)


SUMMARY = ("Round 37 filed and X1-audited: composed 2016-clause readings (C1: clue strings as seeds/keys, LP1 numbers as key schedules, the map-road-direction rule; 17,392 decodes, panel-R36, all below bars), "
           "prime-line-sum recognizer (no separation; X1 corrected a line-alignment error on page 03), book-code indices (negative on 240 powered cells; word readout inconclusive), geometry (inconclusive: recognizer unpowered), "
           "and the Round 10/11/22 English-only readings re-scored under 12 registers (all negative; closest beam row 6.30 vs bar 6.90), 12-register plumbing; "
           "X1 found 5 errors (U4 alignment, C1 candidate/line-sum gaps and the 'literal' label, C3 post-data null swap, O4 correction only half-applied) in "
           "`liber-primus/analysis/round37/X1-redteam/RESULTS.md`. " + I12)

# 1. root README status line
def f_readme(t):
    if "Round 37 filed and X1-audited" in t:
        return t
    key = "*Status current as of 2026-10-30 (**Round 36 filed, B1 still sweeping**:"
    assert key in t
    return t.replace(key, "*Status current as of 2026-10-30 (**" + SUMMARY + "** Earlier: **Round 36 filed, B1 still sweeping**:", 1)
rw(os.path.join(ROOT, "README.md"), f_readme)

# 2. ELIMINATION-LEDGER: new section above Round 36
def f_elim(t):
    if "## Round 37 " in t:
        return t
    sec = ("## Round 37 — THE UNTRIED READINGS AND THE 12-REGISTER TOOLING (2026-10-30)\n\n"
           "Rows `R37-*` in `LEDGER.json` (T1, C1 x3, C2 U4/U7/U7-W/U8, C3 x11, X1) plus retro-rows `R10-L2-MAP`, `R10-L3-ROAD`; `F-02` -> partially-run; `R11-*`, `R22-C` restated with an ADDED 12-register result (the original English-only result is kept). "
           + I12 + " Full write-up `analysis/round37/X1-redteam/RESULTS.md`; every verdict below is conditional on key space x transition model x register panel, with positive controls planted in EN_MODERN (C1) or EN_MODERN/LATIN/GREEK (C3) only.\n"
           "- **R37-C1** the signed 2016 message as seeds/keys (83 strings x direct / SHA-256-CTR / PBKDF2; 17,392 decodes in all), LP1's own Gematria sums as key schedules (16 variants), and the composed map -> road -> direction rule (348 settings x 3 page heads): controls 6/6, 32/32, 24/24; best 5.24 / 4.79 / 5.09 vs actual-N bars 6.5-7.2. **X1:** 5 of 7 signed clauses were seeded (C-2016-6/7 missing); the printed LP1 line sums were not used (the koans-file lines match only A WARNING); the composed rule's \"literal\" label is C1's operationalization (lagged cipher-word pointer, O4 seed orders, semantic \"meaning\" untested). The \"words/map, meaning/road\" row F-02 is therefore partially-run, not closed.\n"
           "- **R37-C2** U4 prime line sums: NO-SEPARATION (plaintext pooled 21/60 vs null 0.162, but one page, A WARNING, carries it; ciphertext at null). **X1 corrected** a line-boundary misalignment on pages with interrupters (page 03 4/8 -> 3/8). U7 book-code indices: negative on 240 R/F selections (144 powered), 80 word-readout cells inconclusive (control B failed: random LP1 word bags score 12.2 vs 14.5). U8 per-page geometry: inconclusive (the glyph recognizer found 0/5 planted glyphs; the 232-render sweep is diagnostic only).\n"
           "- **R37-C3** Round 10 L2/L3, Round 11 N1-N5/S1/S2 and Round 22-C re-scored under panel-R36 + beam_v3: all negative; the Round 10 z=6.94 near-flag is an English-gated artefact (pmax 3.94, p~0.07 single reading); closest beam row N5 6.30 vs bar 6.90 (within-family tail p~0.05, listed for L=240). **X1:** the doublet-matched null replaced the first-pass plain shuffle after three families showed p(Z)<0.01 in it; flagged `threshold_fixed_in_advance=false`.\n"
           "- **R37-T1** 12-register plumbing: stock `validate_store` now reads the R36 B1 12-wide store and still reads the R35 9-wide store; `hitfn20`/`panelmax20` refuse a mismatched panel; CI runs `tests/test_12reg_plumbing.py`.\n"
           "- **R37-X1** FOUND-ERROR x5 (above) and O4 recount: NEVER 68 -> 66 (R36 X1) -> 60; English-only/legacy 46; the semantic family F5 (19 NEVER cells) is untouched.\n\n")
    key = "## Round 36 — THE 12-REGISTER PANEL AND THE RE-GATE (2026-10-30)"
    assert key in t
    return t.replace(key, sec + key, 1)
rw(os.path.join(LP, "ELIMINATION-LEDGER.md"), f_elim)

# 3. analysis/README.md rows
def f_an(t):
    if "round37/X1-redteam/" in t:
        return t
    key = "| [`round36/`](round36/) |"
    assert key in t
    row = ("| [`round37/`](round37/) | **Round 37 — THE UNTRIED READINGS (T1, C1, C2 U4/U7/U8, C3; I1/I2 per their own RESULTS; no survivor) 2026-10-30** | "
           "**C1** 2016 clauses as seeds/keys, LP1 numbers as schedules, composed map-road-direction: 17,392 decodes, all below bars. **C2** U4 prime-line sums NO-SEPARATION, U7 book-code negative (W cells inconclusive), U8 geometry inconclusive. "
           "**C3** R10/R11/R22-C re-scored in 12 registers, negative (z=6.94 near-flag = artefact). **T1** 12-wide stores validate. **X1** FOUND-ERROR: U4 alignment, C1 candidate/line-sum gaps, C3 post-data null, O4 correction half-applied. "
           "| [`CAMPAIGN-PLAN.md`](round37/CAMPAIGN-PLAN.md), [`X1-redteam/RESULTS.md`](round37/X1-redteam/RESULTS.md), [`C1-composed-clue-readings/RESULTS.md`](round37/C1-composed-clue-readings/RESULTS.md) |\n")
    return t.replace(key, row + key, 1)
rw(os.path.join(LP, "analysis", "README.md"), f_an)

# 4. PICKUP-HERE
def f_pick(t):
    if "Round 37 X1" in t:
        return t
    key = "> **Round 36 closeout (coordinator, 2026-10-30):**"
    assert key in t
    blk = ("> **Round 37 X1 (red-team, 2026-10-30):** the untried clue readings (C1/C2/C3) and the 12-register plumbing (T1) are filed; no survivor; "
           "`LEDGER.json` now holds **" + str(total) + " entries**. X1 FOUND-ERROR x5 -> `analysis/round37/X1-redteam/RESULTS.md`. **Still open:** the semantic reading of \"their meaning is the road\" (19 NEVER F5 cells) and "
           "C1's skipped literal alternatives (lagged cipher-word pointer, printed-line sums, C-2016-6/7); N5 top rows at L=240; a power-adequate U8 glyph recognizer; O4 `matrix.md` still says NEVER 68 (true: 60 after Round 37). "
           "**Time-critical:** the sandbox S2 window lists expire ~2026-11-06 and are not exported. " + I12 + "\n\n")
    t = t.replace(key, blk + key, 1)
    # keep the other count lines true
    t = re.sub(r"\(220 rows as of the R36 X1 merge, 2026-10-30; was 181", "(%d rows as of the R37 X1 merge, 2026-10-30; was 220 at R36 X1, 181" % total, t)
    t = re.sub(r"\*\*220 entries\*\* \(R36 X1-merge count; was 162", "**%d entries** (R37 X1-merge count; was 220 at R36 X1, 162" % total, t)
    return t
rw(os.path.join(LP, "PICKUP-HERE.md"), f_pick)

# 5. PAPER.md counts
def f_paper(t):
    t = t.replace("220 ledger entries", "%d ledger entries" % total).replace("All 220 entries", "All %d entries" % total)
    return t
rw(os.path.join(ROOT, "PAPER.md"), f_paper)
