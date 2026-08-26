# L8 — PROVENANCE OSINT · PRE-REGISTRATION

_Written 2026-08-25, **before** any verification run, keyserver fetch, or archive search._
_Lane of Round 18 (`round18/CAMPAIGN-PLAN.md`). Rules 1, 2, 6, 7, 8 apply._

## Standing constraint (read first)

This lane touches attribution. The repository's own standing rule (`AGENTS.md` §1,
`KNOWLEDGE.json: attribution`) is that **no falsifiable attribution exists**, and that
asserting one is the field's single most common error. Nothing in this lane may name a
person as Cicada 3301. The deliverable is an **evidence table**, not a name.

Scope limits fixed in advance, and not negotiable after seeing a result:

- **Public, lawful sources only.** Public keyservers, public web archives, public mailing-list
  archives, published articles. No breach databases, no people-search / paid lookup services,
  no attempt to deanonymise a private individual.
- **No contact.** Nobody is emailed, messaged, or approached.
- **No publication of a real person's identity**, including a partial or probabilistic one.
- A negative here is a *coverage bound*, never a clearance.

---

## Job 1 — G-02: the PGP verification table

### Hypothesis (H1)
Every message the community treats as canonically Cicada verifies against key
`7A35090F` (fp `6D854CD7933322A601C3286D181F01E57A35090F`), and no second signing key
appears anywhere in the corpus.

### Instrument
`gpg --batch --status-fd --verify` (GnuPG 2.4.8, WSL Ubuntu) against an **isolated keyring**
(`GNUPGHOME` = a fresh throwaway dir) containing **only** the 3301 public key, so that a PASS
cannot be produced by some other key already present on the box. Timestamps are read from the
**signature packet itself** via `gpg --list-packets` on the extracted signature block, so a
signature that fails to verify still yields its real creation time.

Scope: **every `*.asc` in the repository** (enumerated: 228 files), not the subset a previous
lane scanned. Key files are classified `KEY`, not `PASS`/`FAIL`.

### Positive control (rule 2)
Before trusting any FAIL, the instrument must be shown to work in both directions:

| control | construction | must produce |
|---|---|---|
| **C1 PASS** | an untouched message file known-good in `corpus/A-primary-artifacts/SIGNATURES.json` | `GOODSIG 181F01E57A35090F` |
| **C2 FAIL-on-tamper** | C1 with exactly one character of the *signed body* altered | `BADSIG` |
| **C3 FAIL-on-foreign-key** | a message clear-signed by a locally generated throwaway key | not `GOODSIG` for 7A35090F; `NO_PUBKEY`/`ERRSIG` for the foreign keyid |
| **C4 timestamp recovery** | `--list-packets` on C2's damaged file | still emits the original `created <unix>` |

**If any of C1–C4 does not produce its stated output, no PASS/FAIL count from this lane is
reportable and the run is void.** Measured control outcomes are printed verbatim in RESULTS.md.

### Threshold / decision rule (fixed now)
- A file is `PASS` iff gpg emits `GOODSIG`/`VALIDSIG` for fingerprint
  `6D854CD7933322A601C3286D181F01E57A35090F`.
- `FAIL` = a signature packet is present and gpg does not emit that.
- `NO-SIG` = no `BEGIN PGP SIGNATURE` block in the file.
- `KEY` = the file is a public-key block, not a message.
- A `FAIL` is only reported as a **finding about the message** if the *same message text* has
  no PASSing copy elsewhere in the corpus (sha256 + normalised-body comparison). A FAIL whose
  text passes elsewhere is a **transport/mirror defect**, not a canon failure, and is labelled
  as such.

### Null
H1 is *not* refuted by mirror damage. H1 **is** refuted if a message with no clean copy
anywhere fails, or if a second signing key ID appears.

## Job 1b — G-09: signature timestamps as a seed-candidate dataset

### Hypothesis (H2)
Round 8 enumerated every unix second of 2011–2015 uniformly for 10 generators. Seeds are not
uniform: a human types a number they have at hand. Timestamps the author *provably* produced
(signature creation times, key creation/expiry) are therefore a **prior**, not a new keyspace.

### Instrument
Deterministic derivation, no search: for each authenticated timestamp, emit the raw unix
second plus a fixed, pre-declared set of arithmetic neighbours a programmer plausibly types:
`t`, `t±1`, truncation to the minute/hour/day (`t - t mod 60/3600/86400`), the UTC date as the
integers `YYYYMMDD` and `YYYYMMDDHHMMSS`, and `t` in milliseconds. **The neighbour set is fixed
here and may not be extended after seeing results.**

### Ranking (fixed now, in descending weight)
1. `provenance_class` — `verified` (from a PASSing signature packet in our own run)
   > `reported` (documented elsewhere, not machine-verified here) > `speculated` (never used).
