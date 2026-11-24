# R45-W1 Q2: the word-length multiset (PREREG s2 Q2): M1 LP2 vs solved Cicada, M2 LP2 vs English (leave-own-corpus-out
# window null), M3 geometric GOF (+ descriptive AIC), M4 fixed-period / keyed generator scan.
import sys, os, json, math, random, collections
import w1lib as w

ALPHA = 0.01 / 4
K9 = 9  # classes 1..8, 9+ for M1/M2
rng = random.Random(4502)


def c9(n): return min(n, K9) - 1


def counts(L, K=K9):
    c = [0] * K
    for x in L: c[c9(x) if K == K9 else min(x, K) - 1] += 1
    return c


def G2(a, b):
    n1, n2 = sum(a), sum(b); N = n1 + n2; G = 0.0
    for x, y in zip(a, b):
        t = x + y
        if x: G += x * math.log(x * N / (n1 * t))
        if y: G += y * math.log(y * N / (n2 * t))
    return 2 * G


def Gfit(c, q):
    n = sum(c)
    return 2 * sum(x * math.log(x / (n * p)) for x, p in zip(c, q) if x)


def dist_of(c):
    t = sum(c) + 0.5 * len(c)
    return [(x + 0.5) / t for x in c]


def perm_test(A, B, R):
    obs = G2(counts(A), counts(B)); P = A + B; n = len(A); ge = 0
    for _ in range(R):
        rng.shuffle(P)
        ge += G2(counts(P[:n]), counts(P[n:])) >= obs
    return obs, (ge + 1) / (R + 1)


def desc(L):
    n = len(L)
    return dict(n=n, mean=round(sum(L) / n, 4), p1=round(L.count(1) / n, 4), p2=round(L.count(2) / n, 4),
                p_ge8=round(sum(x >= 8 for x in L) / n, 4), max=max(L),
                hist={k: L.count(k) for k in range(1, max(L) + 1)})


# ---- period scan ----
def period_stat(L, Pmax=300):
    n = len(L); m = sum(L) / n; v = sum((x - m) ** 2 for x in L) / n; T = sum(L)
    best = -1e9; bestP = None
    for P in range(2, Pmax + 1):
        ss = 0.0
        for ph in range(P):
            s = L[ph::P]; ss += sum(s) ** 2 / len(s)
        ss -= T * T / n
        z = (ss / v - (P - 1)) / math.sqrt(2 * (P - 1))
        if z > best: best, bestP = z, P
    return best, bestP


