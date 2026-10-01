"""A2 controls: establish the sub-pixel noise floor and prove the measurer.

We build a synthetic 'text grid' of an identical glyph repeated on a lattice.
- NEGATIVE control: every glyph on the exact integer lattice -> measured
  sub-pixel residuals should be ~0 and NOT bimodal.
- POSITIVE control: half the glyphs shifted by a KNOWN sub-pixel dx (e.g.
  +0.4 px). After JPEG q92 compression (matching the corpus), the measurer
  must recover the two clusters and separate them above the noise floor.

The glyph is drawn with PIL antialiasing then optionally sub-pixel shifted
via a fractional affine, matching how a PDF rasterizer places glyphs off the
pixel grid. This is the honest test: can centroid recover a fractional shift
through the SAME JPEG pipeline the Cicada pages went through (q92, optimized).
"""
import io, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import measure as M

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(3301)

CELL = 60          # cell size px
NCOLS, NROWS = 20, 20
GLYPH_R = 18       # glyph half-extent


def draw_glyph(canvas_size=CELL, dx=0.0, dy=0.0, supersample=8):
    """Draw a fixed asymmetric glyph at sub-pixel offset (dx,dy) via supersample."""
    S = supersample
    big = Image.new('L', (canvas_size * S, canvas_size * S), 255)
    d = ImageDraw.Draw(big)
    cx = (canvas_size / 2 + dx) * S
    cy = (canvas_size / 2 + dy) * S
    r = GLYPH_R * S
    # asymmetric shape (an 'F'-like rune stroke set) so centroid is well defined
    lw = max(2, int(0.16 * r))
    d.line([(cx - r*0.3, cy - r), (cx - r*0.3, cy + r)], fill=0, width=lw)      # stave
    d.line([(cx - r*0.3, cy - r), (cx + r*0.7, cy - r*0.5)], fill=0, width=lw)  # top arm
    d.line([(cx - r*0.3, cy - r*0.15), (cx + r*0.5, cy + r*0.25)], fill=0, width=lw)  # mid arm
    small = big.resize((canvas_size, canvas_size), Image.LANCZOS)
    return np.asarray(small)


def build_grid(shifts):
    """shifts[(r,c)] = (dx,dy). Returns full-page grayscale array."""
    H, W = NROWS * CELL, NCOLS * CELL
    page = np.full((H, W), 255, np.uint8)
    for r in range(NROWS):
        for c in range(NCOLS):
            dx, dy = shifts.get((r, c), (0.0, 0.0))
            g = draw_glyph(dx=dx, dy=dy)
            page[r*CELL:(r+1)*CELL, c*CELL:(c+1)*CELL] = g
    return page


def jpeg_roundtrip(arr, quality=92, optimize=True):
    im = Image.fromarray(arr).convert('L')
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality, optimize=optimize)
    buf.seek(0)
    return np.asarray(Image.open(buf).convert('L'))


def measure_grid(gray):
    ink = M.to_ink(gray)
    rows = []
    for r in range(NROWS):
        for c in range(NCOLS):
            x0, y0 = c*CELL, r*CELL
            res = M.centroid(ink, x0, y0, x0+CELL, y0+CELL)
            if res:
                cx, cy, mass = res
                rows.append((r, c, cx - (x0 + CELL/2), cy - (y0 + CELL/2), mass))
    return np.array(rows)  # r,c,rel_cx,rel_cy,mass


def run():
    out = {}

    # NEGATIVE: perfect lattice
    neg_gray = jpeg_roundtrip(build_grid({}))
    neg = measure_grid(neg_gray)
    # residual = deviation of rel centroid from the mean (all should be equal)
    rx = neg[:, 2];
    out['negative'] = {
        'rel_cx_mean': float(rx.mean()), 'rel_cx_std': float(rx.std()),
        'rel_cx_ptp': float(np.ptp(rx)),
        'note': 'clean lattice; std IS the empirical sub-pixel noise floor'
    }
    noise_floor = float(rx.std())

    # POSITIVE: half shifted by known dx = +0.40 px (checkerboard by column parity)
    KNOWN = 0.40
    shifts = {}
    truth = {}
    for r in range(NROWS):
        for c in range(NCOLS):
            bit = (c % 2)  # column parity carries the bit
            dx = KNOWN if bit else 0.0
            shifts[(r, c)] = (dx, 0.0)
            truth[(r, c)] = bit
    pos_gray = jpeg_roundtrip(build_grid(shifts))
    pos = measure_grid(pos_gray)
    # recover: does rel_cx separate the two groups?
    g0 = np.array([row[2] for row in pos if truth[(int(row[0]), int(row[1]))] == 0])
    g1 = np.array([row[2] for row in pos if truth[(int(row[0]), int(row[1]))] == 1])
    sep = float(g1.mean() - g0.mean())
    pooled_std = float(np.sqrt((g0.var() + g1.var()) / 2))
    dprime = sep / pooled_std if pooled_std > 0 else float('inf')
    # blind recovery: threshold at midpoint, measure bit accuracy
    thr = (g0.mean() + g1.mean()) / 2
    correct = 0; total = 0
    for row in pos:
        rc = (int(row[0]), int(row[1]))
        pred = 1 if row[2] > thr else 0
        correct += (pred == truth[rc]); total += 1
    out['positive'] = {
        'known_shift_px': KNOWN,
        'recovered_shift_px': sep,
        'pooled_std_px': pooled_std,
        'dprime': dprime,
        'blind_bit_accuracy': correct / total,
        'noise_floor_px': noise_floor,
        'verdict': 'RECOVERED' if dprime > 2 and correct/total > 0.9 else 'FAILED'
    }

    # POSITIVE-SMALL: can we detect a 0.10 px shift? (near noise floor)
    KS = 0.10
    shifts2 = {(r, c): (KS if c % 2 else 0.0, 0.0) for r in range(NROWS) for c in range(NCOLS)}
    ps_gray = jpeg_roundtrip(build_grid(shifts2))
    ps = measure_grid(ps_gray)
    g0 = np.array([row[2] for row in ps if int(row[1]) % 2 == 0])
    g1 = np.array([row[2] for row in ps if int(row[1]) % 2 == 1])
    out['positive_small'] = {
        'known_shift_px': KS,
        'recovered_shift_px': float(g1.mean() - g0.mean()),
        'detectable': bool(abs(g1.mean()-g0.mean()) > 2*noise_floor)
    }

    with open(os.path.join(HERE, 'control_results.json'), 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    return out


if __name__ == '__main__':
    run()
