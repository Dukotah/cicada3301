# RECON-B — REGISTER of open leads and round-coverage gaps

_2026-08-12. Documentation audit only; no attack run, nothing added to the LEDGER tally._
Scope and acceptance rules fixed in advance: `PREREG.md`.

Two sections. **§1** is what the repo itself still calls open. **§2** is the harder job — where
the *stated scope* of a round falls short of the *claim* the navigation docs now make from it.
Round 9 already caught one of these (the word-length "anomaly" was a large-*n* comparison
artifact that survived a whole round). §2 lists the others.

Status vocabulary: `never-run` · `partially-run` · `scope-limited` ·
`stated-but-uninterpreted` · `declared-closed-but-thin`.

---

## §0. Headline of this audit

Three findings dominate, in order of how much they change what the repo believes:

1. **B-16 — Round 7's "closed by mechanism, not by exhaustion" argument is logically
   incompatible with the repo's own pinned construction.** The kill says any full-length
   natural-language running key injects ~3.3% doublets and only 0.66% are observed. But
   `FINAL-SYNTHESIS.md:40` pins the construction as a **soft anti-repeat rewrite (p_keep≈0.18)
   applied to the output** — which rewrites ~2.8% of positions and would erase exactly those
   injected doublets. Under the repo's own model the doublet deficit cannot discriminate a
   running key at all. The *conclusion* still stands on the ~200 direct keytext sweeps; the
   claim that makes it **independent of which text** does not. This matters because that claim
   is what closed `PICKUP-HERE`'s former #1 open avenue and what killed three verified-absent
   texts at Gate #1 without running them.
2. **B-17 — the multiple-comparisons tally has been frozen at 5 since Round 6** while Rounds 8
   and 9 executed seven more statistical tests. `LEDGER.md:7` declares itself the authority for
   the correction; the correction is now stale by seven tests and by the ~2,670-reading and
   ~166-representation families inside them.
3. **B-15 — Round 6's trigram arm was disclosed INCONCLUSIVE (underpowered, 0.531 counts/cell)
   and is restated in four navigation docs as a flat "no second-order structure."** This is the
   single cleanest case in the repo of a disclosed-underpowered arm being promoted into a
   closure.

---

## §1. Leads the repo itself lists as open, partial or uninterpreted

| id | title | source | status | priority |
|---|---|---|---|---|
| B-01 | Full 32-bit seed sweep — 2 of 10 generators done, not running | `PICKUP-HERE.md:121` | partially-run | high |
| B-04 | Round 9 TEMPLATE re-transcription — stage 3 (diff) never run | `research/ROUND-9-RESULTS.md:133` | partially-run | high |
| B-10 | OutGuess 0.2 Linux control — "closed pending" a run never made | `analysis/stego/STEGO-VERDICT.md:78` | declared-closed-but-thin | high |
| B-03 | Ornament inventory — 47 non-text bands, nobody has read them | `research/DEAD_ENDS.md:358` | stated-but-uninterpreted | medium |
| B-05 | "words are the map" / "meaning is the road" — uninterpreted | `research/ROUND-9-RESULTS.md:129` | stated-but-uninterpreted | medium |
| B-08 | SEED residue — >2³² seeds, other generators, nonzero keystream offset | `research/DEAD_ENDS.md:329` | never-run | medium |
| B-02 | SKELETON corpus extension beyond the 51-text corpus | `PICKUP-HERE.md:123` | scope-limited | medium |
| B-11 | Source PDF + rune-font identification (FRESH-ANGLES track 5) | `research/FRESH-ANGLES-2026-08.md:227` | never-run | medium |
| B-12 | Line geometry + line-fill / per-page word counts | `research/FRESH-ANGLES-2026-08.md:115` | never-run | medium |
| B-13 | O/A/AE per-glyph adjudication — bounded, never individually settled | `analysis/independent-read/FINDINGS.md:95` | partially-run | medium |
| B-23 | Separator audit covered 170 of 604 lines; 19 disagreements unread | `research/ROUND-8-RESULTS.md:377` | partially-run | medium |
| B-09 | OSINT residue — T2/T3 blobs, items 6–9 | `analysis/OSINT-SWEEP-2026-07-27.md:94` | scope-limited | low |
| B-06 | A signed/archival pointer that a specific text *is* the key | `PICKUP-HERE.md:117` | never-run | low |
| B-07 | A correctly-targeted, locally-held archive for the AN END page | `PICKUP-HERE.md:119` | never-run | low |
| B-14 | AUTO_EVOLUTION epoch-6 SEEK roadmap (S1/S2/S3) never executed | `AUTO_EVOLUTION.md:61` | never-run | low |

### Uncommitted-work inventory (asked for explicitly)

**`analysis/direction/`** — COMPLETE and reported. `direction.py` (7.9 KB) +
`direction_results.json`. Ran 2,670 readings on the real ciphertext and on six shuffles;
REAL best −16.0800, null mean −15.9671 sd 0.2825 max −15.6722. Untracked in git. Nothing
unfinished in the run itself; the unfinished part is its *scope statement* — see **B-20**.

