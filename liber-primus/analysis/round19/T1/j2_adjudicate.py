"""JOB 2 (PREREG section 6) -- adjudicate the 450 located O/A/AE disagreements.

Locating them.  `independent-read/oae_mismatch.json` stores each record as
(page_image, line_in_image, pos_in_line, global_line, global_glyph_index) in the
segmented-glyph index space of `analysis/stones/`.  `stones/pipeline.global_lines()`
builds the same 594-line global sequence from `krisyotam_runes.txt`, so

    canon_page = page_of[global_line]
    cpos       = (runes in earlier lines of that page) + pos_in_line

puts every record in this lane's coordinates.  GATE: the canon rune at the located
position must equal the record's own `canon` field, for all 450.  Records that fail are
reported UNLOCATABLE and counted; none are silently re-aligned.

Then the located crop's call is read off this lane's corpus pass -- the same
`read_page()` that scored 180/180 on the solved control pages and 99.98% under
leave-one-bitmap-out.
"""
import os, sys, json, collections
import numpy as np
import t1_reader as T, t1_align as A
sys.path.insert(0, os.path.join(T.LP, 'src'))
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS  # noqa: E402

TR = [IDX_TO_TRANS[i] for i in range(29)]
RUNES = set('ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ')
MM = os.path.join(T.LP, 'analysis', 'independent-read', 'oae_mismatch.json')


def global_lines():
    """Verbatim analysis/stones/pipeline.py: the 594-line global sequence, pages 0-54."""
    t = open(os.path.join(T.LP, 'data', 'krisyotam_runes.txt'), encoding='utf-8').read()
    kch = t.split('%')
    lines, page_of = [], []
    for p in range(55):
        for l in kch[p].split('/'):
            seq = [c for c in l if c in RUNES]
            if seq:
                lines.append(seq)
                page_of.append(p)
    return lines, page_of


def canon2img(ce):
    """canonical_pages.json entry -> relikd image page (image p50 is the blank page)."""
    return ce if ce <= 49 else ce + 1


def main():
    lines, page_of = global_lines()
    # offset of each global line inside its own page
    off, seen = [], collections.Counter()
    for gl, p in enumerate(page_of):
        off.append(seen[p])
        seen[p] += len(lines[gl])

    recs = json.load(open(MM, encoding='utf-8'))
    canon = T.canon_pages()
    z = np.load(os.path.join(T.HERE, 'work', 'corpus_lp2.npz'), allow_pickle=True)
    read = {}
    for i in range(len(z['page'])):
        read[(int(z['page'][i]), int(z['cpos'][i]))] = i

    # margin cut, fixed from the control pages BEFORE the 450 are looked at (PREREG 6.3)
    g = json.load(open(os.path.join(T.HERE, 'out_gread_lp2.json')))
    cm = [m for m, ok in g['margins']]
    CUT = float(min(cm))
    print('control-set margin (d1-d0): n=%d  min %.0f  p50 %.0f  -- all %d control calls'
          ' correct, so the DECIDED cut is the control minimum, %.0f'
          % (len(cm), min(cm), np.median(cm), len(cm), CUT))

    out, tally = [], collections.Counter()
    dirn = collections.Counter()
    for r in recs:
        gl = int(r['global_line'])
        ce = page_of[gl]
        cpos = off[gl] + int(r['pos_in_line'])
        cr = canon.get(ce, '')
        located = cpos < len(cr) and cr[cpos] == r['canon']
        img = canon2img(ce)
        row = dict(record_page_image=int(r['page_image']),
                   record_line_in_image=int(r['line_in_image']),
                   record_pos_in_line=int(r['pos_in_line']),
                   global_line=gl, canon_page=int(ce), image_page=int(img),
                   cpos=int(cpos),
                   canon_call=IDX_TO_TRANS[RUNE_TO_IDX[r['canon']]],
                   clusterer_call=IDX_TO_TRANS[RUNE_TO_IDX[r['looks_like']]],
                   unsolved_page=bool(ce <= 54))
        if not located:
            row.update(verdict='UNLOCATABLE', t1_call=None, d0=None, d1=None,
                       margin=None, confidence=None)
            tally['UNLOCATABLE'] += 1
            out.append(row); continue
        k = read.get((img, cpos))
        if k is None:
            row.update(verdict='UNLOCATABLE', t1_call=None, d0=None, d1=None,
                       margin=None, confidence=None, note='canon position not aligned '
                       'to any segmented glyph in the T1 corpus pass')
            tally['UNLOCATABLE'] += 1
            out.append(row); continue
        t1 = TR[int(z['t1'][k])]
        d0 = float(z['d0'][k]); d1 = float(z['d1'][k])
        margin = (d1 - d0) if d1 >= 0 else float('inf')
        decided = margin >= CUT
        agree = (t1 == row['canon_call'])
        verdict = ('AGREE' if agree else 'DISAGREE') if decided else 'UNDECIDABLE'
        row.update(t1_call=t1, d0=d0, d1=(d1 if d1 >= 0 else None),
                   margin=(margin if np.isfinite(margin) else None),
                   kind=str(z['kind'][k]),
                   confidence=('HIGH' if margin >= 10 * CUT else
                               'MEDIUM' if decided else 'LOW'),
                   verdict=verdict)
        tally[verdict] += 1
        dirn['%s->%s' % (row['canon_call'], row['clusterer_call'])] += 1
        out.append(row)

    print('\nlocation gate: %d/%d located (%d UNLOCATABLE)'
          % (len(recs) - tally['UNLOCATABLE'], len(recs), tally['UNLOCATABLE']))
    print('clusterer direction breakdown (cross-check vs T3: A->O 306, O->A 72,'
          ' AE->A 70, A->AE 2):')
    for k, v in dirn.most_common():
        print('   %-8s %d' % (k, v))
    print('\nVERDICTS: ' + '  '.join('%s=%d' % (k, v) for k, v in tally.most_common()))

    dis = [r for r in out if r['verdict'] == 'DISAGREE']
    print('\nT1 disagrees with canon at %d of the 450.' % len(dis))
    for r in dis:
        print('   image p%-2d cpos %5d canon=%-3s clusterer=%-3s T1=%-3s d0=%.0f margin=%s'
              % (r['image_page'], r['cpos'], r['canon_call'], r['clusterer_call'],
                 r['t1_call'], r['d0'], r['margin']))
    agree_with_canon = sum(1 for r in out if r['verdict'] == 'AGREE')
    agree_with_clu = sum(1 for r in out if r['verdict'] == 'DISAGREE'
                         and r['t1_call'] == r['clusterer_call'])
    print('\nT1 sides with CANON at %d/%d located positions (%.4f%%)'
          % (agree_with_canon, len(recs) - tally['UNLOCATABLE'],
             100.0 * agree_with_canon / max(1, len(recs) - tally['UNLOCATABLE'])))
    print('T1 sides with the CLUSTERER at %d' % agree_with_clu)
    print('margins at the 450: min %.0f  p1 %.0f  p50 %.0f'
          % tuple(np.percentile([r['margin'] for r in out if r['margin'] is not None],
                                [0, 1, 50])))
    json.dump(dict(cut=CUT, tally=dict(tally), direction=dict(dirn),
                   n_records=len(recs), rows=out),
              open(os.path.join(T.HERE, 'adjudication.json'), 'w'), indent=1)
    print('-> adjudication.json')


if __name__ == '__main__':
    main()
