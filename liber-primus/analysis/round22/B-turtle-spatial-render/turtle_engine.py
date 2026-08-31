"""Round 22 Lane B — turtle-graphics render + geometry structure detector.

"The numbers are the direction." Reads the LP2 value / prime-index / totient stream
as turtle turn+step instructions, renders the path, and runs a 6-stat geometry
detector against a size-matched, histogram-preserving, order-destroyed shuffle null
(seed 3301). Pure stdlib + numpy + PIL. No English scorer touches this lane.

Trust: reuses round11/lib_numchannel.py, which is gated by round11/PHASE0-GATE.py and
the repo-wide tests/validate.py (both PASS as of 2026-08-29).
"""
import os, sys, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R11 = os.path.abspath(os.path.join(HERE, "..", "..", "round11"))
sys.path.insert(0, R11)
import lib_numchannel as lc  # noqa: E402

MODULI = [4, 6, 8, 12, 29, 360]
STREAMS = {"value": lc.v_prime, "pi": lc.v_prime_index, "phi": lc.v_totient}
TURN_INTERP = ["absolute", "relative"]
STEP_RULES = ["unit", "value"]

RASTER = 128  # detector raster resolution


# ----------------------------------------------------------------- turtle
def walk(values, modulus, turn_interp, step_rule):
    """Return (xs, ys) float arrays of the turtle path.

    - heading contribution per step = (value % modulus) * (360/modulus) degrees.
    - absolute: heading is set to that angle each step (compass read).
    - relative: heading accumulates (classic turtle turn).
    - step length: 1 (unit) or the value magnitude (value), normalised so the
      longest single step = 1 to keep coordinates finite (vector stats are
      scale-invariant ratios, so this does not affect them).
    """
    vals = np.asarray(values, dtype=np.float64)
    unit = 360.0 / modulus
    ang = (np.mod(vals, modulus)) * unit  # degrees
    if turn_interp == "relative":
        heading = np.cumsum(ang)
    else:
        heading = ang
    rad = np.deg2rad(heading)
    if step_rule == "value":
        steps = vals / (vals.max() if vals.max() > 0 else 1.0)
    else:
        steps = np.ones_like(vals)
    dx = steps * np.cos(rad)
    dy = steps * np.sin(rad)
    xs = np.concatenate([[0.0], np.cumsum(dx)])
    ys = np.concatenate([[0.0], np.cumsum(dy)])
    return xs, ys


# ------------------------------------------------------------- rasterize
def rasterize(xs, ys, res=RASTER, subsamples=8):
    """Vectorised raster: mark visited cells by densely sampling every segment
    with a fixed number of interior points (no Python per-segment loop). At
    unit step, cells are ~1 apart in world units and RASTER=128 spans the whole
    path, so `subsamples`=8 fills lines with no gaps at this resolution."""
    minx, maxx = xs.min(), xs.max()
    miny, maxy = ys.min(), ys.max()
    w = max(maxx - minx, 1e-9)
    h = max(maxy - miny, 1e-9)
    scale = (res - 1) / max(w, h)
    x0, y0 = xs[:-1], ys[:-1]
    x1, y1 = xs[1:], ys[1:]
    ts = np.linspace(0.0, 1.0, subsamples).reshape(1, -1)  # (1, S)
    # broadcast: (nseg, S)
    sx = x0[:, None] + ts * (x1 - x0)[:, None]
    sy = y0[:, None] + ts * (y1 - y0)[:, None]
    gx = np.clip(((sx - minx) * scale).astype(np.int64).ravel(), 0, res - 1)
    gy = np.clip(((sy - miny) * scale).astype(np.int64).ravel(), 0, res - 1)
    grid = np.zeros((res, res), dtype=bool)
    grid[gy, gx] = True
    return grid


# ------------------------------------------------------------- detector
def _ccw_v(ax, ay, bx, by, cx, cy):
    return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)


