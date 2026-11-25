"""R46-A1 (a), descriptive follow-up to downstream.py: is the O/A/AE '450' a stable instrument output?
Re-runs oae_deepdive's PCA(30)+KMeans(3) on v1 and v2 labels over KMeans seeds 0..9 and reports the mismatch counts.
Also names the one v2 label where the committed all_pred disagrees. Writes oae_stability.json. (Needs sklearn: run in WSL.)"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.argv = [sys.argv[0]]
src = open(os.path.join(HERE, 'downstream.py'), encoding='utf8').read()
src = src.split("print('oae', OUT['oae450']")[0]  # reuse everything up to the final print/dump
exec(compile(src, 'downstream.py', 'exec'))


def run_seed(feats, labs, seed):
    feats = np.asarray(feats, dtype=np.float32); labs = np.asarray(labs); m = np.isin(labs, FAM)
    Xp = PCA(n_components=30, random_state=0).fit_transform(feats[m])
    sub = KMeans(n_clusters=3, n_init=10, random_state=seed).fit_predict(Xp)
    cmx = np.zeros((3, 3), int)
    for s, r in zip(sub, labs[m]): cmx[s, FAM.index(r)] += 1
    row, col = linear_sum_assignment(-cmx)
    return int(cmx.sum() - cmx[row, col].sum())

lab2 = [L2[k][1] for k in keys2]
res = dict(seeds=list(range(10)), v1=[run_seed(X, y, s) for s in range(10)], v2=[run_seed(F2, lab2, s) for s in range(10)])
bad = [dict(key=list(k), gline=L2[k][0], canon=L2[k][1], all_pred=str(allp[all_of[k]])) for k in L2
       if k in all_of and allp[all_of[k]] != L2[k][1]]
res['all_pred_v2_disagreements'] = bad
print(res)
json.dump(res, open(os.path.join(HERE, 'oae_stability.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)

# data-perturbation sensitivity (descriptive): v1 minus 42 random O/A/AE glyphs (the size of the v2 family change), 10 draws
rng = np.random.default_rng(46)
fam_rows = np.where(np.isin(y, FAM))[0]; pert = []
for _ in range(10):
    keep = np.ones(len(y), bool); keep[rng.choice(fam_rows, 42, replace=False)] = False
    pert.append(run_seed(X[keep], y[keep], 0))
res['v1_minus_42_random_family_glyphs'] = pert
print('perturbation', pert)
json.dump(res, open(os.path.join(HERE, 'oae_stability.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
