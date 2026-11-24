# R45-X1 audit of W1: is LP2's "no order" an artifact of segmentation?  Recompute A_global (LLR, MI) under
# alternative segmentations: (S0) W1 canonical; (S1) line breaks also break words; (S2) page breaks also break;
# (S3) line-wrapped words dropped (only words wholly on one line kept, adjacency only between consecutive kept words
# on the same line).  Same English LLR model as W1 (first halves of 8 corpora).  Global-shuffle null, 2000 draws.
import sys, os, random, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'W1-spaces'))
import w1lib as w

def words_from(runes, extra):
    # rebuild word lengths from rune records with extra break conditions
    out = []; cur = 0; online = []
    for x in runes:
        b = x['brk_before'] or ('line' in extra and x['line_before']) or ('page' in extra and x['page_before'])
        if b and cur: out.append(cur); cur = 0
        cur += 1
    if cur: out.append(cur)
    return out

def single_line_words(runes):
    # sequences of words wholly inside one line; list of per-line lists
    lines = []; cur = 0; wrapped = False; line = []
    for x in runes:
        if x['brk_before'] or x['line_before']:
            if cur and not wrapped: line.append(cur)
            if x['line_before'] and not x['brk_before']:
                wrapped = True  # the next word starts mid-word
            elif x['brk_before']:
                wrapped = False
            if x['line_before']:
                lines.append(line); line = []
            cur = 0
        cur += 1
    lines.append(line)
    return lines

def stat_seq(L, S):
    C = [w.cls(n) for n in L]
    return w.llr(C, S), w.mi(C)

def test(L, S, draws, rng):
    o = stat_seq(L, S); nl = []; nm = []
    M = L[:]
    for _ in range(draws):
        rng.shuffle(M); a, b = stat_seq(M, S); nl.append(a); nm.append(b)
    zl = w.zp(o[0], nl); zm = w.zp(o[1], nm)
    return dict(n=len(L), LLR_z=round(zl[0], 2), LLR_p=round(zl[1], 4), MI_z=round(zm[0], 2), MI_p=round(zm[1], 4),
                mean_len=round(sum(L) / len(L), 3), frac2=round(sum(1 for v in L if v == 2) / len(L), 4))

def main():
    rng = random.Random(4545)
    seqs = []
    for fn in w.CORPORA:
        c = w.load_corpus(fn); seqs.append([w.cls(n) for n, s in c[:len(c) // 2]])
    S = w.train_llr(seqs)
    r2, _ = w.load_lp2(); r1, _ = w.load_lp1(); rs, _ = w.load_lp2_solved()
    out = {}
    for name, R in (('LP2', r2), ('solved', r1 + rs)):
        for seg, extra in (('S0_canonical', ()), ('S1_line_breaks', ('line',)), ('S2_page_breaks', ('page',))):
            L = words_from(R, extra)
            out[name + '/' + seg] = test(L, S, 2000, rng)
            print(name, seg, out[name + '/' + seg], flush=True)
    json.dump(out, open('x1_w1_segmentation.json', 'w'), indent=1)

if __name__ == '__main__':
    main()
