# Launch copy — the instrument-blindness result

Drafts for posting `PAPER.md` off-repo. Roadmap initiative **3.1** (see
[`AI-AUTHORITY-ROADMAP.md`](AI-AUTHORITY-ROADMAP.md)) — answer engines and humans read prose on
reputation-bearing surfaces, never JSON in a GitHub repo.

**Angle:** the methodology finding, not the puzzle. "A null from an unvalidated instrument is
not a negative" travels to ML evals, A/B tests, security scanning and monitoring — so it gets
shared by people who do not care about Cicada 3301, which is the whole point.

**Hard rules for every surface below** (from the roadmap's guiding principles):
- Never claim a solve, never claim an attribution, never drop the "OTP-**class**" qualifier.
- No agent-seeded engagement. All promotion human-authored and disclosed, or it doesn't happen.
- Every number here traces to a reproduce command. If someone asks, give them the file path.

---

## 1. LinkedIn — primary draft

> Posting notes: the first two lines are all that shows before "…see more", so they carry the
> hook alone. Keep the line breaks — they survive the paste; markdown does not, so the `**`
> below is stripped for the real post. Link in the first comment if you want reach, in the post
> if you want attribution. ~1,900 characters.

---

I spent 30 research rounds and roughly 10,000,000,000 decode attempts trying to break the last unsolved Cicada 3301 cipher.

The most valuable thing I found was that my own measuring instrument was blind.

Here's the moment it came apart. I planted a known-good key — the right answer, handed to my own pipeline — and asked the obvious question nobody had asked in months of work:

Would it recognise its own answer if it saw it?

Mostly, no.

The decoder worked fine. It recovered 100% of the symbols against Latin, Old English, German and Welsh test plaintexts. Then the scorer — a language model trained on English — called all four of them noise.

Against vowel-dropped English it was worse than useless. The correct key scored BELOW a deliberately wrong key. An instrument that ranks the right answer beneath a wrong one isn't a weak detector. It's an inverted one.

Measured statistical power at my own published decision threshold:

→ 1.00 for English
→ 0.58 for Old English
→ 0.33 for Latin
→ 0.00 for Welsh
→ 0.00 for vowel-dropped English

Every negative result I had published was an English-only negative. I just hadn't said so.

And I couldn't go back and fix it. A standing rule to save language-agnostic statistics at sweep time had 0 out of 15 compliance, so ten billion decodes are unrecoverable. The verdicts survived. The evidence didn't.

Four things I'd now do on any search or eval pipeline, puzzle or not:

1. Plant a known signal and prove recovery BEFORE you trust silence. One afternoon. Highest-leverage afternoon in the project.

2. Name all three conditionals on every negative: the space you swept, the model your detector can represent, the register your judge can see. Two are invisible by default. Both of mine were wrong.

3. Persist the raw statistic, not the verdict. What you discard at measurement time is unrecoverable at any price.

4. When a bigger budget changes your result by exactly 0.000, stop tuning. That zero is a model error announcing itself.

The cipher is still unsolved. I wrote up what the sweeps actually measured, including the three terminal verdicts I've had to retract, and made all of it reproducible in four commands.

Full paper and repo in the comments.

---

## 2. LinkedIn — short variant

> For a second post, or if the long one underperforms. ~700 characters.

---

Ten billion decode attempts against an unsolved cipher. Every one came back negative.

Then I planted the correct key in my own pipeline to see if it would notice.

It didn't. The decoder recovered 100% of the symbols — and the scorer called them noise. Against one test language the correct key scored below a deliberately wrong one.

Measured power at my own decision threshold: 1.00 for English. 0.00 for Welsh.

Every negative I'd published was an English-only negative. I hadn't said so, because I'd never measured it.

A null from an unvalidated instrument isn't a negative. It's an unknown wearing a negative's clothes.

Plant a signal. Prove recovery. Then trust silence.

---

## 3. X / Twitter — thread

```
1/
I ran ~10,000,000,000 decode attempts at the last unsolved Cicada 3301 cipher across 30 pre-registered rounds.

Every one negative.

The most useful thing I found had nothing to do with the cipher.

2/
I planted the correct key in my own pipeline and asked whether it would recognise its own answer.

Decoder: recovered 100% of symbols against Latin, Old English, German, Welsh.

Scorer: called all four noise.

3/
Against vowel-dropped English the correct key scored BELOW a deliberately wrong key.

Not a weak detector. An inverted one.

Measured power at my own published bar:
English 1.00
Old English 0.58
Latin 0.33
Welsh 0.00
No-vowel English 0.00

4/
So every negative result I'd published was an English-only negative.

I'd never said so, because I'd never measured it.

5/
Worse: a standing rule to persist language-agnostic stats at sweep time had 0/15 compliance.

10^10 decodes can't be re-adjudicated. The verdicts survived. The evidence didn't.

What you discard at measurement time is gone at any price.

6/
Second failure, deeper. My decoder could represent exactly ONE rejection-loop implementation.

A one-character variant of that loop — which independently reproduces the cipher's own doublet rate — hides the correct key at 25.8% recovery.

7/
Raising the beam width and search budget changed that by exactly 0.000.

That zero is the tell. It's a MODEL error, not a search error. No amount of compute touches it.

8/
Generalises past ciphers to any eval or search pipeline:

• Plant a signal, prove recovery, then trust silence
• Name 3 conditionals: space swept, model representable, register visible
• Save the statistic, not the verdict
• Fixed thresholds are invalid at scale

9/
Cipher's still unsolved. Verdict is OTP-class — can't distinguish a true one-time pad from a short-seed keystream.

Paper, ledger of all 172 tested hypotheses, and 4 commands to falsify any of it:

github.com/Dukotah/cicada3301
```

---

## 4. Hacker News

**Title** (≤80 chars, no "Show HN" — this is a write-up, not a launch):

```
Every negative was an English-only negative: 10^10 decodes and a blind instrument
```

Alternates:
```
I ran 10^10 decode attempts at an unsolved cipher. My instrument was blind.
A null from an unvalidated instrument is not a negative
```

**First comment** (post immediately, as the author):

```
Author here. The short version:

I spent 30 pre-registered rounds attacking the unsolved section of the Cicada 3301 Liber
Primus. All negative. Then I planted a known-good key to check whether my own pipeline could
recognise a success, and found it mostly couldn't.

The decoder recovered 100% of symbols against Latin/Old English/German/Welsh plaintexts; the
English-trained quadgram scorer then rated all four as noise. Against vowel-dropped English
the correct key scored below a deliberately wrong one. Measured power at my own published
-5.5 bar: 1.00 English, 0.58 Old English, 0.33 Latin, 0.00 Welsh, 0.00 no-vowel English.

So every negative in the repo was an English-register negative and no entry said so.

The compounding error is that a standing requirement to persist language-agnostic statistics
at sweep time had 0/15 compliance, so ~10^10 decodes can't be re-adjudicated. Only the
summary verdicts survive, and those verdicts came from an instrument with near-zero power
over much of the space they claimed to close.

Separately the decoder's transition relation turned out exact for exactly one rejection-loop
implementation. A one-character variant that independently reproduces the observed doublet
rate hides the correct key at 25.8% recovery, and raising the beam/budget changes it by
exactly 0.000 — the signature of a model error rather than a search error.

Happy to be told I'm still wrong somewhere. The repo is built to be falsified rather than
believed; four commands check the claims rather than the prose, and if any fail the right
move is to distrust all of it:

  python3 liber-primus/tests/validate.py
  python3 liber-primus/verify_solution.py --selftest
  python3 -m pytest liber-primus/benchmark/ -q
  python3 liber-primus/analysis/handoff/validate_ledger.py

The cipher is still unsolved, and I'm explicit in the paper that the project stopped because
it ran out of machine and instrument, not ideas.
```

---

## 5. Reddit (r/cicada, r/codes)

Different audience: they care about the cipher, not the methodology, and they are
(correctly) hostile to self-promotion and to solve claims. Lead with what it means for
*their* work and do not bury the no-solve.

**Title:** `Measured the power of my own LP2 scorer against a planted correct key — every published negative here, including mine, is an English-only negative`

**Body opening:**

```
No solve, and I want that at the top. LP2 0-54 is still unsolved and the verdict is unchanged
(OTP-class: the ciphertext can't distinguish a true external pad from a short-seed-derived
keystream).

What I do have is a measurement that I think affects how everyone here should read a null,
mine included. I planted a known-good key, decoded it correctly, and scored the result across
nine plaintext registers...
```

---

## Where the paper should live

The repo copy (`PAPER.md`) is the source of record. For a citable off-repo URL:

1. **Zenodo** — `.zenodo.json` is already written and DOI-ready. Enable the GitHub–Zenodo
   integration, then the `v2026.10.5-round30-handoff` tag mints a DOI on release. Add the DOI
   to `CITATION.cff` and `PROBLEM.json` afterwards (roadmap H2).
2. **arXiv** — plausible under `cs.CR` or `stat.AP`, but it needs LaTeX and, for a first-time
   submitter, an endorsement. Zenodo first.
3. A blog/Substack copy is fine as long as it links the repo and carries the date.

Post order that makes sense: mint the DOI → LinkedIn (your audience) → HN (hostile review,
which is useful) → Reddit (the people who actually work on this) last, once the paper has
survived being read.
