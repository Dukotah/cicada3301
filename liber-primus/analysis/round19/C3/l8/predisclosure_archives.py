"""C3 / L8 closeout -- I-03 pre-disclosure search over the MAILING-LIST archives.

Round 18's `predisclosure_search.sh` fetched blind: it hit a fixed URL for every month of
2011-2013 and treated a 404 as "nothing there". That conflates two completely different
facts -- *the month was searched and held no hit* versus *the month does not exist in the
archive at all* -- and only the first is a negative. This script separates them.

Method
  1. Fetch each list's pipermail INDEX and parse out which monthly archives actually exist.
     That is the archive's own statement of what it covers, and it is the denominator of
     any coverage claim.
  2. Download every month that exists inside the window.
  3. Grep the real mbox text for the terms fixed in `round18/L8-provenance/PREREG.md`.
  4. Report coverage as `months_present / months_in_window`, per list, and the hit count.

A term list is fixed at module scope and is NOT edited after seeing results.
"""
import gzip, io, json, os, re, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'archives')
os.makedirs(OUT, exist_ok=True)

# The PREREG term list, verbatim. Regexes are case-insensitive.
TERMS = {
    '3301':                  r'\b3301\b',
    '845145127':             r'\b845145127\b',
    'cicada+puzzle':         r'cicada',
    'instar':                r'\binstar\b',
    'highly intelligent':    r'looking for highly intelligent',
    'liber primus':          r'liber\s+primus',
    'futhorc':               r'futhorc|futhark',
    'mabinogion':            r'mabinogion',
    'outguess':              r'outguess',
    'onion a2e7j6ic78h0j':   r'a2e7j6ic78h0j',
    'cicada 3301':           r'cicada[\s\-]*3301',
    'gematria+rune':         r'gematria',
}

LISTS = [
    # name, index url, month url template
    ('metzdowd-cryptography',
     'https://www.metzdowd.com/pipermail/cryptography/',
     'https://www.metzdowd.com/pipermail/cryptography/%s.txt.gz'),
    ('cpunks-cypherpunks',
     'https://lists.cpunks.org/pipermail/cypherpunks/',
     'https://lists.cpunks.org/pipermail/cypherpunks/%s.txt.gz'),
    ('mail-archive-cypherpunks',
     'https://www.mail-archive.com/cypherpunks@cpunks.org/',
     None),
]

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
WINDOW_HARD = [(2011, m) for m in range(1, 13)] + [(2012, 1)]      # -> 2012-01-04
WINDOW_CTX = ([(2011, m) for m in range(1, 13)] +
              [(2012, m) for m in range(1, 13)] +
              [(2013, m) for m in range(1, 13)])


def get(url, timeout=45):
    req = urllib.request.Request(url, headers={'User-Agent':
                                               'cicada3301-research/1.0 (archive coverage audit)'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception as e:                                          # noqa: BLE001
        return 0, str(e).encode()


def main():
    res = dict(retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               terms={k: v for k, v in TERMS.items()}, lists=[])

    for name, index_url, tmpl in LISTS:
        entry = dict(list=name, index_url=index_url)
        code, body = get(index_url)
        entry['index_http'] = code
        if code != 200:
            entry['reachable'] = False
            entry['months_present_in_archive'] = []
            entry['note'] = 'index not reachable: %s' % body[:120].decode('utf-8', 'replace')
            res['lists'].append(entry)
            print('%-26s index http=%s UNREACHABLE' % (name, code), flush=True)
            continue
        entry['reachable'] = True
        html = body.decode('utf-8', 'replace')
        present = sorted(set(re.findall(r'(\d{4}-[A-Z][a-z]+)\.txt(?:\.gz)?', html)))
        entry['months_present_in_archive'] = present
        entry['n_months_present_total'] = len(present)
        print('%-26s index OK, %d monthly archives listed' % (name, len(present)), flush=True)

        if tmpl is None:
            entry['note'] = ('no pipermail monthly .txt.gz endpoint; search-interface only. '
                             'Not downloadable as an mbox, so it yields no coverage number here.')
            res['lists'].append(entry)
            continue

        def label(y, m):
            return '%d-%s' % (y, MONTHS[m - 1])

        want_hard = [label(y, m) for y, m in WINDOW_HARD]
        want_ctx = [label(y, m) for y, m in WINDOW_CTX]
        have_hard = [w for w in want_hard if w in present]
        have_ctx = [w for w in want_ctx if w in present]
        entry['window_hard'] = dict(months_requested=len(want_hard),
                                    months_present=len(have_hard),
                                    present=have_hard,
                                    absent=[w for w in want_hard if w not in present])
        entry['window_context'] = dict(months_requested=len(want_ctx),
                                       months_present=len(have_ctx))

        hits, fetched, bytes_total = [], [], 0
        for ym in have_ctx:
            path = os.path.join(OUT, '%s__%s.txt.gz' % (name, ym))
            if not os.path.exists(path) or os.path.getsize(path) < 100:
                c, b = get(tmpl % ym)
                if c != 200 or not b:
                    continue
                open(path, 'wb').write(b)
            raw = open(path, 'rb').read()
            bytes_total += len(raw)
            try:
                txt = gzip.decompress(raw).decode('utf-8', 'replace')
            except OSError:
                txt = raw.decode('utf-8', 'replace')
            fetched.append(dict(month=ym, bytes=len(raw), chars=len(txt)))
            for tname, pat in TERMS.items():
                for m in re.finditer(pat, txt, re.I):
                    a = max(0, m.start() - 120); b2 = min(len(txt), m.end() + 120)
                    hits.append(dict(month=ym, term=tname,
                                     context=txt[a:b2].replace('\n', ' ')))
        entry['months_downloaded'] = len(fetched)
        entry['bytes_downloaded'] = bytes_total
        entry['n_term_hits'] = len(hits)
        entry['hits'] = hits[:200]
        print('%-26s downloaded %d months, %.1f MB, %d raw term hits'
              % (name, len(fetched), bytes_total / 1e6, len(hits)), flush=True)
        res['lists'].append(entry)

    json.dump(res, open(os.path.join(HERE, 'predisclosure_archives.json'), 'w'), indent=1)
    print('\nwrote predisclosure_archives.json')
    for e in res['lists']:
        wh = e.get('window_hard')
        if wh:
            print('  %-26s HARD WINDOW coverage %d/%d months  (%s)'
                  % (e['list'], wh['months_present'], wh['months_requested'],
                     ', '.join(wh['present']) or 'none'))


if __name__ == '__main__':
    main()
