# The PGP verification table — every claimed Cicada 3301 signature in this repository

_Round 18 lane **L8-provenance**. Generated 2026-08-26T17:32:10Z by `liber-primus/analysis/round18/L8-provenance/verify_all_signatures.py`._

Closes the machine-verification half of `corpus/GAPS.md` **G-02** (*"no file in this repository records which signatures verify against key 7A35090F and which do not"*).

**Every row below is `verified`** in the confidence sense of `KNOWLEDGE.json`: it is the output of
running `gpg --verify` on bytes held in this tree, reproducible by the command in §6. Nothing in this
file is reported or speculated. Provenance of the *bytes* — which mirror they came from — is a
separate question and is treated in §5.

> A valid signature from `7A35090F` proves **keyholder continuity**. It does not prove authorship,
> identity, or that the timestamp inside it is the real wall-clock time it was made. See §7.

## 1. The instrument, and proof that it works in both directions

- gpg: `gpg (GnuPG) 2.4.8`
- verification key: `6D854CD7933322A601C3286D181F01E57A35090F` (`0x181F01E57A35090F`, short `7A35090F`)
- keyring: **isolated** — a throwaway `GNUPGHOME` holding exactly one primary key, `6D854CD7933322A601C3286D181F01E57A35090F`, so a PASS cannot come from any other key on the box
- scope: **every `*.asc` in the repository** — 228 files, 113 distinct by sha256

Rule 2 of the campaign plan: *a null from an unvalidated instrument is not a negative.* The four
controls were fixed in `PREREG.md` before the run.

| control | what it does | required output | measured | met |
|---|---|---|---|---|
| **C1** | verify an untouched known-good file | `GOODSIG 181F01E57A35090F` | `GOODSIG 181F01E57A35090F` | ✅ |
| **C2** | flip one character of the *signed body* | `BADSIG` | `BADSIG 181F01E57A35090F`, no GOODSIG | ✅ |
| **C3** | verify a message signed by a freshly generated foreign key | not GOODSIG for 3301 | `NO_PUBKEY B585B79B99A9714B` / `ERRSIG B585B79B99A9714B`, no GOODSIG | ✅ |
| **C4** | recover the timestamp from the *tampered* file | original `created` unchanged | `1357187609` → `1357187609` | ✅ |

**All four controls met: YES.** C2/C3 are what make a FAIL in this
table mean something; C4 is why a FAILing file still yields a usable timestamp.

## 2. Headline counts

| verdict | files | meaning |
|---|---|---|
| **PASS** | 192 | `GOODSIG` + `VALIDSIG` for the canonical fingerprint |
| **FAIL** | 3 | a signature packet is present and does not verify |
| **NO-SIG** | 22 | no signature block in the file at all |
| **KEY** | 11 | the file is a public-key block, not a message |
| total | 228 | |

- **Distinct signing key IDs across every signed message in the repository: 1 — `181F01E57A35090F`.**
  No second signing key appears anywhere. That is the single most load-bearing line in this table:
  the corpus is internally consistent with one keyholder throughout 2012–2017.
- Distinct signed **messages** (grouped by normalised body): **54**. The 228 files are mostly mirrors of each other.
- Distinct verified signature timestamps: **54**, spanning `2012-01-05T03:46:03Z` → `2017-04-04T23:23:28Z`.

## 3. The messages — one row per distinct signed text

Chronological by signature-packet timestamp. `copies` = how many byte-different files in this
repository carry this same signed body.

