# Lane C — REPORT (community sources)

Branch `corpus-sweep`. Working dir `corpus/C-community/`.
Lane resumed and closed 2026-08-19/20 UTC after a network outage killed it mid-fetch.

**Deliverables:** `MANIFEST.json`, `GAPS-C.md`, `CONFLICTS-C.md`, this file.

---

## 1. What the lane holds

| | |
|---|---|
| files | **465** |
| bytes | **31.0 MB** |
| files with recorded provenance (source URL + retrieval UTC + HTTP status + method) | **385** |
| files without (lane scripts and probe outputs only) | 80 |

| directory | files | what it is |
|---|---|---|
| `forums/boards_net/` | 202 | `cicada3301.boards.net` Wayback captures |
| `wikis/uncovering-cicada/` | 89 | Uncovering Cicada wiki, MediaWiki XML export via Fandom API |
| `forums/boards_net_live/` | 79 | the **live** board: 63 of 64 threads + 15 board indexes |
| `mailinglists/metzdowd-cryptography/` | 20 | monthly pipermail archives |
| `mailinglists/cypherpunks/` | 13 | HyperKitty mbox exports, 2011–2015 |
| `forums/cicadasolvers_com/` | 6 | WordPress REST API dumps (posts, pages, media, categories) |
| `irc/` | 2 | **the 2013 winners'-leak IRC log** + onion-3 Linode logs |
| `twitter/` | 2 | full 2013 `@1231507051321` feed (text + spreadsheet) |
| `reddit/` | 3 | `a2e7j6ic78h0j` community archive, IRC-mention index, held-dump statistics |
| `discord/`, `non-english/`, `youtube/` | **0** | empty — see section 3 |

Per-file provenance is in `_logs/manifest.jsonl` (716 records: 391 retrievals, 325
failures). That log was malformed JSON when the lane died; it has been repaired in this
pass and the original bytes preserved as `_logs/manifest.jsonl.orig`
(`GAPS-C.md` C-G-13).

---

## 2. What was newly retrieved that the corpus did not have

- **A 2013 IRC log of self-claimed 3301 insiders** (`irc/2013_winners-leak_irc-log.txt`,
  820 lines, two sessions: 2013-02-13 and 2013-05-06). This is primary-record material of
  exactly the class corpus `GAPS.md` G-05 names as the biggest hole. It is analysed in
  `CONFLICTS-C.md` C-C-01 through C-C-03.
- **The live `cicada3301.boards.net` board.** It is not dead. `robots.txt` permits
  `/thread/` and `/board/`, and 63 of 64 threads plus 15 board indexes were fetched
  politely and directly.
- **The 2013 Twitter feed in full**, as text and as a spreadsheet.
- **Cypherpunks list mbox exports for 2011–2015** and 19 months of the metzdowd
  cryptography list.
- **`reddit/irc_mentions_in_reddit.jsonl`** — every IRC-referencing record mined out of the
  pre-existing Reddit dumps. This is the working lead-list for finding the still-missing
  channel logs.
- **`reddit/HELD_DUMPS_STATS.json`** — record counts and true date bounds for the
  pre-existing Reddit dumps, which had never been measured.

---

## 3. What blocked the lane

Full detail in `GAPS-C.md`; the short version, because the brief asked for it precisely:

| source | block | what sits behind it |
|---|---|---|
| **Reddit** | API requires OAuth since 2023; bulk history needs an approved research account. **Nothing pulled from Reddit itself.** | `r/a2e7j6ic78h0j`, `r/Cicada`, and deleted/removed content no mirror holds evenly |
| **Discord** | Token + **guild membership** required. No anonymous read path, no public archive endpoint. **Nothing retrieved.** | the CicadaSolvers server — where most Liber Primus *negative* results live, which is why the same dead ends keep getting re-run |
| **Twitter/X** | anonymous timeline reading removed 2023; historical search is a paid API tier | `@1231507051321`, `@3301actual`, replies and quote-tweets |
| **metzdowd.com** | 56 consecutive HTTP 404s on constructed monthly-mbox filenames | 2011–2015 cryptography-list traffic; 19 months did return and are held |
| **`cicada3301.boards.net` (Wayback)** | 325 connection-level failures (`http_status 0`) — the ENOTFOUND outage, not a host block | retryable; 202 files already retrieved from the successful part of the same sweep |
| **IRC `#cicadasolvers`** | no public bulk log archive found; Freenode's 2021 collapse likely took channel-side bots with it | the continuous 2013+ working record |
| **non-English communities** | not attempted | Portuguese material incl. the `5fpp2orjc2ejd2g7` site Lane D found and the `desmistificando-cicada-3301` archive.org item; Russian, German, Chinese, Japanese |
| **YouTube** | not attempted | documentaries, explainers, and their comment threads |

