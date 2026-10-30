"""gen.py -- feature generator (Round 34 ext.py recipe, round32/I4 engine) with an added EN_HALFVOWEL plant stream.
Usage: python gen.py <L> <key> <stream> <reps> <out.json>   (seed stream = round34 ext.py convention, 100000+ksd*7 per stream offset)"""
import sys, os, json, random, time
HERE = os.path.dirname(os.path.abspath(__file__))
I4 = os.path.abspath(os.path.join(HERE, '..', '..', 'round32', 'I4-nonfold-seal'))
sys.path.insert(0, I4)
import shim
shim.install(); AD = shim.load_panel()
import driftbeam as DB, panelmax20 as PM, plants as PL3, skipdecode as sk, ks
SUPP, PRESET, N_CANON = 0.83, "exact", 10 ** 6
SEED0 = {"EN_NOVOWEL": 100000, "EN_HALFVOWEL": 400000, "LATIN": 300000, "DE": 310000, "OE": 320000, "EN_KJV": 330000}
def run(L, key, sname, reps, outp):
    panels = PL3._panels(); kf = ks.make_ks("sha256_ctr", "mod29", key, L * 4 + 1024); K = list(kf)
    bar = float(PM.panelmax_bar(PRESET, N_CANON, 0.01)); kw = DB.PRESETS[PRESET]
    ksd = sum(key) % 997; seed0 = SEED0[sname] + ksd * 7
    out = {"key": key.decode(), "L": L, "stream": sname, "bar": bar, "draws": reps, "cases": []}
    stream = panels[sname]; t0 = time.time()
    for rep in range(reps):
        rng = random.Random(seed0 + rep)
        s = rng.randrange(0, len(stream) - L - 1); P = list(stream[s:s + L])
        C, _, _ = sk.encipher_keyskip(P, kf, sign=-1, supp=SUPP, seed=seed0 + 50000 + rep); C = list(C)
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **kw)
        idx = d["plain_idx"]; a = AD.adjudicate(idx, translit=d["translit"]); rec = DB.recovery(idx, P)
        pm = float(a["pmax"])
        if pm < bar: continue
        label = "halluc" if rec < 0.90 else ("genuine" if rec >= 0.95 else "gray")
        out["cases"].append({"stream": sname, "rep": rep, "label": label, "rec": float(rec), "pmax": pm,
                             "preg_name": AD.panel().registers[int(a["preg"])]})
    out["secs"] = round(time.time() - t0)
    json.dump(out, open(outp, "w"))
    print(key, L, sname, reps, "cases", len(out["cases"]), out["secs"], "s", flush=True)
if __name__ == "__main__":
    L, k, sn, r, o = sys.argv[1:6]; run(int(L), k.encode(), sn, int(r), o)
