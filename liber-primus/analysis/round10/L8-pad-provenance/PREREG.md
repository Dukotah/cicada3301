# L8 — PAD PROVENANCE — PRE-REGISTRATION

_Written 2026-08-12, **before any search was run**. No cryptanalysis happens in this lane.
The deliverable is an external-evidence verdict on one sentence in the repo's own terminal
conclusion._

## The claim under test

`ELIMINATION-LEDGER.md` iter-11 states:

> **Key-location = UNPUBLISHED-BY-DESIGN:** author-intent enumeration — the pad's most-consistent
> home is private delivery to vetted 2014 winners … NOT a public page.

That is an **inference from author intent**, explicitly labelled as such (it is derived from
thematic reading of the koans plus the observation that pages 0–54 were onion7's terminal
deliverable). It has never been sourced. `PICKUP-HERE.md` §"What is actually still open" item 1
names the missing evidence exactly:

> **A signed or archival pointer** that a specific text *is* the key — i.e. evidence from outside
> the ciphertext, not another text to try.

## H1 (the hypothesis)

There exists at least one **sourced, attributable primary statement** about the **existence, form,
or delivery** of Liber Primus key/pad material.

## The hit condition — all four clauses required

A candidate counts as a HIT only if it satisfies **(a) AND (b) AND (c) AND (d)**:

- **(a) ATTRIBUTABLE** — to a *named* person, or to a filed/archived document that is the record
  itself (court filing, docket entry, signed message, dated transcript). Anonymous forum posts,
  unattributed wiki prose, SEO content-farm articles and AI-generated summaries are **excluded by
  definition** and do not count even if they say exactly the right thing.
- **(b) PRIMARY STANDING** — the speaker has firsthand standing (winner / insider / recipient /
  3301 itself), or the document is a primary record. A journalist repeating a witness counts only
  as a *carrier* of that witness's primary statement, and is graded to the witness.
- **(c) ON-TOPIC** — the statement is specifically about **LP2 key or pad material** — that it
  exists, what form it takes, how or to whom it was delivered, or that it was withheld. Statements
  about the puzzle in general, about the 2012/2013 chains, or about the *existence of the runic
  book* do **not** count.
- **(d) INDEPENDENCE GRADED** — every source is graded primary/secondary/tertiary **and** for
  independence from the Schoenberger lineage. Re-citing Schoenberger-derived material is not
  corroboration and is scored as one source, not many.
  - **Explicit carve-out, pre-registered:** a **Schoenberger-side court filing or discovery
    document** is a primary document *about what it describes* even though his authorship
    self-claim fails the PGP gate. If a filing describes key handling, custody, or delivery, it
    satisfies (a)(b)(d) and is a HIT regardless of whether his broader claim is true. Its truth
    value is a separate question from its status as a sourced statement.

## Pre-registered thresholds (fixed before running)

| Outcome | Condition |
|---|---|
| **HIT** | ≥ 1 candidate satisfying (a)+(b)+(c)+(d). |
| **CLEAN NEGATIVE** (the useful null) | 0 candidates satisfying (a)–(d), **AND** the minimum-effort bar below is met, **AND** positive controls 3/3 surfaced, **AND** decoy controls 0/2 "confirmed". |
| **VOID** (lane proves nothing) | Positive controls < 2/3 surfaced → the search pipeline is broken and its silence is not evidence. |
| **CONTAMINATED** | ≥ 1 decoy control returns apparently-sourced confirmation → the channel manufactures agreement, and any HIT found in this lane must be discounted to rumor-tier. |

**Minimum-effort bar for a negative to count:** ≥ 20 distinct search queries spanning ≥ 6 source
classes, plus ≥ 8 direct document fetches (not search snippets). Source classes required:
1. named-winner interviews / talks / AMAs / podcasts,
2. court records and dockets (Michigan Court of Claims, PACER-visible federal, any Cicada-named
   filing),
3. documentaries and long-form journalism **and their published source/outtake material**,
4. 3301's own signed messages,
5. community primary archives (CicadaSolvers official, wiki, GitHub org),
6. academic/conference literature.

## Controls (mandatory — a search lane without controls is not a result)

Search lanes fail in two opposite directions: the pipeline can be too weak to find anything
(false negative), or the channel can hallucinate agreement with whatever it is asked (false
positive). Both are controlled.

### Positive control — can this pipeline find a statement that IS known to exist?
Three facts already documented in this repo, of the *same shape* as the target claim (a named
witness describing what Cicada delivered to whom), must be re-surfaced **from the open web by
this lane's own queries**, without consulting the repo's copies:

- **P1** — Wanner: 2012 winners were admitted to a private onion forum and told to build
  "technological freedom" software.
- **P2** — Cicada distributed *individualized* RSA-encrypted messages, one per numbered
  recipient, at a v2 onion address.
- **P3** — Eriksson: solved the final 2012 public stage but missed the registration window.

3/3 required for a negative to count. < 2/3 = VOID.

### Negative / decoy control — does the channel manufacture sources on demand?
Two claims **invented for this lane**, plausible in shape and never asserted by anyone, are
searched with the same query style and effort as the real target:

- **D1** — "the 2014 winners were mailed a printed one-time pad / key booklet."
- **D2** — "a 3301 message instructed winners to destroy the Liber Primus key after use."

Expected: 0/2 return an attributable primary source. If either does, the channel is
CONTAMINATED and this lane's own positive findings (if any) drop to rumor-tier.

### Independence ledger
Every source that survives to the candidate list is written into a table with: source, tier
(primary/secondary/tertiary), witness it grades to, and whether its chain of custody passes
through Schoenberger. Sources whose chains merge are collapsed to one.

## What a clean negative buys (stated in advance so it cannot be inflated afterwards)

A clean negative does **not** prove no key material exists, and does **not** prove it was never
delivered. It upgrades one specific thing: the repo's `unpublished-by-design` verdict moves from
**inference from author intent** to **inference from author intent PLUS a bounded, pre-registered,
control-validated search of the public record that found no contrary statement**. That is an
epistemic upgrade of the repo's central claim, and it is the entire value of the lane. It must be
reported as exactly that and no more.

## What this lane cannot establish (scope, fixed in advance)

- Private channels are invisible to it: email to winners, the dead 2012 forum, the CicadaSolvers
  Discord (not publicly archived), sealed or paywalled court exhibits.
- Absence of a public statement is compatible with the material existing privately — indeed that
  is the hypothesis being *supported*, which means this lane can only ever weakly confirm and
  strongly refute. It is designed as a falsifier, not a confirmer.
- No cryptanalysis is run and no key is tested. Nothing in this lane can solve or unsolve LP2.
- Non-English-language sources are searched only opportunistically.
