"""Key-set builders for the head-screened families (all regenerated from committed code)."""
import os, sys, re, json
from c1common import *
from engine import KeySet
from lib import _load
sys.path.insert(0, os.path.join(AN, "round10b", "B1-overlooked-artifact"))
import b1_keys
from lp import gematria as gp
NN = 29
NEED = 1100

def tile(base, n=NEED):
    out = []
    while len(out) < n: out.extend(base)
    return np.array(out[:n], dtype=np.int64)

PS = ("1041279065891998535982789873959431895640442510695567564373922695237268242385295908173" "9834390370374475764863415203423499357108713631")
MAYAN = [10, 2, 14, 7, 19, 6, 18, 12, 7, 8, 17, 0, 19]

def vig_entries():
    """R30 B1 grid: keys x sign x phase (<=12 as MAXPHASE). Returns list of (label, base_key_array, phase_count, sign)."""
    alpha, numer = b1_keys.build()
    ents = []
    for r in alpha:
        try: k = gp.keyword_to_indices(r["key"])
        except ValueError: continue
        if len(k) < 1: continue
        ents.append(("A:%s:%s" % (r["tag"], r["key"][:24]), k, min(len(k), 12)))
    for r in numer:
        d = r["digits"]
        for rd, st in (("digit", [int(c) for c in d]), ("pair29", [int(d[i:i + 2]) % NN for i in range(0, len(d) - 1, 2)])):
            if len(st) >= 2: ents.append(("N:%s:%s:%s" % (r["tag"], rd, d[:12]), st, min(len(st), 12)))
    return ents, len(alpha), len(numer)

def c18_entries():
    """R10b / campaign18 numeric2: P.S. digit string, Mayan list, @1231507051321 handle: single/pairs/reversed, ALL phases."""
    ents = []
    tw = "1231507051321"
    for nm, d in (("PS", PS), ("TWEET1231507051321", tw)):
        sg = [int(c) % NN for c in d]; pr = [int(d[i:i + 2]) % NN for i in range(len(d) - 1)]; pr2 = [int(d[i:i + 2]) % NN for i in range(0, len(d) - 1, 2)]
        for tag, st in (("single", sg), ("pairs_overlap", pr), ("pairs_disjoint", pr2), ("rev_single", sg[::-1]), ("rev_pairs", [int(d[i:i + 2]) % NN for i in range(len(d) - 1)][::-1])):
            ents.append(("C18:%s:%s" % (nm, tag), st, len(st)))
    ents.append(("C18:MAYAN", [x % NN for x in MAYAN], len(MAYAN))); ents.append(("C18:MAYAN_rev", [x % NN for x in reversed(MAYAN)], len(MAYAN)))
    return ents

def vig_keyset(ents):
    """expand entries x phases x signs -> KeySet (plain = C + sign*K  =>  E = -sign*K)."""
    cols = []; meta = []
    for (lab, k, nph) in ents:
        kk = np.array(k, dtype=np.int64)
        for ph in range(nph):
            for sign in (-1, +1):
                meta.append((lab, ph, sign)); cols.append((kk, ph, sign))
    B = len(meta); heads = np.empty((28, B), dtype=np.int8)
    for b, (kk, ph, sign) in enumerate(cols):
        L = len(kk); idx = (np.arange(28) + ph) % L; heads[:, b] = (-sign * kk[idx]) % NN
    def full(b):
        kk, ph, sign = cols[b]; L = len(kk); return [int(v) for v in (-sign * kk[(np.arange(NEED) + ph) % L]) % NN]
    return KeySet(heads, full, lambda b: "%s|ph%d|s%+d" % meta[b])

def page_Cs(minlen=120, atbash=True, pages=None):
    out = []
    segs = NC.segments()[:-2]
    for p, s in enumerate(segs):
        if pages is not None and p not in pages: continue
        if len(s) < minlen: continue
        out.append(("p%02d" % p, list(s[:minlen])))
        if atbash: out.append(("p%02d_atb" % p, [(NN - 1 - c) % NN for c in s[:minlen]]))
    return out


# ---------------------------------------------------------------- R43 (B5 composed keys) : copied from composed_key.py
from lp import ciphers as cph
COEFS = [(+1, +1), (+1, -1), (-1, +1), (-1, -1), (+1, 0), (-1, 0), (0, +1), (0, -1)]

def b5_words():
    ws = []
    for line in open(os.path.join(LP, "data", "keys", "thematic.txt"), encoding="utf-8"):
        w = line.strip().upper()
        if w: ws.append(w)
    seeds = json.load(open(os.path.join(AN, "recon", "i7_constants", "priority_seeds.json")))
    for w in seeds.get("keyword_seeds", []):
        if w.upper() not in ws: ws.append(w.upper())
    out = []
    for w in ws:
        k = gp.keyword_to_indices(w)
        if 2 <= len(k) <= 20: out.append((w, np.array(k, dtype=np.int64)))
    return out

