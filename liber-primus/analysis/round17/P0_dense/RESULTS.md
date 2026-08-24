# Round 16 — Lane P0: dense offset re-sweep of the author's CicadaOS pads

**VERDICT: NEGATIVE** — at the coverage stated below, and only there.

| | |
|---|---|
| Best `score_norm` over the whole lane | **−6.7685** (`560.13`, `lo_nibble`, sign +1, offset 15,558,717) |
| Pre-registered HIT bar | `score_norm ≥ −5.5` **and** `≥ null_max + 0.5` |
| Margin below the bar | **1.27** below −5.5; the best row beats its own null by **+0.22**, not the required +0.50 |
| Scale-corrected bar, `benchmark/null.threshold_for(2,900,403,446)` | **−5.3386** — *stricter* than the fixed bar, and missed by **1.43** |
| Offsets scanned (ms=3 primary pass) | **2,900,403,446** |
| Effective coverage, **per-pad measured** survival | **1,545,470,711** |
| With the `nibbles` builder added | 3,911,819,734 scanned → **2,084,401,212** effective (mean rate **0.533**) |
| A1's coverage on the same pads, for comparison | **8 offsets per keystream variant** |

> **The round's flat ×0.625 survival discount is not used here.** I measured the prefilter's
> retention by planting in each real pad (24 plants per pad) and every pad above 1 MB came in
> *below* 0.625. Coverage below is discounted at each pad's own measured rate, which costs
> this lane ~360 M effective offsets versus quoting the round constant.

Nothing in this lane reached the bar. No decode was read for meaning; every number here comes
from `score_norm` and a shuffle null.

---

## 1. What this lane attacked

Round 12 front A1 fed six CicadaOS blobs — including the 118,818,811-byte `DATA/560.13` — to
the skip-aware beam decoder and returned NEGATIVE. It walked an **eight-offset ladder** per
keystream variant (`0, 1000, 5000, 20000, 100000, 1e6, 1e7, 5e7`). On `560.13` that is
8 / 118,818,811 = **6.7 × 10⁻⁸** of the offset space.

A1's verdict is sound *as a verdict on those eight offsets*. It was never a bound on the pad.
This lane replaces the ladder with `lib_padsweep.dense_scan`, which scores **every** offset.

Everything downstream of the scan is A1's, unchanged, so the numbers are directly comparable
to `round12/A1/results_560_13.json`: `beam_w=120`, `max_skip=3`, `head=400`, A1's `score_norm`
scale, A1's shuffle null at n=200.

## 2. Controls relied on

A negative from an unvalidated instrument is not a negative (AGENTS.md lesson 1). Four
controls stand behind this one.

**(a) Survival gate — `lib_padsweep.control()`, re-run on this box, PASS.**
Eight keystreams planted at random deep offsets, enciphered under the anti-repeat filter:
the beam recovered **8/8 at 100 % of runes** (−4.212); the dense prefilter retained the true
offset in **5/8** (ranks 0, 0, 2, 0, 0) → the round's constant, **0.625**. It is a *power*
limit, not a soundness limit — the beam recovers 8/8 wherever the prefilter hands it the
offset.

**That constant is not used for this lane's coverage, because it was measured in a 1 MB
blob.** Retention inside a fixed keep window is a *rank* statistic, so it depends on how many
offsets compete. `control_at_scale.py` measures it per pad — **24 plants in each real pad** —
under the criterion this pipeline actually applies (`rank < 40`, the top 40 per sign that
`sweep.py` escalates), with `rank < 400` reported alongside for comparability with the round
constant and with lane P2:

| pad | bytes | competing offsets | survival, rank<400 | **survival, rank<40** | beam recovery |
|---|---:|---:|---:|---:|---:|
| `tmp_folly` | 3,368 | 3,344 | 0.792 | **0.750** | 24/24 |
| `usr_local_bin_prime_echo` | 12,248 | 12,224 | 0.667 | **0.583** | 24/24 |
| `DATA_560.17` | 1,183,811 | 1,183,787 | 0.500 | **0.500** | 24/24 |
| `DATA__560.00.iso-authoritative` | 3,992,970 | 3,992,946 | 0.375 | **0.375** | 24/24 |
| `DATA_560.13` | 118,818,811 | 118,818,787 | 0.542 | **0.542** | 24/24 |

