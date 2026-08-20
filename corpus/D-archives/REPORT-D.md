# Lane D — REPORT (archives)

Branch `corpus-sweep`. Working dir `corpus/D-archives/`.
Lane resumed and closed 2026-08-19/20 UTC after a network outage killed the fetch stage.

**Deliverables:** `MANIFEST.json`, `TIMELINE.json`, `CONFLICTS-D.md`, `GAPS-D.md`, this file.

---

## 1. What the lane holds

| | |
|---|---|
| files | **764** |
| bytes | **51.8 MB** |
| files with recorded provenance | 341 |
| files without recorded provenance | 423 (see `GAPS-D.md` D-G-07) |

Structure:

| directory | contents |
|---|---|
| `cdx/` | 354 raw CDX API responses, one per target query (7.5 MB) |
| `captures/` | 253 fetched Wayback bodies across 48 host directories (23 MB) |
| `bytediff/` | 91 bodies fetched specifically for the cross-date byte comparison (4.3 MB) |
| `iarchive/` | 43 archive.org item-metadata records (6.2 MB) |
| `logs/` | CDX query log, fetch failure log (2,496 rows), run transcripts |
| `TIMELINE.json` | the capture-history index: **15,474 URLs / 25,064 capture records** |
| `manifest.jsonl`, `manifest_normalised.jsonl`, `bytediff_manifest.jsonl` | per-file provenance with SHA-256 |

---

## 2. The headline question: do an archived file's bytes differ across capture dates?

**Answer: for the canonical Cicada artifacts, no — and that had never been established.**

The check was run at two levels (method in `CONFLICTS-D.md` D-C-01).

**Census level.** 1,597 URLs in `TIMELINE.json` have more than one HTTP-200 capture *and*
more than one distinct CDX payload digest. Taken at face value that looks like mass
divergence. It is not — see section 3.

**Byte level.** 33 immutable-resource URLs (images, raw pastes, audio, binaries) were
re-fetched at every 200-capture with the Wayback `id_` modifier, normalised for
Content-Encoding, and SHA-256'd. **28 of 33 are byte-identical across every capture date.**

The primary artifacts specifically:

- `i.imgur.com/KXLOP.jpg` — identical over 3 captures, 2020-11-12 -> 2024-02-05
- `i.imgur.com/zN4h51m.jpg` — identical over 8 captures, 2020-05-17 -> 2024-12-26
- `i.imgur.com/8D7hN.jpg` — identical over 3 captures, 2020-11-12 -> 2025-03-19
- `i.imgur.com/m9sYK.jpg` — identical over 6 captures
- `i.imgur.com/vjuNp.jpg` — identical over **9** captures spanning 2015-06-24 -> 2023-05-07,
  across both the `http://` and `https://` URL forms
- `i.imgur.com/hkdgl.png` — identical over 2 captures, 2022 -> 2025
- `pastebin.com/raw/yEiTHhvF` (the April-2017 "Beware false paths" PGP message) — identical
  over 2 captures, 2021-05-07 -> 2023-03-31
- 19 media files on `yniir5c6cmuwslfl.onion.link` — identical
- 3 images on `opensource.exposed` — identical

The 3 URLs that do differ are **not** canonical artifacts: two are imgur's own
server-generated derivatives (`zN4h51mh.jpg`, the "huge thumbnail"; and
`zN4h51m_d.webp?maxwidth=...&fidelity=...`, a transcoding endpoint that switched from JPEG
to WebP output between 2021 and 2025), and one is `845145127.com/` long after the domain
was parked. Full hashes and timestamps in `CONFLICTS-D.md`.

**What this negative is worth.** A solver working from an archived copy of the 2012–2014
imgur images does not need to care which capture date they pulled. That was previously an
untested assumption underlying every stego and hash analysis in this repository.

**What this negative does not cover.** 33 URLs out of 1,597 candidates. The untested
classes with real potential — Twitter media, 4plebs `/x/` threads, `clevcode.org`,
`liberprimus.com` — are enumerated in `GAPS-D.md` D-G-02.

---

## 3. Two traps that would each have produced a false major finding

Recorded in full in `CONFLICTS-D.md` D-C-03 because anyone repeating this check will hit them.

