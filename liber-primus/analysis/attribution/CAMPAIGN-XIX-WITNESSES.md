# Campaign XIX — Insider-Witness Research: Wanner & Eriksson (2026-07-27)

_Deep-research harness: 100 agents, 5 search angles, 18 sources fetched, 88 claims
extracted, top 25 adversarially verified (3-vote panels): 18 confirmed, 7 killed.
Public-record only (interviews, articles, talks, the witnesses' own writings)._

## The question

We have proven (Campaigns IV–XVIII) that LP2's key is external by construction. The two
people who got closest to the inside of Cicada in 2012 are Marcus Wanner (entered the
private winners' onion forum, worked on CAKES) and Joel Eriksson ("clevcode", solved the
final public stage). Do their public statements point at WHERE the key might live?

## The one-paragraph verdict

**Neither witness ever saw Liber Primus key material, and the one true insider space —
the winners' private onion forum — died roughly a year before the Liber Primus existed.**
Wanner's first-person accounts (Nox Populi interview, Rolling Stone 2015) establish the
entire insider surface (minimal onion forum + chat + 3301-hosted CAKES wiki + git + PGP
email, ~20 winners), that the only directive was to build "technological freedom"
software, that no puzzle material or keys were ever distributed there, and that the site
vanished un-archived in ~March 2013 — mid-2013-puzzle, before the LP's 2014 release.
Eriksson, by his own repeated testimony, **missed the registration window entirely and
never entered the insider track** ("my sleep-wake cycle resulted in me missing that
window"); his value is corroborative hearsay plus a live contact channel. The 2012 forum
is therefore **eliminated as a key location by timeline**, and the surviving leads point
elsewhere: Cicada's per-person RSA-encrypted email channel, whatever individual winners
privately retained (Wanner kept the CAKES git repo), and the never-found SHA-512 "AN END"
page from solved page 56.

## Confirmed findings (verified verbatim vs. lore)

1. **The insider surface, bounded** (high, 3-0/3-0/2-1): onion thread-forum ("like a
   text-post-only Reddit" — Wanner verbatim) + later chat + 3301-provisioned CAKES wiki +
   git + PGP email; ~20 winners + a few 3301 representatives; credentials via PGP-signed
   anonymous email from Feb 28, 2012. This inventory bounds what ANY insider could have
   seen.
2. **NEGATIVE KEY FINDING** (high, 3-0): full-transcript check of Wanner's account finds
   zero mentions of Liber Primus / AN END / pages / keys. 3301 explicitly withheld prior
   material for opsec ("we weren't given any ideas or examples of previous projects for
   operational security reasons"). Timeline seals it: forum gone before LP release.
3. **Brood b.0h / CAKES** (high): the only concrete insider work product — a
   dead-man's-switch key-escrow system for whistleblowers. Winners were networked, never
   inducted. (Noted irony: the insiders' own project was itself a timed key-release
   system.)
4. **The forum vanished un-archived** (high, 3-0×3): dwindled to Wanner + Sage ("We've
   been laid off"), then gone without warning; no archive or leak has surfaced 2015–2026.
   The only recoverable insider artifact is **Wanner's retained CAKES git repo** (git is
   distributed — his copy persists regardless of hosting), plus any wiki snapshots
   individual winners kept.
5. **Eriksson was never inside** (high, 3-0×3, his own primary sources): solved the final
   public stage, missed the first-come registration window (flooded by ~50 group-solvers).
   Zero firsthand insider knowledge. BUT: his blog notes he later received messages from
   people **claiming** to represent 3301 (unverified) — a legitimate outreach question.
6. **Distribution was per-person email** (high, 3-0×2): early onion arrivals submitted
   emails, each got a personal number and a DIFFERENT RSA-encrypted message at
   sq6wmgv2zcsrix6t.onion/NUMBER. If key material was ever distributed, it could exist in
   fragmentary individualized form across recipients — no single canonical copy.
7. **AN END core confirmed** (medium, 2-1): page 56 directs pilgrims to a deep-web page
   identified only by a SHA-512 hash; never publicly found. (Conveying source — Malicious
   Life — is sloppy on other LP facts; only this core survived corroboration.)
8. **Archive lead** (high, 3-0): upstream krisyotam/cicada3301's `papers/` dir (134
   files, verified real PDF captures: VT Magazine Wanner profile, ClevCode writeup, WNYC
   Wanner interview, Rolling Stone 2015) — the primary witness record, surviving link rot
   (The Face 404s already). **NOT present in our local clone — mirror it.**

## Ranked actionable leads

1. **Eriksson outreach — viable TODAY**: `je at clevcode dot org` (verified on
   clevcode.org, site active 2026; also @OwariDa / LinkedIn /in/owarida). Don't ask for
   the key (he can't have it); ask: (a) the messages he received from self-claimed 3301
   representatives — when, what, any that could postdate 2013 and touch the LP era;
   (b) provenance of his "small chat group over Tor" hearsay (who told him, when — is it
   independent of Rolling Stone?).
2. **Locate Wanner's current public channel** — no 2026 channel survived verification, so
   locating one (professional profile, GitHub, talks) is itself the first task. Then three
   narrow questions: does the CAKES git repo still exist; did the 3301-hosted wiki content
   travel with it; did any brood member (Sage, Tekk, or the ~18 others) snapshot the
   forum.
3. **AN END hash-hunt in archived onion corpora**: has anyone systematically hashed
   candidate pages from 2012–2014 Tor crawls / academic snapshots / onion-index archives
   against the page-56 SHA-512? This is the prime external-key candidate and it is a
   finite, checkable corpus problem.
4. **Deprioritize the 2012 private forum** as a key source — the verified timeline rules
   it out. (This is a genuine narrowing: it removes a whole romantic hypothesis from the
   board.)
5. **Mirror `papers/` from upstream** into the local rig as the canonical witness-document
   store.

## Caveats (honest limits)

- Nearly everything about the forum rests on **Wanner alone**, recollected years later;
  Rolling Stone corroboration is partly circular (sourced from Wanner/Tekk).
- The negative findings are arguments from silence — they prove what witnesses SAID, not
  that no winner kept anything.
- ~20-winner count is Wanner/Tekk's estimate, not an independent tally.
- 7 plausible-sounding claims were REFUTED 0-3 in verification (e.g., "the LP was
  distributed via the 2014 winner cohort", "the repo's wiki/IRC archive would contain
  witness statements") — recorded in the workflow output; do not reuse them.

## Relation to prior campaigns

Campaign VIII profiled Eriksson as an authorship *suspect* (cleared: solver, not author).
This campaign re-examined both men as *witnesses* to key distribution — a different lens.
Its net effect on the standing verdict: **strengthens** the external-key thesis (the only
insider space is timeline-eliminated), and converts "talk to the insiders" from a vague
hope into two concrete, scoped outreach actions plus one finite archive-search program.
