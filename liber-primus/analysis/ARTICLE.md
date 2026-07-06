# The Object in the Data Files

### Six AI campaigns declared the hardest puzzle on the internet a closed case. The one thing none of them had ever looked at was sitting in their own repository the whole time.

---

There is a particular kind of failure that only happens to people who are very thorough. You build the machine. You run it, and run it again, and run it a hundred different ways. You write down everything it rules out, so carefully that the list of dead ends becomes its own achievement. And somewhere in all that rigor, you stop noticing the thing you never fed into the machine at all — because it was never on the list of things to rule out. It was just *there*, in the folder, waiting.

That is the story of what happened when a swarm of AI agents spent six campaigns trying to break the last unsolved section of Cicada 3301's Liber Primus — and then, on the seventh, discovered that the one object nobody had ever loaded had been living in the project's own data files the entire time.

It is a story with two halves, and neither is the one you'd expect. The technical half is not "AI solved Cicada." It's subtler and, honestly, more interesting: AI-agent swarms methodically exhausted every hypothesis humans had proposed for cracking this thing, proved *why* the popular approaches must fail — and very nearly walked past the single un-analyzed piece of the puzzle in the process. The human half is a manhunt that comes back empty in a way that tells you something real about how the mystery was built.

Let's take them in order.

## A quick orientation, for the uninitiated

Cicada 3301 was a series of ferociously difficult puzzles that appeared on the internet starting in January 2012, signed by an anonymous entity using military-grade cryptography and a private PGP key. The puzzles blended steganography, classical ciphers, number theory, and a heavy dose of esoteric philosophy — privacy, enlightenment, "the primes are sacred." They were widely assumed to be a recruiting tool for *something*, though nobody outside the group has ever credibly said what.

The final artifact Cicada left behind is the **Liber Primus** — a book written in runes, most of which remains undeciphered to this day. Call the unsolved runic section LP2. It has resisted a decade of the best amateur and professional cryptanalysis the internet can throw at it.

The project at the center of this story is a home-built cryptanalysis rig — a system of orchestrated AI agents, each "campaign" a coordinated fan-out of dozens of agents attacking the problem from different angles, with every result committed to a repository and every dead end documented so the next campaign wouldn't waste effort re-running it. Over four campaigns, that rig reached a hard and honest verdict: **LP2's runic pages are statistically indistinguishable from a one-time pad.** To understand why that verdict was both correct and incomplete, you need to understand one number.

## The doublet deficit, in plain language

Here is the single most important thing the rig ever found, and you don't need any math to get it.

In normal written language, letters repeat next to themselves all the time. "Bookkeeper," "coffee," "hello" — double letters are everywhere. If you take any long English text and look at how often two identical letters sit side by side, you land around 3.4% of the time.

That's true of the *plaintext*. But here's the thing cryptographers rely on: it's *also* true of most ciphers built from a running key. If you encrypt a message by adding a stream of key symbols to it — an English book used as a key, a stream of prime numbers, digits of pi, anything that doesn't itself know what the message says — the encryption process injects roughly that same 3.4% rate of side-by-side repeats into the output. It's a statistical fingerprint. Nearly every "add a key stream to the text" cipher leaves it behind.

LP2 doesn't have it.

When the rig measured how often LP2's runes repeat next to themselves, it found a rate of about **0.66%** — against the ~3.45% you'd expect. Roughly four out of five of the expected doublets are simply *gone*. And they're gone in a very specific way: uniformly, across all 29 runes, with no periodicity, no pattern in *where* the missing repeats fall, and — crucially — no other structure anywhere else in the text. Off the diagonal, the cipher looks like perfect randomness. The only fingerprint in the entire stream is this one engineered hole where the double letters should be.

This is the key insight, and it reframes the entire decade of failed attempts. For years, solvers assumed LP2 was encrypted with some *running key* — some specific book, or poem, or number sequence — and that cracking it was a matter of guessing the right one. People tried hundreds of candidate texts. They all failed, and everyone assumed they just hadn't found the *right* text yet.

