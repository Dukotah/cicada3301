import sys,os,collections,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2
out,canon=load2.stream(); S=out[:12956]
N=len(S)
cat=collections.Counter(); dub=collections.Counter()
pos=[]
for i in range(1,N):
    sep=S[i]['sep']
    keys=['all']
    keys.append('inword' if not any(c in sep for c in '-.&$%§') and not any(c.isdigit() for c in sep) else 'crossword')
    if '-' in sep and '.' not in sep: keys.append('dash')
    if '.' in sep: keys.append('period')
    if '/' in sep: keys.append('linebreak')
    if '/' in sep and not any(c in sep for c in '-.&$%'): keys.append('linebreak_inword')
    if '%' in sep: keys.append('pagebreak')
    if '&' in sep or '$' in sep: keys.append('sectionbreak')
    d=S[i]['v']==S[i-1]['v']
    if d: pos.append(i)
    for k in keys:
        cat[k]+=1; dub[k]+=d
print('N',N,'doublets',dub['all'])
for k in cat:
    n=cat[k]; x=dub[k]; e=n/29
    print(f'{k:18s} pairs={n:6d} doublets={x:3d} rate={100*x/n:5.2f}% expected_uniform={e:6.1f} ratio={x/e:4.2f}')
# per page
pp=collections.Counter(S[i]['page'] for i in pos); pn=collections.Counter(x['page'] for x in S)
print('per-page doublets:',[(p,pp.get(p,0)) for p in range(55)])
# values
print('doubled rune values:',sorted(collections.Counter(S[i]['v'] for i in pos).items()))
# position in word of doublet (index of 2nd rune within word) & word len
import json
json.dump(pos,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'doublet_positions.json'),'w'))  # R46-A1: was cwd-relative
# difference histogram
dh=collections.Counter((S[i]['v']-S[i-1]['v'])%29 for i in range(1,N))
print('diff hist:',[dh[d] for d in range(29)])
exp=(N-1-dh[0])/28; chi=sum((dh[d]-exp)**2/exp for d in range(1,29)); print('chi2 nonzero diffs (27 df):',round(chi,1))
for lag in range(2,8):
    c=sum(S[i]['v']==S[i-lag]['v'] for i in range(lag,N)); print('lag',lag,'equal',c,'exp',round((N-lag)/29,1))
