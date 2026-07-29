# Campaign VIII — Attribution / OSINT (cypherpunk-focused)

_2026-07-06. Deep-research harness: 99 agents, 17 sources fetched, 70 claims extracted,
25 adversarially verified (3-vote, 2/3-refute-to-kill) → 21 confirmed, 4 killed.
Candidate pool restricted to the cypherpunk / crypto lineage per scoping. For the article._

## Headline

**Negative result across all four evidence lenses.** No named individual — cypherpunk or
otherwise — can be attributed as the author of Cicada 3301 on the accessible evidence.
The honest verdict is **"consistent-with, not evidence-of."** Cypherpunk *influence* is
well-supported as ideology; cypherpunk *authorship by any named person* is unproven.

This matters for the piece: attribution doesn't fail for lack of trying — it fails because
the falsifiable evidence doesn't exist in the surviving record, and the record itself is
partly destroyed.

## Lens-by-lens

**1. Priority-of-knowledge / timestamp leakage (highest weight — the "smoking gun"): EMPTY.**
Zero confirmed leaks. No candidate was documented referencing any Cicada-specific fact
(runic Liber Primus, totient/prime method, the 512-bit "AN END" hash, an onion, the base-60
encoding) *before* its public-disclosure date. **Crucial caveat:** this is
absence-of-evidence, not evidence-of-absence — the relevant Tor v2 onions are dead, the
2012–2014 #cicadasolvers/IRC logs are largely deleted, and 4chan threads are only partly
archived. The smoking gun is *absent from what survives*, which is not the same as proof it
never existed.

**2. Technical fingerprints: confirmed the anchors, found NO attribution path.**
- Key ID `7A35090F`, fingerprint `6D854CD7933322A601C3286D181F01E57A35090F`, UID
  `Cicada 3301 (845145127)`, RSA-4096, created 2012-01-03. **Nice detail for the article:**
  `845145127 = 503 × 509 × 3301` (all prime), and 509×503 are the first image's pixel
  dimensions. OutGuess 0.2 for JPEG stego. PGP clearsigning Jan 2012 → last verified message
  April 2017.
- **No web-of-trust links. No reused-key attribution.** A third-party "Cicada-3301" GitHub
  repo's `PGPKey.txt` holds an unrelated key (`0x8EAF01977B4ADD02`) — a red herring, no link.
  The community `isitcicada` tool verifies only against the single oldest key by full
  fingerprint precisely *because* no trustworthy signing-party links exist.
