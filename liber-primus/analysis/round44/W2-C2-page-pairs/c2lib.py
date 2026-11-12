"""R44 / W2-C2 shared glue — all-pairs page-as-key + canon-as-key scan.

Everything pre-registered in PREREG.md (hash-stamped in run.log before first run).
Pure python3 + numpy, no network. Reuses the R44-R1 validated canon parser and the
standing panel instrument (round19/I2 adjudicate + panel-r36.npz) and bars_v3.
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"),
          os.path.join(LP, "analysis", "round44", "R1-key-resets"),
          os.path.join(LP, "analysis", "round19", "I2"),
          os.path.join(LP, "analysis", "round34", "I1-v3-null")):
    sys.path.insert(0, p)

from lp import gematria as gp      # noqa: E402
import resets as R                 # noqa: E402
import adjudicate as A             # noqa: E402

N = 29
N_BAR = 16_000_000
BARS = {120: 16.7816, 240: 22.6382}          # bar_v3(16e6, L, 'free'), PREREG section 4
MIN_L = 60
# sign patterns (eps_j, eps_i): p = eps_j*C_j + eps_i*K + s
RELS = {"sub": (1, -1), "add": (1, 1), "negadd": (-1, -1)}
SHIFTS = (0, 1, 28)
PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))


def lnode(L):
    return 240 if L >= 240 else 120


def bar_for(L):
    return BARS[lnode(L)]


def canon_pages():
    return R.parse_pages()                   # 57 pages, dict(idx, line_of)


def verify_premise(pages):
    """PREREG Q5(ii): 57 pages; unsolved lens min 66 / max 277 / sum 12956; 7-gram sites."""
    lens = [len(pg["idx"]) for pg in pages]
    flat = [i for pg in pages for i in pg["idx"]]
    gram = (23, 11, 1, 17, 18, 10, 25)
    gA = sum(lens[:27]) + 28
    gB = sum(lens[:54]) + 70
    ok = (len(pages) == 57 and min(lens[:55]) == 66 and max(lens[:55]) == 277
          and sum(lens[:55]) == 12956 and sum(lens) == 13136
          and tuple(flat[gA:gA + 7]) == gram and tuple(flat[gB:gB + 7]) == gram)
    return ok, dict(n_pages=len(pages), min_len=min(lens[:55]), max_len=max(lens[:55]),
                    sum_unsolved=sum(lens[:55]), sum_all=sum(lens))


def line_starts(pg):
    lo = pg["line_of"]
    return sorted({0} | {t for t in range(1, len(lo)) if lo[t] != lo[t - 1]})


def key_offsets(pg):
    """PREREG section 3: {0..29} UNION line starts > 29."""
    return sorted(set(range(30)) | {t for t in line_starts(pg) if t > 29})


# ------------------------------------------------------------------ decode + batch adjudication
def decode_block(ct, key_tail, offsets, eps_j, eps_i, shift, L):
    """Stack of decodes p = eps_j*ct[:L] + eps_i*key_tail[o:o+L] + shift for o in offsets."""
    O = np.asarray(offsets, dtype=np.int64)
    idx = O[:, None] + np.arange(L)[None, :]
    K = key_tail[idx]
    return (eps_j * ct[None, :L] + eps_i * K + shift) % N


def pmax_block(X):
    return A.adjudicate_batch(X, pan=PAN)["pmax"]


def scan_ct_against_key(ct, key_fwd, key_rev, offs, rows_sink, tag):
    """All (dir, rel, shift, offset) cells of one (ct page, key page) ordered pair.

    rows_sink(pmax_array, meta_list, X) consumes results. Returns n_cells.
    One adjudicate_batch call per (dir, L-bucket): all 9 rel x shift variants stacked."""
    n = 0
    len_j = len(ct)
    for d, K in (("fwd", key_fwd), ("rev", key_rev)):
        for o_grp, L in _group_offsets(offs, len(K), len_j):
            O = np.asarray(o_grp, dtype=np.int64)
            Kb = K[O[:, None] + np.arange(L)[None, :]]          # (n_off, L)
            blocks, metas = [], []
            for rel, (ej, ei) in RELS.items():
                for s in SHIFTS:
                    blocks.append((ej * ct[None, :L] + ei * Kb + s) % N)
                    metas += [dict(tag=tag, dir=d, rel=rel, shift=s, off=int(o), L=L)
                              for o in o_grp]
            X = np.vstack(blocks)
            pm = pmax_block(X)
            rows_sink(pm, metas, X)
            n += len(metas)
    return n


def scan_ct_against_canon(ct, canon, rows_sink, sink_overlap, ct_interval, tag,
                          chunk=4096):
    """Canon-as-key over one ct page: all offsets 0..len(canon)-len_j, 9 rel x shift cells.

    Cells whose key window overlaps ct_interval = (start, end) in canon go to sink_overlap
    (PREREG section 3: tagged self_overlap, excluded from the verdict family)."""
    len_j = len(ct)
    o_max = len(canon) - len_j
    st, en = ct_interval
    n = n_ov = 0
    for base in range(0, o_max + 1, chunk):
        O = np.arange(base, min(base + chunk, o_max + 1), dtype=np.int64)
        ov = (O < en) & (O + len_j > st)
        Kb = canon[O[:, None] + np.arange(len_j)[None, :]]
        blocks, metas = [], []
        for rel, (ej, ei) in RELS.items():
            for s in SHIFTS:
                blocks.append((ej * ct[None, :] + ei * Kb + s) % N)
                metas += [dict(tag=tag, dir="fwd", rel=rel, shift=s, off=int(o), L=len_j,
                               self_overlap=bool(v)) for o, v in zip(O, ov)]
        X = np.vstack(blocks)
        pm = pmax_block(X)
        is_ov = np.array([m["self_overlap"] for m in metas])
        if (~is_ov).any():
            idx = np.where(~is_ov)[0]
            rows_sink(pm[idx], [metas[i] for i in idx], X[idx])
            n += len(idx)
        if is_ov.any():
            idx = np.where(is_ov)[0]
            sink_overlap(pm[idx], [metas[i] for i in idx], X[idx])
            n_ov += len(idx)
    return n, n_ov


def _group_offsets(offs, len_k, len_j):
    """Group offsets by usable window L = min(len_j, len_k - o); drop L < MIN_L."""
    buckets = {}
    for o in offs:
        L = min(len_j, len_k - o)
        if L < MIN_L:
            continue
        buckets.setdefault(L, []).append(o)
    return [(sorted(v), L) for L, v in sorted(buckets.items(), reverse=True)]


# ------------------------------------------------------------------ plaintext sources (plants)
def _letters_to_indices(txt, want):
    out = []
    for w in re.findall(r"[A-Z]+", txt.upper()):
        try:
            out.extend(gp.keyword_to_indices(w))
        except (ValueError, KeyError):
            continue
        if len(out) >= want:
            break
    if len(out) < want:
        raise RuntimeError("not enough plaintext")
    return out[:want]


def kjv_plain(want, skip_chars=0):
    txt = open(os.path.join(LP, "data", "kjv.txt"), encoding="utf-8", errors="ignore").read()
    return _letters_to_indices(txt[skip_chars:], want)


def latin_plain(want, skip_chars=0):
    p = os.path.join(LP, "analysis", "latin", "latin_28233.txt")
    txt = open(p, encoding="utf-8", errors="ignore").read()
    return _letters_to_indices(txt[skip_chars:], want)


def encipher(plain, key_seg, eps_j, eps_i, shift):
    """Ciphertext C such that eps_j*C + eps_i*K + shift == plain (mod 29).

    eps_j is +-1 so eps_j inverse is itself: C = eps_j*(plain - eps_i*K - shift)."""
    P = np.asarray(plain, dtype=np.int64)
    K = np.asarray(key_seg, dtype=np.int64)
    return (eps_j * (P - eps_i * K - shift)) % N


# ------------------------------------------------------------------ sinks
class Best:
    """Keeps global top-k rows + per-family stats + crossers."""

    def __init__(self, k=100):
        self.k = k
        self.rows = []          # list of (pmax, meta, decode_list)
        self.n = 0
        self.fam = {}           # (dir,rel,shift) -> [count, max, meta_of_max]
        self.crossers = []

    def __call__(self, pm, metas, X):
        self.n += len(metas)
        for i, m in enumerate(metas):
            v = float(pm[i])
            key = (m["dir"], m["rel"], m["shift"])
            f = self.fam.setdefault(key, [0, -99.0, None])
            f[0] += 1
            if v > f[1]:
                f[1], f[2] = v, m
            if v >= bar_for(m["L"]):
                self.crossers.append((v, dict(m), [int(x) for x in X[i]]))
            if len(self.rows) < self.k or v > self.rows[-1][0]:
                self.rows.append((v, dict(m), [int(x) for x in X[i]]))
                self.rows.sort(key=lambda r: -r[0])
                del self.rows[self.k:]

    def summary(self):
        return dict(
            n_cells=self.n,
            families={"|".join(map(str, k)): dict(n=v[0], best=v[1], best_meta=v[2])
                      for k, v in sorted(self.fam.items())},
            n_crossers=len(self.crossers))


def full_rows(best, with_cross=True):
    """Full adjudicate (14-field SWEEPROW stats) for top rows (+ crossers)."""
    out = []
    seen = set()
    items = list(best.rows) + (best.crossers if with_cross else [])
    for v, m, dec in items:
        key = json.dumps(m, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        res = A.adjudicate(np.asarray(dec, dtype=np.int64), pan=PAN)
        out.append(dict(meta=m, pmax=float(res["pmax"]), preg=int(res["preg"]),
                        pmax_ne=float(res["pmax_ne"]), pcon=float(res["pcon"]),
                        en=float(res["en"]), ioc=float(res["ioc"]), mds=int(res["mds"]),
                        h2=float(res["h2"]), zl=float(res["zl"]),
                        degenerate=bool(res["degenerate"]), bar=bar_for(m["L"]),
                        crossed=bool((not res["degenerate"]) and res["pmax"] >= bar_for(m["L"])),
                        head=gp.indices_to_translit(dec[:40])))
    out.sort(key=lambda r: -r["pmax"])
    return out
