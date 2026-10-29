"""Fit log(beta) = a + b log(L) over the measured cells (+ pooled with round19 calib19 bw400 uniform cells)."""
import json, os, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
cells = json.load(open(os.path.join(HERE, "cells32.json")))
c19 = json.load(open(os.path.join(HERE, "..", "..", "round19", "I3", "calib19.json")))["cells"]

def ols(L, b):
    x, y = np.log(L), np.log(b); n = len(x)
    A = np.vstack([np.ones(n), x]).T
    coef, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ coef; s2 = r @ r / (n - 2)
    cov = s2 * np.linalg.inv(A.T @ A)
    return coef, np.sqrt(np.diag(cov)), n

pts = sorted((v["L"], v["mu"], v["beta"]) for v in cells.values())
L = np.array([p[0] for p in pts], float); mu = np.array([p[1] for p in pts]); be = np.array([p[2] for p in pts])
coef, se, n = ols(L, be)
pooled = pts + [(v["L"], v["mu"], v["beta"]) for k, v in c19.items()
                if k.startswith("EN_QUAD|keyskip1|L") and "bw" not in k]
pl = np.array([p[0] for p in pooled], float); pb = np.array([p[2] for p in pooled])
coefp, sep, npool = ols(pl, pb)
# two-point zero-DOF solve (R19-style) from the extreme L cells for comparison
b2 = math.log(be[-1] / be[0]) / math.log(L[-1] / L[0])
out = {"seed": 3301, "source": "shuffle of real LP2, vecbeam exact keyskip1 beam_w400 max_skip3, M per cell in cells32.json",
       "points": [{"L": int(p[0]), "mu": p[1], "beta": p[2]} for p in pts],
       "fit_new_only": {"n_points": n, "exponent": coef[1], "exponent_se": se[1], "ln_a": coef[0], "ln_a_se": se[0],
                        "df": n - 2, "beta_at_120": math.exp(coef[0] + coef[1] * math.log(120))},
       "fit_pooled_with_r19_uniform": {"n_points": npool, "exponent": coefp[1], "exponent_se": sep[1],
                        "ln_a": coefp[0], "beta_at_120": math.exp(coefp[0] + coefp[1] * math.log(120))},
       "two_point_exponent_extremes": b2, "r19_exponent": -0.583,
       "mu_nodes": [[int(p[0]), p[1]] for p in pts]}
json.dump(out, open(os.path.join(HERE, "null_curve32.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("fit_new_only", "fit_pooled_with_r19_uniform", "two_point_exponent_extremes")}, indent=1))
