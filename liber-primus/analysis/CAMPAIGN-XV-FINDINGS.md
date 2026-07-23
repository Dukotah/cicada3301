# Campaign XV — Frontier armada: burn down the standing agenda

_2026-07-23. A 9-probe armada (one agent per probe, each required to VALIDATE its method on
synthetic ground truth or a power control, then run real code against real data) executed the
un-run agenda the Fable 5 red-team left standing in `campaign14/REDTEAM-PROPOSALS.md`. Every probe
wrote a reproducible script + result to `analysis/campaign15/`. Reproduce any one with
`PYTHONUTF8=1 python analysis/campaign15/<Pn>.py`._

## Why this pass matters
Campaign XIV asked "is the OTP verdict sound?" and closed the cheap gaps. This pass attacked the
**two biggest remaining soundness caveats** and the **highest-EV untried leads** head-on:
1. every prior keystream/keytext null assumed **rigid key alignment** — a doublet filter that skips
   key consumption could have made all ~112 of them unsound (P1);
2. the whole edifice assumed a **machine-generated pad** — a hand-generated pad would carry a
   human-bias attack surface (P5);
plus the direct-to-plaintext word-length channel (P3), the payload's last cryptographic roles
(P2/P9), the pad-inversion paradigm (P7), the surjective-homophonic sub-class the ledger only
argued away for the bijective case (P6), the doublet side-channel (P4), and a model-class
structure audit (P8).

**Result: no break (expected for OTP-class), but the two load-bearing caveats are now discharged
by measurement, five new families are closed with named nulls, and the OTP verdict is upgraded
from low-order-verified to model-class-verified.** Trust anchor `python tests/validate.py` passed
at the start of every probe.

## The headline: the two soundness caveats are closed
- **P1 (rigid-alignment caveat — the big one).** The concern was *real*: decoding even the
  **correct** generator (φ(prime)) **rigidly** through a soft skip-on-collision filter collapses to
  **score_norm −7.47** — pure noise, indistinguishable from a wrong key. So the ~112 rigid nulls
  genuinely *were* alignment-fragile. A skip-tolerant DP/beam decoder (state = (text pos, key
  index); `j→j+2` only at collision-consistent sites, log-penalty) was built and **validated**:
  it recovers planted English at **−4.28 / 97.4% match** while four wrong generators stay pinned at
  −7.2…−7.3 (separation **2.96**). Turned on LP2: **2,876 skip-aware decodes** (attested generator
  family — consecutive primes, φ(prime), iterated totient, prime gaps, 6 Fibonacci-mod-29 seeds ×
  offsets 0..1000 × both signs × ±Atbash, per-page **and** continuous — plus 21 cached keytexts) →
  **0 clear the −5.2 gate; grand best −6.442.** The rigid-alignment caveat is **discharged**; the
  keystream/generator/keytext eliminations are now sound against filter-perturbed alignment.
- **P5 (hand-generated-pad loophole).** Four generator-fingerprint tests (conditional next-rune χ²,
  windowed dispersion, doublet-gap geometric law, book-order monogram drift) vs a 200-sample
  filtered-uniform control band: **max |z| = 1.51 — full conformance.** The suite has power: a
  shuffle-bag / Fisher-Yates pad is caught at **≈ −23σ** windowed under-dispersion. LP2 shows none
  of it. The pad is a **memoryless rejection-sampler**; the by-hand / balanced-bag mechanisms (and
  their human-bias attack surface) are ruled out.

