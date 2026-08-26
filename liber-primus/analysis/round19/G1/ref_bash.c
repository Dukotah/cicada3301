/* Round 19 / G1 -- REFERENCE for bash's $RANDOM, compiled from the GNU bash
 * release sources themselves.
 *
 * Each brand_* function below is a VERBATIM transcription of the corresponding
 * released bash `variables.c` / `lib/sh/random.c`, with only the K&R declaration
 * style modernised and the module-static `rseed` made a parameter of the state
 * struct.  Sources fetched from https://ftp.gnu.org/gnu/bash/ (see fetch_bash_src.sh):
 *
 *   bash-3.2  variables.c:1214  LCG rseed*1103515245+12345, (rseed>>16)&32767
 *   bash-4.0  variables.c       Park-Miller/Schrage, negative-fix #if 0'd, rseed==0 -> seedrand()
 *   bash-4.1  variables.c       identical to 4.0
 *   bash-4.2  variables.c:1236  Park-Miller/Schrage, negative-fix #if 0'd, rseed==0 -> 123459876
 *   bash-4.3  variables.c       identical to 4.2
 *   bash-5.0  variables.c       rseed is u_bits32_t, t is bits32_t, negative-fix ENABLED
 *   bash-5.1+ lib/sh/random.c   intrand32() + brand() folding (rseed>>16)^(rseed&65535)
 *
 * THE POINT OF THIS FILE: in 3.2-4.3 `rseed` is `unsigned long` and `h`,`l` are
 * `long`, so the arithmetic width is the ABI's, and the "#if 0"-disabled negative
 * correction lets rseed go through the unsigned wrap.  A 64-bit (LP64) box and a
 * 32-bit (ILP32) box therefore emit DIFFERENT $RANDOM streams from the same seed.
 * Both are era-plausible for an Ubuntu 11.04-12.04 workstation, so both are covered.
 *
 * Build:  gcc -O2 -o ref_bash ref_bash.c              (LP64)
 *         gcc -O2 -m32 -o ref_bash32 ref_bash.c       (ILP32, needs gcc-multilib)
 * Run:    ./ref_bash <seed> [<seed> ...]
 */
#include <stdio.h>
#include <stdlib.h>

#define NDRAW 2000

/* ---- exact width of the C types bash uses, for the record ---------------- */
static void emit_abi(void)
{
    printf("{\"abi\":{\"sizeof_long\":%d,\"sizeof_ulong\":%d,\"sizeof_int\":%d}}\n",
           (int)sizeof(long), (int)sizeof(unsigned long), (int)sizeof(int));
}

/* ================= bash 3.2 ============================================== */
static unsigned long rseed_32 = 1;
static int brand_bash32(void)
{
    rseed_32 = rseed_32 * 1103515245 + 12345;
    return ((unsigned int)((rseed_32 >> 16) & 32767));
}

/* ================= bash 4.0 / 4.1 ======================================== */
/* MEASURED, not assumed: in 4.0/4.1 `if (rseed == 0) seedrand();` re-seeds the
 * generator from gettimeofday() ^ getpid().  State 0 IS reachable -- e.g.
 * RANDOM=2147483647 reaches it in ONE step -- so a bash-4.0 $RANDOM stream becomes
 * NON-DETERMINISTIC from that point on and cannot be swept past it.  We emit the
 * deterministic prefix and record its length; we never fabricate the rest. */
static unsigned long rseed_40 = 1;
static int nondet_40 = 0;
static int brand_bash40(void)
{
    long h, l;
    if (rseed_40 == 0) { nondet_40 = 1; return -1; }
    h = rseed_40 / 127773;
    l = rseed_40 % 127773;
    rseed_40 = 16807 * l - 2836 * h;
    return ((unsigned int)(rseed_40 & 32767));
}

/* ================= bash 4.2 / 4.3  (Ubuntu 11.04-12.04) ================== */
static unsigned long rseed_42 = 1;
static int brand_bash42(void)
{
    long h, l;
    if (rseed_42 == 0)
        rseed_42 = 123459876;
    h = rseed_42 / 127773;
    l = rseed_42 % 127773;
    rseed_42 = 16807 * l - 2836 * h;
    return ((unsigned int)(rseed_42 & 32767));
}

/* ================= bash 5.0 ============================================== */
static unsigned int rseed_50 = 1;
static int brand_bash50(void)
{
    int h, l, t;
    if (rseed_50 == 0)
        rseed_50 = 123459876;
    h = rseed_50 / 127773;
    l = rseed_50 - (127773 * h);
    t = 16807 * l - 2836 * h;
    rseed_50 = (t < 0) ? t + 0x7fffffff : t;
    return ((unsigned int)(rseed_50 & 32767));
}

