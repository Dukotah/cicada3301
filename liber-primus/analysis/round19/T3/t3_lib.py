"""T3 — THE PROPAGATION MAP — shared instrument.

Loads the pinned 12,956-rune stream, pins its SHA-256 against PROBLEM.json, exposes the
statistic bundle (reusing `lp.stats` wherever the repo already implements it), the layout
structure, the O/A/AE located-disagreement map, and the perturbation models.

Nothing here is new arithmetic where the repo already has an implementation. Where a
statistic had to be re-implemented (lag-1 suppression, s*, draw count, Delta-spectrum,
line-break doublets, line-initial chi2) the re-implementation is checked against the
published value on the UNPERTURBED stream by `t3_baseline.py` (PREREG PC-3).
"""
import os, sys, json, math, random, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))      # liber-primus/
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "stones"),
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round18", "L2-filter-leak")):
    sys.path.insert(0, os.path.join(ROOT, p))

from lp import gematria as gp          # noqa: E402
from lp import stats as lpstats        # noqa: E402

N = gp.N                                # 29
Q = 1.0 / N

PINNED_SHA = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"

# O / A / AE  --> Gematria Primus indices
RUNE_O, RUNE_A, RUNE_AE = "ᚩ", "ᚪ", "ᚫ"
OAE_RUNES = (RUNE_O, RUNE_A, RUNE_AE)
OAE_IDX = tuple(gp.RUNE_TO_IDX[r] for r in OAE_RUNES)     # (3, 24, 25)

DENSE_PAGES = tuple(range(45, 55))       # the dense OTP pages 45-54


# --------------------------------------------------------------- the object
def sha_of(idxs):
    return hashlib.sha256(",".join(map(str, idxs)).encode()).hexdigest()


_CACHE = {}


def layout():
    """(lines, page_of, line_offsets) over pages 0-54, from the repo's own parser."""
    if "layout" in _CACHE:
        return _CACHE["layout"]
    import pipeline as P
    cwd = os.getcwd()
    try:
        os.chdir(ROOT)            # pipeline.global_lines() uses a liber-primus-relative path
        lines, page_of = P.global_lines()
    finally:
        os.chdir(cwd)
    off = [0]
    for L in lines:
        off.append(off[-1] + len(L))
    _CACHE["layout"] = (lines, page_of, off)
    return _CACHE["layout"]


def stream():
    """The pinned 12,956-rune unsolved stream, SHA-verified against PROBLEM.json."""
    if "stream" in _CACHE:
        return _CACHE["stream"]
    import lib_numchannel as nc
    u = nc.unsolved()
    assert len(u) == 12956, len(u)
    h = sha_of(u)
    assert h == PINNED_SHA, f"stream hash {h} != pinned {PINNED_SHA}"
    # the layout parse must reproduce it element-wise (this is what licenses the position map)
    lines, _, _ = layout()
    flat = [gp.RUNE_TO_IDX[c] for L in lines for c in L]
    assert flat == u, "pipeline.global_lines() does not reproduce the pinned stream"
    _CACHE["stream"] = u
    return u


def line_index():
    """array line_of[i] = global line number of stream position i; and is_line_initial[i]."""
    if "lidx" in _CACHE:
        return _CACHE["lidx"]
    lines, page_of, off = layout()
    line_of = [0] * off[-1]
    for gl, L in enumerate(lines):
        for j in range(len(L)):
            line_of[off[gl] + j] = gl
    init = set(off[:-1])
    _CACHE["lidx"] = (line_of, init, page_of)
    return _CACHE["lidx"]


def page_of_pos():
    line_of, _, page_of = line_index()
    return [page_of[g] for g in line_of]


# ------------------------------------------------- the 450 located disagreements
def oae450():
    """[{pos, canon_idx, alt_idx}] in STREAM coordinates. Gate: canon must match."""
    if "oae450" in _CACHE:
        return _CACHE["oae450"]
    recs = json.load(open(os.path.join(ROOT, "analysis", "independent-read",
                                       "oae_mismatch.json"), encoding="utf-8"))
    lines, _, off = layout()
    out, bad = [], 0
    for r in recs:
        gl, j = r["global_line"], r["pos_in_line"]
        if gl >= len(lines) or j >= len(lines[gl]) or lines[gl][j] != r["canon"]:
            bad += 1
            continue
        out.append({"pos": off[gl] + j,
                    "canon_idx": gp.RUNE_TO_IDX[r["canon"]],
                    "alt_idx": gp.RUNE_TO_IDX[r["looks_like"]]})
    assert bad == 0, f"{bad} of {len(recs)} records failed the map gate"
    assert len(out) == 450 and len({d['pos'] for d in out}) == 450
    _CACHE["oae450"] = out
    return out


