"""Round 48 / M1 Arm A — census of mechanisms for LP2's lag-1 leak (86 doublets where 447 are expected).
Rule and mechanism list are fixed in PREREG.md section 2. Run: python census.py  (about 2 min, numpy)."""
import json, os, numpy as np
from common import stream, LAT, HERE
N = 12956; REPS = 400; rng = np.random.default_rng(4802)
DIG = np.array([len(x) == 2 for x in LAT])

def stats(c):
    c = np.asarray(c); eq = c[1:] == c[:-1]; pos = np.flatnonzero(eq) + 1
    gaps = np.diff(pos)
    r1 = float(np.corrcoef(gaps[:-1], gaps[1:])[0, 1]) if len(gaps) > 3 and gaps[:-1].std() > 0 and gaps[1:].std() > 0 else 0.0
    return {"D": int(eq.sum()), "lag2_8": int(sum((c[k:] == c[:-k]).sum() for k in range(2, 9))),
            "lag2": int((c[2:] == c[:-2]).sum()), "dig": int(DIG[c[pos]].sum()),
            "triples": int((eq[1:] & eq[:-1]).sum()), "r1": r1, "gaps": gaps}

def norep(m, n):                      # hard no-repeat chain over m symbols
    u = rng.integers(1, m, n); u[0] = rng.integers(0, m); return np.cumsum(u) % m
def iid_inc(p0, n=N):                 # increments: 0 w.p. p0, else uniform nonzero
    u = rng.integers(1, 29, n); u[rng.random(n) < p0] = 0; u[0] = rng.integers(0, 29); return np.cumsum(u) % 29
def Z4(m):
    def f():
        x = norep(m, int(N * m / 29 * 1.08) + 200); x = x[x < 29]; assert len(x) >= N; return x[:N]
    return f
def Z6(): return norep(256, N) % 29
def Z7():
    x = norep(256, int(N * 256 / 232 * 1.08) + 200); x = x[x < 232]; return x[:N] % 29
FIRST = np.array([ord(x[0]) for x in LAT]); LAST = np.array([ord(x[-1]) for x in LAT])
OK = FIRST[None, :] != LAST[:, None]          # OK[prev, cur]
def Z9():
    c = np.empty(N, dtype=np.int64); c[0] = rng.integers(29); draws = rng.integers(0, 29, N * 2); j = 0
    for i in range(1, N):
        while not OK[c[i-1], draws[j]]: j += 1
        c[i] = draws[j]; j += 1
    return c
P0 = 86 / 12955
def pk(delta):                        # doublet rate after deleting a fraction delta from a no-repeat chain
    p, tot, w = 0.0, 0.0, 1 - delta
    for k in range(1, 60):
        tot += w * p; w *= delta; p = (1 - p) / 28
    return tot
lo, hi = 0.0, 0.9
for _ in range(60):
    mid = (lo + hi) / 2; lo, hi = (mid, hi) if pk(mid) < P0 else (lo, mid)
DELTA = (lo + hi) / 2; Q = P0 * 28
def F2():
    x = norep(29, int(N / (1 - DELTA) * 1.06) + 200); x = x[rng.random(len(x)) >= DELTA]; return x[:N]
def F3():
    x = norep(29, N); ch = rng.random(N) < Q; inc = np.where(ch, rng.integers(1, 29, N), 0); return (x + np.cumsum(inc)) % 29

MECH = {"Z0 no filter": (iid_inc.__call__ if False else (lambda: rng.integers(0, 29, N)), 0),
        "Z1 redraw once": (lambda: iid_inc(1 / 841), 0),
        "Z2 redraw until different (= Z5, last-emitted memory)": (lambda: norep(29, N), 0)}
for m in list(range(30, 41)) + [64]: MECH[f"Z4(m={m}) remembered-drop picker"] = (Z4(m), 0)
MECH["Z6 byte no-repeat, mod 29"] = (Z6, 0); MECH["Z7 byte no-repeat, drop>=232, mod 29"] = (Z7, 0)
MECH["Z9 Latin-letter no-repeat"] = (Z9, 0)
MECH["F1 coin (pinned model, fitted)"] = (lambda: iid_inc(P0), 1)
MECH[f"F2 delete fraction {DELTA:.3f} of a hard-filtered stream (fitted)"] = (F2, 1)
MECH[f"F3 second-layer shift changing w.p. {Q:.3f} (fitted)"] = (F3, 1)

real = stats(stream()); out = {"lp2": {k: v for k, v in real.items() if k != "gaps"}, "fitted": {"delta": DELTA, "q": Q, "p0": P0}, "mechanisms": {}}
sims = {}
for name, (fn, npar) in MECH.items():
    S = [stats(fn()) for _ in range(REPS)]; sims[name] = S; row = {"free_params": npar}; adm = True
    for k in ("D", "lag2_8", "dig"):
        v = np.array([s[k] for s in S]); a, b = np.quantile(v, [0.005, 0.995]); inside = bool(a <= real[k] <= b)
        row[k] = {"mean": float(v.mean()), "q0.5%": float(a), "q99.5%": float(b), "lp2_inside": inside}; adm &= inside
    row["admitted"] = adm; row["frac_r1_ge_0.380"] = float(np.mean([s["r1"] >= 0.380 for s in S]))
    out["mechanisms"][name] = row
    print(f"{'ADMIT ' if adm else 'reject'} {name:62s} D {row['D']['mean']:6.1f} [{row['D']['q0.5%']:.0f},{row['D']['q99.5%']:.0f}]  dig {row['dig']['mean']:5.1f}  r1>=.38 {row['frac_r1_ge_0.380']:.3f}")

# separability of each admitted zero-parameter mechanism from the coin
null = sims["F1 coin (pinned model, fitted)"]; pool = np.sort(np.concatenate([s["gaps"] for s in null]))
def ks(g): 
    g = np.sort(g); return float(np.max(np.abs(np.searchsorted(pool, g, side="right") / len(pool) - (np.arange(len(g)) + 0.5) / len(g)))) if len(g) else 1.0
crit = {"ks": np.quantile([ks(s["gaps"]) for s in null], 0.95),
        "triples": np.quantile([s["triples"] for s in null], [0.025, 0.975]),
        "lag2": np.quantile([s["lag2"] for s in null], [0.025, 0.975])}
out["separability_vs_coin"] = {}
for name, row in out["mechanisms"].items():
    if not row["admitted"] or name.startswith("F1"): continue
    S = sims[name]
    pw = {"ks": float(np.mean([ks(s["gaps"]) > crit["ks"] for s in S])),
          "triples": float(np.mean([not (crit["triples"][0] <= s["triples"] <= crit["triples"][1]) for s in S])),
          "lag2": float(np.mean([not (crit["lag2"][0] <= s["lag2"] <= crit["lag2"][1]) for s in S]))}
    out["separability_vs_coin"][name] = {"power": pw, "best": max(pw.values()), "separable": max(pw.values()) >= 0.20}
    print("separability", name, pw)
out["lp2"]["ks_vs_coin"] = ks(real["gaps"]); out["lp2"]["ks_crit95"] = float(crit["ks"])
json.dump(out, open(os.path.join(HERE, "census.json"), "w"), indent=1)
print("LP2", out["lp2"])
