"""R46/S2 — unseal and score (PREREG §5–6). Refuses to run unless all 13 frozen batches exist and match
reads_frozen.sha256. Records those hashes + time BEFORE opening sealed.json or any S1 file.
Inputs: reads_batch*.json, sealed.json, template_calls.json, round45/S1-transcription/adjudications.json.
Output: results.json, unseal.log
"""
import hashlib
import json
import math
import os
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402

# ---------------------------------------------------------------- freeze check (before any label is opened)
frozen = {}
for line in open(os.path.join(HERE, "reads_frozen.sha256")):
    h, name = line.split()[:2]
    frozen[name] = h
reads, logl = {}, [f"{time.strftime('%Y-%m-%d %H:%M:%S')} unseal start"]
for nn in range(1, 14):
    name = f"reads_batch{nn:02d}.json"
    p = os.path.join(HERE, name)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    assert frozen[name] == h, name
    logl.append(f"{name} sha256 {h} (matches frozen list)")
    reads.update(json.load(open(p))["reads"])
assert len(reads) == 311
logl.append("all 13 batches verified; now opening sealed.json and S1 adjudications.json")

T = gp.RUNE_TO_TRANS
S = json.load(open(os.path.join(HERE, "sealed.json"), encoding="utf-8"))["items"]
TPL = json.load(open(os.path.join(HERE, "template_calls.json"), encoding="utf-8"))
S1rows = json.load(open(os.path.join(LP, "analysis/round45/S1-transcription/adjudications.json"), encoding="utf-8"))["rows"]

FAM = {**{x: "OA" for x in ("O", "A", "AE")}, **{x: "MD" for x in ("M", "D")},
       **{x: "THWR" for x in ("TH", "W", "R")}, **{x: "NI" for x in ("N", "I")}, **{x: "BE" for x in ("B", "E")}}
CORE = {"OA", "MD", "THWR"}


def cp(k, n, alpha=0.05):
    """exact Clopper-Pearson two-sided interval via bisection on the binomial cdf (stdlib)."""
    def cdf(k_, n_, p):
        return sum(math.comb(n_, i) * p ** i * (1 - p) ** (n_ - i) for i in range(k_ + 1))

    def solve(f, lo=0.0, hi=1.0):
        for _ in range(80):
            m = (lo + hi) / 2
            if f(m):
                lo = m
            else:
                hi = m
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, n, p) < alpha / 2)
    hi = 1.0 if k == n else solve(lambda p: cdf(k, n, p) > alpha / 2)
    return round(lo, 4), round(hi, 4)


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return None
    po_ = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / n / n
    return None if pe == 1 else round((po_ - pe) / (1 - pe), 4)


res = {"protocol": {"batches": 13, "items": len(reads), "unseal_log": "unseal.log"}}

# ---------------------------------------------------------------- C: reader control
C = [(cid, T[S[cid]["canon"]], reads[cid]["read"]) for cid in S if S[cid]["frame"] == "C"]
cf = [x for x in C if x[1] in FAM]
res["control_C"] = {"n": len(C), "correct": sum(a == b for _, a, b in C), "cp95": cp(sum(a == b for _, a, b in C), len(C)),
                    "family_n": len(cf), "family_correct": sum(a == b for _, a, b in cf),
                    "family_cp95": cp(sum(a == b for _, a, b in cf), len(cf)),
                    "misses": [x for x in C if x[1] != x[2]],
                    "family_labels": dict(Counter(a for _, a, _ in cf))}

# ---------------------------------------------------------------- W: substitution control
Wl = []
for cid in S:
    r = S[cid]
    if r["frame"] != "W":
        continue
    rd = reads[cid]["read"]
    Wl.append({"id": cid, "claimed": T[r["claimed"]], "shown_donor_canon": T[r["donor_canon"]], "s2_read": rd,
               "caught": rd != T[r["claimed"]], "named": rd == T[r["donor_canon"]],
               "template_on_shown": (TPL["items"].get(cid) or {}).get("call")})
res["swap_W"] = {"n": len(Wl), "caught": sum(w["caught"] for w in Wl), "named": sum(w["named"] for w in Wl), "items": Wl}

