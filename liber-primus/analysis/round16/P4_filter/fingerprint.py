"""Round 16 lane P4 -- FILTER FINGERPRINT.

Not an attack on the key. A *discriminator*: does the ~81% doublet suppression in the
12,956-rune unsolved LP2 stream look like a coded filter (`if c[i]==c[i-1]: redraw`)
or like a human calligrapher applying a "don't write the same rune twice" rule by hand?

`FINAL-SYNTHESIS.md:73-76` asserts the second ("a human calligrapher applying a rule by
hand while inscribing the book"). Register item D-01 (`analysis/round10/RECON-A/REGISTER.md:65`)
records that the sub-tests which would decide it were never run. This module runs them.

It matters because it says which pad families can exist:
  MACHINE -> the pad came out of a program that ingested bytes from somewhere
             (seeded generator / system CSPRNG / an IMPORTED PUBLIC BYTE SOURCE = P0-P3).
  HAND    -> the pad is human-generated "randomness", which is non-uniform far beyond
             lag 1 (Wagenaar 1972; Rapoport & Budescu 1997) and is therefore a
             *statistically attackable* pad -> joint decode under a key prior, an attack
             nobody in this repo has attempted.

This file is measurement only. Generators + power live in `controls.py`.

Transcription used: `liber-primus/data/krisyotam_runes.txt` -- the SAME file
`analysis/run_stats.py:load_pages()` reads, split on '%' page marks, with '/' line marks
retained for the placement tests. Verified rune-for-rune identical to
`round11/lib_numchannel.unsolved()` (assert in `load_structure`).

Run:  PYTHONUTF8=1 python fingerprint.py
"""
import os, sys, io, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))          # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))

from lp import gematria as gp                      # noqa: E402
import lib_numchannel as nc                        # noqa: E402

N = gp.N                                           # 29
Q = 1.0 / N                                        # chance equality rate = 3.4483%
INTERRUPTER = gp.RUNE_TO_IDX[gp.INTERRUPTER]       # rune F, index 0
KRIS = os.path.normpath(os.path.join(ROOT, "data", "krisyotam_runes.txt"))


# --------------------------------------------------------------- structure
def load_structure():
    """Return (stream, struct) for the 12,956-rune unsolved LP2 stream.

    struct holds, per rune: page ordinal, global line ordinal, line-within-page,
    position-in-line, position-in-page, and the length of the containing line/page.
    """
    txt = io.open(KRIS, encoding="utf-8").read()
    stream, page, line, line_in_page, pos_in_line, pos_in_page = [], [], [], [], [], []
    pg = 0
    gline = 0
    kept = [s for s in txt.split("%") if gp.runes_to_indices(s)]
    # kept[:-2] = unsolved pages 0-54, kept[-2] = AN END (solved), kept[-1] = PARABLE
    for s in kept[:-2]:
        lp_, pl, pp = 0, 0, 0
        for ch in s:
            if ch in gp.RUNE_TO_IDX:
                stream.append(gp.RUNE_TO_IDX[ch])
                page.append(pg); line.append(gline); line_in_page.append(lp_)
                pos_in_line.append(pl); pos_in_page.append(pp)
                pl += 1; pp += 1
            elif ch == "/":
                gline += 1; lp_ += 1; pl = 0
        gline += 1; pg += 1
    assert stream == nc.unsolved(), "structure loader disagrees with lib_numchannel.unsolved()"
    st = {k: np.asarray(v, dtype=np.int64) for k, v in
          dict(page=page, line=line, line_in_page=line_in_page,
               pos_in_line=pos_in_line, pos_in_page=pos_in_page).items()}
    st["n_pages"] = int(st["page"].max()) + 1
    st["page_len"] = np.bincount(st["page"])[st["page"]]
    st["line_len"] = np.bincount(st["line"])[st["line"]]
    return np.asarray(stream, dtype=np.int64), st


# --------------------------------------------------------------- helpers
def _binom_z(k, m, p):
    if m <= 0 or p <= 0 or p >= 1:
        return 0.0
    return (k - m * p) / math.sqrt(m * p * (1 - p))


