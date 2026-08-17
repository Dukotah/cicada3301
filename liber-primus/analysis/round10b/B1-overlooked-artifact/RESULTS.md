# Lane B1 — RESULTS: "the overlooked variable"

**Verdict: NEGATIVE, with a positive by-product.**
The owner's thesis, in its *keyword / keystream* form, is now refuted **empirically and
period-correctly** — not by an information-theoretic argument. And the refutation does not
rest on this lane's sweep: it rests on a measurement of **the author's own ciphertext**.

---

## 0. Headline

| | |
|---|---|
| Artifact-derived keys fed (never previously fed to LP2) | **168 alphabetic + 16 numeric** |
| Decodes, rigid arm | ~1.0 M (55 pages × 168 keys × 2 signs × 2 Atbash × ≤12 phases) + keyless 29-shift baseline |
| **Real LP2 best score** | **−6.306** |
| **Null control best** (per-page shuffled LP2, identical grid) | **−6.065** |
| Hits above the pre-registered break bar (−5.2) | **0 real, 0 null** |
| Interrupter-beam arm, real vs null | **−6.375 vs −6.388** (indistinguishable) |
| Positive controls | **3/3 PASS** |
| **The real ciphertext scores WORSE than shuffled ciphertext** | Δ = **−0.24** |

The last row is the decisive one. Under the pre-registered rule, a real-sweep best that
does not exceed the null max is a negative *regardless of its absolute value*. Here it does
not merely fail to exceed it — it falls below it.

---

## 1. Positive controls (the gate; run before any negative was trusted)

**PC-A — rig level.** `python tests/validate.py`, verbatim:

```
PASS  Runes - 01.jpg   4/4 words  score= -4.48  via atbash+shift+0
PASS  05.jpg           3/3 words  score= -4.98  via shift+0
PASS  06.jpg           3/3 words  score= -4.13  via atbash+shift+3
PASS  03.jpg           4/4 words  score= -4.34  via vigenere DIVINITY (+7 interrupters)
PASS  14.jpg           4/4 words  score= -4.24  via vigenere FIRFUMFERENFE (+2 interrupters)
=== ALL VALIDATIONS PASSED — rig reproduces known solves. ===
```

**PC-B — harness level, on REAL Cicada ciphertext.** The B1 sweep itself (not `attack.py`)
was pointed at the two solved Vigenère pages with the true key hidden inside the 168-key
artifact list:

```
PC-B 03.jpg: rank1 key=DIVINITY       score=-4.344  -> PASS   (rank2 EEDITION @ -6.780, margin 2.436)
             WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOALLTHNGS...
PC-B 14.jpg: rank1 key=FIRFUMFERENFE  score=-4.243  -> PASS   (rank2 @ -6.936,  margin 2.693)
             ACOANDURNGALESSONTHEMASTEREXPLAINEDTHEITHEIISTHEUOICEOTHECIRCUM...
```

**PC-C — planted signal, artifact key.** English plaintext enciphered under the 2013 boot-screen
string `THEKEYISALLAROUNDYOU` exactly as the author enciphered page 03 (Vigenère, sign −1,
six ᚠ interrupters spliced in), then dropped into the sweep:

```
PC-C planted artifact key: rank1=THEKEYISALLAROUNDYOU score=-4.218 -> PASS
     THECUICCMORNINGLIGHTFELLUPONTHEOLDSTONEWALLANDTHETRAUELLERCNEW...
```

**The instrument finds an artifact-derived key when one is there, at −4.2, with a >2.4
margin over every wrong key.** Every negative below is therefore load-bearing.

A calibration fact worth recording: against the author's *real* solved pages, the 167
**wrong** artifact keys top out at **−6.78 / −6.94**. That is the same band the real
unsolved pages produce (−6.31). The unsolved pages behave exactly like solved pages
attacked with the wrong key — no partial signal anywhere.

---

## 2. What was fed (the gap list, actually used)

Source of record: the locally-held verbatim scream314 archive
`analysis/armada_osint/artifacts/raw/{2012..2017}.md` (149 KB), cross-read against PA-3's
inventory §G. Builder: `b1_keys.py` (each key carries a provenance string).

