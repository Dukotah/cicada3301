"""R46-X1: independent check of A1's claim that the O/A/AE '450' is basin-dependent.
Reuses A1's downstream.py setup (exec, read-only) for v1/v2 features+labels, then:
 - 20 random 42-glyph removals from v1 AND from v2 (seed 0 KMeans, as committed), record counts and mismatch sets;
 - PCA random_state 0..4 on v1 and v2 (A1 varied only the KMeans seed);
 - 'stable core' = glyphs in the mismatch set in >= 90% of all runs where the glyph is present.
Writes x1_oae_basins.json. Needs sklearn (WSL)."""
import json, os, sys, collections
import numpy as np
X1 = os.path.dirname(os.path.abspath(__file__))
A1 = os.path.join(X1, '..', 'A1-hygiene')
HERE = os.path.abspath(A1); sys.argv = [sys.argv[0]]
src = open(os.path.join(A1, 'downstream.py'), encoding='utf8').read()
src = src.split("print('oae', OUT['oae450']")[0]
src = src.replace("json.dump(OUT, open(os.path.join(HERE, 'downstream.json'), 'w'), indent=1); ", "")  # never write A1 files
exec(compile(src, 'downstream.py', 'exec'))

def run(feats, labs, keys, kseed=0, pseed=0):
    feats = np.asarray(feats, dtype=np.float32); labs = np.asarray(labs); m = np.isin(labs, FAM)
    kf = [k for k, t in zip(keys, m) if t]
    Xp = PCA(n_components=30, random_state=pseed).fit_transform(feats[m])
    sub = KMeans(n_clusters=3, n_init=10, random_state=kseed).fit_predict(Xp)
    cmx = np.zeros((3, 3), int)
    for s, r in zip(sub, labs[m]): cmx[s, FAM.index(r)] += 1
    row, col = linear_sum_assignment(-cmx); s2r = {int(s): FAM[c] for s, c in zip(row, col)}
    pred = np.array([s2r[s] for s in sub]); yf = labs[m]
    return set(kf[i] for i in np.where(pred != yf)[0]), set(kf)

lab2 = [L2[k][1] for k in keys2]
sets = {'v1': (np.asarray(X), np.asarray(y), keys1), 'v2': (np.asarray(F2, dtype=np.float32), np.asarray(lab2), keys2)}
rng = np.random.default_rng(4601)
out = {}; mis_ct = collections.Counter(); pres_ct = collections.Counter()
for name, (F, Y, K) in sets.items():
    fam = np.where(np.isin(Y, FAM))[0]
    r = dict(pca_seeds=[], removals=[])
    for ps in range(5):
        mm, pr = run(F, Y, K, 0, ps); r['pca_seeds'].append(len(mm))
    for t in range(20):
        keep = np.ones(len(Y), bool); keep[rng.choice(fam, 42, replace=False)] = False
        Kk = [k for k, t2 in zip(K, keep) if t2]
        mm, pr = run(F[keep], Y[keep], Kk)
        r['removals'].append(len(mm))
        for k in pr: pres_ct[k] += 1
        for k in mm: mis_ct[k] += 1
    out[name] = r
    print(name, r, flush=True)
committed = {(o['page_image'], o['line_in_image'], o['pos_in_line']) for o in oae}
core = {k for k in pres_ct if mis_ct[k] >= 0.9 * pres_ct[k]}
out['stable_core_n'] = len(core)
out['stable_core_in_committed_450'] = len(core & committed)
out['committed_450_in_core'] = f'{len(core & committed)}/{len(committed)}'
print({k: v for k, v in out.items() if k.startswith('stable') or k.startswith('committed')})
json.dump(out, open(os.path.join(X1, 'x1_oae_basins.json'), 'w'), indent=1)
