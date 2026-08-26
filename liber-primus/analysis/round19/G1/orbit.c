/* Round 19 / G1 -- measure, do not assert: the ORBIT STRUCTURE of each bash brand()
 * state map, with Brent's cycle-detection algorithm.
 *
 * Why this matters for the space statement.  brand() is a pure map s -> f(s) and
 * `RANDOM=<seed>` sets s = seed, so the set of DISTINCT $RANDOM keystreams equals the
 * set of distinct orbits of f.  If f has one big cycle, "enumerate 2**31 seeds" is one
 * pass over one sequence (a sliding window), not 2**31 independent runs.  If f has a
 * short cycle or many components, the true size of the space is smaller than the seed
 * range and must be reported as such.
 *
 * bash 5.0/5.1 use a true Lehmer generator mod 2**31-1 (one cycle, length 2**31-2).
 * bash 3.2-4.3 do NOT: rseed is `unsigned long` and the `if (rseed < 0) rseed +=
 * 0x7fffffff` correction is compiled out by `#if 0`, so on LP64 a negative Schrage
 * residue wraps to a ~1.8e19 unsigned value.  The structure is an empirical question.
 *
 * Build:  gcc -O2 -o orbit orbit.c
 * Run:    ./orbit                       (all variants from a few start states)
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

static uint64_t f_bash42_lp64(uint64_t s)
{
    long h, l;
    if (s == 0) s = 123459876;
    h = (long)(s / 127773);
    l = (long)(s % 127773);
    return (uint64_t)(16807 * l - 2836 * h);
}

static uint64_t f_bash42_ilp32(uint64_t s)
{
    uint32_t r = (uint32_t)s;
    int32_t h, l;
    if (r == 0) r = 123459876;
    h = r / 127773;
    l = r % 127773;
    return (uint64_t)(uint32_t)(16807 * l - 2836 * h);
}

static uint64_t f_bash32_lp64(uint64_t s)
{
    return s * 1103515245ULL + 12345ULL;
}

static uint64_t f_bash32_ilp32(uint64_t s)
{
    return (uint64_t)(uint32_t)((uint32_t)s * 1103515245u + 12345u);
}

static uint64_t f_bash50(uint64_t s)
{
    uint32_t r = (uint32_t)s;
    int32_t h, l, t;
    if (r == 0) r = 123459876;
    h = r / 127773;
    l = r - 127773 * h;
    t = 16807 * l - 2836 * h;
    r = (t < 0) ? (uint32_t)(t + 0x7fffffff) : (uint32_t)t;
    return r;
}

typedef uint64_t (*mapfn)(uint64_t);

struct ent { const char *name; mapfn f; };
static struct ent MAPS[] = {
    {"bash4.2",     f_bash42_lp64},
    {"bash4.2_i32", f_bash42_ilp32},
    {"bash3.2",     f_bash32_lp64},
    {"bash3.2_i32", f_bash32_ilp32},
    {"bash5.0",     f_bash50},          /* == bash5.1's state map */
    {NULL, NULL}
};

/* Brent: returns cycle length lam and tail length mu. */
static void brent(mapfn f, uint64_t x0, uint64_t *lam_out, uint64_t *mu_out)
{
    uint64_t power = 1, lam = 1;
    uint64_t tortoise = x0, hare = f(x0);
    while (tortoise != hare) {
        if (power == lam) { tortoise = hare; power <<= 1; lam = 0; }
        hare = f(hare); lam++;
    }
    tortoise = hare = x0;
    for (uint64_t i = 0; i < lam; i++) hare = f(hare);
    uint64_t mu = 0;
    while (tortoise != hare) { tortoise = f(tortoise); hare = f(hare); mu++; }
    *lam_out = lam; *mu_out = mu;
}

/* NOTE on bash3.2 LP64.  Its map is a full-period LCG mod 2**64 (multiplier
 * 1103515245 = 1 mod 4, increment 12345 odd -> Hull-Dobell full period 2**64), so
 * Brent would need 2**64 evaluations and is not worth running.  Analytically: for an
 * LCG mod 2**m, output bit i has period 2**(i+1), so the 15-bit output (bits 16..30)
 * repeats with period 2**31.  The ILP32 build is a full-period LCG mod 2**32, output
 * period 2**31 by the same argument.  Both are STATED, not measured, and labelled so
 * in RESULTS.md section 3.2.
 *
 * Usage:  ./orbit                       all variants
 *         ./orbit bash5.0 bash3.2_i32   only the named ones
 *         ./orbit -n 2 bash4.2          only the first 2 start states
 */
int main(int argc, char **argv)
{
    static const uint64_t starts[] = {1, 2, 3301, 12345, 123459876,
                                      1376006400ULL, 2147483647ULL, 4294967295ULL};
    unsigned nstart = sizeof starts / sizeof starts[0];
    int first = 1;

    if (argc > 2 && strcmp(argv[1], "-n") == 0) {
        unsigned v = (unsigned)atoi(argv[2]);
        if (v > 0 && v < nstart) nstart = v;
        first = 3;
    }

    printf("variant       start          cycle_len            tail\n");
    for (int i = 0; MAPS[i].name; i++) {
        if (argc > first) {
            int want = 0;
            for (int a = first; a < argc; a++)
                if (strcmp(argv[a], MAPS[i].name) == 0) want = 1;
            if (!want) continue;
        }
        for (unsigned k = 0; k < nstart; k++) {
            uint64_t lam, mu;
            brent(MAPS[i].f, starts[k], &lam, &mu);
            printf("%-13s %-14llu %-20llu %llu\n", MAPS[i].name,
                   (unsigned long long)starts[k],
                   (unsigned long long)lam, (unsigned long long)mu);
            fflush(stdout);
        }
    }
    return 0;
}
