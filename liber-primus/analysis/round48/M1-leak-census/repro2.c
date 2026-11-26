/* Round 48 / M1 Arm B2 — as repro.c, but e extra raw draws are skipped at every printed word start
 * (the word-length draw), with alignment restricted to page starts. See PREREG.md Addendum 2.
 *
 *   gcc -O3 -march=native -fopenmp -o repro2 repro2.c
 *   ./repro2 stream.txt layout.txt <gen> <seed_lo> <seed_hi>
 *   ./repro2 stream.txt layout.txt <gen> emit <seed> <m> <red> <e> <startpos> <n>
 * layout.txt: line 1 = page-start positions; line 2 = one 0/1 per rune (1 = a printed word starts here).
 */
#define main repro_main
#include "repro.c"
#undef main

static int WS[20000], PS[64], NP;
static int BH[2*841+1], BP[128], BA[128];   /* starts bucketed by (word-start-at-p+1, first rune, second rune), order-adjusted */

/* run the picker from text position p; return emitted runes in E (up to want) */
static int emit2x(const int *X, int lim, int e, int p, int *E, int want) {   /* X = reduced draws for one (m, red) */
    int n = 0, last = -1, k = 0;
    while (n < want && p + n < TN) {
        if (n == 0 || WS[p + n]) k += e;
        int got = -1;
        while (k < lim) { int x = X[k++]; if (x == last) continue; last = x; if (x < 29) { got = x; break; } }
        if (got < 0) break;
        E[n++] = got;
    }
    return n;
}
static int emit2(const raws_t *r, int m, int red, int e, int p, int *E, int want) {
    int n = 0, last = -1, k = 0;
    while (n < want && p + n < TN) {
        if (n == 0 || WS[p + n]) k += e;
        int got = -1;
        while (k < NR) {
            int x = red ? (int)(((unsigned __int128)r->v[k] * m) >> r->bits) : (int)(r->v[k] % m);
            k++;
            if (x == last) continue;
            last = x;
            if (x < 29) { got = x; break; }
        }
        if (got < 0) break;
        E[n++] = got;
    }
    return n;
}

int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage\n"); return 2; }
    load(argv[1]); mt_base();
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 2; }
    char line[70000];
    if (!fgets(line, sizeof line, f)) return 2;
    for (char *t = strtok(line, " \n"); t; t = strtok(0, " \n")) PS[NP++] = atoi(t);
    for (int i = 0; i < TN; i++) if (fscanf(f, "%d", &WS[i]) != 1) { fprintf(stderr, "layout short\n"); return 2; }
    fclose(f);
    genfn g = pick(argv[3]);
    if (!strcmp(argv[4], "emit")) {
        raws_t r; g((uint32_t)strtoull(argv[5], 0, 10), &r); int E[NR];
        int n = emit2(&r, atoi(argv[6]), atoi(argv[7]), atoi(argv[8]), atoi(argv[9]), E, atoi(argv[10]));
        for (int k = 0; k < n; k++) printf("%d\n", E[k]);
        return 0;
    }
    { int c = 0; for (int v = 0; v < 2*841; v++) { BH[v] = c;
        for (int a = 0; a < NP; a++) for (int atb = 0; atb < 2; atb++) {
            int p = PS[a], t0 = atb ? 28 - T[p] : T[p], t1 = atb ? 28 - T[p+1] : T[p+1];
            if (WS[p+1]*841 + t0*29 + t1 == v) { BP[c] = p; BA[c] = atb; c++; } } }
      BH[2*841] = c; }
    uint64_t lo = strtoull(argv[4], 0, 10), hi = strtoull(argv[5], 0, 10), hits = 0, near = 0;
    #pragma omp parallel for schedule(dynamic, 65536) reduction(+:hits,near)
    for (uint64_t s = lo; s < hi; s++) {
        raws_t r; g((uint32_t)s, &r); int E[NR];
        for (int m = 29; m <= 40; m++) for (int red = 0; red < 2; red++) {
          int X[NR];
          for (int k = 0; k < 12; k++) X[k] = red ? (int)(((unsigned __int128)r.v[k] * m) >> r.bits) : (int)(r.v[k] % m);
          for (int e = 1; e <= 2; e++) {
            /* first two runes for both cases of 'a word starts at the second rune' */
            for (int ws1 = 0; ws1 < 2; ws1++) {
              int F[2], n2 = 0, last = -1, k = e;
              while (n2 < 2 && k < 12) { int x = X[k++]; if (x == last) continue; last = x; if (x < 29) { F[n2++] = x; if (n2 == 1 && ws1) k += e; } }
              if (n2 < 2) continue;
              int key = ws1*841 + F[0]*29 + F[1];
              for (int q = BH[key]; q < BH[key + 1]; q++) {
                int p = BP[q], atb = BA[q];
                int n = emit2x(X, 12, e, p, E, 3);                     /* cheap screen on the first 12 draws */
                if (runlen(E, n, p, atb) < n) continue;                /* any mismatch among what was emitted */
                int Y[NR];                                             /* survivor: reduce all draws, full check */
                for (int k = 0; k < NR; k++) Y[k] = red ? (int)(((unsigned __int128)r.v[k] * m) >> r.bits) : (int)(r.v[k] % m);
                n = emit2x(Y, NR, e, p, E, NEED); int L = runlen(E, n, p, atb);
                if (L >= NEAR) {
                    #pragma omp critical
                    { printf("%s gen=%s seed=%llu m=%d red=%d e=%d atbash=%d pos=%d run=%d\n", L >= NEED ? "HIT" : "NEAR",
                             argv[3], (unsigned long long)s, m, red, e, atb, p, L); fflush(stdout); }
                    if (L >= NEED) hits++; else near++;
                }
              }
            }
          }
        }
    }
    printf("DONE-B2 gen=%s seeds=[%llu,%llu) near=%llu hits=%llu\n", argv[3], (unsigned long long)lo,
           (unsigned long long)hi, (unsigned long long)near, (unsigned long long)hits);
    return 0;
}
