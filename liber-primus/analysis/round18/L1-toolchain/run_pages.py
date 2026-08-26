"""Fingerprint every LP2 page JPEG and summarise the encoder-parameter partition.

Round 18 lane L1.  Writes:
  pages_fingerprints.json   full per-file record (gitignored if large)
  pages_summary.json        the distinct fingerprint classes + page membership
"""
import os, sys, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jpeg_fingerprint import fingerprint

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PAGES = os.path.join(ROOT, 'corpus', 'A-primary-artifacts', 'cijhho123', '2014',
                     'Liber Primus', 'A drop box of all unmodified files', '2014onion7')


def main():
    rows = []
    for n in range(58):
        p = os.path.join(PAGES, '%d.jpg' % n)
        if not os.path.exists(p):
            print('MISSING', p)
            continue
        fp = fingerprint(p)
        fp['page'] = n
        rows.append(fp)
    with open(os.path.join(HERE, 'pages_fingerprints.json'), 'w') as f:
        json.dump(rows, f, indent=1)

    classes = collections.OrderedDict()
    for r in rows:
        v = r['fingerprint_vector']
        k = json.dumps({kk: v[kk] for kk in
                        ('ncomp', 'subsampling', 'progressive', 'dqt_sha1', 'ijg_q',
                         'dht_class', 'ndht', 'dri', 'apps', 'icc_sha256',
                         'marker_order', 'jfif')}, sort_keys=True)
        classes.setdefault(k, []).append(r['page'])

    summary = {
        'n_files': len(rows),
        'geometries': collections.Counter(tuple(r['fingerprint_vector']['geometry']) for r in rows),
        'classes': [{'members': v, 'n': len(v), 'vector': json.loads(k)}
                    for k, v in classes.items()],
        'trailing_bytes': {r['page']: r['trailing'] for r in rows if r['trailing']},
        'com_segments': {r['page']: r['com'] for r in rows if r['com']},
        'icc': None,
    }
    summary['geometries'] = {('%dx%d' % g): c for g, c in summary['geometries'].items()}
    icc = next((r['icc'] for r in rows if r['icc']), None)
    if icc:
        summary['icc'] = {k: icc[k] for k in icc if k != 'vals'}
    summary['icc_all_identical'] = len(set(
        (r['icc'] or {}).get('sha256') for r in rows)) == 1
    with open(os.path.join(HERE, 'pages_summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1)[:6000])


if __name__ == '__main__':
    main()
