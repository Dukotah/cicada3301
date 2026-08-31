# Solver Strategy 2026 — where to point NEW effort

_Written 2026-08-31 for a future SOLVER (human or AI) who wants to actually crack LP2 and is
asking the only useful question left: given tools that did not exist when Cicada built this, where
is the marginal hour best spent? This is a **targeting** document, not another survey. It assumes
you have read `handoff/FOR-FUTURE-SOLVERS.md` (the cold-start map) and will consult
`ELIMINATION-LEDGER.md` before running anything. Every claim below is traced to a measurement in
this repo; where a prior is low, it says so plainly. This repo's ethos is rigor over hope — hold
this document to it._

> **Trust anchor.** `python3 tests/validate.py` → `ALL VALIDATIONS PASSED` (5/5), confirmed
> 2026-08-31 before this doc was written. It re-derives every known solved page (atbash / atbash+shift /
> Vigenère `DIVINITY` / Vigenère `FIRFUMFERENFE` / totient) from the canonical runes. If it ever
> stops passing, nothing here is trustworthy — fix that first.

---

## 1. The one-paragraph state

LP2 pages 0–54 (12,956 runes) are **OTP-class** — and "OTP-class" is a precise, one-of-two
indistinguishability class, not a shrug. From the ciphertext alone it is impossible to separate
**(a)** a **true external one-time pad** (information-theoretically closed — no cryptanalysis
breaks it, ever) from **(b)** a **keystream derived from a short seed** (finite keyspace, therefore
enumerable and brute-forceable). The ciphertext carries exactly one real structural signature — a
~0.66% adjacent-doublet rate against 3.45% random, a ~5× *deficit* — and that anomaly is itself
produced by a soft anti-repeat rewrite that reveals nothing about which branch is true
(`analysis/round10b/B4-otp-steelman/` G5: a SHA-256-CTR keystream under the same filter is
statistically inseparable from a true pad, max |z| = 1.60). No clever cryptanalysis moves this;
only two things can — an **external key/page surfacing**, or **brute-forcing the finite
derived-key branch to exhaustion**. As of 2026-08-31 the verdict is **hardened, not overturned**,
across **25 rounds**, on the order of **10^10 logged decodes**, and **142 ledger entries**
(`LEDGER.json`). The prior mass sits on "external or unseeded pad, no recoverable key." Read this
document as a map of the two doors that remain and which modern tooling opens them.

---

## 2. What was cutting-edge when Cicada built this (2012–2014)

To know what the puzzle was *designed to resist*, know the era's toolbox. Cicada's chain ran
2012–2014; LP2 was dumped from onion7 (`ky2khlqdf7qdznac.onion`) in May 2014. The state of the
art the makers built against, and which the whole design assumes an attacker has:

- **PGP / GnuPG 1.4** for signing and per-recipient RSA email. The authenticity gate to this day is
  a signature from key `7A35090F` (last authentic signed message: April 2017). GnuPG 1.4.11 spans
  ≥6 OS generations of the era (`analysis/round20/` closeout C).
- **TrueCrypt** for volume encryption; **OutGuess / steghide** for image steganography — the
  community's default first move on any Cicada image, and the reason the stego layer was checked
  exhaustively (all channels empty; the pages are 400-DPI Ghostscript renders, not carriers —
  `analysis/stego/STEGO-VERDICT.md`).
- **Tor v2 hidden services** (16-char `.onion`) as the delivery substrate. This matters enormously
  for §4: Tor v2 was **deprecated and shut off by October 2021**, so the addresses in the 2014
  chain are dead endpoints, and the AN-END destination — gated behind solving LP2 — was never
  independently archivable.
- **Book / running-key ciphers** — the standard humanities-flavored cipher, and the design LP1 and
  the early stages actually used (Vigenère over named keys).
