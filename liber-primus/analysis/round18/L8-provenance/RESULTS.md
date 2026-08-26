# L8 — PROVENANCE OSINT · RESULTS

_Round 18. Pre-registration: `PREREG.md` (written before any run). Rules 1, 2, 6, 7, 8 apply._
_Machine work: WSL Ubuntu, GnuPG 2.4.8. All network retrieval 2026-08-26, URLs given per claim._

**Standing constraint honoured throughout:** no person is named as Cicada 3301. This lane produces
an evidence table, not an identity. Public lawful sources only; no breach databases, no
people-search services, no contact with anyone. See §5 for what was declined and why.

---

## Headline

| job | ledger / gap | result |
|---|---|---|
| **1. PGP verification table** | corpus **G-02** ★★★★★ | **Built.** 228 `.asc` files, **192 PASS / 3 FAIL / 22 NO-SIG / 11 KEY**. Grouped to **54 distinct signed messages: 54 verify, 0 do not.** All 3 FAILs are one message, damaged in transport, which PASSes from 4 other copies. **One signing key ID across the entire corpus.** |
| **1b. Timestamps as a dataset** | corpus **G-09** | **Built.** Every verified signature timestamp extracted from the signature packets themselves, plus key creation — ranked seed-candidate list handed to L6. |
| **2. `mruzuki` / `cicadeur`** | **I-01** `never-run` | **Ruled INDECISIVE against a threshold fixed in advance.** Every field the two keys share is a GnuPG factory default; every field a human chose differs. Also **corrects a factual error** in the auditor loop and the ledger. |
| **3. Pre-disclosure search** | **I-03** `never-run` | See §4. |

Two incidental findings that were not the assignment and matter anyway:

- **19 files in `round10/L6-archives/.../comms/` are 199-byte HTTP 429 error pages**, not Cicada
  communications. They have sat in the tree since Round 10 (§1.4).
- **The signing toolchain changed exactly once.** 53 of 54 messages are signed SHA-1; the final
  2017-04-04 message is signed **SHA-512** (§1.5). Handed to L1-toolchain as a dated prior.

---

## 1. Job 1 — the PGP verification table (corpus G-02)

**Deliverables on disk:**

| file | what |
|---|---|
| `PGP-VERIFICATION-TABLE.md` | the human-readable table — instrument controls, counts, per-message rows, FAIL analysis, NO-SIG analysis, key-file hazards, limits |
| `PGP-VERIFICATION-TABLE.json` | full machine record: every file, sha256, byte length, verdict, raw `[GNUPG:]` status lines, gpg stderr, parsed signature packet |
| `MESSAGES.json` | one row per **distinct signed message** (54), with its copies |
| `verify_all_signatures.py` | the instrument, rerunnable from scratch |
| `build_table_md.py` | renders the `.md` and `MESSAGES.json` from the `.json` |

### 1.1 What G-02 asked for, and what it now has

`corpus/GAPS.md` G-02 states it flatly: the signed message texts are quoted in `research/03-*.md`
and `.asc` files sit under `round10/L6-archives/fetched/jaxonkuipers/corpus/`, but *"no file in this
repository records which signatures verify against key `7A35090F` and which do not"* — despite that
being the repo's own declared authenticity test (`KNOWLEDGE.json: authenticity_test`).

**Scope correction, recorded because it changes the size of the job.** G-02 and `corpus/INVENTORY.md:60`
both say **42** `.asc` files at that one path. Enumeration finds **228** `.asc` files across the
repository — 113 distinct by sha256 — spread over `corpus/A-primary-artifacts/` (ibotpeaches,
krisyotam, cijhho123, scream314, the lane-A `pgp/` tree), `corpus/E-tooling/vendor/`,
`corpus/H-branch-recovery/`, and the round10 fetch. This lane verified **all 228**, not the 42.

**Prior work correction, recorded because credit matters and so does the residual gap.**
`corpus/A-primary-artifacts/SIGNATURES.json` (generated 2026-08-20T05:59:05Z by
`corpus/A-primary-artifacts/_tools/verify_sigs.py`) already verified **140** files. That is a day
*after* GAPS.md was compiled (2026-08-19), which is why G-02 does not mention it — the gap register
is stale on this item, and nothing links the two. What that run did not cover: **88 files**,
including the entire `round10/L6-archives/fetched/jaxonkuipers/` tree that G-02 itself points at,
every `corpus/E-tooling/vendor/` mirror, and `corpus/H-branch-recovery/`. It also emitted no
human-readable table and no per-message grouping. This lane is a superset: independent instrument,
independent keyring, whole tree, both formats.

### 1.2 The instrument, and proof it works in both directions

Rule 2: *a null from an unvalidated instrument is not a negative.* Four controls were fixed in
`PREREG.md` before the run and all four were met.

| control | required | measured | met |
|---|---|---|---|
| **C1** untouched known-good file | `GOODSIG 181F01E57A35090F` | `GOODSIG 181F01E57A35090F` | ✅ |
| **C2** one character of the signed body flipped | `BADSIG`, no `GOODSIG` | `BADSIG 181F01E57A35090F`, no `GOODSIG` | ✅ |
| **C3** message signed by a freshly generated foreign key | not `GOODSIG` for 3301 | `NO_PUBKEY` for the foreign keyid, no `GOODSIG` | ✅ |
| **C4** timestamp recovered from the *tampered* file | original `created` unchanged | `1325738763` → `1325738763` | ✅ |

C2 and C3 are what make a FAIL in this table mean anything. C4 is why a file that fails to verify
still yields a usable timestamp for the seed list.

The keyring is **isolated**: a throwaway `GNUPGHOME` built from scratch each run, into which only
key blocks whose *primary* fingerprint is `6D854CD7933322A601C3286D181F01E57A35090F` are imported.
The script aborts if the resulting keyring holds any other primary key, so a PASS cannot be
produced by the operator's ambient GnuPG state.

### 1.3 Counts

