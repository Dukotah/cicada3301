"""Fetch the targeted corpus extension listed in targets.json.

Resumable (skips files already on disk), verifies each download is a real
Gutenberg text (has the START-OF marker or >20 KB of prose) and DROPS anything
that fails rather than guessing, exactly like campaign12/fetch_keytexts.py.

The corpus is written OUTSIDE the repo by default (repo convention: corpora are
gitignored, the fetcher is the rebuild recipe).  Override with argv[1].

  python3 fetch_corpus.py [outdir] [n_workers]
"""
import os, sys, json, time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.environ.get('TEMP', '/tmp'), 'l4corpus')
NW = int(sys.argv[2]) if len(sys.argv) > 2 else 6
os.makedirs(OUT, exist_ok=True)

URLS = ['https://www.gutenberg.org/cache/epub/{0}/pg{0}.txt',
        'https://www.gutenberg.org/files/{0}/{0}-0.txt',
        'https://www.gutenberg.org/ebooks/{0}.txt.utf-8']


def one(rec):
    gid = rec['gid']
    dst = os.path.join(OUT, 'pg%d.txt' % gid)
    if os.path.exists(dst) and os.path.getsize(dst) > 20000:
        return (gid, 'cached')
    for u in URLS:
        try:
            req = urllib.request.Request(u.format(gid),
                                         headers={'User-Agent':
                                                  'cicada3301-rig/round10-L4'})
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode('utf-8', 'ignore')
        except Exception:
            time.sleep(1); continue
        if len(txt) < 20000 or 'PROJECT GUTENBERG' not in txt.upper():
            continue
        open(dst, 'w', encoding='utf-8').write(txt)
        return (gid, 'ok %d' % len(txt))
    return (gid, 'FAIL')


def main():
    tgt = json.load(open(os.path.join(HERE, 'targets.json')))
    print('fetching %d texts -> %s (%d workers)' % (len(tgt), OUT, NW),
          flush=True)
    ok = fail = 0
    with ThreadPoolExecutor(NW) as ex:
        for i, (gid, st) in enumerate(ex.map(one, tgt)):
            if st == 'FAIL':
                fail += 1
            else:
                ok += 1
            if i % 50 == 0:
                print('  %d/%d ok=%d fail=%d' % (i, len(tgt), ok, fail),
                      flush=True)
    print('done: ok=%d fail=%d  dir=%s' % (ok, fail, OUT))


if __name__ == '__main__':
    main()