- **Anglo-Saxon futhorc + Gematria Primus** — a 29-rune alphabet, each rune mapping to a letter (or
  digraph) *and* a prime, all arithmetic mod 29 (`src/lp/gematria.py`). The 29-rune choice matches
  the Old English Rune Poem exactly; a casual maker would default to the 24-rune Elder Futhark.
- **Prime / totient / number-theoretic keys** — the solved AN-END page (56) is a totient keystream;
  primes and φ recur throughout as key material.

**The cipher's own fingerprint.** The doublet suppression is not a textbook cryptographic hardening
— no cryptographer forbids adjacent repeats by hand (it leaks that a constraint exists while adding
almost no security). It **is** a named object in enumerative combinatorics: a **Smirnov word /
Carlitz composition** — a sequence with no two adjacent equal letters (Carlitz, 1970s). It is a
*combinatorialist's* instinct grafted onto a cypherpunk toolchain, and its softness (~18–20%
residual, memoryless, uniform across all 29 runes) is consistent with a **hand-inscribing
calligrapher** applying a "don't write the same rune twice" rule.
See `analysis/attribution/TECHNIQUE-FINGERPRINT-2026-07-29.md`.

> **One honest correction the repo forces here** (`analysis/round17/P4_filter/RESULTS.md`, Round
> 16/17): "a *person supplied the randomness*" is refuted. Every human-randomness model with any
> signature beyond the bare immediate-repeat rule is excluded at ≥0.99 power; lag-2..8 bleed is
> z = +0.65 (zero, wrong sign for a human); the filter had no per-line scope. So the underlying pad
> is machine-generated even if a person did the *inscribing*. The Smirnov/Carlitz *technique*
> fingerprint stands; the inference to a hand-*applied filter* does not. Do not overclaim the
> calligrapher.

---

## 3. What modern tools have ALREADY been thrown at it

So you do not re-run 2026's work: this whole project **is** the modern-tooling assault. Specifically:

- **LLM multi-agent armadas** — 25 rounds of pre-registered, adversarially-verified fan-out attack
  (`analysis/round1…round25/`), plus an 11-iteration rotating-critic loop (`FINAL-SYNTHESIS.md`)
  that self-corrected three of its own false positives. This is the single largest coordinated AI
  cryptanalysis effort on LP2, and it produced ~10^10 logged decodes and 0 breaks.
- **A 99.2% SVC glyph classifier** that independently re-verified the transcription at the glyph
  level — the transcription is *not* the blocker, confirmed multiple independent ways
  (`analysis/transcription/`, `analysis/vision/AVENUE-1-VISION-VERDICT.md`). Note the contrast:
  whole-page AI-vision re-transcription *failed* (mean alignment 0.145 — the model confabulates on
  dense rune pages), while the narrow classifier and the crossdiff succeeded. The canonical string
  is right.
- **Deep-research OSINT sweeps** — multi-agent, live-checked archival/witness hunts
  (`analysis/anend_hunt/FINDINGS.md`, `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md`).
- **Skip-aware / drift-tolerant decoders** — the load-bearing instrument. LP2's anti-repeat filter
  desynchronizes key from ciphertext, so a *rigid* 1:1 decoder scores even the **correct** key as
  noise (−6.8) while the beam scores it as English (−4.2). This is the single most expensive mistake
  in the problem's history; the repo's decoder is `analysis/campaign18_skip/skipdecode.py` and its
  `driftbeam` presets.
- **A 9-register language adjudicator** — a panel-max null calibrated at M=1e6 (bar 7.634) with
  correct-key power 1.00 across LP1_REAL / Latin / OE / half-vowel English / German / Welsh / KJV,
  plus a hallucination-guarded three-clause hit function
  (`analysis/round20/HITFN/hitfn20.py`) that rejects a bar-clearing decode unless rune-index
  recovery ≥ 0.90 **and** a held-out ¾ of the page reproduces under the same key. Score alone never
  certifies a solve.