# ---------------------------------------------------------------- S1 blind reads by gpos
s1, s1_multi = {}, {}
for r in S1rows:
    if "gpos" not in r or not str(r.get("registration", "")).startswith("ok"):
        continue
    if r.get("read_how") not in ("glyph", "aligned-equal", "aligned-replace"):
        continue
    g = r["gpos"]  # S1 adjudication rows: gpos is the glyph's own position (slot = its place in the rendered pair)
    s1_multi.setdefault(g, []).append(r["blind_read"])
    s1.setdefault(g, (r["blind_read"], r["canon"]))  # first row in file order is the S1 read used
# sanity: S1's canon for a glyph must equal ours at the same position (checks the slot convention)
canon_at = {S[c]["gpos"]: T[S[c]["canon"]] for c in S if S[c]["frame"] in ("A", "R")}
bad = [g for g, (_, c) in s1.items() if g in canon_at and canon_at[g] != c]
assert not bad, bad[:5]
s1 = {g: br for g, (br, _) in s1.items()}
s1_controls = [r for r in S1rows if r.get("frame") in ("C", "C2") and "canon" in r]
s1cf = [r for r in s1_controls if r["canon"] in FAM]
res["S1_controls"] = {"n": len(s1_controls), "correct": sum(r["blind_read"] == r["canon"] for r in s1_controls),
                      "family_n": len(s1cf), "family_correct": sum(r["blind_read"] == r["canon"] for r in s1cf)}

# ---------------------------------------------------------------- A, R: S2 vs canon, S2 vs S1, adjudication
rows = []
for cid in S:
    r = S[cid]
    if r["frame"] not in ("A", "R"):
        continue
    canon = T[r["canon"]]
    rd = reads[cid]["read"]
    tp = (TPL["items"].get(cid) or {}).get("call")
    s1r = s1.get(r["gpos"])
    row = {"id": cid, "frame": r["frame"], "gpos": r["gpos"], "page": r["page"], "gline": r["gline"], "canon": canon,
           "s2": rd, "conf": reads[cid]["conf"], "s1_blind": s1r, "template": tp, "family": FAM.get(canon)}
    if rd == canon:
        row["verdict"] = "canon-confirmed (S2 blind)"
    elif (s1r is not None and s1r == rd) or (tp == rd):
        row["verdict"] = "canon-error-candidate"
    elif tp == canon and (s1r is None or s1r == canon):
        row["verdict"] = "canon-confirmed (S2 reader error)"
    else:
        row["verdict"] = "ambiguous"
    rows.append(row)
res["rows"] = rows

A = [x for x in rows if x["frame"] == "A"]
R = [x for x in rows if x["frame"] == "R"]
AR = A + R


def mm(lst):
    k = sum(x["s2"] != x["canon"] for x in lst)
    return {"n": len(lst), "s2_ne_canon": k, "s2_vs_canon_cp95": cp(k, len(lst)),
            "verdicts": dict(Counter(x["verdict"] for x in lst))}


res["S2_vs_canon"] = {"A": mm(A), "R": mm(R), "A_plus_R": mm(AR),
                      "by_family_A": {f: mm([x for x in A if x["family"] == f]) for f in sorted(set(FAM.values()))},
                      "R_family_glyphs": mm([x for x in R if x["family"]]),
                      "R_nonfamily_glyphs": mm([x for x in R if not x["family"]]),
                      "mismatches": [x for x in AR if x["s2"] != x["canon"]]}

# S2 vs S1 (frame A positions with a usable S1 blind read; also any R position S1 read — none by construction)
both = [x for x in A if x["s1_blind"] is not None]
agree = {"n_A": len(A), "n_with_S1_blind": len(both), "S1_missing_ids": [x["id"] for x in A if x["s1_blind"] is None],
         "agree": sum(x["s2"] == x["s1_blind"] for x in both),
         "kappa_all": kappa([(x["s2"], x["s1_blind"]) for x in both]), "by_family": {},
         "disagreements": [{k: x[k] for k in ("id", "gpos", "canon", "s2", "s1_blind", "template", "verdict")}
                           for x in both if x["s2"] != x["s1_blind"]],
         "S1_vs_canon_on_these": sum(x["s1_blind"] != x["canon"] for x in both)}
