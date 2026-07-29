# LP1 / LP2 Recon + Hypothesis Tests — 2026-07-28

Reconnaissance pass (intelligence, not brute force) over both sections of Liber Primus, plus
validated tests of the three not-in-ledger hypotheses the recon surfaced. All three tested clean
null. Dossiers: `LP1-METHODOLOGY.txt`, `LP2-STRUCTURE.txt`.

## LP1 recon — the author's demonstrated method (what we *can* read)
- The solved section is a deliberate difficulty ramp: plaintext → keyless Atbash → Atbash+Caesar
  → themed-word Vigenère → number-theoretic totient keystream (page 56, AN END).
- **Load-bearing finding:** every *word*-keyed page uses an **LP-thematic word taken from that
  page's own plaintext**, spelled in Gematria-Primus runes with the systematic C→F orthography
  (verified: `FIRFUMFERENFE` vs `CIRCUMFERENCE` differs at exactly the three C's). Key selection
  is **semantic, not numeric** — prime/totient-gematria tested null across 24 themed words. No
  page-to-page key derivation. F-skip interrupter uniform across keyed pages.
- **Pointer hunt:** the only solved plaintext referencing the unsolved corpus is page 56's
  512-bit hash ("...seek out this page") — it points **outward** to the dead Tor-v2 AN-END page,
  not to an in-book key.

## LP2 recon — structure of the unsolved section
- **Numbering settled:** krisyotam canon = 57 segments (0–56); unsolved set = segments **0–54**
  (55 = AN END keystream-gibberish, 56 = PARABLE plaintext). Divergence from relikd is **not a
  clean −1**: relikd keeps the pp49-51 base-60 TABLE as three physical pages that krisyotam
  silently omits, so relikd runs +3 ahead past the table.
- **Sections exist editorially, but the cipher does not reset:** three independent partitions —
  14 red-ink section heads, the base-60 table as a mid-book data-type discontinuity, and two
  margin-art page-sets — but Campaign IV proved the keystream is **continuous across all page
  joins** (doublet suppression holds even at boundaries). Editorial sections, no measured
  per-section key reset.
- **Bridge mapped, no usable key crosses in:** LP1 solved pages are an instructional preface; the
  two solved LP2 pages are strictly book-terminal; AN-END's hash points outward.

## The three hypotheses — all validation-gated, all NULL
| # | Hypothesis (genuinely un-run) | Gate | Result |
|---|---|---|---|
| **LP1-H** | Themed runic word × **no-repeat combiner** (29→28, forbids emitting a rune = prev ciphertext rune → *produces* the doublet deficit; dodges both additive + doublet exclusions) | PASS (planted key 100% recovered, 0 doublets, planted English −4.75) | **NULL** — 58 keys × both signs, best −6.88 (noise). Plus intrinsic nail: combiner is lossy (~4.4% of English un-encipherable) → unlike the author's clean solved ciphers |
| **LP2-H1** | Base-60 table as **per-section index/offset** keyed to the 14 red heads (never tested as an index) | PASS | **NULL** — index-concentration fails Bonferroni; 11 decode models best −7.20; fails geometrically (base-60 first digit 0–4 can't index 13–14 sections) |
| **LP2-H2** | Doublet **continuity restricted to the ~11 red joins** (all-joins test might dilute a sparse reset) | PASS | **NULL** — red joins 0.0 vs non-red 0.0 (perm p=1.0); red actually *lower* in 3×3 window — opposite of a reset |

## Net
Recon converted three plausible-sounding, previously-un-run framings into three sealed lanes,
each with a passing validation gate (so they're real falsifications, not broken harnesses). The
intelligence value: the author's method is **semantic themed-word keys that demonstrably do not
extend to LP2**, and the unsolved section has **editorial structure but no cryptographic section
seam** — both independently re-point at the single surviving lead, the **external AN-END page**.
No solve; the boundary is sharper. Ledger updated; artifacts under `analysis/recon/`.