Two honest readings of that table, and they pull in different directions:

1. **Every pad above 1 MB is below the round's 0.625**, so quoting the flat constant would
   have overstated this lane's coverage. Using the measured rates costs ~360 M effective
   offsets and that is the correct trade.
2. **The decay is not monotone in pad size, and I will not claim it is.** `560.13` at 118.8 MB
   measured **0.542**, *higher* than the 4 MB `_560.00` at 0.375. With 24 trials the standard
   error is ≈ 0.10, so those two differ by ~1.2 SE — noise, not a trend. The defensible
   statement is that survival is **≈ 0.4–0.55, flat, for every pad at or above 1 MB**, not
   that it decays steeply with size. My 0.542 at 118.8 MB is consistent with P2's 0.500 at
   95 MB; my 0.375 at 4 MB is well below P2's 0.875 at 6.4 MB, which suggests the rate is
   driven at least as much by pad statistics as by pad size.

Beam recovery is **24/24 on every pad**, so nothing here threatens soundness: where the
prefilter delivers the offset, the decoder recovers the plaintext. Roughly one true offset in
two was scanned but would not have survived to the beam even had it been correct.

**(b) Skip-budget control on the REAL pads — `control_skip.py`, 20 trials per pad.**
Lane P1 found A1's `max_skip=3` underpowered on a pad with long constant byte runs (18.4 %
zero bytes), because a constant key symbol makes a forced skip a no-op and the filter burns
several in a row. That is a property of the *pad*, so I measured it on mine rather than
inheriting it:

| pad | zero frac | adj-equal frac | max constant run | max consecutive skip observed | recovered ms=3 | recovered ms=8 |
|---|---:|---:|---:|---:|---:|---:|
| `DATA_560.13` | 0.004 | 0.004 | 4 B | 2 | **20/20** | **20/20** |
| `DATA__560.00.iso-authoritative` | 0.004 | 0.004 | 3 B | 2 | **20/20** | **20/20** |
| `DATA_560.17` | 0.004 | 0.004 | 3 B | 2 | **20/20** | **20/20** |
| `usr_local_bin_prime_echo` | 0.000 | 0.052 | 3 B | 2 | **20/20** | **20/20** |
| `tmp_folly` | 0.005 | 0.005 | 2 B | 2 | **20/20** | **20/20** |

P1's failure mode does not bite here. These blobs are high-entropy — adjacent-equal byte rate
0.4 % is chance (1/256), the longest constant run anywhere in 118 MB is **4 bytes**, and no
byte sits in a run of ≥ 8. A1's `max_skip=3` was adequate *for these pads*, and that is now
measured rather than assumed.

**(c) The `max_skip=8` pass, run anyway — and it is bit-identical.**
I re-escalated every survivor at `max_skip=8` with its own null recomputed at ms=8.
**91/91 comparable rows identical, max |Δ| = 0.000000.** The reason is mechanical and worth
recording: `beam_decode` only admits a skip when *every skipped key position would have
reproduced the previous cipher rune* — probability ≈ 1/29 per skipped position. On a
high-entropy pad that validity test, not the budget, is binding, so a budget of 8 buys
nothing. On P1's zero-run pad the same test is trivially satisfiable many times in a row,
which is exactly why the budget bites there and not here. Both numbers are in `results.json`.

**(d) Two consistency checks.** `sweep.py::_assert_window_equiv` asserts, at the start of
every run, that the windowed beam/null wrappers (needed so a 118 M-symbol keystream is not
materialised as a Python list) are bit-identical to `lib_padsweep.escalate` /
`lib_padsweep.null_ceiling`. And this lane's `mod29` shuffle null reproduces A1's published
null exactly — **−6.995** on `_560.00` authoritative (A1: −6.995405944815296) and **−7.037**
on `560.13` (A1: −7.036791950110792).

