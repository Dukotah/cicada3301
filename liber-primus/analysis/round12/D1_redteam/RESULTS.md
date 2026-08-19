# FRONT D1 — Red-team: is the OTP verdict a circular artifact?

_Run 2026-08-17. Trust anchor `tests/validate.py` = PASS (reproduces all known solves).
Mandate: assume the OTP verdict is WRONG; hunt a circularity in a load-bearing exclusion
that, once removed, reopens a lane._

## Bottom line: NO-ERROR-FOUND. The most dangerous candidate circularity (B-16) was
## re-derived, tested with a positive control, and **closed** — not confirmed.

The verdict rests on three load-bearing pillars. I re-derived each from scratch and
attacked the specific place each could be secretly assuming its conclusion:

| Pillar | Circularity hypothesis | Audit result |
|---|---|---|
| **Doublet deficit** (0.66% vs 3.45%) excludes rigid natural keys | Is the "1.5% English floor" secretly computed on canon (circular)? | **NO.** Floor is measured on generic English texts (self_reliance PT × unrelated-text keys → 3.28–4.18% doublets rigid; KJV 1.50% is the extreme low). Never touches canon. Observed 0.66% < every measured floor. Text-independent, sound. |
| **Skip-aware beam decoder** null over ~200 keytexts | Does the decoder cover the mechanism Campaign X/XI actually PINNED? | **This is B-16 — the one real gap. Tested and closed below.** |
| **FP ceiling / confirm threshold** | Is the −5.5 confirm bar an artifact of an under-powered FP estimate? | Already flagged honestly in PA-2 (margin ~0.25, not 1.3). Re-measured: wrong-key FP ceiling at N=975 = −6.77. Sweep best reals (−5.75…−5.88) are best-of-millions order statistics, still below the −5.5 confirm bar → correctly classified null. Thin but not circular. |

## The one real candidate: B-16 (RECON-B, Round 10) — and why it does NOT reopen

**The flagged inconsistency (real).** Campaign X/XI PIN the mechanism as a *soft anti-repeat
REWRITE of the output* (`campaign10.soft_norepeat_pad` / `campaign11.soft_pad`: when a doublet
would occur, RESAMPLE the ciphertext rune at the same position; the key stays SYNCED).
Campaign XVIII BUILT + VALIDATED its beam decoder against a *different* mechanism —
KEY-SKIP (`encipher_keyskip`: when a doublet would occur, ADVANCE the key index; the key
DESYNCS). B-16 correctly observed: the decoder's validation gate covers key **skip** (desync),
not value **rewrite** (in-place corruption), and `armada2/COVERAGE-MATRIX.md` has no rewrite
row. If the correct key under the *rewrite* mechanism failed to decode, every ~200-text
keytext null would be unsound and the keytext lane would reopen.

**The decisive test B-16 proposed, now RUN** (`rewrite_gate.py`, positive-control-gated):

- **ARM 1 (positive control) — SKIP model, correct key, existing beam decoder:** recovers
  English at **−4.27…−4.32, 95–100% rune-match** across 4 keytexts × 2 offsets. Machinery works.
- **ARM 2 (the test) — REWRITE model, correct key, SAME beam decoder:** recovers the correct
  running key to **−4.45…−4.70 beam (95–98% match)** at page length (233 runes, 5–11 rewrites),
  and **−4.80…−5.16** even on longer real English (250 runes) at up to 7% corruption.

**Why it closes rather than confirms B-16:** the rewrite mechanism corrupts only ~2.8% of
positions on the real cipher (deficit arithmetic: (3.45−0.66)/3.45 × 3.45% ≈ 2.79%), and a
~97%-correct running-key decode still scores in the English band because the quadgram scorer
tolerates a few substitution errors. Crucially it does NOT desync the key, so plain **rigid**
decode recovers it just as well as the beam (both −4.45…−4.70). A correct keytext under the
pinned rewrite mechanism would have scored **~−4.5**, versus the **−5.75…−5.88** noise the
actual ~200-text sweeps produced. The nulls therefore DO cover the rewrite mechanism: no real
keytext was hiding at ~−4.5 and getting mis-scored as noise.

**Consequence for the docs (wording, not verdict):** B-16's own recommendation stands — the
keytext closure is sound but should be cited as *"by exhaustion over ~200 texts, verified
robust to both the skip and rewrite constructions"* rather than *"by mechanism, independent of
text."* This is a precision fix, not a reopener. `COVERAGE-MATRIX.md` should gain a REWRITE row
pointing at `rewrite_gate.py`.

## Positive control

`control_passed = true`: this is analysis, and every arm ran its own positive control
(ARM 1 skip recovery −4.3/100%; doublet-floor measured on live texts; FP ceiling from live
beam trials). The rewrite-arm result is only interpretable *because* the skip control passed.

## Verdict

**NO-ERROR-FOUND.** No load-bearing exclusion secretly assumes its conclusion. The single
genuine gap (B-16: rewrite-mechanism coverage) was the correct thing to test and it came back
verifying the closure, not breaking it. The boundary is hardened: the OTP-class verdict is not
a circular artifact of a skip-only decoder. What remains is external-input (Front A), exactly
as the campaign plan states.
