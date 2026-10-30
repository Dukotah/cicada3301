#!/usr/bin/env python3
"""R38 S1 (a): independent exact-relation control generator.
Keystream: Python-3 stdlib random.Random(w) (seed(int<2^32) == Py2.7 init_by_array([w])); random29 = int(random()*29)
 (the Py2.7 randrange(29) reducer: 2 MT words/draw, genrand_res53).  Enciphering: the keyskip1 ONE-draw rejection loop,
 written here from the model definition (c = p - sign*k; if c == c_prev reject the key symbol w.p. supp and advance j by 1),
 sign=-1, supp=0.83.  Nothing imported from round25/skipdecode except the plaintext rune mapping eng_to_idx."""
import json, os, random, sys
LP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))
import skipdecode as sk
N = 29
def ks(w, n):
    r = random.Random(w if w else 0)
    return [int(r.random() * N) for _ in range(n)]
def encipher(P, K, supp, rseed, sign=-1):
    rng = random.Random(rseed); C = []; used = []; j = 0; cp = None
    for p in P:
        while True:
            c = (p - sign * K[j]) % N
            if cp is not None and c == cp and rng.random() < supp:
                j += 1; continue
            break
        C.append(c); used.append(j); j += 1; cp = c
    return C, used
txt = open(os.path.join(LP, "data", "keys", "self_reliance.txt"), encoding="utf-8", errors="ignore").read()
IDX = sk.eng_to_idx(txt)
out = {}
for n, (w, off) in enumerate([(777, 5000), (1234567891, 7000), (3000000017, 9000)]):
    P = IDX[off:off + 240]; K = ks(w, 1200)
    C, used = encipher(P, K, 0.83, 90000 + n)
    nsk = used[119] - 119 if len(used) > 119 else None
    out[str(w)] = {"seed": w, "pt_offset": off, "truth_idx": P, "cipher_idx": C, "n_key_skips_first120": nsk,
                   "n_key_skips_240": used[-1] - 239, "ks_first32": K[:32]}
    json.dump({"cipher_idx": C, "seed": w}, open(f"ctl_cipher_{w}.json", "w"))
json.dump(out, open("control_inputs.json", "w"), indent=1)
for w, v in out.items(): print(w, v["n_key_skips_first120"], v["n_key_skips_240"], len(v["cipher_idx"]))
