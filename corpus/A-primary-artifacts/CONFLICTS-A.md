# CONFLICTS-A.md — Lane A: sources that disagree

Compiled 2026-08-20 by Lane A (primary artifacts). Companion to `REPORT-A.md` and `GAPS-A.md`.

**House rule: nothing here is resolved.** Where two sources disagree, both are recorded with
their hashes and their provenance, and the reader is told what would settle it. Where a
disagreement has a demonstrated mechanical cause, the cause is stated — but the disagreement
is still recorded, because a mechanical explanation is a finding about the *mirror*, not a
licence to delete one side.

Every hash below was computed on this machine from bytes on this disk. None is quoted from a
third party.

---

## C-01 — One signature fails to verify. It is a mangled mirror, not a fake message. ★★★★★

**This is the entry most likely to be misread, so read the whole thing before quoting it.**

`SIGNATURES.json` reports **2 INVALID rows**. Both are the same file, held at two paths:

| path | sha256 | status |
|---|---|---|
| `pgp/messages/ky_2013-01-opening-book-code.asc` | `cbc0abbea8f36fdf30433806a3418b30ad06f21f60eeee212b1692e2d5c9811b` | INVALID (BADSIG) |
| `krisyotam/pgp/messages/2013-01-opening-book-code.asc` | same sha256 | INVALID (BADSIG) |

Source for both: `https://raw.githubusercontent.com/krisyotam/cicada3301/main/pgp/messages/2013-01-opening-book-code.asc`
(retrieved 2026-08-19T23:11:16Z).

### What gpg actually said

```
gpg: invalid armor header: Welcome again.\r\n
gpg: Signature made Wed Jan  2 20:33:29 2013 PST
gpg:                using RSA key 181F01E57A35090F
gpg: BAD signature from "Cicada 3301 (845145127)" [unknown]
```

The first line is the whole story. RFC 4880 §7 requires an **empty line** between the
cleartext armor headers and the start of the signed text. The krisyotam copy has none:

```
-----BEGIN PGP SIGNED MESSAGE-----^M$
Hash: SHA1^M$
Welcome again.^M$          <- should have been preceded by an empty line
```

GnuPG therefore parses `Welcome again.` as an armor header, excludes it from the hashed
text, and the digest no longer matches. BADSIG.

### Three independent checks that this is transcription damage

1. **A clean copy of the same message, from a different mirror, verifies.**
   `pgp/messages/2013-01-opening-book-code.asc`, sha256
   `4c6ecff3eeabc05adb4eabe0a79596bedf74f831b062c587341b9f6052715c7c`, from
   `raw.githubusercontent.com/jaxonkuipers/cicada3301`, is **VALID**, SIG_ID
   `B4/S2U0VepM5G4Idm4YLjSo2aNs`.
2. **Restoring the one missing line makes the damaged copy verify, with the same SIG_ID.**
   `pgp/repaired/ky_2013-01-opening-book-code.repaired.asc` (sha256
   `bd6be7123f455d950177d465d5d6fdf02fcc46ae920971fe55daa4ba6adf5f5d`, **derived, not
   retrieved**) → *Good signature*, SIG_ID `B4/S2U0VepM5G4Idm4YLjSo2aNs`, signature made
   2013-01-03T04:33:29Z. No other byte was changed.
3. **The two mirrors' signature blocks and message bodies are identical.** After CRLF
   normalisation the cleartext bodies hash the same, and the armored signature blocks differ
   only by one trailing newline.

### The correct statement of this finding

> The krisyotam mirror's copy of the 2013 opening book-code message has lost the blank line
> its OpenPGP armor requires, so that copy does not verify. The message itself carries a
> valid Cicada signature; it verifies from an independent mirror and it verifies again once
> the missing line is restored.

**Not** "a Cicada message failed verification", and **not** "1 of 58 Cicada messages is
invalid". Across 140 verified files there is **no message whose signature fails for any
reason other than this one mirror's armor damage**.

### What is still open

Whether the damage originated with krisyotam or was inherited from further upstream. The
`\r\n` line endings throughout that copy suggest a Windows editor or a copy-paste through a
web form somewhere in its history. Not investigated.

---

## C-02 — Two byte-streams claim to be the 2012 opening image, and the archive's copy is the degraded one ★★★★★

