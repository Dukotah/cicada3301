"""Connected-component glyph segmentation for rune lines."""
import numpy as np
from collections import deque


def label_components(img):
    H, W = img.shape
    lab = np.zeros((H, W), np.int32)
    boxes = {}
    cur = 0
    for i in range(H):
        row = img[i]
        for j in range(W):
            if row[j] and lab[i, j] == 0:
                cur += 1
                q = deque([(i, j)])
                lab[i, j] = cur
                x0 = x1 = j; y0 = y1 = i; area = 0
                while q:
                    y, x = q.popleft()
                    area += 1
                    if x < x0: x0 = x
                    if x > x1: x1 = x
                    if y < y0: y0 = y
                    if y > y1: y1 = y
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1),
                                   (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < H and 0 <= nx < W and img[ny, nx] and lab[ny, nx] == 0:
                            lab[ny, nx] = cur
                            q.append((ny, nx))
                boxes[cur] = [x0, x1, y0, y1, area]
    return lab, boxes


def line_glyphs(line_ink, min_h_frac=0.45, dot_area_frac=0.05, merge_gap=10):
    """Return ordered list of glyph cells [(x0,x1,y0,y1)], merging stroke
    fragments of one rune (close in x, both reasonably tall) and dropping dots.

    Wide cells (likely two merged runes) are split at the deepest projection
    valley near their middle when width >> typical."""
    bh = line_ink.shape[0]
    lab, boxes = label_components(line_ink)
    comps = []
    for k, (x0, x1, y0, y1, area) in boxes.items():
        w = x1 - x0 + 1; h = y1 - y0 + 1
        comps.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, w=w, h=h, area=area))
    comps.sort(key=lambda c: c["x0"])
    # classify
    tall = [c for c in comps if c["h"] >= min_h_frac * bh]
    if not tall:
        return []
    # estimate typical glyph width from tall comps median
    ws = sorted(c["w"] for c in tall)
    typ_w = ws[len(ws) // 2]
    # merge fragments: a short/small comp that sits within x-range of, or very
    # close to, a tall comp belongs to it (e.g. dots of D/OE, diacritics)
    cells = []
    used = [False] * len(comps)
    # build glyph cells starting from tall comps, absorbing nearby small comps
    for i, c in enumerate(comps):
        if c["h"] < min_h_frac * bh:
            continue  # handled as fragment
        gx0, gx1, gy0, gy1 = c["x0"], c["x1"], c["y0"], c["y1"]
        used[i] = True
        cells.append([gx0, gx1, gy0, gy1])
    # absorb small comps into nearest cell (by x-overlap / proximity), unless
    # they are clearly standalone separator dots (small & isolated, mid-height)
    dot_area = dot_area_frac * bh * typ_w
    for i, c in enumerate(comps):
        if used[i]:
            continue
        # is it a separator dot? small area, isolated horizontally
        cxc = (c["x0"] + c["x1"]) / 2
        # find nearest cell
        best = None; bd = 1e9
        for cell in cells:
            if cell[0] - merge_gap <= cxc <= cell[1] + merge_gap:
                d = 0
            else:
                d = min(abs(cxc - cell[0]), abs(cxc - cell[1]))
            if d < bd:
                bd = d; best = cell
        if best is not None and bd <= merge_gap and c["area"] > 0:
            best[0] = min(best[0], c["x0"]); best[1] = max(best[1], c["x1"])
            best[2] = min(best[2], c["y0"]); best[3] = max(best[3], c["y1"])
        # else: standalone dot -> dropped (separator/noise)
    cells.sort()
    # split wide cells (merged rune pairs)
    out = []
    for (x0, x1, y0, y1) in cells:
        w = x1 - x0 + 1
        k = int(round(w / typ_w))
        if k >= 2 and w > 1.55 * typ_w:
            sub = line_ink[:, x0:x1 + 1]
            colink = sub.sum(0).astype(float)
            # find k-1 valleys
            cuts = _valleys(colink, k - 1, int(typ_w * 0.55))
            prev = 0
            for cx in cuts + [w]:
                seg = line_ink[:, x0 + prev:x0 + cx]
                ys = np.where(seg.any(1))[0]
                if len(ys):
                    out.append([x0 + prev, x0 + cx - 1, y0, y1])
                prev = cx
        else:
            out.append([x0, x1, y0, y1])
    out.sort()
    return out


def _valleys(prof, n, min_sep):
    L = len(prof)
    cand = sorted(range(min_sep, L - min_sep), key=lambda i: prof[i])
    ch = []
    for i in cand:
        if all(abs(i - c) >= min_sep for c in ch):
            ch.append(i)
            if len(ch) == n:
                break
    return sorted(ch)
