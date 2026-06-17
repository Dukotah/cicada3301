I have enough cross-verified material. Note the WebFetch on Grantland appears to have hallucinated some content (the "We have now found the individuals" message is actually well-attested elsewhere), so I'll attribute that line carefully to the multiple sources that quote it and flag the endgame as disputed. Here is the report.

---

# Cicada 3301: Origins and the Complete 2012 Puzzle Chain

## Origins

Cicada 3301 is the name attached to a set of cryptographic puzzles posted online under the moniker "3301," beginning on or about **January 4–5, 2012**, on 4chan. Two further rounds followed, each launching on January 4 of the next year (2013 and 2014), with sporadic later activity. The stated purpose every year was to **recruit "highly intelligent individuals,"** though who ran it and why has never been confirmed. ([Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301))

**Who was behind it: unknown / heavily speculated.** Theories range from the NSA/CIA/MI6/Mossad, to a Masonic or banking conspiracy, to a cyber-mercenary or hacktivist group, to an elaborate alternate-reality game (ARG) or marketing stunt. None of these is documented; they should all be treated as **speculation**. ([Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301))

> **Authenticity caveat:** The genuine 3301 signed its messages with a **PGP key**. After the early rounds, many copycat/hoax puzzles appeared. Only PGP-signed artifacts are considered authentically 3301; unsigned later material is generally treated as **unverified or hoax**. (General consensus across the Uncovering Cicada community and Wikipedia.)

---

## The Original 4chan Image and Its Text

The puzzle opened with a plain black-and-white image (white text on black) posted to 4chan's /x/ ("paranormal") board. Its text read, in substance:

> "Hello. We are looking for highly intelligent individuals. To find them, we have devised a test. There is a message hidden in this image. Find it, and it will lead you on the road to finding us. We look forward to meeting the few that will make it all the way through. Good luck. 3301"

