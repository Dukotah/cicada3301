# O2 RESULTS - source-artifact hunt: NOT-FOUND (search space below; not exhaustive)
Verdict: no PDF/PS/DjVu/SVG/TIFF/PNG source, no mirror with producer metadata, no named original rune face surfaced. 0 new artifacts. Per PREREG, the covered search space is the result.

## Search space covered (WebSearch standard + WebFetch, 2026-10-30; see search_log.json)
- Generic and Cicada-specific searches for vector/high-res/alt-format LP files; rune-font searches; EXIF/ICC searches; reddit/font/LaTeX authoring searches; GitHub repos krisyotam, iBotPeaches (partial listing), scream314/cicada_tools only as search hits.
- Facts gathered: fan font Primus (https://fontspace.com/xxxx-f50214, 2020); reprint disclaims metadata (https://bookscloud.io/products/the-complete-liber-primus-paperback); KYM says 58-page image dump May 2014 (https://knowyourmeme.com/memes/cicada-3301); CTAN allrunes (https://www.ctan.net/obsolete/help/Catalogue/entries/allrunes.html).

## NOT covered (blockers - do not claim searched-and-empty)
- web.archive.org is refused by WebFetch and CDX on archive.org gave 404: Wayback snapshots of onion mirrors/uncovering-cicada/reddit 2014 were NOT inspected.
- GitHub tree API and krisyotam page 404 via fetch; GitHub code search by SHA-256 not possible (needs auth/gh); fandom wiki 402; reddit not fetched; mirror JPEGs not downloaded so EXIF/XMP diff vs R18-L1 not done.
- Generic web search does not index file bytes, so absence of hits is weak evidence.

## Do not repeat
Generic "Liber primus pdf" web searches (return Latin textbooks); searching font sites for the original face (only fan fonts exist, 2020+).

## Next for a lane with network+git/gh (coordinator decision)
1. Wayback CDX for onion7/uncovering-cicada/reddit 2014 via a tool that allows web.archive.org.
2. `gh search code` on the 58 SHA-256s; clone krisyotam to resolve 61/75 vs 58 and inspect non-JPG files.
3. exiftool/identify on each mirror (neuroretransmit, relikd, Wulfic, iddqd) vs R18-L1 fingerprint.

## Coordinator addendum (2026-10-30, after the lane closed)

The two checks the lane could not reach were run by the coordinator with `gh` and `curl`:
- **GitHub code search** (`gh search code "liber primus" --extension pdf|ps`): 0 results. `krisyotam/cicada3301` is 404 (gone/private).
  Recursive tree scans of the four largest surviving community repos (`henkman/liberprimus` 41 MB, `localavaster/cadrypt`
  45 MB, `ralphatobe/cicada-3301` 12 MB, `Taiiwo/cicada`) for pdf/ps/eps/svg/tif/png/djvu/otf/ttf/tex: only app icons,
  two fan fonts (robotomono, seguisym) and ralphatobe's derived PNG crops. No alternate-format source.
- **Wayback CDX** for uncovering-cicada.wikia.com, cicada3301.org, cicadasolvers.com, reddit.com/r/cicada (2014–2015,
  mimetype pdf): the Internet Archive returned "Temporarily Offline" at query time → **still unsearched**, not empty.
Verdict stands: NOT-FOUND; the Wayback leg remains open for a future searcher.
