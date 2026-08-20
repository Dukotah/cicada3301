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
