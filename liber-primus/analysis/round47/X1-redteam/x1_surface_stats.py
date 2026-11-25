"""R47-X1: are V-BACK / V-NULL excluded by LP2's surface statistics? 20 replicate 12,956-rune English plants
per variant (fresh SHA-256 key, supp = EXACT_SUPP, the C9 encipherers), vs LP2's own values.
Stats: lag-1 (doublet) rate, lag-2 repeat rate, IoC*N."""
import os, sys, random, json, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "challenges")))
import _heavy as H, c9_rejection_loops as C9  # noqa: E402
N = H.N
def stats(x):
    n = len(x)
    l1 = sum(x[i] == x[i-1] for i in range(1, n)) / (n-1)
    l2 = sum(x[i] == x[i-2] for i in range(2, n)) / (n-2)
    f = [0]*N
    for v in x: f[v] += 1
    ioc = N*sum(a*(a-1) for a in f)/(n*(n-1))
    return l1, l2, ioc
lp2 = H.lp2_stream(); s0 = stats(lp2)
stream = H.english_stream()
rng = random.Random(4799)
out = {"LP2": dict(zip(("lag1", "lag2", "iocN"), s0))}
for v in C9.VARIANTS:
    rows = []
    for r in range(20):
        a = rng.randrange(0, len(stream) - 12956)
        P = stream[a:a+12956]
        K = H.rand_key(rng, 3*12956)
        rows.append(stats(C9.VARIANTS[v](P, K, H.EXACT_SUPP, rng)[:12956]))
    cols = list(zip(*rows))
    out[v] = {k: {"mean": st.mean(c), "sd": st.stdev(c), "z_LP2": (s0[i]-st.mean(c))/st.stdev(c)}
              for i, (k, c) in enumerate(zip(("lag1", "lag2", "iocN"), cols))}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "x1_surface_stats.json"), "w"), indent=1)
