"""R44/W2-A2 part 3 — the p55-rune-0 crib sweep (PREREG section 6).
Refuses to run unless both plants passed.  Writes crib_results.json."""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2lib as L                                     # noqa: E402

LP = L.LP
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
import adjudicate as A                                # noqa: E402

N = L.N
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
TOP_BEAM = 10


def gate():
    for f in ("plant_solver.json", "plant_crib.json"):
        if not json.load(open(os.path.join(HERE, f))).get("passed"):
            print("GATE NOT PASSED (%s) — refusing to run (PREREG Q5)." % f)
            sys.exit(1)


def main():
    gate()
    t0 = time.time()
    pages = L.canon_pages()
    ok, facts = L.verify_premise(pages)
    if not ok:
        print("PREMISE RE-VERIFICATION FAILED:", facts)
        sys.exit(2)
    gt = L.p55_ground_truth()
    keys = L.build_keys()
    cells, flags_only = L.crib_cells(keys)
    phases = L.page_phases(pages)
    c_list = [np.asarray(pg["idx"], dtype=np.int64) for pg in pages[:55]]
    lens = [len(c) for c in c_list]

    # propagation depth per cell (cap gt['T_max'])
    depths = [L.propagation_depth(keys[k], o, cfg, mode, gt)
              for (k, cfg, mode, o) in cells]
    dmax = int(max(depths)) if depths else 0
    depth_hist = {str(d): int(sum(1 for x in depths if x == d))
                  for d in sorted(set(depths))}

    # the sweep: per page, batch all surviving cells
    n_dec, best = 0, {"pmax": -99.0}
    crossers = []
    cell_best = np.full(len(cells), -99.0)
    for pi in range(55):
        ph = phases[pi]
        Lp = lens[pi]
        bar = L.BARS[L.lcap(Lp)]
        X = np.empty((len(cells), Lp), dtype=np.int64)
        for ci, (k, cfg, mode, o) in enumerate(cells):
            Kvec = keys[k][o + ph[mode]]
            X[ci] = L.R.decode_block(c_list[pi], Kvec[None, :], cfg)[0]
        r = A.adjudicate_batch(X, pan=PAN)
        pm = r["pmax"]
        n_dec += X.shape[0]
        cell_best = np.maximum(cell_best, pm)
        i = int(pm.argmax())
        if pm[i] > best["pmax"]:
            k, cfg, mode, o = cells[i]
            best = dict(pmax=float(pm[i]), page=pi, key=k, cfg=cfg, mode=mode,
                        offset=o, L=Lp, bar=bar, depth=depths[i])
        for j in np.nonzero(pm >= bar)[0]:
            full = A.adjudicate(X[int(j)], pan=PAN)
            if not full["degenerate"] and full["pmax"] >= bar:
                k, cfg, mode, o = cells[int(j)]
                crossers.append(dict(pmax=float(full["pmax"]), page=pi, key=k,
                                     cfg=cfg, mode=mode, offset=o, bar=bar,
                                     decode=X[int(j)].tolist()))

    # tier 2: top-10 cells by tier-1 best, beam keyskip1 on their best page
    order = np.argsort(-cell_best)[:TOP_BEAM]
    tier2 = []
    for ci in order:
        k, cfg, mode, o = cells[int(ci)]
        # find that cell's best page
        bestpi, bestpm = 0, -99.0
        for pi in range(55):
            ph = phases[pi]
            Kvec = keys[k][o + ph[mode]]
            x = L.R.decode_block(c_list[pi], Kvec[None, :], cfg)[0]
            pm = float(A.adjudicate_batch(x[None, :], pan=PAN)["pmax"][0])
            n_dec += 1
            if pm > bestpm:
                bestpi, bestpm = pi, pm
        ph0 = int(phases[bestpi][mode][0])
        dec = L.R.beam_rigid_decode(list(c_list[bestpi]), keys[k], cfg,
                                    offset=o + ph0, beam_w=200, max_rej=3)
        full = A.adjudicate(np.asarray(dec, dtype=np.int64), pan=PAN)
        n_dec += 1
        bar = L.BARS[L.lcap(lens[bestpi])]
        tier2.append(dict(key=k, cfg=cfg, mode=mode, offset=o, page=bestpi,
                          tier1_pmax=bestpm, beam_pmax=float(full["pmax"]),
                          degenerate=bool(full["degenerate"]), bar=bar,
                          crossed=bool(not full["degenerate"] and full["pmax"] >= bar)))

    out = dict(
        premise=facts, p55=dict(T_max=gt["T_max"], head=gt["head"],
                                n_interrupters=gt["n_interrupters"]),
        required_k=L.REQ_K,
        n_crib_checks=51 * 6 * (171 + 201), n_cells=len(cells),
        n_section_flags_o_le_29=len(flags_only),
        flags_o_le_29=[dict(key=k, cfg=c, o=o) for (k, c, m, o) in flags_only][:200],
        depth_hist=depth_hist, depth_max=dmax, depth_flag_threshold=5,
        depth_flags=[dict(key=k, cfg=cfg, mode=m, o=o, T=d)
                     for (k, cfg, m, o), d in zip(cells, depths) if d >= 5],
        n_tier1_decodes=n_dec - len(tier2), bars=L.BARS, n_bar=L.N_BAR,
        best=best, n_crossers=len(crossers), crossers=crossers,
        tier2=tier2, wall_s=round(time.time() - t0, 1))
    json.dump(out, open(os.path.join(HERE, "crib_results.json"), "w"), indent=1)
    brief = dict(out)
    brief.pop("flags_o_le_29")
    brief["tier2"] = tier2[:3]
    print(json.dumps(brief, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
