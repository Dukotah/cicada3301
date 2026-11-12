# Round 44 / WAVE-2 CELL A4 — CHAINED (CIPHERTEXT-FEEDBACK) CONSTRUCTIONS PARAMETERIZED BY PRESENTATION CHANNELS — PREREG

_Dated 2026-11-09, written BEFORE any execution. Doctrine binds (ARMADA-DOCTRINE.md).
This file is hash-stamped into `run.log` before the first run (R44 X1 hygiene fix)._

## 0. What this cell is

The stated intersection of wave-1's open ground: the **verdict-class construction** (the
output-aware chained cipher — the retained-open member of `VERDICT-OTP-CLASS`) with its
**parameters drawn from the physical presentation channels wave 1 censused** (per-page red
counts, per-page separator counts, page index, red-head section index). A bounded, exactly
enumerable family: ciphertext-feedback lag-k (k=1,2) with a per-page additive offset
`o_p = (σ3·f(ch_p) + s) mod 29` over a small named f-set, both signs, skip-free exact decode,
panel-R36, bars_v3 free at fixed N.

## 1. Cited ledger rows (verified open ground — wording checked in LEDGER.json)

- `R44-P1-RED-SELECTION` (negative) — not_covered: "**chained/output-aware constructions taking
  red as input**". This cell is exactly that reading for the red count channel. Open.
- `R44-P1-RED-KEYPARAM` (negative) — not_covered: "**chained constructions parameterised by
  red**"; also "dot-block counts ... untested as keys" (dot counts stay not_covered here too:
  only 3 pages carry dot blocks, no per-page channel exists). Open.
- `R44-P1-RED-CENSUS` (measured) — source of the per-page red channel (`channel.json per_page
  r_p`) and the red-head section map.
- `R44-P3-APOSTROPHE-NUMERAL-CENSUS` (measured) — not_covered: "Any keyed/derived reading that
  consumes these ... positions as **parameters into another construction**". The separator
  channel as per-page key parameters was never consumed by any construction.
- `R44-R1-RESET-SWEEP` (negative) — its transition model is "key-pointer reset ... position-
  indexed substitution"; chained/output-aware constructions are OUTSIDE it (its decoder cannot
  represent them); its per-page-parameter axis used only generator offsets, not presentation
  channels. This cell is the construction class R1's conditionals exclude.
- `VERDICT-OTP-CLASS` (open) — the chained (output-aware) member is the retained-open branch:
  `L7-C-G3-FLOOR-EXTENDED` measured that the doublet-deficit floor argument HOLDS across 9
  registers ("the key must be output-aware"), which is precisely a prior FOR ciphertext-feedback.
- `R12-C1` (negative) — nearest covered neighbour, and NOT this cell: plain ct-feedback k=2..6
  with 7 natural f × sources × signs, but (its own not_covered, item 3) scored "with the English
  quadgram scorer at the then-fixed bar — **no register panel, no N-scaled bar**", and with
  CONSTANT seeds only — no per-page offsets, no presentation parameters, and no k=1. The
  R11-N1 reopens_if precedent ("Reopen under the repaired instrument") applies.
- Prior art for the decode side (cited by the cell brief): the dense mod-29 linear-feedback
  gate `analysis/campaign18_skip/ctfeedback_coeffs.py` (2026-07 auditor loop,
  `analysis/AUDITOR-LOOP-2026-07-28.md` table row "Non-additive linear ciphertext-feedback").
  Minimal fresh decode glue is built here (own-glue rule); that file is prior art only.

Not re-run: R12-C1's swept ground is k=2..6 × its 21 (f,source) combos under the LEGACY
English-only scorer — this cell's k∈{1,2} ± unit-coefficient family under panel-R36 with
per-page channel offsets is inside R12-C1's not_covered (register axis + parameter axis),
and k=1 was never in its grid at all.

## 2. The Aiming Test

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = some unsolved page (tier A) or the book head (tier B) decodes, under a family member,
into a panel-R36 register. Recognizer = panel-R36 pmax (12 registers) through the identical
sweep glue, vs bars_v3 'free' at the cell's fixed N. Proof: two plants ENCIPHERED with family
constructions through this cell's own encipher glue and pushed through the IDENTICAL sweep
code path must be recovered exactly, be the grid max, and clear the bar — gate before any real
decode (R42 X1 rule). No verdict of any kind without the gate.

