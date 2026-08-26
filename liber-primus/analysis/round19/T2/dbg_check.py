import json, glob, os
for f in sorted(glob.glob('out_*.json')):
    try:
        d = json.load(open(f))
        n = len(d) if isinstance(d, list) else list(d)[:6]
        print('%-24s OK  %s' % (f, n))
    except Exception as e:
        print('%-24s CORRUPT %s' % (f, e))
