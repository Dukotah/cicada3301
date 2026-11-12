/* Round 44 lane S1 - the blind (language-model-free) adjudicator, C kernel.
 *
 * For a candidate keystream K and a ciphertext head C the kernel finds, for each sign s in {+1,-1}
 * and each rejection step q in {1,2}, the key-pointer path with the largest sum of squared symbol
 * counts of the decode d_i = C_i - s*K_j (mod 29), where the pointer may jump only at ADMISSIBLE
 * sites: r draws K[j], K[j+q], .., K[j+(r-1)q] were rejected (so they are all equal) and K[j+rq]
 * was accepted, which forces s*(K[j+rq] - K[j]) = C[i] - C[i-1]. Nothing here knows any language.
 *
 * Three exhaustive stages on the same keystream: L1, L2, L3. For q=2 a visible doublet (C[i] ==
 * C[i-1], one that was kept) may also burn one extra draw at every stage: that is the in-stream
 * coin (round19/I1 enc_coin_from_key). The real page-0 head has no visible doublet before rune 122,
 * so this costs nothing there until stage 3. A (seed, mode) pair that reaches stage 3 is written
 * to the survivor file with all three statistics.
 *
 * build:  gcc -O3 -march=native -o blind blind.c
 * usage:  blind GEN LO HI CIPHER L1 T1 L2 T2 L3 OUT [HIST]
 *   GEN   perl   = Perl rand: srand48(seed), int(rand(29))      (seed in [LO,HI))
 *         glibcmod / glibcscale = glibc srand(seed); rand() % 29  /  floor(29 * rand() / 2^31)   (lane S2)
 *         rnd    = splitmix64-derived uniform keys (calibration; "seed" is just a counter)
 *         dump:G = print the first 24 key values of generator G for seed LO and exit (generator checks)
 *         file:P = one keystream read from text file P (plants / spot checks)
 *   T1,T2 = integer thresholds on the sum of squared counts at L1, L2
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 29
#define MAXL 300
#define KN 420
#define STK 8192

static uint8_t C[MAXL], dC[MAXL];
static int CL;
static uint8_t DEC[2][N][N];      /* DEC[s][c][k] = (c - s*k) mod 29, s index 0 => +1, 1 => -1 */
static uint8_t SD[2][2 * N];      /* SD[s][kb - ka + 28] = s*(kb - ka) mod 29 */

typedef struct { int16_t i, j, used; int32_t ssq; uint8_t cnt[N]; uint8_t coin; } st_t;
static st_t stk[STK];

/* best sum of squares over admissible paths for the first L runes */
static int best_ssq(const uint8_t *K, int si, int q, int L, int maxsk, int coin)
{
    int best = 0, sp = 0;
    stk[sp].i = 0; stk[sp].j = 0; stk[sp].used = 0; stk[sp].ssq = 0; memset(stk[sp].cnt, 0, N); sp++;
    while (sp) {
        st_t s = stk[--sp];
        int i = s.i, j = s.j, used = s.used, ssq = s.ssq;
        while (i < L) {
            if (i > 0 && used < maxsk) {
                int r = 1;
                while (r <= 3) {
                    int jj = j + r * q;
                    if (SD[si][K[jj] - K[j] + 28] == dC[i] && sp < STK - 2) {
                        stk[sp].i = i; stk[sp].j = jj; stk[sp].used = used + r; stk[sp].ssq = ssq;
                        memcpy(stk[sp].cnt, s.cnt, N); sp++;
                    }
                    if (K[jj] != K[j]) break;
                    r++;
                }
            }
            int d = DEC[si][C[i]][K[j]];
            ssq += 2 * s.cnt[d] + 1; s.cnt[d]++;
            i++; j++;
            /* in-stream coin: a visible doublet that was kept still burned one draw (q = 2 only) */
            if (coin && i < L + 1 && i - 1 > 0 && dC[i - 1] == 0 && sp < STK - 2) {
                stk[sp].i = i; stk[sp].j = j + 1; stk[sp].used = used; stk[sp].ssq = ssq;
                memcpy(stk[sp].cnt, s.cnt, N); sp++;
            }
        }
        if (ssq > best) best = ssq;
    }
    return best;
}

