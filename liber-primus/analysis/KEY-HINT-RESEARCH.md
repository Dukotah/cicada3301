# Deep Research — Hidden Key/Method Hints for the Unsolved Liber Primus

_2026-06-17. 99-agent deep-research harness, adversarially verified (2/3 refute to kill)._

## Summary

There is no verified, recoverable KEY or confirmed METHOD hint for the unsolved Liber Primus pages (LP2 0–55); every concrete lead is either documented-but-undiscovered or has been tested and failed. The strongest primary-source self-referential hint is the solved "Some Wisdom" page (05.jpg), which names the exact cipher primitives used in solved pages — "THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED" — corroborated by Cicada's own @3301actual post; this supports (but does not prove) that solved-page text names the unsolved cipher's building blocks. The most concrete hunt-able artifact is the "AN END" page (page 56), which gives a specific 512-bit hash (36367763...c2a8b4) of a deep-web page declared every pilgrim's duty to find; the preimage/page has never been found, the hash algorithm is unconfirmed (SHA-512/BLAKE-512/BLAKE2b), and the leading "hash-as-ed25519-onion-key" interpretation was explicitly tested by cicada-solvers and FAILED across multiple byte-order/clamping variants. All claimed-insider key-knowledge cases (Wind/IRC, Marcus Wanner) are either community-rejected as non-credible or explicitly disclose no key/method, and the community's gating test for any future claim is a valid PGP signature from key 7A35090F. Net: the actionable leads are the totient/prime keystream family named on solved pages and the still-open hash-hunt, both already partially explored, with the easy interpretations ruled out.

## Findings (all high-confidence)

### 1. Self-referential hint #1 (highest-credibility key/method lead): The solved 'Some Wisdom' page (05.jpg / direct transliteration, no cipher) names the exact cipher primitives used in solved pages — 'THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED' — supporting (not proving) that solved-page text names the unsolved cipher's primitives (prime/totient keystreams).

**Confidence:** high (merged 2-1 (x2))

**Evidence:** Text confirmed verbatim across the cited wiki, scream314/cicada3301 liber_primus.md, and an independent transcription (iBotPeaches/cicada_3301 05.md). Crucially corroborated by a PRIMARY Cicada artifact: @3301actual posted the identical text ('The primes are sacred. The totient function is sacred. All things should be encrypted. #cicada3301 #BHUSA2016'). Primes and Euler totient ARE documented keystreams in solved pages (Boxentriq 'Totient Cipher': phi(p)=p-1 stream reduced mod 29 with the F-skip rule). The interpretive leap ('supports the hypothesis') is properly hedged; this is thematic/maxim-level, not a literal procedural instruction for pages 0–55.

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved
- https://github.com/scream314/cicada3301/blob/master/liber_primus.md
- https://x.com/3301actual/status/759942242563821568
- https://www.boxentriq.com/guides/cicada-3301-liber-primus

### 2. Hash-hunt target (the most concrete actionable artifact, lead #2): The solved 'AN END' page (LP2 page 56) states a deep-web page exists that hashes to the 512-bit value 36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4 (128 hex chars) and declares it 'the duty of every pilgrim to seek out this page' — a concrete, code-checkable target that could hold a key.

**Confidence:** high (merged 3-0 (x7))

**Evidence:** The hash is reproduced digit-for-digit across the Uncovering Cicada wiki (PAGE_56, Liber_Primus_Unsolved_Pages, How-pages-were-solved), Boxentriq, scream314/cicada3301, and the repo tweqx/3301-hash-alarm (whose description IS the verbatim message and which hashes candidate .onion pages against this value). Local arithmetic confirms exactly 128 lowercase-hex chars = 512 bits. Plaintext instruction 'IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE' confirmed (rune-transliteration 'DVTY/SEEC OVT').

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/PAGE_56
- https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Unsolved_Pages
- https://www.boxentriq.com/guides/cicada-3301-liber-primus
- https://github.com/scream314/cicada3301/blob/master/liber_primus.md
- https://github.com/tweqx/3301-hash-alarm

