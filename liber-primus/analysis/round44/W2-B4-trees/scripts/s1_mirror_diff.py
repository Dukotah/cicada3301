"""S1: PC1 plant + T1 mirror pixel-diff for p32/p55 across all held non-identical copies."""
import io, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imglib as L

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}

# ---------- PC1: plant ----------
a = L.loadY(L.PATHS['p32_relikd'])
planted = a.copy()
y0, y1, x0, x1 = L.P32_TREE
cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
planted[cy:cy + 40, cx:cx + 40] = np.clip(planted[cy:cy + 40, cx:cx + 40] + 10, 0, 255)
buf = io.BytesIO()
Image.fromarray(planted.astype(np.uint8)).save(buf, format='JPEG', quality=85)
buf.seek(0)
planted_rt = np.asarray(Image.open(buf).convert('L'), float)
# baseline: same q=85 round-trip WITHOUT the plant (isolates the plant from recompression)
buf2 = io.BytesIO()
Image.fromarray(a.astype(np.uint8)).save(buf2, format='JPEG', quality=85)
buf2.seek(0)
clean_rt = np.asarray(Image.open(buf2).convert('L'), float)

pc1 = L.t1_stats(a, planted_rt, L.P32_TREE)
pc1_base = L.t1_stats(a, clean_rt, L.P32_TREE)
out['PC1_plant'] = pc1
out['PC1_clean_roundtrip_baseline'] = pc1_base
out['PC1_passed'] = bool(pc1['T1_fired'])
print('PC1 plant:', pc1)
print('PC1 clean baseline:', pc1_base)
assert pc1['T1_fired'], 'POSITIVE CONTROL PC1 FAILED - stop'

# ---------- real targets ----------
# NOTE (run 2): cijhho 'liber primus images full' numbering is OFFSET — its 32.jpg/55.jpg are
# different pages. Byte-identity search found full/49.jpg == relikd p32 and full/72.jpg ==
# relikd p55 (sha256 equal), so that mirror contributes no pixel variant. The only
# non-byte-identical held copies are the wiki ones.
pairs = [
    ('p32', 'p32_relikd', 'p32_wiki', L.P32_TREE),
    ('p55', 'p55_relikd', 'p55_wiki', L.P55_GHOST),
]
real = {}
for page, k1, k2, box in pairs:
    A = L.loadY(L.PATHS[k1]); B = L.loadY(L.PATHS[k2])
    if A.shape != B.shape:
        real[f'{k1}__vs__{k2}'] = {'error': f'shape mismatch {A.shape} vs {B.shape}'}
        continue
    st = L.t1_stats(A, B, box)
    # where is the max diff?
    d = np.abs(A - B)
    my, mx = np.unravel_index(np.argmax(d), d.shape)
    st['argmax_diff_yx'] = [int(my), int(mx)]
    st['mean_abs_diff'] = round(float(d.mean()), 4)
    real[f'{k1}__vs__{k2}'] = st
    # save diff heatmap crop of tree region
    L.save_png(L.crop(d, box), os.path.join(HERE, 'crops', f'diff_{k1}_vs_{k2}_tree.png'))
    print(f'{k1} vs {k2}:', st)
out['real_pairs'] = real
out['byte_identity'] = {
    'p32': 'relikd == Hadyn ky2khlqdf7qdznac.onion/32.jpg == cijhho123 2014onion7/32.jpg == cijhho123 "liber primus images full"/49.jpg (sha256 c0f77818)',
    'p55': 'relikd == cijhho123 2014onion7/55.jpg == cijhho123 "liber primus images full"/72.jpg (sha256 a8019159); Hadyn mirror has no 55.jpg',
    'wiki': 'wiki 32.jpg/55.jpg differ in BYTES from relikd but decode to pixel-identical arrays (metadata-level re-save)',
}
json.dump(out, open(os.path.join(HERE, 'results', 'mirror_diff.json'), 'w'), indent=1)
print('T1 fired on any real pair:', any(v.get('T1_fired') for v in real.values()))
