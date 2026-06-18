# Open Avenues — can we move the needle?

_2026-06-17. Honest assessment after exhausting the key-guessing attack space._

Solving the unsolved pages from the ciphertext alone is information-theoretically
impossible (see SOLVE-ATTEMPT-FINAL.md). But there are real avenues that can
*move the needle* — verify inputs, contribute findings, or run the one untried
attack. Ranked by genuine value.

## 1. Independent vision re-transcription (NOVEL — top priority)
**Finding that motivates it:** the two most-used machine-readable transcriptions
(krisyotam, relikd) are **byte-for-byte identical** (12,956 runes, 0 differences)
— but they share a common origin, so this proves *consensus, not correctness*. A
systematic mis-read would be present in both and would silently defeat the
correct decryption method. No one has independently re-read the runes from the
original page images.

**Why it's newly feasible:** AI vision can read the Gematria Primus glyphs.
Calibrated on the solved "Some Wisdom" page image — the red header transcribes to
ᛋᚩᛗᛖ·ᚹᛁᛋᛞᚩᛗ = "SOME WISDOM", matching the known plaintext. The original solvers
(2014) had no such tool.

**Plan:** crop each unsolved page image into line strips at full resolution
(2400×3600), vision-transcribe each, assemble, and diff against the canonical
text. Flag only high-confidence disagreements (the vision pass has its own error
rate). Outcome is valuable either way: clean = first independent verification;
discrepancies = candidate transcription errors that may unblock attacks.

## 2. Doublet-avoidant constrained Viterbi decode (last untried attack)
The one cipher model that *predicts* the doublet deficit. A DP/Viterbi decoder
that maximizes rune n-gram likelihood subject to a "no consecutive repeat" rule,
co-searching a short key. Low prior (the differences are flat-random, suggesting
no recoverable structure), but it is the only classical attack not yet built.

## 3. Contribute our novel findings to the community
The integral-test result (the doublet deficit is a first-difference artifact over
an already-random stream) and the precise statistical profile may be a fresh
framing. The public repo + a write-up to active solvers (r/codes, CicadaSolvers)
saves others from re-running the dead ends we eliminated. This moves the
*collective* needle even if our own pages stay unsolved.

## 4. OSINT for the lost "AN END" deep-web page (cold trail)
The only place a key might physically exist. The target page was never found and
Tor v2 (which likely hosted it) was deprecated Oct 2021. A web-archive / cached
hunt is low-odds but non-zero.

## What will NOT move the needle (proven)
More key texts, more keywords, more keystreams, autokey, differencing,
page-keying, transposition-only — all eliminated. Do not re-run them.
