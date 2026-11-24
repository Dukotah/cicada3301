# R45-W1 Q3 (leakage) and Q4 (rune order). PREREG s2 Q3/Q4.
# L1: position-class x rune G (start/interior/end/single), circular-shift null of the boundary pattern.
# L2: doublet rate across printed word boundaries minus within words, same null.  Estimates q (non-filter-adjacent
#     fraction) at word/line/page breaks.  R1: lag-k equality.  R2: OTP blindness demonstration.
import sys, os, json, math, random, collections
import w1lib as w

ALPHA = 0.01 / 2
ZA = w.z_for_alpha(ALPHA)
rng = random.Random(4503)


def classes_from_breaks(brk):
    """brk[i] True if a word boundary precedes rune i (brk[0] True). Returns class per rune 0=start 1=interior 2=end 3=single"""
    N = len(brk); out = [0] * N
    for i in range(N):
        s = brk[i]; e = (i == N - 1) or brk[i + 1]
        out[i] = 3 if (s and e) else 0 if s else 2 if e else 1
    return out


def G_tab(cl, v):
    tab = collections.Counter(zip(cl, v))
    rc = collections.Counter(cl); cc = collections.Counter(v); N = len(v)
    return 2 * sum(c * math.log(c * N / (rc[a] * cc[b])) for (a, b), c in tab.items())


def L1(v, brk, R, seed=None):
    r = random.Random(seed) if seed is not None else rng
    cl = classes_from_breaks(brk); N = len(v)
    obs = G_tab(cl, v); nul = []
    for _ in range(R):
        k = r.randrange(50, N - 50)
        nul.append(G_tab(cl[k:] + cl[:k], v))
    return obs, nul


def dbl_stat(d, brk):
    # d[i] = doublet between i-1 and i (i>=1); brk[i] = boundary between i-1 and i
    xc = xi = nc = ni = 0
    for i in range(1, len(d)):
        if brk[i]: nc += 1; xc += d[i]
        else: ni += 1; xi += d[i]
    return xc / nc - xi / ni, xc, nc, xi, ni


def L2(d, brk, R, seed=None):
    r = random.Random(seed) if seed is not None else rng
    obs = dbl_stat(d, brk); N = len(d); nul = []
    b = brk[1:]
    for _ in range(R):
        k = r.randrange(50, N - 50)
        bb = [True] + b[k:] + b[:k]
        nul.append(dbl_stat(d, bb)[0])
    return obs, nul


def wilson(x, n, z=1.96):
    if n == 0: return (0, 1)
    p = x / n; den = 1 + z * z / n; c = p + z * z / (2 * n); h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / den, (c + h) / den)


def english_runes(n_runes, seed):
    r = random.Random(seed)
    fn = r.choice(['pride.txt', 'moby.txt', 'war.txt', 'keys/king_in_yellow.txt', 'keys/mabinogion.txt'])
    t = w.clean_text(open(os.path.join(w.DATA, fn), encoding='utf8', errors='ignore').read())
    ws = [w.to_runes(x.replace("'", "")) for x in w.WORD_RE.findall(t)]
    ws = [x for x in ws if x]
    a = r.randrange(0, len(ws) - n_runes)
    v = []; brk = []
    for x in ws[a:]:
        for j, y in enumerate(x):
            v.append(y); brk.append(j == 0)
        if len(v) >= n_runes: break
    return v[:n_runes], brk[:n_runes], ws


def otp_filter(p, r):
    c = []
    for i, x in enumerate(p):
        while True:
            y = (x + r.randrange(29)) % 29
            if not c or y != c[-1]: break
        c.append(y)
    return c