**`analysis/retranscribe/`** — **STAGE 2 of 3. This is the largest piece of unfinished work in
the repo.**
- `templates.py` → `templates.npz`, `templates.png`, `templates_report.json` — **done**.
  1,067 distinct exact bitmaps → 226 classes, of which **32 carry ≥100 glyphs**. That is the
  font alphabet recovered from images alone, and it is itself the reported Round-9 result.
- `read.py` → `read_lines.json` (316 KB), `read.log` — **done**. 646 line bands, all 56 pages,
  **16,245 glyphs read** against 13,136 canonical runes (the surplus is separators and
  segmentation splits; nothing has reconciled the two counts).
- `diff.py` — **written, never run.** No diff output exists anywhere on disk. Its own docstring
  states the stakes: *"A clean diff retires the last transcription doubt with a measurement
  rather than an argument… A dirty diff is the transcription discrepancy the program named as
  one of the three inputs that could reopen the cryptanalysis."* Round 9's own text says
  "Status and results appended on completion" — never appended.

**`analysis/seed_sweep/results_full32.txt`** — **INCOMPLETE and NOT RUNNING.** Contents:
```
gen=3 MSVC rand()%29             seeds=0..4294967296  best=-12.8472  hits=0   3013.3s
gen=5 mt19937 init_genrand %29   seeds=0..4294967296  best=-12.7947  hits=0   6520.7s
```
`run_full32.sh` iterates generators in the order `0 3 5 7 9 1 4 6 8 2` and appends `DONE` at
the end. **Two of ten lines are present, gen=0 is missing from the head of its own order, and
there is no `DONE` marker**; file mtime 2026-08-11 20:08 with no live process. So coverage is
**≤2/10 generators at 32 bits** (≈1.7·10¹⁰ of a planned 8.6·10¹⁰ decodes), and the missing
gen=0 line means partial coverage is *not* currently well-defined the way the script intends.
`PICKUP-HERE.md:121` calls it "still running" — that is stale. Note also `sweep.c:389` scores
at `decode_score(k, 0, dir, window)` — **keystream offset is hardcoded 0** and the scoring
window is the **first 48 runes only**, both of which are the documented residue in B-08.

Also untracked: `research/ROUND-9-RESULTS.md` itself, and `research/DEAD_ENDS.md` is modified
but uncommitted — i.e. **the only two places Round 9 exists are both outside git**. See B-18.

---

## §2. Round-vs-claim audit — where a narrow negative became a broad closure

| id | title | source | status | priority |
|---|---|---|---|---|
| B-16 | Round 7's keytext mechanism-kill contradicts the repo's own pinned rewrite construction | `research/DEAD_ENDS.md:238` | declared-closed-but-thin | high |
| B-17 | Multiple-comparisons tally frozen at 5 across Rounds 8–9 | `research/LEDGER.md:11` | declared-closed-but-thin | high |
| B-15 | Round 6 trigram arm disclosed INCONCLUSIVE, restated as flat closure | `research/LEDGER.md:340` | declared-closed-but-thin | high |
| B-18 | Round 9 is invisible to all four navigation docs | `README.md:18` | declared-closed-but-thin | medium |
| B-19 | Round 9 LENGTH closed on the lower bound, not the point estimate | `research/ROUND-9-RESULTS.md:56` | declared-closed-but-thin | medium |
| B-20 | Round 9 DIRECTION: 400-rune reads, ≤64 starts → "do not revive" | `research/DEAD_ENDS.md:483` | scope-limited | medium |
| B-21 | Round 8 SEED residue stated in DEAD_ENDS, dropped by every nav doc | `liber-primus/ELIMINATION-LEDGER.md:273` | declared-closed-but-thin | medium |
| B-22 | Round 7's "orphaned .pyc / not-runnable" premise is now false | `research/DEAD_ENDS.md:255` | declared-closed-but-thin | medium |
| B-24 | Round 2 specificity anchor (AN END, 85 runes) disclosed underpowered | `research/LEDGER.md:110` | declared-closed-but-thin | low |

### The pattern

Rounds 1–9 are, on the whole, unusually honest: **the scope bounds are almost always stated in
`LEDGER.md` and `DEAD_ENDS.md`.** The failure is not in the rounds — it is in the *transfer*
from round doc to navigation doc. In every case above, the bound survives in the round-level
document and is dropped in `README.md` / `PICKUP-HERE.md` / `ELIMINATION-LEDGER.md`, which are
the four docs `CLAUDE.md` designates as carrying the project's state and which are what any
newcomer (or any future agent) actually reads. Round 8's SEED residue paragraph
(`DEAD_ENDS.md:329`) is the cleanest example: it lists Java's 48-bit space, `init_by_array`,
PHP `mt_rand`, .NET, xorshift, RC4 and a nonzero keystream offset as genuinely untested, and
`ELIMINATION-LEDGER.md:273` records the same result as "**seeded-PRNG pads** — do not re-run."

