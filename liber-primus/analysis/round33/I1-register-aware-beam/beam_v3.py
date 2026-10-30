"""Round 33 / I1 -- beam_decode_v3: the driftbeam transition relation with a REGISTER-AWARE search score.

Transition algebra (enumeration of admissible key advances, the 29-bin skipped-window histogram, the
max_free / pair rules) is copied from round19/I1/driftbeam.py::beam_decode unchanged.  What changes is what
ranks the hypotheses in the beam: driftbeam ranks by the English quadgram of the transliteration; v3 ranks by

  design "panel_max"      max_r U_r  (or tau-softmax) over the register trigram LMs of the panel (9 or 12)
  design "register_cond"  7 parallel beams (one per register cluster), merged by panel pmax at the end
  design "agnostic"       negative adaptive order-0/order-1 code length (no language model at all)

U_r = running sum over trigrams of (LM_r - mu_r(L)) / (sd_r(L) * sqrt(L))  (so U_r = z_r * sqrt(m)).
Everything runs on RUNE INDICES.  Pure Python per candidate (beams are narrow on the keyskip relations).
"""
import os
import sys
import math
from operator import add

sys.dont_write_bytecode = True      # never write __pycache__ into other lanes' directories
HERE = os.path.dirname(os.path.abspath(__file__))
R32 = os.path.abspath(os.path.join(HERE, "..", "..", "round32"))
for p in (os.path.join(R32, "I1-skipbytwo-decoder"), os.path.join(R32, "I2-multiregister-readjudication")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                              # noqa: E402
import beam_v2 as B2                            # noqa: E402  (also sets up lp / driftbeam import paths)
import adjudicate as A                          # noqa: E402

N = 29
ADVANCE = B2.ADVANCE
DEFAULT_PANEL_PATH = os.path.join(R32, "I2-multiregister-readjudication", "models", "panel.npz")
PANEL_PATH = os.environ.get("BEAM_V3_PANEL") or DEFAULT_PANEL_PATH     # Round 37 T1: env override

_EN_FAMILY = ("EN_MODERN", "EN_KJV", "LP1_REAL")


def derive_clusters(registers):
    """register_cond clusters from a panel's register list: the EN family (EN_MODERN/EN_KJV/LP1_REAL,
    whichever are present) is one cluster 'EN'; every other register -- including any unknown one --
    is its own cluster.  For the nine-register panel this reproduces the old hard-coded 7."""
    out, en = [], [r for r in registers if r in _EN_FAMILY]
    if en:
        out.append(("EN", en))
    out += [(r, [r]) for r in registers if r not in _EN_FAMILY]
    return out


def _registers_at(path):
    return [str(x) for x in np.load(path, allow_pickle=False)["registers"]]


try:
    CLUSTERS = derive_clusters(_registers_at(PANEL_PATH))
except (OSError, KeyError):         # default panel .npz is gitignored/absent in CI: supply via set_panel()
    CLUSTERS = []

_PAN = None
_WCACHE = {}


def set_panel(path=None):
    """Point beam_v3 at another panel .npz (None = default); resets caches and re-derives CLUSTERS."""
    global PANEL_PATH, CLUSTERS, _PAN
    PANEL_PATH = path or os.environ.get("BEAM_V3_PANEL") or DEFAULT_PANEL_PATH
    _PAN = None
    _WCACHE.clear()
    CLUSTERS = derive_clusters(_registers_at(PANEL_PATH))
    return CLUSTERS


def panel():
    global _PAN
    if _PAN is None:
        _PAN = A.Panel(PANEL_PATH)
    return _PAN


def weight_table(L, regs):
    """list-of-tuples W[f] = per-register increment for trigram f, for the registers `regs` (names)."""
    key = (L, tuple(regs))
    w = _WCACHE.get(key)
    if w is None:
        pan = panel()
        cols = [pan.registers.index(r) for r in regs]
        mu, sd, _, _ = pan.cal(L)
        M = (pan.LMT[:, cols].astype(np.float64) - mu[cols]) / (sd[cols] * math.sqrt(L))
        w = [tuple(r) for r in M.tolist()]
        if len(_WCACHE) > 24:
            _WCACHE.clear()
        _WCACHE[key] = w
    return w


# ------------------------------------------------------------------ hooks
def _hooks_panel(L, regs, tau):
    W = weight_table(L, regs)
    nr = len(regs)
    if tau and tau > 0:
        def gfun(U):
            m = max(U)
            return m + tau * math.log(sum(math.exp((u - m) / tau) for u in U))
    else:
        gfun = max

    def init(p):
        return ((0.0,) * nr, -1, p)

    def child(st, p):
        U, r1, r2 = st
        if r1 >= 0:
            U = tuple(map(add, U, W[r1 * 841 + r2 * 29 + p]))
        return gfun(U), U

    def mat(st, delta, p):
        return (delta, st[2], p)
    return init, 0.0, child, mat


def _hooks_agnostic():
    LOG2 = math.log2

    def init(p):
        n0 = [0] * N
        n0[p] = 1
        return (n0, {}, [0] * N, p, 1, -LOG2(1.0 / N))     # cum = -bits  (stored positive bits; see child)

    def child(st, p):
        n0, n1, n1t, q, m, bits = st
        p0 = (n0[p] + 0.5) / (m + 14.5)
        pr = (n1.get(q * N + p, 0) + 2.0 * p0) / (n1t[q] + 2.0)
        nb = bits - LOG2(pr)
        return -nb, nb

    def mat(st, nb, p):
        n0, n1, n1t, q, m, _ = st
        n0 = list(n0)
        n0[p] += 1
        n1 = dict(n1)
        k = q * N + p
        n1[k] = n1.get(k, 0) + 1
        n1t = list(n1t)
        n1t[q] += 1
        return (n0, n1, n1t, p, m + 1, nb)
    return init, 0.0, child, mat


# ------------------------------------------------------------------ the driver (driftbeam enumeration)
def _drive(C, K, sign, o, beam_w, mode, max_skip, max_free, lam, start_slack, hooks, want_path=True):
    init, g0, child, mat = hooks
    L = len(C)
    if o + L + max_skip * L >= len(K):
        Kx = list(K) + [0] * (L * (max_skip + 1) + 8)
    else:
        Kx = K
    nK = len(Kx)
    pair = (mode == "keyskip2")
    if mode == "keyskip1":
        max_free = 0

    bp_parent = [[]]
    bp_rune = [[]]
    beams = []                  # (score, st, acc, pen, nun_tot, nid)
    for s in range(start_slack + 1):
        acc0 = o + s
        if acc0 >= nK:
            break
        p = (C[0] + sign * Kx[acc0]) % N
        beams.append((g0 - lam * s, init(p), acc0, lam * s, s, len(bp_parent[0])))
        bp_parent[0].append(-1)
        bp_rune[0].append(p)
    cnt = [0] * N
    ms1 = max_skip + 1
    step_pair = 2 if pair else 1

    for i in range(1, L):
        ci = C[i]
        sgn_delta = (sign * (C[i - 1] - ci)) % N
        pmap = [(ci + sign * k) % N for k in range(N)]
        vmap = [(k - sgn_delta) % N for k in range(N)]
        cands = []
        cap = cands.append
        for (sc, st, pa, pen, nun_tot, nid) in beams:
            base = pa + 1
            hi = base
            maxcnt = 0
            for dsk in range(0, ms1):
                acc = base + dsk
                if acc >= nK:
                    break
                if dsk:
                    if not pair or (dsk & 1):
                        km = Kx[acc - 1]
                        c2 = cnt[km] + 1
                        cnt[km] = c2
                        if c2 > maxcnt:
                            maxcnt = c2
                    hi = acc
                    if pair:
                        if dsk & 1:
                            continue
                        need = dsk >> 1
                    else:
                        need = dsk
                    if need - maxcnt > max_free:
                        break
                else:
                    need = 0
                kacc = Kx[acc]
                nun = need - cnt[vmap[kacc]]
                if nun > max_free:
                    continue
                p = pmap[kacc]
                g, delta = child(st, p)
                npen = pen + lam * nun
                cap((g - npen, st, delta, p, acc, npen, nun_tot + nun, nid))
            if hi > base:
                for m in range(base, hi, step_pair):
                    cnt[Kx[m]] = 0
        if not cands:
            break
        cands.sort(key=lambda t: t[0], reverse=True)
        top = cands[:beam_w]
        nb = []
        par_row = []
        rune_row = []
        for (sc, st, delta, p, acc, npen, nt, pnid) in top:
            nb.append((sc, mat(st, delta, p), acc, npen, nt, len(par_row)))
            par_row.append(pnid)
            rune_row.append(p)
        beams = nb
        bp_parent.append(par_row)
        bp_rune.append(rune_row)

    best = beams[0]
    nsteps = len(bp_parent) - 1
    out = {"search_score": best[0], "ptr_end": best[2], "n_skips": best[2] - o - nsteps,
           "n_unexplained": best[4], "steps": nsteps + 1}
    idx = []
    node = best[5]
    for step in range(nsteps, -1, -1):
        idx.append(bp_rune[step][node])
        node = bp_parent[step][node]
    idx.reverse()
    out["plain_idx"] = idx
    return out


def beam_decode_v3(C, K, advance, design="panel_max", sign=-1, o=0, beam_w=400,
                   tau=0.0, lam_u=4.0, **override):
    """Register-aware skip-tolerant beam decode.  advance in {1, 2, "free"}; design in
    {"panel_max", "register_cond", "agnostic"}.  lam_u (free relation) is in U units."""
    if advance not in ADVANCE:
        raise ValueError("advance must be one of %s" % list(ADVANCE))
    cfg = dict(ADVANCE[advance])
    cfg.update(override)
    lam = lam_u if cfg["lam"] else 0.0
    kw = dict(mode=cfg["mode"], max_skip=cfg["max_skip"], max_free=cfg["max_free"], lam=lam,
              start_slack=cfg["start_slack"])
    L = len(C)
    pan = panel()
    if design == "panel_max":
        r = _drive(C, K, sign, o, beam_w, hooks=_hooks_panel(L, pan.registers, tau), **kw)
        r["design"] = design
        return r
    if design == "agnostic":
        r = _drive(C, K, sign, o, beam_w, hooks=_hooks_agnostic(), **kw)
        r["design"] = design
        return r
    if design == "register_cond":
        best = None
        allr = {}
        for name, regs in CLUSTERS:
            r = _drive(C, K, sign, o, beam_w, hooks=_hooks_panel(L, regs, tau), **kw)
            x = np.asarray(r["plain_idx"], dtype=np.int64)
            mu, sd, _, _ = pan.cal(len(x))
            z = float(((pan.raw(x) - mu) / sd).max())
            allr[name] = {"z": round(z, 3), "plain_idx": r["plain_idx"]}
            if best is None or z > best[0]:
                best = (z, name, r)
        r = best[2]
        r["design"] = design
        r["merge_pick"] = best[1]
        r["merge_z"] = best[0]
        r["cluster_z"] = {k: v["z"] for k, v in allr.items()}
        r["cluster_idx"] = {k: v["plain_idx"] for k, v in allr.items()}
        return r
    raise ValueError(design)


recovery = B2.recovery
