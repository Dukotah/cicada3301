# REPORT-A.md — Lane A: primary artifacts

Compiled 2026-08-20. Companions: `GAPS-A.md` (what is still missing), `CONFLICTS-A.md`
(where sources disagree), `SIGNATURES.json` and `SIGNATURE-TIMELINE.json` (the data),
`TRAILING-DATA.json` (post-EOI scan), `MANIFEST.json` (per-file provenance),
`PROGRESS.md` (state for the next operator).

Lane A's remit was `corpus/GAPS.md` **G-01** (the primary puzzle artifacts, which did not
exist in this repository) and **G-02** (no record of which PGP signatures verify), with
**G-09** (signature timestamps as a dataset) following from G-02.

Every number below was measured on this machine from bytes on this disk. Nothing is quoted
from a write-up.

---

## 0. Headline

| | |
|---|---|
| Files collected | **1,686** (from 2 at the start of the campaign) |
| On disk | **~673 MB** |
| Independent sources | 3 keyservers/mirrors for the key, 6 GitHub compilations, Fandom, the Internet Archive, Pastebin |
| PGP messages verified | **140 files, 80 distinct by sha256** |
| Verification result | **137 VALID / 2 INVALID / 1 NO_SIGNATURE** |
| Distinct Cicada signatures | **56** |
| Distinct signing keys | **1** |
| Signature timespan | 2012-01-05T03:46:03Z to 2017-04-04T23:23:28Z (**1,916 days**) |

Two results are worth more than the file count:

1. **Every signature that fails, fails for a reason that is about a mirror, not about
   Cicada.** There is no message in this corpus that is signed by a second key, signed
   badly, or unsigned when it should be signed. (Section 1, `CONFLICTS-A.md` C-01)
2. **The Internet Archive's copy of the single most important 2012 artifact is missing the
   puzzle.** The bytes that carried the first step were stripped by imgur's image pipeline;
   the community mirror kept them. (Section 4, `CONFLICTS-A.md` C-02)

---

## 1. G-02 is closed: the signature record now exists

`SIGNATURES.json` records, per file: path, size, sha256, gpg raw `--status-fd` output,
status, signing key ID and fingerprint, SIG_ID, signature timestamp and where that timestamp
came from, digest and pubkey algorithm, gpg stderr, source URL, retrieval time, upstream
note, whether the row duplicates another by hash, and whether it is a derived file.

Verification key, fetched independently from three places and identical in all three:

```
fingerprint  6D854CD7933322A601C3286D181F01E57A35090F
long id      0x181F01E57A35090F        short id  7A35090F
uid          Cicada 3301 (845145127)
created      2012-01-05        rsa4096
```

Result over 140 files (80 distinct byte-streams; the rest are the same message held at a
second mirror path, verified rather than assumed):

| status | files | what it means |
|---|---|---|
| VALID | 137 | good signature from `181F01E57A35090F` |
| INVALID | 2 | the same file at two paths, armor damaged by one mirror — see below |
| NO_SIGNATURE | 1 | `2014-01-fallen-behind-outguess-08.asc` is a plaintext note (the `TL BE IE OV ...` block), never signed |

**Distinct signing key IDs across all 140 files: exactly one.** Distinct fingerprints:
exactly one. If a second key had ever been used to sign a message that reached these
mirrors, this table would show it.

### The two INVALID rows are one damaged mirror copy, and this must not be reported as a forgery

The krisyotam copy of the 2013 opening book-code message is missing the empty line that
OpenPGP requires between `Hash: SHA1` and the signed text, so GnuPG parses the first line of
the message (`Welcome again.`) as an armor header, excludes it from the digest, and reports
BADSIG. Three independent checks confirm the cause: a copy of the same message from a
different mirror verifies; restoring the one missing line makes the damaged copy verify with
the *same* SIG_ID; and the two copies signature blocks are byte-identical.

Full write-up, with hashes: `CONFLICTS-A.md` **C-01**. Derived repaired copy and its
provenance note: `pgp/repaired/`.

### What made this possible: 17 files that were not signatures

17 of the 42 `.asc` files this repository already held were **199-byte GitHub "429 Too Many
Requests" HTML pages**. A verifier pointed at that directory reports 17 failures, and read
quickly that is "17 Cicada messages do not verify." They were all refetched.
`SIGNATURES.json` now carries a distinct `FETCH_ERROR_PAGE` status so the difference between
*this is not a signature* and *this signature does not verify* can never collapse again.

---

## 2. A third message corpus, and 20 signatures nothing here had

