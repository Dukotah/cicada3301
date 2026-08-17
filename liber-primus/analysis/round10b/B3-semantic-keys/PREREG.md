# Round 10B — Lane B3 — PRE-REGISTRATION

**Lane:** page-local SEMANTIC keys, derived the way a 2014 human solver would derive them.
**Written before any sweep was run.** Nothing below was edited after seeing results.

## 0. What is established (not re-derived here)

- `analysis/recon/RECON-SUMMARY-2026-07-28.md`: on the SOLVED pages key selection is
  **semantic, not numeric** — a thematic word taken from that page's own plaintext, spelled in
  Gematria-Primus runes with the systematic **C→F** orthography (`FIRFUMFERENFE`).
- `ELIMINATION-LEDGER.md:155` + `analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md:32`:
  ~620 Vigenère keywords already swept **skip-aware**, best −6.021, 0 hits.
- `ELIMINATION-LEDGER.md:305-320` (recon LP1-H): 58 themed keys × no-repeat combiner, best
  −6.88, CLOSED.
- `analysis/ARMADA-20-FINDINGS.md:40` (#14): crib-dragging under **running-key**, 9 thematic
  cribs, implied key matched as a *substring of reference texts*. No finding.
- `analysis/armada20/cribdrag.py`: the actual prior crib code — cribs dragged at every offset,
  implied key compared to reference corpora, **never scored as an English word in its own right**.

## 1. The gap this lane claims

Three things the prior work did **not** do, each stated so it can be checked:

**G-a. Orthographic/segmentation variants.** `gp.keyword_to_indices` is a single **greedy
longest-first** parse with a fixed alias table (`V→U, K→C, Z→S, Q→C`). Every prior keyword sweep
therefore tested **exactly one** rune spelling per Latin word. But the author's own demonstrated
key is `FIRFUMFERENFE`, which the greedy parser will **never** generate from `CIRCUMFERENCE` —
it only exists in the prior lists because a human typed it in by hand. The author also had free
choice at every multigraph boundary (`TH|T+H`, `EA|E+A`, `NG|N+G`, `EO|E+O`, `AE|A+E`,
`IA|I+A`, `OE|O+E`), and these change both the key **content** and the key **length**.
→ Novel axis: enumerate the orthographic orbit of each semantic word.

**G-b. Title crib at the alignment-safe point.** The three solved keyed/plain pages all open
with a short **title**: `03.jpg` = `WELCOME`, `14.jpg` = `A KOAN`, `05.jpg` = `SOME WISDOM`,
and the solved LP2 page `56` opens `PARABLE.`. The title is enciphered under the *same* key as
the body, starting at **offset 0**. Offset 0 is the one place in the corpus where the
~83%-active doublet/skip filter has had **no chance to desynchronise anything**. A title crib at
offset 0 recovers the true keystream prefix *whatever the keystream is* — it does not assume the
key is in any word list. Prior crib work dragged at all offsets under a running-key assumption
and never anchored on titles.

**G-c. Key readout scored as language.** The recovered keystream fragment is scored *as English*
and *as a word*, not matched as a substring of a reference corpus.

## 2. Structural observation the lane rests on (measured, reported in RESULTS)

Line census of `data/krisyotam_runes.txt`: LP2 unsolved segments have a uniform 12×~22-rune
body with **no set-apart short header line** (only seg 15's 9-rune line, which is a section
*trailer* — it precedes the `&`/`$` ornament pair, it does not follow it). LP2 titles are
therefore **inline**, terminated by `.` — exactly as the solved seg 56 shows (`PARABLE.`).
So the crib target is "the first sentence of a section", not "the first line of a page".

## 3. Hypotheses and exact pass/fail thresholds

### GATE (must pass or the whole lane is void)

- **GATE-1 (key search re-finds the ground truth).** Run the full expanded candidate set
  against `03.jpg` and `14.jpg`. PASS iff the **rank-1** key on `03.jpg` is a `DIVINITY`
  variant with `score_norm > -5.0` and plaintext containing `WELCOME` and `PILGRIM`, **and**
  the rank-1 key on `14.jpg` is a `CIRCUMFERENCE`-orbit variant (expected: `FIRFUMFERENFE`)
  with `score_norm > -5.0` and plaintext containing `KOAN`/`LESSON`/`CIRCUMFERENCE`
  (validate.py `canon()` collapsing).
- **GATE-2 (crib instrument reads out the key).** Crib `WELCOME` at offset 0 of `03.jpg`:
  the recovered keystream translit must be **exactly** `DIUINIT` (the `DIVINITY` prefix under
  the shared U/V rune). Crib `AKOAN` at offset 0 of `14.jpg`: must be **exactly** `FIRFU`.
  Exact string equality, no partial credit.

Either gate fails → ABORT and report the harness as broken. No negative may be reported
without both gates passing.

### T1 — title crib at LP2 section starts

For every LP2 section-start offset, and every candidate title in its full orthographic orbit,
compute the implied keystream `k` and score `k`'s transliteration with the repo quadgram scorer.

- **NULL CONTROL:** the same procedure with (a) 2,000 length-matched pseudo-titles drawn from
  the quadgram English generator, and (b) the same real titles against per-page **shuffled**
  ciphertext. Record null max and 99th percentile.
- **PASS (positive):** some real-title readout beats the null **max** by ≥ 1.0 score units
  **and** the readout is a recognisable English/Runeglish word ≥ 6 runes **and** repeating that
  readout as a Vigenère key over the whole page scores `> -5.2` under the interrupter beam.
- **FAIL (negative):** best real ≤ null max + 1.0. Reported as z vs the null distribution.

### T2 — orthography-expanded semantic key sweep, all unsolved pages

All 55 unsolved segments × full expanded candidate set × sign ∈ {−1,+1} × atbash ∈ {F,T},
rigid pass; anything above `−6.2` promoted to the interrupter beam.

- **PASS:** any (page, key) with beam `score_norm > -5.2` **and** validate.py-style word check.
- **NULL CONTROL:** identical sweep against per-page shuffled ciphertext; report null max.
- **FAIL:** best real ≤ −5.2, or best real inside the shuffled-null band.

### Novelty accounting (reported as a number, not a claim)

Report `|expanded ∩ prior_lists| / |expanded|` where `prior_lists` = the ~620-keyword sweep
list + `data/keys/thematic.txt` + `data/keys/words_expanded.txt` + `cribdrag.py` CRIBS,
compared as **rune-index tuples** (not Latin strings), because the whole point is that the same
Latin word maps to several different rune keys.

## 4. Scales

Page-scale quadgram `score_norm`: English ≈ −4.0…−4.4, noise floor ≈ −7.4, repo hit threshold
`−5.2`, campaign-18 null-max `−6.82`. All numbers in this lane are on that page scale.

## 5. What would make me wrong

- If GATE-2 fails, the crib arithmetic is wrong and T1 means nothing.
- If the null max for T1 lands within 1.0 of the real best, the readout scorer has no
  discriminating power at title length and T1 is under-powered rather than negative — that must
  be reported as INCONCLUSIVE, not NEGATIVE.
