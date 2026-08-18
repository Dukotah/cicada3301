# Front A2 — deep-OSINT runbook (owner-run; paid/deep vectors authorized)

_The only part of the campaign I can't run from here: it needs accounts / paid queries and lives
outside the sandbox. Everything below is precise enough to execute and bring results back to me._

## Target

The **earliest Cicada-adjacent keyserver actor**, surfaced by the 2026-07-28 auditor loop and
never resolved from public sources:

- **email:** `mruzuki@gmail.com`  (handles seen: `mruzuki`, `cicadeur`)
- **PGP key id:** `02BD208AFB8AFF75`
- **timeline (the reason this matters):** key **created 2012-01-12**, **self-revoked 2012-01-22** —
  i.e. it appeared ~5 days after the first 3301 image and was killed at 7 days. That is
  operational discipline around the exact launch window; it is the earliest human fingerprint
  near the puzzle's origin. Memory's standing note: *only non-public vectors remain* (breach-DB /
  people-search / private 2012–14 IRC logs).

## Goal (LP-relevant, not just doxxing)

Not identity for its own sake. We want a thread to **key material or the channel it moved through**:
a real name/alias that leads to a surviving 2012–14 insider space (IRC/forum/git/key-escrow), an
alternate handle that posted the pad or a pointer, or an archived paste. A bare name with no
archival trail does **not** advance the solve — flag it but keep pulling for the channel.

## Steps (run top-down; stop-and-report if any yields a real thread)

1. **Breach / leak DBs on the email** (highest value):
   - **IntelligenceX** (intelx.io) — search `mruzuki@gmail.com` AND `mruzuki` AND `cicadeur`;
     it indexes pastes, leaks, and *historical* darkweb — set the date filter to 2012–2015.
   - **DeHashed**, **Snusbase**, **LeakCheck**, **HIBP** — query the email; pull linked
     usernames, alternate emails, IPs, and (from combos) reused handles. Pivot on every new alias.
2. **Username pivot** across platforms for `mruzuki` and `cicadeur`:
   - GitHub, Keybase, Reddit, HN, Twitter/X, Freenode/OFTC nick registrations, old forums.
   - Paid: **Maltego** (email + alias transforms) draws the graph fastest.
3. **Paste / historical**: IntelX historical + `psbdmp.ws` + Google `"mruzuki" OR "cicadeur"
   cicada 2012..2014`.
4. **2012–14 IRC / forum archives** (where the pad would actually have moved):
   - Search for archived `#cicada` / `#3301` Freenode logs from 2012–2014 (IRC log mirrors,
     the Uncovering-Cicada wiki's log pages, any winners'-forum snapshot). Look for `mruzuki`/
     `cicadeur` posting key/pad material or an onion for it.
5. **Keyserver forensics** (I can help with this part from here if you want): pull the full
   `02BD208AFB8AFF75` record (keys.openpgp.org / historical SKS dumps) for any UID, secondary
   email, or cross-signature linking it to a real identity or another Cicada key (esp. 7A35090F).

## Bring back to me

Any of: a real name, an alternate email/username, an IP/host, or — the prize — a **link to a
surviving 2012–14 channel or an archived post containing key/pad material or an onion pointing at
it**. I'll immediately test anything that looks like key material against the runes (skip-aware
decoder) and fold provenance findings into the attribution docs.

## Honest prior

Low. Six years of dead Tor-v2 and un-archived forums are the reason this is the residue and not
the main event. But it is the *correct* residue: the OTP construction means the answer is external
by design, and a human who moved key material in Jan 2012 is exactly the kind of external thread
that could carry it. Worth your paid queries; not worth expecting a hit.
