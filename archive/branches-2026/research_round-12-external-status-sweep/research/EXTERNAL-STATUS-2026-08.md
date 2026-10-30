# EXTERNAL-WORLD STATUS SNAPSHOT — Cicada 3301 / Liber Primus — as of 2026-08-06

**Purpose.** A dated, cited baseline of the *external* world so future rounds do not re-scout blind. Produced
by a comprehensive deep-research sweep (5 search angles → 18 sources fetched → 62 claims → 25 adversarially
verified, 3-vote; 23 confirmed, 2 refuted). **Headline: nothing has cleared the reopener bar.** The only thing
that can legitimately reopen the closed ciphertext program is a NEW PGP-signed 3301 message (key `7A35090F`),
a released key/seed/pad, or a vetted transcription correction — none exists.

Source ratings: **[verifiable]** primary/signed/reproducible · **[credible]** reputable, cross-corroborated ·
**[unverified]** single-source, no artifact · **[noise]** scam/AI-slop/hype.

---

## (A) Did anything clear the REOPENER BAR? — NO (high confidence)

**The last verified PGP-signed 3301 communication remains the April 2017 message** (signed 2017-04-04,
surfaced on Pastebin, reported to #cicadasolvers ~2017-04-29), signed by key ID **7A35090F** / fingerprint
**6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F** (RSA-4096, created 2012-01-03). No authentic signed 3301
message, and no released key/seed/pad, has appeared since. Cross-corroborated and current:
- [credible] Wikipedia *Cicada 3301* (last edited **2026-08-03**): last verified OpenPGP-signed message was
  April 2017; timeline ends there. https://en.wikipedia.org/wiki/Cicada_3301
- [credible] krisyotam/cicada3301: verbatim "No authentic PGP-signed messages are known after April 2017."
  https://github.com/krisyotam/cicada3301
- [credible] CicadaSolvers: "Since 2017 we haven't received any communications from 3301."
  https://www.cicadasolvers.com/communications/ · https://www.cicadasolvers.com/quickstart/
- [credible] Boing Boing (2026-06-11): "last verified signed message came in April 2017."
  https://boingboing.net/2026/06/11/an-anonymous-group-posted-internet-puzzles-to-recruit-code-breakers-then-vanished.html
- [verifiable] The community `isitcicada` verifier checks against fingerprint …7A35090F and shows no post-2017
  signed-message additions. https://github.com/cicada-solvers/isitcicada

**No vetted transcription-discrepancy correction** for the unsolved pages surfaced either (the other path that
would reopen the cipher). See open threads.

---

## (B) [credible]-or-better developments worth ARCHIVING (context, NOT reopeners)

1. **LP solve status & public cipher profile unchanged.** [credible] LP1 (17 pp) fully solved; LP2 (58 pp)
   only pages 56–57 solved → 56 unsolved. Public frequency analysis notes the sole deviation from random is a
   **doublet deficit** (below the 1/29 = 3.45% chance rate, not absent) and traditionally guesses
   **autokey/autoclave-class or a bespoke cipher**. https://uncovering-cicada.fandom.com/wiki/Frequency_Analysis_Unsolved_Pages · https://www.cicadasolvers.com/quickstart/
   > **NOTE — this repo is AHEAD of the public consensus here.** The community's "autokey/autoclave" guess is
   > exactly what our rig **positively refuted** (difference-diagonal z = −17.25) before establishing the
   > OTP-class / soft-anti-repeat-filter verdict. There is nothing in the external cipher analysis to import
   > that advances ours; the public frontier is behind this repo.
2. **Schoenberger litigation = defamation/brand, NOT authorship.** [verifiable] (court records) The Michigan
   Court of Claims matter (consolidation order 2025-12-04 under **26-000013-MZ**, merging 25-000045-MM and
   25-000186-MZ) and the federal **Schoenberger et al v. Derrick** (E.D. Mich. **2:2025cv12937**, filed
   2025-09-16, §1332 diversity tort) both have Thomas Schoenberger as **PLAINTIFF** in a defamation/tort suit
   (re: a 2021 QAnon research paper by MSU's Laura Dilley). "Cicada 3301" appears only as a self-styled
   d/b/a/brand (Cicada 3301 …LLC, inc. 2014; CICADA 3301 trademark reg. to Primus Holdings LLC). **No
   proceeding adjudicates authorship of the cipher; consolidation is purely procedural.**
   https://www.courts.michigan.gov/4982de/siteassets/case-documents/uploads/coc/2026/26-000013-mz/2025-12-04-26-000013-mz-21-order-20251204-order-of-consolidation.pdf · https://dockets.justia.com/docket/michigan/miedce/2:2025cv12937/388516 · https://statenews.com/article/2025/04/msu-professors-qanon-paper-prompts-lawsuit-with-cicada-3301-puzzle-leader
3. **Podcast "The World's Hardest Puzzle" (2024-02-19, 7 eps).** [credible] Exclusively interviews Schoenberger
   as a *self-professed* founder but provides **no evidence** validating authorship; presents conflicting
   accounts (incl. unconfirmed "intelligence-recruiter" speculation) and concludes origins "remain shrouded in
   mystery." A self-professed-founder interview is not cryptographic proof and does not clear the bar.
   https://soundsprofitable.com/press-release/new-investigative-documentary-podcast-the-worlds-hardest-puzzle/

---

## (C) [noise] / scams — logged so they are NOT re-chased

- **"53cr37-layer" Solana-token "solve"** [noise] — user-editable fandom page claims LP pp1–73 decrypt (runes
  + Atbash + Vigenère, keys DANAD/MIDBV from the "Know This" square) to a Solana token address
  (`AWM9MQn8J5od6zYDcJBM46SP7LnUVe7FqYdmGKLZYZAa`). Crypto-token promotion, no PGP signature, textbook AI-era
  scam. Do not chase. https://unc0vering-cicada.fandom.com/wiki/53cr37-layer
- **Zenodo "IA Gemini Final Translation" (Becker/OFFELLIA)** [noise] — AI-assisted ciphertext-only personal
  translation, no signature, no key (previously logged R4/R7; reaffirmed).
- **4chan "NEW Cicada 3301 PGP signed message" threads** [noise] — do not verify against 7A35090F.

## Refuted (do NOT launder into fact)
- **"On the Forgery of Cicada 3301 PGP Signatures via SHA-1 Collision Attacks"** (ResearchGate) — both claims
  (that all 3301 signatures used SHA-1, and that future 3301 signatures are therefore untrustworthy/forgeable)
  were **adversarially REFUTED 0-3**. The community standard still treats a valid signature from RSA-4096 key
  7A35090F as authentic. Recorded so a future researcher does not mistake this for an established compromise.
  https://www.researchgate.net/publication/403192960

---

## (D) Definitive external snapshot (trust this baseline until a NEW dated artifact appears)
- **Reopener:** none. Last signed 3301 message = April 2017 (7A35090F). No key/seed/pad released. No vetted
  transcription correction.
- **Cipher (public):** LP2 unsolved (56 pp), near-random, doublet deficit; public consensus "autokey/autoclave"
  — **behind this repo's** refuted-autokey / OTP-class verdict.
- **Authorship (public):** unresolved; Schoenberger self-claims via brand/litigation, no cryptographic proof.
- **Nothing external advances the cryptanalysis or the attribution beyond what this repo already establishes.**

## Open external threads (residual, honest gaps — not runnable internally)
1. **Unvetted GitHub transcription corrections** — the single most plausible live reopener. The sweep did not
   find one, but could not exhaustively vet every repo (relikd/LiberPrayground, cmbcicada3301, libergo,
   LiberPrimusSolver, neuroretransmit-cicada, …). A *community-accepted* corrected transcription would
   legitimately reopen the cipher. Monitor.
2. **AN END deep-web page / LP2 v2-onion archival** — no confirmed Wayback/CDX/Tor2web capture found; remains
   an unverified gap (v2 onions deprecated Oct 2021).
3. **Schoenberger litigation discovery** — monitor 26-000013-MZ / 2:2025cv12937, but a defamation/brand ruling
   cannot adjudicate cipher authorship regardless.

## Method caveats
Several load-bearing sources are community wikis/forums (user-editable, consensus not signed statements), though
cross-corroborated by Wikipedia + GitHub. Two secondary URLs (Boing Boing, RadioInfo) returned HTTP 403 to
direct fetch and were verified via search-index text. Court records are primary for the litigation's procedural
nature. Snapshot anchored to 2026-08-06 (Wikipedia last edited 2026-08-03; dockets active).
