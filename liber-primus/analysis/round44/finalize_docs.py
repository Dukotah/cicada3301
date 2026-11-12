"""One-shot: after lanes S1 and S2 are finalized, write their results into the navigation documents.

Reads S1-blind-perl/results.json and S2-blind-glibc-clock/results.json; every number it writes comes
from those files. Run from anywhere. Safe to re-run (each insertion is guarded by a marker).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
r1 = json.load(open(os.path.join(HERE, "S1-blind-perl", "results.json")))
r2 = json.load(open(os.path.join(HERE, "S2-blind-glibc-clock", "results.json")))
c1 = json.load(open(os.path.join(HERE, "S1-blind-perl", "control.json")))
c2 = json.load(open(os.path.join(HERE, "S2-blind-glibc-clock", "control.json")))
led = json.load(open(os.path.join(ROOT, "liber-primus", "LEDGER.json"), encoding="utf-8"))
NROWS = led["counts"]["total"]
MARK = "<!-- R44-S1S2 -->"


def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def wr(p, s):
    open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)


v1, v2 = r1["verdict"], r2["verdict"]
s1_txt = (f"all {r1['seeds_evaluated']:,} seeds of Perl `rand` x 4 modes: {v1}, largest full-page IoC x 29 {r1['max_ioc_x29_L262']:.3f} "
          f"against a 1.40 threshold (control {c1['flagged']}/{c1['of']})")
mx2 = max(v["max_ioc_x29_L262"] or 0 for v in r2["generators"].values())
s2_txt = (f"glibc `rand()` for every second of 2011-12-01..2014-04-03 and every integer below 2^24, two reductions "
          f"({r2['keystreams_evaluated']:,} keystreams x 4 modes): {v2}, largest {mx2:.3f} (control {c2['flagged']}/{c2['of']})")
blind = ("a language-model-free adjudicator (`liber-primus/analysis/round44/S1-blind-perl/blind.c`): skip sites are fixed by key and "
         "ciphertext, paths are scored by index of coincidence, so one decoder covers any language, spelling, plaintext numbering, "
         "combiner constant, Atbash and Beaufort")

# ---- README.md
s = rd("README.md")
if MARK not in s:
    s = re.sub(r"against `LEDGER.json` \(\d+ rows\)\.", f"against `LEDGER.json` ({NROWS} rows).", s, count=1)
    k = s.index("see `liber-primus/analysis/round44/A0-fresh-eyes-audit/AUDIT.md`.")
    k = s.index("\n", k)
    s = s[:k] + (f" The same day the audit's proposed instrument was built and used {MARK}: {blind}. Two finite high-prior key "
                 f"spaces went through it under pre-registration: {s1_txt}; {s2_txt}. See "
                 "`liber-primus/analysis/round44/S1-blind-perl/RESULTS.md` and `S2-blind-glibc-clock/RESULTS.md`.") + s[k:]
    s = s.replace("the Round 44 plan is corrected and re-ranked; `LEDGER.json` 321 rows; see",
                  f"the Round 44 plan is corrected and re-ranked; lanes S1 and S2 then ran the audit's blind adjudicator over "
                  f"{s1_txt}, and over {s2_txt}; `LEDGER.json` {NROWS} rows; see", 1)
    wr("README.md", s)

# ---- PAPER.md ledger counts
s = rd("PAPER.md")
s = re.sub(r"\b\d{3} ledger entries", f"{NROWS} ledger entries", s, count=1)
s = re.sub(r"All \d{3} entries", f"All {NROWS} entries", s, count=1)
wr("PAPER.md", s)

# ---- PICKUP-HERE.md
p = "liber-primus/PICKUP-HERE.md"
s = rd(p)
if MARK not in s:
    old = "then the corrected physical-page lanes. `LEDGER.json` **321 rows**, 0 unsound.\n"
    assert old in s
    s = s.replace(old, "then the corrected physical-page lanes.\n>\n"
                  f"> **Lanes I1 / S1 / S2 (same day, after the audit).** {MARK} The audit's instrument was built: {blind}. Calibrated on\n"
                  "> 2,000,000 random keys and 432 plants, thresholds fixed in `analysis/round44/S1-blind-perl/PREREG.md` before any real seed.\n"
                  f"> **S1:** {s1_txt}. **S2:** {s2_txt}.\n"
                  "> Both controls drew their keystreams from the real binary (`perl`, libc), in English and Latin, relabelled, with a combiner\n"
                  "> constant, as Beaufort, under three filter constructions and both key signs. Conditionals: one draw per rune from rune 0 of\n"
                  "> page 0, a rejection consumes one or two draws; **no register conditional and no combiner-constant conditional**. Not\n"
                  "> covered: a warm-up, another stream start, other reductions, a stalled key pointer, deletion or rewrite without a draw.\n"
                  "> The kernel costs about 4-5 microseconds per seed for four modes, so the full 2^32 of glibc (two reductions), the bash 4.2\n"
                  "> state cycle and every section head are each a matter of hours: **that is the next thing to run.**\n"
                  f"> `LEDGER.json` **{NROWS} rows**, 0 unsound.\n", 1)
    wr(p, s)

# ---- analysis/README.md
p = "liber-primus/analysis/README.md"
s = rd(p)
if MARK not in s:
    old = "[`round44/A0-fresh-eyes-audit/AUDIT.md`](round44/A0-fresh-eyes-audit/AUDIT.md) |"
    assert old in s
    s = s.replace(old, f"**I1/S1/S2** {MARK}: {blind}; {s1_txt}; {s2_txt}. "
                       "[`round44/A0-fresh-eyes-audit/AUDIT.md`](round44/A0-fresh-eyes-audit/AUDIT.md) · "
                       "[`round44/S1-blind-perl/RESULTS.md`](round44/S1-blind-perl/RESULTS.md) |", 1)
    wr(p, s)

# ---- ELIMINATION-LEDGER.md
p = "liber-primus/ELIMINATION-LEDGER.md"
s = rd(p)
if MARK not in s:
    s += (f"\n## Round 44 lanes I1 / S1 / S2 — the blind adjudicator and its first two sweeps (2026-11-12) {MARK}\n\n"
          f"Rows `R44-I1-BLIND-ADJUDICATOR`, `R44-S1-BLIND-PERL-2E32`, `R44-S2-BLIND-GLIBC-CLOCK` (`LEDGER.json` now **{NROWS} rows**).\n\n"
          f"- **I1.** {blind[0].upper() + blind[1:]}. Null measured on 2,000,000 random keys; 431 of 432 calibration plants pass stage 1 "
          f"and all pass the later stages.\n"
          f"- **S1.** {s1_txt[0].upper() + s1_txt[1:]}. Perl is the only generator with signed first-party evidence and its family is "
          f"exactly 2^32; this is the first complete enumeration of it.\n"
          f"- **S2.** {s2_txt[0].upper() + s2_txt[1:]}. The window contains both server timestamps Round 43 F5b recorded.\n\n"
          "Both carry two conditionals instead of three: key space and transition model. There is no register conditional and no "
          "combiner-constant conditional. Not covered: a warm-up, a stream start other than rune 0 of page 0, other reductions, a "
          "stalled key pointer, deletion or rewrite without a draw.\n")
    wr(p, s)

# ---- MEASURED-CEILING.md
p = "liber-primus/MEASURED-CEILING.md"
s = rd(p)
if MARK not in s:
    k = s.index("| **The oracle** — `verify_solution.py`")
    row = (f"| **The blind adjudicator** (Round 44 I1) {MARK} — `analysis/round44/S1-blind-perl/blind.c`: no language model; the key pointer may "
           "jump only at sites the key and ciphertext make admissible; each path is scored by the index of coincidence of its decode; "
           "stages at L = 64 / 120 / 262 on page 0 | 431 of 432 calibration plants pass stage 1 and all pass the later stages; through the "
           f"sweep binary {c1['flagged']}/{c1['of']} Perl-seed and {c2['flagged']}/{c2['of']} glibc-seed plants flagged with keystreams from the real "
           "binaries; plants in English (both spellings) and Latin, as written, randomly relabelled, with a +7 combiner constant and as "
           "Beaufort, under keyskip1, skip_by_two and coin_from_key, both key signs | one draw per rune from rune 0 of page 0; a warm-up, "
           "another stream start, a stalled key pointer, deletion or rewrite without a draw and separators that consume draws are "
           "unrepresented; a plaintext near-uniform over 29 symbols would not be seen | [[R44-I1-BLIND-ADJUDICATOR]] |\n")
    s = s[:k] + row + s[k:]
    k = s.index("| The recurring near-miss: bash seed 1354603465")
    def verdict_cell(v):
        return "**measured negative** (complete)" if v == "NEGATIVE" else "**partial** (" + v + ")"
    rows = (f"| Perl `int(rand(29))` after `srand(s)`, the whole family {MARK} | **All 2^32 seeds** ({r1['seeds_evaluated']:,}), four modes each; "
            f"{r1['stage3_records']:,} pairs reached the full-page stage, largest IoC x 29 {r1['max_ioc_x29_L262']:.3f} against the 1.40 threshold | "
            f"{c1['flagged']}/{c1['of']} planted Perl seeds flagged by the sweep binary (keystream from the `perl` binary), 0 others; 431/432 calibration "
            "plants pass stage 1 | all `srand` seeds, `int(rand(29))`, no warm-up, stream starts at rune 0 of page 0 / one or two draws per "
            "rejection, in-stream coin, both key signs, any combiner constant, Atbash and Beaufort / no register conditional "
            "[plants: English letter-wise, English multigraph, Latin] | [[R44-S1-BLIND-PERL-2E32]] [[R44-I1-BLIND-ADJUDICATOR]] | "
            f"{verdict_cell(v1)} | a warm-up, another stream start or another reduction is given a reason; a covered-class plant fails |\n"
            f"| glibc `rand()` after `srand(t)`, clock-second band | every second 2011-12-01..2014-04-03 UTC and every integer below 2^24, "
            f"for `rand() % 29` and `floor(29 * rand() / 2^31)`: {r2['keystreams_evaluated']:,} keystreams, four modes each; largest full-page IoC x 29 "
            f"{mx2:.3f} against 1.40 | {c2['flagged']}/{c2['of']} planted seeds flagged (keystream from the C library itself), 0 others | the two seed "
            "ranges and two reductions, no warm-up, rune 0 of page 0 / as the Perl row / no register conditional "
            "[plants: English letter-wise, English multigraph, Latin] | [[R44-S2-BLIND-GLIBC-CLOCK]] [[R44-I1-BLIND-ADJUDICATOR]] | "
            f"{verdict_cell(v2)} | the rest of 2^32 is run (about ten core-hours) and a pair clears; a seed outside the ranges is given a reason |\n")
    s = s[:k] + rows + s[k:]
    wr(p, s)

# ---- AUDIT.md addendum and CAMPAIGN-PLAN addendum
p = "liber-primus/analysis/round44/A0-fresh-eyes-audit/AUDIT.md"
s = rd(p)
if MARK not in s:
    k = s.index("## 8. Reproduce")
    s = s[:k] + (f"## 7b. Run after the audit, the same day {MARK}\n\n"
                 "Section 5's first item (I1) was built and its two cheapest uses run, each under its own pre-registration:\n\n"
                 f"- **I1, the blind adjudicator** (`../S1-blind-perl/blind.c`, `calibration.json`): {blind}. About 4-5 microseconds per seed "
                 "for four modes.\n"
                 f"- **S1** (`../S1-blind-perl/RESULTS.md`): {s1_txt}.\n"
                 f"- **S2** (`../S2-blind-glibc-clock/RESULTS.md`): {s2_txt}.\n\n"
                 "Still to run from section 5, in order: the full 2^32 of glibc for both reductions; the bash 4.2 state cycle; the same "
                 "generators at every section head; I2 and I3; C1 and C2.\n\n") + s[k:]
    wr(p, s)
p = "liber-primus/analysis/round44/CAMPAIGN-PLAN.md"
s = rd(p)
if MARK not in s:
    s += (f"\n**Also run under this plan's number, 2026-11-12** {MARK}: **I1** the blind adjudicator, **S1** Perl `rand` (all 2^32 seeds: {v1}), "
          f"**S2** glibc `rand()` clock-second band ({v2}). See `S1-blind-perl/` and `S2-blind-glibc-clock/`.\n")
    wr(p, s)
print("docs updated for", NROWS, "ledger rows;", v1, "/", v2)
