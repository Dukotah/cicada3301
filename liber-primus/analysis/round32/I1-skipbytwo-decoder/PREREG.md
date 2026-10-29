# Round 32 / I1 -- `beam_decode_v2` and its measured power envelope: PRE-REGISTRATION

_Written 2026-10-28 BEFORE any envelope cell was run. Only the speed probe
(`run_envelope.py speed`, one plant per decoder at L=120/400, EN) and the panel build
(`build_panel_lite.py`) had been executed. Thresholds below are not edited after results; later
changes are dated addenda._

## 0. Findings from reading that shape the lane (stated up front)

1. **The transition relations already exist.** `round19/I1/driftbeam.py` (modes `keyskip1`,
   `keyskip2`, `permissive`; 15 tests; gates G-EQ / G-BASE / G-FIX / G-FP) is exactly the
   `advance in {1, 2, free}` decoder CAMPAIGN-PLAN s3 I1 asks for, and its RESULTS.md reports
   `skip_by_two` recovered at -4.285 / 100% at L=240. The plan was written without that fact.
   `beam_v2.py` is therefore a thin explicit-parameter facade over `driftbeam` (imported,
   unmodified), not a re-derivation. This lane's contribution is the **measurement the plan
   asks for and R19/I1 did not make**: L=120 (the bar length), non-English plaintext registers,
   adjudication through a multi-register panel, a seed-3301 shuffle null per (decoder, L), and a
   decoder-by-construction cross-matrix. Overlap with R19/I1 is disclosed, not hidden.
2. **The I2 nine-register panel cannot be rebuilt on this checkout.** `build_models.py` needs
   `data/keys/mabinogion.txt`, `data/kjv.txt`, `data/keys/welsh/welsh_mabinogion.txt`; none exist.
   Fallback (instructed): `build_panel_lite.py` builds the SAME statistic (interpolated trigram,
   same lambdas, same null recipe, same `adjudicate.Panel` npz format) over the 7 buildable
   registers: EN_MODERN, LP1_REAL, LATIN, OE, DE, EN_HALFVOWEL, EN_NOVOWEL. **EN_KJV and CY (Welsh)
   are NOT covered** -> `not_covered`. The lite panel's z scale differs from I2's, so I3's
   `calib19.json` cells do not apply; bars here are lane-local shuffle-null bars.

## 1. Hypothesis

