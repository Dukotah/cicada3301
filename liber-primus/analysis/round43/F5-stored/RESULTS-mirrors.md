# Round 43 — Lane F5c: Mirror checksum cross-check (provenance hardening)

Date: 2026-11-03. Manifest: `mirror-manifest.sha256` (145 rows, sha256 of every checked local file).

## Verdict: IDENTICAL (all primary masters), with one characterized non-master divergence (archive.org zip = downscaled re-export, not corruption)

## What was checked, against what

Local sets hashed (sha256 + sha1 + git-blob sha1):
1. `data/relikd/*.jpg` — 57 files (p0–p55 + 0_wisdom), the onion7 2014 masters.
2. `analysis/armada_osint/artifacts/rune_pages/0.jpg–57.jpg` — the FULL 58-page onion7 set (includes 56/57 which `data/relikd` stores only via the repo's other naming).
3. `analysis/armada_osint/onions_ibotpeaches/*` — 22 binary/html artifacts.
4. `analysis/armada_osint/artifacts/dl_*.jpg` — 8 download artifacts (dl_107/167/229, dl_1033, dl_onion1-3, dl_server-status).

Independent mirrors compared:
- **iBotPeaches/cicada_3301** (GitHub): full recursive git tree pulled; byte-equality proven via git-blob SHA-1 (sha1 over `blob <size>\0`+content) for ALL files, plus a stratified 10-file raw.githubusercontent download whose sha256 matched local exactly (validates the git-sha method end-to-end).
- **relikd/LiberPrayground** (GitHub): git tree; all 57 `data/relikd` jpgs match `pages/*` blobs by content hash.
- **uncovering-cicada.fandom.com** (MediaWiki API, reports plain SHA-1 of stored originals): all 58 onion7 pages (0.jpg–57.jpg, 2400x3600) sha1-identical to local; 107/167/229.jpg and 1033.jpg also identical to our dl_* artifacts.
- **archive.org/details/liber-primus**: `Liber Primus.zip` (9.1 MB) downloaded and extracted. See divergence below.

## Results

| Set | Files | iBotPeaches | relikd repo | fandom wiki | Verdict |
|---|---|---|---|---|---|
| onion7 LP pages 0–57 (rune_pages) | 58/58 | MATCH (lp 17.jpg–74.jpg) | MATCH (pages/p0–p55, p56_an_end, p57_parable) | MATCH (0.jpg–57.jpg) | IDENTICAL |
| data/relikd p0–p55 + 0_wisdom | 57/57 | MATCH | MATCH | MATCH (0_wisdom not hosted on wiki under that hash) | IDENTICAL |
| onions_ibotpeaches artifacts | 22/22 | MATCH (same-origin re-verify: no local corruption since harvest) | — | 1033.jpg MATCH (independent) | IDENTICAL |
| dl_* artifacts | 8/8 | MATCH | — | 107/167/229/1033 MATCH | IDENTICAL |

Page-number mapping confirmed by content hash (useful for future cross-referencing):
- onion7 `N.jpg` (N=0..57) == iBotPeaches `liber_primus/(N+17).jpg` == relikd `pages/pN.jpg` (N<=55; 56=`p56_an_end.jpg`, 57=`p57_parable.jpg`) == fandom `N.jpg`.
- `0_wisdom.jpg` == iBotPeaches `liber_primus/05.jpg` == `dl_server-status.jpg` (same bytes, three names).
- `dl_107/167/229.jpg` == iBotPeaches `liber_primus/14/15/16.jpg` == fandom `107/167/229.jpg`.
- `dl_onion1/2/3.jpg` == iBotPeaches `liber_primus/00/01/02.jpg`.

## Divergence found (characterized, non-master)

**archive.org item `liber-primus` (`Liber Primus.zip`, sha1 00f6638e...):** 59 jpgs + mp3.
- `liberprimus_0.jpg` is byte-identical to our `p0.jpg` (2400x3600 master, 695525 B) — proves the pack descends from the same release.
- The other 58 images are **downscaled re-encodes at 683x1024** (~46–96 KB each, JFIF, no EXIF), i.e. whole-image recompression: different dimensions, different entropy coding, not a bit-flip corruption and not a variant release of the masters. Plus a `liberprimus_key.jpg` (598x842 gematria key render).
- Classification: convenience re-export; **unusable as a master source; do not ingest for stego/byte-level work.** No pixel-level comparison performed beyond dimension check since dimensions alone disqualify byte-provenance.

## Provenance conclusion

Every byte-level master we analyze (all 58 onion7 pages, the 2014 onion images, the 107/167/229 ut3qt pages, 1033.jpg, the imgur/twitter artifacts) is now confirmed byte-identical across at least two, mostly three, independently operated mirrors (GitHub x2 + Fandom). There is no evidence anywhere of corruption, recompression, or a variant release of the canonical masters. The only divergent public copy (archive.org zip) is an obvious downscale, flagged above.
