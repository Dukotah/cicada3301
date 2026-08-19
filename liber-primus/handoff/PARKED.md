# PARKED — correct to attempt, blocked on capability

_2026-08-19. Written for a reader with better tooling than existed when this was assembled._

Everything here is **parked because of a capability limit, not because it lacks merit**. That
distinction is the whole point of the file: a dead end and a deferred experiment look identical
in a repository six months later, and conflating them means the deferred one never gets run.

Each item states the hypothesis, what specifically blocks it, **the capability threshold that
unparks it**, the procedure, the pass/fail bar, the expected cost, and the honest prior.

Items that are dead on the merits are **not** here — they are in
[`../ELIMINATION-LEDGER.md`](../ELIMINATION-LEDGER.md). Items blocked only on *effort* are in
the table at the bottom, deliberately kept separate: padding a capability-blocked queue with
ordinary to-dos is how a handoff loses its credibility.

**Be honest about the priors.** Most entries below are low. The prior mass in this problem sits
on "the pad is external or unseeded, and there is no recoverable key"; these are the tails worth
checking because they become cheap once the capability exists. A queue that oversells is worse
than none.

**Before running any of these,** read [`FOR-FUTURE-SOLVERS.md`](FOR-FUTURE-SOLVERS.md) — in
particular, do not attack LP2 with a rigid decoder. It scores the *correct* key as noise.

---

## P-1 — Per-rune vision re-transcription · prior: **medium** · the clearest "wait for better tooling" item

**Hypothesis.** The canonical transcription contains rune errors that a from-scratch independent
re-read would expose. This matters far more than it sounds: every statistical result in this
repository — the doublet deficit above all — is computed on that transcription, and its two
supposedly-independent lineages share one 2017 root (rtkd/iddqd), so a *systematic* misread could
have propagated into every attack ever run here.

**Why parked.** Whole-page AI vision was run as a 56-agent armada and **failed**: mean alignment
to canon was 0.145, i.e. noise. The pages are dense (~250 stylized runes each) with near-identical
glyph pairs (ᚦ/ᚩ/ᚹ, ᛒ/ᛖ, ᚾ/ᛁ, ᛗ/ᛞ) and no positional anchors, so models lose their place and
generate plausible-but-invented runs. `analysis/vision/AVENUE-1-VISION-VERDICT.md` names the only
conceivable revival — **per-rune cropping, ~13,000 individual high-zoom reads** — and records it
as cost-prohibitive, documented but not executed.

**Unparks when.** A vision model can read an isolated, high-zoom single rune at ≥99% accuracy on
the *solved* pages. That is a cheap thing to test before committing to the full run, and it is a
capability that has been improving quickly.

**Procedure.**
1. Re-download the images and verify:
   `python3 handoff/capsule/verify_capsule.py --only images` — all 56 must report intact
   (the manifest cross-checks each against the archived onion7 SHA-1).
2. Segment per-rune using the validated R9 template-DP line segmentation
   (`analysis/round12/frontB/` — use the instrument that *passes* control at 98.0%, **not** the
   forced re-segmentation one, which fails its own control at 12.9%).
3. **Calibrate on solved pages first.** Pages 01, 03, 05, 06, 14 have known plaintext. Measure
   per-rune accuracy there before touching an unsolved page.
4. Read every rune of pages 0–54 blind — no canon in the prompt, or the test is worthless.
5. Diff against canon; adjudicate every disagreement by hand at high zoom.

**Pass/fail bar.** The instrument must reach **≥99% per-rune accuracy on the solved control
pages**. Below that, its disagreements on unsolved pages are indistinguishable from its own error
rate and cannot support a conclusion either way — that is exactly the trap the 2026 whole-page run
fell into when it reported 51 "high-confidence candidates" that were all artifacts.
For a *finding*, additionally require: the same crop read identically on ≥3 independent passes,
and a downstream measurement that actually changes. Corrections that change nothing measurable
get logged, not celebrated.

**What a positive result would do.** Change `n`, the doublet count, and therefore every
downstream statistic. Roughly 20 confirmed **merges** would put autokey back on the table.
And a *negative* here is valuable too: it converts "canonical is unverified in the weak sense"
into "canonical is independently confirmed", retro-validating a decade of negatives.

**Cost.** ~13,000 reads × 3 passes ≈ 39,000 inferences, plus segmentation. Trivial for a model
that can read a full page reliably in one pass — which is the actual unpark condition.

