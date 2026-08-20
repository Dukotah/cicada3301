# Lane D — CONFLICTS

Conflicting or divergent evidence found in the archive lane. **Nothing here is resolved.**
Both sides of every conflict are recorded with hashes, timestamps and archive URLs so a
later reader can adjudicate.

Generated 2026-08-19/20 UTC, branch `corpus-sweep`.

---

## D-C-01 — THE HEADLINE CHECK: do an archived file's bytes differ across capture dates?

This is the check the brief called out as never having been run for any Cicada artifact.
It has now been run at two levels.

### Method

1. **Census level (cheap, corpus-wide).** `TIMELINE.json` holds every CDX row for 354 target
   queries: **15,474 distinct URLs / 25,064 capture records**. The CDX `digest` field is a
   payload SHA-1, so URLs whose captures carry more than one digest are *candidates* for
   byte divergence.
2. **Byte level (authoritative).** For a curated set of **immutable-resource** URLs (images,
   raw pastes, audio, binaries — resources whose bytes are not supposed to change), every
   HTTP-200 capture was re-fetched with the Wayback `id_` (identity / no-rewrite) modifier
   and hashed with SHA-256.
3. **Content-Encoding normalisation.** Each fetched body was tested for gzip/zlib/raw-deflate
   framing and, where present, decompressed before hashing. *(This step is not optional —
   see D-C-03.)*

### Census result

| | count |
|---|---|
| distinct URLs in `TIMELINE.json` | 15,474 |
| capture records | 25,064 |
| URLs with >1 capture | 3,472 |
| URLs with >1 HTTP-200 capture **and** >1 distinct CDX payload digest | **1,597** |

Top targets by divergent-URL count: `cicada3301.boards.net` (397), `cicada3301.org` (359),
`uncovering-cicada.wikia.com` (183), `reddit.com/r/cicada` (138),
`uncovering-cicada.fandom.com` (133), `cicadasolvers.com` (103),
`reddit.com/r/a2e7j6ic78h0j` (80), `clevcode.org/cicada-3301/` (47), `845145127.com` (12).

Nearly all of these are *dynamic* pages (forum indexes, wikis, Reddit listings) where
per-render variation is expected and carries no evidential weight. The census is therefore
a candidate list, **not** a finding.

### Byte-level result — 33 immutable-resource URLs, 91 captures fetched

**28 of 33 URLs: bytes are IDENTICAL across every capture date.**
**3 of 33 differ, and none of the three is a canonical Cicada artifact** (below).
**2 URLs had only one capture retrievable and were dropped from the comparison.**

The primary Cicada image artifacts are all stable. This is the documented negative the
brief asked for, and it has never been established before:

| URL | captures | span | SHA-256 (identical across all) |
|---|---|---|---|
| `https://i.imgur.com/KXLOP.jpg` | 3 | 2020-11-12 → 2024-02-05 | `7bc12b2647b38cb426ffb54f9369f36526a1360f53f859c26e41cb7e92565ea6` |
| `https://i.imgur.com/zN4h51m.jpg` | 8 | 2020-05-17 → 2024-12-26 | `07ea379f22c899944df7d009dbeb61e5583a55afccf97e12d14ac0e097f75867` |
| `https://i.imgur.com/8D7hN.jpg` | 3 | 2020-11-12 → 2025-03-19 | `2d9e10b6d779ebc5664bbe21f575e4bb52f58d50ce39b0c1c0d17e741dc52f80` |
| `https://i.imgur.com/m9sYK.jpg` | 6 | 2020-11-01 → … | `47c2891c7b282f2e5fc5f5af65cf66935a1161ebc9518533e90189d0e64147d7` |
| `http://i.imgur.com/vjuNp.jpg` | 4 | 2015-06-24 → 2019-09-18 | `6c8a8e3096208718d75a59d62ac5f66428e73b64e8bb3bdf689ff5dddee84ce4` |
| `https://i.imgur.com/vjuNp.jpg` | 5 | 2020-09-03 → 2023-05-07 | `6c8a8e3096208718d75a59d62ac5f66428e73b64e8bb3bdf689ff5dddee84ce4` |
| `https://i.imgur.com/hkdgl.png` | 2 | 2022-05-03 → 2025-11-17 | `f4be4b74b1cc1479f9482d0e670375450b43d1b500a991de644f1cc9dea00217` |
| `https://pastebin.com/raw/yEiTHhvF` | 2 | 2021-05-07 → 2023-03-31 | `c0e4adbd8aab8e85e9976d6a06c889d415e83cf1e76a0f8b56cad10406eea800` |
| `https://yniir5c6cmuwslfl.onion.link/*` (19 media files) | 2 each | 2017-08-24 → 2017-08-26 | identical per file |
| `http://opensource.exposed/images/*` (3 files) | 2 each | 2018-08-25 → 2022-04 | identical per file |