The doublet deficit says they were looking for the wrong *thing*, not the wrong text. **Any** plaintext-independent key stream — English, non-English, primes, raw numeric pads — would have injected that ~3.45% of doublets. They're absent. So the entire class of "guess the running key" attacks isn't unlucky; it's mechanistically impossible. This is arguably the rig's best intellectual product: it converts dozens of individual keytext failures from *"we didn't find it"* into *"this cannot be how it works."*

What's left, statistically, is a text that behaves like a one-time pad — a cipher whose key is as long as the message, used once, held externally, and never published. Against a true one-time pad, the ciphertext alone tells you nothing. There is no internal purchase. You cannot win from the inside.

Four campaigns reached that verdict. It was correct. And it quietly closed the case on the runic pages — which is exactly where the trouble started.

## The blind spot

Here is the sentence that reopened everything, and it came from an independent review by a separate model looking over the project's own conclusions:

*Every "LP2 is a closed one-time pad" verdict was only ever proven about the **runic** pages.*

Because three of the unsolved pages — 49, 50, and 51 — are not runic prose at all.

Page 49 has a few lines of runes and then a 10-by-8 grid of two-character tokens. Page 50 has no runes whatsoever — it's a 13-by-8 grid, pure table. Page 51 is a 9-by-8 grid plus four lines of runes. These aren't sentences. They're a *table of tokens*. And no campaign had ever loaded them, characterized them, or attacked them — because the rig's data loader only ingested the runic stream. The tables fell on the floor. Every statistical result, every "it's a one-time pad" conclusion, every carefully documented dead end — none of it had ever included these three pages, because the machine had never been fed them.

The pages weren't missing. They weren't hidden in some dead Tor onion or a deleted archive. The transcriptions were sitting in the repository's own data files — `p49.jpg`, `p50.jpg`, `p51.jpg`, and community token tables — the entire time. Six campaigns of exhaustive, documented, adversarially-verified cryptanalysis had walked past them because they weren't shaped like the thing the machine ate.

Count the tokens: **80 + 104 + 72 = exactly 256.**

That number is not an accident. 256 tokens. If each token is one byte, that's 256 bytes — **2,048 bits**. In the world Cicada lives in, 2,048 bits is not a random figure. It's a canonical cryptographic key length. Suddenly the three "leftover" pages look less like leftovers and more like the point.

## Campaign VII: reading three JPEGs

The seventh campaign did the unglamorous work the previous six had skipped. It's worth walking through, because the honesty of the result is the whole point.

**First, canonicalize.** Each two-character token turns out to be a base-60 number — a numbering system with sixty symbols, using the digits `0–9`, then the uppercase letters `A–Z`, then lowercase `a–x`. Sixty symbols exactly. A token like `3N` means 3 × 60 + 23 = **203**. The rig verified its decoding against a solver's independent decimal transcription: `3N → 203`, `3p → 231`, `2l → 167` — all matching. To build the canonical byte stream, the campaign cross-checked three independent witnesses cell by cell — the structural table, a token transcription, and an independent decimal decode — and adjudicated disagreements by majority vote. Of 256 bytes, 11 witnesses disagreed; 5 resolved cleanly, and **6 remain genuinely contested** and flagged as an open item, because settling them needs an OCR trained on Latin characters, and the project's 99%-accurate glyph classifier was trained on *runes* and can't read them. That honesty matters — those six bytes are marked as unsolved, not papered over.

There's a lovely detail buried in the encoding. The lowercase letter `f` — value 41 in this base-60 alphabet — is a perfectly legal symbol that **never once appears** in the data. That's the same "F-skip" convention Cicada uses in its own rune-to-number Gematria system elsewhere in the Liber Primus. It's a small signature that says: yes, base-60 was intended; you're reading this right. (A note for the careful: the community's looser version of this observation — that the alphabet "skips f, y, z" — is imprecise and doesn't survive scrutiny. `y` and `z` are simply out of range in a 60-symbol alphabet by construction. The one *in-range* symbol that never occurs is `f`. The distinction is the difference between a real fingerprint and a coincidence.)

