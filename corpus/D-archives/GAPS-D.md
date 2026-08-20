# Lane D — GAPS

What Lane D did **not** retrieve, could not retrieve, or retrieved without adequate
provenance. Everything here is a real hole in the archive corpus, stated so the owner can
close it deliberately rather than discover it later as a silent assumption.

Branch `corpus-sweep`. Lane state at close: **764 files / 51.8 MB** under
`corpus/D-archives/` (see `MANIFEST.json`).

---

## D-G-01 — The fetch stage completed only a fraction of the enumerated captures

Phase 1 (CDX enumeration) completed: **354 CDX queries → 15,474 distinct URLs / 25,064
capture records** in `TIMELINE.json`.

Phase 2 (fetch) did **not**:

| | count |
|---|---|
| capture-fetch jobs planned (`fetchjobs.json`) | **2,734** |
| captures actually fetched into `captures/` (`manifest.jsonl`) | **253** (139 distinct URLs, 48 host dirs) |
| capture fetches attempted and failed (`logs/fetch_fail.jsonl`) | **2,496** |
| targeted byte-diff fetches completed afterwards (`bytediff_manifest.jsonl`) | 91 (33 URLs) |

Planned jobs by group: `imgur.com` 615, `cicada3301.boards.net` 320, `ONION` 241,
`uncovering-cicada.wikia.com` 220, `uncovering-cicada.fandom.com` 220, `845145127.com` 207,
`opensource.exposed` 160, `clevcode.org` 140, `reddit.com` 120, `cicada3301.org` 90,
`cicadasolvers.com` 90, `twitter.com` 80, `cicada3301.com` 60, `cicada3301.net` 50,
`pastebin.com` 43, `connortumbleson.com` 40, `liberprimus.com` 23, `iamamiwhoami.com` 15.

**2,496 failures against 253 successes is a ~91% failure rate**, so the low coverage is
throttling and outage, not exhaustion of the target list.

Cause: the fetch stage was killed by a network outage (`ENOTFOUND`) partway through, and
web.archive.org rate-limits hard (~4–10 s per request when throttled; parallel fetching
triggered `connection refused` within seconds). The lane was *not* resumed to completion —
only the byte-diff candidate set was.

**To close:** re-run `python3 fetch.py <seconds> [GROUP]` from
`corpus/D-archives/`. It is resumable (skips anything already in `manifest.jsonl` or
`logs/fetch_fail.jsonl`). Run it single-threaded with ≥1 s spacing; three concurrent
workers were refused by the host.

---

## D-G-02 — The byte-diff check covers 33 URLs, not 1,597

`CONFLICTS-D.md` D-C-01 reports a **negative** — canonical Cicada artifacts are byte-stable
across capture dates. That negative is only as wide as its sample.

- Byte-tested: **33 immutable-resource URLs / 91 captures.**
- Census candidates never byte-tested: **~1,564 URLs**, dominated by
  `cicada3301.boards.net` (397), `cicada3301.org` (359), `uncovering-cicada.wikia.com`
  (183), `reddit.com/r/cicada` (138), `uncovering-cicada.fandom.com` (133),
  `cicadasolvers.com` (103), `reddit.com/r/a2e7j6ic78h0j` (80).

Almost all of the untested remainder is dynamic HTML where per-render variation is expected
and evidentially empty. **But the following untested classes could still hide a real
divergence and are worth a targeted pass:**

1. **Twitter/`3301actual` media captures** (7 divergent-digest URLs under target `tw_3301actual`,
   1 under `tw_420087183957966849`). Not fetched at all.
2. **4plebs thread captures** (`archive.4plebs.org/x/thread/18491379/` — 3 divergent URLs;
   `…/18951995/` — 1). The `/x/` threads are primary record for 2012.
3. **`clevcode.org/cicada-3301/`** — 47 divergent URLs. Joel Eriksson's write-up pages;
   a revision there would be substantive.
4. **`liberprimus.com`** — 4 captures, all distinct digests, spanning 2013-06-03 → 2021-12-05.
   Not byte-tested.
5. **`opensource.exposed`** — 3 divergent URLs beyond the 3 images that were tested.
6. **`pastebin.com/yEiTHhvF` (the HTML wrapper, 8 divergent captures)** — the `/raw/` form
   was tested and is stable; the wrapper was not.

**To close:** extend `bytediff_jobs.json` with those targets and re-run
`python3 bytediff_fetch.py <seconds>`. The comparison script already normalises
Content-Encoding, which D-C-03(b) shows is mandatory.

---

## D-G-03 — `uncovering-cicada` wiki, `cicada3301.boards.net` and `r/cicada` CDX
enumeration hit the API row limit

`logs/cdx.log` and `PROGRESS.md` record four targets that returned exactly **3,000 rows**,
the CDX API's default cap:

- `uncovering-cicada.wikia.com` — 3000 (LIMIT HIT)
- `uncovering-cicada.fandom.com` — 3000 (LIMIT HIT)
- `reddit.com/r/cicada` — 3000 (LIMIT HIT)

Their capture histories are therefore **truncated, and truncated silently** — the census
figures in `CONFLICTS-D.md` under-report these three targets by an unknown amount.

