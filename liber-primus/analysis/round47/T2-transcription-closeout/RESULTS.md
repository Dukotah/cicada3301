# R47 / T2 — Transcription close-out: RESULTS

_2026-11-24. Pre-registration: `PREREG.md` (sha256 `d9c40eb4…a3d8ddff` logged in `build_log.txt` before any read;
Addendum T2-A is disclosure only, full-file sha `e4b2e86f…365eb3a` logged after it). Nothing outside this folder was
written. No correction is applied; one position is flagged for the oracle._

## Headline

A third blind reader (T2) read all **27** of S1's look-alike-family glyphs on window lines, as **15 line strips**.
Every strip registered to its canon line with margin ≥ 1.4. **26 of 27 match canon.**

- **3 of the 4 disputed positions are now confirmed by an independent blind reader:** 276 = A, 5054 = TH, 6054 = AE.
  At each of them T2 agrees with canon and S1's blind read was the error.
- **gpos 9877 is not closed.** T2 read **M**, the same as S1's blind read. Canon has **D**, and so does the machine template
  (D 0.969 vs M 0.686). Under the pre-registered rule (§5: T2 = S1 ≠ canon), that makes it a **`canon-error-candidate`**,
  so it is **flagged for the oracle (`HUMAN-ORACLE.md`) and not applied**.
- The evidence on 9877 leans toward **reader error, not canon error**. T2 also read a non-target canon D on line 12
  (gpos 280) as M, and the template calls that one D at 0.949 vs 0.674 (Addendum T2-A, post hoc). So both "M" reads look
  like the same reader bias on this glyph shape. Independently of any reader, M at 9877 would follow the M at
  9876 and create a ciphertext doublet, which LP2's doublet rate (0.66 % vs 3.55 % for any given other rune) disfavours
  5.3 : 1; both blind M reads directly follow a true M (R47-X1). That makes it two readers who may share a bias against a validated
  template (MD 751/751), not an independent confirmation.
- **Controls:** W swaps **8/8 caught and 8/8 named**; C (solved page 73) **24/24**, 11/11 on family runes; plain
  exact-line glyphs in the W strips **48/48**.

**Is the transcription caveat fully closed? No.** It is closed for 26 of the 27 window glyphs and for 3 of the 4 disputed
positions. One position, gpos 9877 (D/M), stays open until the oracle or a higher-resolution master rules on it.

## Per-position verdicts (disputed four first)

| gpos | line:j | canon | T2 (conf) | S1 blind | template | verdict |
|---:|---|---|---|---|---|---|
| **276** | 12:14 | A | A (H) | AE | A | canon-confirmed (T2 blind) |
| **5054** | 232:18 | TH | TH (H) | W | n/a ¹ | canon-confirmed (T2 blind) |
| **6054** | 277:21 | AE | AE (H) | A | n/a ¹ | canon-confirmed (T2 blind) |
| **9877** | 455:6 | D | **M (M)** | **M** | D (0.969 / M 0.686) | **canon-error-candidate → oracle** |
| 277, 1590 ², 1591 ², 5781, 5782, 6053, 6532, 6533, 11334, 11335 | | O/A/AE | = canon | = canon or none | = canon where 1:1 | canon-confirmed ×10 |
| 5097, 9876 | | M | = canon | M | M | canon-confirmed ×2 |
| 5053, 7146, 9663 | | W, W, TH | = canon | = canon | = canon / n/a | canon-confirmed ×3 |
| 900, 6217 | | I | = canon | I | (I is not template-callable) | canon-confirmed ×2 |
| 1593 ², 6364, 6365, 11102, 11103, 11343 | | E | = canon | = canon or none | = canon / n/a | canon-confirmed ×6 |

¹ The strip read has more tokens than boxes (a segmentation merge), so there is no 1:1 box for the template. That leaves
T2 and canon in agreement against S1's blind read: two independent blind sources against one.

² S1 had **no blind read** here (crop misregistered by the old `alignment.json`; S1's own call was an unblinded re-read).
T2 gives the first blind read of these positions, and it equals canon.

The full rows, including every S1 row and the template top-3 scores, are in `results.json` → `targets`.

**T2 vs S1** on the 24 targets with an S1 blind read: 21/24 agree. The 3 disagreements are 276, 5054 and 6054, and S1 is
wrong at all three. At 9877 the two readers agree with each other and disagree with canon.

**By-product.** The strips' 99 non-target glyphs: T2 = canon on 98/99. The one miss is gpos 280 (canon D, T2 M, template D).

## Controls (power)

| control | result |
|---|---|
| **W** substitution: 8 exact-line strips, one box replaced by a different family member, sealed | **8/8 caught, 8/8 named** (D-shown ×1, M-shown ×2, A-shown ×2, O-, AE-, TH-shown ×1 each) |
| **C** solved `73.jpg`: 4 strips × 6 | **24/24** (CP95 [0.858, 1]); family runes 11/11 |
| plain glyphs in W strips (canon-labelled exact lines) | 48/48; family 18/18 |
| Q5 pipeline check after batch 1 | strips well-formed; nothing sealed was opened mid-run |

Both pre-registered gates pass (W ≥ 6/8; C ≥ 90 %). T2's family miss rate on controls is 0/19, so m_T2 ≤ **17.6 %**
(CP95 upper).

**Measured limitation.** T2 made 2 M-for-D errors on canon-D glyphs in window strips (280 for certain, 9877 probably).
On control D's it was right (1 D-shown swap, plus several D's among the 98 by-product agreements). So the reader's D→M miss
rate is **not zero on this font**, and the controls under-sample it. A third reader of 9877 should be judged with that in
mind.

## Two-reader canon error bound (updated)