| verdict | files | meaning |
|---|---|---|
| **PASS** | **192** | `GOODSIG` + `VALIDSIG` for the canonical fingerprint |
| **FAIL** | **3** | a signature packet is present and does not verify |
| **NO-SIG** | **22** | no signature block in the file at all |
| **KEY** | **11** | public-key block, not a message |
| total | **228** | |

Deduplicated to distinct signed texts: **54 messages, 54 PASS, 0 FAIL.**

**The single most load-bearing line:** across every signed message in the repository the set of
signing key IDs has size **1** — `181F01E57A35090F`. No second key appears anywhere, in any mirror,
in any era. The corpus is internally consistent with one keyholder from 2012-01-05 to 2017-04-04.
`verified`.

Verified signature timestamps: **54 distinct**, spanning `2012-01-05T03:46:03Z` →
`2017-04-04T23:23:28Z` (1916 days).

### 1.4 The FAILs, and the NO-SIGs

**The 3 FAILs are one message** — the 2013-01-03 "Welcome again." book-code message — mirrored into
three files (`krisyotam/pgp/messages/2013-01-opening-book-code.asc`,
`pgp/messages/ky_2013-01-opening-book-code.asc`, and the `E-tooling/vendor/krisyotam__cicada3301`
copy), all 1536 bytes.

Under the rule fixed in `PREREG.md` — *a FAIL is a finding about the message only if the same
normalised body has no PASSing copy elsewhere* — this is a **transport defect, not a canon
failure**: 4 other files carry the identical normalised signed text and verify.

gpg names the defect itself: `invalid armor header: Welcome again.` The mirror dropped the blank
line that must separate the `Hash: SHA1` armor header from the message body, so the message's first
line is parsed as a header and excluded from the hashed data. The repo already holds a repaired
copy (`corpus/A-primary-artifacts/pgp/repaired/ky_2013-01-opening-book-code.repaired.asc`, 1538
bytes against 1536) and **it PASSes carrying the identical signature packet**, `2013-01-03T04:33:29Z`.

So: **no message the community treats as canon carries a bad signature from an undamaged file in
this corpus.** That is a clean answer to G-02's question — and it is also the warning. A **two-byte**
whitespace defect turns an authentic Cicada message into a `BADSIG`. Anyone running the repo's own
authenticity test against a casually mirrored copy gets a false negative and may conclude a genuine
message is a forgery. Three such files are in this tree right now.

**19 of the 22 NO-SIGs are not messages at all.** Every one is 199 bytes, every one lives in
`liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/`, and every one contains the
literal text `429: Too Many Requests / For more on scraping GitHub…`. They were written by a fetch
that never checked its HTTP status and have sat in the tree since Round 10 with filenames like
`2012-01-book-code-poem.asc`. This is the same failure mode as the `_560.00` truncation recorded in
`corpus/GAPS.md` **G-12**, and it is a live hazard: any tool that globs `**/*.asc` picks them up as
communications. (The corpus lane did later refetch clean copies into
`corpus/A-primary-artifacts/pgp/messages/`; the stubs were never removed.) The remaining 3 NO-SIGs
are genuinely unsigned held material — a TCP-server transcript, an OutGuess payload fragment, and
two rune data files that merely use the `.asc` extension.

**One key-file naming hazard.** `corpus/A-primary-artifacts/ibotpeaches/keys/67F363C61BA8FB6FDBA9C47D0670B0E57A35090F.asc`
is named for a fingerprint that is **not** the canonical one — the two agree only in the trailing
32-bit short ID `7A35090F`. The block inside the file *is* the canonical key (probed: primary fpr
`6D854CD7933322A601C3286D181F01E57A35090F`), so the filename is a mislabel, not a second key. Two
consequences: do not treat that filename as an identifier, and **do not verify anything by short
ID** — 32 bits is not a key, and the repo's own shorthand "7A35090F" should always be resolved to
the full fingerprint before it is used as a test.

### 1.5 A dated toolchain fingerprint, free of charge

The digest algorithm across the 54 messages is **SHA-1 × 53, SHA-512 × 1**. Every message from
2012-01-05 to 2016-01-01 is SHA-1. The last message, 2017-04-04, is SHA-512.

SHA-1 first is the GnuPG 1.4/2.0 compiled-in default (sourced in §3.2). GnuPG 2.1+ and any explicit
`personal-digest-preferences` move off it. So the signing setup **changed exactly once, between
2016-01-01 and 2017-04-04** — an upgrade, a reinstall, or a config change.

This is `verified` and it is dated. It is exactly the shape of artifact Round 18's thesis is hunting
(*"a person sat down and wrote a program … programs leave fingerprints in their artifacts"*).
Handed to **L1-toolchain** as a prior. Stated honestly: it narrows *when the toolchain changed*. It
does not narrow *who*, and it does not by itself pin a GnuPG version — several share these defaults.

---

## 2. Job 1b — timestamps as a ranked seed-candidate dataset (corpus G-09)

**Deliverable:** `TIMESTAMP-SEED-CANDIDATES.json` (generator: `build_seed_candidates.py`).

### 2.1 Why this is a cryptanalytic contribution and not trivia

Round 8 enumerated **every unix second of 2011–2015** for 10 generators — 2.52 × 10⁹ decodes — and
treated all seconds as equally likely. They are not. A person seeding an RNG types a number they
have in front of them, and §1 just produced, machine-verified, the exact set of numbers **this
author's own machine wrote down**: 54 signature-packet creation times plus the key-creation second.

That converts a uniform sweep into a **ranked prior**. It is the cheapest possible thing for a seed
lane to try first, and until now it did not exist because — per G-09 — the signature timestamps
were *"recorded in prose only"*.

### 2.2 What was built

| | |
|---|---|
| source timestamps | **59** — 57 `verified`, 2 `reported` |
| verified sources | 54 distinct signature creation times + the `7A35090F` primary-key, subkey and UID self-sig second (all `1325734783`) |
| reported sources | 2 puzzle dates from `KNOWLEDGE.json` (date only, no authenticated second) — kept separate and ranked last |
| candidates emitted | **433** |
| tier A / B / C / D | **54 / 107 / 260 / 12** |
| top-ranked candidate | **`1325734783`** — `2012-01-05T03:39:43Z`, the second in which the 3301 primary key, its subkey and its UID self-signature were all created |