The largest single gain this session came from noticing that krisyotam vendors a copy of
someone else collection. Following it upstream reached **`github.com/iBotPeaches/cicada_3301`**,
which was collected from the upstream repo rather than the vendored copy (60 files,
`ibotpeaches/`).

It carries **20 distinct Cicada signatures that no other source in this corpus held**, taking
the verified count from 36 to 56. Almost all are 2013:

| timestamp (UTC) | message |
|---|---|
| 2012-01-15T01:39:42Z | `this-message-will-only-be-displayed` |
| 2012-01-20T03:57:40Z | `the-song-is-your-own-path` |
| 2013-01-06T07:38:19Z | `you-cant-see-the-forest` |
| 2013-01-11T23:20:28Z | `standby-for-coords` |
| 2013-01-12T08:41:05Z | `33.092817` |
| 2013-01-12T20:39:51Z | `26.41968` |
| 2013-01-12T20:46:39Z | `38.977845` |
| 2013-01-15T20:05:42Z | `ssss-03` |
| 2013-01-15T20:05:42Z | `ssss-10` |
| 2013-01-15T20:05:44Z | `ssss-09` |
| 2013-01-17T20:28:43Z | `32.478944` |
| 2013-01-18T17:15:18Z | `welcome-and-congratulations` |
| 2013-01-19T22:15:59Z | `55.793765` |
| 2013-01-19T22:16:44Z | `37.182685` |
| 2013-01-19T22:17:48Z | `34.7477910` |
| 2013-01-26T09:16:23Z | `tcp-server` |
| 2013-01-26T20:26:21Z | `if-you-followed` |
| 2013-01-31T08:08:24Z | `no-more-testing` |
| 2013-03-03T05:32:58Z | `do-not-share-this-information` |
| 2013-03-03T05:33:01Z | `do-not-share-this-information-2` |

Two upstream filenames literally contain angle brackets (`<space>.asc`, `<data-blob>.asc`);
NTFS forbids those characters, so they are stored as `_space_.asc` and `_data-blob_.asc`
with the rename recorded in `MANIFEST.json`. The bytes are untouched.

**The general lesson:** a mirror that vendors another archive is a signpost. Following
`krisyotam/tools/solvers/ibotpeaches/` upstream was worth more than any amount of further
crawling of krisyotam itself.

---

## 3. G-09: the signature timestamps as a dataset

`SIGNATURE-TIMELINE.json` holds every signature-packet creation time, chronologically:
139 timestamped rows, **56 distinct signatures**, plus inter-signature gaps and year, UTC-hour
and UTC-weekday distributions.

Timestamps are read from the signature packet itself (`gpg --list-packets` on the isolated
signature block), **not** from `--verify`. That matters: a file whose signature fails to
verify still yields its true packet timestamp, so the damaged mirror copy in Section 1
contributes its real 2013-01-03T04:33:29Z rather than a null.

### Distribution by year

```
2012  ##############  14
2013  ########################  24
2014  ###############  15
2015  #  1
2016  #  1
2017  #  1
```

### Batch signing is visible

Twelve inter-signature gaps are under ten minutes. Three are seconds apart, and one pair is
**zero seconds apart**:

| interval | what |
|---|---|
| 2013-01-15T20:05:42Z then 20:05:42Z | `ssss-03` and `ssss-10`, two *different* signatures in the same second |
| then 20:05:44Z | `ssss-09`, two seconds later |
| 2013-01-19T22:15:59 / 22:16:44 / 22:17:48 | three coordinate messages, 45 s and 64 s apart |
| 2013-03-03T05:32:58 / 05:33:01 | `do-not-share-this-information` and its `-2` |
| 2014-01-07T03:16:41 / :44 / :48 | three signatures, 3 s and 4 s apart |
| 2014-01-19T07:39:32 / :42 / :50 / :57 | four signatures inside 25 seconds |

Two distinct signatures bearing the same second is not something a person achieves by typing.
These sets were signed by a script in one pass — which means **the number of messages is not
the number of signing sessions.** 56 signatures resolve to considerably fewer occasions on
which someone sat down with the private key.

### A caution about the hour-of-day distribution

The 56 signatures cluster at 03:00-08:00 and 20:00-23:00 UTC and are entirely absent from
11:00 and 13:00-16:00 UTC. That shape is suggestive and it is also **56 samples**, of which
whole clusters were produced in single scripted bursts, which correlates them. OpenPGP stores
UTC and does not record the signer timezone. Anyone converting this into a claim about
where 3301 slept should first collapse the bursts to one event each and see what survives —
the raw material for doing that is in the `inter_signature_gaps` array.

---

## 4. G-01: what the primary artifacts turned out to be

