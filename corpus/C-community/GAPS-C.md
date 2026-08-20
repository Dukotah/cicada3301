# Lane C — GAPS

What Lane C could **not** retrieve, what blocked it, and what sits behind each block, so
the owner can retrieve it manually. Per the brief: **this is a deliverable, not a failure
report.** Every entry names the source, the obstacle, what is behind it, and the concrete
route in.

Lane state at close: **463 files / 30.6 MB** under `corpus/C-community/` (`MANIFEST.json`).
Branch `corpus-sweep`.

---

# PART 1 — Sources that BLOCKED retrieval

## C-G-01 — Reddit: no API access; only third-party mirrors were usable

**Blocked at:** reddit.com itself. Since the 2023 API terms change, `reddit.com/r/*.json`
and the Pushshift bulk endpoints require OAuth credentials and, for historical bulk data,
an approved research account. This lane had neither, so **no data was pulled from Reddit
directly.**

**What sits behind it:**
- `r/a2e7j6ic78h0j` — the 2012-era subreddit; the primary community record for puzzle 1.
- `r/Cicada` — the main long-running community.
- `r/cicada3301`, `r/a2e7j6ic78h0j7eiejd0120`.
- Deleted/removed comments and posts, which mirrors preserve unevenly and Reddit itself
  does not serve at all.

**Retrieved instead (mirrors, not Reddit):**
- `reddit/a2e7j6ic78h0j-archive.tar.gz` (2.35 MB) — from
  `github.com/cicada-solvers/a2e7j6ic78h0j-archive`, a community archive of the 2012
  subreddit.
- `reddit/irc_mentions_in_reddit.jsonl` (115 KB) — every IRC-referencing record mined out of
  the pre-existing Reddit dumps (see C-G-08), as a lead index for C-G-05.
- Wayback captures of Reddit listing pages were **enumerated** in Lane D
  (`reddit.com/r/cicada` 3,000 rows — CDX row cap hit; `r/a2e7j6ic78h0j` 1,140 rows) but
  not fetched here.

