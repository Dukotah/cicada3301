# R45-W1 Q1: order and scope of the printed word-length stream (PREREG s2 Q1).
# A_U order-inside-scope (LLR, MI; within-U shuffle null), B_U composition (G, SS; global null),
# C local-patch scan (max z over windows/scales; global null), D per-page/per-section max z.
# Plants: English 2,896-word windows intact / shuffled within scope; solved Cicada printed lengths.
import sys, os, json, math, random, time, collections
from multiprocessing import Pool
import w1lib as w

SCOPES = ['sentence', 'line', 'para', 'page', 'sect']
ALPHA = 0.01 / 25
ZA = w.z_for_alpha(ALPHA)
WS = [25, 50, 100, 200, 400]
HB = os.path.join(w.HERE, 'heartbeat_q1.txt')


def hb(msg):
    open(HB, 'a').write('%s %s\n' % (time.strftime('%H:%M:%S'), msg))


# ---------- model ----------
def build_model():
    seqs = []; second = {}
    for fn in w.CORPORA:
        c = w.load_corpus(fn)
        h = len(c) // 2
        seqs.append([w.cls(n) for n, s in c[:h]]); second[fn] = c[h:]
    return w.train_llr(seqs), second


def pair_moments(C, S):
    n = len(C); cnt = collections.Counter(C)
    s1 = sum(cnt[a] * cnt[b] * S[a][b] for a in cnt for b in cnt) - sum(cnt[a] * S[a][a] for a in cnt)
    s2 = sum(cnt[a] * cnt[b] * S[a][b] ** 2 for a in cnt for b in cnt) - sum(cnt[a] * S[a][a] ** 2 for a in cnt)
    mu = s1 / (n * (n - 1)); var = s2 / (n * (n - 1)) - mu * mu
    return mu, math.sqrt(var)


