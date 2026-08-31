# Round 24 — candidate slate + Gate-#1 (anti-repeat + feasibility, refute-by-default)

_Drafted 2026-08-30 by the Round-24 coordinator. Binding: `../ARMADA-DOCTRINE.md`.
PLANNING ONLY — no cryptanalysis executed here. Every candidate below is run through
Gate-#1 (four sub-tests, KILL unless ALL clear). This doc records the gate verdicts and,
for survivors, a pre-registration sketch._

## The board Round 24 inherits (why this is hard)

- **Round 23 A2 shipped a clean, control-validated NULL** (printed-line-geometry acrostic).
  That was the *last roadmap-named reopener*. Every Phase 1–5 lens in
  `NEXT-ARMADA-ROADMAP.md` has now been read at least once at the tested resolution.
- Mechanism exclusions that kill most "new cipher" ideas outright:
  - **Doublet-deficit (0.66% vs 3.45%)** — the ONE structural signature; the differences
    `d=cᵢ−cᵢ₋₁` are flat random with a single hole at zero (IoC·N 1.024, entropy 4.83).
    No standard construction reproduces it; it is a hardening artifact, not a crack.
    (`analysis/DOUBLET-INVESTIGATION.md`.)
  - **Autokey POSITIVELY refuted** (not "fails to decrypt"): 28 nonzero difference-diagonals
    flat (cv 0.061) where autokey needs cv≈1.0; z=−17.25 on d=0 only. R20-N2 hardened it
    against ~20 doublet-site haplography merges.
  - **Filter is MACHINE, no per-line scope (power 1.000); lag-2..8 bleed ≤1.70% @95%**
    (`analysis/round17/P4_filter/RESULTS.md`). Pad entropy is not human-produced.
  - **Message-existence UNDECIDABLE** from ciphertext (LP2 inside both English-under-pad and
    filler-under-pad bands on all 10 metrics).
  - **English-only power caveat (R18 L7-A/B)** — every historic negative is English-only and
    covers one rejection-loop; the R19 nine-register beam + panel-max bar repaired this, and
    every lane since must score on rune indices under the drift-tolerant beam.
- Transcription audited clean (single 2017 root, but image-corrected + functionally correct on
  all solved pages). Number channel (R11 N1–N5, S1–S2), turtle/spatial (R22-B), koans-as-ops
  (R22-C), art-as-data drop-caps (R22-D), self-embedded incl. line geometry (R22-A + R23-A2) —
  all NEGATIVE.
- The only technically-live branches — PRNG/seed tail (needs core-days) and `/dev/urandom`
  (needs the pad to leak) — are OUT OF SCOPE for an in-session lane by rule.

The bar for a Round-24 survivor is therefore brutal: it must be a representation/test/artifact
that is (a) not in the ledger, (b) not killed by a mechanism exclusion, (c) anchorable with a
plant→recover control and a seed-3301 order-matched null, and (d) feasible in pure-Python
in-session. See verdicts below.

---

## The candidate slate (8) — Gate-#1 verdicts

Gate-#1 sub-tests: (1) not a re-run, (2) not excluded-by-mechanism, (3) anchorable
(plant→recover + seed-3301 order-matched null), (4) feasible in-session pure-Python.

### C1 — Non-English / matched-runic-scorer re-adjudication of the strongest existing sweeps
Re-score the ALREADY-STORED B-04 / R21-L3 decode rows (or a re-run subset) with the
`round16/scorer` matched-runic adjudicator + Greek/Hebrew/Norse/Latin LMs — the registers
L7-A leaves at power 0.00–0.33 and that NO lane has ever adopted.
- **(1)** Distinct: this is not a new key-space; it is re-adjudicating stored decodes on the
  ONE instrument axis the doctrine (R2, "value=coverage×power") says was never covered.
  Closest prior R22-C X4 re-ran N5 under the repaired instrument — but only on the ENGLISH
  panel. **SURVIVES the re-run test only IF the language-agnostic secondary stats were NOT
  persisted at sweep time** — and R3 says round10b got 0/15 compliance, so most stored decodes
  are un-reinterpretable. → For B-04 the rows are discarded; must RE-RUN a subset to persist
  the new register scores. Materially distinct: new adjudicator register.
- **(2)** Not excluded — L7-A explicitly names "the matched runic scorer of round16/scorer,
  which no lane has yet adopted" as `not_covered`.
