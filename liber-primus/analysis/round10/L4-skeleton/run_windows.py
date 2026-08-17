"""T1b — SUB-WINDOW SWEEP.

run_scan.py answers "is the WHOLE of LP2 a contiguous passage of a corpus text?"
plus a partial probe on the FIRST 400 / FIRST 120 words only.  That leaves the
obvious hole: a passage anywhere else inside LP2.

This sweeps every non-overlapping window of LP2 at W=120 and W=400 against the
whole corpus, with the directional interval matcher, and gives each window its
own shuffled null (the shuffle is of THAT window, so the null carries that
window's own length histogram and interrupter count).

Detection power at these windows is inherited from the positive control that
already ran (positive_control.json):
    W=120  clean plant = 120/120 (100%),  per-text null mean 42.7 sd 2.9 max 49
    W=400  clean plant = 400/400 (100%),  per-text null mean 109.5 sd 6.7 max 133
so a genuinely-present verbatim 120-word stretch would land at z > 25.

  python3 run_windows.py [extra_corpus_glob ...]
"""
import os, sys, json, time
import numpy as np
import skel, scanner

HERE = os.path.dirname(os.path.abspath(__file__))
OUTNAME = os.environ.get('L4_OUT', 'window_results.json')


def main():
    extra = tuple(sys.argv[1:])
    C, _ = skel.load_corpus(extra_globs=extra)
    lp, fc = skel.lp2_words()
    P = len(lp)
    rng = np.random.default_rng(3301)

    pats = []
    spec = []
    for W in (400, 120):
        for s in range(0, P - W + 1, W):
            nm = 'w%d_%04d' % (W, s)
            pats.append(scanner.Pattern(nm, skel.groups_interval(lp[s:s+W],
                                                                 fc[s:s+W]), W))
            spec.append((nm, W, s))
        # 4 nulls per window size: shuffles of randomly chosen windows
        for k in range(4):
            s = int(rng.integers(0, P - W))
            i = rng.permutation(W)
            nm = 'null%d_W%d' % (k, W)
            pats.append(scanner.Pattern(nm, skel.groups_interval(lp[s:s+W][i],
                                                                 fc[s:s+W][i]), W))
            spec.append((nm, W, -1))

    print('%d patterns over %d texts / %d words'
          % (len(pats), len(C), sum(len(v) for v in C.values())), flush=True)
    t0 = time.time()
    best, per_text = scanner.scan_corpus(C, pats, progress=200)
    print('scan %.1f min' % ((time.time() - t0) / 60), flush=True)

    rows = []
    for nm, W, s in spec:
        b, tn, off = best[nm]
        pt = np.array([v for v in per_text[nm].values()])
        rows.append(dict(name=nm, W=W, lp_start=s, best=b, pct=100*b/W,
                         text=tn, offset=off,
                         pt_mean=float(pt.mean()), pt_sd=float(pt.std()),
                         pt_max=float(pt.max())))
    # null band per window size
    for W in (400, 120):
        nl = [r for r in rows if r['W'] == W and r['lp_start'] < 0]
        re_ = [r for r in rows if r['W'] == W and r['lp_start'] >= 0]
        nb = np.array([r['best'] for r in nl])
        nmu, nsd = nb.mean(), nb.std() + 1e-9
        print('\n== W=%d ==  null best-across-corpus: mean %.1f sd %.1f max %.1f (%.1f%%)'
              % (W, nmu, nsd, nb.max(), 100*nb.max()/W))
        re_.sort(key=lambda r: -r['best'])
        for r in re_[:8]:
            r['z_vs_nullband'] = (r['best'] - nmu) / nsd
            print('  lp@%-5d best %5.0f/%d (%5.1f%%) z=%5.2f  %-44s @%d'
                  % (r['lp_start'], r['best'], W, r['pct'],
                     r['z_vs_nullband'], r['text'], r['offset']))
        allb = np.array([r['best'] for r in re_])
        print('  real windows: n=%d mean %.1f sd %.1f max %.1f | null max %.1f'
              % (len(allb), allb.mean(), allb.std(), allb.max(), nb.max()))

    json.dump(dict(corpus_texts=len(C),
                   corpus_words=int(sum(len(v) for v in C.values())),
                   rows=rows), open(os.path.join(HERE, OUTNAME), 'w'), indent=1)
    print('wrote', OUTNAME)


if __name__ == '__main__':
    main()
