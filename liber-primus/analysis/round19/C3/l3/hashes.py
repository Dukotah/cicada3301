"""C3 / L3 -- record the sha256 of every image this lane read.

Crops are gitignorable and rebuildable; the HASH of the source render is the thing that has
to survive, because it is what lets anyone re-derive the same crop and get the same read.
"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

ASSETS = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                      'cicada-solvers__documenting-cicada3301-scream314',
                      'assets', '2014', 'liber-primus-complete')
RELIKD = os.path.join(R.LP, 'data', 'relikd')


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def main():
    out = dict(control_renders={}, target_renders={}, lineage={})
    for f in ('01.jpg', '03.jpg', '05.jpg', '06.jpg', '14.jpg', '17.jpg',
              '73.jpg', '74.jpg'):
        p = os.path.join(ASSETS, f)
        if os.path.exists(p):
            out['control_renders'][f] = dict(sha256=sha(p), bytes=os.path.getsize(p))
    for i in range(56):
        p = os.path.join(RELIKD, 'p%d.jpg' % i)
        if os.path.exists(p):
            out['target_renders']['p%d.jpg' % i] = dict(sha256=sha(p),
                                                        bytes=os.path.getsize(p))
    a = out['control_renders'].get('17.jpg', {}).get('sha256')
    b = out['target_renders'].get('p0.jpg', {}).get('sha256')
    out['lineage'] = dict(
        claim='vendored 2014 asset 17.jpg is byte-identical to data/relikd/p0.jpg',
        asset_17_sha256=a, relikd_p0_sha256=b, identical=(a is not None and a == b))
    out['n_control'] = len(out['control_renders'])
    out['n_target'] = len(out['target_renders'])
    json.dump(out, open(os.path.join(HERE, 'hashes.json'), 'w'), indent=1)
    print('control renders: %d   target renders: %d' % (out['n_control'], out['n_target']))
    print('lineage 17.jpg == relikd p0.jpg :', out['lineage']['identical'])
    print('  17.jpg     ', a)
    print('  relikd p0  ', b)


if __name__ == '__main__':
    main()
