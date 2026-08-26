"""C3 / L8 -- I-03, the bitcointalk arm, upgraded from `reported` to `verified`.

The Round 18 lane's own §4.6 names this as reopening condition #2: *"A local bitcointalk
corpus (the forum's own search, or a database dump) replacing the search-engine layer, which
would upgrade §4.4's `reported` rows to `verified`."*

`api.ninjastic.space` is exactly that -- a third-party full-text index over bitcointalk posts
with post ids, dates and authors, queryable directly. A grep over a real index is reproducible
and its negative is a measurable bound; a search-engine miss is not.

Method, fixed before running:
  * run the twelve terms fixed in `round18/L8-provenance/PREREG.md`, unchanged and unextended;
  * for each, request the OLDEST matching posts (ascending by date);
  * record the earliest dated match, and whether ANY match predates 2012-01-04;
  * a HIT requires a dated, archive-attested post before the element's disclosure date. The
    index carries per-post dates, so a match's date is attestable from the same source.

Anti-motivated-reasoning: the term `cicada` alone matches insects, usernames and unrelated
projects. It is run because it is on the pre-registered list, and any pre-2012 match it
returns is inspected by eye against the HIT bar rather than counted.

Writes `bitcointalk_ninjastic.json`.
"""
import json, os, time, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
API = 'https://api.ninjastic.space/posts'
CEILING = '2012-01-04'

TERMS = [
    '3301', '845145127', 'cicada', 'instar', 'instar emergence',
    'looking for highly intelligent', 'liber primus', 'futhorc',
    'mabinogion', 'outguess', 'a2e7j6ic78h0j', 'cicada 3301',
]


def get(params, timeout=45):
    url = API + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'cicada3301-research/1.0 (I-03 pre-disclosure bound)'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode('utf-8', 'replace')), url
    except urllib.error.HTTPError as e:
        return e.code, None, url
    except Exception as e:                                             # noqa: BLE001
        return 0, {'error': str(e)}, url


def main():
    out = dict(retrieved_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               api=API, ceiling=CEILING,
               method=('twelve pre-registered terms, oldest-first, per-post dates read from '
                       'the index itself'),
               terms=[])
    for t in TERMS:
        row = dict(term=t)
        # oldest-first
        code, js, url = get(dict(content=t, limit=20, order='ASC'))
        row['http'] = code
        row['url'] = url
        if code != 200 or not js or js.get('result') != 'success':
            row['error'] = (js or {}).get('message') or 'request failed'
            out['terms'].append(row)
            print('%-32s http=%s  ERROR' % (t, code), flush=True)
            continue
        data = js.get('data') or {}
        posts = data.get('posts') or []
        row['total_results'] = data.get('total_results')
        row['n_returned'] = len(posts)
        oldest = []
        pre = []
        for p in posts:
            d = (p.get('date') or '')[:10]
            rec = dict(post_id=p.get('post_id'), topic_id=p.get('topic_id'),
                       date=p.get('date'), title=p.get('title'),
                       author=p.get('author'),
                       url='https://bitcointalk.org/index.php?topic=%s.msg%s#msg%s'
                           % (p.get('topic_id'), p.get('post_id'), p.get('post_id')),
                       excerpt=' '.join((p.get('content') or '').split())[:200])
            oldest.append(rec)
            if d and d < CEILING:
                pre.append(rec)
        row['oldest_returned'] = oldest[:5]
        row['earliest_date'] = oldest[0]['date'] if oldest else None
        row['n_predating_ceiling'] = len(pre)
        row['predating_ceiling'] = pre[:10]
        out['terms'].append(row)
        print('%-32s total=%-6s earliest=%-22s pre-%s: %d'
              % (t, row['total_results'], row['earliest_date'], CEILING, len(pre)),
              flush=True)
        time.sleep(0.6)

    hits = [r for r in out['terms'] if r.get('n_predating_ceiling')]
    out['n_terms_with_pre_ceiling_matches'] = len(hits)
    out['terms_with_pre_ceiling_matches'] = [r['term'] for r in hits]
    json.dump(out, open(os.path.join(HERE, 'bitcointalk_ninjastic.json'), 'w'), indent=1)
    print('\nterms with ANY match predating %s: %d  %s'
          % (CEILING, len(hits), [r['term'] for r in hits]))
    print('wrote bitcointalk_ninjastic.json')


if __name__ == '__main__':
    main()
