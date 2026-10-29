"""Round 34 / I1: observed-null family-wise bars for beam_v3 (panel_max, hard max, lam_u=4, beam_w=400) panel pmax.

    bar_v3(N, L, relation, alpha=0.01, family="lp2"|"register", method="gumbel"|"gpd")

Model (fit.json, built by fit.py from null_stream.jsonl): exponential (Gumbel-max) peaks-over-threshold tail above the
empirical 90th percentile of v3 wrong-key pmax, per (family, relation, L) node; beta(L) is the fitted power law over L
(ln beta ~ ln L), mu(L) = u + beta ln p_u is interpolated linearly in ln L between nodes L=31,120,240,400 (flat outside).
bar = mu + beta * ln(N / -ln(1-alpha)): P(max over N independent wrong-key decodes >= bar) = alpha.
`family="lp2"`: shuffled real LP2 stream.  `family="register"`: shuffled held-out EN_NOVOWEL/LATIN/OE/DE pooled.
`relation` in {"keyskip1","keyskip2"}; "free" exists at L=120 only (nodes from 1000 draws, own beta).
method="gpd" gives the lighter-tailed (xi<0) sensitivity bar -- NOT the bar of record (extrapolates a bounded tail).
Round 34 Q5 fired (beta exponent far from Round 32 I3's -0.55): see RESULTS.md; the Gumbel bar is the conservative one
(it over-predicts the observed max at the observed N), the empirical quantile exists only up to N~n_draws.

>>> round(bar_v3(2e5, 120, "keyskip1"), 2)
8.62
>>> bar_v3(1e6, 120, "keyskip1") > bar_v3(1e5, 120, "keyskip1")
True
>>> bar_v3(1e6, 240, "keyskip2", family="register") > 5
True
>>> round(bar_v3(1e5, 120, "free"), 1) > 10
True
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
_FIT = None


def _fit():
    global _FIT
    if _FIT is None:
        _FIT = json.load(open(os.path.join(HERE, "fit.json"), encoding="utf-8"))
    return _FIT


def _params(L, relation, family):
    F = _fit()
    if relation == "free":
        if L != 120:
            raise ValueError("free relation has a null at L=120 only")
        n = F["free"]["120"]
        return n["u"], n["p_u"], n["beta"], n
    ser = F["series"]["%s|%s" % (family, relation)]
    nodes = sorted((int(k), v) for k, v in ser["nodes"].items())
    beta = lambda l: math.exp(ser["ln_a"] + ser["exponent"] * math.log(l))
    mus = [(l, v["u"] + beta(l) * math.log(v["p_u"])) for l, v in nodes]
    x = math.log(min(max(L, nodes[0][0]), nodes[-1][0]))
    mu = None
    for (l0, m0), (l1, m1) in zip(mus, mus[1:]):
        if math.log(l0) <= x <= math.log(l1):
            t = (x - math.log(l0)) / (math.log(l1) - math.log(l0))
            mu = m0 + t * (m1 - m0)
            break
    return mu, None, beta(L), nodes


def bar_v3(N, L, relation, alpha=0.01, family="lp2", method="gumbel"):
    if relation not in ("keyskip1", "keyskip2", "free"):
        raise ValueError(relation)
    if family not in ("lp2", "register"):
        raise ValueError(family)
    N = float(N)
    if method == "gpd":
        F = _fit()
        if relation == "free":
            n = F["free"]["120"]
        else:
            n = None
            ser = F["series"]["%s|%s" % (family, relation)]["nodes"]
            ks = sorted(int(k) for k in ser)
            n = ser[str(min(ks, key=lambda k: abs(math.log(k) - math.log(L))))]
        xi, sg = n["xi_gpd_moments"], n["gpd_sigma"]
        t = N * n["p_u"] / -math.log1p(-alpha)
        return n["u"] + (sg / xi * (t ** xi - 1) if abs(xi) > 1e-6 else sg * math.log(t))
    if relation == "free":
        u, pu, beta, n = _params(L, relation, family)
        return u + beta * math.log(pu) + beta * math.log(N / -math.log1p(-alpha))
    mu, _, beta, _n = _params(L, relation, family)
    return mu + beta * math.log(N / -math.log1p(-alpha))


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())
