"""R46-A1 (a): what the alignment repair changes downstream (PREREG §4). Writes downstream.json.
1. Reconstruct v1 labels (dataset.npz y/prov) exactly from alignment.v1.json + corrected_map counts (Q5 gate).
2. v2 labels from the repaired alignment.json: removed / added / changed, glyph level.
3. Campaign-V classifier: committed oof_pred (per labelled row) and all_pred (per Xall glyph) scored vs v1 and v2.
4. The 450 O/A/AE: overlap with changed lines; re-run of oae_deepdive's PCA(30)+KMeans(3)+Hungarian on v1 (control:
   must give 450) and on v2 labels; the 21 glyphs of line 553 (image 49 clean line 2, never in Xall) are cropped here.
Run from anywhere; ~1 min (one image segmented)."""
import json, os, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
STONES = os.path.join(LP, 'analysis', 'stones'); os.chdir(LP); sys.path.insert(0, STONES)
import pipeline as P
gl, po = P.global_lines()
v1 = json.load(open(os.path.join(STONES, 'alignment.v1.json'))); v2 = json.load(open(os.path.join(STONES, 'alignment.json')))
cm = json.load(open(os.path.join(LP, 'analysis/round45/S1-transcription/corrected_map.json')))
D = np.load(os.path.join(STONES, 'dataset.npz'), allow_pickle=True)
y, prov, provall = D['y'], D['prov'], D['provall']
oof = np.load(os.path.join(STONES, 'oof_pred.npy'), allow_pickle=True); allp = np.load(os.path.join(STONES, 'all_pred.npy'))
OUT = {}


def labels(align):
    """{(n,i,j): canon rune} for every exact line, from counts (no images)."""
    L = {}
    for n in range(56):
        al = align[str(n)]
        for r in cm[str(n)]:
            i = r['clean_i']
            if i >= len(al): break
            g = al[i]
            if g is not None and r['count'] == len(gl[g]):
                for j in range(r['count']): L[(n, i, j)] = (g, gl[g][j])
    return L

# ---- 1. Q5 gate: exact v1 reconstruction ----
L1 = labels(v1)
ds = {(int(p[0]), int(p[1]), int(p[2])): (int(p[3]), p[4]) for p in prov}
gate = (L1 == ds)
OUT['v1_reconstruction'] = dict(n_reconstructed=len(L1), n_dataset=len(ds), exact_match=gate)
print('Q5 gate: v1 labels reconstructed', len(L1), 'vs dataset', len(ds), '->', 'EXACT' if gate else 'FAIL')
if not gate:
    json.dump(OUT, open(os.path.join(HERE, 'downstream.json'), 'w'), indent=1); sys.exit('gate failed: quantification only')

# ---- 2. label diff ----
L2 = labels(v2)
rem = sorted(set(L1) - set(L2)); add = sorted(set(L2) - set(L1)); both = set(L1) & set(L2)
chg = sorted(k for k in both if L1[k][1] != L2[k][1]); reg = sorted(k for k in both if L1[k][0] != L2[k][0])
OUT['labels'] = dict(v1=len(L1), v2=len(L2), removed=len(rem), added=len(add), relined_same_rows=len(reg),
                     rune_changed=len(chg), frac_v1_rows_wrong=round((len(rem) + len(reg)) / len(L1), 5),
                     wrong_v1_lines=sorted({L1[k][0] for k in rem + reg}),
                     added_lines=sorted({L2[k][0] for k in add}),
                     removed_lines=sorted({L1[k][0] for k in rem}))
print('labels', OUT['labels'])

# ---- 3. classifier re-score (not retrained) ----
row_of = {(int(p[0]), int(p[1]), int(p[2])): r for r, p in enumerate(prov)}
all_of = {(int(p[0]), int(p[1]), int(p[2])): r for r, p in enumerate(provall)}
a1 = sum(oof[row_of[k]] == L1[k][1] for k in L1)
# v2 over rows present in v1 dataset (oof exists only there); full v2 via all_pred (in-sample for v1 rows)
k2o = [k for k in L2 if k in row_of]; a2o = sum(oof[row_of[k]] == L2[k][1] for k in k2o)
k2a = [k for k in L2 if k in all_of]; a2a = sum(allp[all_of[k]] == L2[k][1] for k in k2a)
a1a = sum(allp[all_of[k]] == L1[k][1] for k in L1)
newk = [k for k in add if k in all_of]; anew = sum(allp[all_of[k]] == L2[k][1] for k in newk)
dis = json.load(open(os.path.join(STONES, 'disagreements.json')))
dis_lines = collections.Counter(d[3] for d in dis)
dis_res = sum(1 for d in dis if (d[0], d[1], d[2]) in L2 and L2[(d[0], d[1], d[2])][1] == d[5])
OUT['classifier'] = dict(
    oof_agree_v1=f'{a1}/{len(L1)}', oof_disagree_v1=len(L1) - a1,
    oof_agree_v2_on_v1_rows=f'{a2o}/{len(k2o)}', all_pred_agree_v1=f'{a1a}/{len(L1)}',
    all_pred_agree_v2=f'{a2a}/{len(k2a)}', all_pred_agree_on_newly_labelled=f'{anew}/{len(newk)}',
    v2_labels_without_prediction=len(L2) - len(k2a),
    disagreements_json=len(dis), disagreements_by_line=dict(dis_lines),
    disagreements_resolved_by_v2=dis_res,
    disagreements_on_rows_removed_in_v2=sum(1 for d in dis if (d[0], d[1], d[2]) not in L2))