**Prior that it finds a transcription error: LOW.** Three independent lines say canon is right:
the rig reproduces all five solved pages from these exact runes (an ~85%-wrong transcription could
not do that); a manual high-zoom re-read of p0 line 1 matched canon exactly and showed the vision
agent had fabricated; and two careful transcriptions of one image should agree far above 14.5%
even if both were imperfect. **Prior that it is worth running anyway: HIGH.**

**Related but cheaper:** item **P-8** below (haplography *count*-audit) tests the same worry at
1/5th the volume by checking rune **count** rather than rune identity.

---

## P-2 — The full 32-bit seed sweep · prior: **low-medium** · parked *with cause*, not merely unfinished

**Hypothesis.** The pad is a seeded PRNG whose seed lies in a 32-bit space. Eight of Round 8's
ten generators were swept over only the 2011–2015 unix-second slice (~2.9% of the space);
generators 10–13, added and validated in Round 10 lane L5, likewise.

**Why parked.** Not compute — **statistics**. `analysis/round10/L5-seed32/` proved the original
pre-registered threshold is *invalid at full-32 scale*. Round 8 fixed its hit bar at **−12.5**
after observing a null max of −13.13 over 2.52e9 decodes. The completed sweep is ~34× larger per
generator, and best-of-N under a null grows as μ + β·ln N, so a threshold calibrated at one N is
not a threshold at another. Completing the sweep against the old bar would be a completeness
ritual producing garbage: any decode crossing it would be an *expected null event*, not a lead.

**Unparks when.** A scale-corrected threshold is derived. The tool already exists:
`analysis/round10/L5-seed32/nullcurve.py`, exposed as `threshold_for(n_trials, segment_len)` in
`benchmark/null.py`. Measured on 2026-08-19 for the completed 10-generator sweep:

| quantity | value |
|---|---|
| E[null max], one generator, full 2³² × 2 dir (N=8.59e9) | −12.8629 · P(null > −12.5) = 0.032 |
| E[null max], completed 10-gen sweep (N=8.59e10) | **−12.5707** — the old −12.5 bar therefore FAILS |
| E[null max], with L5's 4 new gens (N=1.2e11) | −12.5280 · P(null > −12.5) = 0.363 |
| FWER 0.05 | **−12.2670** |
| FWER 0.01 | **−12.0602** |
| FWER 0.001 | **−11.7674** |
| planted-true recovery | **−11.2360** (margin +0.8242 over FWER-1%, ≈6.5 β) |

The lane's own pre-registered H2 line was "safe iff E[null max] ≤ −12.60" → measured −12.5707 →
**H2 FAIL**. The last row is the important one: **the sweep retains power** under the corrected
bar (H3 line met at margin +1.3347). It is worth resuming — with the corrected threshold.

