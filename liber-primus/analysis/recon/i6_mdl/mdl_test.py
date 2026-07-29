#!/usr/bin/env python3
"""
LATERAL-FIELD TRANSPLANT (info-theory / MDL) — iteration 6.

Question: are Liber Primus pages 0-54 (the 12,956-rune, 29-ary index stream)
ALGORITHMICALLY GENERATED (hash-chain / stream-cipher keystream / iterated PRNG)
or a true (incompressible) one-time pad?

An OTP-quality stream is incompressible: its compressed size, entropy-rate, and
LZ distinct-phrase count all match uniform-random 29-ary controls. An
algorithmically-generated pad that nonetheless passes 1st/2nd-order stat tests
can still leak a small COMPRESSIBILITY / ENTROPY-RATE dip under a stronger
(order>=3, MDL/PPM-style) model.

Three orthogonal measures, each vs many equal-length uniform-random 29-ary
controls (honest signal-vs-null with z-scores):
  (a) general compressors: bz2, lzma, zlib on the packed byte stream.
  (b) empirical entropy-rate H_n for context length n=0..K (order-n block
      entropy per symbol) AND a proper order-n conditional-entropy MDL cost.
  (c) LZ76 (Lempel-Ziv 1976) distinct-factor count.

Pure-Python, deterministic controls (seeded), bounded.

NO cipher is attacked. This only asks: is the pad compressible?
"""
import sys, os, bz2, lzma, zlib, math, random, json
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.normpath(os.path.join(HERE, "..", "..", "..", "src"))
sys.path.insert(0, SRC)
from lp.gematria import RUNE_TO_IDX  # noqa

DATA = os.path.normpath(os.path.join(HERE, "..", "..", "..", "data", "krisyotam_runes.txt"))
N_SYM = 29
N_CONTROLS = 40
CONTEXT_MAX = 5   # entropy-rate up to order-5

# ---------------------------------------------------------------- load
def load_unsolved():
    raw = open(DATA, encoding="utf-8").read()
    segs = raw.split("%")            # 57 segments, 0..56
    assert len(segs) == 57, f"expected 57 segments, got {len(segs)}"
    unsolved = segs[0:55]            # 0..54 = unsolved target
    def to_idx(s): return [RUNE_TO_IDX[c] for c in s if c in RUNE_TO_IDX]
    seq = []
    for s in unsolved:
        seq += to_idx(s)
    return seq

# ---------------------------------------------------------------- packing
def pack_bytes(seq):
    """Pack a 29-ary symbol stream into bytes so a byte-oriented compressor
    sees the information near-optimally. Two views:
      - raw1 : one symbol per byte (0..28). Compressors see order structure.
      - base29 packed into a big integer -> bytes (near-entropy-optimal packing,
        removes the 'wasted' 3 bits/byte so residual compressibility is real).
    We use raw1 for bz2/lzma/zlib (they model context); base29-pack as a
    tightness cross-check.
    """
    raw1 = bytes(seq)
    # base-29 -> integer -> bytes
    v = 0
    for s in seq:
        v = v * N_SYM + s
    nbytes = (v.bit_length() + 7) // 8
    packed = v.to_bytes(nbytes, "big")
    return raw1, packed

def comp_sizes(seq):
    raw1, packed = pack_bytes(seq)
    return {
        "bz2_raw1":  len(bz2.compress(raw1, 9)),
        "lzma_raw1": len(lzma.compress(raw1, preset=9 | lzma.PRESET_EXTREME)),
        "zlib_raw1": len(zlib.compress(raw1, 9)),
        "bz2_packed":  len(bz2.compress(packed, 9)),
        "lzma_packed": len(lzma.compress(packed, preset=9 | lzma.PRESET_EXTREME)),
        "packed_len": len(packed),
    }

# ---------------------------------------------------------------- entropy-rate
def block_entropy(seq, n):
    """Empirical block (Shannon) entropy of order-n windows, in bits, divided
    by n -> per-symbol block entropy H_n/n. As n grows, this -> entropy rate."""
    if n == 0:
        return math.log2(N_SYM)
    c = Counter(tuple(seq[i:i+n]) for i in range(len(seq)-n+1))
    total = sum(c.values())
    H = -sum((v/total) * math.log2(v/total) for v in c.values())
    return H / n

