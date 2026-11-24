# T4: word-length ORDER grammar (adjacent-length MI vs within-chapter shuffle) on unsolved LP2, with English + solved-LP controls.
# T5: is T7 (doublet-gap lag-1 autocorrelation) what PLAINTEXT-coupled rare events look like? English rare-rune / plaintext-doublet gap autocorr.
import sys,os,json,random,math,collections,re
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2
random.seed(5252)
D=r'C:\Users\dukot\projects\cicada3301\liber-primus\data'
TR=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
DG={'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
SG={c:i for i,c in enumerate(TR) if len(c)==1}; SG.update({'K':5,'Q':5,'V':1,'Z':15})
def to_runes(word):
    w=word.upper(); out=[]; i=0
    while i<len(w):
        if w[i:i+3]=='ING': out.append(21); i+=3; continue
        if w[i:i+2] in DG: out.append(DG[w[i:i+2]]); i+=2; continue
        if w[i] in SG: out.append(SG[w[i]])
        i+=1
    return out
def load_text(fn):
    t=open(os.path.join(D,fn),encoding='utf8',errors='ignore').read()
    t=t[len(t)//20:]  # skip front matter
    words=[to_runes(w) for w in re.findall(r"[A-Za-z]+",t)]
    return [w for w in words if w]
def clip(n): return min(n,9)
def MI(L):
    n=len(L)-1; j=collections.Counter(zip(L,L[1:])); a=collections.Counter(L[:-1]); b=collections.Counter(L[1:])
    return sum(c/n*math.log(c*n/(a[x]*b[y])) for (x,y),c in j.items())
def r1len(L):
    x=L[:-1]; y=L[1:]; n=len(x); mx=sum(x)/n; my=sum(y)/n
    return sum((p-mx)*(q-my) for p,q in zip(x,y))/math.sqrt(sum((p-mx)**2 for p in x)*sum((q-my)**2 for q in y))
def ztest(L,stat,R=300):
    o=stat(L); s=[]
    for _ in range(R):
        M=L[:]; random.shuffle(M); s.append(stat(M))
    m=sum(s)/R; sd=(sum((v-m)**2 for v in s)/R)**.5
    return o,m,(o-m)/sd,(sum(v>=o for v in s)+1)/(R+1)
# unsolved word lengths (words continue across line/page wraps; separators - . & $ end a word)
out,canon=load2.stream(); S=out[:12956]
W=[]; cur=0
for i,x in enumerate(S):
    if i>0 and any(c in x['sep'] for c in '-.&$§') : W.append(cur); cur=0
    cur+=1
W.append(cur)
print('unsolved words',len(W),'len2',W.count(2),'len1',W.count(1),'mean',round(sum(W)/len(W),3))
Lc=[clip(w) for w in W]
print('T4 unsolved: MI obs=%.5f null=%.5f z=%+.2f p=%.3f'%ztest(Lc,MI),' | lag1 r obs=%.4f null=%.4f z=%+.2f p(upper)=%.3f'%ztest(W,r1len))
texts={fn:load_text(fn) for fn in ('kjv.txt','moby.txt','pride.txt','war.txt')}
for fn,ws in texts.items():
    zs=[];rs=[]
    for k in range(8):
        st=random.randrange(0,len(ws)-2896); L=[len(w) for w in ws[st:st+2896]]
        zs.append(ztest([clip(v) for v in L],MI,120)[2]); rs.append(r1len(L))
    print('  control %-10s MI z over 8 windows: min %+.1f med %+.1f ; lag1 r: min %+.3f max %+.3f'%(fn,min(zs),sorted(zs)[4],min(rs),max(rs)))
# power at reduced dose: a window where a fraction f of word boundaries is real English and the rest of the lengths are shuffled
ws=texts['pride.txt']
for f in (1.0,0.5,0.25):
    det=0
    for k in range(20):
        st=random.randrange(0,len(ws)-2896); L=[clip(len(w)) for w in ws[st:st+2896]]
        idx=[i for i in range(len(L)) if random.random()>f]; vals=[L[i] for i in idx]; random.shuffle(vals)
        for i,v in zip(idx,vals): L[i]=v
        det+=ztest(L,MI,100)[3]<=0.05
    print('  power (pride, fraction of words left in natural order=%.2f): %.2f'%(f,det/20))
# ---------------- T5 ----------------
def r1(P):
    g=[b-a for a,b in zip(P,P[1:])]
    if len(g)<10: return None
    x=g[:-1]; y=g[1:]; n=len(x); mx=sum(x)/n; my=sum(y)/n
    sx=sum((a-mx)**2 for a in x); sy=sum((b-my)**2 for b in y)
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sx*sy) if sx and sy else None
N=12956; OBS=0.380
print('\nT5: gap lag-1 autocorrelation of plaintext-coupled rare events in English (window = 12,956 runes), observed LP2 T7 = +0.380')
allr=collections.defaultdict(list)
for fn,ws in texts.items():
    flat=[r for w in ws for r in w]
    wstart=set(); p=0
    for w in ws: wstart.add(p); p+=len(w)
    for k in range(40):
        st=random.randrange(0,len(flat)-N); seg=flat[st:st+N]
        # (a) each rune as marker, if its count in window is 40..200
        cnt=collections.Counter(seg)
        for v,c in cnt.items():
            if 40<=c<=200:
                r=r1([i for i,x in enumerate(seg) if x==v]); 
                if r is not None: allr['rune-marker'].append(r)
        # (b) plaintext adjacent doublets thinned to ~86 (independent thinning keeps burstiness scale > gap)
        dp=[i for i in range(1,N) if seg[i]==seg[i-1]]
        if len(dp)>=86:
            allr['pt-doublet(all,n~%d)'%0].append(r1(dp))
            allr['pt-doublet thinned to 86'].append(r1(sorted(random.sample(dp,86))))
        # (c) Bernoulli reference
        allr['bernoulli-86'].append(r1(sorted(random.sample(range(1,N),86))))
for k,v in allr.items():
    v=sorted(x for x in v if x is not None); n=len(v)
    print('  %-26s n=%4d  median %+.3f  5%%..95%% [%+.3f,%+.3f]  frac >= 0.380: %.3f'%(k,n,v[n//2],v[int(.05*n)],v[int(.95*n)],sum(x>=OBS for x in v)/n))