**Route in for the owner:** register a Reddit script app
(https://www.reddit.com/prefs/apps) for OAuth, or use the **arctic-shift** Pushshift mirror
(`https://arctic-shift.photon-reddit.com/api`) which is key-free and is what the
pre-existing dumps used — see `liber-primus/analysis/round10/L6-archives/pull_reddit.py`.
Arctic-shift rate-limits but does not require auth.

---

## C-G-02 — Discord: hard-blocked, requires an authenticated account in the server

**Blocked at:** Discord's API requires a user or bot token, and message history requires
the account to be a **member of the guild**. There is no anonymous read path, no public
archive endpoint, and scraping is against the ToS. **Nothing was retrieved from Discord in
this lane.** `corpus/C-community/discord/` is empty by design, not by oversight.

**What sits behind it:**
- The **CicadaSolvers Discord** — since ~2017 the de facto working centre of Liber Primus
  cryptanalysis. Per-page channels (`0-2`, `3-7`, … `40-55`), plus `gematria-primus`,
  `deep-web-hash`, `solved-pages`, `solving-lp-general-discussion`.
- This is where most negative results live. The repeated pattern in Liber Primus work is
  that an approach is tried, fails, and the failure is recorded only in Discord — so the
  *absence* of this channel is why the same dead ends get re-run.

**Partially mitigated:** a 13-channel export exists in the repo already
(`liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/discord/`, ~14.9 MB), but
its own provenance is incomplete — see C-G-08.

**Route in for the owner:** join `discord.gg/cicada` (CicadaSolvers) with a real account and
run **DiscordChatExporter** (`Tyrrrz/DiscordChatExporter`) per channel with
`--format Json --media`. Record the export date, the tool version, the channel IDs and the
message-ID range — that is exactly the metadata missing from the existing export.

---

## C-G-03 — Twitter/X: no anonymous read; API is paid

**Blocked at:** X removed anonymous timeline reading in 2023 and the v2 API's historical
search is a paid tier. **No live Twitter retrieval was possible.**

**What sits behind it:**
- `@1231507051321` — the 2013 Cicada account.
- `@3301actual` and the impostor/claimant accounts.
- Quote-tweets and replies, which no archive preserves well.

**Retrieved instead:**
- `twitter/2013_cicada_twitter_feed.txt` (139 KB) — the full 2013 `@1231507051321` feed as
  text, from a community source.
- `twitter/1231507051321_user_tweets.xlsx` (1.8 MB) — a tweet spreadsheet for the same
  account.
- Lane D enumerated `tw_3301actual` (7 divergent-digest URLs) and
  `tw_420087183957966849` in CDX but did not fetch them.

**Route in for the owner:** the Internet Archive item `1231507051321` (already indexed in
Lane D, `iarchive/meta__1231507051321.json`) contains `Feed @1231507051321.html` and is
free. For anything beyond that, X's API Basic tier or a manual browser session is the only
route.

---

## C-G-04 — `metzdowd.com` cryptography list: 56 consecutive 404s

**Blocked at:** HTTP 404 on every monthly mbox for the target window.
`_logs/failed.jsonl` records **56 failed URLs**, all of the form
`https://www.metzdowd.com/pipermail/cryptography/YYYY-Month.txt.gz`, covering 2011-01
through 2015-08.

**Retrieved anyway:** 19 monthly archives *did* come back (see `mailinglists/metzdowd-cryptography/`,
e.g. `2011-August.txt.gz`, `2013-June.txt.gz` … `2013-December.txt.gz`), so the list is
partially held. The 404s are for months where the `.txt.gz` filename convention differs or
the month is absent from the public pipermail index.

**Route in for the owner:** fetch the pipermail index page
(`https://www.metzdowd.com/pipermail/cryptography/`) and take the exact filenames from it
rather than constructing them; some months are published only as `.txt` or under a
different capitalisation.

---

## C-G-05 — IRC logs: THE BIGGEST MISSING ITEM (corpus `GAPS.md` G-05)

**Status: partially closed, still the largest hole.**

Why it matters: the April-2017 "Beware false paths" message was *discovered in IRC*, not on
a website. IRC is therefore **primary record**, not commentary — and for the 2012–2014
period it is the only continuous record of how solutions were actually reached.

**Retrieved (2 files):**
- `irc/2013_winners-leak_irc-log.txt` (60 KB) — the leaked 2013 winners' private-channel
  log. Provenance recorded in `_logs/manifest.jsonl` as method `scrape`, notes
  *"IRC log, 2013 winners' private channel leak"*.
- `irc/logs_linode_onion3.docx` (17 KB) — community logs on locating the Linode server
  behind onion 3.

**Still missing, and specifically:**
1. **`#cicadasolvers` on Freenode (later Libera.Chat)** — the main channel, ~2013 onward.
   No bulk log archive was found. Freenode's 2021 collapse means any channel-side logging
   bot's archive may be gone.
2. **Predecessor channels** — `#cicada`, `#cicada3301`, and the 2012-era channels named in
   Reddit threads. `reddit/irc_mentions_in_reddit.jsonl` was built precisely to index these
   mentions and is the lead list to work from.
3. **`logbot`-style public archives** — `_logs/logbot_meta.json` (77 KB) holds a probe of
   logging-bot archive services; no Cicada channel archive was recovered from it.
4. **`ia_search_cicada_irc.json`** — an Internet Archive full-text search for Cicada IRC
   logs. It returned few results; the search itself is preserved in `_logs/` so the query
   need not be re-invented.

**Route in for the owner, in order of likely yield:**
- Ask in the CicadaSolvers Discord for the community's own log archive; long-time members
  are the most probable holders. This is a social route, not a technical one, and it is
  the one most likely to work.
- `irclogs.whitequark.org` and `logs.libera.chat` for the Libera-era channel.
- Search `archive.org` for uploaded log dumps (`collection:opensource` + "cicada" + "irc").
- The 4plebs `/x/` threads (Lane D) frequently quote IRC verbatim; those quotes are a
  partial reconstruction if the logs themselves stay lost.

---

## C-G-06 — `cicada3301.boards.net`: retrieved, but read this caveat

Listed here not because it is missing but because **the retrieval was unusual and needs to
be recorded before someone assumes it was archive-only.**

The board turned out to be **still live**. Its `robots.txt` (`User-agent: *`) permits
`/thread/` and `/board/`, so the lane fetched it directly and politely:

- `forums/boards_net_live/` — **63 of 64 live threads plus 15 board indexes**, 79 files.
- `forums/boards_net/` — 202 files of Wayback captures (206 archive rows in
  `_logs/manifest.jsonl`).
- `forums/cdx_boards_net.json` — the CDX enumeration (2,104 rows in Lane D).

**Missing:** 1 of the 64 live threads (not recorded which; re-run `_logs/live_one.sh`
against `_logs/live_threads.txt` to identify and fetch it). Attachments and user profile
pages were not fetched.

---

## C-G-07 — `uncovering-cicada` wiki: exported as XML, NOT as captures

`wikis/uncovering-cicada/` holds **89 MediaWiki XML exports** pulled through the Fandom
API (`api.php action=query&export`, method `API` in `_logs/manifest.jsonl`).

**What that gives you:** current wikitext of each page.
**What it does NOT give you, and what corpus `GAPS.md` asked for:**
- **Page history / revisions.** The export is `&curonly`-style: only the current revision.
  Deleted and reverted content — often the most interesting, because it is where claims
  were retracted — is absent.
- **Talk pages.**
- **The wikia.com era.** The wiki moved `wikia.com` → `fandom.com`; content that existed
  only before the move is not in the current export. Lane D's CDX enumeration hit the
  **3,000-row cap** on both `uncovering-cicada.wikia.com` and `uncovering-cicada.fandom.com`,
  so even the capture list is truncated.

**Route in:** re-export with `&exportnowrap&curonly=0` for full revision history, or use
Fandom's `Special:Statistics` dumps. For the wikia.com era, paginate the Lane D CDX query
by year to get past the row cap (`GAPS-D.md` D-G-03).

---

## C-G-08 — Non-English communities: NOTHING retrieved

`corpus/C-community/non-english/` is **empty**. No Portuguese, Russian, German, Chinese or
Japanese community source was retrieved.

This is a live gap, not a theoretical one: Lane D found `5fpp2orjc2ejd2g7.onion`, a
**Portuguese-language** Cicada-style site with an 80-name participant roster and its own
countdown (`CONFLICTS-D.md` D-C-02), and there is an archive.org item named
`desmistificando-cicada-3301` ("Demystifying Cicada 3301") — also Portuguese. Neither has a
community record in this corpus.

**Known targets not touched:** Brazilian/Portuguese forums and the "Desmistificando"
material; Russian-language coverage (Habr, `xakep.ru`); German (`heise.de` forums);
Chinese (Zhihu, tieba); Japanese (2ch/5ch threads).

---

## C-G-09 — YouTube: NOTHING retrieved

`corpus/C-community/youtube/` is **empty**. No video, transcript, or comment thread was
retrieved. Documentary and explainer videos are a real part of the record (and their
comment threads occasionally carry solver claims), but nothing was pulled.

**Route in:** `yt-dlp --write-auto-sub --write-description --write-comments` per video,
recording the video ID, upload date and download date.

---

## C-G-10 — `cicada3301.boards.net` predecessor forums and other communities

Not attempted at all:
- **unfiction / ARGN forums** — the ARG-community discussion of 2012, referenced in
  `PAPERS-ARCHIVE.md` (`unfiction_alleged_winners.docx`).
- **`cicadasolvers.com`** — partially retrieved: 6 WordPress REST API JSON files
  (`wp_posts`, `wp_pages`, `wp_media`, `wp_categories`). Media files themselves not
  downloaded; comments not retrieved.
- **PiratePad / EtherPad captures** — referenced in `PAPERS-ARCHIVE.md` as present in the
  press archive but not independently retrieved here.
- **Bitmessage channels** — Cicada used Bitmessage addresses; no channel archive retrieved.

---

# PART 2 — PROVENANCE OF PRE-EXISTING HOLDINGS

The brief specifically required this. Two significant bodies of community data were already
in the repository before this operation. Here is exactly what is known and unknown about
each.

## C-G-11 — The pre-existing Reddit dumps (~52 MB)

**Location:** `liber-primus/analysis/round10/L6-archives/fetched/reddit/`

| file | bytes | records | earliest record | latest record |
|---|---|---|---|---|
| `Cicada_comments.jsonl` | 35,405,280 | 29,871 | 2013-12-30T03:26:07Z | 2026-07-20T21:38:55Z |
| `Cicada_posts.jsonl` | 17,657,927 | 7,160 | 2013-01-07T04:32:31Z | 2026-08-09T04:59:26Z |
| `a2e7j6ic78h0j_comments.jsonl` | 1,113,307 | 660 | 2012-01-04T20:18:11Z | 2026-08-10T19:24:58Z |
| `a2e7j6ic78h0j_posts.jsonl` | 190,171 | 192 | 2012-01-04T18:19:23Z | 2015-06-17T07:30:31Z |
| `cicada3301_comments.jsonl` | 0 | **0 — EMPTY FILE** | — | — |
| `cicada3301_posts.jsonl` | 4,110 | **1** | 2023-12-27T11:45:20Z | 2023-12-27T11:45:20Z |

(Record counts and date bounds computed in this lane and stored at
`corpus/C-community/reddit/HELD_DUMPS_STATS.json`.)

**KNOWN (recovered in this lane, previously unrecorded):**
- **Tool:** `liber-primus/analysis/round10/L6-archives/pull_reddit.py`, a resumable puller
  written for this repository.
- **Source:** the **arctic-shift** Pushshift mirror,
  `https://arctic-shift.photon-reddit.com/api`.
- **Subreddits requested:** `a2e7j6ic78h0j`, `Cicada`, `cicada3301`; kinds `posts`,
  `comments`.
- **Known prior bug, documented in that script's own docstring:** an earlier script
  (`analysis/round10/RECON-C/fetch_recon_c.sh`) paginated with `after=0`, which the API
  rejects, so it recorded 0 rows and *the corpus was mis-scored as empty*. `pull_reddit.py`
  starts at `after=1`. **Any conclusion drawn from the earlier "empty" state is void.**
- **Approximate capture date:** file mtimes are 2026-08-12 12:37–12:42 UTC-local.

**UNKNOWN — record these as unknown, do not assume:**
1. **No capture timestamp was recorded at fetch time.** The 2026-08-12 mtime is filesystem
   metadata, not provenance; a copy or a `touch` would destroy it.
2. **No SHA-256 was recorded at fetch time**, so there is no way to prove the files have
   not been altered since. (`MANIFEST.json` hashes them *now*, which establishes a baseline
   going forward but says nothing about the past.)
3. **No completeness record.** The script is resumable and skips non-empty files; it is
   therefore unknown whether any given file is a *complete* pull or a partial one from an
   interrupted run. `cicada3301_comments.jsonl` being 0 bytes and `cicada3301_posts.jsonl`
   holding exactly 1 record is consistent with either "the subreddit really is that empty"
   or "the pull was interrupted and the skip-if-non-empty logic then locked in the partial
   result." **This is not resolved.**
4. **No API response metadata was kept** — no request URLs, no pagination cursors, no HTTP
   statuses, no arctic-shift snapshot date. Arctic-shift is itself a mirror of Pushshift,
   which stopped ingesting at various points; **the coverage horizon of the underlying
   mirror is unknown**, which matters because Reddit-deleted content is present or absent
   depending on when Pushshift last saw it.
5. **Latest-record dates of 2026-07/2026-08 are unexplained** — they postdate the puzzle by
   more than a decade and indicate the pull included recent activity, but whether the
   *historical* window is complete cannot be inferred from that.

**To close:** re-run `pull_reddit.py` with per-file provenance logging (request URL, HTTP
status, UTC, SHA-256, row count) and diff the row counts against the table above. A
difference tells you the current files are partial.

## C-G-12 — The pre-existing Discord exports (~14.9 MB)

**Location:** `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/discord/`
(13 channel exports + `README.md`; largest is `solving-lp-general.txt` at 6.5 MB.)

**KNOWN (recovered in this lane):**
- **Immediate source:** `github.com/jaxonkuipers/cicada3301`, path `discord/`, fetched over
  `raw.githubusercontent.com` from branch `main` by
  `liber-primus/analysis/round10/L6-archives/fetch_jk.sh`.
- **Channel mapping is documented** in the bundled `README.md`: channel names are page
  ranges and map 1:1 to this repository's page numbering (`33-39` = `page-33`…`page-39`).
- The upstream `README.md` itself states these are *"community discussion, not primary
  source material — treat claims in them as unverified."*
- **Approximate capture date:** file mtimes 2026-08-12 12:53 local.

**UNKNOWN — the important ones:**
1. **No upstream commit pin.** `fetch_jk.sh` pulls from `main`, not a commit SHA. The
   upstream repository can change or disappear and there is **no way to prove which
   revision these files came from.** (Contrast Lane F, which pinned its press archive to
   `krisyotam/cicada3301` @ `1ccf9583b706` by git-blob-SHA1 byte match — the same could and
   should be done here.)
2. **Who exported them from Discord, when, and with what tool is entirely unknown.** These
   are second-hand exports: someone ran an exporter against the CicadaSolvers guild at some
   unknown date and committed the output. There is no export header, no message-ID range,
   no date range, no guild/channel ID.
3. **Completeness is unknown and unverifiable.** Whether a channel export covers the whole
   channel history or an arbitrary window cannot be determined from the files.
4. **No SHA-256 recorded at fetch.** Same caveat as C-G-11.
5. **Attachments, embeds and edits are absent.** These are plain-text exports; images,
   files and edit history posted in-channel are not present.
6. **Only 13 channels.** The guild has more. Which ones were omitted, and why, is unknown.

**To close:** (a) resolve the upstream repo to a commit SHA and record it, verifying the
held files by git blob hash, and (b) obtain a first-party export per C-G-02 so the corpus
has a copy whose export metadata is known.

---

# PART 3 — DATA-QUALITY DEFECTS IN THIS LANE

## C-G-13 — `_logs/manifest.jsonl` was malformed JSON — REPAIRED IN THIS PASS

Two defects in the lane's own fetch log made it machine-unreadable:

1. `"http_status":000` was written for connection-level failures. Leading zeros are invalid
   JSON.
2. Some `source_url` values carried an embedded newline, splitting single records across
   two physical lines.

Together these made **326 of 716 records unparseable**. Both are now repaired
(`_logs/manifest.jsonl.orig` preserves the original bytes). Post-repair the log holds
**716 records: 391 successful retrievals and 325 failures.**

**All 325 failures are the same thing:** `cicada3301.boards.net` Wayback captures, HTTP
status `0` (connection-level, i.e. the ENOTFOUND network outage that killed this lane), not
a block by the host. They are retryable and `forums/boards_net/` already holds 202 files
from the successful portion of that same sweep.

**Fix at source:** the fetch script should write `0` (or `null`) for connection failures
and strip newlines from URLs before logging.

## C-G-14 — provenance coverage in `MANIFEST.json`

After the C-G-13 repair and adding `_logs/manifest.jsonl` to the manifest builder's
provenance sources, `MANIFEST.json` resolves **385 of 465 files** to a recorded
`source_url` + `retrieved_utc` + `http_status` + retrieval `method`.

The remaining **80 files without per-file provenance** are the lane's own working files —
scripts in `_logs/` (`fetch.sh`, `wiki_export.py`, `mine_reddit.py`, …), intermediate probe
outputs (`gh_org.json`, `logbot_meta.json`, `cdx_cicadasolvers.json`, `found_urls.txt`),
and `PROGRESS.md`. None of them is corpus content; all are reproducible from the scripts
themselves. **No retrieved community artifact in this lane is unprovenanced** — the
outstanding provenance problems are C-G-11 and C-G-12, which concern holdings this lane did
not fetch.
