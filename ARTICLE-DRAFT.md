# We Pointed a Frontier AI at the Internet's Hardest Unsolved Puzzle. Here's What It Found — and Didn't.

_Draft, 2026-07-10. Honest framing: **no unsolved page was broken.** This article's
claim is different, and it holds up: a frontier AI ran the experiments the community
proposed but never executed, closed long-standing open questions, corrected published
claims, and produced the field's first consolidated negative-results archive. That is
moving the needle on a puzzle whose entire remaining difficulty is knowing where NOT
to dig._

---

## The setup

Cicada 3301's **Liber Primus** — a 58-page book written in runes — has resisted the
world's puzzle-solving community since 2014. Roughly 56 pages remain undeciphered.
Over several weeks we ran Anthropic's frontier models (Claude Opus 4.8, with final
probes under Claude Fable 5) against it: seven multi-agent campaigns, ~70 distinct
attack families, every result scored by a validated rig that reproduces all known
solves before touching an unsolved page.

## What we can honestly claim

**1. We ran the experiment the community proposed and nobody ever ran.**
A wiki author once wrote about XORing the mysterious base-60 data on pages 49–51
against unused hex from the 2014 onion trail: *"I don't know how to XOR things, so
I'll leave this for somebody else."* Nobody did it — for a decade. We did. Both sides
turn out to be exactly 256 bytes (a suspicious, clean alignment) — and the XOR stays
statistically random. No payload. Question closed after ten years.

**2. We found data everyone's solver was silently ignoring.**
The three "spiral" token pages (relikd images 49–51) are base-60 numeric data — a
different data type than the runes — and they were **absent from the standard
machine-readable corpus** every automated attack (including ours) had been consuming.
We extracted the 256 decoded bytes, characterized them (high-entropy, not a
permutation, not ASCII, not an S-box), and tested them as a key, as ciphertext, and
as a book-cipher index. All null — they behave like true one-time-pad material. But
now it's *known*, not assumed.

**3. We tested "Cicada told us the method" — systematically.**
Every verified hint was mapped to operational methods: the book's own magic squares
as Hill-cipher matrices (all invertible mod 29 — a fair test; all null), the
GPG-verified 2016 hint "their numbers are the direction" as word-gematria self-keying
and as literal reading-direction transforms (null), the community's "count spaces as
runes" and "OutGuess relocation" ideas (null / false premise). One deduction kills an
entire genre: the exhaustive keyword sweeps already covered **every possible keyword
up to ~12 runes** — so no hint-hunting can ever produce a keyword solve.

**4. We corrected the record in small, checkable ways.**
The claim that base-59 is the only encoding keeping the token data in byte range is
wrong (base-60 works too, maxing at exactly 255). scream314's widely-cited catalog
contains two adjudicated transcription typos — one provable against the solved
PARABLE page's plaintext (position 80 is the Y in DIVINITY) — plus one genuinely open
micro-question we surfaced: **does relikd image 56 begin with an extra ᚠ rune?**
scream314 says yes, three other lineages say no, and the page sits outside the range
verified by the field's only image-independent check. Someone with the image can
settle it in five minutes.

**5. We built the map so the next person doesn't start from zero.**
A mechanically-verified Rosetta Stone across the three incompatible page-numbering
schemes (it validated itself by rediscovering a known transcription discrepancy at
its exact documented position), a consolidated do-not-redo wall of ~70 attack
families with scores, and a reproducible probe suite — every negative is one
`python3` command from independent verification.

## What we cannot claim

We did not decrypt a page. Nothing came within noise-distance of readable English
(best ever: −6.02 against a break threshold of −5.0 on a scale where real English
is −4.3). And the analysis explains *why*: two mechanistic results — English running
keys inject adjacent doublets the ciphertext demonstrably lacks, and the observed
doublet suppression is *soft* (stochastic), the signature of a filtered random
keystream rather than any derivable rule. The Liber Primus behaves like a **one-time
pad whose key was never published**. If that's right, no amount of ciphertext
cleverness — human or AI — can break it, and the last honest sentence of the solved
pages already told us so: *"THE PRIMES ARE SACRED... ALL THINGS SHOULD BE ENCRYPTED."*

## Where the needle actually is now

The remaining live surface is external, and we say so precisely: a five-minute image
check on relikd 56's leading rune; a corrected transcription of token-page 50 (its
own transcriber flagged it "wrong!!!"); the deep-web page whose 512-bit hash the book
publishes; and the individuals who completed 2014's interactive phase — the only
channel through which a pad could have been delivered. Everything else is recorded,
scored, and closed in the public archive:
**github.com/Dukotah/cicada3301** (`NEGATIVE-RESULTS.md`).

Negative results are results. Ten years of "somebody should try X" is now a table of
"X was tried, here's the number, here's the script."
