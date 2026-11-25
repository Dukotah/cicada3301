# Round 46 / L1 — one correct printed-word loader, and re-measurement of the ten word-indexed rows

_Pre-registered 2026-11-24, before any output of this lane. Lane spec: `analysis/round46/CAMPAIGN-PLAN.md` row L1.
Inputs read before writing (code and docs only, no runs): `ARMADA-DOCTRINE.md`, `round45/SYNTHESIS.md`,
`round45/I1-decoy-space/{RESULTS.md, arm_wordsched.py, arm_skeleton.py, common45.py}`, `round45/X1-redteam/{AUDIT.md,
x1_r41_linewrap.py}`, `round45/W1-spaces/w1lib.py`, `round41/C1-r14-r15/{camp7.py, run_c1.py, RESULTS.md}`,
`round37/C1-composed-clue-readings/{sweep.py, enciphers_u2_u3.py, c1lib.py}`, `round10/L2-map/mapcommon.py`,
`skeleton/wordlen_search.py`, `round38/C2-never-cells/lib.py`, `round10b/B3-semantic-keys/{b3lib.py, t1_titlecrib.py}`,
the ten `LEDGER.json` rows. The sha256 of this file is written to `run.log` before the first script runs; any later
addendum is appended below a `## Addendum n` header and its prefix sha is stamped in `run.log` (R45 rule)._

## 0. Hypotheses (instrument lane, doctrine R1)

- **H-L (loader).** A single loader can produce the printed words of LP2 (and LP1) from the canonical stream such that
  (i) the 12,956-rune stream is identical to `dataset/liber_primus.json` pages 0–54 and hashes to `PROBLEM.json`
  `ciphertext_identity.sha256_of_comma_joined_indices` (`023312066d…`), (ii) words break at `- . & $ §` and digits and
  NOT at `/` (line wrap) or `%` (page wrap), so line- and page-wrapping words are joined, and (iii) the LP2 count is
  2,896 (the R45-W1 / X1 figure). Any other count is reconciled word-by-word against each legacy loader.
- **H-P (power).** For each word-indexed instrument, power on LP2's real layout is measured under two plaintext
  regimes: **(a)** printed spaces = the plaintext's words, in order; **(b)** printed spaces = the plaintext's words,
  but the words were **shuffled within their sentence** before encipherment (H-shuffle at sentence scope, the reading
  W1 cannot exclude). As a pre-declared supplementary arm, **(b′)** printed lengths permuted within sentence over an
  in-order rune stream (H-decoy at sentence scope; the campaign plan's "spaces shuffled within sentence" wording).
  Each arm is also run through the instrument's **legacy loader** where it had one, to measure what the R41 defect cost.

## 1. Aiming Test

**Q1 — What would a hit look like, and would this instrument recognise it?**
A hit for the loader is: a plant rendered in krisyotam format on LP2's exact page lengths and line-break rune positions
(including words that wrap lines and pages) parses back to the planted word sequence exactly. A hit for each re-run
instrument is its own recognition rule applied to a planted decode: R41 W1–W4 = exact page recovery AND page pmax
above the lane's own matched-null max; R37 U2b/U3 = `sweep.judge()` (pmax120 ≥ bar_v3(1e6,120), pmax240 ≥
bar_v3(1e6,240), recovery240 ≥ 0.90); SKELETON = global argmax at the planted offset and count > max of 5 shuffled-pattern
scans (I1's rule); 7-gram = fraction of printed `3|3|head` windows whose true segmentation is `3|3|head`. Plants are
laid into LP2's real layout and parsed **through words.py**, not handed lengths directly (fixes I1's tautology, X1 §2.1).

**Q2 — What measured fact raises the prior?**
`round45/X1-redteam/AUDIT.md` §2.2: R41's loader split 420 line-wrapped words (3,316 vs 2,896) and its W1/W2/W4 page
recovery was 0.25–0.81 under true spaces. `round45/I1-decoy-space/RESULTS.md` §3: ten rows have power 1.0 → 0.00 under
H-decoy and keep power under H-shuffle *if the segmentation is right*. `round45/W1-spaces/RESULTS.md`: no word order at
any scope, so H-shuffle is live. This is a measured instrument defect (doctrine R1), not a key-space lane.

