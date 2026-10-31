"""R40-B3 pad grids (R17 P3 public pads; CicadaOS ISO pads): bounded offset re-decode under the R37-I2 instrument."""
import os, sys, json, hashlib, time
sys.dont_write_bytecode = True
import numpy as np
from engine import LP, _load, U, F, HERE
import grids as G   # sys.path setup
R17 = os.path.join(LP, "analysis", "round17")
sys.path.insert(0, R17)
LPS = _load("r17lib", os.path.join(R17, "lib_padsweep.py"))
BYTEWISE = ("mod29", "hi_nibble", "lo_nibble", "byte_scaled", "prime_to_idx")
BLOCK = 8 << 20
NEEDROOM = 200   # symbols after the offset required by a sweep decode (L=120 plus skip slack)


def nibbles(b):
    return LPS.ks_nibbles(b).astype(np.int8)


def build(blob, builder):
    """blob bytes -> int8 symbol array (Z29 or Z16)."""
    if builder in BYTEWISE:
        fn = LPS.BUILDERS[builder]; parts = []
        for i in range(0, len(blob), BLOCK): parts.append(fn(blob[i:i + BLOCK]).astype(np.int8))
        return np.concatenate(parts) if len(parts) > 1 else parts[0]
    if builder == "nibbles":
        parts = []
        for i in range(0, len(blob), BLOCK): parts.append(nibbles(blob[i:i + BLOCK]))
        return np.concatenate(parts) if len(parts) > 1 else parts[0]
    if builder == "hexchars":
        return LPS.BUILDERS["hexchars"](blob).astype(np.int8)
    raise KeyError(builder)


def window(blob, builder, off, n):
    if builder in BYTEWISE:
        return build(blob[off:off + n], builder)
    if builder == "nibbles":
        seg = blob[off // 2: off // 2 + n // 2 + 2]
        return nibbles(seg)[off % 2: off % 2 + n]
    raise KeyError(builder)


def offset_set(n_off, cap, ladder, extra):
    S = set(range(0, min(8, n_off))) | {o for o in ladder if 0 <= o < n_off} | {o for o in extra if 0 <= o < n_off}
    if n_off <= cap: return np.arange(n_off, dtype=np.int64)
    stride = n_off / float(cap)
    S |= {int(i * stride) for i in range(cap)}
    return np.array(sorted(S), dtype=np.int64)


class PadGrid:
    atbs = (0,)

    def __init__(s, name, pads, builders, cap, ladder, extra_by_pad=None, hexchars_max=2 << 20):
        """pads: ordered dict name -> path"""
        s.name = name; s.pads = dict(pads); s.builders = list(builders); s.cap = cap; s.ladder = list(ladder)
        s.extra = extra_by_pad or {}; s.hexchars_max = hexchars_max
        s._blob = {}; s._hex = {}
        s.sizes = {n: os.path.getsize(p) for n, p in s.pads.items()}
        s.cells = [(p, b, d) for p in s.pads for b in s.builders for d in ("fwd", "rev") if s.usable(p, b)]
        s.counts = {"pads": len(s.pads), "bytes": int(sum(s.sizes.values())), "cells": len(s.cells), "builders": s.builders, "cap_per_cell": cap}

    def usable(s, pad, b):
        if b == "hexchars" and s.sizes[pad] > s.hexchars_max: return False
        return True

    def blob(s, pad, d):
        k = (pad, d)
        if k not in s._blob:
            for kk in [kk for kk in s._blob if s.sizes[kk[0]] > (4 << 20)]: del s._blob[kk]
            b = open(s.pads[pad], "rb").read(); s._blob[k] = b if d == "fwd" else b[::-1]
        return s._blob[k]

    def arr(s, pad, b, d):
        if b == "hexchars":
            k = (pad, d)
            if k not in s._hex:
                s._hex[k] = build(s.blob(pad, d), "hexchars")
            return s._hex[k]
        return build(s.blob(pad, d), b)

    def symlen(s, pad, b, d):
        n = s.sizes[pad]
        if b == "nibbles": return 2 * n
        if b == "hexchars": return len(s.arr(pad, b, d))
        return n

    def keyfull(s, meta):
        b, d, pad, off = meta["b"], meta["dir"], meta["pad"], meta["off"]
        if b == "hexchars": return s.arr(pad, b, d)[off:off + 1200].astype(np.int64).tolist()
        return window(s.blob(pad, d), b, off, 1200).astype(np.int64).tolist()

    def head28(s, meta):
        k = s.keyfull(meta)[:28]
        if len(k) < 28: k = k + [0] * (28 - len(k))
        return np.array(k, dtype=np.int8)

    def meta_str(s, m): return "%s:%s:%s:o%d" % (m["pad"], m["b"], m["dir"], m["off"])

    def plant_len(s, meta): return 240

    def cfull(s, cname): return U[:240]

    def random_meta(s, rng):
        while True:
            pad, b, d = rng.choice(s.cells)
            n = s.symlen(pad, b, d)
            if n >= 2000: break
        return {"pad": pad, "b": b, "dir": d, "off": rng.randrange(0, n - 1000)}

    def planned(s):
        tot = 0; per = {}
        for (pad, b, d) in s.cells:
            n = s.symlen(pad, b, d) - NEEDROOM
            if n <= 0: continue
            c = len(offset_set(n, s.cap, s.ladder, s.extra.get(pad, []))); per["%s|%s|%s" % (pad, b, d)] = [c, n]; tot += c
        return tot, per

    def batches(s):
        for (pad, b, d) in s.cells:
            a = s.arr(pad, b, d); n = len(a) - NEEDROOM
            if n <= 0: continue
            offs = offset_set(n, s.cap, s.ladder, s.extra.get(pad, []))
            ar = np.arange(28)
            for i in range(0, len(offs), G.BATCH):
                o = offs[i:i + G.BATCH]
                K28 = np.ascontiguousarray(a[o[:, None] + ar[None, :]].T)
                metas = [{"pad": pad, "b": b, "dir": d, "off": int(x)} for x in o]
                yield {"K28": K28, "metas": metas, "Cs": [("U", U[:120])], "group": "%s|%s|%s" % (s.name, pad, b)}
            del a


def regen_p3(scratch):
    """Rebuild the 28 R17-P3 pads into `scratch` using the committed build_pads.py (paths redirected; manifest written to this lane dir)."""
    bp = _load("r17buildpads", os.path.join(R17, "P3_tables", "build_pads.py"))
    bp.DATA = scratch; bp.PADS = os.path.join(scratch, "pads"); bp.HERE = HERE
    os.makedirs(bp.PADS, exist_ok=True)
    bp.main()
    orig = json.load(open(os.path.join(R17, "P3_tables", "pads_manifest.json")))["pads"]
    new = json.load(open(F("pads_manifest.json")))["pads"]
    od = {p["name"]: p for p in orig}; nd = {p["name"]: p for p in new}
    cmp = {"orig_n": len(od), "regen_n": len(nd), "match_sha": [], "mismatch": [], "missing_in_regen": sorted(set(od) - set(nd)), "extra_in_regen": sorted(set(nd) - set(od))}
    for k in sorted(set(od) & set(nd)):
        (cmp["match_sha"] if od[k]["sha256"] == nd[k]["sha256"] else cmp["mismatch"]).append(k if od[k]["sha256"] == nd[k]["sha256"] else {"name": k, "orig_bytes": od[k]["bytes"], "regen_bytes": nd[k]["bytes"]})
    json.dump(cmp, open(F("p3_regen_compare.json"), "w"), indent=1)
    return cmp, bp.PADS
