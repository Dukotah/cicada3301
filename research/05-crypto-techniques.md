I have enough verified, sourced material to compile the technical reference. Compiling now.

---

# Cicada 3301: A Technical Catalog of Cryptographic & Steganographic Techniques

A working reference for someone attempting the puzzles. Each entry says what the technique is, how it appeared in the puzzles, and where it sits on the documented-vs-speculated spectrum.

**Scope note / skepticism warning:** Cicada 3301 ran three "official" rounds (2012, 2013, 2014), each opened on January 4 and authenticated with the same OpenPGP key. Everything after the 2014 round — and most "Cicada is still active" claims — is **unverified or hoax**. Many copycats sign with different (or no) PGP keys; the genuine key fingerprint is the only reliable authenticity test (see §10). The third major puzzle (the **Liber Primus**) is **largely unsolved**; only a minority of its ~58 pages are decrypted. Treat any "complete Liber Primus solution" as a hoax.

---

## 1. Image steganography — OutGuess (primary tool)

**What it is:** OutGuess hides data in the redundant/least-significant bits of JPEG coefficients, leaving the image visually unchanged.

**How it appeared:** This was the *first move* in every round. The 2012 opening 4chan image, run through `outguess -r` (v0.2), yielded ~535 bytes of hidden text. The 2014 opening JPEG hid a quote from Emerson's *Self-Reliance* plus book-code numbers. Throughout the Liber Primus distribution, OutGuess-embedded, PGP-signed messages were found inside many page images (00.jpg, 01.jpg, 03.jpg, 10–13.jpg, 43.jpg, etc.).

**Practical:** Always run a new image through OutGuess first: `outguess -r image.jpg out.txt`. Tools like `stegdetect` were also used to flag appended/embedded bytes.

> Note: the topic prompt lists **steghide** — across the firsthand solver write-ups reviewed here, the documented tool is **OutGuess**, not steghide. Treat "steghide was used" as **unconfirmed** unless tied to a specific artifact.

## 2. Appended-data / metadata steganography

**What it is:** Plain bytes tacked onto the end of a file or hidden in image dimensions/metadata, not true LSB stego.

**How it appeared:** Early analysis of the 2012 image found ~61 appended ASCII bytes. The **image dimensions themselves were a clue**: 509 × 503 pixels — both prime (see §6).

## 3. Caesar / shift cipher

**What it is:** Fixed-offset monoalphabetic substitution.

**How it appeared:** A 2012 hidden message contained the Latin tell `TIBERIVS CLAVDIVS CAESAR`. Claudius was the **4th** Roman emperor → shift of **4**. The string `lxxt>33m2mqkyv2gsq3q=w]O2ntk` decoded (shift back 4) to a URL.

## 4. Atbash

**What it is:** A reversed-alphabet substitution (first↔last letter). Cicada applied it over the **29-rune Gematria Primus alphabet**, not the Latin one.

**How it appeared:** The Liber Primus page "A Warning" (01.jpg) is an Atbash-style reversal of the 29-rune alphabet — solvable directly with a Gematria-Primus-aware Atbash tool.

## 5. Vigenère (polyalphabetic) — with the rune "F-skip" twist

**What it is:** A repeating-key shift cipher.

**How it appeared:**
- **2012:** Reddit posts were Vigenère-encrypted; the numeric key came from **Mayan numerals** in a header image (e.g. `10 2 14 7 19 6 18 12 7 8 17 0 19 7 14 18 14 19 13 0 1 2 0`).
- **Liber Primus:** Vigenère is applied over runes with recovered keys including **DIVINITY** (ᛞᛁᚢᛁᚾᛁᛏᚣ) on the "Welcome" pages (03/04.jpg) and **FIRFUMFERENFE** ("circumference" spelled in rune-transliteration) on later pages.
- **The F-skip rule:** Where the *plaintext/ciphertext* rune is ᚠ (F), it is skipped and does **not** consume a key/shift position. This breaks naive Vigenère cracking — you must account for it. (Same skip logic appears in the totient cipher, §7.)

## 6. Prime numbers & the totient function

**What they are:** Primes (only divisible by 1 and themselves); Euler's totient φ(n) counts integers below *n* coprime to it. For a prime *p*, **φ(p) = p − 1**.

**How they appeared:**
- **Dimensions:** 509 × 503 (both prime).
- **The signature number:** 509 × 503 × **3301** = **845145127**, used as the PGP key comment and as a `.com` domain.
- **Prime countdown video:** a clip printed all primes up to 3301, pausing ~2s at **1033** and **3301**.
- **Totient cipher (Liber Primus):** consecutive primes generate per-position shifts via `shift[i] = (prime[i] − 1) mod 29`; decrypt with `plain = (cipher − shift[i]) mod 29`, mod 29 for the 29-rune alphabet. Documented example: shifts (1,2,4,6,10) from primes (2,3,5,7,11). Same **F-skip** applies. Used on pages such as "An End" (56/73.jpg).