Tiers, per the ranking rule fixed in `PREREG.md`:

- **A** — `verified` + author's own machine + the **exact** second. The 54 raw seconds. Try these first.
- **B** — the same, ±1 (off-by-one at the point the number was copied).
- **C** — the same, truncated to minute/hour/day or reformatted as `YYYYMMDD` / `YYYYMMDDHHMMSS` / milliseconds.
- **D** — anything resting on a `reported` rather than machine-verified timestamp.

Every entry carries per-entry provenance: `provenance_class`, `authorship_proximity`, the derivation
form and why, the source timestamp it came from, the evidence for that timestamp, the source
path/URL, and a retrieval date. Entries reachable from more than one source record all of them and
inherit the best rank.

### 2.3 Limits, stated up front

- **This lane ran none of them.** The list is a prior, not a result, and not a keyspace.
- **Absence is not exclusion.** A seed missing from this list is not ruled out by being missing.
- **The derivation set is fixed.** It was set in `PREREG.md` and was not extended after seeing
  results — which is the only reason a future negative against it will mean anything.
- **The spoofability confound, declared before running.** An RFC 4880 creation time is a hashed
  subpacket from the signer's own clock, so the signer can set it.
  `AUDITOR-LOOP-2026-07-28.md` used exactly that to **refute** the timezone/working-hours biometric
  built on these timestamps (n=26, irreproducible), and that refutation stands here. It does not
  weaken this list, because the two uses are different: a spoofed timestamp is worthless as evidence
  *about a person*, but it is still a number the author **chose and typed** — which is precisely the
  property that makes it a plausible `srand()` argument.
- **Deliberately excluded:** the `mruzuki` key's timestamps. Nothing ties that key to the author
  (§3), so including them would smuggle a `speculated` link into a ranked prior.

---

## 3. Job 2 — I-01, `mruzuki` / `cicadeur`

**Deliverables:** `KEY-COMPARISON.json`, `compare_keys.py`, `fetch_baserate.sh`, and the raw
keyserver exports under `evidence/`.

### 3.1 What was retrieved, and from where

| item | value | class | source | retrieved |
|---|---|---|---|---|
| key exists on a public keyserver | yes, 2143 bytes armored | **verified** | `https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x02BD208AFB8AFF75&options=mr` | 2026-08-26 |
| full fingerprint | `05A85948E01B4ACE3E4E14ED02BD208AFB8AFF75` | **verified** | same, `op=index&options=mr,json` | 2026-08-26 |
| UID | `mruzuki (cicadeur) <mruzuki@gmail.com>` | **verified** | same | 2026-08-26 |
| key created | `2012-01-12T22:43:32Z` (unix 1326408212) | **verified** | packet dump | 2026-08-26 |
| algorithm | RSA 2048 primary + RSA 2048 subkey, both same second | **verified** | packet dump | 2026-08-26 |
| **self-sig carries `key expires after 1d0h0m`** | expiry `2012-01-13T22:43:32Z` | **verified** | packet dump + `op=vindex` | 2026-08-26 |
| self-revoked | `2012-01-22T06:35:04Z`, sigclass `0x20` | **verified** | packet dump | 2026-08-26 |
| revocation reason subpacket | `0x03` = *key is no longer used* | **verified** | packet dump | 2026-08-26 |
| web-of-trust edges | **zero** — the only signatures on the key are its own | **verified** | `op=vindex`, `op=index&options=mr,json` | 2026-08-26 |
| not on keys.openpgp.org | HTTP 404 | **verified** | `https://keys.openpgp.org/vks/v1/by-keyid/02BD208AFB8AFF75` | 2026-08-26 |

### 3.2 The comparison — a falsifiable technical claim, and its answer

Pre-registered threshold (`PREREG.md` §Job 2): **MATCH** = identical ordered preference lists *and*
identical self-sig hash algo *and* identical key-flag/feature bytes. **MISMATCH** = any ordered
preference list differs. **INDECISIVE** = preferences agree but are the era default of a common
client, so the agreement carries no discriminating information.

| field | 3301 `7A35090F` | mruzuki `FB8AFF75` | same? | who chose it |
|---|---|---|---|---|
| key version | 4 | 4 | = | software |
| public-key algorithm | RSA (1) | RSA (1) | = | operator |
| **primary key size** | **4096** | **2048** | **✗** | **operator** |
| **subkey size** | **4096** | **2048** | **✗** | **operator** |
| key created (UTC) | 2012-01-05T03:39:43Z | 2012-01-12T22:43:32Z | ✗ | clock |
| self-sig digest algo | 2 (SHA-1) | 2 (SHA-1) | = | software |
| key flags (primary) | `03` | `03` | = | software |
| **expiry policy** | **none** | **1 day** | **✗** | **operator** |
| pref-sym-algos | `9 8 7 3 2` | `9 8 7 3 2` | = | software default |
| pref-hash-algos | `8 2 9 10 11` | `8 2 9 10 11` | = | software default |
| pref-zip-algos | `2 3 1` | `2 3 1` | = | software default |
| features (MDC) | `01` | `01` | = | software default |
| keyserver prefs | `80` (no-modify) | `80` (no-modify) | = | software default |
| **revoked** | **no** | **2012-01-22T06:35:04Z** | **✗** | **operator** |
| revocation reason | — | `0x03` *no longer used* | ✗ | operator |

**Verdict: INDECISIVE.**

The reason is the point, and it is checkable rather than asserted. GnuPG 1.4.x / 2.0.x, with no
`default-preference-list` in `gpg.conf`, builds its preference set in
`keygen_set_std_prefs()` as `S9 S8 S7 S3 S2` / `H8 H2 H9 H10 H11` / `Z2 Z3 Z1`, with
`int mdc=1, modify=0;` giving features `01` and keyserver-prefs `80`. Those are **exactly** the
values both keys carry.
Source: `https://raw.githubusercontent.com/gpg/gnupg/gnupg-1.4.16/g10/keygen.c` (function
`keygen_set_std_prefs`, the `if (!string || …"default")` branch), retrieved 2026-08-26 — `verified`.