def scan_max(C, S, mu, sd):
    sc = [S[a][b] for a, b in zip(C, C[1:])]
    pre = [0.0]
    for v in sc: pre.append(pre[-1] + v)
    m = len(sc); best = -1e9
    for wdw in WS:
        if wdw > m: continue
        st = max(1, wdw // 2); den = sd * math.sqrt(wdw)
        for i in range(0, m - wdw + 1, st):
            z = (pre[i + wdw] - pre[i] - wdw * mu) / den
            if z > best: best = z
    return best


def unit_sums(C, S, lab):
    d = collections.defaultdict(float)
    for i in range(len(C) - 1):
        if lab[i] == lab[i + 1]: d[lab[i]] += S[C[i]][C[i + 1]]
    return d


def global_stats(R, C, labs, S, mu, sd):
    out = {'A_global_LLR': w.llr(C, S), 'A_global_MI': w.mi(C), 'C_scan': scan_max(C, S, mu, sd)}
    for u in SCOPES:
        out['B_%s_G' % u] = w.comp_G(C, labs[u]); out['B_%s_SS' % u] = w.comp_SS(R, labs[u])
    return out


def run_sample(args):
    """args: (name, Rraw, labs, ndraw, seed, want_units). Returns observed + null lists."""
    name, R, labs, ndraw, seed, units = args
    S = MODEL
    rng = random.Random(seed)
    C = [w.cls(x) for x in R]
    mu, sd = pair_moments(C, S)
    obs = global_stats(R, C, labs, S, mu, sd)
    nul = collections.defaultdict(list)
    idx = list(range(len(R)))
    for _ in range(ndraw):
        perm = idx[:]; rng.shuffle(perm)
        Rg = [R[i] for i in perm]; Cg = [C[i] for i in perm]
        for k, v in global_stats(Rg, Cg, labs, S, mu, sd).items(): nul[k].append(v)
    unit_null = {}
    for u in SCOPES:
        grp = w.groups(labs[u])
        obs['A_%s_LLR' % u] = w.llr(C, S); obs['A_%s_MI' % u] = w.mi(C)
        if u in units:
            unit_null[u] = collections.defaultdict(list)
            obs_units = unit_sums(C, S, labs[u])
        for _ in range(ndraw):
            M = w.shuffle_within(C, grp, rng)
            nul['A_%s_LLR' % u].append(w.llr(M, S)); nul['A_%s_MI' % u].append(w.mi(M))
            if u in units:
                us = unit_sums(M, S, labs[u])
                for k in obs_units: unit_null[u][k].append(us.get(k, 0.0))
        if u in units:
            obs['_units_%s' % u] = dict(obs_units)
    return dict(name=name, obs=obs, null=dict(nul), unit_null={u: {str(k): v for k, v in d.items()}
                                                              for u, d in unit_null.items()})


def init(model):
    global MODEL
    MODEL = model


def dmax(obs_units, unit_null):
    """per-unit z standardised on the draws; returns observed max z, list of max z per draw, per-unit z"""
    keys = list(unit_null)
    st = {}
    for k in keys:
        v = unit_null[k]; m = sum(v) / len(v); s = (sum((x - m) ** 2 for x in v) / len(v)) ** .5
        st[k] = (m, s)
    zs = {k: ((obs_units[k] - st[k][0]) / st[k][1] if st[k][1] > 1e-9 else 0.0) for k in keys}
    nd = len(unit_null[keys[0]])
    nullmax = []
    for j in range(nd):
        nullmax.append(max(((unit_null[k][j] - st[k][0]) / st[k][1]) for k in keys if st[k][1] > 1e-9))
    return max(zs[k] for k in keys if st[k][1] > 1e-9), nullmax, zs


if __name__ == '__main__':
    open(HB, 'w').write('start %s\n' % time.ctime())
    NREAL = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    NPL = int(sys.argv[2]) if len(sys.argv) > 2 else 150
    KPL = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    S, second = build_model(); hb('model built')
    runes, words = w.load_lp2()
    R = [x['len'] for x in words]
    KEYMAP = {'sentence': 'sent', 'line': 'line', 'para': 'para', 'page': 'page', 'sect': 'sect'}
    labs = {u: [x[KEYMAP[u]] for x in words] for u in SCOPES}
    n = len(R)
    master = random.Random(4545)
    tasks = []
    CH = 8
    for c in range(CH):
        tasks.append(('real', R, labs, NREAL // CH, 1000 + c, ['page', 'sect']))
    # solved Cicada reference (global only meaningful; units: give dummy labels = its own)
    r1, w1 = w.load_lp1(); rs, ws = w.load_lp2_solved()
    Rs = [x['len'] for x in w1] + [x['len'] for x in ws]
    labs_s = {u: [0] * len(Rs) for u in SCOPES}
    labs_s['page'] = [x['page'] for x in w1] + [1000 + x['page'] for x in ws]
    labs_s['sentence'] = [x['sent'] for x in w1] + [1000 + x['sent'] for x in ws]
    for c in range(CH):
        tasks.append(('solved', Rs, labs_s, 2000 // CH, 2000 + c, []))
    # plants
    plant_meta = []
    for fn, c2 in second.items():
        if len(c2) <= n + 10: continue  # too short for a 2,896-word plant window (book_of_the_law)
        for k in range(KPL):
            st = master.randrange(0, len(c2) - n)
            win = c2[st:st + n]
            E = [x[0] for x in win]
            lab_e = dict(labs); lab_e['sentence'] = [x[1] for x in win]
            for ptype in ['intact'] + SCOPES + ['global']:
                rr = random.Random(master.random())
                if ptype == 'intact': Ep = E[:]
                elif ptype == 'global': Ep = E[:]; rr.shuffle(Ep)
                else: Ep = w.shuffle_within(E, w.groups(lab_e[ptype]), rr)
                tasks.append(('plant|%s|%s|%d' % (ptype, fn, k), Ep, lab_e, NPL, int(master.random() * 1e9), []))
    hb('tasks %d' % len(tasks))
    res = []
    with Pool(8, initializer=init, initargs=(S,)) as pool:
        for i, r in enumerate(pool.imap_unordered(run_sample, tasks)):
            res.append(r)
            if i % 10 == 0: hb('done %d/%d' % (i + 1, len(tasks)))
    hb('all samples done')
    init(S)
    # ---- merge real ----
    def merge(name):
        rr = [x for x in res if x['name'] == name]
        obs = rr[0]['obs']; nul = collections.defaultdict(list); un = {}
        for x in rr:
            for k, v in x['null'].items(): nul[k] += v
            for u, d in x['unit_null'].items():
                un.setdefault(u, collections.defaultdict(list))
                for k, v in d.items(): un[u][k] += v
        return obs, nul, un
    out = {'alpha_per_test': ALPHA, 'z_alpha_normal': ZA, 'n_words': n, 'draws_real': NREAL}
    obs, nul, un = merge('real')
    tests = {}
    for k in sorted(nul):
        z, p, m, sd = w.zp(obs[k], nul[k])
        tests[k] = dict(obs=obs[k], null_mean=m, null_sd=sd, z=z, p=p, reject=p <= ALPHA)
    for u in ('page', 'sect'):
        ou = {str(k): v for k, v in obs['_units_%s' % u].items()}
        mx, nm, zs = dmax(ou, un[u])
        z, p, m, sd = w.zp(mx, nm)
        tests['D_%s_max' % u] = dict(obs=mx, null_mean=m, null_sd=sd, z=z, p=p, reject=p <= ALPHA,
                                     per_unit_z={k: round(v, 3) for k, v in zs.items()},
                                     null_q_alpha=sorted(nm)[int((1 - ALPHA) * len(nm)) - 1])
    out['real'] = tests
    scan_null = sorted(nul['C_scan']); scan_thr = scan_null[int((1 - ALPHA) * len(scan_null)) - 1]
    out['C_scan_threshold_empirical'] = scan_thr
    # solved reference
    obs_s, nul_s, _ = merge('solved')
    out['solved_reference'] = {k: dict(zip(['z', 'p', 'null_mean', 'null_sd'], w.zp(obs_s[k], nul_s[k])), obs=obs_s[k])
                               for k in ('A_global_LLR', 'A_global_MI', 'C_scan')}
    out['solved_reference']['n_words'] = len(Rs)
    # plants: power table (normal approx with per-plant null)
    pw = collections.defaultdict(lambda: collections.defaultdict(list))
    for x in res:
        if not x['name'].startswith('plant'): continue
        _, ptype, fn, k = x['name'].split('|')
        for key, v in x['null'].items():
            z, p, m, sd = w.zp(x['obs'][key], v)
            pw[ptype][key].append(z >= ZA)
    out['plant_power'] = {pt: {k: round(sum(v) / len(v), 3) for k, v in d.items()} for pt, d in pw.items()}
    out['plant_n_per_type'] = sum(len(c2) > n + 10 for c2 in second.values()) * KPL
    # ---- C patch plants and D unit plants, using the real empirical thresholds ----
    rng = random.Random(77)
    C_lp2 = [w.cls(x) for x in R]
    mu, sd = pair_moments(C_lp2, S)
    allE = [x[0] for c2 in second.values() for x in c2]
    patch = {}
    for wdw in WS:
        hit = 0; T = 40
        for t in range(T):
            bg = R[:]; rng.shuffle(bg)
            st = rng.randrange(0, len(allE) - wdw); pos = rng.randrange(0, n - wdw)
            bg[pos:pos + wdw] = allE[st:st + wdw]
            Cb = [w.cls(x) for x in bg]; m2, s2 = pair_moments(Cb, S)
            hit += scan_max(Cb, S, m2, s2) >= scan_thr
        patch[wdw] = hit / T
    out['C_patch_power'] = patch
    # D plants: one page / one section of intact English inside within-unit-shuffled LP2
    dpow = {}
    for u in ('page', 'sect'):
        grp = w.groups(labs[u]); thr = tests['D_%s_max' % u]['null_q_alpha']
        # stats per unit from real draws
        stt = {}
        for k, v in un[u].items():
            m_ = sum(v) / len(v); s_ = (sum((q - m_) ** 2 for q in v) / len(v)) ** .5; stt[k] = (m_, s_)
        hit = 0; T = 40
        for t in range(T):
            gi = rng.randrange(len(grp)); idxs = grp[gi]
            M = w.shuffle_within(C_lp2, grp, rng)
            st = rng.randrange(0, len(allE) - len(idxs))
            for j, i in enumerate(idxs): M[i] = w.cls(allE[st + j])
            us = unit_sums(M, S, labs[u])
            obs_u = us[labs[u][idxs[0]]]
            # standardise the planted unit by shuffling its own (English) content
            vals = [M[i] for i in idxs]; nv = []
            for _ in range(200):
                rng.shuffle(vals); nv.append(sum(S[a][b] for a, b in zip(vals, vals[1:])))
            m_ = sum(nv) / len(nv); s_ = (sum((q - m_) ** 2 for q in nv) / len(nv)) ** .5
            z = (obs_u - m_) / s_ if s_ > 1e-9 else 0
            # plant fires if its unit z exceeds the real-data max-z threshold (other units are null)
            hit += z >= thr
        dpow[u] = hit / T
    out['D_unit_plant_power'] = dpow
    out['D_unit_plant_note'] = 'planted unit standardised by shuffling its own content; fires if its z >= real max-z threshold'
    json.dump(out, open(os.path.join(w.HERE, 'q1_results.json'), 'w'), indent=1)
    hb('finished')
    print(json.dumps({k: v for k, v in out.items() if k != 'real'}, indent=1)[:4000])
    for k, v in tests.items(): print('%-16s obs=%.4f z=%+.2f p=%.4g %s' % (k, v['obs'], v['z'], v['p'], 'REJECT' if v['reject'] else ''))
