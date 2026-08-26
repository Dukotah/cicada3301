"""C3 / L8 -- I-03, the cypherpunks arm.

Round 18's `predisclosure_search.sh` pointed at `lists.cpunks.org/pipermail/cypherpunks/`
and recorded `http=000` for every month of 2011-2013. Two separate things were going wrong
and neither was "the archive is empty":

  1. the host's TLS certificate has EXPIRED, so a verifying client fails before it sees any
     HTTP status at all -- `http=000` is a transport failure, not a 404, and it is not a
     searched month;
  2. the list is no longer served by pipermail. It runs HyperKitty, whose archive lives at
     `/archives/list/cypherpunks@lists.cpunks.org/` and whose monthly mbox export is a
     different URL entirely.

So the Round 18 negative for this arm covered ZERO months and did not know it. This script
fixes the endpoint, records the TLS caveat explicitly, and reports what the archive actually
holds for the window.
"""
import gzip, json, os, re, ssl, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'archives')
os.makedirs(OUT, exist_ok=True)

sys.path.append(HERE)
from predisclosure_archives import TERMS                               # noqa: E402

BASE = 'https://lists.cpunks.org/archives/list/cypherpunks@lists.cpunks.org/'
# NOTE: verification is disabled ONLY because the host's certificate is expired. That is
# recorded in the output; it is a provenance caveat on this arm, not a silent convenience.
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url, timeout=180):
    req = urllib.request.Request(url, headers={'User-Agent':
                                               'cicada3301-research/1.0 (archive coverage audit)'})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception as e:                                             # noqa: BLE001
        return 0, str(e).encode()


def main():
    res = dict(retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               base=BASE,
               tls_note=('host certificate is EXPIRED; fetched with verification disabled. '
                         'Recorded so the provenance of this arm is not overstated.'),
               years=[])
    code, body = get(BASE)
    res['index_http'] = code
    print('index http=%s' % code, flush=True)

    for year in (2011, 2012, 2013):
        url = ('%sexport/cypherpunks-%d.mbox.gz?start=%d-01-01&end=%d-12-31'
               % (BASE, year, year, year))
        path = os.path.join(OUT, 'cpunks-hyperkitty-%d.mbox.gz' % year)
        if not os.path.exists(path) or os.path.getsize(path) < 64:
            c, b = get(url)
            if c == 200 and b:
                open(path, 'wb').write(b)
            else:
                res['years'].append(dict(year=year, http=c, bytes=0,
                                         note=b[:160].decode('utf-8', 'replace')))
                print('%d export http=%s (no data)' % (year, c), flush=True)
                continue
        raw = open(path, 'rb').read()
        try:
            txt = gzip.decompress(raw).decode('utf-8', 'replace')
        except OSError:
            txt = raw.decode('utf-8', 'replace')
        # months actually represented, from the mbox Date: headers
        months = sorted(set(re.findall(r'^Date:.*?(\w{3}) (\d{4})', txt, re.M | re.I)))
        n_msgs = len(re.findall(r'^From ', txt, re.M))
        hits = []
        for tname, pat in TERMS.items():
            for m in re.finditer(pat, txt, re.I):
                a = max(0, m.start() - 120); b2 = min(len(txt), m.end() + 120)
                hits.append(dict(term=tname, context=txt[a:b2].replace('\n', ' ')))
        res['years'].append(dict(year=year, http=200, bytes=len(raw), chars=len(txt),
                                 n_messages=n_msgs, months_seen=[' '.join(x) for x in months],
                                 n_term_hits=len(hits), hits=hits[:200]))
        print('%d  %.2f MB  %d messages  months %s  hits %d'
              % (year, len(raw) / 1e6, n_msgs, [' '.join(x) for x in months], len(hits)),
              flush=True)

    json.dump(res, open(os.path.join(HERE, 'cpunks_export.json'), 'w'), indent=1)
    print('wrote cpunks_export.json')


if __name__ == '__main__':
    main()
