"""X1/R41 part B: independent re-check of C1 (R14/R15) from the persisted artefacts.

Own arithmetic only -- nothing imported from C1's lib.py/run_c1.py. Reads:
  C1/null_draws.jsonl        per-draw family maxima (bestW, bestP) x 2 fams x 3 blocks x 1000
  C1/result_R14.json, result_R15.json
  C1/ledger.json, ledger_patches.json; ../../../LEDGER.json
The per-unit null matrices (null_*_b*.npz, RESULTS SS4) are NOT in this tree (the lane ran in a
separate clone; only committed artefacts returned), so exceed_Z is checked for arithmetic
consistency only and marked NOT-RERUN as a recount.
"""
import json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
C1 = os.path.join(HERE, "..", "C1-r14-r15")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BLOCKS = (100, 250, 1000)
out = {"raw_p": [], "arith": [], "obs_best": [], "controls": {}, "ledger": {}, "fails": []}

def ck(name, ok, detail=""):
    (out["fails"].append(f"{name}: {detail}") if not ok else None)
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))

# ---- draws ----
draws = defaultdict(list)   # (fam, block) -> [(bestW, bestP)]
for line in open(os.path.join(C1, "null_draws.jsonl"), encoding="utf-8"):
    d = json.loads(line)
    draws[(d["fam"], d["block"])].append((d["bestW"], d["bestP"]))
for k, v in sorted(draws.items()):
    ck(f"draws {k} count=1000", len(v) == 1000, str(len(v)))

for fam in ("R14", "R15"):
    r = json.load(open(os.path.join(C1, f"result_{fam}.json")))
    # ---- observed bests re-derived ----
    wbest = max(r["obs_W"].values())
    pbest = r["obs_top_P"][0][0]
    # ---- per block ----
    for b in BLOCKS:
        blk = r["blocks"][str(b)]
        col = draws[(fam, b)]
        for lv, obs_best, idx in (("W", wbest, 0), ("P", pbest, 1)):
            cell = blk[lv]
            ck(f"{fam} b{b} {lv} obs_best matches re-derived",
               abs(cell["obs_best_pmax"] - obs_best) < 1e-9,
               f"{cell['obs_best_pmax']} vs {obs_best}")
            e_ge = sum(1 for t in col if t[idx] >= obs_best)
            e_gt = sum(1 for t in col if t[idx] > obs_best)
            # The stored exceed came from a float32 null matrix, so draws tying obs exactly can
            # round below it. Finding B-1: R14 b1000 P has 21 exact ties (block-1000 shuffles
            # preserve whole pages, so the observed best page recurs in the null); ties-in count
            # 854 vs stored 833 (p 0.854 vs 0.833, decision p 0.893 from b250 either way).
            ck(f"{fam} b{b} {lv} exceed_raw recount (>= {e_ge}, > {e_gt}, stored {cell['exceed_raw']})",
               cell["exceed_raw"] in (e_ge, e_gt),
               "stored matches neither tie convention")
            if e_ge != e_gt:
                out["arith"].append(f"{fam} b{b} {lv}: {e_ge - e_gt} exact ties; stored {cell['exceed_raw']}")
            ck(f"{fam} b{b} {lv} p_raw arithmetic",
               abs((1 + cell["exceed_raw"]) / (len(col) + 1) - cell["p_raw"]) < 1e-12)
            # Z: arithmetic consistency only (matrices absent)
            pz = (1 + cell["exceed_Z"]) / (cell["D"] + 1)
            ck(f"{fam} b{b} {lv} p_Z arithmetic", abs(pz - cell["p_Z"]) < 1e-12)
    # ---- decision = max over blocks; cross logic ----
    for lv in ("W", "P"):
        dec = r["decision"][lv]
        pzs = [r["blocks"][str(b)][lv]["p_Z"] for b in BLOCKS]
        prs = [r["blocks"][str(b)][lv]["p_raw"] for b in BLOCKS]
        ck(f"{fam} {lv} decision_p_Z = max", dec["decision_p_Z"] == max(pzs))
        ck(f"{fam} {lv} decision_p_raw = max", dec["decision_p_raw"] == max(prs))
        ck(f"{fam} {lv} crosses false & consistent",
           dec["crosses"] == (max(pzs) <= dec["alpha"] and max(prs) <= dec["alpha"]) and not dec["crosses"])
    # ---- controls ----
    pl = r["plants"]
    rec = sum(1 for p in pl if p["recognised"])
    amax = sum(1 for p in pl if p["argmax_is_planted_variant"])
    cc = r["control_cells"]
    ck(f"{fam} plants all recognised ({rec}/{len(pl)})", rec == len(pl))
    # argmax_is_planted_variant is informational, not a C1 claim: W plants 100%, P plants ~50%
    # (the planted page competes with other pages of the same planted variant). Recorded only.
    cks = f"{fam} argmax info: {amax}/{len(pl)} (not a claimed property)"
    print("NOTE " + cks)
    ck(f"{fam} control_cells sum = plants",
       sum(c["n"] for c in cc.values()) == len(pl) and
       sum(c["recognised"] for c in cc.values()) == rec)
    out["controls"][fam] = {"n": len(pl), "recognised": rec, "argmax": amax}
    # ---- null maxima quoted in RESULTS SS1 ----
    # Finding B-3: the RESULTS SS1 parenthetical quotes the BLOCK-1000 maxima only; the
    # all-blocks maxima (what each plant record's recognition actually used,
    # null_best_max_allblocks) are larger. Both are checked; the parenthetical is a wording slip.
    wmax = max(t[0] for b in BLOCKS for t in draws[(fam, b)])
    pmax_ = max(t[1] for b in BLOCKS for t in draws[(fam, b)])
    w1k = max(t[0] for t in draws[(fam, 1000)])
    p1k = max(t[1] for t in draws[(fam, 1000)])
    out["obs_best"].append({fam: {"W": wbest, "P": pbest, "null_W_max": wmax, "null_P_max": pmax_,
                                  "null_W_max_b1000": w1k, "null_P_max_b1000": p1k}})
    want = {"R14": (4.62, 5.50), "R15": (3.92, 4.80)}[fam]
    ck(f"{fam} RESULTS parenthetical = b1000 maxima ({w1k:.2f}/{p1k:.2f} vs {want[0]}/{want[1]})",
       abs(w1k - want[0]) < 0.005 and abs(p1k - want[1]) < 0.005)
    allb = {"R14": (5.23, 5.81), "R15": (4.25, 5.65)}[fam]
    ck(f"{fam} all-blocks null maxima (recognition basis) {wmax:.2f}/{pmax_:.2f}",
       abs(wmax - allb[0]) < 0.005 and abs(pmax_ - allb[1]) < 0.02)
    ck(f"{fam} plant records' null_best_max_allblocks consistent",
       all(abs(p["null_best_max_allblocks"] - (wmax if p["level"] == "W" else pmax_)) < 0.005
           for p in pl))