**(a) The CDX `digest` field is unreliable for this purpose.** 19 files under
`yniir5c6cmuwslfl.onion.link` carry *different* CDX digests across captures while their
fetched payloads are *byte-identical*. Likewise CDX `length` is the compressed record size,
not the payload size — `i.imgur.com/vjuNp.jpg` reports 30829/31126/31044/30917 for four
captures whose payloads are all exactly 31,004 bytes. **The 1,597 census figure is an upper
bound on candidates and nothing more.**

**(b) Transfer framing masquerades as content change.** The 2023 capture of
`pastebin.com/raw/yEiTHhvF` is 763 raw bytes against 970 in 2021 — different SHA-256, same
URL, an immutable raw paste, and the artifact is a *signed Cicada message*. It was the
strongest candidate the lane produced. The 763-byte body is **gzip-framed**; decoded, it is
970 bytes with SHA-256 `c0e4adbd8aab8e85e9976d6a06c889d415e83cf1e76a0f8b56cad10406eea800`,
byte-identical to 2021. Content-Encoding normalisation is not optional in this check.

---

## 4. One genuine cross-date content change — attribution undetermined

`http://5fpp2orjc2ejd2g7.onion.link:80/` demonstrably changed between
`20150919080207` (SHA-256 `09e5d716b3ffcb1a7d8b154c22c21e0f62706c0209e3c6f6d197bc0b1c513ae8`,
8,344 B) and `20170109022131`
(SHA-256 `47783b21fe9b5e3dbe19bc9a903a5c34a36fc009a35877609ded5b6371a329f8`, 7,928 B),
same host, same URL, no compression involved. The 2017 version rewrote the countdown target
and **left the original in a comment** (`var YY = 2017; //2014` ... `var DD = 30; // 03`,
i.e. original target 2014-08-03 01:33:00), renamed the referenced image
`um-caminho-errado.jpg` -> `.png` and gave it a non-standard
`atencao='o invisivel esta apenas em nossos olhos'` attribute, deleted a clock-riddle
paragraph, and dropped an 80-name "Os 80 primeiros escolhidos" roster present in the
2015-08-24 capture.

This proves capture date is load-bearing for that page. It does **not** prove Cicada 3301
changed anything: the site is Portuguese-language, unsigned, and its relationship to
Cicada is unadjudicated (`GAPS-D.md` D-G-04). Recorded as a conflict, deliberately not
resolved.

---

## 5. Coverage, and honesty about it

Enumeration finished; retrieval did not. **2,734 fetch jobs planned, 253 succeeded, 2,496
failed** — a ~91% failure rate driven by Wayback throttling and the outage, not by the
target list running out. Three targets (`uncovering-cicada.wikia.com`,
`uncovering-cicada.fandom.com`, `reddit.com/r/cicada`) hit the CDX 3,000-row cap, so their
capture histories in `TIMELINE.json` are **silently truncated**. Phase 4 (archive.today,
Common Crawl, 4plebs native API, the `warc-cicada3301_org` WARC item) never started.

Most onion captures that *were* retrieved are tor2web proxy failure pages rather than site
content, which is a fact about 2015–2018 proxy availability rather than about Cicada.

Everything above is itemised with a way to close it in `GAPS-D.md`.

---

## 6. Next steps in this lane, in order

1. **Pull the `warc-cicada3301_org` item** from archive.org (`iadl.py` already lists it).
   A WARC preserves request/response headers that the Wayback replay layer strips — it is
   the only way to see original `Content-Encoding`, `ETag` and `Last-Modified` for that
   site, and D-C-03 shows those headers matter.
2. **Extend the byte-diff to the six untested classes** in `GAPS-D.md` D-G-02, especially
   the 4plebs `/x/` threads and `clevcode.org`.
3. **Re-run the three limit-hit CDX queries with pagination** so the census stops being
   silently incomplete.
4. **Query Common Crawl** for the same URL set. It is an *independent* archive; a
   cross-archive byte comparison is a strictly stronger test than a within-Wayback one and
   nobody has run it.
5. **Verify the 7A35090F signature** on the April-2017 message now that its bytes are known
   stable (`GAPS-D.md` D-G-09).