def _ks_two_sample(sample, reference):
    """Two-sample KS statistic: is `sample` drawn from the empirical law of `reference`?"""
    if len(sample) == 0:
        return 0.0
    ref = np.sort(np.asarray(reference, dtype=float))
    s = np.sort(np.asarray(sample, dtype=float))
    grid = np.unique(np.concatenate([s, ref]))
    Fs = np.searchsorted(s, grid, side="right") / len(s)
    Fr = np.searchsorted(ref, grid, side="right") / len(ref)
    return float(np.max(np.abs(Fs - Fr)))


# --------------------------------------------------------------- battery
def lag_profile(x, kmax=8):
    """TEST 1. Equality rate at lags 1..kmax with a binomial(1/29) null.

    A coded `if c[i]==c[i-1]` filter touches lag 1 and NOTHING else.
    A human anti-repeat habit is a recency-avoidance habit and bleeds into lags 2-3
    (Wagenaar 1972; Rapoport & Budescu 1997)."""
    out = {}
    for k in range(1, kmax + 1):
        eq = int((x[k:] == x[:-k]).sum()); m = len(x) - k
        out["lag%d_rate" % k] = eq / m
        out["lag%d_z" % k] = _binom_z(eq, m, Q)
    eq = sum(int((x[k:] == x[:-k]).sum()) for k in range(2, kmax + 1))
    m = sum(len(x) - k for k in range(2, kmax + 1))
    out["bleed28_rate"] = eq / m
    out["bleed28_z"] = _binom_z(eq, m, Q)
    eq3 = sum(int((x[k:] == x[:-k]).sum()) for k in (2, 3))
    m3 = sum(len(x) - k for k in (2, 3))
    out["bleed23_rate"] = eq3 / m3
    out["bleed23_z"] = _binom_z(eq3, m3, Q)
    # fraction of the lag-1 suppression that leaks to lags 2..8  (0 = pure machine)
    s1 = 1.0 - out["lag1_rate"] / Q
    sb = 1.0 - out["bleed28_rate"] / Q
    out["bleed_fraction"] = sb / s1 if s1 > 1e-9 else 0.0
    return out


def run_alternation(x):
    """TEST 2. Run-length / alternation / repeat-gap structure."""
    out = {}
    d = (x[1:] == x[:-1])
    out["run2"] = int(d.sum())
    out["run3"] = int((d[1:] & d[:-1]).sum())
    # ABAB alternation: x[i]==x[i-2] and x[i-1]==x[i-3] and x[i]!=x[i-1]
    a = x[3:]; b = x[2:-1]; c = x[1:-2]; e = x[:-3]
    ab = ((a == c) & (b == e) & (a != b))
    out["abab"] = int(ab.sum())
    out["abab_rate"] = float(ab.mean())
    out["abab_z"] = _binom_z(int(ab.sum()), len(ab), Q * Q)
    # gap to the previous occurrence of the same rune (recency-avoidance detector)
    order = np.argsort(x, kind="stable")          # positions grouped by rune value
    sv = x[order]
    g = np.diff(order).astype(float)
    gaps = g[np.diff(sv) == 0]                    # keep only within-value successors
    out["gap_mean"] = float(gaps.mean())
    out["gap_cv"] = float(gaps.std() / gaps.mean())
    p4 = 1 - (1 - Q) ** 4                              # P(gap<=4) under iid
    k4 = int((gaps <= 4).sum())
    out["gap_le4_rate"] = k4 / len(gaps)
    out["gap_le4_z"] = _binom_z(k4, len(gaps), p4)
    # same, conditioned on gap>=2 -- isolates the human bleed from the machine lag-1 cut
    p24 = ((1 - Q) - (1 - Q) ** 4) / (1 - Q)
    denom = int((gaps >= 2).sum())
    k24 = int(((gaps >= 2) & (gaps <= 4)).sum())
    out["gap_2to4_rate"] = k24 / denom
    out["gap_2to4_z"] = _binom_z(k24, denom, p24)
    return out


def window_balance(x, windows=(29, 58, 116, 290)):
    """TEST 3 (D-01's named sub-test). Windowed chi-square UNDER-dispersion sweep.

    A human who thinks "that rune has come up too often lately" rebalances the histogram
    inside a short window, driving the per-window chi-square BELOW its df. Expected cell
    counts use the stream's own global marginals, so marginal non-uniformity cannot
    masquerade as over-dispersion."""
    out = {}
    n = len(x)
    p = np.bincount(x, minlength=N) / n
    for W in windows:
        nw = n // W
        if nw < 3:
            continue
        M = x[: nw * W].reshape(nw, W)
        counts = np.zeros((nw, N))
        for v in range(N):
            counts[:, v] = (M == v).sum(axis=1)
        exp = W * p
        chi = ((counts - exp) ** 2 / np.maximum(exp, 1e-12)).sum(axis=1)
        df = N - 1
        out["chi2W%d_mean" % W] = float(chi.mean() / df)   # 1.0 = iid; <1 = rebalanced
        out["chi2W%d_sd" % W] = float(chi.std() / math.sqrt(2 * df))
    return out


