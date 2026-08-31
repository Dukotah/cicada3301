#!/usr/bin/env python3
"""Round 26 Lane C -- build the deduplicated corpus-SEMANTIC candidate SEED set.

Every prime / prime-index / totient / date (unix + calendar) / coordinate / notable Cicada
integer in the corpus, PLUS gematria sums of solved LP1/LP2 plaintext words and koan/hint phrases.
Each entry is a (value, kind, label) triple; value is what gets fed AS A SEED (int OR the raw
phrase string) through the generator zoo. Deduplicated on (kind_class, value).

Run: python3 build_seeds.py            # prints the set size + writes seeds.json
"""
import os, sys, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp   # noqa

N = gp.N


def _sieve(count):
    primes, cand = [], 2
    while len(primes) < count:
        if all(cand % p for p in primes if p * p <= cand):
            primes.append(cand)
        cand += 1
    return primes


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


def gematria_sum(phrase):
    """Sum of gematria-primus VALUES of the runes a phrase maps to (Latin -> rune -> value).
    Uses the repo's own gematria table so it matches the corpus arithmetic."""
    idxs = gp.keyword_to_indices(phrase)
    # gematria PRIMUS values: rune index -> its prime value
    return sum(gp.PRIMES[i] for i in idxs)


def build():
    seeds = []          # list of {value, kind, label, is_str}
    seen = set()

    def add(value, kind, label, is_str=False):
        key = (kind if is_str else "int", value if is_str else int(value))
        if key in seen:
            return
        seen.add(key)
        seeds.append({"value": value, "kind": kind, "label": label, "is_str": is_str})

    # ---- notable Cicada integers -----------------------------------------
    notable = {
        3301: "the number", 509: "prime 509", 503: "prime 503",
        761: "koan prime", 3117: "onion-derived", 1033: "telnet prime",
        1595: "prime", 1959: "prime",
        # 7A35090F fingerprint fragments (hex nibble reads)
        0x7A35090F: "fp-7A35090F full", 0x7A35: "fp hi16", 0x090F: "fp lo16",
        0x7A: "fp b0", 0x35: "fp b1", 0x09: "fp b2", 0x0F: "fp b3",
        2049: "2^11+1", 1033: "telnet", 29: "N alphabet", 3: "trigram",
        # 2012 P.S. digit string (public Cicada 2012 puzzle final)
        1033197561: "2012 P.S. digits", 2012: "year 2012",
    }
    for v, lbl in notable.items():
        add(v, "notable", lbl)

    # ---- dates: unix + calendar (Cicada canonical dates) ------------------
    dates = {
        (2012, 1, 4): "2012 start", (2013, 1, 4): "2013 start",
        (2014, 1, 5): "2014 start", (2012, 1, 5): "2012 puzzle",
        (2013, 1, 6): "2013 alt", (2014, 1, 6): "2014 alt",
    }
    for (y, mo, dd), lbl in dates.items():
        try:
            u = int(datetime.datetime(y, mo, dd, tzinfo=datetime.timezone.utc).timestamp())
            add(u, "date_unix", f"{lbl} unix")
        except Exception:
            pass
        add(y * 10000 + mo * 100 + dd, "date_cal", f"{lbl} yyyymmdd")

    # ---- coordinates (notable Cicada-referenced) -------------------------
    for c, lbl in [(37, "lat37"), (122, "lon122"), (37122, "coord37122")]:
        add(c, "coord", lbl)

    # ---- primes + prime-index + totient ladders --------------------------
    primes = _sieve(200)
    for i, p in enumerate(primes[:100]):
        add(p, "prime", f"p_{i}")
        add(i + 1, "prime_index", f"pi_{i}")
        add(_totient(p), "totient_of_prime", f"tot_p_{i}")   # = p-1
    for n in range(2, 60):
        add(_totient(n), "totient", f"tot_{n}")

    # ---- page-56 hash nibbles (the 05.jpg / totient page anchor value) ---
    # canonical solved-page anchor ints already covered by notable+ladders.
    # canon_256 as int: the 256-value gematria alphabet sum
    add(sum(gp.PRIMES), "canon256_sum", "sum of gematria prime VALUES")
    add(len(gp.PRIMES), "alphabet_len", "alphabet length")

    # ---- gematria of solved plaintext WORDS + koan/hint phrases ----------
    phrases = [
        "THE PRIMES ARE SACRED", "THE TOTIENT FUNCTION IS SACRED",
        "A KOAN", "KNOW THIS", "AN INSTAR EMERGENCE", "THE INSTAR EMERGENCE",
        "WELCOME PILGRIM", "THE JOURNEY", "DIVINITY", "CIRCUMFERENCE",
        "THE LOSS OF DIVINITY", "SOME WISDOM", "FIND THE TRUTH",
        "WITHIN THE DEEP WEB", "THE SACRED GEOMETRY", "EMERGENCE",
        "TRUTH", "WISDOM", "PILGRIM", "SACRED", "TOTIENT", "PRIMES",
        "PARABLE", "MOBIUS", "CICADA", "LIBER PRIMUS", "THREE THREE ZERO ONE",
        "SHADOWS", "INSTAR", "PRESERVATION", "ADHERENCE",
    ]
    for ph in phrases:
        add(gematria_sum(ph), "gematria_sum", f"gem[{ph}]")
        # ALSO keep the phrase itself as a STRING seed (Py2 str-hash path)
        add(ph, "phrase_str", ph, is_str=True)

    return seeds


def main():
    seeds = build()
    ints = sum(1 for s in seeds if not s["is_str"])
    strs = sum(1 for s in seeds if s["is_str"])
    out = {"n_total": len(seeds), "n_int": ints, "n_str": strs, "seeds": seeds}
    with open(os.path.join(HERE, "seeds.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"seed set: {len(seeds)} total  ({ints} int, {strs} str)")
    kinds = {}
    for s in seeds:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    for k, v in sorted(kinds.items()):
        print(f"  {k:20s} {v}")


if __name__ == "__main__":
    main()
