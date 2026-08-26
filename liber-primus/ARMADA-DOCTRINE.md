# ARMADA DOCTRINE — how to aim a round so it can actually find something

_Written 2026-08-26, after Round 18. Binding on every round from Round 19 onward._

> **Read this before you write a `CAMPAIGN-PLAN.md`.** It is not a style guide. It is the
> list of mistakes this project has already paid for, written as rules, so that the next
> armada spends its budget somewhere a discovery is physically possible.

---

## 0. The failure this document exists to prevent

Between Round 8 and Round 17 this project ran roughly **10¹⁰ decodes** across seeded PRNGs,
hash-derived keystreams, KDFs, keytexts, public pads and offset ladders. Every one returned
NEGATIVE. Every one was pre-registered, controlled and honestly reported.

**And the information gained was close to zero.** Not because the work was sloppy — it was
unusually rigorous — but because it was aimed at an *unbounded space under a flat prior*,
adjudicated by an instrument nobody had measured the power of. Round 18 then established two
facts that retroactively cost most of those decodes their meaning:

- **L7-A** — every one of those negatives is an **English-only** negative. Handed the *correct
  key*, the beam recovers 100 % of runes for Latin, Old English, German, Welsh and abbreviated
  English, and the quadgram adjudicator then scores the result as noise. Measured power: 0.33
  for Latin, 0.00 for vowel-dropped English (where the correct key ranks *below* a deliberately
  wrong one).
- **L7-B** — every one of them covers a decoder whose transition relation is exact for *one*
  rejection-loop implementation. `skip_by_two` — a one-character variant that reproduces LP2's
  observed doublet rate — is missed at −6.90 / 25.8 % recovery, and raising the beam width and
  skip budget changes the score by **exactly 0.000**.

So: **if the true key had been inside the swept set, the sweep would probably have discarded
it.** That is the failure. Not bad luck, and not a bad hypothesis — a mis-aimed round.

Meanwhile, every genuinely new thing this project has found came from the *opposite* activity:

| finding | came from |
|---|---|
| the derived-key lane is real and never-run (D3) | auditing a **closure** |
| the public-pad branch exists at all (R17) | auditing a **closure** |
| the filter is machine, not hand (R17) | auditing an **assertion** |
| the pipeline is ImageMagick-over-Ghostscript (R18 L1) | auditing an **artifact** |
| every negative is English-only (R18 L7-A) | auditing an **instrument** |
| the beam misses `skip_by_two` (R18 L7-B) | auditing an **instrument** |
| a truncated `_560.00`, a drifted mirror (R12) | auditing an **input** |

**Zero of them came from a new key-space sweep.** The doctrine below is that table, generalised.

---

## 1. The Aiming Test — five questions, answered in writing, before a lane may run

Put the answers in the lane's `PREREG.md`. A lane that cannot answer all five does not run;
it goes back to the drawing board or to the bottom of the queue.

**Q1 — What would a hit look like, and would *this* instrument recognise it?**
Write the recognizer before the search. Plant the thing you are hunting, in the shape you
believe it takes, and prove the pipeline emits it. Not a friendly analogue — the actual shape.
If your instrument cannot recognise your own planted hit, you are not running an experiment,
you are generating a null.

**Q2 — What measured fact raises this family's prior above the flat rate?**
Cite it, with a file path. `round18/L1-toolchain/RESULTS.md` §6 is what this looks like: an
Ubuntu 11.04–12.04 box with GnuPG 1.4.11 promotes Perl 5.14, bash `$RANDOM`, Python 2.7 and
LaTeX LCGs, and demotes .NET to ×0.05. **A lane with no such fact is a completeness ritual.**
Completeness rituals are allowed, but they are labelled as such and they queue last.

**Q3 — Is the space bounded, and by what?**
State the size and whether it is *enumerable*, *samplable*, or *unbounded*. Prefer enumerable.
`$RANDOM` and TeX's `\pgfmathrandom` are enumerable in minutes; "all possible pads" is not a
lane, it is a fog. If the space is unbounded, say what fraction you will cover and be honest
that the null is worth almost nothing.

**Q4 — What are the three conditionals your negative will carry?**
Every negative in this repository is conditional on exactly three things, and all three must
be named in the results or the result is not a result:
1. **the key space** swept (this is the only one the repo used to report),
2. **the decoder's transition model** — which enciphering constructions the beam can represent,
3. **the adjudicator's register** — which plaintext languages/orthographies the scorer can see.

**Q5 — What single observation would make you abandon this lane at 10 % of budget?**
Write the kill condition and the checkpoint. Rounds here have burned full budgets on lanes
that were dead at the first gate.

---

## 2. The seven rules

### R1 — Aim at the instrument before you aim at the space.
No round may open a new key-space sweep until its decoder and adjudicator have a **measured
power envelope for that round's hypothesis class**. Power is measured by planting the correct
key and reading the score — never by reasoning about the design.

