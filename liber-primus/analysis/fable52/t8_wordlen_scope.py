# T8: if the printed word lengths are the true plaintext word lengths SHUFFLED within some scope (sentence/page/chapter),
# local composition survives: unit-to-unit heterogeneity of the length distribution exceeds a global-shuffle null.
# Statistic: between-unit sum of squares of word length (ANOVA), and of the indicator len<=2. Null: global shuffle of lengths.
import sys,os,random,math,re,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2, gp
random.seed(808)
out,canon=load2.stream(); S=out[:12956]
W=[]; U={'page':[], 'sentence':[], 'chapter':[], 'block100':[]}
c=0; page=0; sent=0; chap=0
def push():
    W.append(c); U['page'].append(page); U['sentence'].append(sent); U['chapter'].append(chap); U['block100'].append((len(W)-1)//100)
for i,x in enumerate(S):
    sep=x['sep']
    if i>0 and any(ch in sep for ch in '-.&$§'): push(); c=0
    if i>0:
        if '.' in sep: sent+=1
        if '&' in sep or '$' in sep: chap+=1
    if '%' in sep and i>0: page+=1   # word assigned to page where it ends (approx.)
    c+=1
push()
print('words',len(W),'pages',len(set(U['page'])),'sentences',len(set(U['sentence'])),'chapters(&/$ runs)',len(set(U['chapter'])))
def ssb(L,lab,f=lambda v:v):
    g=collections.defaultdict(list)
    for v,l in zip(L,lab): g[l].append(f(v))
    m=sum(f(v) for v in L)/len(L)
    return sum(len(a)*(sum(a)/len(a)-m)**2 for a in g.values())
def test(L,lab,R=500):
    res=[]
    for f in (lambda v:v, lambda v:1.0*(v<=2)):
        o=ssb(L,lab,f); s=[]
        for _ in range(R):
            M=L[:]; random.shuffle(M); s.append(ssb(M,lab,f))
        m=sum(s)/R; sd=(sum((v-m)**2 for v in s)/R)**.5; res.append(((o-m)/sd,(sum(v>=o for v in s)+1)/(R+1)))
    return res
for k in U:
    r=test(W,U[k]); print('unsolved by %-9s: length z=%+.2f p=%.3f ; short-word-share z=%+.2f p=%.3f'%(k,r[0][0],r[0][1],r[1][0],r[1][1]))
for fn in ('pride.txt','kjv.txt','moby.txt','war.txt'):
    ws=gp.load_text(fn); acc=collections.defaultdict(list)
    for t in range(6):
        st=random.randrange(0,len(ws)-len(W)); L=[len(w) for w in ws[st:st+len(W)]]
        for k in U: acc[k].append(test(L,U[k],150)[0][0])
    print('control %-9s (same unit labels) length z, median over 6 windows:'%fn,{k:round(sorted(v)[3],1) for k,v in acc.items()},' min:',{k:round(min(v),1) for k,v in acc.items()})
