/* Round 48 / M1 Arm B — generator-reproduction sweep.
 * Is the unsolved LP2 rune stream the direct output of a seeded library PRNG driving a
 * no-repeat picker over m symbols (draws >= 29 dropped but remembered)?
 *
 *   gcc -O3 -march=native -fopenmp -o repro repro.c
 *   ./repro stream.txt <gen> <seed_lo> <seed_hi>        sweep
 *   ./repro stream.txt <gen> dump <seed> <n>            print n raw values (validation)
 *   ./repro stream.txt <gen> emit <seed> <m> <red> <n>  print n emitted runes (plants)
 *
 * gen: glibc drand48 py27 bash42 bash42_32 msvc ansi minstd
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define NR 40            /* raw draws kept per seed */
#define NEED 14          /* exact-match run that counts as a HIT */
#define NEAR 10          /* logged as near-hit */
#define P5 20511149u     /* 29^5 */

static int T[20000], TN;
static uint8_t *bits;                 /* 5-gram bitset, forward + atbash */
static int *head, *nxt;               /* 5-gram -> positions (chained) */

typedef struct { uint64_t v[NR]; int bits; } raws_t;   /* v in [0, 2^bits) */

/* ---------------- generators ---------------- */
static void g_glibc(uint32_t seed, raws_t *o) {
    int32_t r[344 + NR];
    if (seed == 0) seed = 1;
    r[0] = (int32_t)seed;
    for (int i = 1; i < 31; i++) {
        int64_t hi = r[i-1] / 127773, lo = r[i-1] % 127773;
        int64_t w = 16807 * lo - 2836 * hi;
        if (w < 0) w += 2147483647;
        r[i] = (int32_t)w;
    }
    for (int i = 31; i < 34; i++) r[i] = r[i-31];
    for (int i = 34; i < 344 + NR; i++) r[i] = (int32_t)((uint32_t)r[i-31] + (uint32_t)r[i-3]);
    for (int k = 0; k < NR; k++) o->v[k] = ((uint32_t)r[k+344]) >> 1;
    o->bits = 31;
}
static void g_drand48(uint32_t seed, raws_t *o) {
    uint64_t x = (((uint64_t)seed) << 16) | 0x330E;
    for (int k = 0; k < NR; k++) { x = (x * 0x5DEECE66DULL + 0xB) & 0xFFFFFFFFFFFFULL; o->v[k] = x; }
    o->bits = 48;
}
static uint32_t MTBASE[624];
static void mt_base(void) {
    MTBASE[0] = 19650218u;
    for (int i = 1; i < 624; i++) MTBASE[i] = 1812433253u * (MTBASE[i-1] ^ (MTBASE[i-1] >> 30)) + i;
}
static void g_py27(uint32_t seed, raws_t *o) {
    uint32_t mt[624 + 2*NR + 2];
    memcpy(mt, MTBASE, sizeof MTBASE);
    int i = 1;
    for (int k = 624; k; k--) {               /* key = [seed], length 1 -> j always 0 */
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1664525u)) + seed;
        if (++i >= 624) { mt[0] = mt[623]; i = 1; }
    }
    for (int k = 623; k; k--) {
        mt[i] = (mt[i] ^ ((mt[i-1] ^ (mt[i-1] >> 30)) * 1566083941u)) - i;
        if (++i >= 624) { mt[0] = mt[623]; i = 1; }
    }
    mt[0] = 0x80000000u;
    uint32_t out[2*NR];
    for (int kk = 0; kk < 2*NR; kk++) {       /* partial twist: needs mt[kk], mt[kk+1], mt[kk+397] */
        uint32_t y = (mt[kk] & 0x80000000u) | (mt[kk+1] & 0x7fffffffu);
        uint32_t z = mt[kk+397] ^ (y >> 1) ^ ((y & 1) ? 0x9908b0dfu : 0);
        z ^= z >> 11; z ^= (z << 7) & 0x9d2c5680u; z ^= (z << 15) & 0xefc60000u; z ^= z >> 18;
        out[kk] = z;
    }
    for (int k = 0; k < NR; k++) o->v[k] = (((uint64_t)(out[2*k] >> 5)) << 26) | (out[2*k+1] >> 6);
    o->bits = 53;
}
static void g_bash42(uint32_t seed, raws_t *o) {       /* LP64: rseed unsigned long */
    uint64_t s = seed; uint32_t last = 0;
    for (int k = 0; k < NR; k++) {
        uint32_t rv;
        do { if (s == 0) s = 123459876; uint64_t h = s / 127773, l = s % 127773;
             s = 16807 * l - 2836 * h; rv = (uint32_t)(s & 32767); } while (rv == last);
        last = rv; o->v[k] = rv;
    }
    o->bits = 15;
}
static void g_bash42_32(uint32_t seed, raws_t *o) {    /* ILP32 */
    uint32_t s = seed, last = 0;
    for (int k = 0; k < NR; k++) {
        uint32_t rv;
        do { if (s == 0) s = 123459876; uint32_t h = s / 127773, l = s % 127773;
             s = 16807 * l - 2836 * h; rv = s & 32767; } while (rv == last);
        last = rv; o->v[k] = rv;
    }
    o->bits = 15;
}
static void g_msvc(uint32_t seed, raws_t *o) {
    uint32_t s = seed;
    for (int k = 0; k < NR; k++) { s = s * 214013u + 2531011u; o->v[k] = (s >> 16) & 0x7fff; }
    o->bits = 15;
}
static void g_ansi(uint32_t seed, raws_t *o) {
    uint32_t s = seed;
    for (int k = 0; k < NR; k++) { s = s * 1103515245u + 12345u; o->v[k] = (s >> 16) & 0x7fff; }
    o->bits = 15;
}
static void g_minstd(uint32_t seed, raws_t *o) {
    uint64_t s = seed % 2147483647u; if (s == 0) s = 1;
    for (int k = 0; k < NR; k++) { s = (s * 16807) % 2147483647u; o->v[k] = s; }
    o->bits = 31;
}
typedef void (*genfn)(uint32_t, raws_t *);
static genfn pick(const char *n) {
    if (!strcmp(n, "glibc")) return g_glibc;
    if (!strcmp(n, "drand48")) return g_drand48;
    if (!strcmp(n, "py27")) return g_py27;
    if (!strcmp(n, "bash42")) return g_bash42;
    if (!strcmp(n, "bash42_32")) return g_bash42_32;
    if (!strcmp(n, "msvc")) return g_msvc;
    if (!strcmp(n, "ansi")) return g_ansi;
    if (!strcmp(n, "minstd")) return g_minstd;
    fprintf(stderr, "unknown generator %s\n", n); exit(2);
}

