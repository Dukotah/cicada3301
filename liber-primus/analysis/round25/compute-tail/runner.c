#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define N 624
#define M 397
#define MATRIX_A 0x9908b0dfUL
#define UPPER_MASK 0x80000000UL
#define LOWER_MASK 0x7fffffffUL

typedef struct {
    uint32_t mt[N];
    int mti;
} mt19937_state;

void init_genrand(mt19937_state *state, uint32_t s) {
    state->mt[0] = s & 0xffffffffUL;
    for (state->mti = 1; state->mti < N; state->mti++) {
        state->mt[state->mti] = (1812433253UL * (state->mt[state->mti - 1] ^ (state->mt[state->mti - 1] >> 30)) + state->mti);
        state->mt[state->mti] &= 0xffffffffUL;
    }
}

void init_by_array(mt19937_state *state, uint32_t init_key[], int key_length) {
    int i, j, k;
    init_genrand(state, 19650218UL);
    i = 1; j = 0;
    k = (N > key_length ? N : key_length);
    for (; k; k--) {
        state->mt[i] = (state->mt[i] ^ ((state->mt[i - 1] ^ (state->mt[i - 1] >> 30)) * 1664525UL)) + init_key[j] + j;
        state->mt[i] &= 0xffffffffUL;
        i++; j++;
        if (i >= N) { state->mt[0] = state->mt[N - 1]; i = 1; }
        if (j >= key_length) j = 0;
    }
    for (k = N - 1; k; k--) {
        state->mt[i] = (state->mt[i] ^ ((state->mt[i - 1] ^ (state->mt[i - 1] >> 30)) * 1566083941UL)) - i;
        state->mt[i] &= 0xffffffffUL;
        i++;
        if (i >= N) { state->mt[0] = state->mt[N - 1]; i = 1; }
    }
    state->mt[0] = 0x80000000UL;
}

