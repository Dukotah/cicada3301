# For future solvers

_Written 2026-08-19 for someone arriving cold — a researcher, or a model with far more compute
and better vision than anything available when this was written. It assumes you know
cryptography and nothing about this repository. It should get you productive in under an hour._

Everything here traces to a document or a measurement in this repo. Where something is uncertain,
it says so. **The most useful thing this project can give you is not a lead — it is an accurate
map of where the walls are**, so you do not spend a month rediscovering them.

---

## 1. The problem, stated precisely

Cicada 3301 published a runic book, the **Liber Primus**, in two parts. Part 1 (LP1, 17 pages)
is essentially solved. Part 2 (**LP2**, 58 pages numbered 0–57, dumped in May 2014 from the Tor
hidden service `ky2khlqdf7qdznac.onion` — "onion7") is not.

- **Two LP2 pages are solved:** page 56 ("AN END", a totient keystream) and page 57 ("PARABLE",
  plaintext transliteration).
- **The unsolved target is pages 0–54: 12,956 runes.** That is `nc.unsolved()` in
  `analysis/round11/lib_numchannel.py` — the flattened first 55 of 57 page-segments. This exact
  number is the handshake: **if your pipeline does not produce 12,956 runes, stop and reconcile
  before comparing anything to this repo's results.** The capsule records a SHA-256 over the
  comma-joined rune indices for precisely this check (`runes.unsolved_stream` in
  `handoff/capsule/MANIFEST.json`).
- **The alphabet is the Gematria Primus:** 29 runes, each mapping to a letter (or digraph:
  TH, EO, NG, OE, AE, IA/IO, EA) *and* to a prime. All arithmetic is **mod 29**.
  `src/lp/gematria.py` is the table.
- **One rune is special:** ᚠ (F, index 0) acts as an **interrupter** on solved pages — a
  skip/no-op marker rather than a plaintext letter. Solved-page decryptions require handling it.

### What "solved" means, and how it is verified

A page is solved when a stated key and method turn its runes into readable English that the
community accepts. In this repo that is mechanised, and it is the **trust anchor** for
everything else:

```bash
python3 liber-primus/tests/validate.py     # must print: ALL VALIDATIONS PASSED
```

It re-derives five known solved pages from the canonical runes through this repo's own cipher
rig, checking each output contains documented words:

| page | method | check |
|---|---|---|
| `Runes - 01.jpg` | Atbash | A WARNING — "BELIEVE", "FROMTHIS", "TRUE" |
| `05.jpg` | plaintext transliteration | SOME WISDOM — "PRIMES", "SACRED", "TOTIENT" |
| `06.jpg` | Atbash + Caesar shift 3 | A KOAN — "MANDECIDED", "MASTER", "STUDY" |
| `03.jpg` | Vigenère `DIVINITY` + interrupters | WELCOME — "PILGRIM", "JOURNEY" |
| `14.jpg` | Vigenère `FIRFUMFERENFE` + interrupters | CIRCUMFERENCE — "LESSON", "EXPLAINED" |

**If that command fails, nothing below is trustworthy.** Run it first, always. It is cheap.

### The scoring scale you will see everywhere

Scores are normalised English quadgram log-probabilities (`nc.eng_norm`, built from
`data/english_quadgrams.txt`). Calibrate on these:

| score | meaning |
|---|---|
| **≈ −4.2** | real English. The solved pages land at −4.1 to −5.0. |
| **≈ −5.5** | the usual pre-registered HIT bar |
| **≈ −6.5 to −7.5** | noise. Shuffled-ciphertext nulls live here. |

A result at −6.5 is **not** "almost English". It is noise. This distinction is where most
enthusiastic false positives in this field come from.

---

## 2. The current honest verdict

> **LP2 pages 0–54 are OTP-class.** The keystream runs the full length of the message, and its
> output was deliberately filtered so the same rune is almost never written twice in a row
> (~83% doublet suppression — Campaign XI). From the ciphertext alone, **it is impossible to
> distinguish a true external one-time pad (information-theoretically closed) from a keystream
> *derived from a short seed* (finite keyspace, and therefore brute-forceable).** Which one it is
> cannot be settled by any statistic; it is settled only by running the derived-key search.

