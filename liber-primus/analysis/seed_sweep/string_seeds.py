"""Track SEED — non-integer and lore seeds.

The C sweep covers integer seeds exhaustively. This covers the seeds a human
would type rather than a clock would supply: `random.seed("3301")`,
`random.seed("DIVINITY")`, dates as YYYYMMDD, the Cicada numbers, the PGP
fingerprint, the onion addresses, the gematria primes. CPython hashes a str or
bytes seed through SHA-512 before init_by_array, so these are NOT reachable from
the integer sweep and must be enumerated separately.

Also covers `random.seed()` with the same wordlist under Python 2 semantics
(hash() of the string), and the numeric seeds of lore significance at full
precision.
"""
import os, sys, random, hashlib, itertools, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 29
ct = np.frombuffer(open(os.path.join(HERE, 'ct.bin'), 'rb').read(), np.uint8)
ng = np.fromfile(os.path.join(HERE, 'ngram.bin'), np.float32)

WORDS = """3301 cicada CICADA Cicada liber primus LIBER PRIMUS liberprimus
divinity DIVINITY instar INSTAR circumference CIRCUMFERENCE firfumferenfe
welcome WELCOME pilgrim PILGRIM sacred SACRED primes PRIMES totient TOTIENT
wisdom WISDOM koan KOAN parable PARABLE anend AN_END emergence EMERGENCE
mobius MOBIUS shadows SHADOWS aholiab AHOLIAB epiphany EPIPHANY
thepathofenlightenment enlightenment ENLIGHTENMENT truth TRUTH
questionallthings selfreliance mabinogion agrippa
7A35090F 6D854CD7933322A601C3286D181F01E57A35090F
845145127 1033 761 167 3301033 33013301
auqgnxjtsyibmxpn ky2khlqdf7qdznac gy3hoy2zizvuzvdb
cicada3301 Cicada3301 CICADA3301 liberprimus3301
""".split()

NUMS = [3301, 1033, 761, 167, 845145127, 33013301, 3301033,
        20140109, 20140110, 20140506, 20140507, 20120104, 20130105,
        2014, 2013, 2012, 42, 1729, 65537, 109, 3, 5, 7,
        1595277641, 1387498126,
        0x3301, 0x7A35090F, 0xDEADBEEF, 0xCAFEBABE]
# every date in the puzzle window as YYYYMMDD
for y in (2012, 2013, 2014):
    for m in range(1, 13):
        for dd in range(1, 32):
            NUMS.append(y * 10000 + m * 100 + dd)


def score(p):
    if len(p) < 20:
        return -99.0
    a = np.asarray(p, np.int32)
    idx = ((a[:-3]*N + a[1:-2])*N + a[2:-1])*N + a[3:]
    return float(ng[idx].mean())


def decode(keys, dirn):
    """decode with interrupter branching over the first F decisions"""
    best = -99.0
    for mask in range(4):
        out, j, fi = [], 0, 0
        for c in ct[:200]:
            if len(out) >= 48:
                break
            if c == 0 and fi < 2:
                if (mask >> fi) & 1:
                    fi += 1
                    continue
                fi += 1
            if j >= len(keys):
                break
            k = int(keys[j]); j += 1
            out.append((int(c) - k) % N if dirn == 0 else (int(c) + k) % N)
        best = max(best, score(out))
    return best


def stream(seedval, mode, n=260):
    r = random.Random()
    r.seed(seedval)
    if mode == 'randrange':
        return [r.randrange(N) for _ in range(n)]
    if mode == 'randint':
        return [r.randint(0, N-1) for _ in range(n)]
    if mode == 'random':
        return [int(r.random() * N) for _ in range(n)]
    if mode == 'choice':
        pool = list(range(N))
        return [r.choice(pool) for _ in range(n)]
    if mode == 'shuffle':
        pool = list(range(N))
        out = []
        while len(out) < n:
            r.shuffle(pool)
            out.extend(pool)
        return out[:n]
    if mode == 'getrandbits':
        return [r.getrandbits(5) % N for _ in range(n)]
    raise ValueError(mode)


MODES = ('randrange', 'randint', 'random', 'choice', 'shuffle', 'getrandbits')


def main():
    cands = []
    for w in WORDS:
        cands.append(w)
        cands.append(w.encode())
    cands.extend(NUMS)
    cands.extend(float(x) for x in (3301, 1033, 3.301))
    best = (-99.0, None, None, None)
    tested = 0
    hits = []
    for s in cands:
        for mode in MODES:
            try:
                ks = stream(s, mode)
            except Exception:
                continue
            for dirn in (0, 1):
                sc = decode(ks, dirn)
                tested += 1
                if sc > best[0]:
                    best = (sc, s, mode, dirn)
                if sc > -12.5:
                    hits.append((sc, str(s), mode, dirn))
    print('candidates %d x modes %d x dirs 2 = %d decodes'
          % (len(cands), len(MODES), tested))
    print('best: %.4f  seed=%r mode=%s dir=%d' % best)
    print('threshold -12.5 hits: %d' % len(hits))
    for h in sorted(hits, reverse=True)[:10]:
        print('  ', h)
    json.dump(dict(tested=tested, best_score=best[0], best_seed=str(best[1]),
                   best_mode=best[2], hits=hits),
              open(os.path.join(HERE, 'string_seed_results.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
