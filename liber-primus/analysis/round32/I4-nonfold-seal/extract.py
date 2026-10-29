"""extract.py -- build one population and cache its oracle-free feature table (feat_<name>.json).

Usage: python extract.py <pop>   with pop in tune_nv tune_en held_nv held_en spread
Reuses round21/L1's recipe (same RNG streams). Truth (P, recovery) is stored ONLY as a label for
evaluation; no feature below reads it.
"""
import sys, os, json, random, time
import shim
shim.install(); AD = shim.load_panel()
import numpy as np
import driftbeam as DB, panelmax20 as PM, plants as PL3, skipdecode as sk, ks
import hitfn21_folds as F

L, SUPP, PRESET, N_CANON = int(os.environ.get('I4_L', 240)), 0.83, "exact", 10 ** 6
POPS = {   # name: (stream(s), key_seed, n_reps, seed0, csd0)
    "tune_nv": (["EN_NOVOWEL"], b"CICADA", 60, 5000, 600),
    "tune_en": (["EN_MODERN"], b"CICADA", 20, 7000, 99),
    "held_nv": (["EN_NOVOWEL"], b"CICADA3301", 90, 8000, 2600),
    "held_en": (["EN_MODERN"], b"CICADA3301", 24, 9100, 770),
    "spread":  (["LATIN", "DE", "OE", "EN_KJV"], b"CICADA3301", 14, 9500, 4100),
    # VIRGIN split (ADDENDUM A of PREREG.md): fast mode -- only k=5 fold cuts, no cross-construction decodes
    "virg_nv": (["EN_NOVOWEL"], b"CICADA-I4", 200, 12000, 6000),
    "virg_en": (["EN_MODERN"], b"CICADA-I4", 30, 13100, 8800),
    "virg_sp": (["LATIN", "DE", "OE", "EN_KJV"], b"CICADA-I4", 14, 14500, 9900),
    "l120_nv": (["EN_NOVOWEL"], b"CICADA-I4c", 500, 32000, 26000),
    "l120_en": (["EN_MODERN"], b"CICADA-I4c", 40, 33100, 28800),
    "l120_sp": (["LATIN", "DE", "OE", "EN_KJV"], b"CICADA-I4c", 20, 34500, 29900),
    "virg2_nv": (["EN_NOVOWEL"], b"CICADA-I4b", 500, 22000, 16000),
    "virg2_en": (["EN_MODERN"], b"CICADA-I4b", 40, 23100, 18800),
    "virg2_sp": (["LATIN", "DE", "OE", "EN_KJV"], b"CICADA-I4b", 20, 24500, 19900),
}
FAST = ("l120_nv", "l120_en", "l120_sp", "virg_nv", "virg_en", "virg_sp", "virg2_nv", "virg2_en", "virg2_sp")

def cut_set(n):
    s = set()
    for k in range(2, 9):
        for lo, hi in F._fold_bounds(n, k):
            if n - hi >= 3:
                s.add(hi)
    s.update(range(8, n - 7, 8))
    return sorted(s)

def tail_recovery(C, K, full_idx, hi, kw):
    pref = DB.beam_decode(C[:hi], K, sign=-1, o=0, beam_w=400, want_path=True, **kw)
    kp = pref["ptr_end"] + 1
    tail = DB.beam_decode(C[hi:], K, sign=-1, o=kp, beam_w=400, want_path=True, **kw)["plain_idx"]
    ref = list(full_idx)[hi:]
    m = min(len(tail), len(ref))
    return sum(1 for a, b in zip(tail[:m], ref[:m]) if a == b) / m if m >= 3 else None

def agree(a, b):
    m = min(len(a), len(b))
    return sum(1 for x, y in zip(a[:m], b[:m]) if x == y) / m if m else 0.0

def main(name):
    streams, key_seed, n_reps, seed0, csd0 = POPS[name]
    panels = PL3._panels()
    Kfull = ks.make_ks("sha256_ctr", "mod29", key_seed, L * 4 + 1024)
    K = list(Kfull)
    bar = float(PM.panelmax_bar(PRESET, N_CANON, 0.01))
    kw = DB.PRESETS[PRESET]
    cuts = [h for h in (48, 96, 144, 192) if L - h >= 3] if name in FAST else cut_set(L)
    out = {"name": name, "bar": bar, "L": L, "cuts": cuts, "cases": [], "n_draws": 0}
    t0 = time.time()
    for sname in streams:
        stream = panels[sname]
        for rep in range(n_reps):
            rng = random.Random(seed0 + rep)
            s = rng.randrange(0, len(stream) - L - 1)
            P = list(stream[s:s + L])
            C, nsk, _ = sk.encipher_keyskip(P, Kfull, sign=-1, supp=SUPP, seed=csd0 + rep)
            C = list(C)
            d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **kw)
            idx = d["plain_idx"]
            a = AD.adjudicate(idx, translit=d["translit"])
            rec = DB.recovery(idx, P)
            out["n_draws"] += 1
            pm = float(a["pmax"])
            if pm < bar:
                continue
            if rec < 0.90:
                label = "halluc"
            elif rec >= 0.95:
                label = "genuine"
            else:
                label = "gray"
            if name in ("tune_nv", "held_nv") and label == "gray":
                pass
            rec_cut = {str(h): tail_recovery(C, K, idx, h, kw) for h in cuts}
            # cross-construction / beam-width self-consistency (oracle-free)
            cons = {}
            _cons_specs = [] if name in FAST else [("ms8", DB.PRESETS["exact_ms8"], 400), ("pair", DB.PRESETS["pair"], 400),
                                                   ("bw100", kw, 100)]
            for nm, kw2, bw in _cons_specs:
                idx2 = DB.beam_decode(C, K, sign=-1, o=0, beam_w=bw, want_path=True, **kw2)["plain_idx"]
                cons[nm] = agree(idx2, idx)
            headp = {}
            for h in (64, 120, 180):
                ah = AD.adjudicate(idx[:h])
                headp[str(h)] = float(ah["pmax"])
            feat = {k: (float(a[k]) if k not in ("z",) else [float(v) for v in a[k]])
                    for k in ("en", "pmax", "pmax_ne", "pcon", "ioc", "mds", "h2", "zl", "z") if k in a}
            feat["preg"] = int(a["preg"])
            feat["preg_name"] = AD.panel().registers[int(a["preg"])]
            out["cases"].append({
                "stream": sname, "rep": rep, "label": label, "true_recovery": float(rec),
                "feat": feat, "cut_rec": rec_cut, "cons": cons, "headp": headp,
                "n_skips": int(d.get("n_skips", -1)), "n_unexpl": int(d.get("n_unexplained", -1)),
                "beam_score": float(d.get("beam_score", d.get("score", 0.0))),
            })
        print(name, sname, "done", len(out["cases"]), "cases", round(time.time() - t0), "s", flush=True)
    json.dump(out, open(os.path.join(shim.HERE, f"feat_{name}.json"), "w"))
    from collections import Counter
    print(name, dict(Counter((c["stream"], c["label"]) for c in out["cases"])), "draws", out["n_draws"])

if __name__ == "__main__":
    main(sys.argv[1])