if __name__ == '__main__':
    NR = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    NP = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    out = {'alpha_per_test': ALPHA}
    _, w2 = w.load_lp2(); L = [x['len'] for x in w2]; n = len(L)
    _, w1 = w.load_lp1(); _, ws = w.load_lp2_solved()
    Sv = [x['len'] for x in w1] + [x['len'] for x in ws]
    corp = {fn: [x[0] for x in w.load_corpus(fn)] for fn in w.CORPORA}
    out['describe'] = {'LP2': desc(L), 'solved_cicada': desc(Sv)}
    for fn, c in corp.items(): out['describe'][fn] = desc(c)
    _, wfull = w.load_lp2()
    bysect = collections.defaultdict(list); bypage = collections.defaultdict(list)
    for x in w2: bysect[x['sect']].append(x['len']); bypage[x['page']].append(x['len'])
    out['describe_per_section'] = {str(k): desc(v) for k, v in bysect.items()}
    out['describe_per_page_mean'] = {str(k): round(sum(v) / len(v), 3) for k, v in bypage.items()}
    # ---- M1 ----
    obs, p = perm_test(L, Sv, NR)
    out['M1_LP2_vs_solved'] = dict(G=obs, p=p, reject=p <= ALPHA)
    # M1 control: English(X, 2896) vs English(Y, 739); size X==Y disjoint, power X!=Y
    ctl = {'same_corpus': [], 'diff_corpus': []}
    names = [f for f in corp if len(corp[f]) > 4000]
    for t in range(60):
        X = rng.choice(names); Y = X if t % 2 == 0 else rng.choice([f for f in names if f != X])
        cx = corp[X]; cy = corp[Y]
        a = rng.randrange(0, len(cx) - n); A = cx[a:a + n]
        while True:
            b = rng.randrange(0, len(cy) - 739)
            if X != Y or b + 739 <= a or b >= a + n: break
        B = cy[b:b + 739]
        _, pp = perm_test(A, B, 400)
        ctl['same_corpus' if X == Y else 'diff_corpus'].append(pp <= max(ALPHA, 1 / 401))
    out['M1_control'] = {k: dict(n=len(v), reject_rate=round(sum(v) / len(v), 3)) for k, v in ctl.items()}
    # Cicada solved vs each English corpus (descriptive G and perm p)
    out['solved_vs_corpora'] = {}
    for fn, c in corp.items():
        st = rng.randrange(0, len(c) - n) if len(c) > n else 0
        g, pp = perm_test(Sv, c[st:st + n], 1000)
        out['solved_vs_corpora'][fn] = dict(G=round(g, 2), p=pp)
    # ---- M2 ----
    Q = {fn: dist_of(counts(c)) for fn, c in corp.items()}
    def mind(sample, exclude=None):
        cc = counts(sample)
        d = {fn: Gfit(cc, q) for fn, q in Q.items() if fn != exclude}
        k = min(d, key=d.get); return d[k], k, d
    dl, kl, dall = mind(L)
    nulld = []
    for fn, c in corp.items():
        if len(c) < n + 10: continue
        for t in range(60):
            a = rng.randrange(0, len(c) - n); nulld.append(mind(c[a:a + n], exclude=fn)[0])
    p2 = (sum(v >= dl for v in nulld) + 1) / (len(nulld) + 1)
    out['M2_LP2_vs_english'] = dict(min_G=dl, nearest=kl, all_G={k: round(v, 2) for k, v in dall.items()},
                                    english_window_null=dict(n=len(nulld), median=sorted(nulld)[len(nulld) // 2],
                                                             q99=sorted(nulld)[int(.99 * len(nulld))], max=max(nulld)),
                                    p=p2, reject=p2 <= ALPHA)
    out['M2_solved_cicada_minG_scaled_note'] = 'solved Cicada (739 words) min G vs English computed for reference'
    out['M2_solved_cicada'] = dict(min_G=mind(Sv)[0], nearest=mind(Sv)[1])
    # M2 power: English with a fraction d of spaces deleted (merge), geometric sample
    thr = sorted(nulld)[min(len(nulld) - 1, int((1 - ALPHA) * len(nulld)))]
    pw = {}
    for dd in (0.05, 0.1, 0.2):
        hits = 0
        for t in range(40):
            fn = rng.choice([f for f in names if len(corp[f]) > 2 * n + 10]); c = corp[fn]; a = rng.randrange(0, len(c) - 2 * n)
            M = []; cur = 0
            for x in c[a:]:
                cur += x
                if rng.random() >= dd: M.append(cur); cur = 0
                if len(M) == n: break
            hits += mind(M, exclude=fn)[0] > thr
        pw['merge_%.2f' % dd] = hits / 40
    out['M2_power'] = pw; out['M2_threshold_G'] = thr
    # ---- M3 geometric ----
    mean = sum(L) / n; pg = 1 / mean
    Kmax = 15
    def geo_q(p): return [p * (1 - p) ** (k - 1) for k in range(1, Kmax)] + [(1 - p) ** (Kmax - 1)]
    def cK(S):
        c = [0] * Kmax
        for x in S: c[min(x, Kmax) - 1] += 1
        return c
    g_obs = Gfit(cK(L), geo_q(pg))
    gn = []
    for _ in range(2000):
        S = []
        for _ in range(n):
            k = 1
            while rng.random() > pg: k += 1
            S.append(k)
        gn.append(Gfit(cK(S), geo_q(1 / (sum(S) / n))))
    p3 = (sum(v >= g_obs for v in gn) + 1) / (len(gn) + 1)
    # power: English windows tested as geometric
    thr3 = sorted(gn)[int((1 - ALPHA) * len(gn))]
    hits = 0
    for t in range(40):
        fn = rng.choice(names); c = corp[fn]; a = rng.randrange(0, len(c) - n); S = c[a:a + n]
        hits += Gfit(cK(S), geo_q(n / sum(S))) > thr3
    # descriptive log-likelihoods
    def ll(q, cc): return sum(x * math.log(max(p, 1e-12)) for x, p in zip(cc, q))
    cc = cK(L)
    lam = mean - 1
    pois = [math.exp(-lam) * lam ** (k - 1) / math.factorial(k - 1) for k in range(1, Kmax)]; pois.append(1 - sum(pois))
    mx = max(L); unif = [1 / mx if k <= mx else 1e-12 for k in range(1, Kmax + 1)]
    allE = [x for c in corp.values() for x in c]; eng = dist_of(cK(allE)) if False else None
    ce = cK(allE); te = sum(ce) + 0.5 * Kmax; eng = [(x + 0.5) / te for x in ce]
    cs = cK(Sv); ts = sum(cs) + 0.5 * Kmax; sol = [(x + 0.5) / ts for x in cs]
    out['M3_geometric'] = dict(p_hat=pg, G=g_obs, p=p3, reject=p3 <= ALPHA, power_vs_english=hits / 40,
                               loglik={'geometric(1 par)': ll(geo_q(pg), cc), 'shifted_poisson(1 par)': ll(pois, cc),
                                       'uniform_1..max': ll(unif, cc), 'english_pooled(0 par)': ll(eng, cc),
                                       'solved_cicada(0 par)': ll(sol, cc)})
    # ---- M4 period scan ----
    obs4, P4 = period_stat(L)
    nul4 = []
    M = L[:]
    for _ in range(NP):
        rng.shuffle(M); nul4.append(period_stat(M)[0])
    p4 = (sum(v >= obs4 for v in nul4) + 1) / (NP + 1)
    thr4 = sorted(nul4)[int((1 - ALPHA) * NP) - 1]
    pw4 = {}
    for P in (13, 29, 97):
        for f in (0.1, 0.2, 0.3):
            hits = 0
            for t in range(20):
                K = [rng.choice(L) for _ in range(P)]
                S = [K[i % P] if rng.random() < f else rng.choice(L) for i in range(n)]
                hits += period_stat(S)[0] >= thr4
            pw4['P%d_f%.1f' % (P, f)] = hits / 20
    out['M4_period'] = dict(max_z=obs4, at_P=P4, p=p4, reject=p4 <= ALPHA, null_draws=NP, threshold=thr4, power=pw4)
    json.dump(out, open(os.path.join(w.HERE, 'q2_results.json'), 'w'), indent=1)
    for k in ('M1_LP2_vs_solved', 'M1_control', 'M2_LP2_vs_english', 'M2_power', 'M2_solved_cicada', 'M3_geometric', 'M4_period'):
        print(k, json.dumps(out[k])[:900])
    print('LP2', out['describe']['LP2']); print('solved', out['describe']['solved_cicada'])
    for fn in corp: print(fn, {k: v for k, v in out['describe'][fn].items() if k != 'hist'})
