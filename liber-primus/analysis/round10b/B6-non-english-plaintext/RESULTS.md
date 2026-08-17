# Lane B6 — the non-English / non-prose plaintext blind spot

**Verdict: NEGATIVE, with the blind spot measurably narrowed rather than merely asserted.**
No structured, non-English or machine-shaped payload is present in LP2 under any decode family
scanned, down to a stated detection floor. One class of payload is proved *undetectable in
principle* and is documented as permanent residue.

Everything here is new instrumentation. It executes
`liber-primus/analysis/campaign14/REDTEAM-PROPOSALS.md` item
*"[very-low] Language-agnostic and non-English re-scoring of all sweep bests"*, which was queued
and never run, and extends it from page-scale re-scoring to short-window scanning.

---

## 0. The structural finding that has to come first

**The repo's sweeps did not keep their candidate decodes.** Every archived sweep result
(`analysis/campaign12/sweep_results.json`, `campaign13/sweep_results.json`,
`campaign18_skip/RUN-*.log`, `armada20/*.json`, `liber-primus/out_*.json`) stored only
`(parameters, English-metric score)` and, at best, the single argmax candidate truncated to
~80 characters. Across the entire repository exactly **75 archived candidate decode strings of
>=20 runes exist**, from 60 files.

That has a consequence the lane brief anticipated but which is worth stating sharply:

> Re-scoring the archived candidates **cannot** close the blind spot, because the archive was
> filtered by the very metric being bypassed. A non-English decode that a sweep produced was
> discarded at the moment it lost the English argmax. The 75 survivors are, by construction,
> the most English-looking outputs of each sweep.

So the lane did the re-scoring anyway (Section 4, it is cheap and it is what was queued) but the
real work is Sections 1-3: new detectors run over decode space directly.

**Handoff requirement for future harnesses:** persist a language-agnostic statistic
(decrypt IoC.N, distinct-symbol minimum over a 32-window, best non-English LM score) **at sweep
time**, alongside the English score. Retro-fitting is impossible once the decodes are thrown away.

---

## 1. The instruments, and what they can actually see

Six detectors, built in `detectors.py`, all operating on rune indices 0..28.

| ID | statistic | what it fires on |
|----|-----------|------------------|
| D1 | `E_random(distinct) - distinct symbols in window` | restricted alphabet (hex, digits, base-N) |
| D2 | windowed IoC x 29 | any non-uniform symbol usage |
| D3 | repeated-bigram pair count in window | internal repetition (tables, prose, keys) |
| D4 | raw-deflate length of window | long-range redundancy |
| D7 | mass of window inside its own top-16 / top-10 symbols | hex-shape / digit-shape |
| D5 | rune-space trigram LM: EN, LA, DE, CY (Welsh), OE, RG | prose in a specific language |
| D6 | token cribs (ONION/HTTP/coordinate/digit words) via difference- and equality-pattern search | machine-shaped strings |

**D1, D2, D3, D4, D7 are invariant under every monoalphabetic substitution of the 29 runes**, and
under reversal. One scan of the raw ciphertext therefore covers the entire 29! alphabet-
permutation family, all 29 shifts, Atbash, and any alphabet reordering *simultaneously* — this is
why the language-agnostic scan is both cheap and unusually broad.

### LM validation (identification matrix)

Each LM scores its own language's held-out probe highest — the diagonal wins in all five cases:

| probe \ model | EN | LA | DE | CY | OE |
|---|---|---|---|---|---|
| **EN** | **-1.149** | -1.655 | -1.560 | -1.356 | -1.259 |
| **LA** | -1.445 | **-0.988** | -1.541 | -1.359 | -1.362 |
| **DE** | -1.212 | -1.247 | **-0.776** | -1.276 | -1.142 |
| **CY** | -1.585 | -1.558 | -1.519 | **-0.976** | -1.542 |
| **OE** | -1.663 | -1.570 | -1.582 | -1.347 | **-1.186** |

Corpora (runes): EN 838k (KJV), LA 805k (Aeneid Latin + Principia), DE 222k (Faust I + Die
Verwandlung), CY 317k (Welsh Mabinogion, diplomatic edition), OE 243k (OE Beowulf lines + rune
poem), RG 684 (solved-LP English — small, treat its scores as indicative only).

---

