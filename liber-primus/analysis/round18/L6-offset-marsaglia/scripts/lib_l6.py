"""Round 18 / L6 — OFFSET & MARSAGLIA — shared instrument layer.

Everything scoring-related is IMPORTED from the existing, gate-validated instruments:

    analysis/round17/lib_padsweep.py   dense_scan (scores EVERY offset), trigram model,
                                       builders, hit_bar
    analysis/campaign18_skip/skipdecode.py   the skip-aware beam (NEVER rigid, AGENTS.md s4)
    benchmark/null.py                  threshold_for(n_trials, segment_len)

This module adds only three things Round 17 did not need:

 1. `sharded_scan` — dense_scan over a pad too large to hold as one int16 array, with an
    overlap that provably loses no offset.  Every builder used here is POSITION-LOCAL
    (byte i -> symbol i, or byte i -> symbols 2i, 2i+1), which is what makes sharding
    exact; `audit_builders.py` proves that by asserting equality against lib_padsweep's
    own whole-blob builders.
 2. `derived_keystream` — rebuilds the exact keystream of a Round-13 B-04 / Round-16 KDF /
    Round-16 PRNG result row, at ARBITRARY length, so its offset axis can be swept.
 3. `mine_configs` — reads the published results JSON of those three lanes.  No prior sweep
    is re-run (Round 18 rule 7); only their surviving configs are extended along the one
    axis they never covered.
"""
import os, sys, json, math, random, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, ".."))
ANALYSIS = os.path.abspath(os.path.join(LANE, "..", ".."))          # liber-primus/analysis
ROOT = os.path.abspath(os.path.join(ANALYSIS, ".."))                # liber-primus/