- **GPU-ready-but-Python seed sweeps** — the derived-key brute force exists and is
  control-validated, but runs in pure Python 2.7-emulated MT
  (`analysis/round25/compute-tail/`, `analysis/round19/G3/gen_py27.py`). This is the bottleneck §4.1
  addresses.

---

## 4. The tools-since-2014 leverage map — RANKED, honest

For each modern capability: what it unlocks, why it might move the needle, and the honest prior.
This ranking was verified against the repo; where the repo refines it, that is noted inline.

### 4.1 GPU / FPGA at 2025 scale — HIGHEST leverage, IF the pad is a short seed

**What it unlocks.** Two finite, well-defined brute-forces that were merely expensive in 2014 and
are cheap now:

1. **The derived-key seed sweep.** The Py2.7 `MT19937().init_by_array([w])` 2^32 word space is the
   one branch that is enumerable *end-to-end without a sieve* and is provably not excluded by the
   ciphertext. The problem: it has been swept **only fractionally**. The Round 25 compute-tail
   grind was parked at **21,539,647 words = ~0.50% of 2^32**, 0 hits, best pmax 6.826 vs the 7.384
   bar (`analysis/round25/compute-tail/RESULTS-parked.md` — the canonical parked-state record; note
   `RESULTS-chunk1.md` shows only the single-core chunk-1 start of ~0.0175% and is superseded by the
   6-core parallel-grind coverage). Even so, **>99.5% of this one generator's space is untouched**,
   and other reducers/offsets/generators are at or near 0%. At **~1,650–1,966 seeds/s on 6 cores in
   pure Python**, the remaining ~4.27 billion words are ~25–32 continuous wall-days. That is the
   *only* reason this grind is measured in weeks.
   A GPU/C port of MT19937 + the mod-29 reducer + the skip-by-two decode finishes 2^32 in **hours**,
   and there are three untouched reducers (grb5_mod / grb5_rej / shuffle29) plus the 64-bit ABI
   word map and non-zero offsets still at 0%.
2. **The AN-END hash preimage.** The page-56 target is a 512-bit content hash
   (`36367763…c2a8b4`). Modern GPU hashing makes candidate-corpus preimage checks orders cheaper —
   *if a correctly-targeted corpus ever surfaces* (see §4.2 for why one does not yet).

**Why it might move the needle.** This is the ONLY internally-runnable path that can *change the
verdict* rather than merely re-confirm it. Finishing the finite seed space converts "probably not a
cheap PRNG" into "definitively not a cheap PRNG" — and a hit (a word whose keystream decodes the
page and reproduces on the held-out ¾) would be an outright solve.

**Honest prior: LOW, but the leverage-per-hour is HIGHEST.** The prior is low because it requires
the author to have used a *guessable, short* seed rather than `/dev/urandom` / hardware RNG / dice —
and the modal behavior for someone building a one-time pad is exactly the unguessable source
(`analysis/round10/L5-seed32/CENSUS.md` §E). But the space is finite, the instrument is
control-validated (Round 25 self-test: plant recovered at recovery 1.000 through the full gate),
and no one has run a GPU port. If you have compute, **this is the one thing worth actually
building.** Doctrine caveat: if you scale the search, recompute the family-wise null bar
(`analysis/round10/L5-seed32/nullcurve.py`) — bigger searches raise the bar, and past ~10^15
decodes the planted-true score stops clearing it.

### 4.2 Modern archival / OSINT forensics — HIGHEST *expected value*, aimed at the external frontier

**What it unlocks.** The external door — the only thing that can reopen a *true* external pad. Modern
tooling the 2014 makers could not have anticipated: Tor v3 crawl corpora, archive.today, Internet
Archive CDX at scale, leaked-onion datasets, breach-DB people-search.

**Why it might move the needle.** Two targets:

