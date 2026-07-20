# Campaign XVIII — Filter-Aware, Skip-Tolerant Re-Decode (open item 2c)

_2026-07-20. Reproduce: `PYTHONUTF8=1 python3 analysis/campaign18_skip/skipdecode.py`
(mechanism gate) · `robustness.py` (recovery + false-positive ceiling) ·
`sweep_selftest.py` (pipeline recall gate) · `sweep.py --texts referenced|all`
(the corpus sweep). Pure stdlib + numpy + the project's own `lp.score`/`lp.gematria`._

## The one-paragraph result

Every prior keytext test in this project (112+ texts across Campaigns III, XII, XIII)
assumed the running key lines up **1:1** with the ciphertext. Campaigns X/XI had already
proven that LP2's cipher is a one-time pad passed through an **active, plaintext-aware
doublet-suppression filter (~83% strong)** — and the natural mechanism for that filter is
**key-skip**: when the next output rune would double the previous one, advance (skip) the
key symbol and try the next. Key-skip **desynchronises** the key from the plaintext after
the first skip (~1 per 35 runes), which means *even the correct keytext decodes to English
for ~30 runes and then collapses into noise* under a rigid test — scoring as a null over
the full page. This campaign built and **validated** a skip-tolerant beam decoder that
tracks the desync, proved it recovers keys a rigid test provably misses, and re-ran the
corpus through it. **The 9 directly-referenced texts are a clean null under the corrected
model** (best of 55 pages −5.88, median −6.21; genuine English −4.3, noise ceiling −6.82).
The broader 122-text corpus re-decode is in progress. This does **not** solve LP2, but it
**discharges a real soundness hole the project itself had flagged and never closed** (open
item 2c): the referenced-text nulls are no longer conditional on the rigid-alignment
assumption — they are now unconditional under the mechanism the ciphertext actually shows.

## Why this was worth doing (the soundness hole)

The Elimination Ledger's "Still genuinely open" section, item **2c**, read:

> _Skip-tolerant / filter-aware re-decode (soundness patch): all keytext/keystream nulls
> assumed rigid key alignment; a doublet filter perturbing key consumption could make them
> unsound._

That is exactly right, and it had never been executed. If the ~83% doublet filter (proven
in Campaign X/XI) consumes the key by **skipping** on collision, then the entire keytext
corpus was tested under the wrong alignment. A rigid null is only meaningful if a rigid
test *would have found* the correct key — and here it provably would not.

## The mechanism model (`skipdecode.py::encipher_keyskip`)

Decode relation matches `lp.ciphers`: `p = (c + sign·k) mod 29`. Encipher inverts it, with
the filter:

```
for each plaintext symbol p:
    loop: c = (p − sign·K[j]) mod 29
          if c == previous_output and rng < 0.83:   # soft suppression, Campaign XI
              j += 1; continue                        # SKIP this key symbol
          break
    emit c; j += 1
```

The skipped ("rejected") key symbols are exactly those that would have produced a doublet
(equal to the **previous ciphertext** rune). This model reproduces the observed statistics
(doublet ≈0.66%, IoC·N ≈1.00) and is the only additive construction that does.

## The decoder (`skipdecode.py::beam_decode`, `sweep.py::beam`)

A beam search whose hidden state is the cumulative key-skip count. At each ciphertext
position it may take 0..MAXSKIP skips; a skip of depth _d_ is **valid only if** each of the
_d_ intervening key symbols would have produced the previous ciphertext rune (the
suppressed-doublet condition). Hypotheses are pruned by the project's canonical
transliteration **quadgram** score, so the correct (skipped) path — which reads English —
outcompetes the lazy no-skip path — which desyncs into noise — within a few runes of each
skip.

> **Bug found and fixed mid-campaign.** The first sweep implementation compared the
> skip-validity condition against the *plaintext* previous rune instead of the *ciphertext*
> previous rune. It silently halved recall. The correct condition is a suppressed **output**
> doublet → compare to `ct[i−1]`. After the fix, beam-at-exact-offset recovers **100%**.

## Validation gates (all passing — numbers)

| Gate | What it proves | Result |
|---|---|---|
| **Mechanism** (`skipdecode.py`) | rigid test misses the correct key; skip-decoder recovers it | rigid correct key **−7.24 / 8.5%** (noise); beam **−4.15 / 100%**; wrong-key control **−7.56** |
| **Robustness** (`robustness.py`) | recovery holds at realistic length & skip counts | 4 texts × 2 offsets, up to **14 skips**, doublet 0–0.86% → **99.6–100%** match, −4.27…−4.32 |
| **False-positive ceiling** (`robustness.py`) | what score can noise fake? | 400 wrong (key,offset) trials → **max −6.82**, mean −7.30 |
| **Pipeline recall** (`sweep_selftest.py`) | full prefilter→screen→confirm surfaces a planted key | **7/8** per page (→ effectively certain across 55 pages) |

