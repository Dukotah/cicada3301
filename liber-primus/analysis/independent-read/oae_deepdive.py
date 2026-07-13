"""Phase 3: put eyes on the O/A/AE triad (the one surviving candidate).

Unsupervised 3-way sub-clustering of {O ᚩ, A ᚪ, AE ᚫ} agrees with canon ~80%.
The ~20% that land with a sibling are the only glyphs in the whole book where a
visual read might disagree with canon. Isolate them and render for adjudication.

Output:
  oae_meanshapes.png  - the 3 canon mean shapes side by side (are they distinct?)
  oae_mismatch.png    - every glyph whose unsupervised subcluster != canon,
                        labelled 'canon->nearest', grouped, for eyeball ID.
  oae_mismatch.json   - provenance of each so a confirmed flip is locatable+testable
"""
import json, collections
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment

H, W = 56, 40
DS = np.load('../stones/dataset.npz', allow_pickle=True)
X, y, prov = DS['X'].astype(np.float32), DS['y'], DS['prov']
FAM = ['ᚩ', 'ᚪ', 'ᚫ']
mask = np.isin(y, FAM)
Xf, yf, pf = X[mask], y[mask], prov[mask]
gidx = np.where(mask)[0]

Xp = PCA(n_components=30, random_state=0).fit_transform(Xf)
sub = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(Xp)

# map subcluster -> canon rune by majority (Hungarian on the confusion matrix)
runes = FAM
cm = np.zeros((3, 3), int)
for s, r in zip(sub, yf):
    cm[s, runes.index(r)] += 1
row, col = linear_sum_assignment(-cm)
sub2rune = {int(s): runes[c] for s, c in zip(row, col)}
pred = np.array([sub2rune[s] for s in sub])

mism = np.where(pred != yf)[0]
print(f'{mask.sum()} O/A/AE glyphs, {len(mism)} unsupervised-vs-canon mismatches '
      f'({100*len(mism)/mask.sum():.1f}%)')
conf = collections.Counter((yf[i], pred[i]) for i in mism)
for (c, p), n in conf.most_common():
    print(f'   canon {c} -> looks like {p}: {n}')

# --- mean shapes: are the 3 canon classes visually distinct at all? ---
def to_img(v): return v.reshape(H, W)
def paste(canvas, img, x0, y0):
    canvas[y0:y0+H, x0:x0+W] = img
pad = 4
means = np.ones((H + 2*pad, 3*(W+pad)+pad)) * 0.4
for i, r in enumerate(FAM):
    paste(means, to_img(Xf[yf == r].mean(0)), pad + i*(W+pad), pad)
Image.fromarray((255*(1-means)).astype(np.uint8)).save('oae_meanshapes.png')

# --- mismatch montage, grouped canon->pred, mean of each group + samples ---
groups = sorted(conf.keys(), key=lambda k: -conf[k])
cols = 10
recs = []
rows_needed = 0
for g in groups:
    ids = [i for i in mism if (yf[i], pred[i]) == g]
    rows_needed += 1 + (len(ids)+cols-1)//cols
canvas = np.ones((rows_needed*(H+pad)+pad, (cols+1)*(W+pad)+pad)) * 0.4
r_cursor = 0
for (c, p) in groups:
    ids = [i for i in mism if (yf[i], pred[i]) == (c, p)]
    # header row: canon mean | pred mean
    paste(canvas, to_img(Xf[yf == c].mean(0)), pad, pad + r_cursor*(H+pad))
    paste(canvas, to_img(Xf[yf == p].mean(0)), pad+(W+pad), pad + r_cursor*(H+pad))
    r_cursor += 1
    for k, i in enumerate(ids):
        rr, cc = divmod(k, cols)
        paste(canvas, to_img(Xf[i]),
              pad + cc*(W+pad), pad + (r_cursor+rr)*(H+pad))
        gi = int(gidx[i])
        recs.append({'canon': c, 'looks_like': p,
                     'page_image': int(pf[i][0]), 'line_in_image': int(pf[i][1]),
                     'pos_in_line': int(pf[i][2]), 'global_line': int(pf[i][3]),
                     'global_glyph_index': gi})
    r_cursor += (len(ids)+cols-1)//cols
Image.fromarray((255*(1-canvas)).astype(np.uint8)).save('oae_mismatch.png')
json.dump(recs, open('oae_mismatch.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('wrote oae_meanshapes.png, oae_mismatch.png (header rows = canon mean | sibling mean), oae_mismatch.json')
