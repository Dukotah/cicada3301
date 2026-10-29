"""B2 Part C driver: reproduce T1 G-READ-LP1 with per-cell output. Mirrors g_read_lp1.main(); writes only here."""
import os, sys, json, difflib, collections, hashlib
sys.dont_write_bytecode = True
T1 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'round19', 'T1'))
sys.path.insert(0, T1)
OUT = os.path.dirname(os.path.abspath(__file__))
import numpy as np
import t1_reader as T, t1_extract as E_, t1_align as A, t1_run as R
T.VENDOR=os.path.join(OUT,"vendor_fetch")
WK=os.path.join(OUT,'work'); os.makedirs(WK,exist_ok=True)
for m in (E_,A,R): m.WORK=WK
from t1_match import Matcher
import g_read_lp1 as G
from lp.gematria import IDX_TO_TRANS
TR = [IDX_TO_TRANS[i] for i in range(29)]

def h(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()[:16] if os.path.exists(p) else None
guard = {f: h(os.path.join(T1, f)) for f in ('out_gread_lp1.json', 'out_gread_lp2.json')}

r2, v2 = R.build('LP2')
S2 = r2['S']
ids2 = np.array(sorted(k for k in r2['blab'] if k in S2.sm_pos))
M2 = Matcher(S2.X[[S2.sm_pos[int(k)] for k in ids2]], np.array([r2['blab'][int(k)] for k in ids2]))
S1 = A.Stream('LP1')
canonseq, marks = G.lp1_canon()
sm = S1.sm_idx
lab, bd0, bd1 = {}, {}, {}
for s in range(0, len(sm), 256):
    ch = sm[s:s+256]
    L, d0, d1 = M2.match(S1.X[[S1.sm_pos[int(b)] for b in ch]])
    for k, b in enumerate(ch):
        lab[int(b)] = int(L[k]); bd0[int(b)] = float(d0[k]); bd1[int(b)] = float(d1[k])
for it in range(6):
    pred = np.array([lab.get(int(b), A.OVERSIZE) for b in S1.ids])
    m, f = A.align_page(list(pred), canonseq)
    votes = collections.defaultdict(collections.Counter)
    for a, b in m + f:
        bm = int(S1.ids[a])
        if S1.small[bm]:
            votes[bm][canonseq[b]] += 1
    new = dict(lab)
    for b, c in votes.items():
        new[b] = c.most_common(1)[0][0]
    if new == lab:
        break
    lab = new
pred = np.array([lab.get(int(b), A.OVERSIZE) for b in S1.ids])
sm2 = difflib.SequenceMatcher(None, list(pred), canonseq, autojunk=False)
n = len(canonseq)
hit = np.zeros(n, bool); status = ['miss'] * n; glyph_of = [None] * n
wrong, missing, spurious = [], [], []
ops = sm2.get_opcodes()
for tag, i1, i2, j1, j2 in ops:
    if tag == 'equal':
        hit[j1:j2] = True
        for k in range(i2 - i1):
            status[j1+k] = 'equal'; glyph_of[j1+k] = i1+k
    elif tag == 'replace':
        if (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                status[j1+k] = 'wrong'; glyph_of[j1+k] = i1+k
        else:
            for k in range(j2 - j1): status[j1+k] = 'replace_unequal'
    elif tag == 'insert':
        for k in range(j2 - j1): status[j1+k] = 'missing'
eq = int(hit.sum())
print('G-READ-LP1 reproduced: %d/%d = %.4f%%' % (eq, n, 100.0*eq/n))
sec_of = lambda j: next(t for t, a, b in marks if a <= j < b)
def cell(i):
    b = int(S1.ids[i])
    return dict(glyph_idx=int(i), page=int(S1.page[i]), bitmap=b, width=int(S1.w[i]),
                bank_label=TR[lab.get(b)] if lab.get(b, 99) < 29 else None,
                d0=bd0.get(b), d1=bd1.get(b), margin_bank=(bd1[b]-bd0[b]) if b in bd0 else None)
rows = []
for j in range(n):
    if status[j] == 'equal': continue
    # nearest aligned glyph on each side for page attribution
    lo = next((glyph_of[x] for x in range(j-1, -1, -1) if glyph_of[x] is not None), None)
    hi = next((glyph_of[x] for x in range(j+1, n) if glyph_of[x] is not None), None)
    row = dict(canon_pos=j, section=sec_of(j), canon=TR[canonseq[j]], status=status[j],
               prev_aligned_page=int(S1.page[lo]) if lo is not None else None,
               next_aligned_page=int(S1.page[hi]) if hi is not None else None)
    if glyph_of[j] is not None:
        row['read'] = TR[int(pred[glyph_of[j]])] if int(pred[glyph_of[j]]) < 29 else '?'
        row['cell'] = cell(glyph_of[j])
    rows.append(row)
# spurious glyphs (delete ops)
spur = []
for tag, i1, i2, j1, j2 in ops:
    if tag in ('delete',):
        for i in range(i1, i2): spur.append(i)
    if tag == 'replace' and (i2-i1) != (j2-j1):
        pass
bypage = collections.Counter(int(S1.page[i]) for i in spur)
# lowest-margin aligned cells (bank-bootstrap margin d1-d0, LP2 bank), all aligned glyphs incl. correct
cells = []
for j in range(n):
    if glyph_of[j] is not None:
        c = cell(glyph_of[j]); c.update(canon_pos=j, section=sec_of(j), canon=TR[canonseq[j]], status=status[j],
                                        read=TR[int(pred[glyph_of[j]])] if int(pred[glyph_of[j]])<29 else '?')
        cells.append(c)
cells = [c for c in cells if c['margin_bank'] is not None]
cells.sort(key=lambda c: c['margin_bank'])
bysec = collections.Counter((r['section'], r['status']) for r in rows)
summ = dict(n_canon=n, correct=eq, accuracy=100.0*eq/n,
            statuses=dict(collections.Counter(status)),
            by_section_status={'%s|%s' % k: v for k, v in bysec.items()},
            spurious_glyphs_total=len(spur), spurious_by_page={str(k): v for k, v in sorted(bypage.items())},
            n_glyphs=int(S1.n), lp1_pages=[int(p) for p in S1.pages],
            guard_hashes_T1_outputs_before=guard)
json.dump(dict(summary=summ, misses=rows, lowest_margin_top20=cells[:20],
               n_aligned_cells=len(cells)), open(os.path.join(OUT, 'lp1_misses.json'), 'w'), indent=1)
guard2 = {f: h(os.path.join(T1, f)) for f in guard}
print('T1 output files untouched:', guard == guard2)
print(json.dumps(summ, indent=1)[:2500])

# ---- block diagnosis: SOME WISDOM canon[659:735] aligned ALONE against the whole LP1 glyph stream
blk = canonseq[659:735]
predl = [int(x) for x in pred]
sb = difflib.SequenceMatcher(None, predl, blk, autojunk=False)
mb = sb.get_matching_blocks()
tot = sum(b.size for b in mb)
longest = max(mb, key=lambda b: b.size)
pgs = collections.Counter(int(S1.page[b.a + k]) for b in mb for k in range(b.size))
# also: full-stream alignment WITH the block removed from canon, to see if rest is unaffected
canon_wo = canonseq[:659] + canonseq[735:]
sm3 = difflib.SequenceMatcher(None, predl, canon_wo, autojunk=False)
eq3 = sum(b.size for b in sm3.get_matching_blocks())
diag = dict(block_canon_range=[659, 735], block_len=len(blk), block_text=''.join(TR[c] for c in blk),
            alone_matched=int(tot), alone_longest=[int(longest.a), int(longest.b), int(longest.size)],
            alone_matched_by_image_page={str(k): v for k, v in sorted(pgs.items())},
            rest_without_block_correct=int(eq3), rest_without_block_n=len(canon_wo),
            rest_without_block_pct=100.0*eq3/len(canon_wo),
            page_glyph_counts={str(p): int((S1.page == p).sum()) for p in S1.pages})
d = json.load(open(os.path.join(OUT, 'lp1_misses.json'))); d['block_diagnosis'] = diag
json.dump(d, open(os.path.join(OUT, 'lp1_misses.json'), 'w'), indent=1)
print(json.dumps(diag, indent=1))
