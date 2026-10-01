# L5 OSINT People / Attribution — FINDINGS (Round 29, live pass 2026-09-28)

**Lead answer: mruzuki did NOT resolve to anything.** The first-ever active handle-reuse pass shows "mruzuki"/"cicadeur" is a zero-footprint burner — it appears in exactly ONE place on the indexed public web: its own self-revoked 2012 keyserver key. Prior work (Round 18 L8) only did the *cryptographic* key comparison and left the *handle-reuse* question open-but-unrun; it is now run, and it's a dead end with one vector left.

## Ranked leads

### 1. mruzuki / cicadeur (keyid 02BD208AFB8AFF75) — PRIMARY, resolved to a dead end
- Key on **keyserver.ubuntu.com only**: RSA-2048, created 2012-01-12, **1-day self-expiry**, self-revoked 2012-01-22, **zero WoT edges**. NOT on keys.openpgp.org (404). Email-index returns only that one key. **verified** (WebFetch + curl).
- **GitHub `mruzuki` and `cicadeur` both 404 — never existed** (user search `total_count: 0`). **verified** (`gh api`).
- Web/social/Reddit/Keybase: nothing. Handle appears in **no** Cicada community writeup or wiki. **verified.**
- Read: total absence from every corpus is mildly *more* consistent with an **unrelated 2012 name-squat** than a real insider burner — a real insider needs no themed handle; a fan/squatter picks one because it's public-facing. Attribution value ≈ zero; downgrade from "highest-value unresolved" to **"resolved: burner, no reuse, no path."** Cicada link **unverified → effectively refuted as a productive lead.**
- **Best next action:** one cold email to `mruzuki@gmail.com` (address may still be live/monitored; a reply or display-name-bearing auto-reply is the only remaining vector). Everything crawlable is now crawled.

### 2. Joel Eriksson (clevcode) — solver, not author; FRESH 2025 activity
- clevcode.org/cicada-3301 live: documents the 2014 "When is a BWV not a BWV?" message and calls it *"doubtful… the real Cicada."* His "chat group" hearsay traces to *other* solvers' **n0v4.com IRC**, not a group he joined — he missed the Tor window (second-hand insider knowledge). No authorship claim. **verified.**
- **Freshness delta:** ~Oct-2025 first podcast appearance, interviewed by **@nostalnerd (Nostalgia Nerd/Peter Leigh)**, YouTube Oct 2025. **verified.** Only genuinely new primary-actor activity; promo contains no attribution content.
- **Best next action:** transcribe that interview for any new detail on the 2014 message's provenance.

### 3. Marcus Wanner (marcuswanner) — insider; CAKES did NOT survive publicly
- GitHub active through Aug 2026 (hobbyist repos). **`futorcap`** (Cryptographic Time-delay Engine, 2014) still public. But **CAKES is NOT on public GitHub** — both `CAKES+cicada+escrow` and `cicada+anonymous+key+escrow` searches return `total_count: 0`. **verified.** No forum snapshot surfaced anywhere. Only surviving fragment is lore + the futorcap re-implementation.
- **Best next action:** direct email (`marcus@wanners.net`) — does his personal CAKES *git* copy still exist on disk. Campaign XIX already emailed him; awaiting reply.

### 4. Nox Populi (@NoxPopuli3301) — credible witness, unverified 2013-winner
- DEF CON 26 (2018) talk is **real** (Crypto & Privacy Village, YouTube sVU4k2gRe_Y). Detailed contents **unverified** (not extractable this session). New detail: Canadian, likely female, **peer-referenced by Wanner** (met in person) — presence real, 2013-winner status not independently documented. Only lead on the LP-era side of the timeline, but a witness narrative, not an authorship claim. Attribution value low.

### 5. Technique fingerprint (combinatorialist + Old-English philologist + cipher designer)
- Actively searched; **no named person** — only generic reference material. Profile-only stands. Not advanceable by keyword search (would need MathSciNet + medievalist prosopography). Adrian Hon still excluded.

## Freshness / doctrine
- **No creator attribution, no new winner reveal** for the original puzzle in 2024-2026. **verified.** Ransomware "Cicada3301" (2024) is an unrelated name-squat. Schoenberger litigation still live but refuted-as-author (not re-chased).
- **Hallucination flags honored:** asserted no onion address; every handle/key claimed was fetched from a live source this session. Refuted a temptation — "Tekknolagi = Max Bernstein" plausible but confirmed by NO public Cicada source; marked **unverified**, not asserted.

**Net:** standing verdict unchanged and slightly tightened. The three lawful, cheap, un-taken actions that could still move Goal 2 are all human-in-the-loop direct contacts (mruzuki@gmail.com; Wanner re: CAKES git; Nox re: 2013 material) — none crawlable.