/* picker Z4(m): redraw while equal to last raw index; draws >= 29 dropped but remembered */
static inline int emit(const raws_t *r, int m, int red, int *E, int want) {
    int n = 0, last = -1;
    for (int k = 0; k < NR && n < want; k++) {
        int x = red ? (int)(((unsigned __int128)r->v[k] * m) >> r->bits) : (int)(r->v[k] % m);
        if (x == last) continue;
        last = x;
        if (x < 29) E[n++] = x;
    }
    return n;
}
static inline uint32_t code5(const int *e) { return (((e[0]*29u + e[1])*29u + e[2])*29u + e[3])*29u + e[4]; }

static void load(const char *path) {
    FILE *f = fopen(path, "r"); if (!f) { perror(path); exit(2); }
    while (fscanf(f, "%d", &T[TN]) == 1) TN++;
    fclose(f);
    bits = calloc(P5 / 8 + 1, 1); head = malloc(sizeof(int) * P5); nxt = malloc(sizeof(int) * TN);
    memset(head, 0xff, sizeof(int) * P5);
    for (int i = TN - 5; i >= 0; i--) {
        uint32_t c = code5(T + i);
        bits[c >> 3] |= 1 << (c & 7); nxt[i] = head[c]; head[c] = i;
        int a[5]; for (int j = 0; j < 5; j++) a[j] = 28 - T[i+j];
        c = code5(a); bits[c >> 3] |= 1 << (c & 7);
    }
}
static int runlen(const int *E, int n, int pos, int atb) {
    int k = 0;
    while (k < n && pos + k < TN && (atb ? 28 - T[pos+k] : T[pos+k]) == E[k]) k++;
    return k;
}

int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    load(argv[1]); mt_base();
    genfn g = pick(argv[2]);
    if (!strcmp(argv[3], "dump")) {
        raws_t r; g((uint32_t)strtoull(argv[4], 0, 10), &r);
        int n = atoi(argv[5]); for (int k = 0; k < n && k < NR; k++) printf("%llu\n", (unsigned long long)r.v[k]);
        return 0;
    }
    if (!strcmp(argv[3], "emit")) {
        /* long emission for plants: re-run the generator by chaining is not possible here, so
           plants are 24 runes long (what one seed yields inside NR raws). */
        raws_t r; g((uint32_t)strtoull(argv[4], 0, 10), &r);
        int E[NR]; int n = emit(&r, atoi(argv[5]), atoi(argv[6]), E, atoi(argv[7]));
        for (int k = 0; k < n; k++) printf("%d\n", E[k]);
        return 0;
    }
    uint64_t lo = strtoull(argv[3], 0, 10), hi = strtoull(argv[4], 0, 10);
    uint64_t hits = 0, near = 0, pre = 0;
    #pragma omp parallel for schedule(dynamic, 65536) reduction(+:hits,near,pre)
    for (uint64_t s = lo; s < hi; s++) {
        raws_t r; g((uint32_t)s, &r);
        int E[NR];
        for (int m = 29; m <= 40; m++) for (int red = 0; red < 2; red++) {
            if (emit(&r, m, red, E, 5) < 5) continue;
            uint32_t c = code5(E);
            if (!(bits[c >> 3] & (1 << (c & 7)))) continue;
            pre++;
            int n = emit(&r, m, red, E, NR);
            for (int atb = 0; atb < 2; atb++) {
                int a[5]; for (int j = 0; j < 5; j++) a[j] = atb ? 28 - E[j] : E[j];
                for (int p = head[code5(a)]; p >= 0; p = nxt[p]) {
                    int L = runlen(E, n, p, atb);
                    if (L >= NEAR) {
                        #pragma omp critical
                        { printf("%s gen=%s seed=%llu m=%d red=%d atbash=%d pos=%d run=%d emitted=%d\n",
                                 L >= NEED ? "HIT" : "NEAR", argv[2], (unsigned long long)s, m, red, atb, p, L, n);
                          fflush(stdout); }
                        if (L >= NEED) hits++; else near++;
                    }
                }
            }
        }
    }
    printf("DONE gen=%s seeds=[%llu,%llu) prefilter_pass=%llu near=%llu hits=%llu\n", argv[2],
           (unsigned long long)lo, (unsigned long long)hi, (unsigned long long)pre,
           (unsigned long long)near, (unsigned long long)hits);
    return 0;
}
