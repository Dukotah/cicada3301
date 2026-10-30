import sys, os, json, math, time, importlib.util
import numpy as np
U8DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'round37', 'C2-recognizer-index-readings', 'U8-geometry'))
spec = importlib.util.spec_from_file_location('u8', os.path.join(U8DIR, 'u8.py')); u8 = importlib.util.module_from_spec(spec); spec.loader.exec_module(u8)
PR = u8.PR; M = u8.M
W = dict(k=1.0, c=1.0, h=1.0, hu=1.0, tf=0.0)   # D1 weights
YY, XX = np.mgrid[0:64, 0:64].astype(np.float64)

def hu(a):
    m00 = a.sum()
    if m00 < 1e-9: return np.zeros(4)
    cx = (a * XX).sum() / m00; cy = (a * YY).sum() / m00
    def eta(p, q): return (a * (XX - cx) ** p * (YY - cy) ** q).sum() / m00 ** (1 + (p + q) / 2)
    n20, n02, n11, n30, n03, n21, n12 = eta(2,0), eta(0,2), eta(1,1), eta(3,0), eta(0,3), eta(2,1), eta(1,2)
    h = [n20 + n02, (n20 - n02) ** 2 + 4 * n11 ** 2, (n30 - 3 * n12) ** 2 + (3 * n21 - n03) ** 2, (n30 + n12) ** 2 + (n21 + n03) ** 2,
         (n30 - 3*n12)*(n30+n12)*((n30+n12)**2 - 3*(n21+n03)**2) + (3*n21 - n03)*(n21+n03)*(3*(n30+n12)**2 - (n21+n03)**2),
         (n20 - n02)*((n30+n12)**2 - (n21+n03)**2) + 4*n11*(n30+n12)*(n21+n03)]
    return np.array([math.log10(abs(x) + 1e-5) for x in h[:4]])  # first four Hu, floor 1e-5 (5/6 unstable on symmetric shapes; fixed pre-power-run)

def feats(c):
    hd = np.array([math.atan2(s[3]-s[1], s[2]-s[0]) for s in c]); ln = np.array([math.hypot(s[2]-s[0], s[3]-s[1]) for s in c])
    turn = (np.degrees(np.diff(hd)) + 180) % 360 - 180
    k = 1 + int((np.abs(turn) >= 20).sum())
    path = ln.sum(); clo = math.hypot(c[-1][2]-c[0][0], c[-1][3]-c[0][1]) / max(path, 1e-9)
    hist = np.bincount((np.round(turn / 15).astype(int)) % 24, minlength=24).astype(float); hist /= max(hist.sum(), 1)
    cum = np.concatenate([[0], np.cumsum(turn * np.pi / 180)]); s = np.concatenate([[0], np.cumsum(ln)[:-1]]) / max(path, 1e-9)
    tf = np.interp(np.linspace(0, 1, 32, endpoint=False), s, cum); tf = tf - tf.mean()
    return dict(k=k, c=clo, h=hist, hu=hu(u8.raster(c)), tf=tf)

def dist(f, g):
    return (W['k'] * abs(math.log(f['k'] / g['k'])) / 0.7 + W['c'] * abs(f['c'] - g['c']) / 0.3 + W['h'] * np.abs(f['h'] - g['h']).sum()
            + W['hu'] * np.abs(f['hu'] - g['hu']).mean() + (W['tf'] * np.abs(f['tf'] - g['tf']).mean() / 0.3 if W['tf'] else 0.0))

def oct_rune(ch): return [i for i in range(29) if PR[i] % 8 == (1 if ch == 0 else 7)][0]
def tri12(ch):
    import itertools
    for a, b, c in itertools.product(range(1, 29), repeat=3):
        if (PR[a] + PR[b] + PR[c]) % 12 == (1 if ch == 0 else 11): return [a, b, c]
HEADIDX = {0: 4, 1: 1, 2: 2, 3: 3}
def block(g, scale, chir, rot):
    if g == 'oct': return 'V1_prime_mod8_rel', [[oct_rune(chir)] * (8 * int(scale))]
    if g == 'gon29': return 'V2_idx_rel_29', [[1 if chir == 0 else 28] * (29 * int(scale))]
    if g in ('T', 'L'):
        E, N, Wd, S = [HEADIDX[(k + rot) % 4] for k in (0, 1, 2, 3)]
        r = lambda n: max(1, int(round(n * scale)))
        run = [E] * r(12) + [Wd] * r(6) + [S] * r(12) if g == 'T' else [S] * r(12) + [E] * r(9)
        return 'V3_idx_abs_card', [run]
    if g == 'gon12': return 'V4_wordsum_rel12', [tri12(chir)] * (12 * int(scale))
