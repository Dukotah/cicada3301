"""R47/T2 — unseal, align, template, adjudicate, bound (PREREG §2, §5, §6).
Refuses to run unless every batch in manifest.json is frozen and matches reads_frozen.sha256; logs those hashes
BEFORE opening sealed.json or any S1/S2 per-position file. Then:
  1. strip alignment (semi-global edit distance; within-family substitution 0.6) of every read to its canon;
  2. template calls (R46/S2 leave-line-out nearest class mean) on target boxes where the strip read is 1:1 with boxes;
  3. adjudication vs S1 frozen blind reads (round45 adjudications.json);
  4. W / C gates; updated two-reader bound using R46/S2 results.json.
Run from liber-primus/: PYTHONUTF8=1 python analysis/round47/T2-transcription-closeout/unseal.py   (~2 min)
Outputs: results.json, unseal.log"""
import hashlib
import json
import math
import os
import sys
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
os.chdir(LP)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "stones"))

# ------------------------------------------------------------ freeze check (before any label is opened)
man = json.load(open(os.path.join(HERE, "manifest.json")))
nb = max(m["batch"] for m in man)
frozen = {}
for line in open(os.path.join(HERE, "reads_frozen.sha256")):
    h, name = line.split()[:2]
    frozen[name] = h
logl = [f"{time.strftime('%Y-%m-%d %H:%M:%S')} unseal start"]
reads = {}
for nn in range(1, nb + 1):
    name = f"reads_batch{nn:02d}.json"
    h = hashlib.sha256(open(os.path.join(HERE, name), "rb").read()).hexdigest()
    assert frozen[name] == h, name
    logl.append(f"{name} sha256 {h} (matches frozen list)")
    reads.update(json.load(open(os.path.join(HERE, name)))["reads"])
assert sorted(reads) == sorted(m["id"] for m in man)
logl.append(f"all {nb} batches verified ({len(reads)} strips); now opening sealed.json, S1 adjudications.json, S2 results.json")

import pipeline as P  # noqa: E402
from build_dataset import norm_crop  # noqa: E402
from lp import gematria as gp  # noqa: E402

S = json.load(open(os.path.join(HERE, "sealed.json"), encoding="utf-8"))["items"]
S1rows = json.load(open("analysis/round45/S1-transcription/adjudications.json", encoding="utf-8"))["rows"]
S2res = json.load(open("analysis/round46/S2-second-reader/results.json", encoding="utf-8"))

FAM = {**{x: "OA" for x in ("O", "A", "AE")}, **{x: "MD" for x in ("M", "D")},
       **{x: "THWR" for x in ("TH", "W", "R")}, **{x: "NI" for x in ("N", "I")}, **{x: "BE" for x in ("B", "E")}}
# alignment-cost family (look-alikes; TH/W are the visual pair, R joins THWR only for S1/S2 bookkeeping)
VF = {**{x: "OA" for x in ("O", "A", "AE")}, **{x: "MD" for x in ("M", "D", "E")}, **{x: "THW" for x in ("TH", "W")}}


def cp(k, n, alpha=0.05):
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
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, n, p) < alpha / 2)
    hi = 1.0 if k == n else solve(lambda p: cdf(k, n, p) > alpha / 2)
    return round(lo, 4), round(hi, 4)


def sub(r, c):
    alts = r.split("|")
    if len(alts) == 1 and r == c:
        return 0.0
    if c in alts or any(VF.get(a) and VF.get(a) == VF.get(c) for a in alts):
        return 0.6
    return 1.0


def align(tok, canon, free_ends):
    """Edit-distance alignment of tokens to canon. free_ends: canon prefix/suffix unpaid (semi-global).
    Returns cost, {canon_index: token_index or None}, margin (best cost at an end >= 2 away minus best)."""
    k, L = len(tok), len(canon)
    D = np.full((k + 1, L + 1), np.inf)
    B = np.zeros((k + 1, L + 1), dtype=int)
    D[0, :] = 0 if free_ends else np.arange(L + 1)
    D[:, 0] = np.arange(k + 1)
    for i in range(1, k + 1):
        for j in range(1, L + 1):
            opts = [D[i - 1, j - 1] + sub(tok[i - 1], canon[j - 1]), D[i - 1, j] + 1, D[i, j - 1] + 1]
            b = int(np.argmin(opts))
            D[i, j], B[i, j] = opts[b], b
    if free_ends:
        jend = int(np.argmin(D[k]))
        far = [D[k, j] for j in range(L + 1) if abs(j - jend) >= 2]
        margin = float(min(far) - D[k, jend]) if far else None
    else:
        jend, margin = L, None
    cost = float(D[k, jend])
    mp = {}
    i, j = k, jend
    while i > 0 and j > 0:
        b = B[i, j]
        if b == 0:
            mp[j - 1] = i - 1
            i, j = i - 1, j - 1
        elif b == 1:
            i -= 1
        else:
            mp[j - 1] = None
            j -= 1
    return cost, mp, margin


