# PICKUP-HERE — where the work left off

_Updated **2026-08-26**. Repo: https://github.com/Dukotah/cicada3301 (default branch `master`)._

> ### ⚠️ READ THIS BEFORE ANYTHING ELSE (2026-08-26)
>
> **Round 18 found that this project has been searching with a broken magnet, and every
> coverage claim below is narrower than it reads.**
>
> 1. **Every negative in this repository is an ENGLISH-ONLY negative.**
>    (`analysis/round18/L7-redteam/RESULTS.md` §A.) Handed the *correct key*, the beam recovers
>    **100 % of runes** for Latin, Old English, German, Welsh and abbreviated English — and the
>    English quadgram adjudicator then scores the result as noise. Measured power at the −5.5
>    bar: **0.33** Latin, **0.58** OE, **0.00** Welsh, **0.00** vowel-dropped English (where the
>    correct key scores *below* a deliberately wrong one). Round 10b required a language-agnostic
>    statistic be stored at sweep time; compliance was **0 of 15**, so 6,224,300 + 692,064 +
>    52,556 decodes and ≈1.45 × 10¹⁰ offsets **cannot be retro-fitted**.
> 2. **Every negative covers exactly ONE rejection-loop construction.** (§B.) The beam admits a
>    key skip only if every skipped position would have reproduced the previous cipher rune —
>    exact for `encipher_keyskip` and nothing else. **`skip_by_two`**, a one-character variant
>    that **reproduces LP2's observed doublet rate** (0.84 % vs 0.664 %), is missed at **−6.90 /
>    25.8 % recovery**, and beam width 1000 + `max_skip` 8 change that by *exactly* 0.000. It
>    appears in no `not_covered` field anywhere.
>
> So **every "NEGATIVE" below carries three conditionals, not one**: the key space swept, the
> decoder's transition model, and the adjudicator's register. If the true key were inside the
> swept set, the sweep would probably have discarded it.
>
> **If you are about to run a round, read [`liber-primus/ARMADA-DOCTRINE.md`](liber-primus/ARMADA-DOCTRINE.md) first.** It is binding.

## 👉 Start with the canonical docs
| Doc | What it holds |
|---|---|
| [`liber-primus/FINAL-SYNTHESIS.md`](liber-primus/FINAL-SYNTHESIS.md) | The terminal verdict on both goals — solve and attribution |
| [`liber-primus/ELIMINATION-LEDGER.md`](liber-primus/ELIMINATION-LEDGER.md) | Everything tried and why it's eliminated — supersedes every scattered "ruled-out" table |
| [`liber-primus/analysis/README.md`](liber-primus/analysis/README.md) | Map of all 183 analysis scripts → campaign → finding |
| [`research/LEDGER.md`](research/LEDGER.md) + [`research/DEAD_ENDS.md`](research/DEAD_ENDS.md) | The 2026-08 pre-registered attack loop — Rounds 1–8, each with its kill reason |
| [`liber-primus/LEDGER.json`](liber-primus/LEDGER.json) | **The machine-readable index** — every hypothesis, its threshold, whether its positive control passed, and what would reopen it. Query this instead of reading the prose docs. |
| [`liber-primus/handoff/FOR-FUTURE-SOLVERS.md`](liber-primus/handoff/FOR-FUTURE-SOLVERS.md) | The entry point for someone arriving cold, incl. what is parked pending better tooling |
| [`liber-primus/benchmark/`](liber-primus/benchmark/) | The plant-and-recover gates — **run these before trusting any null you produce** |

## State in one paragraph

LP2 (unsolved segments 0–54) is **OTP-class**: a full-length keystream filtered to avoid
consecutive-equal runes (soft, ~83% suppression). "OTP-class" is precise and it is *weaker*
than "one-time pad" — the ciphertext is **indistinguishable between a true external pad
(information-theoretically closed) and a short-seed *derived* keystream (finite keyspace,
brute-forceable)**. The derived-key dictionary lane is untested; only running it settles which.
The transcription is verified four independent ways and is **not** the blocker. On attribution,
there is **no falsifiable
name** — stylometry is *provably* impossible at 359 words of authentic connected prose — but the
loop produced the tightest honest **profile** yet, anchored on a technique fingerprint
(Smirnov/Carlitz anti-repeat hardening = a combinatorialist's reflex, applied by hand).

> **⚠️ Superseded 2026-08-17 (Round 12, front D3 — FOUND-ERROR).** This paragraph used to state
> the verdict as "*information-theoretically unsolvable **without the pad***" and "*the internal
> attack surface is **closed**… hardened from unsolved-by-effort to **unsolvable-by-design***".
> Both overstate the evidence. `analysis/round10b/B4-otp-steelman/b4_results.json` (G5) shows the
> ciphertext cannot separate an external pad from a SHA-256 counter-mode keystream derived from a
> short seed (`"separated": false`, max |z| = 1.60), and D3's positive control planted exactly
> such a keystream and **recovered it** through this project's own beam decoder (−4.170, 98.9%
> char-recovery, vs −7.349 on a wrong seed). "No compute recovers it" is therefore false over
> that lane. "Closed" is also the wrong word for a surface with **16 items still marked
> `never-run`** in `liber-primus/analysis/round10/RECON-A/REGISTER.md`. The reasoning is kept;
> the claim is narrowed. See `liber-primus/analysis/round12/D3/RESULTS.md`.

**Since then (2026-08), an eight-round pre-registered attack loop closed the last lanes** —
including the two threads this doc previously listed as open. The OTP characterisation is now
backed by a direct measurement of key **entropy**, not just by the absence of key structure.

## The 2026-08 attack loop — Rounds 1–8

Each round was **pre-registered** (hypothesis + pass/fail threshold written before the run) so a
negative result means something. Full detail: [`research/LEDGER.md`](research/LEDGER.md),
kill reasons in [`research/DEAD_ENDS.md`](research/DEAD_ENDS.md).

| Round | Hypothesis tested | Verdict |
|---|---|---|
| 1 | The doublet deficit is an interrupter artifact | **NEGATIVE** — it is intrinsic |
| 2 | A period-locked fractionation signature exists | **NEGATIVE** |
| 3 | Differencing/DP decode can be anchored | **KILL at Gate #1** — un-anchorable; ciphertext-only program COMPLETE |
| 4 | An external key/seed or a verifiable author identity exists | **NEGATIVE** — cold |
| 5 | Residual doublets carry digraphic/autokey/interleave structure | **NEGATIVE** |
| 6 | Misfiled plaintext windows / transition-lattice structure | **NEGATIVE** — the no-repeat rule is a *pure lag-1 identity*, no second-order structure |
| 7 | Some untried public keytext is the key | **KILL, 0/15 unanimous** — any keytext dies both rigidly (doublet-excluded) and skip-aware (un-anchorable), *independent of which text* |
| 8 | Five never-tested axes (below) | **NEGATIVE ×5** |