## 7. The Gematria Primus alphabet (rune ↔ letter ↔ prime)

**What it is:** Cicada's custom 29-character alphabet (introduced 2013, central to Liber Primus). Each entry maps an Anglo-Saxon **futhorc rune** ↔ a **Latin letter (or digraph)** ↔ a **prime value**, the primes being the first 29 primes in order. A word's **gematria sum** = sum of its rune primes (e.g. "The Instar Emergence" = 761, matching the audio filename 761.mp3 — a built-in checksum).

| Rune | Letter | Prime |  | Rune | Letter | Prime |
|---|---|---|---|---|---|---|
| ᚠ | F | 2 | | ᛋ | S/Z | 53 |
| ᚢ | U/V | 3 | | ᛏ | T | 59 |
| ᚦ | TH | 5 | | ᛒ | B | 61 |
| ᚩ | O | 7 | | ᛖ | E | 67 |
| ᚱ | R | 11 | | ᛗ | M | 71 |
| ᚳ | C/K | 13 | | ᛚ | L | 73 |
| ᚷ | G | 17 | | ᛝ | NG/ING | 79 |
| ᚹ | W | 19 | | ᛟ | OE | 83 |
| ᚻ | H | 23 | | ᛞ | D | 89 |
| ᚾ | N | 29 | | ᚪ | A | 97 |
| ᛁ | I | 31 | | ᚫ | AE | 101 |
| ᛄ | J | 37 | | ᚣ | Y | 103 |
| ᛇ | EO | 41 | | ᛡ | IA/IO | 107 |
| ᛈ | P | 43 | | ᛠ | EA | 109 |
| ᛉ | X | 47 | | | | |

**Practical gotchas:** the digraph runes (TH, EO, NG, OE, IA/IO, EA, AE) mean rune-count ≠ letter-count; U/V, C/K, S/Z share runes. The alphabet closely tracks an Anglo-Saxon **rune poem**, which is itself a thematic/hint source.

## 8. Book ciphers / literary keys

**What it is:** Numbers reference page/paragraph/line/word/letter positions in a specific text to spell a message — so you must identify the exact edition/source.

