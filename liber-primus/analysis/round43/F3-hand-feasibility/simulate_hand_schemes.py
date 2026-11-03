"""R43 F3b — simulate hand-executable cipher families at 13k-glyph scale and
measure the six LP-comparable statistics (IoC, doublet%, lag2%, max periodic
IoC 2..60, difference-stream IoC, bigram IoC).

Plaintext: KJV English transliterated into Gematria Primus indices (29-symbol),
13,100 glyphs — same scale as the unsolved section (13,041 runes excl. Parable).

Run from liber-primus/:  PYTHONUTF8=1 python analysis/round43/F3-hand-feasibility/simulate_hand_schemes.py
"""
import sys, os, collections, random, re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from lp import gematria as gp

random.seed(43)
N = 29

raw = open(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "kjv.txt"),
           encoding="utf-8", errors="ignore").read()
words = re.findall(r"[A-Za-z]+", raw.upper())
wr = []
for w in words[5000:]:
    try:
        wr.append(gp.keyword_to_indices(w))
    except ValueError:
        pass
pt = [i for w in wr for i in w][:13100]
keytext = []
for w in words[300000:320000]:
    try:
        keytext += gp.keyword_to_indices(w)
    except ValueError:
        pass
keytext = keytext[:13100]
assert len(keytext) == 13100, len(keytext)


def ioc(seq, n_=N):
    n = len(seq)
    c = collections.Counter(seq)
    return n_ * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def metrics(ct):
    n = len(ct)
    dbl = 100 * sum(1 for i in range(n - 1) if ct[i] == ct[i + 1]) / (n - 1)
    lag2 = 100 * sum(1 for i in range(n - 2) if ct[i] == ct[i + 2]) / (n - 2)
    best = 0
    bp = 0
    for per in range(2, 61):
        cols = [[] for _ in range(per)]
        for i, v in enumerate(ct):
            cols[i % per].append(v)
        a = sum(ioc(c) for c in cols) / per
        if a > best:
            best, bp = a, per
    D = [(ct[i + 1] - ct[i]) % N for i in range(n - 1)]
    prs = [(ct[i], ct[i + 1]) for i in range(n - 1)]
    cp = collections.Counter(prs)
    np_ = len(prs)
    big = 841 * sum(v * (v - 1) for v in cp.values()) / (np_ * (np_ - 1))
    return ioc(ct), dbl, lag2, best, bp, ioc(D), big


def primes_list(k):
    out, x = [], 2
    while len(out) < k:
        if all(x % q for q in range(2, int(x ** .5) + 1)):
            out.append(x)
        x += 1
    return out


PR = primes_list(14000)


def phi(n):
    r = x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            r -= r // p
        p += 1
    if x > 1:
        r -= r // x
    return r


S = {}
n = len(pt)

S['direct/mono/pure transposition'] = sorted(pt, key=lambda _: random.random())

k7 = gp.keyword_to_indices("DIUINITY")[:7]
S['vigenere key7'] = [(pt[i] + k7[i % 7]) % N for i in range(n)]

k13 = gp.keyword_to_indices("FIRFUMFERENFE")
ct, j = [], 0
for p in pt:
    if p == 0 and random.random() < 0.7:
        ct.append(0)
        continue
    ct.append((p - k13[j % len(k13)]) % N)
    j += 1
S['vig key13 + F-interrupters'] = ct

S['running key (English book)'] = [(pt[i] + keytext[i]) % N for i in range(n)]

S['autokey plaintext primer7'] = [(pt[i] + (k7[i] if i < 7 else pt[i - 7])) % N for i in range(n)]

ct = []
for i, p in enumerate(pt):
    ct.append((p + (k7[i] if i < 7 else ct[i - 7])) % N)
S['autokey ciphertext primer7'] = ct

ct, prev = [], 5
for p in pt:
    prev = (p + prev) % N
    ct.append(prev)
S['running-sum (ct-autokey lag1)'] = ct

ct, prev = [], 5
for p in pt:
    prev = (p + prev + 1) % N
    ct.append(prev)
S['running-sum +1'] = ct

