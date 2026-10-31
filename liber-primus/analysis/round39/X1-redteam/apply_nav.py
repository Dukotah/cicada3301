#!/usr/bin/env python3
"""Round 39 X1: nav-doc edits (idempotent; each edit guarded by a marker)."""
import json, os, re, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOT = os.path.dirname(LP)
total = json.load(open(os.path.join(LP, "LEDGER.json"), encoding="utf-8"))["counts"]["total"]
I1_DONE = os.path.exists(os.path.join(HERE, "..", "I1-v2-page-null", "RESULTS.md"))


def rw(path, fn):
    raw = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    t = raw.replace("\r\n", "\n"); n = fn(t)
    if n != t:
        open(path, "w", encoding="utf-8", newline="").write(n.replace("\n", nl)); print("edited", path)
    else:
        print("unchanged", path)


I1TXT = ("I1 page-matched V2 null: see `analysis/round39/I1-v2-page-null/RESULTS.md`. " if I1_DONE else "I1 page-matched V2 null had no RESULTS.md when X1 audited (not filed). ")
SUMMARY = ("Round 39 filed and X1-audited: `liber-primus/MEASURED-CEILING.md` (one page of what the panel-R36 instrument generation excludes at what power, with `check_ceiling.py` enforcing a ledger row behind every claim; X1 corrected 14 register-scope tags, 3 undisclosed post-data nulls, 4 power-scope claims and 7 omissions and hardened the checker); "
           "T1 standing nulls (degenerate flag, key-matched null, `free` L=120 bar 17.43 -> 15.30; NO-ERROR-FOUND); C1 sense-similarity readings of \"meaning\" (WordNet hypernym depth and lexicographer file, 14,112 decodes, best 5.351 vs bar 7.59; the 18 NEVER F5 cells move to PARTIAL); "
           + I1TXT + "Sandbox lanes S1/S2 were NOT run in Round 39 (moved to Round 40; S2 window 2 recovery is still time-critical).")


def f_readme(t):
    if "Round 39 filed and X1-audited" in t:
        return t
    key = "*Status current as of 2026-10-31 (**Round 38 filed and X1-audited"
    assert key in t
    t = t.replace(key, "*Status current as of 2026-10-31 (**" + SUMMARY + "** Earlier: **Round 38 filed and X1-audited", 1)
    return t


def f_readme2(t):
    t = re.sub(r"\(\d+ rows\)\.", "(%d rows)." % total, t, count=1) if "CI checks every claim on that page against `LEDGER.json`" in t else t
    t = t.replace("swept every enumerable key family and every clue reading the\n> ledger names, each with a planted control.", "swept the enumerable key families and clue readings listed on that page, each with a planted control (the page also lists the enumerable ones it has not finished and the controls that planted only EN_MODERN).")
    return t


def f_readme_all(t):
    return f_readme2(f_readme(t))


rw(os.path.join(ROOT, "README.md"), f_readme_all)


def f_paper(t):
    t = re.sub(r"\b256 ledger entries\b", "%d ledger entries" % total, t)
    t = re.sub(r"\b256 entries\b", "%d entries" % total, t)
    return t


if os.path.exists(os.path.join(ROOT, "PAPER.md")):
    rw(os.path.join(ROOT, "PAPER.md"), f_paper)


def f_elim(t):
    if "## Round 39 " in t:
        return t
    sec = ("## Round 39 — THE MEASURED CEILING (2026-10-31)\n\n"
           "**Read first: [`MEASURED-CEILING.md`](MEASURED-CEILING.md)** (per family: what the panel-R36 instrument generation excludes, at what measured power, under which three conditionals, what re-opens it, and what is not excluded; `analysis/round39/P1-measured-ceiling/check_ceiling.py` fails CI on any claim without a ledger row). "
           "Rows `R39-*` in `LEDGER.json` (P1 audit, T1, C1, S1/S2 never-run, X1" + (", I1" if I1_DONE else "") + "); `R36-O4-CLUE-COVERAGE` carries the cell moves. Full write-up `analysis/round39/X1-redteam/RESULTS.md`.\n"
           "- **R39-P1** MEASURED-CEILING.md written and checker-enforced; X1 corrected its register scope (14 strong-verdict lines had planted EN_MODERN only), 3 undisclosed post-data nulls, the Py2.7 `pair` / SHA-KDF / PHP power scopes and the section-3 omissions (Marsaglia CDROM 77 of 756 units, transcription and additive-cipher assumptions).\n"
           "- **R39-T1** degenerate-decode flag (optional SWEEPROW field), key-matched null benchmark (reproduces the X4 L=120 bar 6.994), `bar_v3(..., 'free')` at L=120 on the 12-register node (17.43 -> 15.30). No cipher claim.\n"
           "- **R39-C1** \"their meaning is the road\" as WordNet 3.1 first-synset hypernym depth and lexicographer-file index (mod 29/28; A1/A2/A3): 14,112 decodes, best 5.351 vs actual-N bar 7.59; negative, definition-conditional. The 18 NEVER F5 cells move to PARTIAL (one generic operationalization), O4 recount: NEVER 0, PARTIAL 25.\n"
           + ("- **R39-I1** see `analysis/round39/I1-v2-page-null/RESULTS.md`.\n" if I1_DONE else "- **R39-I1** page-matched V2 null: no RESULTS.md at audit; not filed.\n")
           + "- **R39-S1-S2-WINDOWS** never-run: the sandbox lanes S1 (S2 window 2 and further windows) and S2 (PHP retry) were not run in Round 39 and moved to Round 40.\n"
           "- **R39-X1** FOUND-ERROR (all bounded, no stored verdict flipped); see RESULTS.md.\n\n")
    key = "## Round 38 — THE SANDBOX WINDOWS, THE SEMANTIC ROAD AND THE NEVER CELLS (2026-10-31)"
    assert key in t
    return t.replace(key, sec + key, 1)


