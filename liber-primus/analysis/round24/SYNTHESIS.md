# Round 24 — SYNTHESIS (bounds, not a verdict)

_Written 2026-08-31 by the coordinator, from `PLAN.md` and the five lane `RESULTS.md` files as
filed on 2026-08-30. Doctrine [`ARMADA-DOCTRINE.md`](../../ARMADA-DOCTRINE.md) R7. Trust anchor
`python tests/validate.py` → **ALL VALIDATIONS PASSED (5/5)** at every lane close;
`validate_ledger.py` Unsound negatives = **0**. Ledger entries:
`R24-C1-MATCHED-RUNIC-READJUDICATION`, `R24-C1-EXT-NONENGLISH-READJUDICATION`,
`R24-C2-SKIP-BY-TWO-DECODER`, `R24-C2-EXT-SKIP-GENERATORS`, `R24-C8-DATE-INDEXED-PAD`._

---

## 0. The one-line result

Round 24 was the doctrine run **at** the doctrine: aim at the instrument, not the space. Its
Gate-#1 planning pass killed 5 of 8 candidates outright (doublet-floor, autokey-refuted,
degenerate-null ×2, flat-IoC) and ran the three survivors — the two **instrument axes Round 18's
L7-A/L7-B proved no negative had ever covered** (the adjudicator's language register, and the
decoder's rejection-loop relation), plus one dated-external-pad steelman. **Every axis came back
clean: the historic negatives HOLD under the corrected instruments.** L7-A and L7-B — the two
findings that re-aimed this whole project — are now themselves **discharged over the swept
slices**: fixing the instrument did not change a single verdict.

**There is no HIT and no flagged-for-oracle survivor.** The honest framing from `PLAN.md` stands:
these lanes could only ever REOPEN old negatives, not manufacture a hit, and they reopened
nothing.

---

## 1. The planning gate (PLAN.md) — 8 candidates, 5 killed before a single decode

Gate-#1 (four sub-tests, KILL unless all clear: not-a-re-run, not excluded-by-mechanism,
anchorable, feasible in-session): **C3** long-period polyalphabetic, **C4** non-additive
ciphertext-feedback, **C5** value-stream-as-binary-object, **C6** words-are-the-map, and **C7**
homophonic-downward all KILLED at the gate — each collides with a positively-measured mechanism
exclusion (the doublet deficit, the refuted autokey diagonals, a degenerate null, or flat IoC).
Survivors: **C1** (adjudicator register axis), **C2** (decoder relation axis), **C8** at reduced
scope. This is the cheapest round the project ever ran per unit of ground actually settled.

---

## 2. C1 + C1-EXT — the REGISTER axis (L7-A) — NULL under the corrected scorer

**C1 (matched-runic).** The one adjudicator the ledger recorded as built-but-never-adopted — the
round16 matched-runic scorer — plus an EN/LA/GR rune-trigram panel and the four R3
language-agnostic statistics, applied to the strongest prior B-04 slice: top-40 R20-prior seeds ×
16 B-04 generators × 4 reductions × sign × atbash × 2 seed-forms = **20,480 decodes**.
- **Control PASS with the L7-A gap reproduced:** planted Latin recovers at matched-power **0.79**
  vs English **0.50** — the matched scorer really does rescue Latin decodes the English scorer
  discards; and EN_NOVOWEL stays 0.00 under both, proving the matched scorer corrects rune
  **orthography**, not language.
- **Result:** best matched score −6.294 vs the family-wise bar −4.685 (**1.6 below**), 0 survivors
  under any of the three adjudicators; best decode flat IoC 1.07, incompressible. Red-team:
  FP ceiling 0.0100 matched vs 0.0101 English — no inflation.

**C1-EXT (genuinely language-aware).** Closed the axis C1 explicitly left `not_covered`:
language-aware models (not merely orthography-corrected English) for **Latin, Greek, Old English
poetic, and Enochian**, each control-validated to recover its OWN planted language 2–5× better
than the English quadgram scorer, from in-repo corpora only (the honest-availability call is
documented per register). Same 20,480-decode slice: **zero survivors.**

**The bound:** the English-only B-04 negatives were **not** structurally hiding a non-English
plaintext in this slice; the negatives hold across every non-English register that can be honestly
modelled from in-repo corpora. **Not covered:** languages with no usable in-repo Latin-script
corpus (e.g. Hebrew/Norse were unavailable at honest mass); slices other than the strongest-prior
B-04 slice. **Reopens if** a connected Latin-script corpus of a new candidate language lands
in-repo, or a different sweep's survivor slice is re-adjudicated.

---

## 3. C2 + C2-EXT — the RELATION axis (L7-B) — NULL under the skip-aware decoder

