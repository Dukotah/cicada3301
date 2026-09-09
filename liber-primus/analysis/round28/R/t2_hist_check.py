#!/usr/bin/env python3
"""R28-R T2: recompute S1-CLOSEOUT histogram claims from a COPY of hist_S1.u64.

Checks (against S1-CLOSEOUT.md sections 1 and 4):
  C1  sum over all 6x2600 u64 bins == 2**32 exactly
  C2  tail >= 5.00 (bins 500..2599) == 392,131
  C3  tail-vs-Gumbel ratio: 392,131 / (6.95e-5 * 2**32) ~= 1.31x, inside [0.2x, 5x]
  C4  tail >= 7.39 (bins 739..2599) == 3
Usage: t2_hist_check.py <hist.u64> [--expect-corrupt]
Exit 0 = all pass; exit 1 = FOUND-ERROR (any mismatch).
"""
import struct, sys

HIST_BINS = 2600
NW = 6
BIN_W = 0.01

path = sys.argv[1]
raw = open(path, 'rb').read()
assert len(raw) == NW * HIST_BINS * 8, f"size {len(raw)} != {NW*HIST_BINS*8}"
bins = struct.unpack('<%dQ' % (NW * HIST_BINS), raw)
# aggregate over workers
agg = [0] * HIST_BINS
for w in range(NW):
    for b in range(HIST_BINS):
        agg[b] += bins[w * HIST_BINS + b]

total = sum(agg)
tail500 = sum(agg[500:])          # pmax >= 5.00
tail739 = sum(agg[739:])          # pmax >= 7.39
gumbel_pred = 6.95e-5 * 2**32
ratio = tail500 / gumbel_pred

ok = True
def chk(name, cond, detail):
    global ok
    print(('PASS' if cond else 'FAIL'), name, '--', detail)
    if not cond:
        ok = False

chk('C1 total==2^32', total == 2**32, f'total={total} vs {2**32} (diff {total-2**32})')
chk('C2 tail>=5.0 == 392131', tail500 == 392131, f'tail500={tail500}')
chk('C3 Gumbel ratio ~1.31x in [0.2,5]',
    0.2 <= ratio <= 5.0 and abs(ratio - 1.31) < 0.01,
    f'pred={gumbel_pred:.0f} ratio={ratio:.4f}')
chk('C4 tail>=7.39 == 3', tail739 == 3, f'tail739={tail739}')

# where do the 3 crossers land: report the occupied bins >= 739
occ = [(b, agg[b]) for b in range(739, HIST_BINS) if agg[b]]
print('occupied bins >=7.39:', [(f'{b*BIN_W:.2f}-{(b+1)*BIN_W:.2f}', c) for b, c in occ])
print('VERDICT:', 'NO-ERROR-FOUND (histogram)' if ok else 'FOUND-ERROR')
sys.exit(0 if ok else 1)