**Tier-3 prose never used as a key** — the 2013 boot screen `The key is all around you.`;
the telnet/TCP-spec command vocabulary (`RAND QUINE BASE29 CODE KOAN DH NEXT GOODBYE`,
`WELCOME OK ERROR DATA GOODBYE`); the **KOAN text itself** (`SOLONGASYOUCANNOTGOBEYONDTHEMOUNTAIN`,
`WHATAFINEMOUNTAINTHISIS`, `WHATISTHEWAY`); the **19 test questions** and their answer
options (`SELFREFERENTIAL`, `STRANGELOOP`, `GAMERULE`, `INDETERMINATE`, `MEANINGLESS`,
`THEREISNOTRUTH`, `ALLTHINGSARETRUE`, `THISSENTENCEISFALSE`, `YOUCANNOTSTEPINTOTHESAMERIVERTWICE`,
`IAMTHEVOICEINSIDEMYHEAD`, the lake/reflection answer); the **2012 phone recording wording**
(`VERYGOODYOUHAVEDONEWELL`, `THEREARETHREEPRIMENUMBERSASSOCIATEDWITHTHEORIGINALFINALJPG`);
the **2012 MIDI plaintext** (`VERYGOODYOUHAVEPROVENTOBEMOSTDEDICATED`) and its per-solver
word list (`GARDENBALLHOUSECATSHOREBACKHEADGALON`) and hint
(`LETTHECHORUSBEYOURGUIDETOTHEDEPTHS`); the 2014 onion prose (`FOREVERYTHINGTHATLIVESISHOLY`,
`GOODWORK`, `ULTIMATETRUTHISTHEULTIMATEILLUSION`, `JOINUSAT`); `GODELESCHERBACH`; the
2014 UA strings; the 2016 message clauses; `BEWAREFALSEPATHS`; `CICADAPG`.

**Filenames / identifiers never used** — `PRIMEECHO`, `SPLASH`, `CICADOS`, `FOLLY`, `WISDOM`,
`HABITRES`, `THEINSTAREMERGENCE`, `INTERCONNECTEDNESS`, `GEMATRIAPRIMUS`.

**All 18 onion addresses 2012–2014** with digits stripped — including the LP host
`ky2khlqdf7qdznac` — never fed as key material anywhere in the repo.

**Tier-2 number sequences never used as keystreams** — the 7 poster access codes
(JD:3789 … NR:2911), the Dataset/Offset triplets, the 7 GPS coordinate digit strings, the 7
poster phone numbers, the SSSS share hex (both as digits and as its a–f letters), the 2013
twitter handle `1231507051321`, the reactivation-tweet parameters, the 2012 book-code
number list, `Port 5243`, the onion7 `133`/`331`/Last-Modified numbers.

**Plus** an automatic sweep of every ALL-CAPS token and backtick-quoted identifier in the
2012–2017 archive, to satisfy the lane's "every key-shaped string" instruction rather than
only the curated ones.

**Novelty, measured not asserted.** The prior keyword sweep
(`campaign18_skip/armada2/keywords_skip.py`) holds exactly **623** keyword literals across
its five lists. Overlap with B1's set is **7** (`CICADA`, `ENCRYPTED`, `LIBERPRIMUS`,
`MESSAGE`, `MOUNTAIN`, `WELCOME`, `WISDOM`). **161 of 168 B1 keys had never been fed to LP2
by any prior campaign.**

Each key also generated the author's demonstrated **C→F orthography variant**
(`FIRFUMFERENFE` vs `CIRCUMFERENCE`), which is the spelling convention she actually used
and which no prior keyword sweep in this repo applied to artifact strings.

**Operations: the author's demonstrated toolkit only.** Vigenère (sign ±1) × Atbash on/off
× key-phase rotation (≤12) ; keyless Caesar over all 29 offsets × Atbash ; numeric strings
as repeating mod-29 additive keystreams in two readings (digit-as-index, digit-pairs mod 29)
× sign × Atbash × phase ; and the validated ᚠ-interrupter beam
(`lp.solve.find_interrupters`) on every promoted candidate.

---

## 3. Result table