H1: `beam_decode_v2(advance=2)` recovers a planted `encipher_skip_by_two` correct key at L=120 with
rune-index recovery >= 0.85 and an adjudicated score above the shuffle-null bar; `advance=1`
(the repo's old relation) does not (replicates L7-B). H2: `advance="free"` recovers all three
constructions (keyskip1, skip_by_two, free drift q=0.05). H3 (register axis): recovery and
adjudication survive non-English plaintext (the beam still searches with the English quadgram, so
this is a genuine open question, per I2 `not_covered`).

## 2. Design (fixed)

* **Key**: SHA-256 counter-mode over Z_29 (`beam_v2.sha_ctr_key`, seed `CICADA3301`), CORRECT key
  and offset 0 handed to the decoder (this is a power test of the decoder+adjudicator, not a search).
* **Enciphers**: `keyskip1` (key +1 per rejection), `skip_by_two` (key +2), `free_q05`
  (keyskip1 + unrelated +1 advance w.p. 0.05). supp = 0.83. Enciphers are re-implemented in
  `beam_v2.py` to match `round18/L7-redteam/b1_power_envelope.py` semantics line for line.
* **Decoders**: `advance` in {1, 2, "free"} = driftbeam presets `exact_ms8`, `pair`, `drift`
  (beam_w 400).
* **Lengths**: L = 120, 400 (full matrix); L = 6000 only for the matched decoders with few seeds,
  because it is cheap at the measured speed (<1 s at L=400 for all decoders); otherwise `not_covered`.
* **Plaintext**: windows drawn from the held-out SECOND half of each register corpus (the panel
  trained on the first half). Registers: EN_MODERN (full matrix); LATIN, EN_NOVOWEL, OE, DE (reduced
  matrix, matched + free decoders).
* **Seeds**: >= 20 plants per EN cell at L=120/400; >= 8 per non-EN cell.
* **Recovery** = fraction of rune INDICES equal to truth (doctrine s4 r5; never the string).
* **Adjudication**: `round19/I2/adjudicate.adjudicate(plain_idx, pan=lite)`; recorded `en`,
  `pmax`, `pmax_ne`, `pcon`, `ioc`, `preg`.
* **Null** (seed 3301): for each (decoder, L), take the planted ciphertext, shuffle it with
  `random.Random(3301+s)`, decode with the same key and same decoder, adjudicate. n=100 (L=120/400),
  smaller at L=6000 (stated). **Bar = max `pmax` over the null decodes of that (decoder, L)** (also
  max `en`). This is an empirical bar with per-decode alpha about 1/n; it is NOT the I3 contract bar
  (see s0.2) and is labelled as such.

## 3. Pass / fail thresholds (fixed now)

A cell is **RECOVERED** iff median recovery >= 0.85 AND >= 80% of its seeds have `pmax` above that
(decoder, L) null bar. A cell with recovery >= 0.85 but adjudicated score below the bar is reported as
**decoder-recovers / adjudicator-misses** (the distinction matters: R2). Positive control = the
matched-decoder cells on EN_MODERN. A replication control: `advance=1` on `skip_by_two` must reproduce
L7-B (low recovery); if it does not, the harness is not the same instrument and the lane is INVALID.

## 4. The five Aiming-Test answers

**Q1 -- recognizer.** The recognizer is the adjudicated `pmax` of the decode of a PLANTED
skip_by_two ciphertext under the correct key, compared with the shuffle null of the same decoder and
length, plus rune-index recovery against the known plaintext. The planted hit has exactly the shape
believed (skip_by_two at supp=0.83, doublet 0.84% target vs LP2 0.664%); the pipeline is the
pipeline under test. If it does not emit the planted hit at L=120, the lane is INVALID.

**Q2 -- measured prior.** `round18/L7-redteam/RESULTS.md` s B: `skip_by_two` reproduces LP2's
observed doublet rate (0.84% vs 0.664%) and is scored -6.90 / 25.8% by the old decoder with
beam_w/max_skip changes giving exactly 0.000. `ledger.json` line 119 in that lane records it. This
is an instrument fact, not a key-space prior; the lane is an instrument lane, queued as such.
Honest caveat: R19/I1 already repaired the decoder; this lane measures what R19/I1 did not (L=120,
registers, panel, null).

**Q3 -- bounded?** Enumerable and small: 3 enciphers x 3 decoders x 2-3 lengths x registers x
tens of seeds ~ 10^3-10^4 decodes, minutes of CPU. No key space is opened.

**Q4 -- the three conditionals this lane's results carry.**
(1) *key space*: none swept; the single SHA-256-CTR(`CICADA3301`) keystream at offset 0 with the
correct key is handed to the decoder; power says nothing about unknown keys or other families.
(2) *transition model*: {keyskip1, keyskip2 pairs, permissive max_skip=40 max_free=2 lam=12
start_slack=2} at beam_w 400; constructions NOT represented: any advance relation outside those
(e.g. skip_by_three, key advances not tied to rejection, rewrite/keyside/plainside constructions,
block-reordering, key-offset resets) -- reported as not_covered, not tested here.
(3) *adjudicator register*: the 7-register lite panel (no Welsh, no KJV; no Greek/Hebrew/Norse);
the BEAM itself still searches with the English quadgram (`lp.score`), so for a non-English plaintext
the beam may select the wrong path before the panel ever sees it -- measured, not assumed.

**Q5 -- kill.** KILL if `advance=2` on planted `skip_by_two` at L=120, EN_MODERN, fails s3's
RECOVERED test (or if the `advance=1` replication control does not reproduce L7-B). Checkpoint: after
the first EN L=120 cell (~10% of budget). Kill outcome is recorded as lane INVALID (instrument
failure), never as a negative about any key.

## 5. Re-adjudication gate

Only if the EN L=120 and L=400 matched cells are RECOVERED: a bounded re-adjudication of the
single highest-prior already-swept family (SHA-256-CTR seed `CICADA3301`) under `advance=2` with a
STATED coverage fraction; otherwise `not_covered`. Further gated on time/RAM: the re-adjudication
needs the actual swept survivors' parameters and the unsolved ciphertext streams; if those cannot be
re-materialised in a few minutes on this laptop it is stated as `not_covered`.

## 6. Addendum A (2026-10-28, after the envelope cells were run, BEFORE the re-adjudication was run)

The matched EN cells at L=120/400 met s3 (see RESULTS.md), so the s5 gate opens. Pre-declared before
running it: **object** = LP2 page 0 head (first 120 cipher runes of `nc.segments()[0]`, the
round13/B04 stage-C head length) against the SHA-256-CTR(`CICADA3301`) keystream
(`benchmark/plant.make_key("sha256_ctr")`, i.e. byte % 29, the B-04 family), **decoder**
`advance=2` (beam_w 400) at every offset 0..3301, sign in {-1,+1}, atbash 0 (atbash=1 and `advance="free"`
are run only at offsets 0..9, the B-04 stage-B offsets, for time); **flag** = `pmax` > 10.0 on the lite
panel (planted skip_by_two correct-key decodes score about 18 at L=120; the shuffle-null max is 4.0-5.7),
which is an ESCALATE flag, not a CLAIM; **in-pipeline positive control** = a plaintext planted at
offset 1000 under `encipher_skip_by_two` with the same key, run through the identical scan, must come
back with the true offset as the unique flagged one. Stated coverage = ONE seed of B-04's 2,165, ONE
page head, offsets 0..3301 for advance=2 only; everything else is not_covered.
