/* Round 28 / L4 -- glibc rand()/random() reference-vector emitter.
 *
 * Links against the REAL resident glibc (the R18-L1 measured authoring
 * environment's libc family) and emits, per seed:
 *   random_raw : srandom(seed); random() x n           (TYPE_3 additive, 31-bit)
 *   rand_raw   : srand(seed);   rand()   x n           (glibc: rand == random)
 *   mod29      : random_raw % 29                        (the gen=0 reduction)
 * The rand-vs-random comparison is emitted so the PREREG's "glibc rand()" cell
 * can be collapsed (or not) on MEASURED identity, not on lore.
 *
 * usage: ./ref_glibc "<seed seed ...>" <ndraws>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    if (argc != 3) { fprintf(stderr, "usage: %s \"<seeds>\" <n>\n", argv[0]); return 1; }
    int n = atoi(argv[2]);
    long *a = malloc(sizeof(long) * n), *b = malloc(sizeof(long) * n);
    printf("{\"libc\": \"glibc\", \"seeds\": [\n");
    char *tok = strtok(argv[1], " ");
    int first = 1;
    while (tok) {
        unsigned long seed = strtoul(tok, NULL, 10);
        srandom((unsigned)seed);
        for (int i = 0; i < n; i++) a[i] = random();
        srand((unsigned)seed);
        for (int i = 0; i < n; i++) b[i] = rand();
        int same = !memcmp(a, b, sizeof(long) * n);
        printf("%s{\"seed\": %lu, \"rand_equals_random\": %s,\n \"random_raw\": [",
               first ? "" : ",\n", seed, same ? "true" : "false");
        for (int i = 0; i < n; i++) printf("%s%ld", i ? "," : "", a[i]);
        printf("],\n \"mod29\": [");
        for (int i = 0; i < n; i++) printf("%s%ld", i ? "," : "", a[i] % 29);
        printf("]}");
        first = 0;
        tok = strtok(NULL, " ");
    }
    printf("\n]}\n");
    free(a); free(b);
    return 0;
}
