# RESULTS — Round 23 Lane A2: Printed-line-geometry acrostic

**Verdict: CLEAN NULL, control-validated.** No first-rune-of-each-printed-line (or
per-word) acrostic of the 5 rig-solved plaintext pages — read at the *true page-image
line breaks + word spacing* — is more English than chance at the pre-registered bar.
**0 family-wise survivors** over 48 reads; the single per-cell crosser is refuted by
default (below the expected false-positive count, gibberish, sub-family-bar).

This is the one representation R22-A could not build. It is now read. The result is the
same NULL R22-A returned on the geometry-free concatenation.

---

## Trust anchor

`python3 tests/validate.py` → **5/5 PASS** (Runes-01, 05, 06, 03, 14 all reproduced),
run before any scoring.

## Geometry source (and why it is trustworthy)

`data/scream314_lp.md`, loaded via `src/lp/corpus.py` — the **same transcription
`tests/validate.py` trusts**. Its per-page runes block preserves the page-image line
breaks (one text line = one printed line) and word boundaries (the `•` separator). No
second/looser transcription (e.g. `data/relikd/*`, which is ciphertext-only and a
different transcription) was used, so the geometry is guaranteed consistent with the
validated decrypt.

Plaintext-on-true-lines is built by decrypting each rune **in place** with the exact
transform `validate.py` reproduces (simple brute 01/05/06; vigenere + interrupter beam
03/14), keeping per-rune (line, word) bookkeeping. Interrupter (null ᚠ) runes emit
nothing and do not advance the key, exactly as `solve.decode`.

## Extractor validated (P0.3, hand-anchored) — YES

`PHASE0-GATE.py` P0.3 confirms the extractor reproduces:
- page 01's known **10** printed lines, and
- its line-first read = **`ABETFEDOEF`** — the first letters of the ten visible English
  lines (A WARNING / BELIEVE / EXCEPT / TEST / FIND / EXPERIENCE / DO NOT / OR THE /
  EITHER / FOR ALL).

Per-page flat decode also matches `validate.py`'s plaintext for all 5 pages
(e.g. 01 → `AWARNNGBELIEUENOTHNG…`, 05 → `SOMEWISDOM…`, 06 → `ACOANAMANDECIDED…`).

Line counts recovered: 01→10, 05→10, 06→20, 03→8, 14→8 (54 lines total; ~500 words).

## Phase-0 recognizer power (Q5 kill gate) — PASS, recovery = 1.000

Planted a known English acrostic in an i.i.d. control page laid out to the **same
line/word widths** as the longest real page (06: 20 lines, 194 words), then confirmed
recovery above the size-matched null bar:
- **P0.1 line-first plant:** recovered (`THEKEYTOTHEBOOKISFIN…`, score −4.29 > bar −4.80,
  line_first is the winning read).
- **P0.2 word-first plant:** recovered (`THEKEYTOTHEBOOKISFINDTHETRUTH…`, score −4.02 >
  bar −6.26, word_first is the winning read).

Recovery/power = **2/2 = 1.000**. The instrument provably sees a line/word acrostic when
one is present, so the real-data null is a genuine bound (not "instrument-broken").

## Coverage × power (doctrine R2, reported together)

- **Coverage:** 48 reads = {line_first, line_last, word_first, word_last} × {5 per-page
  + 1 concat-in-book-order} × {forward, reversed}, over the true printed geometry of the
  5 rig-solved pages.
- **Power:** Phase-0 recovery 1.000 on planted line-first + word-first acrostics of the
  same shape.
- **NOT covered:** keyword-cued / two-stage selections; mixed line+word diagonal reads;
  the wider community-solved LP corpus beyond the rig's 5; k-th-rune-per-line reads for
  k>1; non-English registers beyond the base32/IoC/gzip secondary screen; the
  `/dev/urandom` pad branch (an acrostic null says nothing about it).

## Sweep result

- 48 candidate reads, 20 distinct lengths, solved letter pool = 1887.
- Size-matched, structure-preserving null (1000 order-shuffles of the pool, seed 3301,
  FPR 1e-3), per length cell; family-wise bar = max null over all lengths = **−3.597**.
- Readable English scores ≈ −2.2; the best real read scores **−6.22**.

| reads | family survivors | per-cell survivors (FPR 1e-3) | expected FP |
|---|---|---|---|
| 48 | **0** | 1 | 0.048 |

Top reads by excess over own null bar (all gibberish):

```
06|word_last|rev     L=200  score=-6.223  excess=+0.025   YEOEEUNDREEGNARFDEOOEGNFCTDETEMIDGN...
CONCAT|word_last|fwd L=457  score=-6.445  excess=-0.011   ANGENGMSCTTUWOEETEEDRTHERTHOTTRESCRE...
06|word_last|fwd     L=200  score=-6.264  excess=-0.016   ANANDOODYTHARETOERFEROEUOSOYEDERETDE...
```

## Red-team (R6, mandatory) — refute-by-default

The single per-cell crosser, `06|word_last|rev`, is **refuted**:
- **Below the expected-FP count.** Expected per-cell FP over 48 reads at FPR 1e-3 =
  0.048; observing ~1 marginal per-cell crosser is fully consistent with noise.
- **Does not clear the family-wise bar** (score −6.22 vs family bar −3.60).
- **Trivial excess** (+0.025 over its own tiny-length-cell bar) — a length-cell-null
  artifact, not signal. Re-drawing the null at 5 alternate seeds keeps its score buried
  ~4 log-units below any English threshold.
- **Gibberish text** (`YEOEEUNDREEGNARFDEOOEGN…`), no readable English or pointer.
- **Secondary stats flat:** base32_frac 1.0 is trivial for any A-Z string (not a pointer
  signal); gzip 0.64 / min-distinct-32 = 8 reflect repeated OE/EO transliteration tokens,
  not structure.
- **No silent re-read:** A2 works the DECRYPTED plaintext geometry; distinct from Round-11
  N1–N5/S1–S2 (ciphertext number/value/separator channels) and from R22-A (geometry-free
  concatenation of the same plaintext). New input = the printed line/word geometry only.

**Survivors after red-team: 0.**

## Readable-vs-gibberish

No survivor to read. For completeness, the *visible* line-first acrostics are the plain
first letters of the visible English lines and are unremarkable — e.g. page 01
`ABETFEDOEF`, page 05 `STHTHACSAEOAC`, page 06 `AAHWTHTHWTHTHW…`. None reads as a message.

## Standing verdict / decision line

A2 surfaced **nothing** that justifies running D2 or B2. The sharpest surviving reopener
from R22-A — the printed-line-geometry acrostic — is now read at true resolution and is a
clean, control-validated NULL, consistent with R22-A's geometry-free NULL. Per the Round-23
roadmap seed, **the project sits at the natural stopping point at the tested resolution**:
every hinted channel read, every instrument audited. The only live-but-unreachable branches
remain the bounded-not-closed **PRNG/seed tail** (needs compute, not ideas) and the
**`/dev/urandom`** branch (needs the pad to surface) — neither is a Round-23 lane.

## Seal note (R21 L1)

Moot — no survivor to certify. Any bar-clearer would have been FLAGGED-FOR-ORACLE, not
auto-certified.

## Reproduce

```
cd liber-primus && python3 tests/validate.py            # 5/5
cd analysis/round23/A2-line-acrostic
python3 PHASE0-GATE.py                                   # 3/3 gates, recovery 1.000
python3 run_sweep.py                                     # 0 family survivors -> NULL
```