**Q3 — Is the space bounded?**
Yes, enumerable and small. No new key space. Real-data re-runs use each row's own frozen key space: R41-R14 = 20
deterministic variants × 55 pages (no key), R37 U2b/U3 = the recorded jobs on page heads 0–2 (re-run only where the new
loader changes a word length inside a decoded head or key array; otherwise equality is shown), SKELETON = the
repo-resident corpus (data/*.txt, data/keys/*.txt, skeleton/corpus/*.txt). Plants: ≤ 20 per (instrument × regime) cell.

**Q4 — Three conditionals carried by every result.**
1. **Key space:** none swept. Power cells use the correct key/schedule; real re-runs use each row's frozen space.
2. **Transition model:** R41 W1–W5 exact deterministic inverses (no skips, page reset, word assigned to the page it
   starts on); R37 U2b/U3 beam_v3 keyskip1/keyskip2 and direct A1/A2 as in the lane; SKELETON exact length match
   (slack 0); no `free` relation.
3. **Register:** panel-R36 (12 registers, sha a0682f0c…). Plants are English (`data/pride.txt`, EN mapping of
   `round10b/B6 detectors.text_to_runes`, the I1 convention) only; non-English shuffled-word power is NOT measured.

**Q5 — Kill condition at 10 % of budget.**
(i) If words.py cannot reproduce the PROBLEM.json stream hash, stop — the object is wrong. (ii) If the loader's LP2
word count ≠ 2,896 and the difference cannot be itemised against the W1 parser within the first checkpoint, stop and
report the reconciliation only. (iii) If plants under regime (a) through words.py give R41 W1–W4 exact recovery < 1.0,
the loader or the harness is broken: stop and fix before any power number is reported.

## 2. Instrument specification (frozen)

- **Stream identity.** `dataset/liber_primus.json` pages 0–54 `indices` concatenated = 12,956 runes, sha256 of
  comma-joined = PROBLEM.json value; krisyotam rune stream's first 12,956 runes equal it; per-page rune counts between
  `%` markers equal the dataset's `n_runes` for pages 0–54.
- **Separators.** data/krisyotam_runes.txt (LP2 + solved tail AN END, PARABLE); data/sources/rtkd_master.txt (LP1;
  its LP2 part asserted identical to krisyotam). Break set `- . & $ §` + digits; `/`, `%`, newline, whitespace do not
  break. Sentence boundary at `. & $ §`. A word carries: runes, global start, page of first rune, pages spanned,
  lines spanned, sentence id, `wraps_line`, `wraps_page`.
- **LP2 unsolved = words wholly inside runes 0..12,955.** Any word straddling the 12,955/12,956 boundary is reported.
- **Tests (stdlib, `test_words.py`, pytest-runnable):** stream hash; 2,896 count; zero-length words impossible; every
  `/` inside a word joins; the 32 page-wrap words; LP1 / solved-page segmentation reproduces the documented solved
  plaintext word lengths (PARABLE, AN END, and LP1 pages via `tests/validate.py`'s known transforms where the
  plaintext word list is available) ≥ 0.98 of words; legacy-loader counts reproduced (camp7 3,316; mapcommon/SKELETON
  2,928) so the reconciliation is mechanical.

## 3. Plant protocol on LP2's real layout

English words from `data/pride.txt` (I1's `common45.text_words` mapping, sentences split at `. ! ?`) are laid
contiguously over LP2's 12,956 rune slots. Rendering: `-` between words of a sentence, `.` at sentence ends, `/\n` at
every LP2 line-break rune position, `%\n` at every LP2 page-break position (so words wrap lines and pages exactly as
LP2's layout forces). Regime (a): sentences in order, words in order. Regime (b): words permuted uniformly within each
sentence (sentence order kept), then laid out — the printed spaces are the encipherer's words. Regime (b′): words in
order; the printed length list is a within-sentence permutation of the true lengths. The ciphertext is produced by each
lane's own encipherer on the TRUE word sequence of that regime; the decoder receives words parsed from the rendered text
by (L) words.py and (O) the lane's legacy loader.

Power = fraction of plants meeting the lane's recognition rule (§1 Q1), Wilson 95 % interval reported.

## 4. Pass/fail and verdict rules (fixed now)

- Loader gate: stream hash exact AND LP2 words = 2,896 AND all tests pass. Else verdict on loader = FAIL + reconciliation.
- A cell whose regime-(a) words.py control has power < 0.90 is **uninformative** for that instrument, not negative.
- Row verdict per regime: power ≥ 0.90 → the row's negative **holds** under that regime (as far as its own coverage);
  0.50 ≤ power < 0.90 → **weakened** (report power); power < 0.50 → **conditional** (negative does not bind under that
  regime). Under (a) the real-data re-run decides whether the row's recorded result changes.
- R41-R14 real re-run decision rule = R41's own: alpha 0.0025 per level (W whole-stream, P pages); crosses only if the
  family-Z p AND raw best-of-family p both ≤ alpha, against a matched blockperm null (blocks 100/250/1000,
  `benchmark/bars_matched.matched_shuffle`, Random(60000+j)) rebuilt with the new segmentation each draw. D = 1000 per
  block if a 20-draw timing probe projects < 25 min per block; else D = 400 (the smallest D at which p ≤ 0.0025 is
  reachable) with a heartbeat file. A crosser is **flagged-for-oracle** (`HUMAN-ORACLE.md`), never certified.
- R37 U2b/U3 and the four inherited U3-form rows: if the new loader leaves every word length inside the decoded heads
  and key arrays of pages 0–2 unchanged, the real decodes are identical by construction and the recorded result stands
  under (a); otherwise the affected jobs are re-decoded.
- No decode sweep. No new key space. No edits outside this folder. No `LEDGER.json` edit. No commit.

## 5. Not planned (stated now)

Non-English shuffled-word power; book-scope shuffles; re-running the R38/R39 lexicon sweeps themselves (inherit U3's
power; re-run only if their page-0–2 lengths change); the full 8.2 M-word SKELETON corpus if its files are not in the
repo (run on what is resident; report coverage).
