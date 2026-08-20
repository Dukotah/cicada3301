# Lane D — PROGRESS

Started 2026-08-19. Working dir: `corpus/D-archives/`.

## Phase 1 — CDX enumeration (in progress)
- `targets.tsv` — 354 CDX queries built (core domains, imgur/twitter files, 33 onion addrs x 9 tor2web proxy suffixes)
- `cdx/<id>.json` — raw CDX JSON per target
- `logs/cdx.log` — every query, HTTP status, row count

### Early row counts (distinct-digest captures)
| target | rows |
|---|---|
| 845145127.com (domain) | 309 |
| cicada3301.boards.net (domain) | 2104 |
| uncovering-cicada.wikia.com | 3000 (LIMIT HIT) |
| uncovering-cicada.fandom.com | 3000 (LIMIT HIT) |
| opensource.exposed | 196 |
| clevcode.org/cicada-3301/ | 385 |
| reddit.com/r/a2e7j6ic78h0j | 1140 |
| reddit.com/r/cicada | 3000 (LIMIT HIT) |
| pastebin.com/raw/yEiTHhvF | 4 |

## Phase 2 — fetch distinct captures (pending)
## Phase 3 — byte-diff of files across capture dates (pending)
## Phase 4 — other archives (archive.today, archive.org items, 4plebs) (pending)

## RESUMED 2026-08-19/20 UTC after network outage (ENOTFOUND)

- [x] Consolidated `MANIFEST.json` (764 files / 51.8 MB, 341 with provenance).
- [x] **PRIORITY 1 byte-diff across capture dates — RUN AND CLOSED.**
      Census over `TIMELINE.json`: 15,474 URLs / 25,064 captures; 1,597 URLs with >1 HTTP-200
      capture and >1 distinct CDX digest (candidates only).
      Byte level: `bytediff_jobs.json` -> `bytediff_fetch.py` fetched 91 captures over 33
      immutable-resource URLs; Content-Encoding normalised; SHA-256 compared.
      **Result: 28/33 identical, 3 differ (all non-canonical: 2 imgur server-side
      derivatives + parked 845145127.com). Every canonical Cicada image and the April-2017
      PGP paste are byte-stable across capture dates.**
- [x] Two false-positive traps documented: CDX `digest`/`length` unreliable (19 cases);
      gzip transfer framing (1 case, on the highest-value artifact in the lane).
- [x] One real cross-date content change found and recorded unresolved:
      `5fpp2orjc2ejd2g7.onion.link:80/` 2015-09-19 vs 2017-01-09.
- [x] `CONFLICTS-D.md`, `GAPS-D.md`, `REPORT-D.md` written.
- [ ] Phase 2 fetch still ~91% incomplete; Phase 4 (archive.today / Common Crawl / 4plebs
      native / `warc-cicada3301_org`) never started. See `GAPS-D.md`.
