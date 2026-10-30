# R36-I2 RESULTS: pf_v4 power by keystream generator (frozen m=24,k=2,rel=both, thr 7.0994/7.1761)

500 natural-rate plants per (generator x register x relation), real encipherer, no selection; hit = OR over a=1,2. Cell = natural [Wilson95] / skip-free / with-skip.

| generator | rel | EN_MODERN | EN_NOVOWEL | EN_HALFVOWEL | LATIN |
|---|---|---|---|---|---|
| bash4.2 | keyskip1 | 0.990 [0.977-0.996] / 1.000 / 0.980 | 0.986 [0.971-0.993] / 1.000 / 0.968 | 0.958 [0.937-0.972] / 0.971 / 0.945 | 0.978 [0.961-0.988] / 0.992 / 0.963 |
| bash4.2 | keyskip2 | 0.992 [0.980-0.997] / 1.000 / 0.984 | 0.974 [0.956-0.985] / 0.996 / 0.950 | 0.962 [0.941-0.976] / 0.985 / 0.936 | 0.970 [0.951-0.982] / 0.989 / 0.949 |
| bash4.2_i32 | keyskip1 | 0.994 [0.983-0.998] / 1.000 / 0.988 | 0.986 [0.971-0.993] / 1.000 / 0.970 | 0.956 [0.934-0.971] / 0.986 / 0.918 | 0.976 [0.959-0.986] / 0.996 / 0.954 |
| bash4.2_i32 | keyskip2 | 0.988 [0.974-0.995] / 1.000 / 0.978 | 0.980 [0.964-0.989] / 1.000 / 0.956 | 0.966 [0.946-0.979] / 0.996 / 0.939 | 0.974 [0.956-0.985] / 1.000 / 0.951 |
| php_mt_scale | keyskip1 | 0.984 [0.969-0.992] / 0.996 / 0.974 | 0.988 [0.974-0.995] / 1.000 / 0.976 | 0.976 [0.959-0.986] / 0.985 / 0.965 | 0.976 [0.959-0.986] / 0.983 / 0.970 |
| php_mt_scale | keyskip2 | 0.984 [0.969-0.992] / 1.000 / 0.967 | 0.988 [0.974-0.995] / 0.996 / 0.981 | 0.966 [0.946-0.979] / 0.992 / 0.936 | 0.968 [0.949-0.980] / 0.981 / 0.953 |
| php_mt_mod | keyskip1 | 0.988 [0.974-0.995] / 1.000 / 0.972 | 0.984 [0.969-0.992] / 1.000 / 0.963 | 0.958 [0.937-0.972] / 0.985 / 0.928 | 0.960 [0.939-0.974] / 1.000 / 0.926 |
| php_mt_mod | keyskip2 | 0.982 [0.966-0.991] / 0.996 / 0.969 | 0.988 [0.974-0.995] / 1.000 / 0.976 | 0.940 [0.916-0.958] / 0.980 / 0.898 | 0.972 [0.954-0.983] / 0.980 / 0.964 |
| php_php_scale | keyskip1 | 0.984 [0.969-0.992] / 0.996 / 0.972 | 0.988 [0.974-0.995] / 1.000 / 0.973 | 0.960 [0.939-0.974] / 0.989 / 0.927 | 0.976 [0.959-0.986] / 0.996 / 0.954 |
| php_php_scale | keyskip2 | 0.992 [0.980-0.997] / 1.000 / 0.984 | 0.980 [0.964-0.989] / 0.996 / 0.965 | 0.950 [0.927-0.966] / 0.980 / 0.920 | 0.970 [0.951-0.982] / 1.000 / 0.933 |
| php_php_mod | keyskip1 | 0.986 [0.971-0.993] / 1.000 / 0.972 | 0.980 [0.964-0.989] / 1.000 / 0.959 | 0.960 [0.939-0.974] / 0.980 / 0.939 | 0.980 [0.964-0.989] / 0.985 / 0.974 |
| php_php_mod | keyskip2 | 0.982 [0.966-0.991] / 0.996 / 0.967 | 0.984 [0.969-0.992] / 1.000 / 0.966 | 0.944 [0.920-0.961] / 0.966 / 0.925 | 0.982 [0.966-0.991] / 0.996 / 0.967 |

## Realised FPR (2^16 fresh wrong-key heads per generator, frozen thresholds; target 1e-3)

- bash4.2: 43/65536 = 0.00066 [0.0005-0.0009]
- bash4.2_i32: 46/65536 = 0.00070 [0.0005-0.0009]
- php_mt_scale: 44/65536 = 0.00067 [0.0005-0.0009]
- php_mt_mod: 51/65536 = 0.00078 [0.0006-0.0010]
- php_php_scale: 63/65536 = 0.00096 [0.0008-0.0012]
- php_php_mod: 54/65536 = 0.00082 [0.0006-0.0011]

## Verdicts
- LP64 reproduces Round 35 I1: yes. bash4.2 natural 0.970-0.992 vs R35 I1 held-out 0.948-0.994 (EN_HALFVOWEL 0.958/0.962 vs 0.948/0.949; within binomial noise, ~+-0.01-0.02); FPR 6.6e-4 vs R35 8.4e-4 aggregate. Positive control passed.
- Cells under 0.85: none. Minimum natural power over all 48 cells = 0.940 (php_mt_mod keyskip2 EN_HALFVOWEL 0.940 [0.916-0.958]); every cell is >= 0.94. No Q5 reach restriction is needed for B2 on these four registers.
- ILP32 and the four PHP cells are statistically indistinguishable from LP64 (differences within Wilson intervals), as expected for a screen that sees a uniform-looking key.
- Realised FPR 6.6e-4 to 9.6e-4, all under the 1e-3 target (php_php_scale upper CI 0.0012 touches it; point estimate under).

## not_covered
- registers beyond these four (R35 I1 covers the other five on LP64 only; Greek/Hebrew/Norse via R36 I1); heads past 24 runes; 3+ skips in head; free relation; PHP seeds assumed uniform 32-bit (real seed structure e.g. time-based not modelled for plants; wrong-key FPR uses same); keystream-lag/ other generators; only the ciphertext head U[:24] for FPR; plaintext windows from testhalves (held-out half) only.

Files: PREREG.md, run.py, run.log, power_by_generator.json, fpr_by_generator.json, ledger.json. Runtime 7 s.
