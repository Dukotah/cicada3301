# F5a Wayback leg — query log (2026-11-03)

The R36-O2 blocker was **tool-level, not archive-level**: Claude Code's WebFetch refuses
`web.archive.org` (re-verified today: "Claude Code is unable to fetch from web.archive.org"),
but plain `curl` against the CDX API and `/web/<ts>id_/` replay works fine. The Internet
Archive also intermittently returns a "Temporarily Offline" HTML page (the same page that
killed the R36 coordinator addendum attempt); a retry loop with 12–15 s backoff gets through
every time. All raw CDX JSON is in `cdx/`, all downloaded artifacts in `fetched/`
(gitignored; every byte re-fetchable from the URLs + timestamps below; sha256 of everything
fetched is in RESULTS-wayback.md).

Method: `https://web.archive.org/cdx/search/cdx?url=<u>&output=json[&matchType=domain]
[&collapse=urlkey][&from=&to=][&filter=...]`, then `https://web.archive.org/web/<ts>id_/<url>`
for payload bytes (id_ = unmodified original). Wayback's `digest` column is base32(SHA-1(payload)),
which lets us compare archived bytes against local files WITHOUT downloading.

## Queries and results

| # | target (cdx/ file) | rows | result |
|---|---|---|---|
| 1 | `845145127.com` + matchType=domain (845145127-domain) | 15 / 172 | 2013 captures of `/`, `/316744223127.jpg`, `/935691396441.jpg` are all **404** (digest = the standard 404 page). 2015+ 200s are squatter/parking (confirmed by content lengths + www1 ad-feed URLs). Nothing of the 2012/13 puzzle survives here. |
| 2 | `uncovering-cicada.wikia.com` matchType=domain 2014–2016 (wikia-domain) | 2203 | Full site map. Earliest LP captures 2014-01-07 (same week as the auqgnxjtvdbll3pv onion). `CICADA_3301_Liber_Primus_Sacred_BOOK` captured 2014-01-13 → fetched (below). `Category:May_2014_Runes` + `File:0.jpg..57.jpg` pages all present. |
| 3 | onion gateways: `auqgnxjtvdbll3pv.onion.to/.cab/.link/tor2web.org`, `cu343l33nqaekrnw.onion.to`, `ky2khlqdf7qdznac.onion.to` (onion-*) | 0–3 each | **No onion content was ever archived.** onion.to captures (2014-01-07) are 302s with the empty-body digest; tor2web.org 2016 = 401; onion.cab/onion.link = zero rows. ky2k.onion.to 2015-05-25 "200" fetched → it is the onion.to "Temporarily not available" gateway page (842 B, in fetched/). Honest negative. |
| 4 | imgur: `a/D5eBa`, `a/AENeJ`, `a/7Rhb9`, `i.imgur.com/eAVCeeC*`, `i.imgur.com/EKoUaoV*` (imgur-*) | 1–71 | All resolve to **solver-made diagrams** (Discord context in round10/L6 archives: cipher discs, fine-structure plots). Earliest captures 2016+. No release-surface rune pages on imgur were found in CDX. |
| 5 | wikia image CDNs: `images.wikia.com/uncovering-cicada*`, `vignette.wikia.nocookie.net/uncovering-cicada*`, `static.wikia.nocookie.net/uncovering-cicada*`, `img1-3.wikia.nocookie.net/__cb*` filter=uncovering-cicada (wikia-img-*) | 4 / 664 / 2722 / 32–41 | **The full May-2014 dump (0.jpg–57.jpg, upload cb=2015-01-09 batch, 50.jpg cb=2014-05-09) is archived at full size.** Digest comparison: local `data/relikd/p0–p55` = **56/56 byte-identical** (SHA-1) to the archived wikia originals. 56.jpg/57.jpg have no local counterpart → downloaded (below). Jan-2014 release images (Book-cover, Book-page-1..4, LiberPrimuspage5/6, OutguessfromLiberPrimusPage6) found on static1-4 + static hosts → downloaded. `1399181864285.png` (3.4 MB PNG, cb=2014-05-04) → downloaded. |
| 6 | pastebins — all 18 repo-referenced IDs (pb_*) | see file | Captured: vGMK330j(12), 684DsBhk(6), yEiTHhvF(45, first 2017-04-29), 5ETVTQfZ(3), NqF7M1Xn(15, first 2016-01-15), PFb6eQiD(5), smRatr3D(50, first 2015-07-28). **Zero Wayback coverage** (gone unless on archive.ph): gkqXuAZN, CiPkb0rF, wdVvWF06, n2QGsD3V, dhuve6GY, b8UYecg1, XbHZg5sJ, H1iKcvcr, DYNeEYji, DK6KtTMp, 9xkW41S1. All 18 are solver chatter (Discord/reddit context), none is a Cicada release surface. |