So the "match" says only this: *both keys were made by running `gpg --gen-key` on an era-standard
build and not touching the preference list.* In January 2012 that describes most new OpenPGP keys
on Earth. It is not a link, and reporting it as one would be precisely the error `AGENTS.md` §1
warns about.

**The honest one-line summary: where the software chose, the two keys agree; where a human chose,
they differ.** Key size, expiry policy, and whether to revoke are the operator's decisions, and all
three diverge — a permanent 4096-bit key that was never revoked versus a 2048-bit key created with
a **one-day** lifetime and revoked ten days later as *"no longer used"*.

**Base-rate control: attempted, under-powered, and NOT used for the verdict.** Four public *project*
release keys were retrievable (Tor Browser Developers, Bitcoin Core, GnuPG release, Tails); none was
created in January 2012 (2010, 2014, 2014, 2015) and none carries the `8 2 9 10 11` list. That
sample cannot establish a 2012 base rate, and there is a second confound that would sink it anyway:
a live key's UID self-signature is **reissued** whenever the key is edited or extended, so a
keyserver copy shows the preferences of the last edit rather than of creation — which is exactly why
the 2010-created key in the sample shows the modern GnuPG 2.1+ list. The verdict was decided from
the GnuPG source default instead. A properly matched control needs keys whose self-sigs are frozen
in 2012 (abandoned or revoked keys); this lane did not source one.

### 3.3 A factual correction to the auditor loop and the ledger

`liber-primus/analysis/AUDITOR-LOOP-2026-07-28.md` and `LEDGER.json` entry **I-01** both describe
the key as *"created 2012-01-12, self-revoked 2012-01-22 — **seven days after the first 3301
image**"*. The arithmetic does not work: the first 3301 image is 2012-01-04, so the revocation is
**18** days after it and the creation is **8** days after it.

Seven days is, however, exactly the gap between **3301's key creation (2012-01-05)** and
**mruzuki's key creation (2012-01-12)**. That is almost certainly the fact that was meant, and it
got attached to the wrong anchor and the wrong event on the way into the register. The corrected
statement, `verified` from the packet timestamps: *the mruzuki key was created seven days after the
3301 key, and revoked ten days after that.*

Worth stating plainly because a mis-stated seven-day coincidence is the kind of detail that
hardens into a "lead" through repetition.

### 3.4 What is genuinely new here, and what it is not

New and `verified`: the **1-day self-expiry**. This was not in the auditor's description and it
changes how the key reads. This was not a key that happened to be abandoned — it was **built to
die within 24 hours**, on the day it was made. The later revocation packet is a tidy-up of a key
that had already expired eight days earlier. Combined with zero WoT edges, that is the same
*designed-anonymity* signature the 2026-07-28 auditor identified as the strongest supportable
conclusion about this whole case.

Not new, and not claimed: any connection to Cicada 3301 beyond (a) a handle containing "cicadeur"
and (b) temporal adjacency. There is no signature, no key-material relationship, no WoT path, and —
per §3.2 — no toolchain discriminator. **`speculated`, and this lane does not upgrade it.**

---

## 4. Job 3 — I-03, pre-disclosure search

**Result: NEGATIVE, with a measured coverage bound — and the bound is the interesting part.**

Campaign VIII called this its #1 open thread and recorded it as *"unresolved only because the
archives are thin, not because it was cleared."* It was never executed as a search. It has now been
executed, and the archives turn out not to be *thin* in the way that sentence implies. Two of the
three named lists **did not have a public archive covering the pre-disclosure window at all**, for
reasons that are documented and checkable.

**Deliverables:** `evidence/archives/` — the retrieved monthly mbox archives, `fetch-log.txt`
(every URL with its HTTP status and byte count), `grep-results.txt` (per-term hit counts and the
matching lines), `wayback-cdx.txt`, `supplementary-probes.txt`. Scripts: `predisclosure_search.sh`,
`grep_archives.sh`, `wayback_probe.sh`, `probe_hosts.sh`.

### 4.1 Method — grep the corpus, do not trust an index

The pre-registered terms were run against the **actual monthly mbox archives**, downloaded and
searched locally with `zgrep -aiE`, rather than against a search engine's view of them. A grep over
the real corpus is reproducible and its silence is a measurable bound; a search-engine miss is not
evidence of anything. Where only search engines were available (bitcointalk), the finding is
labelled `reported` and downgraded accordingly.

Window: **2011-01-01 → 2012-01-04** for the hard test (first 3301 image), extended to 2013-12-31
for context.

Terms, exactly as fixed in `PREREG.md`: `3301`, `845145127`, `cicada`, `instar`,
`highly intelligent individuals`, `liber primus`, `futhorc`, `futhark`, `anglo-saxon rune`,
`runic cipher`, `mabinogion`, `outguess`, `a2e7j6ic78h0j`, `onion.*puzzle`, `gematria`,
`totient.*cipher`, plus `mruzuki` and `cicadeur` from §3.

### 4.2 metzdowd — the cryptography list

| claim | class | evidence |
|---|---|---|
| The pipermail index offers, for 2010–2013, only `2010-March`…`2010-October`, **`2011-August`**, then nothing until `2013-June` | **verified** | index page grepped, `https://www.metzdowd.com/pipermail/cryptography/`, 2026-08-26 |
| Every other month in the window returns HTTP 404 | **verified** | `evidence/archives/fetch-log.txt` — 36 months attempted, 8 returned 200 |
| `2011-August` is the list's **relaunch** month: Perry Metzger's test posts of 7 Aug 2011, subject *"The Cryptography and Security mailing list has been [relaunched]"* | **verified** | `zcat 2011-August.txt.gz`, headers |
| Zero hits for any pre-disclosure term in `2011-August` | **verified** | `grep-results.txt` |
| Every Cicada hit in the whole retrieved corpus is in `2013-November` | **verified** | `grep-results.txt` |
| Those hits are one message: Eugen Leitl forwarding the Telegraph article, **Wed 27 Nov 2013 15:08:08 +0100**, `Message-ID: <20131127140808.GC10793@leitl.org>` | **verified** | headers extracted from the mbox |

