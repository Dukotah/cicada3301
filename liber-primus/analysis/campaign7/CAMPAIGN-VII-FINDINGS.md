# Campaign VII — hammering the open surface (2026-07-07)

Executing [`MASTER-ROADMAP.md`](../../../MASTER-ROADMAP.md) §4: the concrete leads
Campaign VI reopened. Each probe applies a candidate key/pad as a mod-29 keystream
over the runic pages under the full variant sweep (sign ±, ±atbash, interrupter-aware
and not, per-page + whole-book). Bar: `score_norm > -5.2` = hit (real English
~ −4.0..−4.4; noise ~ −7.4; the rig finds DIVINITY at −4.34).

## Results so far

| Lead | What | Best score | Verdict |
|------|------|-----------:|---------|
| **B1** | 2012 Mayan rotation key `10 2 14 7 19 6 18 12 7 8 17 0 19` | **−6.895** | **null** — deep noise, no page |
| **B3** | HINTS-NEVER-USED numerics (P.S. digits ×3 readings, telnet missing-primes + gaps, trailing-space seqs 2012/13/14/15) | **−6.757** | **null** — every stream in noise |
| **A2/B2** | pp49-51 base-60 **token pad** (256 bytes) as key + XOR combos | **−6.720** | **null** as a direct mod-29 key |
| **A2-altbase** | token pad re-decoded under base-59/60/62/64, each as key | **−6.745** | **null** across all viable bases |
| **B2** | token pad **XOR the 2014 onion-trail hex** (2nd/3rd/4th onion) — the op nobody ran | **−6.597** | **null**; XOR stays high-entropy (no payload) |
| **token-as-ciphertext** | token bytes as their own cipher (256 single-byte XOR, keyword XOR, prime/totient/prime-1/fib streams mod 256) | printable 0.452 | **null** — no readable ASCII decode |
| **B4** | page-56 512-bit hash as key: raw bytes, hex-digits, SHAKE-256, SHA-512 & BLAKE2b chains | **−6.679** | **null** across all expansions |
| **C1** | **doublet-avoiding running key** (beam search over skip trajectory) vs Tao Te Ching / Gospel of Thomas / PGP prose | **−6.086** | **null** — no readable-English break |
| **token-as-index** | token bytes as a book-cipher index into the runes (abs / gaps / per-page) + as a self gematria message | **−7.339** | **null** — worse than noise (reordering destroys structure) |
| **C2** | cuneiform / base-60 numerals (17 13 55 1; 1033; 3301) as explicit keys | **−6.725** | **null** — confirms subsumption by exhaustive Vigenère |
| **false-holes** | community "untried" ideas: spaces-advance-keystream, first-rune shift, segment key-reset, OutGuess-relocation | **−6.847** (unsolved) | **null** — see below; FH3 re-solves known AN END but nothing new |

Reproduce: `python3 analysis/campaign7/{b1_mayan,b3_hints,a2_tokenpad,a2_altbase,b2_onion_xor,token_as_ciphertext,b4_hash_kdf,c1_skipkey,token_as_index,c2_cuneiform,false_holes}.py`

**Community "false holes"** (`false_holes.py`) — the wiki's own untried ideas, run so
the record is explicit: FH1 spaces-advance-keystream (−6.904), FH2 first-rune gematria
shift (−6.847), FH3 segment key-reset (−7.008 on unsolved; it *does* re-solve the known
AN END page at −5.28, proving the technique works but unlocks nothing new), FH4
OutGuess-relocation (not runnable — premise false; Campaign VII stego proved no payload
on the rune pages). All null on unsolved pages.
(writes `*_results.json` beside each script).

None of the confirmed-Cicada numeric artifacts decrypt the runic pages as an additive
keystream. This is consistent with the OTP verdict — but these were the specific
"never actually run" items, and they are now run and recorded.

## Genuinely new discovery — the token pages were never in our page set

The highest-value item. scream314's catalog
([`sources/community/scream314_liber_primus.md`](../../../sources/community/scream314_liber_primus.md))
documents that **relikd pages 49, 50, 51 are NOT runic prose** — they are **base-60
two-character token tables**, already decoded to decimal bytes (0–255):

- page 49 = 80 bytes, page 50 = 104 bytes (scream314 marks its base-60 read
  "wrong!!!"), page 51 = 72 bytes → **256 bytes total.**

Our rig's `run_stats.load_pages()` splits the krisyotam transcription on `%` and keeps
only rune-bearing segments, so **these three non-runic pages were silently excluded**
from every runic attack — and their byte data had **never been tested as a key/pad**.
Campaign VII is the first test.

**Structure of the 256 bytes:** min 0, max 255, but only **161 distinct** (68 values
duplicated) → **not a permutation of 0..255**, so not an RC4-style S-box or a clean
256-entry substitution table. The 80+104+72 = 256 total appears coincidental (and p50's
count rests on the disputed "wrong!!!" decode). High-entropy, full-range — the profile
of a pad or independent ciphertext, not a structured table.

**As a key:** applied directly as a mod-29 additive keystream (each page alone, all
three concatenated, `p49+p51` dropping the disputed p50, reversed, and pairwise XORs),
against every runic page and the whole book — **all null, best −6.720.** The token data
is not a naive Vigenère/OTP key over the runes in the obvious pairing.

