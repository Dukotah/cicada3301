# GitHub / OSINT Sweep — Overlooked External Artifacts (2026-07-27)

Trigger: "useful info floating around from old pictures of downed onion sites." Three parallel
web/GitHub sweeps (repo catalogue / dead-onion captures / forensic-writeup mining). Purpose:
find EXTERNAL material we never pulled — our internal cryptanalysis verdict says the LP2 runes are
OTP-class and the key is external by construction, so the only live frontier is Cicada's own
un-examined corpus of images and onion pages.

## Confirmed local gap
- We hold: relikd rune-page JPEGs, PGP corpus, the onion5 hex (proven GIMP JPEG), pp49-51 payload
  (canon_256 = "String 4", ends 0x50 — matches community `...C6B424BD50`, good consistency check).
- We hold ZERO raw onion HTML. Our text references only 2 onion addresses
  (`ky2khlqdf7qdznac`, `xsxnaksict6egxkq`) out of 8+ archived by the community.

## Best mirrors (raw, downloadable today)
- **iBotPeaches/cicada_3301 `/onions/`** — per-address `pre/`+`post/` raw HTML of 8 v2 onions
  (the before/after "site changed" states). Unique: preserves onion edit history + HTTP header quirks.
- **Internet Archive per-onion dumps** — `archive.org/details/<onion>` downloadable raw payloads for
  auqgnxjtvdbll3pv / cu343l33nqaekrnw / fv7lyucmeozzd5j4 / avowyfgl5lkzfj3n / ky2khlqdf7qdznac, etc.
- scream314 (cleanest machine-readable), The-Complete-Cicada3301-Archive (⭐101, maintained to Nov 2025),
  krisyotam `original-onion7/` (61 raw onion7 files incl. source HTML), clevcode.org, Tumbleson 4-part.
- Wayback/tor2web (.onion.to/.city) = DEAD END: only saved the gateway "temporarily not available" page.

## GENUINELY OVERLOOKED (not in our local set, not in our elimination ledger)
Ranked by value to the EXTERNAL-KEY question, not just novelty.

1. **5×5-rune JPG, onion3 v3 (~328 KB) — suspected password-protected OutGuess.**
   Community reports VISIBLE RGB runic modification under contrast = provable hidden data, but the
   key was never found. Password space they tried was narrow (gematria 131/151/199/481). Our stego
   verdict only ever cleared the LP *rune pages* — this specific onion image was never in scope.
   Strongest "there is hidden data we never extracted" lead. Broaden key search: magic-square word-grid
   (shadows/aethereal/void/carnal/obscura/mobius/analog/mournful/cabal), LP phrases, the never-found
   3301-valued phrase.
2. **`2.jpg` — OutGuess seed 38370, 7,524-byte blob, no magic header.** Extracted-but-unidentified
   payload. Re-run format/entropy detection + standard Cicada transforms (0xFF bit-flip, bzip2, RSA-OAEP).
3. **The two ~5 MB `.htaccess` hex blobs** — `avowyfgl5lkzfj3n.onion` (5,064,619 B) and
   `fv7lyucmeozzd5j4.onion` (5,577,967 B). Raw onion payloads hidden under a dotfile name so most
   mirrors skip them. `archive.org/download/<onion>/.htaccess`. Decode to gzip'd embedded JPEGs — likely
   image-chain not key, but we never verified. Plus `cu343.../761.hex` (3.6 MB → 3 embedded JPEGs).
4. **ISO `/tmp` files `folly` and `wisdom`** — real files, identical content, never decoded
   (infotomb.com/bjzdi). Cheap byte-for-byte re-examination, untouched.
5. **`4gq25.jpg` (5 Jan 2016, disputed authenticity)** — OutGuess payload preserved; independent
   extraction worthwhile despite the dispute.
6. **HTTP/server-status anomalies (iBotPeaches HTML):** per-onion ports 5240/5241/5242/5243; mock
   `server-status` uptime "1 days 0 hours 33 minutes 14 seconds" -> 1033; leaked host
   li676-224.members.linode.com / 106.186.123.224 / port 5243; `<head>`/`</head>` malformation varying
   per onion (theorized to bind the onions together). Never resolved as a channel.
7. **Whitespace re-audit of the ENTIRE PGP corpus.** Wiki flags the tab/space channel as "never fully
   utilized." Previously blocked for us ("no local source"); scream314 now has the signed bodies with
   trailing whitespace intact -> systematically re-extract from every message.
8. **Unconfirmed 2012 "enjoyed the ride / 7 images" endpoint.** Neither ClevCode nor Tumbleson reached
   it (both lost the trail at the RSA/email stage); only the (fetch-blocked) Fandom wiki claims it.
   Verify-or-debunk lead.
9. **Missing Columbus GA 2013 Shamir-share onion** (6 of 7 poster onions recovered; 7th unknown).

## ALREADY NULL IN OUR LEDGER — do NOT re-chase as keys
- Cookies `167=6941...`, `761=7bc1...` — tested as keys, ARMADA #9, best -6.89. (BUT never XOR'd against
  the four hex strings — that specific cross is untried; low priority.)
- 2012 P.S. digit string (`vjuNp.jpg`) — tested null. The rotate-90 -> "3301" / matrix hypothesis was
  never executed, but P/Q factorization is done; completeness-only.
