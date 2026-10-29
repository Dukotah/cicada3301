# R34 / I2 PREREG (dated 2026-10-29, written before any output file)

Q1 recognizer: planted correct-key heads (held-out text, 9 registers from testhalves.npz) pass the screen.
Required: EN_NOVOWEL power >= 0.85 and every other register >= 0.90 at FPR <= 1e-3.
Screen = statistic on first m in {16,20,24} decoded runes, relation-agnostic. Candidate statistics (fixed now):
 zmax (R32-B1 / v3 panel_max z-sum, baseline), llrmax, lse (logsumexp of per-register LLR = mixture LR),
 pq (max over registers of empirical-tail -log p, split-sample), OR(zmax,lse) at FPR/2 each.
FPR: >=1e5 random wrong-key heads per generator from the real generators (bash4.2 LP64, bash4.2_i32, PHP mt/php x scale/mod);
thresholds calibrated on one half of each null, FPR reported on the held-out other half and per generator.
Plants: no-skip (plaintext window = decode with correct key; real C[:40] has zero doublets so true-key heads are skip-free: operative power)
and with-skip via enc_pair/enc_exact (B1-comparable, pessimistic). Baseline zmax m=16 is the pf.py screen on identical plants.
Q5: if nothing <=24 meets the bar, report best curve + operating point at a stated higher FPR.
Throughput: heads/s end-to-end (generator heads + decode + stat), pf.py trigram m=16 vs pf_v3, single process.
Compute cap ~30 min, one process. No git. Not covered: heads past first skip, free relation, registers outside the nine.
