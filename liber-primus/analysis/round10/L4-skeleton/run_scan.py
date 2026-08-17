"""T1 — the extended-corpus skeleton scan.

Real LP2 word-length sequence vs the whole extended corpus, three matchers
(exact / Round-8 slack-1 / directional interval), against 4 independent shuffles
of the SAME sequence as null (a permutation preserves the length histogram and
the interrupter count exactly, and destroys only the order).

Also runs windows 400 and 120 so a PARTIAL plaintext match -- a single page-group
drawn from a known text -- is not missed by the full-length window.

Round 8's headline z of 2.07 was a max-of-many-offsets artifact: its leaderboard
was an ordering by text length.  This run therefore records the per-text best for
the real sequence AND for every null, so the comparison can be made
length-matched instead of global.

  python3 run_scan.py [extra_corpus_glob ...]
"""
import os, sys, json, time
import numpy as np
import skel, scanner

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    extra = tuple(sys.argv[1:])
    C, meta = skel.load_corpus(extra_globs=extra)
    lp, fc = skel.lp2_words()
    P = len(lp)
    rng = np.random.default_rng(3301)

    pats = []
    pats.append(scanner.Pattern('real:exact', skel.groups_slack(lp, 0), P))
    pats.append(scanner.Pattern('real:slack1', skel.groups_slack(lp, 1), P))
    pats.append(scanner.Pattern('real:interval', skel.groups_interval(lp, fc), P))
    NN = 4
    for k in range(NN):
        i = rng.permutation(P)
        s, sf = lp[i], fc[i]
        pats.append(scanner.Pattern('n%d:exact' % k, skel.groups_slack(s, 0), P))
        pats.append(scanner.Pattern('n%d:slack1' % k, skel.groups_slack(s, 1), P))
        pats.append(scanner.Pattern('n%d:interval' % k,
                                    skel.groups_interval(s, sf), P))
    for W in (400, 120):
        pats.append(scanner.Pattern('realW%d:interval' % W,
                                    skel.groups_interval(lp[:W], fc[:W]), W))
        for k in range(2):
            i = rng.permutation(W)
            pats.append(scanner.Pattern('n%dW%d:interval' % (k, W),
                                        skel.groups_interval(lp[:W][i],
                                                             fc[:W][i]), W))

    print('%d patterns, %d groups; corpus %d texts %d words'
          % (len(pats), sum(len(p.groups) for p in pats), len(C),
             sum(len(v) for v in C.values())), flush=True)
    t0 = time.time()
    best, per_text = scanner.scan_corpus(C, pats, progress=100)
    print('scan %.1f min' % ((time.time() - t0) / 60), flush=True)

    sizes = {k: int(len(v)) for k, v in C.items()}
    out = dict(corpus_texts=len(C), corpus_words=int(sum(sizes.values())),
               window=P, sizes=sizes,
               best={k: dict(count=v[0], text=v[1], offset=v[2]) for k, v in best.items()},
               per_text=per_text)
    json.dump(out, open(os.path.join(HERE, 'scan_results.json'), 'w'))

    # ---- report ----
    for W, tag in ((P, ''), (400, 'W400'), (120, 'W120')):
        for m in ('exact', 'slack1', 'interval'):
            rk = ('real%s:%s' % (tag, m))
            if rk not in best:
                continue
            nulls = [best[k][0] for k in best
                     if k.endswith(':' + m) and k.startswith('n')
                     and (('W%d' % W) in k if tag else 'W' not in k)]
            if not nulls:
                continue
            b, tn, off = best[rk]
            nm, ns = float(np.mean(nulls)), float(np.std(nulls) + 1e-9)
            print('%-18s best %6.0f/%4d (%5.1f%%) in %-40s @%d | null max %.0f mean %.1f | z %.2f'
                  % (rk, b, W, 100 * b / W, tn, off, max(nulls), nm, (b - nm) / ns))
    print('wrote scan_results.json')


if __name__ == '__main__':
    main()
