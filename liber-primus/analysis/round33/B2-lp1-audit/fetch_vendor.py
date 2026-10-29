"""Fetch the 19 vendored scream314 JPEGs T1 used (LP1 00-16, LP2 p56/p57 = 73/74.jpg), verified against the
SHA-256 values T1 committed in work/hashes_*.json. Data only; nothing downloaded is executed. Writes vendor_fetch/."""
import json, subprocess, hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
T1W = os.path.join(HERE, '..', '..', 'round19', 'T1', 'work')
os.makedirs(os.path.join(HERE, 'vendor_fetch'), exist_ok=True)
want = {}
for f in ('hashes_LP1.json', 'hashes_LP2.json'):
    for k, v in json.load(open(os.path.join(T1W, f))).items():
        if 'vendor' in v['path']:
            want[os.path.basename(v['path'])] = v['sha256']
for name, sha in sorted(want.items()):
    out = subprocess.run(['gh', 'api', '-H', 'Accept: application/vnd.github.raw',
        'repos/cicada-solvers/documenting-cicada3301-scream314/contents/assets/2014/liber-primus-complete/' + name],
        capture_output=True).stdout
    assert hashlib.sha256(out).hexdigest() == sha, name
    open(os.path.join(HERE, 'vendor_fetch', name), 'wb').write(out)
print('ok', len(want))