**To close:** re-query with CDX pagination (`&showResumeKey=true` / `&resumeKey=`) or
split by year (`&from=YYYY&to=YYYY`). Until then no completeness claim about these three
domains is admissible.

---

## D-G-04 — `5fpp2orjc2ejd2g7.onion` attribution is undetermined

`CONFLICTS-D.md` D-C-02 documents a genuine cross-date content change on this onion.
Whether the site is Cicada 3301, Cicada-adjacent, or an imitator is **not established**.
Evidence held: Portuguese-language text, a countdown, an "Os 80 primeiros escolhidos"
roster of 80 personal names, Cicada-style register ("os 33", "ao terceiro toque do
martelo"), and an `atencao=` HTML attribute carrying a hidden sentence.

Nothing in this lane authenticates it. There is no PGP signature on any capture of it.
**Do not let D-C-02 be cited as "Cicada changed a page" without that adjudication.**

**To close:** cross-reference the address against Lane A's authenticated onion set and
against the 7A35090F signature record; check whether any signed Cicada communication ever
named it.

---

## D-G-05 — Other archives beyond the Wayback Machine were not swept

Phase 4 of the lane plan never ran. Not retrieved:

- **archive.today / archive.ph / archive.is** — no captures fetched. It holds pages the
  Wayback Machine does not, notably ones blocked by later `robots.txt`. It has no public
  bulk API and rate-limits aggressively; expect to fetch by hand.
- **archive.org *items*** (as distinct from web captures) — partially done. 43 metadata
  files under `iarchive/`, item downloads via `iadl.py` only partially completed. The
  named items still worth pulling in full: `warc-cicada3301_org` (a full WARC of
  cicada3301.org, 2016-11-26), `3301.iso`, `liber-primus` (`Liber Primus.zip`),
  `cicada_202405` (`cicada.zip`), `a2e7j6ic78h0j7eiejd0120`, `avowyfgl5lkzfj3n.onion`,
  `1231507051321`, `desmistificando-cicada-3301`, `cicada3301_midi`, `plpage0`.
  **The `warc-cicada3301_org` WARC is the highest-value un-pulled item** — a WARC preserves
  request/response headers the Wayback replay layer strips.
- **4plebs / desuarchive / warosu** direct APIs — only reached via Wayback, not natively.
  4plebs has a JSON API (`https://archive.4plebs.org/_/api/chan/thread/?board=x&num=…`)
  that returns the original post bodies and would beat the Wayback captures.
- **Common Crawl** — not queried at all. Its index covers 2013+ and would give an
  *independent* second archive of the same URLs, which is exactly what a byte-diff wants.
- **Software Heritage** — not queried in this lane (partially covered elsewhere in the repo).

---

## D-G-06 — Onion captures are dominated by tor2web proxy failure pages

Of the onion captures retrieved, the majority of bodies are proxy error pages
(`OnionLink: Could not connect`, `Tor2web Error: …`, `503 Backend fetch failed`), not site
content — see `CONFLICTS-D.md` D-C-05. The onion target list was built as 33 onion
addresses × 9 tor2web proxy suffixes precisely because no direct onion capture exists, and
the proxies were mostly down when crawlers visited.

**Consequence:** for most onion addresses in the target set this corpus holds **no
retrieved body at all**, only evidence that a proxy was unreachable. Direct Tor retrieval
is not possible (the services are long dead). The realistic remaining sources are the
Internet Archive *items* in D-G-05 and community mirrors.

---

## D-G-07 — Provenance is unrecorded for 423 of 764 files in this lane

`MANIFEST.json` reports **341 files with recorded provenance** (source URL + capture
timestamp + retrieval time) and **423 without**. The unrecorded set is:

- `cdx/*.json` — raw CDX API responses. The *query* is recoverable from `targets.tsv` +
  `logs/cdx.log`, but the exact request URL and response time are not stored per file.
- `iarchive/meta_*.json` — archive.org item metadata. Item identifier is in the filename;
  the fetch time is not recorded.
- lane scripts, logs, and the `bytediff/*.bin` blobs (whose provenance *is* in
  `bytediff_manifest.jsonl`, keyed by path — the manifest builder resolves those, so the
  423 figure is conservative for the blobs and accurate for `cdx/` and `iarchive/`).

**To close:** have `cdxwalk*.py` and `iadl.py` write a per-file provenance row (request
URL, HTTP status, UTC, SHA-256) the way `fetch.py` and `bytediff_fetch.py` already do.

---

## D-G-08 — CDX `length` and `digest` fields must not be used as byte-level evidence

Not a retrieval gap but a data-quality gap that will otherwise be re-discovered:

- **`length`** is the compressed WARC record size, not the payload size. Example:
  `http://i.imgur.com/vjuNp.jpg` shows CDX lengths 30829 / 31126 / 31044 / 30917 across
  four captures whose payloads are all exactly 31,004 bytes.
- **`digest`** diverged across captures for 19 files whose fetched payloads are
  byte-identical (`CONFLICTS-D.md` D-C-03a).

Any future analysis that infers "the file changed" from either field is wrong.

---

## D-G-09 — No signature verification was performed in this lane

The April-2017 PGP-signed message was retrieved and shown byte-stable (D-C-03b), but
**its signature was not verified against key 7A35090F** in this lane. Retrieval integrity
and cryptographic authenticity are different claims and only the first is established here.
