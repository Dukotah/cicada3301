# R46-P1 lead (ii): line breaks inside words. PREREG.md section 3, tests U1-U3.
# Stage 1 = layout simulation plants (calibration, power, size) + LP1 real controls -> lead_ii_stage1.json.
# Stage 2 = LP2 parts -> lead_ii_results.json.
import os, json, math, random, bisect, collections
import p1lib as P

BRK = set('-.&$§0123456789')
PARA = set('&$§%')
rng = random.Random(46101)
OUT1 = os.path.join(P.HERE, 'lead_ii_stage1.json')
OUT2 = os.path.join(P.HERE, 'lead_ii_results.json')
SLACK = 6


def raw_lp2():
    t = open(os.path.join(P.w.DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    return P.w.split_at_rune(t, P.w.N_LP2)[0]


def raw_lp1():
    t = open(os.path.join(P.w.DATA, 'sources', 'rtkd_master.txt'), encoding='utf8').read()
    i = min(t.find(r) for r in P.w.RUNES if t.find(r) >= 0)
    i = t.rfind('\n', 0, i) + 1; t = t[i:]
    k = open(os.path.join(P.w.DATA, 'krisyotam_runes.txt'), encoding='utf8').read()
    kr = ''.join(c for c in k if c in P.w.IDX); tr = ''.join(c for c in t if c in P.w.IDX)
    n1 = tr.find(kr[:60])
    return P.w.split_at_rune(t, n1)[0]


def struct(text):
    """Return dict with gaps, lines, words for a transcription string."""
    runes = []  # (page, sect)
    gaps = []   # gap string between rune i and i+1
    page = sect = 0; buf = ''
    for ch in text:
        if ch in P.w.IDX:
            if runes: gaps.append(buf)
            runes.append((page, sect)); buf = ''
        else:
            buf += ch
            if ch == '%': page += 1
            if ch == '$': sect += 1
    # words
    wid = [0]
    for g in gaps: wid.append(wid[-1] + (1 if any(c in BRK for c in g) else 0))
    wlen = collections.Counter(wid)
    words = [wlen[i] for i in range(wid[-1] + 1)]
    # gap records
    G = []
    for i, g in enumerate(gaps):
        G.append(dict(i=i, page=runes[i][0], sect=runes[i][1], line='/' in g, inside=not any(c in BRK for c in g),
                      running='/' in g and not any(c in PARA for c in g), pagegap='%' in g))
    # lines: segments between gaps containing '/' or '%'
    lines = []; start = 0
    for gr in G:
        if gr['line'] or gr['pagegap']:
            lines.append(dict(n=gr['i'] + 1 - start, page=runes[start][0], sect=runes[start][1],
                              running=gr['running'], inside=gr['inside'], end_gap=gr['i']))
            start = gr['i'] + 1
    span = sorted(set(wid[gr['i']] for gr in G if gr['running'] and gr['inside']))
    span_len = [words[k] for k in span]
    return dict(runes=runes, G=G, words=words, wid=wid, lines=lines, span_len=span_len)


def summ(S, sel=lambda gr: True, lsel=lambda l: True):
    within = [gr for gr in S['G'] if not gr['pagegap'] and sel(gr)]
    c = sum(gr['inside'] for gr in within) / len(within)
    run = [gr for gr in S['G'] if gr['running'] and sel(gr)]
    n = len(run); nin = sum(gr['inside'] for gr in run)
    allb = [gr for gr in S['G'] if (gr['line'] or gr['pagegap']) and sel(gr)]
    x1 = sum(gr['inside'] for gr in allb) / len(allb)
    f = nin / n
    return dict(c=c, n_running=n, inside=nin, f_in=f, pi=1 - f / c, excess=[(0 if gr['inside'] else 1) - (1 - c) for gr in run],
                x1_all_breaks=len(allb), x1_f_in=x1)


def binom_sf(k, n, p):
    """P(X >= k)"""
    lp, lq = math.log(p), math.log(1 - p)
    tot = 0.0
    for j in range(k, n + 1):
        tot += math.exp(math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq)
    return min(1.0, tot)


def perm_less(eA, eB, R, r):
    """one-sided: mean(eA) - mean(eB) > 0 ; returns p"""
    obs = sum(eA) / len(eA) - sum(eB) / len(eB)
    pool = eA + eB; nA = len(eA); ge = 0
    for _ in range(R):
        r.shuffle(pool)
        ge += (sum(pool[:nA]) / nA - sum(pool[nA:]) / len(eB)) >= obs - 1e-12
    return (ge + 1) / (R + 1), obs


def D_stat(lens, pages, inside):
    bypage = collections.defaultdict(list)
    for n, p in zip(lens, pages): bypage[p].append(n)
    med = {p: sorted(v)[len(v) // 2] for p, v in bypage.items()}
    r = [n - med[p] for n, p in zip(lens, pages)]
    a = [x for x, i in zip(r, inside) if i]; b = [x for x, i in zip(r, inside) if not i]
    if not a or not b: return 0.0, r
    return sum(a) / len(a) - sum(b) / len(b), r


def D_test(lens, pages, inside, R, r):
    obs, res = D_stat(lens, pages, inside)
    idx = collections.defaultdict(list)
    for k, p in enumerate(pages): idx[p].append(k)
    lab = list(inside); ge = 0
    for _ in range(R):
        for p, ks in idx.items():
            v = [lab[k] for k in ks]; r.shuffle(v)
            for k, x in zip(ks, v): lab[k] = x
        a = [x for x, i in zip(res, lab) if i]; b = [x for x, i in zip(res, lab) if not i]
        if a and b: ge += (sum(a) / len(a) - sum(b) / len(b)) >= obs - 1e-12
    return (ge + 1) / (R + 1), obs


# ---------------- layout simulation ----------------
def layout(stream, widths, rho, d, r):
    s0 = r.randrange(0, len(stream) - 20000)
    need = sum(widths) + 50
    ends = []; tot = 0; k = s0
    while tot < need:
        tot += stream[k]; ends.append(tot); k += 1
    bset = set(ends)
    pos = 0; lines = []; dropped = set()
    for W in widths:
        tgt = pos + W
        j = bisect.bisect_right(ends, tgt) - 1
        b = ends[j] if j >= 0 else 0
        if b != tgt and r.random() < rho and b > pos and tgt - b <= SLACK:
            cut = b
        else:
            cut = tgt
        inside = cut not in bset
        if not inside and r.random() < d: dropped.add(cut)
        lines.append((cut - pos, inside, cut)); pos = cut
    # observed words in [0,pos): boundaries = ends < pos minus dropped
    obs_b = [e for e in ends if e < pos and e not in dropped]
    edges = [0] + obs_b + [pos]
    words = [edges[i + 1] - edges[i] for i in range(len(edges) - 1)]
    cuts_inside = [c for (_, ins, c) in lines if ins] + sorted(dropped)
    # spanning words: word containing an inside cut or a dropped boundary
    sp = set()
    for c in cuts_inside:
        sp.add(bisect.bisect_left(obs_b, c))  # index of word containing position c (c strictly inside)
    span_len = [words[i] for i in sp if i < len(words)]
    c_frac = 1 - (len(words) - 1) / (pos - 1)
    nl = len(lines); nin = sum(1 for l in lines if l[1] and l[2] not in dropped) + len(dropped)
    f = nin / nl
    return dict(lens=[l[0] for l in lines], inside=[l[1] or (l[2] in dropped) for l in lines], words=words,
                span_len=span_len, c=c_frac, f_in=f, pi=1 - f / c_frac,
                excess=[(0 if (l[1] or l[2] in dropped) else 1) - (1 - c_frac) for l in lines])


def u3_LR(words, span_len):
    g = collections.Counter(words); n = len(words); M = max(max(words), max(span_len) if span_len else 1) + 1
    gp = [g[k] / n for k in range(M + 1)]
    sb = [(k - 1) * gp[k] if k >= 2 else 0 for k in range(M + 1)]; zs = sum(sb); sb = [x / zs for x in sb]
    cv = [sum(gp[a] * gp[k - a] for a in range(1, k)) for k in range(M + 1)]; zc = sum(cv); cv = [x / zc for x in cv]
    def ll(wt):
        s = 0.0
        for L in span_len:
            v = (1 - wt) * sb[L] + wt * cv[L]
            s += math.log(v) if v > 0 else -1e9
        return s
    l0 = ll(0.0); best = (l0, 0.0)
    for i in range(1, 101):
        v = ll(i / 100)
        if v > best[0]: best = (v, i / 100)
    return 2 * (best[0] - l0), best[1]


def running_widths(S, sel=lambda l: True):
    L = [l for l in S['lines'] if l['running'] and sel(l)]
    return [l['n'] for l in L], [l['page'] for l in L], [l['inside'] for l in L]


def calibrate(stream, widths, target, r):
    best = None
    for i in range(0, 51):
        rho = i / 50
        pis = [layout(stream, widths, rho, 0.0, r)['pi'] for _ in range(20)]
        m = sum(pis) / len(pis)
        if best is None or abs(m - target) < abs(best[1] - target): best = (rho, m)
    return best


def main():
    P.heartbeat('lead_ii stage1')
    S2 = struct(raw_lp2()); S1 = struct(raw_lp1())
    _, w2 = P.w.load_lp2()
    assert len(S2['words']) == len(w2) and S2['words'] == [x['len'] for x in w2], 'word parse mismatch with w1lib'
    lp1 = summ(S1); lp2 = summ(S2)
    P.log('LP1: c=%.4f running=%d inside=%d f_in=%.4f pi=%.4f | X1-def %d breaks f_in=%.4f' %
          (lp1['c'], lp1['n_running'], lp1['inside'], lp1['f_in'], lp1['pi'], lp1['x1_all_breaks'], lp1['x1_f_in']))
    P.log('LP2 full: c=%.4f running=%d inside=%d f_in=%.4f pi=%.4f | X1-def %d breaks f_in=%.4f' %
          (lp2['c'], lp2['n_running'], lp2['inside'], lp2['f_in'], lp2['pi'], lp2['x1_all_breaks'], lp2['x1_f_in']))
    sanity_lp1 = binom_sf(lp1['n_running'] - lp1['inside'], lp1['n_running'], 1 - lp1['c'])
    P.log('Q5 sanity: LP1 pi>0 binomial p=%.3g' % sanity_lp1)
    # English stream for plants: 6 FE corpora concatenated
    stream = []
    for rel in ['armada18/homer_odyssey_butler', 'armada19/stoker_dracula', 'armada18/plato_republic_jowett',
                'armada19/cervantes_don_quixote_ormsby', 'armada18/emerson_essays_first_series', 'campaign12/walden']:
        stream += [x[1] for x in P.load_fe(rel)]
    wid2, pg2, _ = running_widths(S2); wid1, _, _ = running_widths(S1)
    rho2, m2 = calibrate(stream, wid2, lp2['pi'], rng)
    rho1, m1 = calibrate(stream, wid1, lp1['pi'], rng)
    P.log('calibration: rho_LP2=%.2f (plant pi %.4f vs %.4f), rho_LP1=%.2f (plant pi %.4f vs %.4f)' %
          (rho2, m2, lp2['pi'], rho1, m1, lp1['pi']))
    # parts
    npages = max(p for p, s in S2['runes']) + 1
    half = npages // 2
    parts = {'P1': lambda p, s: p < half, 'P2': lambda p, s: p >= half,
             'S_odd': lambda p, s: s % 2 == 1, 'S_even': lambda p, s: s % 2 == 0}
    U1_plants = {}
    P.heartbeat('lead_ii U1 plants')
    for name, f in parts.items():
        wp, _, _ = running_widths(S2, lambda l, f=f: f(l['page'], l['sect']))
        pa = pb = sb = 0; K = 100
        for t in range(K):
            pl = layout(stream, wp, rho2, 0.0, rng)
            nb = sum(1 for x in pl['inside'] if not x)
            pa += binom_sf(nb, len(wp), 1 - pl['c']) <= 0.01
            pb += perm_less(lp1['excess'], pl['excess'], 300, rng)[0] <= 0.01
            pz = layout(stream, wp, rho1, 0.0, rng)
            sb += perm_less(lp1['excess'], pz['excess'], 300, rng)[0] <= 0.01
        U1_plants[name] = dict(n_lines=len(wp), power_a=pa / K, power_b=pb / K, size_b=sb / K)
        P.log('U1 plant %s: n=%d power(a)=%.3f power(b)=%.3f size(b)=%.3f' % (name, len(wp), pa / K, pb / K, sb / K))
    # U2 plants on full LP2 widths
    P.heartbeat('lead_ii U2 plants')
    pw = sz = 0; K = 200
    for t in range(K):
        pl = layout(stream, wid2, rho2, 0.0, rng)
        pw += D_test(pl['lens'], pg2, pl['inside'], 300, rng)[0] <= 0.01
        pz = layout(stream, wid2, 0.0, 0.0, rng)
        sz += D_test(pz['lens'], pg2, pz['inside'], 300, rng)[0] <= 0.01
    L1w, L1p, L1i = running_widths(S1)
    p_lp1, D_lp1 = D_test(L1w, L1p, L1i, 10000, rng)
    U2_ctrl = dict(power_rho_LP2=pw / K, size_blind=sz / K, LP1_p=p_lp1, LP1_D=D_lp1)
    P.log('U2 controls: power=%.3f size=%.3f LP1 D=%.3f p=%.4f' % (pw / K, sz / K, D_lp1, p_lp1))
    # U3 bar and power
    P.heartbeat('lead_ii U3 plants')
    nullLR = []
    for t in range(500):
        pl = layout(stream, wid2, 0.0, 0.0, rng); nullLR.append(u3_LR(pl['words'], pl['span_len'])[0])
        pl = layout(stream, wid2, rho2, 0.0, rng); nullLR.append(u3_LR(pl['words'], pl['span_len'])[0])
    bar = P.pct(nullLR, 0.99)
    powd = {}
    for d in (1.0, 0.5):
        hits = []; what = []
        for t in range(200):
            pl = layout(stream, wid2, 0.0, d, rng); lr, wh = u3_LR(pl['words'], pl['span_len'])
            hits.append(lr > bar); what.append(wh)
        powd[str(d)] = dict(power=sum(hits) / len(hits), w_hat_median=P.pct(what, .5))
    lr1, w1h = u3_LR(S1['words'], S1['span_len'])
    U3_ctrl = dict(bar99=bar, power=powd, LP1_LR=lr1, LP1_w_hat=w1h, LP1_n_span=len(S1['span_len']))
    P.log('U3 controls: bar=%.2f power %s LP1 LR=%.2f w=%.2f' % (bar, powd, lr1, w1h))
    st = dict(LP1=dict((k, v) for k, v in lp1.items() if k != 'excess'), LP2_full_pi_used_for_calibration=lp2['pi'],
              sanity_LP1_pi_gt0_p=sanity_lp1, rho_LP2=rho2, rho_LP1=rho1, plant_pi=[m2, m1], slack=SLACK,
              U1_plants=U1_plants, U2_controls=U2_ctrl, U3_controls=U3_ctrl, npages_LP2=npages)
    json.dump(st, open(OUT1, 'w'), indent=1)
    # ---------------- stage 2: LP2 ----------------
    P.heartbeat('lead_ii stage2 LP2')
    r2 = random.Random(46102)
    U1 = {}
    for name, f in parts.items():
        sm = summ(S2, sel=lambda gr, f=f: f(gr['page'], gr['sect']))
        nb = sm['n_running'] - sm['inside']
        pa = binom_sf(nb, sm['n_running'], 1 - sm['c'])
        pb, diff = perm_less(lp1['excess'], sm['excess'], 10000, r2)
        U1[name] = dict(c=sm['c'], n=sm['n_running'], f_in=sm['f_in'], pi=sm['pi'], p_a=pa, pass_a=pa <= 0.01,
                        p_b=pb, excess_diff=diff, pass_b=pb <= 0.01,
                        informative_b=U1_plants[name]['power_b'] >= 0.8 and U1_plants[name]['size_b'] <= 0.02)
        P.log('U1 LP2 %s: n=%d c=%.4f f_in=%.4f pi=%.4f p(a)=%.3g p(b)=%.4g' % (name, sm['n_running'], sm['c'], sm['f_in'],
                                                                               sm['pi'], pa, pb))
    U1_rep = all(v['pass_b'] for v in U1.values())
    pa_full = binom_sf(lp2['n_running'] - lp2['inside'], lp2['n_running'], 1 - lp2['c'])
    pb_full, diff_full = perm_less(lp1['excess'], lp2['excess'], 10000, r2)
    p2, D2 = D_test(wid2, pg2, running_widths(S2)[2], 10000, r2)
    lr2, w2h = u3_LR(S2['words'], S2['span_len'])
    # implied 2-rune share if w_hat of spanning words were merged pairs: descriptive
    res = dict(LP2_full=dict((k, v) for k, v in lp2.items() if k != 'excess'), LP2_full_p_a=pa_full,
               LP2_full_p_b=pb_full, U1=U1, U1_replicates_all=U1_rep,
               U2=dict(D=D2, p=p2, signature=p2 <= 0.01, informative_null=U2_ctrl['power_rho_LP2'] >= 0.8 and U2_ctrl['LP1_p'] <= 0.01),
               U3=dict(LR=lr2, w_hat=w2h, bar99=bar, merged_pairs=lr2 > bar, n_span=len(S2['span_len']),
                       span_mean=sum(S2['span_len']) / len(S2['span_len']),
                       informative=powd['1.0']['power'] >= 0.8))
    P.log('U1 full LP2: p(a)=%.3g p(b)=%.4g replicate_all=%s' % (pa_full, pb_full, U1_rep))
    P.log('U2 LP2: D=%.3f p=%.4f' % (D2, p2))
    P.log('U3 LP2: LR=%.2f (bar %.2f) w_hat=%.2f n_span=%d' % (lr2, bar, w2h, len(S2['span_len'])))
    json.dump(res, open(OUT2, 'w'), indent=1)
    P.heartbeat('lead_ii done')


if __name__ == '__main__':
    main()
