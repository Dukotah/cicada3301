# R45-W1 Q2b — POST-HOC, DESCRIPTIVE ONLY (not registered; written after q2_results.json was seen; see PREREG Addendum 2).
# (1) per-length-class share of LP2 vs the spread of 2,896-word English windows (all 8 corpora) and the solved reference;
# (2) G of LP2 against the solved-Cicada distribution vs G of English windows against the same distribution
#     (substitute comparator for M1, whose permutation null failed its size control).
import os, json, math, random, collections
import w1lib as w

rng = random.Random(4599)
_, w2 = w.load_lp2(); L = [x['len'] for x in w2]; n = len(L)
_, w1 = w.load_lp1(); _, ws = w.load_lp2_solved()
Sv = [x['len'] for x in w1] + [x['len'] for x in ws]
corp = {fn: [x[0] for x in w.load_corpus(fn)] for fn in w.CORPORA}
K = 9
def share(S):
    c = [0] * K
    for x in S: c[min(x, K) - 1] += 1
    return [v / len(S) for v in c]
wins = []
for fn, c in corp.items():
    for t in range(60):
        a = rng.randrange(0, len(c) - n); wins.append((fn, c[a:a + n]))
ws_share = [share(S) for _, S in wins]
lp = share(L); sv = share(Sv)
table = {}
for k in range(K):
    col = sorted(s[k] for s in ws_share)
    table['%d%s' % (k + 1, '+' if k == K - 1 else '')] = dict(
        LP2=round(lp[k], 4), solved=round(sv[k], 4), english_min=round(col[0], 4), english_max=round(col[-1], 4),
        frac_english_windows_as_extreme=round(min(sum(v <= lp[k] for v in col), sum(v >= lp[k] for v in col)) / len(col), 4))
cs = [0] * K
for x in Sv: cs[min(x, K) - 1] += 1
q = [(v + 0.5) / (len(Sv) + 0.5 * K) for v in cs]
def G(S):
    c = [0] * K
    for x in S: c[min(x, K) - 1] += 1
    return 2 * sum(v * math.log(v / (len(S) * p)) for v, p in zip(c, q) if v)
gl = G(L); ge = sorted(G(S) for _, S in wins)
out = dict(note='POST-HOC descriptive; no verdict', class_share=table,
           G_vs_solved=dict(LP2=gl, english_windows_median=ge[len(ge) // 2], english_windows_q99=ge[int(.99 * len(ge))],
                            english_windows_max=ge[-1], frac_english_windows_ge_LP2=sum(v >= gl for v in ge) / len(ge),
                            n_windows=len(ge)))
json.dump(out, open(os.path.join(w.HERE, 'q2b_posthoc.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