The 2012 chain, the poster photographs, the site saves, the Liber Primus scans and the
2013-2017 material are now on disk from multiple mirrors. The interesting result is not the
volume; it is what cross-hashing them showed.

### Seven of eight 2012 chain images agree across three independent holdings

For each imgur-hosted image in the 2012 chain, Lane A now holds the Internet Archive own
raw (`id_`) capture alongside the `cijhho123` and `krisyotam` mirror copies:

| image | Wayback capture | mirrors | agree? |
|---|---|---|---|
| `KXLOP.jpg` | 2013-12-29 | 2 | **identical** |
| `NHYLD.jpg` | 2013-12-29 | 2 | **identical** |
| `m9sYK.jpg` | 2013-12-12 | 2 | **identical** |
| `vjuNp.jpg` | 2015-06-24 | 2 | **identical** |
| `8D7hN.jpg` | 2020-11-12 | 2 | **identical** |
| `hkdgl.png` | 2022-05-03 | 2 | **identical** |
| `cAuUz.jpg` | 2022-06-22 | 2 | **identical** |
| `1CcV1.jpg` | 2013-12-29 **and** 2024-02-05 | 2 | **NO** |

Seven three-way byte-identities is a real result: it means the community mirrors of the 2012
chain are faithful, and the corpus can be trusted where it agrees.

### The one that disagrees is the one that matters

`1CcV1.jpg` is the opening image of the entire puzzle. Three byte-streams exist:

- **29,279 bytes** in both community mirrors,
  `870353b8fbe4d1dd83fdbfc61b07d80213bab035526d3e5fd6a43f7d77db1ead`
- **29,261 bytes** on the Fandom wiki as `Final.jpg_2012.jpg`,
  `a381daf635bc78d8a5b5ddbc25b55d459bc823fb2e02d0012627870ee1240573` — the mirror stream
  minus its 18-byte JFIF APP0 header and nothing else, **payload intact**
- **27,517 bytes** in every Wayback capture of `i.imgur.com/1CcV1.jpg` from 2013 to 2024,
  `72a1fd406da308cd61935fb116f2d73ea5cc008122518a23c9725f6ae1537029` — **payload absent**

All three decode to pixel-identical 509x503 images. The archive copy has optimised Huffman tables;
the mirror copy has the standard ones. And the mirror copy has **61 bytes after the JPEG EOI
marker** that the archive copy does not:

```
TIBERIVS CLAVDIVS CAESAR says "lxxt>33m2mqkyv2gsq3q=w]O2ntk"
```

That is the first step of the puzzle, and imgur optimiser removed it while preserving every
pixel. The Internet Archive holds a faithful record of an image that is no longer the
artifact.

> **For Cicada material, "the Internet Archive has it" does not mean "the bytes that mattered
> survived."**

The Fandom copy was found by the structural scan below rather than looked for, and it matters:
**two archives that are not each other hold the payload-bearing stream, and only imgur's does
not.** That rules out "one archivist appended the line and everything descends from that
file." It does not establish a chain of custody back to 4chan. Which stream, if any, is what
4chan served on 2012-01-04 is **not** resolved here. See `CONFLICTS-A.md` C-02 and
`GAPS-A.md` A-01.

The same diff also explains an unrelated finding: the Fandom copy differs from the mirror copy
by exactly the 18-byte APP0/JFIF segment, which is precisely the constant 18-byte deficit seen
across 288 Fandom JPEGs (`CONFLICTS-A.md` C-05). Two findings that arrived separately turned
out to be the same mechanism.

### That finding generalised into a scan

Because trailing data turned out to be load-bearing, every JPEG and PNG in the corpus was
parsed structurally — walking markers, handling `FF00` byte-stuffing and restart markers — to
find the true end of the image and measure what lies past it. Output: **`TRAILING-DATA.json`**.

Of **1,208 images scanned, 13 carry data after their real EOI/IEND**, and ten of them are not
the 2012 image:

| trailing bytes | file | trailer begins |
|---|---|---|
| 3,486,295 | `cijhho123/2014/Websites/onion 6/onion6.jpg` | a complete second JPEG (`FFD8FFE0 ... JFIF`) |
| 3,486,295 | `cijhho123/2014/Liber Primus/liber primus images full/10.jpg` | same |
| 1,651,773 | `wiki-uncovering-cicada/images/ONION_2_JPG.jpg` | a complete second JPEG |
| 336,713 | `.../liber primus images full/05.jpg` | ASCII, and **ends with a byte-reversed JPEG header** |
| 175,159 | `.../Liber primus pages/Huh2.jpg` **and** `wiki-uncovering-cicada/images/Huh2.jpg` | binary; two independent holdings agree |
| 13,592 | `wiki-uncovering-cicada/images/Outt.png` | after IEND; a short repeating byte pattern |
| 10,923 | `signed-payloads/2014-01-onion5-liber-primus.jpg` | a second JPEG, **and this file's bytes are attested by a verified 3301 signature** |
| 424 | `wiki-uncovering-cicada/images/-016477-.jpg` | mostly printable; contains an `upload.wikimedia.org` URL |
| 61 (x3) | `1CcV1.jpg` in both mirrors, `Final.jpg_2012.jpg` on Fandom | the `TIBERIVS` line |
| 3 | a Blake plate from the wiki | three bytes; almost certainly noise |

