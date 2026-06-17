# Liber Primus — Solved-Page Keys, Transcriptions & the Interrupter Rule

Reference compiled from a research scout over the solver community
(scream314, relikd/LiberPrayground, krisyotam, yo-yo-yo-jbo/cicada_tools,
Uncovering Cicada wiki, Boxentriq). Page numbering differs across sources —
three overlapping schemes: 2014 release filenames (`00.jpg`–`74.jpg`), the
LP1/LP2 split (LP1 = 17 pages, LP2 = `0`–`57`), and sequential rune-image nums.

## Canonical machine-readable transcriptions

- **krisyotam** (single file, easiest to curl — used by our `analysis/`):
  `https://raw.githubusercontent.com/krisyotam/cicada3301/main/liber-primus/runes-text.txt`
  Futhorc unicode; word sep `-`, title mark `.`, line break `/`, **page break `%`**.
- **relikd / LiberPrayground** (per-page + interrupter tooling):
  `https://raw.githubusercontent.com/relikd/LiberPrayground/main/pages/<page>.txt`
  Word sep `•`, period `⁘`, comma `⁚`, semicolon `⁖`, title mark `⁜`.
- **scream314** (best human writeup, per-page keys + plaintext — our gate source):
  `https://raw.githubusercontent.com/scream314/cicada3301/master/liber_primus.md`

## Solved pages (the entire solved corpus = LP1 + exactly 2 LP2 pages)

| Page | Title / first line | Method | Key |
|---|---|---|---|
| 00 | "Liber Primus" (cover) | plaintext transliteration | none |
| 01 | "A WARNING — BELIEVE NOTHING FROM THIS BOOK" | **Atbash** (reversed Gematria) | none |
| 02 | "Intus" | plaintext transliteration | none |
| 03–04 | "WELCOME, PILGRIM…" | **Vigenère** + F-interrupters | **DIVINITY** (shift up / subtract) |
| 05 | "SOME WISDOM — THE PRIMES ARE SACRED…" | plaintext transliteration | none |
| 06–09 | "A KOAN" / "DO FOUR UNREASONABLE THINGS…" | **Atbash + Caesar shift −3** | shift 3 |
| 10–13 | "THE LOSS OF DIVINITY…" | plaintext transliteration | none |
| 14–15 | "A KOAN… THE I IS THE VOICE OF THE CIRCUMFERENCE" | **Vigenère** + F-interrupters | **FIRFUMFERENFE** (=CIRCUMFERENCE, F-spelled) |
| 16 | (short) | plaintext transliteration | none |
| 73 (LP2 p56) | "AN END — WITHIN THE DEEP WEB…" (contains a SHA-512) | **φ(prime) keystream** + F-interrupters | running totient of primes (p−1) mod 29, shift down |
| 74 (LP2 p57) | "PARABLE — like the instar tunneling…" | plaintext transliteration | none |

**Everything from LP2 page `0` to `55` (files `17.jpg`–`72.jpg`) is UNSOLVED.**

## The ᚠ interrupter rule (critical, confirmed against our solves)

1. **Only `ᚠ` (index 0, prime 2, letter F) is ever an interrupter/null.**
2. **Not every `ᚠ` is one** — it is a per-page subset the solver must determine
   (not marked in the text).
3. **A null `ᚠ`:** removed from the readable plaintext and does **NOT advance**
   the keystream (no key letter / prime / totient step consumed).
4. **A non-null `ᚠ`:** enciphered like any other rune (advances the key).

Consequence (cribbing): only F is ever a null, so any non-`ᚠ` ciphertext rune
must come from a non-`ᚠ` plaintext rune. Calibrate a key on a block known to be
interrupter-free (WELCOME's first lines cleanly recover `DIVINITY`). Our
`src/lp/solve.py` implements the per-page interrupter search as a beam search.

> Note our empirical caveat (see FINDINGS.md): even with the correct key, a
> statistics-only interrupter search is ~90% accurate — distinguishing real vs
> null `ᚠ` is genuinely under-determined without ground truth.
