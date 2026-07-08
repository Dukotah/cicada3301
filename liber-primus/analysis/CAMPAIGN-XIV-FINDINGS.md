# Campaign XIV — Fable 5 red-team + decisive soundness probes

_2026-07-08. A different kind of pass: instead of trying more keys, we put fresh eyes
(a 4-lens **Claude Fable 5** red-team) on the whole approach to find what we might be
wrong about, then executed the cheap, decisive probes it surfaced. Artifacts:
`analysis/campaign14/` (`probes.py`, `probes.log`, `REDTEAM-PROPOSALS.md`,
`redteam_raw.json`, `redteam_workflow.js`). Reproduce probes:
`PYTHONUTF8=1 python analysis/campaign14/probes.py`._

## Why this pass matters
The prior campaigns proved a lot *couldn't* break the pages. This one asked the harder
question — **is the "one-time-pad / unsolvable" verdict itself sound, or overstated?**
The Fable 5 panel (4 independent lenses, each required to read the full elimination
ledger and propose only untried, falsifiable, constraint-fitting attacks) produced 22
proposals **and flagged several things the project had over-claimed as closed.** We then
ran the decisive ones. The result: the verdict came out **stronger**, not weaker — but
now for measured reasons, with two genuine soundness gaps closed and one new positive.

## The over-claims Fable caught (and how we resolved them)
| Over-claim the ledger made | Fable's objection | Probe result |
|---|---|---|
| "Every periodic key len 1–40" eliminated | Only tested **per-page, no-skip**; lags 31+ and **corpus-wide** periods were **never scanned** — yet the keystream is continuous across the whole book | **Closed corpus-wide.** P1: 0 coincidence peaks at any lag 1–6478 (>5σ). P2: no periodic-key spike, periods 41–2000 (max IoC·N 1.087 vs English 1.73). |
| "Autokey excluded" (Campaign X) | Only **additive** combiners simulated; generalized-combiner / Latin-square feedback fit every published statistic | **Closed.** P4: off-diagonal bigram χ² vs a *filtered-uniform* null is **+0.81σ = flat** — no second-order structure to exploit. |
| "Substitution/homophonic dead" | Only **bijective** 29→29 ruled out; **many-to-few homophonic** flattens IoC by design and was never tested | **Closed** by the same P4 bigram-flatness measurement. |
| "English-plaintext scoring is a valid null detector" | All 112+ keytext nulls are **conditional** on the plaintext being English prose | **Positively supported** — see P5. |

## Probe results (all reproducible in `probes.py`)
- **P1 — corpus-wide coincidence scan, lags 1..6478:** 0 lags above 5σ. No key reuse or
  periodicity at *any* offset across the whole book. The OTP verdict now holds
  corpus-wide, not just per-page.
- **P2 — long-period column IoC, periods 41..2000:** flat (max 1.087). No periodic key
  of any length up to 2000. Closes the period-31–2000 gap entirely.
- **P3 — page-boundary continuity:** 0 doublets across 54 page boundaries (expected ~1.9
  if unsuppressed) → **the doublet filter runs across page breaks: the book body was
  generated as one continuous stream in book order.** (New structural fact.)
- **P4 — bigram structure beyond monograms:** χ² against the independence model, compared
  to a 200-sample filtered-uniform Monte-Carlo null, is **+0.81σ (flat)**. No exploitable
  second-order structure. (An earlier flat-*uniform* expectation gave a false +12σ; the
  correct independence + MC test removes it — matching Fable's own measurement.)
- **P5 — word-length channel (an OTP hides symbol values, not word boundaries):** the
  `-`/`.`-delimited word-length distribution of the unsolved pages is **closer to the
  solved Cicada pages than to random segmentation** (total-variation distance 0.157 vs
  0.224); the tell is 1-rune words — unsolved 10% / solved 12% / random 26% (natural
  language suppresses one-letter words; random segmentation doesn't). **Directional
  positive evidence the plaintext is genuine English prose with meaningful boundaries**,
  which discharges the "is the English scorer even valid?" worry. (Reference is small —
  51 solved words — so this is directional, not definitive.)
- **P6 — pp49–51 payload as a page-order permutation:** no window's bytes mod 56 form a
  permutation of 0..55. The payload is not an encoded page order / offset table.

## Corpus question — resolved (not just probed)
Campaign XIII flagged that the community corpus had grown to "~75 pages." The ingest
agent pulled the full rtkd/iddqd master (**72 rune-bearing pages, 74 slots**) and
diffed it against our 0–55 set. The 15 pages we "lacked" are the **already-solved**
intro/koan pages (p0 A WARNING, p1 WELCOME, p2 SOME WISDOM, …): aggregate **IoC·N 1.155,
doublet 2.61%** (per-page IoC up to 2.06 — classic monoalphabetic), the *opposite* of
the flat-IoC (1.000) doublet-suppressed (0.66%) signature of the unsolved pages. **There
is no new *unsolved* material to ingest — our 0–55 body is the complete unsolved corpus.**
The "gap" was a page-numbering/scope artifact.

## Net
- **The OTP verdict is hardened, not weakened.** The two real soundness gaps (corpus-wide
  periodicity; generalized-combiner/homophonic) are now closed with measurements, and the
  English-plaintext assumption underpinning every sweep now has positive support.
- **One new structural fact:** the cipher body is a single continuous filtered stream in
  book order (doublet suppression crosses page boundaries).
- **Coverage gap closed:** no additional unsolved pages exist.
- **Fable 5 earned its keep** — it found four legitimate over-claims that a same-model
  review might have rubber-stamped; each is now genuinely, measurably closed.

## Standing agenda for future researchers (Fable's un-executed proposals)
Full list with tests + falsifiable signals in `REDTEAM-PROPOSALS.md`. The two highest-EV
*untried* avenues that remain:
1. **Word-length skeleton match** — slide each page's rune-word-length sequence over the
   112+ already-fetched corpora treated as **plaintext** (not key). A match beyond the
   shuffled-control FPR yields plaintext directly, no key needed. P5 shows the skeleton is
   English-shaped, so this is the fresh avenue with the most plausible direct path.
2. **Skip-tolerant / filter-aware re-decode** — every keytext/keystream elimination
   assumed *rigid* key alignment; a doublet filter that perturbs key consumption (j+2
   skips) would make those nulls unsound. A filter-aware beam decoder over the existing
   corpus + a Old-English/Latin re-scoring pass would discharge the last conditional-null
   worries. (Lower prior, but it's a soundness patch on ~112 prior results.)
Also documented but heavier: pp49–51 as a PRF/stream-cipher seed (RC4/AES-CTR/hash-chain
expansion), and a targeted **haplography image count-audit** of the 86 doublet sites (the
one cheap way to test whether the deficit is partly a transcription-merge artifact).