| # | sig timestamp (UTC) | verdict | copies P/F | hash | first line of the signed text |
|---|---|---|---|---|---|
| 1 | `2012-01-05T03:46:03Z` | **PASS** | 6/0 | SHA-1 | From here on out, we will cryptographically sign all messages with thi |
| 2 | `2012-01-06T20:28:30Z` | **PASS** | 3/0 | SHA-1 | In twenty-nine volumes, knowledge was once contained. |
| 3 | `2012-01-07T07:53:10Z` | **PASS** | 5/0 | SHA-1 | A poem of fading death, named for a king |
| 4 | `2012-01-07T10:07:51Z` | **PASS** | 5/0 | SHA-1 | The key has always been right in front of your eyes. |
| 5 | `2012-01-07T19:45:24Z` | **PASS** | 2/0 | SHA-1 | You have done well to come this far. |
| 6 | `2012-01-08T22:34:35Z` | **PASS** | 6/0 | SHA-1 | 52.216802, 21.018334 |
| 7 | `2012-01-08T23:39:04Z` | **PASS** | 2/0 | SHA-1 | Congratulations! |
| 8 | `2012-01-11T05:07:59Z` | **PASS** | 2/0 | SHA-1 | 162667212858 |
| 9 | `2012-01-11T07:22:18Z` | **PASS** | 6/0 | SHA-1 | Miss round 1? |
| 10 | `2012-01-15T01:39:42Z` | **PASS** | 1/0 | SHA-1 | This message will only be displayed once. |
| 11 | `2012-01-15T12:16:52Z` | **PASS** | 2/0 | SHA-1 | Hello. You have shared your information online. You are now removed fr |
| 12 | `2012-01-20T03:57:40Z` | **PASS** | 1/0 | SHA-1 | This song is your own path |
| 13 | `2012-02-06T22:59:40Z` | **PASS** | 9/0 | SHA-1 | Hello. |
| 14 | `2012-04-18T17:41:42Z` | **PASS** | 3/0 | SHA-1 | Some news organisations have recently claimed that "Cicada 3301" is |
| 15 | `2013-01-03T00:08:11Z` | **PASS** | 17/0 | SHA-1 | @1231507051321 |
| 16 | `2013-01-03T04:33:29Z` | **PASS** | 4/3 | SHA-1 | Welcome again. |
| 17 | `2013-01-04T03:47:31Z` | **PASS** | 5/0 | SHA-1 | — |
| 18 | `2013-01-06T07:38:19Z` | **PASS** | 1/0 | SHA-1 | You can't see the forest when you're looking at the trees. |
| 19 | `2013-01-06T07:51:35Z` | **PASS** | 6/0 | SHA-1 | Very good. |
| 20 | `2013-01-10T17:07:15Z` | **PASS** | 2/0 | SHA-1 | Well done. You have come far. |
| 21 | `2013-01-11T23:20:28Z` | **PASS** | 1/0 | SHA-1 | Standby for coordinates. |
| 22 | `2013-01-12T08:41:05Z` | **PASS** | 1/0 | SHA-1 | 33.092817, -96.08265 |
| 23 | `2013-01-12T20:39:51Z` | **PASS** | 1/0 | SHA-1 | 26.41968, 127.73254 |
| 24 | `2013-01-12T20:46:39Z` | **PASS** | 1/0 | SHA-1 | 38.977845, -76.486451 |
| 25 | `2013-01-14T05:31:07Z` | **PASS** | 3/0 | SHA-1 | You already have everything you need to continue. |
| 26 | `2013-01-15T20:05:42Z` | **PASS** | 1/0 | SHA-1 | ssss, Threshold: 5 |
| 27 | `2013-01-15T20:05:42Z` | **PASS** | 1/0 | SHA-1 | ssss, Threshold: 5 |
| 28 | `2013-01-15T20:05:44Z` | **PASS** | 1/0 | SHA-1 | ssss, Threshold: 5 |
| 29 | `2013-01-17T20:28:43Z` | **PASS** | 1/0 | SHA-1 | 32.478944, -84.983674 |
| 30 | `2013-01-18T17:15:18Z` | **PASS** | 1/0 | SHA-1 | Welcome, and congratulations. We have been pleased with your teamwork. |
| 31 | `2013-01-19T22:15:59Z` | **PASS** | 1/0 | SHA-1 | 55.793765, 37.578608 |
| 32 | `2013-01-19T22:16:44Z` | **PASS** | 1/0 | SHA-1 | 37.182685, -3.605801 |
| 33 | `2013-01-19T22:17:48Z` | **PASS** | 1/0 | SHA-1 | 34.7477910, -92.2690863 |
| 34 | `2013-01-26T20:26:21Z` | **PASS** | 1/0 | SHA-1 | If you followed the rule but did not receive an email, |
| 35 | `2013-01-31T08:08:24Z` | **PASS** | 1/0 | SHA-1 | No more testing. |
| 36 | `2013-03-03T05:32:58Z` | **PASS** | 1/0 | SHA-1 | DO NOT SHARE THIS INFORMATION! |
| 37 | `2013-03-03T05:33:01Z` | **PASS** | 1/0 | SHA-1 | DO NOT SHARE THIS INFORMATION! |
| 38 | `2014-01-06T04:59:26Z` | **PASS** | 5/0 | SHA-1 | The work of a private man |
| 39 | `2014-01-06T07:35:27Z` | **PASS** | 3/0 | SHA-1 | Welcome. |
| 40 | `2014-01-07T03:00:31Z` | **PASS** | 3/0 | SHA-1 | IDGTK UMLOO ARWOE RTHIS UTETL HUTIA TSLLO |
| 41 | `2014-01-07T03:16:41Z` | **PASS** | 6/0 | SHA-1 | 775d0481115f6e4f3ba8873ac66da1df6bbe3ff19389878f2ddb9423881b |
| 42 | `2014-01-07T03:16:44Z` | **PASS** | 3/0 | SHA-1 | 4dd1c8afafceed237cca8a334b24fe09069e3771e416a749687af002b4de |
| 43 | `2014-01-07T03:16:48Z` | **PASS** | 2/0 | SHA-1 | 17a1e10393d3c62b0e2c2d59ca197f85246746c533bf6d8316f2256679e8 |
| 44 | `2014-01-10T05:42:54Z` | **PASS** | 5/0 | SHA-1 | Let the text guide you. |
| 45 | `2014-01-18T01:03:57Z` | **PASS** | 3/0 | SHA-1 | 4944330300000000002c5449543200000013000000496e746572636f6e6e |
| 46 | `2014-01-19T06:28:06Z` | **PASS** | 7/0 | SHA-1 | Very good. You have done well to come this far. |
| 47 | `2014-01-19T07:39:32Z` | **PASS** | 4/0 | SHA-1 | Create one Tor hidden service that can accept CGI file uploads. |
| 48 | `2014-01-19T07:39:50Z` | **PASS** | 3/0 | SHA-1 | Create one Tor hidden service that can accept CGI file uploads. |
| 49 | `2014-01-19T07:39:57Z` | **PASS** | 2/0 | SHA-1 | Create one Tor hidden service that can accept CGI file uploads. |
| 50 | `2014-01-25T08:26:57Z` | **PASS** | 3/0 | SHA-1 | Hello. You have done well to come this far. |
| 51 | `2014-04-02T08:49:51Z` | **PASS** | 19/0 | SHA-1 | Hello. Your enlightenment awaits you. |
| 52 | `2015-07-28T05:12:39Z` | **PASS** | 6/0 | SHA-1 | Some news organisations have recently claimed that "3301" is |
| 53 | `2016-01-01T00:01:07Z` | **PASS** | 2/0 | SHA-1 | Hello. |
| 54 | `2017-04-04T23:23:28Z` | **PASS** | 9/0 | SHA-512 | Beware false paths. Always verify PGP signature from 7A35090F. |

