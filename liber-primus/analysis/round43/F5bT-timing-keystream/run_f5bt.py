"""R43 / F5b-T step 2 - the onion-2 interval/5 streams as key material over the 55 unsolved LP2
pages, through the STANDING instrument (adjudicate/adjudicate_batch + panel-R36 + bars_v3 'free'),
exactly as pre-registered in PREREG.md.  Three positive controls are planted as synthetic pages and
scored by the same loop; no verdict without all three recovering.

Matrix per page (fixed in PREREG): 7 streams x 2 directions x 3 mappings x 6 configs x
{repeating all rotations, one-shot suffix >= 60}  ->  N = 34,668 decodes/page.
Bars of record at N=34,668: L_cap 120 -> 13.513, L_cap 240 -> 18.103.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp                      # noqa
from run_stats import load_pages                   # noqa
import adjudicate as A                             # noqa
import bars_v3 as B                                # noqa

N = gp.N                                           # 29
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
FREE_LS = (120, 240, 400, 729)
MIN_ONESHOT = 60

KS = json.load(open(os.path.join(HERE, "key_streams.json")))
S_A, S_B = KS["S_A"]["k"], KS["S_B"]["k"]
STREAMS = {"S_A": S_A, "S_B": S_B}
for a, b in KS["bridge_variants"]:
    STREAMS["S_AB_%d%d" % (a, b)] = S_A + [a, b] + S_B
assert len(STREAMS) == 7 and all(len(v) == 114 for k, v in STREAMS.items() if k.startswith("S_AB"))

MAPPINGS = {"m1": lambda k: k % N,
            "m2": lambda k: (5 * k) % N,
            "m3": lambda k: gp.PRIMES[k % N] % N}
CFGS = ["vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb"]


def decode(c, K, cfg):
    """c, K: equal-length int arrays. Returns plaintext-index array."""
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":
        return (x - K) % N
    if base == "vigp":
        return (x + K) % N
    return (K - x) % N


def free_bar(Ngrid, L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(Ngrid, max(cand), "free")


def key_variants(stream):
    """(dirname, mapname, mapped-key-array) for the 6 dir x map combos."""
    out = []
    for dname, seq in (("fwd", stream), ("rev", stream[::-1])):
        for mname, fn in MAPPINGS.items():
            out.append((dname, mname, np.array([fn(k) for k in seq], dtype=np.int64)))
    return out


# ------------------------------------------------------------------ positive controls (PREREG)
def to_idx(text):
    out = []
    for w in text.split():
        try:
            out.extend(gp.keyword_to_indices(w))
        except Exception:
            pass
    return out


PT1 = ("A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE "
       "FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED "
       "WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED SOME WISDOM THE PRIMES ARE SACRED "
       "THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS")
PT2 = ("WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR "
       "THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL "
       "STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY "
       "YOU WILL DISCOVER AN END TO SELF")
PT3 = ("SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL "
       "THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY A KOAN DURING A LESSON THE MASTER "
       "EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO "
       "EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD")


def build_controls():
    """Encrypt known plaintexts so exactly one swept cell inverts each (PREREG P1-P3)."""
    plants = []
    # P1: S_AB_33 fwd m1, vigm, rot 17, L=240
    p = np.array(to_idx(PT1)[:240], dtype=np.int64)
    K = np.array([MAPPINGS["m1"](k) for k in STREAMS["S_AB_33"]], dtype=np.int64)
    Lk = len(K)
    kk = K[(17 + np.arange(len(p))) % Lk]
    plants.append(("P1", (p + kk) % N, dict(stream="S_AB_33", dir="fwd", map="m1", cfg="vigm",
                                            mode="R", rot=17), p))
    # P2: S_B rev m3, beau, rot 5, L=200
    p = np.array(to_idx(PT2)[:200], dtype=np.int64)
    K = np.array([MAPPINGS["m3"](k) for k in STREAMS["S_B"][::-1]], dtype=np.int64)
    Lk = len(K)
    kk = K[(5 + np.arange(len(p))) % Lk]
    plants.append(("P2", (kk - p) % N, dict(stream="S_B", dir="rev", map="m3", cfg="beau",
                                            mode="R", rot=5), p))
    # P3: S_A fwd m2, vigp_atb, rot 0, L=240
    p = np.array(to_idx(PT3)[:240], dtype=np.int64)
    K = np.array([MAPPINGS["m2"](k) for k in STREAMS["S_A"]], dtype=np.int64)
    Lk = len(K)
    kk = K[np.arange(len(p)) % Lk]
    plants.append(("P3", ((N - 1) - ((p - kk) % N)) % N, dict(stream="S_A", dir="fwd", map="m2",
                                                              cfg="vigp_atb", mode="R", rot=0), p))
    return plants


# ------------------------------------------------------------------ the sweep
def sweep_page(c):
    """Full pre-registered matrix over one page. Returns (count, best, crossers)."""
    c = np.asarray(c, dtype=np.int64)
    Lp = len(c)
    best = {"pmax": -99.0}
    crossers = []
    count = 0
    for sname, seq in STREAMS.items():
        for dname, mname, K in key_variants(seq):
            Lk = len(K)
            # ---- Mode R: all rotations, full page, batched (6 cfgs x Lk rotations)
            idx = (np.arange(Lk)[:, None] + np.arange(Lp)[None, :]) % Lk
            Kmat = K[idx]                                     # (Lk, Lp)
            rows, meta = [], []
            for cfg in CFGS:
                rows.append(decode(c[None, :], Kmat, cfg))
                meta.extend((cfg, "R", r) for r in range(Lk))
            X = np.concatenate(rows, axis=0)
            r = A.adjudicate_batch(X, pan=PAN)
            count += X.shape[0]
            barR = free_bar(NGRID, Lp)
            _collect(r, X, meta, sname, dname, mname, Lp, barR, best, crossers)
            # ---- Mode O: one-shot suffix, page-start aligned, length >= MIN_ONESHOT
            for rot in range(0, Lk - MIN_ONESHOT + 1):
                Lr = min(Lk - rot, Lp)
                kk = K[rot:rot + Lr]
                rows, meta = [], []
                for cfg in CFGS:
                    rows.append(decode(c[None, :Lr], kk[None, :], cfg))
                    meta.append((cfg, "O", rot))
                X = np.concatenate(rows, axis=0)
                r = A.adjudicate_batch(X, pan=PAN)
                count += X.shape[0]
                barO = free_bar(NGRID, Lr)
                _collect(r, X, meta, sname, dname, mname, Lr, barO, best, crossers)
    return count, best, crossers


def _collect(r, X, meta, sname, dname, mname, L, bar, best, crossers):
    pm = r["pmax"]
    i = int(pm.argmax())
    if pm[i] > best["pmax"]:
        cfg, mode, rot = meta[i]
        best.update(pmax=float(pm[i]), preg=int(r["preg"][i]), stream=sname, dir=dname, map=mname,
                    cfg=cfg, mode=mode, rot=rot, L=int(L), bar=round(float(bar), 4),
                    decode=X[i].tolist())
    for i in np.nonzero(pm >= bar)[0]:
        full = A.adjudicate(X[i], pan=PAN)
        if not full["degenerate"] and full["pmax"] >= bar:
            cfg, mode, rot = meta[int(i)]
            crossers.append(dict(pmax=float(full["pmax"]), preg=full["preg"], stream=sname,
                                 dir=dname, map=mname, cfg=cfg, mode=mode, rot=rot, L=int(L),
                                 bar=round(float(bar), 4), decode=X[int(i)].tolist()))


NGRID = 34668


def main():
    t0 = time.time()
    pages = load_pages()[:-2]
    assert len(pages) == 55
    plants = build_controls()

    # expected grid: assert the PREREG arithmetic before running
    per_cfg = sum(len(v) for v in STREAMS.values()) + sum(max(0, len(v) - MIN_ONESHOT + 1)
                                                          for v in STREAMS.values())
    assert per_cfg * 2 * 3 * 6 == NGRID, per_cfg

    out = {"ngrid_per_page": NGRID, "bars": {str(L): round(free_bar(NGRID, L), 4) for L in (120, 240)},
           "controls": [], "pages": [], "crossers": [], "verdict": None}

    # ---- controls FIRST (gate)
    ok = True
    for name, cipher, cell, p in plants:
        cnt, best, cross = sweep_page(cipher)
        assert cnt == NGRID, (name, cnt)
        hit = (best["pmax"] >= best["bar"]
               and all(best[k] == cell[k] for k in ("stream", "dir", "map", "cfg", "mode", "rot")))
        recovered = bool(hit and best["decode"] == list(map(int, p)))
        full = A.adjudicate(np.array(best["decode"], dtype=np.int64), pan=PAN)
        rec = dict(control=name, planted=cell, grid_best={k: best[k] for k in
                   ("pmax", "preg", "stream", "dir", "map", "cfg", "mode", "rot", "L", "bar")},
                   non_degenerate=bool(not full["degenerate"]),
                   found_planted_cell=bool(hit), plaintext_recovered=recovered,
                   passed=bool(hit and recovered and not full["degenerate"]))
        out["controls"].append(rec)
        ok &= rec["passed"]
        print(json.dumps(rec), flush=True)
    out["control_gate"] = "passed" if ok else "FAILED"
    if not ok:
        out["verdict"] = "KILLED - positive control failed; no keystream verdict"
        json.dump(out, open(os.path.join(HERE, "f5bt_results.json"), "w"), indent=1)
        print(out["verdict"])
        return

    # ---- the real pages
    gbest = {"pmax": -99.0}
    for pi, c in enumerate(pages):
        cnt, best, cross = sweep_page(c)
        best.pop("decode", None)
        best["page"] = pi
        out["pages"].append(best)
        for x in cross:
            x["page"] = pi
        out["crossers"].extend(cross)
        if best["pmax"] > gbest["pmax"]:
            gbest = dict(best)
        if pi % 5 == 0:
            print("page %d/55 gbest %.3f (page %s %s/%s/%s/%s %s rot %s) %.0fs"
                  % (pi, gbest["pmax"], gbest.get("page"), gbest.get("stream"), gbest.get("dir"),
                     gbest.get("map"), gbest.get("cfg"), gbest.get("mode"), gbest.get("rot"),
                     time.time() - t0), flush=True)

    out["observed_global_best"] = gbest
    out["n_crossers"] = len(out["crossers"])
    out["verdict"] = ("NEGATIVE" if not out["crossers"]
                      else "CROSSER(S) - FLAGGED-FOR-ORACLE per HUMAN-ORACLE.md, not certified")
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "f5bt_results.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("control_gate", "observed_global_best", "n_crossers",
                                          "verdict", "bars", "elapsed_s")}, indent=1))


if __name__ == "__main__":
    main()
