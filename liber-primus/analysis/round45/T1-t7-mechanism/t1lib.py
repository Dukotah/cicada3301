"""R45 / T1 shared glue — T7 mechanism lane.

ONE code path for the null, the plants (Stage A/B) and the real data (PREREG.md, sha in run.log).
Point processes on the pair axis t = 0..T-1 (T = 12,955 pairs of the 12,956-rune unsolved stream).
Likelihood form: sum_i log lam(t_i) - sum_t lam(t)   (inhomogeneous Poisson on the pair grid).
"""
import json
import math
import os
import sys

import numpy as np
from scipy.special import gammaln, gammaincc

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402

NEV = 86
LN_NEV = math.log(NEV)
BIN = 25
LEV = np.linspace(math.log(5e-4), math.log(4e-2), 48)        # M2 log-rate levels
LAM = np.exp(LEV)
SIGMAS = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.14, 0.2, 0.3, 0.45, 0.7])
KMAX = 6
FANO_W = (250, 500, 1000, 2000)
MODELS = ["M0", "M1a", "M1b", "M1c", "M2", "M3a", "M3b", "M4"]


# ------------------------------------------------------------------ data + structure
def load():
    txt = open(os.path.join(LP, "data", "krisyotam_runes.txt"), encoding="utf-8").read()
    x, seg = [], 0
    page_start = [0]
    amp, dol = [], []
    for ch in txt:
        if ch in gp.RUNE_TO_IDX:
            if seg <= 54:
                x.append(gp.RUNE_TO_IDX[ch])
        elif ch == "%":
            seg += 1
            if seg <= 54:
                page_start.append(len(x))
        elif ch == "&" and seg <= 54:
            amp.append(len(x))
        elif ch == "$" and seg <= 54:
            dol.append(len(x))
    x = np.asarray(x, dtype=np.int64)
    assert len(x) == 12956, len(x)
    T = len(x) - 1
    ev = np.flatnonzero(x[1:] == x[:-1])
    b3 = json.load(open(os.path.join(LP, "analysis", "round44", "W2-B3-doublet-sites", "results.json")))
    ref = b3["real_sites_U86"]["positions_first_rune"]
    if len(ev) != NEV or list(map(int, ev)) != list(map(int, ref)):
        raise SystemExit("HALT: census does not reproduce B3 real_sites_U86")
    chap = sorted(set(b for b in dol if 0 < b < len(x)))
    sect = sorted(set(b for b in amp + dol if 0 < b < len(x)))
    pages = sorted(set(page_start))
    return dict(x=x, T=T, ev=ev, chap_ends=chap, sect_ends=sect, page_starts=pages)


def edges_from(bounds, T):
    return np.array([0] + [b for b in bounds if 0 < b < T] + [T], dtype=np.int64)


def piece_index(edges, T):
    t = np.arange(T)
    return np.searchsorted(edges, t, side="right") - 1


def within_fraction(edges, T):
    t = np.arange(T)
    j = np.searchsorted(edges, t, side="right") - 1
    return (t - edges[j]) / (edges[j + 1] - edges[j]).astype(float)


class Struct:
    def __init__(self, D):
        T = D["T"]
        self.T = T
        self.e_chap = edges_from(D["chap_ends"], T)
        self.e_sect = edges_from(D["sect_ends"], T)
        self.e_page = edges_from(D["page_starts"], T)
        self.z3 = within_fraction(self.e_sect, T)
        self.z4 = within_fraction(self.e_page, T)
        self.nbin = int(math.ceil(T / BIN))
        self.bin_len = np.full(self.nbin, BIN, dtype=float)
        self.bin_len[-1] = T - BIN * (self.nbin - 1)
        self.grid = np.unique(np.append(np.arange(0, T, BIN), T))


# ------------------------------------------------------------------ likelihood pieces
def _xlogx_rate(k, n):
    k = np.asarray(k, float)
    n = np.asarray(n, float)
    out = np.zeros_like(k)
    m = k > 0
    out[m] = k[m] * np.log(k[m] / n[m])
    return out - k


