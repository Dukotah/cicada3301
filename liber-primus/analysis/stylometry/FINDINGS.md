# Stylometric attribution of Cicada 3301 — FINDINGS

_2026-07-13. Can AI stylometry unmask who wrote Cicada 3301? Short answer: no —
and the *reason* is the interesting part, quantified here for the first time.
Artifacts: `analysis/stylometry/` (`build_corpus.py`, `forensic.py`,
`corpus.json`, `forensic.json`). Reproduce:
`PYTHONUTF8=1 python build_corpus.py && python forensic.py`._

## The question

Cicada 3301 signed everything with military-grade crypto and gave away nothing
about its identity for over a decade. Could the one thing it *couldn't* encrypt —
its own writing voice — betray it? Forensic stylometry has unmasked anonymous
authors before (the Unabomber, the author of *Primary Colors*, JK Rowling's
Galbraith). We pointed the same lens at Cicada.

## The wall, measured

Stylometric authorship attribution has a hard floor: reliable methods (Burrows's
Delta and kin) want on the order of **500–1000 words of connected prose per
document**, across multiple documents. Below that, the feature estimates are
noise and any "match" is a coin flip.

Cicada's entire authentic connected-prose corpus — every PGP-signed message body
it ever published, 2012–2015, stripped of hashes, book-code numbers, and armor:

- **359 words. Total.** Across 8 messages.
- **Largest single message: 62 words.** The rest: 16–54.

That is roughly an **order of magnitude below** the floor — not per document,
but *in aggregate*. There is no suspect to match it against either: no named
candidate has ever surfaced with a writing corpus (confirmed in the prior
attribution sweep). So both halves of an attribution — the questioned text and
the candidate text — are missing or too small. **Attribution is not hard here;
it is impossible, and provably so.**

## Why even the workaround fails

The obvious move is to add the solved Liber Primus prose (the koans, ~547 words)
to fatten the sample. It doesn't help, for a measurable reason: those texts are
**aphoristic**. Their function-word density is **36%** versus **~54%** in the
messages — and function words (the, of, and, to…) are precisely the features
authorship attribution relies on, because they're used unconsciously and are
hard to fake. Aphorisms like "THE PRIMES ARE SACRED. THE TOTIENT FUNCTION IS
SACRED." are almost pure content words. So the koans add length but almost no
*authorship signal*. The usable signal stays ~359 words.

## What the prose does reveal (profiling, which short texts *can* support)

Forensic *profiling* (as opposed to attribution) can work on small samples. What
survives here is thin and, tellingly, impersonal:

- **Spelling: nothing leaked.** Zero US *and* zero UK diagnostic markers
  (color/colour, realize/realise, …). The vocabulary is too small and too
  aphoristic to contain a single one — so even the crudest nationality tell is
  absent.
- **Register: archaic / literary, and fairly consistent.** "Thus," "alas,"
  "shall," "pilgrim," "sacred," "journey" — a formal, quasi-Biblical cadence
  recurring across independent 2012 messages. This is the one stable stylistic
  trait. But a register is a **costume, not a fingerprint**: anyone can adopt an
  archaic voice, and doing so actively *suppresses* the idiosyncratic modern
  tics that would identify a real person.
- **Typographic tics: inconsistent.** A double-space-after-period habit appears
  in some messages (up to 40% of sentence ends in one) but not others (22%
  aggregate). Too sparse to call a signature — but the inconsistency is itself
  mildly interesting (a shared style guide loosely followed, or more than one
  hand — the sample can't decide).

## Verdict

**Cicada 3301 is stylometrically un-attributable, and the anonymity looks
engineered into the prose itself.** An entity this obsessed with operational
security communicated almost exclusively in the exact modes that leave no
linguistic fingerprint: terse instructions, numeric book-codes, quoted mysticism,
and aphorism — never sustained personal prose. The absence of evidence is
*patterned*. They didn't only hide their identity in the cryptography; they hid
it in the writing, by producing as little connected prose as possible and keeping
what little there was impersonal and archaic.

This sharpens rather than contradicts the prior attribution sweep's "stylometry
empty" note: it was empty because the corpus is quantifiably below the floor, and
that appears to be by design.

## Follow-up: could a *small candidate pool* rescue it? (calibration + rejection)

A fair objection: the people who could have built Cicada — cypherpunks with the
exact stack (crypto + stego + number theory + esoterica + opsec) active c.2012 —
are a *small, enumerable* pool (~dozens), and closed-set attribution needs far
less text than open-set. We tested this properly instead of assuming.

- **Raw power at 359 words is real.** Burrows's Delta, leave-one-work-out on
  known authors (Carroll, Blake) vs a 9-author pool (chance 11%): 76% correct at
  359 words, collapsing only below ~200w (`calibration_power.py`). So length is
  *not* the fundamental blocker for a small pool — the user's intuition was right.
- **But the naming gate fails.** A matcher always returns a nearest name, even
  when the true author is absent. `calibration_reject.py`: at 359w the
  correct-match Delta (median 150.7) and the *forced-wrong* impostor Delta
  (median 157.3) overlap almost entirely — a threshold accepting 80% of true
  matches also accepts **62% of impostors**. You cannot tell "found them" from
  "accused an innocent."
- **Demonstrated live.** Running Cicada's actual 365 words against 8 candidates
  (`cicada_rank.py`), the confident "top match" is **Richard Stallman** — over
  Hughes by **1.44 Delta**, inside a **6.61** noise band, with the top six tied.
  It is naming the wrong person with a straight face. That is the whole point:
  the 76% closed-set accuracy is a *lie for attribution purposes* because it
  assumes the author is already in the lineup. Drop that assumption and confident
  matches are wrong most of the time.

**So: identification is not possible here, but not for the reason I first gave.**
The blocker isn't only sample length — it's that the open-set problem (is the
author even in our pool?) is unsolvable at this length, so any name the method
emits is a lead-shaped artifact, never an identification.

## Honest limits

Profiling on ~359 words is directional, not probative. The register observation
is qualitative. And "looks deliberate" is an inference about intent from a
structural fact (the corpus shape) — defensible, but not provable. What *is*
provable: the numbers above, and therefore the impossibility of a stylometric
attribution.
