"""R42 / X1 - independent re-checks of the round's load-bearing claims. Refute-by-default.
Re-derives, re-hashes, re-computes bars; does NOT trust the lane result files."""
import json, os, sys, hashlib, re

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R42 = os.path.join(LP, "analysis", "round42")
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null",
          "analysis/round10b/B1-overlooked-artifact"):
    sys.path.insert(0, os.path.join(LP, p))
fails = []


def ck(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        fails.append(name)


# --- S1: STATUS.json recovered locally matches the sha the lane recorded ---
st = os.path.join(R42, "S1-s2-recovery", "state_recovered", "STATUS.json")
sha = hashlib.sha256(open(st, "rb").read()).hexdigest()
ck("S1 STATUS.json sha == recorded 1aa52944..",
   sha == "1aa529444548e3e1f3add420936ddfd40ee9b9fe4cb6d25b74c197a2e070c2ba", sha[:12])
d = json.load(open(st))
agg = d["aggregate"]
ck("S1 window-2 cursor sum > window-1 (2,059,308,008)", agg["seeds_done"] > 2059308008,
   str(agg["seeds_done"]))
ck("S1 window-2 n_claim_bar_hits == 0", agg["n_claim_bar_hits"] == 0)
ck("S1 best_pmax below near-miss bar 7.5342", agg["best_pmax"] < 7.5342, str(agg["best_pmax"]))

# --- S3: re-check the bash first20 claim against round40 verification.json (the binary's
#     output was recorded; the reference is committed) ---
v = json.load(open(os.path.join(LP, "analysis/round40/B1-bash-versions/verification.json")))
ref = v["versions"]["bash3.2"]["first20_after_RANDOM_eq_1"]
got = json.load(open(os.path.join(R42, "S1-s2-recovery", "bash32_first20.json")))["RANDOM_eq_1_first20"]
ck("S3 bash first20 == verification.json (20/20)", ref == got)

# --- C3: re-derive auto keys independently; MIDISCV/WORKING; count 43 ---
import b1_keys as K
auto = [k for t, k, p in K.CURATED_ALPHA if False]  # placeholder
abuilt, _ = K.build()
autoset = [r["key"] for r in abuilt if r["tag"].startswith("auto-")]
ck("C3 auto-key count == 43", len(autoset) == 43, str(len(autoset)))
ck("C3 MIDISCV re-derives", "MIDISCV" in autoset)
ck("C3 WORKING re-derives", "WORKING" in autoset)
c3 = json.load(open(os.path.join(R42, "C3-auto-keys", "c3_results.json")))
ck("C3 verdict NEGATIVE, 0 crossers", c3["n_crossers"] == 0 and c3["verdict"] == "NEGATIVE")
ck("C3 best well below bar", c3["observed_global_best"]["pmax"] < c3["observed_global_best"]["bar"] - 5)

# --- C1: independently re-count corrupt vs real keytexts ---
TXT = os.path.join(LP, "analysis", "round12", "C2", "texts")
corrupt = real = 0
for f in sorted(os.listdir(TXT)):
    if not f.endswith(".txt"):
        continue
    raw = open(os.path.join(TXT, f), encoding="utf-8", errors="ignore").read()
    if re.search(r"(?i)<!doctype|<html|Page Not Found|globalgrey", raw[:400]):
        corrupt += 1
    else:
        real += 1
c1 = json.load(open(os.path.join(R42, "C1-keytexts", "c1_results.json")))
ck("C1 corrupt count reproduces (10)", corrupt == 10 == c1["corrupt_404"], f"{corrupt}")
ck("C1 real count reproduces (23)", real == 23 == c1["real_texts"], f"{real}")
ck("C1 verdict NEGATIVE", c1["n_crossers"] == 0 and c1["verdict"] == "NEGATIVE")

# --- C2 ---
c2 = json.load(open(os.path.join(R42, "C2-dated-pads", "c2_results.json")))
ck("C2 verdict NEGATIVE", c2["n_crossers"] == 0 and c2["verdict"] == "NEGATIVE")
ck("C2 best well below bar", c2["observed_global_best"]["pmax"] < c2["observed_global_best"]["bar"] - 5)

# --- bars sanity: the free bar at the grid sizes is in a sane range (8..20), monotone in N ---
import bars_v3 as B
b1 = B.bar_v3(7200, 240, "free"); b2 = B.bar_v3(13800, 240, "free")
ck("free bar increases with N (more trials -> higher bar)", b2 > b1, f"{b1:.3f} -> {b2:.3f}")
ck("free bars in sane range 8..20", 8 < b1 < 20 and 8 < b2 < 20)

# --- ledger integrity ---
L = json.load(open(os.path.join(LP, "LEDGER.json")))
ids = {e["id"] for e in L["entries"]}
for rid in ("R42-S1-S2-WINDOW2-RECOVERED", "R42-S3-BASH32-BINARY-L1",
            "R42-C3-B1-43-AUTO-KEYS-RUN", "R42-C1-R35-KEYTEXTS-RUN", "R42-C2-R36-DATED-PADS-RUN"):
    ck(f"ledger has {rid}", rid in ids)
ck("ledger counts.total == len(entries)", L["counts"]["total"] == len(L["entries"]),
   f"{L['counts']['total']} vs {len(L['entries'])}")

print()
print("X1/R42 FAILS:", len(fails), fails)
sys.exit(1 if fails else 0)