| Arm | Real best | Null best | Real hits > −5.2 |
|---|---|---|---|
| keyless Caesar/Atbash baseline | −6.756 | −6.895 | 0 |
| Vigenère, artifact keywords | **−6.306** | **−6.065** | 0 |
| numeric artifact keystreams | (no improvement) | (no improvement) | 0 |
| ᚠ-interrupter beam on top-40 | −6.375 | −6.388 | 0 |

Real top-5 (all gibberish):

```
-6.306  p50  WORKING                  vigenere sign+1 atb0 ph4     [auto-extracted]
-6.375  p49  IAMTHEVOICEINSIDEMYHEAD  vigenere sign-1 atb1 ph8     [2013 test questions]
-6.476  p32  THEINSTAREMERGENCE       vigenere sign-1 atb1 ph5     [761.mp3 ID3 title]
-6.538  p49  THEWAY                   vigenere sign-1 atb1 ph2     [2013 telnet KOAN]
-6.609  p49  ALLAROUNDYOU             vigenere sign+1 atb0 ph7     [2013 boot screen]
```

Null top-2, for scale: `-6.065 MIDISCV`, `-6.383 PAMJOPGRICDFDI`. The null's leaders are
the same *kind* of string as the real sweep's leaders. There is no structure being found on
either side — the ranking is an artifact of key length and letter distribution.

---

## 4. Skip-aware arm (PA-3 caveat I)

PA-3 warns that a rigid additive test is the wrong model under a soft anti-repeat rewrite,
and requires the Campaign XVIII beam. That arm was run — the beam and its planted-key gate
were imported **verbatim** from `analysis/campaign18_skip/armada2/keywords_skip.py`, no new
solver written. See §6 for its numbers.

---

## 5. H3 — the conflation audit, and the lane's real finding

Full output: `CONFLATION-AUDIT.txt`. Reproduce: `python b1_conflation_audit.py`.

The lane brief suspected the repo had killed short semantic keywords using an argument that
only covers long running keys. **It has not.** Two independent kills exist and each is
correctly scoped:

- **KILL-1** (Round 7 / Campaign IV): a *full-length natural-language running key* injects
  ~3.3% doublets. Scope: long keys.
- **KILL-2** (`analysis/DOUBLET-INVESTIGATION.md` §2, table row **"short Vigenère (len 8)
  — 3.44%"**): a *short repeating keyword* injects ~3.44% doublets. Scope: short keywords.
  This row is a separate measurement, not an extension of KILL-1.

So the class is not wrongly declared dead. But KILL-2 was a simulation against synthetic
English. **This lane upgrades it to a measurement against the author's own output**, which
is the period-correct form of the argument and is new:

| page | how the author made it | doublets |
|---|---|---|
| 03.jpg | Vigenère **DIVINITY** + interrupters | 14/393 = **3.56%** |
| 14.jpg | Vigenère **FIRFUMFERENFE** + interrupters | 9/318 = **2.83%** |
| Runes-01 | Atbash, keyless | 5/183 = 2.73% |
| 05.jpg | plaintext / shift | 7/156 = 4.49% |
| 06.jpg | Atbash + Caesar 3 | 14/741 = 1.89% |
| **all solved** | **the demonstrated toolkit** | **49/1791 = 2.74%** |
| **LP2 0–54** | ? | **86/12901 = 0.67%** |

If LP2 0–54 had been made with the toolkit that demonstrably made the solved pages, it would
carry **353 ± 18.5** doublets. It carries **86**. One-sample **z = −14.41**; the conservative
two-proportion test (which pays for the small 1,791-rune reference sample) gives
**z = −8.60** vs all solved pages and **z = −7.48** vs the two keyword-Vigenère pages alone.

**And it survives the tightest possible reference.** Under a *short* repeating keyword of
period P, `k[i] == k[i-1]` at (P−1)/P of positions, so `c[i] == c[i-1]` exactly when
`p[i] == p[i-1]` there: a keyword-Vigenère ciphertext **inherits** most of its doublets
from the plaintext. So the correct *floor* on the expected LP2 rate is not the random 3.45%
but the author's own **plaintext** doublet rate. Recovered from her substitution-class solved
pages, that is **26/1080 = 2.41%** — expected 311 ± 17.4, observed 86, **z = −12.90**
(two-proportion **z = −6.16**, p ≈ 4 × 10⁻¹⁰).

Every reference — random floor, her solved ciphertext, her solved ciphertext's 2σ lower
bound, and her own plaintext — excludes LP2 0–54 from the keyword construction.

**This is the lane's actual result, and it is stronger than the sweep.** It says: *no key
whatsoever — artifact-derived, literary, numeric, or otherwise — can be the answer under the
author's demonstrated hand-scale toolkit, because that toolkit leaves a doublet fingerprint
on her own pages that LP2 0–54 does not have.* The owner's thesis is refuted at the level of
the **operation**, not the level of the **key**, and refuted with a hand-checkable count of
identical adjacent runes rather than an information-theoretic claim about pads.

The corner this does **not** close: a keyword *plus a post-encipherment anti-repeat rewrite*.
That composite is not the author's demonstrated toolkit (she never used it on any solved
page), and it is the one thing Campaign XVIII's skip beam exists to test — which is why §4/§6
matter.

