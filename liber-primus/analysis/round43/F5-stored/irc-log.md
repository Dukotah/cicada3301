# Round 43 — Lane F5b query log (archived IRC / pads / wiki talk / early reddit, KEY-MATERIAL hunt)

Date: 2026-11-03. Prior campaigns searched these sources for attribution only; this lane re-searched them for key material.
Baseline read first: `analysis/armada_osint/artifacts/raw/{2012..2017}.md` (3,552 lines total; 2014.md holds the onion-7
index.html verbatim: title `133`, `div id="331"`, sequential `<img src="0.jpg">`..`57.jpg`).

## Queries run (chronological)

| # | Tool | Query / URL | Result |
|---|------|-------------|--------|
| 1 | WebSearch | `#cicadasolvers IRC log 2014 archive "3301" onion log site:archive.org OR irclog` | Pointed to spiers.usr.sh:808/#cicadasolvers.log (dead), uncovering-cicada fandom, krisyotam/cicada3301 archive repo |
| 2 | WebSearch | `"ky2khlqdf7qdznac" onion index.html "57.jpg" OR "runes.txt" OR directory listing` | fandom "What Happened Liber Primus (Post 2014)"; micheloosterhof/cicada-2014 |
| 3 | WebFetch | fandom What_Happened_Liber_Primus_(Post_2014) | HTTP 402 (fandom blocks WebFetch); recovered instead from LOCAL wiki export (corpus/C-community/wikis/uncovering-cicada/export_cur_01780.xml) |
| 4 | gh api | micheloosterhof/cicada-2014 full tree | stage11 = ky2khlqdf7qdznac.onion mirror incl. index.html + 0-57.jpg + message.txt.asc |
| 5 | curl | raw stage11/index.html (md5 aaf1aa4d3fc0440c3a62eed5452c2876) + message.txt.asc (md5 6808ed6409c243aacfe8a0f077dba606) | Byte-exact confirmation of our record's ordering; trailing-space primes measured: 2,3,5,7,11,13,17,23,29,31,37 (19 absent), leading 5 spaces before onion line |
| 6 | wayback API | spiers.usr.sh IRC log; uncovering-cicada Talk:Liber_Primus | no snapshots |
| 7 | gh api / curl | krisyotam/cicada3301 tree → cijhho Titanpad mirrors | Fetched the two hex megastrings our raw/2014.md marks "TODO: missing"; md5-identical copies ALREADY HELD at corpus/A-primary-artifacts/cijhho123/... (f2f0841a..., 0cfa2e67...) |
| 8 | local grep | corpus/C-community (irc/, wikis/, reddit/), cijhho pads | winners-leak log already adjudicated (CONFLICTS-C C-C-01..03); wiki ns1 talk pages (500) held locally; no entity-authored strings beyond record |
| 9 | local extract | wiki pages "Possible hints never used", "What Happened LP (Post 2014)", "MAIN ... PAGE PART 2", "ONION 2 with 3 JPGs ..." | cookies/P.S. number/missing-primes all already in raw record; found the onion-2 growing-string TIMING tables + pastebin pointers |
| 10 | IRC pad (local+fetched) | "We dont have legit html of onion 3 v2 string logs.txt" (#33012014, 2014-01-11 14:36-14:51) | the "with 57 / without 57" capture dispute of the Jan-11 onion-3 hex; dragonstudios.tk and gjvc.com capture URLs |
| 11 | wayback CDX | dragonstudios.tk/cicada33012014-fv7lyucmeozzd5j4.onion.txt; gjvc.com/3301/* | dragonstudios: single 2022 snapshot = parked-domain page (original lost); gjvc: 404s only (2016). The "with 57" variant is UNRECOVERABLE |
| 12 | WebSearch | `"cicadasolvers" OR "#33012014" IRC log full archive ... "Lurker69"`; reddit Jan 2014 ky2khlqdf7qdznac | No surviving bulk #cicadasolvers archive (consistent with GAPS-C C-G-05); Zenodo 18199474 = crank "complete translation" (solver speculation, context only) |
| 13 | WebFetch | cicada-solvers/documenting-cicada3301-scream314 links.md | no IRC-log/pad links |
| 14 | curl | pastebin raw qn8jmPJr and 5bTLHqCN | BOTH LIVE — onion-2 growing-string timing datasets recovered and stored (see RESULTS) |

## Sources that are dead / out of reach
- spiers.usr.sh:808/#cicadasolvers.log — dead, never archived.
- dragonstudios.tk "with 57" onion-3 capture — parked since ≤2022, no content snapshot.
- gjvc.com/3301/* curl capture — 404 since 2016, no content snapshot.
- Fandom live talk pages via WebFetch — 402/Cloudflare; mitigated: full ns1 (Talk:) export already held locally in corpus.
- infotomb.com (all onion dumps: his5u, 1fn08, svu5q, k11ys, pqdcz, 6mtc6, vnq3e, pnid9, xgh2q, 3kcte.txt) — infotomb is dead; the payloads survive only via micheloosterhof/cijhho mirrors (held).
