import os,itertools,numpy as np
exec(open("analysis/round30/A1-font/variant_cluster.py").read().split("if __name__")[0])
t=open('data/krisyotam_runes.txt').read().split('%')
kp=[parse(b) for b in t if parse(b)]
from collections import defaultdict
allg=defaultdict(list)
for pi in range(min(len(kp),54)):
    path=f'data/relikd/p{pi}.jpg'
    if not os.path.exists(path): continue
    for r,pos,m in extract(path,kp[pi]):
        if m.size>0: allg[r].append((pi,pos,m))
# For rune ᛗ find a pair that is byte-identical after best-shift
rune='ᛗ'
items=allg[rune]
ws=np.array([m.shape[1] for _,_,m in items]); mw=np.median(ws)
clean=[(pi,pos,m) for pi,pos,m in items if abs(m.shape[1]-mw)<=3]
found=0
for (p1,q1,a),(p2,q2,b) in itertools.combinations(clean,2):
    if a.shape==b.shape and np.array_equal(a,b):
        print(f'BYTE-IDENTICAL {rune}: p{p1}#{q1} == p{p2}#{q2} shape={a.shape} area={int(a.sum())}')
        found+=1
        if found>=3: break
print('byte-identical pairs found for',rune,':',found,'(of',len(clean),'clean)')
# Now the design-choice runes: is the choice FIXED across the book?
for rune in ['ᚷ','ᛄ','ᛝ','ᛞ']:
    items=allg[rune]
    ws=np.array([m.shape[1] for _,_,m in items]); ars=np.array([int(m.sum()) for _,_,m in items])
    mw,ma=np.median(ws),np.median(ars)
    clean=[m for _,_,m in items if 0.75*mw<=m.shape[1]<=1.3*mw and 0.75*ma<=int(m.sum())<=1.25*ma]
    # single-linkage at 0.90, report the fraction in the biggest cluster among 40 sampled
    import random
    cl,used=single_linkage(clean,0.90,cap=50)
    frac=len(cl[0])/len(used)
    print(f'{rune}: biggest-cluster fraction among sampled = {frac:.2f} (sizes {[len(c) for c in cl[:4]]})')
