# C3 — CLOSEOUT of Round 18 lanes L3 (ORNAMENTS) and L8 (PROVENANCE) · PRE-REGISTRATION

_Round 19, Phase 3. Written 2026-08-26 **before** any C3 measurement was scored._
_Binding: [`liber-primus/ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md); campaign
[`round19/CAMPAIGN-PLAN.md`](../CAMPAIGN-PLAN.md)._

---

## 0. What this lane is, and what it is not

C3 is a **closeout**, not a new hypothesis. Two Round 18 lanes stopped mid-run:

| lane | what is on disk | what is missing |
|---|---|---|
| `round18/L3-ornaments` | `PREREG.md`, `PREREG-ADDENDUM.md`, `inventory.json` (109 bands), `calibration.json` (gate G-A), `nonrunic.json`, `linegeom.json`, `linetests.log`, and a `RESULTS.md` marked **IN PROGRESS** with §3, §4, §5 empty | the band reads themselves — `read_bands.log` stops at band **45 of 109** — and every hypothesis verdict |
| `round18/L8-provenance` | `MESSAGES.json`, `PGP-VERIFICATION-TABLE.{json,md}`, `verify_all_signatures.py`, `KEY-COMPARISON.json`, `TIMESTAMP-SEED-CANDIDATES.json`, `evidence/`, and a `RESULTS.md` with §4 (I-03) and §6 (coverage) empty | an independent re-derivation of the table, the I-03 result, and the coverage/reopen block |

**Inherited thresholds.** C3 adopts, unchanged, every pass/fail bar fixed in
`round18/L3-ornaments/PREREG.md`, `round18/L3-ornaments/PREREG-ADDENDUM.md` and
`round18/L8-provenance/PREREG.md`. No bar in either lane is edited here. Specifically:

- **L3 gate G-A** — solved-page per-glyph agreement **≥ 90 %** for the reader to be trusted.
  Measured in Round 18 at **44.2 %** pooled → **FAIL**. That failure is inherited, not re-litigated.
- **L3 H1–H8** — the family bar `p < 0.001/6 = 1.67 × 10⁻⁴` on any family headline statistic.
- **L3 H9** (addendum) — intensity outlier = **> 4 σ** above the page's own body-text mean grey,
  significant only at **p < 0.001** against 10 000 size-matched draws, with a stroke-width-matched
  re-test, and **"a single outlier is not a channel"** (< 10 book-wide ⇒ report as an annotated
  anomaly list, not a channel).
- **L3 B-12 / I-3a** — bimodality PASS iff **separation ≥ 2.0 σ AND ΔBIC > 10**; bit-decode
  PASS iff **p < 0.001** vs a size-matched shuffle null.
- **L8** — PASS iff gpg emits `GOODSIG`+`VALIDSIG` for
  `6D854CD7933322A601C3286D181F01E57A35090F`; a FAIL is a finding about the *message* only if the
  same normalised signed body has **no** PASSing copy elsewhere; controls C1–C4 must all be met.
- **L8 I-03** — HIT = a dated, archive-attested post **before** its element's disclosure date, with
  a URL and a capture carrying the date. Anything undateable is not a hit.

## 0.1 One new instrument gate, added openly

C3 adds exactly one thing Round 18 did not have, and it is added because the brief for this
closeout requires it and because doctrine mechanic 2 requires it:

> **G-A2 — the band-shaped control.** Round 18's G-A measured the reader **whole-page**. This
> lane does not read pages, it reads **bands**. A whole-page number is not a statement about a
> band read, in either direction. G-A2 therefore plants band-shaped objects of known identity
> and measures recovery through the *identical* code path `read_bands.py` uses on real bands.

G-A2 does **not** replace G-A and does **not** relax it. G-A's 90 % bar is inherited verbatim and
applied to G-A2's pooled figure as well. G-A2 is registered here, before it is scored.

**G-A2 design, fixed now:**

- **Plant.** On every Liber Primus page whose plaintext is known *by decryption* — LP1 `01/03/05/06/14`
  and LP2 `73` (p56) / `74` (p57), all from the vendored 2014 render set that is byte-identical in
  lineage to `data/relikd/` — synthesise a band record `(page, x₀..x₁, y₀..y₁)` around each image
  text row and push it through `read_bands.py`'s band path: page ink → box mask → `rows_from_ink`
  → `read_ink_strip` / `read_scaled` → stored R9 bijection → RUNIC / DEGENERATE / NON-RUNIC call.
- **Truth attribution.** The corpus's rune lines are broken **semantically**; the image's lines are
  broken **typographically**, and they do not agree. This is a fact established in Round 18
  (`calibrate.py` docstring) and not by looking at any C3 result. Per-line matching would therefore
  measure the transcriber's paragraph breaks, not the reader. Truth is attributed by aligning the
  concatenated band reads, in reading order, against the page's **flat** canonical rune stream
  (`difflib`, `autojunk=False`), then attributing matched glyphs back to the band that produced them.
- **Two-sided.** Sensitivity alone is uninformative — a reader that calls everything runic has
  100 % sensitivity and zero information. G-A2 therefore also probes ink that is **known not to be
  runes** (blank margin, woodcut interiors, vine-margin strokes) and reports the fraction **not**
  called RUNIC.
- **Reported statistics** (all fixed now): pooled per-glyph agreement; the same split by typeface
  era (LP2 = the target set's face, LP1 = out of the template domain); per-band **precision**
  (matched ÷ glyphs read) for bands whose read is **≤ 16 glyphs**, which is P-9's stated band size;
  the fraction of bands read verbatim; sensitivity; specificity.
- **Gate rule.** G-A2 **PASSES** at pooled agreement ≥ 90 % (inherited). Below that, the reader may
  be used to **classify** band ink and to **corroborate** a read against an independent
  transcription, and may **not** be used to assert the content of an uncorroborated band. Any such
  band is labelled `UNRESOLVED-AT-THIS-ACCURACY`. This is the same consequence Round 18 already
  applied to G-A, restated so it binds G-A2 identically.

---

## 1. The Aiming Test (doctrine §1)

### Q1 — What would a hit look like, and would *this* instrument recognise it?

**Two different hits, two different recognizers.**

**Item 1 (ornaments).** A hit is a catalogued non-text band that contains **glyphs carrying
information** — runes forming a word, a token block, an index, a pointer. The recognizer is
`read_bands.py` + `hypotheses.py` (H1–H8, thresholds above). The plant is **G-A2**: real bands of
**known** content pushed through the identical path. If G-A2 cannot recover known runes from a
band-shaped box, then a silence over the 109 real bands is not a negative — it is an unmeasured
instrument, and it will be reported as such. That is the whole point of adding G-A2 rather than
quoting Round 18's whole-page 44.2 % in either direction.

The recognizer is also known **in advance** to have a specific blind spot, and it is named here:
the band reader emits a *rune-index sequence*, and `hypotheses.py`'s H1 recognizer is an
**English/known-Cicada-string** matcher. Per Round 18 L7-A that register is 0.33-powered for Latin
and 0.00 for vowel-dropped English. So H1's negative is an English-register negative, and it is
labelled that way in the results. H3–H8 (numeric/positional/length channels) are register-free and
do not carry that conditional.

**Item 2 (provenance).** A hit is a **verification-table row that changes**: a message that does
not verify against `7A35090F` from an undamaged file, or a **second signing key** anywhere in the
corpus. The recognizer is `gpg --verify` inside an isolated keyring, and its plant is the C2/C3
control pair — a body-tampered message that **must** FAIL and a foreign-key message that **must
not** verify as 3301. Without those two, a table of 192 PASSes is a table that says only "gpg ran".
For **I-03** a hit is a dated, archive-attested pre-disclosure post; the recognizer is a regex grep
over the actual mbox bytes, and its denominator is *how many months of the window the archive
holds at all* — which is measured, not assumed.

### Q2 — What measured fact raises this family's prior above the flat rate?

**Item 1.** Three, each with a path:

1. `round18/L3-ornaments/RESULTS.md` §1 — Round 8's ornament catalogue contains, **mislabelled as
   ornament**, the pages of the Liber Primus that are *not runic*: the alphanumeric blocks on
   pp. 49–51 and the 4×4 numeric grid on p15. The pipeline's non-text rejection rule
   (`analysis/geometry/*`: outside the dominant column, or median component height > 240 px)
   discarded real data. That is a **demonstrated instance** of the exact failure this lane hunts,
   which is what raises the prior on the other 100-odd bands above flat.
2. `round18/L3-ornaments/RESULTS.md` §0 — `ornaments.json` stores
   `[page, x_lo, x_hi, n_components, median_height]` and **drops y**. No one could crop these bands
   for eight rounds because the coordinate needed to do it was not in the file. A never-inspected
   object is a higher-prior target than a swept key space (doctrine R5.1).
3. `analysis/round9/` — the whole-page vision armada scored 0.145 alignment on dense pages. A
   ≤ 16-glyph band at high zoom is a materially different task. **The prior says so; G-A2 measures
   whether it is true.** This lane does not get to assert it.

**Item 2.** `corpus/GAPS.md` **G-02** ★★★★★ states that no file in this repository records which
signatures verify against `7A35090F`, *despite that being the repo's own declared authenticity
test* (`KNOWLEDGE.json: authenticity_test`). An unbuilt table that the project's own trust model
depends on is the highest-prior object there is: its value does not depend on finding an anomaly.

### Q3 — Is the space bounded, and by what?

**Both items are doctrine-R5 rank-1 objects: finite, human-checkable, and fully enumerable.**

| object | size | enumerable? |
|---|---|---|
| catalogued bands | **109** records over **39** pages (deduped union of Round 8's 62-row and 47-row catalogues, y restored) | yes — every one is read |
| P-9's "real candidates" | **30** with n ≤ 16 | yes |
| non-runic token blocks pp. 49–51 | **256** base-60 tokens | yes |
| text rows for B-12 line geometry | **616** rows over 56 pages | yes |
| connected components for H9 | every component on all 56 sha256-verified renders | yes |
| `.asc` files in the repository | **228** (113 distinct by sha256) | yes |
| distinct signed messages | **54** | yes |
| I-03 mailing-list window | 13 months (2011-01 → 2012-01); **the archive's own coverage of that window is measured, not assumed** | yes, and the denominator is reported |

Nothing here is sampled. Every count above is an exhaustive enumeration of a held object.

### Q4 — What are the three conditionals the negative will carry?

1. **Key space / object space** — the 109 catalogued bands and the 228 `.asc` files. Bands that
   Round 8's grouping never emitted are **not** covered; the ornament rejection rule is itself the
   thing under suspicion, so its output cannot be treated as a complete frame. `.asc` files not
   mirrored into this repository are not covered.
2. **Decoder / transition model** — the R9 template-DP reader with the stored 29-class bijection,
   templates clustered from **LP2** renders. LP1's face is out of domain (measured). Non-Futhorc
   glyph systems, glyphs set below ~30 px, and glyph sets absent from `templates.npz` are outside
   the transition model entirely. For L8, GnuPG 2.4.8's parser: a signature in a format this build
   cannot parse would read as NO-SIG, not as FAIL.
3. **Adjudicator register** — H1's word matcher is **English + a known-Cicada-string list**. Per
   L7-A that register is 0.33-powered for Latin and 0.00 for vowel-dropped English. A band holding
   Latin, Old English, or abbreviated English would very likely be scored as noise by H1. H3–H8 are
   numeric/positional and register-free. Say which conditional applies to which verdict, per verdict.

### Q5 — What single observation abandons the lane at 10 % of budget?

**Item 1 kill condition:** if **G-A2's specificity probe calls known non-rune ink RUNIC at ≥ 50 %**,
the reader has no discriminating power at band scale and every band verdict in this lane is
vacuous. In that case C3 stops reading bands, reports G-A2 as the lane's only result, and files
A-06/B-12 as `instrument-limited` rather than as any kind of negative.
Checkpoint: immediately after `band_control.py`, before any hypothesis is scored.

**Item 2 kill condition:** if **control C2 does not FAIL** — i.e. a message with a flipped body byte
still verifies — the keyring or the instrument is wrong and the entire table is void. In that case
C3 reports the instrument defect as the finding and publishes no counts.
Checkpoint: the control block runs *first* in `verify_all_signatures.py`, before the corpus sweep.

---

## 2. Hypotheses under test, with the inherited thresholds

### Item 1 — L3 (ledger A-06, B-12; parked P-9)

| id | hypothesis | threshold (inherited) |
|---|---|---|
| **G-A2** | the band reader recovers known runes from band-shaped boxes | pooled per-glyph agreement ≥ 90 % (from G-A) |
| **H1** | a short runic band contains a ≥ 8-char English / known-Cicada string | any hit, adjudicated; English-register conditional stated |
| **H2** | band content recurs at ≥ 3 sites | p < 1.67 × 10⁻⁴ vs size-matched null |
| **H3/H4** | a band's Gematria value equals its page index / a prime index | exact match count vs null, same bar |
| **H5** | a band's value is a checksum of its page | same bar |
| **H6** | bands are pointers/indices into the ciphertext | same bar; cross-checked against the 86 residual doublets |
| **H7** | band lengths lie on a binary ladder (2^k) | same bar vs base rate |
| **H8** | band positions carry a channel independent of content | KS uniformity, same bar |
| **H9** (addendum) | per-glyph ink intensity is a covert channel | > 4 σ outlier, p < 0.001 vs 10 000 draws, stroke-width-matched; **< 10 book-wide ⇒ anomaly list, not a channel** |
| **B-12 / I-3a** | line geometry is bimodal / carries bits | sep ≥ 2.0 σ **and** ΔBIC > 10; bit-decode p < 0.001 |

### Item 2 — L8 (ledger I-01, I-03; corpus G-02)

| id | hypothesis | threshold (inherited) |
|---|---|---|
| **G-02** | every canon message verifies against `7A35090F`, and the corpus contains exactly one signing key | PASS = `GOODSIG`+`VALIDSIG` for the canonical fingerprint; refuted by a FAIL with no PASSing copy of the same normalised body, or by a second signing key ID |
| **C1–C4** | the instrument works in both directions | C1 GOODSIG · **C2 BADSIG on tamper** · **C3 not-GOODSIG on foreign key** · C4 timestamp survives tamper. All four required |
| **I-01** | `mruzuki`/`cicadeur` `02BD208AFB8AFF75` is toolchain-linked to `7A35090F` | MATCH = identical ordered preference lists + self-sig hash + key-flag/feature bytes; MISMATCH = any ordered list differs; **INDECISIVE** = agreement is the era default of a common client |
| **I-03** | a dated pre-disclosure post exists in a named public archive | HIT = archive-attested, dated before disclosure, URL + dated capture. **Coverage is reported as `months_present / months_in_window`, per archive** — a 404 month is *not* a searched month |

---

## 3. Reproduction — what C3 runs, and where

Everything C3 executes writes **inside `round19/C3/`**. C3 does not overwrite any Round 18
artifact; it re-derives them independently and compares.

| script | what it re-derives |
|---|---|
| `l3/read_bands.py` | all **109** bands (Round 18 stopped at 45) → `l3/bands.json` |
| `l3/band_control.py` | **gate G-A2** → `l3/band_control.json` |
| `l3/intensity.py` | **H9** → `l3/intensity.json` (never run in Round 18) |
| `l3/hypotheses.py` | **H1–H8** → `l3/hypotheses.json` |
| `verify_all_signatures_rerun.py` | the **whole PGP table from scratch**, isolated keyring, all four controls → `PGP-VERIFICATION-TABLE.json` |
| `l8/predisclosure_archives.py` | **I-03** archive coverage + term grep → `l8/predisclosure_archives.json` |

Trust anchor `python3 liber-primus/tests/validate.py` is run **before and after** the lane and its
output recorded in `RESULTS.md`.

## 4. What C3 will not claim, whatever it finds

1. That the 109-band catalogue is the complete set of non-text ink in the book. It is the output of
   the very rejection rule this lane suspects.
2. That a band which reads as noise **is** decoration, unless a measurement shows it — the
   measurement, not the read, carries the verdict.
3. That an archive search returning nothing has cleared anything, or that a month the archive does
   not hold was searched.
4. That any person is Cicada 3301.
5. The words "exhausted", "closed", or "unsolvable" (doctrine R7).
