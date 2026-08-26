import json
B='/mnt/c/Users/dukot/projects/cicada3301/liber-primus/'
d=json.load(open(B+'analysis/vision/canonical_pages.json'))
print('entries',len(d))
for p in d[44:]: print(p['page'], p['n_runes'])
raw=open(B+'data/krisyotam_runes.txt',encoding='utf-8').read()
chunks=raw.split('%')
print('chunks',len(chunks))
for i,c in enumerate(chunks):
    if i>=44: print(i, len(c), repr(c[:30]))
