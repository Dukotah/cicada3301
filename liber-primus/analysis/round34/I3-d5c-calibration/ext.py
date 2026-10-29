"""ext.py -- lean re-implementation of round32/I4 extract.py main() (same RNG streams/recipe, no cut/cons/headp work).
Usage: python ext.py <L> <keyname> <nv_reps> <en_reps> <sp_reps>   -> feat_<key>_<L>.json"""
import sys, os, json, random, time
HERE = os.path.dirname(os.path.abspath(__file__))
I4 = os.path.abspath(os.path.join(HERE, '..', '..', 'round32', 'I4-nonfold-seal'))
sys.path.insert(0, I4)
import shim
shim.install(); AD = shim.load_panel()
import driftbeam as DB, panelmax20 as PM, plants as PL3, skipdecode as sk, ks
SUPP, PRESET, N_CANON = 0.83, "exact", 10 ** 6
def run(L, key, nv, en, sp):
    panels = PL3._panels(); kf = ks.make_ks("sha256_ctr", "mod29", key, L * 4 + 1024); K = list(kf)
    bar = float(PM.panelmax_bar(PRESET, N_CANON, 0.01)); kw = DB.PRESETS[PRESET]
    ksd = sum(key) % 997
    plan = [(["EN_NOVOWEL"], nv, 100000 + ksd * 7), (["EN_MODERN"], en, 200000 + ksd * 7), (["LATIN", "DE", "OE", "EN_KJV"], sp, 300000 + ksd * 7)]
    out = {"key": key.decode(), "L": L, "bar": bar, "cases": [], "draws": {}}
    t0 = time.time()
    for ssi, (streams, n, seed0) in enumerate(plan):
        tag = ["nv", "en", "sp"][ssi]; cnt = 0
        for sname in streams:
            stream = panels[sname]
            for rep in range(n):
                rng = random.Random(seed0 + rep)
                s = rng.randrange(0, len(stream) - L - 1); P = list(stream[s:s + L])
                C, _, _ = sk.encipher_keyskip(P, kf, sign=-1, supp=SUPP, seed=seed0 + 50000 + rep); C = list(C)
                d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **kw)
                idx = d["plain_idx"]; a = AD.adjudicate(idx, translit=d["translit"]); rec = DB.recovery(idx, P); cnt += 1
                pm = float(a["pmax"])
                if pm < bar: continue
                label = "halluc" if rec < 0.90 else ("genuine" if rec >= 0.95 else "gray")
                out["cases"].append({"pop": tag, "stream": sname, "rep": rep, "label": label, "rec": float(rec),
                                     "pmax": pm, "preg_name": AD.panel().registers[int(a["preg"])]})
        out["draws"][tag] = cnt
        print(key, L, tag, cnt, "draws", len(out["cases"]), "cases", round(time.time() - t0), "s", flush=True)
    json.dump(out, open(os.path.join(HERE, f"feat_{key.decode()}_{L}.json"), "w"))
if __name__ == "__main__":
    L, k, a, b, c = sys.argv[1:6]; run(int(L), k.encode(), int(a), int(b), int(c))
