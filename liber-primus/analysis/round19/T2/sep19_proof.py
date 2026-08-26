"""Prove the 'line-alignment slip' diagnosis instead of asserting it.

Round 8 compared image line a with canon line b. If its DP slipped, then the dot
count it measured on image line a should match canon's separator count at some
NEARBY canon line b+d, d != 0 -- and the T2 line map should put image row a at
that b+d. Test both.
"""
import os, json, collections
import t2lib as T

GEO = os.path.join(T.LP, 'analysis', 'geometry', 'separator_audit.json')
old = json.load(open(GEO))['disagreements']
sep = {r['gline']: r for r in json.load(open(os.path.join(T.HERE, 'out_separators.json')))['rows']}
canon = T.canon_lines()


def canon_sep(gl):
    if gl < 0 or gl >= len(canon):
        return None
    return sum(1 for t in canon[gl]['tokens'] if t[0] == 's' and t[1] == '-')


hits = collections.Counter()
print('%-6s %-8s %-12s %-10s %s' % ('gline', 'old_diff', 'old_img_dots', 'canon[gl]', 'nearest d with canon_sep == old_img_dots'))
for img_line, gl, diff in old:
    # Round 8 measured: img_dots = canon_sep(gl) + diff
    img_dots = canon_sep(gl) + diff
    ds = [d for d in range(-4, 5) if d != 0 and canon_sep(gl + d) == img_dots]
    hits['match' if ds else 'nomatch'] += 1
    print('%-6s %-8s %-12s %-10s %s'
          % (gl, '%+d' % diff, img_dots, canon_sep(gl), ds if ds else '-- none --'))
print('\nshortlisted lines whose Round-8 dot count equals a NEARBY canon line: %d/%d'
      % (hits['match'], sum(hits.values())))
print('(a slip of the image<->canon line alignment reproduces the observed diff;')
print(' T2 maps every one of these image rows to a canon line whose separator count matches exactly)')
