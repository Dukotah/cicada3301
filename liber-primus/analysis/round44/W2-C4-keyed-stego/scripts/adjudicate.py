#!/usr/bin/env python3
"""R44 W2-C4 — payload adjudicator (PREREG 'Adjudicator', FIXED) + null calibration.

Run as a script to calibrate F2/F3/naive on 10,000 random blobs -> results/calibration.json.
Imported by sweep.py for the live flags.
"""
import json, math, os, random, re

MAGICS = [b"\x1f\x8b", b"PK\x03\x04", b"7z\xbc\xaf", b"\xfd7zXZ", b"BZh",
          b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"%PDF", b"Rar!",
          b"Salted__", b"\x78\x01", b"\x78\x9c", b"\x78\xda",
          b"-----BEGIN PGP"]
ARMOR = b"-----BEGIN PGP"
PGP_TAGS = {1, 2, 3, 4, 6, 8, 9, 11, 14, 18}
PRINTABLE = set(range(32, 127)) | {9, 10, 13}

def entropy(b):
    if not b:
        return 0.0
    n = len(b)
    cnt = [0] * 256
    for x in b:
        cnt[x] += 1
    return -sum(c / n * math.log2(c / n) for c in cnt if c)

def printable_ratio(b):
    if not b:
        return 0.0
    return sum(1 for x in b if x in PRINTABLE) / len(b)

def f1_magic(b):
    head = b[:1024]
    return any(b.startswith(m) for m in MAGICS) or ARMOR in head

def f2_printable(b, declared_len):
    return declared_len >= 32 and len(b) >= 32 and printable_ratio(b[:8192]) >= 0.95

def naive_pgp(b):
    """the weak tag-byte check R43-F6 measured at 32.8% on noise — advisory record only."""
    if not b:
        return False
    c = b[0]
    return bool(c & 0x80) and ((c >> 2) & 0x0F in PGP_TAGS if not (c & 0x40)
                               else (c & 0x3F) in PGP_TAGS)

def f3_strict_pgp(b):
    """strict OpenPGP packet-chain parse: 1..8 packets, tags whitelisted, lengths
    consistent, >=95% of bytes consumed."""
    n = len(b)
    if n < 8:
        return False
    off, pkts = 0, 0
    while off < n and pkts < 8:
        c = b[off]
        if not (c & 0x80):
            break
        if c & 0x40:                       # new format
            tag = c & 0x3F
            if tag not in PGP_TAGS:
                break
            if off + 1 >= n:
                break
            l1 = b[off + 1]
            if l1 < 192:
                hl, plen = 2, l1
            elif l1 < 224:
                if off + 2 >= n:
                    break
                hl, plen = 3, ((l1 - 192) << 8) + b[off + 2] + 192
            elif l1 == 255:
                if off + 5 >= n:
                    break
                hl, plen = 6, int.from_bytes(b[off + 2:off + 6], "big")
            else:
                break                      # partial lengths: reject (not author shape)
        else:                              # old format
            tag = (c >> 2) & 0x0F
            if tag not in PGP_TAGS:
                break
            lt = c & 0x03
            if lt == 0:
                if off + 1 >= n: break
                hl, plen = 2, b[off + 1]
            elif lt == 1:
                if off + 2 >= n: break
                hl, plen = 3, int.from_bytes(b[off + 1:off + 3], "big")
            elif lt == 2:
                if off + 4 >= n: break
                hl, plen = 5, int.from_bytes(b[off + 1:off + 5], "big")
            else:
                break                      # indeterminate length: reject
        if plen > n - off - hl:
            break
        off += hl + plen
        pkts += 1
    return pkts >= 1 and off >= 0.95 * n

def adjudicate(payload, declared_len):
    """returns dict of stats + flags; FLAG = F1 or F2 or (F3 if armed by calibration)."""
    return dict(out_len=len(payload),
                entropy=round(entropy(payload[:8192]), 4),
                printable=round(printable_ratio(payload[:8192]), 4),
                f1=f1_magic(payload),
                f2=f2_printable(payload, declared_len),
                f3=f3_strict_pgp(payload),
                naive=naive_pgp(payload))

if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    CELL = os.path.abspath(os.path.join(HERE, ".."))
    rng = random.Random(44)                 # fixed seed, preregistered run
    N = 10000
    f1 = f2 = f3 = nv = 0
    for _ in range(N):
        size = int(math.exp(rng.uniform(math.log(16), math.log(85000))))
        b = rng.randbytes(size)
        a = adjudicate(b, size)
        f1 += a["f1"]; f2 += a["f2"]; f3 += a["f3"]; nv += a["naive"]
    cal = dict(n=N, seed=44, size_model="log-uniform 16..85000 bytes",
               f1_fpr=f1 / N, f2_fpr=f2 / N, f3_fpr=f3 / N, naive_fpr=nv / N,
               f3_armed=(f3 / N) < 0.005,
               prereg_rule="F3 armed iff FPR < 0.5% on 10k random blobs; naive never flags")
    json.dump(cal, open(os.path.join(CELL, "results", "calibration.json"), "w"), indent=1)
    print(json.dumps(cal, indent=1))
