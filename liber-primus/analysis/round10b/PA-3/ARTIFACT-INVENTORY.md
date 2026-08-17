# Lane PA-3 — The Cicada 3301 Artifact Inventory (2012–2017) and the LP2 Input-Gap List

**No attack was run in this lane.** This is the instrument for testing the owner's thesis
("an overlooked variable was released back when the puzzle came out"). It reconstructs the
complete list of things Cicada 3301 *emitted*, and for each one answers two independent
questions:

1. **HELD?** — does this repo have the bytes locally?
2. **FED?** — has it ever been an *input to an LP2 decode attempt* (key / keystream / crib /
   plaintext hypothesis), as opposed to merely being *read about* or *stego-scanned*?

Those are different axes and the repo systematically conflates them. Almost everything has
been *read*; a very small subset has been *fed*.

Primary source for the narrative reconstruction: the scream314 year-by-year archive already
mirrored locally at `analysis/armada_osint/artifacts/raw/{2012,2013,2014,2015,2016,2017}.md`
(149 KB, verbatim), cross-checked against the Uncovering Cicada wiki via the MediaWiki API
(`/api.php?action=parse&page=...` — the normal Fandom HTML path returns HTTP 402 to fetchers,
the API does not; this is a reusable access route).

---

## A. The headline finding

The repo's key-hunting has been almost entirely **literary**: ~112 named natural-language
keytexts (Mabinogion, Self-Reliance, Agrippa, Book of the Law, King in Yellow, then Campaigns
XII/XIII/XVIII adding 15 + 82 + 88 more), plus Cicada's own **English prose** (armada20 #3:
the PGP message bodies), plus **numeric** streams (primes, totients, pi/e/phi, PRNG seeds,
magic squares, the AN-END hash, the 2012 P.S. digits, the 2013 cookies).

**The one class that was never fed is the class Cicada actually used to deliver keystreams:
her own published high-entropy binary files.**

In 2013 Cicada shipped a 130 MB ISO ("Cicada OS") whose `DATA/` directory contained
`_560.00` (3,992,970 B), `560.17` (1,183,811 B) and `560.13`. Those files were **explicitly
designed as XOR pads by the author**: `telnet hint` output XOR `_560.00` → the "forest/trees"
message; the phone-poster payloads (`Dataset:13 / Offset:12821`, `Dataset:17 / Offset:77977`)
XOR `560.13` / `560.17` → the per-location onion addresses. That is a *published, indexed,
offset-addressed pad library*, authored by the same person, one year before Liber Primus, on
a boot screen that literally says **"The key is all around you."**

- This repo does **not hold** those files.
- No script in `analysis/` references `560` at all (grep-verified; the only `560` hit is a
  Whirlpool test vector in `pp49_51/whirlpool_ref.py`).
- The community XOR'd them **against each other as bytes**, hunting file signatures
  (wiki: *XOR all the things*) — never as a **mod-29 additive keystream against the LP2 rune
  indices**, which is the operation the LP cipher family actually uses.

Same status for `assets/2013/twitter.txt` (138 KB — the full @1231507051321 hex tweet stream,
itself one half of a published XOR pair), `usr_local_bin/prime_echo` (12 KB ELF),
`SPLASH.RLE` / the `3301.img` filesystem inside the ISO, and the three 2014 onion 256-byte
RSA hex blobs (those three *are* now held, characterized as high-entropy, but never fed).

This is a genuine, period-correct, hand-scale, never-tried input class. It is precisely
"a variable released when the puzzle came out."

---

## B. Inventory — 2012 chain