1. **The lost AN-END deep-web page.** This is the external key candidate. But the repo's own hunt
   (`analysis/anend_hunt/FINDINGS.md`) sharpened it from "cold trail" to **unreachable-by-construction**:
   its address is produced by *solving the pages between* — i.e. LP2 0–54 itself — so there is no
   independent address to look up, Tor v2 died October 2021, and no genuinely-retrievable in-scope
   corpus exists (Wayback tor2web indexed the *known* onion7 host and captured only downtime
   placeholders; DUTA / Memex / LIGHTS / Ahmia are all out-of-window or not downloadable). Every
   held artifact hashes null against the target across all major 512-bit digests, in both raw and
   content-representation axes. **So modern crawl tooling helps only if a NEW correctly-targeted
   corpus surfaces** — a 2014-era Tor snapshot that indexed the page independently of the chain.
   That is the specific thing to hunt.
2. **Attribution.** The witness/attribution threads the repo already keeps live: the per-person
   RSA-encrypted email channel, the retained CAKES git repo, and reachable humans — Joel Eriksson
   (`je@clevcode.org`, verified active) and Marcus Wanner (located 2026-07-27). Modern breach-DB and
   private-IRC-log access are non-public vectors that could corroborate the profile.

**Honest prior: LOW on cracking the cipher, but this is where the repo's OWN live threads point** —
precisely because the cipher is math-locked and the external door is the only one a true pad can
open. Best run as **passive monitoring** (zero cost) plus one **targeted archival hunt** for a
new in-scope corpus, not a repeat of the exhausted OSINT sweeps.

### 4.3 Modern ML image / glyph forensics — worth it only if a new representation is suspected

**What it unlocks.** Beyond the 2014-era OutGuess-only stego checks and the SVC classifier:
diffusion-era anomaly detection on the 400-DPI scans (learned-prior residual analysis that can flag
statistically-anomalous pixel structure invisible to fixed LSB/DQT tests).

**Why it might move the needle.** It wouldn't, on current evidence — every stego channel is empty
and the pages are Ghostscript renders (not stego carriers). The only scenario where this pays is if
a *new representation* is suspected (a channel nobody has modeled). Note that whole-page vision
re-transcription is a known dead end (0.145 alignment); do not re-attempt it.

**Honest prior: LOW.** Worthwhile only as a cheap sanity pass with a working positive control, not a
campaign.

### 4.4 SMT / SAT + neural cryptanalysis — mostly foreclosed by the OTP proof

**What it unlocks.** Constraint-solving and learned distinguishers — powerful against *structured*
ciphers.

**Why it (mostly) won't move the needle.** A true one-time pad has **no structure to solve for** —
there is no constraint system whose solution is the plaintext, because for any chosen plaintext a
valid structureless key exists. Neural distinguishers need a signal; the ciphertext is at the random
floor (IoC·N = 1.000, entropy ≈ 4.857/4.858 bits) with a single anomaly already fully explained by
the rewrite filter.

**Honest prior: essentially zero.** Worth at most **one honest framing pass** — e.g., an SMT
encoding of the *derived-key* branch (the seed → keystream → decode relation is structured even
though the pad is not) as an alternative front-end to the §4.1 brute force. Not a campaign.

---

## 5. The genuinely-open threads, ranked for a solver

What is actually worth trying, with the honest prior on each. **No entry here is likely to
succeed** — the prior mass sits on "external or unseeded pad." These are ranked tails.

1. **External / archival — a surfacing AN-END page or a new Cicada release.** The ONLY thing that
   reopens the cipher if the pad is truly external. Run as passive monitoring (watch
   `cicada-solvers/Cicada-DWH-HashcatAttempts` and `tweqx/3301-hash-alarm` commit feeds for any
   non-zero match; watch for a new `7A35090F`-signed message) plus a targeted hunt for a *new
   in-scope 2014-era Tor corpus*. **Prior: LOW, highest EV among the tails** — because it is the
   only door a true pad can open, and it costs almost nothing to watch.
   Ref: `analysis/anend_hunt/FINDINGS.md`, `handoff/FOR-FUTURE-SOLVERS.md` §8.