if __name__ == '__main__':
    NR = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    NPL = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    out = {'alpha_per_test': ALPHA}
    runes, words = w.load_lp2()
    v = [x['v'] for x in runes]; brk = [True] + [x['brk_before'] for x in runes[1:]]; N = len(v)
    # ---- L1 real ----
    obs, nul = L1(v, brk, NR, 11)
    z, p, m, sd = w.zp(obs, nul)
    out['L1_real'] = dict(G=obs, null_mean=m, null_sd=sd, z=z, p=p, reject=p <= ALPHA)
    # descriptive: per-class rune distribution deviations (top cells)
    cl = classes_from_breaks(brk); tab = collections.Counter(zip(cl, v)); rc = collections.Counter(cl); cc = collections.Counter(v)
    cells = sorted(((tab[(a, b)] - rc[a] * cc[b] / N) / math.sqrt(rc[a] * cc[b] / N), a, b) for a in range(4) for b in range(29))
    out['L1_real_top_cells'] = [dict(z=round(c[0], 2), cls=['start', 'interior', 'end', 'single'][c[1]], rune=w.TR[c[2]]) for c in cells[:3] + cells[-3:]]
    out['L1_class_counts'] = {['start', 'interior', 'end', 'single'][k]: c for k, c in rc.items()}
    # ---- L1 LP1 reference (solved, real ciphertext) ----
    r1, w1_ = w.load_lp1()
    v1 = [x['v'] for x in r1]; b1 = [True] + [x['brk_before'] for x in r1[1:]]
    o1, n1 = L1(v1, b1, 2000, 12)
    z1, p1, _, _ = w.zp(o1, n1)
    out['L1_LP1_reference'] = dict(G=o1, z=z1, p=p1, n_runes=len(v1))
    # ---- L1 plants ----
    def plant_power(make, T, label):
        hits = 0; zs = []
        for t in range(T):
            vv, bb = make(t)
            o, nn = L1(vv, bb, NPL, 1000 + t)
            zz = w.zp(o, nn)[0]; zs.append(zz); hits += zz >= ZA
        return dict(power=hits / T, median_z=sorted(zs)[len(zs) // 2], n=T)
    pw = {}
    bpos = [i for i in range(1, N) if brk[i]]
    for q in (0.05, 0.1, 0.2, 0.3):
        def make(t, q=q):
            r = random.Random(5000 + t + int(q * 1000)); Sset = set(r.sample(range(29), 4))
            bb = brk[:]
            for i in bpos:
                if r.random() < q:
                    cands = [j for d in (0, 1, -1, 2, -2, 3, -3) for j in [i + d] if 1 <= j < N and v[j - 1] in Sset]
                    if cands and (cands[0] == i or not bb[cands[0]]):
                        bb[i] = False; bb[cands[0]] = True
            return v, bb
        pw['keyed_rewire_q%.2f' % q] = plant_power(make, 30, 'rewire')
    def make_vig(t):
        r = random.Random(6000 + t); p, bb, _ = english_runes(N, 6000 + t); key = [r.randrange(29) for _ in range(8)]
        return [(x + key[i % 8]) % 29 for i, x in enumerate(p)], bb
    pw['english_true_spaces_vigenere8'] = plant_power(make_vig, 20, 'vig')
    def make_otp(t):
        r = random.Random(7000 + t); p, bb, _ = english_runes(N, 7000 + t)
        return otp_filter(p, r), bb
    pw['english_true_spaces_OTP_filter'] = plant_power(make_otp, 20, 'otp')
    def make_rk(t):
        p, bb, ws = english_runes(N, 8000 + t); k, _, _ = english_runes(N, 9000 + t)
        return [(x + y) % 29 for x, y in zip(p, k)], bb
    pw['english_true_spaces_running_key_english'] = plant_power(make_rk, 20, 'rk')
    out['L1_plants'] = pw
    # ---- L2 real ----
    d = [False] + [v[i] == v[i - 1] for i in range(1, N)]
    (diff, xc, nc, xi, ni), nul2 = L2(d, brk, NR, 13)
    z2, p2two, m2, sd2 = w.zp(abs(diff), [abs(x) for x in nul2])
    out['L2_real'] = dict(rate_cross=xc / nc, n_cross=nc, dbl_cross=xc, rate_in=xi / ni, n_in=ni, dbl_in=xi, diff=diff,
                          p_two_sided=p2two, z_abs=z2, reject=p2two <= ALPHA)
    # L2 plants: fraction q of cross-boundary adjacencies non-filter-adjacent (doublet prob 1/29)
    pw2 = {}
    for q in (0.05, 0.1, 0.2, 0.3, 0.5):
        hits = 0
        for t in range(40):
            r = random.Random(9500 + t + int(q * 1000))
            dd = d[:]
            for i in range(1, N):
                if brk[i] and r.random() < q: dd[i] = r.random() < 1 / 29
            (df, *_), nn = L2(dd, brk, NPL, 9900 + t)
            hits += w.zp(abs(df), [abs(x) for x in nn])[0] >= ZA
        pw2['q%.2f' % q] = hits / 40
    out['L2_plants'] = pw2
    # ---- Q4 R1: q estimates at word/line/page breaks ----
    r_in = xi / ni
    def qest(x, n):
        lo, hi = wilson(x, n); base = r_in; full = 1 / 29
        f = lambda r: max(0.0, (r - base) / (full - base))
        return dict(doublets=x, pairs=n, rate=x / n, q_hat=f(x / n), q_upper95=min(1.0, f(hi)))
    lb = [x['line_before'] for x in runes]; pb = [x['page_before'] for x in runes]
    est = {'word_break': qest(xc, nc)}
    for name, flag in (('line_break', lb), ('page_break', pb)):
        x = sum(d[i] for i in range(1, N) if flag[i]); n = sum(1 for i in range(1, N) if flag[i])
        est[name] = qest(x, n)
    x = sum(d[1:]); est['all_pairs_vs_zero_residual'] = dict(doublets=x, pairs=N - 1,
                                                            q_upper95=min(1, wilson(x, N - 1)[1] * 29))
    est['note'] = 'q = fraction of printed adjacencies that were NOT adjacent when the doublet filter ran; baseline = within-word residual rate %.4f' % r_in
    out['R1_q_estimates'] = est
    out['R1_lag_equality'] = {k: dict(eq=sum(v[i] == v[i - k] for i in range(k, N)), expected_uniform=round((N - k) / 29, 1))
                              for k in range(1, 11)}
    # ---- R2: OTP blindness demo: English vs word-shuffled English, both OTP+filter ----
    demo = {}
    for lab, shuf in (('ordered', False), ('word_shuffled', True)):
        r = random.Random(4242)
        _, _, ws = english_runes(N, 4242)
        a = r.randrange(0, len(ws) - 4000); seg = ws[a:a + 4000]
        if shuf: r.shuffle(seg)
        p = [y for x in seg for y in x][:N]
        c = otp_filter(p, random.Random(1))
        ic = sum(k * (k - 1) for k in collections.Counter(c).values()) / (N * (N - 1)) * 29
        demo[lab] = dict(plaintext_lag1_eq=sum(p[i] == p[i - 1] for i in range(1, N)),
                         cipher_lag_eq={k: sum(c[i] == c[i - k] for i in range(k, N)) for k in range(1, 6)},
                         cipher_ioc_x29=round(ic, 4))
    out['R2_otp_demo'] = demo
    json.dump(out, open(os.path.join(w.HERE, 'q3q4_results.json'), 'w'), indent=1)
    print(json.dumps(out, indent=1)[:6000])
