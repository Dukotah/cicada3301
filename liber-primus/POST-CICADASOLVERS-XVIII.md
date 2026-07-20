# Community note — CicadaSolvers / r/codes (Campaign XVIII addendum)

_Post under your own name. Same house tone: humble, skeptical, negative-results-first,
NOT a solve. This one is a **methodological warning + a tool**, which is the part I think
is genuinely useful to anyone still brute-forcing running keys against LP2._

---

**Title:** If you're brute-forcing running keys against LP2, your nulls may be unsound —
here's why, and a fixed decoder

**Short version.** The unsolved Liber Primus pages are OTP-class with one real anomaly:
adjacent equal runes are suppressed ~5× below chance (doublet rate ≈0.66% vs 3.45%). A
prior result in this repo pinned that to an **active, ~83%-strong doublet-suppression
filter** applied at encipherment (an unfiltered pad and every autokey variant sit at the
~3.45% random rate — so the filter is real and deliberate). This note is about a
consequence nobody had followed through on:

**If that filter works by *skipping a key symbol* whenever the next output rune would
double the previous one, then the running key DESYNCHRONISES from the plaintext after the
first skip (~1 per 35 runes). A rigid 1:1 running-key test — the standard approach, and the
one behind essentially every published LP2 keytext null — would then score *even the
correct keytext as noise*, because it reads English for ~30 runes and then shifts by one
key position into garbage.**

I built the obvious fix — a **skip-tolerant beam decoder** that tracks the key/plaintext
desync — and validated it honestly before trusting anything:

- **Mechanism gate:** encipher a known English plaintext under the skip model. Decoded
  *rigidly* with the correct key it scores −7.24 / 8.5% match (pure noise). The
  skip-tolerant decode recovers it at **−4.15 / 100%**. A wrong key stays at −7.56.
- **Robustness:** recovers 99.6–100% through up to 14 skips at realistic page length.
- **False-positive ceiling:** 400 wrong (key,offset) trials top out at −6.82, vs genuine
  English ≈ −4.3 — a wide margin, so a real hit would be unmistakable.
- **Pipeline recall:** planted keys recovered 7/8 per page end-to-end.

**What I then re-tested under the corrected decoder (all null so far):**
- The **9 directly-referenced texts** (Mabinogion, Self-Reliance, King in Yellow, Agrippa,
  Book of the Law, rune poems, solved-page plaintext) across all 55 pages → clean null
  (best of 55 pages −5.88, median −6.21). These nulls are now **unconditional**, not
  conditional on the rigid-alignment assumption.
- The **pp49-51 256-byte payload** as a skip-aware key over each page → null (−6.76).
- **Word-length skeleton** match (an OTP can't hide word boundaries; we have them) against
  11 high-prior texts, high-power longest-run statistic vs shuffled control → strong null.
- The full 122-text corpus re-decode is running as I write this.

**Why I'm posting this even though it's null.** Two reasons I think are useful to the group:

1. **A warning.** If you are running running-key / keytext searches against LP2 with rigid
   alignment, a null tells you *almost nothing* — the correct key would look like noise.
   You need skip-tolerant alignment (or a proof that the filter is in-place "bump", which
   *doesn't* desync — but that variant is already excluded by existing rigid nulls, so
   key-skip is the only filter mechanism that defeats a rigid test).
2. **A tool.** The decoder is open and runs any candidate text through correctly-aligned
   decoding in seconds. If you have a keytext you always suspected but which "just barely
   didn't score," it's worth re-running here.

**What this does NOT claim.** Not a solve. It doesn't touch the possibility of an *external*
key that was never a public text (the lost "AN END" deep-web page remains the real
frontier), and a fundamentally non-additive feedback cipher is still formally unbounded.
It narrows the honest space and fixes a soundness hole; that's all.

**Code / reproduce:** repo `Dukotah/cicada3301` →
`liber-primus/analysis/campaign18_skip/` (decoder + all four validation gates + the sweep),
writeup in `CAMPAIGN-XVIII-FINDINGS.md`, and the master index in `ELIMINATION-LEDGER.md`.
Please poke holes in it — especially the skip model itself.