### R2 — Value = coverage × power. Report both or report neither.
A sweep of 10⁶ decodes at power 0.3 excludes less than 10⁵ decodes at power 1.0. Publishing a
coverage number without its power is how this repo produced ten rounds of nulls that did not
mean what they said. Every `RESULTS.md` states measured power against the class it claims to
exclude, over **both** the register axis and the construction axis.

### R3 — Persist language-agnostic statistics at sweep time. Non-negotiable.
Alongside the English score, every sweep row stores: **decrypt IoC·N**, **minimum distinct
symbols over a 32-rune window**, the **best non-English LM score** over the register panel, and
a **compressibility** figure. Round 10b required this in 2026-08 and got **0/15 compliance**;
6.2 M + 692 k + 52 k decodes and 1.45 × 10¹⁰ offsets are permanently un-reinterpretable as a
result. Retro-fitting is impossible once the decodes are discarded. This rule is CI-enforced
(`analysis/handoff/validate_ledger.py`).

### R4 — Prior beats volume, and the prior must come from evidence.
10⁴ decodes against an evidence-derived prior beat 10⁷ against a flat one. Evidence means a
measurement on a held artifact — a file header, a signature version, a render parameter, a
page geometry. Lore, vibes and "it feels like something 3301 would do" are not priors.

### R5 — Prefer bounded objects to unbounded spaces.
Ranked by how often it has actually worked here:
1. a **finite, human-checkable object** (the 450 located O/A/AE disagreements; 6 contested
   payload bytes; 47 unread ornament bands),
2. an **enumerable generator space** (`$RANDOM`, a TeX LCG, a 2³¹ seed range),
3. an **instrument or a closure** to audit,
4. a **samplable** space with a stated coverage fraction,
5. an **unbounded** space. This is last for a reason. Do not lead a round with it.

### R6 — Lanes audit each other; at least one lane per round audits *this project*.
Round 17 found two instrument defects because its lanes cross-checked. Round 18's L7 found the
two errors that reaimed everything. Every armada carries a standing **red-team lane** whose
target is the repository's own current claims, and it reports FOUND-ERROR or NO-ERROR-FOUND —
never "confirmed".

### R7 — Bounds, not verdicts.
Never write "exhausted", "closed", "unsolvable" or "the frontier is complete". Write what was
measured, what was **not** covered, and the concrete condition that reopens it. This repository
has published a terminal verdict twice and been wrong twice; both times it foreclosed a lane
that was later run and turned out tractable. When reading, `LEDGER.json`'s `status` is the
least reliable field in it — read `coverage` and `not_covered`.

---

## 3. Budget allocation for a round

Unless a round's plan argues otherwise **in writing**:

| share | goes to |
|---:|---|
| **≈30 %** | instrument — power envelopes, adjudicator panels, null recalibration |
| **≈40 %** | high-prior bounded lanes (Q2 answered with a citation, Q3 answered "enumerable") |
| **≈20 %** | red-team / closure audit (R6) |
| **≈10 %** | completeness rituals and closeout of previous rounds' unfinished lanes |

If a round proposes to spend more than 40 % on new key space, its plan must first show a
measured power envelope covering that space's construction and register classes.

---

## 4. Mechanics (unchanged from Round 18, restated so this file stands alone)

1. **Pre-register before you run.** `<LANE>/PREREG.md` — hypothesis, instrument, positive
   control, null, pass/fail threshold, plus the five Aiming Test answers. Do not edit a
   threshold after seeing a result; append dated addenda with the reason.
2. **A null from an unvalidated instrument is not a negative.** Plant, prove recovery, then
   trust silence. State the control's measured recovery in the results.
3. **Never use a rigid decoder on LP2.** Rigid scores the *correct* key at −6.835; the beam
   recovers it at −4.170. `pytest liber-primus/benchmark/ -k rigid_scores_correct`.
4. **Fixed score bars are invalid at large N.** Use `benchmark/null.py: threshold_for(...)`,
   report it, compare against it — not against −5.5 out of habit.
5. **Score on rune indices, not the transliteration string** (7 of 29 runes are 2 chars).
6. **Do not re-run measured ground.** Query `LEDGER.json` first, and read each entry's
   `coverage` / `not_covered`, not its `status`.
7. **Write files; do not `git commit`.** Lanes share one worktree; the coordinator commits.
8. **Keep the navigation docs true** — `README.md`, `ELIMINATION-LEDGER.md`,
   `analysis/README.md`, `PICKUP-HERE.md`. A result that exists only in its own folder is a
   result nobody will find.

---

## 5. The optimism clause

None of the above is a counsel of despair, and a round that reads this file and concludes
"there is nothing left to do" has misread it.

The honest position is: the pad may well have come from `/dev/urandom`, in which case no
instrument and no compute ever recovers it. That branch is real and it may be the true one.
**But it is not the only branch, and this project has repeatedly discovered that the branch it
called closed was open.** Three times now — the derived-key dictionary, the public-pad branch,
and the entire register axis — a lane the repo believed foreclosed turned out to be live, and
each time the discovery came from looking harder at *what we were doing* rather than at the
cipher.

So be optimistic about **finding the gap inside a closure**, and disciplined about **not
re-running the measured part**. Those are the same skill, and it is the one this project is
actually good at.
