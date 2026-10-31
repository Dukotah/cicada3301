"""Round 39 X1: does the I1 page-matched null (A = shuffle within physical line) preserve LP2's adjacent-equal-pair
constraint, and does restoring it change the realised FPR on clean V2 windows?  Uses I1's own functions unchanged."""
import os, sys, json, time
sys.dont_write_bytecode = True
os.environ['D2'] = '1'
H = os.path.dirname(os.path.abspath(__file__)); I1 = os.path.join(H, '..', 'I1-v2-page-null')
sys.path.insert(0, I1); sys.path.insert(0, os.path.join(H, '..', '..', 'round38', 'I1-glyph-recognizer'))
import numpy as np
import run as RUN
R, u8, VAR = RUN.R, RUN.u8, RUN.VAR


def ndoub(words):
    flat = [x for w in words for x in w]
    return sum(1 for a, b in zip(flat, flat[1:]) if a == b and a != 0)


def shuf_dm(words, lines, r, cap, tries=300):
    for _ in range(tries):
        out = RUN.shuf(words, lines, 'A', r)
        if ndoub(out) <= cap:
            return out, True
    return out, False


rng = np.random.default_rng(39001)
real_d = ndoub(RUN.W0); plain_d = float(np.mean([ndoub(RUN.shuf(RUN.W0, RUN.L0, 'A', rng)) for _ in range(100)]))
print('page0 adjacent-equal pairs real', real_d, 'of', sum(len(w) for w in RUN.W0), 'runes; plain A null mean', plain_d, flush=True)
NFP, ND = 50, 100
hits_plain = hits_dm = 0; acc = 0; tot = 0; t0 = time.time(); rows = []
r = np.random.default_rng(39777)
for i in range(NFP):
    ws, ls = RUN.clean(r); s, _ = R.score(u8.walk(ws, VAR), VAR); cap = ndoub(ws)
    ns_plain = np.array([R.score(u8.walk(RUN.shuf(ws, ls, 'A', r), VAR), VAR)[0] for _ in range(ND)])
    nd = []
    for _ in range(ND):
        o, ok = shuf_dm(ws, ls, r, cap); tot += 1; acc += ok
        nd.append(R.score(u8.walk(o, VAR), VAR)[0])
    ns_dm = np.array(nd)
    hp = bool(s < np.quantile(ns_plain, .05)); hd = bool(s < np.quantile(ns_dm, .05)); hits_plain += hp; hits_dm += hd
    rows.append(dict(score=float(s), real_doublets=cap, plain_mean_doublets=None, thr_plain=float(np.quantile(ns_plain, .05)), thr_dm=float(np.quantile(ns_dm, .05)), hit_plain=hp, hit_dm=hd))
    if i % 10 == 9:
        print(i + 1, hits_plain, hits_dm, round(time.time() - t0), flush=True)
out = dict(real_doublets_page0=real_d, plain_A_mean_doublets_page0=plain_d, n_clean=NFP, draws=ND, fpr_plain=hits_plain / NFP, fpr_doublet_matched=hits_dm / NFP,
           doublet_matched_acceptance=acc / tot, rows=rows)
json.dump(out, open(os.path.join(H, 'rerun_i1_doublet.json'), 'w'), indent=1)
print('FPR plain A %.3f  doublet-matched A %.3f  acceptance %.2f' % (hits_plain / NFP, hits_dm / NFP, acc / tot))
