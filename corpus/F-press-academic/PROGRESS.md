# Lane F — PROGRESS

Started 2026-08-19 UTC. Lane F = press/documentary/podcast/interview + **cipher-space academic literature** (GAPS.md G-08).

## Log
- [t0] Lane dir created. Read corpus/GAPS.md G-08, corpus/INVENTORY.md Lane F, PAPERS-ARCHIVE.md.
- KEY PROVENANCE FINDING: PAPERS-ARCHIVE.md states the 135-file archive is a mirror of
  `github.com/krisyotam/cicada3301` `papers/` (sparse checkout). So provenance is recoverable
  at the *collection* level: upstream repo + path. Per-file upstream URLs to be confirmed via GitHub API.
- [t1] PRESS RE-PROVENANCE **DONE (method: byte-match + footer extraction)**:
  - 134 local files in papers-archive/. **133 are byte-identical (git blob sha1 match) to
    `github.com/krisyotam/cicada3301` `papers/` @ commit 1ccf9583b706 (2026-04-20T08:01:14Z).**
    1 local-only file: `marcus-wanners-net-wayback.txt` (added locally 2026-07-27).
    Mirror-level provenance therefore VERIFIED, not asserted.
  - Deeper: 126 of them are PDFs, and they are browser **print-to-PDF captures** whose
    running header/footer preserves the ORIGINAL article URL and the CAPTURE DATE.
    Extracted with pdftotext: **102/126 yielded both a source URL and a capture date.**
    Capture dates cluster 2020-12-04 .. 2021-03-21 (locale dd.mm.yyyy => German-locale browser).
    This dates a previously undated archive.
- [t2] Building MANIFEST rows for press half.
- [t3] CIPHER-SPACE DISCOVERY sweeps run (metadata harvest before download):
  - arXiv API: 25 queries, results cached.
  - DBLP: 40 queries -> found the canonical running-key literature (Cryptologia 2002/2005/2006 + ACL 2012).
  - OpenAlex: 30 queries (replaced Semantic Scholar, which 429'd on nearly every call and was killed).
  - IACR ePrint: search page fetched.
- [t4] DOWNLOADS begun. `dl.py` writes meta/downloads.json (sha256 + retrieved_utc + source_url per file).
  First 10 stored: ACL-2012 Reddy&Knight running-key, 8 HistoCrypt open-access PDFs (runic cryptography,
  Zodiac-340 unicity distance, Gutenberg+hexagram keytext search, Kryptos K4 cryptodiagnosis,
  ML cipher-type detection, CrypTool2 components, encrypted epigraphy, DL known-plaintext).
  KEY VENUE FINDING: **HistoCrypt** (Linkoping Electronic Conf. Proc., ep.liu.se) is fully open access
  and is the venue of record for computational historical cryptology. Cryptologia is Taylor & Francis
  paywalled -> citations to GAPS-F.md.
- [t5] 14 more stored: Ryabko Vernam-robustness (the single most on-point paper for derived-vs-true-pad),
  Ryabko two-Shannon-ciphers, 2 unicity-distance papers, 3 multiple-testing/peak-detection papers
  (family-wise error over best-of-N score maxima), 5 Smirnov/Carlitz anti-repeat combinatorics papers,
  NIST SP800-22r1a and SP800-90B. Second HistoCrypt batch (9) also stored incl. the Upplandic
  non-lexical rune stones paper (runic ciphers-or-nonsense) and Lost in Transcription.
- [t6] Next: theses (SJSU ScholarWorks / OATD), IACR ePrint, non-English, then press half extension
  (documentaries/podcasts/interviews/attribution claims + PGP 7A35090F signature status).
