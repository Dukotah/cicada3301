# Round 45 — SYNTHESIS: the spaces are not the words

_Coordinator closeout, 2026-11-24. Lanes: M0 (committed `4aba42e`), I1, W1, T1, S1, S1b, X1.
Plan of record: `CAMPAIGN-PLAN.md`. Every lane pre-registered, planted its own control, and closed with a
stamp; X1 audited all of them. Verdict on the cipher: **OTP-class, UNCHANGED.** No decode was run._

## 1. What Round 45 established

1. **LP2's printed word breaks are not the plaintext's words in order: at no scale.** (W1, X1-upheld)
   Order statistics with 100% power on English at every scope: LP2 z = −1.2, solved Cicada pages ≈ +7.5 at
   LP2's size (95% range ≈ +3.6…+11.4). Twelve order tests null (all p ≥ 0.38). Segmenting at line or page
   breaks does not create order (X1). Not random spacing (p ≤ 5e-4), not periodic/keyed up to period 300,
   not tied to cipher runes, inside English's length spread. Best description: **an English-like length
   multiset over a contiguous rune stream, order destroyed** — true lengths permuted, or lengths from another
   text. Scope of the scramble (sentence/page/chapter/global) is **not identifiable** with these tools.
2. **The rune stream itself is contiguous in printed order** (W1 Q4): the doublet filter ran over runes as
   printed; ≥ ~80% of word breaks sit inside unbroken runs. Decoders should treat LP2 as one stream.
3. **The standing instrument stack never reads the spaces** (I1): beam_v3, pf_v4, panel-R36, bars_v3 and
   verify_solution only see runes, so the ~10^10-decode negatives are **not** conditional on spaces. (X1: the
   "bit-identical" plant check could not fail; the conclusion holds from the loader code, not that check.)
4. **Ten word-indexed rows lose all power if the spaces are decoy** (I1 reopen list, power 1.0 → 0):
   C-01, R37-C1-U2 (U2b half), R37-C1-U3, R38-C1-SEMANTIC-WORDNET, R38-C1-SEMANTIC-FREQRANK,
   R39-C1-SENSE-SIMILARITY, R38-C2-G3-LAGGED-POINTERS, R41-C1-R14-WORDSUM-SELFKEY, R44-W2A2-7GRAM-DIFFPLAIN,
   R40-C1-INCONCLUSIVE-R31. **Plus an older defect (X1):** R41's loader split words at line breaks
   (3,316 vs 2,896 words), so R41 W1–W4 recovered only 25–91% of planted pages **even with true spaces**.
5. **The transcription holds** (S1, S1b): 0 canon errors in 398 blind-read glyphs (random-frame bound
   0–2.5%; look-alike classes rest on a single reader — X1 caveat), all 86 doublet sites confirmed, and **no
   hidden doublet or count error in all 1,138 adjacent pairs T7 is fragile to** (S1b; controls 29/30 and
   28/30; template check 257/257; miss bound ≤ 2.8% per look-alike pair). The "~149 RAT disagreements"
   premise was wrong: RAT agrees with canon at 12,807/12,807 aligned glyphs; 149 are unaligned, uncovered.
6. **T7 is HARDENED but unexplained** (T1, S1b, X1): r = +0.380, p ≈ 0.001 (X1 independent null 0.00055),
   on a transcription now verified where it matters. It is **not a rate change**: a gate-passed smooth-drift
   test (power 0.865) fits zero drift (p = 1.0); block dispersion and change-point search null; no fitted
   mechanism (sessions, drift, section-position, renewal loop) reproduces it (all Stage-B 95th pct < 0.28).
   86 events cannot separate mechanisms. T1's "top 5 pairs carry 0.29 of 0.38" is **what chance produces**
   at that r (X1: median 76%), so it does not localise T7; with them removed the residual is borderline
   (p ≈ 0.04–0.05). T7 is a gap-ordering property, neither "one void" nor demonstrated "distributed".

## 2. Defects found (to fix in Round 46)

- `analysis/stones/alignment.json` drops lines < 10 glyphs and mis-assigns pages for lines 399/432, so ~4
  lines (~89 glyphs, ~0.8% of `dataset.npz` labels) are cropped from the wrong line (S1; line 402
  verified). Affects the Campaign-V classifier and possibly the 450 O/A/AE disagreements. S1's
  `corrected_map.json` is the working replacement.
- R41's printed-word loader (above). R37/R38/R39 loaders split the 32 page-wrapping words.
- `HUMAN-ORACLE.md` §3 rejects "word-salad"; under a shuffled-word plaintext a correct decode reads as
  word-salad (I1). Amended this round.
- Fable52 scripts hard-code paths to an external clone (X1 list in `X1-redteam/AUDIT.md`).
- W1/S1 PREREG addenda were appended without hash stamps (T1's were stamped — make that the rule).

## 3. Leads (post-hoc — need pre-registration before they count)

- **2-rune words are scarce in LP2** (15.5% vs ≥ 19.7% in all 480 English samples, 24.1% solved). "THE"
  is 2 runes. Fewer articles (another language/register) or lengths not from the plaintext.
- **Line breaks fall inside words 71% of the time** (chance ≈ 78%) vs LP1's 53% (chance ≈ 75%) (X1).

## 4. Round 46

CONTINUE, narrow. (1) One correct printed-word loader; re-run R41 W1–W4 and recheck R37 U2b/U3 with
planted shuffled-within-sentence controls on LP2's real layout. (2) Pre-register the 2-rune-word test and
the line-break test. (3) Repair `stones/alignment.json` from S1's map. (4) A second independent reader for
the look-alike classes (closes S1's single-reader caveat). (5) T7: no generation-model sweep is warranted;
separating mechanisms needs an independent stream of filtered events, none known.
