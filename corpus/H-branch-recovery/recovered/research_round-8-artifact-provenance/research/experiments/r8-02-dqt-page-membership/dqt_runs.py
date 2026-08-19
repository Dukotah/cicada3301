#!/usr/bin/env python3
"""R8-S2: DQT page-membership runs test + confound check. Executes pre-registration exactly.
Seed 3301 for the Monte-Carlo permutation null. Writes results.json."""
import json, os, re, random, math

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RES = os.path.join(REPO, "liber-primus", "analysis", "stego", "out_authentic", "results.json")

def pageno(fn):
    return int(re.search(r"p(\d+)\.jpg", fn).group(1))

def runs_count(seq):
    return 1 + sum(1 for i in range(1, len(seq)) if seq[i] != seq[i-1])

def mannwhitney_u(a, b):
    """Two-sided Mann-Whitney U with normal approx (ties handled simply)."""
    combined = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    # rank with average ties
    ranks = [0.0]*len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j+1 < len(combined) and combined[j+1][0] == combined[i][0]:
            j += 1
        r = (i + j) / 2.0 + 1
        for k in range(i, j+1):
            ranks[k] = r
        i = j + 1
    Ra = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    na, nb = len(a), len(b)
    Ua = Ra - na*(na+1)/2.0
    Ub = na*nb - Ua
    U = min(Ua, Ub)
    mu = na*nb/2.0
    sigma = math.sqrt(na*nb*(na+nb+1)/12.0)
    z = (U - mu)/sigma if sigma else 0.0
    # two-sided normal p
    p = math.erfc(abs(z)/math.sqrt(2))
    return dict(U=U, z=z, p=p)

def spearman(x, y):
    n = len(x)
    def rank(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0]*n; i = 0
        while i < n:
            j = i
            while j+1 < n and v[order[j+1]] == v[order[i]]:
                j += 1
            avg = (i+j)/2.0 + 1
            for k in range(i, j+1):
                r[order[k]] = avg
            i = j+1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    den = math.sqrt(sum((rx[i]-mx)**2 for i in range(n))*sum((ry[i]-my)**2 for i in range(n)))
    return num/den if den else 0.0

def main():
    data = json.load(open(RES))
    data = sorted(data, key=lambda e: pageno(e["file"]))
    fps = [e["dqt_fingerprint"] for e in data]
    sizes = [e["size"] for e in data]
    pages = [pageno(e["file"]) for e in data]
    groups = sorted(set(fps))
    assert len(groups) == 2, f"expected 2 DQT groups, got {len(groups)}: {groups}"
    g0 = groups[0]
    seq = [0 if f == g0 else 1 for f in fps]
    n0 = seq.count(0); n1 = seq.count(1); N = len(seq)
    R = runs_count(seq)
    # analytic W-W
    ER = 1 + 2*n0*n1/N
    VarR = 2*n0*n1*(2*n0*n1 - N)/(N*N*(N-1))
    zR = (R - ER)/math.sqrt(VarR) if VarR > 0 else 0.0
    # Monte-Carlo permutation null, seed 3301
    rng = random.Random(3301)
    NPERM = 100000
    base = seq[:]
    le = 0  # count |R_perm - ER| >= |R - ER|  (two-sided)
    obs_dev = abs(R - ER)
    perm_runs_le = 0
    for _ in range(NPERM):
        rng.shuffle(base)
        rp = runs_count(base)
        if abs(rp - ER) >= obs_dev - 1e-9:
            le += 1
        if rp <= R:
            perm_runs_le += 1
    p_two = le / NPERM
    p_low = perm_runs_le / NPERM
    # confound: size by group
    size0 = [sizes[i] for i in range(N) if seq[i] == 0]
    size1 = [sizes[i] for i in range(N) if seq[i] == 1]
    mw = mannwhitney_u(size0, size1)
    rho_page_size = spearman(pages, sizes)
    # boundary description: list run boundaries (page indices where group switches)
    switches = [pages[i] for i in range(1, N) if seq[i] != seq[i-1]]
    membership = {str(pages[i]): (g0 if seq[i] == 0 else groups[1]) for i in range(N)}

    # pre-registered interpretation rule
    positional = p_two < 0.001
    complexity_diff = mw["p"] < 0.05
    if not positional:
        verdict = "NEGATIVE"
    elif positional and not complexity_diff:
        verdict = "SURVIVES (production-batch signal; not complexity-explained)"
    else:
        verdict = "INCONCLUSIVE (positional but confounded by content complexity)"

    out = {
        "experiment": "r8-02-dqt-page-membership",
        "seed": 3301, "n_perm": NPERM,
        "groups": {g0: n0, groups[1]: n1}, "N": N,
        "runs_observed": R, "expected_runs": ER, "var_runs": VarR, "z_runs": zR,
        "p_two_sided_montecarlo": p_two, "p_runs_le_montecarlo": p_low,
        "positional_p_lt_0.001": positional,
        "confound_size_by_group": {
            "median_g0": sorted(size0)[len(size0)//2], "median_g1": sorted(size1)[len(size1)//2],
            "mannwhitney": mw, "groups_differ_in_size_p_lt_0.05": complexity_diff,
            "spearman_pageindex_vs_size": rho_page_size,
        },
        "group_switch_pages": switches,
        "membership_by_page": membership,
        "VERDICT": verdict,
    }
    outpath = os.path.join(os.path.dirname(__file__), "results.json")
    with open(outpath, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "membership_by_page"}, indent=2))
    print("membership_by_page:", membership)

if __name__ == "__main__":
    main()
