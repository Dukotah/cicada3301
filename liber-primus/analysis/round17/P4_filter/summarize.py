"""Pull the RESULTS.md tables out of results.json. Run after controls.py."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "results.json")))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
real = r["real"]

print("== GATE ==", r["gates"]["PASS"], "lag1_z power",
      r["gates"]["uniform_vs_machine"]["lag1_z"]["power"])
print("== calibration ==", json.dumps(r["calibration"], indent=1)[:600])
print("\n== fairness lag1 ==")
for k, v in r["fairness_lag1_rate"].items():
    print("  %-22s %s" % (k, v))

print("\n== LAG PROFILE (real) ==")
for k in range(1, 9):
    print("  lag%d  rate %.5f  z %+.2f" % (k, real["lag%d_rate" % k], real["lag%d_z" % k]))
print("  bleed23 rate %.5f z %+.2f | bleed28 rate %.5f z %+.2f | bleed_fraction %+.4f"
      % (real["bleed23_rate"], real["bleed23_z"], real["bleed28_rate"],
         real["bleed28_z"], real["bleed_fraction"]))

print("\n== BLEED BOUND ==", json.dumps(r["bleed_bound"], indent=1))

print("\n== RUNG TABLE ==")
hdr = "%-20s %8s %8s %8s %8s %-26s" % ("rung", "supp2-8", "cmbPow", "logLR", "called", "verdict")
print(hdr)
for name, a in r["adjudication"].items():
    print("%-20s %7.2f%% %8.3f %8.1f %8s %-26s"
          % (name, 100 * a["lag2to8_suppression"], a["combined"]["power"],
             a["combined"]["real_logLR_machine_over_hand"],
             a["combined"]["real_called"], a["verdict"]))

print("\n== PRIMARY STATS, per rung (power | real inside machine95 | real inside hand95) ==")
for name, a in r["adjudication"].items():
    print(" %s   [supp2-8 %.2f%%]" % (name, 100 * a["lag2to8_suppression"]))
    for k, v in a["primary"].items():
        print("   %-22s real %+9.4f  power %.3f  inM95 %-5s (p=%.3f)  inH95 %-5s (p=%.3f)"
              % (k, v["real"], v["power_machine_vs_hand"], v["inside_machine_95"],
                 v["p_two_sided_machine"], v["inside_hand_95"], v["p_two_sided_hand"]))

print("\n== SECONDARY, worst rung (hand_bleed_small) ==")
a = r["adjudication"]["hand_bleed_small"]
for k, v in a["secondary"].items():
    print("   %-22s real %+9.4f  power %.3f  inM95 %-5s  inH95 %-5s"
          % (k, v["real"], v["power_machine_vs_hand"], v["inside_machine_95"], v["inside_hand_95"]))

print("\n== SCOPE TEST (flat filter vs line-scoped filter) ==")
for k, v in r["scope_test"].items():
    if k == "combined":
        print("   combined: power %.3f  real logLR %.1f  called %s"
              % (v["power"], v["real_logLR_machine_over_hand"], v["real_called"]))
    else:
        print("   %-22s real %+9.4f  power %.3f  inFLAT95 %-5s (p=%.3f)  inLINE95 %-5s (p=%.3f)"
              % (k, v["real"], v["power_flat_vs_linescoped"], v["inside_flat_95"],
                 v["p_flat"], v["inside_linescoped_95"], v["p_linescoped"]))

print("\n== CONTROL MEANS for the key stats ==")
keys = ["lag1_rate", "bleed28_z", "chi2W29_mean", "chi2W58_mean", "chi2W116_mean",
        "chi2W290_mean", "gap_cv", "gap_2to4_z", "page_rate_dispersion",
        "page_homog_z", "half_split_z", "supp_drift_z", "dbl_line_cross_rate",
        "dbl_posinline_ks", "n_doublets", "bigram_offdiag_chi2_df", "dbl_gap_disp"]
names = ["uniform", "machine", "machine_lines", "hand_bleed_none", "hand_bleed_tiny",
         "hand_bleed_small", "hand_bleed_mid", "hand_bleed_strong", "hand_rebalance_only"]
print("%-24s %10s | " % ("stat", "REAL") + " | ".join("%-16s" % n[:16] for n in names))
for k in keys:
    row = "%-24s %10.4f | " % (k, real[k])
    row += " | ".join("%7.4f+-%-7.4f" % tuple(r["controls"][n][k]) if k in r["controls"][n]
                      else "%-16s" % "-" for n in names)
    print(row)
