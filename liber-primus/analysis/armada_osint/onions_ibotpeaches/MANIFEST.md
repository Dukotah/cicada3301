# iBotPeaches/cicada_3301 `/onions/` full harvest (2026-07-28, lane: external)

Complete pull of the archived-onion HTML/image corpus we previously held ZERO raw HTML for.
Source: `raw.githubusercontent.com/iBotPeaches/cicada_3301/master/onions/` (enumerated via GitHub tree API).
34 small/medium files pulled verbatim (`onions__*`), plus derived artifacts below.

## Onion inventory (community naming, from per-dir READMEs)
| dir | puzzle | states held | note |
|-----|--------|-------------|------|
| 845145127.com | 2012 first site | post, post2 | post = GPS coords; **post2 = whitespace stego** |
| sq6wmgv2zcsrix6t.onion | 2012 "RSA/MIDI" | post | PGP "email us a number" gate |
| auqgnxjtvdbll3pv.onion | 2014 Onion 1 | post | "For Every Thing That Lives Is Holy" + 1033.jpg |
| cu343l33nqaekrnw.onion | 2014 Onion 2 | pre | `<!--761-->` + 256B RSA hex |
| fv7lyucmeozzd5j4.onion | 2014 Onion 3 | pre | `<!--1033-->` + 256B RSA hex |
| avowyfgl5lkzfj3n.onion | 2014 Onion 4 | pre, post | pre `<!--3301-->`+256B hex+`Port 5243`; post = 5MB gzip'd JPEG |
| q4utgdi2n4m4uim5.onion | 2014 Onion 5 | pre, post | pre = onion5 PGP/GIMP-JPEG hex (already held) |
| ut3qtzbrvs7dtvzp.onion | 2014 Onion 6 | pre, post, post2 | pre 8.6MB=embedded JPEG hex; post=magic-squares form; post2=107/167/229 |
| ky2khlqdf7qdznac.onion | 2014 Onion 7 | post | the 58-image LP2 index (0.jpg..57.jpg) |

## GENUINELY NEW to our corpus (not previously in repo — grep-verified)
1. **`DECODED_845145127_post2.txt`** — the 2012 countdown page's whitespace (tab/space) channel,
   fully recovered here for the first time locally. Mapping: **tab=0, space=1, MSB-first, 8-bit**.
   Decodes to a complete PGP SIGNED MESSAGE whose body is `162667212858` + a long digit block,
   signed by keyid `181F01E57A35090F` (`iQIcBAEBAgAGBQJPDRkv...`). This is a *known-solved* 2012
   artifact (the poster/coordinate stage) but was absent from our local set. NEW-TO-CORPUS, not a break.
2. **`rsahex_cu343_761.bin` / `rsahex_fv7ly_1033.bin` / `rsahex_avowy_3301.bin`** — the three
   256-byte (2048-bit) RSA-signed message hex strings embedded in the 2014 onion 2/3/4 `pre` pages.
   None of these hex strings appeared anywhere in the repo before. Same 256B/high-entropy class as
   `pp49_51/canon_256.bin` ("String 4"). Characterized below.
3. **`avowy_post_gzip_inner_2400x3600.jpg`** — the avowyfgl `post` 5MB hex, un-hex'd + gunzip'd,
   yields a 400-DPI 2400x3600 baseline JPEG rune-page render. SHA1 `7e5296ad...` is **NOT** in
   `stego/provenance.json` (a render variant we hadn't hashed).

## Characterization / verdicts (all bounded probes this session)
- **Three 256B hex blobs**: entropy 7.12 / 7.13 / 7.28 b/B. Pairwise XOR and XOR-vs-canon_256 give
  no structure (<=3 zero bytes). = independent RSA-signed-message ciphertext/signature blocks, the
  standard 2014 onion payloads. Not additive keys, not related to each other or to canon_256.
- **avowy inner JPEG + OutGuess (default key)**: extracts 58152 bytes at entropy **7.997 b/B** =
  the documented OutGuess **default-key keystream false-positive** (per ELIMINATION-LEDGER). NULL.
- **Header/port quirk (item 6)**: only `avowyfgl.../pre` carries `<address>Apache Server at 127.0.0.1
  Port 5243</address>`; the others have no server-status footer. Single data point, not a channel.
- **Big files**: ut3qtz `pre` (8.6MB) = `<!--761-->` + hex of a raw JFIF JPEG (embedded image).
  q4utgdi `pre` (13.5MB) = the onion5 PGP-signed GIMP-JPEG hex (ALREADY HELD/characterized).

## folly/wisdom
Not present in /tmp this session; local copies were byte-identical random (SEALED). No non-identical
variant surfaced in the iBotPeaches corpus (folly/wisdom are infotomb.com ISO /tmp files, not onion HTML).

## NET
No plaintext break, no external key. All decoded content resolves to already-known 2012/2014 puzzle
stages or the known OutGuess keystream artifact. Value = we now hold the raw onion HTML corpus locally
(closes "we hold ZERO raw onion HTML" gap) + first local copy of the 845145127 whitespace payload +
the three 256B RSA hex blobs for any future cross-tests.
