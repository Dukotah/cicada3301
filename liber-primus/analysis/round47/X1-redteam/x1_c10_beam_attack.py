"""R47-X1: a cheap C10 submission (attack under shuffled printed lengths).
Beam search over within-sentence orderings of the printed length multiset, scored by the repo's English
quadgram table (lp.score). Uses only (C, K, printed) - nothing the checker withholds.
    python challenges/c10_shuffled_lengths.py liber-primus/analysis/round47/X1-redteam/x1_c10_beam_attack.py --n 50 --seed 4702
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "challenges"))
import _heavy as H  # noqa: E402
import skipdecode as sk  # noqa: E402
from lp import gematria as gp  # noqa: E402

N = H.N
S = [gp.PRIMES[j % 29] for j in range(4096)]
Q = H.Q
TR = [gp.IDX_TO_TRANS[i] for i in range(N)]
BEAM = int(os.environ.get("X1_BEAM", "64"))


def _add(tail, s, new):
    t = tail + new
    for i in range(max(0, len(tail) - 3), len(t) - 3):
        s += Q.d.get(t[i:i + 4], Q.floor)
    return t[-3:], s


def attack(C, K, printed):
    """Position-synchronous beam: states are bucketed by rune position so only equal-length prefixes compete."""
    n = len(C)
    ends = []
    acc = 0
    for s in printed:
        acc += sum(s)
        ends.append(acc)
    buckets = {0: [(0.0, 0, 0, tuple(sorted(printed[0])), 0, "", ())]}
    for pos in range(n + 1):
        b = buckets.pop(pos, None)
        if not b:
            continue
        b.sort(key=lambda x: -x[0])
        seen, keep = set(), []
        for st in b:
            key = (st[3], st[4], st[5])
            if key in seen:
                continue
            seen.add(key)
            keep.append(st)
            if len(keep) >= BEAM:
                break
        if pos == n:
            return list(keep[0][6])
        for sc, J, k, rem, si, tail, out in keep:
            if not rem:
                si += 1
                rem = tuple(sorted(printed[si]))
            Jk = J + S[k]
            for l in sorted(set(rem)):
                r = list(rem); r.remove(l)
                dec = tuple((C[pos + i] - K[pos + i + Jk]) % N for i in range(l))
                t2, s2 = _add(tail, sc, "".join(TR[x] for x in dec))
                buckets.setdefault(pos + l, []).append((s2, Jk, k + 1, tuple(r), si, t2, out + dec))
    raise RuntimeError("no complete parse")
