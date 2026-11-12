"""R44/R1 library — fixed keys, reset phase maps, tier-1 vectorised reset decode, tier-2
reset-aware keyskip1 beam (adapted from round33/I2-construction-axis/relation_skip_by_k.py,
which R33-I2 shipped as a patch proposal and never applied to a sweep).

Everything here is pre-registered in PREREG.md.  Pure python3 + numpy, no network.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round19/G1", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))
from lp import gematria as gp      # noqa: E402
from lp import score as _score     # noqa: E402
import gen_bash                    # noqa: E402  (round19/G1, byte-exact validated)

N = 29
KEY_LEN = 4096                     # longest section (p40..52) is ~3,400 runes + offset 200
SECTIONS = [0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54]
MODES = ("page", "line", "section")
CFGS = ("vigm", "vigp", "beau", "vigm_atb", "vigp_atb", "beau_atb")
BASE_OFFSETS = list(range(30))     # 0..29
ANCHOR_MAX_O, ANCHOR_CAP = 200, 10
N_BAR = 2_000_000                  # bar computed at this N (upper bound on cells, PREREG)

KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")


# ------------------------------------------------------------------ canon parse
def parse_pages():
    """57 canon pages: dict(idx=list[int], line_of=list[int])."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        idx, line_of = [], []
        line = 0
        for ch in seg:
            if ch in gp.RUNE_TO_IDX:
                idx.append(gp.RUNE_TO_IDX[ch])
                line_of.append(line)
            elif ch == "/":
                line += 1
        if idx:
            pages.append(dict(idx=idx, line_of=line_of))
    assert len(pages) == 57
    return pages


def phase_vectors(pages):
    """For each of the 55 unsolved pages, the key-phase vector per mode.

    page    : 0..Lp-1
    line    : position within the canon '/'-line
    section : cumulative rune position since the start of the red-head section
    """
    out = []
    for pi, pg in enumerate(pages[:55]):
        Lp = len(pg["idx"])
        ar = np.arange(Lp, dtype=np.int64)
        lo = np.asarray(pg["line_of"], dtype=np.int64)
        starts = np.zeros(Lp, dtype=np.int64)
        for t in range(1, Lp):
            starts[t] = t if lo[t] != lo[t - 1] else starts[t - 1]
        sec_start = max(x for x in SECTIONS if x <= pi)
        sec_base = sum(len(pages[q]["idx"]) for q in range(sec_start, pi))
        out.append({"page": ar, "line": ar - starts, "section": sec_base + ar})
    return out


# ------------------------------------------------------------------ fixed keys (51)
_CICADA_SEEDS = [3301, 1033, 761, 509, 29, 58, 2, 1]