### 3. Hash-hunt STATUS: the preimage/target page has never been found, the hashing algorithm is NOT confirmed (candidates SHA-512, BLAKE-512, BLAKE2b — the 'SHA-512' label is an assumption), and what is hashed is unknown (candidates: a URL, an image/file, web-page contents, or a Distributed-Hash-Table file identifier for Freenet/GnuNet/P2P). The target page and any key it holds remain undiscovered.

**Confidence:** high (merged 3-0 (x3))

**Evidence:** Uncovering Cicada PAGE_56 states verbatim: 'The hashing algorithm is not known, but potential candidates are SHA-512, BLAKE-512 or BLAKE2b' and 'It is not known what is hashed. Possible options are a URL, an image or other file or the contents of a web page. The hash can also be a unique file identifier for deep web applications such as Freenet, GnuNET or P2P file sharing systems, which use Distributed Hash Tables.' LP2 remains 2/58 solved as of 2024; no source reports a found preimage. Note: Tor v2 deprecation (Oct 2021) makes any v2 .onion target unreachable.

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/PAGE_56

### 4. Hash-hunt NEGATIVE RESULT (rules out the leading interpretation): The cicada-solvers community tested interpreting the AN END hash DIRECTLY as an ed25519 secret key to derive a Tor v3 onion (deep-web) address — modifying mkp224o's ed25519_seckey_expand to bypass normal SHA-512 seed expansion — across multiple variants (custom hash, unaltered/skip-clamping via -DDONT_ALTER_HASH, reversed byte-order via -DREVERSE_ENDIANNESS). ALL generated onion addresses were unreachable; this 'hash is directly the key/address' family of theories failed.

**Confidence:** high (merged 3-0 (x3))

**Evidence:** Primary source: github.com/cicada-solvers/deep-web-hash-as-ed25519 README states the experiment is 'Documenting a failed attempt' and 'All onion addresses generated by this method are not reachable.' Three test flags documented verbatim (-DCUSTOM_HASH, -DDONT_ALTER_HASH 'skip secret modifications', -DREVERSE_ENDIANNESS 'reverses hash byte ordering'). Sibling repo cicada-solvers/Cicada-DWH-HashcatAttempts shows the community also pursued the hash by brute-force/hashcat means.

**Sources:**
- https://github.com/cicada-solvers/deep-web-hash-as-ed25519
- https://github.com/cicada-solvers/Cicada-DWH-HashcatAttempts

### 5. Authentication of self-referential clues as genuine (lead #3 primary-source basis): The 2016 Cicada message is cryptographically authenticated — GPG yields a good signature from 'Cicada 3301 (845145127)', key ID 7A35090F, fingerprint 6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F, signed 31 Dec 2015 19:01:07 EST (= 01 Jan 2016 00:01:07 UTC). So the 2016 'their numbers are the direction' clue is a primary-source Cicada statement, not a hoax.

**Confidence:** high (3-0)

**Evidence:** Good-signature line and full fingerprint reproduced verbatim across the cited wiki and two independent GitHub mirrors (scream314/cicada3301 2016.md, micheloosterhof/cicada-2016 stage01/README.md). Key 7A35090F is the documented Cicada signing key since 2012-01-03; Cicada's April 2017 message itself instructs 'Always verify PGP signature from 7A35090F.' NOTE: a good signature proves key possession, not metaphysical authorship — but it meets the domain's authenticity standard.

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/2016_Message
- https://github.com/scream314/cicada3301/blob/master/2016.md
- https://github.com/micheloosterhof/cicada-2016/blob/master/stage01/README.md

