"""R44/W2-A2 PLANT-C1 — the crib filter -> decode -> adjudicate path must recover a
synthetic continuous-stream two-page join at exactly the planted offset (PREREG section 9).
Writes plant_crib.json."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2lib as L                                     # noqa: E402

LP = L.LP
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
import adjudicate as A                                # noqa: E402
from lp import gematria as gp                         # noqa: E402

N = L.N
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
O_STAR, CFG, KNAME = 137, "vigm", "G-bash-1033"
BAR = L.BARS[120]


def heldout_english(n):
    txt = open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
               encoding="utf-8", errors="ignore").read()
    half = txt[len(txt) // 2:]
    import re
    letters = re.sub(r"[^A-Za-z]", "", half).upper()
    idx = gp.keyword_to_indices(letters[:3 * n])
    return idx[:n]


def main():
    keys = L.build_keys()
    K = np.asarray(keys[KNAME], dtype=np.int64)
    gt = L.p55_ground_truth()

    # synthetic join: pageX (120 held-out EN) + pageY (real p55 plaintext prefix, starts A)
    pX = heldout_english(120)
    pY = [p for p in gt["plain"] if p is not None][:60]
    assert pY[0] == L.CRIB_P
    P_all = pX + pY
    C_all = L.R.encipher_reset(P_all, K, CFG, [len(P_all)], offset=O_STAR)
    cX, cY = C_all[:120], C_all[120:]

    # the filter, same rule as crib_cells: required key at the join index, scan offsets
    req = L.derive_key(cY[0], pY[0], CFG)
    survivors = [o for o in range(0, 201) if K[o + 120] == req]

    # decode pageX at every surviving offset through the same decode glue + panel
    ph = {"section": np.arange(120, dtype=np.int64)}
    X = np.stack([L.decode_cell_pages([cX], [ph], K, o, CFG, "section")[0]
                  for o in survivors])
    r = A.adjudicate_batch(X, pan=PAN)
    pm = r["pmax"]
    best_i = int(pm.argmax())
    best_o = survivors[best_i]
    rec = float((X[best_i] == np.array(pX)).mean())
    others_below = all(float(pm[i]) < BAR for i in range(len(survivors)) if i != best_i)

    # propagation depth at o*: required key from the synthetic pageY vs K
    reqvec = [L.derive_key(cY[j], pY[j], CFG) for j in range(30)]
    t = 0
    while t < 30 and K[O_STAR + 120 + t] == reqvec[t]:
        t += 1

    rep = dict(o_star=O_STAR, cfg=CFG, key=KNAME, required_k=int(req),
               n_surviving_offsets=len(survivors), o_star_flagged=O_STAR in survivors,
               best_offset=best_o, best_pmax=float(pm[best_i]), bar=BAR,
               recovery_at_best=rec, others_below_bar=bool(others_below),
               propagation_T=t, T_cap=30,
               n_adjudicated=int(X.shape[0]))
    rep["passed"] = (rep["o_star_flagged"] and best_o == O_STAR and rec == 1.0
                     and rep["best_pmax"] >= BAR and others_below and t == 30)
    json.dump(rep, open(os.path.join(HERE, "plant_crib.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