**Do not write "information-theoretically unsolvable" without that qualifier.** That is the exact
overreach a red-team audit caught in this repo, and it matters because it foreclosed a real,
tractable, never-run lane. The full finding is `analysis/round12/D3/RESULTS.md`; the corrected
paragraph now heads `ELIMINATION-LEDGER.md`.

The evidence for the correction, in one line each:
- `analysis/round10b/B4-otp-steelman/b4_results.json` (G5): a SHA-256 counter-mode keystream
  derived from a short seed, under the same filter, is **statistically inseparable** from a true
  pad — `"separated": false`, max |z| = 1.60 across a 6-statistic battery.
- D3's positive control **planted** such a keystream (seed `CICADA3301`) under the repo's own
  pinned anti-repeat filter and **recovered it**: beam decode **−4.170**, 98.9% character
  recovery, against **−7.349** for a wrong seed and a null max of −6.044 over 200 shuffles.
  So "no compute recovers it" is demonstrably false over that lane.

A short-seed-derived keystream lives in a finite, enumerable keyspace. One member of the
indistinguishability class is closed; the class is not.

**The practical consequence for you:** if the pad is external, no amount of compute helps and the
only path is obtaining the key. If it is derived, compute *does* apply. Nothing in the ciphertext
tells you which. Both branches are live, and the honest split of prior mass favours "external or
unseeded" (see §4).

---

## 3. Proven vs merely unrefuted

Keeping these apart is the whole point of this repo. Conflating them is how a decade of work
turns into folklore.

### Proven (measured, reproducible, with a passing positive control)

- **The transcription is not the blocker.** Verified three independent ways: all community
  lineages are rune-identical (`analysis/transcription/`); the rig reproduces every solved page
  from these exact runes; and a manual high-zoom re-read of p0 line 1 matched canonical exactly.
- **The page images are the authentic originals.** All **56/56 SHA-1 hashes** of the circulating
  relikd copies match the values published in the archived onion7 dump
  (`analysis/stego/provenance.json`; independently re-verified 56/56 by this capsule, and
  extended to SHA-256). This is the first published cryptographic provenance chain for these
  files.
- **There is no recoverable image steganography** in the LP2 pages. Appended-data, EXIF/COM/XMP,
  embedded-file carve, spatial LSB, colour channel and DQT are all empty; OutGuess extracts empty
  on 30 of 33 sampled pages, and the 3 "hits" are capacity-length false positives sharing an
  identical 1417-byte prefix — a default-key tool artifact. The pages are 400-DPI Ghostscript
  renders, which are not OutGuess carriers in the first place. (`analysis/stego/STEGO-VERDICT.md`)
- **The doublet suppression is real and extreme** (~83%), and it defeats rigid decoding. See §5.
- **The skip-aware beam decoder recovers planted signals that a rigid decoder scores as noise.**
  Demonstrated repeatedly with plant-and-recover controls (D3, Round 12 A1, Round 13 B-04 G1).
- **The old seed-sweep threshold is statistically invalid at full-32 scale.** Measured, not
  argued: E[null max] over a completed 10-generator sweep = **−12.5707**, against a
  pre-registered threshold of −12.5 that required ≤ −12.60 to remain safe.
  (`analysis/round10/L5-seed32/nullcurve.py`, re-run 2026-08-19.)

### Unrefuted but not proven — treat as open questions, not results

- **"The pad is external."** Cannot be shown from the ciphertext (§2). It is a *hypothesis
  consistent with* the evidence, not a finding.
- **"The keytext family is dead by mechanism."** What actually survives is a ~200-text
  **exhaustion** sweep (best −5.75…−5.88) under an **unverified robustness assumption**: the
  validated skip-aware gate covers key *skip* (desync), not value *rewrite*. Round 10's RECON-B
  item B-16 flagged this; the fix is a rewrite-tolerant gate row. Read the ledger's keytext rows
  as "closed by exhaustion", not "closed by mechanism".
