"""Build ledger.json and ledger_patches.json from the lane's stored results (no heavy compute)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R37 = json.load(open(os.path.join(LP, "analysis", "round37", "I2-pfv4-12reg", "sweep_summary_final.json")))["cells"]
S = json.load(open(os.path.join(HERE, "sweep_summary_final.json")))["cells"]
REPL = json.load(open(os.path.join(HERE, "replication_4.1_vs_R37.json")))
D = "2026-10-31"; EV = "analysis/round40/B1-bash-versions/"
common_ev = [EV + "RESULTS.md", EV + "PREREG.md", EV + "PREREG-ADDENDUM-1.md", EV + "generators.py", EV + "verification.json", EV + "sweep.py", EV + "sweep_summary_final.json"]
PLANTS = "10 EN_MODERN + 10 EN_NOVOWEL + 10 HEBREW per relation (60 plants), pooled >=3 recoveries in every register x skip split"


def cell(c, k): return c["%s|%s" % (c_name := k[0], k[1])]


def cdesc(src, name):
    o = []
    for rel in ("keyskip1", "keyskip2"):
        e = src["%s|%s" % (name, rel)]
        o.append("%s best %.3f (seed %d, %s) vs 12-register bar %.3f at actual N=%d (%.3f at N=1e6)" % (rel, e["best_pmax"], e["best_seed"], e["best_preg"], e["bar120_actualN"], e["N_actual"], e["bar120_declN"]))
    return "; ".join(o)


def ctl(v):
    c = json.load(open(os.path.join(HERE, "control_%s.json" % v)))
    return "control_%s.json: %d natural-rate plants (%s) through the real 2^16-seed chunk path; %d recovered end-to-end (pmax>=N=1e6 bars at L120 and L240, recovery>=0.90); gate (>=3 per pooled split) %s" % (v, c["n_plants"], PLANTS, c["recover_total"], c["gate_ge3_recover_each_pooled_split"])


NOT_COV_COMMON = "Heads with >= 3 skips in 24 runes; free relation; L=31; key offsets != 0 and sign +1; $RANDOM first used inside a command/process substitution (subshell reseed); registers outside the twelve; other reductions than %29; the seeds' time window outside tv_sec 2012-01-01..2014-06-01."
R37_ILP = lambda n: R37["bash4.2_i32|%s" % n]; R37_LP = lambda n: R37["bash4.2|%s" % n]


def entry(i, status, ver, hyp, cov, res, tc, notcov, reopens, pc, store=None, extra=None):
    e = {"id": i, "round": 40, "lane": "B1", "date": D, "status": status, "positive_control": pc, "control_detail": ctl(ver) if ver else "", "hypothesis": hyp, "coverage": cov, "result": res,
         "threshold": "12-register POT bars from round36/B1 null12.json (mu, beta per cell) at actual N and N=1e6; pf_v4_12 frozen point (round37/I2 frozen_op12.json) unchanged",
         "threshold_fixed_in_advance": True, "three_conditionals": tc, "not_covered": notcov, "reopens_if": reopens, "evidence": common_ev + [EV + "control_%s.json" % ver] if ver else common_ev}
    if store: e["sweep_store"] = store; e["evidence"] = e["evidence"] + [store]
    if extra: e.update(extra)
    return e


tc41 = {"key_space": "bash 4.0/4.1 auto-seed sbrand(tv_sec ^ tv_usec ^ getpid()): the same 74 x 2^20 = 77,594,624-seed orbit as 4.2, LP64 and ILP32, %29, offset 0, sign -1",
        "transition_model": "keyskip1+keyskip2 under beam_v3 panel_max, L120 screen / L240 gate; heads with <= 2 skips in 24 runes; not free, not L31", "adjudicator_register": "panel-R36, 12 registers; pf_v4_12 reach 0.952-0.994 per register x v3 recovery (60-plant control: 59-60/60)"}
cov41 = ("Covered BY IDENTITY, not re-run in full: the RANDOM code of bash 4.0 and 4.1 is textually identical and differs from 4.2 only in the zero-state branch (seedrand() vs the constant 123459876); state 0 is reachable only from s = m*(2^31-1), heuristic expected orbit seeds touching it in 1024 steps: LP64 2e-7, ILP32 ~37 of 77.6M. Every other orbit seed therefore emits the bash 4.2 stream, so R37-I2's complete bash 4.2 sweeps (296/296 chunks, LP64 65,815 + ILP32 65,971 survivors, all decoded) are the 4.x result. Independent re-execution through the 4.1 generator and the full pipeline: %d of 296 chunks (%d seeds, %d survivors), survivor/decode sets identical to R37's and pmax equal to the stored 3 dp (max |diff| %.4f = rounding)." % (REPL["chunks"], REPL["seeds"], REPL["survivors_4.1"], REPL["max_abs_pmax_diff_3dp"]))
res41 = "0 flagged, 0 near-miss. LP64 (R37-I2): " + cdesc(R37, "bash4.2").replace("keyskip1 best", "keyskip1 best", 1) if False else None
lp = "; ".join("%s best %.3f vs %.3f (N=%d; %.3f at N=1e6)" % (r, R37_LP(r)["best_pmax"], R37_LP(r)["bar120_actualN"], R37_LP(r)["N_actual"], R37_LP(r)["bar120_declN"]) for r in ("keyskip1", "keyskip2"))
il = "; ".join("%s best %.3f vs %.3f (N=%d; %.3f at N=1e6)" % (r, R37_ILP(r)["best_pmax"], R37_ILP(r)["bar120_actualN"], R37_ILP(r)["N_actual"], R37_ILP(r)["bar120_declN"]) for r in ("keyskip1", "keyskip2"))
res41 = "0 flagged, 0 near-miss. LP64: " + lp + ". ILP32: " + il + "."
reop41 = "a bash 4.0/4.1 binary run shows a stream differing from 4.2's on an orbit seed; the oracle flags a row; or a true-key head with > 2 skips in 24 runes is shown; or a register outside the twelve is added."
ent = []
ent.append(entry("R40-B1-BASH41-RANDOM-AUTOSEED", "negative", "4.1", "The LP2 key is the bash 4.1 auto-seed $RANDOM stream (tv_sec ^ tv_usec ^ pid orbit, LP64 or ILP32), <= 2 key skips in the first 24 runes, plaintext in one of the 12 panel-R36 registers.",
    cov41, res41, tc41, NOT_COV_COMMON + " Seeds whose stream enters state 0 (nondeterministic re-seed). No bash 4.1 binary was run (generator verified by source identity to the L1-verified 4.2).", reop41, "passed",
    store=EV + "replication_rows_bash4.1.jsonl", extra={"declares_sweep": True, "generator_verification": "source-identity to bash 4.2 (R19-G1 L1 binary) + R19-G1 cross-implementation 0/2000 mismatches (verification.json)"}))
ent.append(entry("R40-B1-BASH40-RANDOM-AUTOSEED", "negative", "4.0", "The LP2 key is the bash 4.0 auto-seed $RANDOM stream (tv_sec ^ tv_usec ^ pid orbit, LP64 or ILP32), <= 2 key skips in the first 24 runes, plaintext in one of the 12 panel-R36 registers.",
    "Covered BY IDENTITY: the bash 4.0 RANDOM code block is textually identical to bash 4.1 (empty diff, verification.json) and so shares the 4.1 -> 4.2 equivalence and R37-I2's complete 4.2 sweeps (296/296 chunks per ABI). Own control (control_4.0.json) run through the 4.0 generator. No separate orbit re-execution (the 4.1 replication of %d chunks stands for both)." % REPL["chunks"],
    res41, tc41, NOT_COV_COMMON + " Seeds whose stream enters state 0. No bash 4.0 binary was run.", reop41, "passed", extra={"generator_verification": "source-identity to bash 4.1/4.2 (empty 4.0-vs-4.1 diff)"}))
r32 = S["bash3.2|keyskip1"], S["bash3.2|keyskip2"]
ent.append(entry("R40-B1-BASH32-RANDOM-AUTOSEED", "partially-run", "3.2", "The LP2 key is the bash 3.2 auto-seed $RANDOM stream (seed = pid + time(0); ANSI-C LCG 1103515245/12345), <= 2 key skips in the first 24 runes, plaintext in one of the 12 panel-R36 registers.",
    "Full enumerated orbit: 291/291 chunks, 76,237,568 seeds = every integer in [SEC0+1, SEC1+32768] (tv_sec 2012-01-01..2014-06-01 + pid 1..32768); %d survivors, all decoded under both relations (%d decodes each)." % (r32[0]["survivors"], r32[0]["N_actual"]),
    "0 flagged, 0 near-miss. " + cdesc(S, "bash3.2") + ".",
    {"key_space": "bash 3.2 sbrand(getpid() + shell_start_time): 76,237,568 consecutive integer seeds (pid <= 32768), LCG stream, %29, offset 0, sign -1 (ABI-independent)", "transition_model": tc41["transition_model"], "adjudicator_register": tc41["adjudicator_register"]},
    NOT_COV_COMMON + " pid_max > 32768 (up to 4,194,304; ~5.5% more seeds); a bash 3.2 binary was not available: the generator is source-derived and cross-checked only against R19-G1's second transcription and the ISO-C-sample LCG sequence (RANDOM=1 -> 16838, 5758, 10113, ...).",
    "a bash 3.2 binary (or its published sequence for a stated seed) confirms the generator, which would upgrade this row to negative; or a pid_max > 32768 extension is run; or the oracle flags a row.", "passed",
    store=EV + "sweep_rows.jsonl", extra={"declares_sweep": True, "generator_verification": "source-derived, unverified (no bash 3.2 binary): Q5 -> partially-run"}))
ent.append(entry("R40-B1-BASH51-RANDOM-AUTOSEED", "negative", "5.1", "The LP2 key is the bash 5.1 auto-seed $RANDOM stream of a NON-PIE build (genseed() with constant address term; folded output), <= 2 key skips in the first 24 runes, plaintext in one of the 12 panel-R36 registers.",
    "Full enumerated family: 352/352 chunks, 92,274,688 seeds = prefixes (tv_sec>>20) XOR {0..7} (88 x 2^20); the x=4 image (one build, 74 x 2^20 = 77,594,624 seeds, 296 chunks) first; %d survivors, all decoded under both relations. PIE/ASLR builds (effective orbit ~2^31 = 2.15e9 seeds) NOT covered: enumerated fraction of that orbit ~4.3%%." % S["bash5.1|keyskip1"]["survivors"],
    "0 flagged, 0 near-miss. " + cdesc(S, "bash5.1") + ".",
    {"key_space": "bash 5.1 genseed() = tv_sec ^ tv_usec ^ pid ^ ppid ^ uid ^ constant (non-PIE): 88 x 2^20 seeds, 32-bit Lehmer, folded output (compat > 50), %29, offset 0, sign -1", "transition_model": tc41["transition_model"], "adjudicator_register": tc41["adjudicator_register"]},
    NOT_COV_COMMON + " PIE/ASLR 5.1 builds (the address term randomises seed bits 12-31); BASH_COMPAT<=50 (unfolded output); bash 5.0, 5.2, 5.3 seeding differences not read; the 2012-2014 time window is anachronistic for 5.1 (released 2020) and was kept only for comparability.",
    "the oracle flags a row; a PIE-orbit (2^31) sweep is run; a BASH_COMPAT=50 or other 5.x build is hypothesised with evidence; or a true-key head with > 2 skips is shown.", "passed",
    store=EV + "sweep_rows.jsonl", extra={"declares_sweep": True, "generator_verification": "verified against a live bash 5.3.9 binary (6 seeds x 200 values, all match) + R19-G1 cross-implementation 0/2000 mismatches"}))
json.dump({"$comment": "written by R40 B1 lane agent", "entries": ent}, open(os.path.join(HERE, "ledger.json"), "w"), indent=1)

line = ("| Other bash versions and seedings; other PHP variants; offsets other than 0; sign +1 on most rows | bash 3.2 (pid_max > 32768 only), bash 5.x PIE/ASLR builds (orbit ~2^31) and BASH_COMPAT<=50, a real 32-bit bash 4.2 beyond the swept ILP32 orbit, non-zero key offsets | partial | "
        "[[R40-B1-BASH41-RANDOM-AUTOSEED]] [[R40-B1-BASH40-RANDOM-AUTOSEED]] [[R40-B1-BASH32-RANDOM-AUTOSEED]] [[R40-B1-BASH51-RANDOM-AUTOSEED]] [[R32-B1-BASH42-RANDOM-AUTOSEED]] | a stated offset, a pid_max extension, a PIE-orbit sweep, or a bash 3.2 binary confirming the generator |")
pins = ["<!-- pin: R40-B1-BASH32-RANDOM-AUTOSEED | 76,237,568 -->", "<!-- pin: R40-B1-BASH51-RANDOM-AUTOSEED | 92,274,688 -->",
        "<!-- pin: R40-B1-BASH32-RANDOM-AUTOSEED | 7.098 -->", "<!-- pin: R40-B1-BASH51-RANDOM-AUTOSEED | 6.522 -->", "<!-- pin: R40-B1-BASH41-RANDOM-AUTOSEED | 7.065 -->"]
patches = {"$comment": "R40 B1 (not applied by lane). Replaces the MEASURED-CEILING section-3 'Other bash versions and seedings' line; pins must be added next to it. The new line says 'partial' (a not-excluded remainder stays), cites only rows that exist in ledger.json of this lane once applied.",
           "measured_ceiling_replace_line_starting": "| Other bash versions and seedings; other PHP variants; offsets other than 0; sign +1 on most rows |",
           "measured_ceiling_new_line": line, "pins_to_add": pins,
           "patches": [{"id": "R32-B1-BASH42-RANDOM-AUTOSEED", "coverage_add": "R40-B1: bash 4.0/4.1 share the 4.2 LP64/ILP32 stream except the zero-state branch (covered by identity with R37-I2); bash 3.2 (76,237,568 seeds) and bash 5.1 non-PIE (92,274,688 seeds) orbits swept in full under pf_v4_12 + beam_v3 + panel-R36: 0 flagged, 0 near-miss."},
                       {"id": "R37-I2-PFV4-12REG-ORBIT", "coverage_add": "R40-B1: 8/296 chunks re-executed through the bash 4.1 generator: identical survivor and decode sets, pmax equal at 3 dp."}]}
json.dump(patches, open(os.path.join(HERE, "ledger_patches.json"), "w"), indent=1)
print("ok", [e["id"] + ":" + e["status"] for e in ent])
