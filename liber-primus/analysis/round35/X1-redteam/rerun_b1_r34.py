"""X1/R35 re-derivation of round34/B1 facts from on-disk artifacts (no sweep re-run)."""
import json, os, re, collections
H = os.path.dirname(os.path.abspath(__file__))
B = os.path.join(H, "..", "..", "round34", "B1-orbits-v3")
out = {}
summ = json.load(open(os.path.join(B, "sweep_summary_final.json")))
st = json.load(open(os.path.join(B, "sweep_summary.json")))
out["cells"] = {k: {"N": v["N_actual"], "best": v["best_pmax"], "seed": v["best_seed"], "reg": v["best_preg"],
                    "bar120_actual": v["bar120_actualN"], "bar120_decl": v["bar120_declN"], "clears": v["clears_actualN"]}
                for k, v in summ["cells"].items()}
out["phase"] = st["phase"]
out["chunk_arith"] = {"2^18": 1 << 18, "296*2^18": 296 * (1 << 18), "74*2^20": 74 * (1 << 20)}
log = open(os.path.join(B, "sweep.log")).read()
out["log_progress_lines"] = {v: len(re.findall(r"^%s chunk \d+/296" % v, log, re.M)) for v in ("bash4.2", "bash4.2_i32")}
out["log_last"] = {v: re.findall(r"^%s chunk (\d+)/296 t=(\d+)s" % v, log, re.M)[-1] for v in ("bash4.2", "bash4.2_i32")}
out["sweep_php_log"] = open(os.path.join(B, "sweep_php.log")).read().split("\n")
out["php_seeds_per_cell"] = {k: v["seeds_screened"] for k, v in st["cells"].items()}
out["php_tier_a_core_unfiltered"] = st["phase"]["php"]["tier_a_core"]
out["php_tier_a_dense_prefiltered"] = st["phase"]["php"]["tier_a_dense"]
out["tier_b_fraction"] = st["phase"]["php"]["tier_b_seeds"] / 2.0 ** 32
rows = [json.loads(l) for l in open(os.path.join(B, "sweep_rows.jsonl"))]
cnt = collections.Counter(r[0].split(":")[0] + ":" + r[0].split(":")[1] for r in rows[1:])
out["store_rows"] = len(rows) - 1
out["store_rows_by_cell"] = dict(cnt)
out["bash_decodes_expected_unstored"] = 2 * (st["cells"]["bash4.2"]["survivors"] + st["cells"]["bash4.2_i32"]["survivors"])
out["store_header_flags"] = {"key_space_says_ILP32_stated_fraction": "ILP32 stated fraction" in rows[0]["key_space"],
                             "power_EN_NOVOWEL": rows[0]["prefilter"]["power_EN_NOVOWEL"]}
rp = 0.66, 0.71
out["reach"] = {"pf_v3_operative": rp, "v3_recovery": (0.98, 1.00), "NOVOWEL": [round(0.66 * x, 3) for x in (0.98, 1.0)], "MODERN": [round(0.71 * x, 3) for x in (0.98, 1.0)]}
out["gap_reading"] = "2,621,440 seeds is logged AT t=38223 s; the last pre-sleep line is 1,966,080 at t=110 s; rate ~17.9k seeds/s -> cap 2100 s alone would reach ~%.2f%% of 2^32" % (100 * (2100 - 21) * (1966080 / (110 - 21)) / 2.0 ** 32)
json.dump(out, open(os.path.join(H, "rerun_b1_r34.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("log_progress_lines", "log_last", "php_seeds_per_cell", "store_rows", "store_rows_by_cell", "bash_decodes_expected_unstored", "store_header_flags", "tier_b_fraction", "reach", "gap_reading")}, indent=1))
