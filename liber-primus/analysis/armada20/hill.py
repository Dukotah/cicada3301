"""Hill cipher attack over 29-rune alphabet (mod 29). id=16."""
import sys, itertools, time
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import runes_to_indices, indices_to_translit
from lp.score import default

MOD = 29
q = default()

def egcd(a, b):
    if b == 0: return (a, 1, 0)
    g, x, y = egcd(b, a % b)
    return (g, y, x - (a // b) * y)

def modinv(a, m=MOD):
    a %= m
    g, x, _ = egcd(a, m)
    if g != 1: return None
    return x % m

def det2(m):  # m = [a,b,c,d]
    return (m[0]*m[3] - m[1]*m[2]) % MOD

def inv2(m):
    d = det2(m)
    di = modinv(d)
    if di is None: return None
    return [(m[3]*di) % MOD, (-m[1]*di) % MOD,
            (-m[2]*di) % MOD, (m[0]*di) % MOD]

def hill_decrypt2(idx, kinv):
    # apply kinv to ciphertext blocks of 2 -> plaintext
    out = []
    a, b, c, d = kinv
    n = len(idx) - (len(idx) % 2)
    for i in range(0, n, 2):
        x, y = idx[i], idx[i+1]
        out.append((a*x + b*y) % MOD)
        out.append((c*x + d*y) % MOD)
    return out

def load_pages():
    t = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt').read()
    return [runes_to_indices(p) for p in t.split('%')]

def score_idx(idx):
    return q.score_norm(indices_to_translit(idx))

CRIBS = ["THE", "AND", "THAT", "WITHIN", "DIVINITY", "CIRCUMFERENCE",
         "WELCOME", "PILGRIM", "WISDOM", "INSTAR", "PRIMES", "SACRED"]

def crib_count(tr):
    return sum(tr.count(c) for c in CRIBS)

if __name__ == "__main__":
    pages = load_pages()
    # concatenate a few pages for a robust score, but also test per-page
    # Use page 0 alone as primary target (262 runes).
    target = pages[0]
    print("target len", len(target))

    t0 = time.time()
    best = []  # (score, matrix-as-key, kinv)
    # Enumerate all invertible 2x2 KEY matrices. We treat the searched matrix as
    # the DECRYPTION matrix directly (so we apply it to ciphertext). That covers
    # the whole invertible group regardless of enc/dec convention.
    count = 0
    for a in range(MOD):
        for b in range(MOD):
            for c in range(MOD):
                for d in range(MOD):
                    m = (a, b, c, d)
                    det = (a*d - b*c) % MOD
                    if det == 0: continue
                    count += 1
                    dec = hill_decrypt2(target, list(m))
                    s = score_idx(dec)
                    if len(best) < 30 or s > best[-1][0]:
                        best.append((s, m))
                        best.sort(key=lambda x: -x[0])
                        best = best[:30]
    print("invertible matrices tested:", count, "time", round(time.time()-t0,1))
    print("=== TOP 2x2 (decryption matrices applied to page 0) ===")
    for s, m in best[:15]:
        dec = hill_decrypt2(target, list(m))
        tr = indices_to_translit(dec)
        print(f"{s:7.3f} crib={crib_count(tr):2d} mat={m} {tr[:50]}")