def oae_family_positions(C=None):
    C = C if C is not None else stream()
    return [i for i, c in enumerate(C) if c in OAE_IDX]


# ------------------------------------------------------------ statistic bundle
def lag1_suppression(C):
    """L7-C.1's definition: 1 - r_obs / r_unigram, where r_unigram is the stream's OWN
    unigram collision rate (NOT 1/29).

    NOTE (T3, resolved during PC-3): "the stream's own unigram collision rate" is the
    UNBIASED / without-replacement estimator sum c_i(c_i-1) / n(n-1) -- i.e. exactly
    `lp.stats.ioc` -- not the plug-in sum p_i^2.  On the pinned stream the two differ in
    the 3rd significant figure (3.44784 % vs 3.45529 %) and only the unbiased one
    reproduces L7's published 3.4478 % / 80.746 %.  Using the plug-in estimator instead
    shifts the published lag-1 suppression by 0.042 pp.  Both are defensible statistics;
    the repo's published number is the unbiased one and that is what is used here.
    """
    r_uni = lpstats.ioc(C)
    r_obs = lpstats.doublet_rate(C)
    return 1.0 - r_obs / r_uni, r_uni


def s_star(r, q=Q):
    """Invert L2 §1's closed form r(s) = q(1-s)/(1-q s)."""
    return (q - r) / (q * (1.0 - r))


def draw_count(n, s, q=Q):
    rho = q * s / (1.0 - q * s)
    return rho * n, rho


def delta_spectrum(C):
    """L2 §2: D_i = (c_i - c_{i-1}) mod 29 over the 28 NON-ZERO cells.
    Returns (chi2_over_df, max_abs_z, argmax_cell)."""
    n = len(C) - 1
    cnt = collections.Counter((b - a) % N for a, b in zip(C, C[1:]))
    m = n - cnt.get(0, 0)                       # non-zero-delta events
    exp = m / 28.0
    cells = [d for d in range(1, N)]
    chi2 = sum((cnt.get(d, 0) - exp) ** 2 / exp for d in cells)
    df = 27                                     # 28 cells, 1 constraint (total)
    sd = math.sqrt(exp * (1 - 1.0 / 28.0))
    zs = {d: (cnt.get(d, 0) - exp) / sd for d in cells}
    dmax = max(cells, key=lambda d: abs(zs[d]))
    return chi2 / df, abs(zs[dmax]), dmax


def line_break_doublets(C):
    """Doublets whose two runes straddle a line boundary (round17/round18-L4: 4 of 86)."""
    line_of, _, _ = line_index()
    return sum(1 for i in range(len(C) - 1)
               if C[i] == C[i + 1] and line_of[i] != line_of[i + 1])


def line_initial_chi2(C):
    """L4 Arm A1: chi2 of the 594 line-initial runes' 29-bin histogram against the
    FULL-TEXT distribution of the same stream."""
    _, init, _ = line_index()
    n = len(C)
    full = collections.Counter(C)
    sub = [C[i] for i in sorted(init)]
    k = len(sub)
    cs = collections.Counter(sub)
    chi2 = 0.0
    for r in range(N):
        e = k * full.get(r, 0) / n
        if e > 0:
            chi2 += (cs.get(r, 0) - e) ** 2 / e
    return chi2


def bundle(C):
    """Every stream-dependent statistic this lane tracks, in one dict."""
    d = lpstats.doublet_count(C)
    r = lpstats.doublet_rate(C)
    supp, r_uni = lag1_suppression(C)
    s = s_star(r)
    dc, rho = draw_count(len(C), s)
    dchi, dz, dcell = delta_spectrum(C)
    return {
        "n": len(C),
        "sha256": sha_of(C),
        "doublets": d,
        "doublet_rate_pct": 100.0 * r,
        "ioc_norm": lpstats.ioc_norm(C),
        "entropy_bits": lpstats.shannon_entropy(C),
        "chi2_uniform": lpstats.chi2_uniform(C),
        "unigram_collision_pct": 100.0 * r_uni,
        "lag1_suppression_pct": 100.0 * supp,
        "s_star": s,
        "draws_extra": dc,
        "rho": rho,
        "delta_chi2_over_df": dchi,
        "delta_max_abs_z": dz,
        "delta_argmax_cell": dcell,
        "line_break_doublets": line_break_doublets(C),
        "line_initial_chi2": line_initial_chi2(C),
    }


CHEAP_KEYS = ("doublets", "doublet_rate_pct", "ioc_norm", "entropy_bits",
              "lag1_suppression_pct", "s_star", "draws_extra",
              "delta_chi2_over_df", "delta_max_abs_z",
              "line_break_doublets", "line_initial_chi2", "chi2_uniform")


