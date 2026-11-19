"""p15 4x4 grid closed form (njloof, Dukotah/cicada3301#14, 2026-11-19), reproduced here.

Every cell is |3301 - prime(F+1)| for a distinct Fibonacci F in {0,1,2,3,5,...,987},
and F advances along a square spiral that starts at the red 3299 cell (r1,c1, 0-based).
The two cells R44 P2 counted as breakers (4516, 1206) are the sign flips prime > 3301.

    python closed_form_check.py      # exits 0 and prints PASS if both claims hold
"""

GRID = [  # row-major, R44-P2-P15GRID-TRANSCRIPTION
    [3258, 3222, 3152, 3038],
    [3278, 3299, 3298, 2838],
    [3288, 3294, 3296, 2472],
    [4516, 1206, 708, 1820],
]
FIBS = [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
SPIRAL = [(1, 1), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0), (0, 0), (0, 1),
          (0, 2), (0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (3, 0)]


def primes(n):
    sieve = bytearray([1]) * n
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n) if sieve[i]]


def main():
    p = primes(10000)  # p[F] = prime(F+1)
    value = {f: abs(3301 - p[f]) for f in FIBS}
    cells = sorted(v for row in GRID for v in row)
    assert sorted(value.values()) == cells, "closed form does not cover all 16 cells"
    along_spiral = [GRID[r][c] for r, c in SPIRAL]
    assert along_spiral == [value[f] for f in FIBS], "spiral order does not follow F"
    flips = [value[f] for f in FIBS if p[f] > 3301]
    assert sorted(flips) == [1206, 4516]
    print("PASS: 16/16 cells = |3301 - prime(F+1)|, F Fibonacci 0..987 along the spiral "
          "from red 3299; sign flips at", sorted(flips))


if __name__ == "__main__":
    main()
