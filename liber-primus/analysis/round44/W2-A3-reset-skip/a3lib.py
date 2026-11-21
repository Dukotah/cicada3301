"""R44 WAVE-2 / A3 — glue for the reset+keyskip1 FULL-grid beam sweep.

The beam instrument itself is R44-R1's `resets.py` (gate-validated G3 0.989 vs rigid 0.364),
imported UNMODIFIED.  This module only supplies: longer keys (KEY_LEN 8192, prefix-asserted
identical to R1's 4096), the whole-section application (the repair of R1's tier-2 mid-section
zero-rejection approximation), the generic target structures (so plants ride the identical
code path as real pages), and the multiprocessing task runner.

Pre-registered in PREREG.md.  Pure python3 + numpy, no network.
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R1 = os.path.abspath(os.path.join(HERE, "..", "R1-key-resets"))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, R1)
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
sys.path.insert(0, os.path.join(LP, "analysis", "round34", "I1-v3-null"))
import resets as R                     # noqa: E402  (the R44-R1 instrument, unmodified)
import adjudicate as A                 # noqa: E402
import bars_v3 as B                    # noqa: E402

KEY_LEN_A3 = 8192                      # deepest section (~3,400) + offset + rejection slack
FREE_LS = (120, 240, 400, 729)
PAN = None                             # set by init() (parent, pre-fork)
KEYS = None
TARGETS = None                         # dict mode -> target list, set by parent pre-fork


def free_bar(L):
    cand = [x for x in FREE_LS if x <= L] or [120]
    return B.bar_v3(R.N_BAR, max(cand), "free")


def build_keys_a3():
    """R1's 51 keys rebuilt at KEY_LEN 8192; first-4096 prefix asserted identical to R1's."""
    k4 = R.build_keys()
    old = R.KEY_LEN
    R.KEY_LEN = KEY_LEN_A3
    try:
        k8 = R.build_keys()
    finally:
        R.KEY_LEN = old
    for n in k4:
        assert np.array_equal(k8[n][:old], k4[n]), n
    return k8


# ------------------------------------------------------------------ targets
# page    target: (tid, c, bar)                        -> beam [len(c)] at offset o
# line    target: (tid, c, segs, bar)                  -> beam segs at offset o (cp carried)
# section target: (sid, c_concat, slices)              -> ONE beam [len(c_concat)] at offset o,
#                 slices = [(tid, a, b, bar)]             then adjudicated per page slice
def real_targets():
    pages = R.parse_pages()
    tp, tl, ts = [], [], []
    for pi in range(55):
        c = np.asarray(pages[pi]["idx"], dtype=np.int64)
        bar = free_bar(len(c))
        tp.append(("p%02d" % pi, c, bar))
        lo = pages[pi]["line_of"]
        segs, cur, n = [], lo[0], 0
        for x in lo:
            if x != cur:
                segs.append(n)
                n, cur = 0, x
            n += 1
        segs.append(n)
        tl.append(("p%02d" % pi, c, segs, bar))
    starts = [s for s in R.SECTIONS if s < 55]
    for si, s0 in enumerate(starts):
        s1 = starts[si + 1] if si + 1 < len(starts) else 55
        cs, slices, a = [], [], 0
        for pi in range(s0, s1):
            c = pages[pi]["idx"]
            slices.append(("p%02d" % pi, a, a + len(c), free_bar(len(c))))
            cs.extend(c)
            a += len(c)
        ts.append(("s%02d" % s0, np.asarray(cs, dtype=np.int64), slices))
    return {"page": tp, "line": tl, "section": ts}


# ------------------------------------------------------------------ one task = (mode, key)
def run_task(args):
    """Sweep one (mode, kname) over TARGETS[mode] x 30 offsets x 6 configs.

    Returns per-page best (with decode) + crossers (full-adjudicated, non-degenerate) + count.
    """
    mode, kname = args
    K = KEYS[kname]
    t0 = time.time()
    per_page = {}                      # tid -> rows: list of (o, cfg, dec)
    bars = {}
    for o in R.BASE_OFFSETS:
        for cfg in R.CFGS:
            if mode == "page":
                for tid, c, bar in TARGETS["page"]:
                    dec = R.beam_reset_decode(c, K, cfg, [len(c)], offset=o)
                    per_page.setdefault(tid, []).append((o, cfg, dec))
                    bars[tid] = bar
            elif mode == "line":
                for tid, c, segs, bar in TARGETS["line"]:
                    dec = R.beam_reset_decode(c, K, cfg, segs, offset=o)
                    per_page.setdefault(tid, []).append((o, cfg, dec))
                    bars[tid] = bar
            else:
                for sid, c, slices in TARGETS["section"]:
                    dec = R.beam_reset_decode(c, K, cfg, [len(c)], offset=o)
                    for tid, a, b, bar in slices:
                        per_page.setdefault(tid, []).append((o, cfg, dec[a:b]))
                        bars[tid] = bar
    out, crossers, n_cells = {}, [], 0
    for tid, rows in per_page.items():
        X = np.asarray([r[2] for r in rows], dtype=np.int64)
        res = A.adjudicate_batch(X, pan=PAN)
        pm = res["pmax"]
        n_cells += X.shape[0]
        i = int(pm.argmax())
        out[tid] = dict(pmax=float(pm[i]), preg=int(res["preg"][i]), offset=rows[i][0],
                        cfg=rows[i][1], dec=X[i].tolist(), L=int(X.shape[1]),
                        bar=round(float(bars[tid]), 4))
        for j in np.nonzero(pm >= bars[tid])[0]:
            full = A.adjudicate(X[int(j)], pan=PAN)
            if not full["degenerate"] and full["pmax"] >= bars[tid]:
                crossers.append(dict(tid=tid, mode=mode, key=kname, offset=rows[int(j)][0],
                                     cfg=rows[int(j)][1], pmax=float(full["pmax"]),
                                     preg=int(full["preg"]), bar=round(float(bars[tid]), 4),
                                     decode=X[int(j)].tolist()))
    return dict(mode=mode, key=kname, n_cells=n_cells, best=out, crossers=crossers,
                elapsed=round(time.time() - t0, 1))


def init(targets):
    """Parent-side init (PAN/KEYS for the parent's own adjudications)."""
    global PAN, KEYS, TARGETS
    PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
    KEYS = build_keys_a3()
    TARGETS = targets
    R._quad()
    return KEYS


def worker_init(targets):
    """Spawn-safe worker initializer (the 2026-11-09 mp fix: py3.14 fork-after-threads
    is deprecated and hung the first gate run; each spawned worker rebuilds PAN/KEYS
    (~3 s, prefix-asserted) and receives TARGETS pickled via initargs)."""
    global PAN, KEYS, TARGETS
    PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
    KEYS = build_keys_a3()
    TARGETS = targets
    R._quad()


def heartbeat(msg):
    """Dead-man heartbeat line into run.log (timestamp + progress)."""
    with open(os.path.join(HERE, "run.log"), "a") as f:
        f.write("%s HEARTBEAT %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S%z"), msg))
