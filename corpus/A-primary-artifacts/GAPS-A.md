# GAPS-A.md — Lane A: what is still not here, and what is behind it

Compiled 2026-08-20 by Lane A (primary artifacts). Companion to `REPORT-A.md` and
`CONFLICTS-A.md`. Scoped to `corpus/GAPS.md` **G-01** (primary puzzle artifacts) and
**G-09** (signature timestamps); G-02 is closed, see `REPORT-A.md` §1.

**Rule inherited from `corpus/GAPS.md`:** a gap is listed only if its absence was *verified*,
and it is stated specifically enough that someone else could act on it. "We need better
images" is not a gap. "The 2012 countdown page has zero Wayback captures before
2013-05-17, and that one is a 404" is.

Each entry says what is missing, **what was actually tried**, and what would close it.

---

## A-01 — The bytes 4chan served on 2012-01-04 ★★★★★

**Missing:** the original image file as delivered by 4chan, and the thread around it.

**Held instead:** two later copies of the same image, disagreeing with each other —
see `CONFLICTS-A.md` C-02. The 29,279-byte community copy carries the
`TIBERIVS CLAVDIVS CAESAR` payload after EOI; the 27,517-byte imgur/Wayback copy does not.
Neither has a chain of custody back to 4chan.

**Tried:**

| route | result |
|---|---|
| `archive.4plebs.org` | **Blocked by robots.txt.** Its `robots.txt` carries `User-agent: ClaudeBot / Disallow: /`. Not fetched. Logged, not circumvented. |
| `archived.moe` | **Blocked by robots.txt**, same `ClaudeBot / Disallow: /` directive. Not fetched. |
| `desuarchive.org` | Permitted by robots.txt and fetched. Its board list is `a aco an c cgl co d desu fit g his int k m meta mlp mu q qa r9k tg vr wsg` — **23 boards, and neither `/b/` nor `/x/` is among them.** Nothing to search. Index saved at `_logs/desuarchive_index.html`. |
| Wayback, `i.imgur.com/1CcV1.jpg` | 4 successful captures 2013-12-29 → 2024-02-05, **all one digest**. That is the imgur re-encode, not the 4chan bytes. |

**Why this is probably permanent:** no public FoolFuuka-family archive has ever covered
`/b/`, and the two large archives that might hold adjacent material both refuse this agent
class at robots level. A human operator, or an operator with a different agreed user-agent,
is not blocked by the same rule.

**What would close it:** (a) a `/b/` or `/x/` dump from January 2012 held privately;
(b) a solver's own 2012-era copy with a plausible chain of custody; (c) an outguess run
against the two copies we do hold, which at least tells us which one still carries a
recoverable payload — see C-06 and A-07.

---

## A-02 — `845145127.com` in its 2012 state ★★★★★

**Missing:** any capture of the countdown page as it stood in January 2012.

**Verified absent, not assumed.** The Wayback CDX index for `845145127.com`
(`_logs/cdx_845145127.com.txt`, 200 rows) begins at:

```
20130517065023 http://845145127.com text/html 404 …
```

**There is no capture from 2012 at all**, and the earliest capture there is — May 2013 —
is a 404. The first HTTP 200 is `20150801045502`, by which point the domain's content is
from a different era of the puzzle.

**Held instead:** third-party saves of the page, `cijhho123/2012/websites/the GPS
coordinates website/845145127.html` plus its `845145127_files/` directory, and the same
save under `krisyotam/puzzles/2012/websites/`. These are browser "Save page as" captures of
unknown date, not archival records — the HTML has been rewritten by the saving browser.

**What would close it:** a WARC from a non-IA crawler; a hosting-provider snapshot; or a
contemporaneous screenshot with verifiable metadata. Note that even a perfect capture of the
page would not recover the countdown's live state.

---

## A-03 — 8 of the 14 physical poster photographs ★★★★☆

**Held:** **6 distinct 2012 poster photographs** (verified distinct by sha256, deduplicated
across two mirrors):

| bytes | sha256 (first 16) | held as |
|---|---|---|
| 35,778 | `9582e3c02468fd5e` | Paris |
| 11,458 | `fc51d1380c7176cc` | Seoul (small) |
| 113,529 | `c24f7a129dc36051` | US |
| 19,592 | `89d1237547bcd65f` | Seoul |
| 82,001 | `1fee82c0ba65b2ac` | telegraph pole |
| 482,985 | `bac6a0807f1f9b67` | `cAuUz.jpg` |