print('classifier', OUT['classifier'])

# ---- 4. O/A/AE ----
oae = json.load(open(os.path.join(LP, 'analysis/independent-read/oae_mismatch.json'), encoding='utf8'))
wrong_lines = set(OUT['labels']['wrong_v1_lines'])
on_wrong = [o for o in oae if o['global_line'] in wrong_lines]
OUT['oae450'] = dict(n=len(oae), on_misregistered_v1_lines=len(on_wrong),
                     by_line=dict(collections.Counter(o['global_line'] for o in on_wrong)))
# extra crops for line 553
from build_dataset import norm_crop
lines, b, gray = P.segment_image('data/relikd/p49.jpg'); clean = [L for L in lines if len(L) >= 10]
garr = np.asarray(gray); extra = {}
for j, box in enumerate(clean[2]):
    c = norm_crop(garr, box)
    if c is not None: extra[(49, 2, j)] = c.flatten()
assert len(clean[2]) == 21
X, Xall = D['X'], D['Xall']
# determinism check: re-crop image 49 clean lines 0/1 and compare with Xall
redo = [np.array_equal(norm_crop(garr, box).flatten(), Xall[all_of[(49, i, j)]]) for i in (0, 1) for j, box in enumerate(clean[i])]
OUT['crop_determinism_img49'] = f'{sum(redo)}/{len(redo)} identical to Xall'
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
FAM = ['ᚩ', 'ᚪ', 'ᚫ']


def oae_run(feats, labs, keys):
    feats = np.asarray(feats, dtype=np.float32); labs = np.asarray(labs)
    m = np.isin(labs, FAM); Xf, yf = feats[m], labs[m]; kf = [k for k, t in zip(keys, m) if t]
    Xp = PCA(n_components=30, random_state=0).fit_transform(Xf)
    sub = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(Xp)
    cmx = np.zeros((3, 3), int)
    for s, r in zip(sub, yf): cmx[s, FAM.index(r)] += 1
    row, col = linear_sum_assignment(-cmx); s2r = {int(s): FAM[c] for s, c in zip(row, col)}
    pred = np.array([s2r[s] for s in sub])
    return int(m.sum()), {kf[i]: (yf[i], pred[i]) for i in np.where(pred != yf)[0]}

# control: v1 exactly as oae_deepdive (dataset order)
keys1 = [(int(p[0]), int(p[1]), int(p[2])) for p in prov]
n1, mm1 = oae_run(X, y, keys1)
ctrl = set(mm1) == {(o['page_image'], o['line_in_image'], o['pos_in_line']) for o in oae}
# v2: same build order as build_dataset (image, clean_i, j)
keys2 = sorted(L2)
F2 = [Xall[all_of[k]] if k in all_of else extra[k] for k in keys2]
n2, mm2 = oae_run(F2, [L2[k][1] for k in keys2], keys2)
s1, s2 = set(mm1), set(mm2)
OUT['oae_rerun'] = dict(control_v1_family=n1, control_v1_mismatches=len(mm1), control_reproduces_committed_450=ctrl,
                        v2_family=n2, v2_mismatches=len(mm2), dropped=len(s1 - s2), new=len(s2 - s1), kept=len(s1 & s2),
                        dropped_on_misregistered_lines=sum(1 for k in s1 - s2 if L1[k][0] in wrong_lines),
                        new_on_added_lines=sum(1 for k in s2 - s1 if k in set(add)),
                        v2_confusions=dict(collections.Counter(f'{a}->{b}' for a, b in mm2.values())))
print('oae', OUT['oae450'], OUT['oae_rerun'], OUT['crop_determinism_img49'])
json.dump(OUT, open(os.path.join(HERE, 'downstream.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
