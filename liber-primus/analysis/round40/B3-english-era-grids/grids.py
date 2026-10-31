"""R40-B3 grids: B-04 and R16-KDF key-list regeneration from the committed original code."""
import os, sys, time, random, itertools
sys.dont_write_bytecode = True
import numpy as np
from engine import LP, _load, U, F
sys.path[:0] = [os.path.join(LP, "src"), os.path.join(LP, "analysis"), os.path.join(LP, "analysis", "round11"), os.path.join(LP, "analysis", "campaign18_skip")]
import lib_numchannel as nc
B04 = os.path.join(LP, "analysis", "round13", "B04")
SEEDS = _load("b04seeds", os.path.join(B04, "seeds.py"))
KS = _load("b04ks", os.path.join(B04, "ks.py"))
BATCH = 12288
PAGES = [list(p) for p in nc.segments()[:-2]]
assert len(PAGES) == 55
OFFS_B = [0, 1, 2, 3, 4, 5, 6, 7, 16, 29, 64, 128, 256, 512, 1024, 3301]


class Acc:
    def __init__(self): self.d = {}
    def add(self, g, col, meta):
        c = self.d.setdefault(g, ([], []))
        c[0].append(col); c[1].append(meta)
        if len(c[0]) >= BATCH:
            out = (g, c); self.d[g] = ([], []); return out
        return None
    def rest(self):
        for g, c in list(self.d.items()):
            if c[0]: yield g, c
        self.d = {}


def _pack(g, c, Cs):
    return {"K28": np.stack(c[0], axis=1).astype(np.int8), "metas": c[1], "Cs": Cs, "group": g}


class B04Grid:
    name = "B04"
    NSYM = {"A": 728, "B": 4029, "C": 628}

    def __init__(s):
        s.entries = SEEDS.build(); s.core = SEEDS.core(s.entries)
        s.counts = {"seeds": len(s.entries), "core": len(s.core), "generators": len(KS.GEN_NAMES), "reductions": len(KS.RED_NAMES)}

    def stream(s, seedb, gen, red, nsym):
        raw = KS.make_bytes(gen, seedb, int(nsym * 1.35) + 256)
        return KS.make_ks(gen, red, seedb, nsym, raw=raw)

    def keyfull(s, meta):
        b = bytes.fromhex(meta["seed"]); base = s.stream(b, meta["gen"], meta["red"], s.NSYM[meta["stage"]])
        K = base if meta["dir"] == "fwd" else base[::-1]
        return list(K[meta["off"]:])

    def head28(s, meta): return np.array(s.keyfull(meta)[:28], dtype=np.int8)

    def meta_str(s, m): return "%s:%s:%s:%s:%s:o%d:%s" % (m["stage"], m["seed"][:24], m["gen"], m["red"], m["dir"], m["off"], m.get("label", "?"))

    def plant_len(s, meta): return 240

    def cfull(s, cname):
        if cname == "U": return U[:240]
        return PAGES[int(cname[2:4])][:240]

    def random_meta(s, rng):
        stage = rng.choice(("A", "B"))
        if stage == "A":
            lab, b = rng.choice(s.entries); red = rng.choice(KS.RED_NAMES); off = 0
        else:
            lab, b = rng.choice(s.core); red = rng.choice(("mod29", "rej29")); off = rng.choice(OFFS_B)
        return {"stage": stage, "label": lab, "seed": b.hex(), "gen": rng.choice(KS.GEN_NAMES), "red": red, "dir": rng.choice(("fwd", "rev")), "off": off}

    stages = ("A", "B", "C")

    def batches(s):
        stages = s.stages
        CsU = [("U", U[:120])]
        if "A" in stages:
            acc = Acc()
            for lab, b in s.entries:
                for g in KS.GEN_NAMES:
                    raw = KS.make_bytes(g, b, int(s.NSYM["A"] * 1.35) + 256)
                    for red in KS.RED_NAMES:
                        base = np.array(KS.make_ks(g, red, b, s.NSYM["A"], raw=raw), dtype=np.int8)
                        for dr in ("fwd", "rev"):
                            col = (base if dr == "fwd" else base[::-1])[:28].copy()
                            r = acc.add("A|" + red, col, {"stage": "A", "label": lab, "seed": b.hex(), "gen": g, "red": red, "dir": dr, "off": 0})
                            if r: yield _pack(r[0], r[1], CsU)
            for g, c in acc.rest(): yield _pack(g, c, CsU)
        if "B" in stages:
            acc = Acc()
            for lab, b in s.core:
                for g in KS.GEN_NAMES:
                    raw = KS.make_bytes(g, b, int(s.NSYM["B"] * 1.35) + 256)
                    for red in ("mod29", "rej29"):
                        base = np.array(KS.make_ks(g, red, b, s.NSYM["B"], raw=raw), dtype=np.int8)
                        for dr in ("fwd", "rev"):
                            K = base if dr == "fwd" else base[::-1]
                            for off in OFFS_B:
                                r = acc.add("B|" + red, K[off:off + 28].copy(), {"stage": "B", "label": lab, "seed": b.hex(), "gen": g, "red": red, "dir": dr, "off": off})
                                if r: yield _pack(r[0], r[1], CsU)
            for g, c in acc.rest(): yield _pack(g, c, CsU)
        if "C" in stages:
            CsP = [("pg%02d" % i, p[:min(120, len(p))]) for i, p in enumerate(PAGES)]
            acc = Acc()
            for lab, b in s.core:
                for g in KS.GEN_NAMES:
                    raw = KS.make_bytes(g, b, int(s.NSYM["C"] * 1.35) + 256)
                    for red in ("mod29", "rej29"):
                        base = np.array(KS.make_ks(g, red, b, s.NSYM["C"], raw=raw), dtype=np.int8)
                        r = acc.add("C|" + red, base[:28].copy(), {"stage": "C", "label": lab, "seed": b.hex(), "gen": g, "red": red, "dir": "fwd", "off": 0})
                        if r: yield _pack(r[0], r[1], CsP)
            for g, c in acc.rest(): yield _pack(g, c, CsP)

    def planned(s):
        ne, nc_ = len(s.entries), len(s.core); G = len(KS.GEN_NAMES)
        return {"A": ne * G * 5 * 2 * 4, "B": nc_ * G * 2 * 2 * 4 * len(OFFS_B), "C": nc_ * G * 2 * 1 * 4 * 55}