### Why this still matters (what it does NOT rule out)

The naive "bytes mod 29 → Vigenère key" pairing is only the first cut. The token pages
remain the most interesting object in LP2 because they are a *different data type*, and
these are untested:

1. **Token pages as their own ciphertext.** 256 high-entropy bytes could be an encrypted
   payload (the "key" delivered enciphered), not a plaintext key. Needs its own attack.
   *(Note on the base: contrary to the community claim that base-59 is uniquely valid,
   both base-59 (max 251) and base-60 (max exactly 255) keep every value in 0-255;
   base-62/64 overflow. Both viable readings tested as keys → null.)*
2. **Byte-domain XOR against the runes**, not mod-29 — map runes→bytes (e.g. via the
   Gematria prime or index) and XOR the pad in byte space.
3. **XOR against the 2014 onion-trail hex** (the proper Track B2). The exact 2nd/3rd/4th
   onion-page hex strings still need sourcing — not present in our vendored corpus. This
   is the one operation a wiki author explicitly proposed and nobody ran; **still open.**
4. **p50 base-60 re-read.** scream314 flags its own p50 decode as wrong; a corrected
   transcription of the p50 token glyphs could change that page's 104 bytes.

## The token pages are OTP-like — avenue closed in every self-contained form

Follow-up on the discovery. Having pinned the pp49-51 token pad as the concrete
frontier, it was attacked from every angle that needs no external data:

- **As a key over the runes** (mod-29 additive, all bases, XOR combos): null.
- **XOR the 2014 onion-trail hex** — both sides now vendored (each exactly 256 bytes,
  clean full-length alignment). The XOR result stays **entropy ~7.1 bits, printable
  ~0.38, distinct ~160** — indistinguishable from random; **no payload emerges** — and
  as a key it is null (−6.597). This is the operation a wiki author explicitly proposed
  and never ran; **now run, and negative.** (The 2nd/3rd/4th onion hex is vendored at
  `sources/community/scream314_2014.md`.)
- **As its own ASCII ciphertext** (byte-domain, mod 256): 0/many decodes reach even 0.85
  printable; best 0.452 (random ≈ 0.37). Not enciphered ASCII text.

**Conclusion:** the token pad behaves as **true one-time-pad / random data** — the
last genuinely "different data type" in LP2 yields nothing in any recoverable pairing.
What could still change it: a **corrected p50 transcription** (scream314 flags its own
p50 base-60 read "wrong!!!"), or the pad pairing with a page/scan we don't have. Both
require new *external* input, not more computation.

## C1 — the one novel mechanism, tested

Finding #2 killed natural-language running keys because a real key *injects* ~3.3%
doublets while LP2 shows 0.68%. The escape hatch: a running key where the encoder
**skips a key char whenever the raw output would create an adjacent ciphertext
doublet** — this both reproduces the fingerprint and is *not* on the do-not-redo list
(which covered plain running keys and short-key collision-skip, not a long key with
insertions). Implemented as a beam search over the key-pointer trajectory (advance ∈
{1,2}), decrypting with quadgram-guided pruning, over Tao Te Ching / Gospel of Thomas /
Cicada PGP prose × a coarse offset sweep × the 6 longest pages.

**Result: null (−6.086).** The mild lift above pure noise (−7.4) is just beam-search
bias — the search cherry-picks English-looking fragments from *any* ciphertext, so
−6.0 is the floor here, not signal. No page crosses the −5.0 break. This is a bounded
mechanism test (3 texts, 6 pages, 3 offsets), not an exhaustive one, but it exercises
the single best-motivated uncovered mechanism and it does not light up.

## Data-provenance caveat surfaced by the token discovery

Verifying the token-page finding exposed a numbering mismatch worth recording:
`run_stats.load_pages()` returns **57 all-runic pages** (krisyotam `%`-split order), and
our page 49/50/51 hold **66/92/263 runes** — but scream314's **relikd** images 49/50/51
are the **80/104/72-token tables**. So **our per-page indices are krisyotam-order, not
relikd image numbers.** Consequences:

- When cross-referencing any community claim that uses relikd/scream314 numbering
  (e.g. "pp49-51 are token tables"), **translate the index first** — our "page 49" is
  not relikd image 49.
- **The cryptanalysis negatives are unaffected:** every Campaign VII (and prior) probe
  swept *all* pages *and* the whole-book concatenation, so coverage is label-independent
  — no page was skipped, only labels differ.
- A full krisyotam↔relikd page-map (anchored on the solved pages) is the clean fix and
  is now the remaining piece of roadmap A1. The token tables live in the relikd/scream314
  image set (vendored), not in the krisyotam rune corpus our rig loads.

## Standing status

- Roadmap **B1, B3 → CLOSED (null)**; recorded, do not re-run.
- Roadmap **A2 (direct-key form) → CLOSED (null)**; the token-pad-as-Vigenère-key is dead.
- Roadmap **A2/B2 remains OPEN** in the forms (1)–(4) above — the token pages are the
  live frontier. **B2 (token ⊕ 2014 onion hex) is blocked only on sourcing the onion hex.**
- Net: the OTP verdict holds, but Campaign VII converted three vague "never tried" leads
  into recorded negatives and pinned the token pages as the concrete object worth the
  next push.
