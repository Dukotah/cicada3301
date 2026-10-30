import sys, os, json, re, time, random
import numpy as np
LP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(LP, 'src')); sys.path.insert(0, os.path.join(LP, 'analysis', 'round19', 'I2'))
sys.path.insert(0, os.path.join(LP, 'analysis', 'round10', 'L2-map'))
from lp import gematria as g
import adjudicate as A
import mapcommon as M
pan = A.Panel(os.path.join(LP, 'data', 'panels', 'panel-r36.npz'))
ne = pan.ne_idx
rng = np.random.default_rng(3301)


def pm(x):
    x = np.asarray(x, dtype=np.int64)
    if len(x) < 3:
        return -9.9
    mu, sd, _, _ = pan.cal(len(x)); z = (pan.raw(x) - mu) / sd
    return float(z[ne].max())


def pm_batch(X):
    X = np.asarray(X, dtype=np.int64); B, n = X.shape
    mu, sd, _, _ = pan.cal(n); out = np.empty(B)
    for s in range(0, B, 500):
        blk = X[s:s + 500]; f = blk[:, :-2] * 841 + blk[:, 1:-1] * 29 + blk[:, 2:]
        raw = pan.LMF[:, f].mean(axis=2, dtype=np.float64).T
        out[s:s + 500] = ((raw - mu) / sd)[:, ne].max(axis=1)
    return out


txt = open(os.path.join(LP, 'data', 'keys', 'armada18', 'cicada_koans_and_lp_sections.txt'), encoding='utf-8').read()
lp1_lines = []; lp1_words = []
for ln in txt.split('\n'):
    ws = [w for w in re.sub(r'[^A-Z ]', ' ', ln.upper()).split() if w]
    if not ws:
        continue
    ids = [g.keyword_to_indices(w) for w in ws]
    lp1_words += ids; lp1_lines.append([r for w in ids for r in w])
P = M.parse(max_page=54)
T = {'LP1': {'word': lp1_words, 'line': lp1_lines, 'flat': [r for w in lp1_words for r in w]},
     'UNS': {'word': P['words'], 'line': P['lines'], 'flat': [r for p in P['pages'] for r in p]}}
SIZES = {k: {u: len(v) for u, v in d.items()} for k, d in T.items()}

S1 = "1041279065891998535982789873959431895640" + "442510695567564373922695237268242385295908173" + "9834390370374475764863415203423499357108713631"
S2 = "1231507051321"
BLOCKS = "162667212858 414974253863 598852142735 876873892385 935691396441 316744223127 427566844663 644169769482 889296759263 963846244281".split()
LOC = "".join(BLOCKS)


def vals(name, scheme, rev):
    if name == 'LOCW':
        b = [x[::-1] if rev else x for x in BLOCKS]; return [int(x) for x in b]
    D = {'S1': S1, 'S2': S2, 'LOC': LOC}[name]
    if rev:
        D = D[::-1]
    k = {'pair': 2, 'triple': 3, 'single': 1}[scheme]
    return [int(D[i:i + k]) for i in range(0, len(D) - k + 1, k)]


def select(tgt, ro, vs, base):
    if ro == 'R':
        fl = T[tgt]['flat']; return [[fl[(v if base == 0 else v - 1) % len(fl)]] for v in vs]
    kind, mode = ro.split('-')
    U = T[tgt][kind]; out = []
    for v in vs:
        u = U[(v if base == 0 else v - 1) % len(U)]
        out.append(u[:1] if mode == 'F' else u)
    return out


def flatten(units):
    return [r for u in units for r in u]


VMAX = 99; BASE = 0   # set per selection: null draws index VALUES uniformly over the scheme's own alphabet


def _idx(size, shape):
    v = rng.integers(0, VMAX + 1, shape)
    return (v if BASE == 0 else v - 1) % size


