"""Round 19 / G1 -- reduction of a raw generator draw stream to Z29, plus the
seed-derivation cross-product, following the conventions of
`liber-primus/analysis/round13/B04/PREREG.md` sections 3.3-3.5 so that G1's rows are
directly comparable with B-04's, R16-PRNG's and R17's.

A generator in this lane exposes ONE thing:

    raws(seed, n) -> iterator of non-negative ints, each in [0, rmax]

`reduce_stream()` turns that into a Z29 keystream.  `variants()` enumerates the
(reduction, sign, direction, atbash, offset) cross that the sweep must run.

NOTHING HERE SCORES ANYTHING.  Phase 0 (I1/I2/I3) owns scoring; this module stops
at "here is a list of ints in 0..28".
"""

N = 29

# --------------------------------------------------------------------- reductions
# Each reduction is (name, fn) where fn(raw_iter, rmax, n) -> list[int] of length n.
# `rmax` is the generator's inclusive maximum draw, needed for the unbiased and the
# scaled forms.


def _mod29(it, rmax, n):
    out = []
    for x in it:
        out.append(x % N)
        if len(out) == n:
            return out
    return out


def _rej29(it, rmax, n):
    """Unbiased rejection sampling -- the form a careful author writes.
    Keep only draws < floor((rmax+1)/29)*29, then % 29."""
    lim = ((rmax + 1) // N) * N
    out = []
    for x in it:
        if x >= lim:
            continue
        out.append(x % N)
        if len(out) == n:
            return out
    return out


def _scale29(it, rmax, n):
    """`x * 29 / (rmax+1)` -- the `$((RANDOM * 29 / 32768))` / `int(drand48()*29)` idiom."""
    m = rmax + 1
    out = []
    for x in it:
        out.append((x * N) // m)
        if len(out) == n:
            return out
    return out


def _hi_nib(it, rmax, n):
    out = []
    for x in it:
        out.append(((x >> 4) & 0xFF) % N)
        if len(out) == n:
            return out
    return out


def _lo_byte(it, rmax, n):
    """Low byte % 29 -- what you get if the stream is consumed a byte at a time."""
    out = []
    for x in it:
        out.append((x & 0xFF) % N)
        if len(out) == n:
            return out
    return out


def _bits5(it, rmax, n):
    """5 bits at a time off the low end of each draw, rejecting 29..31.
    (Matches B-04's `bits5` in intent; here the bit source is the draw's low bits.)"""
    out = []
    nb = max(1, (rmax.bit_length() // 5))
    for x in it:
        for k in range(nb):
            v = (x >> (5 * k)) & 31
            if v >= N:
                continue
            out.append(v)
            if len(out) == n:
                return out
    return out


REDUCTIONS = [
    ("mod29", _mod29),
    ("rej29", _rej29),
    ("scale29", _scale29),
    ("hi_nib", _hi_nib),
    ("lo_byte", _lo_byte),
    ("bits5", _bits5),
]
REDUCTIONS_CORE = ["mod29", "rej29", "scale29"]
_RED = dict(REDUCTIONS)


def reduce_stream(raw_iter, rmax, n, reduction="mod29"):
    return _RED[reduction](raw_iter, rmax, n)


# ------------------------------------------------- the seed-derivation cross-product
# B-04 section 3.4 / 3.5, unchanged so results stay comparable.
SIGNS = (-1, +1)                 # key subtracted / key added, decode p = (c + sign*k) % 29
DIRECTIONS = ("fwd", "rev")      # keystream consumed forward / reversed
ATBASH = (False, True)           # plaintext-alphabet reflection i -> 28 - i
OFFSETS_STAGE_A = (0,)
OFFSETS_STAGE_B = (1, 4, 16, 29, 64, 128, 256, 512, 1024, 3301)


def apply_atbash(ks):
    return [(N - 1 - k) % N for k in ks]


def orient(ks, direction="fwd", atbash=False):
    out = list(ks)
    if direction == "rev":
        out = out[::-1]
    if atbash:
        out = apply_atbash(out)
    return out


def variants(stage="A"):
    """Yield dicts describing every (reduction, sign, direction, atbash, offset) cell."""
    offs = OFFSETS_STAGE_A if stage == "A" else OFFSETS_STAGE_B
    reds = [r for r, _ in REDUCTIONS] if stage == "A" else REDUCTIONS_CORE
    for red in reds:
        for sign in SIGNS:
            for direction in DIRECTIONS:
                for atb in ATBASH:
                    for off in offs:
                        yield {"reduction": red, "sign": sign, "direction": direction,
                               "atbash": atb, "offset": off}


def variant_count(stage="A"):
    return sum(1 for _ in variants(stage))
