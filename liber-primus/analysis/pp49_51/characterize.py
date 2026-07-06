"""Phase 2: what KIND of object is the 2048-bit pp49-51 payload?
Structural tests, no external deps. 'The primes are sacred' -> primality is the money test."""
import os

HERE = os.path.dirname(__file__)
data = open(os.path.join(HERE, "canon_256.bin"), "rb").read()
assert len(data) == 256

def miller_rabin(n, witnesses=(2,3,5,7,11,13,17,19,23,29,31,37)):
    if n < 2: return False
    for p in witnesses:
        if n % p == 0: return n == p
    d, r = n - 1, 0
    while d % 2 == 0: d //= 2; r += 1
    for a in witnesses:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

def small_factor(n, limit=100000):
    if n % 2 == 0: return 2
    f = 3
    while f < limit:
        if n % f == 0: return f
        f += 2
    return None

def report(label, n):
    print(f"\n[{label}]  {n.bit_length()}-bit")
    sf = small_factor(n)
    print(f"  smallest factor < 1e5: {sf}")
    print(f"  Miller-Rabin probable prime: {miller_rabin(n)}")

be = int.from_bytes(data, "big")
le = int.from_bytes(data, "little")
rev = int.from_bytes(data[::-1], "big")
print("=== full 2048-bit integer interpretations ===")
report("big-endian", be)
report("little-endian", le)
report("reversed-bytes", rev)

print("\n=== two 1024-bit halves (RSA p,q style?) ===")
for name, half in [("high-1024", data[:128]), ("low-1024", data[128:])]:
    report(name, int.from_bytes(half, "big"))

print("\n=== structural sanity ===")
print(f"  LSB (odd?): {be & 1}  MSB byte: {data[0]:#04x}  last byte: {data[-1]:#04x}")

# gcd against known Cicada / 3301 constants (none are true 2048-bit RSA moduli publicly,
# but test the obvious: 3301, and the page-56 512-bit hash if present)
import math
print(f"  is big-endian a perfect square: {math.isqrt(be)**2 == be}")
for k in (3301, 1595277641, 0xFFFF):  # 3301, the 2013 pubkey id fragment, sanity
    g = math.gcd(be, k)
    if g > 1: print(f"  gcd(be, {k}) = {g}  <-- shares factor!")

print("\n=== ASCII / text probes ===")
for name, b in [("forward", data), ("reversed", data[::-1])]:
    printable = sum(1 for x in b if 32 <= x < 127)
    runs = 0; best = 0; cur = 0
    for x in b:
        if 32 <= x < 127: cur += 1; best = max(best, cur)
        else: cur = 0
    print(f"  {name}: {printable}/256 printable, longest printable run = {best}")
print("  (a real ASCII message would be ~95%+ printable with long runs; 40% = binary)")

print("\n=== byte-value distribution ===")
import collections
h = collections.Counter(data)
print(f"  distinct: {len(h)}/256   most common: {h.most_common(3)}")
print(f"  bytes never appearing: {256 - len(h)}")
