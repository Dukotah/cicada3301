"""L5 / PREREG A.5 - re-run every payload-consuming test on the RESOLVED payload.

A-04 changed 3 of 256 bytes (indices 45, 50, 246). Every prior result over this payload was
computed on the un-corrected stream, and B-05's own control measured that flipping a single
byte moves a keystream decode from -4.170 (perfect) to -7.38 (noise) -- so "3 bytes" is not
a rounding error for any hash- or PRF-consuming test.

This script covers the fast tests. The B-05 generator family is a separate, longer job
(`propagate_b05.py`) because it is a beam sweep.

  1. structural characterization (entropy / printability / primality / factorisation)
  2. hash_hunt -- the page-56 "AN END" 512-bit target, over the resolved payload's
     representations x 10 algorithms
  3. round16 zeroFP E-02A / E-02B / H-03, re-run with the round16 instrument itself,
     pointed at the resolved payload by redirecting its `load_bytes`

    python3 propagate.py
"""
import hashlib
import io
import json
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PP = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51")
Z16 = os.path.join(ROOT, "liber-primus", "analysis", "round16", "zeroFP")

AN_END = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

PAYLOADS = {
    "canon_majority": os.path.join(PP, "canon_256.bin"),
    "canon_decimal_preferred": os.path.join(PP, "canon_256_decpref.bin"),
    "L5_resolved": os.path.join(HERE, "payload_resolved.bin"),
}


# ------------------------------------------------------------------ 1. structure
def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2:
        return False
    for p in witnesses:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in witnesses:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def small_factor(n, limit=100000):
    if n % 2 == 0:
        return 2
    f = 3
    while f < limit:
        if n % f == 0:
            return f
        f += 2
    return None


def characterize(data):
    from collections import Counter
    from math import log2
    c = Counter(data)
    H = -sum((v / len(data)) * log2(v / len(data)) for v in c.values())
    be = int.from_bytes(data, "big")
    le = int.from_bytes(data, "little")
    out = {
        "entropy_bits_per_byte": round(H, 4),
        "distinct_byte_values": len(c),
        "ascii_printable": sum(0x20 <= b < 0x7F for b in data),
        "has_00": 0 in data, "has_ff": 255 in data,
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    for name, v in (("big_endian", be), ("little_endian", le)):
        out[name] = {
            "bits": v.bit_length(),
            "is_probable_prime": miller_rabin(v),
            "smallest_factor_below_1e5": small_factor(v),
        }
    return out


# ------------------------------------------------------------------ 2. hash hunt
def representations(name, b):
    yield name, b
    yield name + ":reversed", b[::-1]
    yield name + ":hexstr", b.hex().encode()
    yield name + ":HEXSTR", b.hex().upper().encode()
    yield name + ":+newline", b + b"\n"
    yield name + ":hexstr+newline", b.hex().encode() + b"\n"
    yield name + ":bitrev8", bytes(int(format(x, "08b")[::-1], 2) for x in b)


ALGOS = ["sha512", "sha256", "sha384", "sha3_512", "sha3_256",
         "blake2b", "blake2s", "shake_256", "md5", "sha1"]


def hash_hunt(payloads):
    hits, n = [], 0
    for pname, b in payloads.items():
        for rname, rb in representations(pname, b):
            for a in ALGOS:
                h = hashlib.new(a)
                h.update(rb)
                d = h.hexdigest(64) if a == "shake_256" else h.hexdigest()
                n += 1
                if d == AN_END:
                    hits.append({"rep": rname, "algo": a})
    return {"hashes_computed": n, "target": AN_END, "hits": hits}


# ------------------------------------------------------------------ 3. zeroFP re-run
def zerofp_on(path_for_canon):
    sys.path.insert(0, Z16)
    import zerofp_tests as zfp
    real = zfp.load_bytes

    def redirected(p):
        if os.path.basename(str(p)) == "canon_256.bin":
            return real(path_for_canon)
        return real(p)

    zfp.load_bytes = redirected
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            e02 = zfp.e02_meta_parameters()
            h03 = zfp.h03_cookies_xor()
    finally:
        zfp.load_bytes = real
    return {"E-02": e02, "H-03": h03, "stdout_tail": buf.getvalue()[-1500:]}


def main():
    data = {k: open(v, "rb").read() for k, v in PAYLOADS.items() if os.path.exists(v)}
    out = {"payloads": sorted(data)}

    print("=" * 74)
    print("1. STRUCTURAL CHARACTERIZATION")
    print("=" * 74)
    out["characterization"] = {}
    for k, b in data.items():
        c = characterize(b)
        out["characterization"][k] = c
        print("  %-24s H=%.4f  distinct=%d  printable=%d  BE prime=%s (small factor %s)"
              % (k, c["entropy_bits_per_byte"], c["distinct_byte_values"],
                 c["ascii_printable"], c["big_endian"]["is_probable_prime"],
                 c["big_endian"]["smallest_factor_below_1e5"]))

    print("\n" + "=" * 74)
    print("2. HASH HUNT vs the page-56 'AN END' 512-bit target")
    print("=" * 74)
    hh = hash_hunt(data)
    out["hash_hunt"] = hh
    print("  %d hashes computed over %d payload variants; hits: %s"
          % (hh["hashes_computed"], len(data), hh["hits"] or "none"))

    print("\n" + "=" * 74)
    print("3. round16 zeroFP E-02 / H-03 re-run on the RESOLVED payload")
    print("=" * 74)
    z = zerofp_on(PAYLOADS["L5_resolved"])
    out["zerofp_on_resolved"] = {"E-02": z["E-02"], "H-03": z["H-03"]}
    print("  E-02 verdict: %s" % z["E-02"].get("verdict"))
    print("       %s" % str(z["E-02"].get("detail", ""))[:300])
    print("  H-03 verdict: %s" % z["H-03"].get("verdict"))
    print("       %s" % str(z["H-03"].get("detail", ""))[:300])

    with open(os.path.join(HERE, "propagation_results.json"), "w") as f:
        json.dump(out, f, indent=1, default=str)
    print("\nwrote propagation_results.json")


if __name__ == "__main__":
    main()
