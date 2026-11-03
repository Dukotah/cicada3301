"""R43/F6 part (c): the page-56 512-bit hash as an additive mod-29 keystream over the
55 unsolved LP2 pages. Grid and bar per PREREG.md; glue copied from round42/C3."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))

from run_stats import load_pages      # noqa
import adjudicate as A                # noqa
import bars_v3 as B                   # noqa

N = 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
HASH56 = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
SIGNS, ATB, OFFS = (1, -1), (0, 1), range(64)
FREE_LS = (120, 240, 400, 729)


def vig(c, key, sign, atb, off):
    Lk = len(key)
    if atb:
        return [(((N - 1) - c[i]) + sign * key[(i + off) % Lk]) % N for i in range(len(c))]
    return [(c[i] + sign * key[(i + off) % Lk]) % N for i in range(len(c))]


def free_bar(Ngrid, L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return float(B.bar_v3(Ngrid, max(cand), "free"))


def main():
    t0 = time.time()
    hb = bytes.fromhex(HASH56)
    keys = [("byte", [x % N for x in hb]),
            ("nibble", [int(c, 16) % N for c in HASH56])]
    pages = load_pages()[:-2]
    grid = len(keys) * len(SIGNS) * len(ATB) * len(OFFS)
    per_page, crossers, gbest = [], [], {"pmax": -99.0}
    for pi, c in enumerate(pages):
        best = {"pmax": -99.0}
        for ktag, ki in keys:
            for sign in SIGNS:
                for atb in ATB:
                    for off in OFFS:
                        r = A.adjudicate(vig(c, ki, sign, atb, off), pan=PAN)
                        if r["pmax"] > best["pmax"]:
                            best = {"pmax": float(r["pmax"]), "preg": int(r["preg"]),
                                    "key": ktag, "cfg": f"sign{sign:+d} atb{atb} off{off}",
                                    "degenerate": bool(r["degenerate"])}
        bar = free_bar(grid, len(c))
        best.update(page=pi, L=len(c), bar=round(bar, 4),
                    clears=bool((not best["degenerate"]) and best["pmax"] >= bar))
        per_page.append(best)
        if best["clears"]:
            crossers.append(best)
        if not best["degenerate"] and best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 10 == 0:
            print(f"  page {pi}/{len(pages)} gbest {gbest['pmax']:.3f} "
                  f"{time.time()-t0:.0f}s", flush=True)

    out = {"grid_per_page": grid, "n_pages": len(pages),
           "n_decodes_total": grid * len(pages),
           "observed_global_best": gbest, "n_crossers": len(crossers),
           "crossers": crossers[:10],
           "verdict": "NEGATIVE" if not crossers else "CROSS - inspect",
           "per_page_best_pmax": [round(b["pmax"], 3) for b in per_page],
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "f6_keystream_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("grid_per_page", "n_decodes_total",
          "observed_global_best", "n_crossers", "verdict", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