- Telnet missing-prime gaps (71-1229; space-flagged 29/31, 3257/3259) — covered by prime-gap sweep -6.81.
- Mayan rotation key — tested null, autocorrelation-excluded.
- pp49-51 hex ("String 4") — this IS our Campaign VII canon_256, fully characterized (high-entropy
  binary, not prime, not a runic key, both signs/variants swept null).
- onion5 q4utgdi hex — we have it; it's the GIMP JPEG.
- Stego on the LP rune pages — real OutGuess built + validated, null (does NOT cover item 1 above).

## Honest read
Most raw onion payloads decode to the puzzle-chain images (lower odds of being THE external key).
The higher-value items are the ones with PROVABLE-but-unextracted hidden data (item 1) or
extracted-but-unidentified blobs (items 2, 4, 5) — those are true loose ends we never held locally.
None overturns the OTP verdict on the runes; they are candidate EXTERNAL material, which is exactly
the only class our verdict left open.

---

## Session extraction results (2026-07-27) — what we actually pulled & ran

The sweep above is the *plan*; below is the *outcome* after downloading the mirrors and
running the extraction/key-test rig (`armada_osint/`, scripts committed, 79 MB of raw dumps
gitignored — reproduce via the pointers above). **Net: no new break. Extractions reproduced
already-known Cicada payloads, and the broadened key sweep is null.** Recorded here so no one
re-chases these as open.

| # | Lead | What we got | Verdict |
|---|------|-------------|---------|
| T1 | onion3 5×5-rune JPG (item 1, "strongest lead") | OutGuess extract = **known 2013 RSA message** ("Welcome. Good luck. 3301. `e = 65537, n = 75579…`") | **Known payload reproduced**, not new hidden data. The "provable-but-unextracted" claim resolves to the standard message. |
| T2 | `2.jpg` OutGuess blob (seed 38370, 7,524 B) | High-entropy `data`, no magic header; format/entropy/standard-transform detection = nothing | **Unidentified blob, still open** (low prior — looks like keystream/noise) |
| T3 | `.htaccess` / folly-wisdom class blob | High-entropy `data`, no magic header | **Unidentified blob, still open** (low prior) |
| T5 | `4gq25.jpg` (2016, disputed) OutGuess | **Known 2016 PGP message** ("The path lies empty; epiphany seeks the devoted… Verify OpenPGP 7A35090F") | **Known payload reproduced** — independent confirmation, not new |
| T6 | Whitespace (tab/space) channel across PGP corpus | Run-lengths only re-encode already-known numbers (2013 riddle `5,3,2,2,3,5` reproduced; rest = `1,1,1…` noise) | **Null** — no unused whitespace payload |
| key sweep | 60 broadened OutGuess passwords (gematria words, LP phrases, primes — `keys.txt`) vs the onion images | Every key → capacity-length entropy-≈8 garbage or empty (`keytest_results.txt`); seed scan shows the uniform OutGuess **default-key keystream** (`seed_scan.txt`), i.e. the known false-positive artifact | **Null** — password-protected-OutGuess hypothesis unsupported at these keys |

**Still genuinely open after this session** (candidate *external* material only — none overturns the OTP verdict on the runes): the two unidentified high-entropy blobs T2/T3, the ranked items 6–9 in the sweep (per-onion HTTP/port anomalies, full-corpus whitespace re-audit at scale, the unconfirmed 2012 "7 images" endpoint, the missing 2013 Columbus GA Shamir-share onion). These are documentation/OSINT loose ends, not cryptographic openings.

---

## Red-rune (color-layer) follow-up — the T1 residue, closed (`armada_osint/t1_chroma/` + `armada_osint/redrune/`)

The armada's T1 "visible RGB modification, key never found" was chased to a conclusion.

- **It is genuine saturated RED ink** (~#C80000, RGB ≈ 187,2,3), verified not a JPEG artifact
  (signal on the ink strokes not high-gradient edges; red channel offset while G≈B). Corrected the
  armada mis-framing: the three files (107/167/229) are full **LP2 pages** (drop-cap ᚠ + shrouded-figure
  art), not magic-square cells, and 167 also carries red (a central ornament) → **not** a clean control.
- **It is a KNOWN LP feature already in our corpus** — 24 relikd pages carry real red. So this is not a
  discovery of hidden pixels. The genuinely-untested angle: our rig reads a **colorblind** transliteration,
  so the red runes as a *selection* were never fed to cryptanalysis in 18 campaigns.
- **Extracted + tested** (`redrune/extract.py`, reusing the verified `analysis/stones/` alignment —
  relikd line-order == krisyotam line-order, 594 identical lines): **187 red runes across 14/55 pages**.
  **Verdict = DECORATION, cryptographically null.** 12/14 red pages are contiguous opening/section-initial
  runs = the page's own literal opening word (e.g. canon p0 opens S·HEOGMIAF·SYENGC → red = HEOGMIAFSYENGC,
  leading S = the height-excluded drop-cap). Keytest: best −7.13 vs English baseline −4.0 / threshold −5.2 /
  noise floor −7.49; direct −7.76, atbash −7.65, red-as-key-over-black −7.47; 0/~30 configs beat threshold.

**Net:** the color channel — the last un-analyzed representation of the canonical ciphertext — is now
extracted and null. An honest, novel negative that *tightens* the OTP verdict rather than a loose end.