Documented source texts:
- **The Mabinogion** (specifically *"The Lady of the Fountain"*, via Thomas Bulfinch's *Mythology* / Project Gutenberg pg5160) — 2012 book code → phone number / coordinates. Clue: *"In twenty-nine volumes, knowledge was once contained… How many lines of the code remained when the Mabinogion paused?"*
- **Agrippa (A Book of the Dead)** by William Gibson — a famously self-erasing poem; its book code decoded to a Tor onion address.
- **Self-Reliance** by Ralph Waldo Emerson — 2014 opening; the quote + numbers built a URL.
- **The King in Yellow** by Robert W. Chambers (1895) — referenced as a clue/source in 2012. *(Used as a thematic/clue reference; its precise role is less rigorously documented than Mabinogion/Agrippa — treat exact mechanics as partially **unverified**.)*
- **The Book of the Law** (Aleister Crowley) and **William Blake** (*The Marriage of Heaven and Hell* — "for everything that lives is holy") appear as **thematic/answer references**, per Wikipedia. Whether they functioned as literal book-cipher keys is **less certain** than the four above.

## 9. Magic squares

**What it is:** A grid where every row, column, and main diagonal sum to the same constant.

**How it appeared:** Squares appear in the 2014 puzzle and in Liber Primus pages, functioning mainly as **verification/calibration** artifacts and thematic confirmation rather than primary decryption keys. Documented magic constants from solver archives include **1033** and a **5×5 square summing to 620**.

> **Caution:** A widely repeated claim is that a Cicada magic square sums to **3301**. The 3301-summing square is real in community lore, but the specific squares confirmed in the firsthand solver/archive sources reviewed here had constants of **620** and **1033**. Treat "the magic square sums to 3301" as **plausible but verify against the specific page** before relying on it.

## 10. PGP / OpenPGP signatures (authentication)

**What it is:** Public-key signatures proving a message came from the holder of Cicada's private key.

**How it appeared:** **Every** genuine clue was signed by the same key. Solvers verified with `gpg`, getting `Good signature from 'Cicada 3301 (845145127)'`. The short **Key ID 7A35090F** is the canonical authenticity marker — this is the single best filter against impostors and copycats.

## 11. Tor hidden services (.onion)

**What it is:** Anonymous services reachable only over the Tor network.

**How it appeared:** Book ciphers (e.g. via *Agrippa*) decoded to onion addresses (e.g. `sq6wmgv2zcsrix6t.onion`). Some onion stages gatekept progress (email submission, RSA-encrypted keys, MIDI files). One Liber Primus instruction even asked solvers to **"create a Tor hidden service that can accept CGI file uploads."**

## 12. RSA / number-theoretic challenges

**What it is:** RSA security rests on the hardness of factoring large semiprimes.

**How it appeared:** A Tor stage presented an RSA modulus (reports cite a ~112-digit number) requiring factorization (Number Field Sieve class of methods) to proceed. *(Exact digit count/parameters vary across retellings — treat the "112-digit" figure as approximate.)*

## 13. QR codes

**What it is:** 2D barcodes encoding URLs/text.

**How it appeared:** Physical **posters** were placed at GPS coordinates worldwide; each carried QR codes pointing to unique images/clues on Cicada domains (often then re-entering the stego/cipher chain).

## 14. Audio steganography & spectrograms

**What it is:** Data hidden inside audio — either in a spectrogram (visible when frequency-analyzed) or encoded structurally (e.g. MIDI pitch/duration).

**How it appeared:** Original tracks **"The Instar Emergence"** and **"Interconnectedness"** carried data; solvers used spectrogram tools (e.g. Sonic Visualiser) to surface hidden links/text. MIDI files at Tor stages encoded instructions via note data. The "The Instar Emergence" filename = its gematria sum **761** (see §7), tying audio to the rune cipher.

## 15. Multi-media / out-of-band delivery (meta-technique)

Clues deliberately spanned channels — 4chan/Reddit, image files, **telephone** (a 2012 voicemail gave the 503/509/3301 primes), original music, **bootable Linux CDs/disk images** (with data hidden in unallocated/OOB regions), physical paper posters, and the runic books. The recurring pattern: *stego → cipher → number theory → new channel*, all gated by **PGP** verification.

---

## Quick operator's playbook
1. **Verify PGP** (Key ID 7A35090F). No valid signature → likely copycat/hoax.
2. **Run OutGuess** (`outguess -r`) + `stegdetect`; check appended bytes and **image dimensions for primes**.
3. **Spot the cipher tell** (Latin names → Caesar shift; Mayan numerals → Vigenère key).
4. **Identify the book** for any positional number stream (Mabinogion / Agrippa / Self-Reliance / King in Yellow).
5. **For runes:** transliterate via Gematria Primus, then test **Atbash → Vigenère (keys like DIVINITY, FIRFUMFERENFE) → totient/prime-stream**, always honoring the **ᚠ F-skip**.
6. **Compute gematria sums** as checksums (match filenames/numbers).
7. **Check spectrograms/MIDI** in any audio; **decode QR** in any poster image.
8. **Follow onion/RSA** gates; magic squares are usually confirmation, not the key.

---

## Sources
- Wikipedia — Cicada 3301: https://en.wikipedia.org/wiki/Cicada_3301
- Wikipedia — The King in Yellow: https://en.wikipedia.org/wiki/The_King_in_Yellow
- ClevCode — Solving Cicada 3301 (firsthand solver write-up): https://clevcode.org/cicada-3301/
- Boxentriq — Cicada 3301 First Puzzle Walkthrough: https://www.boxentriq.com/guides/cicada-3301-first-puzzle-walkthrough
- Boxentriq — Gematria Primus Translator (rune/letter/prime table): https://www.boxentriq.com/encodings/gematria-primus-translator
- Boxentriq — Cicada 3301 Totient Cipher Tool: https://www.boxentriq.com/ciphers/cicada-3301-totient-cipher
- Boxentriq — Cicada 3301 Liber Primus Guide: https://www.boxentriq.com/guides/cicada-3301-liber-primus
- scream314 — cicada3301 / liber_primus.md (archive of solves, magic squares, keys): https://github.com/scream314/cicada3301/blob/master/liber_primus.md
- Uncovering Cicada Wiki — Gematria Primus: https://uncovering-cicada.fandom.com/wiki/Gematria_Primus
- Uncovering Cicada Wiki — How the solved pages of the Liber Primus were solved: https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved
- Uncovering Cicada Wiki — 2014 Puzzle: https://uncovering-cicada.fandom.com/wiki/CICADA_3301_2014_PUZZLE
- Connor Tumbleson — The Cicada 3301 Mystery (Puzzle 1 Solve): https://connortumbleson.com/2019/09/30/the-cicada-3301-mystery/
- The Register — Cicada 3301 2014 puzzle returns: https://www.theregister.com/2014/01/11/cicada_3301_2014/

**Confidence/uncertainty flags:** "steghide" usage (prompt-listed) is **unconfirmed** in reviewed sources — documented tool is OutGuess. The **3301-sum magic square** is community lore; confirmed magic constants here are **620** and **1033**. The RSA modulus size (~112 digits) is **approximate**. *King in Yellow*, *Book of the Law*, and Blake appear as references whose exact cipher mechanics are **less rigorously documented** than Mabinogion/Agrippa/Self-Reliance. The Liber Primus remains **mostly unsolved**; no complete solution exists.
