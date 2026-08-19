# The solver benchmark — validate your instrument before you trust its silence

_For anyone attacking Liber Primus, or any cipher with a filtered keystream. Written for a
reader who has better tools than 2026 had._

```bash
python3 -m pytest liber-primus/benchmark/ -q      # 7 gates, ~2 minutes
python3 liber-primus/benchmark/gates.py           # same, with a readable table
python3 liber-primus/benchmark/null.py            # scale-corrected thresholds
```

## The one rule

> **A null result from an instrument that has never been shown to recover a *planted*
> signal is not a negative. It is an unknown wearing a negative's clothes.**

Almost all published work on Liber Primus violates this. Someone runs an attack, sees no
English, and writes "ruled out". They never checked whether their machinery *could* have
found the answer.

This is not a hypothetical concern here. It happened, at scale, in this repository:

**Every seed sweep before Round 12 used rigid alignment.** Under the pinned anti-repeat
filter, rigid decoding scores the **correct** key at **−6.835** — squarely in the noise
band — while the skip-aware beam recovers it at **−4.170** with 98.9% rune accuracy.
Round 8 alone ran **2.52 × 10⁹ decodes** through a decoder that could not have succeeded
even if its hypothesis had been right.

`test_rigid_scores_correct_key_as_noise` reproduces that in about two seconds. Run it
before you believe anyone's negative, including ours.

## The gates

| gate | what it plants | why it exists |
|---|---|---|
| `running_key/no_filter/rigid` | plain running key, no filter | baseline — if this fails, stop and fix your setup |
| `running_key/skip_filter/beam` | running key, **key-skip** filter (key desyncs) | the mechanism Campaign XVIII validated against |
| `running_key/rewrite_filter/beam` | running key, **value-rewrite** filter (output corrupted, key stays synced) | the mechanism Campaigns X/XI actually pinned. RECON-B/B-16 flagged that the decoder had never been checked against it |
| `derived_sha256_ctr/skip/beam` | SHA-256 counter keystream from a short seed | **the one hypothesis class the ciphertext cannot exclude.** If your instrument fails this, any "the pad is not derived" claim you make is empty |
| `seeded_prng/skip/beam` | seeded PRNG pad | the family Round 8 swept — rigidly |
| `rigid_vs_beam/DIAGNOSTIC` | same ciphertext, same correct key, two decoders | the fact above, made mechanical |
| `shuffled_plant/NEGATIVE` | a plant with its order destroyed | negative direction — guards against a scorer that rewards letter frequency rather than structure |

Each gate asserts **both** directions: the plant is recovered **and** a wrong key stays in
noise. A benchmark that can only pass is decoration.

## Validating your own decoder

```python
from gates import run_all
run_all(decoder=my_decode)
# my_decode(C, K, sign=-1) -> {"score": float, "translit": str, "plain_idx": [int]}
```

`score` must be a per-symbol English log-probability (negative; higher is more English).
Return `plain_idx` if you can — see the recovery-metric trap below.

## Thresholds: `null.py`

A fixed score bar is **not** scale-free. The maximum of N draws from a null grows like
`mu + beta*(ln N + gamma)`. Sweeping millions of wrong keys and reporting the best as
"close" is the order statistic doing its job.

```python
from null import threshold_for, report
threshold_for(n_trials=6_200_000)          # the bar you should actually use
report(n_trials=6_200_000, best_score=-5.885)   # adjudicates it for you
```

**A calibration trap, found while building this.** The obvious way to estimate `beta` is
from the null's standard deviation (`sd = beta*pi/sqrt(6)`). For this statistic that is
**wrong by 2.5×**, because the beam-decoder score distribution is left-skewed and bounded
above — its bulk spread says nothing about its upper tail. The bulk estimate would have
predicted a best-of-1.3M null at −4.9 and **declared an entire null sweep a hit**.

Fitting from two real order statistics instead (a 200-draw null and a 1,385,600-decode
sweep) gives `beta = 0.0725`, which then predicts out-of-sample:

| sweep | N | predicted E[max] | observed |
|---|---|---|---|
| B-04 stage B | 1,290,240 | −6.190 | **−6.129** |
| B-04 stage C | 3,548,160 | −6.116 | **−5.885** |

**Calibrate an extreme-value bar from extreme values, never from the bulk.** If you have no
order statistics, run a small null at two very different N and fit the slope. It costs
minutes.

## The recovery-metric trap

Measure recovery on **rune indices**, not on the transliteration string. Seven of the 29
runes expand to two characters (`TH EO NG OE AE IA EA`), so one wrong rune shifts the whole
string and makes a 98.6%-correct decode look 32% correct. That mistake produced a false
FAIL in these very gates before it was caught, and it is exactly the kind of thing that
turns a real signal into a discarded one.

## The method, in four lines

1. **Pre-register** — hypothesis, search bound, and pass/fail threshold, written *before*
   running. A bar chosen after seeing the scores is a story, not a test.
2. **Plant and recover** — prove the instrument works on a known answer first.
3. **Match your null** — size-matched, histogram-preserving, and scale-corrected for the
   number of trials you actually ran.
4. **State your power** — not "we found nothing", but "we found nothing, and we would have
   detected anything above X". Only the second form saves the next person any work.

## Reusing this outside Liber Primus

`null.py` is dependency-free and problem-agnostic; lift it as-is. `plant.py` and `gates.py`
are specific to a mod-29 filtered-keystream cipher, but the *shape* generalises to any
problem where you are about to claim a negative: build a synthetic instance with a known
answer, run your real pipeline against it unmodified, and refuse to report a null until the
synthetic case comes back positive.
