# Round 38 / S1 - S2 windows: PREREG (dated 2026-10-30, written BEFORE any control result)

Sandbox: indigo-negative-rhinoceros-y1foyJ / session sbx_FqrhoEiqDPULsZT7sN0gN0v7Asrj, created from snapshot snap_fWma12lA4k5RXsR6LHPwhV2p0DnN (4 vCPU, 8 GB), unix 1793398713.

## (a) Independent exact-relation control - recognizer
* Generator: my OWN pure-Python MT19937 init_by_array([w]) + random29 reducer + keyskip1 one-draw rejection enciphering, written in this lane (not imported from round25/skipdecode); cross-checked against the engine's ks128 via `--mode score --full` (pair-relation lane, keystream only) and against Python 3 `random.seed(w)` getrandbits words.
* Plaintext: 240 known English runes (self_reliance.txt eng_to_idx slice, distinct offsets per seed), supp=0.83, sign=-1. Three seeds, chosen now: 777, 1234567891, 3000000017 (one outside the 2^31 half, the S2 sweep never having covered them is irrelevant: the control runs a narrow band via the engine's own exact-lane sweep path).
* Path: engine stage path (`--plan` run_lane, relation exact, GRIND27_S2_CONTROL_OK deliberately NOT relied on as evidence) on a copy of the inputs with the ciphertext swapped (C_SCREEN := cipher[:120]); a band of width 4096 containing the seed is swept.
* PASS per seed: seed ranked FIRST by pmax in the band, pmax >= 7.6341931878728095 (S2 claim bar) and >= cand bar 5.0, and the engine pmax is reproducible. Control (a) PASSES if 3/3.
* KILL: any seed not ranked first or below the bar -> stop; S2 stays parked; no windows run; record exactly what failed.
* Engine change: only a control-only variant binary (grind27_ctl) that, AFTER the unmodified launch self-test passes on the original cipher, loads a replacement C_SCREEN from env GRIND27_CTL_CIPHER. The production binary used for windows is the unmodified one.
## (b)-(d)
(b) rescoring top_S2.json (Round 19-scored, local run/) under panel-R36 via the engine's score path with S2 relation semantic (exact) - the stock `--mode score` is hard-wired to the pair lane, so the ctl variant gets an exact-relation score mode if needed; reported with that caveat. (c) export lists from snapshot; (d) >=2 windows <=45 min, 4 threads=vCPU, cursors from run_r36/STATUS.json. Crossers >= 7.6342 -> flagged-for-oracle + local beam_v3 L=240 re-screen; near-miss >= 7.5342 listed. No "solved/closed/exhausted".