def _sieve(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    return primes


def _phi(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def build_keys():
    """OrderedDict name -> np.int64 array (KEY_LEN,) of values 0..28, exactly the PREREG set."""
    keys = {}
    pr = _sieve(KEY_LEN)
    keys["P-prime"] = np.array([p % N for p in pr], dtype=np.int64)
    keys["P-totient"] = np.array([(p - 1) % N for p in pr], dtype=np.int64)
    keys["P-phi"] = np.array([_phi(n) % N for n in range(2, KEY_LEN + 2)], dtype=np.int64)
    sp = json.load(open(os.path.join(LP, "analysis", "round20", "P3", "seedprior20.json")))
    seeds = [e["seed"] for e in sp["order"][:40]] + _CICADA_SEEDS
    assert len(seeds) == 48 and len(set(seeds)) == 48
    for s in seeds:
        keys["G-bash-%d" % s] = np.array(
            [v % N for v in gen_bash.raws(s, KEY_LEN, variant="bash4.2", anti_repeat=True)],
            dtype=np.int64)
    assert len(keys) == 51
    return keys


# ------------------------------------------------------------------ 7-gram anchor
# sites measured by verify_7gram.py (sevengram.json): A = p27 pos 28..34 (in-page == in-section,
# p27 opens a section); B = p54 pos 70..75 + 7th rune at p55 pos 0 (page mode) / section offsets
# 70..76 contiguous (section mode, p54 opens a section and p55 continues it).
def anchor_offsets(K, mode, base=BASE_OFFSETS, omax=ANCHOR_MAX_O, cap=ANCHOR_CAP):
    """(anchored_extras, base_flags): offsets o in (max(base)+1)..omax satisfying the
    same-plaintext 7-gram constraint (first `cap`), and the flag per base offset."""
    def holds(o):
        if mode == "page":
            return (all(K[o + 28 + j] == K[o + 70 + j] for j in range(6))
                    and K[o + 34] == K[o + 0])
        if mode == "section":
            return all(K[o + 28 + j] == K[o + 70 + j] for j in range(7))
        return False
    flags = [bool(holds(o)) for o in base] if mode in ("page", "section") else [False] * len(base)
    extras = []
    if mode in ("page", "section"):
        for o in range(max(base) + 1, omax + 1):
            if holds(o):
                extras.append(o)
                if len(extras) >= cap:
                    break
    return extras, flags


# ------------------------------------------------------------------ tier-1 decode
def decode_block(c, Kmat, cfg):
    """c (Lp,) int64 ciphertext; Kmat (B, Lp) key rows -> (B, Lp) plaintext."""
    x = (N - 1) - c if cfg.endswith("_atb") else c
    base = cfg.split("_")[0]
    if base == "vigm":
        return (x[None, :] - Kmat) % N
    if base == "vigp":
        return (x[None, :] + Kmat) % N
    return (Kmat - x[None, :]) % N


def build_rows(c, ph, keys, anchors):
    """All tier-1 rows for one page under one mode.

    c (Lp,), ph (Lp,) phase vector, keys = build_keys(), anchors[kname] = (extras, flags).
    Returns X (B, Lp) int64 and meta list of (kname, offset, cfg, anchored_flag).
    """
    rows, meta = [], []
    for kname, K in keys.items():
        extras, flags = anchors[kname]
        offs = BASE_OFFSETS + extras
        fl = flags + [True] * len(extras)
        Kmat = K[np.add.outer(np.asarray(offs, dtype=np.int64), ph)]     # (n_off, Lp)
        for cfg in CFGS:
            rows.append(decode_block(c, Kmat, cfg))
            meta.extend((kname, o, cfg, f) for o, f in zip(offs, fl))
    return np.concatenate(rows, axis=0), meta


# ------------------------------------------------------------------ tier-2 beam
# Adapted from round33/I2-construction-axis/relation_skip_by_k.py (k=1), with the ciphertext
# pre-transformed per config so the one additive relation covers all six (algebra in PREREG/
# RESULTS): vigm -> sign -1 raw; vigp -> sign +1 raw; beau -> sign +1 on (-c);
# *_atb -> same on (28-c) first.  The skipped-draw consistency check generalises as
# (p - sign*K[skip]) % N == cprev_transformed, which for each config reproduces the real
# output-side anti-repeat on the VISIBLE ciphertext.
_Q = None


def _quad():
    global _Q
    if _Q is None:
        _Q = _score.default()
    return _Q


_TR = [gp.IDX_TO_TRANS[i] for i in range(N)]


def _beam_keyskip1(C, K, sign, cprev0=None, beam_w=200, max_rej=3):
    Q = _quad()
    d, floor = Q.d, Q.floor
    Kx = list(K) + [0] * (len(C) * (max_rej + 2) + 8)

    def qd(tl, add):
        s = tl + add
        t = 0.0
        for e in range(max(4, len(tl) + 1), len(s) + 1):
            t += d.get(s[e - 4:e], floor)
        return t

    beams = [(0.0, -1, "", [], cprev0)]
    for ci in C:
        nxt = []
        for sc, pa, tl, pidx, cp in beams:
            for m in range(max_rej + 1):
                acc = pa + 1 + m
                p = (ci + sign * Kx[acc]) % N
                if m and cp is None:
                    continue
                if m and not all((p - sign * Kx[pa + 1 + t]) % N == cp for t in range(m)):
                    continue
                add = _TR[p]
                nxt.append((sc + qd(tl, add), acc, tl + add, pidx + [p], ci))
        nxt.sort(key=lambda x: x[0], reverse=True)
        beams = nxt[:beam_w]
    b = beams[0]
    return {"plain_idx": b[3], "score": b[0]}


def _transform(C, cfg):
    """(C_transformed ct, sign) so that decode is p = (ct + sign*K) % N for every config,
    and the beam's skipped-draw check (p - sign*K_skip) % N == cp_ct reproduces the real
    output-side anti-repeat on the VISIBLE ciphertext (algebra per config in RESULTS.md):
      vigm:  ct = c'',        sign = -1   (c'' = atbash?(c);  p = c'' - K)
      vigp:  ct = c'',        sign = +1   (p = c'' + K)
      beau:  ct = (-c'') % N, sign = +1   (p = K - c'' = ct + K)
    Doublet equality is preserved by both the atbash and the negation transforms."""
    c = np.asarray(C, dtype=np.int64)
    if cfg.endswith("_atb"):
        c = (N - 1) - c
    base = cfg.split("_")[0]
    if base == "vigm":
        return c, -1
    if base == "vigp":
        return c, +1
    return (-c) % N, +1


def beam_reset_decode(C, K, cfg, seg_lens, offset=0, beam_w=200, max_rej=3):
    """Tier-2: reset-aware keyskip1 beam over segments (page/line/section pieces).

    seg_lens = lengths of the segments of C at which the key pointer returns to `offset`.
    The previous segment's last TRANSFORMED ciphertext rune is carried as cprev (the
    anti-repeat filter sees the visible stream across the boundary).
    Returns plain indices (list, len == len(C)).
    """
    ct, sign = _transform(C, cfg)
    out, a, cp = [], 0, None
    Ko = list(K[offset:offset + max(seg_lens) * (max_rej + 2) + 64])
    for x in seg_lens:
        seg = ct[a:a + x]
        if len(seg) == 0:
            continue
        out += _beam_keyskip1(list(seg), Ko, sign, cprev0=cp, beam_w=beam_w, max_rej=max_rej)["plain_idx"]
        cp = int(seg[-1])
        a += x
    return out


def beam_rigid_decode(C, K, cfg, offset=0, beam_w=200, max_rej=3):
    """The rigid (non-reset) counterpart: one segment, key never resets."""
    return beam_reset_decode(C, K, cfg, [len(C)], offset=offset, beam_w=beam_w, max_rej=max_rej)


def recovery(a, b):
    a, b = list(a), list(b)
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] == b[i]) / max(1, len(b))


