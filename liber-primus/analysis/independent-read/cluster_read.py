"""Independent, LABEL-FREE re-transcription audit of LP2 (pages 0-54).

Motivation: every prior "independent" read was not actually independent.
  - The whole-page vision armada confabulated (0.145 alignment) -> useless.
  - The Campaign-V SVC classifier was TRAINED on canon labels
    (build_dataset.py: "Label by position from canon") -> it can only reproduce
    canon; agreeing with its own training target is circular, not verification.

This script never shows canon to the clustering. It groups the ~10.7k glyph
bitmaps purely by visual shape, THEN compares the emergent partition to canon.

Two failure modes a systematic mis-read would produce, and how each is caught:
  (A) canon SPLITS one visual shape into two runes, or MERGES two shapes into one
      -> the cluster<->canon contingency table is not block-diagonal (a cluster
         straddles two canon runes, or a canon rune is torn across two clusters).
  (B) canon consistently MISLABELS a clean cluster (right partition, wrong name)
      -> invisible to clustering; flagged for human/vision shape-ID by dumping a
         mean-image + sample crops per cluster (adjudicate against Gematria Primus).

Outputs:
  metrics.json         - ARI / homogeneity / completeness / per-cluster purity
  contingency.txt      - cluster x canon-rune table (human readable)
  candidates.json      - clusters straddling >1 rune & runes torn across clusters
  reps/cluster_XX.png  - mean image + 16 sample crops per cluster (for shape-ID)
Reproduce: PYTHONUTF8=1 python cluster_read.py
"""
import json, collections
import numpy as np
from PIL import Image
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import (adjusted_rand_score, homogeneity_score,
                             completeness_score, v_measure_score)

H, W = 56, 40
DS = np.load('../stones/dataset.npz', allow_pickle=True)
X, y, prov = DS['X'].astype(np.float32), DS['y'], DS['prov']
N = len(X)
runes = sorted(set(y))
print(f'{N} glyphs, {len(runes)} canon runes')

# --- unsupervised: shape only, canon never seen ---
Xp = PCA(n_components=50, random_state=0).fit_transform(X)
K = 29  # alphabet size: ask for exactly as many clusters as runes
km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(Xp)
lab = km.labels_

ari = adjusted_rand_score(y, lab)
homo = homogeneity_score(y, lab)      # do clusters contain a single rune? (split test)
comp = completeness_score(y, lab)     # is each rune in a single cluster? (merge test)
vm = v_measure_score(y, lab)
print(f'ARI={ari:.4f} homogeneity={homo:.4f} completeness={comp:.4f} V={vm:.4f}')

# --- contingency: cluster x canon rune ---
cont = {c: collections.Counter() for c in range(K)}
for c, r in zip(lab, y):
    cont[c][r] += 1

lines = []
for c in range(K):
    tot = sum(cont[c].values())
    top = cont[c].most_common()
    purity = top[0][1] / tot
    frag = ' '.join(f'{rr}:{nn}' for rr, nn in top[:4])
    lines.append(f'cluster {c:2d}  n={tot:4d}  purity={purity:.3f}  -> {frag}')
open('contingency.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')

# --- candidates: real split/merge signatures (not benign minority confusion) ---
# A cluster is "impure" if its 2nd rune holds a MEANINGFUL share (>=15% and >=25 glyphs)
# -> canon may be splitting one shape into two runes.
impure = []
for c in range(K):
    tot = sum(cont[c].values())
    top = cont[c].most_common()
    if len(top) > 1 and top[1][1] >= max(25, 0.15 * tot):
        impure.append({'cluster': int(c), 'total': int(tot),
                       'runes': [(rr, int(nn)) for rr, nn in top[:5]]})

# A rune is "torn" if its glyphs are spread across clusters with no dominant home
# (top cluster holds <70% of the rune's mass) -> canon may be merging two shapes.
rune_home = {r: collections.Counter() for r in runes}
for c, r in zip(lab, y):
    rune_home[r][c] += 1
torn = []
for r in runes:
    tot = sum(rune_home[r].values())
    top = rune_home[r].most_common()
    share = top[0][1] / tot
    if share < 0.70:
        torn.append({'rune': r, 'total': int(tot), 'top_share': round(share, 3),
                     'clusters': [(int(cc), int(nn)) for cc, nn in top[:5]]})

json.dump({'ari': ari, 'homogeneity': homo, 'completeness': comp, 'v_measure': vm,
           'K': K, 'n': N},
          open('metrics.json', 'w'), indent=2)
json.dump({'impure_clusters': impure, 'torn_runes': torn},
          open('candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'impure clusters (possible canon SPLIT): {len(impure)}')
for it in impure:
    print('   ', it['cluster'], it['runes'])
print(f'torn runes (possible canon MERGE): {len(torn)}')
for it in torn:
    print('   ', it['rune'], it['top_share'], it['clusters'])

# --- dump per-cluster reps for independent shape-ID (failure mode B) ---
def tile(imgs, cols=8, pad=2):
    n = len(imgs)
    rows = (n + cols - 1) // cols
    canvas = np.ones((rows * (H + pad) + pad, cols * (W + pad) + pad)) * 0.4
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        y0, x0 = pad + r * (H + pad), pad + c * (W + pad)
        canvas[y0:y0 + H, x0:x0 + W] = im
    return canvas

for c in range(K):
    idx = np.where(lab == c)[0]
    mean_img = X[idx].mean(0).reshape(H, W)
    samp = idx[np.linspace(0, len(idx) - 1, min(15, len(idx))).astype(int)]
    crops = [X[i].reshape(H, W) for i in samp]
    grid = tile([mean_img] + crops)  # first tile = mean shape
    Image.fromarray((255 * (1 - grid)).astype(np.uint8)).save(f'reps/cluster_{c:02d}.png')
print('wrote reps/cluster_XX.png (tile[0] = mean shape, rest = samples)')