Full per-file detail — path, sha256, byte length, raw gpg status lines, signature packet —
is in `PGP-VERIFICATION-TABLE.json`; the per-message grouping is in `MESSAGES.json`.

### 3b. A toolchain fingerprint in the hash column

The `hash` column is not decoration. Across all 54 messages the digest algorithm is: **SHA-1 × 53**, **SHA-512 × 1**.

Every message from 2012-01-05 to 2016-01-01 is signed with **SHA-1**. The last message,
2017-04-04, is signed with **SHA-512**. The signing setup changed exactly once, near the end.

SHA-1 was GnuPG's compiled-in default `personal-digest-preference` for the 1.4 / early-2.0 era;
newer builds and any `digest-algo` line in `gpg.conf` move it off SHA-1. So this single switch is a
**dated, verified observation about the author's tooling** — an upgrade, a reinstall, or a config
change somewhere between 2016-01-01 and 2017-04-04 — and it is exactly the kind of artifact Round
18's thesis is looking for (`round18/CAMPAIGN-PLAN.md`: *we are hunting a short script written by a
human being*). Handed to **L1-toolchain** as a prior, not as a conclusion.

Stated honestly: this narrows *when the toolchain changed*. It does not narrow *who*, and it does
not by itself identify a GnuPG version — several versions share these defaults.

