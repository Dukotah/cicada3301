# GATE-CHANGE: the S2 engine's panel gate moves from the Round 19 panel to panel-R36
Round 36 / P1, 2026-10-30. Status: measured (instrument / governance). The live engine inputs are NOT modified; the change is staged in `engine_inputs_copy/` for S1.

## 1. What the Round 19 panel was
`round19/I2/models/panel.npz`: nine interpolated trigram language models over the 29 runes (EN_MODERN, EN_KJV, LP1_REAL, LATIN, OE, DE, CY, EN_HALFVOWEL, EN_NOVOWEL),
lambdas (0.70, 0.20, 0.09, 0.01), null calibration of 20,000 uniform-random strings per length. The Round 27 engine froze its LM table as `panel_lm.f32`
(9 x 24389 float32), sha256 `14a23d3619fa02dfb6aa20efafdd0fc0ff633c83d8dc5f02ac4d5d035b996297`, recorded in `engine.dat` (`PANEL_SHA256`), and froze the 64 V1
reference pmax values, the V2 planted pmax and the n=120 mu/sd from it. The Round 19 build recorded its corpora by sha (`round19/I2/out_build.json`), but the CY corpus
(`data/keys/welsh/welsh_mabinogion.txt`, sha 4b3fd926.., 524,561 B, described as a "Welsh Mabinogion, diplomatic edition") was never given a URL and never committed. It is lost:
Round 32 I2 and Round 35 P1 both tried, and Round 35 P1 compared six archive.org OCR texts, none matched.

## 2. Why it cannot be rebuilt
A byte-exact `panel.npz` / `panel_lm.f32` needs all nine corpora byte-exact. Eight are available (KJV and Mabinogion were restored in Round 35 as byte-exact originals, sha 0f1a83cb.. / 80dc6f0d..);
the Welsh one is not recoverable. Round 32 built a SUBSTITUTE panel (modern Welsh prose) which fails the engine self-test (Round 34 S1: V1 26/64).
Because the gate hash is of a file nobody can regenerate, the old gate was never reproducible from a clone.

## 3. What panel-R36 is
Twelve registers: the nine above (built FROM DISK) plus GREEK, HEBREW, NORSE (Round 36 I1). One command builds it: `python analysis/round36/P1-panel-r36/build_r36.py <outdir>`, which calls
I1's `build_models_r36.py --nine=rebuild` unchanged (plus one determinism fix, below). All 53 corpus files are in `inputs_r36.json` with path, sha256, bytes, URL or acquisition route, and
whether they match the Round 32 and Round 19 records.

* `panel12.npz` sha256 **`a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c`**.
  Engine blob `panel_lm.f32` (12 x 24389 float32) sha256 **`e46d4bb73d16adeb02262361325b2a6ff578ae436b1374a7725a0a240f7e9928`**.
  `testhalves12.npz` sha256 `cdd55adac8c9731116d3e059afa183503b21f1a532706720f58e7c9873736494`.
* Built twice in separate processes with different `PYTHONHASHSEED` (1 and 2): byte-identical (`build_twice.json`). Environment: Python 3.12.10, numpy 2.4.6, Windows 11.
* Power gate (Round 32 `power.py` protocol, 24 reps, L=120/240, nproc=1, reduced null): all 12 registers >= 0.90 at both lengths (`gate_proof_r36.json`). EN_NOVOWEL at L=120 is 22/24 = 0.917, the same 22/24 as Round 32, the thinnest cell.
* Relationship to Round 19, stated plainly: for eight of the nine original registers the n=120 mu/sd of the on-disk rebuild are identical (<= 5e-16 relative) to the Round 19 values frozen in `vectors.json`, so the rebuild reproduces
  those eight Round 19 models. The exception is CY (mu differs by 0.0116, sd by 4.3 %), because Welsh is the Round 32 substitute (modern Welsh prose, Gutenberg 3680/57981/56275/67424), not the lost text.
  So panel-R36 is the Round 19 panel with CY substituted and three registers added.
* It is NOT I1's `models/panel12.npz` (sha ea8ef0fd..), whose nine registers are carried verbatim from Round 32 (drifted English-family models) and whose Hebrew mapping was hash-seed dependent. Panel-R36 supersedes it as the recorded gate; do not mix them.

### Determinism finding (fixed in the wrapper; I1's file untouched)
`mappings_r36.hebrew_to_ascii` iterates a python `set` of combining marks. For the 15 of 384,147 Hebrew clusters that carry two vowel marks the output depends on `PYTHONHASHSEED`, so I1's
HEBREW rune stream, LM and test half are not run-to-run reproducible (the first build-twice attempt failed on exactly this). `build_r36.py` sorts the marks (code-point order) at import time and asserts the patch applied.
Effect on the gate: none (HEBREW 24/24 at both lengths).