S['trithemius step+1'] = [(pt[i] + i) % N for i in range(n)]
S['progressive keyword (7,+1/cyc)'] = [(pt[i] + k7[i % 7] + i // 7) % N for i in range(n)]

pidig = [int(c) for c in "14159265358979323846" * 700][:n]
S['gronsfeld pi-digits 0-9'] = [(pt[i] + pidig[i]) % N for i in range(n)]

S['phi(prime) stream (AN-END ext.)'] = [(pt[i] - ((PR[i] - 1) % N)) % N for i in range(n)]
S['totient phi(n) stream'] = [(pt[i] + phi(i + 2) % N) % N for i in range(n)]

seed = gp.keyword_to_indices("CICADA")[:5]
ks = list(seed)
while len(ks) < n:
    ks.append((ks[-1] + ks[-5]) % N)
S['chain-addition w5 (VIC-style)'] = [(pt[i] + ks[i]) % N for i in range(n)]

fib = [1, 1]
while len(fib) < n:
    fib.append((fib[-1] + fib[-2]) % N)
S['fibonacci mod29'] = [(pt[i] + fib[i]) % N for i in range(n)]

otk = [random.randrange(N) for _ in range(n)]
S['OTP uniform (dice/deck pad)'] = [(pt[i] + otk[i]) % N for i in range(n)]

hk, prev = [], -1
for _ in range(n):
    x = random.randrange(N)
    while x == prev:
        x = random.randrange(N)
    hk.append(x)
    prev = x
S['OTP human pad (pad avoids rpts)'] = [(pt[i] + hk[i]) % N for i in range(n)]

# bifid 6x6 (29 runes + 7 fillers), period 7
grid = list(range(N)) + [random.randrange(N) for _ in range(7)]
random.shuffle(grid)
pos = {}
for i, v in enumerate(grid):
    pos.setdefault(v, (i // 6, i % 6))
cell = {(i // 6, i % 6): v for i, v in enumerate(grid)}
ct = []
for b in range(0, n - 7, 7):
    blk = pt[b:b + 7]
    rows = [pos[x][0] for x in blk]
    colz = [pos[x][1] for x in blk]
    seq = rows + colz
    for j in range(7):
        ct.append(cell[(seq[2 * j], seq[2 * j + 1])] % N)
S['bifid 6x6 period7'] = ct

ct = []
for i in range(0, n - 1, 2):
    a, b = pt[i], pt[i + 1]
    ct += [(3 * a + 5 * b) % N, (1 * a + 2 * b) % N]
S['hill 2x2'] = ct

pairsyms = [(a, b) for a in range(N) for b in range(N) if a != b]
random.shuffle(pairsyms)
allpairs = [(a, b) for a in range(N) for b in range(N)]
random.shuffle(allpairs)
tbl = {ab: pairsyms[i % len(pairsyms)] for i, ab in enumerate(allpairs)}
ct = []
for i in range(0, n - 1, 2):
    ct += list(tbl[(pt[i], pt[i + 1])])
S['digraphic table (no XX out)'] = ct

L = list(range(N))
R = list(range(N))
random.shuffle(L)
random.shuffle(R)
ct = []
for p in pt:
    i = R.index(p)
    c = L[i]
    ct.append(c)
    zi = L.index(c)
    L = L[zi:] + L[:zi]
    x = L.pop(1)
    L.insert(14, x)
    zi = R.index(p)
    R = R[zi:] + R[:zi]
    R = R[1:] + R[:1]
    x = R.pop(2)
    R.insert(14, x)
S['chaocipher-29'] = ct

pad = [random.randrange(N) for _ in range(3 * n)]
ct, prev, j = [], -1, 0
for p in pt:
    c = (p + pad[j]) % N
    j += 1
    while c == prev:
        c = (p + pad[j]) % N
        j += 1
    ct.append(c)
    prev = c
S['OTP + strict skip-on-collision'] = ct

ct, prev, j = [], -1, 0
for p in pt:
    c = (p + pad[j]) % N
    j += 1
    while c == prev and random.random() < 0.80:
        c = (p + pad[j]) % N
        j += 1
    ct.append(c)
    prev = c
S['OTP + no-repeat (80% compl.)'] = ct

ct, prev, j = [], -1, 0
for p in pt:
    c = (p - ((PR[j] - 1) % N)) % N
    j += 1
    while c == prev and random.random() < 0.80:
        c = (p - ((PR[j] - 1) % N)) % N
        j += 1
    ct.append(c)
    prev = c
S['phi(prime) + no-repeat (80%)'] = ct

ct, cnt = [], 0
for w in wr:
    if cnt >= n:
        break
    s = random.randrange(N)
    for x in w:
        ct.append((x + s) % N)
    cnt += len(w)
S['per-word random shift (Alberti)'] = ct[:n]

print(f"{'scheme':34s} {'IoC':>6s} {'dbl%':>6s} {'lag2%':>6s} {'maxPer':>7s} {'@p':>3s} {'D-IoC':>6s} {'bigIoC':>7s}")
print(f"{'LP TARGET (56 pages)':34s} {'1.000':>6s} {'0.678':>6s} {'3.440':>6s} {'1.0110':>7s} {'':>3s} {'1.024':>6s} {'1.0253':>7s}")
print('-' * 86)
for name, ctxt in S.items():
    io, db, l2, mp, bp, dio, bg = metrics(ctxt)
    print(f"{name:34s} {io:6.3f} {db:6.3f} {l2:6.3f} {mp:7.4f} {bp:3d} {dio:6.3f} {bg:7.4f}")
