"""R42 / C2 - the R36 dated pads (R17 P1 blockchain + P2 beacons/random.org byte streams) as
additive mod-29 pads over the 55 unsolved pages, adjudicated under panel-R36 vs the standing
free-null bar of record. Honest-instrument re-run of the legacy H7xF9 pad cell.

Each pad .bin is read to a bounded prefix (PREFIX bytes), bytes -> mod 29; a window of page length
is slid from ~OFFSETS stride-sampled start positions, both signs (c+pad, c-pad) and atbash.
Statistic per page = max panel-R36 pmax over the whole (pad x offset x sign x atb) grid.
"""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from run_stats import load_pages                   # noqa
import adjudicate as A                             # noqa
import bars_v3 as B                                # noqa

N = 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
R17 = os.path.join(LP, "analysis", "round17")
SIGNS, ATB = (1, -1), (0, 1)
OFFSETS = 150
PREFIX = 4_000_000     # bytes read per pad (logged cap)
FREE_LS = (120, 240, 400, 729)

PADS = [
    "P1_blockchain/data/hash_display.bin", "P1_blockchain/data/hash_internal.bin",
    "P1_blockchain/data/merkle_display.bin", "P1_blockchain/data/merkle_internal.bin",
    "P1_blockchain/data/nonce_le.bin", "P1_blockchain/data/time_le.bin",
    "P1_blockchain/data/hash_display_2013.bin", "P1_blockchain/data/hash_internal_2013.bin",
    "P2_beacons/data/pad_outputValue_2013-09-05_2013-11-14.bin",
    "P2_beacons/data/pad_seedValue_2013-09-05_2013-11-14.bin",
    "P2_beacons/data/pad_randomorg_2013-09_2013-11.bin",
    "P2_beacons/data/pad_randomorg_2013-12_2014-01.bin",
]


def free_bar(Ngrid, L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(Ngrid, max(cand), "free")


def load_pads():
    out = []
    for rel in PADS:
        p = os.path.join(R17, rel)
        if not os.path.exists(p):
            continue
        b = open(p, "rb").read(PREFIX)
        out.append((os.path.basename(rel), [x % N for x in b]))
    return out


def offsets_for(keylen, pagelen):
    span = max(1, keylen - pagelen)
    if span <= OFFSETS:
        return list(range(span))
    stride = span // OFFSETS
    return list(range(0, span, stride))[:OFFSETS]


def dec(c, pad, start, sign, atb):
    Lk = len(pad)
    if atb:
        return [(((N - 1) - c[i]) + sign * pad[(start + i) % Lk]) % N for i in range(len(c))]
    return [(c[i] + sign * pad[(start + i) % Lk]) % N for i in range(len(c))]


def main():
    t0 = time.time()
    pages = load_pages()[:-2]
    pads = load_pads()
    grid = len(pads) * OFFSETS * len(SIGNS) * len(ATB)
    print(json.dumps({"pads": len(pads), "pad_names": [n for n, _ in pads],
                      "prefix_bytes": PREFIX, "offsets_per_pad": OFFSETS, "grid": grid}))

    gbest = {"pmax": -99.0}
    per_page, crossers = [], []
    for pi, c in enumerate(pages):
        best = {"pmax": -99.0}
        for name, pad in pads:
            for st in offsets_for(len(pad), len(c)):
                for sign in SIGNS:
                    for atb in ATB:
                        r = A.adjudicate(dec(c, pad, st, sign, atb), pan=PAN)
                        if r["pmax"] > best["pmax"] and not r["degenerate"]:
                            best = {"pmax": r["pmax"], "preg": r["preg"], "pad": name,
                                    "start": st, "cfg": f"sign{sign:+d} atb{atb}",
                                    "degenerate": r["degenerate"]}
        bar = free_bar(grid, len(c))
        best.update(page=pi, L=len(c), bar=round(bar, 4), clears=bool(best["pmax"] >= bar))
        per_page.append(best)
        if best["clears"]:
            crossers.append(best)
        if best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 10 == 0:
            print(f"  page {pi}/{len(pages)} gbest {gbest['pmax']:.3f} "
                  f"({gbest.get('pad')}) {time.time()-t0:.0f}s", flush=True)

    out = {"pads": len(pads), "prefix_bytes": PREFIX, "offsets_per_pad": OFFSETS, "grid": grid,
           "observed_global_best": gbest, "n_crossers": len(crossers), "crossers": crossers[:10],
           "verdict": "NEGATIVE" if not crossers else "CROSS - inspect",
           "per_page_best": [round(b["pmax"], 3) for b in per_page],
           "elapsed_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(HERE, "c2_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("pads", "observed_global_best", "n_crossers",
          "verdict", "grid", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
