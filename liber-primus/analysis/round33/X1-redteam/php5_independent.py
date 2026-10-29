"""X1/R33: independent re-derivation of PHP 5.x mt_srand/mt_rand (ext/standard/mt_rand.c, 5.2-7.0) in the C pointer form,
written from the source's structure (php_mt_initialize / php_mt_reload / twist with loBit(u)), NOT from php_mt.py."""
import sys, json
sys.path.insert(0, 'round32/B2-php-mtrand')
import php_mt
M32 = 0xFFFFFFFF
def php5_stream(seed, n):
    st = [0]*624; st[0] = seed & M32
    for i in range(1, 624): st[i] = (1812433253 * (st[i-1] ^ (st[i-1] >> 30)) + i) & M32
    out = []
    def tw(m, u, v): return m ^ ((((u & 0x80000000) | (v & 0x7FFFFFFF)) >> 1)) ^ ((-(u & 1)) & 0x9908B0DF)  # loBit(u): the PHP<=7.0 form
    while len(out) < n:
        p = 0
        for _ in range(624-397): st[p] = tw(st[p+397], st[p], st[p+1]) & M32; p += 1
        for _ in range(397-1): st[p] = tw(st[p+397-624], st[p], st[p+1]) & M32; p += 1
        st[p] = tw(st[p+397-624], st[p], st[0]) & M32
        for s1 in st:
            s1 ^= s1 >> 11; s1 ^= (s1 << 7) & 0x9D2C5680; s1 ^= (s1 << 15) & 0xEFC60000
            out.append(((s1 ^ (s1 >> 18)) & M32) >> 1)
    return out[:n]
r = {'seed1_first': php5_stream(1, 1)[0], 'published_PHP5_mt_srand1_mt_rand_(recalled)': 1244335972,
     'match_published': php5_stream(1,1)[0] == 1244335972,
     'match_php_mt_all_seeds_1500_draws': all(php5_stream(s, 1500) == php_mt.stream31(s, 'php', 1500) for s in (1, 777, 3301, 1325734783, 4294967295, 0))}
print(json.dumps(r, indent=1))
