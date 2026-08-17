/* L5-seed32 fork of analysis/seed_sweep/sweep.c (Round 8).
 * ONLY change: ct/ngram paths honour env LP_CT / LP_NGRAM so the same binary can
 * be pointed at shuffled-ciphertext null controls without duplicating ngram.bin.
 * Algorithm, generators, scoring and interrupter branching are byte-identical.
 *
 * Track SEED — exhaustive seeded-PRNG keystream reconstruction against LP2 0-54.
 *
 * Hypothesis: the "one-time pad" is a PRNG stream from a small seed. Every prior
 * round measured keystream STRUCTURE (none) but never keystream ENTROPY. A seeded
 * PRNG is indistinguishable from a pad by every structural test yet carries only
 * 31-48 bits of key -- far below the ~32,000 bits of English redundancy in 12,956
 * runes, so a hit cannot be manufactured by search.
 *
 * Decoder honours the documented interrupter rule: only rune 0 (F) may be a null;
 * a null is removed from the plaintext and does NOT advance the keystream. We
 * branch over the (few) F decisions inside the scored window and keep the best.
 *
 * Build:  gcc -O3 -march=native -fopenmp -o sweep sweep.c -lm
 * Usage:  ./sweep <gen> <lo> <hi> [window] [thresh]
 *         ./sweep selftest
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>

#define N 29
#define MAXW 96          /* max scored plaintext runes                     */
#define MAXCT 256        /* ciphertext runes consumed to fill the window   */
#define MAXK 96          /* keystream values generated per seed. L5 change: was 320.
                          * decode_score never reads k[] beyond index window-1 (<=47 at
                          * the pre-registered window=48), and every generator produces
                          * a fixed prefix, so the shorter buffer yields byte-identical
                          * results -- A/B verified on gen0 seeds 0..1e7. Pure speedup. */

static uint8_t ct[13000];
static int ctlen;
static float *ngram;     /* 29^4 log probs */

/* ------------------------------------------------------------------ PRNGs */

/* --- glibc random() TYPE_3 additive feedback (also what rand() calls) --- */
/* state is a 31-word ring; ring[p] holds value at index i-31, ring[(p+28)%31]
 * holds i-3, matching glibc's TYPE_3 trinomial x^31 + x^3 + 1. */
typedef struct { int32_t ring[31]; int p; } glibc_t;
static inline void glibc_seed(glibc_t *g, uint32_t seed)
{
    int32_t r[344];
    if (seed == 0) seed = 1;
    r[0] = (int32_t)seed;
    for (int i = 1; i < 31; i++) {
        int64_t hi = r[i-1] / 127773;
        int64_t lo = r[i-1] % 127773;
        int64_t word = 16807 * lo - 2836 * hi;
        if (word < 0) word += 2147483647;
        r[i] = (int32_t)word;
    }
    for (int i = 31; i < 34; i++) r[i] = r[i-31];
    for (int i = 34; i < 344; i++) r[i] = (int32_t)((uint32_t)r[i-31] + (uint32_t)r[i-3]);
    for (int i = 0; i < 31; i++) g->ring[i] = r[313 + i];   /* indices 313..343 */
    g->p = 0;
}
static inline uint32_t glibc_next(glibc_t *g)
{
    int p = g->p;
    uint32_t v = (uint32_t)g->ring[p] + (uint32_t)g->ring[(p + 28) % 31];
    g->ring[p] = (int32_t)v;
    g->p = (p + 1) % 31;
    return v >> 1;
}

/* --- MSVC / ANSI C LCG rand() --- */
typedef struct { uint32_t s; } msvc_t;
static inline void msvc_seed(msvc_t *m, uint32_t seed) { m->s = seed; }
static inline uint32_t msvc_next(msvc_t *m)
{
    m->s = m->s * 214013u + 2531011u;
    return (m->s >> 16) & 0x7fff;
}