**Q2 — What measured fact raises the prior?**
(i) `round18/L7-redteam` / ledger `L7-C-G3-FLOOR-EXTENDED`: min_d Pdp(d) ≥ 0.972% across 9
registers vs LP2's observed 0.664% — "the key must be output-aware" survived the register
red-team. Ciphertext-feedback IS output-aware; it is the construction class that measured fact
points at, and `VERDICT-OTP-CLASS` keeps open. (ii) The parameters are MEASURED physical
quantities from wave 1's census files (`round44/P1-red-ink/channel.json`,
`round44/P3-punct-channels/channels.json` + its committed extraction glue), not lore: per-page
red counts (13 pages non-zero), per-page separator counts, the red-head section map — the
channel direction the pp49–51 loader blind-spot proved can hide a payload (R43 SYNTHESIS §4).
(iii) R12-C1's not_covered makes every existing ct-feedback negative English-only.

**Q3 — Is the space bounded, and by what?**
Enumerable, exactly. **Collapse lemma** (stated in advance, verified by assert in the code):
for a FIXED page p, the per-page offset `o_p = (σ3·f(ch_p)+s) mod 29` ranges over all of Z_29
as s sweeps 0..28, for every (ch, f, σ3). Therefore:
- **Tier A (page-local, COMPLETE cover of the family at page granularity):**
  (σ1,σ2) ∈ {±1}² × k ∈ {1,2} × scope ∈ {page, continuous} × o ∈ Z_29 × 55 pages
  = 4·2·2·29·55 = **25,520 cells**. Any page that decodes under ANY family member decodes in
  this grid (lemma). (Page 0's scope pair is structurally duplicate: 232 duplicate rows, kept.)
- **Tier B (book-wide joint-consistency over the head):** full nominal family
  (σ1,σ2) 4 × k 2 × scope 2 × ch 5 × f 3-effective × σ3 2 × s 29 = **13,920 constructions**,
  decoded over head-729 (= pages 0+1+2 exactly, 262+266+201=729), deduped by decoded stream,
  all adjudicated. Tier B can only fire if one (ch,f) family explains pages 0–2 jointly.
Total adjudicated real cells ≤ 39,440. **N_bar = 50,000** (fixed upper bound).

**Q4 — The three conditionals of any negative here:**
1. *key space:* per-page additive offsets from the named channel×f×sign×shift family — which,
   by the collapse lemma, tier A covers as ALL of Z_29 per page; ±1 (unit) coefficients on
   c_i and c_{i−k} only; lag k ∈ {1,2}; forward reading direction only.
2. *transition model:* exact skip-free ciphertext-feedback decode
   `p_i = (σ1·c_i + σ2·c_{i−k} + o_p) mod 29` with zero-fill at scope starts (i<k ⇒ feedback
   term 0), scope ∈ {per-page restart, book-continuous}. NOT represented: multiplicative
   coefficients a∉{±1} (D-04's ground), k≥3, plaintext-feedback (R37-C3-U6A-N1-PT's ground),
   mixed pt/ct sources, constructions with an ADDITIONAL keystream + rejection loop (a
   ct-feedback key needs no pointer, so no skip relation exists to drift — but a hybrid
   keystream+feedback cipher is outside this model), reversed streams.
3. *adjudicator register:* panel-R36 (12 registers), pmax, vs bars_v3 'free' at N_bar=50,000.

**Q5 — Kill condition at 10% of budget:**
The plant gate IS the first ~1% of compute. If either plant fails any of its three clauses
(exact recovery / grid-max / pmax ≥ bar) → **INSTRUMENT-INCOMPLETE**, stop, no verdicts
(`run_sweep.py` refuses to run without `gate.json: passed`). Additional kill: if the collapse-
lemma assert fails (some (ch,f,σ3,s) offset outside Z_29 coverage — impossible by arithmetic,
checked anyway), stop and re-derive the enumeration.

## 3. Fixed instrument + thresholds (BEFORE any run)

- **Decode (FIXED):** for global position i on page p (in-scope index t):
  `p_i = (σ1·c_i + σ2·fb + o_p) mod 29`, fb = c_{i−k} within the scope stream (page-restart or
  continuous over the 12,956-rune unsolved stream), fb = 0 where t<k.
- **Offsets (FIXED):** `o_p = (σ3·f(ch_p) + s) mod 29`;
  channels ch (values derived from the cited wave-1 files during PREREG drafting; asserted in
  code against those files): `r_p` (red rune count, P1 channel.json per_page), `s3_p` (3-symbol
  separator count per page, via P3's own committed parse glue over data/relikd/*.txt, bucketed
  by P1 page_starts), `s4_p` (all separators incl. word dots, same glue), `page` (index 0..54),
  `sec` (red-head section index 0..12 from the section starts [0,3,6,7,8,15,23,27,33,39,40,53,54]
  — the red-head map of P1/R1);
  f-set (named): identity, mod29, prime-index (f(v) = (v+1)-th prime mod 29, P(0)=2),
  cumulative (inclusive Σ_{q≤p} ch_q mod 29). identity ≡ mod29 under mod-29 arithmetic:
  3 effective f, 4 named (recorded, deduped).
- **Adjudicator:** standing panel-R36 (`round19/I2/adjudicate.py`, `data/panels/panel-r36.npz`),
  `adjudicate_batch` pmax; crossers re-checked with full `adjudicate` and the standing
  degenerate guard. Doctrine-R3 statistics persisted for every page-best row and every crosser.
- **Bars (bars_v3 'free', N_bar = 50,000, computed and frozen now):**
  - tier A, page L_cap = largest of {120,240,400,729} ≤ page length, floor 120 (the R44-R1
    protocol): **bar(120) = 13.7082**, **bar(240) = 18.3740** (page lengths 66–277 ⇒ only these
    two nodes occur: 20 pages at 120, 35 at 240).
  - tier B, head-729: **bar(729) = 22.6951**.
- **Crosser rule:** non-degenerate AND pmax ≥ bar ⇒ **FLAGGED-FOR-ORACLE** per HUMAN-ORACLE.md,
  never certified. Pre-registered diagnostic for any tier-A crosser (descriptive only): list the
  (ch,f,σ3,s) family members whose o_p equals the crossing offset on that page.

## 4. Positive controls (through THIS cell's own glue, gated BEFORE the sweep)

- **G1 (tier-A glue):** pages 10 and 20 of a COPY of the real corpus replaced by known-English
  plaintext (the F5b-T LP-register control texts of record, as in R44-R1) ENCIPHERED with
  θ* = (σ1=+1, σ2=−1, k=1, scope=page, o_p from ch=s3, f=prime-index, σ3=−1, s=17) by this
  cell's encipher glue. The IDENTICAL tier-A sweep runs on those pages (with real neighbour
  pages supplying continuous-scope context). PASS iff on BOTH pages: planted cell decode ==
  plaintext exactly, planted cell is the grid max (its scope-twin may tie), pmax ≥ bar(L_cap).
