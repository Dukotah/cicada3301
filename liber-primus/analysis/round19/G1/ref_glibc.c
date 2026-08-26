/* Round 19 / G1 -- REAL-LIBRARY REFERENCE for the glibc generator family.
 *
 * This program calls the actual system libc.  Nothing here re-implements anything;
 * its whole job is to emit ground truth that gen_glibc.py must reproduce exactly.
 *
 * Emits JSON lines:  {"gen":"random","seed":S,"vals":[...]}
 *
 * Build:  gcc -O2 -o ref_glibc ref_glibc.c
 * Run:    ./ref_glibc 0 1 2 3301 12345 2147483647 4294967295 1376006400
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NDRAW 2000

static void emit(const char *gen, unsigned long seed, const long *v, int n)
{
    int i;
    printf("{\"gen\":\"%s\",\"seed\":%lu,\"vals\":[", gen, seed);
    for (i = 0; i < n; i++) printf("%s%ld", i ? "," : "", v[i]);
    printf("]}\n");
}

int main(int argc, char **argv)
{
    int a, i;
    long v[NDRAW];
    unsigned long s;

    for (a = 1; a < argc; a++) {
        s = strtoul(argv[a], NULL, 0);

        /* --- random() : glibc TYPE_3 additive feedback (the default) --- */
        srandom((unsigned int)s);
        for (i = 0; i < NDRAW; i++) v[i] = random();
        emit("random", s, v, NDRAW);

        /* --- rand() : on glibc this is the same TYPE_3 generator --- */
        srand((unsigned int)s);
        for (i = 0; i < NDRAW; i++) v[i] = rand();
        emit("rand", s, v, NDRAW);

        /* --- lrand48() : 48-bit LCG, high 31 bits --- */
        srand48((long)s);
        for (i = 0; i < NDRAW; i++) v[i] = lrand48();
        emit("lrand48", s, v, NDRAW);

        /* --- mrand48() : signed 32 bits of the same 48-bit LCG --- */
        srand48((long)s);
        for (i = 0; i < NDRAW; i++) v[i] = mrand48();
        emit("mrand48", s, v, NDRAW);

        /* --- drand48() : the double.  Emitted as its exact 53-bit mantissa
         *     integer  floor(x * 2^53)  so the comparison is exact, not fp-fuzzy. */
        srand48((long)s);
        for (i = 0; i < NDRAW; i++) {
            double d = drand48();
            v[i] = (long)(d * 9007199254740992.0);   /* 2^53 */
        }
        emit("drand48_x2p53", s, v, NDRAW);

        /* --- random_r() with the 8/32/64/128/256-byte state sizes ------------
         *     TYPE_0..TYPE_4.  A 2012 C author who called initstate() with a
         *     non-default buffer gets a different stream.  Only the default
         *     (128 B / TYPE_3) is what srandom() gives, but the others are one
         *     line of code away and cost nothing to cover. */
        {
            static const int sizes[5] = {8, 32, 64, 128, 256};
            static const char *nm[5] = {"initstate8","initstate32","initstate64",
                                        "initstate128","initstate256"};
            int k;
            for (k = 0; k < 5; k++) {
                char buf[256];
                char *old;
                memset(buf, 0, sizeof buf);
                old = initstate((unsigned int)s, buf, (size_t)sizes[k]);
                for (i = 0; i < NDRAW; i++) v[i] = random();
                setstate(old);
                emit(nm[k], s, v, NDRAW);
            }
        }
    }
    return 0;
}