def drift(x, st):
    """TEST 4. Monogram drift / fatigue across the book, and drift of the suppression
    rate itself. A tiring hand drifts; a loop does not."""
    out = {}
    pages = st["page"]; npg = st["n_pages"]
    tab = np.zeros((npg, N))
    for pgi in range(npg):
        tab[pgi] = np.bincount(x[pages == pgi], minlength=N)
    row = tab.sum(axis=1, keepdims=True); col = tab.sum(axis=0, keepdims=True)
    exp = row @ col / tab.sum()
    chi = ((tab - exp) ** 2 / np.maximum(exp, 1e-12)).sum()
    df = (npg - 1) * (N - 1)
    out["page_homog_chi2_df"] = float(chi / df)
    out["page_homog_z"] = float((chi - df) / math.sqrt(2 * df))
    h = len(x) // 2
    t2 = np.vstack([np.bincount(x[:h], minlength=N), np.bincount(x[h:], minlength=N)]).astype(float)
    e2 = t2.sum(axis=1, keepdims=True) @ t2.sum(axis=0, keepdims=True) / t2.sum()
    chi2h = float(((t2 - e2) ** 2 / np.maximum(e2, 1e-12)).sum())
    out["half_split_chi2_df"] = chi2h / (N - 1)
    out["half_split_z"] = (chi2h - (N - 1)) / math.sqrt(2 * (N - 1))
    d = (x[1:] == x[:-1]).astype(float)
    t = np.arange(len(d)) / len(d)
    r = float(np.corrcoef(d, t)[0, 1]) if d.std() > 0 else 0.0
    out["supp_drift_r"] = r
    out["supp_drift_z"] = r * math.sqrt(len(d))
    return out


def page_rate_constancy(x, st):
    """TEST 6. Is the suppression rate constant across the book?
    Binomial dispersion of the per-page doublet count around one fitted rate.
    A hand-applied filter has a VARIABLE miss rate (over-dispersion); a probabilistic
    coded filter has a constant one (dispersion == 1)."""
    pages = st["page"]; npg = st["n_pages"]
    d = (x[1:] == x[:-1])
    dp = pages[1:]
    same = pages[1:] == pages[:-1]          # only within-page adjacencies
    obs = np.zeros(npg); mm = np.zeros(npg)
    for pgi in range(npg):
        sel = same & (dp == pgi)
        mm[pgi] = sel.sum()
        obs[pgi] = d[sel].sum()
    phat = obs.sum() / mm.sum()
    exp = mm * phat
    var = mm * phat * (1 - phat)
    keep = var > 0
    k = int(keep.sum())
    disp = float((((obs - exp) ** 2 / var)[keep]).sum() / (k - 1))
    return {"page_supp_rate": float(phat),
            "page_rate_dispersion": disp,               # 1.0 = constant rate
            "page_rate_disp_z": float((disp - 1) * math.sqrt((k - 1) / 2.0)),
            "page_doublets_min": float(obs.min()),
            "page_doublets_max": float(obs.max()),
            "pages_with_zero_doublets": int((obs == 0).sum())}


