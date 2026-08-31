# Round 26 — LANE B — PREREG

## Lane
Run R12-C2's staged-but-never-executed keytext running-key sweep. Each of the 33 texts
in `analysis/round12/C2/texts/` is mapped to rune indices and slid as a RUNNING KEY K
across every UNSOLVED rune-bearing LP2 page (the OTP-class target), THROUGH the skip-aware
decoder (preset `exact`=keyskip1 AND preset `pair`=keyskip2), panel-max adjudicated, hitfn20
certified. Prior: LOW. Expected outcome: HARDEN.

## ANTI-REPEAT PROOF
**Extends ledger id: `R12-C2`.**
Its `coverage`: *"Texts fetched (29 files, ~12 MB); the sweep was never run."* Its
`not_covered`: `None`. The sweep this entry staged was **never executed** — there is no
per-decode artefact, no control, no null anywhere in the repo for these texts run as
running keys. This lane RUNS it, so it cannot duplicate an existing negative: the negative
does not yet exist.

Distinctness from neighbours that DID run:
- `R12-A1` swept the SIX author pads as **literal byte→symbol reductions** (mod-29 / nibble /
  bit-scaled), *"not as PRF seeds or salts."* Those are a DIFFERENT six files and a DIFFERENT
  mechanism (byte-reduction pad, not a letters-only running key), and they were fed to the
  rigid Vigenère/one-time-pad stream, NOT the skip-aware decoder. This lane: 33 mysticism/
  philosophy texts, letters-only running key, keyskip1 + keyskip2.
- `R24-C2-EXT-SKIP-GENERATORS` explicitly lists in its `not_covered`:
  *"skip_by_two under generators OUTSIDE S-G3: … sha256_ctr **keytexts**, the public-pad lanes …
  each is a cheap re-run with preset='pair'."* — it named keytexts as UN-RUN and left them open.
  This lane consumes exactly that open item for the C2 text corpus.
- `R24-C2-SKIP-BY-TWO-DECODER` built the pair decoder but its `not_covered` also lists
  keytexts as un-swept. I EXTEND its validated instrument, I do not re-measure its plant.

No committed artefact holds a keytext-running-key null over LP2 pages. PROVEN not-covered.

## Q1 — What would a hit look like, and would THIS instrument recognise it? (plant + recover)
A hit = a keytext whose letters-only running key, at some offset, decodes an unsolved page
to a decode that (1) clears the calibrated panel-max bar, (2) has rune-index recovery ≥0.90
from the DECODE PATH, (3) reproduces on the held-out 3/4 under the key attributed on 1/4.
CONTROL (`control.py`): I plant `plotinus_enneads_mackenna.txt` as the running key over
English `self_reliance.txt` (L=240, 7 seeds, random keytext offsets), encipher under BOTH
the keyskip1 filter (`skipdecode.encipher_keyskip`) and the skip_by_two filter (`j+=2`),
then decode with preset `exact` and preset `pair` respectively. **Measured recovery: keyskip1
median/min = 1.000/1.000; pair median/min = 1.000/1.000 → CONTROL_PASSED=True.** The
instrument recovers a keytext running-key plant at 1.00, far above the 0.90 bar. It WOULD
recognise a real hit.

## Q2 — What measured fact raises this family's prior above flat? (cite a file path)
LOW prior, and I state it as low. The only fact lifting it above zero: R12-C2
(`LEDGER.json`) deliberately curated these 33 texts as the *plausible Cicada running-key
corpus* (Gnostic/Hermetic/Neoplatonic/Kabbalistic sources thematically aligned with LP1's
solved content) and then never tested them — a genuine unexplored, hand-picked slice rather
than a random baseline. Rigid running-key is doublet-excluded (`round18/L7-redteam/RESULTS.md`),
which is precisely why a SKIP-AWARE pass over these curated texts is the one un-run test.
That is a curation prior, not a signal prior — hence LOW.

## Q3 — Is the space bounded? size + enumerable/samplable + fraction covered
BOUNDED and fully enumerated within its own definition. Space = {33 texts} × {offsets/text}
× {9 unsolved rune-pages} × {2 presets: keyskip1, keyskip2}, sign=−1. Primary pass uses 4
evenly-spaced offsets/text (a companion off8 pass covers pages 19-20 at 8 offsets as an
offset-density corroborator). The 4 truncated 5,336-rune texts cannot span the longest pages
as a full running key (usable = len(K) − pageLen·9 − 8 < 0), and those combos are legitimately
UNCOVERABLE by a running key — reported, not hidden. Under multi-lane CPU contention the large
pages (1,729-3,008 runes) proved too slow to finish inside a bounded round, so per doctrine the
sweep is CAPPED and the un-swept pages (20 mostly, 22, 25, 27, 29) go into not_covered — the
negative claims only the pages that completed. See RESULTS §2/§2.1 for the exact per-page
coverage and the 45.4% swept fraction of the off4 feasible plan.

## Q4 — The three conditionals the negative carries
1. **Key-space swept:** 33 curated texts × 8 offsets × sign=−1 only. NOT covered: +1 sign,
   >8 offsets/text, texts outside this corpus, per-line/per-page key restarts, reversed texts.
2. **Decoder transition model:** keyskip1 (repo relation, exact for encipher_keyskip) and
   keyskip2 (skip_by_two-exact, pairs). NOT covered: permissive drift (lam=12), multi-rune
   correlated errors, transpositions.
3. **Adjudicator register:** the 9-register panel (EN_MODERN/EN_KJV/LP1_REAL/LATIN/OE/DE/CY/
   EN_HALFVOWEL/EN_NOVOWEL) via `AD.adjudicate`, panel-max bar from `panelmax20` at the
   family-wise N of THIS sweep. Blind spot = any language/plaintext outside those 9 panels.

## Q5 — The single observation that kills this lane at 10% budget
Checkpoint after the first ~10% of decodes (logged every 500 rows in `sweep.log`): if the
running best pmax stays well below the panel-max bar (bar ≈ 4.1) — i.e. best pmax < 3.5 with
no clears — the lane is HARDEN and continues only to complete coverage, never expecting a
hit. A single decode that clears the bar is FLAGGED-FOR-ORACLE (never auto-solved, per
R21-L1 leaky-proxy). Kill signal = 10% in, zero bar-clears, best pmax far under bar.
