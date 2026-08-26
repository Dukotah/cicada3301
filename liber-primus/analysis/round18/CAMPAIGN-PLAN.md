# Round 18 — "THE PAD CAME OUT OF A PROGRAM. FIND THE PROGRAM."

_Opened 2026-08-25. Eight parallel lanes. Pre-registration required before any sweep._

## The thesis this round is built on

Round 17 established, at ≥0.99 power, that **the anti-repeat filter is MACHINE-applied**, not a
human calligrapher's habit (`round17/SYNTHESIS.md` §2). That finding refuted the attribution
anchor in `FINAL-SYNTHESIS.md:73-76` — and then **nothing was built on it**.

It should have changed the whole search. If the filter is machine, then in 2012–2014 a person sat
down and wrote a *program*: a script, in a language, on a platform, with a library, an RNG, a
typesetting toolchain, and an output pipeline that ends in the 400-DPI Ghostscript renders we
hold. Programs leave fingerprints in their artifacts, and every one of those fingerprints is a
**prior** over the derived-key dictionary that Round 13/16 swept blind.

That is the optimistic frame for this round: we are not hunting a mystical pad. We are hunting a
short script written by a human being, and physical evidence of that script's toolchain is
sitting in files this repository already holds.

## The rules (non-negotiable, they are why our negatives mean anything)

1. **Pre-register before you run.** Write `<LANE>/PREREG.md` — hypothesis, instrument, positive
   control, null, pass/fail threshold — and do not edit the threshold after seeing a result.
2. **A null from an unvalidated instrument is not a negative.** Plant a known signal; prove
   recovery; only then trust silence. State the control's measured recovery in the results.
3. **Never use a rigid decoder on LP2.** Rigid scores the *correct* key at −6.835 (noise); the
   skip-aware beam recovers it at −4.170. `pytest liber-primus/benchmark/ -k rigid_scores_correct`.
4. **Fixed score bars are invalid at large N.** Use `benchmark/null.py: threshold_for(n_trials,
   segment_len)`, report it, and compare against it — not against −5.5 out of habit.
5. **Score on rune indices, not the transliteration string** (7 of 29 runes are 2 chars).
6. **Report coverage, not conclusion.** Every lane ends with what it measured, what it did NOT
   cover, and the concrete condition that reopens it. Do not write "exhausted", "closed", or
   "unsolvable". This repo has been wrong in that mood twice, and both times it foreclosed a lane
   that was later run and turned out tractable (D3 2026-08-17; R17 2026-08-20).
7. **Do not re-run measured ground.** Query `liber-primus/LEDGER.json` first; read each entry's
   `coverage`/`not_covered` field, not its `status`. Re-running R16-KDF's 692,064 configs or
   B-04's 6,224,300 decodes is a waste; extending them past their stated `not_covered` is not.
8. **Write files; do not `git commit`.** Eight lanes share one worktree. The coordinator commits.

## Lanes

| id | name | the gap |
|---|---|---|
| L1 | TOOLCHAIN | G-01/B-11 provenance track, proposed and **never executed** — turn file forensics into an RNG/language prior |
| L2 | THE FILTER AS A LEAK | new — the rejection sampler consumes draws and emits constraints; nobody has treated it as information |
| L3 | ORNAMENTS & LAYOUT | A-06 + B-12 — 47 catalogued bands **nobody has ever read**, plus line geometry as a channel |
| L4 | FORCING | C-02 — the acrostic/forcing detector, specified with a hard gate, **no script ever written** |
| L5 | PAYLOAD CLOSURE | A-04 (6 contested bytes, never OCR'd) + E-01 completion (7A35090F moduli never fetched) |
| L6 | OFFSET & MARSAGLIA | B-02 (every sweep assumed key index 0 = rune 0) + the named, unswept Marsaglia CDROM |
| L7 | INSTRUMENT RED-TEAM | the pattern that produced every real finding here — audit the beam's power envelope and the English-only scorer |
| L8 | PROVENANCE OSINT | I-01 mruzuki, I-03 cypherpunks 2011–13, and corpus G-02 (no PGP verification table exists anywhere) |

Each lane writes `round18/<LANE>/PREREG.md` + `RESULTS.md` and appends its entry to a
`round18/LEDGER-ADDITIONS.json` fragment for merge into `liber-primus/LEDGER.json`.