uint32_t genrand_uint32(mt19937_state *state) {
    uint32_t y;
    static uint32_t mag01[2] = {0x0UL, MATRIX_A};
    if (state->mti >= N) {
        int kk;
        for (kk = 0; kk < N - M; kk++) {
            y = (state->mt[kk] & UPPER_MASK) | (state->mt[kk + 1] & LOWER_MASK);
            state->mt[kk] = state->mt[kk + M] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        for (; kk < N - 1; kk++) {
            y = (state->mt[kk] & UPPER_MASK) | (state->mt[kk + 1] & LOWER_MASK);
            state->mt[kk] = state->mt[kk + (M - N)] ^ (y >> 1) ^ mag01[y & 0x1UL];
        }
        y = (state->mt[N - 1] & UPPER_MASK) | (state->mt[0] & LOWER_MASK);
        state->mt[N - 1] = state->mt[M - 1] ^ (y >> 1) ^ mag01[y & 0x1UL];
        state->mti = 0;
    }
    y = state->mt[state->mti++];
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680UL;
    y ^= (y << 15) & 0xefc60000UL;
    y ^= (y >> 18);
    return y;
}

double py27_random(mt19937_state *state) {
    uint32_t a = genrand_uint32(state) >> 5;
    uint32_t b = genrand_uint32(state) >> 6;
    return (a * 67108864.0 + b) * (1.0 / 9007199254740992.0);
}

void get_keystream_random29(uint32_t seed, int n, int *out) {
    mt19937_state state;
    uint32_t init_key[1];
    init_key[0] = seed ? seed : 0;
    init_by_array(&state, init_key, 1);
    for (int i = 0; i < n; i++) {
        out[i] = (int)(py27_random(&state) * 29);
    }
}

// ---------------------------------------------------- Beam Decode

const char *TRANS[29] = {
    "F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO", "P", 
    "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE", "Y", "IA", "EA"
};

float qgrams[26*26*26*26];
float floor_val;

void init_qgrams() {
    FILE *f = fopen("../../../data/english_quadgrams.txt", "r");
    if (!f) {
        fprintf(stderr, "Cannot open english_quadgrams.txt\n");
        exit(1);
    }
    char buf[256];
    long long total = 0;
    int counts[26*26*26*26] = {0};
    while (fgets(buf, sizeof(buf), f)) {
        char q[5];
        int c;
        if (sscanf(buf, "%4s %d", q, &c) == 2) {
            int idx = (q[0]-'A')*26*26*26 + (q[1]-'A')*26*26 + (q[2]-'A')*26 + (q[3]-'A');
            counts[idx] = c;
            total += c;
        }
    }
    fclose(f);
    double log_tot = log10((double)total);
    floor_val = log10(0.01) - log_tot;
    for (int i=0; i<26*26*26*26; i++) {
        if (counts[i] > 0) {
            qgrams[i] = log10((double)counts[i]) - log_tot;
        } else {
            qgrams[i] = floor_val;
        }
    }
}

static inline float get_qgram(const char *q) {
    int i0 = q[0]-'A', i1 = q[1]-'A', i2 = q[2]-'A', i3 = q[3]-'A';
    if (i0<0 || i0>25 || i1<0 || i1>25 || i2<0 || i2>25 || i3<0 || i3>25) return floor_val;
    return qgrams[i0*26*26*26 + i1*26*26 + i2*26 + i3];
}

typedef struct {
    float sc;
    int acc;
    int nchars;
    char buf[256];
} BeamNode;

int compare_beams(const void *a, const void *b) {
    float sa = ((BeamNode*)a)->sc;
    float sb = ((BeamNode*)b)->sc;
    if (sa < sb) return 1;
    if (sa > sb) return -1;
    return 0;
}

float fast_beam(int *C, int L, int *K, int lenK, int beam_w, int max_skip) {
    BeamNode beams[beam_w];
    BeamNode nxt[beam_w * (max_skip/2 + 1)];
    int n_beams = 1;
    
    int p = (C[0] - K[0]) % 29;
    if (p < 0) p += 29;
    beams[0].sc = 0.0f;
    beams[0].acc = 0;
    beams[0].nchars = strlen(TRANS[p]);
    strcpy(beams[0].buf, TRANS[p]);

    for (int i = 1; i < L; i++) {
        int ci = C[i];
        int c_prev = C[i-1];
        int nxt_count = 0;
        for (int b = 0; b < n_beams; b++) {
            int base = beams[b].acc + 1;
            for(int dsk = 0; dsk <= max_skip; dsk += 2) {
                int acc2 = base + dsk;
                if (acc2 >= lenK) break;
                int kacc = K[acc2];
                if (dsk > 0) {
                    int v = (kacc - ci + c_prev) % 29;
                    if (v < 0) v += 29;
                    int valid = 1;
                    for (int j = base; j < acc2; j += 2) {
                        if (K[j] != v) { valid = 0; break; }
                    }
                    if (!valid) continue;
                }
                int p = (ci - kacc) % 29;
                if (p < 0) p += 29;
                const char *t = TRANS[p];
                int la = strlen(t);
                
                BeamNode new_node;
                new_node.acc = acc2;
                new_node.nchars = beams[b].nchars + la;
                memcpy(new_node.buf, beams[b].buf, beams[b].nchars);
                memcpy(new_node.buf + beams[b].nchars, t, la);
                new_node.buf[new_node.nchars] = '\0';
                
                float tot = 0.0f;
                if (beams[b].nchars < 3) {
                    for (int e = 4; e <= new_node.nchars; e++) {
                        tot += get_qgram(new_node.buf + e - 4);
                    }
                } else {
                    if (la == 1) {
                        tot += get_qgram(new_node.buf + new_node.nchars - 4);
                    } else if (la == 2) {
                        tot += get_qgram(new_node.buf + new_node.nchars - 5);
                        tot += get_qgram(new_node.buf + new_node.nchars - 4);
                    }
                }
                new_node.sc = beams[b].sc + tot;
                nxt[nxt_count++] = new_node;
            }
        }
        if (nxt_count == 0) return -999.0f;
        qsort(nxt, nxt_count, sizeof(BeamNode), compare_beams);
        n_beams = nxt_count < beam_w ? nxt_count : beam_w;
        for (int b=0; b<n_beams; b++) beams[b] = nxt[b];
    }
    return beams[0].sc / (beams[0].nchars - 3);
}

int C_SCREEN[] = {15, 8, 18, 3, 6, 19, 27, 0, 15, 26, 18, 21, 5, 2, 11, 6, 25, 0, 11, 22, 3, 9, 2, 9, 18, 7, 17, 24, 15, 22, 12, 10, 21, 1, 9, 25, 6, 10, 2, 8, 17, 9, 27, 13, 17, 9, 12, 11, 2, 24, 21, 26, 14, 17, 23, 13, 18, 27, 0, 14, 6, 0, 15, 13, 16, 0, 13, 1, 21, 26, 21, 14, 27, 26, 8, 17, 1, 6, 3, 13, 21, 25, 2, 10, 25, 8, 14, 2, 13, 6, 26, 0, 21, 5, 11, 2, 24, 19, 10, 21, 10, 27, 26, 8, 12, 16, 8, 25, 27, 14, 26, 18, 1, 21, 5, 0, 9, 12, 2, 11};
int L_SCREEN = 120;
int SCREEN_BEAM_W = 64;
int MAX_SKIP = 8;
int LEN_K = 120 * 6 + 64; // 784
float BAR = -5.8f;

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <start_seed> <end_seed>\n", argv[0]);
        return 1;
    }
    uint32_t start = strtoul(argv[1], NULL, 10);
    uint32_t end = strtoul(argv[2], NULL, 10);
    
    init_qgrams();
    
    // Always check the planted positive control (seed 777)
    int K_test[784];
    get_keystream_random29(777, LEN_K, K_test);
    float sc_test = fast_beam(C_SCREEN, L_SCREEN, K_test, LEN_K, SCREEN_BEAM_W, MAX_SKIP);
    if (sc_test < -6.97f) {
        fprintf(stderr, "Self-test failed! Seed 777 score is %f\n", sc_test);
        return 1;
    }

    uint32_t best_seed = 0;
    float best_sc = -999.0f;

    #pragma omp parallel
    {
        int K[784];
        #pragma omp for
        for (uint32_t seed = start; seed < end; seed++) {
            get_keystream_random29(seed, LEN_K, K);
            float sc = fast_beam(C_SCREEN, L_SCREEN, K, LEN_K, SCREEN_BEAM_W, MAX_SKIP);
            
            #pragma omp critical
            {
                if (sc > best_sc) {
                    best_sc = sc;
                    best_seed = seed;
                }
                if (sc >= BAR) {
                    printf("%u %f\n", seed, sc);
                    fflush(stdout);
                }
            }
        }
    }
    
    fprintf(stderr, "Sweep %u..%u done. Best: %u (score %f)\n", start, end, best_seed, best_sc);
    return 0;
}
