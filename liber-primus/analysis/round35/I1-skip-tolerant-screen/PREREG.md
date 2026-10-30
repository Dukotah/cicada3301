# R35 / I1 PREREG (dated 2026-10-30, written before any output file; addenda go in PREREG_ADDENDUM_*.md)

Question: can a skip-tolerant head screen (pf_v4) recover true-key heads that contain key skips, at FPR <= 1e-3,
with EN_NOVOWEL power >= 0.85 and every other of the nine registers >= 0.90 on NATURAL-rate plants?

Statistic: per-register Viterbi over per-position cumulative key offset s_t*a (s_t nondecreasing, s_0=0, s_t<=k),
a = 1 (keyskip1) or 2 (keyskip2), score_r = max_path [ sum trigram log10 LM_r(P_t,P_t+1,P_t+2) - pen*s_end/ln10 ],
P_t = (C_t - K[t + a*s_t]) % 29; then the pf_v3 `lse` over the nine registers (nats, same LN10/(m-2)ln29 conversion).
k=0 must reproduce pf_v3.lse_stat exactly (unit check). Grid: m in {20,24}, k in {1,2}, a in {1,2}, pen (nats/skip) in {0,1,2,3}.
Relation-agnostic "both" screen = OR of the a=1 and a=2 masks (each at FPR/2 so the OR sits at the stated FPR).

Nulls: 2^17 = 131072 wrong-key heads per generator (bash LP64, bash ILP32, PHP mt_scale, mt_mod, php_scale, php_mod),
real generators, decoded against real C[:28]. Split in halves A/B per generator: threshold = pooled-over-generators
quantile on half A; FPR reported on held-out half B pooled and per generator (flag any generator > 1.5e-3 at the 1e-3 point).
Plants: 2000 per register (all nine, testhalves.npz, random windows), per relation (keyskip1 via sk.encipher_keyskip,
keyskip2 via enc_pair-style j+=2), enciphered through the real encipherer with bash LP64 keystream heads, natural skip rate,
NO selection of skip-free windows. Plants 0-999 per register = calibration, 1000-1999 = held-out. Choose pen per (m,k,a)
on calibration plants+half-A nulls by maximising min-over-registers natural power at FPR 1e-3 (tie: smaller pen);
report ALL power on held-out plants. Power reported split: skip-free head / with-skip head / natural (all); also
conditional on no doublet in the ciphertext head (as the real C[:40] has none).
FPR points: 3e-4, 1e-3, 3e-3, 1e-2. Bar: EN_NOVOWEL >= 0.85 and others >= 0.90 (held-out natural) at FPR <= 1e-3.
Q5: if no (m,k,a) reaches the bar report best curve and the operating point at stated higher FPR; if even 1e-2 fails,
record "skips in the head are not screenable at m<=24". Freeze (m,k,pen,thr) for B1; expose prefilter_mask(seeds,variant,Chead,LMT,m).
Throughput: heads/s end-to-end on 2^18 bash seeds, single process, pf_v3 vs pf_v4 (same m, and each at its frozen m); target <=3x.
Not covered: heads past the first 24 runes, skip patterns beyond k, free relation, registers outside the nine, generators other than the six.
Compute cap ~45 min, one process, no git.