/* --- Mersenne Twister MT19937 (C++ std::mt19937 / init_genrand) --- */
typedef struct { uint32_t mt[624]; int idx; } mt_t;
static inline void mt_seed(mt_t *m, uint32_t seed)
{
    m->mt[0] = seed;
    for (int i = 1; i < 624; i++)
        m->mt[i] = 1812433253u * (m->mt[i-1] ^ (m->mt[i-1] >> 30)) + i;
    m->idx = 624;
}
static void mt_twist(mt_t *m)
{
    for (int i = 0; i < 624; i++) {
        uint32_t y = (m->mt[i] & 0x80000000u) | (m->mt[(i+1) % 624] & 0x7fffffffu);
        uint32_t n = m->mt[(i + 397) % 624] ^ (y >> 1);
        if (y & 1) n ^= 0x9908b0dfu;
        m->mt[i] = n;
    }
    m->idx = 0;
}
static inline uint32_t mt_next(mt_t *m)
{
    if (m->idx >= 624) mt_twist(m);
    uint32_t y = m->mt[m->idx++];
    y ^= y >> 11;
    y ^= (y << 7) & 0x9d2c5680u;
    y ^= (y << 15) & 0xefc60000u;
    y ^= y >> 18;
    return y;
}

/* --- Python 3 random.seed(int) : init_by_array over the int's 32-bit words --- */
static inline void mt_seed_bykey(mt_t *m, const uint32_t *key, int klen)
{
    mt_seed(m, 19650218u);
    int i = 1, j = 0;
    int k = (624 > klen) ? 624 : klen;
    for (; k; k--) {
        m->mt[i] = (m->mt[i] ^ ((m->mt[i-1] ^ (m->mt[i-1] >> 30)) * 1664525u))
                   + key[j] + (uint32_t)j;
        i++; j++;
        if (i >= 624) { m->mt[0] = m->mt[623]; i = 1; }
        if (j >= klen) j = 0;
    }
    for (k = 623; k; k--) {
        m->mt[i] = (m->mt[i] ^ ((m->mt[i-1] ^ (m->mt[i-1] >> 30)) * 1566083941u))
                   - (uint32_t)i;
        i++;
        if (i >= 624) { m->mt[0] = m->mt[623]; i = 1; }
    }
    m->mt[0] = 0x80000000u;
    m->idx = 624;
}

/* --- Java java.util.Random 48-bit LCG --- */
typedef struct { uint64_t s; } java_t;
static inline void java_seed(java_t *j, uint64_t seed)
{ j->s = (seed ^ 0x5DEECE66DULL) & ((1ULL << 48) - 1); }
static inline uint32_t java_bits(java_t *j, int bits)
{
    j->s = (j->s * 0x5DEECE66DULL + 0xBULL) & ((1ULL << 48) - 1);
    return (uint32_t)(j->s >> (48 - bits));
}
static inline int java_nextInt(java_t *j, int bound)
{
    int r = (int)java_bits(j, 31);
    int m = bound - 1;
    for (int u = r; u - (r = u % bound) + m < 0; u = (int)java_bits(j, 31)) ;
    return r;
}