- **(3)** Anchorable: plant a Latin/Greek plaintext under a known key, confirm the matched
  scorer recovers it above a seed-3301 order-matched null where the English scorer does not.
- **(4)** Feasible: re-running a bounded B-04 subset (say the top-prior seed slice) + scoring
  is minutes-to-hours, pure-Python.
- **VERDICT: SURVIVE (instrument lane, doctrine-preferred).**

### C2 — `skip_by_two` decoder-envelope power measurement + targeted re-decode
Build the `skip_by_two` (2 draws per rejection) transition relation the beam CANNOT represent
(L7-B), measure its recovery power, and IF it recovers planted keys, re-decode the top-prior
seed slice under it.
- **(1)** Distinct: R18 L7-B only PROVED the beam misses skip_by_two (recovery 25.8%,
  score −6.90); it never BUILT a decoder that represents it. R21-L2 measured n_skips crossover
  for keyskip1 only ("skip_by_two beam-unrepresentable, crossover None"). No lane has ever
  decoded LP2 under a skip_by_two-representing decoder.
- **(2)** Not excluded — it is the exclusion. L7-B: "any evidence the 2013 rejection loop
  consumed more than one draw per rejection invalidates every beam-based negative." skip_by_two
  is LP2-doublet-consistent.
- **(3)** Anchorable: plant a key enciphered under skip_by_two, confirm the new decoder
  recovers it (the beam gets 0.258); seed-3301 null.
- **(4)** Feasible: building one alternate transition relation + decoding a bounded seed slice
  is in-session. (Full 2^32 re-decode is NOT — scope it to the R20 seedprior top slice.)
- **VERDICT: SURVIVE (instrument lane; this is the single highest-leverage un-audited closure).**

### C3 — Long-period (p ≥ ~400) polyalphabetic sweep under the drift-tolerant beam
Sweep periodic keys of period 400–1500 — the band flat-IoC does NOT exclude (p*≈400 is the
smallest IoC-invisible period at N=12,956; the OTP claim rests only on the doublet argument).
- **(1)** Distinct on paper from "periodic keys len 1-40" (dataset ruled_out) and all-lag
  key-reuse — those are short periods; this is the IoC-blind long-period band nobody swept.
- **(2)** **KILLED by mechanism.** A periodic Vigenère-class key, whatever its period, cannot
  produce the 0.66% doublet deficit: doublets are relabel-invariant, so a period-800 additive
  key lands at the same 2.9–4.2% doublet rate as period-8 (DOUBLET-INVESTIGATION §2). Long
  period buys IoC-invisibility but the doublet-deficit floor (L7-C-G3, min_d 0.972% English)
  still refutes it. Same wall as every additive lane.
- **VERDICT: KILL — doublet-deficit floor (L7-C-G3-FLOOR-EXTENDED).**

### C4 — D-04 full-page non-additive ciphertext-feedback (complete the aborted lane)
D-04 (non-additive coefficient sweep) ran only 3/55 pages at k≤3. Complete it to all 55 pages,
k≤ the doublet-consistent bound.
- **(1)** Distinct from what D-04 covered (3 pages) — but NOT distinct from the autokey CLASS.
- **(2)** **KILLED by mechanism.** Autokey/ciphertext-feedback is POSITIVELY refuted, not merely
  un-decrypted: the 28 nonzero difference-diagonals are flat (cv 0.061) where any feedback model
  needs cv≈1.0 (FINAL-SYNTHESIS iter 9; R12-C1 NEGATIVE over 21 feedback fns; A-03 K_bound 26 <
  K_needed 93). Finishing pages 4–55 cannot revive a class refuted by a whole-corpus diagonal
  statistic. D-04's `not_covered` (higher k, more pages) does not escape the diagonal refutation.
- **VERDICT: KILL — autokey positively-refuted (diagonal-flatness, z=−17.25).**