**The derivation, recorded so it survives this repo.** Fit a Gumbel to per-chunk maxima
(location μ, scale β) over 2²⁶-seed chunks; E[max of N] = μ + β·(ln N + γ), γ = 0.5772156649;
the family-wise threshold at level α over N decodes is μ + β·(ln N − ln(−ln(1−α))).
`nullcurve.py` estimates β three independent ways — E1 (same-N MLE on this lane's generator-0
chunk maxima, real ciphertext), E2 (the same on the shuffled-ciphertext control), E3 (across-N
slope from Round 8's own logs, two points 34× apart) — and **uses the largest β**, because a
larger β makes false positives more likely and is therefore conservative. Measured on this box:
real μ = −13.4332, β = 0.1124 (n=22); shuffled μ = −13.3029, β = 0.1149 (n=16). The
real-vs-shuffled location difference is 0.1304 (1.16 β) — **no signal in the swept range**.

**Procedure.**
```bash
cd liber-primus/analysis/round10/L5-seed32
gcc -O3 -march=native -fopenmp -o sweep32  sweep32.c  -lm
gcc -O3 -march=native -fopenmp -o sweep32x sweep32x.c -lm
./sweep32x selftest        # must print "selftest: 14/14 generators recovered"
./validate_gens.sh         # must print "HARNESS GATE: PASS"
python3 nullcurve.py       # RE-DERIVE on your hardware; do not reuse the table above blindly
./run32.sh <gen 0-9> real  # resumable, checkpointed per 2^26-seed chunk
python3 coverage.py        # the authoritative coverage statement
```
**Do not use `analysis/seed_sweep/run_full32.sh`.** `L5-seed32/RESUME.md` is explicit: it appends
one line per *generator*, so a kill mid-generator loses hours with no record. That is exactly what
happened — its log holds 2 lines and no `DONE`, and `gen=0` (glibc, the highest-prior generator
and first in its own priority order) is **absent from `results_full32.txt` entirely**. Use
`L5-seed32/run32.sh`, which checkpoints per chunk and resumes automatically.

**Pass/fail bar.** A hit = a decode above **−12.0602** (FWER 0.01) on the 48-rune window, which
must then survive (a) re-decode of the full 12,956-rune stream under `skipdecode.beam_decode`,
and (b) a score better than −5.5. Anything crossing the bar but failing (a) or (b) is logged as an
expected null event. Zero hits at the corrected bar over a completed sweep is a **real** negative
and should be written into `ELIMINATION-LEDGER.md` as one.

**Cost.** ≈11.3 h wall / ≈1.5 CPU-days for the 8 unfinished Round-8 generators (measured:
1.17 M seeds/s, 2²⁶ seeds ≈ 55 s); +≈4 h for generators 10–13. Embarrassingly parallel.

---

## P-3 — `DATA/560.13` · prior: **low-medium** · **block broken 2026-08-19**

**Hypothesis.** Cicada's own authored binary files from the 2013 CicadaOS are the pad. Round 12
front A1 fed five of them under the skip-aware decoder and got a clean NEGATIVE — but
`DATA/560.13` (118,818,811 bytes, sha256 `db79072c…`) is the largest and it was **not covered**:
in both the cicada-solvers and krisyotam mirrors the file is a 134-byte Git-LFS pointer, and the
LFS batch API returns `404 Object does not exist` on both remotes. A1's own closing line: *"the
one remaining A1 lever."*

**Status change.** The file **is retrievable** from archive.org's `3301.iso` item as an inner
file. The item is 136,398,848 bytes (not multi-GB, as had been assumed), archive.org serves an
inner-file listing for it, and the whole ISO honours HTTP `Range` (verified: `206 Partial
Content`, `Content-Range: bytes 0-99/136398848`), so it is resumable in bounded chunks:

```
https://archive.org/download/3301.iso/3301.iso/          # lists 11 members incl. DATA/560.13
https://archive.org/download/3301.iso/3301.iso/DATA%2F560.13   # returns HTTP 200, streams
https://archive.org/download/3301.iso/3301.iso           # whole ISO, Range-resumable
```

**RECOVERED AND VERIFIED 2026-08-19.** sha256
`db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f`, 118,818,811 bytes — both
matching the Git-LFS pointer's own claim in `analysis/round12/A1/lfs_req.json`. The bytes are in
place at `analysis/round12/A1/pads/DATA_560.13` (gitignored; hash receipt committed at
`handoff/capsule/recovered/DATA_560.13.sha256`). **The A1 re-run was NOT performed** — that is
this item's remaining work. See [`capsule/RECOVERY-560.13.md`](capsule/RECOVERY-560.13.md).

> ### ⚠ And a second, unplanned finding: A1's `_560.00` was TRUNCATED
>
> Cross-checking every pad against the authoritative ISO turned up a defect. The `_560.00` that
> Round 12 A1 actually swept is **2,412,544 bytes**; the file in the CicadaOS ISO is
> **3,992,970 bytes** — the community-archive copy is **1,580,426 bytes short (~40% missing)**
> and has a different sha256. `560.17` from the same archive is byte-perfect, so this is specific
> to `_560.00`.
>
> This is not a bystander: `sweep.py`'s `null_ceiling()` loads `PADS["_560.00"]`, so A1 used the
> truncated file both as a swept pad **and** to build its positive control and null ceiling.
> **A1's `_560.00` negative therefore covers only ~60% of the real blob.**
>
> The authoritative copy is in place as `pads/DATA__560.00.iso-authoritative` (sha256
> `a24051a8…`). The truncated file was deliberately **left unmodified** so A1's existing results
> remain reproducible against the input that produced them.
>
> **So P-3 is now two pads, not one:** sweep `560.13` *and* the authoritative `_560.00`, and
> record which `_560.00` each result used.

**VERIFY BEFORE USE — non-negotiable.**
```bash
sha256sum DATA_560.13
# must equal db79072ce580efa54acf5f31f3ef0eb00aef867871a051d04e27ee5e7fbc112f
# size must equal 118818811
# (oid+size recorded in analysis/round12/A1/lfs_req.json — the authoritative fingerprint)
```

**Procedure.** Drop it into `analysis/round12/A1/pads/` as `DATA_560.13` and re-run that harness
**unchanged** — it is already written, already control-gated, and already covers the reductions
{mod29, prime_to_idx, hi_nibble, lo_nibble, byte_scaled}, both signs, both byte directions,
whole-stream and per-page:

```bash
cd liber-primus/analysis/round12/A1 && python3 sweep.py     # then sweep2.py for per-page
```

**Re-confirm A1's positive control first** (it already passes; re-use it): PARABLE-like plaintext
enciphered with the real `_560.00` pad (`mod29`, key-skip filtered, offset 5000) recovers at beam
**−4.211 / 100% rune match**, while rigid decode of the same gives **−6.668** (the desync trap)
and the wrong pad gives **−7.049**.

**Pass/fail bar.** As A1: **HIT = max(−5.5, null_max + 0.5)**. Measured nulls: head sweep n=200,
mean −7.291, max −6.995; per-page n=200, mean −7.308, max −6.877. For calibration, A1's best over
340 configs on five pads was −6.883 — 1.38 below the bar, squarely noise. Anything at or below
−5.5 closes A1 completely.

**Cost.** 136 MB download (minutes); harness re-run minutes-to-low-hours. Note 560.13 is ~100×
the length of the runic stream, so **offset coverage is the binding constraint** — sweep offsets
more densely here than A1 did for the small pads.

**Prior: LOW.** Five sibling pads from the same directory, same author, same day, produced nothing
above noise. But this is the difference between "we tested the author's pads" and "we tested five
of the author's six", and it closes a named lane outright rather than opening one.

---

## P-4 — PHP `mt_rand` and the other uncovered generators · prior: **medium** · blocked on a reference runtime

Listed here because the navigation docs said "seeded-PRNG pads — do not re-run", which is wrong
and would otherwise stop you. Round 8 covered **10 generators over ~3% of each seed space**
(2 fully) and that was written up as a class kill.
`analysis/round10/L5-seed32/CENSUS.md` §C names as **uncovered**:

| Generator | Prior | Missing capability |
|---|---|---|
| **PHP `mt_rand()`** | **High** — the census's highest-prior open generator, period-appropriate for a 2013 web-hosted puzzle. Has a *documented* deviation from reference MT19937 (the `MT_RAND_PHP` bug, fixed only in PHP 7.1) plus its own `RAND_RANGE` scaling ⇒ **unreachable from the swept generator 5**. | no `php` binary on the box ⇒ cannot pass the harness gate |
| **.NET `System.Random`** | Medium (Windows author). Knuth subtractive / lagged-Fibonacci `ran3`, seeded via the 161803398 constant — structurally unlike everything swept. | no `mono`/.NET runtime |
| **Blum–Blum–Shub as a real seed space** | Medium. ARMADA-20 tested 2,080 configs seeded by *Cicada constants only* — a keyword probe, not a seed sweep. "BBS dead" is true of those 2,080 configs and nothing wider. | needs implementing + a reference to gate against |
| ISAAC · LFSR/Geffe/Gollmann · KISS/MWC/WELL/lagged-Fibonacci | Low–medium | not implemented anywhere in the repo |
| Seed spaces beyond 2³², millisecond-resolution seeds, offset ≠ 0 | — | see **P-10** (compute) and RECON-A B-02 (a separate lane) |

**Excluded by date — do not re-open.** PCG (published August 2014), xoroshiro / xorshift128+
(Vigna 2014). LP2 was posted **January 2014**. V8/SpiderMonkey `Math.random` is low-prior *by
construction*: not seedable from JavaScript, so an author could not reproduce their own pad.

**Requirement before sweeping:** validate each generator against a real reference implementation
(a `php` binary, published test vectors) and *reproduce known output exactly* — 5 seeds × 2000
draws, as `validate_gens.sh` does for generators 10–13. An unvalidated generator cannot produce a
trustworthy null; that was Round 8's own standard and this lane's pre-registration forbids
relaxing it.

**And use the beam decoder.** Round 8 swept rigid-only, which returns noise even on a correct seed
once the filter applies.

**Pass/fail bar.** As P-2, but **recompute** — adding generators increases total N and therefore
*raises* the bar. Do not reuse the −12.0602 figure at a different N.

**Cost.** ~1 h wall per generator over the full 32-bit space, plus implementation and gating.

**Prior: LOW overall, MEDIUM for PHP `mt_rand` specifically.** The census's own arithmetic:
adding all remaining generators multiplies total coverage by ~1.3×; PHP alone by ~1.1×.

> **The category that makes this whole hypothesis conditional (CENSUS §E).** `/dev/urandom`, a
> hardware RNG, random.org, or physical dice produce a pad with **no compressible key**. That is
> the *modal* behaviour for anyone who sets out to build a one-time pad, it holds the majority of
> the prior mass, and **nothing in any seed sweep — finished or unfinished — can touch it.** The
> seed sweep's value is that it cheaply excludes the *lazy* implementations. It was never able to
> exclude the competent one. Do not read a completed sweep as more than that.

---

## P-5 — The "AN END" deep-web page · prior: **very low** · closed by construction; passive only

LP2 page 56 publishes a 512-bit hash (`36367763…c2a8b4`) of a deep-web page it declares every
pilgrim's duty to find. The lost page's address is gated behind solving LP2 0–54 (the 2014 chain
grammar is "each onion's solved content yields the next address"), so **it cannot be reached
without the thing it would help solve**. The circulating `gy3hoy2…onion` address is a debunked
hallucination. No genuinely retrievable in-scope Tor-v2 corpus exists (Wayback's tor2web CDX is
empty-of-content even for the *known* onion7 host and rejects blind queries with HTTP 403;
DUTA/DUTA-10K is 2016+ and off-topic; DARPA Memex CDR bulk data was never released; LIGHTS is not
downloadable; historical Ahmia publishes no 2014 dump). The held corpus hashes null across
**2,706 tests** (2,574 + 132).

Community status 2026: CicadaSolvers official — "the referenced hash has never been found";
`cicada-solvers/Cicada-DWH-HashcatAttempts` — **zero** matches, latest activity **2025-10-29**;
`tweqx/3301-hash-alarm` (~15 hash families incl. SHA-512 / BLAKE2b / BLAKE-512 / SHA-3 / Streebog
/ Skein / Whirlpool) — never logged a hit.

**Residual activity: passive monitoring only.** Take no retrieval action. Act only on:
1. a **non-zero match** in `cicada-solvers/Cicada-DWH-HashcatAttempts` commit history;
2. a **hit logged by `tweqx/3301-hash-alarm`** (dormant since 2021, not retired);
3. a **new message signed by PGP key `7A35090F`** (none authentic since April 2017);
4. a **new Tor-v2-era archival corpus of 2014 vintage becoming publicly retrievable** with blind
   search — the only genuinely capability-shaped unpark, and the reason this is parked rather than
   deleted.

On trigger 1, 2 or 3, everything downstream reopens, including this file. Do not spend effort on
an active hunt — `analysis/anend_hunt/FINDINGS.md` documents why it is unreachable by
construction. **Cost: zero until a trigger fires.**

---

## P-6 — CT-log brute force for the AN END hash · **NOT parked — closed by construction**

The idea (originated by GitHub user `relikd`, recorded in `analysis/DEEPWEB-HASH-OSINT.md`): hash
early-2014 Certificate Transparency log entries against `36367763…c2a8b4` across the candidate
algorithm set.

**This is non-viable *by construction*, not on volume grounds, and no amount of compute or bulk
access unparks it.** CT logs hold **CA-issued certificate domains** — not page contents, and not
Tor v2 onion addresses, which are self-signed and never appear in CT at all. There is therefore
**no relevant candidate in the corpus to hash**, at any scale. Closed in Campaign XIII; recorded
at `ELIMINATION-LEDGER.md:168`.

It is kept in this file for one reason only: it *looks* like a compute-blocked lane and is not
one, so deleting it silently would invite its rediscovery as a fresh idea.

---

## P-7 — The 6 contested payload bytes (RECON-A A-04) · prior: **medium** · blocks another lane

Pages 49–51 carry a 256-byte non-runic payload (`analysis/pp49_51/canon_256.bin`). Six byte
positions — indices **25, 175, 182, 199, 215, 237** — have been flagged as contested since
Campaign VII and repeated in Campaign IX, and never resolved, because adjudicating them needs a
**Latin/digit OCR**, which the rune classifier structurally cannot do (it is trained on the
futhorc glyph set).

**Why it matters beyond itself.** Lane B-05 tests the payload as a PRF seed, and a PRF is
avalanche-sensitive: one wrong byte destroys the keystream completely. B-05's own control
confirms this — flipping a single contested byte drops recovery from −4.170 to −7.38, i.e. from
perfect to noise. So **B-05 cannot be fully settled while these bytes are contested**, and every
negative over `canon_256.bin` (Campaigns VII, IX, XX, and B-05) is a *conditional* negative.

**Unparks when.** A vision/OCR model can read Latin characters and digits from these page crops
reliably. Same capability class as P-1, far lower volume — six positions, not 13,000.
**Gate it on a control:** read 100 *uncontested* bytes from the same pages and reproduce
`canon_256.bin` exactly at those positions. If that fails, the reader cannot adjudicate the
contested ones. Then require ≥3 concordant independent reads per contested byte.

**Cheaper interim procedure that needs no new capability — do this first.** Do not wait for OCR.
Enumerate: for each of the 6 indices list every plausible reading, form the Cartesian product
(≈64–few hundred variants), and run **every variant** through the B-05 harness. That is a small
multiplier on an already-built sweep and it removes the conditionality entirely without ever
resolving a glyph. Raise the family-wise threshold by the variant count — adding N variants
multiplies the search space by N, so recompute the null rather than reusing B-05's
single-payload bar.

**Prior: LOW that a corrected payload decodes anything** (the payload has failed as key material,
as ciphertext, and as a container). **MEDIUM that the enumeration is worth doing anyway**, because
it is cheap and converts a conditional negative into an unconditional one.

---

## P-8 — Haplography count-audit of the 86 doublet sites (RECON-A A-03) · prior: **medium**

**Rides on P-1's pipeline; listed separately because its prior is materially higher and its
volume is 5× lower.**

**Hypothesis.** LP2's near-total absence of doubled runes (~83% suppression, Campaign XI) is this
repo's central structural finding and the entire basis for the "engineered anti-repeat filter"
model that motivates the skip-aware decoder. **A transcription artifact would look identical:**
if transcribers silently merged doubled glyphs (haplography), the "filter" is an illusion and the
autokey kill has to be reopened.

**Why parked.** Requires auditing **rune count** (not identity) in the neighbourhood of each of
the 86 doublet sites at high zoom — the same per-rune vision capability as P-1. Campaign IX's
`i9_ocr` only spot-checked p0 lines 1–3. Flagged twice in the repo as "documented but heavier";
never run.

**Unparks when.** P-1's reader clears its solved-page control. Counting is an *easier* task than
identification, so this may unpark first; if so, gate on a **count** control instead — reproduce
the exact rune count of each solved page.

**Procedure.** Crop the neighbourhood of each of the 86 sites; count glyphs; compare to canon's
count at that position. Report merges (canon short by one) separately from splits.

**Pass/fail bar** — the repo's own stated threshold, pre-registered here:
**≥20 sites where an independent count exceeds canon's by exactly one**, each confirmed on ≥3
passes ⇒ the engineered-filter model is falsified, the autokey kill reopens, and every skip-aware
negative in the repo needs re-reading. **<5 ⇒ the filter model is confirmed and this closes.**
**5–19 ⇒ inconclusive** — report the raw counts and do not spin them.

**Cost.** ~86 sites × ~10 runes of context × 3 passes ≈ 2,600 reads.

**Prior: MEDIUM.** This is the cheapest available falsifier of the largest load-bearing structure
in the repo, and it has never been run. That combination is unusual and is why it is called out.
It does not mean the filter is likely fake — ~83% suppression is a great deal of haplography to
ask for — but "never audited" is not "checked".

---

## P-9 — The unread ornament bands (RECON-A A-06) · prior: **low**

Round 8 catalogued **47 non-text ornament bands across 23 pages** (`geometry/ornaments.json`
holds 62 rows) and explicitly recorded this as *"inventory, not a result — the one item in Round
8 left as an open thread"*. The short bands (1, 3, 4, 8, 16 glyphs) are the only real candidates,
and in Round 8's own words **"nobody has read them."**

**Why parked.** Non-text glyph runs at page scale. The automated pipeline classified them as
non-text and skipped them; whole-page vision cannot read them (P-1's 0.145 alignment). Needs the
same per-rune reader.

**Procedure.** From `geometry/ornaments.json`, crop each short band; read glyph-by-glyph; map
through the Gematria Primus where the glyphs are futhorc, record raw sequences where they are not.

**Pass/fail bar — deliberately brutal, because 1–16 symbols is pareidolia territory.** A band
counts as signal only if (a) it decodes to an English word or known Cicada string of length **≥8**
under a cipher already validated on the solved pages, **or** (b) the same short band recurs at ≥3
sites and decodes consistently at all of them. A 3-glyph band reading as some 3-letter word is
**not** a result — with 47 bands over a 29-symbol alphabet, expect several by chance.

**Cost.** ~300 glyph reads once the reader exists.

**Prior: LOW.** Ornaments in a hand-set book are usually ornaments. But "nobody has read them" is
a true statement about a primary-source artifact of the target, and the cost is near zero once
P-1 unparks.

---

## P-10 — Seed spaces wider than 32 bits · prior: **low** · with a documented power ceiling

The case `CENSUS.md` §D names as uncovered *inside* generators that are otherwise fully swept.

| Extension | Size vs the 32-bit space | Feasibility, 2026 laptop |
|---|---|---|
| Java's full 48-bit `setSeed` space | ×65,536 | ~2,500 CPU-days. Not reachable. |
| Millisecond time seeds, Java/Python (64-bit) | 1.26e11 values for 2011–2015 ⇒ ×30, and **disjoint** from the 32-bit space | Not reachable |
| MT `init_by_array` multi-word keys | unbounded | dictionary-only, not a sweep |
| CPython `random.seed()` on `str`/`bytes` | routes through SHA-512 ⇒ dictionary-only | 15,408 tested (Round 8); unbounded in principle |
| Keystream offset ≠ 0 | ×8,192 for a modest range, and it multiplies **every** generator | separate lane (RECON-A B-02) |

**Unparks when.** ~10³–10⁵× the throughput of a 2026 laptop — a GPU/FPGA port of the
decode-and-score inner loop, or a cluster. Genuinely a capability threshold: the algorithm is
unchanged, only the scale is out of reach.

**Procedure.** Port `sweep32x.c`'s inner loop (generate → reduce mod 29 → score a 48-rune window)
to the accelerator; validate with `./sweep32x selftest` (must recover all planted generators)
**before** trusting any output; then extend the range.

**Pass/fail bar — and the honest killer of this lane.** Re-derive with `nullcurve.py` at the new
N, and note the direction: **larger N raises the bar.** At N ≈ 10¹⁵ the family-wise threshold
moves up by roughly β·ln(10¹⁵/10¹¹) ≈ 0.11 × 9.2 ≈ **+1.0**, i.e. to about **−11.06** at FWER
0.01 — against a measured planted-true score of **−11.2360**, leaving a margin of only ~0.18.
**Past roughly 10¹⁵ decodes the sweep loses the power to distinguish a real hit from the null
even if the hit is there.** Compute alone does not fix that; a *sharper scorer* (longer window,
or more bits of evidence per decode) is required alongside it. Any proposal to brute-force a
wider seed space must state its expected null max and planted-true margin **before** running.

**Prior: LOW** — same reasoning as P-2/P-4: the no-seed case (CENSUS §E) holds the majority of the
prior mass and is untouchable by any of this. Parked with its power ceiling documented so nobody
spends a cluster on a search that could not report a hit if it found one.

---

## P-11 — Attribution leads blocked on non-public archives · prior: **low**

Two RECON-A items blocked on **archive availability**, not effort. Neither would yield a key even
on success — at best a name. Ranked last deliberately.

**I-01 — `mruzuki` / `cicadeur`** (keyid `02BD208AFB8AFF75`, `mruzuki@gmail.com`; key created
2012-01-12, **self-revoked 2012-01-22** — seven days after the first 3301 image). The earliest
Cicada-adjacent keyserver actor, and the repo auditor's own #1 remaining item. No identity
resolution was attempted beyond public/sandbox sources.
*Unpark:* only with additional **public-record** sources. **Do not pursue this into private data,
and do not attempt to deanonymise a living person.** The puzzle is not worth that, and a solved
cipher is not a licence. If the only remaining route is non-public, this stays parked
permanently — that is a decision, not an oversight.

**I-03 — Pre-disclosure archive search**, cypherpunks / metzdowd / bitcointalk, 2011–2013.
Campaign VIII's own #1 open thread, *"unresolved only because the archives are thin, not because
it was cleared."* Never executed as a search.
*Unpark:* a materially more complete public archive of those lists for 2011–2013 becoming
searchable.
*Bar:* a **pre-2014-01** post referencing Liber Primus content, the Gematria Primus, or the
onion7 material **before** its public release. Nothing weaker counts — post-hoc thematic
resemblance in cypherpunk mailing lists is free.

---

## Not parked — merely unfinished

These RECON-A `never-run` items need **an afternoon, not a capability**, and are excluded from the
queue above on purpose. Anyone arriving today can run all of them with the tooling already here.

| id | lead | why it is only effort |
|---|---|---|
| **C-02** | Line/word/page-initial ciphertext-rune uniformity test — the detector for *forcing* (an acrostic or layout constraint imposed in ciphertext). Proposed with a hard gate (p<0.001); no script, no result. | statistics over data already in-repo |
| **D-01** | Generator-fingerprint suite: conditional next-rune distribution, windowed χ² under-dispersion sweep, monogram drift across the book (fatigue signature). The two provenance sub-tests **Campaign IV skipped**. Discriminates a machine sampler from a human drawing a pad by hand — the load-bearing claim in `FINAL-SYNTHESIS`. | statistics over data already in-repo |
| **E-01** | Payload as an **RSA signature/ciphertext** under known Cicada moduli: `pow(s,e,n)` in both endiannesses for every published 3301 modulus, pattern-match PKCS#1 v1.5 / PSS. Zero-false-positive, minutes of compute. | stdlib arithmetic |
| **E-02** | Payload as **meta-parameters**: (a) slide a 56-byte window, test for a permutation of 0–55 (chance ≈1e−24 per window); (b) read it as 85–128 gap values (8/16-bit LE/BE, varint) and rank-correlate against the real doublet gaps [122, 85, 249, 197, 129, …]. Both "instant"; neither run. | stdlib arithmetic |
| **F-01** | **LP2-as-pad inversion** — treat the 12,956 runes as *key material*, not a message, against every other machine-readable Cicada object. Finite candidate set, hours of compute. Survives (is not killed by) the iter-2 "message-existence is undecidable" finding. | hours of ordinary CPU |
| **G-01** | The **PROVENANCE track**, proposed and never executed: source-PDF + rune-font identification, Ghostscript build fingerprint from DQT+ICC+geometry, hunt circulating PDFs with a real text layer, re-read the archived `onion7_index.html` for non-`.jpg` assets, match glyph outlines against stock runic faces. | OSINT + file forensics |
| **G-02** | `STEGO-VERDICT`'s own "decisive next experiment": `outguess -r` on a blank control JPEG through the same 400-DPI Ghostscript pipeline, to prove the shared 1417-byte prefix is a default-key artifact. **Was** blocked ("no WSL/Docker/compiler"); that constraint has evaporated — WSL2 + gcc are present and OutGuess 0.4 was later built for the OSINT sweep. | the stated blocker no longer exists |
| **H-01** | Per-onion HTTP/server-status anomalies: ports 5240–5243, mock uptime "1 days 0 hours 33 minutes 14 seconds" → 1033, leaked host `li676-224.members.linode.com` / 106.186.123.224, per-onion `<head>` malformation. Raw HTML held locally; never resolved as a channel. | local files |
| **H-03** | Two named micro-crosses: the 2013 onion cookies (`167=6941…`, `761=7bc1…`) **XOR'd against the four hex strings**; and the 2012 P.S. digit-string rotate-90°/matrix reading. Both explicitly "never executed"; completeness-only. | minutes |
| **A-01 / A-02 / A-05** | Three *partially-run* transcription audits with data on disk and no verdict ever written: A-01's `read_lines.json` (16,245 glyphs, 646 lines) with stage-3 `diff.py` producing no artifact; A-02's `oae_mismatch.json` (450 located O/A/AE disagreements) with no per-instance adjudication; A-05's 19 rune-count-exact lines disagreeing on separator count. | the measurements exist; only the write-up is missing |

---

## How to add to this file

State the capability threshold in **testable** terms ("≥99% per-rune accuracy on solved control
pages"), never as a vague "when models get better". A threshold you can test in an afternoon is
what turns a parked item back into a runnable one.

An entry qualifies **only** if you can name the missing capability. "We didn't get to it" belongs
in the table above, not in the queue. And every entry must carry its pass/fail bar written
*before* the run — a bar written after seeing output is not a bar, and this project's entire claim
to producing meaningful negatives rests on that distinction.