- **"Seeded-PRNG pads are closed."** Round 8 covered **10 generators over ~3% of each seed
  space** (2 fully). Written up as a class kill. `analysis/round10/L5-seed32/CENSUS.md` §C lists
  what is named, plausible and *never swept* — PHP `mt_rand` foremost.
- **The pp49–51 payload results.** Conditional on **6 contested bytes** (indices 25, 175, 182,
  199, 215, 237) that no one has ever adjudicated. Key material is not error-tolerant, so those
  negatives are conditional negatives. (`handoff/PARKED.md` P-7.)
- **"The author's own CicadaOS pads are dead" (Round 12 A1).** Two holes, both found 2026-08-19.
  `DATA/560.13` — the largest of the six — was never tested at all (it was unfetchable; it is now
  recovered). And the `_560.00` that *was* tested is **truncated by ~40%** relative to the copy in
  the authoritative CicadaOS ISO, so that pad's negative covers only ~60% of the real file. See
  `handoff/capsule/RECOVERY-560.13.md`. Read A1 as "four of six pads swept, one partially".
- **The engineered-filter model itself.** Never audited against the alternative explanation that
  transcribers merged doubled glyphs (haplography). The audit is cheap and has never been run
  (`handoff/PARKED.md` P-8).

---

## 4. The method — why this repo's negatives are worth anything

A negative result in cryptanalysis is worthless unless you can show your instrument would have
seen a positive. Most public Liber Primus work does not do this, which is why so little of it
compounds. Two rules make the difference here, and **you should adopt both before running
anything**:

**Rule 1 — Pre-registration.** Write the hypothesis, the exact search bound, the null model, and
the pass/fail threshold to a file *before* the run. Round 13's `PREREG.md` files are the pattern.
A threshold chosen after seeing output is not a threshold.

**Rule 2 — A passing plant-and-recover positive control, every time.** Plant a known key/seed of
the family under test, encipher known English through the same filter, and confirm your
instrument recovers it. If it cannot recover a *planted* signal, your negative says nothing about
the real ciphertext.

Both rules exist because of a specific, repeated failure mode: **the rigid decoder scores the
correct key as noise on filtered ciphertext** (−6.835 for the correct seed, vs −4.170 for the
same seed under the beam). Every attack in this problem's history that used a rigid decoder
produced a false negative and did not know it.

> **The shared harness for this lives at `liber-primus/benchmark/`.** It packages the plant,
> the null, the gates, and a power calculation so a new attack can be validated in minutes rather
> than reinvented. *(Being built in parallel with this document by agent H-2; if the directory is
> incomplete when you arrive, the components it harvests are all present and usable directly:
> `analysis/round12/D3/pc_derivedkey.py`, `analysis/round12/C1/control.py`,
> `analysis/round13/B04/sweep.py`, `analysis/campaign18_skip/skipdecode.py`,
> `analysis/round11/lib_numchannel.py`, `analysis/round10/L5-seed32/nullcurve.py`.)*

**The null model to use:** `nc.shuffled` (seed 3301) — length-matched shuffles of the real
ciphertext, N ≥ 200. Report `null_mean` and `null_max`, and set your bar at
`max(−5.5, null_max + 0.5)`.

**One statistical trap to internalise.** Best-of-N under a null grows as μ + β·ln N. A threshold
calibrated at one search size is invalid at another, and **bigger searches raise the bar**. This
already invalidated one of this repo's own pre-registered thresholds (§3). If you scale a search
up, recompute the family-wise threshold with `nullcurve.py` — and check that your *planted-true*
score still clears it, because past roughly 10¹⁵ decodes it stops doing so and the search can no
longer report a hit even if one exists.

---

## 5. What NOT to waste time on

Each of these is closed with a reason and a place to reproduce it. The full record, ~30 rows
deep, is `liber-primus/ELIMINATION-LEDGER.md`.

