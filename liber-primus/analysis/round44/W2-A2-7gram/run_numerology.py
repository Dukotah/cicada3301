"""R44/W2-A2 part 2 — fixed positional-numerology predicate table (PREREG section 5).
Measured-only.  Writes numerology.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

S = {  # site-derived numbers, exactly the PREREG section 5 list
    "pageA_0b": 27, "pageB_0b": 54, "pageA_1b": 28, "pageB_1b": 55,
    "posA": 28, "posB": 70, "globalA": 6555, "globalB": 12950, "p55_global": 12956,
    "lenA": 234, "lenB": 76, "len55": 85,
    "dpos": 42, "dpage": 27, "dglobal": 6395, "dglobal_p55": 6401,
    "idxsum": 105, "gpsum": 389,
    "sumglobals": 6555 + 12950, "doubling_residual": 12950 - 2 * 6555,
}
C = [1, 2, 3, 29, 58, 311, 509, 761, 1033, 3299, 3301, 1595277641]


def is_prime(n):
    n = abs(int(n))
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def main():
    matches = []
    names = list(S)
    for a in names:
        x = S[a]
        for c in C:
            if x == c:
                matches.append(f"{a} == {c}")
            if c != 0 and x % c == 0 and abs(x) > c > 1:
                matches.append(f"{a} ({x}) divisible by {c}")
            if x != 0 and c % x == 0 and c > abs(x) > 1:
                matches.append(f"{c} divisible by {a} ({x})")
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if S[a] + S[b] in C:
                matches.append(f"{a}+{b} = {S[a] + S[b]} in constants")
            if abs(S[a] - S[b]) in C:
                matches.append(f"|{a}-{b}| = {abs(S[a] - S[b])} in constants")
            if S[a] * S[b] in C:
                matches.append(f"{a}*{b} = {S[a] * S[b]} in constants")
    mods = {a: {"mod29": S[a] % 29, "mod3301": S[a] % 3301} for a in names}
    primes = {a: is_prime(S[a]) for a in names}
    out = dict(S=S, constants=C, matches=matches, mods=mods,
               primality={a: bool(v) for a, v in primes.items()},
               prime_members=[a for a, v in primes.items() if v])
    json.dump(out, open(os.path.join(HERE, "numerology.json"), "w"), indent=1)
    print(json.dumps(dict(matches=matches, prime_members=out["prime_members"],
                          mod29={a: mods[a]["mod29"] for a in names}), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
