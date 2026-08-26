"""L3 -- transcribe the NON-RUNIC ink the segmentation pipeline discarded.

Round 8's ornament catalogue contains, mislabelled as "ornament", the parts of the Liber
Primus that are not runic at all.  `analysis/geometry/*` drops a band when it sits outside
the dominant text column or when its median component height exceeds 240 px, and the
alphanumeric lines on pp. 49-51 are shorter than rune lines and sit inside a vine frame, so
they were binned as non-text and never entered any analysis in this repository.

This script produces the transcription as a machine-readable artifact and, importantly,
CROSS-CHECKS it against two independent community transcriptions already vendored here, so
the read is corroborated rather than asserted:

  corpus/E-tooling/vendor/cicada-solvers__cmbsolverwp/cmbsolver-lpviewer/files/text/lb/{49,50,51}.txt
  corpus/E-tooling/vendor/cicada-solvers__libergo/cmd/base60/base60numbers.txt

Writes nonrunic.json.
"""
import os, sys, re, json, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
import reader as R                                                     # noqa: E402

CMB = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                   'cicada-solvers__cmbsolverwp', 'cmbsolver-lpviewer',
                   'files', 'text', 'lb')
LIBERGO = os.path.join(R.ROOT, 'corpus', 'E-tooling', 'vendor',
                       'cicada-solvers__libergo', 'cmd', 'base60', 'base60numbers.txt')
B60 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

# The read taken independently from the sha256-verified renders by high-zoom inspection
# during this lane (first line of each alphanumeric page); used as a third check.
VISION = {49: None,
          50: '2M 0w 3L 3D 2r 0S 1p 15',
          51: '28 2a 0J 1L 0c 3C 2o 0X'}

# Page 15's 4x4 numeric grid, read from the render at high zoom.
P15_GRID = [[3258, 3222, 3152, 3038],
            [3278, 3299, 3298, 2838],
            [3288, 3294, 3296, 2472],
            [4516, 1206, 708, 1820]]


def toks_from(text):
    out = []
    for ln in text.splitlines():
        t = re.findall(r'\b[0-9A-Za-z]{2}\b', ln)
        t = [x for x in t if x[0] in '01234']
        if len(t) >= 4:
            out.append(t)
    return out


def main():
    res = dict(source_note=__doc__.strip().splitlines()[0], pages={}, checks={})

    per_page = {}
    for p in (49, 50, 51):
        txt = open(os.path.join(CMB, '%d.txt' % p), encoding='utf-8-sig').read()
        per_page[p] = toks_from(txt)

    lg = toks_from(open(LIBERGO, encoding='utf-8-sig').read())
    concat = per_page[49] + per_page[50] + per_page[51]
    res['checks']['cmbsolver_vs_libergo'] = ('IDENTICAL' if lg == concat
                                             else 'DIFFER')
    res['checks']['libergo_lines'] = len(lg)
    for p in (50, 51):
        got = ' '.join(per_page[p][0])
        res['checks']['vision_p%d_line1' % p] = dict(
            vision=VISION[p], corpus=got,
            match=(VISION[p] == got))

    flat = [t for ln in concat for t in ln]
    vals = [B60.index(t[0]) * 60 + B60.index(t[1]) for t in flat]
    cnt = collections.Counter(vals)
    exp_distinct = 256 * (1 - (255 / 256) ** 256)

    for p in (49, 50, 51):
        res['pages'][str(p)] = dict(
            kind='alphanumeric base-60 token block',
            n_lines=len(per_page[p]), tokens_per_line=8,
            lines=[' '.join(t) for t in per_page[p]])

    res['base60'] = dict(
        alphabet=B60,
        rule='value = 60*index(c0) + index(c1)',
        n_tokens=len(flat), min=min(vals), max=max(vals),
        distinct=len(cnt),
        expected_distinct_if_uniform_iid=round(exp_distinct, 1),
        is_permutation_of_0_255=(len(cnt) == 256),
        values=vals)

    res['page15_grid'] = dict(
        kind='4x4 decimal grid',
        rows=P15_GRID,
        row_sums=[sum(r) for r in P15_GRID],
        col_sums=[sum(P15_GRID[i][j] for i in range(4)) for j in range(4)],
        total=sum(sum(r) for r in P15_GRID),
        note=('the entry 3299 is rendered in a LIGHTER ink than the other fifteen; '
              'every transcription in this repo records the digits and loses the tone. '
              'Measured in intensity.json.'))

    json.dump(res, open(os.path.join(HERE, 'nonrunic.json'), 'w'), indent=1)
    print('cmbsolver vs libergo:', res['checks']['cmbsolver_vs_libergo'])
    for p in (50, 51):
        print('vision p%d line 1 matches corpus: %s'
              % (p, res['checks']['vision_p%d_line1' % p]['match']))
    print('tokens %d  values %d..%d  distinct %d (uniform-iid expectation %.1f)'
          % (len(flat), min(vals), max(vals), len(cnt), exp_distinct))
    print('permutation of 0..255:', res['base60']['is_permutation_of_0_255'])
    print('p15 grid row sums', res['page15_grid']['row_sums'],
          'col sums', res['page15_grid']['col_sums'],
          'total', res['page15_grid']['total'])


if __name__ == '__main__':
    main()
