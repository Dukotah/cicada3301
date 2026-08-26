# T2 — THE DENSE PAGES · RESULTS

_Round 19, transcription phase. Pre-registered in [`PREREG.md`](PREREG.md) before any
measurement was scored; no threshold was edited after a result was seen. Binding:
[`ARMADA-DOCTRINE.md`](../../../ARMADA-DOCTRINE.md)._

**Trust anchor — before and after:** `python3 liber-primus/tests/validate.py` →
`ALL VALIDATIONS PASSED — rig reproduces known solves.` (5/5: 01, 03, 05, 06, 14.)

---

## 0. Headline — five numbers

| question | answer |
|---|---|
| **the indel bound** (T3's stated gap) | Canon can contain **k ≤ 1 insertion and k ≤ 1 deletion at 95 % confidence**, from **zero** surviving candidates over **13,121** tested positions at measured localisation power **0.990 / 0.974**. Charging *every* unadjudicated flag to canon gives the crude ceiling **≤ 26**, all on the unsolved stream |
| **A-01 (Round 9 Track TEMPLATE)** | **COMPLETE.** Independent per-slot agreement with canon **0.9973** over 13,121 slots on **604/604 lines** — up from stage 2's 0.9693 over 5,207 glyphs on 232 lines |
| **coverage of Round 10's 61.6 % blind spot** | **fully covered.** 604/604 lines, **13,121 / 13,136 rune slots = 99.89 %**. The 15 unadjudicated slots are named: illuminated initials |
| **frontB** | **SETTLED, and canon is upheld.** Control **1.0000** on the decryption-proven LP2 pages (frontB's forced instrument: 0.129). Pages 45–54 read at **1.0000 over 1,992 slots**, with **zero** substitution and **zero** surviving indel candidates |
| **A-05 / B-23 — the 19 lines** | **all 19 read and adjudicated. Canon is correct on every one**, in count *and* position. The Round 8 diffs are its own instrument: 10/19 a line-alignment slip, 9/19 a dot-extraction failure |

**One sentence.** Forced alignment — taking the token *count and order* from canon and
letting the ink choose the cut points — passes its positive control at **1.0000** where
frontB's forced re-segmentation scored 0.129, and it reads the dense OTP pages perfectly,
so the pages that carried the coverage hole now carry the strongest per-rune audit in the
repository.

---

## 1. Why this worked where frontB did not

frontB forced a **number of pieces** and let the cuts fall where they may. T2 forces the
**identity sequence** and lets the ink choose the cuts. The difference is not cosmetic:
a count can be forced onto ink that does not separate, but it cannot manufacture identity —
which is exactly what frontB's own results said. Forced alignment never has to discover the
segmentation, so the dense pages stop being special.

Three inherited measurements made it work, and none of them is new to this lane:

- **Round 8** — the median glyph has a **pixel-identical twin** (NN Hamming 0.0000), so
  templates are exact and matching is a lookup.
- **round12/frontB** — the **height classes**: rune bodies 95–132 px, ornaments 41–91 px,
  separator dots 7–10 px. frontB measured these and then did not use them as a *mask*.
- **round18/L4** — the fitted glyph-width table, externally validated at **corr = +0.879**
  against `BabelStoneRunicBeorhtnoth.ttf`. T2's template widths reproduce its ordering
  independently (I narrowest at 10 px, EA widest at 87 px; L4: 0.37 and 1.85).

### 1.1 The segmentation gap was an artifact of not masking

frontB reported 30–41 geometry boxes per line on p45 against canon's 21–25 and concluded the
dense lines could not be segmented. With the height-and-column mask applied first:

| | count-exact lines | residual |
|---|---:|---:|
| R9 raw-band template DP | 232 / 604 (38.4 %) | — |
| **T2 masked components** | **530 / 604 (87.7 %)** | **83 mis-localised glyphs over 13,136 = 0.63 %** |

`linemap.py` maps **57/57 pages and 604/604 canon lines**. The relikd↔canon page offset is
confirmed and pinned: identity for p0–p49, **p50 is the runeless illustration page**, p51–p55
→ segments 50–54, and segments 55/56 (LP2 pages 56/57) come from the scream314 vendor assets
C3 identified.

---

## 2. The instrument and its controls

`t2lib.py` (forced alignment + forward/backward), `probe.py`, `indel.py`. The per-column
mismatch and every DP constant are **verbatim R9** (`dy ∈ {−3,−1,0,1,3}`, blank-skip
`colink·3.0 + 0.5`, per-glyph prior `+6.0`), and the 29 templates and the class→rune bijection
are R9's stored artifacts. **No new classifier was built** — T1 owns that instrument, and its
per-glyph reader and T2's line-level forced alignment are complementary: T1 needs the
components to be right, T2 takes the count from canon and is therefore immune to merges.

### C1 — ground-truth control (the registered gate)

LP2 pages 56 and 57 — the only pages whose plaintext is known **by decryption** *and* whose
typeface is the LP2 face of pages 0–54.

> **loo_agreement = 1.0000 (178 / 178 adjudicated slots).** Gate was ≥ 0.90.

| instrument | control on the LP2 face |
|---|---:|
| round12/frontB forced re-segmentation | 0.129 |
| round19/C3 band reader (LP2 face) | 0.9556 |
| Round 9 template DP, native regime | 0.980 |
| **T2 forced alignment** | **1.0000** |

Per the coordinator's calibration note, a claim that canon is wrong needs a control tighter
than the 0.9556 at which C3's reader itself errs. **T2's control is 1.0000, above that bar** —
so T2 is entitled to speak about canon, and it reports that canon is right.

**False-positive rate:** on those 178 slots, **0 slots have `delta > 0` at all**. τ is
therefore fixed at 0 and applied unchanged to every other page. (LP1 pages are excluded
throughout: they are a different typeface, outside the template domain, and pooling them is
what made Round 18's 44.2 % and C3's 53.95 % uninterpretable.)

### C2′ — ink-splice plant (the control frontB never ran)

Real page ink, one slot's pixels physically overwritten with a different rune, probe run with
**uncorrupted** canon tokens.

| stratum | n | detection | recovery |
|---|---:|---:|---:|
| solved-LP2 | 168 | **1.0000** | **1.0000** |
| **dense-45-54** | **189** | **1.0000** | **1.0000** |
| pages-0-44 | 188 | **1.0000** | **1.0000** |

29.5 % of (slot, rune) pairs were excluded because the splice would not fit the erased span
and would have damaged a neighbour — stated as coverage, not hidden.

**This is the number that makes the silence mean something.** A perfect agreement rate alone
is consistent with an inert probe; 545/545 recovery of a planted foreign glyph is not.

### C5 — indel plants

A planted **canon** length error (no ink surgery): drop a token from the forced sequence
(canon pretending to miss a rune the ink has), or insert one (canon pretending to carry a rune
the ink lacks). One of each on every line, n = 604 each.

| planted error | stratum | n | fired | **localised to the right position** | rune named |
|---|---|---:|---:|---:|---:|
| canon missing a rune | solved-LP2 | 10 | 1.0000 | **1.0000** | 1.0000 |
| canon missing a rune | **dense-45-54** | 91 | 1.0000 | **0.9890** | **1.0000** |
| canon missing a rune | pages-0-44 | 503 | 0.9980 | **0.9901** | 0.9940 |
| canon missing a rune | *pooled* | 604 | 0.9983 | **0.9901** | 0.9950 |
| canon carrying an extra rune | solved-LP2 | 10 | 1.0000 | **1.0000** | — |
| canon carrying an extra rune | **dense-45-54** | 91 | 1.0000 | **0.9780** | — |
| canon carrying an extra rune | pages-0-44 | 503 | 0.9960 | **0.9722** | — |
| canon carrying an extra rune | *pooled* | 604 | 0.9967 | **0.9735** | — |

The dense pages are **not** the weak stratum for this instrument — they match or beat
pages 0–44 on both plants. That is the reversal of the situation every prior audit reported.

---

## 3. The indel bound — T3's gap, closed

T3: *"every model here is substitution-only and preserves n = 12,956. Insertions/deletions and
segmentation errors are not bounded at all."*

The deletion and insertion probes fall straight out of the forward/backward tables:

```
delta_del[j] = C_canon − min_x ( alpha[j][x] + beta[j+1][x] )        > 0 ⇒ canon has an EXTRA rune
delta_ins[j] = C_canon − min_{r,x} ( alpha[j][x] + m_r[x] + 6 + beta[j][x+w_r] )  > 0 ⇒ canon MISSES one
```

**Threshold from the decryption-proven pages:** their worst values are `max_del = −1860` and
`max_ins = −212` — both strictly negative, i.e. on pages canon is *proven* right, canon's rune
count is strictly the cheapest explanation of the ink. τ = 0 for both.

| stratum | lines | flagged EXTRA-rune | flagged MISSING-rune |
|---|---:|---:|---:|
| solved-LP2 | 10 | **0** | **0** |
| pages-0-44 | 503 | 1 | 23 |
| dense-45-54 | 91 | 0 | 2 |

**All 26 flags adjudicate to SEG** (`adj_indel.py`). The decisive image-side test is one the
line map already computes: on 20 of the 26 the image carries **exactly** canon's number of
rune-body components, so no rune can be missing and none extra — the delta is non-rune ink
inside the band. On the rest the count mismatch runs in the *opposite* direction to the flag
(a merge, where the DEL probe fires), which is also not a canon error.

### 3.1 The mechanism, measured

Both remaining substitution candidates and 21 of the 26 indel flags sit on a **mid-size mark
class**: ink 35–94 px tall — between a separator dot and a rune body — mostly thin vertical
ticks (h ≈ 50, w ≈ 5–19). `orphan.py` inventories **487 of them across 349 of 604 lines**,
on essentially every page.

**They appear on the decryption-proven pages too (3 on p56, 1 on p57), where canon omits them
and the decrypt is correct.** So this mark class is **proven non-textual by decryption**, and
canon is right not to transcribe it. That is a stronger statement than any consistency
argument could give.

The clincher (`variant.py`) — raise the band mask to rune bodies only (h ≥ 95) and re-run:

| mask | control loo_agreement | substitution disagreements | lines with an indel flag |
|---|---:|---:|---:|
| **h ≥ 40 (operating point)** | **1.0000** | 35 | 26 / 36 |
| h ≥ 95 (rune bodies only) | 0.9775 | 58 | 6 / 36 |

Raising the mask removes 20 of the 26 flags — confirming the mechanism — but **breaks the
control**, because the same 35–94 px class also contains genuine split strokes of real runes.
No single height threshold zeroes both. That is a real and quotable limit of component-height
stripping at this render, and it is why the operating point is the one whose control is exact.

### 3.2 The bound

Zero surviving candidates over **13,121 tested positions**, at the measured localisation power
above (95 % lower bounds 0.9822 and 0.9607):

> **k ≤ 0.74 missing runes and k ≤ 0.93 extra runes at 95 % confidence — i.e. k ≤ 1 of each.**
>
> Crude ceiling, charging *every* flag to canon without adjudication: **≤ 26 indels**, of which
> **24 on pages 0–44 and 2 on pages 45–54** — all on the unsolved stream, none on a solved page.

**Why this matters more than the substitution bound.** T3 measured that the *decode* channel
is the fragile one: at k = 200 substitutions 17 % of correct-key decodes derail, at k = 450
50 %, and `max_skip` can only run the key ahead, never recover sync. An indel breaks sync
outright, so the indel curve is far steeper than the substitution curve — a single
uncorrected insertion misaligns every downstream rune. **T2's result is that the input to
that curve is 0, bounded at ≤ 1.** The steepness is real but there is nothing to feed it.

---

## 4. A-01 — Round 9 Track TEMPLATE, completed

Stage 2 stopped at 96.93 % over 5,207 glyphs on the **232 count-exact lines (38.4 %)**, and its
`FINDINGS.md` named the honest limit: *"only 38.4 % of lines are glyph-diffable, and the OTP
pages that could actually reopen the case are exactly where the independent read is weakest."*

**Completed here:**

| stratum | lines | slots | per-slot agreement with canon |
|---|---:|---:|---:|
| solved-LP2 (ground truth) | 10 | 178 | **1.0000** |
| **dense-45-54** | **91** | **1,992** | **1.0000** |
| pages-0-44 | 503 | 10,951 | 0.9968 |
| **all** | **604** | **13,121** | **0.9973** |

**Coverage: 13,121 / 13,136 = 99.89 %.** The 15 unadjudicated slots are **illuminated
initials** and are named, not silently dropped (§4.2).

### 4.1 Segmentation vs rune identity — kept apart, as registered

Of 35 slot-level disagreements at τ = 0:

| class | n | what it is |
|---|---:|---|
| **SEG** | 33 | line count mismatch, or a run of ≥ 2 adjacent flagged slots — the alignment slipped |
| **CONF** | 0 | a known shape-confusable family (U↔Y, O/A/AE, L↔W, C↔I) |
| **ID** | 2 | isolated slot, count-exact line, τ exceeded |

Both **ID** cases — page 4 gline 51 slot 15 (canon I, probe L) and page 40 gline 452 slot 2
(canon F, probe X) — coincide **exactly** with an insertion flag at the same position, and
both lines are count-exact. Cropping gline 452 shows the cause directly: an unrecorded
**double-tick mark** between the separator and the next rune. They are therefore **SEG**, and
**zero disagreements in the corpus have the signature of a real rune-identity error in canon.**

Pages 45–54 contribute **0 SEG, 0 CONF, 0 ID.**

### 4.2 Two errors found in the Round 9 write-up (doctrine R6)

**FOUND-ERROR 1 — R9's "solved pages" are not solved.** `retranscribe/FINDINGS.md` bucket B
reports three confusable mis-reads on "p29, p34, p35" and argues *"these pages are
cryptographically solved, so canon is proven correct by decryption."* **They are not.** LP2
pages 0–54 are the unsolved 12,956 runes (`PROBLEM.json`). The only LP2 pages solved by
decryption are **56 and 57** (canon segments 55/56, vendor `73.jpg` / `74.jpg`). R9's bucket-B
argument has no ground truth behind it. Its *conclusion* survives — T2 reads all three pages at
canon — but its stated reason does not.

**FOUND-ERROR 2 — R9's bucket A is diagnosed, not an "edge effect".** R9 reported *"15 loci,
all pinned at position 0, x = 601 — a mechanical DP edge effect."* x = 601 is the left edge of
an **illuminated initial**: an oversized decorative first glyph, h 497–608 px against a 113 px
rune body, which no 108–120 px template can match. There are **15 such line-starts** in the
corpus. T2 excludes and names those slots; doing so is what lifted the control from 0.9500 to
**1.0000**.

---

## 5. A-05 / B-23 — the 19 lines, read

### 5.1 The mark classes, measured first

Round 8 counted **every** component with h < 30 as one separator dot. `sepmeasure.py` shows
the ink is cleanly bimodal and that this is wrong:

| class | clusters | x-span | what it is |
|---|---:|---|---|
| single dot | **2,767** | 9–10 px | the word separator `-` |
| lozenge | **187** | 24–60 px, fragmenting into 3/4/10/13/23 components | the sentence mark `.` |

A single `.` therefore contributed **up to 23** to Round 8's dot count. This also confirms
L4's fitted advance widths from the other direction: `.` at 1.82 against `-` at 0.32.

### 5.2 Whole-book separator audit — 604 lines, not 170

| | canon | image |
|---|---:|---:|
| `-` | 2,764 | **2,767** |
| `.` | 183 | **187** |

- lines with exact separator **counts**: **582 / 604 (96.36 %)**
- lines with exact separator **positions** (per gap between forced-aligned runes): **580 / 604 (96.03 %)**
- **control (segments 55/56, proven by decryption): 10 / 10 positionally exact**

Of the 24 lines with a positional disagreement, **15 are at gap 0** and most of the rest within
two gaps of the line end — i.e. **line-boundary attribution**, because canon breaks lines
semantically and the image breaks them typographically (the same effect C3 documented). B-23's
coverage of 170/604 lines is superseded by 604/604.

### 5.3 The 19 shortlisted lines — verdict

**All 19 reproduce canon exactly, in count and in position.** `out_sep19.json`.

| gline | page | canon | T2 image read | Round 8 diff |
|---|---|---|---|---|
| 75, 83, 93, 123, 127, 130, 133, 153, 158 | 6–13 | matches | matches | +1,+3,−1,+1,−1,−2,+7,−1,+1 |
| 466, 475, 495, 515, 526 | 41–46 | matches | matches | +1,+1,+1,+3,+4 |
| 536, 538, 545, 550 | 47–48 | matches | matches | −5,−4,−6,−5 |
| 554 | 51 | matches | matches | −3 |

The Round 8 diffs are its own instrument, in two distinct failure modes (`sep19_proof.py`):

- **10 / 19 — a line-alignment slip.** Round 8's dot count for the image row equals canon's
  separator count at a *nearby* canon line (d ∈ −4…+4). Its count-based DP aligned 599 of 604
  lines; T2's mask-based map aligns 604/604.
- **9 / 19 — a dot-extraction failure.** Four of these (glines 536, 538, 545, 550, all on
  dense pages 47–48) Round 8 measured at **zero dots**. Cropping gline 545 shows **six**
  separator dots plainly, exactly matching canon's six `-`. Its `h < 30` extraction from
  `glyphs2.npz` simply failed on those rows.

Round 11's S2 finding stands untouched: separators are typography, not a hidden channel. This
lane only establishes that the *count and placement* are right.

---

## 6. Disagreements in the form T3 needs

| class | confirmed | crude ceiling (every flag charged to canon) | on unsolved pages 0–54 | on solved pages |
|---|---:|---:|---:|---:|
| **substitutions** | **0** | 2 (pages 4, 40) | 2 | 0 |
| **insertions / deletions** | **0** | 26 (24 on pp 0–44, 2 on pp 45–54) | 26 | 0 |
| **separator count/position** | **0** | 24 lines, 15 of them line-boundary attribution | 24 | 0 |

Every ceiling number lands on the unsolved stream and none on a page proven by decryption.
Feeding T3's own curves: 2 substitutions is **two orders of magnitude** below its k = 200
first-derailment point, and the indel count — the error class it could not bound and the one
that breaks decode sync outright — is **0, bounded at ≤ 1**.

**Crypto impact: none.** No ciphertext change is warranted; the doublet rate, IoC and the
12,956-rune identity are untouched.

---

## 7. Bounds, not verdicts — what is *not* covered

Per doctrine R7 and PREREG Q4, the three conditionals on every negative here:

1. **Hypothesis space swept.** Single-token substitutions at all 13,121 slots (complete,
   29-way), single insertions at all 13,725 gap positions, single deletions at all 13,121
   slots, and separator count/placement on all 604 lines. **Not covered:** multi-rune
   correlated errors, transpositions, and whole-line omissions — a line canon omits entirely
   would not appear, because the line map is driven by canon's line inventory. The page-level
   count check (§1.1, residual 0.63 %) constrains but does not eliminate this.
2. **Transition model.** Left-to-right, non-overlapping, canon-ordered placement with the R9
   constants. It **cannot** represent overlapping or kerned glyph pairs, ligatures, reordering,
   or a rune rendered outside the template's size.
3. **Adjudicator register.** Pixel mismatch against the R9 template library at *this* render
   (2400×3600, Ghostscript→ImageMagick q92). Its blind spot is the confusable families, which
   are reported as a separate column and were **0 at τ = 0**.

**Ground-truth width.** The control rests on **180 runes** — the only LP2-face text proven by
decryption in existence. The 1.0000 is exact but narrow; a second solved LP2 page would tighten
it, and nothing else would.

**What render would strengthen this.** Not a higher DPI — at 2400×3600 the median glyph already
has a pixel-identical twin, and the residual is *class* ambiguity in the 35–94 px mark band, not
resolution. What would settle the residual is the **publisher's vector/font source**, which
would separate a split rune stroke from a typographic tick by construction rather than by
height threshold. Absent that, §3.1's table is the honest ceiling.

**Reopens if:** a second LP2-face page is solved by decryption and T2's probe disagrees with it;
or the mid-size mark class (`out_orphan.json`, 487 marks) is shown to carry information, which
this lane did not test and which is a separate question from transcription fidelity.

---

## 8. Artifacts

| file | what |
|---|---|
| `t2lib.py` | line geometry, masking, templates, forced alignment, forward/backward |
| `linemap.py` → `out_linemap.json` | 57/57 pages, 604/604 canon lines, illuminated-initial detection |
| `probe.py` → `out_probe.json` | forced alignment + LOO substitution probe, all 604 lines |
| `score.py`, `adjudicate.py` → `out_a01.json` | C1 gate, strata, SEG/ID/CONF adjudication |
| `splice.py` → `out_splice.json` | C2′ ink-splice plant, 545 splices |
| `indel.py`, `score_indel.py` → `out_indel.json`, `out_indel_score.json` | indel probes, plants, the bound |
| `adj_indel.py` → `out_indel_adj.json` | adjudication of all 26 indel flags |
| `orphan.py` → `out_orphan.json` | the 487-mark mid-size class |
| `variant.py` | the decisive h ≥ 95 mask test |
| `sepmeasure.py`, `separators.py` → `out_separators.json` | mark classes; 604-line positional audit |
| `sep19.py`, `sep19_proof.py` → `out_sep19.json` | the 19 A-05/B-23 lines, adjudicated |
| `recon.py` → `out_recon.json` | page↔segment map, mark-class reconnaissance |

Reproduce: `python3 linemap.py && python3 probe.py && python3 adjudicate.py &&
python3 splice.py && python3 indel.py && python3 score_indel.py && python3 adj_indel.py &&
python3 separators.py && python3 sep19.py`

`crop_*.png` and `dbg_*.py` are rebuildable diagnostics (`crop_line.py <gline>`) and are not
results.