---

## 6. Skip-beam numbers

Logs: `RUN-skip.log`, `skip_stdout.txt`, `b1_skip_results.json`
(18-page run preserved as `b1_skip_results_run2_18pages_112keys.json`; an earlier
8-page/151-key pass is kept as `b1_skip_results_run1_8pages_151keys.json`).

**Gate first (this arm's positive control).** The Campaign XVIII planted-key gate was run
before the sweep and re-run independently during verification; it passed identically both
times. It plants `CIRCUMFERENCE` under an ~83% doublet-skip filter (resulting ciphertext
doublet rate 0.47%, i.e. matched to LP2's regime) and demands that the rigid test *miss* it
while the beam *recovers* it:

```
rigid, correct key+offset : score_norm = -7.017   match =  20.8%   (need < -6.0)
beam,  correct key+offset : score_norm = -4.154   match = 100.0%   (need > -5.0)
beam,  WRONG keyword ctrl : score_norm = -7.363                    (need < -6.0)
GATE RESULT: PASS
```

This is the load-bearing control for §5's open corner. It proves the arm can see a keyword
*through* an anti-repeat rewrite — the exact composite that neither KILL-1 nor KILL-2 binds.

**Sweep.** 112 of the 168 artifact keywords qualify (the beam takes the author's demonstrated
key lengths, 3–14 idx symbols: DIVINITY is 8, FIRFUMFERENFE is 13). 18 unsolved pages on a
stride-3 scaling, real and null (per-page shuffle, seed 20260812), each key × sign × Atbash ×
beam.

| | real | null |
|---|---|---|
| best `score_norm` | **−6.164** (p21, `ERWFFSDVXPMRSK`, sign −1, atb0, off 13) | **−6.248** (p0, `YWYUVRQRAOWAGF`, sign −1, atb1, off 2) |
| confirmed hits (> −5.5) | **0** | **0** |
| screened hits (> −6.0) | 0 | 0 |

**Δ (real − null) = +0.084.** Pre-registered reading: `> +0.5` would be signal, `≤ 0` a clean
negative. +0.084 is inside the null's own spread — the real ciphertext and its own shuffle are
indistinguishable under the beam. Per-page bests span −6.16 to −6.50 with no page separating
from the pack, and the leaderboard mixes real artifact prose (`THEREISNOTRUTH`, `WHATISTHEWAY`,
`INDETERMINATE`, `FOLLYWISDOM`) with auto-extracted noise strings (`ERWFFSDVXPMRSK`,
`QWMHFHZVUQFMF`) — the ordering is key length and letter distribution, not structure.

**Verdict for this arm: NEGATIVE.** Since the gate proves the instrument recovers a planted
keyword at −4.15 through a doublet filter tuned to LP2's own rate, this closes the composite
corner §5 left open *for artifact-derived keywords*: an artifact keyword plus a
post-encipherment anti-repeat rewrite is excluded, not merely untested.

**Coverage caveats, stated plainly.** (i) 56 of the 168 keys fall outside the beam's 3–14
length window and were tested only in the rigid arm. (ii) 18 of 55 pages, stride-3. A full
55-page re-run is scripted (`b1_skip_arm.py --pages 55`) and was launched during verification.
On the pages the two runs share it is **bit-for-bit reproducible** — p0 −6.443, p3 −6.397,
p6 −6.408, p9 −6.364, identical to `RUN-skip.log` — and the newly-covered pages land in the
same band (p1 −6.347, p2 −6.244, p4 −6.307, p5 −6.364, p7 −6.305, p8 −6.329), with no page
approaching the −5.5 confirm bar. The extension is completeness, not a live avenue. It is
resumable and its output goes to `skip_stdout_full55.txt`.

---

## 7. Honest scope limits

- This lane tests artifact strings as **keys/keystreams under the author's demonstrated
  operations**. It does **not** test PA-3's **Tier 1** — the author's own published binary
  pad files (`DATA/_560.00`, `560.13`, `560.17`, `twitter.txt`, the raw `761.mp3` /
  `Interconnectedness.mp3` bytes). Those are not held locally and are a different lane.
  *However*, §5's z = −14.41 is key-agnostic: it excludes the **operation**, so a Tier-1
  binary pad fed through plain additive Vigenère is excluded by the same measurement. Tier 1
  survives only in composite form (pad **+** anti-repeat rewrite).
- The ≤12 key-phase cap means keys longer than 12 were not rotated to all phases. For a
  repeating key, phases > period are redundant; for keys of length 13–40 this leaves some
  phases untested. Prior art already covers arbitrary offsets for keys of this class
  (campaign18 `prefilter`), so this is a completeness gap, not an open avenue.
- The auto-extraction pulls ALL-CAPS/backtick tokens from a **community-written** archive,
  so some keys are community vocabulary rather than author-emitted. This inflates the
  multiple-comparisons denominator against us (more chances to false-positive) and is
  handled by the null control.
- ~112 keytexts, ~620 keywords and 874 numeric streams were already dead before this lane;
  the 168+16 here are the never-fed complement, not a re-run.

## 7b. Verification pass (second session, after the network outage)

The original run was cut off by a network outage before §6 was written. Everything above was
re-verified from disk rather than trusted:

| Checked | How | Outcome |
|---|---|---|
| PC-A | `tests/validate.py` re-run | 5/5 PASS, identical scores (−4.48/−4.98/−4.13/−4.34/−4.24) |
| PC-B, PC-C | `b1_sweep.py --pc` re-run end to end | identical to RUN.log, to 3 dp, incl. margins 2.436 / 2.693 |
| §5 conflation audit | `b1_conflation_audit.py` re-run twice | byte-identical output; every z reproduces |
| §5 headline doublet stat | **independent recount** off `run_stats.load_pages`, not the audit's own code path | 86/12901 = 0.6666%, z = −14.41 vs 2.74%, z = −17.32 vs random — exact match |
| KILL-2 citation | `analysis/DOUBLET-INVESTIGATION.md` line 41 | verbatim row `\| short Vigenère (len 8) \| 3.44 \|` — the citation is real and correctly scoped |
| Novelty claim | recomputed overlap of B1 keys vs `campaign18_skip/armada2/keywords_skip.py` literals | 168 keys, overlap **7**, **161 novel** — exact match |
| Round-4 non-redundancy | `research/DEAD_ENDS.md:131` | Round 4 killed **three specific numeric/hash cribs** (P.S. 130-digit, 2013 cookies, missing-primes), not the alphabetic artifact-prose corpus. B1 does not re-dig it. |
| Skip gate | `keywords_skip.gate()` re-run | PASS with identical stats (−7.017 / −4.154 / −7.363 / 100%) |
| Sweep JSON vs prose | field-by-field diff of `b1_results.json` against §3 | every figure in the tables matches the stored run |

No number in this document changed under verification.

## 8. Reproduce

```
cd liber-primus
PYTHONUTF8=1 python tests/validate.py                                              # PC-A
PYTHONUTF8=1 python analysis/round10b/B1-overlooked-artifact/b1_sweep.py --pc      # PC-B, PC-C
PYTHONUTF8=1 python analysis/round10b/B1-overlooked-artifact/b1_sweep.py --real
PYTHONUTF8=1 python analysis/round10b/B1-overlooked-artifact/b1_sweep.py --null
PYTHONUTF8=1 python analysis/round10b/B1-overlooked-artifact/b1_conflation_audit.py
PYTHONUTF8=1 python analysis/round10b/B1-overlooked-artifact/b1_skip_arm.py --pages 8
```