### C5 — Non-linguistic PAYLOAD hypothesis: value-stream as a compressed/encoded binary object
Test the number/value stream (or digit planes) as a NON-LINGUISTIC payload — gzip/deflate
member, PNG/JPEG magic, protobuf, base64/base85-under-transform, key material — since the
doublet-floor `not_covered` explicitly exempts "non-linguistic plaintexts, which by construction
can reach any floor," and B6 proved a non-linguistic payload is undetectable to the LM scorer.
- **(1)** Distinct? Compression/MDL was run on the LETTER stream (FINAL-SYNTHESIS: "exactly
  incompressible → not a machine pad"); base-60/base-32 decode of the value stream was in R11
  N2 route(d) and R22-B G3 (POINTER_FOUND=False). Magic-byte / container-format scanning of the
  value stream across representations was NOT systematically done.
- **(2)** **KILLED by mechanism — message-existence undecidable.** This is exactly the lane the
  undecidability result forecloses: LP2 sits inside the filler-under-no-message band on all 10
  metrics (ELIMINATION-LEDGER:551-557), and a non-linguistic payload has NO positive control that
  distinguishes signal from an order-matched null — any byte string base64-decodes to *something*.
  Fails Gate sub-test (3): the null is degenerate (every candidate "hits" trivially), which is the
  rule that has killed lanes before. B6 = "undetectable in principle."
- **VERDICT: KILL — degenerate null / message-existence-undecidable (fails Gate-3 anchorability).**

### C6 — F-02: interpret the 2016-01-01 signed clause "its words are the map / their meaning is the road"
The one signed Cicada message clause the ledger records as UNINTERPRETED. Treat it as an
explicit instruction and enumerate the bounded operations it licenses.
- **(1)** Distinct: F-02 is flagged OPEN, never treated as first-class; R22-C executed the
  koans INSIDE the solved pages, not this external 2016 message.
- **(2)** Not a cipher mechanism, so no mechanism excludes it — BUT: "words are the map" most
  naturally re-points to the keytext/running-key class (closed by ~200-text exhaustion) or the
  self-embedded read (R22-A/R23-A2, clean null). Every concrete operationalization I can write
  collapses onto an already-NEGATIVE lane.
- **(3)** **Fails anchorability.** There is no falsifiable pre-registered test — "interpret a
  koan" is not a hypothesis with a plant→recover control until it names a specific operation, and
  every specific operation it names is already covered. This is the "un-anchorable lane" the rule
  kills.
- **VERDICT: KILL — un-anchorable (degenerate); collapses onto exhausted keytext / R22-A.**

### C7 — D-03: homophonic-downward (surjective 29→k) recovery via annealing/EM
D-03 is specified-but-never-coded; closed only by a bigram-flatness INFERENCE, not a run.
A surjective 29→k mapping followed by a pad could in principle sit under the doublet floor.
- **(1)** Distinct: never coded. Homophonic (k→29 expansion) is DEAD by mechanism, but
  homophonic-DOWNWARD (29→k contraction) is the untested direction.
- **(2)** **KILLED by mechanism + undecidability.** A downward map to k<29 symbols raises IoC
  above flat (fewer symbols = higher collision), contradicting the measured flat IoC·N≈1.00 —
  unless immediately re-padded, at which point it is indistinguishable from the OTP null and the
  EM has no gradient (message-existence undecidable). Bigram-flatness inference already covers it;
  the annealing objective has no anchorable positive control that beats the seed-3301 null.
- **VERDICT: KILL — flat-IoC contradiction + degenerate null.**

### C8 — Cross-artifact provenance: does the pad correlate with a DATED external public source?
Under R18's Ubuntu-11.04/GnuPG-1.4.11 + per-page signature-timestamp prior (54 distinct sig
timestamps 2012→2017), test whether each page's pad segment aligns to a DATED public random
source AT that page's signing date (NIST beacon started 2013-09; blockchain by date; that day's
`/dev/urandom` is gone but dated public entropy is not).
- **(1)** Distinct: R17-PUBLIC-PAD swept beacon/blockchain but as UNDATED contiguous offsets;
  it never used the per-page signature TIMESTAMP as the index into a dated source. That is a
  genuinely new join key (artifact provenance → pad offset), and R17's `not_covered` explicitly
  lists "the beacon beyond 2013-11-13" and "non-contiguous selections."
- **(2)** Not mechanism-excluded — a public-pad indexed by a real date is a full-entropy pad the
  doublet floor permits IF output-aware (the filter is separate), and it is NOT the keytext class.
- **(3)** Anchorable: plant a page enciphered from the beacon value at a known date, confirm
  recovery when indexed by that date and non-recovery at wrong dates; seed-3301 null over dates.
- **(4)** **Partially feasible / partially out-of-scope.** The NIST beacon full history and dated
  blockchain headers are fetchable (bounded, small) — but many pages predate the beacon (2012
  sig timestamps < 2013-09 beacon start), and the fetch is an EXTERNAL input. Flag: the beacon
  slice is in-session-feasible for post-2013-09 pages ONLY; pre-beacon pages need another dated
  source. Net: a REDUCED-SCOPE survivor (beacon-dated pages), not a full lane.
