# L8 — PAD PROVENANCE — FINDINGS

_Adjudication of the four pre-registered gates in `PREREG.md` against the already-fetched
documents. No cryptanalysis. Refute-by-default. Write-scope: this folder only._

## Verdict (one line)

**CLEAN NEGATIVE.** No attributable primary statement about LP2 key/pad material exists in
the fetched public record. The Schoenberger material is a primary document about *what it
describes* (defamation), but it **FAILS gate (c) ON-TOPIC** — it says nothing about key or
pad existence, form, custody, or delivery — and its author fails gate (b) PRIMARY STANDING
on the pad question. This upgrades the repo's `unpublished-by-design` verdict from "inference
from author intent" to "inference from author intent PLUS a control-validated search of the
public record that found no contrary statement," and no more.

## Documents fetched and adjudicated

| Doc | What it is | On-topic hits |
|---|---|---|
| `schoenberger_complaint.pdf/.txt` | MI Court of Claims verified complaint, Schoenberger+Cicada 3301 Metaverse LLC v. MSU Trustees (Case 25-000045-MM) — First-Amendment / defamation over MSU journalism | 182,510 chars; `cipher`=1 (marketing prose), `puzzle`=13, `defam`=66; **`liber primus`=0, `key`=0, `pad`=0, `one-time pad`=0, `gematria`=0, `rune`=0, `7A35090F`=0, `2014`=0** |
| `mied388516_1.0.txt` | ED Michigan federal complaint (2:25-cv-12937), Schoenberger v. Derrick & Davis — defamation | 51,717 chars; `puzzle`=1, `defam`=41; 0 pad/key/LP terms |
| `mied388516_19.0.txt` | Federal amended complaint / brief | 30,267 chars; `puzzle`=1, `2012`=1 (a case citation *Yoost v Caspari, 2012*), `defam`=11; 0 pad/key/LP terms |
| `mied388516_17.1.txt` | 1-page exhibit cover (PageID.132) | no substantive content |
| `mi_case_26-000013.html` | MI docket page | docket metadata only |
| `cl_cicada_search.json` | CourtListener "cicada" search | count=8: Schoenberger v. Derrick + Sweigert/Goodman defamation + unrelated crypto-fraud cases (Li v Doe, Cohn v Popescu, etc.) |
| `cl_derrick.json` | CourtListener "Derrick" search | count=1: Schoenberger v. Derrick (same lineage) |
| `cl_recapdocs.json` | RECAP docs API | `{"detail":"Authentication credentials were not provided."}` — walled, no content |

## Gate-by-gate result (the four clauses)

**(a) ATTRIBUTABLE — PASS for the filings.** They are filed court documents that are the
record itself (verified complaint, docket, federal ECF filings). Not anonymous forum posts
or AI summaries. Gate (a) is satisfied by the documents *as documents*.

**(b) PRIMARY STANDING — FAILS on the pad question.** Standing project finding holds:
Schoenberger is a post-2014 brand claimant with **zero tie to the 2012 external key
7A35090F**, and the filings are on the brand/defamation dispute. The pre-registered
carve-out (a Schoenberger court filing *is* primary about custody/delivery **if it describes
key handling**) is **not triggered**, because — see (c) — no filing describes any key
handling, custody, or delivery. So there is no clause-(b) primary statement about the pad to
grade. (String `7A35090F` appears **0 times** across all fetched filings.)

**(c) ON-TOPIC — FAILS. This is the dispositive gate.** The hit condition requires a
statement specifically about **LP2 key or pad material** — that it exists, its form, how or
to whom delivered, or that it was withheld. Across all three substantive filings:
- `liber primus` = **0**, `one-time pad` = **0**, `pad` = **0**, `key` = **0**,
  `gematria` = **0**, `rune`/`runic` = **0**, `encrypt`/`decrypt` = **0**, `7A35090F` = **0**.
- The single `cipher` occurrence is generic brand prose:
  *"The ethos of Cicada 3301 has used ciphers, steganography, riddles and illusions to take
  the pilgrim on a journey..."* — a characterization of the ARG, **not** a statement about
  LP2 key/pad material. Per PREREG, statements "about the puzzle in general" explicitly do
  **not** count.
