"""T0 / T0b / T0c — POSITIVE CONTROL and DETECTION FLOOR.

Round 8 ran the skeleton scan and reported a negative WITHOUT ever showing that
the instrument can find a plaintext it is known to contain.  This does that
first, then measures how far a genuinely-present plaintext can drift before the
scan goes blind.  That drift number is what turns a negative into a bound.

Two independent degradation axes, because they fail differently:
  SUB   - per-word length noise (edition spelling, hyphenation, transliteration
          convention, an unknown extra null class).  Degrades the score linearly.
  INDEL - inserted/deleted WORDS (a different translation/recension, an editor's
          "and", a paraphrase).  Destroys the ALIGNMENT, so a fixed-offset
          correlation collapses after the first few.  This is the hard limit,
          and short windows are the only defence.
"""
import os, sys, json, time
import numpy as np
import skel, scanner

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(3301)
LP_F_TOTAL = 458
LP_FC_HIST = [2506, 387, 34, 1]      # LP2's own per-word interrupter histogram


def plant(true_lens, rng):
    """add interrupters with LP2's exact per-word F histogram -> (obs, fc)"""
    n = len(true_lens)
    fc = np.zeros(n, np.int16)
    counts = np.array(LP_FC_HIST, float)
    counts = counts / counts.sum() * n
    idx = rng.permutation(n)
    at = int(round(counts[1]))
    fc[idx[:at]] = 1
    fc[idx[at:at + int(round(counts[2]))]] = 2
    fc[idx[at + int(round(counts[2])):at + int(round(counts[2])) + 1]] = 3
    return (true_lens + fc).astype(np.int16), fc


def corrupt_sub(lens, p, rng):
    n = len(lens)
    out = lens.astype(np.int32).copy()
    hit = rng.random(n) < p
    d = rng.choice([-2, -1, 1, 2], size=n, p=[0.15, 0.35, 0.35, 0.15])
    out[hit] += d[hit]
    return np.clip(out, 1, 20).astype(np.int16)


def draw_indel(src, need, p_indel, rng):
    """walk src emitting words, randomly deleting one or inserting a plausible
    extra word, until `need` emitted -> the drifted 'other edition' """
    out = []
    i = 0
    pool = src
    while len(out) < need and i < len(src) - 1:
        r = rng.random()
        if r < p_indel / 2:
            i += 1                                   # deletion
            continue
        if r < p_indel:
            out.append(int(pool[rng.integers(0, len(pool))]))   # insertion
        out.append(int(src[i])); i += 1
    return np.array(out[:need], np.int16)


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    extra = tuple(sys.argv[2:])
    C, meta = skel.load_corpus(extra_globs=extra)
    lp, fc_lp = skel.lp2_words()
    P = len(lp)
    names = sorted(C, key=lambda k: -len(C[k]))
    print('stage %s | corpus %d texts %d words'
          % (stage, len(C), sum(len(v) for v in C.values())), flush=True)

    # three plant sources spanning size and register
    srcs = []
    for want in ('kjv', 'emerson', 'hermetic', 'blake', 'dhammapada'):
        for n in names:
            if want in n.lower() and len(C[n]) > 4 * P:
                srcs.append(n); break
    srcs = srcs[:3]
    print('plant sources:', srcs)

    pats, truth = [], {}

    # ---- T0: clean plants, both matchers ----------------------------------
    for si, s in enumerate(srcs if stage in ('all', 'T0') else []):
        arr = C[s]
        off = int(RNG.integers(0, len(arr) - P))
        true = arr[off:off + P]
        obs, fcp = plant(true, RNG)
        truth['T0_%d' % si] = dict(text=s, offset=off)
        pats.append(scanner.Pattern('T0_%d:exact' % si, skel.groups_slack(obs, 0), P))
        pats.append(scanner.Pattern('T0_%d:interval' % si,
                                    skel.groups_interval(obs, fcp), P))
        if si == 0:
            sh = RNG.permutation(P)
            pats.append(scanner.Pattern('T0null:exact',
                                        skel.groups_slack(obs[sh], 0), P))
            pats.append(scanner.Pattern('T0null:interval',
                                        skel.groups_interval(obs[sh], fcp[sh]), P))

    # ---- T0b: substitution curve (interval matcher) ------------------------
    s = srcs[0]; arr = C[s]
    off = int(RNG.integers(0, len(arr) - P))
    base_true = arr[off:off + P]
    SUBP = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70] if stage in ('all','T0b') else []
    for p in SUBP:
        t = corrupt_sub(base_true, p, RNG)
        obs, fcp = plant(t, RNG)
        nm = 'SUB_%02d' % int(p * 100)
        truth[nm] = dict(text=s, offset=off, p=p)
        pats.append(scanner.Pattern(nm + ':interval',
                                    skel.groups_interval(obs, fcp), P))

    # ---- T0c: indel curve, three windows ----------------------------------
    INDELP = [0.0, 0.001, 0.003, 0.01, 0.03]
    for W in ((P, 400, 120) if stage in ('all','T0c') else ()):
        for pi in INDELP:
            need = W
            o2 = int(RNG.integers(0, len(arr) - 4 * need - 10))
            drift = draw_indel(arr[o2:o2 + 4 * need + 10], need, pi, RNG)
            obs, fcp = plant(drift, RNG)
            nm = 'IND_W%d_%s' % (W, str(pi).replace('.', 'p'))
            truth[nm] = dict(text=s, offset=o2, p_indel=pi, W=W)
            pats.append(scanner.Pattern(nm + ':interval',
                                        skel.groups_interval(obs, fcp), W))
        # window-matched null
        o2 = int(RNG.integers(0, len(arr) - need - 10))
        d = arr[o2:o2 + W]
        obs, fcp = plant(d, RNG)
        sh = RNG.permutation(W)
        pats.append(scanner.Pattern('INDnull_W%d:interval' % W,
                                    skel.groups_interval(obs[sh], fcp[sh]), W))

    print('scanning %d patterns over corpus ...' % len(pats), flush=True)
    t0 = time.time()
    best, per_text = scanner.scan_corpus(C, pats, progress=60)
    print('scan %.1f min' % ((time.time() - t0) / 60))

    out = []
    for k, (b, tn, off) in sorted(best.items()):
        base = k.split(':')[0]
        W = P
        if base.startswith('IND_') or base.startswith('INDnull'):
            W = int(base.split('_W')[1].split('_')[0])
        tr = truth.get(base, {})
        hit = (tn == tr.get('text')) if tr else None
        row = dict(pattern=k, best=b, pct=100 * b / W, text=tn, offset=off,
                   window=W, truth=tr, found_right_text=hit)
        out.append(row)
        print('%-28s %6.0f/%4d (%5.1f%%)  %-42s @%d  %s'
              % (k, b, W, 100 * b / W, tn, off,
                 'RIGHT-TEXT' if hit else ('' if hit is None else 'wrong-text')))
    json.dump(dict(stage=stage, results=out, corpus_texts=len(C),
                   corpus_words=int(sum(len(v) for v in C.values())),
                   per_text_null={k: v for k, v in per_text.items()
                                  if 'null' in k}),
              open(os.path.join(HERE, 'positive_control_%s.json' % stage), 'w'), indent=1)
    print('wrote positive_control_%s.json' % stage)


if __name__ == '__main__':
    main()