**Round 8 in detail** ([`research/ROUND-8-RESULTS.md`](research/ROUND-8-RESULTS.md)) — these were
the axes that were never ciphertext-only attacks at all, so "ciphertext-only complete" had never
actually covered them:

- **SEED** — is the pad a seeded PRNG? 10 validated generators (glibc/MSVC/MT19937/CPython/Java,
  each reproduced exactly against the real library) × both directions × every unix-second seed
  2011–2015 = **2.52 × 10⁹ decodes, 0 hits**, best −13.13 (= the null max); plus 15,408
  lore/string/date-seed decodes, 0 hits. → `analysis/seed_sweep/`
- **GEOMETRY** — these are 400-DPI renders of a *typeset* document and only FILE-level stego had
  ever been swept. Glyph-shape substitution is dead (median nearest-neighbour Hamming distance
  **0.0000** — the median glyph has a pixel-identical twin); micro-spacing is 1.86σ unimodal;
  baseline jitter fails BIC. → `analysis/geometry/`
- **PAYLOAD** — "flat IoC" is blind to a compressed/binary plaintext. 166 representations scanned
  for magics/armor/inflate: nothing; byte histogram exactly uniform (χ² 246.7 / 255 df).
- **SKELETON** — word length is a cleartext invariant no pad touches, so a known text could be
  identified as the *plaintext* without a key. FFT scan of every offset across 51 texts / 8.2M
  words: best 20.0% vs a shuffled control's 19.8%. Negative **for that corpus**; the tool is built
  to extend. → `analysis/skeleton/`
- **POINTERS** — the 86 residual doublets read as a book-cipher index: every reading sits inside
  the random null.

**AN-END hunt CLOSED (2026-08)** ([`liber-primus/analysis/anend_hunt/FINDINGS.md`](liber-primus/analysis/anend_hunt/FINDINGS.md)) —
the lost deep-web page is **unreachable by construction**: its address is gated behind solving
OTP-class LP2 0–54 (the 2014 chain grammar is "each onion's solved content yields the next
address"), `gy3hoy2…onion` is a debunked hallucination, no genuinely-retrievable in-scope Tor-v2
corpus exists, the held corpus hashes null across representations (2,706 tests), and the 2026
community status is a sourced negative. **The only remaining door is solving LP2 0–54 —
cryptanalysis, not OSINT.**

## Round 9/10 — multi-lens armada (2026-08-11 → 17)

A fresh, wide 22-lens re-attack (distinct from the `research/round-1…8` sequence), run
across the plaintext/word, keystream/pad, and external/provenance fronts — each lens
pre-registered with a positive control and a size-matched null. The window crashed
mid-run; it was recovered, finished, and synthesized on 2026-08-17.
Full detail: [`liber-primus/analysis/round10/SYNTHESIS.md`](liber-primus/analysis/round10/SYNTHESIS.md).

**Zero hits across all lenses — the OTP / unsolvable-by-design verdict holds and is
hardened.** The value is three things, not another null:

1. **Two prior claims corrected** (marked as superseding in the synthesis):
   - *"Flat IoC forces a full-length key"* is **false** — the smallest IoC-invisible period at
     N=12,956 is **p\*≈400**, not 12,956. The OTP conclusion rests on the **doublet** argument,
     not IoC.
   - *"OTP"* is really **one member of a ciphertext-indistinguishability class**: a SHA-256
     counter-mode derived key + filter, and ciphertext-autokey over flat non-English plaintext,
     both pass the full statistics battery inside the external-pad model's band (no statistic
     separates them at |z|>2.93). State it as OTP-*class*, not a unique external pad.
2. **The transcription got a 4th, genuinely-independent audit** (label-free glyph clustering,
   not canon-trained): 96.93% agreement, clean 29→29 bijection, **no reopener** — every
   disagreement is a DP artifact or a misread on an already-*solved* page. Bounded: only 38.4%
   of lines were glyph-diffable, and the OTP pages are where the read is weakest.
3. **The doublet-deficit argument was stress-tested from both sides** (B4/G3 hardens it — the
   plaintext-independent floor is 1.50% > observed 0.664%; RECON-B/B-16 objects that the soft
   anti-repeat filter, not the key, sets the rate) and **reconciled**: the deficit excludes
   *rigid* plaintext-independent keys; the anti-repeat-aware decoders exclude the rest to the
   audited limit of their power.

**One genuinely-new untested input surfaced (PA-3):** the author's own ~4 MB binary pads from
the 2013 CicadaOS (`DATA/_560.*`, `761.mp3`⊕`twitter.txt`) — period-correct key material she
demonstrably used — have **never been fed under the skip-aware decoder**. Not held in-repo;
would need fetching. It is the highest-prior remaining input, though still low absolute prior.

## Round 11 — the NUMBER CHANNEL (2026-08-17)

