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

Reproduce: `python3 analysis/campaign7/{b1_mayan,b3_hints,a2_tokenpad}.py`
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
2. **Byte-domain XOR against the runes**, not mod-29 — map runes→bytes (e.g. via the
   Gematria prime or index) and XOR the pad in byte space.
3. **XOR against the 2014 onion-trail hex** (the proper Track B2). The exact 2nd/3rd/4th
   onion-page hex strings still need sourcing — not present in our vendored corpus. This
   is the one operation a wiki author explicitly proposed and nobody ran; **still open.**
4. **p50 base-60 re-read.** scream314 flags its own p50 decode as wrong; a corrected
   transcription of the p50 token glyphs could change that page's 104 bytes.

## Standing status

- Roadmap **B1, B3 → CLOSED (null)**; recorded, do not re-run.
- Roadmap **A2 (direct-key form) → CLOSED (null)**; the token-pad-as-Vigenère-key is dead.
- Roadmap **A2/B2 remains OPEN** in the forms (1)–(4) above — the token pages are the
  live frontier. **B2 (token ⊕ 2014 onion hex) is blocked only on sourcing the onion hex.**
- Net: the OTP verdict holds, but Campaign VII converted three vague "never tried" leads
  into recorded negatives and pinned the token pages as the concrete object worth the
  next push.
