"""Campaign VII — word-gematria-sum self-keying ("their numbers are the direction").

The GPG-verified 2016 Cicada message: "Liber Primus is the way. Its words are the
map, their meaning is the road, and THEIR NUMBERS ARE THE DIRECTION." Combined
with A WARNING ("either the words or their numbers, for all is sacred") and the
SOME WISDOM square (words' gematria sums literally complete a magic square), the
most direct operational reading is: each word's gematria-prime-sum drives the
decryption of what follows. Word-granular self-keying was never tested (prior
autokey was rune-granular index autokey; prior word-boundary tests were
positional stats, not keying).

Variants (word w_j's runes all shifted by k_j, mod 29):
  W1 cipher-fed  : k_j = primesum(ciphertext word j-1); k_0 = 0
  W2 plain-fed   : k_j = primesum(DECRYPTED word j-1) (progressive autokey)
  W3 cumulative  : k_j = primesum(ciphertext words 0..j-1)
  W4 phi-of-sum  : k_j = phi(primesum(ciphertext word j-1)) mod 29
  W5 rune-prime autokey: k(rune i) = prime(C_{i-1}) mod 29 (per-rune control)
Each with sign +/- and +/- atbash, per page (word boundaries from the raw
transcription's '-' separators). score_norm > -5.0 = break.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, score as _score  # noqa

N = gp.N
SC = _score.default()
BREAK = -5.0
KRIS = os.path.join(HERE, "..", "..", "data", "krisyotam_runes.txt")


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


def word_pages():
    """Pages as lists of words; each word = list of rune indices."""
    txt = open(KRIS, encoding="utf-8").read()
    pages = []
    for seg in txt.split("%"):
        words, cur = [], []
        for c in seg:
            if gp.is_rune(c):
                cur.append(gp.RUNE_TO_IDX[c])
            elif cur:
                words.append(cur)
                cur = []
        if cur:
            words.append(cur)
        if words:
            pages.append(words)
    return pages


def primesum(word):
    return sum(gp.PRIMES[i] for i in word)


def decrypt_variant(words, variant, sign, atb):
    def tf(c):
        return (N - 1 - c) if atb else c
    plain = []
    if variant == "W5":  # per-rune prime autokey
        flat = [i for w in words for i in w]
        prev = 0
        for c in flat:
            plain.append((tf(c) + sign * (gp.PRIMES[prev] % N)) % N)
            prev = c
        return plain
    k, cum = 0, 0
    for j, w in enumerate(words):
        dec = [(tf(c) + sign * k) % N for c in w]
        plain.extend(dec)
        if variant == "W1":
            k = primesum(w) % N
        elif variant == "W2":
            k = primesum(dec) % N
        elif variant == "W3":
            cum += primesum(w)
            k = cum % N
        elif variant == "W4":
            k = _totient(primesum(w)) % N
    return plain


def run():
    pages = word_pages()
    unsolved = pages[:-2]
    best = {"score": -99.0, "rec": None}
    per_variant = {}
    for variant in ("W1", "W2", "W3", "W4", "W5"):
        for sign in (-1, +1):
            for atb in (False, True):
                for pi, words in enumerate(unsolved):
                    plain = decrypt_variant(words, variant, sign, atb)
                    s = SC.score_norm(gp.indices_to_translit(plain))
                    if s > per_variant.get(variant, -99):
                        per_variant[variant] = round(s, 3)
                    if s > best["score"]:
                        best.update(score=s, rec={
                            "variant": variant, "sign": sign, "atbash": atb,
                            "page": pi,
                            "text": gp.indices_to_translit(plain)[:70]})
    out = {"campaign": "VII", "track": "wordsum-selfkey (hint-derived)",
           "hint": "2016 verified: 'their numbers are the direction'",
           "break_threshold": BREAK, "best_score": round(best["score"], 3),
           "best": best["rec"], "per_variant_best": per_variant}
    json.dump(out, open(os.path.join(HERE, "wordsum_selfkey_results.json"), "w"),
              indent=2)
    print("Word-gematria-sum self-keying ('numbers are the direction'):")
    for v, s in sorted(per_variant.items(), key=lambda x: -x[1]):
        print(f"  {v}  best {s}")
    r = best["rec"]
    print(f"  best: {r['variant']} sign{r['sign']:+d} atb{int(r['atbash'])} "
          f"p{r['page']}\n    {r['text']}")
    print("  BREAK!" if best["score"] > BREAK
          else "  null — word-sum self-keying is not the mechanism")
    return out


if __name__ == "__main__":
    run()
