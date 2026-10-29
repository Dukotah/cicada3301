"""Vectorised bash-4.2 $RANDOM keystream head + IoC prefilter (numpy, streaming)."""
import numpy as np
M32 = np.uint64(0xFFFFFFFF)
def heads(seeds, m, variant):
    """First m $RANDOM values (mod 29) for each seed, seeds uint64 array. anti-repeat approximated:
    consecutive-equal raw values (p~3e-5/draw) are NOT collapsed here; exact generator is used downstream."""
    s = seeds.astype(np.uint64)
    if variant == "bash4.2_i32":
        s = s & M32
    out = np.empty((m, len(s)), dtype=np.int8)
    for t in range(m):
        z = s == 0
        if z.any(): s = np.where(z, np.uint64(123459876), s)
        h = s // np.uint64(127773); l = s - h * np.uint64(127773)
        s = np.uint64(16807) * l - np.uint64(2836) * h      # uint64 wraps == C unsigned long (LP64)
        if variant == "bash4.2_i32": s = s & M32
        out[t] = (s & np.uint64(32767)) % np.uint64(29)
    return out
def ioc_stat(P):
    """P: (m, B) int8 -> number of equal pairs per column (coincidence count)."""
    m, B = P.shape
    tot = np.zeros(B, dtype=np.int16)
    for a in range(m - 1):
        for b in range(a + 1, m):
            tot += (P[a] == P[b])
    return tot

def tri_stat(P, LMT, mu=None, sd=None):
    """P (m,B) int8 plaintext idx -> (B,R) summed trigram log10 score, optionally z-normalised per register."""
    m, B = P.shape
    P = P.astype(np.int32)
    acc = np.zeros((B, LMT.shape[1]), dtype=np.float32)
    for t in range(m - 2):
        acc += LMT[P[t] * 841 + P[t + 1] * 29 + P[t + 2]]
    if mu is not None:
        acc = (acc - mu) / sd
    return acc