- **Base-60 / F-skip probe: not a cross-linkable fingerprint.** Solvers debated the missing
  lowercase `f` post-hoc ("I'd have been sure that was a meaningless accident, if the missing
  letter hadn't been f!"), but this is speculation about the *puzzle's own* encoding, not a
  habit any candidate displays elsewhere. The community's imprecise "skips f/y/z" version was
  refuted 0-3. **NOTE (our correction):** our Campaign VII analysis is more precise — the
  alphabet is exactly `0-9 A-Z a-x` (60 symbols; y/z are out of range by construction, not
  "skipped"), and `f` (value 41) is the one in-range symbol that never occurs. Our technical
  finding stands; the forum framing was just loose.

**3. Stylometry: empty.** No verified claim compared Cicada's prose to any named candidate at
any confidence band. Per the brief, stylometry is never proof — here it produced no
reportable suggestive hit either.

**4. Thematic / ideological alignment: well-supported but explicitly NON-attributive.**
A peer-reviewed paper (Brill, *Gnosis: Journal of Gnostic Studies* 6(1), 2021) places
Cicada's gnosis "within the libertarian concerns of freedom of information and privacy" and
describes "Cicadianism" as a technomystical order — but names no one. The Malicious
Life / Cybereason podcast raises the cypherpunk link and then states plainly: *"Can we be
sure that a member of the Cypherpunks movement is behind Cicada 3301? Of course not."*
(The specific claim that the Cypherpunks list ran on host `cicada.berkeley.edu` was
**refuted 0-3** — do not use it in the article.)

## Ranked candidate table (deliverable A)

| candidate | band | best fact | most-damning fact |
|---|---|---|---|
| Unnamed cypherpunk-tradition author | **weak (ideology only)** | dense ideological + toolchain match (PGP/OutGuess/Tor, privacy/gnosis themes, peer-reviewed lineage placement) | zero priority-of-knowledge leak, zero technical link — "cypherpunk" names an aesthetic, not a person |
| Joel Eriksson ("clevcode") | **negligible as author** | documented skills/proximity as a 2012 first-round solver | he's a *solver* the puzzle even addressed by name ("Our goal, Clevcode…" — a probable spoof); holds no key, claims nothing |
| IRC "Wind" | **negligible** | claimed membership | community-rejected, never provided proof |
| Marcus Wanner (winner) | **negligible** | documented insider of the post-solve group | discloses no key/method; inner project fizzled |

No agency/secret-society theory produced a cypherpunk bridge, so those stayed out of scope.

## What we could not access (deliverable F)

- **Tor v2 onions** (e.g. `a2e7j6ic78h0j`) are permanently dead.
- **Original 2012–2014 IRC logs** (#cicadasolvers etc.) are largely deleted/incomplete.
- **4chan threads** only partially archived (4plebs).
- So the highest-weight lens is *unresolved*, not *cleared*.
- Forensic footnote: a 2025 result makes SHA-1 PGP signatures forgeable via chosen-prefix
  collision — this future-caveats "definitive" for any NEW purported 3301 message but does
  **not** retroactively undermine the 2012–2017 verified chain. And note: a valid signature
  from `7A35090F` proves *keyholder continuity*, NOT authorship or identity.

## Open threads (could move it, if pursued)

1. Archived cypherpunks/metzdowd or bitcointalk posts (2011–2013) — a dated pre-disclosure
   reference to a Cicada-specific fact would be the smoking gun. Unresolved only because the
   archives are thin, not because it was cleared.
2. Keyserver forensics on `7A35090F` (upload-era logs, adjacent-key co-occurrence, signing
   timestamps) — not exhaustively run; no positive WoT path found so far.
3. A real stylometric study: authenticated Cicada prose (2012–2017 signed messages + manifesto
   lines) vs a defined candidate corpus. Doesn't exist yet in the literature.
4. **Niels Provos** — author of OutGuess, the exact stego tool Cicada used — surfaced only as a
   toolchain source, with no finding tying him in. A thread to note honestly, not oversell.

## Article framing

The truthful, strong line: **cypherpunk DNA is everywhere in Cicada — the PGP-first OPSEC, the
Tor infrastructure, the primes-as-sacred number mysticism, the privacy/enlightenment ethos, a
peer-reviewed placement in the Hughes/May/Gilmore lineage — yet after a targeted OSINT sweep
across exactly that community, not one falsifiable thread (a pre-disclosure leak, a
web-of-trust link, a stylometric match) connects the ideology to a person.** The mystery
survives not because no one looked, but because the author built it to survive looking — and
because the parts of the record that might have betrayed them are now gone.

---

## Addendum (2026-07-28) — Technical-fingerprint lane, closed

Targeted re-attack of the four "configuration choice" fingerprints (OutGuess 0.2, PGP impl,
509x503, base-60 f-absent) + a hard Provos ruling. **Result: NULL. No attribution path; the
"config choices" are not personal fingerprints.**

- **"OutGuess 0.2" is NOT a distinguishing choice.** Verified (Wikipedia OutGuess + solver
  wiki): 0.2 was released Feb-2001 and is the *terminal Provos release* — the only real
  OutGuess in existence, and the Debian/apt `outguess` package, from 2001 until the 2013
  "OutGuess Rebirth" (OGR) fork. Anyone doing JPEG-coefficient stego in 2012 uses 0.2 *by
  default*. This is a floor, not a signature — it excludes no one and implicates no one. The
  "up to 0.13" figure is StegDetect's internal detection namespace within the 0.2 series, not
  a separate program.
- **509x503 / 845145127 are public puzzle mechanics, not private author habits.** They live
  in the key UID *because* the puzzle used them (509·503 = image dims, ·3301 = the .com hop).
  Visible to every solver; zero attribution value.
- **base-60 `0-9 A-Z a-x`, f-absent: reaffirmed non-cross-linkable** (Campaign VIII stands) —
  a property of the puzzle's own encoding, not a habit any named person displays elsewhere.
- **Niels Provos — RULED OUT as more than a toolchain source**, three independent grounds:
  (1) *Timeline*: last OutGuess release 2004, never returned; 11 yr gap to LP2. (2) *Opsec
  profile is the inverse of Cicada's*: Provos is a fully-doxxed public figure — Google
  Distinguished Engineer (security) 2003-2018, PhD Michigan, real-name conference presence,
  public EDM hobby ("Activ8te"), swordsmithing. Cicada is defined by anonymity. (3) *No
  falsifiable link*: no pre-disclosure leak, no WoT tie, no stylometric hit. Authoring the
  tool a decade earlier is the weakest possible circumstantial thread; it is "used-his-tool,"
  which is true of every OutGuess user. Note honestly, do not oversell — matches Campaign
  VIII's own caveat.
- **Smoking-gun (pre-disclosure knowledge): still EMPTY.** No documented instance of any named
  person referencing a Cicada-specific fact before its disclosure date. The original 4chan
  poster ("3301", Jan-2012) was never IP-traced or identified. Archives that could hold such a
  leak (dead Tor v2 onions, deleted 2012-14 IRC, partial 4chan) remain the only place it could
  survive — unresolved, not cleared.

**Net:** the technical-fingerprint lane produces no named creator. The four "configuration
choices" are either forced defaults (OutGuess 0.2), public mechanics (509x503), or
puzzle-internal (f-absent). Provos is out. The lane is closed as NULL; the only live
attribution thread remains the archive-based pre-disclosure smoking gun (Campaign VIII open
thread #1), which is an archive-recovery problem, not a fingerprint problem.
