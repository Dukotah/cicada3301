import os, sys, json, time, math
os.environ['D2'] = '1'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'round38', 'I1-glyph-recognizer'))
import numpy as np
import recognizer as R
u8 = R.u8; PR = u8.PR; VAR = 'V2_idx_rel_29'
P0 = R.M.parse(max_page=0); W0 = P0['words']; L0 = P0['w_line']

def shuf(words, lines, mode, r):
    groups = {}
    for wi, w in enumerate(words):
        key = ('w', wi) if mode == 'B' else ('l', lines[wi])
        for ri, x in enumerate(w):
            if x != 0: groups.setdefault(key, []).append((wi, ri))
    out = [list(w) for w in words]
    for key, slots in groups.items():
        vals = [words[a][b] for a, b in slots]; p = r.permutation(len(vals))
        for (a, b), k in zip(slots, p): out[a][b] = vals[k]
    return out

def nullset(words, lines, mode, n, r):
    return np.array([R.score(u8.walk(shuf(words, lines, mode, r), VAR), VAR)[0] for _ in range(n)])

def clean(r):
    n = len(W0); s = int(r.integers(n)); need = int(r.integers(60, 141)); ws = []; ls = []; acc = 0; i = s
    while acc < need:
        ws.append(W0[i % n]); ls.append(L0[i % n] + (i // n) * 1000); acc += len(W0[i % n]); i += 1
    for j in range(20):
        ws.append(W0[(i + j) % n]); ls.append(L0[(i + j) % n] + ((i + j) // n) * 1000)
    return ws, ls

def v2idx(headings, h0=0.0):
    out = []; h = h0; step = 360 / 29
    for t in headings:
        need = ((t - h + 180) % 360) - 180; k = int(round(need / step)) % 29
        if k == 0: k = 1 if need >= 0 else 28
        h += k * step; out.append(k)
    return out

def glyph(g, r):
    ch = int(r.integers(0, 2)); rot = int(r.integers(0, 4)) * 90.0
    if g == 'gon29': return [1 if ch == 0 else 28] * (29 * int(r.integers(1, 3)))
    if g == 'oct':
        sc = int(r.integers(1, 4)); return v2idx([(k + 1) * 45.0 * (1 if ch == 0 else -1) for k in range(8 * sc)])
    if g == 'gon12':
        sc = int(r.integers(1, 3)); return v2idx([(k + 1) * 30.0 * (1 if ch == 0 else -1) for k in range(12 * sc)])
    sc = float(r.choice([1, 1.5, 2, 2.5])); n = lambda a: max(1, int(round(a * sc)))
    hd = [0.0] * n(12) + [180.0] * n(6) + [270.0] * n(12) if g == 'T' else [270.0] * n(12) + [0.0] * n(9)
    return v2idx([x + rot for x in hd], h0=0.0)

def planted(g, r, own_line=False):
    ws, ls = clean(r)
    blk = glyph(g, r); pos = int(r.integers(max(2, len(ws) // 3), len(ws) // 2))
    ln = ls[pos - 1]
    ins_l = (-1) if own_line else ln
    ws2 = ws[:pos] + [[0]] + [blk] + [[0]] + ws[pos:]; ls2 = ls[:pos] + [ln, ins_l, ln] + ls[pos:]
    return ws2, ls2

def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = p + z*z/(2*n); a = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return [round((c-a)/d, 3), round((c+a)/d, 3)]

def run_variant(mode, ntr=40, nn=200, nfp=50, own=False):
    r = np.random.default_rng(39001 + (1 if mode == 'B' else 0)); t0 = time.time(); out = {'mode': mode, 'glyphs': {}}
    leaks = []; planted_p5 = []
    for g in R.GLYPHS:
        det = 0; rows = []
        for t in range(ntr):
            ws, ls = planted(g, r, own)
            s, tg = R.score(u8.walk(ws, VAR), VAR); ns = nullset(ws, ls, mode, nn, r); thr = float(np.quantile(ns, .05)); ok = bool(s < thr)
            det += ok; lk = float((ns <= s).mean()); leaks.append(lk); planted_p5.append(thr)
            rows.append(dict(score=float(s), thr=thr, ok=ok, tmpl=tg, correct=tg == g, leak=lk, null_min=float(ns.min())))
        out['glyphs'][g] = dict(detected=det, n=ntr, rate=det/ntr, wilson=wilson(det, ntr), correct_template=sum(x['correct'] for x in rows if x['ok']),
                                mean_leak=float(np.mean([x['leak'] for x in rows])), trials=rows)
        print(mode, own, g, det, ntr, round(time.time()-t0), flush=True)
    if own:
        out['mean_leak'] = float(np.mean(leaks)); return out
    k = 0; cp5 = []; crow = []
    for t in range(nfp):
        ws, ls = clean(r); s, _ = R.score(u8.walk(ws, VAR), VAR); ns = nullset(ws, ls, mode, nn, r); thr = float(np.quantile(ns, .05))
        k += bool(s < thr); cp5.append(thr); crow.append(dict(score=float(s), thr=thr, hit=bool(s < thr)))
    out['fpr'] = dict(hits=k, n=nfp, rate=k/nfp, wilson=wilson(k, nfp), rows=crow)
    out['mean_leak'] = float(np.mean(leaks)); out['mean_null_p5_planted'] = float(np.mean(planted_p5)); out['mean_null_p5_clean'] = float(np.mean(cp5))
    out['leak_ok'] = bool(out['mean_leak'] <= 0.05)
    out['pass'] = bool(all(out['glyphs'][g]['rate'] >= .9 for g in R.GLYPHS) and out['fpr']['rate'] <= .05 and out['leak_ok'])
    out['seconds'] = round(time.time()-t0); print(mode, 'PASS' if out['pass'] else 'FAIL', out['fpr']['hits'], out['mean_leak'], flush=True)
    return out

if __name__ == '__main__':
    modes = sys.argv[1].split(',')
    res = {}
    for m in modes:
        res[m] = run_variant(m)
        json.dump(res, open(os.path.join(HERE, 'power_v2_%s.json' % sys.argv[1].replace(',', '_')), 'w'), indent=1)
    if 'own' in sys.argv[2:]:
        for m in modes: res[m + '_ownline_sensitivity'] = run_variant(m, ntr=20, nn=100, own=True)
    json.dump(res, open(os.path.join(HERE, 'power_v2_%s.json' % sys.argv[1].replace(',', '_')), 'w'), indent=1)