The "3301" signature and the recruitment framing are the documented, defining features of the post. ([Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301); [All That's Interesting](https://allthatsinteresting.com/cicada-3301))

---

## The Documented Step-by-Step Solution Chain (2012)

The following sequence is consistently reported across a first-hand solver writeup (ClevCode), independent technical walkthroughs (Boxentriq, connortumbleson), and the Uncovering Cicada community. The major steps below are **documented and reproducible**; I flag the disputed/rumored parts explicitly.

### Step 1 — Hidden text in the image → Caesar cipher
Opening the image's raw bytes (e.g., in a text editor) revealed appended text:

> `TIBERIVS CLAVDIVS CAESAR says "lxxt>33m2mqkyv2gsq3q=w]O2ntk"`

Claudius was the 4th Roman Emperor → **Caesar cipher, shift 4**. Decoding produced an **Imgur URL** to a second image. ([Boxentriq](https://www.boxentriq.com/code-breaking/cicada-3301-first-puzzle-walkthrough); [connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/))

### Step 2 — The "duck" decoy → OutGuess steganography
The linked Imgur image looked like a near-blank/duck image with text containing the words **"out"** and **"guess,"** pointing solvers to the steganography tool **OutGuess**. Running OutGuess on the image extracted a hidden message containing a **book-code fragment** and a **Reddit link**: `reddit.com/r/a2e7j6ic78h0j/`. ([60out](https://www.60out.com/blog/unsolved-mystery-cicada-3301-cypher); [Boxentriq](https://www.boxentriq.com/code-breaking/cicada-3301-first-puzzle-walkthrough); [ClevCode](https://clevcode.org/cicada-3301/))

### Step 3 — The Reddit thread /r/a2e7j6ic78h0j, Mayan numerals, and a Vigenère key
The subreddit contained encoded text and images. **Mayan numerals** in the material decoded to the number sequence:

> `10 2 14 7 19 6 18 12 7 8 17 0 19 7 14 18 14 19 13 0 1 2 0`

This sequence was used as a **Vigenère cipher key** to decrypt the posted text. ([Boxentriq](https://www.boxentriq.com/code-breaking/cicada-3301-first-puzzle-walkthrough); [connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/))

### Step 4 — The book code: which book?
- The OutGuess/Reddit book code resolved against **William Hope Hodgson's / Bulfinch-style mythological texts** — specifically the **Mabinogion** ("The Lady of the Fountain," opening "King Arthur was at Caerlleon upon Usk..."). The Mabinogion / Arthurian text is the **well-documented** book used at this stage. ([connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/))
- **On "The King in Yellow":** Robert W. Chambers' *The King in Yellow* is widely **associated with Cicada lore** and appears in some later/other Cicada material and in popular retellings, but for the **2012 first-puzzle book-code step the documented texts are the Mabinogion (and later Gibson's *Agrippa* and the *Encyclopaedia Britannica*)**, not *The King in Yellow*. Treat a 2012-specific "King in Yellow" claim as **likely conflation/unverified**.

### Step 5 — The phone number
Decoding the book code produced spelled-out digits:

> "Call us at us telephone number two one four three nine oh nine six oh eight" → **(214) 390-9608**

Calling it played a recorded message stating that **three prime numbers** were associated with the original image. ([connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/); [Cybereason "Malicious Life"](https://www.cybereason.com/blog/malicious-life-podcast-the-mystery-of-cicada-3301))

### Step 6 — The prime-numbered image and 845145127.com
The original image's dimensions were **509 × 503 pixels** — both prime. The third prime was the signature **3301**. Their product:

> **509 × 503 × 3301 = 845,145,127**

Visiting **845145127.com** showed a **cicada image with a countdown clock** (counting to ~January 9, 2012 UTC). When the clock expired, the site posted **GPS coordinates**. ([Boxentriq](https://www.boxentriq.com/code-breaking/cicada-3301-first-puzzle-walkthrough); [connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/))

### Step 7 — GPS coordinates and physical posters in multiple cities
**14 sets of coordinates across five countries** pointed to real-world locations where solvers found **paper posters bearing a cicada image and a QR code** taped to poles/walls. Reported locations included Warsaw (Poland), Paris (France), Seattle (USA), Seoul (South Korea), Miami, Honolulu (Hawaii), New Orleans, the Salton Sea area (California), and Sydney (Australia), among others. The physical, multi-city aspect is **documented**; it required real people on the ground photographing the posters. ([Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301); [ClevCode](https://clevcode.org/cicada-3301/))

### Step 8 — QR codes → more book codes → a Tor (.onion) address
Scanning the QR codes led to **PGP-signed images containing two new book codes**:
- One keyed to **William Gibson's poem *Agrippa (A Book of the Dead)***
- One keyed to the **Encyclopaedia Britannica (11th ed.)**

Decoding produced a **Tor hidden-service URL** (reported as `sq6wmgv2zcsrix6t.onion`, with a near-duplicate variant). ([ClevCode](https://clevcode.org/cicada-3301/); [connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/))

### Step 9 — The onion site and the "first to arrive" gate
The hidden service told visitors to **create a new free, anonymous email address and submit it**, with a message along the lines of: *"We will email you a number in the next few days."* Crucially, the site only accepted a **limited number of the first solvers** before going offline — a deliberate **leaderboard/first-come gate**. ([connortumbleson](https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/); [ClevCode](https://clevcode.org/cicada-3301/))

> **Documented controversy at this gate:** It is well-reported that some solvers **publicly shared the .onion address**, which 3301 considered a violation. 3301 then posted (PGP-signed) words to the effect that **the solution was not meant to be shared publicly**, and the public/collaborative track was effectively shut down. The private email track continued only for those who had not leaked. (Reported by [ClevCode](https://clevcode.org/cicada-3301/) and the Uncovering Cicada community.)

### Step 10 — The final private emails (the part that goes dark)
Winners who submitted addresses **before the gate closed** reportedly received private emails. Beyond this point, **public documentation thins out and becomes second-hand**. Reported private-stage content (from participant comments, **not** independently verifiable) included **RSA challenges (small modulus to factor), MIDI/audio steganography, and substitution ciphers**, plus instructions to set up GPG keys. ([ClevCode](https://clevcode.org/cicada-3301/) — note these specifics rest on commenter testimony.)

---

## The Public Closing Message

After roughly a month, "3301" posted a **PGP-signed closing message** widely quoted as:

> "Hello. We have now found the individuals we sought. Thus our month-long journey ends. ... We are not a 'hacker' group nor are we 'Anonymous.' We are not the illuminati ... You are undoubtedly wondering what it is that we do — we are much like a 'think tank' in that our primary focus is on researching and developing techniques to aid the ideas we advocate: liberty, privacy, security. ... Thank you for your interest. 3301."

This message — declaring they had **found the people they were looking for** and describing themselves as a privacy/security "think tank" — is **documented and quoted across multiple sources**. ([Cybereason](https://www.cybereason.com/blog/malicious-life-podcast-the-mystery-of-cicada-3301); cross-referenced via the closing-message quote in [Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301) and community archives.)

---

## What Did Finishing the 2012 Puzzle Reportedly Lead To?

This is where **documented** ends and **rumored** begins:

- **Documented / strongly reported:** Solvers who reached the end were funneled into a **private channel** and the operation publicly declared it had **"found the individuals we sought."** For the **2013** round, it is reported by Wikipedia that finishers were **asked about their views on information freedom, online privacy, and rejecting censorship**, and that those who answered satisfactorily were **invited to a private forum and asked to devise/complete a project advancing the group's ideals**. ([Wikipedia](https://en.wikipedia.org/wiki/Cicada_3301))
- **Rumored / unverified for 2012 specifically:** Claims that 2012 winners were **recruited into an organization**, given jobs, asked to build **open-source privacy/crypto software**, or simply **disqualified everyone** because the solution leaked. The Uncovering Cicada community reports that final-stage winners essentially **"went dark."** One solver (handle "Tekk.nolagi") claimed the endgame was to **build do-gooding open-source software** and that he lost interest — but journalists who relayed this expressed skepticism, so treat it as **uncorroborated**. (Reported via [Grantland](https://grantland.com/hollywood-prospectus/a-wild-bug-chase-cracking-cicada-3301-the-internets-biggest-puzzle/) and community wikis.)
- **Bottom line:** **No verified, public account exists of what specifically happened to the 2012 winners after the private emails.** The honest answer to "what did it lead to" is **unknown.**

---

## Documented vs. Rumored — Quick Map

| Element | Status |
|---|---|
| Jan 2012 4chan image + recruitment text + "3301" sig | **Documented** |
| Caesar cipher (TIBERIVS CLAVDIVS CAESAR, shift 4) → Imgur | **Documented** |
| OutGuess stego → Reddit /r/a2e7j6ic78h0j | **Documented** |
| Mayan numerals → Vigenère key | **Documented** |
| Mabinogion book code | **Documented** |
| **"The King in Yellow" as the 2012 book** | **Unverified / likely conflation** (documented 2012 books are Mabinogion, Agrippa, Britannica) |
| Phone (214) 390-9608, prime message | **Documented** |
| 509×503 prime image → 845145127 → countdown site | **Documented** |
| GPS coords + physical posters/QR codes in multiple cities | **Documented** |
| Gibson's *Agrippa* / Britannica book codes → .onion | **Documented** |
| Public sharing of .onion broke the public track | **Reported / well-attested** |
| RSA/MIDI/substitution private-stage puzzles | **Second-hand commenter testimony — uncertain** |
| Closing "we have found the individuals" / "think tank" message | **Documented (PGP-signed)** |
| What recruitment actually led to (jobs, software, org) | **Rumored / unknown** |
| Who runs 3301 (NSA, MI6, ARG, etc.) | **Pure speculation** |

---

## Sources

- https://en.wikipedia.org/wiki/Cicada_3301
- https://www.boxentriq.com/code-breaking/cicada-3301-first-puzzle-walkthrough
- https://www.boxentriq.com/guides/cicada-3301-first-puzzle-walkthrough
- https://clevcode.org/cicada-3301/
- https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/
- https://allthatsinteresting.com/cicada-3301
- https://www.cybereason.com/blog/malicious-life-podcast-the-mystery-of-cicada-3301
- https://www.60out.com/blog/unsolved-mystery-cicada-3301-cypher
- https://grantland.com/hollywood-prospectus/a-wild-bug-chase-cracking-cicada-3301-the-internets-biggest-puzzle/
- https://www.fastcompany.com/3025785/meet-the-man-who-solved-the-mysterious-cicada-3301-puzzle (referenced; returned HTTP 403 on fetch, not directly quoted)

**Note on reliability:** The step-by-step chain (Steps 1–9) is corroborated across an independent solver writeup, two technical walkthroughs, and community archives, so it is treated as documented. The private final-stage contents (Step 10) and the ultimate purpose rest largely on participant testimony and are flagged as uncertain. I avoided asserting any specific identity for 3301, as none is verified.