def b5_keyset(goffs=64):
    words = b5_words(); GL = 1100 + goffs + 40
    GS = [("phi_prime", np.array(cph.prime_totient_stream(GL), dtype=np.int64)), ("prime", np.array(cph.prime_stream(GL), dtype=np.int64)), ("totient", np.array(cph.totient_stream(GL), dtype=np.int64))]
    blocks = []; meta = []
    t = np.arange(28)[:, None]
    for wname, W in words:
        Lw = len(W)
        for gname, G in GS:
            for cw, cg in COEFS:
                wps = np.arange(Lw) if cw else np.array([0]); gos = np.arange(goffs) if cg else np.array([0])
                kw = (cw * W[(t[:, :, None] + wps[None, None, :]) % Lw]) if cw else np.zeros((28, 1, 1), dtype=np.int64)  # (28,1,nwp)
                kg = (cg * G[gos[None, None, :] + t[:, :, None]]) if cg else np.zeros((28, 1, 1), dtype=np.int64)               # (28,1,ngo)
                # combine: (28, nwp, ngo)
                a = kw[:, 0, :][:, :, None] if cw else np.zeros((28, 1, 1), dtype=np.int64)
                b = kg[:, 0, :][:, None, :] if cg else np.zeros((28, 1, 1), dtype=np.int64)
                K = (a + b) % NN; nwp, ngo = K.shape[1], K.shape[2]
                K = np.broadcast_to(K, (28, len(wps), len(gos))).reshape(28, -1)
                blocks.append((-K) % NN)   # sign +1 : plain = C + K  =>  E = -K
                for wp in wps:
                    for go in gos: meta.append((wname, gname, cw, cg, int(wp), int(go)))
    heads = np.concatenate(blocks, axis=1).astype(np.int8); assert heads.shape[1] == len(meta)
    WD = dict(words); GD = dict(GS)
    def full(b):
        wname, gname, cw, cg, wp, go = meta[b]; W = WD[wname]; G = GD[gname]; Lw = len(W)
        kw = cw * W[(np.arange(NEED) + wp) % Lw] if cw else np.zeros(NEED, dtype=np.int64)
        kg = cg * G[go:go + NEED] if cg else np.zeros(NEED, dtype=np.int64)
        return [int(v) for v in (-(kw + kg)) % NN]
    return KeySet(heads, full, lambda b: "%s|%s|%+d|%+d|wp%d|go%d" % meta[b]), len(words)


# ---------------------------------------------------------------- R32 (B04 slogan seeds)
def b04_keyset(prefixes=("slogan",)):
    b04 = os.path.join(AN, "round13", "B04"); sys.path.insert(0, b04)
    import importlib
    S = _load("b04_seeds", os.path.join(b04, "seeds.py")); KSm = _load("b04_ks", os.path.join(b04, "ks.py"))
    import re as _re
    hs = open(os.path.join(b04, "harness.py"), encoding="utf-8").read()
    MAX_SKIP = int(_re.search(r"^MAX_SKIP\s*=\s*(\d+)", hs, _re.M).group(1)); HEAD_L = int(_re.search(r"^HEAD_L\s*=\s*(\d+)", hs, _re.M).group(1))
    nsym = 0 + HEAD_L * (MAX_SKIP + 2) + 128           # harness._init: max(offs)+maxlen*(MAX_SKIP+2)+128 with offs=(0,), maxlen=HEAD_L
    seeds = [(l, b) for (l, b) in S.build() if l.startswith(prefixes)]
    gens = list(KSm.GEN_NAMES); reds = list(KSm.RED_NAMES)
    base = {}; heads = []; meta = []
    for si, (label0, seed) in enumerate(seeds):
        label = "%s#%d:%s" % (label0, si, seed[:24].decode('latin1').replace('|','/'))
        for g in gens:
            try: raw = KSm.make_bytes(g, seed, int(nsym * 1.35) + 256)
            except Exception: continue
            for rd in reds:
                bs = KSm.make_ks(g, rd, seed, nsym, raw=raw)
                for dr in ("fwd", "rev"):
                    K = bs if dr == "fwd" else bs[::-1]
                    if len(K) < 28: continue
                    for sg in (-1, +1):
                        # plain = C + sg*K -> E = -sg*K
                        E_ = [(-sg * int(v)) % NN for v in K[:28]]
                        heads.append(E_); meta.append((si, label, g, rd, dr, sg))
                    base[len(base)] = None
    # (re-derive lazily) -- keep only seed bytes lookup
    H = np.array(heads, dtype=np.int8).T.copy()
    cache = {}
    def full(b):
        si, label, g, rd, dr, sg = meta[b]; key = (si, g, rd)
        if key not in cache:
            seed = seeds[si][1]; raw = KSm.make_bytes(g, seed, int(nsym * 1.35) + 256); cache[key] = KSm.make_ks(g, rd, seed, nsym, raw=raw)
            if len(cache) > 4000: cache.clear(); cache[key] = KSm.make_ks(g, rd, seed, nsym, raw=raw)
        bs = cache[key]; K = bs if dr == "fwd" else bs[::-1]
        K = list(K) + [0] * max(0, NEED - len(K))      # keyskip decode only needs the first ~L*2 symbols
        return [(-sg * int(v)) % NN for v in K[:NEED]]
    return KeySet(H, full, lambda b: "%s|%s|%s|%s|s%+d" % meta[b][1:]), len(seeds), nsym
