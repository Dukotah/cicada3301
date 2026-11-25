"""R46-A1 (a): repair analysis/stones/alignment.json from R45-S1 corrected_map.json under PREREG §3 rules R-a1..R-a4.
Copies the original to alignment.v1.json (once; never overwritten), writes the repaired alignment.json (same schema:
"0".."55" -> [canon gline per clean line, positional]) and alignment_diff.json here. Needs no images: the per-line
box counts come from corrected_map.json (S1's segmentation pass). Stdlib only."""
import json, os, shutil, sys, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__)); LP = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
STONES = os.path.join(LP, 'analysis', 'stones')
V1 = os.path.join(STONES, 'alignment.v1.json'); CUR = os.path.join(STONES, 'alignment.json')
CMAP = os.path.join(LP, 'analysis', 'round45', 'S1-transcription', 'corrected_map.json')
sys.path.insert(0, STONES)


def canon_lines():
    # same object as pipeline.global_lines() without importing numpy/PIL
    import pipeline as P
    return P.global_lines()


if not os.path.exists(V1):
    shutil.copyfile(CUR, V1)
v1 = json.load(open(V1)); cm = json.load(open(CMAP)); gl, po = canon_lines()
v2, rows = {}, []
for n in range(56):
    k = str(n); al = v1[k]; out = []
    for r in cm[k]:
        i = r['clean_i']; old = al[i] if i < len(al) else None; t = r['true_gline']; rule = 'R-a1'
        if n == 49 and i == 2:
            assert t is None and old is None and r['count'] == len(gl[553]) == 21 and po[553] == 49
            t, rule = 553, 'R-a3'
        elif n == 11 and i == 3:  # R-a5 (PREREG Addendum 1): S1 A5 blind strip read (K250) fits 127, not the DP's 128
            assert t == 128 and old == 127
            t, rule = 127, 'R-a5'
        elif t is None:
            assert old is not None and r['count'] != len(gl[old]), (n, i)
            t, rule = old, 'R-a2 (unresolved; non-exact, no label)'
        out.append(t)
        if t != old:
            rows.append(dict(image=n, clean_i=i, v1=old, v2=t, count=r['count'],
                             v1_len=len(gl[old]) if old is not None else None, v2_len=len(gl[t]), rule=rule,
                             v1_exact=old is not None and r['count'] == len(gl[old]), v2_exact=r['count'] == len(gl[t])))
        elif rule.startswith('R-a2'):
            rows.append(dict(image=n, clean_i=i, v1=old, v2=t, count=r['count'], v1_len=len(gl[old]), v2_len=len(gl[t]),
                             rule=rule, v1_exact=False, v2_exact=False))
    v2[k] = out
dropped = {k: v1[k][len(v2[k]):] for k in v1 if len(v1[k]) > len(v2[k])}
# acceptance (PREREG §3)
c = collections.Counter(g for v in v2.values() for g in v)
dups = sorted(g for g, m in c.items() if m > 1)
r_a2 = {r['v2'] for r in rows if r['rule'].startswith('R-a2')}
assert all(g in r_a2 for g in dups), dups
assert all(isinstance(g, int) for v in v2.values() for g in v)
json.dump(v2, open(CUR, 'w'))
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
diff = dict(v1_sha256=sha(V1), v2_sha256=sha(CUR), corrected_map_sha256=sha(CMAP),
            semantics='v2[str(n)][i] = canon global line shown by the i-th clean (>=10-box) segmented line of image n',
            changed_or_flagged=rows, dropped_v1_tails=dropped, duplicate_glines=dups,
            glines_v1_not_v2=sorted(set(g for v in v1.values() for g in v) - set(c)),
            glines_v2_not_v1=sorted(set(c) - set(g for v in v1.values() for g in v)))
json.dump(diff, open(os.path.join(HERE, 'alignment_diff.json'), 'w'), indent=1)
print('changed/flagged rows', len(rows), '| dropped tails', dropped, '| dups', dups)
for r in rows: print(' ', r)