A further **9 files do not parse as well-formed JPEG/PNG at all** and are listed under
`unparseable` in the same file — malformed structure is itself a signal worth a second look.
The scanner is committed as `_tools/trailing_scan.py` and is cheap to re-run as the corpus
grows.

The `signed-payloads/2014-01-onion5-liber-primus.jpg` row deserves emphasis: those bytes were
carried *inside* a clearsigned message that verifies against the Cicada key, so unlike
everything else in this table its chain of custody runs back to the signer rather than to a
mirror.

Lane A stops at measurement. Interpreting these trailers is Lane G job, and Lane G will
need an outguess build this machine does not have (`GAPS-A.md` A-07).

---

## 5. Method notes worth inheriting

Five things cost time here and will cost the next lane the same time if they are not written
down.

1. **Distinguish "not a signature" from "bad signature."** 17 held `.asc` files were HTTP 429
   error pages. Any verifier that reports both as failure manufactures false findings.
2. **Read the timestamp from the packet, not from `--verify`.** `gpg --verify` reports no
   VALIDSIG for a signature that fails, so a naive timeline silently drops exactly the rows
   worth looking at. `gpg --list-packets` on the isolated signature block always works.
3. **`?format=original` on Fandom is mandatory.** Without it Fandom returns a WebP re-encode
   at roughly 3% of the original size, with HTTP 200 and a plausible content-type. Nothing in
   the response says a substitution happened. Even with it, **486 of 829** files do not
   match the wiki's own declared SHA-1, **288 of them short by exactly 18 bytes**
   (`CONFLICTS-A.md` C-05).
4. **imgur URLs are case-sensitive, and Wayback CDX will happily list the neighbours.** A
   CDX query for `i.imgur.com/NHYLD.jpg` returns fifteen digests, fourteen of which are
   case-variant URLs (`Nhyld`, `nhYld`, `NHylD` ...) that are unrelated uploads captured by
   somebody permutation scanner in 2023. Filter to the exact case or you will "discover"
   fifteen versions of an image that has one.
5. **A resume that trusts the manifest is not a resume.** `_tools/grab.py` skipped any path
   already recorded in `MANIFEST.json`, including paths whose file was never written because
   the run died. Every resumed batch was a silent no-op. It now requires the bytes to be on
   disk. Fixed; the same bug is worth checking for in the other lanes fetchers.

---

## 6. State handed over

**Closed.** G-02 in full. G-09 for message signatures. G-01 substantially: the 2012 chain,
the 2012 and 2013 poster photographs, the `845145127.com` saves, the Liber Primus scans, the
2017 material, and **all three later entry images, each visually confirmed**:

| year | file | opening line |
|---|---|---|
| 2013 | `cijhho123/2013/additional images/1357366592898.jpg` | *"Hello again. Our search for intelligent individuals now continues."* |
| 2014 | `cijhho123/2014/additional images/zN4h51m.jpg` | *"Hello. Epiphany is upon you. Your pilgrimage has begun."* |
| 2016 | `cijhho123/2016/2016/additional images/4gq25.jpg` | *"The path lies empty; epiphany seeks the devoted"* (faint tree behind the text) |

None of the three has yet been cross-hashed against a second independent holding — the check
that turned `1CcV1.jpg` into C-02 — so that trap is still open for them (`GAPS-A.md` A-05).

**Finished this session.** The Fandom image pull completed at **829/829, 0 failures,
345 MB**; `cijhho123` completed at **447/447, 192 MB**. Nothing is left running.

**Still open**, ranked, with what is behind each: `GAPS-A.md`. The top five are an outguess
toolchain (unblocks three separate questions on files already held), decoding the poster QR
codes, mining the 315 third-party certifications on the public key, hash-verifying the
2013/2014/2016 entry images against a second mirror, and chasing the pre-Fandom
`uncovering-cicada.wikia.com` originals.

**Unresolved disagreements**, all recorded rather than adjudicated: `CONFLICTS-A.md`, C-01
through C-07.
