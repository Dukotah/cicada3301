"""Final consistency check: every headline number in RESULTS.md against the JSON."""
import json, os, hashlib, collections
import t2lib as T

def j(f): return json.load(open(os.path.join(T.HERE, f)))

a01, sp, ind, isc, iadj = j('out_a01.json'), j('out_splice.json'), j('out_indel.json'), j('out_indel_score.json'), j('out_indel_adj.json')
sep, s19, orph = j('out_separators.json'), j('out_sep19.json'), j('out_orphan.json')
lmr = j('out_linemap.json')
probe = j('out_probe.json')

ok = []
def chk(name, got, want):
    good = (abs(got-want) < 1e-9) if isinstance(want, float) else (got == want)
    ok.append(good)
    print('%-52s %-16s %s' % (name, got, 'OK' if good else 'MISMATCH want %s' % (want,)))

chk('lines probed', a01['n_lines'], 604)
chk('slots adjudicated', a01['n_slots'], 13121)
chk('illuminated-initial slots excluded', a01['skipped_initial'], 15)
chk('canon rune total', sum(len(c['runes']) for c in T.canon_lines()), 13136)
chk('coverage %', round(100*a01['n_slots']/13136, 2), 99.89)
cls = collections.Counter(f['cls'] for f in a01['flags'])
chk('SEG / CONF / ID', '%d/%d/%d' % (cls['SEG'], cls['CONF'], cls['ID']), '33/0/2')
chk('canon lines mapped', len(lmr['map']), 604)
chk('pages mapped', sum(1 for r in lmr['report'] if r['ok']), 57)
chk('count-exact lines', sum(r['count_exact'] for r in lmr['report'] if r['ok']), 530)

strat = collections.defaultdict(lambda: [0,0])
for r in probe:
    if 'fail' in r: continue
    s = 'solved' if r['seg'] in (55,56) else ('dense' if 45<=r['seg']<=54 else 'p0_44')
    for k,c in enumerate(r['canon']):
        strat[s][0]+=1
        if r['best'][k]==c: strat[s][1]+=1
for s in ('solved','dense','p0_44'):
    n,h = strat[s]
    print('%-52s %d/%d = %.4f' % ('agreement '+s, h, n, h/n))
chk('dense slots', strat['dense'][0], 1992)
chk('dense agreement', strat['dense'][1], 1992)
chk('solved agreement', strat['solved'][1], strat['solved'][0])
chk('overall agreement', round(sum(v[1] for v in strat.values())/sum(v[0] for v in strat.values()), 4), 0.9973)

chk('splice n', len(sp['results']), 545)
chk('splice all recovered', sum(r['recover'] for r in sp['results']), 545)
chk('indel flags', len(iadj), 26)
chk('indel flags all SEG', sum(1 for a in iadj if a['verdict']=='SEG'), 26)
chk('sep19 count', len(s19), 19)
chk('sep19 all resolved', sum(1 for r in s19 if r['verdict'].startswith('RESOLVED')), 19)
chk('separator lines pos-exact', sep['totals']['pos_exact'], 580)
chk('separator lines count-exact', sep['totals']['count_exact'], 582)
chk('image dashes', sep['totals']['img_dash'], 2767)
chk('image dots', sep['totals']['img_dot'], 187)
chk('mid-size marks', orph['total'], 487)
chk('indel positions tested', isc['n_positions'], 13121)

print('\nledger.json parses:', bool(json.load(open(os.path.join(T.HERE,'ledger.json')))['entries']))
print('ALL CHECKS PASS' if all(ok) else 'SOME CHECKS FAILED')
