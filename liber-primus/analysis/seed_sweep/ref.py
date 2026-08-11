"""Independent reference keystreams — validates the C generators in sweep.c.

Prints the first 12 keystream values for the Python and Java generator variants
at the same seeds sweep.c's `selftest` uses, so the C implementations can be
checked against the real CPython `random` module and against Java's documented
LCG spec. A generator that does not reproduce these is not a valid null.
"""
import random

SEEDS = {7: 1399000000 + 7 * 7919, 8: 1399000000 + 8 * 7919,
         9: 1399000000 + 9 * 7919, 5: 1399000000 + 5 * 7919}

random.seed(SEEDS[7])
print("gen7 py3 randrange(29)   :", [random.randrange(29) for _ in range(12)])

random.seed(SEEDS[8])
print("gen8 py3 int(random()*29):", [int(random.random() * 29) for _ in range(12)])


class Java:
    """java.util.Random, per the Javadoc-specified LCG."""

    def __init__(self, seed):
        self.s = (seed ^ 0x5DEECE66D) & ((1 << 48) - 1)

    def next(self, bits):
        self.s = (self.s * 0x5DEECE66D + 0xB) & ((1 << 48) - 1)
        return self.s >> (48 - bits)

    def nextInt(self, bound):
        r = self.next(31)
        m = bound - 1
        u = r
        r = u % bound
        while u - r + m >= (1 << 31):       # signed-overflow retry condition
            u = self.next(31)
            r = u % bound
        return r


j = Java(SEEDS[9])
print("gen9 java nextInt(29)    :", [j.nextInt(29) for _ in range(12)])


def mt_init_genrand(seed):
    mt = [0] * 624
    mt[0] = seed
    for i in range(1, 624):
        mt[i] = (1812433253 * (mt[i-1] ^ (mt[i-1] >> 30)) + i) & 0xffffffff
    return mt


def mt_stream(mt):
    idx = 624
    while True:
        if idx >= 624:
            for i in range(624):
                y = (mt[i] & 0x80000000) | (mt[(i+1) % 624] & 0x7fffffff)
                n = mt[(i + 397) % 624] ^ (y >> 1)
                if y & 1:
                    n ^= 0x9908b0df
                mt[i] = n
            idx = 0
        y = mt[idx]; idx += 1
        y ^= y >> 11
        y ^= (y << 7) & 0x9d2c5680
        y ^= (y << 15) & 0xefc60000
        y ^= y >> 18
        yield y & 0xffffffff


g = mt_stream(mt_init_genrand(SEEDS[5]))
print("gen5 mt19937 %29         :", [next(g) % 29 for _ in range(12)])
