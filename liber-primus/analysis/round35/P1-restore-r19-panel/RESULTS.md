# R35 / P1 RESULTS (2026-10-30): NO-MATCH, panel not rebuilt (Q5 stop)

| corpus | recorded | fetched | variant |
|---|---|---|---|
| data/kjv.txt | 0f1a83cb.. 4,436,268 | gutenberg.org/files/10/10-0.txt = 0f1a83cb.. 4,436,268 | MATCH, raw (CRLF as served; no trimming) |
| data/keys/mabinogion.txt | 80dc6f0d.. 617,362 | gutenberg.org/files/5160/5160-0.txt = 80dc6f0d.. 617,362 | MATCH, raw |
| data/keys/welsh/welsh_mabinogion.txt | 4b3fd926.. 524,561 | none | NOT FOUND |
| other 8 inputs | per out_build.json | on disk | already match |

The cache/epub pg10/pg5160 URLs (what R32 evidently used) give the 4,455,950 / 617,553 B substitutes. The old `/files/N/N.txt` URLs 404.
Welsh: described as "Welsh Mabinogion, diplomatic edition" (B6); no URL was ever recorded; fetch_sources.py says unrecoverable. Gutenberg has no Welsh text.
Tried six archive.org OCR djvu texts (Rhys-Evans Text of the Mabinogion x3, Edwards x2, Pedeir Keinc); sizes 152k-671k B, none equals 524,561 B or the hash.
Whether numpy or Welsh differs does not matter yet: panel depends on CY, so no byte-exact rebuild is possible. Not built; no per-model hash comparison possible (out_build.json stores no per-model hashes).
Power gate not run (gated on match). No files written outside the lane dir; matched downloads remain in dl_kjv_10-0/ and dl_mab_5160b/ (not placed); substitutes untouched.
Decision for coordinator: S2 stays parked unless the original Welsh file is found (another checkout/backup, e.g. ._round31_stale_backup in the home dir, or an older clone) or a decision is made to accept a CY-substitute panel, which cannot pass the 14a23d36 gate.


## Addendum (Round 35 X1, 2026-10-30)

The sentence "No files written outside the lane dir ... substitutes untouched" was true when written (09:30:29) and is **no longer true**: afterwards `data/kjv.txt` and `data/keys/mabinogion.txt` were replaced with the matched originals (sha 0f1a83cb... / 80dc6f0d...), `handoff/capsule/MANIFEST.json` was refreshed and `data/fetch_sources.py` edited. The Round 32 substitutes (sha 0204adae... / e177d7c2... / welsh 624ffc97...) are preserved only in `backup/`. X1 also found that the fetch_sources.py edit had altered the Welsh SUBSTITUTE recipe (cache/epub -> /files/N/N-0.txt, ~20 KB different bytes) and that the script had no fetch for KJV/Mabinogion; both were fixed (Welsh URL form restored; `ensure_r19_corpora()` / `--r19` added, sha-verified). The Welsh CY corpus remains unrecoverable (tried, not found); the panel was not rebuilt. See `round35/X1-redteam/RESULTS.md`.
