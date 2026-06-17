I now have thorough, well-sourced material covering all requested points. Compiling the report.

---

# Cicada 3301: The 2014 Puzzle and Its Transition into the LIBER PRIMUS

## Overview

The 2014 round was Cicada 3301's third annual recruitment puzzle. Unlike the 2012 and 2013 rounds — which had clear, sequential solve paths that ultimately led to private Tor sites and (reportedly) personal contact — the 2014 puzzle is notable because it **introduced the *Liber Primus* ("First Book")**, a long runic text that became (and remains) the central unsolved artifact of the entire Cicada 3301 phenomenon. The puzzle did not so much "end" as **converge onto the Liber Primus and stall there**, with later signed messages (2016, 2017) essentially telling solvers that the book *is* the puzzle now.

Note on dates: Wikipedia says the 2014 round began **January 4, 2014** (the Twitter announcement); solver documentation typically gives **January 5, 2014** as the start of the actual puzzle path. Both dates appear in reputable-ish sources and the one-day discrepancy is announcement-vs-first-clue, not a contradiction.

---

## The Jan 4/5 2014 start

- A new clue was announced via the same verified Cicada 3301 Twitter account used in prior years, on/around **January 4–5, 2014** (Wikipedia: Jan 4; solver archives: the puzzle path on Jan 5). [Wikipedia; scream314 archive]
- As in prior years, the entry point was a **public image** containing hidden data, and every legitimate step was **authenticated with the same OpenPGP private key**, so solvers could distinguish real clues from fakes. [Wikipedia]

---

## Techniques used in 2014

The 2014 path layered many of the same techniques as earlier rounds, plus heavier use of runes and number theory:

- **OutGuess steganography** — hidden data (often PGP-signed text) embedded in JPEG images; the primary extraction tool throughout the round. [scream314; boxentriq]
- **OpenPGP signature verification** at each step. [Wikipedia; scream314]
- **Book ciphers** and **Tor (.onion) hidden services** as later-stage waypoints. [scream314; boxentriq]
- **A 5×5 Magic Square** (see below). [scream314]
- **Anglo-Saxon / Futhark runes** decoded via the **Gematria Primus** mapping (carried over from 2013). [scream314; boxentriq]
- **Number theory themes** — decoded runic text declared *"THE PRIMES ARE SACRED"* and *"THE TOTIENT FUNCTION IS SACRED,"* foreshadowing the totient-based ciphers later used on the book. [scream314]
- Media variety overall across Cicada rounds included "the Internet, telephone, original music, bootable Linux CDs, digital images, physical paper signs, and pages of unpublished cryptic books written in runes." [Wikipedia]

---

## The Magic Square

A **5×5 magic square** appeared as a central element of the 2014 path (documented form):

```
272  138  341  131  151
366  199  130  320   18
226  245   91  245  226
 18  320  130  199  366
151  131  341  138  272
```

It is symmetric, and rows/columns/diagonals share a common sum — functioning as both a structural key and a verification/consistency device within the puzzle. [scream314]