So the list carried **no** Cicada-adjacent traffic before the puzzle, and its first mention came
**23 months after** the puzzle began, second-hand, from a newspaper. The archive is not thin because
captures were lost — **the list was dormant** across almost the whole window. That is a much
stronger statement than Campaign VIII's, and it is checkable.

### 4.3 cypherpunks

| claim | class | evidence |
|---|---|---|
| The cpunks.org pipermail archive's earliest monthly file is **2013-August**; earliest message permalink seen is `2013-August/000198.html` | **verified** | Wayback CDX, `wayback-cdx.txt`; 36 monthly fetches all non-200, `fetch-log.txt` |
| `al-qaeda.net/pipermail/cypherpunks*` — the host that carried the list in 2011–2012 — has **zero** Wayback CDX rows; live probe returns HTTP 403 | **verified** | `wayback-cdx.txt`, `probe-hosts` output |
| `cypherpunks.venona.com` live probe returns HTTP 522 (origin down) | **verified** | probe output, 2026-08-26 |
| The principal public mirror states plainly that it covers **1992 → early 1999** and that archives for **2000–2013 are not available**, and that its maintainers are *"actively seeking"* them | **verified** | `https://mailing-list-archive.cryptoanarchy.wiki/`, retrieved 2026-08-26 |

**There is no public cypherpunks archive covering 2011–2012 to search.** That is the finding. It is
not a null result from a search; it is the absence of the instrument. Recorded plainly so nobody
records I-03's cypherpunks half as *searched and clear* — it is **unsearchable from public sources
as of 2026-08-26**, which is a completely different state and has a completely different reopening
condition.

### 4.4 bitcointalk

| claim | class | evidence |
|---|---|---|
| The earliest bitcointalk thread about Cicada 3301 located is `topic=347716`, *"What is Cicada 3301?"*, first post **2013-11-26 16:43:36**, opening with a link to the Telegraph article | **verified** (thread page read directly) | `https://bitcointalk.org/index.php?topic=347716.0`, retrieved 2026-08-26 |
| No bitcointalk thread predating 2012-01-04 mentioning any pre-registered term was surfaced | **reported** — search-engine coverage only, no local corpus | domain-restricted searches, 2026-08-26 |
| No pre-2012 occurrence of the string `845145127` was surfaced anywhere | **reported** — search-engine coverage only | web search, 2026-08-26 |
| `845145127.com` has **zero** Wayback captures (CDX query completed, returned no rows) | **verified** | CDX, 2026-08-26 |

Note the convergence: bitcointalk's first mention (2013-11-26) and the cryptography list's first
mention (2013-11-27) are **one day apart and both are the same newspaper article**. Two separate
technical communities that a Cicada-adjacent insider would plausibly inhabit had the puzzle on their
radar only when a mainstream paper put it there, nearly two years in.

### 4.5 Verdict against the pre-registered decision rule

- **HIT**: none. No dated, archive-attested post referencing a Cicada-specific element before its
  disclosure date was found in any searched corpus.
- Every hit in the machine-searched corpus is **post-disclosure and traceable to one 2013 news
  article**. Under the anti-motivated-reasoning clause fixed in `PREREG.md`, none is a hit.
- The result is therefore a **bound**: *searched the metzdowd cryptography archive (all 8 monthly
  mbox files that exist for 2011–2013, ~1.8 MB, 18 terms, `zgrep -aiE`), the cpunks.org cypherpunks
  archive (no file exists before 2013-August), and bitcointalk via domain-restricted search; window
  2011-01-01 → 2012-01-04 hard, → 2013-12-31 for context; nothing.*

**This is not a clearance and this lane does not report it as one.** For the highest-weight lens in
the whole attribution question, the honest 2026-08-26 state is: *the cryptography list was dormant,
the cypherpunks archive for the window does not publicly exist, and bitcointalk was only reachable
through a search index.* Campaign VIII's instinct was right; what it lacked was the measurement.

### 4.6 What would reopen it

1. **A cypherpunks 2000–2013 archive surfacing.** The cryptoanarchy.wiki maintainers say they are
   looking for exactly this. If it appears, `grep_archives.sh` runs against it unchanged — the term
   set is already fixed, so the result would be immediately comparable to this one.
