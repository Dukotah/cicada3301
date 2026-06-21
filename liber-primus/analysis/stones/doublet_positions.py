"""Where do surviving doublets occur? Test for non-random structure."""
import sys, collections, math, random
sys.path.insert(0,'/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/stones')
from doublet_analysis import build, RUNE_TO_IDX, IDX_TO_TRANS, RUNES, N, F_IDX

pages = build()
scope = list(range(0,55))

# Recompute survivors WITH full positional context.
survivors=[]   # dict per doublet: page, line, stream_pos(in page), idx, dist_to_F, word_pos
all_adjacent=[] # baseline: every intra-word adjacent pair position
for pi in scope:
    recs=pages[pi]
    # build per-page absolute rune position & F positions
    fpos=[k for k,r in enumerate(recs) if r['idx']==F_IDX]
    # word index: increment when prec_sep in (word,sent,line,start)
    widx=0
    for k,r in enumerate(recs):
        if r['prec_sep'] in ('word','sent','line','start'):
            widx+=1; posinword=0
        else:
            posinword+=1
        r['word']=widx; r['posinword']=posinword; r['k']=k
    for j in range(1,len(recs)):
        cur=recs[j]; prev=recs[j-1]
        if cur['prec_sep'] is None:
            # distance to nearest F rune
            dF = min((abs(j-f) for f in fpos), default=9999)
            rec={'page':pi,'line':cur['line'],'k':j,'idx':cur['idx'],
                 'dF':dF,'posinword':cur['posinword'],'word':cur['word'],
                 'frac': j/max(1,len(recs)-1)}
            all_adjacent.append(rec)
            if cur['idx']==prev['idx']:
                survivors.append(rec)

print('survivors:',len(survivors),' baseline adjacent pairs:',len(all_adjacent))

# --- (1) Per-page residual rate: constant or variable? ---
print('\n=== Per-page doublet counts ===')
pg_adj=collections.Counter(); pg_dbl=collections.Counter()
for r in all_adjacent: pg_adj[r['page']]+=1
for r in survivors: pg_dbl[r['page']]+=1
rates=[]
for pi in scope:
    a=pg_adj[pi]; d=pg_dbl[pi]
    rate=d/a if a else 0
    rates.append((pi,a,d,rate))
# distribution
counts=[d for _,_,d,_ in rates]
print('mean doublets/page:',round(sum(counts)/len(counts),2),'min',min(counts),'max',max(counts))
# Poisson dispersion test: var/mean ~1 if random
m=sum(counts)/len(counts); v=sum((c-m)**2 for c in counts)/len(counts)
print('var/mean (Poisson index of dispersion):',round(v/m,3),'(=1 random)')
# expected per page if rate uniform
total_d=len(survivors); total_a=len(all_adjacent)
chi=0
for pi,a,d,rate in rates:
    exp=total_d*a/total_a
    if exp>=0.5: chi+=(d-exp)**2/exp
print('chi-sq per-page vs uniform-rate:',round(chi,2),'dof~',sum(1 for _,a,_,_ in rates if total_d*a/total_a>=0.5))
print('pages with >=4 doublets:',[(pi,d) for pi,a,d,rate in rates if d>=4])
print('pages with 0 doublets:',[pi for pi,a,d,rate in rates if d==0])

# --- (2) Position within page (frac): clustered at start/end? ---
print('\n=== Position-in-page (frac 0..1) ===')
fracs=[r['frac'] for r in survivors]
base_fracs=[r['frac'] for r in all_adjacent]
import statistics
print('survivor frac mean',round(statistics.mean(fracs),3),'baseline',round(statistics.mean(base_fracs),3))
# binned
for lo in [0,0.2,0.4,0.6,0.8]:
    sc=sum(1 for f in fracs if lo<=f<lo+0.2)
    bc=sum(1 for f in base_fracs if lo<=f<lo+0.2)
    exp=len(fracs)*bc/len(base_fracs)
    print(f'  [{lo:.1f},{lo+0.2:.1f}) obs={sc} exp={exp:.1f}')

# --- (3) Proximity to F interrupter ---
print('\n=== Distance to nearest F rune ===')
def hist_dF(recs):
    c=collections.Counter()
    for r in recs:
        d=r['dF']
        b=d if d<=3 else (5 if d<=6 else 10)
        c[b]+=1
    return c
sh=hist_dF(survivors); bh=hist_dF(all_adjacent)
for b in sorted(set(sh)|set(bh)):
    obs=sh[b]; basefrac=bh[b]/len(all_adjacent)
    exp=len(survivors)*basefrac
    print(f'  dF~{b}: obs={obs} exp={exp:.1f} base_n={bh[b]}')
# is a survivor itself an F doublet? (F-F)
ff=sum(1 for r in survivors if r['idx']==F_IDX)
print('F-F doublets among survivors:',ff)

# --- (4) Position within word ---
print('\n=== Position within word (posinword of 2nd rune) ===')
sp=collections.Counter(r['posinword'] for r in survivors)
bp=collections.Counter(r['posinword'] for r in all_adjacent)
for k in sorted(bp):
    exp=len(survivors)*bp[k]/len(all_adjacent)
    print(f'  pos{k}: obs={sp[k]} exp={exp:.1f} base={bp[k]}')

# --- (5) Cross-page line-position correlation ---
# Do doublets recur at the same line index across pages?
print('\n=== Doublet line-index distribution ===')
sl=collections.Counter(r['line'] for r in survivors)
print('top lines:',sl.most_common(8))
print('distinct lines used:',len(sl),'of survivors',len(survivors))

# --- Monte Carlo: are 60 survivors consistent with random thinning? ---
# Under "uniform random thinning of doublet candidates", survivors should
# look like a random subset of positions where, under independence, doublets
# would occur. We test clustering via nearest-neighbor gaps in global stream.
print('\n=== Monte Carlo clustering test (global stream gaps) ===')
# Build global ordered list of survivor global-positions
glob=[]
offset=0
pageoff={}
for pi in scope:
    pageoff[pi]=offset
    offset+=len(pages[pi])
spos=sorted(pageoff[r['page']]+r['k'] for r in survivors)
gaps=[spos[i+1]-spos[i] for i in range(len(spos)-1)]
print('survivor global gaps: min',min(gaps),'median',statistics.median(gaps),'max',max(gaps))
# CV of gaps; random (Poisson) => CV~1
cv=statistics.pstdev(gaps)/statistics.mean(gaps)
print('gap CV:',round(cv,3),'(~1 random/exponential; <1 regular; >1 clustered)')
adjacent_close=sum(1 for g in gaps if g<=5)
print('survivor pairs within 5 runes of each other:',adjacent_close)
