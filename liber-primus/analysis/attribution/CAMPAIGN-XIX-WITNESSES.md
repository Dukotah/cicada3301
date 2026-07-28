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
2. **Wanner outreach — LOCATED (2026-07-27, by Duke)**: LinkedIn
   `/in/marcus-wanner-a03133379`, now running a biotech company. Identity consistent with
   the documented trajectory (VT Magazine: he worked at the Virginia Bioinformatics
   Institute as an undergrad — bioinformatics → biotech founder is a straight line);
   LinkedIn blocks automated verification (HTTP 999), so final confirmation happens on
   contact. Three narrow questions: does the CAKES git repo still exist; did the
   3301-hosted wiki content travel with it; did any brood member (Sage, Tekk, or the ~18
   others) snapshot the forum.
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

## Roster sweep (2026-07-27, deep-research workflow wf_cf045169-3a3, 104 agents, 21 confirmed / 4 refuted)

Full enumeration of every identifiable Cicada winner/insider across 2012–2014, split by
evidentiary status. **Bottom line: the confirmed insider roster is tiny, real-name-anchored,
and NONE of it contains an LP page, an AN END page, or OTP keying material.** The sweep
also surfaced Wanner's live GitHub and his 2014 key-escrow repo.

### CONFIRMED insiders
| Person | Handle | Round / role | Reachable? | Evidence |
|---|---|---|---|---|
| **Marcus Wanner** | marcusw / @cryptonomaly | 2012 winner, private forum, CAKES lead, self-ID "3301 librarian" | **YES** — GitHub `marcuswanner` (active TODAY, AeroSpace pushed 2026-07-27), `marcus@wanners.net`, IRC oftc.net/marcusw | Rolling Stone/Kushner (reproduces PGP emails, real name), VT Magazine, his own site — triple-sourced, real-name |
| **"Tekk"** | Tekk | 2012 co-solver, same IRC group + private forum, "faded away" | NO — anonymous by choice | Rolling Stone (Kushner interviewed him in person); single-journalist source |
| **"Sage"** | Sage | 2012/2013 insider; sent the March 2013 "We've been laid off" message that killed the forum | NO — went dark | Kushner, via Wanner's first-person account only |

### PUBLIC-STAGE-ONLY (not insiders)
| Person | Handle | Note |
|---|---|---|
| **Joel Eriksson** | owarida | Solved 2012 PUBLIC puzzle solo, MISSED the Tor email window, never entered insider track. Highly reachable (Keybase/GitHub/X owarida, clevcode.org, BlackHat/DefCon/RSA speaker) but holds no forum artifacts by his own account. Note: two claims sourced to his blog about INSIDER-stage entry mechanics were REFUTED 1-2 — treat his account of the insider stage as second-hand. |

### CLAIMED / unverified (treat with caution)
| Persona | Channel | Status |
|---|---|---|
| **"Nox Populi"** | X @NoxPopuli3301, YouTube, DEF CON 26 (2018) talk "Cicada: What we can learn from the puzzles" | Self-claims to be a **2013 winner** — real public presence + real talk, but winner status NOT independently corroborated. Reachable; worth a low-priority contact as a possible 2013-cohort artifact-holder, claim held as unverified. |
| **crashdemons** | (on Wanner's site) | Drew up the "cicada bounty" wager with Wanner; community collaborator, not attested as an insider. |
| Schoenberger et al. | — | Known HOAX lineage; keep firmly on the fabricated-lore side. |

### Top artifact found — `github.com/marcuswanner/futorcap` (MIRRORED)
"Cryptographic Time-delay Engine" — a delay-based **key-escrow** system (Python, 19 commits,
**2014-02-13 → 2014-03-24**), the same escrow primitive as the CAKES project he built inside
the forum. **Mirrored locally** to `papers-archive/futorcap-repo/` (full git history).
Honest read for the key-hunt: it **predates the Liber Primus (May 2, 2014) by ~5–6 weeks**,
never names CAKES/Cicada/LP, and its "key" is a time-released escrow keypair, NOT OTP
material for the runes. It is the closest surviving insider artifact and a good talking
point with Wanner, but it is **not the LP key**. Adjacent repo of mild interest:
`nameless-ircd` (anonymous IRC daemon, Feb 2013 — the forum-death window).

### Site confirmed + archived
`marcus.wanners.net` was unreachable live (ECONNREFUSED) but captured via Wayback to
`papers-archive/marcus-wanners-net-wayback.txt`: confirms the "3301 librarians" self-ID,
the signing-key fingerprint `…7A35090F` (a SIGNING key, not an encryption/OTP key —
relevance to the actual LP key is limited), and durable contact = `marcus@wanners.net` +
GitHub (Twitter @cryptonomaly is now locked/renamed — weak vector).

### What the roster does NOT change
The external-key thesis stands and is **strengthened**: the only confirmed insider space
(2012 forum) is timeline-eliminated, and the fully-enumerated confirmed roster holds zero
LP/AN-END/key material. Open threads worth noting: (1) was there a SEPARATE 2013/2014
winner forum, post-CAKES and closer to the LP, whose membership is publicly identifiable?
The confirmed record only documents the 2012 forum's death. (2) Nox Populi's 2013-winner
claim, if real, would be the first insider on the LP side of the timeline.

## Relation to prior campaigns

Campaign VIII profiled Eriksson as an authorship *suspect* (cleared: solver, not author).
This campaign re-examined both men as *witnesses* to key distribution — a different lens.
Its net effect on the standing verdict: **strengthens** the external-key thesis (the only
insider space is timeline-eliminated), and converts "talk to the insiders" from a vague
hope into two concrete, scoped outreach actions plus one finite archive-search program.

## Outreach log

- 2026-07-27: Duke emailed Wanner (channel from his startup site) and plans one follow-up call to the company number. Questions per lead list. Status: awaiting response.