## 4. The FAILs

3 files fail. They are **one message**, mirrored three times:

| file | bytes | gpg | sig timestamp | keyid in packet |
|---|---|---|---|---|
| `corpus/A-primary-artifacts/krisyotam/pgp/messages/2013-01-opening-book-code.asc` | 1536 | BADSIG | `2013-01-03T04:33:29Z` | `181F01E57A35090F` |
| `corpus/A-primary-artifacts/pgp/messages/ky_2013-01-opening-book-code.asc` | 1536 | BADSIG | `2013-01-03T04:33:29Z` | `181F01E57A35090F` |
| `corpus/E-tooling/vendor/krisyotam__cicada3301/pgp/messages/2013-01-opening-book-code.asc` | 1536 | BADSIG | `2013-01-03T04:33:29Z` | `181F01E57A35090F` |

**Verdict under the pre-registered rule: transport defect, not a canon failure.** `PREREG.md`
fixed the test in advance — *a FAIL is a finding about the message only if the same body has no
PASSing copy elsewhere, compared by sha256 and normalised body*. Under that comparison this body
**does** pass elsewhere: 4 other files in the tree carry the identical normalised signed text and
verify (row 18 of §3, `copies 4/3`).

The defect is named exactly by gpg's own stderr: `invalid armor header: Welcome again.` The
mirror dropped the blank line that must separate the `Hash: SHA1` armor header from the message,
so the message's first line is parsed as a header and excluded from the hashed data. The repo
already holds a deliberately repaired copy —
`corpus/A-primary-artifacts/pgp/repaired/ky_2013-01-opening-book-code.repaired.asc`, 1538 bytes
against the damaged 1536 — and **it PASSes carrying the identical signature packet**
(`2013-01-03T04:33:29Z`). The text is authentic; three files are damaged in transport.

**So the answer to G-02's question is: of the 54 distinct signed messages held here, 54 verify
against `7A35090F` and 0 do not.** No message the community treats as canon has been shown by
this run to carry a bad signature from an undamaged file.

That is a clean result, and it is also the warning. A **two-byte** whitespace defect turns an
authentic Cicada message into a `BADSIG`. Any solver who runs the repo's own authenticity test
against a casually-mirrored copy will get a false negative and may conclude a real message is a
forgery. Three such files are sitting in this tree right now.

This is a corpus-hygiene finding, not a canon failure: no message that the community treats as
Cicada has been shown here to carry a bad signature from a good file. It is also a warning —
a two-byte transport defect turns an authentic message into a BADSIG, which is exactly how a
real authenticity test gets quietly mis-scored.

## 5. The NO-SIGs — and a truncated-download finding

22 files carry no signature block. They are not one thing:

- **16 files are 199-byte GitHub rate-limit stubs**, not messages at all. Every one is in
  `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/`, and every one contains
  the literal text `429: Too Many Requests`. They were saved by a fetch that did not check its
  HTTP status, and they have sat in the tree since Round 10 looking like a corpus of communications.
  This is the same failure mode as the `_560.00` truncation recorded in `corpus/GAPS.md` **G-12**,
  and it is why that section's re-collection rule exists. The corpus lane already refetched clean
  copies into `corpus/A-primary-artifacts/pgp/messages/`; the stubs under `round10/` were never
  cleaned up and are still reachable by any tool that globs the tree.
- The rest are genuinely unsigned held material: a raw TCP-server transcript, an OutGuess payload
  fragment, and two rune data files that merely use the `.asc` extension.

| file | bytes | what it is |
|---|---|---|
| `corpus/A-primary-artifacts/ibotpeaches/messages/2013/tcp-server.asc` | 3837 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `corpus/A-primary-artifacts/pgp/messages/2014-01-fallen-behind-outguess-08.asc` | 150 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `corpus/E-tooling/vendor/thomasandfriends__Cicada3301Runes/data/runeasc.asc` | 51790 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `corpus/E-tooling/vendor/thomasandfriends__Cicada3301Runes/data/xorrunes.asc` | 58152 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-anonymous-email-enrollment.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-book-code-poem.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-key-in-front-of-you.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-location-numbers.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-patience-check-back.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2012-01-sharing-disqualification.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2013-01-onion-pointer.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2013-01-opening-book-code.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2013-01-rune-table-morse.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-fallen-behind-outguess-08.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-interconnectedness-hex.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-liber-primus-hash-block-outguess-01.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-magic-square-upload-outguess-10.asc` | 54890 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-magic-square-upload-outguess-11.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-magic-square-upload-outguess-13.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-onion-welcome.asc` | 199 | **HTTP 429 stub — not a message** |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2014-01-opening-book-code.asc` | 452 | unsigned held text / data (`.asc` extension, not OpenPGP) |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/2016-01-liber-primus.asc` | 199 | **HTTP 429 stub — not a message** |