### 6. CREDIBILITY GATE for any claimed key/method hint or insider artifact: authenticity is decided by a valid PGP signature from Cicada's key 7A35090F (fp 6D85...090F). The 2012 'last chance' fake was proven illegitimate purely because it was signed by a different key (07CB82E3D0E8A26C, 'Wind 3301'). Any future key/insider claim must clear this gate.

**Confidence:** high (3-0)

**Evidence:** Fake_puzzles wiki states verbatim that the message 'was signed by the key 07CB82E3D0E8A26C ("Wind 3301")... which is not 3301's key, which proves this puzzle not to be legitimate.' The community-built 'isitcicada' tool (cicada-solvers) verifies messages client-side against the single canonical key by full fingerprint, confirming this is the operative authentication test. Corroborated by Know Your Meme, Bibliotheca Anonoma, ClevCode.

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/Fake_puzzles
- https://github.com/cicada-solvers/isitcicada

### 7. Insider key-knowledge claims (lead #5) are NOT credible: (a) IRC user 'Wind' (with same-IP accounts Mashima/Mahisha, IP 24.247.129.78 / Traverse City MI) repeatedly claimed 3301 membership and physical meetings with members but never provided proof — community consensus is she was not a real member; (b) documented winner/insider Marcus Wanner discloses NO key, method, or technical hint and states he has not solved the LP. No verifiable insider has hinted at or leaked a key.

**Confidence:** high (merged 3-0 (x2) [Wanner source = blog, but a negative/limiting claim about its own content])

**Evidence:** Fake_puzzles wiki: Wind 'claims to be a member of 3301, but never provided proof and it is commonly agreed that she wasn't.' (Minor nuance: Mashima/Mahisha are described as separate same-IP accounts, not strict aliases; Wind herself claimed the IP was fake.) Samizdat interview (verified by WebFetch) shows Wanner gives zero cryptographic detail, says 'Z has no idea what parts of the LP I've looked at,' and discusses only authentication (legit puzzles must be PGP-signed), not decryption. Rolling Stone / Wikipedia / Virginia Tech Magazine confirm Wanner's insider status but also that the inner project fizzled and he lacked canonical PGP materials.

**Sources:**
- https://uncovering-cicada.fandom.com/wiki/Fake_puzzles
- https://therealsamizdat.com/2019/10/24/cicada-files-marcus-wanner-speaks/

---

## What we did with these leads (tested in code, 2026-06-17)

**Lead #1 — totient/prime keystream ("primes/totient sacred", "numbers are the direction").**
Re-tested with an EXPANDED non-periodic keystream sweep across all 55 unsolved
pages: φ(n) for integers, iterated totient φ(φ(n)), prime gaps, cumulative prime
and cumulative φ(p) sums, page-number-seeded prime/totient streams, and
prime-indexed-by-prime — each with both signs and Atbash. **Best score anywhere
−6.81 (deep gibberish).** Nothing decrypts.
- **Principled exclusion:** any *additive* keystream over English plaintext
  produces a ~2.9–3.4% doublet rate; the unsolved pages show **0.66%**. So the
  whole additive-keystream family — prime, totient, fibonacci, periodic, or
  running — is ruled out by the doublet deficit. The hint names the *solved*-page
  primitives (which had normal doublets); it does not unlock the unsolved pages.

**Lead #2 — the "AN END" deep-web hash (36367763…c2a8b4).**
Not a cipher attack — it is a scavenger hunt for a deep-web page that was never
found. The leading "hash = ed25519 onion key" interpretation was tested by the
community and FAILED; Tor v2 deprecation (Oct 2021) likely makes any original
target unreachable. Nothing for our rig to compute; no recoverable key.

**Leads #3–#5 — PGP-authenticated clues / insiders.** The authentication gate is
PGP key 7A35090F; no credible insider (Wind = rejected; Wanner = discloses
nothing) has hinted at or leaked a key.

**Net:** the deep research surfaced no recoverable key or method hint. The one
code-actionable lead (number-theoretic keystreams) is now exhaustively tested and
additionally excluded on principle by the doublet evidence.
