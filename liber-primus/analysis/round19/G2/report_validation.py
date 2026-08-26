"""Human-readable digest of validation.json (lane G2)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "validation.json")))

print("installed perl:", d["installed_perl"], "| overall:", "PASS" if d["overall_pass"] else "FAIL")
for g in ("A", "B", "C"):
    rows = d[f"gate_{g}"]["rows"]
    print(f"GATE {g}: {'PASS' if d[f'gate_{g}']['pass'] else 'FAIL'}  {len(rows)} checks")

print("\n--- GATE A2, per reduction (all seeds) ---")
seen = {}
for r in d["gate_A"]["rows"]:
    if r["gate"] == "A2":
        seen.setdefault(r["what"], []).append(r["match"])
for k, v in seen.items():
    print(f"  {k:12s} {sum(v)}/{len(v)} seeds byte-exact   first8={[]}")

print("\n--- GATE A2 first-8 sample, seed 3301 ---")
for r in d["gate_A"]["rows"]:
    if r["gate"] == "A2" and r["seed"] == 3301:
        print(f"  {r['what']:12s} perl={r['first8_perl']}  mine={r['first8_mine']}")

print("\n--- GATE B: perl rand() vs glibc drand48(), 1024 draws each ---")
for r in d["gate_B"]["rows"]:
    print(f"  seed {r['seed']:>11}  match={r['match']}  glibc[0]={r['first2_glibc'][0]}")

print("\n--- GATE C3: srand() argument coercion ---")
hdr = f"  {'arg':<14} {'5.40 srand ret':<22} {'5.14 seed32':>12} {'5.40 seed32':>12}  {'diverge':>7}  model==perl5.40"
print(hdr)
for r in d["gate_C"]["rows"]:
    if r["gate"] == "C3":
        for c in r["detail"]:
            print(f"  {repr(c['arg']):<14} {c['perl540_srand_ret']:<22} "
                  f"{c['my_5.14_seed32']:>12} {c['my_5.40_seed32']:>12}  "
                  f"{str(c['eras_diverge']):>7}  {c['model_matches_running_perl']}")

print("\n--- GATE C1/C2 ---")
for r in d["gate_C"]["rows"]:
    if r["gate"] in ("C1", "C2"):
        print(f"  {r['gate']}  {r['what']:<55} match={r['match']}"
              + (f"  mismatches={r['mismatches']}/{r['n']}" if "mismatches" in r else ""))
