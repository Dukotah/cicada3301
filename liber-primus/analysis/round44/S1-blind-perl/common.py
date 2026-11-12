"""Shared helpers for lane S1 (blind adjudicator sweep). See PREREG.md."""
import os
import random
import re
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "A0-fresh-eyes-audit"))
import lp2  # noqa: E402

sys.path.insert(0, os.path.join(lp2.LP, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(lp2.LP, "analysis", "round19", "I1"))
sys.path.insert(0, os.path.join(lp2.LP, "src"))
N = 29
BLIND = os.path.join(HERE, "blind")
PAGE0 = os.path.join(HERE, "page0.txt")
MODES = ["s=+1 q=1", "s=+1 q=2", "s=-1 q=1", "s=-1 q=2"]


def build():
    subprocess.check_call(["gcc", "-O3", "-march=native", "-o", BLIND, os.path.join(HERE, "blind.c")])
    C = lp2.idx(lp2.unsolved())[0]
    open(PAGE0, "w").write(" ".join(map(str, C)) + "\n")
    return C


def ioc29(ssq, L):
    return N * (ssq - L) / (L * (L - 1))


def ssq_for(ioc, L):
    """Smallest integer sum of squares whose IoC x 29 is >= ioc."""
    import math
    return int(math.ceil(ioc * L * (L - 1) / N + L))


def run_kernel(gen, lo, hi, cipher, L1, T1, L2, T2, L3, hist=False):
    """Run the C kernel; return (records, hist or None). A record = (seed, mode, v1, v2, v3)."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "o.bin"); h = os.path.join(td, "h.bin")
        cmd = [BLIND, gen, str(lo), str(hi), cipher, str(L1), str(T1), str(L2), str(T2), str(L3), out] + ([h] if hist else [])
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
        raw = open(out, "rb").read()
        recs = [struct.unpack_from("<5I", raw, o) for o in range(0, len(raw), 20)]
        H = None
        if hist:
            hb = open(h, "rb").read()
            H = [list(struct.unpack_from("<2048Q", hb, m * 2048 * 8)) for m in range(4)]
        return recs, H


def perl_stream(seed, n):
    """Perl's int(rand(29)) after srand(seed): glibc/Perl drand48, 32-bit seed."""
    x = ((seed & 0xFFFFFFFF) << 16) | 0x330E
    out = []
    for _ in range(n):
        x = (x * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        out.append((x * 29) >> 48)
    return out


def perl_real(seed, n):
    """The same stream from the perl binary itself (independent of every line of this lane's code)."""
    r = subprocess.run(["perl", "-e", f"srand({seed}); print join(' ', map {{ int(rand(29)) }} 1..{n})"],
                       capture_output=True, text=True, check=True)
    return [int(x) for x in r.stdout.split()]


_SINGLE = {x: i for i, x in enumerate(lp2.TR) if len(x) == 1}
_SINGLE.update({"K": _SINGLE["C"], "V": _SINGLE["U"], "Z": _SINGLE["S"], "Q": _SINGLE["C"]})
_MULTI = sorted(((x, i) for i, x in enumerate(lp2.TR)), key=lambda z: -len(z[0]))


def _lw(w):
    return [_SINGLE[c] for c in w]


def _mg(w):
    w = w.replace("K", "C").replace("V", "U").replace("Z", "S").replace("Q", "C"); o = []; i = 0
    while i < len(w):
        if w.startswith("ING", i):
            o.append(21); i += 3; continue
        for x, k in _MULTI:
            if w.startswith(x, i):
                o.append(k); i += len(x); break
        else:
            i += 1
    return o


def plant_texts():
    def load(path, enc):
        t = open(path, encoding="utf-8", errors="ignore").read().upper()
        ws = re.sub(r"[^A-Z]+", " ", t[len(t) // 4: 3 * len(t) // 4]).split()
        return [v for w in ws[:60000] for v in enc(w)]
    keys = os.path.join(lp2.LP, "data", "keys")
    return {"English letter-wise": load(os.path.join(keys, "armada18", "melville_moby_dick.txt"), _lw),
            "English multigraph": load(os.path.join(keys, "armada18", "plato_republic_jowett.txt"), _mg),
            "Latin letter-wise": load(os.path.join(lp2.LP, "analysis", "latin", "latin_28233.txt"), _lw)}


VARIANTS = ["as written", "random relabelling", "C = P + K + 7", "Beaufort C = K - P"]
CONSTRUCTIONS = ["keyskip1", "skip_by_two", "coin_from_key"]


def make_plant(rng, stream, variant, construction, K, L=262, sign=+1):
    """Encipher a passage with keystream K under one of the repo's own constructions.

    sign=+1: C = P + K. sign=-1: C = P - K (done by handing the encipherer the negated key).
    Returns (C, info)."""
    import skipdecode as sk
    import constructions as cons
    a = rng.randrange(0, len(stream) - L - 1)
    P = stream[a:a + L]
    if variant == "random relabelling":
        perm = list(range(N)); rng.shuffle(perm); P = [perm[x] for x in P]
    elif variant == "C = P + K + 7":
        P = [(x + 7) % N for x in P]
    elif variant.startswith("Beaufort"):
        P = [(-x) % N for x in P]
    Kuse = K if sign == +1 else [(-k) % N for k in K]
    seed = rng.randrange(10 ** 6)
    if construction == "keyskip1":
        C, skips, _ = sk.encipher_keyskip(P, Kuse, sign=-1, supp=0.83, seed=seed)
        return C, {"n_skips": int(sum(skips))}
    if construction == "skip_by_two":
        return cons.enc_skip_by_two(P, Kuse, supp=0.83, seed=seed)
    return cons.enc_coin_from_key(P, Kuse, supp=0.83, seed=seed)