def null_draw(tgt, ro, n, M_):
    if ro == 'R':
        fl = np.array(T[tgt]['flat']); return fl[_idx(len(fl), (M_, n))]
    kind, mode = ro.split('-'); U = T[tgt][kind]
    fi = np.array([u[0] if u else 0 for u in U]); return fi[_idx(len(U), (M_, n))]


def pvals(tgt, ro, units, M_b, M_a):
    real = pm(flatten(units)); n = len(units)
    if ro.endswith('-W'):
        U = T[tgt][ro.split('-')[0]]
        nb = np.empty(M_b)
        for i in range(M_b):
            idx = _idx(len(U), n); nb[i] = pm([r for j in idx for r in U[j]])
        na = np.empty(M_a)
        for i in range(M_a):
            na[i] = pm([r for j in rng.permutation(n) for r in units[j]])
    else:
        fl = np.array(flatten(units))
        if len(fl) >= 3:
            nb = pm_batch(null_draw(tgt, ro, n, M_b)); na = pm_batch(np.stack([rng.permutation(fl) for _ in range(M_a)]))
        else:
            nb = np.full(M_b, -9.9); na = np.full(M_a, -9.9)
    pb = (1 + (nb >= real).sum()) / (len(nb) + 1); pa = (1 + (na >= real).sum()) / (len(na) + 1)
    return real, pa, pb, float(nb.max()), float(np.quantile(nb, 0.999))


def run_sel(tgt, ro, vs, base, M_b=2000, M_a=2000, vmax=None):
    global VMAX, BASE
    VMAX = vmax if vmax is not None else max(vs); BASE = base
    units = select(tgt, ro, vs, base); real, pa, pb, nbmax, q999 = pvals(tgt, ro, units, M_b, M_a)
    return dict(n=len(flatten(units)), nunits=len(units), real=real, p_a=pa, p_b=pb, p_gate=max(pa, pb),
                null_max=nbmax, null_q999=q999, text=g.indices_to_translit(flatten(units))[:140])


def plant_digits(positions, w):
    return "".join(str(p).zfill(w) for p in positions)


def refine(tgt, ro, units, real):
    n = len(units)
    if ro.endswith('-W'):
        U = T[tgt]['word']; nb = np.empty(20000)
        for i in range(20000):
            idx = _idx(len(U), n); nb[i] = pm([x for j in idx for x in U[j]])
        pb = (1 + (nb >= real).sum()) / 20001
        na = np.array([pm([x for j in rng.permutation(n) for x in units[j]]) for _ in range(20000)])
        pa = (1 + (na >= real).sum()) / 20001
    else:
        flr = np.array(flatten(units)); tot = 0; pbs = 0; pas = 0
        for _ in range(25):
            pbs += (pm_batch(null_draw(tgt, ro, n, 4000)) >= real).sum(); tot += 4000
            pas += (pm_batch(np.stack([rng.permutation(flr) for _ in range(4000)])) >= real).sum()
        pb = (1 + pbs) / (tot + 1); pa = (1 + pas) / (tot + 1)
    return pa, pb