Plus **5 distinct 2013 poster images** under `cijhho123/2013/additional images/Posters/`.

**Missing:** roughly eight of the fourteen reported 2012 poster locations have no photograph
here at all. Which eight cannot be stated with confidence, because Lane A holds no
authoritative list of the fourteen locations tied to specific images — only the coordinate
list inside the signed `cicada.jpg` payload, which gives locations, not photographs.

**What would close it:** the coordinate list in `cijhho123/2012/additional
docs/outguss/cicada.jpg.out` is a signed primary source and enumerates the sites. Matching
each held photograph to a coordinate, then enumerating the unmatched coordinates, would turn
"roughly eight" into a specific list. That is an hour of work and was not done this session.

---

## A-04 — QR codes as data, rather than as pixels inside a photograph ★★★☆☆

**Held:** poster photographs that contain QR codes.

**Missing:** the decoded QR payloads as an independent record, and any capture of what those
QR codes resolved to in 2012.

**Tried:** nothing. No QR decoder is installed on this machine (`zbar` absent; Pillow 12.1.1
is present but does not decode QR).

**What would close it:** `pyzbar`/`opencv` against the six held poster photographs, cross-
checked against the URLs quoted in write-ups. Cheap, and it converts an image-only holding
into text that can be searched and compared. Recommended as the first thing the next lane
does with these files.

---

## A-05 — The 2013, 2014 and 2016 entry images ★★★☆☆

**Status: largely closed this session.**

The `cijhho123` collection was interrupted mid-pull by the outage; 198 of its 447 files were
absent. All 198 were refetched (`_logs/batch_cijhho_resume.tsv`, log
`_logs/batch_cijhho_resume.log`) and the collection now stands at **447/447, 191.7 MB**,
recovering the whole of the previously-empty `2016/`, `2017/`, `2014/additional images/` and
`2014/additional docs/` trees.

**Confirmed held for 2013:** `cijhho123/2013/additional images/1357366592898.jpg` is the
2013 entry image — **visually confirmed**, it reads *"Hello again. Our search for intelligent
individuals now continues. The first clue is hidden within this image."* Its filename is a
4chan-style epoch-millisecond stamp (1357366592898 = 2013-01-05T05:36:32Z). A second image,
`1357373692810.jpg`, sits beside it. Neither has yet been **cross-hashed against a second
independent holding**, which is what turned `1CcV1.jpg` into `CONFLICTS-A.md` C-02 — so the
same trap is still open here.

**Confirmed held for 2016:** `cijhho123/2016/2016/additional images/4gq25.jpg` is the
oak-tree-with-runes image — **visually confirmed**, faint tree behind the text *"The path
lies empty; epiphany seeks the devoted … Beware false paths. Verify OpenPGP 7A35090F."*
Also not yet cross-hashed against a second holding.

**Still open:** the **2014 entry image** has not been identified by eye in the recovered
trees. `cijhho123/2014/additional images/` holds 57 files, none of which has been visually
checked against the 2014 opening message. And none of the 2013/2014/2016 entry images has a
second independent holding on disk, so none of them has had the check that produced
`CONFLICTS-A.md` C-02.

**What would close it:** (a) open the 2014 image set and identify the entry image by eye,
the way 2013 and 2016 were identified here; (b) re-run the cross-mirror hash comparison used
for the 2012 chain (`REPORT-A.md` §4) over all three entry images, which needs at least one
more mirror pulled (A-08).

---

## A-06 — Fandom's original image bytes for 424 JPEGs ★★★★☆

**Missing:** the byte-exact originals of the wiki images whose delivered SHA-1 does not match
the wiki's own declared SHA-1.

**Measured, not estimated:** the pull finished this session at **829 of 829 files, 0
failures, 345 MB**. Of those, 343 match the wiki's declared SHA-1 and **486 do not**. Of the
486 mismatches, **424 are JPEGs** and **288 are short by exactly 18 bytes**. Full per-file
evidence in `_logs/fandom_manifest.json`.

Given `CONFLICTS-A.md` C-02 — where 61 trailing bytes were the whole first puzzle step — a
constant 18-byte deficit concentrated in JPEGs is not a cosmetic problem.