The canonical 256-byte stream this produced **did not previously exist** in the solver community. It is, itself, a new primary source — the first documented byte-level rendering of pp49–51, with a full provenance and conflict table attached.

**Second, characterize.** What kind of object is this 2,048-bit stream? The campaign ran it through every test that matters:

- Its **entropy** is 7.17 bits per byte — genuinely high, near-random. 161 of the 256 possible byte values appear; 95 never do.
- Only 40% of it is printable ASCII, and the longest run of printable characters is five bytes. **It is not text.**
- Is it the "2048-bit sacred prime" that Cicada's *"the primes are sacred"* refrain seems to promise? **No.** Interpreted as a big-endian integer, as little-endian, reversed, and split into two 1024-bit halves — it is **composite in every single interpretation**. It's not even odd: the number ends in `0x50`, so it's divisible by two. A prime it is not.
- Is it an RSA public key — the product of two primes, the kind of number Cicada's cryptography is built on? **No.** RSA moduli are odd by definition. This one is even, with small factors. It cannot be one.

So the romantic hypotheses die here, cleanly. This is not a sacred prime, not a hidden RSA key, not a secret message in disguise. What it *is* consistent with is a **pad, a key stream, or a ciphertext** — high-entropy binary material that means nothing on its own and requires an external key to unlock. Which is to say: it belongs to exactly the same class the doublet analysis assigned to the runic pages. The one object six campaigns missed turns out to point at the same locked door as everything else.

**Third, attack it anyway.** Maybe the table is itself the key to the runes — especially the runic lines on its own pages, which are short enough that the doublet statistic doesn't bite. The campaign tried it exhaustively: **337,944 decryption configurations** — both canonical variants of the byte stream, forward and reversed, added and subtracted, run as Vigenère, Beaufort, and Atbash keys, swept across every unsolved page individually and the whole corpus. Calibrated against a known-English baseline and a random-noise floor, the best result any of those 337,944 attempts produced was **−6.385** — squarely in the noise. **Zero** configurations cleared the threshold for even being worth a human look.

For completeness, the campaign also ran the last two catalogued numeric keys the community had ever proposed — a 2012 "Mayan rotation key" and a long digit string from an end-of-puzzle postscript — through the same harness: another **76,360 configurations**, another clean null. And the once-tantalizing idea of XORing these pages against the 2014 Tor onion trail's hex data? Dead on inspection — that "hex" is just a JPEG file dump, an embedded image, not free key material.

So the net result of Campaign VII is not a solution. It's something more durable: **the one un-analyzed object in the entire corpus is now fully characterized** — provably not a prime, provably not an RSA key, provably not text, provably not a simple key over the runes — and every sourceable numeric lead anyone ever proposed has now been executed and documented as null. The residual mystery is honest and specific: pp49–51 is high-entropy material that would require an externally-held key to interpret, which is the same wall the runes hit. The rig didn't break Cicada. It did something a solver can actually build on: it drew the exact shape of what's left.

## The manhunt that comes back empty

If you can't break the cipher, you can try to find the person. That was the eighth campaign — a targeted OSINT sweep aimed at the single most likely candidate pool: the cypherpunks.

This is not a random guess. Cicada's DNA is cypherpunk to the core. PGP-first operational security. Tor infrastructure. The sacralization of prime numbers. An ethos of privacy and enlightenment that reads like it was lifted straight from the 1990s cypherpunk mailing list. A peer-reviewed paper in a Gnostic studies journal places Cicada's philosophy squarely "within the libertarian concerns of freedom of information and privacy" and situates it in the lineage of Eric Hughes, Timothy May, and John Gilmore — the founding cypherpunks. If Cicada came from anywhere, it came from that world.

So the campaign — 99 agents, 17 sources fetched, 70 claims extracted, 25 of them adversarially verified by a three-vote panel where two of three votes to refute killed the claim — went looking for a falsifiable thread connecting the ideology to a *person*. It checked four lenses. All four came back negative.

