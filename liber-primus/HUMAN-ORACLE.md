# HUMAN-ORACLE — what happens when something crosses the bar

_Written 2026-10-30 (R36 audit, apply-now item). Binding companion to `ARMADA-DOCTRINE.md` section 4 item 9._

The auto-certification seal is below bar (`SEAL_PASS=false`: R21-L1, R35-I3, R36-I3). So no script in
this repo may declare a solve. Any survivor that clears a pre-registered bar is **flagged-for-oracle**:
a human reads it. This file says exactly what the crosser hands over, who reads it, and what "pass" means.
Until a human passes it, the ledger status may NOT move to `positive`; it stays `open` / `partially-run`
with a `flagged-for-oracle` note. Nothing here changes any bar or any measured result.

## 1. The bundle a crosser must produce

Put it in `analysis/<round>/<lane>/ORACLE-<id>/` (the existing `analysis/round27/ORACLE-<seed>.md` files are the
older, informal form of this) containing all of:

1. **Provenance of the key**: the seed / key / generator and its exact parameters (family, ABI, init, skip or
   rejection rule), the **relation** it was scored under (`rigid` is never acceptable; `keyskip1`, `pair` /
   `skip_by_two`, `exact`, ...), and the **offset / page / sign** where relevant. Enough to regenerate the
   full 12,956-symbol keystream with one command (`reproduce:`).
2. **Decoded text for at least two independent pages** (both the rune-index decode and the transliteration),
   full length, not an excerpt. Pages must not be adjacent copies of one another and should include one the
   key was NOT selected on (held-out clause).
3. **The three verifier outputs**: the outputs of the three refute-by-default checks the lane pre-registered
   (the `hitfn20` three clauses: panel-max bar at the stated N, rune-index recovery >= 0.90, held-out 3/4
   reproduction), pasted verbatim with the commands used. Add `python verify_solution.py --keystream ...` output
   as supporting evidence only: its English-only -5.5 band can FAIL a true non-English or `skip_by_two` solve
   (L7-A) and cannot overrule a human read.
4. **The panel argmax trace**: per-register z-scores for the decoded pages, the argmax register, the panel sha,
   the bar and N used, and the observed-null max for that decoder (so a reader can see how far over the bar it is).
5. **Controls**: the lane's planted-control recovery, the language-agnostic row (IoC, mds, pmax_ne, zl) from the
   persisted SWEEPROW store, and the exact commit hash of the code that produced it.
6. **Stop-and-alert**: the lane STOPS, writes the bundle, and does not run further sweeps over the same space
   until the oracle answers.

## 2. Who adjudicates, and the channel

- **Adjudicator: the repo owner** (Dukotah Hutcheon), or a person the owner names in writing in the issue.
- **Channel: the GitHub issue tracker of this repository.** Open an issue titled `ORACLE: <lane> <id>`, attach or
  link the bundle, and apply the label `oracle`. A coordinator who cannot open an issue leaves the bundle in
  place and writes `ORACLE-PENDING.md` in the lane folder; the next overseer run opens the issue.
- External corroboration (the CicadaSolvers community) is welcome *after* the owner's read, not instead of it.
  The community's acceptance test remains a PGP-signed claim (key 7A35090F); this repo's passing a bundle
  is a reproduction gate, not a claim to be the puzzle's authors.

## 3. What "pass" means

A **human reads the plaintext of two independent pages as language** (any register in the panel, including
non-English ones) and judges that it is connected prose, not word-salad that merely scores. Both pages must be
readable without the reader being told what to expect. Only then:

1. The adjudicator records `PASS` (or `NOISE-CROSSER`, with the reason) in the bundle and the issue.
2. The coordinator may move the ledger row to `positive` and update `README.md`, `PICKUP-HERE.md`,
   `ELIMINATION-LEDGER.md` and `analysis/README.md` (CLAUDE.md "keep the navigation docs true").
3. The key is re-run from a clean checkout over all 55 pages before any public statement.

`NOISE-CROSSER` is the expected outcome: all three Round 27 S1 crossers were adjudicated this way
(`analysis/round27/ORACLE-*.md`). Record it, keep the bundle, and file the row with its coverage and `not_covered`.