/* ------------------------------------------------- keystream construction */
/* gen encodes generator x reduction. Fills k[0..n-1] with values 0..28. */
static void keystream(int gen, uint64_t seed, uint8_t *k, int n)
{
    switch (gen) {
    case 0: { /* glibc random() % 29 */
        glibc_t g; glibc_seed(&g, (uint32_t)seed);
        for (int i = 0; i < n; i++) k[i] = glibc_next(&g) % N;
        break; }
    case 1: { /* glibc random() scaled: (double)r/RAND_MAX*29 */
        glibc_t g; glibc_seed(&g, (uint32_t)seed);
        for (int i = 0; i < n; i++) {
            uint32_t v = glibc_next(&g);
            uint32_t x = (uint32_t)(((uint64_t)v * N) / 2147483648ULL);
            k[i] = (uint8_t)(x >= N ? N - 1 : x);
        }
        break; }
    case 2: { /* glibc random() % 29 with rejection resample on doublet */
        glibc_t g; glibc_seed(&g, (uint32_t)seed);
        int prev = -1;
        for (int i = 0; i < n; i++) {
            uint8_t v;
            do { v = glibc_next(&g) % N; } while (v == prev);
            k[i] = v; prev = v;
        }
        break; }
    case 3: { /* MSVC rand() % 29 */
        msvc_t m; msvc_seed(&m, (uint32_t)seed);
        for (int i = 0; i < n; i++) k[i] = msvc_next(&m) % N;
        break; }
    case 4: { /* MSVC rand() scaled */
        msvc_t m; msvc_seed(&m, (uint32_t)seed);
        for (int i = 0; i < n; i++) {
            uint32_t x = (uint32_t)(((uint64_t)msvc_next(&m) * N) >> 15);
            k[i] = (uint8_t)(x >= N ? N - 1 : x);
        }
        break; }
    case 5: { /* MT19937 (init_genrand) % 29 */
        mt_t m; mt_seed(&m, (uint32_t)seed);
        for (int i = 0; i < n; i++) k[i] = mt_next(&m) % N;
        break; }
    case 6: { /* MT19937 (init_genrand) scaled by random()*29 (52-bit double) */
        mt_t m; mt_seed(&m, (uint32_t)seed);
        for (int i = 0; i < n; i++) {
            uint32_t a = mt_next(&m) >> 5, b = mt_next(&m) >> 6;
            double d = (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
            int x = (int)(d * N);
            k[i] = (uint8_t)(x >= N ? N - 1 : x);
        }
        break; }
    case 7: { /* Python3 random.seed(int) + randrange(29): getrandbits(5) reject */
        mt_t m; uint32_t key[2];
        key[0] = (uint32_t)(seed & 0xffffffffu);
        key[1] = (uint32_t)(seed >> 32);
        mt_seed_bykey(&m, key, (seed >> 32) ? 2 : 1);
        for (int i = 0; i < n; i++) {
            uint32_t v;
            do { v = mt_next(&m) >> 27; } while (v >= N);
            k[i] = (uint8_t)v;
        }
        break; }
    case 8: { /* Python3 random.seed(int) + int(random()*29) */
        mt_t m; uint32_t key[2];
        key[0] = (uint32_t)(seed & 0xffffffffu);
        key[1] = (uint32_t)(seed >> 32);
        mt_seed_bykey(&m, key, (seed >> 32) ? 2 : 1);
        for (int i = 0; i < n; i++) {
            uint32_t a = mt_next(&m) >> 5, b = mt_next(&m) >> 6;
            double d = (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
            int x = (int)(d * N);
            k[i] = (uint8_t)(x >= N ? N - 1 : x);
        }
        break; }
    case 9: { /* Java new Random(seed).nextInt(29) */
        java_t j; java_seed(&j, seed);
        for (int i = 0; i < n; i++) k[i] = (uint8_t)java_nextInt(&j, N);
        break; }
    default:
        for (int i = 0; i < n; i++) k[i] = 0;
    }
}
static const char *GENNAME[] = {
    "glibc random()%29", "glibc random() scaled", "glibc random()%29 +norepeat",
    "MSVC rand()%29", "MSVC rand() scaled", "mt19937 init_genrand %29",
    "mt19937 init_genrand double", "py3 seed(int) randrange(29)",
    "py3 seed(int) int(random()*29)", "java Random.nextInt(29)"
};
#define NGEN 10

/* --------------------------------------------------------------- scoring */
static inline float ngram_score(const uint8_t *p, int n)
{
    const float *g = ngram;
    float s = 0.f;
    for (int i = 3; i < n; i++)
        s += g[((p[i-3]*N + p[i-2])*N + p[i-1])*N + p[i]];
    return s / (float)(n - 3);
}

/* Decode a window with interrupter branching. dir 0: p=c-k, dir 1: p=c+k.
 * Returns best mean 4-gram score over the branch set. */
static float decode_score(const uint8_t *k, int off, int dir, int window)
{
    /* branch over F decisions; at most 2^BR paths, F is rare (1 per ~28 runes) */
    enum { BRMAX = 16 };
    uint8_t buf[BRMAX][MAXW];
    int blen[BRMAX], bj[BRMAX], nb = 1;
    blen[0] = 0; bj[0] = off;
    for (int i = 0; i < MAXCT && i < ctlen; i++) {
        uint8_t c = ct[i];
        int done = 1;
        int cur = nb;
        for (int b = 0; b < cur; b++) {
            if (blen[b] >= window) continue;
            done = 0;
        }
        if (done) break;
        if (c == 0 && nb * 2 <= BRMAX) {
            /* fork: this F is a null in the new branches */
            for (int b = 0; b < nb; b++) {
                memcpy(buf[nb + b], buf[b], blen[b]);
                blen[nb + b] = blen[b];
                bj[nb + b] = bj[b];          /* null: no key advance, no emit */
            }
            for (int b = 0; b < nb; b++) {   /* original branches: treat as real */
                if (blen[b] < window) {
                    int kv = k[bj[b]];
                    buf[b][blen[b]++] = dir ? (uint8_t)((c + kv) % N)
                                            : (uint8_t)((c - kv + N) % N);
                    bj[b]++;
                }
            }
            nb *= 2;
        } else {
            for (int b = 0; b < nb; b++) {
                if (blen[b] < window) {
                    int kv = k[bj[b]];
                    buf[b][blen[b]++] = dir ? (uint8_t)((c + kv) % N)
                                            : (uint8_t)((c - kv + N) % N);
                    bj[b]++;
                }
            }
        }
    }
    float best = -1e9f;
    for (int b = 0; b < nb; b++) {
        if (blen[b] < 16) continue;
        float s = ngram_score(buf[b], blen[b]);
        if (s > best) best = s;
    }
    return best;
}

/* ------------------------------------------------------------------ main */
static void load(void)
{
    const char *ctpath = getenv("LP_CT");     if (!ctpath) ctpath = "ct.bin";
    const char *ngpath = getenv("LP_NGRAM");  if (!ngpath) ngpath = "ngram.bin";
    FILE *f = fopen(ctpath, "rb");
    if (!f) { perror(ctpath); exit(1); }
    ctlen = (int)fread(ct, 1, sizeof ct, f);
    fclose(f);
    ngram = malloc(sizeof(float) * N * N * N * N);
    f = fopen(ngpath, "rb");
    if (!f) { perror(ngpath); exit(1); }
    if (fread(ngram, sizeof(float), N*N*N*N, f) != (size_t)(N*N*N*N))
        { fprintf(stderr, "short ngram\n"); exit(1); }
    fclose(f);
}

static void selftest(void)
{
    /* plant: encipher a known English plaintext with each generator at a known
     * seed, write it over a copy of the ciphertext head, and confirm the sweep
     * recovers exactly that seed. Also confirms interrupter branching. */
    const char *pt = "WITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOTHISVALUEITISTHE"
                     "DUTYOFEVERYPILGRIMTOSEEKOUTTHISPAGE";
    /* crude transliteration: A..Z single runes only (no multigraphs) so the plant
     * is scoreable English-in-futhorc */
    static const int LUT[26] = {24,17,5,23,18,0,6,8,10,11,5,20,19,9,3,13,5,4,15,
                                16,1,1,7,14,26,15};
    uint8_t plain[MAXCT]; int pn = 0;
    for (const char *s = pt; *s && pn < 200; s++) plain[pn++] = LUT[*s - 'A'];
    uint8_t saved[MAXCT]; memcpy(saved, ct, MAXCT);
    int fails = 0;
    for (int g = 0; g < NGEN; g++) {
        uint64_t seed = 1399000000ULL + g * 7919;
        uint8_t k[MAXK]; keystream(g, seed, k, MAXK);
        /* encipher with two nulls inserted at positions 5 and 21 */
        int ci = 0, kj = 0;
        for (int i = 0; i < pn && ci < MAXCT - 2; i++) {
            if (i == 5 || i == 21) ct[ci++] = 0;             /* null F */
            ct[ci++] = (uint8_t)((plain[i] + k[kj++]) % N);  /* dir 0 */
        }
        float sc = decode_score(k, 0, 0, 48);
        /* and confirm a wrong seed does not score */
        uint8_t k2[MAXK]; keystream(g, seed + 1, k2, MAXK);
        float bad = decode_score(k2, 0, 0, 48);
        printf("  gen %d %-30s true %.3f  wrong %.3f  %s\n", g, GENNAME[g],
               sc, bad, (sc > -12.5f && bad < -13.5f) ? "OK" : "FAIL");
        if (!(sc > -12.5f && bad < -13.5f)) fails++;
    }
    memcpy(ct, saved, MAXCT);
    printf("selftest: %d/%d generators recovered\n", NGEN - fails, NGEN);
}

int main(int argc, char **argv)
{
    load();
    if (argc > 1 && !strcmp(argv[1], "selftest")) { selftest(); return 0; }
    if (argc > 1 && !strcmp(argv[1], "dumpkey")) {
        /* first 12 keystream values per generator at the selftest seeds --
         * cross-check against ref.py (independent CPython / Java-spec impls) */
        for (int g = 0; g < NGEN; g++) {
            uint8_t k[MAXK];
            keystream(g, 1399000000ULL + g * 7919, k, 16);
            printf("gen%d %-30s :", g, GENNAME[g]);
            for (int i = 0; i < 12; i++) printf(" %d", k[i]);
            printf("\n");
        }
        return 0;
    }
    if (argc < 4) {
        fprintf(stderr, "usage: %s <gen 0-%d|all> <lo> <hi> [window] [thresh]\n",
                argv[0], NGEN - 1);
        return 1;
    }
    int g0 = 0, g1 = NGEN - 1;
    if (strcmp(argv[1], "all")) { g0 = g1 = atoi(argv[1]); }
    uint64_t lo = strtoull(argv[2], 0, 0), hi = strtoull(argv[3], 0, 0);
    int window = argc > 4 ? atoi(argv[4]) : 48;
    float thresh = argc > 5 ? atof(argv[5]) : -13.0f;
    if (window > MAXK - 16) { fprintf(stderr, "window %d too large for MAXK=%d\n", window, MAXK); return 1; }

    for (int g = g0; g <= g1; g++) {
        double t0 = omp_get_wtime();
        long long hits = 0;
        float gmax = -1e9f;
        uint64_t gmaxseed = 0;
#pragma omp parallel
        {
            float lmax = -1e9f; uint64_t lseed = 0; long long lh = 0;
            uint8_t k[MAXK];
#pragma omp for schedule(static)
            for (long long s = (long long)lo; s < (long long)hi; s++) {
                keystream(g, (uint64_t)s, k, MAXK);
                for (int dir = 0; dir < 2; dir++) {
                    float sc = decode_score(k, 0, dir, window);
                    if (sc > lmax) { lmax = sc; lseed = (uint64_t)s; }
                    if (sc > thresh) {
                        lh++;
#pragma omp critical
                        printf("HIT gen=%d seed=%llu dir=%d score=%.4f\n",
                               g, (unsigned long long)s, dir, sc);
                    }
                }
            }
#pragma omp critical
            { if (lmax > gmax) { gmax = lmax; gmaxseed = lseed; } hits += lh; }
        }
        double dt = omp_get_wtime() - t0;
        printf("gen=%d %-30s seeds=%llu..%llu  best=%.4f @%llu  hits>%.1f=%lld  %.1fs\n",
               g, GENNAME[g], (unsigned long long)lo, (unsigned long long)hi,
               gmax, (unsigned long long)gmaxseed, thresh, hits, dt);
        fflush(stdout);
    }
    return 0;
}
