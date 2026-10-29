import os, sys, json, random, statistics
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
I2 = os.path.abspath(os.path.join(HERE, '..', 'I2-construction-axis'))
L7 = os.path.abspath(os.path.join(HERE, '..', '..', 'round18', 'L7-redteam'))
sys.path.insert(0, I2); sys.path.insert(0, L7)
import enciphers as E                      # I2's (wraps round32 beam_v2 encipher_skip_by_two)
B = E.B
import b1_power_envelope as L7M           # round18 L7's own enciphers + self_reliance plaintext (import has no side effects beyond loading)
sys.path.insert(0, os.path.join(L7, '..', '..', 'round10', 'L2-map'))
import mapcommon as M
pages = [len(p) for p in M.parse()["pages"]]; Lfull = sum(pages)
TEST = np.load(os.path.join(B.HERE, "models", "testhalves_lite.npz")); a = TEST["EN_MODERN"].astype(np.int64)
def rate(C): 
    d = sum(1 for i in range(1, len(C)) if C[i] == C[i-1]); return d, len(C)-1
out = {"LP2_observed_pct": 0.66384, "L7_claim": "round18/L7-redteam/ledger.json:119 ct_doublet_pct 0.84 (median of 7 seeds, L=240, self_reliance.txt)"}
def study(tag, L, nrep, mode):
    rs = []; dcounts = []
    for s in range(nrep):
        if mode == 'i2':
            r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1); P = a[st:st+L].tolist()
            K = B.sha_ctr_key(L * 12 + 2048, seed=b"X1R33_%d" % s)
            C, _ = E.skip_by_two(P, K, 0.83, 3301 + s)
        elif mode == 'l7enc_i2text':      # L7's own encipher function, I2's plaintext
            r = random.Random(9000 + s); st = r.randrange(0, len(a) - L - 1); P = a[st:st+L].tolist()
            K = L7M.key_sha(L * 8 + 1024, seed=b"X1R33_%d" % s)
            C, _ = L7M.enc_skip_by_two(P, K, seed=3301 + s)
        else:                              # L7 plaintext (self_reliance) + L7 encipher + L7 key maker
            P = L7M.take_plain(L, s) if L <= 5000 else L7M.ENG[1000:1000+L]
            K = L7M.key_sha(L * 8 + 1024, seed=b"X1R33_%d" % s)
            C, _ = L7M.enc_skip_by_two(P, K, seed=3301 + s)
        d, n = rate(C); dcounts.append(d); rs.append(100 * d / n)
    ent = {"L": L, "n_reps": nrep, "mean_pct": round(float(np.mean(rs)), 4), "median_pct": round(float(np.median(rs)), 4),
           "sd_pct": round(float(np.std(rs)), 4), "mean_doublet_count": round(float(np.mean(dcounts)), 3),
           "median7_first7": round(float(np.median(rs[:7])), 4), "expected_uniform_key_pct": round(100 * 0.17 / 29, 4)}
    out[tag] = ent; print(tag, ent, flush=True)
for mode in ('i2', 'l7enc_i2text', 'l7'):
    study(f'skip_by_two|{mode}|L240', 240, 300, mode)
    study(f'skip_by_two|{mode}|Lfull{Lfull}', Lfull, 30, mode)
out["what_2_of_239_equals_pct"] = round(100 * 2 / 239, 4)
json.dump(out, open(os.path.join(HERE, 'rerun_i2_doublet.json'), 'w'), indent=1)