| Don't | Why | Reproduce / read |
|---|---|---|
| **Attack with a rigid (1:1) decoder** | LP2's anti-repeat filter desynchronises key from ciphertext. The *correct* key scores −6.8 (noise) rigidly and −4.2 (English) under the beam. This is the single most expensive mistake in this problem. | `analysis/campaign18_skip/skipdecode.py`; D3 control |
| **Try another book as a running key** | ~200 texts swept, best −5.75…−5.88, all noise. *Caveat: closed by exhaustion, not by mechanism — see §3.* | `analysis/CAMPAIGN-XII/XIII-FINDINGS.md` |
| **Re-run integer-seeded hobbyist PRNGs over the time-seed slice** | 2.52e9 decodes, 0 hits. *But the class is not closed — §3, and `PARKED.md` P-2/P-4 for what genuinely remains.* | `analysis/seed_sweep/`, `round10/L5-seed32/CENSUS.md` |
| **Autokey** | Positively refuted (not merely unfound). *Reopens only if P-8 finds ~20 haplography merges.* | `ELIMINATION-LEDGER.md` |
| **Image steganography** | Every channel empty; the pages are Ghostscript renders, not stego carriers. | `analysis/stego/STEGO-VERDICT.md` |
| **Whole-page AI vision re-transcription** | Mean alignment vs canonical **0.145** across 56 pages — the model confabulates. The canonical is right and vision was wrong. | `analysis/vision/AVENUE-1-VISION-VERDICT.md` |
| **Hunting the "AN END" deep-web page by OSINT** | Unreachable **by construction**: its address is gated behind solving pages 0–54. No retrievable in-scope Tor-v2 corpus exists; organised hashcat efforts report zero matches as recently as 2025-10-29. | `analysis/anend_hunt/FINDINGS.md` |
| **CT-log brute force for that hash** | Non-viable by construction — CT logs hold CA-issued cert domains, not page contents or v2 onions. **More compute does not help.** | `ELIMINATION-LEDGER.md:168` |
| **Transposition-only, fractionation/Polybius/trifid, Hill, homophonic-IoC-preserving substitution, page-on-page keying, differencing/integration, alphabet reordering** | All killed by structural gates. | `ELIMINATION-LEDGER.md`, `research/DEAD_ENDS.md` |
| **PCG, xoroshiro, xorshift128+ as the generator** | **Excluded by date.** Published Aug 2014 / 2014; LP2 was posted January 2014. | `round10/L5-seed32/CENSUS.md` §C |
| **Claiming a solve without a PGP signature** | The community's gating test for any claim is a valid signature from key **7A35090F**. The 2026 Zenodo "complete translation" (AI-generated) is rejected on exactly this basis. | `analysis/KEY-HINT-RESEARCH.md` |

---

## 6. What IS open, ranked by honest prior

**No entry here is likely to succeed.** The prior mass sits on "the pad is external or unseeded,
and there is no recoverable key". These are ranked tails.

1. **The derived-key dictionary (RECON-A B-04/B-05)** — *the one lane the ciphertext provably
   cannot exclude.* Cryptographic keystreams (MD5/SHA-1/SHA-256/SHA-512 chain & counter,
   HMAC-DRBG, AES-CTR, RC4, ChaCha20) from a dictionary of Cicada strings and constants, reduced
   mod 29, under the skip-aware beam. Round 8 swept only *hobbyist* PRNGs; the "incompressible ⇒
   not algorithmically generated" kill has **no power** here, since hash keystreams are
   incompressible by construction.
   **Status: IN FLIGHT as this is written (Round 13, `analysis/round13/B04/`, `B05/`).**
   Its pre-registration is at `round13/B04/PREREG.md`.
   *Verified as of writing:* the **positive control passes**. A planted dictionary-resident seed
   ranks **#1 at −4.186**, reading `THEPRIMESARESACRED…` in clear, against a runner-up of −6.62
   (noise). The narrower G1 gate is on disk and also passes: beam(correct) **−4.170**,
   rigid(correct) −6.835, beam(wrong) −7.349, character recovery 0.989.
   **The sweep result itself is NOT known to me and is not recorded anywhere in this document.**
   Read `analysis/round13/B04/RESULTS.md` (and `B05/`) for the outcome. Do not assume either
   direction.
   *Honest prior: LOW-MEDIUM* — genuinely untested and control-detectable, which is rare here;
   but it requires the author to have used a *guessable* seed, and the dictionary is the whole
   bet.
