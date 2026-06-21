"""Task 5 (armada id5): Primes/totients as transposition OR interrupter schedule.

(a) Prime sequence -> columnar transposition order applied per page,
    THEN short-keyword Vigenere / monoalphabetic decode, quadgram-scored.
(b) Prime positions and totient(n) positions as an INTERRUPTER SCHEDULE
    (those positions are nulls / do not advance the key) layered over a keyword.

Scored with the rig's quadgram scorer. Baseline to beat: -6.23.
"""
import sys, json
sys.path.insert(0, "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src")
sys.path.insert(0, "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis")
from lp import gematria as gp
from lp import score as _score
from run_stats import load_pages

N = gp.N
SC = _score.default()
PAGES = load_pages()
UNSOLVED = PAGES[:-2]

KEYWORDS = ["DIVINITY", "PRIMES", "CIRCUMFERENCE", "FIRFUMFERENFE",
            "CICADA", "WELCOME", "PILGRIM", "MOBIUS", "INSTAR",
            "TOTIENT", "SACRED", "WISDOM", "ADHERE", "KOAN",
            "TRUTH", "AETHEREAL", "EMERGENCE", "SHADOWS", "PARABLE", "ENLIGHTEN"]

def primes_upto_count(k):
    out, n = [], 2
    while len(out) < k:
        isp = True
        for p in out:
            if p * p > n: break
            if n % p == 0: isp = False; break
        if isp: out.append(n)
        n += 1
    return out

def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

def totient(n):
    if n == 0: return 0
    result, nn, p = n, n, 2
    while p * p <= nn:
        if nn % p == 0:
            while nn % p == 0: nn //= p
            result -= result // p
        p += 1
    if nn > 1: result -= result // nn
    return result

def columnar_order_from_primes(ncols):
    primes = primes_upto_count(ncols)
    keys = [p % ncols for p in primes]
    return sorted(range(ncols), key=lambda c: (keys[c], c))

def columnar_transpose(idxs, ncols, col_order):
    out, n = [], len(idxs)
    for c in col_order:
        j = c
        while j < n:
            out.append(idxs[j]); j += ncols
    return out

def vig_decode(idxs, keyidx, sign):
    L = len(keyidx)
    return [(c + sign * keyidx[i % L]) % N for i, c in enumerate(idxs)]

def mono_decode(idxs, shift, sign):
    return [(c + sign * shift) % N for c in idxs]

def run_part_a():
    best = {"score": -999}; results = []
    kw_idx = {w: gp.keyword_to_indices(w) for w in KEYWORDS}
    for pi, page in enumerate(UNSOLVED):
        for ncols in range(2, 14):
            order = columnar_order_from_primes(ncols)
            trans = columnar_transpose(page, ncols, order)
            for atbash in (False, True):
                base = [(N - 1 - c) if atbash else c for c in trans]
                for w in KEYWORDS:
                    for sign in (-1, 1):
                        dec = vig_decode(base, kw_idx[w], sign)
                        s = SC.score_norm(gp.indices_to_translit(dec))
                        rec = {"part": "a", "page": pi, "ncols": ncols, "key": w,
                               "sign": sign, "atb": atbash, "score": round(s, 4)}
                        if s > best["score"]:
                            best = dict(rec, plaintext=gp.indices_to_translit(dec)[:100])
                        results.append(rec)
                for shift in range(N):
                    for sign in (-1, 1):
                        dec = mono_decode(base, shift, sign)
                        s = SC.score_norm(gp.indices_to_translit(dec))
                        rec = {"part": "a", "page": pi, "ncols": ncols,
                               "key": f"mono{shift}", "sign": sign, "atb": atbash,
                               "score": round(s, 4)}
                        if s > best["score"]:
                            best = dict(rec, plaintext=gp.indices_to_translit(dec)[:100])
                        results.append(rec)
    return best, results

def decode_with_nulls(idxs, keyidx, sign, nulls, atbash):
    out, j, L = [], 0, len(keyidx)
    for pos, c in enumerate(idxs):
        if pos in nulls: continue
        cc = (N - 1 - c) if atbash else c
        out.append((cc + sign * keyidx[j % L]) % N); j += 1
    return out

def run_part_b():
    best = {"score": -999}; results = []
    kw_idx = {w: gp.keyword_to_indices(w) for w in KEYWORDS}
    for pi, page in enumerate(UNSOLVED):
        n = len(page)
        prime1 = {p for p in range(n) if is_prime(p + 1)}
        prime0 = {p for p in range(n) if is_prime(p)}
        totvals = set(t for k in range(1, n + 1) for t in [totient(k)] if 0 <= t < n)
        totprime = {p for p in range(n) if is_prime(totient(p + 1))}
        scheds = {"prime1idx": prime1, "prime0idx": prime0,
                  "totientvals": totvals, "totientprime": totprime, "none": set()}
        for sname, nulls in scheds.items():
            for atbash in (False, True):
                for w in KEYWORDS:
                    for sign in (-1, 1):
                        dec = decode_with_nulls(page, kw_idx[w], sign, nulls, atbash)
                        if len(dec) < 8: continue
                        s = SC.score_norm(gp.indices_to_translit(dec))
                        rec = {"part": "b", "page": pi, "sched": sname, "key": w,
                               "sign": sign, "atb": atbash, "score": round(s, 4)}
                        if s > best["score"]:
                            best = dict(rec, plaintext=gp.indices_to_translit(dec)[:100])
                        results.append(rec)
    return best, results

if __name__ == "__main__":
    ba, ra = run_part_a()
    ra.sort(key=lambda r: -r["score"])
    bb, rb = run_part_b()
    rb.sort(key=lambda r: -r["score"])
    print("PART A best:", json.dumps(ba))
    print("PART A top5:")
    for r in ra[:5]: print("  ", json.dumps(r))
    print("PART B best:", json.dumps(bb))
    print("PART B top5:")
    for r in rb[:5]: print("  ", json.dumps(r))
    out = {"part_a_best": ba, "part_b_best": bb,
           "part_a_top": ra[:10], "part_b_top": rb[:10]}
    json.dump(out, open("/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada20/task5_armada_results.json", "w"), indent=2)
    print("baseline=-6.23 OVERALL_BEST=", round(max(ba["score"], bb["score"]), 4))
