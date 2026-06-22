# Campaign VI — OSINT Key-Artifact Hunt (2026-06-22)

**Goal.** Campaigns I–V closed *internal* cryptanalysis of the runic LP2 pages (0–54):
verified-faithful OTP / long-running-key ciphertext, information-theoretically
unbreakable without an **external key**. The doublet analysis (Campaign IV)
*mechanistically* excludes any natural-English running key (English injects ~3.3 %
doublets; LP2 shows ~0.68 %). So if a key was ever published, it must be
**non-linguistic** — numeric / structured data. This campaign is a deep OSINT sweep
of the 2012–2017 corpus for exactly that.

**Method.** `deep-research` harness: 5 search angles → 15 sources fetched →
67 falsifiable claims extracted → 25 top claims adversarially verified
(3-vote, 2/3 refutes to kill) → 15 confirmed, 10 killed.

---

## Confirmed DEAD (stop circling these)

| Artifact | Verdict | Vote |
|---|---|---|
| **2017 "Beware false paths" PGP message** | No key/pad/coordinate/hash. `7A35090F`, `3301`, CRC `=6zQ2` are standard PGP signature mechanics, not cipher material. Purely an authentication warning. | merged 3-0 |
| "Page-32 numeric matrix" | Does not exist. | 0-3 |
| "Page-73 hex hash" | Misattribution — it's the **page-56** 512-bit hash. | 0-3 |
| "Base-60 indexes the page files 0–57.jpg" | False. | 0-3 |
| Onion cookie hashes (167=/761=) | Real, but **already tested** as keys (ARMADA #9, best −6.89). | (prior) |
| Magic-square digit streams (p05/p16) | Real, but **already tested** (best −6.54); palindromic, low entropy. | (prior) |

**Self-referential confirmations, not key payloads:** the cuneiform numerals on
pp33–39 read 17,13,55,1 → base-60 → 17×60+13 = **1033** (magic-square sum) and
55×60+1 = **3301** (group signature). Establishes base-60 as the intended
interpretive frame but yields no independent entropy.

---

## Live, UNTESTED leads (ranked)

### 1. pp49–51 "spiral data" — strongest lead
Community transcription says unsolved pages **49–51 are NOT runic prose** but a
**~250-element table of two-char tokens** (`3N 3p 2l 36 1b 3v 26 33 1W 49 2a 3g 47 04…`)
drawn from exactly **59 distinct characters** (all digits + upper/lower letters
*minus* `f`, `y`, `z`). Readable as base-59/60 positional notation → a byte stream.
Base-59 (alphabet `0-9 A-Z a-x`) is the only permutation whose decoded values all
fall in 0–255.

**Why it matters:** this is a *different data type* than the OTP-runic model the
campaigns assumed. **Action item (a):** verify how our rig represents pages 49–51
(runes vs. this token table). If they were modeled as runic, the OTP
characterization never applied to them.

> ⚠️ Recall (Campaign V): community page-numbering diverges from relikd image-numbering
> past ~p34, so "pp49–51" may be different physical pages than our 49–51. Resolve first.

*Caveats:* the exact 250 count rests on indexed snippets (fandom 403'd on direct
fetch); a specific base-60 decoded integer sequence was **refuted 0-3** as overclaimed.
Confidence: medium (2-1).

### 2. XOR pp49–51 data against the 2014 onion-trail hex — top untried operation
A wiki author explicitly proposed it and never did it:
> "XORing the data… probably the strings of hex from the 2nd, 3rd and 4th onion
> pages of the 2014 trail, which have never been used for anything yet. I don't
> know how to XOR things, so I'll leave this for somebody else."

Known leftover data + named target + an operation literally nobody has run. (3-0.)

### 3. 2012 Mayan rotation key — cross-round reuse
Confirmed Cicada-authored numeric key from the 2012 round:
`10 2 14 7 19 6 18 12 7 8 17 0 19` (per-character polyalphabetic rotation, used to
decode the 2012 Reddit posts). **Never tried against the LP rune pages.** Cheap to
run as a polyalphabetic shift over Gematria-Primus rune values. (2-1.)

### 4. `HINTS-NEVER-USED.md` leftovers — untested as Gematria keys
Cataloged in upstream `krisyotam/cicada3301` (same `liber-primus/analysis/` layout —
likely already local). The onion cookie hashes there were tested; **these were not**:
- 2012 end-message **P.S. digit string** (`1041279065891998535982789873959431895640…`, reads "3301" rotated 90°)
- **telnet missing-prime gaps** (gaps between 71 and 1229)
- **trailing-space anomalies** encoding prime sequences

### 5. page-56 512-bit hash — pointer, weak key candidate
`36367763ab73783c…132c2a8b4` (128 hex chars, SHA-512/BLAKE-512 shape), preceded by
"WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO…". A pointer to an unfound
page, not itself a usable key, but concrete structured data; testable for XOR/key
derivation. (3-0.)

---

## Open questions
1. Has the pp49–51 ⊕ 2014-onion-hex XOR ever actually been run? No source confirms it.
2. Exact complete pp49–51 sequence + element count, and which base (59 vs 60) yields a
   byte-range stream usable as a key/pad?
3. Have the `HINTS-NEVER-USED.md` numerics (P.S. string, prime gaps, trailing spaces)
   ever been applied as Gematria-Primus-indexed keys?
4. Does the 2012 Mayan key work as a polyalphabetic shift against Gematria rune values?

## Standing verdict (updated)
Internal cryptanalysis of the **runic** pages 0–54 remains **CLOSED**. But
**pp49–51-as-numeric-data** and candidates #2–#4 above are genuinely **not yet run** —
the OSINT sweep reopened a small, concrete experimental surface rather than confirming
total closure.

## Key sources
- uncovering-cicada.fandom.com — *Liber Primus pp49-51 data interpreted as base 59/60/62/64*; *Unsolved Pages*; *Art of Liber Primus*; *PGP Signed Message April 2017*
- github.com/scream314/cicada3301 — `liber_primus.md`, `2017.md`
- github.com/krisyotam/cicada3301 — `HINTS-NEVER-USED.md`
- clevcode.org/cicada-3301 (Mayan key, primary write-up)
- en.wikipedia.org/wiki/Cicada_3301; boxentriq.com/guides/cicada-3301-liber-primus
- ResearchGate 403192960 — *On the Forgery of Cicada 3301 PGP Signatures via SHA-1 Collision Attacks*

*Caveat: candidate sources are community/forum-tier — appropriate for "this data
exists" claims, NOT for any "this is THE key" assertion (none was confirmed).*
