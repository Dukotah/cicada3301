"""Phase 2: are canon's near-identical families visually self-consistent?

Phase 1 showed the ONLY impurity is K-means fusing known look-alike families
(O/A/AE, R/W, L/W). Two explanations:
  (i)  K-means underfits look-alikes at K=29; the shapes ARE separable and canon
       is consistent  -> raising K makes clusters rune-pure. (canon confirmed)
  (ii) canon cross-cuts the real shapes (systematic within-family confusion)
       -> some cluster stays mixed even at high K. (candidate error)

Test A: K sweep. Report best-match purity achievable per rune as K grows.
Test B: isolate each fused family, re-cluster ONLY those glyphs into its own
        member count, and measure how well the sub-partition aligns to canon
        (ARI). High ARI = canon's within-family split matches the visual split.
"""
import json, collections
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, homogeneity_score

DS = np.load('../stones/dataset.npz', allow_pickle=True)
X, y = DS['X'].astype(np.float32), DS['y']
Xp = PCA(n_components=50, random_state=0).fit_transform(X)

print('=== Test A: K sweep (homogeneity should rise toward 1 if canon is separable) ===')
for K in (29, 40, 58, 87):
    lab = KMeans(n_clusters=K, n_init=10, random_state=0).fit_predict(Xp)
    homo = homogeneity_score(y, lab)
    # per-rune best recovery: largest single-cluster share of each rune's glyphs
    best = {}
    for r in sorted(set(y)):
        m = (y == r)
        cnt = collections.Counter(lab[m])
        best[r] = cnt.most_common(1)[0][1] / m.sum()
    worst = sorted(best.items(), key=lambda kv: kv[1])[:5]
    print(f'K={K:3d}  homogeneity={homo:.4f}  worst-recovered runes: ' +
          ' '.join(f'{r}={s:.2f}' for r, s in worst))

print('\n=== Test B: within-family self-consistency ===')
families = [
    ['ᚩ', 'ᚪ', 'ᚫ'],   # O / A / AE  (page24:172 dispute family)
    ['ᚱ', 'ᚹ'],          # R / W
    ['ᛚ', 'ᚹ'],          # L / W
    ['ᛗ', 'ᛖ'],          # M / E
    ['ᛗ', 'ᛞ'],          # M / D (chart look-alikes)
    ['ᚾ', 'ᛁ'],          # N / I
    ['ᛒ', 'ᛖ'],          # B / E
]
report = []
for fam in families:
    mask = np.isin(y, fam)
    Xf = PCA(n_components=30, random_state=0).fit_transform(X[mask])
    yf = y[mask]
    sub = KMeans(n_clusters=len(fam), n_init=10, random_state=0).fit_predict(Xf)
    ari = adjusted_rand_score(yf, sub)
    # confusion: for each canon rune in family, dominant subcluster purity
    pur = []
    for r in fam:
        m = (yf == r)
        c = collections.Counter(sub[m])
        pur.append((r, int(m.sum()), round(c.most_common(1)[0][1] / m.sum(), 3)))
    report.append({'family': fam, 'ari': round(ari, 3), 'purity': pur})
    tag = 'CONSISTENT' if ari >= 0.5 else 'CROSS-CUT -> candidate'
    print(f'{"".join(fam):6s} ari={ari:.3f}  {tag}   ' +
          ' '.join(f'{r}(n{n},p{p})' for r, n, p in pur))

json.dump(report, open('family_probe.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\nwrote family_probe.json')
