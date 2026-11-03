# F5a RESULTS — the Wayback leg (R36-O2's "BLOCKED-not-searched" caveat)

**Verdict: FOUND (corpus gaps filled + mirror integrity proven) — and the leg is now actually
searched, so R36-O2's Wayback caveat is CLOSED.** Full query log: `wayback-log.md`;
raw CDX JSON in `cdx/`; artifacts in `fetched/` (gitignored, re-fetchable; hashes below).

The R36 blocker was the tool, not the archive: WebFetch refuses web.archive.org, `curl`
does not. Every target the task named was queried (CDX + payload replay, retry-with-backoff
through the Archive's intermittent "Temporarily Offline" page).

## Findings

1. **Mirror integrity of the May-2014 dump is now PROVEN, not assumed.** All 58 images of the
   dump are archived full-size on the uncovering-cicada wikia CDN (upload batch cb=2015-01-09;
   50.jpg cb=2014-05-09). Wayback's digest column is base32(SHA-1), so comparison needs no
   download: **local `data/relikd/p0–p55` are 56/56 byte-identical to the archived copies.**
   Every negative over the rune corpus also covers the wikia lineage.

2. **FOUND — two dump pages our relikd set lacks**, recovered at full 2400x3600:
   - `56.jpg` = the "an end" page (red ᚠ, 512-bit hash, dot constellation) — `fetched/56_2022.jpg`,
     sha256 `a4c1c9ae1246c3197fc1d7bd0155cbc97f60d4bba84a104d45f180feab1814dc`
   - `57.jpg` = the parable page (wing figure) — `fetched/57_2022.jpg`,
     sha256 `1dabc100ddbf1fc49715219636984eb6ad96a2bd8035e196c12e66db77a1077b`
   (2022 vs 2025 captures differ only by a stripped 18-byte JFIF header.)
   Transcriptions existed (`data/sources/relikd_p56_an_end.txt`, `_p57_parable.txt`); the
   master images did not.

3. **FOUND — the January-2014 first-release generation, with intact steganography.** The
   earliest LP wiki page (captured 2014-01-13) links the release uploads of 2014-01-09/12.
   Recovered at 2400x3600 with **outguess payloads intact**:
   - `fetched/jan14_p5.jpg` (`LiberPrimuspage5.jpg`, cb=20140112101311), sha256
     `b8b142f9b7854ec4f240e076cad03a98a2e3e9cf7c20f1da4fcde1ed25e3be3f` — payload = PGP-signed
     "Let the text guide you" + embedded 587x109 JPEG, **byte-identical (`cmp`) to
     `analysis/armada20/og_out/lp_page_03_715a8ff0_kNONE.bin`**.
   - `fetched/jan14_p6.jpg` (`LiberPrimusPage6.jpg`, cb=20140112101510), sha256
     `745c6a46f67de1e5a2a9ac76175c323af82c2432e3b7483a8dc6244f8de9478f` — payload
     byte-identical to `og_out/lp_page_04_3a8f1a3f_kNONE.bin`.
   Why this matters: armada20's 17 Jan-2014 carriers (`lp_page_00..16`) came from a side-clone
   (`<repo-root>/puzzles/2014/images/liber_primus_pages/`) that **no longer exists on disk** —
   the gitignore/side-clone artefact trap. These two carriers are now restored with archive
   provenance, and the archived copies independently CONFIRM armada20's extractions from a
   different byte-lineage (the wiki files differ in container bytes from the side-clone's —
   different sha, same pixels, same recoverable payload — so the extractions do not depend on
   one mirror's bytes). Also recovered: Book-cover (= our dl_1033.jpg, pixel-match 1.3 mean
   abs diff), Book-page-1/2/4, Page3-book (small 700px wiki uploads), and the community's
   OutguessfromLiberPrimusPage6 screenshot. Hashes in wayback-log.md.

4. **CLEAN on the task's alternate-format hypothesis:** no PDF/PS/DjVu/SVG/TIFF/vector source
   of any LP page exists in any capture; no resolution above 2400x3600 anywhere; every
   full-size copy is the same 2400x3600 JPEG family. This upgrades R36-O2's "not searched"
   to a searched-and-empty over the Wayback surface (coverage: the CDX result sets in `cdx/`,
   power: byte-level digest comparison).

5. **Honest negatives on the remaining named targets:**
   - Onion gateways (`auqgnxjtvdbll3pv`/`cu343l33nqaekrnw`/`ky2khlqdf7qdznac` × onion.to/
     onion.cab/onion.link/tor2web.org): no onion content was ever archived — 302s, 401, a
     gateway-down page, or zero rows.
   - `845145127.com`: every 2013-era capture is a 404; 2015+ is a squatter.
   - imgur targets incl. the Discord-cited eAVCeeC/D5eBa/EKoUaoV: solver diagrams, not sources.
   - Pastebins (18 repo-referenced IDs): 7 archived (earliest 2015-07-28), **11 have zero
     Wayback coverage** — all solver chatter; archive.ph is the only remaining place to look
     for the 11, deliberately not chased (out of lane scope, nothing suggests key material).
   - `1399181864285.png` (3.4 MB PNG from the dump week): community artwork collage, recorded
     with hash, not a source.

## Follow-ons for the coordinator
- Import `fetched/56_2022.jpg` + `57_2022.jpg` into `data/relikd/` (or record where the rig
  wants dump-page masters) — the corpus is currently 56/58.
- The other 13 Jan-2014 carriers (`lp_page_00..16` minus the 4 recovered/held) are likely in
  the surviving community GitHub mirrors (the deleted side-clone's upstream) and partially on
  the wikia CDN; a 30-minute fetch pass would restore the full first-release generation.
- X1 should spot-check: re-run `outguess -r` on `fetched/jan14_p5.jpg` and `cmp` against
  `armada20/og_out/lp_page_03_715a8ff0_kNONE.bin` (one command, reproduces finding 3).