2. **Derived-key PRNG / seed brute force.** Bounded, enumerable, built byte-exact, control-validated,
   and only ~0.50% swept (>99.5% of the Py2.7 space untouched). Needs a GPU/C port to finish (§4.1). The one internally-runnable
   long-shot that can *change* the verdict. **Prior: LOW** (requires a guessable short seed) **but
   the only lane compute helps and the only finite one.**
   Ref: `analysis/round25/compute-tail/`, `analysis/round19/G3/`, `handoff/PARKED.md` P-2.

3. **Attribution.** Maxed at a defensible profile (combinatorialist + Old-English philologist +
   cypherpunk, likely a small collective), with **no falsifiable name**. Only non-public vectors
   remain: breach-DB, private IRC logs, and direct contact with reachable witnesses (Eriksson
   `je@clevcode.org`, Wanner). **Prior: LOW for a name; a name would not solve the cipher anyway.**
   Ref: `analysis/attribution/TECHNIQUE-FINGERPRINT-2026-07-29.md`,
   `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md`.

4. **Non-fold oracle / seal.** Round 21 L1 *proved* the disjoint-fold no-oracle held-out proxy
   leaky (best 0.80 catch, below the 0.90 bar — `analysis/round21/L1-seal-realmode-proxy/RESULTS.md`):
   a bar-clearing survivor currently cannot be auto-certified as a solve, only flagged-for-oracle. A
   *different* real-mode proxy that reaches ≥0.90 catch would unblock auto-HIT-calling for the §5.2
   sweep. **Prior: LOW** (instrument work, not a solve, but it hardens the one runnable lane).

5. **Figural-motif channel.** Round 22-D built the first drop-cap catalog and read it out
   (`SLXHXFUMDSFAINGP` — null against a 10,000-shuffle size-matched null;
   `analysis/round22/D-illustration-dropcap/RESULTS.md`). The broader figural illustrations
   (trees, crosses, turtle/spatial renders) as a data channel **never opened** — but the extractor
   must be **control-validated first**: Round 22-B's turtle/spatial render (Q1) is a weak,
   uncontrolled extractor and any positive from it is untrustworthy until it recovers a plant.
   **Prior: LOW, and beware pareidolia** in a 14–16-symbol channel.

---

## 6. The honest bottom line

The highest-EV moves are the **external / archival** ones — not more cipher-bashing — because the
cipher itself is provably math-locked: a true one-time pad has no cryptanalytic attack surface, and
25 rounds of the largest modern AI assault on LP2 confirmed exactly that. A solver's time is best
spent:

1. **Hunting the lost AN-END page and the attribution trail with modern archival tooling** — the
   only door a true external pad can open, and the direction the repo's own live threads already
   point. Passive-monitor at zero cost; hunt specifically for a *new* correctly-targeted 2014-era
   corpus, since the known ones are exhausted and null.
2. **If (and only if) you have GPU compute: finish the finite seed brute-force.** Port the
   control-validated Py2.7-MT + skip-by-two pipeline to GPU/C and enumerate the remaining 99.98% of
   2^32 (plus the three untouched reducers, the 64-bit map, non-zero offsets). This converts
   "probably not a cheap PRNG" into "definitively not," and a hit is an outright solve. It is the
   only internally-runnable move that can change the verdict rather than re-confirm it.

**Do not re-run anything in the `ELIMINATION-LEDGER.md`.** The value of this repo is an accurate map
of where the walls are. Every negative here was produced with a passing plant-and-recover positive
control and a pre-registered threshold; re-running them gains nothing. Aim at the two open doors, or
aim at the instrument (per `ARMADA-DOCTRINE.md`) — never at the exhausted spaces.

---

_Written 2026-08-31. Trust anchor `python3 tests/validate.py` → ALL VALIDATIONS PASSED (5/5),
before and after. No git commit (WSL has no creds; the owner commits from Windows)._