Note the `vjuNp.jpg` result crosses the `http://` and `https://` URL forms **and a
2015→2023 span**: the same SHA-256 in nine independent captures over eight years.

Per-file rows: `bytediff_manifest.jsonl` (fields `norm_sha256`, `norm_bytes`,
`content_encoding_detected`, `archive_url`, `capture_timestamp`).

### The 3 URLs that DO differ — and why none is a Cicada content change

| URL | capture | norm SHA-256 | bytes | what it is |
|---|---|---|---|---|
| `https://i.imgur.com/zN4h51mh.jpg` | `20230518103925` | `4977342d031774de071bc495d830522a22c883b3aa838933e76de693a89e14c1` | 17,429 | imgur **`h` thumbnail** derivative |
| | `20260622154916` | `46a3a5b3ae4dfde76879ba06fe4ba88c234c3ea4fed1c903112449dbebdb2331` | 40,930 | same URL, re-encoded server-side |
| `https://i.imgur.com/zN4h51m_d.webp?maxwidth=760&fidelity=grand` | `20210119033448` | `5a4ede3b544c1bc42ebffa0f3ffffb3152c98926fbe7cc5c7bd89774c3d82ea9` | 11,136 | served as `image/jpeg` |
| | `20250425173905` | `53a455c04f87b656d39410c11d9367de72079b707a0c69cf7182a95350a9e0d1` | 16,278 | served as `image/webp` |
| | `20260322230228` | `cd90c2b428ea2949a3e4b1bcf2278af242099d8c03adfb02c44f61c094b2df7e` | 11,122 | `image/webp`, re-encoded again |
| `http://845145127.com/` | `20210610`–`20250627` (7 captures) | `c53b3887bde90d93cc6139eb7c1e0bdd0cf9deec08055d25ff952d5a682fc99b` | 108 | domain long since parked |
| | `20260209050503`, `20260621050724` | `565339bc4d33d72817b583024112eb7f5cdf3e5eef0252d6ec1b9c9a94e12bb3` | 2 | parking page shrank to 2 bytes |

Both imgur cases are **server-side derivatives**, not the canonical upload: `…mh.jpg` is
imgur's generated "huge thumbnail" and `…_d.webp?maxwidth=…&fidelity=…` is a transcoding
endpoint whose output format demonstrably changed (JPEG → WebP) between 2021 and 2025.
The canonical `zN4h51m.jpg` is byte-stable across all eight captures in the same period.
`845145127.com` in 2021+ is parked-domain boilerplate, years after the puzzle.

**Conclusion for D-C-01.** For the canonical Cicada image and paste artifacts held in the
Wayback Machine, **no file's bytes differ across capture dates.** Divergence exists only
in (a) server-generated derivative URLs and (b) dynamic or post-abandonment pages. This is
a *negative*, and it is a useful one: the community's working copies of the 2012–2014
imgur artifacts are not date-dependent, and a solver need not worry that a different
capture date would yield different carrier bytes.

**Scope limit — read this before citing the negative.** 33 URLs were byte-tested out of
1,597 census candidates. The untested remainder is overwhelmingly dynamic HTML. The
untested classes that *could still* hide a divergence are listed in `GAPS-D.md` (D-G-02).

---

## D-C-02 — A REAL cross-date content change: the `5fpp2orjc2ejd2g7` onion

Distinct from D-C-01 (which concerns *files*), one **page** in the target set demonstrably
changed content between captures, on the same host, same URL.

**URL:** `http://5fpp2orjc2ejd2g7.onion.link:80/` (tor2web proxy of the
`5fpp2orjc2ejd2g7.onion` hidden service)