for f in sorted(set(FAM.values())):
    sub = [x for x in both if x["family"] == f]
    agree["by_family"][f] = {"n": len(sub), "agree": sum(x["s2"] == x["s1_blind"] for x in sub),
                             "kappa": kappa([(x["s2"], x["s1_blind"]) for x in sub]) if len(sub) >= 15 else None,
                             "s2_canon_agree": sum(x["s2"] == x["canon"] for x in sub),
                             "s1_canon_agree": sum(x["s1_blind"] == x["canon"] for x in sub)}
agree["S1_glyphs_read_twice_inconsistently"] = {g: v for g, v in s1_multi.items() if len(set(v)) > 1 and g in canon_at}
res["S2_vs_S1"] = agree

# ---------------------------------------------------------------- two-reader canon error bound (family glyphs)
# per-reader family miss rate m = CP95 upper of misses on family-labelled controls (S2: C-family + W; S1: its C-family)
s2_fam_ctrl_n = res["control_C"]["family_n"] + res["swap_W"]["n"]
s2_fam_ctrl_miss = (res["control_C"]["family_n"] - res["control_C"]["family_correct"]) + (res["swap_W"]["n"] - res["swap_W"]["caught"])
s1_n, s1_miss = res["S1_controls"]["family_n"], res["S1_controls"]["family_n"] - res["S1_controls"]["family_correct"]
m2 = cp(s2_fam_ctrl_miss, s2_fam_ctrl_n)[1]
m1 = cp(s1_miss, s1_n)[1] if s1_n else 1.0
fam_both = [x for x in both if x["family"]]
k_err = sum(x["verdict"] in ("canon-error-candidate", "ambiguous") for x in fam_both)
ub = cp(k_err, len(fam_both))[1]
fam_AR = [x for x in AR if x["family"]]
k2 = sum(x["verdict"] in ("canon-error-candidate", "ambiguous") for x in fam_AR)
ub2 = cp(k2, len(fam_AR))[1]
res["error_bound"] = {
    "S2_family_control": {"n": s2_fam_ctrl_n, "misses": s2_fam_ctrl_miss, "miss_rate_cp95_upper": m2},
    "S1_family_control": {"n": s1_n, "misses": s1_miss, "miss_rate_cp95_upper": m1},
    "two_reader": {"n_family_glyphs_read_by_both": len(fam_both), "errors_or_ambiguous": k_err,
                   "cp95_upper_detected": ub, "joint_miss": round(m1 * m2, 4),
                   "eps_upper": round(ub / (1 - m1 * m2), 4)},
    "S2_only": {"n_family_glyphs_A_plus_R": len(fam_AR), "errors_or_ambiguous": k2, "cp95_upper_detected": ub2,
                "eps_upper": round(ub2 / (1 - m2), 4)},
    "uniform_R": {"n": len(R), "errors_or_ambiguous": sum(x["verdict"] in ("canon-error-candidate", "ambiguous") for x in R),
                  "eps_upper": round(cp(sum(x["verdict"] in ("canon-error-candidate", "ambiguous") for x in R), len(R))[1] / (1 - m2), 4)},
    "assumption": "reader misses independent given the glyph (both read the same relikd render, so not fully independent)"}
res["template_validation"] = TPL["validation"]
res["gates"] = {"C_accuracy_ge_0.90": res["control_C"]["correct"] / res["control_C"]["n"] >= 0.90,
                "W_caught_ge_6_of_8": res["swap_W"]["caught"] >= 6}
logl.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} scored")
json.dump(res, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(HERE, "unseal.log"), "w").write("\n".join(logl) + "\n")
print(json.dumps({k: res[k] for k in ("control_C", "S1_controls", "gates", "error_bound")}, ensure_ascii=False, indent=1))
print(json.dumps({k: v for k, v in res["swap_W"].items() if k != "items"}), [(w["claimed"], w["shown_donor_canon"], w["s2_read"]) for w in Wl])
print(json.dumps({k: v for k, v in res["S2_vs_canon"].items() if k != "mismatches"}, indent=1))
print("MISMATCHES", json.dumps(res["S2_vs_canon"]["mismatches"], ensure_ascii=False))
print(json.dumps({k: v for k, v in agree.items()}, ensure_ascii=False, indent=1))
