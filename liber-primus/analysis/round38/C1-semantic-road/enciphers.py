"""R38/C1 independent forward encipherers for the semantic-direction variants. Writes nothing."""
import os, sys, json
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); R37 = os.path.join(HERE, "..", "..", "round37", "C1-composed-clue-readings")
sys.path.insert(0, R37)
import enciphers_u2_u3 as E
IDX = json.load(open(os.path.join(HERE, "lp1_meaning_index.json")))["rows"]
VARIANTS = [(r, red) for r in ("A", "B") for red in ("R29", "R28", "D29")]
VAL = {"%s-%s" % v: [row[v[0]][v[1]] for row in IDX] for v in VARIANTS}
N = len(IDX); K0 = E.K0


def d_seq(var, lens, s):
    return [VAL[var][(s + k) % N] for k in range(len(lens))]


def enc(P, lens, var, s, sigma, mode, rel=None, seed=1):
    d = d_seq(var, lens, s)
    if mode in ("A1", "A2"):
        C, i, D = [], 0, 0
        for k, l in enumerate(lens):
            D += d[k]; sh = d[k] if mode == "A1" else D
            for t in range(l):
                if i >= len(P): return C
                C.append((P[i] + sigma * sh) % 29); i += 1
        return C
    K = []; r = 0; J = 0
    for k, l in enumerate(lens):
        J += sigma * d[k]
        for t in range(l): K.append(K0[(r + J + t) % len(K0)])
        r += l
    return E.encipher_with_key(P, K, rel, seed)