The formula is the pre-registered §6 one: ε ≤ CP95(k, n) / (1 − m_S1 · max(m_S2, m_T2)).
Inputs: m_S1 = 0.265, m_S2 = 0.143, m_T2 = 0.176, so the joint miss rate is 0.047.
The population is all of S1's family glyphs with an S1 blind read plus one further blind reader: S2's 179 exact-line
glyphs plus T2's 24 window glyphs.

| family | n (S2 + T2) | k | **ε upper, R47** | R46 (X1) |
|---|---:|---:|---:|---:|
| **O/A/AE** | 72 + 10 = 82 | 0 | **4.6 %** | 5.2 % |
| **M/D** | 24 + 3 = 27 | 1 (9877) | **19.9 %** | 14.8 % |
| M/D if the oracle upholds canon at 9877 | 27 | 0 | 13.4 % | |
| TH/W/R | 46 | 0 | 8.1 % | 8.7 % |
| N/I | 24 | 0 | 15.0 % | 16.0 % |
| B/E | 24 | 0 | 15.0 % | 18.3 % |
| all five | 203 | 1 | 2.8 % | 2.1 % |
| all five, 9877 upheld | 203 | 0 | 1.9 % | |
| S1's full family census (206), second reader only | 206 | 1 | 3.2 % | |

The pre-registered rule counts the candidate as an error. That is why the M/D bound goes **up**, from 14.8 % to 19.9 %,
until the oracle rules. The M/D bound is limited by sample size (27 glyphs) whichever way 9877 resolves.

**Independence caveat.** All readers read the same relikd render, so their misses are not fully independent. The 9877 case
is exactly the situation where two readers may share a bias.

## The three conditionals (Q4)

1. **Read set.** A census of S1's 27 window-line family glyphs, plus 99 strip neighbours.
   **Not covered:** the other ≈ 1,800 off-exact positions and RAT's 149 unaligned positions.
2. **Location model.**
   - Lines are registered with the repaired `analysis/stones/alignment.json` (v2, R46-A1). It agrees with S1's
     `corrected_map.json` on 14 of 15 lines; line 291 is null in `corrected_map` and v2 places it.
   - Within a line, the blind token sequence is aligned to canon by semi-global edit distance. 13 strips align at cost 0,
     2 at cost 0.6 (the two D→M reads), and the margin is ≥ 1.4 everywhere.
3. **Reader.** One further vision reader (a different agent from S1, S1b and S2) on the sha-pinned relikd 2400×3600 renders,
   using R46/S2's solved-page reference strips.

## Blinding record

- `manifest.json` held strip ids only.
- 10 batches (≤ 25 boxes each) were sha-frozen in `reads_frozen.sha256`, with `heartbeat.txt` written after each batch.
- **`sealed.json` was not loaded by any code, inline or saved, before `unseal.py`**, which verifies all 10 hashes first
  (`unseal.log`).
- S1/S2 per-position files were opened only after the freeze.
- **Disclosed prior knowledge:** required reading had already given the family pairs of the 4 disputed gpos and S1's
  "D→M ×2, TH→W ×1" aggregate. Mitigations:
  - strips are opaque and shuffled, and the target's place in its strip is never shown;
  - on 9877 itself T2 read *against* canon, so the leak did not steer that read toward canon.
- Sizing probe `probe.py` printed no canon (PREREG §0).

## What reopens / closes this

- **9877:** the human oracle (`HUMAN-ORACLE.md`) or a higher-resolution master.
  - If upheld as D: the caveat is fully closed, with M/D ≤ 13.4 % and all five families ≤ 1.9 %.
  - If M: canon has a family error at 9877 (line 455), and the stream gains an MM doublet at 9876–9877 (9876 is M).
    LP2's doublet suppression alone makes that 5.3 : 1 less likely than D (R47-X1).
- A fourth reader or the oracle disagreeing with T2 at any of 276, 5054 or 6054.

## Files

| kind | files |
|---|---|
| Scripts | `probe.py`, `build.py`, `zoom.py`, `save_batch.py`, `unseal.py`, `posthoc_md.py` (Addendum T2-A) |
| Data | `manifest.json`, `sealed.json`, `reads_batch01..10.json`, `reads_frozen.sha256`, `heartbeat.txt`, `build_log.txt`, `unseal.log`, `unseal_stdout.txt`, **`results.json`**, `posthoc_md.json`, `ledger_rows.json` |
| Ignored | `crops/` (gitignored; regenerated by `build.py`) |

To reproduce, run from `liber-primus/`:

```
PYTHONUTF8=1 python analysis/round47/T2-transcription-closeout/build.py && … unseal.py
```

The reads are agent input and are not regenerated.

---
CLOSING STAMP — R47/T2 closed 2026-11-24. 27/27 window family glyphs read blind (15 strips, 10 frozen batches). W 8/8
named, C 24/24. T2 = canon 26/27. Disputed: 276, 5054, 6054 confirmed canon; 9877 = canon-error-candidate (T2 M = S1 M ≠
canon D = template D), flagged for oracle, not applied. O/A/AE ≤ 4.6 %, M/D ≤ 19.9 % (13.4 % if 9877 upheld). 0 corrections.

## X1 corrections applied

_Applied by the Round 47 coordinator from `../X1-redteam/AUDIT.md` §1.4 (2026-11-25); PREREG untouched._ Items 1–3: reading M at 9877 would create an MM doublet with 9876 (M), so LP2's doublet rate favours canon D about 5.3 : 1 independently of any reader; inserted in the summary and in "What reopens / closes this", and in `ledger_rows.json` `reopens_if`. The pre-registered verdict is unchanged: 9877 stays canon-error-candidate, flagged for the oracle. New row R47-X1-T2-9877-DOUBLET-PRIOR.
