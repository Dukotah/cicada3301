# Round 36 / I1 — Greek, Hebrew, Norse registers: PRE-REGISTRATION

_Dated 2026-10-30, written BEFORE any model, null or power output of this lane exists (only corpus-availability probes
were made; they are deleted). Addenda go in a separate dated file, never here._

## Aiming Test (ARMADA-DOCTRINE §1)
- **Q1 recognizer.** Plant the correct key over HELD-OUT (second-half) text of each new register, decode with the
  Round 32 beam (`beam_w=400, max_skip=3, supp=0.83, sha256_ctr(CICADA3301)`), adjudicate with the 12-register panel.
  Power = fraction of 24 replicates with `pmax >= bar`, bar = max(empirical, GPD) wrong-key (real-LP2 window, random
  key) 1-1e-3 quantile of the **12-register** `pmax`. Identical to `round32/I2/power.py` + `gates.py`.
- **Q2.** `round32/I2/RESULTS.md` "Not covered: Greek, Hebrew, Norse"; `round35/X1` Round-36 #1.
- **Q3.** Bounded: 3 corpora, one build, 12 registers x 2 lengths x 24 replicates.
- **Q4 conditionals.** key space: none swept here (instrument lane); decoder model: Round 32 keyskip beam; adjudicator
  register: now 12 registers, each defined by a romanisation + the existing Latin->rune map (so a Greek/Hebrew/Norse
  plaintext written in runes by a *different* convention is still uncovered).
- **Q5.** A new register < 0.90 power at L=120 after ONE mapping revision is recorded at its measured power and left
  OUT of the panel. The gate is not weakened.

## Frozen design (no tuning after seeing power)
- Model form, lambdas (0.70,0.20,0.09,0.01), first-half-train / second-half-plant split, null (20,000 uniform rune
  strings x 14 grid lengths, seed 3301): unchanged from `round32/I2/build_models.py`.
- Register order: the nine Round 32 registers in their order, then GREEK, HEBREW, NORSE (indices 9-11). The nine LMs are
  rebuilt from the same corpora when present and compared with the Round 32 `panel.npz` (diff reported).
- Corpora (data only, each in its own subdirectory, URL+sha256+bytes in `fetch_log.json`):
  Greek = Nestle 1904 GNT base text (biblicalhumanities/Nestle1904 xhtml, declared public domain, 27 books);
  Hebrew = Westminster Leningrad Codex via openscriptures/morphhb OSIS XML, Gen-Deut + Josh + Judg (PD text);
  Norse = normalised Old Norse sagas from heimskringla.no (Gudni Jonsson / Heimskringla editions), as many of the
  probed pages as load.
- Mapping v1 for each register is fixed in `mappings.md` before the build. Revision v2 permitted ONCE per register,
  only for a register failing 0.90 at L=120, and the v1 power stays on record.
- Gate (both must hold): new register power(pmax, L=120) >= 0.90 (target 0.92) and L=240 recorded; every existing
  register's L=120 and L=240 power under the 12-panel >= (Round 32 gate_proof value - 0.02). 24 replicates give 1/24
  resolution, so for a register at 1.00 a single miss (0.958) is a FAIL by this rule; this is stated, not softened.
- Wrong-key null sizes (reduced, nproc=1): L=120: 4000 beam decodes, L=240: 2000. The same stored decodes are scored
  under both the 9- and 12-register panels (bar9 vs bar12 on identical draws), so null-size noise cancels.
- Null shift: shuffled-LP2 (permuted real LP2 stream, random key, same beam) at L=120, 2,000 draws, `pmax` 9 vs 12:
  mean, sd, q0.99, q0.999, max, plus the empirical 1e-3 quantile. Fixed seeds.
- Consumers: `beam_v3.py` `panel_max` reads `pan.registers` and the panel path; `register_cond` uses a hard-coded
  7-cluster CLUSTERS list. Reported, not edited.