# ------------------------------------------------------------ template instrument (R46/S2 template_call.py)
T = gp.RUNE_TO_TRANS
gl, po = P.global_lines()
start = np.cumsum([0] + [len(L) for L in gl])[:-1]
flat = [c for L in gl for c in L]
line_of = np.repeat(np.arange(len(gl)), [len(L) for L in gl])
cm = json.load(open("analysis/round45/S1-transcription/corrected_map.json"))
vec, segs = {}, {}
for n in range(56):
    lines, b, gray = P.segment_image(f"data/relikd/p{n}.jpg")
    g = np.asarray(gray)
    clean = [L for L in lines if len(L) >= 10]
    segs[n] = (g, clean)
    for r in cm[str(n)]:
        G = r["true_gline"]
        if G is None or r["count"] != r["true_len"]:
            continue
        for j, bx in enumerate(clean[r["clean_i"]]):
            v = norm_crop(g, bx)
            if v is not None:
                vec[int(start[G] + j)] = v.ravel().astype(np.float64)
runes = sorted(set(flat), key=lambda r: gp.RUNE_TO_IDX[r])
tot = {r: np.zeros_like(next(iter(vec.values()))) for r in runes}
cnt = {r: 0 for r in runes}
per_line = {}
for p, v in vec.items():
    r = flat[p]
    tot[r] += v
    cnt[r] += 1
    s = per_line.setdefault(int(line_of[p]), {}).setdefault(r, [np.zeros_like(v), 0])
    s[0] += v
    s[1] += 1


def corr(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def tcall(v, line):
    ex = per_line.get(line, {})
    sc = {}
    for r in runes:
        s, c = tot[r].copy(), cnt[r]
        if r in ex:
            s -= ex[r][0]
            c -= ex[r][1]
        if c > 0:
            sc[r] = corr(v, s / c)
    best = sorted(sc, key=sc.get, reverse=True)
    return T[best[0]], {T[r]: round(sc[r], 3) for r in best[:3]}


logl.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} templates built ({len(vec)} exact-line glyph vectors)")

# ------------------------------------------------------------ S1 blind reads by gpos (all rows kept for the record)
s1_all = {}
for r in S1rows:
    if "gpos" in r:
        s1_all.setdefault(r["gpos"], []).append({k: r.get(k) for k in ("id", "frame", "blind_read", "read_how", "registration",
                                                                       "confidence", "verdict", "unblinded_reread")})


def s1_blind(g):
    for r in s1_all.get(g, []):
        if str(r.get("registration", "")).startswith("ok") and r.get("read_how") in ("glyph", "aligned-equal", "aligned-replace"):
            return r["blind_read"]
    return None


res = {"protocol": {"batches": nb, "strips": len(reads), "tokens": sum(map(len, reads.values())),
                    "registration": "analysis/stones/alignment.json (repaired v2, R46-A1); corrected_map agrees on 14/15 target lines, null on 291"}}

# ------------------------------------------------------------ controls
Wl, Cl, plainW = [], [], []
for cid, rec in S.items():
    tok = [t["read"] for t in reads[cid]]
    if rec["frame"] == "W":
        cost, mp, _ = align(tok, rec["canon_seq"], False)
        ti = mp.get(rec["swap_index"])
        rd = tok[ti] if ti is not None else None
        Wl.append({"id": cid, "claimed": rec["claimed"], "shown_donor": rec["donor_canon"], "t2_read": rd,
                   "caught": rd != rec["claimed"], "named": rd == rec["donor_canon"], "align_cost": cost,
                   "n_tokens": len(tok)})
        for j, c in enumerate(rec["canon_seq"]):
            if j == rec["swap_index"]:
                continue
            ti = mp.get(j)
            plainW.append((c, tok[ti] if ti is not None else None))
    elif rec["frame"] == "C":
        cost, mp, _ = align(tok, rec["canon_seq"], False)
        for j, c in enumerate(rec["canon_seq"]):
            ti = mp.get(j)
            Cl.append({"id": cid, "label": c, "t2": tok[ti] if ti is not None else None})