| # | Artifact | HELD? | FED to LP2? |
|---|----------|-------|-------------|
| 1 | `1CcV1.jpg` original 4chan image (509×503, Futura) | no (payload text only, in `raw/2012.md`) | no (image); its ROT-4 tail string was seen in armada20 #12 EXIF/append forensics |
| 2 | `m9sYK.jpg` "WHOOOPS decoys" | yes (`onions__imgur.com__m9sYK.jpeg`) | no |
| 3 | OutGuess payload of #1: book code (76 pairs) + reddit URL | yes (text) | no — the 76-number sequence has never been used as a keystream |
| 4 | `/r/a2e7j6ic78h0j` subreddit: header image, `KXLOP.jpg` "Welcome", `8D7hN.jpg` "Problems?" (Grail autostereogram) | yes (all 3 images) | no |
| 5 | The subreddit scrambled-text block + its unscramble key `10,2,14,7,19,6,18,12,7,8,17,0,19,7,14,18,14,19,13,0,1,2,0` (from `a2e7j6ic78h0j7eiejd0120` hex) | yes (text) | **partly** — period-13 prefix `[10,2,14,7,19,6,18,12,7,8,17,0,19]` fed in `campaign18_skip/armada2/numeric2_skip.py` §3 |
| 6 | Mabinogion "King Arthur at Caerlleon" plaintext block | yes | **yes** (running key, all offsets/signs/Atbash, rigid + skip-aware) |
| 7 | Phone `(214) 390-9608` recording ("three prime numbers… multiply") | text only | no |
| 8 | `845145127.com` cicada.jpg + countdown + its 2 OutGuess payloads | yes (`onions__845145127.com__post__cicada.jpg`) | no |
| 9 | The 14 GPS coordinates | yes (text) | no — never tried as a numeric keystream |
| 10 | Physical fliers/QR posters (Warsaw `BxVYf`, Paris `XdNGo`, Miami `cAuUz`, Arkansas/Sydney `sppR9`) | **no** (imgur photos not pulled) | no |
| 11 | The 10 QR-target JPEGs `162667212858.jpg` … `963846244281.jpg` + their 2 book-code payloads | no (images); payload text yes | no |
| 12 | `845145127.com` whitespace-stego page (tab=0/space=1) | **yes** — `onions_ibotpeaches/DECODED_845145127_post2.txt` (first local copy, 2026-07-28) | no |
| 13 | Agrippa (Gibson) book-code target → `sq6wmgv2zcsrix6t.onion` | yes | **yes** (keytext, dead) |
| 14 | `sq6wmgv2zcsrix6t.onion` HTML + email gate | yes | no |
| 15 | `1853143003544.tk` / `33091839349.tk`, `NHYLD.jpg` Lady of Shalott + payload | no image; text yes | no |
| 16 | `hkdgl.png` → Blake, *Marriage of Heaven and Hell* book code | yes (image + 3 MHH texts in `armada20/mhh_*.txt`) | **yes** (armada20 #4, refuted −6.104) |
| 17 | Per-solver RSA challenges (Crypt::RSA, low modulus) | text sample only | n/a (per-solver) |
| 18 | The **MIDI puzzle** (`habitres.midi`, infotomb.com/oq17i) + note↔letter table + the per-solver word lists ("garden ball house cat shore back head galon") | **no** — no `.mid` file anywhere in repo | **no** |
| 19 | `vjuNp.jpg` Valēte! final message + P.S. 130-digit number + asterisk/prime spacing | payload text yes | **yes** (`armada20/psnum_key.txt`, `test9_psnum.json`; Round-4 Gate-1 kill) |
| 20 | The leaked recruitment email (pastebin RmqxWcnB) | text | no |
| 21 | 2012-04-18 "Necrome" denial | yes (`armada20/pgp_2012-04-necrome-denial.txt`) | **yes** (armada20 #3) |

## C. Inventory — 2013 chain

| # | Artifact | HELD? | FED to LP2? |
|---|----------|-------|-------------|
| 22 | `232.jpg` / `gqvvmk.jpg` 4chan image + its book-code payload (Crowley riddle) | **no** image; payload text yes | no |
| 23 | *Liber AL vel Legis* (Book of the Law) | yes (`data/keys/book_of_the_law.txt`) | **yes** (keytext, dead) |
| 24 | **`3301.iso` "Cicada OS"** (130 MB, Tiny Core; Dropbox `r7sgeb5dtmzj14s`; also `archive.org/details/3301.iso`) | **NO** | **NO** |
| 24a | └ `DATA/_560.00` (3,992,970 B) — author's own XOR pad | **NO** | **NO** |
| 24b | └ `DATA/560.17` (1,183,811 B) — pad, offset-addressed by phone posters | **NO** | **NO** |
| 24c | └ `DATA/560.13` — pad, offset-addressed by phone posters | **NO** | **NO** |
| 24d | └ `usr_local_bin/prime_echo` (12,248 B ELF) + `usr_local_bin/cicada` (106 B) | **NO** | **NO** |
| 24e | └ `tmp/folly`, `tmp/wisdom` (3,368 B, identical) | yes (`armada_osint/artifacts/folly.bin`, `wisdom.bin`) | **no** — hash-compared to AN-END only; never used as keystream |
| 24f | └ `SPLASH.RLE`, `3301.img` filesystem, boot prime sequence (pauses at 1033, 3301) | **NO** | **NO** |
| 25 | Boot-screen text `@1231507051321 / The key is all around you.` | text | no |
| 26 | `761.mp3` "The Instar Emergence" (4,010,732 B) + ID3 + hidden parable poem + parable number 1,595,277,641 | **yes** (`puzzles/2013/artifacts/761_The-Instar-Emergence.mp3`) | **partly** — the *poem text* and *1595277641 as a PRNG seed* were fed (`armada20/prng_attack.py`, `campaign18_skip/armada/numeric_skip.py`); the **4 MB of MP3 bytes as a mod-29 keystream: never** |
| 27 | **`twitter.txt`** — the full @1231507051321 hex tweet stream (~138 KB, 65 B/tweet, Jan 6–8 2013) | **NO** | **NO** |
| 28 | The reactivation tweet `Offset: 0, Skip: 0, Col: 65, Line: 988` | text | no |
| 29 | `gematria-primus.jpg` (the 29-rune table as published) + its whitespace-stego OutGuess payload | extracted payload only (`armada20/og_out/06-gematria-primus_*.bin`) | table itself = the alphabet (used); alphabet reorderings tested & dead |
| 30 | `emiwp4muu2ktwknf.onion` — telnet shell: ASCII-art banner, `hello`, `hint`/`clue` hex blocks, `primes` list with the **missing-primes gap 73–1223**, `count`, `[number]` factorizer | text | **partly** — missing-primes fed as additive key (Round-4 Gate-1 KILL); the ASCII banner, the `hint` hex block, and the "forest.raw" undecoded outputs: **never** |
| 31 | `xsxnaksict6egxkq.onion` (v1/v2.5) + the **ICMP ping-payload gzip channel** | text | no |
| 32 | `pklmx2eeh6fjt7zf.onion` "standby for coordinates" | text | no |
| 33 | The 7 physical posters (Dallas/Okinawa/Moscow/Little Rock/Annapolis/Portland/Columbus GA): phone numbers ending 3301/1033, access codes (JD:3789, YF:1032, CR:1311, LM:7167, PX:4347, GH:1723, NR:2911), Dataset/Offset/Data triplets | text table yes; poster photos **no** | **no** |
| 34 | The 6 recovered SSSS shares (`02-41cc…`, `03-7678…`, `05-fcd8…`, `07-f3ad…`, `08-b970…`, `09-82a9…`) + the 7th (Columbus GA) never recovered | text | **no** — never fed as keystream; ledger notes the missing share is deterministically redundant |
| 35 | `p7amjopgric7dfdi.onion` — the 19 test questions (statements, free-text, the lake/reflection question) | text | **no** |
| 36 | The two cookies `167=6941f7…`, `761=7bc1e7…` | yes (`armada20/key_cookie167.txt`, `key_cookie761.txt`) | **yes** (armada20 #7/#9, −6.89; Round-4 Gate-1 kill) |
| 37 | The TCP-server protocol spec email (RAND/QUINE/BASE29/CODE/**KOAN**/DH/NEXT/GOODBYE) incl. the mountain-koan text | text | **no** |

## D. Inventory — 2014 chain (the Liber Primus release)

| # | Artifact | HELD? | FED to LP2? |
|---|----------|-------|-------------|
| 38 | Tweet 420087183957966849 + `zN4h51m.jpg` + OutGuess (Emerson riddle + 4-level book code) | yes (image ×2 copies) | payload text yes; **image bytes no** |
| 39 | *Self-Reliance* (Emerson) | yes | **yes** (keytext, dead) |
| 40 | Onion 1 `auqgnxjtvdbll3pv` — `index.html` ("For Every Thing That Lives Is Holy") + `1033.jpg` + RSA-encrypted message + e/n | yes (HTML + JPG) | no |
| 41 | Onion 2 `cu343l33nqaekrnw` — `<!--761-->`, the slow-growing 512-char string, `index.html.2` (3.6 MB → 3 JPEGs), the **inter-byte timing intervals** (multiples of 5, recorded by solvers) | HTML yes; `rsahex_cu343_761.bin` yes; **timing series NO** | **no** |
| 42 | The 3 onion JPEGs → OutGuess → XOR → columnar-transposition `GOOD WORK / ULTIMATE TRUTH IS THE ULTIMATE ILLUSION / JOIN US AT…` | text | phrase appears in `data/keys/armada18/cicada_2012_2013_puzzle_texts.txt` → **yes** (armada18 skip-aware sweep) |
| 43 | Onion 3 `fv7lyucmeozzd5j4` — `<!--1033-->` string; the **leaked Apache `server-status` page** (orig 17 KB / new 1.37 MB) with the appended twin-JPEG hex and the **OOB magic-square bytes** | `server-status` (fv7ly) yes in `anend_hunt/fetched/`; the 1.37 MB `_new` **partially** | magic-square numbers **yes** (`armada20/magicsq_keystream.py`, `key_magicsquare_nums.txt`); the server-status *text/uptime/counters* **no** |
| 44 | The 5×5-rune JPG on onion3 v3 (~328 KB) — community reports visible RGB modification = probable password-protected OutGuess, key never found | yes (`armada_osint/artifacts/dl_onion3.jpg` class) | OutGuess key sweep run (60 keys, null); **not a decode input** |
| 45 | The Vigenère key **`welcome pilgrim to the`** and offsets `22,11,9,24,26,10,11,16,19,9,23,25,19,10,13,26,27,11` | text | **yes** (solved-page keys; used as controls) |
| 46 | Onion 4 `avowyfgl5lkzfj3n` — `<!--3301-->` + 256 B hex + `Port 5243`; post state = 5 MB gzip'd 2400×3600 rune render | yes (`rsahex_avowy_3301.bin`, `avowy_post_gzip_inner_2400x3600.jpg`) | **no** (blob characterized, never fed) |
| 47 | Onion 5 `q4utgdi2n4m4uim59133` — `Interconnectedness.mp3` (gematria 772, 277.133 s), the Goya *Portrait of Andrés del Peral* with the hidden Rasputin/number overlay (1033 & 3301 column sums), the Gödel/Escher/Bach book code | portrait yes (`onion5portrait.jpg`); **`Interconnectedness.mp3` NO** | numbers → magic squares (fed); **MP3 bytes never**; GEB never fed as keytext |
| 48 | **OpenPuff v4.00 container** in `Interconnectedness.mp3`, password `33011033` → the three magic squares | squares text yes | squares **yes**; the OpenPuff *carrier* & any second/third-layer container **no** |
| 49 | Onion 6 `ut3qtzbrvs7dtvzp` — 4 JPEGs (10–13), the magic-square submission form, `107.jpg`/`167.jpg`/`229.jpg` | yes (`dl_107/167/229.jpg`) | no |
| 50 | 2014-05-02 `message.txt.asc` pushed to solver hidden services; UA strings `Cicada/33.01 CicaDOS 1.033 E Edition` / `Cic/DOS/ 1.033 S Edition`; prime-count `+` spacing 2,3,5,7,11,13,17,23,29,31,37 | text yes | prime spacing = known numeric family (dead); **UA strings never** |
| 51 | Onion 7 `ky2khlqdf7qdznac` — `index.html` (title `133`, div `331`), thttpd/2.25b 29dec2003, Last-Modified 2014-04-02 08:33:19, 404→`Port 5243`, the malformed `UNKNOWN 400 BaO'[d Request` | yes (`anend_hunt/fetched/stage11__…index.html`, `onions_ibotpeaches/…post__index.html`) | structural analysis yes; **no numeric derivation of these headers ever fed** |
| 52 | **The 58 rune pages `0.jpg`–`57.jpg`** = Liber Primus (LP2) | yes (`armada_osint/artifacts/rune_pages/`, `data/relikd/`, provenance-verified 56/56 SHA1) | this *is* the target |
| 53 | Solved LP pages (intro, A WARNING, koans, parable, AN END) + their keys (DIVINITY, FIRFUMFERENFE, totient/prime shifts) | yes | **yes** (as keys, as plaintext, as skeleton, as controls) |
| 54 | The AN-END page SHA-512 (`36367763…c2a8b4`) | yes (`armada20/key_anend_hash.txt`) | **yes** (bytes mod 29 fed; hash-preimage hunted; archival hunt exhausted) |

## E. Inventory — 2015–2017

| # | Artifact | HELD? | FED to LP2? |
|---|----------|-------|-------------|
| 55 | 2015-07-28 Planned Parenthood denial (spaces 5-3-2-5-7 / `5321257` / `53212330157`) | yes | **yes** (armada20 #3; digit strings in numeric sweeps) |
| 56 | 2016-01-05 tweet 684596461628223488 → `4gq25.jpg` → "The path lies empty… Its words are the map, their meaning is the road, and their numbers are the direction." | yes (image + payload) | **yes** as prose keytext (armada20 #3); the *directive reading* is Round-10's lane |
| 57 | 2017-04-04 signed "Beware false paths" (Version: `CicadaPG v.3301`, Hash: SHA512) | yes (text) | **yes** (PGP corpus) |
| 58 | The PGP key `0x7A35090F` itself (packets, base64, fingerprint) | yes (`armada20/pubkey_packets.json`, `key_fpr_letters.txt`) | **yes** (armada20 #13, refuted) |

---

## F. What "FED" has actually covered (so the gap list is honest)

- **Literary keytexts**: ~112 + 82 + 88 named texts, rigid and skip-tolerant. Dead, and dead
  *by mechanism* per Round 7 / Campaign XVIII.
- **Cicada's English prose**: every PGP body, combined/individual/reversed. Dead (armada20 #3).
- **Numeric**: primes, prime gaps, totients, iterated totient, π/e/φ/√2/ln2, Fibonacci (841
  seeds), Catalan/Lucas/triangular/partition, PRNG (LCG/BBS/MT × 6 Cicada seeds), magic
  squares, AN-END hash bytes, the pp49-51 256-byte payload at all offsets, the 2012 Mayan
  rotation key, the 2012 P.S. digits, the 2013 cookies, missing primes. Dead.
- **Stego**: real OutGuess 0.4 (validated on historical payloads) over every LP2 page → null;
  LSB/DCT/EXIF/append/carve → null.

## G. The gap list — ranked by "key-shapedness"

Ranking criterion: *did the author demonstrably hide keys/payloads inside artifacts of exactly
this type in 2012–2013?* Everything in Tier 1 answers yes.

**Tier 1 — author-authored keystream files (she used these AS PADS herself).**
1. `DATA/_560.00` (4 MB), `DATA/560.17` (1.18 MB), `DATA/560.13` — never held, never fed.
2. `761.mp3` raw bytes (held!) as a mod-29 additive stream at offsets — the author XOR'd this
   exact file against the tweet stream to produce the Gematria Primus.
3. `twitter.txt` — the 2013 hex tweet stream, the other half of that same published XOR pair.
4. `Interconnectedness.mp3` (2014) raw bytes — the OpenPuff carrier; not held.
5. `tmp/folly` / `tmp/wisdom` (3,368 B, held) — the community's canonical "never used" files.
6. `prime_echo` ELF / `cicada` script / `SPLASH.RLE` / `3301.img` — never pulled.

**Tier 2 — published number sequences never used as keystreams.**
7. The 2012 book-code number list (76 pairs) and the two poster book codes.
8. The 14 GPS coordinate digit strings.
9. The 6 SSSS shares (hex) and the 7 poster access codes / Dataset-Offset triplets.
10. The onion-2 **inter-byte timing series** (multiples of 5, recorded by solvers over 23 h) —
    a genuine author-emitted numeric channel, nowhere in this repo.
11. The three 2014 onion 256-byte RSA hex blobs (held, characterized, never fed).

**Tier 3 — published prose never used as a key.**
12. The 2013 telnet KOAN + the TCP-spec text; the ASCII-art banner; the `hint` output.
13. The 19 test questions.
14. The 2012 phone recording wording; the 2013 phone-message wording.
15. The MIDI plaintext ("verygood you have proven to be most dedicated…") + the per-solver
    word lists.
16. Gödel, Escher, Bach (the 2014 book-code source book) as a running key — the 2014 chain's
    own referenced book was never added to the keytext corpus.

**Tier 4 — artifacts not held at all (pull first, then decide).**
17. `1CcV1.jpg`, `232.jpg`/`gqvvmk.jpg` original uploads.
18. The 2012 QR-poster photographs and the 10 QR-target JPEGs.
19. The 1.37 MB `li676-224_server-status_new.txt`.
20. `habitres.midi`.

## H. Access notes for the next agent

- scream314 tree API (gives exact sizes, no clone needed):
  `https://api.github.com/repos/scream314/cicada3301/git/trees/master?recursive=1`
  → `assets/2013/cicados/DATA/_560.00`, `.../560.17`, `assets/2013/twitter.txt`,
  `assets/2013/cicados/usr_local_bin/prime_echo`, `assets/2014/li676-224_server-status_new.txt`.
  (Note `560.13` and the `*.rev` entries are 134-byte symlink blobs in git — resolve them.)
- Full ISO: `https://archive.org/details/3301.iso`.
- Uncovering Cicada wiki is 402 to normal fetchers; use the API:
  `https://uncovering-cicada.fandom.com/api.php?action=parse&page=<Title>&prop=wikitext&format=json`.
  Relevant pages: *Possible hints never used*, *Loose ends*, *XOR all the things*,
  *Liber Primus Ideas and Suggestions*, *Files found in Cicada OS*.
- The community's own "never used" list (wiki) = P.S. number, the two cookies, wisdom/folly,
  missing primes, trailing spaces. **Four of those five are already killed in this repo.**
  The wiki's *XOR all the things* page shows the binary pads were only ever XOR'd
  **byte-against-byte hunting file magic** — never applied as mod-29 rune keystreams.

## I. Caveat the attack lanes must respect

Round 4 (`research/DEAD_ENDS.md`) killed "external cribs as LP2 additive key" on a
*mechanism* argument: any additive key injects ~2.9–3.4% doublets vs the observed 0.66%.
If that argument is taken at face value it kills Tier 1 and Tier 2 sight-unseen. But
Campaign XVIII built the **skip-tolerant beam decoder precisely because the rigid additive
model is the wrong model** under a soft anti-repeat rewrite (rigid misses a *known planted*
key at −7.24; the beam recovers it at −4.15), and then re-ran the literary corpora under it.
The binary-pad class was never in any of those corpora, rigid or skip-aware. So the correct
statement is: **Tier 1/2 are untested under the only decoder that has ever been shown to
survive the doublet filter.** Any lane that runs them must use the Campaign XVIII beam and
must carry the planted-key positive control.