# ------------------------------------------------------------- perturbations
def p_rand(C, k, rng):
    out = list(C)
    for i in rng.sample(range(len(C)), k):
        out[i] = rng.choice([v for v in range(N) if v != C[i]])
    return out


def p_dense(C, k, rng, pool=None):
    pool = pool if pool is not None else _dense_pool()
    out = list(C)
    for i in rng.sample(pool, min(k, len(pool))):
        out[i] = rng.choice([v for v in range(N) if v != C[i]])
    return out


def _dense_pool():
    if "densepool" not in _CACHE:
        pp = page_of_pos()
        _CACHE["densepool"] = [i for i, p in enumerate(pp) if p in DENSE_PAGES]
    return _CACHE["densepool"]


def p_oae450(C, k, rng, recs=None):
    """The located set, using the clusterer's OWN recorded alternative."""
    recs = recs if recs is not None else oae450()
    out = list(C)
    for r in rng.sample(recs, min(k, len(recs))):
        out[r["pos"]] = r["alt_idx"]
    return out


def p_oae450r(C, k, rng, recs=None):
    """The located set, random direction inside {O,A,AE}."""
    recs = recs if recs is not None else oae450()
    out = list(C)
    for r in rng.sample(recs, min(k, len(recs))):
        cur = C[r["pos"]]
        out[r["pos"]] = rng.choice([v for v in OAE_IDX if v != cur])
    return out


def p_oaefam(C, k, rng, pool=None):
    pool = pool if pool is not None else oae_family_positions(C)
    out = list(C)
    for i in rng.sample(pool, min(k, len(pool))):
        out[i] = rng.choice([v for v in OAE_IDX if v != C[i]])
    return out


def adv_sites(C):
    """Classify substitution sites for the doublet-maximising adversary.

    A substitution at position i can add at most 2 doublets, and only when
    C[i-1] == C[i+1] != C[i] (set C[i] to that value and BOTH adjacent pairs double).
    Otherwise the best a single substitution can do is +1 (set C[i] = C[i-1]), and only
    where it does not simultaneously DESTROY an existing doublet.

    Returns (gain2_sites, gain1_sites), both filtered so that chosen sites are >= 2 apart
    and never sit on an existing doublet.
    """
    n = len(C)
    dbl = set()
    for i in range(n - 1):
        if C[i] == C[i + 1]:
            dbl.add(i); dbl.add(i + 1)
    g2, g1 = [], []
    for i in range(1, n - 1):
        if i in dbl:
            continue                              # would destroy an existing doublet
        if C[i - 1] == C[i + 1] and C[i] != C[i - 1]:
            g2.append(i)
        elif C[i] != C[i - 1] and C[i] != C[i + 1]:
            g1.append(i)
    return g2, g1


def _spread(sites, used, gap=2):
    """Greedily take sites at least `gap` apart from each other and from `used`."""
    out = []
    for i in sites:
        if all(abs(i - j) >= gap for j in out) and all(abs(i - j) >= gap for j in used):
            out.append(i)
    return out


def adv_prediction(C, k):
    """Exact analytic doublet count after the greedy adversarial perturbation of size k."""
    g2, g1 = adv_sites(C)
    g2s = _spread(g2, [])
    m2 = min(k, len(g2s))
    g1s = _spread(g1, g2s[:m2])
    m1 = min(k - m2, len(g1s))
    base = lpstats.doublet_count(C)
    return base + 2 * m2 + m1, m2, m1


def p_adv(C, k, rng=None):
    """Adversarial: create as many doublets as possible with k substitutions.

    Greedy and, for this objective, optimal up to the site-spacing heuristic: spend the
    budget first on +2 sites (C[i-1] == C[i+1] != C[i]) and then on +1 sites, never
    touching a position that participates in an existing doublet.
    """
    out = list(C)
    g2, g1 = adv_sites(C)
    g2s = _spread(g2, [])
    take2 = g2s[:k]
    for i in take2:
        out[i] = C[i - 1]
    rem = k - len(take2)
    if rem > 0:
        g1s = _spread(g1, take2)
        for i in g1s[:rem]:
            out[i] = C[i - 1]
    return out


def p_collapse(C):
    """independent-read/FINDINGS.md §4's maximum-damage case: merge O/A/AE into one symbol.
    Returned as a symbol stream over 27 symbols (family -> a single sentinel)."""
    sent = OAE_IDX[0]
    return [sent if c in OAE_IDX else c for c in C]


MODELS = {
    "P-RAND": p_rand,
    "P-DENSE": p_dense,
    "P-OAE450": p_oae450,
    "P-OAE450R": p_oae450r,
    "P-OAEFAM": p_oaefam,
}