/* ================= bash 5.1 / 5.2 / 5.3 (compat > 50) ==================== */
static unsigned int rseed_51 = 1;
static unsigned int intrand32(unsigned int last)
{
    int h, l, t;
    unsigned int ret;
    ret = (last == 0) ? 123459876 : last;
    h = ret / 127773;
    l = ret - (127773 * h);
    t = 16807 * l - 2836 * h;
    ret = (t < 0) ? t + 0x7fffffff : t;
    return ret;
}
static int brand_bash51(void)
{
    unsigned int ret;
    rseed_51 = intrand32(rseed_51);
    ret = (rseed_51 >> 16) ^ (rseed_51 & 65535);     /* compat level > 50 */
    return (ret & 32767);
}
static int brand_bash51_compat50(void)
{
    unsigned int ret;
    rseed_51 = intrand32(rseed_51);
    ret = rseed_51;                                   /* BASH_COMPAT=5.0 path */
    return (ret & 32767);
}


/* ============ ILP32 transcriptions =======================================
 * gcc-multilib is not installed on this box, so a real `-m32` build is not
 * available.  Instead the same bash source is transcribed with the types an
 * ILP32 compiler would give it: `unsigned long` -> uint32_t, `long` -> int32_t.
 * That is what an ILP32 compiler emits, so these are exact, not approximate --
 * but they are labelled MODELLED in validation.json, because the validating
 * artefact is a re-typed transcription rather than a 32-bit binary. */
#include <stdint.h>

static uint32_t rseed_32i = 1;
static int brand_bash32_i32(void)
{
    rseed_32i = rseed_32i * 1103515245u + 12345u;
    return ((unsigned int)((rseed_32i >> 16) & 32767));
}

static uint32_t rseed_42i = 1;
static int brand_bash42_i32(void)
{
    int32_t h, l;
    if (rseed_42i == 0)
        rseed_42i = 123459876;
    h = rseed_42i / 127773;
    l = rseed_42i % 127773;
    rseed_42i = (uint32_t)(16807 * l - 2836 * h);
    return ((unsigned int)(rseed_42i & 32767));
}

/* ============ the shared $RANDOM wrapper: get_random_number() ============
 * Identical in every version from 3.2 to 5.2:
 *     do   rv = brand ();  while (rv == last_random_value);
 *     last_random_value = rv;
 * i.e. bash's $RANDOM carries its OWN anti-repeat rejection loop, at 15-bit
 * granularity.  sbrand() sets last_random_value = 0, so the FIRST $RANDOM of a
 * freshly-seeded shell can never be 0 either. */
static int run_random(int (*bf)(void), long *out, int n)
{
    int last = 0, rv, i;
    nondet_40 = 0;
    for (i = 0; i < n; i++) {
        do {
            rv = bf();
            if (nondet_40) return i;      /* deterministic prefix ends here */
        } while (rv == last);
        last = rv;
        out[i] = rv;
    }
    return n;
}

static void emit(const char *gen, unsigned long seed, const long *v, int n)
{
    int i;
    printf("{\"gen\":\"%s\",\"seed\":%lu,\"vals\":[", gen, seed);
    for (i = 0; i < n; i++) printf("%s%ld", i ? "," : "", v[i]);
    printf("]}\n");
}

int main(int argc, char **argv)
{
    int a;
    long v[NDRAW];
    unsigned long s;

    emit_abi();
    for (a = 1; a < argc; a++) {
        s = strtoul(argv[a], NULL, 10);   /* exactly what assign_random() does */

        rseed_32 = s; run_random(brand_bash32, v, NDRAW); emit("bash3.2", s, v, NDRAW);
        rseed_40 = s; { int got = run_random(brand_bash40, v, NDRAW); emit("bash4.0", s, v, got); }
        rseed_42 = s; run_random(brand_bash42, v, NDRAW); emit("bash4.2", s, v, NDRAW);
        rseed_50 = (unsigned int)s; run_random(brand_bash50, v, NDRAW); emit("bash5.0", s, v, NDRAW);
        rseed_51 = (unsigned int)s; run_random(brand_bash51, v, NDRAW); emit("bash5.1", s, v, NDRAW);
        rseed_51 = (unsigned int)s; run_random(brand_bash51_compat50, v, NDRAW); emit("bash5.1c50", s, v, NDRAW);
        rseed_32i = (uint32_t)s; run_random(brand_bash32_i32, v, NDRAW); emit("bash3.2_i32", s, v, NDRAW);
        rseed_42i = (uint32_t)s; run_random(brand_bash42_i32, v, NDRAW); emit("bash4.2_i32", s, v, NDRAW);
    }
    return 0;
}