Each row in `GAPS-C.md` carries a concrete route in — API endpoint, tool, or the social
route where that is the honest answer (for IRC logs, asking long-time CicadaSolvers members
is more likely to work than any scrape).

---

## 4. Provenance of what we already held — the part that was never recorded

The brief asked for this specifically. Two large pre-existing bodies of community data sat
in the repository with **no capture date, tool or source recorded**. Both are now
documented in `GAPS-C.md` C-G-11 and C-G-12. Summary:

**Reddit dumps (~52 MB, `liber-primus/analysis/round10/L6-archives/fetched/reddit/`).**
*Now known:* pulled by this repo's own `pull_reddit.py` from the **arctic-shift** Pushshift
mirror (`arctic-shift.photon-reddit.com/api`), subreddits `a2e7j6ic78h0j` / `Cicada` /
`cicada3301`, mtimes 2026-08-12.
*Still unknown:* no capture timestamp recorded at fetch, no SHA-256 recorded at fetch, **no
completeness record** (the script skips non-empty files, so a partial file from an
interrupted run is indistinguishable from a complete one), no API response metadata, and no
record of the underlying mirror's own coverage horizon — which decides whether
Reddit-deleted content is present at all.

**Discord exports (~14.9 MB, `.../fetched/jaxonkuipers/discord/`).**
*Now known:* fetched by `fetch_jk.sh` from `github.com/jaxonkuipers/cicada3301`, path
`discord/`, branch `main`; the bundled `README.md` documents the channel-to-page mapping and
states the material is community discussion, not primary source.
*Still unknown, and this is the serious part:* **no upstream commit pin** (pulled from
`main`, so there is no way to prove which revision), and **who exported them from Discord,
when, and with what tool is entirely unknown** — no export header, no message-ID range, no
date range, no guild or channel IDs. Completeness is unverifiable. Attachments, embeds and
edits are absent. Only 13 channels of an unknown total.

Lane F demonstrates the fix on comparable material: it pinned its 133-file press archive to
`krisyotam/cicada3301` @ commit `1ccf9583b706` by **git-blob-SHA1 byte match**, turning an
asserted provenance into a verified one. The same is possible for the Discord export and
has not been done.

---

## 5. Conflicts found

Six, recorded unresolved in `CONFLICTS-C.md`. The two that matter most:

- **C-C-01.** The 2013 IRC log carries first-person insider claims ("Actually I WAS a 3301
  brood member", "They gave us access to a board in the tor network"). Measured against
  this repository's own pre-registered falsifier — which requires a claim that 3301
  distributed **cipher material or keys** and explicitly rules "they gave us access to a
  board" insufficient — **the log does not clear the bar.** It is still the dated primary
  material the falsifier was written to be tested against, and the log's own participants
  argue about each other's credibility in-channel.
- **C-C-06.** The pre-existing Reddit corpus was once scored **empty** because an earlier
  script paginated with `after=0`, which the API rejects. It is not empty: 29,871 `Cicada`
  comments, 7,160 `Cicada` posts, 660 + 192 for `a2e7j6ic78h0j`. **Any conclusion resting
  on "the Reddit corpus is empty" is void.**

---

## 6. Next steps in this lane, in order

1. **Diff the live `boards.net` threads against their Wayback captures.** Both corpora are
   already on disk (`forums/boards_net_live/` vs `forums/boards_net/`), the diff is cheap,
   and nobody has run it. It is the community-text analogue of the byte-diff Lane D ran on
   files, and a forum post edited after the fact would show up here.
2. **Retry the 325 boards.net Wayback failures** — they are connection-level, not blocks.
3. **Get a first-party Discord export** (C-G-02) and **pin the existing one to a commit
   SHA** (C-G-12). Until then the largest body of Liber Primus working discussion in this
   repo has unverifiable provenance.
4. **Work `reddit/irc_mentions_in_reddit.jsonl` as a lead list** for the missing channel
   logs, and ask in the CicadaSolvers Discord for the community's own archive. That is the
   single highest-value missing item in the whole corpus (G-05).
5. **Re-export the Uncovering Cicada wiki with full revision history** (`curonly=0`) — the
   current export drops exactly the reverted and deleted content that is most worth reading.
6. **Open the non-English gap**, starting with the Portuguese material, since Lane D turned
   up a live Portuguese-language Cicada-style site with an 80-name participant roster.