Per P4: the anti-repeat filter is **machine, not hand-applied** — flat, unscoped, single-lag
at supp = 0.813, with any lag-2..8 suppression above 1.70 % excluded at 95 %. That confirms
the cipher model the beam assumes against the real data, and it raises rather than lowers the
prior on an imported-byte-source pad of exactly the kind this lane sweeps.

## 3. Coverage achieved — stated exactly

Primary pass: **6 builders × {fwd, rev} × {sign −1, +1} = 24 configs per pad**, every offset
scored, top 400 kept per config, top 40 per sign beam-escalated. The cross product completed
on **every pad**; nothing was dropped for time.

| pad file | bytes | configs | offsets scanned | measured survival | effective | best `score_norm` | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| `DATA_560.13` | 118,818,811 | 24 | 2,725,884,690 | 0.542 | 1,476,520,874 | −6.7685 | NEGATIVE |
| `DATA__560.00.iso-authoritative` | 3,992,970 | 24 | 91,605,492 | 0.375 | 34,352,060 | −6.8137 | NEGATIVE |
| `DATA__560.00` | 2,412,544 | 24 | 55,348,856 | 0.375\* | 20,755,821 | −6.8164 | NEGATIVE |
| `DATA_560.17` | 1,183,811 | 24 | 27,154,056 | 0.500 | 13,577,028 | −6.8072 | NEGATIVE |
| `usr_local_bin_prime_echo` | 12,248 | 24 | 257,020 | 0.583 | 149,928 | −6.9588 | NEGATIVE |
| `tmp_folly` | 3,368 | 24 | 76,666 | 0.750 | 57,500 | −6.9227 | NEGATIVE |
| `tmp_wisdom` | 3,368 | 24 | 76,666 | 0.750\* | 57,500 | −6.9227 | NEGATIVE |
| **total** | | **168** | **2,900,403,446** | | **1,545,470,711** | **−6.7685** | **NEGATIVE** |

\* borrowed, and marked as borrowed: `tmp_wisdom` is byte-identical to `tmp_folly`, and
`DATA__560.00` is an exact byte prefix of the authoritative copy. Neither was measured
separately. Quoting the round's flat 0.625 instead would have claimed 1,812,752,154 effective
offsets — **267 M more than this lane actually earned.**

Supplementary passes, both NEGATIVE:

