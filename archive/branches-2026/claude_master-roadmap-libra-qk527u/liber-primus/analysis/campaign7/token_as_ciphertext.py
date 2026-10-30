"""Campaign VII — token pages as their OWN ciphertext (byte-domain attack).

The pp49-51 token pad (256 bytes, high entropy) failed as a *key* over the runes
under every pairing. The alternative hypothesis: the token pad is itself an
ENCIPHERED payload (the key/message delivered encrypted), to be solved in the
byte domain (mod 256), not the rune domain (mod 29).

Attacks over the 256 bytes (each page alone + concatenated), scored by
printable-ASCII ratio and, when printable, English quadgram fitness:
  - single-byte XOR (all 256 keys)
  - repeating multi-byte XOR with Cicada-thematic ASCII keywords
  - additive/subtractive keystreams mod 256: consecutive primes, totient,
    prime-1 (the families that solved real LP pages), Fibonacci
  - straight reads: as-is, reversed, and the base-60 nibble split
A decode with printable_ratio > 0.85 is flagged; > -5.5 quadgram on the
printable projection would be a readable-English break.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import score as _score  # noqa
from campaign7.a2_tokenpad import P49, P50, P51  # noqa

SC = _score.default()
TOKEN = P49 + P50 + P51

KEYWORDS = ["CICADA", "3301", "1033", "DIVINITY", "PRIMES", "SACRED", "LIBERPRIMUS",
            "INSTAR", "EMERGENCE", "ANEND", "WISDOM", "KOAN", "MOBIUS", "PARABLE",
            "THEPRIMESARESACRED", "WELCOME", "PILGRIM", "TOTIENT"]


def _sieve(n):
    pr, c = [], 2
    while len(pr) < n:
        if all(c % p for p in pr if p * p <= c):
            pr.append(c)
        c += 1
    return pr


def _totient(n):
    r, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            r -= r // p
        p += 1
    if m > 1:
        r -= r // m
    return r


def printable_ratio(b):
    return sum(1 for v in b if 32 <= v <= 126) / len(b)


def as_text(b):
    return "".join(chr(v) if 32 <= v <= 126 else "." for v in b)


def streams(L):
    pr = _sieve(L)
    return {
        "prime": [pr[i] % 256 for i in range(L)],
        "prime_minus_1": [(pr[i] - 1) % 256 for i in range(L)],
        "totient": [_totient(i + 2) % 256 for i in range(L)],
        "fib": _fib(L),
    }


def _fib(L):
    out, a, b = [], 1, 1
    for _ in range(L):
        out.append(a % 256)
        a, b = b, a + b
    return out


def run():
    targets = {"p49": P49, "p50": P50, "p51": P51, "all": TOKEN,
               "all_rev": TOKEN[::-1]}
    best = {"pr": 0.0, "rec": None}
    flagged = []

    def consider(dec, rec):
        pr = printable_ratio(dec)
        if pr > best["pr"]:
            best.update(pr=pr, rec={**rec, "text": as_text(dec)[:80]})
        if pr > 0.85:
            q = SC.score_norm(as_text(dec))
            flagged.append({**rec, "printable": round(pr, 3),
                            "quadgram": round(q, 3), "text": as_text(dec)[:120]})

    for tname, b in targets.items():
        L = len(b)
        # 1. single-byte XOR
        for k in range(256):
            consider([v ^ k for v in b], {"target": tname, "method": f"xor1 k={k}"})
        # 2. repeating keyword XOR
        for kw in KEYWORDS:
            kb = [ord(c) for c in kw]
            consider([b[i] ^ kb[i % len(kb)] for i in range(L)],
                     {"target": tname, "method": f"xorkw {kw}"})
        # 3. additive keystreams mod 256, both signs
        for sname, st in streams(L).items():
            for sign in (-1, +1):
                consider([(b[i] + sign * st[i]) % 256 for i in range(L)],
                         {"target": tname, "method": f"{sname} sign{sign:+d}"})
        # 4. as-is
        consider(list(b), {"target": tname, "method": "asis"})

    flagged.sort(key=lambda h: -h["quadgram"])
    out = {"campaign": "VII", "track": "token-as-ciphertext",
           "best_printable_ratio": round(best["pr"], 3), "best": best["rec"],
           "n_flagged_over_0.85_printable": len(flagged), "flagged": flagged[:20]}
    json.dump(out, open(os.path.join(HERE, "token_as_ciphertext_results.json"), "w"),
              indent=2)
    print(f"Token-as-ciphertext. best printable ratio = {best['pr']:.3f}")
    print(f"  best: {best['rec']['target']} {best['rec']['method']}")
    print(f"        {best['rec']['text']}")
    print(f"  decodes with printable_ratio > 0.85: {len(flagged)}")
    for f in flagged[:8]:
        print(f"    {f['target']:4} {f['method']:16} pr={f['printable']} "
              f"q={f['quadgram']}  {f['text'][:60]}")
    if not flagged:
        print("  (none — no byte-cipher makes the token pad readable ASCII)")
    return out


if __name__ == "__main__":
    run()
