"""R42 / C3 - the artifact keys (CURATED_ALPHA + C->F variants + hex-letter NUMER +
auto_alpha_from_raw(), incl. the auto-extracted set from the PRESENT raw) as Vigenere /
running keys over the 55 unsolved LP2 pages, adjudicated under panel-R36 (12 registers, the R41
instrument) and judged against the STANDING free-null bar of record (bars_v3), not a fresh
per-shuffle null (that would be ~10^8 decodes).

This is the honest-instrument re-run of R30-B1, whose original pass scored English-only.
X1-B/R41 showed the raw is present (C1's 'absent' was a clone-scoped search), so the auto keys
re-derive here: MIDISCV and WORKING both reproduce.

Statistic per page: max panel-R36 pmax over the whole (key x sign x atb x phase) grid.
Bar: bars_v3.bar_v3(N=grid_per_page, L in {120,240,400} nearest-and-conservative, 'free') -- the
measured 12-register free-decode null at the family size. A page crosses iff its non-degenerate
grid-max >= its bar.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null",
          "analysis/round10b/B1-overlooked-artifact"):
    sys.path.insert(0, os.path.join(LP, p))

from lp import gematria as gp                      # noqa
from run_stats import load_pages                   # noqa
import adjudicate as A                             # noqa
import bars_v3 as B                                # noqa
from b1_keys import build                          # noqa

N = gp.N
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
SIGNS, ATB, MAXPHASE = (1, -1), (0, 1), 12
FREE_LS = (120, 240, 400, 729)


def vig_decode(c, key, sign, atb, phase):
    Lk = len(key)
    if atb:
        return [(((N - 1) - c[i]) + sign * key[(i + phase) % Lk]) % N for i in range(len(c))]
    return [(c[i] + sign * key[(i + phase) % Lk]) % N for i in range(len(c))]


def free_bar(Ngrid, L):
    """Conservative free-null bar: use the smallest tabulated L that is <= the page length
    (shorter L => higher bar), defaulting to 120 for the shortest pages."""
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(Ngrid, max(cand), "free")


def key_idxs():
    alpha, numer = build()
    keys = []
    for r in alpha:
        ki = gp.keyword_to_indices(r["key"])
        if ki:
            keys.append((r["tag"], r["key"], ki))
    for r in numer:
        ki = [int(d) % N for d in r["digits"]]
        if len(ki) >= 3:
            keys.append((r["tag"], "#" + r["digits"][:24], ki))
    return keys, len(alpha), len(numer)


def grid_max(c, keys):
    best = {"pmax": -99.0}
    for tag, kname, ki in keys:
        for sign in SIGNS:
            for atb in ATB:
                for ph in range(MAXPHASE):
                    r = A.adjudicate(vig_decode(c, ki, sign, atb, ph), pan=PAN)
                    if r["pmax"] > best["pmax"]:
                        best = {"pmax": r["pmax"], "preg": r["preg"], "tag": tag,
                                "key": kname, "cfg": f"sign{sign:+d} atb{atb} ph{ph}",
                                "degenerate": r["degenerate"]}
    return best


def main():
    t0 = time.time()
    pages = load_pages()[:-2]
    keys, na, nn = key_idxs()
    auto = sum(1 for t, _, _ in keys if t.startswith("auto-"))
    grid_per_page = len(keys) * len(SIGNS) * len(ATB) * MAXPHASE
    print(json.dumps({"n_alpha": na, "n_numer": nn, "n_keys": len(keys), "n_auto": auto,
                      "n_pages": len(pages), "grid_per_page": grid_per_page}))

    per_page, gbest = [], {"pmax": -99.0}
    crossers = []
    for pi, c in enumerate(pages):
        b = grid_max(c, keys)
        bar = free_bar(grid_per_page, len(c))
        b.update(page=pi, L=len(c), bar=round(bar, 4),
                 clears=bool((not b["degenerate"]) and b["pmax"] >= bar))
        per_page.append(b)
        if b["clears"]:
            crossers.append(b)
        if not b["degenerate"] and b["pmax"] > gbest["pmax"]:
            gbest = dict(b)
        if pi % 10 == 0:
            print(f"  page {pi}/{len(pages)} gbest {gbest['pmax']:.3f} "
                  f"({gbest.get('key')}) {time.time()-t0:.0f}s", flush=True)

    out = {"n_keys": len(keys), "n_auto": auto, "grid_per_page": grid_per_page,
           "n_decodes_total": grid_per_page * len(pages),
           "MIDISCV_reproduced": any(k == "MIDISCV" for _, k, _ in keys),
           "WORKING_reproduced": any(k == "WORKING" for _, k, _ in keys),
           "observed_global_best": gbest,
           "n_crossers": len(crossers), "crossers": crossers[:10],
           "verdict": "NEGATIVE" if not crossers else "CROSS - inspect",
           "per_page_best_pmax": [round(b["pmax"], 3) for b in per_page],
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "c3_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("n_keys", "n_auto", "MIDISCV_reproduced",
          "WORKING_reproduced", "observed_global_best", "n_crossers", "verdict",
          "n_decodes_total", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