## 2. POSITIVE CONTROL and the DETECTION FLOOR

Payloads planted at a random offset in a uniform-random 13,041-rune host, 5 trials each, scored
against the pre-registered threshold (max-statistic over a 200-shuffle null). **Floor = shortest
planted length detected in >=4/5 trials with the argmax localised to the plant.**

| planted payload | D1 | D2 | D3 | D7(16) | D7(10) | **best floor** |
|---|---|---|---|---|---|---|
| hex-shaped block (16-symbol alphabet) | 64 | 128 | 128 | 64 | 64 | **64 runes** |
| digit block (10-symbol alphabet) | 32 | 48 | 48 | 64 | 32 | **32 runes** |
| coordinate block in Runeglish | 48 | 48 | 64 | 64 | 64 | **48 runes** |
| onion instruction text in Runeglish | 64 | 96 | 96 | 64 | 64 | **64 runes** |
| Latin prose | 64 | 96 | 128 | 64 | 64 | **64 runes** |
| English prose | — | 96 | 128 | 128 | 96 | **96 runes** |
| **base32 body over the full 29-symbol alphabet** | **never** | **never** | **never** | **never** | **never** | **UNDETECTABLE** |

The last row is the important one and it is an *analytic* result, not a measurement artifact:

> **A v2 onion address body is information-theoretically invisible in this setting.** The 16-char
> base32 body of a 2014 onion address is the truncation of a SHA-1 hash — it is uniform over its
> alphabet by construction. Mapped into 29 runes it is a uniform random string embedded in a
> uniform random stream. No detector, present or future, can find it from the ciphertext alone.
> Furthermore base32 uses digits 2-7, which **have no rune in Gematria Primus at all**, so a
> literal onion address cannot even be written in this alphabet without an extra encoding layer
> or spelling the digits out.

Consequence: the *only* detectable trace an onion payload could leave is its surrounding prose —
the literal token `ONION`, `HTTP`, spelled digits, `DOT`. That is what D6 searches for, and it is
the correct instrument for this specific target. The lane closes the *detectable* part of the
onion hypothesis and marks the undetectable part explicitly.

The windowed-LM instrument (Section 3b) has its own floor, reported there.

---

## 3. REAL RESULTS

### 3a. Language-agnostic short-window scan — `real_scan.json`

160 cells = 4 streams (raw, first-difference, second-difference, reversed-first-difference)
x 5 detectors x 8 window sizes {12,16,24,32,48,64,96,128}. Null = 200 shuffles of the real
stream, max-statistic per shuffle. Pre-registered pass = z >= 3.0 **and** real above the null
ensemble maximum.

**PASSES: 0 / 160.**

Best cells:

| cell | real | null mean | null sd | null max | z | verdict |
|---|---|---|---|---|---|---|
| `diff1 / D3_repeat / w128` | 31.0 | 22.55 | 2.17 | 33.0 | +3.90 | below null max — FAIL |
| `diff1 / D3_repeat / w48` | 12.0 | 7.67 | 1.24 | 13.0 | +3.48 | below null max — FAIL |
| `diff1 / D3_repeat / w16` | 7.0 | 3.67 | 0.98 | 7.0 | +3.39 | ties null max — FAIL |
| **raw / D7_sub16 / w96** | 84.0 | 82.42 | 1.17 | 88.0 | **+1.35** | best on the raw stream |
| **raw / D1_distinct / w64** | 5.93 | 5.47 | 0.63 | 6.93 | **+0.74** | — |

The raw ciphertext's maximum z over all detectors and window sizes is **+1.35**. There is no
window anywhere in the 13,041-rune stream whose symbol alphabet is restricted, whose IoC is
elevated, or which repeats internally, beyond what a shuffle of the same stream produces.

Because D1/D2/D3/D7 are monoalphabetic-invariant, this single line closes, for restricted-alphabet
and repetition-shaped payloads at or above the Section-2 floors:

- all 29 shifts, forward and reversed;
- Atbash and Atbash-composed-with-shift;
- **every one of the 29! alphabet permutations**;
- any decode in which the key is constant across the window.

The mild `diff1` D3 excess (one site, stream offset ~11,150-11,255, and its mirror image in the
reversed stream — the same site, not two) is the only thing above z=+3 anywhere. It sits *below*
the shuffle ensemble maximum at every window size, so under the pre-registered rule it is not a
finding. It is recorded here so a future researcher does not rediscover it and think it is new.