# ------------------------------------------------------------------ KDF
R15 = os.path.join(LP, "analysis", "round15", "KDF")
sys.path.insert(0, R15)
KSW = _load("kdf15sweep", os.path.join(R15, "sweep.py"))
KDF = KSW.kdf
KDF_BUF = 120 + 64


class KdfGrid:
    name = "KDF"

    def __init__(s):
        s.secrets = KSW.build_secrets()
        s.salts = KSW.STAGE_A_SALTS; s.kdfs = list(KDF.KDF_NAMES); s.reds = KSW.REDUCTIONS
        s.counts = {"secrets": len(s.secrets), "kdfs": len(s.kdfs), "salts": len(s.salts), "reductions": len(s.reds)}
        s._blk = {}

    def block(s, secret_hex, salt, kname):
        k = (secret_hex, salt, kname)
        if k not in s._blk:
            if len(s._blk) > 4000: s._blk.clear()
            s._blk[k] = KDF.derive(bytes.fromhex(secret_hex), salt, kname)
        return s._blk[k]

    def keyfull(s, meta):
        blk = s.block(meta["secret"], meta["salt"], meta["kdf"])
        if meta["dir"] == "fwd": return KDF.expand(blk, 1024, meta["red"])
        return KDF.expand(blk, KDF_BUF, meta["red"])[::-1]

    def head28(s, meta): return np.array(s.keyfull(meta)[:28], dtype=np.int8)

    def meta_str(s, m): return "%s:%s:%s:%s:%s" % (m["secret"][:24], m["kdf"], m["salt"], m["red"], m["dir"])

    def plant_len(s, meta): return 240 if meta["dir"] == "fwd" else 120

    def cfull(s, cname): return U[:240]

    def random_meta(s, rng):
        lab, b = rng.choice(s.secrets)
        return {"label": lab, "secret": b.hex(), "kdf": rng.choice(s.kdfs), "salt": rng.choice(s.salts), "red": rng.choice(s.reds), "dir": rng.choice(("fwd", "rev"))}

    def batches(s):
        CsU = [("U", U[:120])]; acc = Acc()
        for lab, b in s.secrets:
            sh = b.hex()
            for salt in s.salts:
                for kn in s.kdfs:
                    try: blk = KDF.derive(b, salt, kn)
                    except Exception: continue
                    for red in s.reds:
                        K = np.array(KDF.expand(blk, KDF_BUF, red), dtype=np.int8)
                        for dr in ("fwd", "rev"):
                            col = (K if dr == "fwd" else K[::-1])[:28].copy()
                            r = acc.add("KDF|" + red, col, {"label": lab, "secret": sh, "kdf": kn, "salt": salt, "red": red, "dir": dr})
                            if r: yield _pack(r[0], r[1], CsU)
        for g, c in acc.rest(): yield _pack(g, c, CsU)

    def planned(s): return len(s.secrets) * len(s.kdfs) * len(s.salts) * len(s.reds) * 8