2. **A local bitcointalk corpus** (the forum's own search, or a database dump) replacing the
   search-engine layer, which would upgrade §4.4's `reported` rows to `verified`.
3. **4chan /b/ and /x/ archives for 2011.** Not covered here at all; 4plebs' /x/ coverage begins
   well after the window and no 2011 corpus was located.
4. **Any archive that carries per-post dates for a technical forum of the era** — sci.crypt,
   Freenode IRC logs, the `full-disclosure` list.

---

## 5. What this lane declined to do, on purpose

The 2026-07-28 auditor's own #1 remaining item was a **breach-DB / people-search lookup on
`mruzuki@gmail.com`**. `PREREG.md` declined it in advance and this lane did not run it.

That is a scope decision, not a failure to find something, and it is recorded so nobody re-reads it
as an untried lead. Resolving a private individual's identity from a puzzle handle is not a
cryptanalytic result, it is not lawful-public-sources work, and the repository's standing position
(`AGENTS.md` §1, `KNOWLEDGE.json: attribution`) is that no falsifiable attribution exists — a
name obtained that way would still not be evidence, because it would carry no cryptographic proof
of key control. The falsifiable version of the question is the packet comparison in §3.2, and it
was run.

---

## 6. Coverage, non-coverage, and reopening conditions

Rule 6: *report coverage, not conclusion.*

| | covered | **not covered** | reopens if |
|---|---|---|---|
| **G-02** PGP table | All 228 `.asc` in the repo, 113 distinct by sha256, 54 distinct signed bodies, verified under GnuPG 2.4.8 against an isolated single-key keyring with 4 passing controls; `.md` + `.json` + per-message grouping | **Completeness of the corpus** — this verifies what we hold, and everything we hold is a mirror-of-a-mirror (G-12). Detached `.sig` files and inline signatures on non-`.asc` carriers were not enumerated. The 2023 public self-claim is untouched: no `.asc` for it is held. Wall-clock truth of timestamps, and authorship, are outside what a signature can show | Any new `.asc` enters the tree; a claimed message is recovered from an archive; a non-`.asc` carrier survey is run; an independent verifier disagrees with a row |
| **G-09** seed prior | Every verified signature-packet time plus the canonical key's creation second → 433 ranked candidates, 4 tiers, per-entry provenance | **No seed was run** — coverage of the candidates is zero by design. Onion post times, 4chan/Twitter post times, image-dump and CicadaOS file mtimes: none sourced. The general chronological timeline G-09 also asks for is not built | A seed lane runs tier A and states its generators and offsets; or an authenticated onion post time is recovered |
| **I-01** mruzuki | Full public keyserver material (armored key, `op=index` JSON, `op=vindex` signature graph, keys.openpgp.org lookup); 15-field packet comparison against 7A35090F; era-default resolved from GnuPG's released source | **Identity — declined in advance and not attempted** (§5). Archived mentions of the handles `mruzuki` / `cicadeur` not searched. Other keyservers not queried. Keyserver upload-time logs not obtainable via public HKP. A properly matched 2012-frozen base-rate population not sourced | A message signed by `02BD208AFB8AFF75` is recovered; an archived post ties the handle to a Cicada-specific fact before its disclosure; a 2012-frozen key population becomes available; a keyserver upload-time record surfaces |
| **I-03** pre-disclosure | metzdowd: all 8 monthly mbox files that exist for 2011–2013, 18 terms, local `zgrep`. cypherpunks: existence and coverage of every public mirror probed. bitcointalk: earliest Cicada thread read directly | **The cypherpunks 2011–2012 archive does not publicly exist** — that half is *unsearchable*, not searched-and-clear. bitcointalk rests on a search index, not a local corpus (`reported`). 4chan /b/ and /x/ 2011: not covered at all. sci.crypt, full-disclosure, Freenode logs: not covered | A cypherpunks 2000–2013 archive surfaces; a local bitcointalk corpus becomes available; a 2011 4chan corpus is located; any dated technical-forum archive of the era is added |

### 6.1 Instrument controls, in one place

| control | lane | met |
|---|---|---|
| C1 known-good file verifies | G-02 | ✅ |
| C2 one-character body tamper → `BADSIG` | G-02 | ✅ |
| C3 foreign-key signature → no `GOODSIG` for 3301 | G-02 | ✅ |
| C4 timestamp survives tamper | G-02 | ✅ |
| keyring isolation enforced in code (aborts on any extra primary key) | G-02 | ✅ |
| I-01 discrimination base rate | I-01 | ❌ **under-powered, reported as such, not used for the verdict** (§3.2) |
| I-03 corpus is the real mbox, not a search index | I-03 | ✅ for metzdowd; ❌ for bitcointalk, which is labelled `reported` |

### 6.2 Corrections this lane makes to existing repo files

1. **`corpus/GAPS.md` G-02 is stale.** It says the verification status is recorded nowhere; a
   140-file verification (`corpus/A-primary-artifacts/SIGNATURES.json`) landed 2026-08-20, one day
   after GAPS.md was compiled. The gap is real but smaller than stated, and nothing cross-links the
   two. (§1.1)
2. **`corpus/GAPS.md` G-02 and `corpus/INVENTORY.md:60` both say "42 `.asc` files".** The repo-wide
   count is **228**. (§1.1)
3. **`AUDITOR-LOOP-2026-07-28.md` and `LEDGER.json` I-01 mis-date the mruzuki key.** "Seven days
   after the first 3301 image" does not hold for either its creation or its revocation; seven days
   is the gap between the two **key creations**. (§3.3)
4. **19 files under `round10/L6-archives/fetched/jaxonkuipers/comms/` are HTTP 429 error pages**
   masquerading as communications, still glob-reachable. (§1.4)
5. **Do not verify by short ID.** `7A35090F` is 32 bits, and the tree already contains a key file
   *named* for a different fingerprint sharing that short ID. Resolve to the full fingerprint
   before using it as a test. (§1.4)

### 6.3 Standing verdict, unchanged

Nothing in this lane identifies anyone, and nothing in it should be read as narrowing who Cicada
3301 is. The repository's position holds: **no falsifiable attribution exists.** What the lane adds
is a machine-checked authenticity table where there was prose, a ranked seed prior where there was a
uniform sweep, one falsifiable technical question about the mruzuki key answered `INDECISIVE` for a
reason that is itself checkable, and a measured bound on the pre-disclosure archives in place of an
assumption about them.

---

## 7. Addendum — Round 19 lane C3, 2026-08-26

_Appended, not merged: §§1–6 above were completed by a concurrent Round-18 continuation and are
left exactly as written. C3 (`analysis/round19/C3/`) re-derived this lane's table independently and
this section records only what C3 **adds**, **converges with**, or **corrects**. Full C3 record:
[`round19/C3/RESULTS.md`](../../round19/C3/RESULTS.md); machine summary
`round19/C3/out_l8_provenance.json`; ledger fragments `round19/C3/ledger.json`._

### 7.1 The table reproduces exactly — independent re-derivation

C3 did **not** read `PGP-VERIFICATION-TABLE.json` as evidence. It re-ran
`verify_all_signatures.py` from a fresh isolated `GNUPGHOME` under GnuPG 2.4.8 over the whole
repository, then diffed the result against this lane's stored table **file by file**.

| | C3 run | this lane | on the 228 files **both** runs saw |
|---|---:|---:|---|
| files scanned | 238 | 228 | 228 |
| PASS | 192 | 192 | **192 = 192** |
| FAIL | 3 | 3 | **3 = 3** |
| NO-SIG | 27 | 22 | **22 = 22** |
| KEY | 16 | 11 | **11 = 11** |
| distinct signing key IDs | 1 — `181F01E57A35090F` | 1 | identical |

**Verdict changed on a shared file: 0. sha256 changed on a shared file: 0. Files present here and
missing from C3: 0.** All four controls **C1–C4 met in the independent run**, including the two
that matter — **C2** (one flipped body character ⇒ `BADSIG`, no `GOODSIG`) and **C3** (a
freshly-generated foreign key ⇒ `NO_PUBKEY`, no `GOODSIG` for 3301).

The 10 extra files C3 scanned are fully accounted for and are **not** Cicada corpus: they are this
lane's *own* `evidence/` artifacts, fetched **after** its verification run — seven third-party
project keys under `evidence/baserate/`, the two `mruzuki` keyserver exports, and one zero-byte
`.asc`. Excluding them the two runs are identical in every field.

### 7.2 **FOUND-ERROR** — L1's `46/46` GnuPG fingerprint, and R1's convergent finding

§1.5 hands L1-toolchain a dated toolchain fingerprint. C3 checked the claim L1 built its prior on
— finding **F6**: *"46/46 curated 3301 PGP messages, 2012→2014, are `GnuPG v1.4.11 (GNU/Linux)`"*,
supporting *"one environment, three years, no drift"*. Measured over the same directory
(`corpus/A-primary-artifacts/ibotpeaches/messages/`):

| | |
|---|---|
| PASSing files there | **56**, not 46 |
| distinct signature timestamps | **54** |
| actual span | **2012-01-05 → 2017-04-04**, not 2012→2014 |
| armor `Version:` strings | **53 × `GnuPG v1.4.11 (GNU/Linux)`, 2 × `GnuPG v1`, 1 × `CicadaPG v.3301`** |

Repo-wide per **distinct message**: 54 × `v1.4.11 (GNU/Linux)` (2012-01-05 → **2014-04-02**),
2 × `GnuPG v1` (2015-07-28, 2016-01-01), 1 × `CicadaPG v.3301` (2017-04-04).

**Three consequences.**

1. F6's denominator and window are both wrong, and the window truncates the span at exactly the
   point where the version string changes. The claim is true *inside* its window; the headline
   drawn from it is contradicted by the same directory's own later files.
2. **The signing toolchain changed twice, not once.** §1.5 dates one change from the *digest
   algorithm* (SHA-1 × 53 → SHA-512 × 1 at 2017-04-04). The armor `Version:` header shows an
   **earlier, independent** change between **2014-04-02 and 2015-07-28**. Two dated transitions
   from two independent fields; the later is corroborated by both. §1.5's "exactly once" should be
   read as "exactly once *in the digest field*".
3. **`CicadaPG v.3301` is hand-set** — no GnuPG build emits it. It is a customised armor version
   on the final 2017-04-04 message, which is also the only SHA-512 one.

**L1's conclusion survives and the correction sharpens it:** the 1.4.11 environment is now attested
over **2012-01-05 → 2014-04-02, 818 days**, covering the entire Liber Primus release window.

**Independent convergence — cite R1.** Round 19's red-team lane reached the same defect in L1's
prior from the *render and packaging* side: a **non-ImageMagick** chain (Ghostscript → PIL with
`quality="keep"`) reproduces **all four** of LP2's discriminating JPEG fields, and **GnuPG 1.4.11
shipped in at least six OS generations including Ubuntu 12.10 — outside L1's stated 11.04–12.04
bracket** (`round19/R1/RESULTS.md` §C). Two lanes, two independent evidence bases — one physical,
one cryptographic — landing on the same conclusion: **L1's environment bracket is narrower than its
evidence supports.** That matters because L1's prior is what justifies Round 19's entire Phase 1.

*Recommended, outside C3's write scope: correct F6/F7's numbers and window in
`round18/L1-toolchain/RESULTS.md` §6 and its ledger entry, marking the old figures superseded
rather than deleting them.*

### 7.3 The Perl fact this corpus has been carrying all along

§1.5 mines the corpus for toolchain fingerprints and finds the digest algorithm. There is a much
stronger one in the same files, and no lane in this repository had cited it.

**Four files in the verification table mention `Crypt::RSA`. They are two distinct messages, and
all four PASS** against `181F01E57A35090F`:

| date (from the signature packet) | verdict | carries |
|---|---|---|
| **2012-01-15T01:39:42Z** | **PASS** | the prose claim, plus `Version: 1.99` / `Scheme: Crypt::RSA::ES::OAEP` |
| **2014-01-06T07:35:27Z** (3 mirrors) | **PASS** × 3 | `Version: 1.99` / `Scheme: Crypt::RSA::ES::OAEP` |

The 2012-01-15 message — ten days after the first 3301 image — says, over a signature that
verifies:

> "Here is a message that has been encrypted with RSA (the Crypt::RSA Perl module available in
> CPAN)"