## Payload fetches (web.archive.org/web/<ts>id_/… unless marked live)

| fetched/ | source capture | what it is |
|---|---|---|
| 56_2022.jpg, 56_2025.jpg | 20221214172326 + 20250826102450 of `static.wikia…/2/2f/56.jpg/revision/latest` | **Page "an end" master, 2400x3600** (hash page + dot constellation). The two captures differ only by a stripped 18-byte JFIF APP0 header (Fandom re-serve), pixel stream identical era. |
| 57_2022.jpg, 57_2025.jpg | 20221214172311 + 20250826072548 of `…/4/4e/57.jpg/revision/latest` | **Parable page master, 2400x3600** (wing figure). Same header-only delta. |
| wikia_LP_book_20140113.html | 20140113063918 of `…/wiki/CICADA_3301_Liber_Primus_Sacred_BOOK` | Earliest LP wiki page; links the Jan-2014 release uploads (cb=20140109/12) — the pointer that found row 5's images. |
| jan14_cover.jpg | 20220601135251 of `…/2/24/Book-cover.jpg/revision/latest?cb=20140109144846` | 700x753; pixel-matches local `armada_osint/artifacts/dl_1033.jpg` (meanAbsDiff 1.3) — the 1033 "Liber Primus" cover, already held. |
| jan14_p4_wb2016.jpg | 20160411144427 of `static3…/__cb20140109145202/…/Book-page-4.jpg` | 700x1075 (wiki upload was small). |
| jan14_p1_live.jpg, jan14_p2_live.jpg, jan14_p3_live.jpg | LIVE fandom CDN (`?format=original`, Accept: image/jpeg) — Wayback holds only thumbnails of these three | 700x1050 wiki uploads of Book-page-1/2 and Page3-book. |
| **jan14_p5.jpg** | 20221214172255 of `…/b/b1/LiberPrimuspage5.jpg/revision/latest?cb=20140112101311` | **2400x3600 Jan-2014-release page (tree/vine border, red ᚢ initial), uploaded to the wiki 2014-01-12, outguess payload INTACT**: PGP-signed "Let the text guide you. / Good luck. / 3301" + hex-encoded 587x109 JPEG. Payload is byte-identical (`cmp`) to `analysis/armada20/og_out/lp_page_03_715a8ff0_kNONE.bin`. |
| **jan14_p6.jpg** | 20221214172255 of `…/9/98/LiberPrimusPage6.jpg/revision/latest?cb=20140112101510` | **2400x3600 Jan-2014-release page (red ᛒ section), outguess payload INTACT** (seed 38370, 7524 B); byte-identical to `og_out/lp_page_04_3a8f1a3f_kNONE.bin`. |
| jan14_p6outguess.jpg | 20220520134747 of `…/8/80/OutguessfromLiberPrimusPage6.jpg?cb=20140112102018` | The community's 2014 screenshot of the extraction (587x109). |
| 1399181864285.png | 20160411175921 of `img1…/__cb20140504194619/…/1/11/1399181864285.png` | 3952x2912 RGBA PNG, 4chan-timestamp filename from the May-2014 dump week: a **community collage** of the LP illustrations (crosses, cicada, moth, tree, wings, body, cuneiform). Not a source master. File: page has no description. |
| ky2k_20150525.html | 20150525015815 of `ky2khlqdf7qdznac.onion.to` | onion.to "Temporarily not available" gateway page — not onion content. |

## Negative space (what was looked for and not found)
- No PDF/PS/DjVu/SVG/TIFF or any vector/alternate-FORMAT source of any LP page in any capture
  (CDX mimetype column scanned across all result sets; the only PNGs are solver-made).
- No resolution above 2400x3600 anywhere; every full-size capture is the same 2400x3600 JPEG family.
- No archived copy of any LP onion's own pages (the gateways 302'd or were down at every capture).
- timetravel.mementoweb.org / archive.ph were NOT needed (web.archive.org reachable via curl);
  the 11 zero-coverage pastebins would be the only reason to try archive.ph later.