`1CcV1.jpg` is the 2012-01-04 opening image (509×503, black, "Hello. We are looking for
highly intelligent individuals…"). Lane A holds **two distinct byte-streams** for it:

| copy | bytes | sha256 | provenance |
|---|---|---|---|
| community mirrors | 29,279 | `870353b8fbe4d1dd83fdbfc61b07d80213bab035526d3e5fd6a43f7d77db1ead` | `cijhho123/2012/additional media/images/1CcV1.jpg` and `krisyotam/puzzles/2012/images/1CcV1.jpg` — byte-identical to each other |
| Internet Archive | 27,517 | `72a1fd406da308cd61935fb116f2d73ea5cc008122518a23c9725f6ae1537029` | `2012/wayback/20131229091245_1CcV1.jpg`, Wayback raw (`id_`) capture of `http://i.imgur.com/1CcV1.jpg`, 2013-12-29 |

Wayback's CDX index lists that same digest (`SYTRWGOSHT3PKVDFNPXRJAK3INJU3J62`) for every
successful capture of that exact-case URL from **2013-12-29 through 2024-02-05**, and a second
fetch of the 2024 capture reproduces the 27,517-byte stream byte for byte. imgur has served
one unchanging file for eleven years.

### What the difference is

Measured here, not asserted:

- **Both decode to pixel-identical 509×503 RGB images.** SHA-256 of the decoded pixel buffer
  is `21d65d997c42c0aee2d008c7918557b7…` for both. The image content is the same.
- The archive copy uses **optimised Huffman tables** (four DHT segments, 28/79/20/20 bytes);
  the mirror copy uses the **standard tables** (31/181/31/181 bytes). That is a re-encode of
  the entropy coding only, which is why the pixels survive.
- The mirror copy has **61 bytes after the EOI marker**. The archive copy has **none**.

Those 61 bytes are:

```
TIBERIVS CLAVDIVS CAESAR says "lxxt>33m2mqkyv2gsq3q=w]O2ntk"
```

— the payload of the first puzzle step, stored as plaintext appended to the JPEG.

### Why this matters more than the file it is about

The imgur copy is the one the Internet Archive holds, and it is the one that **does not
contain the puzzle**. An optimiser that preserves every pixel still discarded the only part
of the file that was the artifact.

> For Cicada material, "the Internet Archive has it" does not mean "the bytes that mattered
> survived". Trailing data, EXIF, and steganographic payloads live outside the region that
> image pipelines consider content.

Any forensic battery run on the Wayback copy of this image will find nothing, and will be
right about that file and wrong about the artifact.

### What is *not* resolved

Which stream, if either, is the bytes 4chan actually served on 2012-01-04. Both are copies:
one via imgur's pipeline, one via a community archive of unknown chain of custody. It is
equally consistent with the evidence that a solver appended the decoded line to their own
copy as a note. **Recorded, not resolved.** The 4chan original is A-01 in `GAPS-A.md`.

### Contrast: the rest of the chain agrees

Seven of the eight imgur-hosted 2012 chain images are **byte-identical across all three
independent holdings** (Internet Archive capture, cijhho123 mirror, krisyotam mirror):
`KXLOP.jpg`, `NHYLD.jpg`, `m9sYK.jpg`, `vjuNp.jpg`, `8D7hN.jpg`, `hkdgl.png`, `cAuUz.jpg`.
`1CcV1.jpg` is the only disagreement — and it is the one file in the set that had something
appended past EOI.

---

## C-03 — Two snapshots of the public key disagree about who certified it ★★★★☆

The key itself is not in dispute. Four independently sourced copies all carry primary key
fingerprint `6D854CD7933322A601C3286D181F01E57A35090F`, uid `Cicada 3301 (845145127)`,
rsa4096, created 2012-01-05. The **certifications attached to it** differ:

| copy | bytes | signature packets |
|---|---|---|
| `pgp/keys/cicada-3301-pubkey.keys.openpgp.org.asc` | 2,341 | 1 |
| `pgp/keys/key-local-jaxonkuipers.asc` | 3,057 | 2 |
| `ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` | 149,198 | **313** |
| `pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc` | 151,959 | **315** |

keys.openpgp.org strips third-party certifications by policy, which accounts for the small
copies. The interesting pair is the two large ones — an older vendored snapshot and today's
live keyserver — because the difference is **not** a simple "older has fewer".

Certifying key IDs present in **today's keyserver copy but not** in the iBotPeaches snapshot:
`0C027B894CF1D90B`, `0D48F3F626E6757B`, `23A03821D23403D3`, `ABFCD13BAEE5A8DA`,
`BAD8A092A2F590F6`, `BB3499116F8071FB`, `F11522829AB6E65D`.

Certifying key IDs present in the **iBotPeaches snapshot but not** in today's keyserver copy:
`6D22F7E629158E0F` (×2), `90F320D0DF4751F8`, `F822A051503B61A4` (×2).

That second list is the finding: **certifications that were once attached to the Cicada key
and are no longer served by keyserver.ubuntu.com.** Causes could be keyserver policy, a
reconciliation gap between SKS-era pools, or deliberate removal. Not investigated. The older
snapshot is the only copy in this corpus that preserves them.

---

## C-04 — iBotPeaches' key file is named with a fingerprint that is not the key's ★★☆☆☆

The file `ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` contains a key
whose actual fingerprint is `6D854CD7933322A601C3286D181F01E57A35090F`. The two strings
share only their last eight hex digits (`7A35090F`, the short key ID).

There is no second Cicada key here — the file's content is the canonical key. This is a
filename defect, recorded because a filename that looks like a fingerprint will be read as
one, and because "a second 3301 key with fingerprint 67F363…" is exactly the kind of claim
that gets repeated. Across all 140 verified messages, `SIGNATURES.json` records exactly
**one** signing key ID and **one** signing fingerprint.

---

## C-05 — Fandom serves image bytes that do not match Fandom's own declared SHA-1 ★★★☆☆

The 829-file pull from `uncovering-cicada.fandom.com` was done with `?format=original`
(without it, Fandom returns a WebP re-encode at roughly 3% of the original size — a silent
substitution, HTTP 200, correct content-type). Even with it, the wiki's `allimages` API
declares a SHA-1 and a byte count per file that the delivered bytes do not always match:

Final numbers, over the **complete 829-file pull** (0 failures):

| | count |
|---|---|
| files whose delivered SHA-1 **matches** the wiki's declared SHA-1 | 343 |
| files whose delivered SHA-1 **differs** | 486 |
| files not retrieved | 0 |

The mismatch is not random:

- **424 of the 486 mismatches are JPEGs.** 267 of the 343 matches are PNGs.
- **288 of the 486 mismatches are short by exactly 18 bytes.**

A constant 18-byte deficit concentrated in JPEGs is the signature of a delivery-side
transformation stripping a fixed-size trailer or metadata segment, not of corrupt storage.
In light of **C-02** — where 61 trailing bytes were the entire puzzle — an 18-byte deficit in
288 files is not a rounding error. It is 288 files that may have been silently trimmed in
precisely the region where Cicada put payloads.

**Not resolved.** Settling it needs a fetch path that bypasses the image pipeline (a Fandom
image dump, or the pre-Fandom `uncovering-cicada.wikia.com` originals via Wayback) and a
byte-level diff against these copies. Recorded as A-06 in `GAPS-A.md`.

Per-file evidence: `_logs/fandom_manifest.json` carries `wiki_declared_sha1`,
`wiki_declared_bytes`, `sha1`, `bytes` and `sha1_matches_wiki` for all 829 rows.

---

## C-06 — cijhho123's outguess dump maps a payload to an image the usual account does not ★★☆☆☆

`cijhho123/2012/additional docs/outguss/` holds six `.out` files, presented as outguess
extractions from the 2012 chain images. Two things in that folder do not line up with the
commonly told version of the 2012 chain:

- `1CcV1.jpg.out` contains the book code and the `reddit.com/r/a2e7j6ic78h0j` pointer.
  The usual account attributes the book code to a **later** image in the chain, and gives
  `1CcV1.jpg` the `TIBERIVS CLAVDIVS CAESAR` line — which this corpus finds appended in
  plaintext to `1CcV1.jpg` itself (C-02), not extracted by outguess.
- There is **no `.out` file at all** for `m9sYK.jpg`, the image the usual account credits
  with an outguess payload.

Both readings are internally consistent: either the folder's file→payload mapping is wrong,
or the widely repeated ordering of the 2012 chain is. Lane A has no outguess binary on this
machine and therefore cannot re-extract and settle it.

**Recorded, not resolved.** Settling it needs `outguess` run against the 29,279-byte
`1CcV1.jpg` and against `m9sYK.jpg` — a Lane G job, on files this lane now holds.

---

## C-07 — The repo's own `.asc` collection contained 17 error pages ★★★☆☆

Not a disagreement between sources so much as a disagreement between a file's name and its
contents, and it is recorded because it produced a false negative that looked like a real one.

17 of the 42 `.asc` files this repo already held were **199-byte GitHub "429 Too Many
Requests" HTML stubs**, not signatures. A verification run over that directory reports those
files as unverifiable. Read quickly, that is "17 Cicada messages do not verify."

All 17 were refetched. The lesson is in `REPORT-A.md` §5: a signature verifier must
distinguish *this file is not a signature* from *this signature does not verify*, and
`SIGNATURES.json` now carries a distinct `FETCH_ERROR_PAGE` status for exactly this case.

---

## Summary table

| id | conflict | severity | resolvable now? |
|---|---|---|---|
| C-01 | BADSIG caused by mirror armor damage, not forgery | ★★★★★ | cause demonstrated; upstream origin open |
| C-02 | Two byte-streams for `1CcV1.jpg`; archive copy lacks the payload | ★★★★★ | no — needs the 4chan original (A-01) |
| C-03 | Key snapshots disagree on third-party certifications | ★★★★☆ | no — needs keyserver history |
| C-04 | Key file named with a non-matching fingerprint | ★★☆☆☆ | yes — filename defect, content canonical |
| C-05 | Fandom bytes vs Fandom's declared SHA-1; 288 files short by 18 bytes | ★★★☆☆ | no — needs a non-pipeline fetch path |
| C-06 | outguess payload→image mapping vs the usual 2012 chain | ★★☆☆☆ | no — needs an outguess run (Lane G) |
| C-07 | 17 held `.asc` files were HTTP 429 error pages | ★★★☆☆ | yes — refetched |
