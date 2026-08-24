# PREREG — Lane F-01: LP2-as-pad inversion

**Pre-registration date:** 2026-08-23  
**Lane:** F-01, Round 16 derived-keystream armada

---

## Hypothesis

The 12,956-rune unsolved LP2 stream is not ciphertext but KEY MATERIAL. Under this
inversion, Cicada may have encrypted a *shorter* object (a fragment, fragment pair,
message body, or hash-byte sequence) using the LP2 rune stream as a running key.

**Candidates for the ciphertext (shorter object being decrypted):**
1. The 2012/2013 English puzzle text fragments (the `cicada_2012_2013_puzzle_texts.txt`
   file, extracted as rune indices via `skipdecode.eng_to_idx`)
2. The solved LP1 pages (rune indices, all five solved pages concatenated)
3. The Cicada PGP message bodies (English text of all known PGP-signed messages)
4. The AN-END SHA-512 hash bytes, rendered as mod-29 indices
5. The `canon_256` / pp49-51 payload bytes, rendered as mod-29 indices

**Key material variants tested (LP2 stream as key K):**
- Forward LP2 stream
- Reversed LP2 stream
- Atbash of LP2 stream (index -> 28 - index)
- Negated LP2 (index -> -index mod 29)

**Decode relation:** `p = (c + sign * k) mod 29` for sign ∈ {-1, +1},
where c = candidate ciphertext rune, k = LP2 key symbol. The beam decoder
handles the skip filter desync.

---

## Pass/fail bar

- **HIT threshold:** score_norm >= -5.5 (repo-wide bar from PROBLEM.json)
- **Null:** size-matched (N=200) shuffled surrogates; candidate must beat null_max by 0.5
- **Confidence:** A HIT that reads as English prose on manual re-derivation

---

## Positive control (mandatory gate before trusting any null)

**Plant and recover:** create a synthetic ciphertext by XOR-ing (mod 29) the LP2 rune
stream against a known English plaintext, then run the beam decoder on that synthetic ct
using the LP2 stream as the key, and verify score jumps to English band (-4.2 to -5.0).

Specifically:
- Take the first 120 runes of LP2 as key K
- Encipher a known English sentence under the key-skip model
- Recover through beam_decode with K as key
- Gate: beam score >= -5.5 and >= null_max + 0.5 and > rigid_score + 0.5

A null with a FAILED positive control is NOT evidence.

---

## Size-matched null

For each candidate ciphertext of length L:
- Shuffle the candidate 200 times (seed 3301 .. 3500)
- Run beam_decode on each shuffle with the LP2 stream as key
- Record the null distribution (mean and max)
- Any real candidate must beat null_max by >= 0.5

---

## Coverage bound

Given the 8-minute compute budget, the following is the full enumeration:

- 5 candidate objects × 4 LP2 variants × 2 signs × beam offsets ∈ {0}
- Total: 40 primary decode runs (one per configuration)
- Plus: reversed-LP2 tested at all 4 offsets for the two highest-prior candidates
- All with skip-aware beam decoder (beam_w=400, max_skip=3)

This is a FINITE candidate set (not a statistical sweep) — every combination runs.

---

## What "HIT" requires

A configuration c* must:
1. Score >= -5.5 on the beam decode
2. Beat the size-matched null_max by >= 0.5
3. On manual re-derivation (fresh beam run): score >= -5.5 and text reads as English
4. The decoded text makes sense in the context of the Cicada 3301 puzzle

Absent (3): INCONCLUSIVE regardless of score.
