"""What is the recurring ink that produces the identical indel deltas?"""
import os, json, collections
import t2lib as T
from lp.gematria import IDX_TO_TRANS

adj = json.load(open(os.path.join(T.HERE, 'out_indel_adj.json')))
res = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_probe.json')))
       if 'fail' not in r}
canon = T.canon_lines()
byd = collections.defaultdict(list)
for a in adj:
    byd[a['delta']].append(a)

print('recurring delta values and the canon runes flanking the flagged position:')
ctx = collections.Counter()
for delta in sorted(byd, key=lambda d: -len(byd[d])):
    grp = byd[delta]
    rr = []
    for a in grp:
        r = res[a['gline']]
        p = a['pos']
        left = IDX_TO_TRANS[r['canon'][p - 1]] if p - 1 >= 0 else '^'
        here = IDX_TO_TRANS[r['canon'][p]] if p < len(r['canon']) else '$'
        rr.append('%s|%s' % (left, here))
        ctx[(left, here)] += 1
    print('  delta %-9s n=%d   %s' % (delta, len(grp), rr))
print('\nmost common (left, at) rune context over all 26 flags:')
for k, v in ctx.most_common(10):
    print('   %-4s %-4s  %d' % (k[0], k[1], v))