**C2 (the skip_by_two decoder).** L7-B's hole was that every beam-based negative covers a
rejection loop advancing the key by exactly **one** symbol per rejection, while `skip_by_two` —
which reproduces LP2's observed doublet rate — is beam-unrepresentable (25.8 % recovery). C2 built
the decoder that represents it (`driftbeam` mode `keyskip2`, preset `pair`), proved **100 %**
plant recovery where the beam gets 25.8 %, calibrated the pair claim bar (**7.384** at N=1e6), and
re-decoded the top-prior seed slice under it: **245,975 words, 0 hits, max pmax 5.904 (1.48 below
bar); wrong-key null 0/4000 full-gate false positives.**

**C2-EXT (broaden the closure).** Does the skip_by_two hole reopen a beam-based negative under
**other generators**, **non-zero offsets**, or the **continuous drift cousin**? Seven axes, each
under the decoder that models its relation, **8/8 positive controls validated** (pair 100 % on
skip_by_two under bash/perl/tex/sha/py27; drift 98.3 % on free_drift/drift_at; the plain beam
10–33 % on all — reproducing the hole being audited):

| axis | keys | hits | max pmax | bar |
|---|---:|---:|---:|---:|
| A1 bash `$RANDOM` mod29 | 20,487 | **0** | 5.204 | 7.384 |
| A2 perl `int(rand(29))` | 20,487 | **0** | 5.715 | 7.384 |
| A3t/A3l tex pgf + lcg | 48,836 | **0** | 5.563 | 7.384 |
| A4 sha256_ctr keytext dict (full) | 2,165 | **0** | 4.669 | 7.384 |
| A5 Py2.7 non-zero offsets | 1,024 | **0** | 3.969 | 7.384 |
| A6 free_drift / drift_at | 20,433 | **0** | 9.287* | 13.842 |

_\* A6's closest approach (seed 4437, self-consistent recovery 0.911) is 4.6 below its own drift
claim bar and inside the wrong-key null tail._

**The bound:** **113,432 keys, 0 hits — no beam-based negative reopens over any swept axis.**
L7-B is now discharged across generators, offsets, and the drift cousin **for the prior-dense
slices**; this is partial coverage of each generator, stated per axis, never full-space closure.
**Not covered:** the full 2³²/2³¹ seed tails (compute-only, out of scope by PREREG), offsets
beyond o=16, drift regimes beyond the control set. **Reopens if** a broader sweep of the same axes
with the same committed scripts finds a bar-clearing survivor.

---

## 4. C8 — date-indexed public pad — UNAVAILABLE at Step 0 (premise fails)

The lane's join key — per-page PGP signature timestamp → offset into a dated public pad — **does
not exist for the decrypt target**: exactly 8 clearsigned blocks exist in the canonical corpus,
all on prose/index pages; **the unsolved LP2 runic pages carry no PGP signature at all.** The
pipeline was built and control-validated anyway (right-date recovery 1.000; wrong-date /
wrong-source 0.03), and the fullest defensible steelman the artifacts permit — 630 tests (15
pages × 7 distinct timestamps × 6 builders) against the NIST beacon — returned a clean null,
0 survivors. **Closed for its stated purpose**; reopens only if a signed, dated artifact tied to
the unsolved pages surfaces.

---

## 5. What Round 24 moved, and what it did not

**Moved.** The two conditionals that have hung over every negative since Round 18 — "…but only in
English" (L7-A) and "…but only for one rejection loop" (L7-B) — are now **measured through, over
the strongest-prior slices, and the negatives survive both corrections.** This is the round the
Aiming Test was written for: five bad lanes killed for free at the gate, three instrument audits
run at full control validation, zero new key-space fog.

**Did not move.** The standing verdict — **LP2 0–54 is OTP-class** with a soft anti-repeat rewrite
on the ciphertext output — is unchanged. The frontier after Round 24 is exactly what `PLAN.md`
predicted if C1/C2 came back clean: **dry at the tested resolution**, with two live branches —
the **PRNG core-day tail** (picked up immediately by Round 25) and **`/dev/urandom`**
(unrecoverable by construction).

---

## 6. Live threads leaving Round 24

1. **The Py2.7-MT 2³² tail is the one runnable branch left** — enumerable, gate-ready
   (skip-aware pair decoder + hitfn20), honestly low-prior. _(Round 25 began grinding it.)_
2. **Any bar-clearing survivor anywhere remains flagged-for-oracle** (R21-L1's KILL stands; no
   no-oracle gate clears 0.90).
3. The C1 register axis reopens per-language as honest corpora land in-repo; the C2 axes reopen
   per-generator as core-days are spent.