and then pastes the public key **as Perl `Data::Dumper` output** — `$VAR1 = bless( { 'e' => 65537,
'n' => '...', 'Version' => '1.99' }, 'Crypt::RSA::Key::Public' );`. That `$VAR1 = bless(...)` form
is literally `Data::Dumper`'s default emission, so the author ran a Perl script, dumped a live
`Crypt::RSA::Key::Public` object, and pasted the dump into a message they then signed.

**Three independent Perl signals inside one PASSing artifact** — a prose claim, the library's own
machine-emitted armor (the module version is pinned by the library itself at **1.99**), and
`Data::Dumper` output — and the armor recurs on a **second** message **twenty-four months later**.
Both dates fall inside the 1.4.11 window §7.2 bounds.

**Why it matters.** Round 19's Phase-1 lane **G2** sweeps Perl 5.14 `rand`/`srand`, ranked by L1 at
×2.5 on the inference *"Ubuntu 11.04–12.04 shipped Perl 5.14"* — an inference §7.2 shows rests on
a looser bracket than claimed. **The Perl prior does not need that inference**: the author *says*
they used Perl, in a signed message, and the library's own output is in the artifact, twice, two
years apart. That is a measurement on a held artifact, which is the class of evidence doctrine R4
asks for, and it is strictly stronger than a distro-version argument. **G2's prior should be
re-sourced to this.**