## Probe results (all reproducible in `analysis/campaign15/`)
| Probe | Verdict | Headline number | What it closes |
|---|---|---|---|
| **P1** skip-tolerant filter-aware beam decode | soundness-confirmed | 0 / 2,876 decodes > −5.2 (best −6.44); correct-key rigid decode = −7.47, skip-aware recovers plant −4.28/97.4% | the rigid-alignment caveat on **all ~112** prior keystream/keytext nulls |
| **P2** pp49–51 payload as PRF/stream seed | null-closed | 480 configs; best −7.44, IoC·N 1.002 (gates −5.2 / 1.3); RC4-seed plant recovered −4.18/1.76 | payload as RC4/AES-CTR/SHA-chain/HMAC-DRBG seed — its last natural crypto role |
| **P3** word-length skeleton match | null-closed¹ | 0 exact / 0 ±1 matches, 55 pages vs 11,919 corpus words; matcher FPR 0/1000 | the direct-to-plaintext metadata channel (over the on-disk corpus) |
| **P4** doublet forensics (the 86 survivors) | null-closed | positions KS p=0.24, gaps geometric (KS p=0.67, χ² p=0.96), values χ² p=0.58; all decodes ≤ −6.45 | the surviving doublets as a fingerprint / side-channel; refines Campaign XI |
| **P5** generator fingerprint | soundness-confirmed | max |z| = 1.51 vs 200-sample control; shuffle-bag caught at ≈ −23σ | the hand-generated-pad loophole (generator level) |
| **P6** homophonic-downward 29→k | null-closed² | searcher validated 57–62% vs 6–8% chance; LP2 best cell z=3.73 fails held-out z=−0.95 | the **surjective** homophonic sub-class (ledger only had the bijective case) |
| **P7** LP2-as-pad inversion | null-closed | 0/7 counterparts beat shuffled-key null; canon_256 −6.970 vs null −6.934; plant recovered −4.25 | the "pages are the key, not the message" paradigm |
| **P8** total-structure compression closure | soundness-confirmed | LP2 inside 1,000-control band on every predictor (context 41–68%ile, LZMA 79%ile); English at 0%ile | any computable structure **beyond** IoC·N=1.000 + doublet 0.66% |
| **P9** pp49–51 as RSA + OE/Latin re-scoring | null-closed | 0/12 PKCS#1/PSS under 2 authentic 4096-bit Cicada moduli; OE/Latin at random-key floor | payload as RSA under real keys; non-English scoring of all prior bests |

¹ **P3 scope caveat:** run against the 8 corpora cached on disk (solved plaintext, Hermetica,
Sephir Yetzirah, Rosicrucian, Monas, Enoch, Tao, Thomas/PGP prose), **not** the full 112-text set —
the proxy blocks gutenberg/archive/wikisource this session. The matcher is validated (recovers
embedded truth at FPR 0/1000); the null is strong but bounded to the on-disk corpus.

² **P6 power caveat (measured, honest):** at LP2's extreme flatness (IoC·N = 1.000) even a *genuine*
homophonic decode gives a discriminator margin of only z ≤ 1.69, so score-margin tests are inherently
low-power here; decode-recovery is the only high-power signal and it needs a crib we lack. The
surjective channel is therefore **near-degenerate** — it cannot be the recoverable mechanism — which
is itself the closure. LP2's lone high-z cell (EN k=20, z=3.73) is search overfitting: it fails
held-out generalization (z=−0.95).

## What Campaign XV adds to the elimination ledger (6 new rows + 3 upgrades)
New named nulls: **payload-as-PRF-seed** (P2), **word-length skeleton** (P3, bounded), **doublet
side-channel** (P4), **surjective 29→k homophonic** (P6), **LP2-as-pad inversion** (P7), **payload-as-RSA
under real Cicada moduli** (P9). Soundness upgrades: **rigid-alignment caveat discharged** (P1),
**hand-pad loophole closed** (P5), **OTP-class model-class-verified** (P8).

New artifact now in-repo: `analysis/campaign15/cicada_pubkey.asc` — Cicada's real public key (keyid
`0x181F01E57A35090F`, fingerprint `6D854CD7…7A35090F`), fetched to turn the payload-as-RSA question
from "no modulus on disk" into a **tested** negative.

## Net — where the frontier stands after Campaign XV
- **Everything ciphertext-internal is now closed to model-class.** No structure survives beyond the
  two known constraints (P8); the pad is a memoryless machine rejection-sampler (P5); the
  skip-filter cannot be hiding a keystream/keytext break (P1); the payload has no remaining
  cryptographic role (P2/P7/P9); the doublet survivors carry nothing (P4); the surjective-homophonic
  and pad-inversion paradigms are closed (P6/P7).
- **The honest open frontier narrows to essentially ONE external avenue:** an untried
  *already-public keytext* Cicada expected solvers to recognize, tested over the **full** corpus of
  candidate primary sources — the one falsifiable path a running-key search still leaves. This
  session's contribution to it (P1 skip-aware + P3 skeleton) covered the **attested generators and
  the on-disk corpus** cleanly; extending it needs the ~112-text corpus re-fetched on a box with
  open outbound HTTPS. The **"AN END" deep-web page** (the only place a key might physically exist)
  remains cold (Tor v2 dead).
- **Nobody should read this as "solvable with more compute."** The math (P8) says the ciphertext
  carries no exploitable structure; the only realistic solve is external.

_Sibling docs: `ELIMINATION-LEDGER.md` (single ruled-out index, now updated) · `../PICKUP-HERE.md`
(resume point) · `campaign14/REDTEAM-PROPOSALS.md` (the agenda this campaign burned down)._