GLYPHS = ['oct', 'gon29', 'T', 'L', 'gon12']
def make_bank():
    B = []
    for g in GLYPHS:
        for sc in (1, 2, 3):
            for ch in (0, 1):
                var, blk = block(g, sc, ch if g not in ('T', 'L') else 0, ch)
                st = u8.strokes(u8.walk(blk, var))
                if not st or sum(len(s) for s in st) < 3: continue
                B.append((g, sc, ch, feats(sum(st, []))))
    return B
BANK = make_bank()

def cands(segs, var):
    st = u8.strokes(segs); ms = u8.MINSTEPS[var]
    c = [s for s in st if ms <= len(s) <= 80]
    c += [st[i] + st[i+1] for i in range(len(st)-1) if ms <= len(st[i]) + len(st[i+1]) <= 80 and len(st[i]) >= 2 and len(st[i+1]) >= 2]
    return c

def score(segs, var):
    best = (9e9, None)
    for c in cands(segs, var):
        f = feats(c)
        for (g, sc, ch, t) in BANK:
            d = dist(f, t)
            if d < best[0]: best = (d, g)
    return best

def null_scores(words, var, n, r):
    return np.array([score(u8.walk(u8.shuffled_words(words, var, r), var), var)[0] for _ in range(n)])

P0 = M.parse(max_page=0)['words']
def noise(r):
    n = len(P0); s = int(r.integers(n)); need = int(r.integers(60, 141)); pre = []; acc = 0; i = s
    while acc < need:
        w = P0[i % n]; pre.append(w); acc += len(w); i += 1
    return pre, [P0[(i + j) % n] for j in range(20)]
def trial_words(g, r, planted=True):
    pre, post = noise(r)
    if not planted: return pre + post
    sc = {'oct': int(r.integers(1, 4)), 'gon29': int(r.integers(1, 3)), 'T': float(r.choice([1, 1.5, 2, 2.5])), 'L': float(r.choice([1, 1.5, 2, 2.5])), 'gon12': int(r.integers(1, 3))}[g]
    ch = int(r.integers(0, 2)); rot = int(r.integers(0, 4))
    var, blk = block(g, sc, ch, rot)
    return pre + [[0]] + blk + [[0]] + post, var

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); a = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return [round((c-a)/d, 3), round((c+a)/d, 3)]

def power(tag, ntr=40, nnull=200):
    r = np.random.default_rng(3838); out = {'weights': dict(W), 'glyphs': {}}; t0 = time.time()
    for g in GLYPHS:
        det = 0; rows = []
        for t in range(ntr):
            words, var = trial_words(g, r)
            s, tg = score(u8.walk(words, var), var); ns = null_scores(words, var, nnull, r); thr = float(np.quantile(ns, 0.05))
            ok = bool(s < thr); det += ok; rows.append(dict(score=s, thr=thr, ok=ok, tmpl=tg, correct=tg == g))
        out['glyphs'][g] = dict(detected=det, n=ntr, rate=det/ntr, wilson=wilson(det, ntr), correct_template=sum(x['correct'] for x in rows if x['ok']), trials=rows)
        print(tag, g, det, ntr, round(time.time()-t0), flush=True)
    fp = 0; nfp = 0; per = {}
    for v in ['V1_prime_mod8_rel', 'V2_idx_rel_29', 'V3_idx_abs_card', 'V4_wordsum_rel12']:
        k = 0
        for t in range(50):
            words = trial_words(None, r, planted=False); s, _ = score(u8.walk(words, v), v)
            ns = null_scores(words, v, nnull, r); k += bool(s < np.quantile(ns, 0.05))
        per[v] = k; fp += k; nfp += 50
    out['fpr'] = dict(hits=fp, n=nfp, rate=fp/nfp, wilson=wilson(fp, nfp), per_variant=per)
    out['pass'] = bool(all(out['glyphs'][g]['rate'] >= 0.9 for g in GLYPHS) and out['fpr']['rate'] <= 0.05)
    out['seconds'] = round(time.time()-t0)
    json.dump(out, open(f'power_{tag}.json', 'w'), indent=1); print(tag, 'PASS' if out['pass'] else 'FAIL', out['fpr'], flush=True)
    return out

if __name__ == '__main__':
    if sys.argv[1] == 'quick':
        r = np.random.default_rng(1); t0 = time.time()
        for g in GLYPHS:
            words, var = trial_words(g, r); s, tg = score(u8.walk(words, var), var); print(g, s, tg)
        ns = null_scores(words, var, 20, r); print('null20', time.time()-t0, ns.min(), ns.mean())
    elif sys.argv[1] == 'power': power(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
