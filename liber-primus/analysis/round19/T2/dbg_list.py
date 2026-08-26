import json, os, sys
import t2lib as T
res = json.load(open(os.path.join(T.HERE, sys.argv[1])))
for r in res:
    print(r.get('gline'), 'seg', r.get('seg'), 'nrune', r.get('nrune'), 'ncomp', r.get('ncomp'),
          'bad', sum(1 for j, c in enumerate(r.get('canon', [])) if r['best'][j] != c) if 'canon' in r else r)