(Magic squares are a recurring Cicada motif; the 2013 round also famously contained one. Wikipedia confirms magic squares as part of the broader Cicada toolkit but does not itemize the 2014 square specifically — the matrix above comes from the solver archive, which I'd class as **well-documented community record rather than a 3301-PGP-signed primary artifact**.)

---

## Gematria Primus (the rune → letter → prime mapping)

The **Gematria Primus** is a custom **29-rune alphabet** first surfaced in the **2013** puzzle and used heavily in 2014/Liber Primus. Each rune maps to:

- an **English/Latin letter (or digraph)** equivalent,
- a **decimal position** (0–28), and
- a **prime number value**, with the primes running in ascending order from **2 up to 109** (the 29th prime). [boxentriq; scream314; Uncovering Cicada Wiki]

Examples (documented): ᚠ = F → position 0 → prime 2; ᚾ = N → position 9 → prime 29. [boxentriq guide]

Because every rune carries a prime value, any runic word has a "gematria sum" (sum of its rune-primes), and runes can be addressed either by position or by prime — which is exactly what the book's ciphers exploit. [boxentriq; Uncovering Cicada Wiki]

**Totient cipher (used on the book):** Because for a prime *p*, Euler's totient φ(*p*) = *p* − 1, solved Liber Primus pages use a running key derived from consecutive primes, shifting each rune's position by `(prime − 1) mod 29`. One known quirk: cleartext ᚠ (F) is copied unchanged and does **not** consume a key step. This is the documented method behind solving the page known as **"An End."** [boxentriq totient cipher tool]

---

## How 2014 introduced the runic "book" — Liber Primus

- The 2014 path led to the release of **runic pages** — first as part of the puzzle chain, then as a **larger dump** of book pages (commonly described as embedded/extractable from numbered images, e.g. `00.jpg`–`57.jpg`). [scream314; boxentriq]
- The text is titled **Liber Primus ("First Book")**, opening (decoded) with: **"WELCOME, PILGRIM, TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS."** [scream314]
- Solved passages are philosophical/instructional in tone — e.g. *"QUESTION ALL THINGS,"* *"DISCOVER TRUTH INSIDE YOURSELF,"* and similar koan-like directives — emphasizing introspection and rejection of dogma rather than technical next-steps. [scream314]
- Total length is generally documented as **~74–75 pages of runes**. Solver consensus: roughly **17 pages solved** (often grouped as "LP1"), with a much larger remainder (the "LP2" bulk, ~57–58 pages) **still unsolved**. [boxentriq; scream314; Wikipedia ("contains many pages, only some of which have been decrypted")]

---

## PGP-signed messages and the warning about fakes/impersonators

- Throughout, Cicada's authenticity guarantee was its **OpenPGP key**. Wikipedia: "Each clue was signed by the same OpenPGP private key to confirm authenticity." [Wikipedia]
- The key is documented as **0x181F01E57A35090F** (fingerprint `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`), commonly referenced by its short ID **7A35090F**. [scream314]
- Cicada repeatedly warned that **unsigned puzzles/clues are fakes**, a response to numerous impersonators and copycat "Cicada" puzzles that proliferated after media attention. Wikipedia notes their April 2017 statement **"denying the validity of any unsigned puzzle."** [Wikipedia]

---

## How the 2014 puzzle "ended" / stalled

- The 2014 path is generally documented as terminating in the **full Liber Primus** rather than in a clean private-contact finale like 2012/2013. After the complete book surfaced (~74–75 runic pages, ~17 solved), public progress **slowed dramatically** with no validated mechanism to advance. [scream314; connortumbleson; Wikipedia]
- The practical "end" is therefore a **pointer, not a finish line**: Liber Primus became the ongoing challenge. Why it stalled is **unknown/speculative** — possibilities range from the remaining pages being genuinely unsolved, to private solvers succeeding and going quiet, to the text being intentionally open-ended. The "private solvers went silent" idea is **community speculation, not documented fact.** [connortumbleson; community archives — flagged as speculation]

---

## 2015: no new puzzle (and a disavowal)

- **No recruitment puzzle was released on January 4/5, 2015.** [Wikipedia]
- Cicada's verified channel was used around this period mainly to **disavow association** with parties misusing the Cicada name/symbols — i.e., reinforcing the "verify PGP / beware fakes" stance rather than launching a challenge. The exact 2015 disavowal details are thinly documented; treat specifics cautiously. [Wikipedia; community archives — partially unverified]

---

## The 2016 message ("Beware false paths")

- A new clue was posted via Twitter on **January 5, 2016** — an **image (commonly described as a bare oak tree with runes)** carrying an OutGuess-hidden, PGP-signed message. [Wikipedia; scream314]
- **Verbatim message:** *"Hello. The path lies empty; epiphany seeks the devoted. Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction. Seek and you will be found. Good luck. 3301"* — followed by the warning **"Beware false paths. Verify OpenPGP 7A35090F."** [scream314]
- Signature metadata (documented): signed **2016-01-01 00:01:07 UTC**, valid signature from key **0x181F01E57A35090F (7A35090F)**. [scream314]
- Significance: an explicit statement that **the Liber Primus itself is now the puzzle** ("Liber Primus is the way") — confirming the transition from a linear recruitment chain to the book as the standing challenge.

---

## The April 2017 message (the last verified one), then silence

- On **April 29, 2017**, a user in the official **#cicadasolvers IRC** channel found a previously unnoticed PGP-signed Cicada message on **Pastebin** (by searching the key "7A35090F" and sorting by date). [scream314; archive.4plebs]
- The message had been **signed on April 4, 2017 (~23:23 GMT)** with key **7A35090F**. Pastebin link of record: `https://pastebin.com/yEiTHhvF`. [scream314]
- **Verbatim text:**
  ```
  -----BEGIN PGP SIGNED MESSAGE-----
  Hash: SHA512

  Beware false paths.
  Always verify PGP signature from 7A35090F.

  3301
  ```
  [scream314; 4plebs thread]
- This is generally regarded as the **last verified, PGP-signed Cicada 3301 communication**. Wikipedia frames the April 2017 statement as their last verified OpenPGP-signed message, denying the validity of any unsigned puzzle. **Since then: silence.** [Wikipedia; scream314]

---

## Documented vs. rumored — quick reckoning

**Documented (primary artifacts / strong record):**
- Use of OutGuess, OpenPGP signing, Tor sites, book ciphers; the Gematria Primus 29-rune/prime alphabet; the totient cipher; the existence and partial solving of Liber Primus (~17 of ~74–75 pages). [Wikipedia; scream314; boxentriq]
- The **verbatim 2016 and April-2017 PGP-signed messages** and the **7A35090F** key/fingerprint. [scream314; 4plebs]
- No 2015 recruitment puzzle. [Wikipedia]

**Documented-community-record (reliable but not 3301-signed):**
- The exact 5×5 magic square matrix and the per-image page-dump mechanics — well-attested in solver archives. [scream314]

**Rumored / speculative / hoax-prone — flagged as such:**
- *Why* it stalled (private solvers "won and went silent," intentional open-endedness, etc.) — **speculation**.
- Persistent claims linking Cicada 3301 to intelligence agencies, secret societies, banking cartels, AI, or a cult — **unverified rumor/lore**; Cicada itself has only ever said (via signed text) that it seeks "highly intelligent individuals." Treat any **unsigned** "Cicada" puzzle, statement, or "solution" after April 2017 as **presumed fake** per Cicada's own warning. [Wikipedia; scream314]

---

## Sources

- Wikipedia — Cicada 3301: https://en.wikipedia.org/wiki/Cicada_3301
- scream314 cicada3301 archive — Liber Primus: https://github.com/scream314/cicada3301/blob/master/liber_primus.md
- scream314 cicada3301 archive — 2016 message: https://github.com/scream314/cicada3301/blob/master/2016.md
- scream314 cicada3301 archive — 2017 message: https://github.com/scream314/cicada3301/blob/master/2017.md
- Boxentriq — Liber Primus guide: https://www.boxentriq.com/guides/cicada-3301-liber-primus
- Boxentriq — Totient Cipher tool: https://www.boxentriq.com/ciphers/cicada-3301-totient-cipher
- Boxentriq — First Puzzle Walkthrough (background on technique stack): https://www.boxentriq.com/guides/cicada-3301-first-puzzle-walkthrough
- Uncovering Cicada Wiki — Gematria Primus: https://uncovering-cicada.fandom.com/wiki/Gematria_Primus
- Uncovering Cicada Wiki — PGP Signed Message April 2017: https://uncovering-cicada.fandom.com/wiki/PGP_Signed_Message_April_2017
- Uncovering Cicada Wiki — 2016 Message: https://uncovering-cicada.fandom.com/wiki/2016_Message
- 4plebs /x/ archive — discovery of the April 2017 PGP message (Pastebin yEiTHhvF): https://archive.4plebs.org/x/thread/18951995/
- Connor Tumbleson — The Cicada 3301 Mystery (Puzzle 3 Solve), Parts 2–4: https://connortumbleson.com/2024/02/05/the-cicada-3301-mystery-puzzle-3-solve-part-2/ ; https://connortumbleson.com/2024/06/03/the-cicada-3301-mystery-puzzle-3-solve-part-3/ ; https://connortumbleson.com/2024/12/23/the-cicada-3301-mystery-puzzle-3-solve-part-4/

(Note: I was unable to fetch a couple of fandom pages directly — they returned HTTP 403 — so their content above is drawn from search-result excerpts of those same pages rather than full-page fetches.)
