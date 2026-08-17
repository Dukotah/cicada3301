# PA-1 — PRE-REGISTRATION (Round 10B): Public Prior-Art Census

Written before searching. **No attack is run in this lane.** Deliverable is a census, not a
cryptanalytic result. Nothing here can break or confirm a cipher.

## Questions (each with a falsifiable answer condition)

**Q1 (enumeration).** What public Liber Primus / Cicada 3301 code and analysis exists that this
repo does not cite? Answer = a list of `owner/repo` + URLs, each checked against a repo-wide grep.

**Q2 (methods).** For each source, what does its *existence* prove was already attempted?

**Q3 (the load-bearing one).** Did the solver community converge on the OTP / "unsolvable by
design" verdict, or is that verdict this repo's own?

## Pass/fail thresholds, fixed in advance

- **Q1 PASS:** >= 10 public repos/sources bearing directly on LP2 cryptanalysis that return
  **zero hits** on a repo-wide case-insensitive grep of their distinctive token. FAIL if < 10.
- **Q3 is decided by primary community sources ONLY**, ranked:
  1. The official CicadaSolvers DEF CON 31 talk (Aug 2023) — the community speaking for itself.
  2. cicadasolvers.com/quickstart — the community's own maintained cryptanalysis briefing.
  3. uncovering-cicada.fandom.com technical pages — the community's own analysis wiki.
  - **Verdict "community converged on OTP"** requires an explicit OTP/information-theoretic
    unsolvability claim in >= 2 of those 3.
  - **Verdict "OTP is this repo's own"** requires **0 of 3** to claim it AND >= 1 of the 3 to
    assert the opposite (solvable / a findable algorithm).
  - Anything in between = **unresolved**, report as such.
- Journalism/blog/SEO-farm sources are **excluded** from the Q3 vote. They paraphrase each other
  and several already paraphrase this repo's own public README. Counting them would be circular.

## Controls

- **Novelty control (false-positive guard).** Before claiming any source is uncited, grep a decoy
  set the repo demonstrably *does* hold: `relikd`, `scream314`, `krisyotam`, `iBotPeaches`,
  `LiberPrimusSolver`, `cicada-solvers`. If the grep does not flag all six, the grep is wrong and
  every novelty claim in this lane is void.
- **Negative control on Q3.** Actively search for the OTP claim using OTP-loaded query terms
  ("one-time pad", "unbreakable", "unsolvable by design"). If the claim exists in community
  primary sources, a query biased *toward* it will surface it. Concluding "not found" after a
  biased-toward-finding search is a much stronger negative than after a neutral one.
- **Extraction control.** The DEF CON 31 PDF has an obfuscated font encoding. Any claim of
  "term absent from the talk" is only valid if the decode is verified readable first (check that
  known plaintext — the 2014 PGP message, the speaker names — comes out clean). An absence
  measured on garbled text is meaningless.

## What this lane cannot establish

"Nobody has tried X" is bounded by what is *published*. The CicadaSolvers Discord (10k+ members)
is the community's real working surface and is **not** publicly archived. Every UNDUG claim below
must therefore be stated as "no public record of X", not "X was never tried", and must name what
would falsify it.