## 4. How to reproduce from a fresh clone (cwd = `liber-primus/`)
```
python data/fetch_sources.py --r19        # data/kjv.txt + data/keys/mabinogion.txt, sha256-verified (both gitignored)
mkdir -p data/keys/welsh && cp analysis/round36/P1-panel-r36/inputs_frozen/welsh_mabinogion.txt data/keys/welsh/welsh_mabinogion.txt
python analysis/round36/I1-new-registers/fetch_r36.py          # 42 Greek/Hebrew/Norse files -> I1-new-registers/corpora/ (gitignored; URLs in fetch_log.json)
python analysis/round36/P1-panel-r36/make_inputs.py --check    # must print "53 / 53 inputs match"
python analysis/round36/P1-panel-r36/build_r36.py analysis/round36/P1-panel-r36/build1
sha256sum analysis/round36/P1-panel-r36/build1/panel12.npz     # a0682f0c39978d75c4c9e6f491e3d046a1da5ee29501d3ec951c69ca3a5bbe6c
```
There is no `--r36` flag in `fetch_sources.py`; the Round 36 corpora come from I1's `fetch_r36.py` (it also rewrites I1's `fetch_log.json`).
Do NOT use `fetch_sources.py --welsh` for this: it rebuilds a Welsh file of 761,024 B (sha da02fef6..), 6 bytes (three CRLFs) different from the one panel-R36 was built on (761,030 B, sha 624ffc97..),
and that changes the panel. The 624ffc97.. file is therefore frozen in `inputs_frozen/` (public-domain Gutenberg text, 0.76 MB).
`verify_fetch.json`: on 2026-10-30 a fresh download matched the on-disk file for 44 of 45 network-obtained files (KJV, Mabinogion, 42 I1 files); the 45th is exactly the `--welsh` mismatch.

Caveats. heimskringla.no pages are live wiki pages and could change; `make_inputs.py --check` is the tripwire. Same-machine byte-exactness (and hash-seed independence) is demonstrated; cross-machine byte-exactness of the
null-calibration floats under another numpy/BLAS is not. Whatever file S1 uploads is the gate, identified by the two hashes above, not by "whatever the script produces on that machine".

## 5. Statement of record
**S2 results obtained after the re-gate are adjudicated by panel-R36 and are a NEW measurement, not a continuation of the Round 19-gated rows.** pmax values are not comparable across the change:
28 of the 64 V1 vectors change pmax when re-scored (range -0.66 to +1.34; `engine_inputs_copy/rescore_r36.json`) because the max now runs over 12 registers with a different CY.
The completed Round 27 S1 lane (all 2^32 seeds, three oracle-adjudicated noise crossers) and the S2 progress to 44.14 % (1,895,728,884 seeds, 171,160 candidates, 0 claim-bar hits) were produced under the Round 19 gate
and stay recorded as such; they are not re-scored here. The S2 histogram and top-1024 list accumulated so far are Round 19-gated (decision D2).

## 6. What changes in the engine config (full diff: `engine_config_diff.txt`)
* `grind27.c`: `NREG` 9 -> 12 plus three message strings. The panel-max loop, gather table and file read are all NREG-parametrised; nothing else is touched.
* `engine.dat`: `PANEL_SHA256`, `NREG`, `MU`, `SD` (n=120, from the panel-R36 calibration), and the 64 V1 `pmax` plus `PLANT_PMAX` re-scored under panel-R36 from the stored plaintexts. The beam decode uses quadgram scores only,
  so every other V1 field, the ciphertext, `CAND_BAR` 5.0 and the quadgram constants are unchanged. The V2 planted pmax stays 17.931158509762 (LP1_REAL is still the argmax).
  Check on the re-scoring formula: where the argmax register is unchanged it reproduces the Round 19 values bit-for-bit (seed 2149309687: 6.825835461843649; plant: 17.93115850976196).
* `panel_lm.f32`: 12 x 24389 float32 from panel-R36. New `check_panel_gate.py`: `grind27.c` parses `PANEL_SHA256` but never compares it to the file, so the hash gate is enforced by this script, to be run before `--self-test`.
* Paths in `engine.dat` are now relative (`panel_lm.f32`, `english_quadgrams.txt`, a copy of the quadgram file is included); run the engine from `engine_inputs_copy/`.
* NOT changed: `sweep_plan.json`, the claim bars (S1 7.3835, S2 7.6342; Gumbel-cell quantities of the Round 19 panel's null), `CAND_BAR`.
* Not run here: compile and `--self-test` (no C compiler on the laptop). S1's acceptance: V1 64/64 exact, V2 pmax to 4 dp, `check_panel_gate.py` PASS.

## 7. Decisions left to the coordinator
* D1. Claim bars are not recalibrated for 12 registers. I1 measured the 1e-3 pmax bar rising 0.02-0.07; here 4.394 at L=120 (reduced null) against I1's 4.370. Candidates (>= 5.0) are unaffected; the Python adjudication on a 12-panel is what decides a crosser.
* D2. Whether S2 continues in the existing run dir (histogram and top list would mix Round 19- and R36-scored pmax) or in a copy with the change-point cursors recorded and hist/top reset. Resume semantics are for S1 to check on a copy.
* D3. Accept the frozen Welsh substitute in `inputs_frozen/` as the CY input (it is modern Welsh prose, not the Mabinogion the register name implies).
* D4. Downstream consumers (B1 and later) should adjudicate with panel-R36 (`a0682f0c..`), not I1's carried `panel12.npz`.
* D5. SWEEPROW stores are 9-wide; new stores need 12-wide (I1 noted).
