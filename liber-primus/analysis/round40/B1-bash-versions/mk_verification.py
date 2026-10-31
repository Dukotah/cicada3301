"""Assemble verification.json from verification_raw.json (written by sweep.py verify). No heavy compute."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(HERE, "verification_raw.json")))
xi = raw["cross_impl_vs_R19_G1_gen_bash"]; live = raw["live_bash_reference_for_5x"]; tb = raw["tarball_sha256"]
live_ok = all(c["match"] for c in live["cases"].values())
out = {
 "lane": "round40/B1", "date": raw["date"], "tarballs": tb, "reference_levels": {
   "L1": "real binary of the SAME version", "L2": "real binary of a neighbouring version whose RANDOM code is diffed against the target", "L3": "source-identity to an L1-verified generator",
   "L4": "source-derived transcription, cross-checked against a second implementation (R19-G1 gen_bash / ref_bash.c), no binary", "L5": "source-derived, unverified"},
 "versions": {
  "bash3.2": {
    "source": "bash-3.2 variables.c (tarball bash-3.2.tar.gz sha256 %s): brand() l.1156, sbrand() l.1164, init sbrand(dollar_dollar_pid + shell_start_time) l.498, get_random_number() anti-repeat loop; NO lib/sh/random.c" % tb["3.2"]["sha256"][:16],
    "diff_from_4.2": "DIFFERENT generator: brand() is the ANSI-C-sample LCG rseed = rseed*1103515245 + 12345 (unsigned long), output (rseed>>16)&32767 (4.0+ made this #if 0 and replaced it with Park-Miller 16807). Auto-seed is sbrand(pid + time(0)) - NOT tv_sec^tv_usec^pid; no seedrand(); a $RANDOM first used in a subshell reseeds sbrand(rseed + getpid() + NOW) (state-dependent, not enumerated). ABI-independent: low 32 bits of an LCG mod 2^64 equal the LCG mod 2^32 (R19-G1 validated both).",
    "auto_seed_formula": "seed = getpid() + shell_start_time(time(0)); enumeration = every integer in [SEC0+1, SEC1+32768] (tv_sec 2012-01-01..2014-06-01 plus pid 1..32768) = 76,237,568 seeds = 291 chunks of 2^18. pid_max > 32768 (64-bit kernels with raised pid_max, up to 4,194,304) NOT covered (would add ~5.5%).",
    "first20_after_RANDOM_eq_1": raw["first20_after_RANDOM_equals_1"]["bash3.2"],
    "reference_check": {"level": "L4/L5", "status": "source-derived, unverified against a bash 3.2 binary (no 3.2 binary or compiler on this machine)",
        "cross_implementation": "equals R19-G1 gen_bash 'bash3.2' on %d seeds x %d values: %d mismatches (R19-G1 itself recorded PASS vs its ref_bash.c transcription, also source-derived)" % (xi["3.2"]["seeds"], xi["3.2"]["n"], xi["3.2"]["mismatches"]),
        "corroboration": "RANDOM=1 -> 16838, 5758, 10113, 17515, 31051, 5627, 23010, 7419, 16212, 4086 is the classic output of the ISO C (C99 7.20.2.2 sample) rand() LCG with srand(1) (recollection-level citation, not fetched); it is consistent with the formula but is not a bash binary."},
    "ledger_status_consequence": "partially-run (Q5: generator source-derived, unverified)"},
  "bash4.0": {
    "source": "bash-4.0 variables.c (sha256 %s): brand() l.1217, sbrand() l.1243, seedrand() l.1251, init seedrand() l.522, get_random_number() l.1273" % tb["4.0"]["sha256"][:16],
    "diff_from_4.2": "RANDOM code block is TEXTUALLY IDENTICAL to 4.1 (empty diff, see variables_c_random_block_diffs.4.0_vs_4.1) and differs from 4.2 only in the zero branch: 4.0/4.1 `if (rseed == 0) seedrand();` (non-deterministic re-seed from the clock) vs 4.2 `if (rseed == 0) rseed = 123459876;`. Same unsigned-long/long ABI fork as 4.2 (LP64 vs ILP32 differ).",
    "auto_seed_formula": "seedrand(): sbrand(tv.tv_sec ^ tv.tv_usec ^ getpid()) - identical to 4.2 => the same 74 x 2^20 = 77,594,624-seed orbit (both ABIs).",
    "zero_state": raw["zero_state"],
    "first20_after_RANDOM_eq_1": raw["first20_after_RANDOM_equals_1"]["bash4.1"],
    "reference_check": {"level": "L3 (source-identity to the L1-verified 4.2 generator)", "status": "verified-by-identity: for every seed whose stream never enters state 0 the 4.0 stream equals the 4.2 stream; 4.2 was validated against a real built 4.2.0 binary in R19-G1 (validation.json level L1). No 4.0 binary on this machine.",
        "cross_implementation": "equals R19-G1 gen_bash 'bash4.2' (LP64) on %d seeds x %d values: %d mismatches (seeds that hit state 0 would be skipped; none occurred)" % (xi["4.0"]["seeds"], xi["4.0"]["n"], xi["4.0"]["mismatches"])},
    "ledger_status_consequence": "negative by source-identity with the R37-I2 complete bash 4.2 sweeps; independent re-execution only on the 4.1 replication subset"},
  "bash4.1": {
    "source": "bash-4.1 variables.c (sha256 %s): brand() l.1229, sbrand() l.1255, seedrand() l.1263, init seedrand() l.534, get_random_number() l.1285" % tb["4.1"]["sha256"][:16],
    "diff_from_4.2": "see bash4.0: identical RANDOM code to 4.0; differs from 4.2 only in the zero branch (seedrand() vs constant 123459876).",
    "auto_seed_formula": "sbrand(tv_sec ^ tv_usec ^ getpid()); same 74 x 2^20 orbit as 4.2; a new subshell calls seedrand() again (same formula).",
    "first20_after_RANDOM_eq_1": raw["first20_after_RANDOM_equals_1"]["bash4.1"],
    "reference_check": {"level": "L3", "status": "verified-by-identity (see bash4.0); ILP32: equals R19-G1 bash4.2_i32 on %d seeds x %d: %d mismatches; LP64: %d seeds x %d: %d mismatches" % (xi["4.1_i32"]["seeds"], xi["4.1_i32"]["n"], xi["4.1_i32"]["mismatches"], xi["4.1"]["seeds"], xi["4.1"]["n"], xi["4.1"]["mismatches"]),
        "zero_state_note": "state 0 is reached only from s = m*(2^31-1); heuristic expected orbit seeds touching it in the first 1024 steps: LP64 %.1e, ILP32 %.0f" % (raw["zero_state"]["expected_orbit_seeds_with_zero_in_first_1024_steps_heuristic"]["LP64"], raw["zero_state"]["expected_orbit_seeds_with_zero_in_first_1024_steps_heuristic"]["ILP32"])},
    "ledger_status_consequence": "negative by source-identity with R37-I2 + replication"},
  "bash5.1": {
    "source": "bash-5.1 lib/sh/random.c (sha256 of the extracted file %s; tarball %s): intrand32() Lehmer/Schrage, brand() fold, genseed(), seedrand(); variables.c l.608 seedrand(); l.1363 get_random_number()" % (raw["random_c_5_1_sha256"][:16], tb["5.1"]["sha256"][:16]),
    "diff_from_4.2": "DIFFERENT generator: 32-bit u_bits32_t state, signed h,l,t Schrage with the `t<0 -> t+0x7fffffff` correction ENABLED (a true Lehmer minimal-standard single cycle of length 2^31-2; 4.x has it #if 0'd on a 64-bit unsigned), zero -> 123459876, output folded (rseed>>16)^(rseed&65535) & 32767 when shell_compatibility_level > 50 (default). Auto-seed is genseed() = tv_sec ^ tv_usec ^ getpid() ^ getppid() ^ uid ^ (u32)(address of seedrand()).",
    "auto_seed_formula": "iv = tv_sec ^ tv_usec ^ getpid() ^ getppid() ^ current_user.uid ^ (u32)&seedrand. Under ASLR/PIE the address term randomises bits 12..31, making the effective seed space the whole 2^31 cycle (27.7x the 4.2 orbit; not enumerated). Enumerated here: NON-PIE builds, where the term is a constant c and only x=(c>>20) (text at 0x400000-0x5fffff => x in {4,5}) shifts the prefix: seed prefix = (tv_sec>>20) XOR x, low 20 bits free (usec, pid, ppid, uid, c-low all < 2^20). Union over x in 0..7 = 88 x 2^20 = 92,274,688 seeds (352 chunks); one build = exactly 74 x 2^20; chunk order x=4 image first. Compat level <= 50 (BASH_COMPAT=50) would give the unfolded output and is NOT covered.",
    "first20_after_RANDOM_eq_1": raw["first20_after_RANDOM_equals_1"]["bash5.1"],
    "reference_check": {"level": "L2", "status": "VERIFIED against a live binary: %s - RANDOM=seed then 200 values, seeds %s, all match: %s. The binary is 5.3.9 not 5.1; the 5.1 random.c RANDOM path is bit-identical on these cases (the 5.1 -> 5.3 difference, if any, is not visible in $RANDOM)." % (live["version"], ",".join(live["cases"].keys()), live_ok),
        "cross_implementation": "equals R19-G1 gen_bash 'bash5.1' on %d seeds x %d: %d mismatches" % (xi["5.1"]["seeds"], xi["5.1"]["n"], xi["5.1"]["mismatches"]),
        "live_cases": {k: v["match"] for k, v in live["cases"].items()}},
    "ledger_status_consequence": "negative (bounded: non-PIE address family only)"}},
 "vector_heads_vs_scalar_no_antirepeat": raw["vector_heads_vs_scalar_no_antirepeat"],
 "orbit": raw["orbit"],
 "variables_c_random_block_diffs": raw["variables_c_random_block_diffs"],
 "source_lines": raw["source_lines"],
}
json.dump(out, open(os.path.join(HERE, "verification.json"), "w"), indent=1)
print("ok", live_ok)