res["swap_W"] = {"n": len(Wl), "caught": sum(w["caught"] for w in Wl), "named": sum(w["named"] for w in Wl), "items": Wl}
cf = [c for c in Cl if c["label"] in FAM]
res["control_C"] = {"n": len(Cl), "correct": sum(c["t2"] == c["label"] for c in Cl),
                    "cp95": cp(sum(c["t2"] == c["label"] for c in Cl), len(Cl)),
                    "family_n": len(cf), "family_correct": sum(c["t2"] == c["label"] for c in cf),
                    "misses": [c for c in Cl if c["t2"] != c["label"]]}
pf = [x for x in plainW if x[0] in FAM]
res["plain_W_glyphs"] = {"n": len(plainW), "correct": sum(a == b for a, b in plainW),
                         "family_n": len(pf), "family_correct": sum(a == b for a, b in pf),
                         "misses": [x for x in plainW if x[0] != x[1]]}
res["gates"] = {"W_caught_ge_6_of_8": res["swap_W"]["caught"] >= 6,
                "C_accuracy": round(res["control_C"]["correct"] / res["control_C"]["n"], 4),
                "C_ge_0.90": res["control_C"]["correct"] / res["control_C"]["n"] >= 0.90}

# ------------------------------------------------------------ targets
rows, strips, byprod = [], [], []
for cid, rec in S.items():
    if rec["frame"] != "T":
        continue
    tok = [t["read"] for t in reads[cid]]
    conf = [t["conf"] for t in reads[cid]]
    cost, mp, margin = align(tok, rec["canon_line"], True)
    nbox = rec["box_hi"] - rec["box_lo"] + 1
    one2one = len(tok) == nbox
    g, clean = segs[rec["image"]]
    span = sorted(j for j, t in mp.items() if t is not None)
    strips.append({"id": cid, "gline": rec["gline"], "image": rec["image"], "n_boxes": nbox, "n_tokens": len(tok),
                   "align_cost": cost, "margin": margin, "canon_span": [span[0], span[-1]] if span else None,
                   "tokens": tok})
    tset = {t["j"] for t in rec["targets"]}
    for j, ti in mp.items():
        if ti is not None and j not in tset:
            byprod.append((rec["canon_line"][j], tok[ti]))
    for t in rec["targets"]:
        ti = mp.get(t["j"])
        registered = ti is not None and margin is not None and margin > 0
        rd = tok[ti] if ti is not None else None
        tp = None
        if registered and one2one:
            bx = clean[rec["clean_i"]][rec["box_lo"] + ti]
            v = norm_crop(g, bx)
            if v is not None:
                c_, top = tcall(v.ravel().astype(np.float64), rec["gline"])
                tp = {"call": c_, "top3": top}
        s1r = s1_blind(t["gpos"])
        canon = t["canon"]
        tpc = tp["call"] if tp else None
        if not registered:
            verdict = "ambiguous (unregistered)"
        elif rd == canon:
            verdict = "canon-confirmed (T2 blind)"
        elif (s1r is not None and s1r == rd) or tpc == rd:
            verdict = "canon-error-candidate"
        elif tpc == canon and (s1r is None or s1r == canon):
            verdict = "canon-confirmed (T2 reader error)"
        else:
            verdict = "ambiguous"
        rows.append({"gpos": t["gpos"], "gline": rec["gline"], "j": t["j"], "strip": cid, "canon": canon, "t2": rd,
                     "t2_conf": conf[ti] if ti is not None else None, "registered": registered, "s1_blind": s1r,
                     "s1_rows": s1_all.get(t["gpos"], []), "template": tp, "family": FAM.get(canon),
                     "disputed": t["gpos"] in (276, 5054, 6054, 9877), "verdict": verdict})
rows.sort(key=lambda r: (not r["disputed"], r["gpos"]))
res["strips_T"] = strips
res["targets"] = rows
res["byproduct_nontarget"] = {"n": len(byprod), "agree": sum(a == b for a, b in byprod),
                              "disagreements": [x for x in byprod if x[0] != x[1]]}
res["T2_vs_canon"] = {"n": len(rows), "registered": sum(r["registered"] for r in rows),
                      "t2_eq_canon": sum(r["t2"] == r["canon"] for r in rows),
                      "verdicts": dict(Counter(r["verdict"] for r in rows)),
                      "by_family": {f: {"n": sum(r["family"] == f for r in rows),
                                        "t2_eq_canon": sum(r["family"] == f and r["t2"] == r["canon"] for r in rows)}
                                    for f in sorted(set(FAM.values()))}}
