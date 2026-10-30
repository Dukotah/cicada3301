# R36-I2 PREREG (dated 2026-10-30, written before any output)
Question: power of pf_v4 at the FROZEN operating point (m=24,k=2,rel=both,pen=2, thr a1=7.099447749731914 / a2=7.176139668549184, from round35/I1 frozen_op.json) on natural-rate plants, per keystream generator.
Generators: bash4.2 (LP64, reference), bash4.2_i32 (ILP32), php_mt_scale, php_mt_mod, php_php_scale, php_php_mod.
Registers: EN_MODERN, EN_NOVOWEL, EN_HALFVOWEL, LATIN (testhalves.npz of round32 I2 panel); plaintext 30-rune windows at random offsets.
Plants: 500 per (generator x register x relation keyskip1/keyskip2) = 24000, real encipherer (sk.encipher_keyskip for keyskip1; j+=2 enc_pair form for keyskip2), supp 0.83, no skip-free selection. Seeds: bash = 2^20-granular window 2012-01-03..2014-05-31 as in I1 run.py; PHP = uniform 32-bit. Hit = OR over a=1,a=2 of pf_v4 LSE > frozen threshold (m=24).
Splits: skip_free (first deviation of key index >= 24), with_skip, natural. Wilson 95% intervals.
FPR: 2^16 fresh wrong-key heads per generator, same OR rule.
Positive control: bash LP64 should reproduce R35 I1 held-out natural power (EN_MODERN ~0.98, EN_NOVOWEL ~0.98, EN_HALFVOWEL ~0.95, LATIN ~0.97) within binomial noise (+-0.03); FPR ~8e-4.
Q5: any (generator, register) natural power <0.85 (either relation) is reported as-is; thresholds NOT re-tuned. One process, seeds fixed (rng 3601).
