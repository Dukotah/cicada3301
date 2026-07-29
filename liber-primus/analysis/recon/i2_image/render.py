"""NAIVE-OUTSIDER probe: plot LP2 unsolved runes (segments 0-54) as images.
No decryption. Just: does the raw rune stream show visual structure?
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')))
import numpy as np
from PIL import Image
from lp import gematria as gp

OUT = os.path.dirname(__file__)
txt = open(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'krisyotam_runes.txt')).read()
segs = txt.split('%')
unsolved = ''.join(segs[0:55])
idxs = np.array(gp.runes_to_indices(unsolved), dtype=np.int64)
N = gp.N  # 29
PRIMES = np.array(gp.PRIMES)
n = len(idxs)
print("unsolved runes:", n)

def save(arr, name, upscale=1):
    a = np.asarray(arr, dtype=np.float64)
    lo, hi = a.min(), a.max()
    if hi > lo:
        a = (a - lo) / (hi - lo)
    img = (a * 255).astype(np.uint8)
    im = Image.fromarray(img, mode='L')
    if upscale > 1:
        im = im.resize((im.width*upscale, im.height*upscale), Image.NEAREST)
    im.save(os.path.join(OUT, name))
    print("wrote", name, im.size)

# ---- Value mappings ----
mappings = {
    "index": idxs.astype(float),                      # 0..28
    "prime": PRIMES[idxs].astype(float),              # 2..109
    "binary": (idxs % 2).astype(float),               # parity
    "isF": (idxs == 0).astype(float),                 # interrupter/F mask
    "delta": np.concatenate([[0], np.diff(idxs)]) % N,# first difference
}

# ---- Widths to try ----
# divisors of n, plus 29, sqrt, and typical page line lengths (~34 from earlier)
divisors = [d for d in range(2, n) if n % d == 0]
widths = sorted(set(divisors + [29, 28, 34, 40, int(n**0.5), 55, 58]))
widths = [w for w in widths if 2 <= w <= 400]
print("widths:", widths)

for mname, mvals in mappings.items():
    for w in widths:
        rows = n // w
        if rows < 3:
            continue
        block = mvals[:rows*w].reshape(rows, w)
        up = 1
        if w <= 60: up = 4
        elif w <= 120: up = 2
        save(block, f"{mname}_w{w:03d}_r{rows}.png", upscale=up)

# ---- Line-length shape (structure of the poem layout) ----
lines = [l for l in unsolved.split('/')]
lens = np.array([len(gp.runes_to_indices(l)) for l in lines])
maxlen = int(lens.max()) if len(lens) else 1
shape = np.zeros((len(lens), maxlen), dtype=np.uint8)
for i, L in enumerate(lens):
    shape[i, :L] = 255
Image.fromarray(shape, mode='L').save(os.path.join(OUT, "linelength_shape.png"))
print("wrote linelength_shape.png", shape.shape, "line-len range", lens.min(), lens.max())

# ---- Run-length image of parity ----
parity = idxs % 2
runs = []
cur = parity[0]; cnt = 1
for p in parity[1:]:
    if p == cur: cnt += 1
    else: runs.append((cur, cnt)); cur = p; cnt = 1
runs.append((cur, cnt))
rl = np.array([c for _, c in runs])
print("run-length stats: n_runs", len(runs), "max_run", rl.max(), "mean", round(rl.mean(),2))

# stats: is the index distribution flat (OTP-like) or skewed?
import collections
cnt = collections.Counter(idxs.tolist())
freqs = np.array([cnt.get(i,0) for i in range(N)])
exp = n / N
chi2 = ((freqs - exp)**2 / exp).sum()
print("chi2 uniformity (df=28):", round(chi2,1), "expected~28 if uniform; >41.3 => non-uniform p<.05")
print("min/max rune freq:", freqs.min(), freqs.max(), "expected", round(exp,1))