2. **Finish the 32-bit seed sweep at a corrected threshold** — `PARKED.md` P-2. ~11 h of
   compute; the only blocker was that the old bar was invalid. *Prior: LOW-MEDIUM* — completes a
   finite space rather than opening a new one.
3. **Re-run Round 12 A1 over two pads it never really tested** — `PARKED.md` P-3.
   `DATA/560.13`, the largest authored CicadaOS blob, was recorded LOST; it is now **recovered
   and hash-verified** (`handoff/capsule/RECOVERY-560.13.md`). And cross-checking turned up that
   the `_560.00` A1 actually swept is **truncated by ~40%** against the authoritative ISO copy —
   including in the pad A1 used to build its own positive control and null ceiling. Both are in
   place; neither has been swept. *Prior: LOW* — sibling pads produced nothing above noise; but
   this closes a named lane outright instead of opening one, and it repairs a partially-covered
   negative.
4. **Per-rune vision re-transcription and the haplography audit** — `PARKED.md` P-1 / P-8.
   The clearest "wait for better tooling" item, and P-8 is the cheapest available falsifier of
   the repo's largest load-bearing structure. *Prior: LOW that canonical is wrong; MEDIUM that
   the audit is worth running.*
5. **PHP `mt_rand` and the uncovered generators** — `PARKED.md` P-4. *Prior: LOW overall,
   MEDIUM for PHP specifically* (most plausible 2013 web-puzzle language, with a documented
   MT deviation that makes it unreachable from the swept generators).
6. **The pp49–51 payload's 6 contested bytes** — `PARKED.md` P-7. Cheap to settle by
   enumeration; converts conditional negatives into unconditional ones. *Prior: LOW.*
7. **The unread ornament bands** — `PARKED.md` P-9. 47 catalogued bands nobody has ever read.
   *Prior: LOW*, and beware pareidolia in 1–16 symbols.
8. **Passive monitoring** — `PARKED.md` P-5. Zero cost, and one of its triggers would reopen
   everything.

**And the honest bottom of the distribution:** if the author used `/dev/urandom`, a hardware RNG,
or dice — the *modal* behaviour for someone setting out to build a one-time pad — then **no
search in this list can ever succeed**, and the ciphertext cannot tell you that is what happened.
`round10/L5-seed32/CENSUS.md` §E states this plainly. Any honest ranking has to put a large
chunk of probability there.

### Queryable index

`liber-primus/LEDGER.json` is the machine-readable index of every attempted attack, its
disposition, and its evidence pointer — query it instead of grepping 100+ markdown files.
*(Being generated in parallel with this document by agent H-1; if it is absent when you arrive,
`ELIMINATION-LEDGER.md` and `analysis/round10/RECON-A/REGISTER.md` are the human-readable
equivalents.)*

**Rounds 13 and 14 were mid-sweep as this was written.** Anything in `analysis/round13/` or
`analysis/round14/` may have a result that postdates this document. Check those directories
before trusting §6's ranking.

---

## 7. Thirty-minute quickstart

