"""Round 18 / L4-FORCING — POST-HOC confound analysis for the Arm A / A1 hit.

DECLARED AS POST-HOC. Arm A was pre-registered and A1 (line-initial runes) cleared
its gate. This script does not change that result; it asks the question any hit has
to survive: *is there a non-cryptographic process that produces it?*

The candidate confound is typographic, and it is the classic inspection paradox.
LP2 breaks words across lines (see the transcription's hyphen-free continuations),
so the line breaks are not linguistic — they are a greedy fill against a fixed
column width. Under a greedy fill the rune that *straddles* the right margin is the
one pushed to the start of the next line, and a rune is length-biased into that role
in proportion to its glyph width:

        P(rune r starts a line)  ~  p(r) * width(r)

That predicts an excess of wide runes at line-initial position and NO corresponding
effect at line-final position -- which is exactly the shape of the observed A1/A2 pair.

Three tests, in increasing strength:
  T1  fit per-token widths from the 594 observed line compositions (least squares,
      the fill target W is what makes every full line the same physical width) and
      check the fit is much tighter than an equal-width (rune-count) model;
  T2  correlate those fitted widths with the A1 per-rune excess, and cross-validate
      (fit widths on odd lines, predict the line-initial histogram of even lines);
  T3  the decisive one -- REFLOW. Re-run the greedy line-breaker on the real token
      stream and check it reproduces the real line breaks; then build a null by
      shuffling the rune stream, reflowing, and recomputing the A1 chi-square. If the
      observed 78.66 sits inside that null, layout explains the hit with no forcing.

An external cross-check uses the BabelStone Runic advance widths shipped in
corpus/E-tooling/ (a different, independent source of relative rune widths).
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp  # noqa: E402
from parse_structure import Geometry  # noqa: E402

KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")
FONT = os.path.join(ROOT, "corpus", "E-tooling", "vendor", "0x676f64__Cicada-3301",
                    "iddqd", "ttf", "BabelStoneRunicBeorhtnoth.ttf")
N = 29
SEP = {"-": N, ".": N + 1}          # two extra "tokens" with their own widths
NTOK = N + 2


# ------------------------------------------------------------------ tokenising
def token_lines(n_pages=55):
    """[(page, [token ids])] per physical line, separators included, in book order."""
    txt = open(KRIS, encoding="utf-8").read()
    out, page, cur = [], 0, []
    for ch in txt:
        if ch == "%":
            if cur:
                out.append((page, cur)); cur = []
            page += 1
            continue
        if page >= n_pages:
            continue
        if ch == "/":
            out.append((page, cur)); cur = []
            continue
        if ch in SEP:
            cur.append(SEP[ch]); continue
        if gp.is_rune(ch):
            cur.append(gp.RUNE_TO_IDX[ch]); continue
    if cur:
        out.append((page, cur))
    return [(p, t) for p, t in out if any(v < N for v in t)]


def counts_matrix(lines):
    M = np.zeros((len(lines), NTOK))
    for i, (_, toks) in enumerate(lines):
        for t in toks:
            M[i, t] += 1
    return M


# ------------------------------------------------------------------ T1: fit widths
def fit_widths(lines, use=None, ridge=1e-3):
    """Least squares w s.t. every FULL line has total width 1."""
    M = counts_matrix(lines)
    Mf = M[use] if use is not None else M
    y = np.ones(Mf.shape[0])
    A = Mf.T @ Mf + ridge * np.eye(NTOK)
    w = np.linalg.solve(A, Mf.T @ y)
    return w, M


def full_line_mask(lines):
    """A line is width-limited unless it is the last line of its page."""
    pages = [p for p, _ in lines]
    mask = np.ones(len(lines), dtype=bool)
    for i in range(len(lines)):
        if i == len(lines) - 1 or pages[i + 1] != pages[i]:
            mask[i] = False
    return mask


# ------------------------------------------------------------------ T3: reflow
def reflow(tokens, w, budget):
    """Greedy fill: break BEFORE the token that would overflow the budget."""
    lines, cur, acc = [], [], 0.0
    for t in tokens:
        if cur and acc + w[t] > budget:
            lines.append(cur); cur = []; acc = 0.0
        cur.append(t); acc += w[t]
    if cur:
        lines.append(cur)
    return lines


def line_initial_runes(lines):
    out = []
    for L in lines:
        for t in L:
            if t < N:
                out.append(t); break
    return out


def chi2_vs(counts, p_ref, k):
    e = p_ref * k
    return float(((counts - e) ** 2 / e).sum())


def main(nnull=2000, seed=3301):
    rng = np.random.default_rng(seed)
    g = Geometry()
    x = np.array(g.runes)
    p_full = np.bincount(x, minlength=N) / len(x)

    obs_init = np.array([g.runes[i] for i in g.subsets()["A1_line_initial"]])
    obs_counts = np.bincount(obs_init, minlength=N).astype(float)
    obs_chi2 = chi2_vs(obs_counts, p_full, len(obs_init))

    lines = token_lines()
    assert len(lines) == 594, len(lines)
    mask = full_line_mask(lines)
    print(f"lines={len(lines)}  full(width-limited)={mask.sum()}")

    # ---- T1 -------------------------------------------------------------
    w, M = fit_widths(lines, use=mask)
    tot = M[mask] @ w
    # equal-width baseline: all tokens width 1, target = mean token count
    Meq = counts_matrix(lines)[mask].sum(axis=1)
    cv_fit = tot.std() / tot.mean()
    cv_eq = Meq.std() / Meq.mean()
    print(f"T1  fitted-width line totals : cv = {cv_fit:.4f}")
    print(f"T1  equal-width (rune count) : cv = {cv_eq:.4f}   "
          f"-> width model tightens line extent by {cv_eq / cv_fit:.2f}x")

    wr = w[:N]
    order = np.argsort(-wr)
    print("T1  fitted relative rune widths (widest first):")
    print("    " + "  ".join(f"{gp.IDX_TO_TRANS[i]}:{wr[i] / wr.mean():.2f}" for i in order))
    print(f"    separators  '-':{w[N] / wr.mean():.2f}  '.':{w[N + 1] / wr.mean():.2f}")

    # external font cross-check
    font_w = None
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(FONT)
        cm = f.getBestCmap(); hm = f["hmtx"]; upm = f["head"].unitsPerEm
        font_w = np.array([hm[cm[ord(gp.IDX_TO_RUNE[i])]][0] / upm for i in range(N)])
        r = np.corrcoef(wr, font_w)[0, 1]
        print(f"T1  external check: corr(fitted width, BabelStone advance width) = {r:+.3f}")
    except Exception as e:  # pragma: no cover
        print("T1  external font check unavailable:", e)

    # ---- T2 -------------------------------------------------------------
    excess = np.log((obs_counts + 0.5) / (p_full * len(obs_init) + 0.5))
    r_w = np.corrcoef(wr, excess)[0, 1]
    print(f"T2  corr(fitted width, line-initial log excess) = {r_w:+.3f}")
    if font_w is not None:
        print(f"T2  corr(font width,   line-initial log excess) = "
              f"{np.corrcoef(font_w, excess)[0, 1]:+.3f}")

    # size-biased prediction q ~ p*w, chi-square of the observed initials against it
    q = p_full * wr
    q = q / q.sum()
    chi2_q = chi2_vs(obs_counts, q, len(obs_init))
    print(f"T2  chi2 of line-initials vs FLAT model   = {obs_chi2:8.3f}")
    print(f"T2  chi2 of line-initials vs SIZE-BIASED  = {chi2_q:8.3f}  "
          f"(28 df; drop of {obs_chi2 - chi2_q:.1f})")

    # cross-validated: fit widths on odd full lines, predict even lines' initials
    odd = mask.copy(); odd[::2] = False
    w_odd, _ = fit_widths(lines, use=odd)
    even_idx = [i for i in range(len(lines)) if i % 2 == 0]
    ev_init = np.array(line_initial_runes([lines[i][1] for i in even_idx]))
    ev_counts = np.bincount(ev_init, minlength=N).astype(float)
    q_odd = p_full * w_odd[:N]; q_odd = q_odd / q_odd.sum()
    print(f"T2  CV: even-line initials  chi2 vs flat = "
          f"{chi2_vs(ev_counts, p_full, len(ev_init)):7.3f}   vs size-biased(odd-fit) = "
          f"{chi2_vs(ev_counts, q_odd, len(ev_init)):7.3f}")

    # ---- T3 reflow ------------------------------------------------------
    toks = [t for _, L in lines for t in L]
    budget = float(np.median(M[mask] @ w))
    best = None
    for b in np.linspace(budget * 0.90, budget * 1.10, 201):
        rl = reflow(toks, w, b)
        if best is None or abs(len(rl) - 594) < abs(len(best[1]) - 594):
            best = (b, rl)
    b, rl = best
    # agreement, drift-free: RESYNCHRONISE at every real line start and ask whether
    # the greedy filler ends the line where the book does. (An absolute-offset
    # comparison is worthless here: one early break shifts every later one.)
    hit = 0
    for _, L in lines:
        acc, k = 0.0, 0
        for t in L:
            if k and acc + w[t] > b:
                break
            acc += w[t]; k += 1
        if k == len(L):
            hit += 1
    agree = hit / len(lines)
    # distribution of predicted-minus-actual line length, resynchronised
    errs = []
    toks_flat = [t for _, L in lines for t in L]
    off = 0
    for _, L in lines:
        acc, k = 0.0, 0
        j = off
        while j < len(toks_flat):
            t = toks_flat[j]
            if k and acc + w[t] > b:
                break
            acc += w[t]; k += 1; j += 1
        errs.append(k - len(L))
        off += len(L)
    errs = np.array(errs)
    print(f"T3  reflow budget {b:.4f} -> {len(rl)} lines (real 594)")
    print(f"T3  resynchronised per-line accuracy: {agree:.3f} exact  "
          f"(|err|<=1: {(np.abs(errs) <= 1).mean():.3f})  mean err {errs.mean():+.3f}")

    # null: shuffle runes (keep separator positions), reflow, chi-square.
    # Also carried for the other three line-position subsets, which are exposed to
    # the same geometry and therefore need the same null, not the flat one.
    def subsets_from_lines(rlines):
        first, last, second, penult = [], [], [], []
        for L in rlines:
            rs = [t for t in L if t < N]
            if not rs:
                continue
            first.append(rs[0]); last.append(rs[-1])
            if len(rs) > 1:
                second.append(rs[1]); penult.append(rs[-2])
        return {"A1": first, "A2": last, "A9": second, "A10": penult}

    tarr = np.array(toks)
    is_rune = tarr < N
    keys = ["A1", "A2", "A9", "A10"]
    nulls = {k: np.empty(nnull) for k in keys}
    for i in range(nnull):
        tt = tarr.copy()
        v = tt[is_rune].copy(); rng.shuffle(v); tt[is_rune] = v
        rlines = reflow(list(tt), w, b)
        for k, vals in subsets_from_lines(rlines).items():
            c = np.bincount(np.array(vals), minlength=N).astype(float)
            nulls[k][i] = chi2_vs(c, p_full, len(vals))
    null = nulls["A1"]

    real_lines = [L for _, L in lines]
    obs_sub = subsets_from_lines(real_lines)
    print("T3  layout-aware null vs flat null, per line-position subset:")
    layout_table = {}
    for k in keys:
        vals = obs_sub[k]
        c = np.bincount(np.array(vals), minlength=N).astype(float)
        o = chi2_vs(c, p_full, len(vals))
        pl = (1.0 + np.sum(nulls[k] >= o)) / (1.0 + nnull)
        layout_table[k] = {"n": len(vals), "obs_chi2": o,
                           "layout_null_mean": float(nulls[k].mean()),
                           "layout_null_p95": float(np.quantile(nulls[k], .95)),
                           "p_layout": float(pl)}
        print(f"    {k:4s} n={len(vals):4d}  obs={o:7.2f}  layout-null mean="
              f"{nulls[k].mean():6.2f} p95={np.quantile(nulls[k], .95):6.2f}  "
              f"p_layout={pl:.4f}")
    p_layout = layout_table["A1"]["p_layout"]
    print(f"T3  LAYOUT-AWARE NULL (n={nnull}): mean {null.mean():.2f}  sd {null.std():.2f}  "
          f"95% {np.quantile(null, .95):.2f}  max {null.max():.2f}")
    print(f"T3  observed {obs_chi2:.2f}  ->  p_layout = {p_layout:.5f}")

    # flat null for contrast (positions resampled, no layout)
    flat = np.empty(nnull)
    for i in range(nnull):
        c = rng.multivariate_hypergeometric(
            np.bincount(x, minlength=N).astype(np.int64), len(obs_init))
        flat[i] = chi2_vs(c.astype(float), p_full, len(obs_init))
    print(f"T3  FLAT null (n={nnull}):        mean {flat.mean():.2f}  sd {flat.std():.2f}  "
          f"95% {np.quantile(flat, .95):.2f}  max {flat.max():.2f}")

    out = {
        "observed_chi2_line_initial": obs_chi2,
        "T1_cv_fitted": cv_fit, "T1_cv_equal_width": cv_eq,
        "T1_fitted_widths": {gp.IDX_TO_TRANS[i]: float(wr[i] / wr.mean()) for i in range(N)},
        "T1_corr_fitted_vs_font": (None if font_w is None
                                   else float(np.corrcoef(wr, font_w)[0, 1])),
        "T2_corr_width_vs_excess": float(r_w),
        "T2_chi2_vs_size_biased": chi2_q,
        "T3_reflow_agreement": agree, "T3_reflow_budget": b, "T3_reflow_nlines": len(rl),
        "T3_layout_null_mean": float(null.mean()), "T3_layout_null_sd": float(null.std()),
        "T3_layout_null_p95": float(np.quantile(null, .95)),
        "T3_layout_null_max": float(null.max()),
        "T3_p_layout": float(p_layout),
        "T3_flat_null_mean": float(flat.mean()), "T3_flat_null_p95": float(np.quantile(flat, .95)),
        "n_null": nnull,
        "T3_layout_table": layout_table,
        "T3_reflow_err_within1": float((np.abs(errs) <= 1).mean()),
    }
    json.dump(out, open(os.path.join(HERE, "results_confound_layout.json"), "w"), indent=2)
    print("wrote results_confound_layout.json")
    return out


if __name__ == "__main__":
    main(nnull=int(sys.argv[1]) if len(sys.argv) > 1 else 2000)