## 6. The key files

11 files are public-key blocks. Each was probed with `--import-options show-only`; only
blocks whose primary fingerprint is the canonical one were imported into the verification keyring.

| file | bytes |
|---|---|
| `corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` | 151497 |
| `corpus/A-primary-artifacts/ibotpeaches/other/service/src/key.asc` | 2617 |
| `corpus/A-primary-artifacts/krisyotam/pgp/key/cicada-3301-public-key.asc` | 3057 |
| `corpus/A-primary-artifacts/pgp/keys/cicada-3301-pubkey.keys.openpgp.org.asc` | 2380 |
| `corpus/A-primary-artifacts/pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc` | 154301 |
| `corpus/A-primary-artifacts/pgp/keys/key-local-jaxonkuipers.asc` | 3107 |
| `corpus/E-tooling/vendor/AegisTrustCore__Liber-Primus-HMS-Run-Time/keys/cicada-3301-2012.asc` | 3057 |
| `corpus/E-tooling/vendor/krisyotam__cicada3301/pgp/key/cicada-3301-public-key.asc` | 3107 |
| `corpus/H-branch-recovery/recovered/claude_cicada-3301-scope-cigxzi/liber-primus/analysis/campaign15/cicada_pubkey.asc` | 154301 |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/cicada-3301-public-key.asc` | 3057 |
| `liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/corpus/cicada-3301-public-key.asc` | 3057 |

**One naming hazard worth recording.** `corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc` is named
for the fingerprint `67F3…0670B0E5**7A35090F**`, which is **not** the canonical
`6D85…181F01E5**7A35090F**` — the two agree only in the trailing 32-bit short ID. The block *inside*
the file is the canonical key (verified: primary fpr `6D854CD7933322A601C3286D181F01E57A35090F`),
so the filename is a mislabel rather than a second key. Do not treat the filename as an identifier,
and do not verify anything by short ID: 32 bits is not a key.

## 7. What this table does and does not establish

**Establishes (verified):**
1. Which held files verify against `7A35090F`, by name, with hashes — the thing G-02 says is
   recorded nowhere.
2. That exactly one signing key ID appears across every signed message in the tree.
3. A machine-read timestamp for every signature, including for files that fail to verify.
4. That 19 files in the Round-10 fetch are HTTP error pages rather than communications.

**Does not establish:**
1. *Completeness.* This is a corpus of mirrors of mirrors. A message nobody mirrored is not here,
   and its absence is not evidence. `corpus/GAPS.md` G-12 applies to every byte in it.
2. *Authorship.* A good signature proves the signer held the private key. Nothing more.
3. *Wall-clock truth of any timestamp.* Under RFC 4880 the creation time is a hashed subpacket
   taken from the signer's own clock, and is therefore settable by the signer.
   `liber-primus/analysis/AUDITOR-LOOP-2026-07-28.md` used exactly this to **refute** the
   timezone/working-hours biometric built on these timestamps (n=26, irreproducible). That
   refutation stands and this table does not reopen it.
4. *That the 2023 public self-claim is settled by anything here.* It is out of scope: no `.asc`
   attributable to it is held in this tree, so it is neither confirmed nor refuted by this run.

## 8. Reproduce

```bash
wsl -d Ubuntu -- bash -lc "cd /mnt/c/Users/dukot/projects/cicada3301 && \
  python3 liber-primus/analysis/round18/L8-provenance/verify_all_signatures.py"
python3 liber-primus/analysis/round18/L8-provenance/build_table_md.py
```

The script builds its own keyring from scratch every run and refuses to proceed if that keyring
holds more than the one primary key, so the result cannot be contaminated by the operator's
existing GnuPG state.
