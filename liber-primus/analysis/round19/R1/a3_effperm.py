"""R1 / sub-attack A, supplement 2 — the frontier's scalar.

`mean_branching` counts admissible transitions but ignores the cost a penalty imposes.  The
measurable permissiveness is the REALISED drift rate on the winning path when the key is WRONG:
how often, per rune, the decoder actually exercises its freedom to steer noise toward English.
Plot that against the wrong-key null level and the frontier becomes one curve.
"""
import json, os, random, statistics as st
import r1_lib as R

HERE = os.path.dirname(os.path.abspath(__file__))
L, NN = 240, 60
CFG = [("exact/ms3","exact",3,0.0), ("union2/ms3","union2",3,0.0),
       ("free/ms1","free",1,0.0), ("free/ms2","free",2,0.0), ("free/ms3","free",3,0.0),
       ("freepen1.0/ms3","freepen",3,1.0), ("freepen2.0/ms3","freepen",3,2.0),
       ("freepen4.0/ms3","freepen",3,4.0), ("freepen6.0/ms3","freepen",3,6.0),
       ("freepen10.0/ms3","freepen",3,10.0)]

def main():
    uns = R.unsolved()
    rows = []
    for label, model, ms, lam in CFG:
        rng = random.Random(90210)
        dr, sc = [], []
        for k in range(NN):
            off = rng.randrange(0, len(uns)-L-1)
            C = uns[off:off+L]
            K = R.random_key(rng, L*10+512)
            bd = R.beam_decode(C, K, beam_w=400, max_skip=ms, model=model, lam=lam)
            dr.append(bd["n_drift"]/L); sc.append(bd["score"])
        # correct-key realised drift, baseline construction
        EN = R.build_registers()["EN"]
        cdr = []
        for rep in range(5):
            r2 = random.Random(700+rep); s = r2.randrange(0, len(EN)-L-1); P = EN[s:s+L]
            K = R.sha_key(b"CICADA3301"+bytes([rep]), L*10+512)
            Cc, _ = R.encipher_keyskip(P, K, supp=0.83, seed=700+rep)
            b2 = R.beam_decode(Cc, K, beam_w=400, max_skip=ms, model=model, lam=lam)
            cdr.append(b2["n_drift"]/L)
        rows.append({"label": label, "nominal_branching": R.mean_branching(model, ms),
                     "lam": lam,
                     "wrongkey_drift_per_rune": st.median(dr),
                     "correctkey_drift_per_rune_keyskip": st.median(cdr),
                     "wrongkey_null_mean": st.mean(sc), "wrongkey_null_max": max(sc), "n": NN})
        print("%-16s nominal %5.3f lam %4.1f | wrong-key drift/rune %.4f  correct-key %.4f | "
              "null mean %7.3f max %7.3f" % (label, rows[-1]["nominal_branching"], lam,
              rows[-1]["wrongkey_drift_per_rune"], rows[-1]["correctkey_drift_per_rune_keyskip"],
              rows[-1]["wrongkey_null_mean"], rows[-1]["wrongkey_null_max"]), flush=True)
    json.dump({"rows": rows, "L": L}, open(os.path.join(HERE, "out_a3.json"), "w"), indent=1)
    print("wrote out_a3.json")

if __name__ == "__main__":
    main()
