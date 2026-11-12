"""R44 / W2-A1 step 4 — enumerative structural table (PREREG §5) -> structural.json.

The 30-bit dot stream vs the pre-registered constant list; base groupings; zero positions;
numerals; gematria-prime sums.  Everything RECORDED, nothing certified; any exact
constant match is reported loudly (match flags collected in `matches`).
"""
import json

import numpy as np

import shortnull as S

BITS = "111111111111111111111001110111"
CONSTS = [3301, 1033, 761, 509, 311, 29, 3299, 1595277641]


def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def factor(n):
    f, d = [], 2
    while d * d <= n:
        while n % d == 0:
            f.append(d)
            n //= d
        d += 1
    if n > 1:
        f.append(n)
    return f


def runlen(s):
    out, cur, k = [], s[0], 0
    for ch in s:
        if ch == cur:
            k += 1
        else:
            out.append((cur, k))
            cur, k = ch, 1
    out.append((cur, k))
    return out


matches = []
out = {"bits_13_as_1": BITS, "constants_prereg": CONSTS, "variants": {}}

variants = {"fwd": BITS, "rev": BITS[::-1],
            "comp": "".join("1" if b == "0" else "0" for b in BITS)}
variants["revcomp"] = variants["comp"][::-1]
const_bins = {k: bin(k)[2:] for k in CONSTS}

for name, s in variants.items():
    v = int(s, 2)
    rec = {"bits": s, "decimal": v, "is_prime": is_prime(v),
           "factors": factor(v) if v > 1 else [v],
           "mod29": v % 29, "mod29_translit": S.gp.indices_to_translit([v % 29])}
    # exact equality vs constants (decimal), containment of constant binaries
    for k, kb in const_bins.items():
        if v == k:
            matches.append({"variant": name, "match": "decimal == %d" % k})
        if kb in s:
            matches.append({"variant": name, "match": "binary of %d contained" % k,
                            "at": s.index(kb)})
    # groupings
    g = {}
    for w in (2, 3, 5, 6, 10, 15):
        vals = [int(s[i:i + w], 2) for i in range(0, 30, w)]
        g["%d-bit" % w] = vals
        if w == 5:
            g["5-bit_baconian"] = ["".join(chr(65 + x)) if x < 26 else "?" for x in vals]
    rec["groupings"] = g
    rec["runlengths"] = runlen(s)
    out["variants"][name] = rec

out["zero_positions_1based"] = [i + 1 for i, b in enumerate(BITS) if b == "0"]
out["ten_dot_images"] = [36, 38, 49]
out["counts"] = {"ones": BITS.count("1"), "zeros": BITS.count("0"),
                 "dot_sum": 27 * 13 + 3 * 10, "dot_sum_mod29": (27 * 13 + 3 * 10) % 29,
                 "dot_sum_mod29_translit": S.gp.indices_to_translit([(27 * 13 + 3 * 10) % 29])}
out["ascii"] = "UNBUILDABLE: 30 bits not divisible by 8; 0-padded-to-32 fwd bytes: " + \
    str([int(("00" + BITS)[i:i + 8], 2) for i in range(0, 32, 8)])
out["dot_values_as_mod29_translit"] = "13->P, 10->I: " + \
    "".join("P" if b == "1" else "I" for b in BITS)

# numerals
num = {"margin": [1, 2, 3, 4, 5], "grid_red": 3299}
num["margin_mod29_translit"] = S.gp.indices_to_translit([1, 2, 3, 4, 5])
num["grid_mod29"] = 3299 % 29
num["grid_mod29_translit"] = S.gp.indices_to_translit([3299 % 29])
num["notes"] = ["3301-3299 = 2", "3299 is prime: %s" % is_prime(3299),
                "margin numerals label the five numbered list items (P1 census note)"]
out["numerals"] = num

# gematria prime sums
c = S.canon()
dc = c[np.asarray([d["pos"] for d in json.load(
    open("../P1-red-ink/channel.json"))["full"]["dropcaps"]])]
PR = S.gp.PRIMES


def gsum(x):
    v = int(sum(PR[i] for i in x))
    return {"sum": v, "is_prime": is_prime(v), "mod29": v % 29,
            "rel3301": "3301-%d=%d" % (v, 3301 - v)}


out["gematria_prime_sums"] = {
    "dropcaps13": gsum(dc), "title9": gsum(c[3603:3612]), "urpn4": gsum(c[12644:12648]),
    "all26": gsum(np.concatenate([dc, c[3603:3612], c[12644:12648]]))}

out["matches"] = matches
json.dump(out, open("structural.json", "w"), indent=1)
print("matches:", matches if matches else "NONE")
for n, r in out["variants"].items():
    print(n, r["decimal"], "prime" if r["is_prime"] else r["factors"])
print("sums:", out["gematria_prime_sums"])
print("zero positions:", out["zero_positions_1based"])
