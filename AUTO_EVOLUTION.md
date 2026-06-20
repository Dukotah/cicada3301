# AUTO_EVOLUTION.md — Autonomous evolution log

Long-term memory for the recursive audit→execute→verify→re-plan loop on the
`Dukotah/cicada3301` repository. Newest epoch at the top.

---

## Epoch 3 — 2026-06-20

### 1. Current Status
Health **excellent**. CI is confirmed **green on GitHub** (Epochs 1–2, ~19s runs).
This epoch added solver onboarding (README quickstart + CI badge), de-noised the
stego tool, added a live provenance regression test, and **fixed a real packaging
bug** that made the advertised install/CLI broken. The rig is gated (pytest 7/7),
fully fresh-clone runnable, and documented end-to-end.

### 2. Completed in This Epoch
- **README quickstart + CI badge (roadmap #1, #5).** Rewrote `liber-primus/README.md`
  from a stub into a real quickstart: install, `lp_try.py` usage, the analysis
  commands, the dataset schema, a CI status badge, and a link to the dossier.
- **Gated stego spatial-LSB behind `--lsb` (roadmap #2).** `stego_scan.py` no longer
  computes JPEG spatial-LSB by default (it's compression noise for lossy images);
  `--lsb` opts in, with a "lossless-only" note. Verified: `lsb` key absent by
  default, present with the flag.
- **Live provenance regression test (roadmap #3).** `test_image_provenance_live`
  fetches the onion7 `files.xml` + two images and asserts SHA1 == the published
  archive.org hashes — guarding the headline byte-authenticity claim. Network-gated
  (skips, never fails, if archive.org is unreachable). Passed live (7/7).
- **Fixed a real packaging bug (discovered this epoch).** `pip install -e .` plus
  the `lp-try` console script failed with `ModuleNotFoundError: No module named
  'lp_try'` — a mixed root/src layout that editable installs don't expose. Removed
  the console-script entry; the install now cleanly provides the `lp` **library**,
  and the CLI runs directly as `python lp_try.py` (documented). Verified both.
- **Confirmed CI green on GitHub** via `gh run list` (roadmap #5).

### 3. Discovered Debt / Opportunities
- The `lp-try`/`pip install -e .` breakage was a genuine bug shipped in Epoch 2 and
  advertised by this epoch's README before verification caught it. Lesson: **run
  every install/CLI command you document**, in a clean-ish path, before claiming it.
- The pytest gate is now ~15s (the live provenance test adds a ~1.3 MB download);
  no fast/slow split yet (carry-over roadmap #4).
- The stego REPORT still prints "lossless (LSB-meaningful): 0" when LSB is skipped —
  mildly misleading; should say "skipped (pass --lsb)".
- No single convenience runner (commands are sprawling across README).

### 4. The Next Epoch Roadmap (priority order)
1. **Split the test gate by speed**: mark the subprocess + network tests `slow`
   (`pytest -m "not slow"` fast locally; full suite in CI). Carry-over.
2. **Clarify the stego REPORT when LSB is skipped** ("LSB: skipped — pass --lsb").
3. **Add a convenience runner** (`nox`/`make`/`tasks.py`: `validate`, `test`,
   `analyze`, `dataset`, `fetch`) to collapse the command sprawl.
4. **Extend regression guards** to the stego + transcription headline claims: a
   small test that fetches 2–3 images and asserts 0 trailing-bytes and
   rune-identical lineages (depends on `fetch_sources`).
5. **Publish the dataset** as a GitHub Release artifact (versioned, citable) so
   solvers can pull `liber_primus.json` without cloning.

---

## Epoch 2 — 2026-06-20

### 1. Current Status
Architectural health **very good**. This epoch closed the reproducibility and
regression-gating gaps from Epoch 1: the rig is now gated by a **pytest** suite,
**every** analysis script runs on a fresh clone (gitignored sources auto-fetched),
and a real cross-platform output bug was fixed. CI mirrors the full local battery.
The research itself remains complete (ciphertext is one-time-pad-class); work
continues on robustness, reproducibility, and solver onboarding.

### 2. Completed in This Epoch
- **Fresh-clone runnability for the source-dependent scripts (roadmap #1).** Added
  `data/fetch_sources.py` (stdlib urllib, idempotent) and wired `ensure_sources()`
  into `structure_analysis.py` and `crossdiff.py` so they auto-download the
  gitignored rtkd/relikd transcriptions on demand. Verified by hiding
  `data/sources/` and re-running — both fetched and produced identical results
  (13136/13136, 0 divergences). Both are now in CI.
- **Pytest regression gate (roadmap #3).** Added `tests/test_rig.py` — 6 tests:
  gematria invariants (incl. the V/U shared-rune behavior), an **OTP-flatness
  guard** on the unsolved corpus (IoC≈1.0, doublet<1.5% — protects the core
  finding from silent drift), and integration wrappers for `validate.py`,
  `attack.py selftest`, `lp_try --selftest`, plus the kjv-fallback baseline. CI
  now gates on `pytest`.
- **UTF-8 stdout guard (roadmap #2).** The loop surfaced a *real* latent bug:
  `run_stats.py` (`→`) and `lp_try.py` (`≈`) crashed under Windows cp1252 when
  stdout is piped. Added guarded `sys.stdout.reconfigure(encoding="utf-8")` to
  both (and to the source-dependent scripts). Verified against the exact failure
  condition (piped, no `PYTHONUTF8`). Confirmed the other scripts are ASCII-only.
- **Tidy (roadmap #5a).** Removed the stray tracked `data/tmp.txt`
  ("404: Not Found" fetch artifact).
- **CI updated** (`.github/workflows/ci.yml`): installs pytest, runs the pytest
  gate, fetches sources, then smoke-tests all four analysis scripts.

### 3. Discovered Debt / Opportunities
- The cp1252 crash was a **genuine latent bug**, not theoretical — it only shows
  when stdout is piped without `PYTHONUTF8`. Lesson: exercise scripts under the
  failing condition (piped), not just interactively.
- `tests/test_rig.py` shells out via subprocess (~5s). Could import-and-call for
  speed, or mark the integration tests `slow`.
- No assertion-level coverage for the stego / vision / transcription *verdicts*
  (they need gitignored images; a tiny fetch-a-few-images provenance test could
  guard the 56/56 SHA1 claim).
- Any doc citing the old kjv English-IoC (~1.785) is now slightly stale (the
  quadgram fallback gives ~1.69); cosmetic.
- Still no `liber-primus/README.md` quickstart; `stego_scan.py` still computes
  JPEG spatial-LSB (noise) unconditionally.

### 4. The Next Epoch Roadmap (priority order)
1. **`liber-primus/README.md` quickstart**: `pip install -e .`, `lp-try` usage,
   dataset schema, CI badge, link to `SOLVERS-DOSSIER.md`.
2. **Gate `stego_scan.py` spatial-LSB behind `--lsb`** with a "lossless-only"
   note (reduce false-signal confusion).
3. **Provenance regression test**: fetch 2–3 onion7 images in CI and assert their
   SHA1 == the published archive.org hashes (guards the headline provenance claim).
4. **Speed up the test gate**: convert subprocess integration tests to
   import-and-call, or mark `slow` and run a fast subset on PRs.
5. **Confirm CI is green on GitHub** after first push (Actions enabled), add the
   status badge.

---

## Epoch 1 — 2026-06-20

### 1. Current Status
The repo is a mature Cicada 3301 / Liber Primus research archive + a validated,
pure-Python cryptanalysis rig (`liber-primus/`). Architectural health is **good**:
clear `src/lp` core (gematria, ciphers, stats, score, solve), an analysis layer,
a self-validating test (`tests/validate.py` reproduces all solved pages), a
pip-installable package (`pyproject.toml`), a canonical dataset
(`dataset/liber_primus.json`), a solver CLI (`lp_try.py`), and a consolidated
solver dossier. The investigation itself is effectively complete (ciphertext is
one-time-pad-class). Main gaps were **reproducibility on a fresh clone** and the
**absence of automated regression gating** — both addressed this epoch.

### 2. Completed in This Epoch
- **Fixed a fresh-clone reproducibility bug (high-leverage).** `english_baseline()`
  in `analysis/run_stats.py` hard-required the **gitignored** `data/kjv.txt`,
  which crashed `attack.py selftest`, `analysis/run_stats.py`, and
  `analysis/doublet_probe.py` for anyone cloning the public repo. Added a
  deterministic, fixed-seed **quadgram Markov-walk fallback** built from the
  committed `data/english_quadgrams.txt`. It reproduces realistic English
  monogram *and* sequence statistics (doublet 2.88%, IoC 1.69 — verified), which
  the order-sensitive consumer `doublet_probe.py` requires. kjv.txt is still
  preferred when present. *Why:* the rig must run for the community it's published
  for; this was the single biggest correctness gap.
- **Added CI (`.github/workflows/ci.yml`).** Runs on push/PR touching
  `liber-primus/**`: rig validation, `attack.py selftest`, `lp_try --selftest`,
  and committed-data analysis smoke-tests. The fresh-clone fix above is what makes
  this green on a clean checkout. *Why:* satisfies the standing Regression
  Prevention directive with an automated gate instead of manual runs.
- **Regenerated `analysis/STATS.md`** so the committed artifact matches the
  fresh-clone-reproducible baseline (English-baseline row shifted; all load-bearing
  unsolved-corpus numbers unchanged: IoC·N 0.9999, doublet 0.664%, entropy 4.857).

### 3. Discovered Debt / Opportunities
- `structure_analysis.py` and `transcription/crossdiff.py` depend on the
  **gitignored `data/sources/`** with no self-fetch, so they cannot run on a fresh
  clone and had to be excluded from CI.
- Many rune-printing scripts crash on Windows under the default **cp1252** stdout
  (need `PYTHONUTF8=1`); they should self-configure UTF-8 output.
- The test story is ad-hoc scripts with `sys.exit`/prints, not **pytest**
  assertions — fine for CI invocation but not introspectable/parametrized.
- Stray committed scratch file `data/tmp.txt` (14 bytes).
- `liber-primus/` lacks a focused **quickstart README** (install → `lp-try` →
  dataset) for first-time solvers; onboarding currently routes through the dossier.
- `stego_scan.py` still computes spatial-LSB for JPEGs (documented as noise) —
  could be gated off to reduce confusion.

### 4. The Next Epoch Roadmap (priority order)
1. **Make `structure_analysis.py` + `crossdiff.py` fresh-clone-runnable**: add a
   `data/fetch_sources.py` (downloads rtkd_master + relikd chunks from their raw
   URLs) and call it on-demand; then add both scripts to CI.
2. **UTF-8 stdout guard**: add `sys.stdout.reconfigure(encoding="utf-8")` (guarded)
   to every script that prints runes, so they work cross-platform without env vars.
3. **Promote tests to pytest**: wrap `validate`, `attack selftest`, `lp_try
   selftest` as real `test_*` assertions under `tests/`; point CI at `pytest`.
4. **Add `liber-primus/README.md` quickstart**: install, `lp-try` usage, dataset
   schema, link to dossier — reduce solver onboarding friction.
5. **Tidy**: remove `data/tmp.txt`; gate JPEG spatial-LSB in `stego_scan.py` behind
   a `--lsb` flag with a clear "lossless-only" note.