def ll_piecewise(ev, edges, w=None):
    """MLE piecewise-constant log-lik. w: optional exposure mask (bool array len T)."""
    if w is None:
        k = np.histogram(ev, bins=edges)[0]
        n = np.diff(edges)
    else:
        k = np.histogram(ev[w[ev]], bins=edges)[0]
        cw = np.concatenate([[0], np.cumsum(w)])
        n = cw[edges[1:]] - cw[edges[:-1]]
    keep = n > 0
    return float(_xlogx_rate(k[keep], n[keep]).sum())


def ll0(ev, T):
    n = len(ev)
    return n * math.log(n / T) - n


def m1c_fit(ev, S, w=None):
    """Optimal partition on the 25-pair grid, K = 0..KMAX change points.
    Returns list of (logL, changepoints) indexed by K."""
    g = S.grid
    if w is None:
        cnt = np.searchsorted(np.sort(ev), g, side="left").astype(float)
        cl = g.astype(float)
    else:
        e2 = np.sort(ev[w[ev]])
        cnt = np.searchsorted(e2, g, side="left").astype(float)
        cw = np.concatenate([[0], np.cumsum(w)])
        cl = cw[g].astype(float)
    m = len(g)
    K_ = cnt[None, :] - cnt[:, None]
    N_ = cl[None, :] - cl[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        seg = np.where(K_ > 0, K_ * np.log(np.where(N_ > 0, K_ / N_, 1.0)), 0.0) - K_
    seg = np.where(np.triu(np.ones((m, m), bool), 1), seg, -np.inf)
    seg = np.where((N_ <= 0) & (K_ > 0), -np.inf, seg)
    seg = np.where((N_ <= 0) & (K_ == 0) & np.triu(np.ones((m, m), bool), 1), 0.0, seg)
    best = seg[0].copy()                      # 1 segment from 0 to j
    arg = []
    out = [(float(best[-1]), [])]
    prev = best
    for K in range(1, KMAX + 1):
        tot = prev[:, None] + seg             # i -> j
        a = np.argmax(tot, axis=0)
        cur = tot[a, np.arange(m)]
        arg.append(a)
        # backtrack
        cps = []
        j = m - 1
        for kk in range(K, 0, -1):
            i = arg[kk - 1][j]
            cps.append(int(g[i]))
            j = i
        out.append((float(cur[-1]), sorted(cps)))
        prev = cur
    return out


def _trans(sig):
    d = LEV[:, None] - LEV[None, :]
    if sig == 0:
        return np.eye(len(LEV))
    P = np.exp(-0.5 * (d / sig) ** 2)
    return P / P.sum(axis=1, keepdims=True)


TRANS = np.stack([_trans(s) for s in SIGMAS])          # (S, L, L)


def bin_counts(ev, S):
    return np.bincount(ev // BIN, minlength=S.nbin).astype(float)


def emissions(k, S, mask=None):
    E = k[:, None] * LEV[None, :] - LAM[None, :] * S.bin_len[:, None]   # (nbin, L)
    if mask is not None:
        E = E * mask[:, None]
    return E


def hmm_ll_all(E):
    """log-lik for every sigma, uniform initial prior. E: (nbin, L)."""
    nS, L = len(SIGMAS), len(LEV)
    a = np.full((nS, L), 1.0 / L)
    tot = np.zeros(nS)
    for b in range(E.shape[0]):
        if b > 0:
            a = np.einsum("sl,slm->sm", a, TRANS)
        e = E[b]
        mx = e.max()
        a = a * np.exp(e - mx)[None, :]
        c = a.sum(axis=1)
        tot += np.log(c) + mx
        a = a / c[:, None]
    return tot


def hmm_smooth(E, si):
    """Posterior mean of lambda and of log-lambda per bin for sigma index si."""
    P = TRANS[si]
    nb, L = E.shape
    al = np.zeros((nb, L))
    a = np.full(L, 1.0 / L)
    for b in range(nb):
        if b > 0:
            a = a @ P
        a = a * np.exp(E[b] - E[b].max())
        a /= a.sum()
        al[b] = a
    be = np.ones(L)
    post = np.zeros((nb, L))
    post[-1] = al[-1]
    for b in range(nb - 2, -1, -1):
        be = P @ (np.exp(E[b + 1] - E[b + 1].max()) * be)
        be /= be.sum()
        p = al[b] * be
        post[b] = p / p.sum()
    return post @ LAM, post @ LEV


def m3_fit(ev, z, w=None):
    """log lam = a + b z ; Newton. Returns (logL, a, b)."""
    if w is None:
        w = np.ones(len(z), bool)
    zt = z[w]
    ze = z[ev[w[ev]]]
    n = len(ze)
    a, b = math.log(max(n, 1) / len(zt)), 0.0
    for _ in range(60):
        lam = np.exp(a + b * zt)
        g = np.array([n - lam.sum(), ze.sum() - (lam * zt).sum()])
        H = -np.array([[lam.sum(), (lam * zt).sum()], [(lam * zt).sum(), (lam * zt * zt).sum()]])
        step = np.linalg.solve(H, g)
        a, b = a - step[0], b - step[1]
        if abs(step).max() < 1e-9:
            break
    lam = np.exp(a + b * zt)
    return float(n * 0 + (a * n + b * ze.sum()) - lam.sum()), float(a), float(b)


KAP = np.exp(np.linspace(math.log(0.2), math.log(4.0), 49))
SCF = np.exp(np.linspace(-0.6, 0.6, 31))


def _gamma_logpdf(g, k, th):
    return (k - 1) * np.log(g) - g / th - gammaln(k) - k * np.log(th)


def _gamma_logsf(c, k, th):
    return np.log(np.maximum(gammaincc(k, c / th), 1e-300))


def m4_fit(ev, T):
    """Gamma renewal; first gap from -1, last gap censored. Grid MLE. Returns (logL, kappa, theta)."""
    g = np.diff(np.concatenate([[-1], ev])).astype(float)
    c = float(T - ev[-1])
    mg = (g.sum() + c) / len(g)
    K = KAP[:, None, None]
    TH = (mg / KAP)[:, None, None] * SCF[None, :, None]
    ll = _gamma_logpdf(g[None, None, :], K, TH).sum(axis=2) + _gamma_logsf(c, K[:, :, 0], TH[:, :, 0])
    i, j = np.unravel_index(np.argmax(ll), ll.shape)
    return float(ll[i, j]), float(KAP[i]), float(mg / KAP[i] * SCF[j])


# ------------------------------------------------------------------ statistics
def ac1(v):
    v = np.asarray(v, float)
    x, y = v[:-1], v[1:]
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def rank(v):
    r = np.empty(len(v))
    r[np.argsort(v, kind="mergesort")] = np.arange(len(v))
    return r


def fano_vec(ev, T):
    out = []
    for W in FANO_W:
        nw = T // W
        c = np.bincount(ev[ev < nw * W] // W, minlength=nw).astype(float)
        out.append(c.var() / c.mean() if c.mean() > 0 else 0.0)
    return out


def fit_all(ev, S, keep_detail=False):
    """Every model + every statistic for one event set. The single code path."""
    ev = np.sort(np.asarray(ev, dtype=np.int64))
    T = S.T
    L = {"M0": ll0(ev, T),
         "M1a": ll_piecewise(ev, S.e_chap),
         "M1b": ll_piecewise(ev, S.e_sect)}
    c = m1c_fit(ev, S)
    bic_c = [-2 * c[K][0] + (2 * K + 1) * LN_NEV for K in range(1, KMAX + 1)]
    Kb = int(np.argmin(bic_c)) + 1
    L["M1c"] = c[Kb][0]
    E = emissions(bin_counts(ev, S), S)
    h = hmm_ll_all(E)
    si = int(np.argmax(h))
    L["M2"] = L["M0"] + float(h[si] - h[0])
    L["M3a"], a3, b3 = m3_fit(ev, S.z3)
    L["M3b"], a4, b4 = m3_fit(ev, S.z4)
    L["M4"], kap, th = m4_fit(ev, T)
    k = {"M0": 1, "M1a": len(S.e_chap) - 1, "M1b": len(S.e_sect) - 1, "M1c": 2 * Kb + 1,
         "M2": 2, "M3a": 2, "M3b": 2, "M4": 2}
    bic = {m: -2 * L[m] + k[m] * LN_NEV for m in MODELS}
    g = np.diff(ev).astype(float)
    s5 = max(2 * (c[K][0] - L["M0"]) - 2 * K * LN_NEV for K in range(1, KMAX + 1))
    r = {"L": L, "k": k, "bic": bic, "choice": min(bic, key=bic.get),
         "S1": ac1(g), "S2": ac1(rank(g)), "S3": float(h[si] - h[0]),
         "fano": fano_vec(ev, T), "S5": float(s5),
         "par": {"M1c_K": Kb, "M1c_cps": c[Kb][1], "M2_sigma": float(SIGMAS[si]), "M2_si": si,
                 "M3a": [a3, b3], "M3b": [a4, b4], "M4": [kap, th]}}
    if keep_detail:
        r["m1c_all"] = c
        r["hmm_ll"] = h.tolist()
    return r


# ------------------------------------------------------------------ simulators (86 events exactly)
def draw_weighted(w, rng):
    p = np.asarray(w, float)
    p = p / p.sum()
    return np.sort(rng.choice(len(p), size=NEV, replace=False, p=p))


def lam_piecewise(edges, logr, T):
    return np.exp(np.asarray(logr)[piece_index(edges, T)])


def lam_rw(S, s, rng, start=0.0):
    steps = rng.normal(0, s, S.nbin)
    steps[0] = 0
    path = start + np.cumsum(steps)
    path -= path.mean()
    return np.exp(np.repeat(path, BIN)[:S.T])


def sim(model, S, rng, sl=None, par=None):
    """sl = Stage-A strength sigma_L; par = Stage-B fitted parameters."""
    T = S.T
    if model == "M0":
        return np.sort(rng.choice(T, size=NEV, replace=False))
    if model in ("M1a", "M1b"):
        e = S.e_chap if model == "M1a" else S.e_sect
        logr = np.log(par) if par is not None else rng.normal(0, sl, len(e) - 1)
        return draw_weighted(lam_piecewise(e, logr, T), rng)
    if model == "M1c":
        if par is not None:
            cps, rates = par
            e = np.array([0] + list(cps) + [T])
            logr = np.log(rates)
        else:
            e = np.array([0] + sorted(rng.choice(np.arange(1, T), 4, replace=False).tolist()) + [T])
            logr = rng.normal(0, sl, 5)
        return draw_weighted(lam_piecewise(e, logr, T), rng)
    if model == "M2":
        s = par if par is not None else sl * math.sqrt(6.0 / S.nbin)
        return draw_weighted(lam_rw(S, s, rng), rng)
    if model in ("M3a", "M3b"):
        z = S.z3 if model == "M3a" else S.z4
        if par is not None:
            b = par
        else:
            b = (sl / 0.2887) * (1 if rng.random() < 0.5 else -1)
        return draw_weighted(np.exp(b * z), rng)
    if model == "M4":
        kap = par if par is not None else (0.6 if sl == 0.5 else 0.4)
        while True:
            gg = rng.gamma(kap, 1.0, NEV + 1)
            pos = np.floor(np.cumsum(gg)[:NEV] / gg.sum() * T).astype(np.int64)
            pos = np.clip(pos, 0, T - 1)
            if len(np.unique(pos)) == NEV:
                return pos
    raise ValueError(model)


def addone_upper(null, obs):
    null = np.asarray(null, float)
    return float((1 + (null >= obs).sum()) / (len(null) + 1))


def addone_two(null, obs):
    null = np.asarray(null, float)
    lo = (1 + (null <= obs).sum()) / (len(null) + 1)
    hi = (1 + (null >= obs).sum()) / (len(null) + 1)
    return float(min(1.0, 2 * min(lo, hi)))