s1b = [r for r in rows if r["s1_blind"] is not None and r["registered"]]
res["T2_vs_S1"] = {"n_with_S1_blind": len(s1b), "agree": sum(r["t2"] == r["s1_blind"] for r in s1b),
                   "S1_ne_canon": [{k: r[k] for k in ("gpos", "canon", "t2", "s1_blind", "verdict")}
                                   for r in s1b if r["s1_blind"] != r["canon"]],
                   "no_S1_blind_read": [r["gpos"] for r in rows if r["s1_blind"] is None]}

# ------------------------------------------------------------ two-reader bound (PREREG §6)
fam_ctrl_n = res["swap_W"]["n"] + res["control_C"]["family_n"]
fam_ctrl_miss = (res["swap_W"]["n"] - res["swap_W"]["caught"]) + (res["control_C"]["family_n"] - res["control_C"]["family_correct"])
m_T2 = cp(fam_ctrl_miss, fam_ctrl_n)[1]
m_S2 = S2res["error_bound"]["S2_family_control"]["miss_rate_cp95_upper"]
m_S1 = S2res["error_bound"]["S1_family_control"]["miss_rate_cp95_upper"]
m2 = max(m_S2, m_T2)
BAD = ("canon-error-candidate", "ambiguous", "ambiguous (unregistered)")
s2A = [x for x in S2res["rows"] if x["frame"] == "A" and x["s1_blind"] is not None and x["family"]]
t2B = [r for r in rows if r["s1_blind"] is not None and r["family"]]
bound = {"m_S1": m_S1, "m_S2": m_S2, "m_T2": m_T2, "m_T2_controls": {"n": fam_ctrl_n, "misses": fam_ctrl_miss},
         "second_reader_m_used": m2, "joint_miss": round(m_S1 * m2, 4),
         "assumption": "misses independent given the glyph (all readers share the relikd render)", "by_family": {}}
for f in ("OA", "MD", "THWR", "NI", "BE", "ALL"):
    a = [x for x in s2A if f == "ALL" or x["family"] == f]
    b = [r for r in t2B if f == "ALL" or r["family"] == f]
    k = sum(x["verdict"] in BAD for x in a) + sum(r["verdict"] in BAD for r in b)
    n = len(a) + len(b)
    ub = cp(k, n)[1]
    k0 = sum(x["verdict"] in BAD for x in a)
    old = round(cp(k0, len(a))[1] / (1 - m_S1 * m_S2), 4) if a else None
    bound["by_family"][f] = {"n_S2_exact": len(a), "n_T2_window": len(b), "n": n, "k": k, "cp95_upper": ub,
                             "eps_upper": round(ub / (1 - m_S1 * m2), 4), "R46_eps_upper_recomputed": old}
# all of S1's family glyphs with >= 1 further blind read, any S1 status (one-or-two reader, S2/T2 only)
allf = [x for x in S2res["rows"] if x["frame"] == "A" and x["family"]] + [r for r in rows if r["family"] and r["registered"]]
k_all = sum(x["verdict"] in BAD for x in allf)
bound["S1_family_census_second_reader_only"] = {"n": len(allf), "k": k_all,
                                                "eps_upper": round(cp(k_all, len(allf))[1] / (1 - m2), 4)}
res["error_bound"] = bound
logl.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} scored")
json.dump(res, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(os.path.join(HERE, "unseal.log"), "w").write("\n".join(logl) + "\n")
print(json.dumps({k: res[k] for k in ("gates", "T2_vs_canon", "T2_vs_S1", "error_bound")}, ensure_ascii=False, indent=1))
print("W", [(w["claimed"], w["shown_donor"], w["t2_read"]) for w in Wl])
print("C", {k: v for k, v in res["control_C"].items()}, "plainW", {k: v for k, v in res["plain_W_glyphs"].items()})
for r in rows:
    print(r["gpos"], r["canon"], r["t2"], r["t2_conf"], r["s1_blind"], (r["template"] or {}).get("call"), r["verdict"])
for s in strips:
    print(s["id"], s["gline"], s["n_boxes"], s["n_tokens"], s["align_cost"], s["margin"], s["canon_span"])
print("byproduct", res["byproduct_nontarget"])