rw(os.path.join(LP, "ELIMINATION-LEDGER.md"), f_elim)


def f_an(t):
    if "round39/X1-redteam/" in t:
        return t
    key = "| [`round38/`](round38/) |"
    assert key in t
    row = ("| [`round39/`](round39/) | **Round 39 — THE MEASURED CEILING (P1, T1, C1, I1; S1/S2 not run; X1) 2026-10-31** | "
           "**P1** [`MEASURED-CEILING.md`](../MEASURED-CEILING.md) + `check_ceiling.py` (every claim tied to a ledger row). **T1** standing nulls (degenerate flag, key-matched null, `free` L=120 bar 15.30). "
           "**C1** WordNet hypernym depth / lexicographer file as \"meaning\": 14,112 decodes, negative; the 18 NEVER F5 cells move to PARTIAL. **I1** " + ("see its RESULTS.md" if I1_DONE else "no RESULTS.md at audit") + ". "
           "**S1/S2** not run (moved to Round 40). **X1** FOUND-ERROR on the page (register scope, post-data nulls, power scopes, omissions) and the checker. | "
           "[`CAMPAIGN-PLAN.md`](round39/CAMPAIGN-PLAN.md), [`X1-redteam/RESULTS.md`](round39/X1-redteam/RESULTS.md), [`P1-measured-ceiling/RESULTS.md`](round39/P1-measured-ceiling/RESULTS.md), [`MEASURED-CEILING.md`](../MEASURED-CEILING.md) |\n")
    return t.replace(key, row + key, 1)


rw(os.path.join(LP, "analysis", "README.md"), f_an)


def f_pick(t):
    if "Round 39 X1" in t:
        return t
    key = "> **Round 38 X1 (red-team, 2026-10-31):**"
    assert key in t
    blk = ("> **Round 39 X1 (red-team, 2026-10-31):** read [`MEASURED-CEILING.md`](MEASURED-CEILING.md) first (what is excluded at what power, and what is not). P1/T1/C1 are filed" + (", I1 too" if I1_DONE else "; I1 had no RESULTS.md") + "; no survivor; `LEDGER.json` now holds **" + str(total) + " entries**. "
           "X1 FOUND-ERROR on the page and checker (all bounded; `analysis/round39/X1-redteam/RESULTS.md`). **Sandbox lanes S1/S2 were not run in Round 39.** **Time-critical (unchanged):** recover S2 window 2 from snapshot `snap_ff0SWU76EW32OqbWJvp00fnORypR` "
           "after 2026-11-01 00:00 UTC and before ~2026-11-07, export the lists, then persistent-session windows; the PHP retry persists control and FPR first. **Owner decisions pending:** the N5/N4 L=240 bundle read; whether the page's scope edits stand; whether `with_degenerate` becomes the SWEEPROW default. "
           "**Still open:** the 18 F5 cells' clue-specific readings (now PARTIAL, not NEVER); the 14 EN_MODERN-only controls re-planted in LATIN/GREEK/EN_NOVOWEL; `skip_by_two` re-runs of the SHA/KDF/public-pad grids; the Marsaglia CDROM (77 of 756 units); O4 `matrix.md` table bodies still say NEVER 68 (true after Round 39: 0 NEVER, 25 PARTIAL).\n\n")
    t = t.replace(key, blk + key, 1)
    t = re.sub(r"\(256 rows as of the R38 X1 merge, 2026-10-31; was 244", "(%d rows as of the R39 X1 merge, 2026-10-31; was 256 at R38 X1, 244" % total, t)
    t = re.sub(r"\*\*256 entries\*\* \(R38 X1-merge count; was 244", "**%d entries** (R39 X1-merge count; was 256 at R38 X1, 244" % total, t)
    return t


rw(os.path.join(LP, "PICKUP-HERE.md"), f_pick)
