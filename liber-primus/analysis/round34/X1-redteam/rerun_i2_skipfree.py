"""X1/R34 re-run of R32-B1 prefilter_power_trigram logic with plants split by whether a key-skip falls inside the head,
and whether the CIPHERTEXT head contains a doublet. Also the I2 frozen lse m=20 screen on the same plants."""
import sys, json, random, numpy as np
sys.dont_write_bytecode = True
sys.path.insert(0, '.')
from common import *
import pf
sys.path.insert(0, '../../round34/I2-novowel-prefilter')
import pf_v3
print('U[:40] doublets:', sum(1 for i in range(1, 40) if U[i] == U[i-1]), ' U[:120]:', sum(1 for i in range(1, 120) if U[i] == U[i-1]))
rng = random.Random(3301)
PREF = list(range(1325376000 >> 20, (1401580800 >> 20) + 1))
def rand_seeds(n): return np.array([(rng.choice(PREF) << 20) | rng.randrange(1 << 20) for _ in range(n)], dtype=np.uint64)
pan = AD.panel(); LMT = pan.LMT.astype(np.float32)
MS = (18, 24); v = 'bash4.2'
C = np.array(U[:24], dtype=np.int8)[:, None]
sd_ = rand_seeds(1 << 18); K = pf.heads(sd_, 24, v)
nulls = {}
for m in MS:
    S = pf.tri_stat((C[:m] - K[:m]) % 29, LMT); mu, sdv = S.mean(0), S.std(0)
    mx = ((S - mu) / sdv).max(1); nulls[m] = (mu, sdv, float(np.quantile(mx, 0.999)))
# lse m=20 null threshold: use frozen
cor = corpora(); out = {}
NP = 600
for reg in ('EN_NOVOWEL', 'EN_MODERN'):
    txt = cor[reg]
    for rel, enc in (('keyskip2', enc_pair), ('keyskip1', enc_exact)):
        seeds = rand_seeds(NP); rows = []
        for i, s in enumerate(seeds):
            st = rng.randrange(0, len(txt) - 130); P = txt[st:st+120]; Ks = ks(int(s), v)
            Cc = enc(P, Ks, seed=i + 1)[:24]
            nos = [(p + Ks[t]) % 29 for t, p in enumerate(P[:24])]
            f = next((t for t in range(24) if Cc[t] != nos[t]), 99)       # first index where a skip has occurred
            dbl = next((t for t in range(1, 24) if Cc[t] == Cc[t-1]), 99)
            rows.append((Cc, f, dbl))
        Cs = np.array([r[0] for r in rows], dtype=np.int8).T; Kp = pf.heads(seeds, 24, v)
        f = np.array([r[1] for r in rows]); dbl = np.array([r[2] for r in rows])
        res = {}
        for m in MS:
            mu, sdv, thr = nulls[m]
            hit = pf.tri_stat((Cs[:m] - Kp[:m]) % 29, LMT, mu, sdv).max(1) > thr
            res['zmax_m%d' % m] = {'power_all': float(hit.mean()), 'frac_skip_free_head': float((f >= m).mean()),
                'power_skip_free': float(hit[f >= m].mean()) if (f >= m).any() else None,
                'power_skip_in_head': float(hit[f < m].mean()) if (f < m).any() else None,
                'frac_cipher_head_has_doublet': float((dbl < m).mean()),
                'frac_skip_free_given_no_cipher_doublet': float((f[dbl >= m] >= m).mean()),
                'power_given_no_cipher_doublet': float(hit[dbl >= m].mean())}
        m = 20
        Pm = (Cs[:m] - Kp[:m]) % 29; hit = pf_v3.screen(Pm, LMT, pf_v3.FROZEN[20])
        res['lse_m20_frozen'] = {'power_all': float(hit.mean()), 'frac_skip_free_head': float((f >= m).mean()),
            'power_skip_free': float(hit[f >= m].mean()), 'power_skip_in_head': float(hit[f < m].mean()),
            'frac_cipher_head_has_doublet': float((dbl < m).mean()),
            'frac_skip_free_given_no_cipher_doublet': float((f[dbl >= m] >= m).mean()),
            'power_given_no_cipher_doublet': float(hit[dbl >= m].mean())}
        out[reg + '|' + rel] = res
        print(reg, rel, json.dumps(res), flush=True)
json.dump({'U40_doublets': sum(1 for i in range(1, 40) if U[i] == U[i-1]), 'n_plants': NP, 'cells': out},
          open('../../round34/X1-redteam/rerun_i2_skipfree.json', 'w'), indent=1)
