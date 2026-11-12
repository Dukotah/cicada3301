"""Fresh-eyes audit, part 6: the page-15 4x4 number grid is fully determined by one rule.

Round 43 X0 and the Round 44 plan (lane P2) describe it as "14/16 cells = 3301 - prime" with free
information left over. All sixteen cells equal |3301 - p_F|, where p_0 = 2, p_1 = 3, ... and F runs
over the Fibonacci numbers 0, 1, 2, 3, 5, 8, ..., 987. The grid carries no free numbers.
"""
GRID = [3258, 3222, 3152, 3038, 3278, 3299, 3298, 2838, 3288, 3294, 3296, 2472, 4516, 1206, 708, 1820]


def primes(n):
    s = bytearray([1]) * (n + 1); s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


P = primes(9000)
F = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
pred = [abs(3301 - P[f]) for f in F]
assert sorted(pred) == sorted(GRID)
print("Fibonacci index F :", F)
print("prime p_F (p_0=2)  :", [P[f] for f in F])
print("|3301 - p_F|       :", pred)
print("all 16 grid cells explained:", sorted(pred) == sorted(GRID))
