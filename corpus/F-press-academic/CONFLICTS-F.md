# Lane F — CONFLICTS

Conflicting or non-reconcilable records found in this lane. Nothing here is resolved; both
sides are recorded.

---

## F-C-01 — Two extractions of the same press archive disagree on how many files yield
provenance

The press half's per-file provenance is recovered by reading the print-to-PDF running
header/footer out of 126 mirrored PDFs.

| run | extractor | PDFs yielding **both** URL and capture date |
|---|---|---|
| pre-outage (`PROGRESS.md` [t1]) | `pdftotext`, implementation not preserved | **102 / 126** |
| this pass (`press_reprov.py` → `meta/press_provenance.json`) | `pdftotext -layout`, first page + last 3,000 chars, URL regex excluding font/schema hosts | **88 / 126** |

**Not reconcilable:** the pre-outage run's output was never written to disk before the
network outage killed the lane, so there is nothing to diff against. The two runs may
differ in how much of the document they scanned, in which URLs they accepted, or in which
date formats they matched.

**Recorded position:** `88/126` is the figure this lane can currently evidence, and
`meta/press_provenance.json` is the artifact that backs it. The `102/126` figure is
retained here as the earlier claim, not as a superseded error — it may well be the better
extraction. Re-running a more permissive extractor would settle it.

Both runs agree on the substantive finding: the capture dates are `dd.mm.yyyy`
(German-locale browser) and cluster in **2021-01 to 2021-03**. This pass measures
**87 of 88** dates as `dd.mm.yyyy`, distributed 2021-01 (19), 2021-02 (51), 2021-03 (17),
with a single 2017-04 outlier that is probably an in-article date rather than a capture
date.

---

## F-C-02 — The press archive's capture horizon conflicts with its use as a current record

The mirrored press archive was captured in a single January–March 2021 browser session
(F-C-01, `BIBLIOGRAPHY.md` half 2). But `PAPERS-ARCHIVE.md` describes it as the on-disk home
for primary documents "so link rot … can't erase them", and notes *The Face already 404s*.

The conflict is a scope one, and it matters: **the archive cannot contain anything published
after March 2021**, and it cannot contain anything that had *already* link-rotted before
January 2021. Any argument of the form "this claim does not appear in the press archive,
therefore it was not made" is unsound for both ends of that window.

Unresolved because closing it requires the press-half extension that was never run
(`GAPS-F.md` F-G-08).

---

## F-C-03 — Cryptologia's runic-cryptography pair is itself a published dispute

Recorded as a conflict because it is one, and because it is directly analogous to this
project's central question.

- O. G. Landsverk. **Cryptography in Runic Inscriptions.** *Cryptologia* 8(4):302–319
  (1984). DOI 10.1080/0161-118491859141
- Ben Johnsen. **Cryptography in Runic Inscriptions: A Remark on the Article "Cryptography
  in Runic Inscriptions" by O. G. Landsverk.** *Cryptologia* 25(2):95–100 (2001).
  DOI 10.1080/0161-110191889833

Johnsen's paper is explicitly a rebuttal. **Neither is held** — both are paywalled
(`GAPS-F.md` F-G-02) — so the substance of the dispute is unknown to this corpus and is
**not** summarised here, because summarising an unread paper would be inventing its content.

Flagged because the shape of the dispute (does a runic sequence encode a cipher, or is the
cipher reading an artifact of the analyst?) is the same shape as the Liber Primus question,
and because the one held open-access paper in this space — Wase, *The Upplandic Non-Lexical
Rune Stones: Ciphers or Nonsense?* — is one side of that same argument.

---

## F-C-04 — 133 of 134 press files verify against upstream; 1 does not exist upstream

Not a contradiction so much as a divergence that must not be silently smoothed over.

- **133 files** are byte-identical (git blob SHA-1 match) to `github.com/krisyotam/cicada3301`
  `papers/` at commit `1ccf9583b706` (2026-04-20T08:01:14Z).
- **1 file is local-only**: `marcus-wanners-net-wayback.txt`, added locally 2026-07-27.

The local-only file therefore has **no upstream provenance at all**, and its own provenance
(who made it, from which Wayback capture, when) is not recorded anywhere this lane could
find. It is named for Marcus Wanner, the confirmed 2012 winner, so it is not a trivial file.

**Unresolved.** It should be re-derived from a named Wayback capture with a recorded
timestamp, or marked as unverifiable.