| capture | SHA-256 (identity encoding) | bytes | archive URL |
|---|---|---|---|
| `20150919080207` | `09e5d716b3ffcb1a7d8b154c22c21e0f62706c0209e3c6f6d197bc0b1c513ae8` | 8,344 | `https://web.archive.org/web/20150919080207id_/http://5fpp2orjc2ejd2g7.onion.link:80/` |
| `20151015071107` | `55fc2881b7083718b8116ef6942d63c9ebbc7731ac2fc946b27d01a359088c43` | 1,941 | `https://web.archive.org/web/20151015071107id_/http://5fpp2orjc2ejd2g7.onion.link:80/` |
| `20160424183856` | `55fc2881b7083718b8116ef6942d63c9ebbc7731ac2fc946b27d01a359088c43` | 1,941 | `https://web.archive.org/web/20160424183856id_/http://5fpp2orjc2ejd2g7.onion.link:80/` |
| `20170109022131` | `47783b21fe9b5e3dbe19bc9a903a5c34a36fc009a35877609ded5b6371a329f8` | 7,928 | `https://web.archive.org/web/20170109022131id_/http://5fpp2orjc2ejd2g7.onion.link:80/` |

(The two 1,941-byte captures are an `OnionLink: Could not connect` proxy error page, not
site content.)

Substantive differences between the 2015-09-19 and 2017-01-09 page bodies:

- **The countdown target was rewritten, and the original left in a comment.** 2015 reads
  `var YY = 2015; var MM = 09; var DD = 15;`. 2017 reads
  `var YY = 2017; //2014` / `var MM = 04; // 08` / `var DD = 30; // 03` — i.e. the 2017
  page carries the *original* target date `2014-08-03 01:33:00` as an inline comment.
  A third capture, `http://5fpp2orjc2ejd2g7.onion.city/` at `20150824075800`
  (SHA-256 `4d194e043cec6e14c12ff1a97f9c80ab300165d727a6196a7a679f64264e5910`, 9,067 B)
  reads `var YY = 2014; var MM = 08; var DD = 03;` — matching that comment.
- **The referenced image changed name, extension and attributes:**
  `<img src="um-caminho-errado.jpg">` (2015) → `<img src='um-caminho-errado.png'
  atencao='o invisível está apenas em nossos olhos'>` (2017). The 2017 form carries a
  non-standard HTML attribute containing a Portuguese sentence — i.e. a message placed in
  markup, not in rendered text.