# ---- expected counts: R14 120 plants, R15 144 ----
ck("R14 plant count 120", out["controls"]["R14"]["n"] == 120)
ck("R15 plant count 144", out["controls"]["R15"]["n"] == 144)

# ---- RESULTS SS1 table p values ----
tab = {("R14", "W"): (0.538, 0.374), ("R14", "P"): (0.886, 0.893),
       ("R15", "W"): (0.641, 0.749), ("R15", "P"): (0.771, 0.424)}
for fam in ("R14", "R15"):
    r = json.load(open(os.path.join(C1, f"result_{fam}.json")))
    for lv in ("W", "P"):
        dz, dr = tab[(fam, lv)]
        d = r["decision"][lv]
        ck(f"{fam} {lv} table decision p ({dz}/{dr})",
           abs(d["decision_p_Z"] - dz) < 0.0006 and abs(d["decision_p_raw"] - dr) < 0.0006)

# ---- ledger: filed rows equal the lane's rows; patches applied ----
L = json.load(open(os.path.join(LP, "LEDGER.json")))
ids = {e["id"]: e for e in L["entries"]}
lane = json.load(open(os.path.join(C1, "ledger.json")))["entries"]
for e in lane:
    cur = ids.get(e["id"])
    if cur is None:
        ck(f"ledger row {e['id']} filed", False, "missing"); continue
    # Exact equality except where a later patch APPENDED to a text field (part B appends to
    # notes/not_covered): there the lane's text must survive as a prefix of the filed value.
    diff = [k for k, v in e.items()
            if cur.get(k) != v and not (isinstance(v, str) and str(cur.get(k, "")).startswith(v))]
    ck(f"ledger row {e['id']} == lane text (+appends)", not diff, "diff fields: " + ",".join(diff))
pats = json.load(open(os.path.join(C1, "ledger_patches.json")))["patches"]
for p in pats:
    e = ids.get(p["id"])
    for k, v in p.items():
        if k == "id": continue
        if e is None:
            ck(f"patch {p['id']}.{k}", False, "row missing"); continue
        if k == "status":
            ok = e.get("status") == v
        elif k == "status_note":                      # filed into `notes`
            ok = v[:50] in str(e.get("notes", ""))
        elif k.endswith("_replace"):                  # full-field replacement
            ok = str(e.get(k[: -len("_replace")], "")) == v
        elif k.endswith("_add"):                      # appended to the field
            ok = v[:50] in str(e.get(k[: -len("_add")], ""))
            # C1's R30-B1 not_covered_add was never applied and its text is wrong (finding
            # B-2): superseded by ledger_patches_b.json, whose corrected text IS in the row.
            if not ok and p["id"] == "R40-C1-R30-B1-ARTIFACT-KEYS":
                ok = "R41-X1B: C1's patch text" in str(e.get("not_covered", ""))
                ck(f"patch {p['id']}.{k} superseded by part B corrected text", ok)
                continue
        else:
            ok = False
        ck(f"patch {p['id']}.{k}", ok)

# ---- r44 kill ----
r44 = json.load(open(os.path.join(C1, "r44_first6.json")))
ck("R44 kill: all 6 recoveries < 0.90",
   len(r44) == 6 and all(x < 0.90 for x in r44),
   f"min {min(r44):.3f} max {max(r44):.3f}")

print()
print("FAILS:", len(out["fails"]))
json.dump(out, open(os.path.join(HERE, "x1b_c1_out.json"), "w"), indent=1)
sys.exit(1 if out["fails"] else 0)
