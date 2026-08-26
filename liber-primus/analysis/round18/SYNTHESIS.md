# Round 18 — SYNTHESIS

_Eight lanes, run 2026-08-25/26. Every lane pre-registered before running, each with a positive
control and a size-matched null. Zero decodes over bar. **The value of this round is not a hit —
it is that four of the eight lanes found the instruments, not the search space, to be the limit.**_

Campaign plan: [`CAMPAIGN-PLAN.md`](CAMPAIGN-PLAN.md) · Doctrine written from it:
[`../../ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md)

---

## The thesis it was built on, and how it fared

Round 17 proved at ≥0.99 power that the anti-repeat filter is **machine**-applied — and then
nothing was built on it. Round 18's premise: *the pad came out of a program, so hunt the program.*

**The premise paid, but not where it was aimed.** It was aimed at recovering the generator. What
it actually bought was a measurement of how blind the existing instruments are, and that is worth
more than another sweep.

| Lane | Verdict | What it bought |
|---|---|---|
| **L1** TOOLCHAIN | **measured** | The images are a **two-stage `gs` → ImageMagick** pipeline, not "Ghostscript renders". `gs` bounded to **9.04–9.14** by a byte-identical ICC profile. A ranked generator prior. |
| **L2** FILTER AS A LEAK | **measured / eliminated** | The filter acts on the **ciphertext** (alternatives excluded at power 1.000). Drift **373.6 ± 19.6** draws. Info-budget: the SAT route is **proved dead**. A **language-free key-side screen**. |
| **L3** ORNAMENTS | **negative** | 109 bands read (**9,899 glyphs**) — the first time ever. Found **256 non-runic base-60 tokens the analysis tree never held**. |
| **L4** FORCING | **negative** | C-02's own specified detector has **FPR 0.490** at f=0. Running it as written would likely have announced a false discovery. |
| **L5** PAYLOAD | **measured / negative** | Six contested bytes **resolved at 100% calibrated accuracy** — none change. Then **3 real errors found elsewhere** in `canon_256.bin`. E-01 null, its coverage gap closed. |
| **L6** OFFSET + MARSAGLIA | **negative** | **2.04 × 10⁹ offsets**, 0 hits, controls 40/40 and 16/16 **on the real pad family**. Marsaglia CDROM fetched, 110/110 hashes verified, **swept for the first time**. |
| **L7** INSTRUMENT RED-TEAM | **FOUND-ERROR ×3** | **Every negative in this repo is an English-register negative, and no entry said so.** |
| **L8** PROVENANCE OSINT | **measured / inconclusive** | The **PGP verification table** this repo never had: 54/54 verify, one key. Plus 433 ranked seed candidates. |

---

## 1. The correction that reaches every other entry

**L7-A.** The word "English" appeared in no `coverage` or `not_covered` field of the ledger's 62
entries. Measured power of this project's own instrument to detect a **correct key**:

| register | correct-key score (L=120) | power |
|---|---|---|
| LP1 solved-page register | −4.33 | **1.00** |
| Old English | −5.39 | 0.58 |
| Latin | −5.58 | 0.33 |
| half-vowel English | −5.62 | 0.33 |
| Welsh | −6.58 | **0.00** |
| vowel-dropped English | −7.60 | **0.00** |

Rune-index recovery is **100% in every row**: the beam decodes it perfectly and the scorer calls
it noise. In the worst row the correct key scores *below* a deliberately wrong one.

**Stated as loudly: this does not void the negatives.** The register LP2 demonstrably uses scores
−4.33 at power 1.00, and re-scoring the 340 archived candidates is negative and *powered* for
Latin, Old English and half-vowel English. What changes is the claim, not the result. `B-04`,
`R16-KDF`, `R16-PRNG`, `R17-PUBLIC-PAD` and `B-21` now carry restated coverage; the original text
is preserved verbatim in each entry's `restated_from`.

**Compounding it:** Round 10b/B6 issued a binding handoff requirement — persist a language-agnostic
statistic at sweep time, "retro-fitting is impossible". **0 of 15** post-B6 sweep files comply, and
~10¹⁰ decodes have already been discarded.

## 2. Two independent answers to it, from lanes that did not know

- **L2** found the filter *is* a leak — on the key. Inferred skip count separates a correct key
  from wrong keys at **3.08 sd** (power 0.924 at 5% FPR), **orthogonal to the English scorer**.
- **L6** re-scored every survivor under an 8-register panel plus three language-agnostic
  statistics, unprompted. One row tripped at 4.0σ; escalation decayed it to −7.272 and it was
  **reported as a selection artifact rather than quietly dropped**.

A language-free screen now exists. That is the single most useful thing to carry forward.

## 3. Instruments that were measuring less than believed

- **The beam represents exactly one rejection-loop implementation** (one key advance per
  rejection). A sampler consuming **two draws per rejection** reproduces LP2's doublet rate and is
  missed entirely: −6.90 at 25.8% recovery. Raising `max_skip` 3→8 and beam 400→1000 changes it by
  **exactly 0.000**. (L7-B)
- **A correct key is undetectable at the offset every per-page test here has used**: a planted key
  scores **−3.949** drift-corrected versus **−6.94** uncorrected. (L2)
- **`threshold_for()` accepts `segment_len` and never uses it**; its constants are calibrated at
  L≈120, and it was used to adjudicate the very sweep it was fitted on. Consequence: **R17's
  headline P3 best of −5.679 was the null's own maximum**, not a 0.18 near-miss. The repo-wide
  family-wise bar is **−5.210**, stricter than the −5.5 in common use. No verdict flips. (L7-C, L6)
- **`ks_hexchars` is worse than R17 documented** — beyond dropping digits it also collapses the
  runic digraphs `AE`/`EA`. (L6)
- **C-02's specified detector has FPR 0.490 at f=0** against a nominal 4.8e-5. (L4)
- **A flat null is wrong for any line-position statistic on LP2**: typography alone lifts the
  line-initial χ² from a flat-null mean of 26.9 to 65.6. (L4)

## 4. What was found that nobody was looking for

- **256 non-runic base-60 tokens spanning exactly 0…255** across pp. 49–51, binned as "ornament"
  by the geometry pipeline and therefore **never held in this repo's analysis tree**. Transcribed
  into `L3-ornaments/nonrunic.json`; **not yet attacked**. (L3)
- **Three byte errors in `canon_256.bin`** (idx 45, 50, 246), each turning on a stroke that is
  simply absent. `canon_256.bin` is **left intact**; the correction ships beside it as
  `payload_resolved.bin`. Overwriting canon is the owner's call. (L5)
- **On page 15 the four digits of `3299`** are set in a lighter ink tone (min grey 47–51) where
  every other digit on that page is 0.0. 3299 is the prime immediately preceding 3301. Absent from
  every transcription here and from both vendored community ones. **Measured, not interpreted.** (L3)
- **19 files posing as Cicada communications are 199-byte HTTP `429` error pages.** That is the
  third instance of this failure shape, after `_560.00`'s silent truncation and a misnamed key
  file whose name asserts a fingerprint that is not the key's. (L8, L5)
- **`gs` 9.04–9.14 and GnuPG 1.4.11 on one unchanged Linux box for three years**, the latter from
  46/46 PGP version strings — independent corroboration of L1's render forensics. (L1, L8)

## 5. Coverage added

| | |
|---|---|
| Offsets swept | **2.04 × 10⁹** (L6) |
| Drift-corrected ladder decodes | 1,371,030 (L2) |
| B-05 grid on the corrected payload | 20,160 — best −6.685, **0 hits** (L5) |
| Keyless Gematria reads | 56,376 (L4) |
| Band glyphs read | 9,899 across 109 bands (L3) |
| PGP signatures adjudicated | 228 files → 54 distinct, **54/54 verify** (L8) |
| Ledger entries | 62 → **83**; `never-run` **15 → 5** |

## 6. What this round says to do next

Not another flat-prior sweep. Four outputs compose into one targeted attack:

1. **L1's ranked generator prior** — glibc, Python **2.7**, Perl and bash `$RANDOM` at the top,
   .NET at ×0.05. `$RANDOM`'s seed space is enumerable in minutes and **has never been run**; and
   any past sweep that called `random.seed("...")` under **Python 3 tested the wrong semantics**.
2. **L8's 433 ranked seed candidates**, top-ranked `1325734783` — the second the 3301 key, subkey
   and UID self-signature were created. Round 8 treated all unix seconds as equally likely.
3. **L2's language-free key-side screen**, so the English scorer is no longer the only judge.
4. **L2's drift correction**, so a correct key is no longer invisible at the tested offset.

Highest-value single item outside that: **find a Liber Primus PDF with a text layer or an embedded
font subset.** The renders prove one existed; a subset's `/BaseFont` name plus its subset tag would
name the typesetting program and the rune face outright — and if it names `allrunes`, L1's
LaTeX-internal PRNG jumps from rank 5 to rank 1. The local corpus is scanned; the off-repo search
is open.

Cheapest untouched item: **attack the 256 non-runic tokens L3 recovered.**

## 7. What is NOT covered

- **L6:** 10 of 12 Marsaglia builder × byte-order combinations remain queued and resumable.
- **L7-A:** the negatives are **not** extended to Welsh or vowel-dropped English at any useful power.
- **L2:** key-skip versus value-rewrite is **not separable** (power 0.175); both remain in scope.
- **L5:** E-01 covers only *published* moduli and only PKCS#1 v1.5 / PSS. An unpublished
  **2048-bit** modulus is the one size for which the payload is a natural full-width block — that
  reopens it. Cells 186/210/211 were never segmented.
- **L3:** the recovered non-runic block is transcribed, not attacked.
- **L4:** below f≈0.2, forcing is excluded at no useful power.
- **L8:** **no public cypherpunks archive covering 2011–2012 exists.** That half is *unsearchable*,
  not searched-and-clear.

_Trust anchor at close: `validate.py` ALL PASSED · 8/8 benchmark gates · `validate_ledger.py`
reports **Unsound negatives: 0**._