Two exceptions where the round doc itself is the problem rather than the transfer: **B-16**
(the argument is unsound at the round level) and **B-19** (the closing statistic is not the one
the claim needs).

### B-16 in detail — the load-bearing one

`FINAL-SYNTHESIS.md:40` and `README.md:36` both pin the construction as *"a soft
rejection-sampling / anti-repeat filter (p_keep≈0.18) over a memoryless base."* At p_keep 0.18
against a 3.45% collision rate, **~2.8% of ciphertext positions are values that were rewritten
after the additive step.**

Now read the foreclosure the whole keytext closure rests on
(`DEAD_ENDS.md:213`, restated at `:238`, `LEDGER.md:371`, `ELIMINATION-LEDGER.md:72`):

> *Any running-key / full-length natural-language keystream: ruled out by the doublet deficit
> (z ≈ −16.9); such keystreams reproduce a normal ~2.9–3.4% doublet rate.*

Those two statements cannot both be doing work. If the anti-repeat filter is applied to the
*output*, then a running key underneath produces exactly the observed 0.66% — the deficit is a
property of the filter, not of the key. The deficit therefore has **no discriminating power
over key type**, and "dead rigidly (doublet-excluded)" is not an argument.

What actually survives: the ~200-text direct sweeps (Campaigns III/XII/XIII/XVIII, best −5.75
to −5.88 against an English band of −4.0 to −4.35). Those are real and they very likely *do*
cover the rewrite model, because a value-rewrite corrupts only ~2.8% of runes without
desynchronising the key — a 97.2%-correct decode should score near English. **But nobody has
measured that.** Campaign XVIII's validated gate covers key **skip** (desync), not value
**rewrite**; `armada2/COVERAGE-MATRIX.md` has no rewrite row.

So the honest state is: the keytext avenue is closed *by exhaustion over ~200 texts under an
unverified robustness assumption*, not *by mechanism independent of text*. The three
verified-absent texts Round 7 killed at Gate #1 on the mechanism argument alone — Blake's
*Jerusalem* / *Milton* / *The Four Zoas* (`ROUND-7-GATE1-SYNTHESIS.md:11`) — were never run.

**The test that settles it costs an afternoon and is not a revival of a dead family:** plant a
known key, encipher known English, apply the soft anti-repeat rewrite at p_keep = 0.18, and run
the *existing* validated Campaign XVIII decoder over it. If the correct key still scores in the
English band, the coverage assumption is verified, `armada2/COVERAGE-MATRIX.md` gains a rewrite
row, and the closure is sound but should be reworded from "by mechanism" to "by exhaustion." If
it does **not**, then every keytext null in the repo is unsound the same way rigid alignment was
shown to be unsound in Campaign XVIII — and the ~200-text corpus needs re-running under a
rewrite-tolerant decoder.

### B-19 in detail

Round 9 closed the word-length excess by sliding a 2,928-word window across 47 texts and finding
**44 of 47 contain a passage reaching 4.268** (`skeleton/length_anomaly.json` → `h1.n_reaching`).
But **4.268 is the lower bound of the LP2 interval** — it assumes *all 458* ᚠ interrupters are
nulls. The point estimate is **4.425**, the upper bound, and the per-text percentages in the
round table (`ROUND-9-RESULTS.md:39`) are all "% of passages ≥ 4.268". No figure is reported for
≥ 4.425. The verdict "unremarkable for an English passage of its size and register" is therefore
demonstrated at the *most favourable* end of the interval only.

Separately, Round 8 listed four surviving explanations (`DEAD_ENDS.md:430`). Round 9's H2 arm
**quantified** the first — "more nulls than the 458 ᚠ" would need **1,098 inserted runes, a 2.40×
ratio** (`length_anomaly.json` → `h2`) — but quantifying is not refuting, and
`DEAD_ENDS.md:462` nevertheless writes **"Do not re-open the word-length excess."** Re-running
the same sliding-window test at the 4.425 point estimate is roughly a one-line change to
`length_anomaly.py` and would either convert this into a clean closure or expose it.

---

## §3. What this lane deliberately did NOT register

- Any revival of a killed family. B-16 and B-20 are findings about *arguments and scope
  statements*, not proposals to re-run keytexts or walks.
- The 183-vs-210 analysis-script count disagreement (`PICKUP-HERE.md:10` vs `README.md:61`) and
  similar cosmetic drift — real, trivial, folded into B-18.
- The AN-END passive-monitoring residual — already correctly scoped as monitoring, not a lead
  (`DEAD_ENDS.md:295`), folded into B-07.
- `ELIMINATION-LEDGER.md:572`'s "doublet deficit as a forward distributional constraint" —
  discharged by iter-9's forward simulation (`:588`) and independently foreclosed as a decode
  constraint by R3-H1/H2. Not open.