# ------------------------------------------------------------------ tier-1 page sweep
def tier1_sweep_page(c, phases, keys, anchors_by_mode, bar, A, PAN, keep_decodes=False):
    """The full pre-registered tier-1 matrix over ONE page (real or planted).

    c: (Lp,) ciphertext indices.  phases: dict mode -> (Lp,) phase vector.
    anchors_by_mode[mode][kname] = (extras, flags).  bar: pmax bar at this page's L_cap.
    A = the round19/I2 adjudicate module, PAN = its Panel.
    Returns (count, best, crossers); best/crossers carry (mode, key, offset, cfg, anchored).
    """
    best = {"pmax": -99.0}
    crossers, count = [], 0
    for mode, ph in phases.items():
        X, meta = build_rows(np.asarray(c, dtype=np.int64), ph, keys, anchors_by_mode[mode])
        r = A.adjudicate_batch(X, pan=PAN)
        count += X.shape[0]
        pm = r["pmax"]
        i = int(pm.argmax())
        if pm[i] > best["pmax"]:
            kname, o, cfg, anch = meta[i]
            best.update(pmax=float(pm[i]), preg=int(r["preg"][i]), mode=mode, key=kname,
                        offset=int(o), cfg=cfg, anchored=bool(anch), L=int(X.shape[1]),
                        bar=round(float(bar), 4))
            if keep_decodes:
                best["decode"] = X[i].tolist()
        for j in np.nonzero(pm >= bar)[0]:
            full = A.adjudicate(X[int(j)], pan=PAN)
            if not full["degenerate"] and full["pmax"] >= bar:
                kname, o, cfg, anch = meta[int(j)]
                crossers.append(dict(pmax=float(full["pmax"]), preg=int(full["preg"]), mode=mode,
                                     key=kname, offset=int(o), cfg=cfg, anchored=bool(anch),
                                     L=int(X.shape[1]), bar=round(float(bar), 4),
                                     decode=X[int(j)].tolist()))
    return count, best, crossers


def cell_decode(c, ph, K, offset, cfg):
    """The single tier-1 decode of one named cell (for plant checks / differentials)."""
    Kmat = K[np.asarray([offset], dtype=np.int64)[:, None] + np.asarray(ph, dtype=np.int64)[None, :]]
    return decode_block(np.asarray(c, dtype=np.int64), Kmat, cfg)[0]


# ------------------------------------------------------------------ encipher (plants)
def encipher_reset(P, K, cfg, seg_lens, offset=0, keyskip=False, supp=0.83, seed=3301):
    """Encrypt plaintext P so that the tier-1 cell (key, mode, offset, cfg) inverts it.
    keyskip=True applies the R33-I2 output-side anti-repeat (enciphers._core semantics:
    a draw whose VISIBLE ciphertext equals the previous one is rejected with prob supp and
    the key pointer advances by 1), with the pointer returning to `offset` at each segment."""
    import random
    rng = random.Random(seed)
    bounds, a = set(), 0
    for x in seg_lens[:-1]:
        a += x
        bounds.add(a)
    C, j, cp = [], offset, None
    atb = cfg.endswith("_atb")
    base = cfg.split("_")[0]
    for i, p in enumerate(P):
        if i in bounds:
            j = offset
        while True:
            k = int(K[j])
            if base == "vigm":
                c = (p + k) % N          # decode p = c - K
            elif base == "vigp":
                c = (p - k) % N          # decode p = c + K
            else:
                c = (k - p) % N          # decode p = K - c
            if atb:
                c = (N - 1) - c          # decode applies atbash first
            if keyskip and cp is not None and c == cp and rng.random() < supp:
                j += 1
                continue
            break
        C.append(c)
        j += 1
        cp = c
    return C