Ran the roadmap's flagship idea (`analysis/NEXT-ARMADA-ROADMAP.md`): every exclusion in this
repo lived on the mod-29 **letter** stream, while the signed hints obsess over the **numbers**
("the primes are sacred", "either the words or their numbers", "their numbers are the
direction"). Arithmetic on the raw prime magnitudes lives in ℤ, outside the group where the
proofs hold — so we built a validated instrument (`analysis/round11/lib_numchannel.py`,
gated PASS) and attacked that space plus the interrupter and separator channels nobody had
transcribed. **7 pre-registered lenses, all NEGATIVE, all positive controls PASSED, 0 hits.**
Full: [`analysis/round11/SYNTHESIS.md`](liber-primus/analysis/round11/SYNTHESIS.md).

The number channel — the single most-cited "surely they meant the primes" intuition in the
whole mystery — is now a measured, control-validated negative (feedback autokey, number-theoretic
structure, digit planes, the totient ladder, interrupter positions, separators). Two findings
beyond the null: **N3** — the ciphertext is *anti*-special (0 primes / powers / notable shapes in
55 segments; less number-theoretic coincidence than random); **S2** — the separators are
typography (line-wrap / sentence / word markers), not a hidden channel, which closes RECON-A's
"ornaments never read" flag. Verdict tightened, not reopened.

## What the 2026-07 sessions did

- **2026-07-27 — OSINT / external-artifact sweep.** Pulled the onion images and HTML never held
  locally from community mirrors (iBotPeaches, archive.org, scream314, krisyotam) and re-extracted.
  **No new key**: T1 and T5 decode to already-known 2013/2016 messages; a 60-key OutGuess sweep was
  null; T2/T3 remain unidentified high-entropy blobs (low prior).
  → `liber-primus/analysis/OSINT-SWEEP-2026-07-27.md`, `analysis/armada_osint/`
- **2026-07-28 — LP1/LP2 recon + Campaign XIX.** Method dossier for the solved section (key
  selection is **semantic, not numeric**), structure dossier for the unsolved one (editorial
  sections exist; the cipher does **not** reset at them), and the full winner/insider roster —
  none of whom holds LP or key material.
  → `analysis/recon/RECON-SUMMARY-2026-07-28.md`, `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md`
- **2026-07-29 — the 11-iteration auditor loop.** A rotating-critic loop (contrarian → naïve
  outsider → author-empathy → historian → data-provenance → lateral-field → game-theorist →
  devil's-advocate believer) that sealed the remaining lanes, **positively refuted autokey**, and
  self-corrected three of its own false positives.
  → `liber-primus/FINAL-SYNTHESIS.md`, `analysis/recon/`, `analysis/attribution/TECHNIQUE-FINGERPRINT-2026-07-29.md`

## If you're picking this up cold

```bash
cd liber-primus
python tests/validate.py     # trust anchor — reproduces every known solved page
pytest -m "not network"      # fast regression gate
```

### How to start a fresh armada without repeating one

The two goals — **stay optimistic** and **don't overlap** — are not in tension, but only if you
keep two things apart that this repo has repeatedly conflated:

| | what it is | how to treat it |
|---|---|---|
| **A coverage bound** | *"swept 2,165 seeds × 16 generators × 5 reductions, best −6.185 against a −5.5 bar, control passed"* | **Trust it.** This is a measured fact and it saves you from redoing a sweep. Check `LEDGER.json` → `coverage` and `not_covered`. |
| **A terminal verdict** | *"exhausted"*, *"wind down"*, *"unsolvable by design"* | **Distrust it — including ours.** This repo has been wrong with that mood twice, and both times it foreclosed a lane that was later run and turned out to be tractable. |

**The practical test before you start:** for the lane you have in mind, open `LEDGER.json` and
read its `coverage` and `not_covered` fields, not its `status`. A `status: eliminated` with a
coverage bound of *"10 generators at ~3% of each seed space"* is an **open** lane wearing a
closed label — that is exactly how PHP `mt_rand` stayed untested for months.

**Three lanes were found this way, each inside something previously called closed:**

- **B-04** — declared dead by *"internal solve frontier EXHAUSTED"* (2026-07-29), was in fact
  marked `never-run` in the repo's own register, and ran for the first time in Round 13.
- **PHP `mt_rand`** — inside *"seeded-PRNG pads, do not re-run"*, whose real coverage was ~3%.
- **KDF / key stretching** — inside B-04's own `not_covered` declaration, and arguably a
  *higher* prior than the bare-hash family B-04 swept.

So: be optimistic about **finding the gap inside a closure**, and disciplined about **not
re-running the measured part**. Those are the same skill.

---

Then read the ledger. **Do not re-run** anything in its "Do NOT re-run" list — more keywords,
short/periodic keys, number-theoretic keystreams, autokey, differencing/integration, page-on-page
keying, transposition-only, fractionation, substitution/homophonic, image stego, AI-vision
re-transcription, or pp49–51 as a runic key. Every one is eliminated with a reason and a
reproduce pointer.

## Round 18 — "THE PAD CAME OUT OF A PROGRAM. FIND THE PROGRAM." (2026-08-25/26)

Eight lanes, built on Round 17's finding that the anti-repeat filter is **machine**-applied.
Full: [`analysis/round18/CAMPAIGN-PLAN.md`](liber-primus/analysis/round18/CAMPAIGN-PLAN.md).

| Lane | Tested | Verdict |
|---|---|---|
| **L1** TOOLCHAIN | G-01/B-11 provenance, never-run | **FINDING** — the pages are **ImageMagick over Ghostscript**, not Ghostscript alone (q92, optimised Huffman, auto-gray, ICC pass-through, control-reproduced). 400 dpi × 2400×3600 = exactly **6.00×9.00 in**, a typeset trade-paperback page; runes typeset from a proportional font, i.e. character data before pixels. **46/46** signed 3301 messages 2012→2014 are `GnuPG v1.4.11 (GNU/Linux)`. Composite: an **Ubuntu 11.04–12.04-class box, unchanged for three years** — and the project's first **evidence-derived prior** over generator families |
| **L2** FILTER AS A LEAK | Is the rejection sampler an information channel? | **BOUND** — the filter acts on the **ciphertext** (power 1.000); draw count 373.6 ± 19.6; `fastbeam` is bit-identical to the repo beam at **9× speed** (gate F0, max Δ 7.99e-15) and lands the **first full-book positive control at 12,956 runes** (−4.098, recovery 0.9997) |
| **L3** ORNAMENTS | A-06/B-12, never-run | **IN PROGRESS** → carried to Round 19 C3. Restored the **y coordinate `ornaments.json` drops** (which is why nobody could ever crop these bands): **109 band records / 39 pages**, 30 with n ≤ 16. Also found a **solved-page control render** the relikd mirror does not carry |
| **L4** FORCING | C-02, never-run | **NEGATIVE** — the line-initial distribution is non-uniform at p ≤ 5e-6, the first ciphertext-visible anomaly that is not the filter, and it is then **fully explained by a greedy line-breaker** (layout-aware null → p = 0.177). Leaves a measured **glyph-width table** and the layout-aware null every future positional attack must use |
| **L5** PAYLOAD | A-04 + E-01 | **UNFINISHED** → Round 19 C1 |
| **L6** OFFSET & MARSAGLIA | B-02 + the Marsaglia CDROM | **UNFINISHED** (data fetched, no results) → Round 19 C2 |
| **L7** INSTRUMENT RED-TEAM | The repo's own instrument | **FOUND-ERROR ×2** — see the box at the top of this file. The most consequential result since D3 |
| **L8** PROVENANCE | I-01/I-03 + G-02 | **UNFINISHED** (table built, no results) → Round 19 C3 |

## Round 19 — "FIX THE MAGNET, THEN SWEEP THE SMALL HAYSTACK" (2026-08-26, COMPLETE)

The first round run under [`ARMADA-DOCTRINE.md`](liber-primus/ARMADA-DOCTRINE.md). 14 lanes.
Plan: [`analysis/round19/CAMPAIGN-PLAN.md`](liber-primus/analysis/round19/CAMPAIGN-PLAN.md).
**The sweep it was named for did not run** — the red-team lane showed it could not, and the round
was redirected mid-flight. What it produced instead is a working instrument and a closed question.

### The three headlines

**1. THE INSTRUMENT IS REPAIRED.** Both Round 18 defects are fixed and measured.

- **I1 (decoder).** `skip_by_two` — which reproduces LP2's doublet rate and which the old beam
  missed at −6.90 / 25.8% — now recovers at **−4.285 / 100.0%**. 20/20 gate cells where the repo
  decoder scores 0/20. Exact mode is **faster** than Round 18's `fastbeam` (0.87×) and
  bit-identical. L7-B's constant-run failures turned out to be a *budget* setting, fixable at zero
  cost. **Trap pinned: at lambda=0 the decoder scores −4.4…−4.9 at 12–51% recovery — validate on
  RECOVERY, never on score.**
- **I2 (adjudicator).** **27/27 registers at >=0.90 power** (min 0.92). Latin 0.33 -> **1.00**,
  Welsh 0.00 -> **1.00**, vowel-dropped English 0.00 -> **1.00** (it had been *anti*-selected — the
  correct key scored below a deliberately wrong one). G-SPEED **failed** at 4.79x and is reported
  failed, with the finding that the gate was mis-specified.
- **I3 (thresholds).** **−5.5 was the wrong bar in 14 of 14 historical sweeps**, twelve times
  *too strict*: at R17's L=400 geometry the correct bar is about −6.6, which Latin/OE/DE/half-vowel
  all clear. **No verdict flips.** And the correction that matters: **dropping the unjustified
  floor alone, with no scorer change, takes Latin 0.75 -> 1.00 and German 0.67 -> 1.00 — so much of
  what L7-A diagnosed as an English-only *scorer* was an English-only *bar*.** `threshold_for` was
  fed offsets not decodes in 4/4 R17 lanes; L7-C.6's tally is inflated **6.7x**.

**2. THE TRANSCRIPTION IS NOT THE BLOCKER — closed from three independent directions.**

- **T1** built a per-rune reader scoring **100.0000% (180/180)** on the decryption-proven LP2
  control pages — meeting `AGENTS.md` section 8's own unpark threshold — and adjudicated the 450
  located O/A/AE disagreements: **450/450 AGREE with canon**, all six ordered O/A/AE pairwise
  confusion rates **exactly 0** over 1,404 glyphs. It failed its LP1 gate at 95.09% and reported
  95.09%.
- **T2** bounded length errors: canon holds **at most 1 insertion and 1 deletion at 95%
  confidence** over 13,121 positions. **A-01 is finally complete** (stalled at stage 2 since
  Round 9): **0.9973** agreement, and **zero** of its 35 disagreements is a real rune-identity
  error. Coverage **38.4% -> 99.89%**. Control **1.0000** vs frontB's 0.129.
- **T3** measured the sensitivity nobody had asked for: even *adversarially* relabelling the entire
  1,385-rune O/A/AE family reaches 1.4357%, below every English and Latin floor. Expected wrong
  runes: **0**.
- => **Canon is correct.** Two standing beliefs died: the dense pages 45–54 are **not** the weak
  stratum (T1 99.80%, T2 1.0000), and the delta-spectrum statistic L2 recorded "so that a future
  re-read can check whether it moves" **does not move**.

**3. THE SPACES ARE SMALLER THAN THE REPO BELIEVED.** Four era-correct generator families validated
**byte-exactly against real binaries** (a bash 4.2 compiled from GNU source, real perl and glibc,
three real CPython 2.7 builds including Ubuntu 12.04's own and an i386 one, real `pdflatex`) — and
every one collapsed a space called unbounded: **bash is one orbit, so seed IS offset**; **Perl's
un-seeded `rand` takes four bytes of `/dev/urandom` into a U32**; **Python 2.7 on i386 folds any
string seed to 2^32**; **TeX is a single cycle that absorbs the offset ladder outright**. pgf's real
multiplier is **69621** — the obvious 16807 appears only in a comment, so a sensible
reimplementation would have swept the wrong stream and reported a confident negative.

### The rest

| lane | verdict |
|---|---|
| **R1** red-team | **REDIRECT**, 11 FOUND-ERROR triggers. Three of four "enumerable" spaces cost **16–32 years** through the repaired instrument — the plan priced keystream *generation*, not *adjudication*. The missing lane is a **skip-aware multi-register prefilter**; G1 and G4 independently designed one (about 900x beam speed, giving 100% coverage of the top two families in about 3 days on 16 cores). |
| **C1** payload | Six contested bytes **confirm** canon under a 100% / 59-of-59 control — but **three others are wrong: 45->107, 50->47, 246->198**. The old canonicalisation was tie-broken by its own *worst* witness (2/11). **B-05's negative was VOID** and is re-run clean: 20,160 decodes, 0 escalations, **the repo's first R3-compliant sweep** (prior: 0/15). **E-01** NULL against generic PKCS#1 *and* against 3301's own signed-and-declared `Crypt::RSA::ES::OAEP`, whose wire format was **measured by decrypting 3301's own ciphertext** using primes held in the corpus (`emLen = k-1`, not OpenSSL's shape). |
| **C2** offset / Marsaglia | First measurement of what R17's 1.45e10 offsets actually bought, **by register**: composite power **0.77** English, 0.23 Latin, **0.00** Welsh, **0.000** vowel-dropped. Only **0.054%** of 2.5e9 derived-key decodes ever ran at a nonzero key offset. Marsaglia data verified 112 PASS / 0 DRIFT. |
| **C3** ornaments / PGP | All **109** bands read (Round 18 stopped at 45): decoration and mis-grouped body text; both "passing" hypotheses die under new controls; **P-9 refuted at its premise** (its `n` field is a row-group count, not a glyph count). PGP corpus re-derived from scratch — verdicts and every sha256 identical. **Two signed, verified messages carry `Version: 1.99`, `Scheme: Crypt::RSA::ES::OAEP` and Perl `Data::Dumper` output**, so the Perl prior is the author's own signed declaration, not a distro inference. |

### Errors found in this repo's own prior work

**Six lanes independently found defects in Round 18's L1 prior** — its `46/46 GnuPG v1.4.11` is
really 56 files / 54 messages / **three** version strings running to 2017; a **non-ImageMagick**
chain reproduces all four discriminating JPEG fields; `$RANDOM` is **not** a glibc `rand()`
derivative; and Perl was **not** "never swept", it was swept with a broken magnet. **Four lanes
independently refused to judge a permissive decode against −5.5. Two independently found that a
soft decoder scoring −4.4 at 12% recovery is hallucinating, not hitting.**

**T1-02 is the one that propagates furthest:** the rune **Y is typeset as TWO disconnected
components** — an outline identical to U plus a detached inner stroke. 54 of 55 sampled Y glyphs
carry one; **no other rune has one at all.** Any segmentation filtering components by rune height
discards that stroke and makes **every Y in the book pixel-identical to a U** (ink 2134 vs 2133 on
the same box). `analysis/geometry/segment.py` and `analysis/stones/pipeline.py` both filter that
way, which is very likely why `("U","Y",6)` is the top confusion in `retranscribe/diff_report.json`.

### What Round 20 inherits

1. **The sweep still has not run.** Use G1's and G4's screens, not direct enumeration. Gated on
   I3 measuring each screen's power first (doctrine R1).
2. **S2 must re-seed B-04, R16-KDF and R17 from `payload_resolved.bin`, not `canon_256.bin`.**
   `canon_256.bin` is deliberately left in place — promoting the corrected payload to canonical is
   an owner decision, not a lane's.
3. **The beam still steers by English score** (I2's stated residual). A hit in a low-recovery
   register arrives as a detection, not readable plaintext. A `pmax`-scored beam would likely
   close it.
4. **Still unbounded:** nothing covers a single key-pointer jump of J>=8 (I1), and I1's `drift`
   preset **fails G-RECOVER on Old English**.

## Round 16 — Derived-keystream armada (2026-08-23)

Six pre-registered lanes; 0 hits; all positive controls PASS.

| Lane | Tested | Verdict |
|---|---|---|
| **scorer** | Matched runic quadgram scorer (multi-char transliteration corrections) | **BOUND** — instrument production-ready; POC's SD-improvement claim not reproduced (+3.6% sigma sep, not +18%) |
| **A-03** | Haplography count-audit of 86 doublet sites | **BOUND** — K_bound=26 < K_needed=93 for autokey restoral; 3 convergent tests; K_est=0 |
| **zeroFP** | E-01 RSA/PKCS#1 (partial), E-02A/B permutation+correlation (complete), H-03 cookie XOR (complete), H-01 HTTP (partial) | **NEGATIVE** (3/4 sub-tests complete nulls at FP ~1e-24; E-01 coverage-limited — 7A35090F moduli not fetched) |
| **F-01** | LP2-as-key inversion against all held Cicada objects | **NEGATIVE** — 40 decodes, best −7.032 vs bar −5.500; RECON-A never-run item F-01 resolved |
| **KDF** | Key stretching (PBKDF2/scrypt/EVP/iterated-hash) — the primary B-04 not_covered extension | **NEGATIVE** — 692,064 decodes, 27 KDF configs × 534 secrets × 3 salts × 16 decode variants, best −6.259 vs bar −5.500; **first measured negative over key stretching** |
| **PRNG family** | 7 uncovered generators (PHP `mt_rand`, .NET, ISAAC, BBS ×2, LFSR32, Geffe) | **NEGATIVE** — 52,556 decodes over 1,877 seeds × 7 generators, best −6.347 vs bar −5.500 |

Full detail: [`liber-primus/analysis/round16/SYNTHESIS.md`](liber-primus/analysis/round16/SYNTHESIS.md).

## Round 12 — the "honest best shot" campaign (2026-08-17, committed 2026-08-19 at `06003eb`)

Six fronts ran; the campaign plan is `liber-primus/analysis/round12/CAMPAIGN-PLAN.md`.

| Front | Tested | Verdict |
|---|---|---|
| **A1** | The author's own CicadaOS binary pads (`_560.00`/`.17`, `prime_echo`, `folly`/`wisdom`, `761.mp3`) fed under the skip-aware beam for the first time — the "highest-prior untested input" from PA-3 | **NEGATIVE** (best −6.517 vs a −5.5 bar) |
| **C1** | Unbounded k-history feedback / autokey | **NEGATIVE** (21/21 positive controls recovered at 100%) |
| **C2** | 29-text fresh esoteric corpus | **UNFINISHED** — texts fetched, sweep never run |
| **D1** | Red-team: is the OTP verdict circular? | **NO-ERROR-FOUND** — B-16 (decoder validated on key-*skip*, never value-*rewrite*) tested via `rewrite_gate.py` and **closed** |
| **D2** | Independent recomputation of every load-bearing statistic | **NO-ERROR-FOUND** — all 7 reproduce exactly |
| **frontB** | Forced re-segmentation of dense pages 45–54 | **NO-ERROR-FOUND** — but honest: the forced instrument fails its own control (12.9%), so it certifies nothing; the validated R9 template DP reproduces 98.0% and upholds canon |
| **D3** | Red-team: scope overreach | **FOUND-ERROR** — see below |

**D3 is the live one.** Three load-bearing closures each state more than their evidence supports,
and the biggest hides a tractable, control-detectable, **never-run** lane:

1. *"Information-theoretically unsolvable / no compute recovers it"* → really **OTP-class**; a
   short-seed-derived keystream is statistically inseparable but has a finite keyspace.
   D3's `pc_derivedkey.py` plants one and the existing beam **recovers it at 98.9%**.
   ⇒ **RECON-A B-04, the derived-key dictionary, is real, powered and never-run.**
2. *"Seeded-PRNG pads — do not re-run"* → really 10 generators over ~3% of each seed space.
   `round10/L5-seed32/CENSUS.md` names PHP `mt_rand` as the highest-prior open generator.
3. *"Keytexts dead by mechanism"* → really dead **by exhaustion** (D1 independently agrees).

Also: `round10/RECON-A/REGISTER.md` holds **16 items still marked `never-run`**, which the line
"the internal attack surface is closed" papers over.

## Rounds 13 / 14 — in flight (started 2026-08-19)

| Lane | What | Status |
|---|---|---|
| **B-04** | The derived-key dictionary: 2,165 Cicada seeds × 16 hash/stream generators × 5 mod-29 reductions × sign × Atbash × direction × offsets, ≈6.2M decodes through the skip-aware beam | **running** — gates **G1 PASS** (D3 replicated: beam −4.170, rigid −6.835, 98.9%) and **G2 PASS** (a planted dictionary-resident seed ranks **#1 at −4.186**, reading `THEPRIMESARESACRED…` in clear, vs runner-up noise −6.62). Pre-registration: `analysis/round13/B04/PREREG.md` |
| **B-05** | The pp49–51 payload expanded as a PRF seed into a runic keystream | **running** — control PASSES on all 4 generators (98.9% recovery) |
| **PRNG** | PHP `mt_rand`, .NET `System.Random`, ISAAC, BBS, LFSR/Geffe/Gollmann | queued |
| **A-03** | Haplography count-audit of the 86 doublet sites — the cheap falsifier of the whole doublet-deficit edifice | queued |
| **zeroFP** | E-01 RSA/PKCS#1, E-02 meta-parameters, H-03 micro-crosses, H-01 onion HTTP anomalies | queued |
| **provenance** | D-01 generator fingerprint, A-06 the 47 unread ornament bands, C-02 forcing detector, G-01 source/font provenance, G-02 OutGuess blank control | queued |

**RECOVERED AND VERIFIED 2026-08-19 — `DATA/560.13`.** Round 12 A1 recorded this pad
(118,818,811 B, sha256 `db79072c…`) as unrecoverable: in both the cicada-solvers and krisyotam
mirrors it is a 134-byte Git-LFS pointer, and the LFS batch API answers `404 Object does not
exist` on both remotes. A1/RESULTS.md named archive.org's `3301.iso` as "the one remaining A1
lever" and did not attempt it.

The item exposes the ISO's **inner files** directly —
`https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13` returns HTTP 200 — and the
download verifies **byte-exact** against the LFS pointer's own digest: 118,818,811 bytes,
sha256 `db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f`.

A1's declared gap is therefore closed by measurement rather than left open. Verdict:
**NEGATIVE** — 160 configs, best −6.965 against a −5.5 bar and a null max of −7.037, i.e. 0.07
above pure noise.

**And a second, UNDECLARED gap surfaced the same day.** Building the provenance capsule revealed
that A1 swept a **truncated** `_560.00`: the cicada-solvers mirror copy is 2,412,544 B, while the
`3301.iso` copy is 3,992,970 B, and the mirror copy is an **exact byte prefix** of it — so A1
covered 60.4% of that blob and **1,580,426 bytes were never decoded**. (`560.17` from the same
mirror is byte-perfect, so the defect is file-specific.) A1's positive control and null ceiling
remain **sound** — they plant and recover under the same keystream, so truncation changes which
keystream, not whether the instrument works — but the coverage claim does not. The completion
sweep is `analysis/round12/A1/sweep_560_00_full.py`, which re-proves the prefix relation on every
run and tags results that fall in the newly-recovered tail.

Both gaps had one shape: **a file accepted as what it claimed to be, without its size or digest
checked against an independent source.** `handoff/capsule/MANIFEST.json` now records a measured
SHA-256 and length for every input, and `verify_capsule.py` reports **DRIFT** separately from
absence — a mirror serving *different* bytes is more dangerous than one serving none. Verify
against the manifest before sweeping. The completion run
is `analysis/round12/A1/sweep_560_13.py`, which reuses A1's own builders, beam settings, null
and HIT bar unchanged (so the result is directly comparable), extending only the offset ladder —
this pad is ~100× longer than the others, so it supports offsets to 5×10⁷ that A1 could not
sweep. Verdict in `analysis/round12/A1/results_560_13.json`.

## Round 18 — AIM AT THE INSTRUMENT (2026-08-25/26)

Full: [`liber-primus/analysis/round18/SYNTHESIS.md`](liber-primus/analysis/round18/SYNTHESIS.md).
Plan: [`round18/CAMPAIGN-PLAN.md`](liber-primus/analysis/round18/CAMPAIGN-PLAN.md).
Doctrine written out of it: [`liber-primus/ARMADA-DOCTRINE.md`](liber-primus/ARMADA-DOCTRINE.md).

Eight pre-registered lanes, every one with a positive control. **0 decodes over bar — and the
round is still the most consequential since D3**, because four lanes found the *instruments*, not
the search space, to be the limit.

**The correction that reaches every other entry (L7).** The word "English" appears in no
`coverage` field of the ledger's 62 entries — yet this project's own instrument, handed a
**correct key**, recovers 100% of rune indices over a Latin, Welsh or vowel-dropped-English
plaintext and still scores it as noise (worst case: **below a deliberately wrong key**). Every
"NEGATIVE" here is an **English-register** negative. `B-04`, `R16-KDF`, `R16-PRNG`,
`R17-PUBLIC-PAD` and `B-21` now carry restated coverage, with the original preserved in each
entry's `restated_from`. **This does not void them** — the register LP2 demonstrably uses scores
−4.33 at power 1.00.

| Lane | Tested | Verdict |
|---|---|---|
| **L1** | Toolchain forensics → a generator prior (G-01/B-11, never-run) | **MEASURED** — two-stage `gs` → ImageMagick; `gs` **9.04–9.14**; ranked prior promotes glibc/Python 2.7/Perl/`$RANDOM`, demotes .NET to ×0.05 |
| **L2** | The filter as a side channel (new) | **MEASURED** — the filter acts on the **ciphertext**; drift **373.6 ± 19.6** draws; SAT route proved dead; a **language-free key-side screen** at 3.08 sd |
| **L3** | The 47 unread ornament bands (A-06/B-12, never-run) | **NEGATIVE** — 109 bands, 9,899 glyphs read; found **256 non-runic tokens the analysis tree never held** |
| **L4** | The forcing/acrostic detector (C-02, never-run) | **NEGATIVE** — and C-02's *specified* detector has **FPR 0.490**; running it as written would likely have announced a false discovery |
| **L5** | The 6 contested payload bytes + E-01 (A-04, never-run) | **MEASURED** — all six resolved at 100% calibrated accuracy, **none change**; **3 real errors found elsewhere** in `canon_256.bin`; E-01 null |
| **L6** | Offset ≠ 0 + the Marsaglia CDROM (B-02/B-08) | **NEGATIVE** — **2.04 × 10⁹ offsets**, controls 40/40 and 16/16 on the real pad family; Marsaglia hash-verified and swept for the first time |
| **L7** | Instrument red-team | **FOUND-ERROR ×3** — see above, plus the beam represents exactly one rejection-loop implementation, and `threshold_for()` was used outside its calibrated domain |
| **L8** | PGP verification table + attribution (G-02/I-01/I-03) | **MEASURED** — 54/54 signatures verify under one key; **433 ranked seed candidates**; I-01 INDECISIVE; I-03 no hit |

**Three things it found that nobody was looking for:** 256 non-runic base-60 tokens across
pp. 49–51 that the geometry pipeline binned as "ornament" (transcribed, **not yet attacked**);
three byte errors in `canon_256.bin` (canon left intact — `payload_resolved.bin` ships beside it);
and the four digits of **`3299`** on page 15 set in a lighter ink tone than every other digit on
that page, absent from every transcription here.

**Where a correct key was invisible:** planted keys score **−3.949** drift-corrected versus
**−6.94** at the offset every per-page test in this repo has used.

**What to do next — not another flat-prior sweep.** L1's ranked generators × L8's 433 ranked
seeds, judged by L2's language-free screen, at L2's drift correction. Cheapest untouched item:
attack L3's 256 recovered tokens. `$RANDOM` is enumerable in minutes and has never been run, and
any past sweep that called `random.seed("...")` under **Python 3 tested the wrong semantics**.

Ledger: 62 → **83** entries; `never-run` **15 → 5**.

## Round 17 — THE PUBLIC PAD (2026-08-19/20)

Full: [`liber-primus/analysis/round17/SYNTHESIS.md`](liber-primus/analysis/round17/SYNTHESIS.md).
Pre-registered: [`round17/PREREG.md`](liber-primus/analysis/round17/PREREG.md).

**The gap.** The keystream taxonomy had exactly two branches — short-seed **derived** (finite,
being swept) and **private pad** (closed) — and the seed census folded everything else into the
second with one sentence, repeated verbatim in three load-bearing places: *"`/dev/urandom`, a
hardware RNG, **random.org**, or physical dice … nothing in the seed sweep touches it, **and
nothing can**."* That merges two different properties. **Dice and `/dev/urandom` leave no seed
AND no record. random.org, NIST's Randomness Beacon, a blockchain and a printed random-number
table leave no seed but a permanent PUBLIC RECORD** — a third branch, enumerable today, never
swept. Same failure shape D3 caught twice: a measured bound written up as a settled conclusion.

**Second gap:** every external-pad sweep here walked an **8-offset ladder** (A1's). On the 118 MB
`560.13` pad that is 7e-8 of the offset space. `round17/lib_padsweep.py` scores **every** offset.

| Lane | Pad family | Offsets | Best (bar −5.5) | Verdict |
|---|---|---|---|---|
| **P0** | A1's CicadaOS blobs, re-swept densely | 3,911,819,734 | −6.769 | NEGATIVE |
| **P1** | Bitcoin, heights 0–303,726 (both byte orders, merkle/nonce/time) | 1,389,182,016 | −6.802 | NEGATIVE |
| **P2** | NIST Beacon v1 + RANDOM.ORG daily archives | 3,464,597,548 | −6.811 | NEGATIVE |
| **P3** | RAND's million digits + 3301's own published bytes | 5,757,316,748 | −5.679 | NEGATIVE |
| **P4** | Filter fingerprint (register item **D-01**) | — | — | **MACHINE** |

≈**14.5 × 10⁹ offsets** (≈8.4 × 10⁹ effective), **0 hits**, every control recovered at 100 % of
runes, and `threshold_for()` at each lane's true trial count is *stricter* than the fixed bar in
all four sweeps. The value is the three corrections:

1. **"Nothing can touch it" is refuted for random.org — by download.** It has published a 1 MiB
   true-random file **every day since 2006-03-11**; P2 pulled **153 files (2013-09 → 2014-01),
   153/153 MD5-verified**. NIST Beacon v1's legacy endpoint still serves 2013 (v2 cannot — it
   clamps to 2018). ANU QRNG and HotBits *are* unreachable, with cause. The output is a measured
   source table, not an assertion. **Live and unswept: the Marsaglia Random Number CDROM (1995)**,
   634 MB with published SHA-256s — the cheapest remaining item in this branch.
2. **The anti-repeat filter is MACHINE, not hand-applied** — refuting `FINAL-SYNTHESIS.md:73-76`,
   which asserted a human calligrapher applying the rule by hand and used it as the attribution
   profile's anchor. Human-randomness models excluded at **≥0.99 power**; lag-2..8 bleed z = +0.65
   (zero, sign wrong for a human); no per-line scope (power 1.000). **Bound: lag-1 suppression
   80.75 %, any lag-2..8 suppression > 1.70 % excluded at 95 %.** Honest residue, reported as
   UNDERPOWERED (0.110): a human eye applying *only* that rule to a machine pad is not separable,
   and cannot be in principle. ⇒ Do **not** build a human-key-prior joint decode; the pad came out
   of a program or a file.
3. **Two instrument defects, found by lanes auditing each other** — `max_skip=3` is underpowered on
   pads with constant byte runs (P1's control *failed on its real pad*, 6/8; fixed at ms=8, 60/60),
   though P0 and P2 then measured that it does **not** bite on high-entropy pads and explained why;
   and `ks_hexchars` silently dropped digits, sweeping the A–F subsequence of hex text rather than
   hex text. Also: the flat ×0.625 survival discount is **not a constant** (0.375–0.875, non-monotone
   in size) — every lane restated its coverage downward from its own measurement.

## What is actually still open

_Superseded 2026-08. The two threads this section used to list — "an untried public keytext" and
"the AN END page" — were **both closed by mechanism** in Rounds 7–8. A new keytext is no longer a
lead on its own (any keytext is dead independent of which text it is), and the AN END page is
unreachable by construction._

_Further superseded 2026-08-17 by Round 12 D3: the framing below ("nothing in the ciphertext can
close any of it") is exactly the overreach D3 caught. The **derived-key dictionary is internal,
tractable and never-run** — it needs no external input at all. Items 1–4 below remain accurate as
the list of *external* leads._

> **Updated 2026-08-23 (Round 16).** Items B and C (KDF key stretching, PRNG uncovered
> generators) are now partially measured negatives, not untested extensions. KDF: 692,064
> decodes across 27 configs × 534 secrets × 3 salts — first measured negative. PRNG: 7
> previously-uncovered generators × 1,877 seeds. Both remain coverage-bounded (not closed).
> F-01 (LP2-as-key) is now a measured negative over all held Cicada objects (40 configs).
> See `analysis/round16/SYNTHESIS.md` for what each bound covers and what remains.

**Internal derived-keystream branch — coverage-bounded, not closed:**

A. **KDF extensions:** Argon2, bcrypt, salts outside the 3 Stage-A salts (especially
   onion-derived, pp49-51-derived), secrets outside the 534-item dictionary, per-page/
   position-varying salts, multi-stage constructions, KDF offset ≠ 0. The 692,064
   already-swept configs are in `LEDGER.json` entry `R16-KDF` — do not re-run those.

B. **PRNG seed coverage:** hour-stride seeds (×24 per generator), offsets ≠ 0 (×~100),
   full 2^32 (×~250 per generator), KISS/MWC/WELL/lagged Fibonacci. The 52,556
   already-swept decodes are in `LEDGER.json` entry `R16-PRNG` — do not re-run those.

C. **E-01 (RSA/PKCS#1 completion):** the 7A35090F RSA-4096 primary + subkey moduli are the
   right size for the 256-byte payload and have never been checked. Script at
   `analysis/round16/zeroFP/zerofp_tests.py` accepts additional moduli.

What is left externally is **low-prior**:

1. **A signed or archival pointer** that a specific text *is* the key — i.e. evidence from outside
   the ciphertext, not another text to try.
2. **A correctly-targeted, locally-held archive** that could contain the lost AN END page.
   (Residual activity here = passive monitoring only; the active hunt is closed.)
3. **The author's own binary pads (PA-3, 2026-08)** — the 2013 CicadaOS `DATA/_560.*` files and
   the `761.mp3`⊕`twitter.txt` pair, period-correct key material Cicada demonstrably used, never
   fed under the skip-aware decoder. Not held in-repo; needs fetching. Highest-prior *input*
   remaining (still low absolute prior). → `analysis/round10b/PA-3/ARTIFACT-INVENTORY.md`
4. **RECON-C** — a pre-registered, resumable community-archive fetch (cijhho insider tree, Reddit)
   deliberately deferred, not a crash. Cheap to run. → `analysis/round10/RECON-C/`

_Superseded by Round 9/10:_ the **32-bit seed sweep** (Round 8 loose end) is now **parked with
cause** — L5-seed32 proved the pre-registered threshold is statistically invalid at full-32 scale,
so completing it is a "completeness ritual" (do not resume without a scale-corrected threshold from
`nullcurve.py`). The **SKELETON corpus extension** ran as L4 against 224 texts / 22.6M words:
**negative** (best 22.7% match, z=−1.03, inside the null band).

**What would reopen the case:** a new 7A35090F-signed Cicada release, a CicadaSolvers-accepted
reproducible page solve, or the private pad surfacing.

---

# Historical detail

_Kept for provenance. The avenue log below is from the 2026-06-20 snapshot; where it disagrees
with the ledger, the ledger wins._

## The 4 avenues
| # | Avenue | Status |
|---|---|---|
| 1 | Independent **vision re-transcription** of the 56 page images | ✅ **closed 2026-06-20** — not viable; canonical verified — `liber-primus/analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| 2 | Doublet-avoidant / fractionation attacks | ✅ closed (ruled out) — `analysis/OPEN-AVENUES.md` |
| 3 | Contribute findings to community | ✅ shipped — `liber-primus/docs/FINDINGS-FOR-SOLVERS.md`, repo public |
| 4 | OSINT for the lost deep-web hash page | ✅ **closed 2026-08** — unreachable-by-construction; `analysis/anend_hunt/FINDINGS.md` |

## ✅ AVENUE #1 — what happened (closed)

Ran the full 56-agent vision armada (one Sonnet agent per page, blind reads).
**Result: vision cannot transcribe these dense ~250-rune pages** — mean
alignment vs canonical was only **0.145** (noise). Confirmed canonical is the
correct one, not vision, via (a) `tests/validate.py` reproducing every solved
page from the canonical runes, and (b) a manual high-zoom re-read of p0 matching
canonical exactly. No transcription error exists to find. Full writeup +
artifacts: `liber-primus/analysis/vision/` (`AVENUE-1-VISION-VERDICT.md`,
`DIFF-REPORT.md`, `vision_results.json`, `build_canonical.py`, `diff_vision.py`).

To reproduce: re-download images (gitignored) then re-run the helpers:
```bash
cd liber-primus/data/relikd
for i in $(seq 0 55); do curl -sL -o p$i.jpg \
  "https://raw.githubusercontent.com/relikd/LiberPrayground/main/pages/p$i.jpg"; done
cd ../.. && python analysis/vision/build_canonical.py   # ground truth
# armada writes analysis/vision/vision_results.json, then:
python analysis/vision/diff_vision.py                   # DIFF-REPORT.md
```
Only conceivable revival = per-rune cropping (~13k individual high-zoom reads) —
cost-prohibitive, documented but not executed.

## ✅ AVENUE #5 — Image steganography (NEW, run + closed 2026-06-20)

Asked: do the LP2 page images carry stego (like Cicada's 2012/2013 images)? Never
examined here before. Result: **no recoverable image stego.** Highlights:
- **Provenance proven:** our circulating images are byte-authentic — **56/56 SHA1
  match** the archive.org `ky2khlqdf7qdznac.onion` onion7 hashes (first published
  verification). They're 400-DPI Ghostscript/Artifex renders ⇒ not OutGuess carriers.
- No appended-data (0 trailing bytes/56), no EXIF/COM, carve = validated-clean,
  LSB = lossy-noise, red/black color = **relikd solver annotation** (dead).
- OutGuess: 30/33 LP2 pages **empty**; 3 give capacity-length (58152 B) entropy-7.997
  false-positives that share a **1417-byte prefix** — most likely OutGuess default-key
  keystream over the pages' shared blank margins (artifact, not payload).
- Full writeup: `liber-primus/analysis/stego/STEGO-VERDICT.md` (+ `stego_scan.py`,
  `provenance.json`). **Not 100% closed:** the decisive control needs OutGuess 0.2 on
  a Linux env (no WSL/Docker/compiler on this box) — see verdict §"decisive next experiment".

## ✅ AVENUE #6 — Transcription cross-verification (NEW, run + closed 2026-06-20)

Re-attacked the "canonical transcription unverified" question the right way (after
AI vision failed). Recon armada mapped every machine-readable LP2 transcription:
**the whole field has ONE root — rtkd/iddqd (2017)** (krisyotam credits it, the
wiki copies it, cadrypt/LiberPrimusSolver/cicada-library/JBO derive from it). So
unanimity ≠ independence. BUT a 3-way rune-stream diff (`analysis/transcription/crossdiff.py`)
shows all distinct lineages — krisyotam (canonical), relikd (diff delimiters,
"double-checked"), rtkd (root) — are **rune-for-rune IDENTICAL: 13136/13136, 0
divergences**. Plus the rtkd baseline was image-audited via PRs (2017–21), I
spot-verified p0/p20/p44 lines by eye against the authentic images (`linecrop.py`),
and it reproduces all solved pages. **Verdict: canonical corroborated; no
transcription error found** (full writeup `analysis/transcription/TRANSCRIPTION-VERDICT.md`).
Limit: not a from-scratch independent re-read (none exists; vision can't deliver one).

## Other live (long-shot) thread, if wanted
- **CT-logs brute force** for the "AN END" deep-web hash (avenue #4 tail): hash
  early-2014 Certificate Transparency log entries against
  `36367763…c2a8b4` across the candidate algorithm set (tweqx/dwh-check).
  Low odds; documented in `analysis/DEEPWEB-HASH-OSINT.md`.

## Key files
- `liber-primus/docs/FINDINGS-FOR-SOLVERS.md` — what's eliminated + why (start here)
- `liber-primus/analysis/OPEN-AVENUES.md` — ranked remaining avenues
- `liber-primus/attack.py` — validated attack CLI (`selftest` re-finds DIVINITY)
- `liber-primus/tests/validate.py` — proves the rig on all solved pages

## Do NOT re-run (proven dead)
More key texts, keywords, keystreams, autokey, differencing, page-keying,
fractionation, transposition-only. All eliminated with reasons recorded.