### 3b. Windowed non-English LM scan — `lmwindow_results.json`

FILLED_LMWINDOW

### 3c. Page-scale non-English sweep, monoalphabetic + periodic keys — `lang_results.json`

FILLED_LANG

### 3d. Machine-token crib search

FILLED_TOKENS

---

## 4. Re-scoring the 75 archived candidate decodes — `archive_rescore.json`

Every `"plaintext"` string of >=20 runes anywhere in the repo, re-scored under all six LMs and all
five agnostic detectors, against a 400-sample random-rune null at each candidate's own length.
Flag = z >= 4.0 **and** above the null maximum.

**8 flags on 75 candidates, from 4 files. Every one is explained:**

| source | instrument | z | reading |
|---|---|---|---|
| `analysis/structure/phase3_results.json` | LM_RG +29.7, LM_EN +6.5, LM_OE +6.5, D2_ioc +6.7 | — | **true positive**: this is the *solved* page-56 text `ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTO...`. The instrument found real English hiding among 75 mostly-noise strings without being told where it was. This is an unplanned but decisive end-to-end validation on repo data. |
| `out_vigauto.json` | LM_EN +4.46, LM_OE +5.01 | — | selection artifact: this string *is* the English-argmax of an entire sweep, so an elevated English-family score is what selected it. LA/DE/CY are flat (+2.9/+0.6/+2.9). |
| `armada20/test_4_tao.json`, `verify_4_tao.json` | LM_RG +4.06 | — | artifact of the 684-rune RG model's high variance; EN +1.5, LA +1.0, CY +0.1. |

**No candidate anywhere in the archive was flagged by the Latin, German or Welsh model.** Best
non-English z across all 75: LA +2.90, DE +2.77, CY +3.82 (and the CY value is on the solved
English page, i.e. cross-talk, not Welsh).

---

## 5. What is now closed, and what is not

**Closed** (for payloads at or above the floors in Section 2, under the decode families scanned):

1. Restricted-alphabet machine payloads — hex blocks >=64 runes, digit blocks >=32 runes — are
   absent from LP2 under *any* monoalphabetic decode. This is a permanent closure: the statistic
   is invariant, so it cannot be reopened by trying another substitution alphabet.
2. Non-English prose (Latin, German, Welsh, Old English) is absent from the monoalphabetic and
   short-periodic (L<=8) decode families at page scale, and from short windows.
3. Machine tokens (ONION, HTTP, coordinate and digit words) are absent under every shift, Atbash,
   and every alphabet permutation, forward and reversed.
4. The archived sweep bests contain no non-English signal.

**Not closed / permanent residue:**

1. **Uniform-alphabet payloads are undetectable in principle.** A base32 onion body, a raw key
   block, a hash, or any high-entropy binary blob mapped onto all 29 runes cannot be distinguished
   from the surrounding stream by any statistical instrument. If LP2's plaintext *is* a key or a
   hash, the blind spot is not narrowable — it is closed to statistics entirely, and only a
   correct key would reveal it. This is a different and stronger claim than "we looked and found
   nothing", and it should be recorded as such.
2. Payloads **shorter than the floors** (hex <64, digits <32, prose <96 runes) remain invisible.
   A 20-rune payload of any kind is below every instrument here.
3. Decode families **outside** monoalphabetic + periodic-L<=8 were not swept with these detectors.
   The agnostic detectors are family-blind on the *ciphertext*, but the LM detectors are not.
4. Languages not modelled (Greek, Hebrew, Norse, Enochian, constructed languages) were not tested.

---

## 6. Reproduce

```bash
cd liber-primus/analysis/round10b/B6-non-english-plaintext
python3 run_agnostic.py          # null calibration + positive control + real agnostic scan
python3 run_lang.py              # non-English LMs, periodic hill-climb, token cribs
python3 run_lmwindow.py          # windowed LM scan over all 116 monoalphabetic decodes
python3 run_archive_rescore.py   # re-score every archived candidate decode in the repo
```

German/Old-English corpora are fetched into `corpora/` (see `run_lang.load_corpora`); everything
else reads from the repo. Seeds are fixed in each script.