- `puzzle` appears only in marketing/branding recitals ("music, art, poetry and puzzles",
  "2017-2018 puzzle releases"). The lone `2012` is a legal citation, not the puzzle year.

The filings are entirely about a First-Amendment/defamation dispute (MSU journalism;
Derrick/Davis). **Zero content about key or pad material.** Gate (c) fails outright.

**(d) INDEPENDENCE GRADED — single Schoenberger lineage, collapses to one.** Every fetched
court source (MI Court of Claims complaint, ED-Mich federal complaints, both CourtListener
hits that are Cicada-primary) flows through the Schoenberger/Cicada-3301-Metaverse-LLC
party. The remaining CourtListener results (Sweigert v Goodman, Steele v Goodman, and the
unrelated crypto-fraud cases) are not about LP2 pad material. Chains merge -> **one source,
tertiary-to-the-pad-question, chain-of-custody through Schoenberger.**

## Controls

**Positive control (can this pipeline find a known-shape statement?)** — the fetched
CourtListener/court channel is a *litigation* channel; it is the wrong instrument for the
P1/P2/P3 witness statements (Wanner private-forum admission; individualized RSA messages;
Eriksson missed-window), which live in journalism/interview channels not fetched here. Under
the strict PREREG reading (>=20 queries / 8 fetches / P-controls 3/3 from the open web) the
*full* minimum-effort bar spanning all six source classes was interrupted before the window
crashed; what was fetched is the court-records class only. **Caveat honestly recorded:** on
the fetched-court-records slice alone, the CLEAN-NEGATIVE label is fully earned *for that
class* (the class that could have contained the pre-registered Schoenberger carve-out HIT,
and did not). It is **not** a whole-lane CLEAN NEGATIVE across all six classes; the other
five classes are open residue.

**Negative / decoy control (does the channel manufacture sources?)** — D1 ("2014 winners
mailed a printed one-time pad / key booklet") and D2 ("a 3301 message told winners to
destroy the LP key after use") return **0 attributable primary sources** in the fetched
court record: no filing mentions a pad, a booklet, key destruction, winners, or 2014 at all.
**0/2 confirmed — channel is NOT contaminated.** The court-records channel does not
fabricate pad provenance on demand.

## Does the Schoenberger material clear (b) and (c)? — explicit answer

- **Gate (b) PRIMARY STANDING: NO.** Schoenberger has no firsthand standing on the 2012 key
  (post-2014 brand claimant, zero tie to 7A35090F), and the carve-out that would make his
  filing primary-about-custody is not triggered because the filings describe no key handling.
- **Gate (c) ON-TOPIC: NO.** The filings contain zero statements about LP2 key or pad
  material — 0 occurrences of `liber primus`, `key`, `pad`, `one-time pad`, `gematria`,
  `rune`, or `7A35090F`. They are about defamation and brand ownership.

Because (b) and (c) both fail, the Schoenberger material is **not** a HIT, consistent with
the standing strong prior.

## Verdict

**NEGATIVE — no attributable primary statement about LP2 pad material in the fetched
record.** The single load-bearing pair of numbers: across ~264,000 characters of Schoenberger
court filings there are **0 occurrences of `liber primus`, `key`, `pad`, or `7A35090F`**, and
the only `cipher` reference is generic ARG marketing prose ("has used ciphers, steganography,
riddles and illusions"). The decoy controls returned **0/2**, so the channel is not
manufacturing agreement. The Schoenberger material **fails gate (b) and gate (c)** and is
graded as a single tertiary source of the Schoenberger lineage.

Epistemic value, stated as exactly and no more than PREREG allows: for the court-records
source class, the repo's `unpublished-by-design` verdict is upgraded from bare
author-intent inference to author-intent inference PLUS a bounded, decoy-controlled search
of the litigation record that found no contrary statement. The other five source classes
(winner interviews, documentaries + outtakes, 3301 signed messages, community primary
archives, academic literature) remain open residue and were not exhausted in this window.