def doublet_placement(x, st):
    """TEST 5. Where do the residual doublets sit?

    A filter with a SCOPE leaks its implementation: a calligrapher checking "the rune I
    just wrote" loses the check across a line break or a page turn, so residuals pile up
    at boundaries. A filter running over the flat stream cannot know a line exists."""
    out = {}
    d = np.flatnonzero(x[1:] == x[:-1]) + 1        # index of the SECOND rune of a doublet
    out["n_doublets"] = int(len(d))
    if len(d) < 2:
        return out
    line, page = st["line"], st["page"]
    cross_line = (line[d] != line[d - 1])
    cross_page = (page[d] != page[d - 1])
    base_line = float((line[1:] != line[:-1]).mean())
    base_page = float((page[1:] != page[:-1]).mean())
    out["dbl_line_cross"] = int(cross_line.sum())
    out["dbl_line_cross_rate"] = float(cross_line.mean())
    out["base_line_cross_rate"] = base_line
    out["dbl_line_cross_z"] = _binom_z(int(cross_line.sum()), len(d), base_line)
    out["dbl_page_cross"] = int(cross_page.sum())
    out["dbl_page_cross_z"] = _binom_z(int(cross_page.sum()), len(d), base_page)
    pl = st["pos_in_line"] / np.maximum(st["line_len"], 1)
    pp = st["pos_in_page"] / np.maximum(st["page_len"], 1)
    out["dbl_posinline_ks"] = _ks_two_sample(pl[d], pl)
    out["dbl_posinpage_ks"] = _ks_two_sample(pp[d], pp)
    out["dbl_posinline_mean"] = float(pl[d].mean()); out["base_posinline_mean"] = float(pl.mean())
    out["dbl_posinpage_mean"] = float(pp[d].mean()); out["base_posinpage_mean"] = float(pp.mean())
    g = np.diff(d).astype(float)
    out["dbl_gap_mean"] = float(g.mean())
    out["dbl_gap_disp"] = float(g.var() / g.mean() ** 2)      # 1.0 = Poisson
    ip = np.flatnonzero(x == INTERRUPTER)
    if len(ip):
        def _nd(pos):
            j = np.searchsorted(ip, pos)
            lo = ip[np.maximum(j - 1, 0)]; hi = ip[np.minimum(j, len(ip) - 1)]
            return np.minimum(np.abs(pos - lo), np.abs(pos - hi))
        dist = _nd(d); dist_all = _nd(np.arange(len(x)))
        sd = dist_all.std() / math.sqrt(len(d))
        out["dbl_interrupter_dist_mean"] = float(dist.mean())
        out["base_interrupter_dist_mean"] = float(dist_all.mean())
        out["dbl_interrupter_z"] = float((dist.mean() - dist_all.mean()) / sd) if sd > 0 else 0.0
    return out


def conditional_next(x):
    """D-01 sub-test (1). Conditional next-rune distribution after each rune value:
    the 29x29 bigram table with the diagonal REMOVED, tested for independence.
    A hand rule that also avoids visually-similar runes shows up off the diagonal;
    `if c==c_prev` shows nothing off the diagonal."""
    tab = np.bincount(x[:-1] * N + x[1:], minlength=N * N).reshape(N, N).astype(float)
    off = tab.copy()
    np.fill_diagonal(off, 0.0)
    r = off.sum(axis=1); c = off.sum(axis=0); T = off.sum()
    exp = np.outer(r, c) / T
    np.fill_diagonal(exp, 0.0)
    rs = exp.sum(axis=1, keepdims=True)
    exp = np.where(rs > 0, exp * (r[:, None] / np.maximum(rs, 1e-12)), 0.0)
    m = exp > 0
    chi = float((((off - exp) ** 2 / np.maximum(exp, 1e-12))[m]).sum())
    df = int(m.sum()) - 2 * (N - 1) - 1
    return {"bigram_offdiag_chi2_df": chi / df,
            "bigram_offdiag_z": (chi - df) / math.sqrt(2 * df)}


# --------------------------------------------------------------- driver
def measure(x, st):
    """Full battery on one stream. `st` supplies line/page structure (tests 4-6)."""
    x = np.asarray(x, dtype=np.int64)
    out = {}
    out.update(lag_profile(x))
    out.update(run_alternation(x))
    out.update(window_balance(x))
    out.update(drift(x, st))
    out.update(page_rate_constancy(x, st))
    out.update(doublet_placement(x, st))
    out.update(conditional_next(x))
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    x, st = load_structure()
    print("stream n=%d  pages=%d  lines=%d" % (len(x), st["n_pages"], int(st["line"].max()) + 1))
    m = measure(x, st)
    for k in sorted(m):
        print("  %-32s %+.6f" % (k, m[k]))
    json.dump({"n": int(len(x)), "n_pages": int(st["n_pages"]),
               "n_lines": int(st["line"].max()) + 1,
               "transcription": "data/krisyotam_runes.txt",
               "real": m},
              open(os.path.join(HERE, "real_measure.json"), "w"), indent=1)