- **G2 (tier-B glue):** pages 0–2 of a copy replaced by control English enciphered with
  θ** = (σ1=−1, σ2=+1, k=2, scope=continuous, ch=r, f=cumulative, σ3=+1, s=5). The IDENTICAL
  tier-B enumeration (all 13,920 θ) runs on the planted head. PASS iff the global argmax lies
  in θ**'s decoded-stream equivalence class, recovery exact, pmax ≥ 22.6951.
- **Differential (report-only):** G1 page under wrong offset o+1 and wrong feedback sign:
  recovery and pmax reported (expected ≈ chance / noise).

## 5. Budget / N accounting

Real adjudicated cells: 25,520 (tier A) + ≤13,920 (tier B) = ≤39,440 ≤ N_bar 50,000. Plants:
2 pages × 464 + ≤13,920. Pure python3 + numpy, no network, no image work (wave-1 census files
are the artifacts of record). Expected minutes.

## 6. Outputs

`chained.py` (glue), `plant_gate.py` → `gate.json` + `plant_results.json`, `run_sweep.py` →
`results.json`, `RESULTS.md`, `ledger_rows.json`, `run.log` (hash-stamped). LEDGER.json NOT
modified.

## Appendix — fixed channel values (inputs, derived from the cited wave-1 files)

- `r_p` (p=0..54): 13,0,0,19,0,0,9,14,10,0,0,0,0,0,0,10(+title 9 on p15 per census: the value
  used is channel.json per_page r_p verbatim — asserted in code, not retyped here for pages
  beyond the spot-checks p0=13, p3=19).
- `s3_p` (p=0..54): 2,5,1,4,4,3,3,5,4,2,4,6,6,2,3,8,3,5,2,3,1,1,3,2,3,2,2,4,3,4,5,6,1,4,5,2,1,
  3,5,3,6,3,3,5,2,3,3,4,7,0,1,3,2,2,0 (sum + solved-tail remainder == 180 global, asserted).
- `s4_p`: computed by the same glue (sum 2,910 over unsolved pages; global 2,911+180 tokens),
  asserted against channels.json totals.
- `sec_p`: step function over the section starts above.
Code asserts: relikd rune stream == canon prefix (12,956), page_starts/page_lens == P1
channel.json, channel sums == the wave-1 global totals. Any assert failure ⇒ stop (Q5).

### Addendum 0 — 2026-11-09, before first execution (wording fix only)
Appendix s4 line: `sep4_len` = 2,911 is the count of ALL separator tokens (word dots + the
180 3-symbol separators INCLUDED); the in-code assert is `sum(s4_p) + solved-tail == 2,911`.
No threshold or enumeration changed.
