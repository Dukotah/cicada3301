"""Fresh-eyes audit, part 7: what src/lp/corpus.py parse() actually hands a lane that asks for "unsolved pages".

corpus.parse() reads data/scream314_lp.md. It is the right loader for the SOLVED pages and the wrong
one for LP2: it keeps the first rune block of each section only, its sections are not pages, and until
the fix that accompanies this audit it flagged three unsolved sections as solved (an OutGuess note
was taken for a plaintext). This script maps every section onto the canonical stream. Run it on the
commit before the fix (f63501d) to see the old flags.
"""
import os
import sys

import lp2

sys.path.insert(0, os.path.join(lp2.LP, "src"))
from lp import corpus, gematria as gp  # noqa: E402

PI = lp2.idx(lp2.unsolved()); U = [x for p in PI for x in p]
starts = [0]
for p in PI:
    starts.append(starts[-1] + len(p))


def locate(ix):
    n = len(ix)
    for i in range(len(U) - n + 1):
        if U[i:i + n] == ix:
            a = max(k for k in range(55) if starts[k] <= i); b = max(k for k in range(55) if starts[k] <= i + n - 1)
            return f"flat {i}..{i + n - 1} = p{a}+{i - starts[a]} .. p{b}+{i + n - 1 - starts[b]}"
    return "not a contiguous slice of the canonical unsolved stream"


kept = unsolved = 0
for i, pg in enumerate(corpus.parse()):
    ix = gp.runes_to_indices(pg.get("runes") or "")
    if not ix:
        continue
    kept += len(ix)
    flag = "solved  " if pg.get("plaintext") else "UNSOLVED"
    unsolved += len(ix) if not pg.get("plaintext") else 0
    print(f"{i:2d} {pg['label'][:30]:30s} n={len(ix):4d} {flag} {locate(ix) if len(ix) >= 20 else ''}")
total = sum(1 for ch in open(corpus.DATA, encoding="utf-8").read() if ch in gp.RUNE_TO_IDX)
print(f"runes in scream314_lp.md: {total}; kept by parse(): {kept}; flagged unsolved: {unsolved} of the canonical 12956")
