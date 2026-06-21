"""Doublet-residual micro-analysis for LP2 pages 0-54.

Records each rune with positional metadata, then analyzes the ~20% of
doublets (adjacent identical runes) that survive the anti-repeat rule.
"""
import sys, collections, math
sys.path.insert(0, '/mnt/c/Users/dukot/projects/cicada3301/liber-primus/src')
from lp.gematria import RUNE_TO_IDX, IDX_TO_TRANS, RUNES, N

RAW = open('/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/krisyotam_runes.txt', encoding='utf-8').read()
F_IDX = RUNE_TO_IDX['ᚠ']  # interrupter rune index 0

# Token model: walk char by char, tracking page, line, position-in-stream.
# Separators: '%' page, '\n' or '/' line, '-' word, '.' sentence.
# We build a per-page list of rune records that ALSO know what separator
# immediately precedes/follows them.
WORD_SEP = set(['-'])
SENT_SEP = set(['.'])
LINE_SEP = set(['\n', '/'])

def build():
    pages = RAW.split('%')
    out = []  # list of pages; each page = list of rune-records
    for pi, pg in enumerate(pages):
        recs = []
        line = 0
        pending_sep = 'start'  # separator type seen since last rune
        last_was_rune = False
        for ch in pg:
            if ch in RUNE_TO_IDX:
                recs.append({
                    'page': pi,
                    'idx': RUNE_TO_IDX[ch],
                    'rune': ch,
                    'line': line,
                    'prec_sep': pending_sep,  # what separated this rune from prev
                })
                pending_sep = None  # adjacent (no sep) until proven otherwise
                last_was_rune = True
            elif ch in LINE_SEP:
                line += 1
                pending_sep = 'line' if pending_sep in (None,'start') else pending_sep
                last_was_rune = False
            elif ch in WORD_SEP:
                pending_sep = 'word'
                last_was_rune = False
            elif ch in SENT_SEP:
                pending_sep = 'sent'
                last_was_rune = False
            # else ignore other chars
        out.append(recs)
    return out

def main():
    pages = build()
    # Restrict to unsolved set 0-54
    scope = list(range(0, 55))

    # --- Global stream of (idx, page, prec_sep) for in-scope pages ---
    # Doublet = two ADJACENT runes (no separator between) that are identical.
    # prec_sep == None means adjacent to previous rune.
    total_adjacent_pairs = 0
    doublet_pairs = 0
    per_rune_doublet = collections.Counter()
    per_rune_total = collections.Counter()  # count of rune at position i where i-1 adjacent
    survivor_records = []  # (page,line,idx,rune, context)

    # also count expected baseline doublets from rune frequency
    freq = collections.Counter()

    for pi in scope:
        recs = pages[pi]
        for r in recs:
            freq[r['idx']] += 1
        for j in range(1, len(recs)):
            cur = recs[j]; prev = recs[j-1]
            if cur['prec_sep'] is None:  # truly adjacent (within a word)
                total_adjacent_pairs += 1
                per_rune_total[prev['idx']] += 1
                if cur['idx'] == prev['idx']:
                    doublet_pairs += 1
                    per_rune_doublet[cur['idx']] += 1
                    survivor_records.append(cur)

    nrunes = sum(freq.values())
    print('=== SCOPE pages 0-54 ===')
    print('total runes:', nrunes)
    print('total adjacent (intra-word) pairs:', total_adjacent_pairs)
    print('observed doublets:', doublet_pairs, '=', round(100*doublet_pairs/total_adjacent_pairs,3),'%')

    # Expected doublet rate under independence (sum p_i^2) using global freq
    p = {i: freq[i]/nrunes for i in freq}
    exp_rate = sum(v*v for v in p.values())
    print('expected doublet rate (sum p_i^2):', round(100*exp_rate,3),'%')
    print('exp doublets:', round(exp_rate*total_adjacent_pairs,1))
    print('residual ratio obs/exp:', round(doublet_pairs/(exp_rate*total_adjacent_pairs),3))

    # --- Which runes survive as doublets vs expected? ---
    print('\n=== Per-rune doublet survival vs expected ===')
    print('rune  translit  obs  exp   obs/exp   freq')
    rows=[]
    for i in range(N):
        exp_i = total_adjacent_pairs * p.get(i,0)**2
        obs_i = per_rune_doublet.get(i,0)
        ratio = obs_i/exp_i if exp_i>0 else float('nan')
        rows.append((i, IDX_TO_TRANS[i], obs_i, exp_i, ratio, freq.get(i,0)))
    for i,tr,obs,exp,ratio,fr in sorted(rows,key=lambda x:-x[2]):
        print(f'{RUNES[i]}  {tr:<3}  {obs:>3}  {exp:>5.1f}  {ratio:>6.2f}   {fr}')

    # Chi-square: is survival uniform across runes (proportional to freq^2)?
    chi=0.0; dof=0
    for i,tr,obs,exp,ratio,fr in rows:
        if exp>=1:
            chi += (obs-exp)**2/exp
            dof+=1
    print(f'\nchi-square (doublet uniformity by freq): {chi:.2f}, cells>=1exp: {dof}')

    return pages, scope, survivor_records, doublet_pairs, total_adjacent_pairs

if __name__=='__main__':
    main()