**Priority-of-knowledge leaks — the smoking gun.** Did any candidate ever reference a Cicada-specific fact — the runic book, the totient method, the "AN END" hash, the base-60 encoding — *before* it was publicly known? That would be a genuine tell. The answer was zero confirmed leaks. But — and this is the honest caveat that makes the whole result meaningful — this is absence of evidence, not evidence of absence. The relevant Tor v2 onions are permanently dead. The 2012–2014 IRC logs where such a leak would live are largely deleted. The 4chan threads are only partly archived. The highest-weight lens isn't *cleared*; it's *unresolved*, because the records that might have held the answer no longer exist.

**Technical fingerprints.** The campaign nailed down the anchors — the signing key `7A35090F`, RSA-4096, created January 3, 2012 — but found no attribution path. No web-of-trust links to other keys. No reused-key trail. A third-party "Cicada-3301" GitHub repo turned out to hold an unrelated key — a red herring. The community's own verification tool checks new messages against that single oldest key precisely *because* no trustworthy signing links to anyone else exist.

**Stylometry.** No verified comparison of Cicada's prose to any named candidate exists at any confidence level. Stylometry is never proof anyway — but here it didn't even produce a suggestive hit.

**Thematic alignment.** Well-supported, and explicitly non-attributive. Cypherpunk ideology is all over Cicada. But as one security podcast put it plainly when it raised the cypherpunk link: *"Can we be sure that a member of the Cypherpunks movement is behind Cicada? Of course not."*

The verdict, delivered honestly, is **"consistent-with, not evidence-of."** Cypherpunk *influence* is well-supported. Cypherpunk *authorship by any named person* is unproven — not because nobody looked, but because the falsifiable evidence doesn't exist in the surviving record.

There are a couple of details too good to leave out. That signing key's user ID is `Cicada 3301 (845145127)` — and 845,145,127 factors cleanly into **503 × 509 × 3301**, all three prime, with 509 and 503 being the exact pixel dimensions of the very first Cicada image. The number-mysticism runs all the way down into the metadata. And there's a thread worth noting honestly without overselling it: Niels Provos, the author of OutGuess — the *exact* steganography tool Cicada used to hide data in its images — surfaced in the research as the toolchain's source. There is nothing tying him to Cicada beyond that. It's a coincidence of provenance, not a lead. But it's the kind of coincidence that keeps a mystery warm.

## What it means that a puzzle is built to survive looking

Put the two halves together and you get the real shape of this thing.

On the technical side, a swarm of AI agents did something genuinely useful and genuinely humbling. It exhausted the human-proposed hypothesis space for LP2 and proved, mechanistically, *why* the popular attacks must fail — the doublet deficit rules out the entire running-key family, and the newly-characterized pp49–51 payload turns out to be one more locked box that needs an external key. That's real progress: it tells future solvers exactly where *not* to dig, and it produces a new primary source in the process. But the same swarm, for six campaigns, walked past the one object it hadn't been fed — a reminder that thoroughness and completeness are not the same thing, and that the most dangerous blind spot is the one that isn't shaped like the things you know how to check.

On the human side, the manhunt comes back empty in a way that isn't a failure at all. Cicada's author left a cryptographic trail so clean it has no web of trust, an ideology so legible it reads like a cypherpunk manifesto, and an operational discipline so complete that a decade later — after a targeted, adversarially-verified sweep of exactly the community they came from — not one falsifiable thread connects the philosophy to a person. The mystery survives not because no one has looked hard enough. It survives because it was *built* to survive looking. And because the parts of the record that might have betrayed the author — the dead onions, the deleted IRC logs, the un-archived threads — are simply gone.

The cipher may hold forever; a true one-time pad gives up nothing without its key. But the more durable lesson is the one about the object in the data files. The answer to the hardest question wasn't hidden in a place too clever to find. It was sitting in plain sight, in a shape nobody's machine had been taught to read — which, when you think about it, is the most Cicada thing of all.

---

*The full technical record — the canonical 256-byte stream, the characterization and key-test scripts, the doublet analysis, and the attribution sweep — is committed at [github.com/Dukotah/cicada3301](https://github.com/Dukotah/cicada3301), branch `findings-2026`. Every figure in this piece is reproducible from the standard-library Python in `liber-primus/analysis/pp49_51/`.*
