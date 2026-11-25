# R46-P1 lead (i): the 2-rune word deficit. PREREG.md section 3, tests T1-T4.
# Stage 1 builds every reference and control and writes lead_i_stage1.json BEFORE LP2 is compared.
# Stage 2 reads LP2 and writes lead_i_results.json.
import os, json, math, random, collections
import p1lib as P

N = 2896
S_LP2_PREREG = 0.155
rng = random.Random(46001)
OUT1 = os.path.join(P.HERE, 'lead_i_stage1.json')
OUT2 = os.path.join(P.HERE, 'lead_i_results.json')


def wins(L, n, k, r):
    return [P.window(L, n, r) for _ in range(k)]


def stage1():
    P.heartbeat('lead_i stage1 loading FE')
    fe_tok, dropped, group_of = {}, [], {}
    for g, lst in P.FE.items():
        for rel in lst:
            t = P.load_fe(rel)
            if len(t) < 3 * N:
                dropped.append([rel, len(t)]); continue
            fe_tok[rel] = t; group_of[rel] = g
    fe = {k: [x[1] for x in v] for k, v in fe_tok.items()}
    P.log('FE corpora kept %d, dropped %s' % (len(fe), dropped))
    names = list(fe)
    # T1 windows (n = 2896), 200 per corpus
    W = {k: [P.s2(x) for x in wins(fe[k], N, 200, rng)] for k in names}
    pooled = [v for k in names for v in W[k]]
    bar1 = P.pct(pooled, 0.01)
    kill_frac = sum(v <= S_LP2_PREREG for v in pooled) / len(pooled)
    # S1 leave-one-corpus-out size
    s1 = {}
    for k in names:
        others = [v for j in names if j != k for v in W[j]]
        b = P.pct(others, 0.01)
        s1[k] = sum(v <= b for v in W[k]) / len(W[k])
    s1_mean = sum(s1.values()) / len(s1)
    # PC2 thinning to 0.155, power at 0.01 bar
    def thin_q(L, target):
        p2 = P.s2(L)
        return 0.0 if p2 <= target else (p2 - target) / (p2 * (1 - target))
    pc2 = []
    thinned = {}
    for k in names:
        T = P.thin2(fe[k], thin_q(fe[k], S_LP2_PREREG), rng); thinned[k] = T
        pc2 += [P.s2(x) <= bar1 for x in wins(T, N, 50, rng)]
    pc2_power = sum(pc2) / len(pc2)
    # PC1 article deletion
    noart = {k: [x[1] for x in fe_tok[k] if x[0] not in P.ARTICLES] for k in names}
    pc1 = [P.s2(x) for k in names for x in wins(noart[k], N, 50, rng)]
    pc1_desc = dict(median=P.pct(pc1, .5), q01=P.pct(pc1, .01), q99=P.pct(pc1, .99),
                    frac_le_0155=sum(v <= S_LP2_PREREG for v in pc1) / len(pc1),
                    power_vs_bar1=sum(v <= bar1 for v in pc1) / len(pc1))
    P.log('T1 stage1: bar1=%.4f kill_frac(<=0.155)=%.4f S1 size=%.4f PC2 power=%.3f PC1 %s' %
          (bar1, kill_frac, s1_mean, pc2_power, pc1_desc))
    # T2 bars at part sizes (structure of LP2 only: word counts per part, not lengths)
    _, w2 = P.w.load_lp2()
    sect = [x['sect'] for x in w2]
    odd = sum(1 for s in sect if s % 2 == 1); even = N - odd
    sizes = {'H1': N // 2, 'H2': N - N // 2, 'S_odd': odd, 'S_even': even}
    t2 = {}
    for part, n in sizes.items():
        vals = [P.s2(x) for k in names for x in wins(fe[k], n, 60, rng)]
        b5 = P.pct(vals, 0.05)
        pw = [P.s2(x) <= b5 for k in names for x in wins(thinned[k], n, 20, rng)]
        t2[part] = dict(n=n, fe_vals=vals, bar05=b5, pc2_power=sum(pw) / len(pw))
    P.log('T2 stage1: ' + ', '.join('%s n=%d bar05=%.4f power=%.3f' % (p, d['n'], d['bar05'], d['pc2_power'])
                                   for p, d in t2.items()))
    # section heterogeneity plant
    P.heartbeat('lead_i stage1 section plant')
    order = []
    for s in sect:
        if s not in order: order.append(s)
    cum, first = 0, set()
    cnt = collections.Counter(sect)
    for s in order:
        if cum >= N // 2: break
        first.add(s); cum += cnt[s]
    het_hits = []
    for t in range(100):
        k = names[t % len(names)]
        L = P.window(fe[k], N, rng)
        target = int(round(S_LP2_PREREG * N)); c2 = sum(1 for x in L if x == 2)
        idx = [i for i, x in enumerate(L) if x == 2 and sect[i] in first]
        rng.shuffle(idx); drop = set(idx[:max(0, c2 - target)])
        Lp = [x for i, x in enumerate(L) if i not in drop]; sp = [s for i, s in enumerate(sect) if i not in drop]
        het_hits.append(sect_G_p(Lp, sp, 1000, rng) <= 0.01)
    het_power = sum(het_hits) / len(het_hits)
    P.log('T2 section heterogeneity plant power=%.3f (first-half sections %s)' % (het_power, sorted(first)))
    # T3 references
    P.heartbeat('lead_i stage1 T3 references')
    refs = {}
    refs['EN-FE'] = [fe[k] for k in names]
    refs['EN-noART'] = [noart[k] for k in names]
    r10, r20 = random.Random(4610), random.Random(4620)
    refs['EN-merge10'] = [P.merge(fe[k], 0.10, r10) for k in names]
    refs['EN-merge20'] = [P.merge(fe[k], 0.20, r20) for k in names]
    for code in ['LA', 'DE', 'CY', 'OE']:
        refs[code] = [[x[1] for x in c] for c in P.load_lang(code)]
    _, w1 = P.w.load_lp1(); _, wsol = P.w.load_lp2_solved()
    solved = [x['len'] for x in w1] + [x['len'] for x in wsol]
    ref_desc, qR, nullR, sampler = {}, {}, {}, {}
    for R, cs in refs.items():
        A = [x for c in cs for x in c[:len(c) // 2]]
        Bs = [c[len(c) // 2:] for c in cs]
        qR[R] = P.dist9(A)
        ok = [b for b in Bs if len(b) >= N]
        ref_desc[R] = dict(n_corpora=len(cs), words=sum(len(c) for c in cs), s2=P.s2([x for c in cs for x in c]),
                           mean_len=sum(x for c in cs for x in c) / sum(len(c) for c in cs),
                           second_halves_usable=len(ok))
        sampler[R] = (lambda ok: (lambda r, i: P.window(ok[i % len(ok)], N, r)))(ok)
    qR['SOLVED'] = P.dist9(solved)
    ref_desc['SOLVED'] = dict(n_corpora=1, words=len(solved), s2=P.s2(solved), mean_len=sum(solved) / len(solved))
    def solved_draw(r, i):
        res = [solved[r.randrange(len(solved))] for _ in range(len(solved))]
        return [res[r.randrange(len(res))] for _ in range(N)]
    sampler['SOLVED'] = solved_draw
    R_names = list(qR)
    for R in R_names:
        nullR[R] = [P.G(sampler[R](rng, i), qR[R]) for i in range(300)]
    bar99 = {R: P.pct(nullR[R], 0.99) for R in R_names}
    conf = {}
    for R in R_names:
        ws = [sampler[R](rng, i) for i in range(100)]
        conf[R] = {R2: sum(P.G(x, qR[R2]) <= bar99[R2] for x in ws) / len(ws) for R2 in R_names}
        conf[R]['_s2_median'] = P.pct([P.s2(x) for x in ws], .5)
    P.log('T3 stage1 bars: ' + json.dumps({R: round(b, 1) for R, b in bar99.items()}))
    for R in R_names:
        P.log('  conf %-10s ' % R + ' '.join('%s=%.2f' % (R2, conf[R][R2]) for R2 in R_names))
    out = dict(fe_kept=names, fe_dropped=dropped, group_of=group_of, N=N,
               T1=dict(bar1=bar1, kill_frac_le_0155=kill_frac, S1_size_mean=s1_mean, S1_per_corpus=s1,
                       PC2_power=pc2_power, PC1_noART=pc1_desc,
                       windows={k: W[k] for k in names}),
               T2={p: {kk: vv for kk, vv in d.items()} for p, d in t2.items()},
               T2_sect_plant=dict(power=het_power, first_half_sections=sorted(first)),
               T3=dict(ref_desc=ref_desc, q=qR, bar99=bar99, confusion=conf),
               solved_len=solved)
    json.dump(out, open(OUT1, 'w'), indent=0)
    return out, fe


def sect_G_p(L, sect, R, r):
    def g(L):
        tab = collections.defaultdict(lambda: [0, 0])
        for x, s in zip(L, sect): tab[s][x == 2] += 1
        n = len(L); tot = [sum(v[0] for v in tab.values()), sum(v[1] for v in tab.values())]
        G = 0.0
        for v in tab.values():
            rs = v[0] + v[1]
            for j in (0, 1):
                if v[j]: G += v[j] * math.log(v[j] * n / (rs * tot[j]))
        return 2 * G
    obs = g(L); M = L[:]; ge = 0
    for _ in range(R):
        r.shuffle(M); ge += g(M) >= obs
    return (ge + 1) / (R + 1)


def stage2(st, fe):
    P.heartbeat('lead_i stage2 LP2')
    runes, w2 = P.w.load_lp2()
    L = [x['len'] for x in w2]; sect = [x['sect'] for x in w2]
    s = P.s2(L)
    names = st['fe_kept']; W = st['T1']['windows']
    pooled = [v for k in names for v in W[k]]
    p_fe = sum(v <= s for v in pooled) / len(pooled)
    by_group = {}
    for g in P.FE:
        vals = [v for k in names if st['group_of'][k] == g for v in W[k]]
        if vals: by_group[g] = dict(p=sum(v <= s for v in vals) / len(vals), min=min(vals), median=P.pct(vals, .5))
    per_corpus = {k: dict(min=min(W[k]), median=P.pct(W[k], .5), p=sum(v <= s for v in W[k]) / len(W[k])) for k in names}
    t1_inf = st['T1']['S1_size_mean'] <= 0.03 and st['T1']['PC2_power'] >= 0.8
    T1 = dict(s_LP2=s, p_FE=p_fe, replicates=p_fe <= 0.01, informative=t1_inf, by_group=by_group, per_corpus=per_corpus,
              fe_pooled_min=min(pooled), fe_pooled_q01=st['T1']['bar1'], fe_pooled_median=P.pct(pooled, .5))
    P.log('T1 LP2: s=%.4f p_FE=%.4f replicates=%s informative=%s pooled min=%.4f' % (s, p_fe, p_fe <= 0.01, t1_inf, min(pooled)))
    # T2
    parts = {'H1': L[:N // 2], 'H2': L[N // 2:], 'S_odd': [x for x, q in zip(L, sect) if q % 2 == 1],
             'S_even': [x for x, q in zip(L, sect) if q % 2 == 0]}
    T2 = {}
    for p, Lp in parts.items():
        d = st['T2'][p]; sp = P.s2(Lp)
        pp = sum(v <= sp for v in d['fe_vals']) / len(d['fe_vals'])
        T2[p] = dict(n=len(Lp), s=sp, p=pp, pass_=pp <= 0.05, informative=d['pc2_power'] >= 0.8, pc2_power=d['pc2_power'])
    T2_rep = all(v['pass_'] for v in T2.values())
    per_sect = {str(k): dict(n=sum(1 for q in sect if q == k), s2=P.s2([x for x, q in zip(L, sect) if q == k]))
                for k in sorted(set(sect))}
    het_p = sect_G_p(L, sect, 10000, random.Random(46002))
    P.log('T2 LP2: ' + ', '.join('%s s=%.4f p=%.4f' % (p, v['s'], v['p']) for p, v in T2.items()) +
          ' replicate_all=%s; section G p=%.4f' % (T2_rep, het_p))
    # T3
    T3 = {}
    for R, q in st['T3']['q'].items():
        g = P.G(L, q); b = st['T3']['bar99'][R]
        T3[R] = dict(G=g, bar99=b, admitted=g <= b, diag_ok=st['T3']['confusion'][R][R] >= 0.95)
    P.log('T3 LP2: ' + ', '.join('%s G=%.1f/%.1f %s' % (R, v['G'], v['bar99'], 'ADMIT' if v['admitted'] else 'reject')
                                 for R, v in T3.items()))
    # T4 line-merge ceiling
    pieces = []; cur = 0; prev_wi = None
    for x in runes:
        if prev_wi is not None and x['wi'] == prev_wi and x['line_before'] and not x['brk_before']:
            pieces.append(cur); cur = 0
        if prev_wi is not None and x['wi'] != prev_wi:
            pieces.append(cur); cur = 0
        cur += 1; prev_wi = x['wi']
    pieces.append(cur)
    pieces = [p for p in pieces if p]
    # sanity: total runes preserved
    assert sum(pieces) == sum(L)
    n4 = len(pieces); smax = P.s2(pieces)
    r4 = random.Random(46004)
    v4 = [P.s2(P.window(fe[k], n4, r4)) for k in names for _ in range(60)]
    b4 = P.pct(v4, 0.01)
    T4 = dict(n_words_after_split=n4, s_max=smax, mean_len=sum(pieces) / n4, fe_q01=b4, fe_min=min(v4),
              p=sum(v <= smax for v in v4) / len(v4), ceiling_below_english=smax <= b4)
    P.log('T4 LP2: split n=%d s_max=%.4f fe_q01=%.4f p=%.4f' % (n4, smax, b4, T4['p']))
    out = dict(T1=T1, T2=dict(parts=T2, replicates_all=T2_rep, sections=per_sect, section_G_p=het_p,
                              section_heterogeneous=het_p <= 0.01, section_plant_power=st['T2_sect_plant']['power']),
               T3=T3, T4=T4, LP2_hist={k: L.count(k) for k in range(1, max(L) + 1)})
    json.dump(out, open(OUT2, 'w'), indent=1)
    return out


if __name__ == '__main__':
    st, fe = stage1()
    stage2(st, fe)
    P.heartbeat('lead_i done')