- **VERDICT: SURVIVE (reduced scope) — but flagged: needs a bounded external fetch (NIST beacon
  archive) and only covers post-2013-09-signed pages. Queue behind C1/C2.**

---

## Survivor pre-registration sketches

### C1 pre-reg — matched-runic + non-English re-adjudication
- **Hypothesis:** a stored/re-run decode that is a TRUE key but in a non-English register
  (Latin/Greek/Hebrew/Norse) or that the English quadgram scorer cannot see, will score above a
  seed-3301 order-matched null under `round16/scorer` + the multi-register panel, where it did
  not under the English scorer.
- **Test:** re-run the R20-seedprior top slice of B-04 (bounded, ~10^4–10^5 decodes), persisting
  R3's mandatory language-agnostic stats + a per-register score from round16/scorer.
- **Positive control:** plant Latin + Greek plaintexts under known keys; confirm matched scorer
  recovers each above its null and the English scorer does NOT (reproduces L7-A power 0.33/0.00).
- **Null:** seed-3301 order-shuffled decodes, per register, per length cell.
- **Family-wise bar:** panel-max threshold_for() at the actual N (never −5.5).
- **Coverage×power:** coverage = the re-run slice; power = measured per-register recovery
  (expected ≈1.0 English, 0.33 Latin, 0.00 Welsh — report the envelope, not a single number).

### C2 pre-reg — skip_by_two decoder envelope
- **Hypothesis:** if the 2013 rejection loop consumed 2 draws per rejection (skip_by_two), the
  correct key is recoverable only by a decoder that represents that relation; the beam misses it
  (L7-B: 0.258). Building that decoder either recovers a key from the top-prior slice or measures
  the power lost.
- **Test:** implement the skip_by_two transition relation; (a) measure planted-key recovery vs
  the beam; (b) IF recovery ≥ ~0.9, re-decode the R20-seedprior top slice under it.
- **Positive control:** encipher a known plaintext under skip_by_two; confirm the new decoder
  recovers it (≥0.9) where the beam gets ≈0.26.
- **Null:** seed-3301 wrong-key decodes under the SAME skip_by_two decoder (order-matched).
- **Family-wise bar:** panel-max at N; seal note R21-L1 (any bar-clearer is flagged-for-oracle).
- **Coverage×power:** coverage = the seed slice re-decoded under skip_by_two; power = the newly
  measured recovery for that relation (the number L7-B says was 0.258 for the beam).

### C8 pre-reg (reduced scope) — date-indexed public pad
- **Hypothesis:** a page signed on date D was enciphered against a public random source's value
  at/near D (NIST beacon 2013-09→).
- **Test:** for each post-2013-09-signed page, index the beacon (and dated block headers) by the
  signature timestamp, decrypt under the pinned filter, score.
- **Positive control:** plant a page from the beacon value at a known date; recover at right date,
  fail at wrong dates.
- **Null:** seed-3301 over the date axis (shuffle which date maps to which page).
- **Family-wise bar:** panel-max at N over the date family.
- **Scope flag:** needs a bounded external fetch (beacon archive); pre-2013-09 pages OUT.

---

## Bottom line

Of 8 candidates: **C3/C4/C5/C6/C7 KILL** (doublet-floor, autokey-refuted, degenerate-null ×2,
flat-IoC). **C1 and C2 SURVIVE as instrument-audit lanes** — the two doctrine-preferred kinds
(auditing an instrument / a closure), each targeting a `not_covered` boundary the ledger states
verbatim (the matched runic scorer no lane adopted; the skip_by_two relation the beam cannot
represent). **C8 SURVIVES at reduced scope** but needs a bounded external fetch and covers only
post-2013-09 pages.

Honest note: C1 and C2 are NOT new key-space sweeps — they are re-adjudications on the two
instrument axes L7-A/L7-B proved were never covered. They can only REOPEN old negatives, not
manufacture a new hit; their realistic best case is "the old negatives were English-only /
beam-only, here is the corrected bound." That is genuine ground, but it is bound-tightening, not
a probable solve. If C1/C2 return clean, the frontier is dry at the tested resolution and the
only live branches remain the PRNG core-day tail and `/dev/urandom`.
