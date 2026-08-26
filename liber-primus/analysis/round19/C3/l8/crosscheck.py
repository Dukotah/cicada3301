"""C3 / L8 -- independent re-derivation vs Round 18's stored table, and the L1 cross-check.

Three jobs:
  1. DIFF the C3 re-run against `round18/L8-provenance/PGP-VERIFICATION-TABLE.json`, file by
     file. A stored JSON is not evidence until someone reproduces it; a discrepancy that is
     not explained is a defect in one of the two runs.
  2. CROSS-CHECK the `GnuPG v1.4.11 (GNU/Linux)` count Round 18's L1-toolchain built its
     evidence-derived prior on (reported 46/46). L1's prior promotes Perl 5.14, bash $RANDOM,
     Python 2.7 and LaTeX LCGs and demotes .NET x0.05, and Round 19's whole Phase-1 generator
     set rests on it. If the denominator is wrong, so is the prior.
  3. Report the armor `Version:`/`Comment:` header distribution over the VERIFIED messages
     only, which is the population L1's claim is about.
"""
import json, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
C3 = os.path.normpath(os.path.join(HERE, '..', 'PGP-VERIFICATION-TABLE.json'))
R18 = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'round18', 'L8-provenance',
                                    'PGP-VERIFICATION-TABLE.json'))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))


def index(tbl):
    rows = tbl['rows'] if isinstance(tbl, dict) and 'rows' in tbl else (
        tbl['files'] if isinstance(tbl, dict) and 'files' in tbl else tbl)
    return {r['path']: r for r in rows}


def main():
    a = json.load(open(C3))
    b = json.load(open(R18))
    ia, ib = index(a), index(b)
    out = dict(c3_files=len(ia), r18_files=len(ib))

    only_c3 = sorted(set(ia) - set(ib))
    only_r18 = sorted(set(ib) - set(ia))
    both = sorted(set(ia) & set(ib))
    changed = [p for p in both if ia[p].get('verdict', ia[p].get('kind')) != ib[p].get('verdict', ib[p].get('kind'))]
    hash_changed = [p for p in both if ia[p].get('sha256') != ib[p].get('sha256')]

    out['only_in_c3'] = only_c3
    out['only_in_round18'] = only_r18
    out['in_both'] = len(both)
    out['verdict_changed'] = [dict(path=p, round18=ib[p].get('verdict', ib[p].get('kind')),
                                   c3=ia[p].get('verdict', ia[p].get('kind'))) for p in changed]
    out['sha256_changed'] = hash_changed
    out['only_in_c3_verdicts'] = collections.Counter(ia[p].get('verdict', ia[p].get('kind')) for p in only_c3)

    print('C3 rows %d | R18 rows %d | in both %d' % (len(ia), len(ib), len(both)))
    print('only in C3   : %d  %s' % (len(only_c3), dict(out['only_in_c3_verdicts'])))
    for p in only_c3:
        print('    +', p, '->', ia[p].get('verdict', ia[p].get('kind')))
    print('only in R18  : %d' % len(only_r18))
    for p in only_r18:
        print('    -', p, '->', ib[p].get('verdict', ib[p].get('kind')))
    print('verdict changed on a shared file : %d' % len(changed))
    for c in out['verdict_changed']:
        print('    !', c)
    print('sha256 changed on a shared file  : %d' % len(hash_changed))

    # ---- headline agreement on the counts that matter
    def counts(tbl, idx, restrict=None):
        rows = [r for p, r in idx.items() if restrict is None or restrict(p)]
        return collections.Counter(r.get('verdict', r.get('kind')) for r in rows)
    ca = counts(a, ia); cb = counts(b, ib)
    ca_shared = counts(a, {p: ia[p] for p in both})
    cb_shared = counts(b, {p: ib[p] for p in both})
    out['verdict_counts'] = dict(c3=dict(ca), round18=dict(cb),
                                 c3_on_shared_files=dict(ca_shared),
                                 round18_on_shared_files=dict(cb_shared))
    out['counts_agree_on_shared_files'] = (ca_shared == cb_shared)
    print('\nverdicts C3          :', dict(ca))
    print('verdicts R18         :', dict(cb))
    print('on SHARED files C3   :', dict(ca_shared))
    print('on SHARED files R18  :', dict(cb_shared))
    print('AGREE on shared files:', out['counts_agree_on_shared_files'])

    # ---- signing key ids
    def keyids(idx):
        s = set()
        for r in idx.values():
            for p in (r.get('signature_packets') or []):
                if p.get('keyid'):
                    s.add(p['keyid'].upper())
        return s
    out['signing_keyids_c3'] = sorted(keyids(ia))
    out['signing_keyids_r18'] = sorted(keyids(ib))
    print('\nsigning key ids C3 :', out['signing_keyids_c3'])
    print('signing key ids R18:', out['signing_keyids_r18'])

    # ---- 2. the L1 cross-check: armor Version headers on VERIFIED messages
    ver = collections.Counter()
    ver_all = collections.Counter()
    per_file = []
    for p, r in ia.items():
        fp = os.path.join(REPO, p)
        if not os.path.exists(fp):
            continue
        try:
            txt = open(fp, 'rb').read().decode('utf-8', 'replace')
        except OSError:
            continue
        # the Version:/Comment: header of the SIGNATURE armor block
        m = re.search(r'-----BEGIN PGP SIGNATURE-----\s*\n((?:[A-Za-z][\w-]*:.*\n)*)', txt)
        hdr = m.group(1) if m else ''
        vm = re.search(r'^Version:\s*(.+?)\s*$', hdr, re.M)
        v = vm.group(1) if vm else None
        if r.get('verdict', r.get('kind')) in ('PASS', 'FAIL'):
            ver_all[v] += 1
            per_file.append(dict(path=p, verdict=r.get('verdict', r.get('kind')), version=v))
        if r.get('verdict', r.get('kind')) == 'PASS':
            ver[v] += 1
    out['signature_armor_version_PASS_files'] = dict(ver)
    out['signature_armor_version_PASS_or_FAIL_files'] = dict(ver_all)

    # per distinct message, not per file (a mirror is not an independent observation)
    bodies = {}
    for p, r in ia.items():
        if r.get('verdict', r.get('kind')) != 'PASS':
            continue
        k = r.get('body_sha256') or r.get('normalised_body_sha256') or r.get('message_key')
        if k is None:
            for pkt in (r.get('signature_packets') or []):
                k = pkt.get('created_unix')
                break
        v = next((f['version'] for f in per_file if f['path'] == p), None)
        bodies.setdefault(k, set()).add(v)
    permsg = collections.Counter()
    for k, vs in bodies.items():
        permsg[tuple(sorted(x or '(none)' for x in vs))] += 1
    out['version_per_distinct_message'] = {str(k): v for k, v in permsg.items()}
    out['n_distinct_messages_counted'] = len(bodies)

    print('\n--- L1 cross-check: signature-armor Version header ---')
    print('per FILE (PASS only)      :', dict(ver))
    print('per DISTINCT MESSAGE (%d) :' % len(bodies))
    for k, v in sorted(permsg.items(), key=lambda x: -x[1]):
        print('    %-40s %d' % (k, v))

    json.dump(out, open(os.path.join(HERE, 'crosscheck.json'), 'w'), indent=1)
    print('\nwrote crosscheck.json')


if __name__ == '__main__':
    main()