static uint64_t sm_state;
static inline uint64_t splitmix(void)
{
    uint64_t z = (sm_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

static void gen_perl(uint32_t seed, uint8_t *K, int n)
{
    uint64_t x = ((uint64_t)seed << 16) | 0x330E;
    for (int t = 0; t < n; t++) {
        x = (x * 0x5DEECE66DULL + 0xB) & 0xFFFFFFFFFFFFULL;
        K[t] = (uint8_t)((x * 29) >> 48);
    }
}

/* glibc rand()/random(), TYPE_3 additive feedback, after srand(seed). how = 0: rand() % 29;
 * how = 1: floor(29 * rand() / 2^31), the scaling PHP 5's rand(0, 28) and much C code use. */
static void gen_glibc(uint32_t seed, uint8_t *K, int n, int how)
{
    static uint32_t r[344 + KN];
    int32_t w = (int32_t)seed; if (w == 0) w = 1;
    r[0] = (uint32_t)w;
    for (int i = 1; i < 31; i++) {
        int32_t hi = w / 127773, lo = w % 127773;
        w = 16807 * lo - 2836 * hi; if (w < 0) w += 2147483647;
        r[i] = (uint32_t)w;
    }
    for (int i = 31; i < 34; i++) r[i] = r[i - 31];
    for (int i = 34; i < 344 + n; i++) r[i] = r[i - 31] + r[i - 3];
    for (int t = 0; t < n; t++) {
        uint32_t o = r[344 + t] >> 1;
        K[t] = how ? (uint8_t)(((uint64_t)o * 29) >> 31) : (uint8_t)(o % 29);
    }
}

static void gen_rnd(uint64_t ctr, uint8_t *K, int n)
{
    sm_state = ctr * 0xD1B54A32D192ED03ULL + 0x1234567;
    for (int t = 0; t < n; t++) K[t] = (uint8_t)((splitmix() >> 11) % 29);
}

int main(int argc, char **argv)
{
    if (argc < 11) { fprintf(stderr, "usage: blind GEN LO HI CIPHER L1 T1 L2 T2 L3 OUT [HIST]\n"); return 2; }
    const char *gen = argv[1];
    uint64_t lo = strtoull(argv[2], 0, 10), hi = strtoull(argv[3], 0, 10);
    if (!strncmp(gen, "dump:", 5)) {
        uint8_t D[KN];
        if (gen[5] == 'p') gen_perl((uint32_t)lo, D, KN);
        else gen_glibc((uint32_t)lo, D, KN, !strcmp(gen + 5, "glibcscale"));
        for (int t = 0; t < 24; t++) printf("%d ", D[t]);
        printf("\n"); return 0;
    }
    FILE *f = fopen(argv[4], "r"); if (!f) { perror("cipher"); return 2; }
    int v; CL = 0; while (CL < MAXL && fscanf(f, "%d", &v) == 1) C[CL++] = (uint8_t)v; fclose(f);
    int L1 = atoi(argv[5]), T1 = atoi(argv[6]), L2 = atoi(argv[7]), T2 = atoi(argv[8]), L3 = atoi(argv[9]);
    if (L3 > CL) L3 = CL;
    if (L2 > CL) L2 = CL;
    for (int i = 1; i < CL; i++) dC[i] = (uint8_t)((C[i] - C[i - 1] + N) % N);
    for (int c = 0; c < N; c++) for (int k = 0; k < N; k++) {
        DEC[0][c][k] = (uint8_t)((c - k + N) % N); DEC[1][c][k] = (uint8_t)((c + k) % N); }
    for (int d = -28; d <= 28; d++) { SD[0][d + 28] = (uint8_t)(((d % N) + N) % N); SD[1][d + 28] = (uint8_t)(((-d % N) + N) % N); }
    FILE *out = fopen(argv[10], "wb"); if (!out) { perror("out"); return 2; }
    static uint64_t hist[4][2048]; memset(hist, 0, sizeof hist);
    static uint8_t K[KN];
    uint8_t filekey[KN]; int isfile = !strncmp(gen, "file:", 5);
    if (isfile) {
        FILE *kf = fopen(gen + 5, "r"); if (!kf) { perror("key"); return 2; }
        int n = 0; while (n < KN && fscanf(kf, "%d", &v) == 1) filekey[n++] = (uint8_t)v; fclose(kf);
        for (; n < KN; n++) filekey[n] = 0;
        lo = 0; hi = 1;
    }
    uint64_t n1 = 0, n2 = 0, n3 = 0;
    for (uint64_t sd = lo; sd < hi; sd++) {
        if (isfile) memcpy(K, filekey, KN);
        else if (gen[0] == 'p') gen_perl((uint32_t)sd, K, KN);
        else if (!strcmp(gen, "glibcmod")) gen_glibc((uint32_t)sd, K, KN, 0);
        else if (!strcmp(gen, "glibcscale")) gen_glibc((uint32_t)sd, K, KN, 1);
        else gen_rnd(sd, K, KN);
        for (int si = 0; si < 2; si++) for (int q = 1; q <= 2; q++) {
            int mode = si * 2 + (q - 1);
            int v1 = best_ssq(K, si, q, L1, 8, q == 2);
            hist[mode][v1 < 2047 ? v1 : 2047]++;
            if (v1 < T1) continue;
            n1++;
            int v2 = best_ssq(K, si, q, L2, 12, q == 2);
            if (v2 < T2) continue;
            n2++;
            int v3 = best_ssq(K, si, q, L3, 24, q == 2);
            n3++;
            uint32_t rec[5] = { (uint32_t)sd, (uint32_t)mode, (uint32_t)v1, (uint32_t)v2, (uint32_t)v3 };
            fwrite(rec, sizeof rec, 1, out);
        }
    }
    fclose(out);
    if (argc > 11) { FILE *h = fopen(argv[11], "wb"); fwrite(hist, sizeof hist, 1, h); fclose(h); }
    fprintf(stderr, "seeds %llu  stage1-pass %llu  stage2-pass %llu  written %llu\n",
            (unsigned long long)(hi - lo), (unsigned long long)n1, (unsigned long long)n2, (unsigned long long)n3);
    return 0;
}