**Tried:** `?format=original`, which is required (without it Fandom returns a WebP re-encode
at ~3% of original size, HTTP 200, no error). It is necessary but not sufficient.

**What would close it:** the pre-Fandom `uncovering-cicada.wikia.com` originals via Wayback
(a CDX walk for that host already exists at `_logs/cdx_uncovering-cicada.wikia.com.txt` and
has not been mined for image URLs), or a Fandom image export that bypasses the delivery
pipeline.

---

## A-07 — No steganography toolchain, so the payload question cannot be settled here ★★★☆☆

**Missing:** `outguess`, `steghide`, `zsteg`, `binwalk`. None is installed and this lane did
not install any.

**Consequence:** three separate questions in this corpus are all blocked on the same thing —
which copy of `1CcV1.jpg` carries a recoverable payload (C-02), whether cijhho's
`.out`-to-image mapping is right (C-06), and whether any of the 91 short JPEGs (A-06) lost
something embedded rather than something appended.

**What would close it:** Lane G, with an outguess build, against files this lane now holds on
disk. This is the highest-value handoff Lane A produces: the artifacts are here, the
instrument is not.

---

## A-08 — Mirrors identified but not yet collected ★★★☆☆

Enumerated from their GitHub trees (`_logs/tree_*.json`), sizes from the GitHub API:

| repo | size | status |
|---|---|---|
| `krisyotam/cicada3301` | 529 MB upstream | 34 MB collected; the rest untouched |
| `BHQST/3301` | ~100 MB | tree fetched, 108 entries, nothing pulled |
| `0x676f64/Cicada-3301` | ~54 MB | tree fetched, 213 entries, nothing pulled |
| `scream314/cicada3301` | — | tree fetched, 445 entries, nothing pulled |

These are ranked below the items above because they are *mirrors*: their value is
cross-checking hashes of things already held, which is exactly the method that produced C-02.
That makes them cheap corroboration rather than new material — but C-02 shows the method is
worth running.

---

## A-09 — The 315 third-party certifications on the public key ★★★★☆

**Not missing — held and unmined.** `pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc`
carries **315 signature packets**; the older `ibotpeaches` snapshot carries **313**, and the
two sets are not nested (see `CONFLICTS-A.md` C-03).

Every packet names a certifying key ID and a creation time. That is a signed social graph
around the Cicada key with its own timeline, and nothing in this repository has ever looked at
it. It is listed here because an unmined dataset in hand is a gap in the analysis, not in the
collection.

**What would close it:** extract `(certifying key id, creation timestamp)` for all 315 into a
JSON alongside `SIGNATURE-TIMELINE.json`, then ask which certifications cluster in time with
the message timestamps.

---

## A-10 — G-09 is closed for messages, open for everything else ★★☆☆☆

`SIGNATURE-TIMELINE.json` now holds every **message** signature timestamp: 139 rows,
**56 distinct signatures**, 2012-01-05T03:46:03Z → 2017-04-04T23:23:28Z.

Not in it, and needed before any timing argument is sound:

- the 315 key certification timestamps (A-09);
- file-level timestamps from the artifacts themselves — JPEG EXIF, PNG `tIME`, ID3, ZIP
  entry times — none of which has been extracted;
- onion-service and web-server dates, which are gone with the services.

A timing analysis built on 56 message signatures alone is an analysis of *when 3301 chose to
run `gpg --clearsign`*, which is a narrower claim than it will be tempting to make.

---

## Ranked list for whoever picks this up

| rank | item | why first |
|---|---|---|
| 1 | **A-07** — get an outguess build in front of the files already on disk | unblocks C-02, C-06 and A-06 at once; artifacts are already here |
| 2 | **A-04** — decode the poster QR codes | one afternoon, converts pixels into searchable text |
| 3 | **A-09** — mine the 315 key certifications | a complete unmined dataset already in hand |
| 4 | **A-05** — finish and hash-verify the 2013/2014/2016 entry images | the pull is already running; only the verification is owed |
| 5 | **A-06** — chase the pre-Fandom wikia originals through Wayback | the CDX walk already exists, unmined |
| 6 | **A-03** — match poster photos to the signed coordinate list | turns "roughly eight missing" into a specific list |
| 7 | **A-08** — pull the remaining mirrors for cross-hashing | cheap corroboration; C-02 proves the method earns its keep |
| — | **A-01, A-02** | recorded as probably-permanent; do not spend time here without a new source |