| pass | configs | offsets scanned | effective (measured) | best |
|---|---:|---:|---:|---:|
| `nibbles` builder, ms=3 (P1's true hex-text reading) | 28 | 1,011,416,288 | 538,930,501 | −6.8225 |
| `max_skip=8` re-escalation, null recomputed at ms=8 | 116 | 2,900,237,574 | 1,545,348,396 | −6.7685 |

The ms=8 pass covers **116 of 168 configs, not all of them**, and the shortfall is structural
rather than a time cut: at `max_skip=8` a 400-rune head needs 3,608 key symbols, so the
3,368-byte `tmp_folly`/`tmp_wisdom` and the short `hexchars` streams of the small pads are
too short to decode at all and were skipped. Those 52 configs have an ms=3 result only.

**Grand total, ms=3 distinct hypotheses: 196 configs, 3,911,819,734 offsets scanned →
2,084,401,212 effective at the per-pad measured rates (mean 0.533).** Against A1's 8 offsets
per variant, that is a factor of ~1.5 × 10⁷ more offsets on `560.13` alone.

Two of the seven pad files are not independent, and the totals above do **not** discount for
it: `tmp_folly` and `tmp_wisdom` are **byte-identical** (sha256 `7e5ec097…`), and
`DATA__560.00` is an exact byte **prefix** of `DATA__560.00.iso-authoritative` — its rows
duplicate the authoritative pad's at the same offsets, visible as rows 6/7 and 13/14 of the
table below. Seven files, **six distinct blobs**, five of them distinct at any size worth
counting.

### The recovered `_560.00` tail — a declared gap, now closed and empty

A1 swept a 2,412,544-byte mirror copy of `_560.00`. The ISO's authoritative copy is
3,992,970 bytes, so **1,580,426 bytes — 39.6 % of the real blob — were never in A1's input at
all.** This lane scanned every offset of the authoritative copy: **1,580,402 offsets per
forward byte-builder config lie in bytes A1 provably never saw**, and the reverse variants
read the same bytes from the other end. Four of those tail offsets reached the lane's top 20
(`prime_to_idx` +1 @ 2,564,716 and @ 2,784,486; `hi_nibble` +1 @ 2,426,276; `mod29` −1 @
3,564,931), all in the −6.93 to −6.96 noise band. **The recovered tail produced nothing.**
That is the honest close of the gap A1 declared: not "the tail is unlikely", but "the tail was
scanned at every offset under 24 configs and its best score is 1.4 below the bar".

## 4. Top 20

Ranked by `score_norm` across the primary ms=3 pass. `pre` is the dense prefilter score that
won the offset its escalation; `bar` is the pre-registered HIT threshold.

| # | pad | variant | sign | offset | pre | `score_norm` | bar | head (48 runes) |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | `560.13` | `lo_nibble` | +1 | 15,558,717 | −1.283 | **−6.7685** | −5.50 | `NGBARNEARFERLACITIIFPASTONATMAYUIADNGEOIJETINDEO` |
| 2 | `560.13` | `prime_to_idx` | −1 | 102,759,418 | −1.265 | **−6.7919** | −5.50 | `THJJOELIFYPREACERSNOFPICTIDIGTWEOSJLMNGIHPOEOMPT` |
| 3 | `560.17` | `lo_nibble` | +1 | 493,780 | −1.412 | **−6.8072** | −5.50 | `AEDYETFIRBJEWCIMWGODOESABLTHWIAYBATSTHNETHTAETHI` |
| 4 | `_560.00_auth` | `hi_nibble_rev` | +1 | 725,377 | −1.356 | **−6.8137** | −5.50 | `AESYOBYEAHAFLANTHEIUILHEANAYBBNMTHAELEAJEHMNGWBT` |
| 5 | `560.13` | `byte_scaled_rev` | +1 | 32,212,442 | −1.255 | **−6.8152** | −5.50 | `HETHEYRTHEFFOUJADUNDANYOURUECIACWNLEAROEHIABMMRE` |
| 6 | `_560.00_auth` | `prime_to_idx` | −1 | 972,806 | −1.366 | **−6.8164** | −5.50 | `OEHJYHENDEEFIGNTHERIPEDUTHLPOTTOAEUEOOSFOEIAROYE` |
| 7 | `_560.00_trunc` | `prime_to_idx` | −1 | 972,806 | −1.366 | **−6.8164** | −5.50 | `OEHJYHENDEEFIGNTHERIPEDUTHLPOTTOAEUEOOSFOEIAROYE` |
| 8 | `560.13` | `hexchars` | +1 | 61,885,226 | −1.289 | **−6.8294** | −5.50 | `SPEOFANGESSENDTHCAPECINGOAENEOAECALBWCNGUOPDSWPC` |
| 9 | `_560.00_trunc` | `mod29` | −1 | 972,806 | −1.442 | **−6.8356** | −5.50 | `OEHJYHENDEEFIGNTHORILEDUTHLPOTTOAEUEOOSFOEIAROYE` |
| 10 | `560.17` | `prime_to_idx_rev` | −1 | 138,558 | −1.414 | **−6.8433** | −5.50 | `MJURTHALOCTUFAGYBEGOLLBYDXAERYMUOOAAYIAHHGBEAGEA` |
| 11 | `560.13` | `lo_nibble` | +1 | 117,135,165 | −1.111 | **−6.8630** | −5.50 | `AELARWRINSUDUCNEINCERSAPTFJAYDOMEIARIONGOEWPNGBT` |
| 12 | `560.17` | `prime_to_idx_rev` | −1 | 1,046,946 | −1.458 | **−6.8647** | −5.50 | `THMIWBIAHEPTTHERGNGIOANIAPBYRSTALRSBEOEOMJLRSOTH` |
| 13 | `_560.00_auth` | `prime_to_idx` | −1 | 1,653,285 | −1.435 | **−6.8711** | −5.50 | `OIAEAOELNGEAEANBPXXIEUIDEDSLYATGNTMDSIARSALMCHSI` |
| 14 | `_560.00_trunc` | `prime_to_idx` | −1 | 1,653,285 | −1.435 | **−6.8711** | −5.50 | `OIAEAOELNGEAEANBPXXIEUIDEDSLYATGNTMDSIARSALMCHSI` |
| 15 | `560.17` | `prime_to_idx_rev` | +1 | 400,139 | −1.381 | **−6.8717** | −5.50 | `ARETHSSGCGBEARINGBETEARDENTOCBGEOGNCBLDIARECLOOE` |
| 16 | `560.17` | `lo_nibble_rev` | −1 | 1,150,170 | −1.444 | **−6.8727** | −5.50 | `THEABULIMAOBENMACRIEWBODATHINGINPBWFBLRNGOEGAEHE` |
| 17 | `560.13` | `prime_to_idx` | −1 | 64,834,954 | −1.272 | **−6.8751** | −5.50 | `FFIRAMOITIDUNOESNENGALMORDSTTNFNFFOEOETHEOTNGTOE` |
| 18 | `560.17` | `mod29` | +1 | 1,043,411 | −1.417 | **−6.8918** | −5.50 | `MAEPEAGUTDABLUEJANATDOETHELMATHNGNREJSIAWWIAEOEY` |
| 19 | `_560.00_auth` | `lo_nibble_rev` | +1 | 616,433 | −1.396 | **−6.8941** | −5.50 | `DXUITAEWEOSEOTHUNOTHYHAUSENNOEBORFRIAEDTHTFLSJEO` |
| 20 | `560.13` | `mod29_rev` | +1 | 55,706,999 | −1.280 | **−6.8963** | −5.50 | `EOTHMENCEOXIANUERXIIAEEOTHTHERSXWHDIAJOAECJAEWAA` |

Those heads contain `BEARING`, `PASTON`, `THEYR`, `CAPE`, `SEND` and similar. **They are
noise.** A flat 29-symbol channel emits English-looking fragments constantly; that is exactly
the failure mode AGENTS.md §4 and PREREG kill-rule 3 forbid acting on. The adjudication is
`score_norm` against the null, and every one of these rows sits in the null's own band.

## 5. Scale-corrected threshold (AGENTS.md lesson 3)

A fixed −5.5 bar is invalid at large trial counts. `benchmark/null.threshold_for()` at this
lane's counts, with the repo's tail-calibrated `mu = −7.2517, beta = 0.0725`:

| trial count | what it counts | `threshold_for` | `expected_null_max` |
|---|---|---:|---:|
| 5,554 | beam decodes actually scored on the `score_norm` scale | −5.5000 (floor binds) | −6.5847 |
| 2,900,403,446 | offsets examined by the prefilter, primary pass | **−5.3386** | −5.6302 |
| 3,911,819,734 | offsets examined, all ms=3 passes | **−5.3169** | −5.6085 |

The conservative reading is the largest count: the bar this lane should be held to is
**−5.34**, stricter than the pre-registered −5.5, because the 40 offsets escalated per config
were selected adversarially from 10⁸ by a correlated statistic. **Raw best −6.7685 misses it
by 1.43, and misses the expected null maximum by 1.14.** The verdict does not depend on which
of the three bars is used.

## 6. What this negative does and does not exclude

It excludes one specific thing, and it is worth being precise about how narrow that is.
**Excluded:** that the LP2 keystream is a rigid, contiguous read of one of these six distinct
CicadaOS blobs, starting at any byte offset whatsoever, under any of seven byte→rune mappings
(`mod29`, `hi_nibble`, `lo_nibble`, `byte_scaled`, `prime_to_idx`, `hexchars`, `nibbles`),
forwards or backwards, at either combining sign, decoded with a skip budget the pads
themselves are measured not to exceed. That is a real strengthening: A1 tested 8 points per
variant; this tested every point, and the recovered 39.6 % tail of `_560.00` that A1 never
held is now scanned too. **Not excluded, and not even touched:** any keystream that is not a
contiguous forward or reverse walk of one blob — a stride, an interleave of two files, a
per-page reseed, a concatenation of several blobs in some publication order, or a start offset
inside a file this lane does not have; any byte→rune mapping outside the seven tried,
including a keyed alphabet or an offset added to the mapping; and any pad that is not one of
these six blobs at all. The coverage discount matters as much as the coverage: the prefilter's
retention is **measured at 0.375–0.75 per pad, ≈ 0.4–0.55 for every pad at or above 1 MB**, so
**roughly one true offset in two was scanned but would not have reached the beam even had it
been correct** — the numbers in the table are already discounted for that, and they are the
number of offsets genuinely tested, not the number swept past. Add that the ms=8 pass covers
116 of 168 configs, and that two of the seven pad files are not independent blobs. The honest
one-line form of this result is not "the CicadaOS pads are dead" but: **six distinct CicadaOS
blobs, 196 configs, 3.91 × 10⁹ offsets scanned → 2.08 × 10⁹ effective at measured survival,
best −6.7685 against a −5.5 pre-registered bar and a −5.34 scale-corrected one.**

### Where this sits among the round's lanes

All five public-pad lanes returned NEGATIVE, none within 1.1 of the bar:

| lane | family | coverage | best |
|---|---|---:|---:|
| **P0** (this) | CicadaOS binaries, dense | 3.91e9 offsets, 196 configs | **−6.7685** |
| P1 | Bitcoin block hashes | 1.39e9 offsets, 303,727 blocks | −6.802 |
| P2 | NIST Beacon + RANDOM.ORG | 3.46e9 offsets | −6.811 |
| P3 | RAND digits + Cicada's published bytes | 5.76e9 offsets, 28 pads | −5.679 |

P3's −5.679 is the closest anything came, and it is still short of both the −5.5 fixed bar and
the scale-corrected bar at its own trial count. Mine is the weakest raw best of the four,
which is what an author-supplied-pad hypothesis with no signal in it should look like.

---

## Reproduce

```bash
cd liber-primus/analysis/round16/P0_dense
python ../lib_padsweep.py                 # round survival gate: expect 8/8 beam, 5/8 dense
python control_at_scale.py --trials 24    # per-pad survival: 0.75 / 0.583 / 0.50 / 0.375 / 0.542
python control_skip.py --trials 20        # skip budget on the real pads: expect 20/20 at ms=3 and ms=8
python sweep.py --pads small              # 6 pads, 144 configs
python sweep.py --pads big                # DATA_560.13, 24 configs, 2.73e9 offsets
python sweep.py --pads all --builders nibbles --tag _nib
python sweep.py --pads big --max-skip 8 --reuse-offsets ckpt
python sweep.py --pads small --max-skip 8
python merge.py                           # -> results.json + the tables above
```

Runtime on this box, uncontended: ~50 min for `--pads big`, ~30 min for `--pads small`.
`sweep.py` checkpoints per keystream variant into `ckpt/`, so an interrupted run resumes
without repeating finished variants. Files: `sweep.py`, `control_skip.py`, `merge.py`,
`control_at_scale.py`, `results.json`, per-pass `results_*.json`, `sweep_*.log`,
`control_skip.json`, `control_at_scale.json`.

No HIT was produced, so `verify_solution.py` adjudication was not triggered; had any row
cleared the bar it would have gone to the full 12,956-rune stream and then to
`python liber-primus/verify_solution.py --selftest` before being written down as anything.