if __name__ == '__main__':
    t0 = time.time(); out = {'sizes': SIZES, 'controls': {}, 'selections': []}
    fl = T['LP1']['flat']
    ph = g.keyword_to_indices("ITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONE")[:60]
    rs = random.Random(7); pos = []
    for r in ph:
        c = [i for i in range(min(1000, len(fl))) if fl[i] == r]; pos.append(rs.choice(c))
    D = plant_digits(pos, 3); vs = [int(D[i:i + 3]) for i in range(0, len(D), 3)]
    out['controls']['A_digits'] = D
    out['controls']['A_LP1_R_triple'] = run_sel('LP1', 'R', vs, 0, vmax=999)
    out['controls']['A0_random_digits'] = run_sel('LP1', 'R', [int(x) for x in rng.integers(0, 1000, 60)], 0, vmax=999)
    sent = "THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED".split()
    wl = [g.keyword_to_indices(w) for w in sent]; W = T['LP1']['word']
    st = None
    for i in range(len(W) - len(wl)):
        if all(W[i + k] == wl[k] for k in range(len(wl))):
            st = i; break
    out['controls']['B_found_at'] = st
    if st is not None:
        out['controls']['B_LP1_W_triple'] = run_sel('LP1', 'word-W', list(range(st, st + len(wl))), 0, vmax=999)
        out['controls']['B0_random'] = run_sel('LP1', 'word-W', [int(x) for x in rng.integers(0, len(W), len(wl))], 0, vmax=999)
    UW = T['UNS']['word']
    ph2 = g.keyword_to_indices("WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGSITISNOT")[:60]
    pos = []
    for r in ph2:
        c = [i for i in range(len(UW)) if UW[i] and UW[i][0] == r]; pos.append(rs.choice(c))
    out['controls']['C_UNS_F_triple_indices_note'] = 'word indices up to %d (mod size; triple digits cover <1000 so plant uses mod-wrap-free positions <1000 only)' % len(UW)
    pos = [p for p in pos]
    # triple digits can only address <1000 -> restrict plant positions to <1000
    pos = []
    for r in ph2:
        c = [i for i in range(1000) if UW[i] and UW[i][0] == r]; pos.append(rs.choice(c))
    out['controls']['C_UNS_F_triple'] = run_sel('UNS', 'word-F', pos, 0, vmax=999)
    out['controls']['C0_random'] = run_sel('UNS', 'word-F', [int(x) for x in rng.integers(0, 1000, 60)], 0, vmax=999)
    for k, v in out['controls'].items():
        if isinstance(v, dict):
            print(k, v['n'], round(v['real'], 2), v['p_gate'], round(v['null_max'], 2), flush=True)
    ok = all(out['controls'][k]['p_gate'] <= 0.002 for k in ('A_LP1_R_triple', 'B_LP1_W_triple', 'C_UNS_F_triple')) and \
        all(out['controls'][k]['p_gate'] > 0.01 for k in ('A0_random_digits', 'B0_random', 'C0_random'))
    out['controls_pass'] = bool(ok); print('controls_pass', ok, time.time() - t0, flush=True)
    json.dump(out, open('results.json', 'w'), indent=1)
    specs = []
    for nm in ('S1', 'S2', 'LOC'):
        for sc in ('pair', 'triple', 'single'):
            for tgt in ('LP1', 'UNS'):
                for ro in ('R', 'word-F', 'line-F', 'word-W'):
                    for base in (0, 1):
                        for rev in (0, 1):
                            specs.append((nm, sc, tgt, ro, base, rev))
    for tgt in ('LP1', 'UNS'):
        for ro in ('R', 'word-F', 'line-F', 'word-W'):
            for base in (0, 1):
                for rev in (0, 1):
                    specs.append(('LOCW', 'whole', tgt, ro, base, rev))
    print('specs', len(specs), flush=True)
    for k, (nm, sc, tgt, ro, base, rev) in enumerate(specs):
        vs = vals(nm, sc, rev)
        r = run_sel(tgt, ro, vs, base, vmax={'pair':99,'triple':999,'single':9,'whole':10**12-1}[sc]); r.update(string=nm, scheme=sc, target=tgt, readout=ro, base=base, rev=rev)
        if r['p_gate'] <= 0.005 and r['n'] >= 3:
            pa, pb = refine(tgt, ro, select(tgt, ro, vs, base), r['real'])
            r.update(refined=True, p_a_ref=pa, p_b_ref=pb, p_gate=max(pa, pb))
        out['selections'].append(r)
        if k % 40 == 0:
            print(k, round(time.time() - t0), flush=True)
    out['N'] = len(specs); out['bar_fw'] = 0.01 / len(specs)
    out['flagged'] = [s for s in out['selections'] if s['p_gate'] <= out['bar_fw'] and s['n'] >= 3]
    json.dump(out, open('results.json', 'w'), indent=1)
    print('done', round(time.time() - t0), 'flagged', len(out['flagged']))