**What it is not:** it does not establish that the Liber Primus keystream came from Perl. It
establishes a working Perl + CPAN environment in January 2012 and still in January 2014, by the
author's own signed statement. That `Crypt::RSA::ES::OAEP` draws padding randomness through
`Crypt::Random` is a **lead for a generator lane, not a claim made here**.

**A bonus for G-02 itself.** The same PASSing message contains 3301's *own* statement of the
authenticity test — *"There are many fake messages out there. Only messages signed with public key
ID 7A35090F are valid."* That is the keyholder, in a message that verifies, declaring the exact
rule `KNOWLEDGE.json: authenticity_test` encodes and that corpus G-02 exists to operationalise.
§1 is not applying a community convention; it is applying the rule 3301 published. *(The key dump
also carries an `Identity` email field. It is an artifact field, already public in this corpus, and
neither run pursues it — §5's standing constraint applies.)*

### 7.4 I-03 — convergent, plus the coverage denominators and one closed gap

C3 ran the mailing-list arm independently and reached **§4's conclusions by different evidence**:
metzdowd holds exactly **one** month of the 13-month hard window (`2011-August`) and it contains
**zero** term hits; the cypherpunks archive holds **nothing** before 2013. C3 adds three things.

1. **Coverage as a denominator.** Stated as a ratio so the bound is not read as a 36-month sweep:
   **metzdowd 1/13 months of the hard window; cypherpunks 0/13.**
2. **The transport diagnosis behind `http=000`.** §4.3 correctly concludes no public 2011–2012
   cypherpunks archive exists. The `http=000` in `fetch-log.txt` has two *separate* causes, and
   neither is absence: the host's **TLS certificate has expired**, so a verifying client fails
   before it sees any HTTP status, **and** the list no longer runs pipermail —
   `/pipermail/cypherpunks/` returns **404** and the archive is served by **HyperKitty** at
   `/archives/list/cypherpunks@lists.cpunks.org/`. C3 fetched the live HyperKitty yearly mbox
   exports directly and confirmed **zero messages before 2013** from the archive's *own export*
   rather than from a Wayback inference — and grepped all **2 645 messages of 2013** (5.5 MB) for
   all twelve terms: **zero hits**. Worth recording so a future run points at a live endpoint.
3. **§4.6's reopening condition #2 is closed.** *"A local bitcointalk corpus … replacing the
   search-engine layer, which would upgrade §4.4's `reported` rows to `verified`."* C3 ran the
   twelve pre-registered terms, unchanged and unextended, against **`api.ninjastic.space`**, a
   full-text index over bitcointalk posts with per-post ids and dates, ceiling 2012-01-04.

   **Result: NO HIT.** All 29 pre-ceiling matches were adjudicated by eye and every one fails the
   bar — `3301` × 2 are the number inside MtGox order-book JSON; `cicada` × 20 are a bitcointalk
   **username** posting in GPU-mining threads; `instar` × 3 are French *"à l'instar de"*; the
   multi-word term hits are unrelated. The one near-miss, named and rejected: `outguess`,
   2011-01-11, a thread *"steganography: Hiding your wallet in a JPEG image"* — genuine JPEG stego
   talk a year before the first image, but with **no Cicada element and no recruitment element**,
   and the pre-registered term was *outguess + steganography + recruit*.

   **The strongest part is the zeroes:** `845145127`, `futhorc` and the onion string
   `a2e7j6ic78h0j` have **zero occurrences in the entire bitcointalk index at any date**.

   **Two caveats that bound it.** The API **token-matches** multi-word queries rather than
   phrase-matching, so the four multi-word terms were **not** tested as phrases; the strong zeroes
   are all single-token. And ninjastic's earliest `cicada 3301` is 2014-03-15 while §4.4 read topic
   **347716** directly at **2013-11-26** — so the index is *not complete* for that topic and the
   direct read is the better evidence. Recorded rather than reconciled: the index is a
   **supplement**, not a replacement.

**Residual gap, unchanged from §4.6 except for the bitcointalk row:** 12 of 13 months of the hard
window are held by no public archive and were **not searched**; multi-word terms are not
phrase-tested; 4chan `/x/` and `/b/` for 2011 are **structurally incapable** of a hit rather than
merely unsearched; sci.crypt, Freenode logs and `full-disclosure` were not searched at all.

### 7.5 I-01 — §3's INDECISIVE verdict stands, and §7.2 does not disturb it

Recorded explicitly so two C3 findings are not later welded into a claim neither supports: the
`CicadaPG v.3301` armor header (§7.2) proves the author edited armor output **in 2017**. §3.2's
verdict rests on **key preference packets set in January 2012** — five years earlier, a different
part of the format. **The INDECISIVE verdict is unaffected.**

§3.2's own residual also stands and still matters: the base-rate control needs keys whose UID
self-signatures are **frozen in 2012** (abandoned or revoked keys), because a live key's self-sig is
reissued on every edit. Neither this lane nor C3 sourced one.

### 7.6 What C3 files to the ledger

| item | status | one line |
|---|---|---|
| **CORPUS-G-02** | `run` | table independently reproduced, 228/228 shared files identical in verdict and hash; one signing key ID confirmed; C1–C4 met in the independent run |
| **L1-F6-CORRECTION** | `run` — **FOUND-ERROR** | 46/46 is really 56 files / 54 messages / three version strings running to 2017; toolchain changed twice; convergent with `round19/R1` §C |
| **I-03** | `run` | mailing-list bound **1/13 months**; bitcointalk upgraded `reported` → `verified`, **no hit** |
| **I-01** | `run` | INDECISIVE, unchanged |

Fragments: `round19/C3/ledger.json`. C3's re-derived table: `round19/C3/PGP-VERIFICATION-TABLE.json`.

**One correction to §1.1's framing, for the record.** C3 does **not** endorse the PREREG claim that
*no PGP verification table exists anywhere* — §1.1 already credits
`corpus/A-primary-artifacts/SIGNATURES.json` (140 files, 2026-08-20), and that credit is right. The
defensible claim, which C3 does endorse, is the narrower and still-substantial one §1.1 makes at the
end: **first verification of the whole tree, first with published positive *and* negative controls,
first grouped to distinct messages, first in human-readable form.**