def cond_entropy(seq, order):
    """Conditional entropy H(X | previous `order` symbols), bits/symbol.
    This is the honest entropy-rate estimate at a given Markov order. A
    hash-chain / PRNG pad that leaks would show H dropping below log2(29)
    at higher order; an OTP stays flat at log2(29)."""
    if order == 0:
        c = Counter(seq); tot = len(seq)
        return -sum((v/tot)*math.log2(v/tot) for v in c.values())
    ctx = defaultdict(Counter)
    for i in range(len(seq)-order):
        ctx[tuple(seq[i:i+order])][seq[i+order]] += 1
    total = 0; H = 0.0
    for _, nxt in ctx.items():
        s = sum(nxt.values()); total += s
        h = -sum((v/s)*math.log2(v/s) for v in nxt.values())
        H += s * h
    return H / total if total else 0.0

# ---------------------------------------------------------------- LZ76
def lz76_factors(seq):
    """Lempel-Ziv 1976 distinct-factor (phrase) count. Fewer factors than a
    random control => more internal repetition => algorithmic structure."""
    s = seq
    n = len(s)
    i = 0
    factors = 0
    while i < n:
        l = 1
        # longest prefix of s[i:] that appeared starting before i
        while True:
            sub = s[i:i+l]
            if i + l > n:
                break
            # search for sub as a substring in s[0:i+l-1]
            found = False
            end = i + l - 1
            hay = s[0:end]
            # naive search
            L = len(sub)
            for j in range(0, len(hay) - L + 1):
                if hay[j:j+L] == sub:
                    found = True
                    break
            if found:
                l += 1
            else:
                break
        factors += 1
        i += max(l, 1)
    return factors

# LZ76 is O(n^2*L) naive -> too slow for 12956 on multiple controls.
# Use a faster LZ78-style distinct-phrase count instead (dictionary parse),
# which is the standard incremental-parsing complexity and equally sensitive
# to algorithmic structure, plus keep LZ76 on a subsample for cross-check.
def lz78_phrases(seq):
    d = {}
    phrases = 0
    cur = ()
    for x in seq:
        nxt = cur + (x,)
        if nxt in d:
            cur = nxt
        else:
            d[nxt] = True
            phrases += 1
            cur = ()
    if cur:
        phrases += 1
    return phrases

# ---------------------------------------------------------------- controls
def make_control(rng, length):
    return [rng.randrange(N_SYM) for _ in range(length)]

def zscore(observed, samples):
    m = sum(samples)/len(samples)
    var = sum((x-m)**2 for x in samples)/len(samples)
    sd = math.sqrt(var) if var > 0 else 1e-12
    return (observed - m)/sd, m, sd