def _seg_intersections_sampled(xs, ys, max_pairs=60000, rng=None):
    """Count crossing segment pairs on a random sample of pairs, scaled up.
    Vectorised proper-crossing test. Deterministic given rng; same sampler for
    real + null."""
    n = len(xs) - 1
    if n < 4:
        return 0.0
    if rng is None:
        rng = np.random.default_rng(3301)
    total_pairs = n * (n - 1) / 2.0
    k = int(min(max_pairs, total_pairs))
    ia = rng.integers(0, n, size=k)
    ib = rng.integers(0, n, size=k)
    keep = np.abs(ia - ib) >= 2
    ia, ib = ia[keep], ib[keep]
    if len(ia) == 0:
        return 0.0
    ax, ay = xs[ia], ys[ia]
    bx, by = xs[ia + 1], ys[ia + 1]
    cx, cy = xs[ib], ys[ib]
    dx, dy = xs[ib + 1], ys[ib + 1]
    c1 = _ccw_v(ax, ay, cx, cy, dx, dy) != _ccw_v(bx, by, cx, cy, dx, dy)
    c2 = _ccw_v(ax, ay, bx, by, cx, cy) != _ccw_v(ax, ay, bx, by, dx, dy)
    cnt = int(np.count_nonzero(c1 & c2))
    return cnt / len(ia) * total_pairs  # estimated total crossings


def _components(grid):
    """4-connected component count of the boolean grid (scipy label)."""
    from scipy import ndimage
    _, n = ndimage.label(grid)
    return n


def _iou(a, b):
    u = np.logical_or(a, b).sum()
    return (np.logical_and(a, b).sum() / u) if u else 1.0


def _symmetry(grid):
    lr = _iou(grid, grid[:, ::-1])
    ud = _iou(grid, grid[::-1, :])
    r90 = _iou(grid, np.rot90(grid))
    return float(max(lr, ud, r90))


def detect(xs, ys, rng_seed=3301):
    """The 6 frozen geometry stats. Deterministic given rng_seed."""
    rng = np.random.default_rng(rng_seed)
    dvec = np.stack([np.diff(xs), np.diff(ys)], 1)
    seglen = np.hypot(dvec[:, 0], dvec[:, 1])
    path_len = float(seglen.sum()) or 1e-9
    net = math.hypot(xs[-1] - xs[0], ys[-1] - ys[0])
    grid = rasterize(xs, ys)  # rasterize ONCE, reuse for the 3 grid stats
    return {
        "closure": net / path_len,
        "self_intersections": _seg_intersections_sampled(xs, ys, rng=rng),
        "bbox_fill": float(grid.sum()) / (grid.shape[0] * grid.shape[1]),
        "caging": net / path_len,  # net/path (same numerator/denominator family; kept as named stat)
        "symmetry": _symmetry(grid),
        "components": float(_components(grid)),
    }


# ------------------------------------------------------------- null test
STATS = ["closure", "self_intersections", "bbox_fill", "caging", "symmetry", "components"]


def null_band(values, modulus, turn_interp, step_rule, n=200, seed0=3301):
    """Detector stats over n histogram-preserving shuffles."""
    acc = {s: [] for s in STATS}
    for k in range(n):
        sh = lc.shuffled(values, seed0 + k)
        xs, ys = walk(sh, modulus, turn_interp, step_rule)
        d = detect(xs, ys, rng_seed=seed0 + k)
        for s in STATS:
            acc[s].append(d[s])
    return acc


def two_sided_p(real, samples):
    """Empirical two-sided p-value of `real` vs the null `samples`."""
    arr = np.asarray(samples, dtype=np.float64)
    n = len(arr)
    lo = (arr <= real).sum()
    hi = (arr >= real).sum()
    return 2.0 * min(lo, hi) / n if n else 1.0


def save_png(xs, ys, path, res=800):
    from PIL import Image, ImageDraw
    minx, maxx, miny, maxy = xs.min(), xs.max(), ys.min(), ys.max()
    w = max(maxx - minx, 1e-9); h = max(maxy - miny, 1e-9)
    scale = (res - 20) / max(w, h)
    img = Image.new("L", (res, res), 255)
    d = ImageDraw.Draw(img)
    px = 10 + (xs - minx) * scale
    py = 10 + (ys - miny) * scale
    pts = list(zip(px.tolist(), py.tolist()))
    d.line(pts, fill=0, width=1)
    img.save(path)