- **A paragraph present in 2015 is deleted in 2017** (the "23 horas, 54 minutos e 06
  segundos … 46 horas, 58 minutos e 05 segundos" clock passage), and a clause is added to
  the red-text line ("É um novo tempo e uma nova busca").
- **An 80-name "Os 80 primeiros escolhidos" list appears in the 2015-08-24 capture and is
  absent from later captures.**
- Character encoding changed from Latin-1 to UTF-8 between the two.

**Conflict, unresolved:** this establishes that *page content behind an onion address in
this corpus's target list did change across capture dates*, so the capture date is
load-bearing for that page. **It does NOT establish that Cicada 3301 changed anything.**
`5fpp2orjc2ejd2g7.onion` is a Portuguese-language site; this repo's target list includes
it among the onion addresses to sweep, but **whether it is Cicada 3301, a Cicada-adjacent
project, or an imitator ARG is not determined here and is not adjudicated.** Both
readings are on the record; see `GAPS-D.md` D-G-04.

---

## D-C-03 — METHODOLOGICAL CONFLICT: two indicators disagree about "the bytes differ"

Two near-misses would each have produced a false major finding. Both are recorded because
anyone repeating this check will hit them.

### (a) CDX `digest` diverges while the payload bytes are identical — 19 cases

For all 19 media files under `https://yniir5c6cmuwslfl.onion.link/`, the two captures
carry **different CDX digests** but, once fetched, **identical SHA-256 payloads**.

Example — `https://yniir5c6cmuwslfl.onion.link/gold.png`:

| capture | CDX digest | fetched SHA-256 | bytes |
|---|---|---|---|
| `20170824211626` | `4ERRL5QOEKYSKUWEBITA5PEXUKTD7UOZ` | `0de247f4c94e914ffe8452f41bdc3e2c37a971505a362499c68cac7de4035bd1` | 41,655 |
| `20170826010300` | `TQWCTHXYIMPCRBLAJTHZZT2NJOERGA2R` | `0de247f4c94e914ffe8452f41bdc3e2c37a971505a362499c68cac7de4035bd1` | 41,655 |

Same for `airhorn.ogg`, `alien.gif`, `bax.png`, `bls.jpg`, `bug.gif`, `coments.gif`,
`i2p.png`, `milk.png`, `money.jpg`, `redshit.gif`, `rss.png`, `rw.jpg`,
`sanictwitter.png`, `spooky.gif`, `stamp2.png`, `tinykek.png`, `tmb.png`, `wewlad.png`.

**Consequence: the CDX `digest` field is not a sound basis for claiming byte divergence.**
It appears to be computed over a record whose framing (transfer-encoding / proxy headers)
varied between crawls. The 1,597-URL census figure in D-C-01 must therefore be read as an
**upper bound on candidates**, never as a count of divergent files.

### (b) A gzip-framed replay that looks like a different file — 1 case, and it was the
best candidate in the whole lane

`https://pastebin.com/raw/yEiTHhvF` is the paste containing the **April-2017 PGP-signed
"Beware false paths" message** — a primary Cicada artifact. Raw fetch:

| capture | raw SHA-256 | raw bytes | framing |
|---|---|---|---|
| `20210507215131` | `c0e4adbd8aab8e85e9976d6a06c889d415e83cf1e76a0f8b56cad10406eea800` | 970 | identity |
| `20230331122257` | `ed03c0f363f2e89b8e283ab23d4458f2ef2e17c039c362c2c50c2600cb905725` | 763 | **gzip** |

At the raw level these are different bytes for the same immutable paste — which, taken at
face value, would have been the major finding. **After gzip decoding, the 2023 body is
970 bytes with SHA-256 `c0e4adbd8aab8e85e9976d6a06c889d415e83cf1e76a0f8b56cad10406eea800`
— byte-identical to the 2021 capture.** Verified content of both:

```
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Beware false paths.  Always verify PGP signature from 7A35090F.

3301

-----BEGIN PGP SIGNATURE-----
Version: CicadaPG v.3301
[…]
=6zQ2
-----END PGP SIGNATURE-----
```

**Finding: NEGATIVE, and strongly so.** The April-2017 message's paste is byte-stable
across the archive. The apparent difference was transfer framing.

---

## D-C-04 — `http://845145127.com/935691396441.jpg`: 404 page vs. actual JPEG

| capture | SHA-256 | bytes | body |
|---|---|---|---|
| `20130811103715` | `dc1d54dab6ec8c00…` (see `manifest_normalised.jsonl`) | 1,245 | XHTML **404 page**, not an image |
| `20210402181919` | `2c4fb730a3df3516…` | 2,940 | actual JFIF JPEG |

Conflict recorded, not resolved: the *earlier* capture of an image URL on the original
2012 countdown domain returns a 404 body while a *later* (2021, post-parking) capture
returns image bytes. The 2021 bytes almost certainly belong to the parking service, not to
Cicada, but nothing here proves that, and the 2013 404 is itself evidence about what was
served at that path in 2013.

---

## D-C-05 — Proxy-layer divergence (recorded, low evidential value)

16 of the 19 multi-capture URLs in the main `captures/` set differ across dates. Excluding
D-C-02 and D-C-04, every remaining case is a **tor2web proxy layer** artifact: alternating
`OnionLink: Could not connect`, `OnionLink: Generic Error`, `Tor2web Error: Hidden Service
Not Reachable`, `Tor2web Error: Generic Sock Error`, `503 Backend fetch failed`, and
`robots.txt` requests answered with an HTML error page rather than a robots file.

These say nothing about Cicada content; they record the *availability history of the tor2web
proxies*, which is itself the reason so many onion captures in this corpus are empty.
Listed in full in `manifest_normalised.jsonl`; the affected URL families are
`5fpp2orjc2ejd2g7`, `a.l.i.cia.5fpp2orjc2ejd2g7`, `auqgnxjtvdbll3pv`,
`cu343l33nqaekrnw`, `lwplxqzvmgu43uff`, `rjzdqt4z3z3xo73h`, `yniir5c6cmuwslfl` across the
`.to`, `.link`, `.city` and `.cab` proxy suffixes.

---

## D-C-06 — `cu343l33nqaekrnw.onion.to` content vs. later proxy error

| capture | SHA-256 | bytes | body |
|---|---|---|---|
| `20140107125633` | `b9722427c162f3b2…` | 368 | `<!--Patience is a virtue-->` followed by a long hex string |
| `20160411073840` | `997418c4a40c948a…` | 860 | `Tor2web Error: Generic Sock Error` |

Recorded because the 2014 capture is the *only* retrieved body for this onion and its
content (an HTML comment "Patience is a virtue" plus a hex blob) is substantive. The 2016
difference is proxy failure, not content change. Not resolved here; flagged for Lane A/B
to cross-reference against the known 2014 onion set.
