# Round 44 / WAVE-2 CELL C8 — DELTA-STREAM COMPOSITES k≥7 / OUT-OF-SET FEEDBACK — PREREG

_Dated 2026-11-09, written BEFORE any execution of this cell (no plant, no decode, no sweep).
The only numbers computed in advance are instrument/premise facts, listed in §1: the bars_v3
thresholds from the committed fit, the panel register list, the segment-length table, a
panel-speed benchmark on random arrays, and the ledger-overlap scan. Doctrine binds
(ARMADA-DOCTRINE.md). This file is hash-stamped into `run.log` before the first execution
(the R44 X1 hygiene fix). No `git commit` from this cell._

## 0. What this cell is

R12-C1 bounded k-history feedback/autokey ciphers for **k=2..6 over 7 natural f** — and its own
`not_covered` names the residue verbatim: *"History length k=2..6 only; k>=7 unswept. f
restricted to 7 natural functions … feedback functions outside those … not covered."* It also
carries the X1-noted caveat that its negative is **English-quadgram era** (scored "with the
English quadgram scorer at the then-fixed bar — no register panel, no N-scaled bar"), i.e. the
entire family has NEVER been seen by a register panel (the L7-A hole). This cell runs the
bounded extension:

1. **Lag-k affine composites, k=7..13** (the hinted constants 7 and 13 bound the range): key
   `K_i = (a·s[i−1] + b·s[i−k]) mod 29` — which contains the lag-k **difference** (a=1,b=28)
   and **sum** (a=1,b=1) composites and pure lag-k autokey (a=0,b=1) as cells.
2. **Out-of-set window f**: `K_i = f(s[i−k..i−1])` for f ∈ {**product mod 29**, **max**,
   **min**} — three functions outside R12-C1's 7-f basis.
3. Sources ct / pt / mix (self-referential decode streams, R12-C1's own axis), both
   orientations, continuous + per-segment scopes — adjudicated under **panel-R36**
   (`round19/I2/adjudicate.py` + `data/panels/panel-r36.npz`, 12 registers) against
   **bars_v3** thresholds, fixing the L7-A hole in the original.

## 1. Cited ledger rows + advance-computed instrument/premise facts

- **R12-C1** (negative, 2026-08-17) — not_covered clause 1 (quoted above) is this cell's
  charter; clause 3 is the L7-A caveat this cell carries and fixes for the NEW ground.
  `reopens_if`: "k beyond the swept bound, or a feedback function outside the 21 tested." Both
  reopeners are exercised here.
- **R43 X0 item 1 edge** (`analysis/round43/X0-firewall/ADJUDICATION.md`): the 6/6 blind
  convergence hypothesis ("output-aware chained cipher … the delta-tape") stamps CITED, but
  the adjudication itself lists the residue in §(b): *"Delta-stream composites outside
  R12-C1's f-set — R12-C1 not_covered: 'k≥7 unswept… feedback functions outside those… not
  covered' (item 1 edge)."* This cell is that edge.
- **Overlap scan (done read-only 2026-11-09 before writing this):** R37-C3-U6A-N1-CT/PT cover
  only the 24 R11-N1 cumulative-gematria feedback configs; R41-C1-R14 covers word-sum
  self-keying; R20-N2 covers haplography-vs-autokey; R24-C2 covers skip_by_two under fixed
  keys. None covers lag-k≥7 affine composites or prod/max/min window f. Open ground.
- **Advance-computed facts** (instrument prep, not results): unsolved stream = 12,956 runes,
  55 segments, lengths [262,266,…,76] (min 66; segments 49/50/54 and 32 are < 133);
  panel-R36 registers = EN_MODERN EN_KJV LP1_REAL LATIN OE DE CY EN_HALFVOWEL EN_NOVOWEL
  GREEK HEBREW NORSE; bars in §4; panel batch speed 0.85 s per 812×12,949 (total sweep fits
  in minutes).

## 2. Construction space — exact enumeration (FROZEN)

Decode proceeds left-to-right over a stream C (mod 29 throughout).

**Source stream s:** `ct` → s = C; `pt` → s = P (recovered plaintext); `mix` → s = (C+P) mod 29.
**Orientation:** fwd (stream as-is) and rev (stream reversed before decode; segments reversed
individually in per-segment scope).
**Seed convention (R12-C1's, verbatim):** positions i < k take `K_i = seed`; ct-source is
seed-independent for i ≥ k, so ct decodes use seed 0 and SCORE the tail [k:] only. pt/mix
sweep the 29 all-equal seeds eq0..eq28 (a documented representative probe, NOT exhaustive
over 29^k — same bound as R12-C1). ALL rows score the region [k:].

| family | relation (i ≥ k) | cells | k | orient | src | seeds | rows/stream |
|---|---|---|---|---|---|---|---|
| CT-AFFINE | p_i = (c_i − (a·C[i−1] + b·C[i−k])) mod 29 | a∈0..28 × b∈1..28 = 812 (negation-closed: sign −1 fixed WLOG) | 7..13 | 2 | ct | — | 11,368 |
| CT-WINDOW | p_i = (c_i + sign·f(C[i−k..i−1])) mod 29 | f∈{prod,max,min} × sign∈{−1,+1} | 7..13 | 2 | ct | — | 84 |
| PT/MIX-AFFINE | p_i = (c_i − (a·s[i−1] + b·s[i−k])) mod 29 | (a,b) ∈ {(1,1),(1,28),(28,1),(28,28),(0,1),(0,28)} (the named diff/sum composites + pure lag-k autokey; negation-closed set) | 7..13 | 2 | pt,mix | 29 | 4,872 |
| PT/MIX-WINDOW | p_i = (c_i + sign·f(s[i−k..i−1])) mod 29 | f∈{prod,max,min} × sign∈{−1,+1} | 7..13 | 2 | pt,mix | 29 | 4,872 |

Rows per stream = **21,196**. Streams = 1 continuous (12,956) + 55 segments = 56.
**N_real = 21,196 × 56 = 1,186,976.** Plant streams add ≤ ~110k rows.
**N_bar = 1,500,000 ≥ actual total N** (bars computed at N_bar; conservative).

The full 29×28 affine grid runs on the ct source only (seedless ⇒ exhaustive, the R12-C1
asymmetry); pt/mix get the six pre-registered composite cells. b=0 (pure scaled lag-1) is
excluded by design — not a k≥7 object.

## 3. The Aiming Test

**Q1 — What would a hit look like, and would THIS instrument recognise it?**
A hit = one (family, src, k, cell, orient, seed, stream) row whose decode is non-degenerate
(R38-I2 guard) and whose panel-R36 pmax ≥ the bars_v3 bar at its scored length. Recognizer =
`adjudicate_batch` pmax over the identical decode path. BEFORE any real target, FIVE plants
in the exact shape hunted are pushed through this cell's OWN glue (full config enumeration on
the plant stream, same code path as the real sweep): P1 lag-7 ct difference composite
(a,b)=(1,28), English — **the prompt-mandated lag-7 planted construction**; P2 pt-affine
k=9 (1,1) seed eq4, rev; P3 ct-window prod k=13 sign +1; P4 = P1's construction over LATIN
plaintext (the register axis the original row could not see); P5 a 240-rune English segment
through the per-segment driver. Gate: each plant's planted cell must be recovered exactly
(round-trip on [k:]), be the global argmax of its full-enumeration sweep, cross its bar, and
no non-planted cell may cross. Round-trip asserts additionally cover every family × source
branch (incl. mix) at k=7 and k=13. Any plant failure ⇒ INSTRUMENT-INCOMPLETE, stop.

**Q2 — What measured fact raises this family's prior above the flat rate?**
(a) R43's blind armada: **6/6 blind agents independently converged** on the output-aware
chained / delta-tape hypothesis (X0 ADJUDICATION item 1) — the strongest blind convergence in
that round — and the adjudication's own residue line names exactly this cell's space as the
uncovered edge. (b) The register hole is a measured fact, not a vibe: R12-C1's negative was
adjudicated by the English quadgram scorer alone (its not_covered clause 3), and L7-A measured
that scorer's power at 0.33 Latin / 0.00 vowel-dropped English — so NO feedback-family
negative at any k has ever been panel-adjudicated; this cell's new ground gets panel-R36 from
the start. (c) Honest label: beyond (a)+(b) this is a bounded completeness extension of a
CITED edge; it queues in wave 2 accordingly.

**Q3 — Is the space bounded, and by what?**
Enumerable and enumerated exactly: 21,196 rows/stream × 56 streams = 1,186,976 rows (§2 table
is the complete generator). No sampling anywhere except the pre-registered 29-seed probe
(R12-C1's own documented bound). Estimated wall < 10 min.

**Q4 — The three conditionals** — see `three_conditionals` in §7 / ledger_rows.json.

**Q5 — Kill condition at 10% of budget.**
(i) Premise gate fails (unsolved stream ≠ 12,956 runes, segments ≠ 55, concat(segments) ≠
stream, or `tests/validate.py` not 5/5) ⇒ stop, report UNAVAILABLE-BY-PREMISE. (ii) Any plant
P1–P5 or round-trip assert fails ⇒ stop, report INSTRUMENT-INCOMPLETE (the plant gate IS the
~10% checkpoint). (iii) If the continuous scope projects > 30 min wall, stop and report
partial coverage honestly.

## 4. Thresholds (FIXED IN ADVANCE)

Bar of record: `bars_v3.bar_v3(N_bar=1.5e6, L, "free")` from the committed fit
(`analysis/round34/I1-v3-null/bars_v3.py`), panel-R36 free-relation nodes:

| node L | bar |
|---|---|
| 120 | **15.5204** |
| 240 | **20.8883** |
| 400 | **21.9469** |
| 729 | **25.1583** |

Applied at `Lbar(n)` = largest node ≤ scored length n, clamped to the 120 node for n < 120.
The free-beam null strictly dominates this cell's deterministic single-pass decoder (the beam
has ~n/8 free choices to optimize pmax; this decoder has none), so the free bar is
conservative — the W2-A2 / R44-R1 precedent. A crosser must ALSO be non-degenerate
(`is_degenerate`: mds ≤ 6 or IoC·N ≥ 4.24 rejects). Any bar-crosser is
**FLAGGED-FOR-ORACLE** per `HUMAN-ORACLE.md`, never certified.

**Primary verdict set:** rows with scored length ≥ 120 (plant-validated power regime).
Segments 49/50/54 (lens 66/92/76), segment 32 (len 121 ⇒ n = 121−k < 120 ∀k≥7) and segment 22
at k ∈ {12,13} fall below 120: they are swept and recorded as DIAGNOSTIC-ONLY (the 120-node
bar is applied, but power at those lengths is only measured, not guaranteed — short-L power
diagnostics at L≈120 and L≈66 are reported alongside the plants, no gate).

**Diagnostic null (no verdict role):** 200 shuffles of the unsolved stream (seed 3301)
through the full ct-affine k=7 fwd batch (812 cells each); report the per-draw max-pmax
distribution as the measured deterministic-null gap below the free bar.

## 5. R3 statistics (persistence plan)

Every row persists pmax, preg, pmax_ne, pcon and decrypt IoC·N at sweep time
(`rows.npz`, rebuildable by `sweep.py`); full SWEEPROW records (incl. mds, h2, zl, en) are
persisted for the global top-200 and every crosser — the `adjudicate_batch` fast-path /
`adjudicate`-the-rows-that-matter split the instrument itself documents.

## 6. Coverage / not_covered (committed wording, to be carried into results)

Covered on success: lag-(1,k) affine composites k=7..13, full 29×28 grid on ct source +
6-cell composite set on pt/mix (29 all-equal seeds); window prod/max/min k=7..13, both signs,
all three sources; both orientations; continuous + 55 segments; panel-R36 × bars_v3 at
N_bar=1.5e6.

NOT covered (named now): k ≥ 14; the full affine grid under pt/mix sources (only the 6
composite cells there); arbitrary (non-all-equal) seeds; lag pairs other than (1,k); 3-term
and higher combos; nonlinear f outside {affine-2-term, prod, max, min}; b=0 scaled lag-1;
composite + skip/interrupter hybrids (this decoder models NO rejection loop — the L7-B axis);
scored lengths < 120 at guaranteed power; registers outside panel-R36's 12; R12-C1's
ORIGINAL k=2..6 × 7-f ground is NOT re-adjudicated here (remains an English-quadgram-only
negative per its own row).

## 6b. ADDENDUM (dated 2026-11-09, appended BEFORE first execution — no plant or decode has
run; reason: a plant-gate equivalence predictable from construction algebra alone)

The §3 Q1 clause "no non-planted cell may cross" has one foreseeable benign violation: cells
ALGEBRAICALLY ENTANGLED with the planted construction. Concretely, for P3 (window prod): any
k-window containing a zero rune (F) has prod ≡ 0 mod 29, so K=0 there and BOTH signs decode
identically to the plaintext; a single zero in the stream zeroes k consecutive windows, so the
sign-sibling provably shares long correct plaintext runs (expected zero-window fraction
1−(28/29)^k ≈ 36% at k=13) and may legitimately cross. Frozen handling: a non-planted
crosser on a PLANT stream is acceptable iff its decode matches the planted plaintext on
≥ 25% of scored positions (measured, reported per plant) — i.e. it is a partial
reconstruction of the plant, not a false positive. A non-planted crosser below 25% plaintext
match remains a gate FAILURE (INSTRUMENT-INCOMPLETE). The argmax requirement is unchanged.

## 7. Artifacts

`c8lib.py` (decoders + glue), `plant_gate.py` → `plant_results.json`, `sweep.py` →
`sweep_results.json` + `rows.npz`, `null_diag.json`, `RESULTS.md`, `ledger_rows.json`
(draft rows; coordinator applies — this cell never modifies LEDGER.json), `run.log`
(hash-stamp first line). Pure python3 + numpy, no network.
