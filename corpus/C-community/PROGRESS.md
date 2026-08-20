# Lane C — PROGRESS

Started 2026-08-19. Working dir: `corpus/C-community/`.

| time (UTC) | action | result |
|---|---|---|
| 22:0x | Probed archive.org availability API | 429 rate-limited (other lanes active); CDX API works |
| 22:0x | CDX enumerate `cicada3301.boards.net` | 228 URLs, 83 thread captures |
| 22:0x | Wayback fetch boards.net | slow (~4-10s/req, throttled); partial |
| 22:1x | **Discovered cicada3301.boards.net is LIVE** | robots.txt UA:* permits `/thread/`, `/board/`; 15 boards, 64 threads enumerated |
| 22:1x | Fetched 63/64 live threads + 15 board indexes | forums/boards_net_live/ |

## RESUMED 2026-08-19/20 UTC after network outage (ENOTFOUND)

| action | result |
|---|---|
| Repaired `_logs/manifest.jsonl` | was malformed JSON (`"http_status":000` plus newlines inside `source_url`); 326 of 716 records unparseable. Original kept as `.orig`. Now 716 valid: 391 retrievals, 325 failures |
| Built `MANIFEST.json` | 465 files / 31.0 MB; **385 with resolved provenance**, 80 without (lane scripts/probes only) |
| Wrote `GAPS-C.md` | per-source block analysis (Reddit / Discord / Twitter / metzdowd / IRC / non-English / YouTube) plus a **provenance audit of the pre-existing Reddit dumps and Discord exports** |
| Wrote `CONFLICTS-C.md` | 6 conflicts, incl. the 2013 IRC insider claims vs the repo own Campaign XIX falsifier, and the void "Reddit corpus is empty" scoring |
| Wrote `REPORT-C.md` | lane report |

Open: 325 retryable boards.net Wayback failures; live-vs-archived thread diff never run;
Discord / non-English / YouTube still empty.