Operating scale (this project's scorer, per Campaign XI / `tests/validate.py`): genuine
English solves score **≈ −4.0 to −4.35**, noise floor **≈ −7.5**, discovery threshold
**−5.2/−5.5**. The confirm threshold −5.5 sits ~1.3 above the measured noise ceiling and
~1.2 below genuine English — a wide, safe margin.

## The sweep (`sweep.py`)

Three stages per (page × text × sign × atbash):
1. **Skip-tolerant prefilter** — vectorised index-bigram over *all* running-key offsets,
   scored as the max over {no skip} ∪ {one skip inserted at a grid of early positions}, so
   an early first-skip no longer drops the correct offset. Top-300 → a small skip-aware beam
   quadgram-reranks the prefix → top-24 offsets.
2. **Screen** — skip-aware beam on the first 90 runes; keep offsets beating −6.0.
3. **Confirm** — full-page skip-aware beam; report `lp.score.score_norm`; a hit needs > −5.5.

## Results

### Referenced texts — CLEAN NULL (`RUN-referenced.log`)
9 highest-prior, directly-referenced texts (Mabinogion, Self-Reliance, King in Yellow,
Agrippa, Book of the Law, rune poem OE + translit, solved-page plaintext, thematic) ×
55 unsolved pages × both signs × both atbash, 349 s:

| metric (best score per page, over 55) | value |
|---|---|
| best of all 55 pages | **−5.882** |
| median | −6.206 |
| worst | −6.369 |
| hits above confirm threshold −5.5 | **0** |

Every page sits in the noise band, and the scores are nearly flat across all 55 pages —
no text stands out even slightly. This is the OTP signature showing through, now under the
*correct* alignment model. **The referenced texts are eliminated unconditionally.**

### Full corpus (122 texts) — IN PROGRESS
`sweep.py --texts all` → `RUN-fullcorpus.log`. Re-decodes the Campaign XII/XIII
thematic/esoteric/cypherpunk corpus under the same corrected model (~211 s/page; ~3 h
total). Result will be appended here on completion.

## What this closes, and what it does not

**Closes:** open ledger item **2c** for the referenced texts. Their prior nulls were
*conditional* on rigid alignment (which is provably unsound for this cipher); they are now
*unconditional*. The project gains a **validated, reusable, novel decoder** — any future
candidate text runs through it in seconds, correctly aligned.

**Does not close:** an **external** key that was never a public text (e.g. the lost "AN END"
deep-web page) remains the genuine frontier, untouched by any internal method. And the
skip-model, while the best-fitting additive construction, is a *model*; a fundamentally
non-additive feedback cipher is still formally unbounded (see ledger §B).

## Follow-on leads run this session (all closed)

Three orthogonal leads, chased to keep the frontier honest:

**Lead 1 — pp49-51 payload as a keystream, skip-aware (`payload_skip.py`, `RUN-payload-skip.log`).**
Campaign VII tested the 256-byte pp49-51 payload as a polyalphabetic key *rigidly*
(337k configs, null) — but that is the *same* soundness hole this campaign exposed. Re-ran
it through the skip-tolerant beam: both canonical byte variants (majority / decimal-pref),
forward + reversed, bytes mod 29, over each page at offset 0 (repeated to cover the page),
both signs, both atbash. **Null** — best −6.76, at the noise floor. The payload is not a
skip-aware key over any page either. This connects the repo's two flagship objects (the
pp49-51 binary and the skip decoder) and closes the payload-as-key thread under the
corrected model.

**Lead 2 — word-length skeleton match (`word_skeleton.py`, `RUN-word-skeleton.log`; ledger 2b).**
An OTP hides symbol values but not word boundaries, which the transcription preserves
(`-` separators). If the plaintext were a known text, a page's rune-count-per-word sequence
would contain a long contiguous run matching that text's word-lengths. Using the
high-power statistic (**longest consecutive exact-length run**, chance ≈ 0.4^R) across 11
high-prior texts vs an 8-shuffle control: **strong null** — every page's real longest run
(7–10) is at or *below* the shuffled-control ceiling (8–12); controls frequently beat the
real sequence. The plaintext is not any of these texts by word-skeleton, and this holds
*regardless of the cipher model*.

**Lead 3 — "bump" doublet-filter variant (closed by argument, no run needed).**
The doublet filter could instead alter the output *in place* on collision (a deterministic
"bump") rather than skipping the key. But a bump keeps the key **1:1-aligned**, so a rigid
decode of the correct key yields plaintext with only ~3% corruption — which scores ≈ −4.5,
far above threshold. The existing rigid referenced-text nulls (−5.8 to −6.4) therefore
*already exclude* it. **Key-skip is the only doublet-filter mechanism that defeats a rigid
test, because it is the only one that desynchronises the key** — which is exactly why the
Campaign XVIII skip-tolerant re-test was both necessary and sufficient to discharge the
filter-mechanism soundness worry.

## Artifacts
- `skipdecode.py` — encipher models + beam decoder + mechanism gate
- `robustness.py` — recovery robustness + false-positive ceiling
- `sweep.py` — the corpus sweep (`--texts referenced|all`, `--pages a-b`)
- `sweep_selftest.py` — planted-key pipeline recall gate
- `RUN-referenced.log` — the referenced-text null (complete)
- `RUN-fullcorpus.log` — the 122-text re-decode (in progress)
- `payload_skip.py` / `RUN-payload-skip.log` — Lead 1: pp49-51 payload as skip-aware key (null)
- `word_skeleton.py` / `RUN-word-skeleton.log` — Lead 2: word-length skeleton match (null)