2. `authorship_proximity` — the timestamp was written by the author's own machine
   (signature packet, key creation) > written by infrastructure the author controlled
   (onion post time) > written by a third party (a solver's post time).
3. `derivation_distance` — exact `t` > ±1 > truncation > reformatting.

### Deliverable and its limits
A ranked JSON candidate list handed to L6 / the ledger. **This lane does not run the seeds.**
Nothing here is a cryptanalytic claim; it is a prior. If L6 runs the list and finds nothing,
that is a negative about *these* seeds only.

### Known confound, recorded before running
`AUDITOR-LOOP-2026-07-28.md` established that a PGP signature timestamp is **attacker-settable**
(RFC 4880 hashed subpacket, taken from the local clock) and it **refuted** the timezone /
working-hours biometric built on those timestamps (n=26, irreproducible). That refutation
applies to using timestamps as *evidence about a person*. It does **not** apply to using them
as *seed candidates*: a spoofed timestamp is still a number the author chose and typed, which
is exactly the property that makes it a plausible `srand()` argument. This distinction is
declared now so it cannot be invented later to rescue a result.

---

## Job 2 — I-01: `mruzuki` / `cicadeur`, keyid `02BD208AFB8AFF75`

### Hypothesis (H3)
The `mruzuki` key (created 2012-01-12, self-revoked 2012-01-22, seven days after the first
3301 image) was produced by the **same OpenPGP toolchain** as 3301's `7A35090F`.

This is deliberately a *technical* hypothesis, not an identity one. It is falsifiable, which
"is it the same person" is not.

### Instrument
`gpg --list-packets` on both keys, exported from public keyservers, compared on:
key algorithm and size, creation timestamp, self-signature hash algorithm, the ordered
preference lists (`pref-sym-algos`, `pref-hash-algos`, `pref-zip-algos`), key flags,
keyserver-no-modify, features/MDC, expiry policy, packet ordering, and the revocation
packet's reason code and timestamp. Armor version headers where present.

### Threshold (fixed now)
- **MATCH** = identical ordered preference lists *and* identical self-sig hash algo *and*
  identical key-flag/feature bytes.
- **MISMATCH** = any ordered preference list differs.
- **INDECISIVE** = preferences agree but are the era-default of a common client, so the
  agreement carries no discriminating information.

**Declared in advance:** a MATCH is *weak* evidence at best, because two people running the
same GnuPG version in the same month produce identical defaults. The lane will state the
base-rate problem in the result whichever way it comes out. A MATCH will **not** be reported
as a link to a person.

### Out of scope, by rule
Breach databases, people-search services, paid lookups, and any attempt to resolve
`mruzuki@gmail.com` to a human being. The 2026-07-28 auditor listed a paid breach lookup as
the next step; **this lane declines it.** That refusal is a scope decision, recorded here, not
a failure to find something.

---

## Job 3 — I-03: pre-disclosure search, 2011 → 2012-01-04

### Hypothesis (H4)
A post predating **2012-01-04** (first 3301 image) exists in a public archive referencing a
Cicada-specific element before its disclosure.

### Search terms (fixed now, so the negative is meaningful)
`3301` · `845145127` · cicada + puzzle/recruit · instar / "instar emergence" ·
"we are looking for highly intelligent individuals" · Liber Primus · runes + futhorc + cipher ·
Mabinogion + cipher · outguess + steganography + recruit · Anglo-Saxon rune + prime/gematria ·
`a2e7j6ic78h0j` and sibling onion strings · "Cicada 3301".

### Archives named in advance
cypherpunks (venona / mailing-list-archive mirrors), metzdowd cryptography list archives,
bitcointalk, 4plebs /x/ and /b/ where indexed, Wayback / archive.today for the above, and
Google-indexed mirrors of each. Date window **2011-01-01 → 2012-01-04** for the hard test,
extended to 2013-12-31 for context hits.

### Decision rule
- **HIT** = a dated, archive-attested post before its element's disclosure date, with a URL
  and a capture that carries the date.
- **NEGATIVE** = every named archive searched with every named term, no hit. Reported as
  *"searched X, terms Y, window Z, nothing"* — a **bound**, with the reopening condition
  stated. Not a clearance.
- A hit whose date cannot be independently established from the archive is **not** a HIT.

### Anti-motivated-reasoning clause
A pre-disclosure hit would be the strongest external evidence in this case, which is exactly
why the bar is set now: date-attestable, archive-hosted, element-specific. "Someone mentioned
cicadas" is not a hit. "Someone discussed runic ciphers" is not a hit.

---

## What this lane will NOT claim, whatever it finds

1. That any person is Cicada 3301.
2. That the corpus of signed messages is complete (it is a corpus of *mirrors*; see G-12).
3. That an archive search which returns nothing has cleared anything.
4. That a timestamp seed candidate is a solution, or that L6 running it settles the seed
   question — the neighbour set is a prior, not a keyspace.
5. The words "exhausted", "closed", or "unsolvable" (rule 6).