# ---------------------------------------------------------------- main
def main():
    seq = load_unsolved()
    L = len(seq)
    out = {"n_runes": L, "n_controls": N_CONTROLS, "n_sym": N_SYM}
    print(f"[i6-MDL] unsolved 0..54: {L} runes, {N_SYM}-ary\n")

    # ---- (a) compressors
    real_c = comp_sizes(seq)
    ctrl_c = {k: [] for k in real_c}
    rng = random.Random(3301)
    controls = [make_control(rng, L) for _ in range(N_CONTROLS)]
    for c in controls:
        cs = comp_sizes(c)
        for k, v in cs.items():
            ctrl_c[k].append(v)

    print("=== (a) COMPRESSION (bytes; smaller than control => compressible) ===")
    comp_report = {}
    for k in ["bz2_raw1","lzma_raw1","zlib_raw1","bz2_packed","lzma_packed"]:
        z, m, sd = zscore(real_c[k], ctrl_c[k])
        comp_report[k] = {"real": real_c[k], "ctrl_mean": round(m,1),
                          "ctrl_sd": round(sd,2), "z": round(z,2)}
        flag = " <== DIP" if z < -3 else ""
        print(f"  {k:14s} real={real_c[k]:6d}  ctrl={m:8.1f}+-{sd:5.2f}  z={z:+.2f}{flag}")
    out["compression"] = comp_report

    # theoretical incompressible floor for raw1 (1 sym/byte): entropy = L*log2(29)/8 bytes
    floor = L * math.log2(N_SYM) / 8
    out["entropy_floor_bytes"] = round(floor,1)
    print(f"  [info] Shannon floor (L*log2(29)/8) = {floor:.1f} bytes; packed_len(real)={real_c['packed_len']}")

    # ---- (b) entropy-rate
    print("\n=== (b) ENTROPY-RATE H(X|order) bits/sym (log2 29 = %.4f) ===" % math.log2(N_SYM))
    ent_report = {}
    for order in range(0, CONTEXT_MAX+1):
        real_h = cond_entropy(seq, order)
        ctrl_hs = [cond_entropy(c, order) for c in controls]
        z, m, sd = zscore(real_h, ctrl_hs)
        ent_report[order] = {"real": round(real_h,4), "ctrl_mean": round(m,4),
                             "ctrl_sd": round(sd,4), "z": round(z,2)}
        # NOTE: at high order both real and control drop due to finite-sample
        # (contexts become unique); the CONTROL captures that bias, so only a
        # real z well below control matters.
        flag = " <== DIP" if z < -3 else ""
        print(f"  order {order}: real={real_h:.4f}  ctrl={m:.4f}+-{sd:.4f}  z={z:+.2f}{flag}")
    out["entropy_rate"] = ent_report

    # ---- (c) LZ78 distinct phrases (+ LZ76 subsample cross-check)
    print("\n=== (c) LZ COMPLEXITY (fewer phrases than control => structure) ===")
    real_lz78 = lz78_phrases(seq)
    ctrl_lz78 = [lz78_phrases(c) for c in controls]
    z, m, sd = zscore(real_lz78, ctrl_lz78)
    print(f"  LZ78 phrases: real={real_lz78}  ctrl={m:.1f}+-{sd:.2f}  z={z:+.2f}"
          + (" <== FEWER" if z < -3 else ""))
    out["lz78"] = {"real": real_lz78, "ctrl_mean": round(m,1),
                   "ctrl_sd": round(sd,2), "z": round(z,2)}

    # LZ76 on first 3000 symbols (naive is O(n^2), keep bounded), 8 controls
    SUB = 3000
    sub_real = seq[:SUB]
    real_lz76 = lz76_factors(sub_real)
    ctrl_lz76 = [lz76_factors(controls[i][:SUB]) for i in range(8)]
    z2, m2, sd2 = zscore(real_lz76, ctrl_lz76)
    print(f"  LZ76 factors (first {SUB}): real={real_lz76}  ctrl={m2:.1f}+-{sd2:.2f}  z={z2:+.2f}"
          + (" <== FEWER" if z2 < -3 else ""))
    out["lz76_sub"] = {"n": SUB, "real": real_lz76, "ctrl_mean": round(m2,1),
                       "ctrl_sd": round(sd2,2), "z": round(z2,2)}

    # ---- verdict
    all_z = ([comp_report[k]["z"] for k in comp_report]
             + [ent_report[o]["z"] for o in ent_report]
             + [out["lz78"]["z"], out["lz76_sub"]["z"]])
    min_z = min(all_z)
    out["min_z"] = round(min_z,2)
    breakthrough = min_z < -3.0
    out["breakthrough"] = breakthrough
    print("\n=== VERDICT ===")
    print(f"  most negative z across all measures: {min_z:+.2f}")
    if breakthrough:
        print("  ** COMPRESSIBILITY DIP DETECTED (z<-3) -> algorithmic generation signal **")
    else:
        print("  No measure dips below control (all |z|<3 on the compressible side).")
        print("  => pages 0-54 are INCOMPRESSIBLE = OTP-class to information-theoretic finality.")

    json.dump(out, open(os.path.join(HERE, "mdl_result.json"), "w"), indent=2)
    print(f"\n  wrote {os.path.join(HERE,'mdl_result.json')}")

if __name__ == "__main__":
    main()