```bash
# 1. clone and enter                                                    (~2 min)
git clone <this repo> cicada3301 && cd cicada3301/liber-primus
pip install -e .                       # the `lp` core library

# 2. THE TRUST ANCHOR — never skip this                                 (~1 min)
python3 tests/validate.py              # must print: ALL VALIDATIONS PASSED

# 3. check the data capsule is intact                                   (~1 min)
python3 handoff/capsule/verify_capsule.py
#    99+ OK offline. Then, to confirm the outside world still has what
#    is not committed (probes mirrors, downloads nothing):
python3 handoff/capsule/verify_capsule.py --net --only transcription
#    Anything reporting DRIFT means a mirror changed bytes — do not compare
#    your numbers to this repo's until you have reconciled it.

# 4. fetch what is gitignored                                           (~5 min)
python3 data/fetch_sources.py          # third-party transcription lineages
#    Page images (data/relikd/) and corpora: see the mirrors recorded per item in
#    handoff/capsule/MANIFEST.json. The derived scorer (data/english_quadgrams.txt)
#    IS committed — prefer it over rebuilding, or every threshold here shifts.

# 5. confirm you have the right target                                  (~1 min)
python3 -c "import sys; sys.path[:0]=['src','analysis/round11']; \
import lib_numchannel as nc; print(len(nc.unsolved()))"
#    must print 12956

# 6. run the benchmark / positive control BEFORE your own attack        (~5 min)
python3 -m pytest benchmark/ -q        # (or, if benchmark/ is incomplete:)
python3 analysis/round12/D3/pc_derivedkey.py
#    You are looking for the planted signal recovering at ~-4.2 while the wrong
#    key stays ~-7.3. If your instrument cannot do that, it cannot produce a
#    meaningful negative.

# 7. query what has already been tried — do this before designing anything
python3 -c "import json; d=json.load(open('LEDGER.json')); print(len(d))"
#    (or read ELIMINATION-LEDGER.md and analysis/round10/RECON-A/REGISTER.md)

# 8. run your first attack, correctly                                  (~10 min)
python3 lp_try.py --key YOURKEY        # quick hypothesis test, with a sanity gate
python3 lp_try.py --selftest           # proves the scorer separates English from ciphertext
```

**Then, before you run anything real:**
1. Write a `PREREG.md`: hypothesis, exact search bound, null model, pass/fail threshold.
2. Plant a known key of your family, encipher known English through the anti-repeat filter,
   and confirm your decoder recovers it.
3. Only then point it at the real 12,956 runes.
4. Report `null_mean`, `null_max`, and your margin — not just your best score.

---

## 8. What would reopen the case

The case is not closed, but it is *quiet*. Three things would genuinely change it:

1. **A new Cicada release signed by PGP key `7A35090F`.** No authentic signed message has
   appeared since **April 2017**. This is the community's gating test for authenticity and the
   only channel through which a key or a new stage could legitimately arrive.
2. **A reproducible page solve accepted by CicadaSolvers** — a stated key and method that
   another party can re-run to the same plaintext. Note the standard: *reproducible*. Unsigned
   "complete translations" (including the 2026 Zenodo/AI one) do not meet it and are rejected.
3. **The private pad surfacing** — the external key material itself, via the "AN END" page,
   an author disclosure, or an archive nobody has looked in. If the keystream is a true external
   pad, this is the *only* thing that solves it.

Two lesser triggers, worth a passive watch at zero cost: a non-zero match appearing in
`cicada-solvers/Cicada-DWH-HashcatAttempts`, or a hit logged by `tweqx/3301-hash-alarm`.

---

## 9. Where things are

| what | where |
|---|---|
| **Run this first** | `tests/validate.py` |
| Frozen data capsule + hashes + mirrors | `handoff/capsule/MANIFEST.json` |
| Capsule integrity checker | `handoff/capsule/verify_capsule.py` |
| Capability-blocked queue, with unpark conditions | `handoff/PARKED.md` |
| The `DATA/560.13` recovery record | `handoff/capsule/RECOVERY-560.13.md` |
| Everything tried and why it died | `ELIMINATION-LEDGER.md` |
| Machine-readable index of the above | `LEDGER.json` |
| Un-executed leads mined from every doc | `analysis/round10/RECON-A/REGISTER.md` |
| The verdict correction that matters most | `analysis/round12/D3/RESULTS.md` |
| The decoder you must use | `analysis/campaign18_skip/skipdecode.py` |
| Data/null/scorer harness | `analysis/round11/lib_numchannel.py` |
| Threshold calibration | `analysis/round10/L5-seed32/nullcurve.py` |
| Shared positive-control harness | `benchmark/` |
| Machine-readable corpus | `dataset/liber_primus.json` |

---

_A closing note on tone. This repository contains a great deal of failed work, and that is its
value. The individual negatives matter less than the discipline that produced them: every claim
here is supposed to be traceable to a measurement, every negative to a control that could have
detected a positive, and every threshold to a value written down before the run. Where this
project failed at that — and §3 documents where — the failures were caught by red-teaming its own
conclusions rather than by anyone outside. If you take one thing from this repo, take the method,
not the map._
