# AUTO_EVOLUTION.md — Autonomous evolution log

Long-term memory for the recursive audit→execute→verify→re-plan loop on the
`Dukotah/cicada3301` repository. Newest epoch at the top.

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