for p in (os.path.join(ANALYSIS, "round17"),
          os.path.join(ANALYSIS, "round13", "B04"),
          os.path.join(ANALYSIS, "round15", "KDF"),
          os.path.join(ANALYSIS, "round16", "prng"),
          os.path.join(ROOT, "benchmark")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np                                   # noqa: E402
import lib_padsweep as L                              # noqa: E402
import skipdecode as sk                               # noqa: E402
import null as nullmod                                # noqa: E402

N = 29
DATA = os.path.join(LANE, "data")
OUT = os.path.join(LANE, "out")
os.makedirs(OUT, exist_ok=True)

# ---- instrument settings, fixed in PREREG s2.2 ---------------------------------
MS = 8                 # max_skip. PREREG s2.1: R17/P1 measured 6/8 recovery at ms=3 on a
                       # real run-heavy pad and 60/60 at ms=8.  ms=3 is never used here
                       # except as the explicitly-labelled diagnostic in control_marsaglia.
HEAD = 400             # adjudication window, runes
BEAM_W = 120           # tier-1 beam width (lib_padsweep's, for comparability)
BEAM_W2 = 400          # tier-2 beam width (round13/B04's)
PLEN = L.PREFILTER_LEN # 24, the dense prefilter window
TIER2_GATE = -6.00     # PREREG s2.2

OFF_MAX_A1 = 1 << 20   # PREREG s3.1
OFF_MAX_A2 = 1 << 18   # PREREG s3.1

# span of keystream a single escalation consumes, worst case
SPAN = HEAD * (MS + 1) + 8            # 3608


# ================================================================= builders (local)
# Byte -> Z29 reductions. These are POSITION-LOCAL by construction, which is what makes
# sharding exact.  audit_builders.py asserts each is identical to lib_padsweep's.
def b_mod29(a):        return (a.astype(np.int16) % N)
def b_hi_nibble(a):    return ((a.astype(np.int16) >> 4) % N)
def b_lo_nibble(a):    return ((a.astype(np.int16) & 0xF) % N)
def b_byte_scaled(a):  return ((a.astype(np.int32) * N) // 256).astype(np.int16)


_P2I = None
def b_prime_to_idx(a):
    global _P2I
    if _P2I is None:
        p2i = np.full(256, -1, dtype=np.int16)
        for i, p in enumerate(L.gp.PRIMES):
            if p < 256:
                p2i[p] = i
        _P2I = p2i
    out = _P2I[a].astype(np.int16)
    return np.where(out < 0, a.astype(np.int16) % N, out)


def b_nibbles(a):
    """The TRUE hex-text reading: each hex character as its value 0-15, in order.

    `lib_padsweep.ks_hexchars` is NOT used anywhere in this lane: R17/P1 found it routes
    through `eng_to_idx`, which discards the digits 0-9, so it sweeps the A-F subsequence
    of the hex string (36.8% of it) rather than the hex reading.  See audit_builders.py,
    which re-derives that defect rather than taking it on trust.
    """
    x = a.astype(np.int16)
    out = np.empty(x.size * 2, dtype=np.int16)
    out[0::2] = x >> 4
    out[1::2] = x & 0xF
    return out


BUILDERS = {                     # name -> (fn, symbols per byte)
    "mod29":        (b_mod29, 1),
    "hi_nibble":    (b_hi_nibble, 1),
    "lo_nibble":    (b_lo_nibble, 1),
    "byte_scaled":  (b_byte_scaled, 1),
    "prime_to_idx": (b_prime_to_idx, 1),
    "nibbles":      (b_nibbles, 2),
}
EXCLUDED_BUILDERS = {
    "hexchars": "drops the digits 0-9 (eng_to_idx); it is the A-F subsequence of the hex "
                "string, not the hex reading. Replaced by `nibbles`. R17/P1 finding, "
                "re-derived in audit_builders.py."
}


# ================================================================= sharded dense scan
def sharded_scan(arr_u8, builder, sign, C, keep=1000, shard_bytes=1 << 25, reverse=False):
    """dense_scan over a pad too large to materialise as one keystream array.

    Returns (hits, n_offsets) with hits = [(pre_score, global_symbol_offset)] best-first.

    Correctness of the sharding: every builder in BUILDERS is position-local, and shards
    overlap by SPAN+PLEN symbols, so every offset whose 24-symbol prefilter window and
    whose SPAN-symbol escalation window both fit inside the pad is scored in at least one
    shard.  Offsets are de-duplicated on the global index.
    """
    fn, spb = BUILDERS[builder]
    n_bytes = arr_u8.size
    ov_sym = SPAN + PLEN + 16
    ov_bytes = int(math.ceil(ov_sym / spb)) + 8
    step = max(1, shard_bytes - ov_bytes)
    best = {}
    n_off = 0
    src = arr_u8[::-1] if reverse else arr_u8
    start = 0
    while start < n_bytes:
        stop = min(start + shard_bytes, n_bytes)
        seg = np.ascontiguousarray(src[start:stop])
        K = fn(seg)
        if K.size > PLEN:
            hits = L.dense_scan(K, C, sign=sign, keep=keep)
            base = start * spb
            for s, o in hits:
                g = base + int(o)
                if best.get(g, -1e9) < s:
                    best[g] = s
            n_off += K.size - PLEN
        del K, seg
        if stop >= n_bytes:
            break
        start += step
    rows = sorted(((v, k) for k, v in best.items()), reverse=True)[:keep * 4]
    # n_off double-counts the overlap regions; correct to the true distinct-offset count
    total_sym = n_bytes * spb
    n_true = max(0, total_sym - PLEN)
    return rows, min(n_off, n_true), total_sym


def build_full(arr_u8, builder, reverse=False):
    fn, _ = BUILDERS[builder]
    src = arr_u8[::-1] if reverse else arr_u8
    return fn(np.ascontiguousarray(src))


# ================================================================= escalation + nulls
def escalate(hits, K, C, sign, top=40, head=HEAD, ms=MS, beam_w=BEAM_W):
    """Beam-decode the dense survivors.  Skip-aware beam only (AGENTS.md s4 lesson 2)."""
    Kl = K if isinstance(K, list) else [int(x) for x in K]
    nk = len(Kl)
    Ch = [int(x) for x in C[:head]]
    out = []
    for score, o in hits[:top]:
        o = int(o)
        if o + head * (ms + 1) + 8 >= nk:
            continue
        bd = sk.beam_decode(Ch, Kl, sign=sign, o=o, beam_w=beam_w, max_skip=ms)
        out.append({"offset": o, "sign": sign, "pre": float(score),
                    "score": float(bd["score"]), "head": bd["translit"][:64]})
    out.sort(key=lambda r: r["score"], reverse=True)
    return out


def shuffle_null(K, seq_len=HEAD, n=200, seed0=3301, ms=MS, beam_w=BEAM_W):
    """This lane's OWN null: histogram-preserving, order-destroying, measured at ms=8 on
    the same keystream family and the same window.  A bigger skip budget gives the beam
    more freedom, so the null must be re-measured, never inherited."""
    Kl = K if isinstance(K, list) else [int(x) for x in K]
    base = [int(x) for x in L.nc.unsolved()[:seq_len]]
    span = max(1, len(Kl) - seq_len * (ms + 1) - 8)
    vals = []
    for k in range(n):
        r = random.Random(seed0 + k)
        s = list(base)
        r.shuffle(s)
        vals.append(sk.beam_decode(s, Kl, sign=-1, o=(k * 37) % span,
                                   beam_w=beam_w, max_skip=ms)["score"])
    return float(np.mean(vals)), float(np.max(vals))


def bar_for(n_trials, null_max, segment_len=HEAD):
    """PREREG s4: HIT iff score >= max(threshold_for(N), null_max + 0.5).

    `threshold_for` already carries the historical -5.5 as a FLOOR, so this bar is never
    looser than the habitual bar and is usually stricter.  It is the one reported.
    """
    t = nullmod.threshold_for(max(2, int(n_trials)), segment_len=segment_len)
    return max(t, null_max + 0.5), t


# ================================================================= derived keystreams
_KDF = _B04 = _PRNG = _SEEDS = None


def _lanes():
    global _KDF, _B04, _PRNG, _SEEDS
    if _B04 is None:
        import ks as b04ks
        import seeds as b04seeds
        import kdf as kdfmod
        import prng_sweep as prng
        _B04, _SEEDS, _KDF, _PRNG = b04ks, b04seeds, kdfmod, prng
    return _B04, _SEEDS, _KDF, _PRNG


def derived_keystream(cfg, nsym):
    """Rebuild the EXACT keystream of a mined result row, at arbitrary length.

    cfg["kind"] in {"b04", "kdf", "prng"}; the generator code is the originating lane's
    own, imported, never re-implemented.
    """
    b04ks, _, kdfmod, prng = _lanes()
    kind = cfg["kind"]
    if kind == "b04":
        seed = bytes.fromhex(cfg["seed_hex"])
        K = b04ks.make_ks(cfg["gen"], cfg["red"], seed, nsym)
    elif kind == "kdf":
        secret = bytes.fromhex(cfg["secret_hex"])
        block = kdfmod.derive(secret, cfg["salt"], cfg["kdf"])
        K = kdfmod.expand(block, nsym, cfg["reduction"])
    elif kind == "prng":
        K = list(prng.GEN_FUNCTIONS[cfg["gen"]](int(cfg["seed"]), nsym))
    else:
        raise ValueError(kind)
    K = list(K)[:nsym]
    if cfg.get("dir", "fwd") == "rev":
        K = K[::-1]
    return np.asarray(K, dtype=np.int16)


def ciphertext_for(cfg, n=None):
    """The ciphertext this config is scored against, with the row's own atbash applied."""
    C = [int(x) for x in L.nc.unsolved()]
    if int(cfg.get("atbash", 0) or 0):
        C = [(N - 1) - c for c in C]
    return C if n is None else C[:n]


# ================================================================= config mining
def _key(c):
    return (c["kind"], c.get("seed_hex") or c.get("secret_hex") or str(c.get("seed")),
            c.get("gen") or c.get("kdf"), c.get("red") or c.get("reduction"),
            c.get("salt"), int(c.get("sign", -1)), int(c.get("atbash", 0) or 0),
            c.get("dir", "fwd"))


def mine_configs():
    """Top configs of B-04 / R16-KDF / R16-PRNG, from their PUBLISHED results JSON.

    No sweep is re-run.  This reads what those lanes already measured and extends the ONE
    axis they all fixed at 0.
    """
    out, seen = [], set()

    def add(c):
        k = _key(c)
        if k in seen:
            return
        seen.add(k)
        out.append(c)

    b04 = os.path.join(ANALYSIS, "round13", "B04")
    for st in ("A", "B", "C"):
        p = os.path.join(b04, f"results_{st}.json")
        if not os.path.exists(p):
            continue
        for r in json.load(open(p)).get("top50", []):
            add({"kind": "b04", "src": f"B04/{st}", "seed_hex": r["seed_hex"],
                 "label": r.get("label"), "gen": r["gen"], "red": r["red"],
                 "sign": int(r["sign"]), "atbash": int(r.get("atbash", 0)),
                 "dir": r.get("dir", "fwd"), "prior_score": r["score"],
                 "prior_offset": r.get("offset", 0)})

    p = os.path.join(ANALYSIS, "round16", "KDF", "results_A.json")
    if os.path.exists(p):
        for r in json.load(open(p)).get("top50", []):
            add({"kind": "kdf", "src": "R16-KDF", "secret_hex": r["secret_hex"],
                 "label": r.get("label"), "kdf": r["kdf"], "salt": r["salt"],
                 "reduction": r["reduction"], "sign": int(r["sign"]),
                 "atbash": int(r.get("atbash", 0)), "dir": r.get("dir", "fwd"),
                 "prior_score": r["score"], "prior_offset": 0})

    p = os.path.join(ANALYSIS, "round16", "prng", "results.json")
    if os.path.exists(p):
        d = json.load(open(p))
        for r in d.get("top20", []):
            add({"kind": "prng", "src": "R16-PRNG", "gen": r["gen"], "seed": int(r["seed"]),
                 "sign": int(r["sign"]), "atbash": 0, "dir": r.get("dir", "fwd"),
                 "prior_score": r["score"], "prior_offset": 0})
    return out


def core_seeds():
    """B-04's 504-entry core dictionary, from its own validated builder."""
    _, b04seeds, _, _ = _lanes()
    return b04seeds.core(b04seeds.build())


def jdump(obj, path):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    os.replace(tmp, path)
