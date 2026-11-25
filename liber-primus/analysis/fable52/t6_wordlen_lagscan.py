# T6: generic word-level transposition detector. English adjacent word lengths anticorrelate (r ~ -0.08..-0.19).
# Any transposition that moves originally-adjacent words to a (mostly) constant offset k shows that anticorrelation at lag k.
# Scan lag 1..1448 on the 2,896 printed word lengths; null = min z over the same scan on shuffles. Plus solved-LP lag-1 control.
import sys,os,random,math,re,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2, gp
random.seed(606)
out,canon=load2.stream(); S=out[:12956]
W=[]; cur=0
for i,x in enumerate(S):
    if i>0 and any(c in x['sep'] for c in '-.&$§'): W.append(cur); cur=0
    cur+=1
W.append(cur)
def scan(L,K):
    n=len(L); m=sum(L)/n; v=sum((x-m)**2 for x in L)/n; d=[x-m for x in L]; res=[]
    for k in range(1,K+1):
        r=sum(d[i]*d[i+k] for i in range(n-k))/((n-k)*v); res.append(r*math.sqrt(n-k))
    return res
K=1448
z=scan(W,K); zmin=min(z); kmin=z.index(zmin)+1; zmax=max(z)
nul=[]
for _ in range(60):
    M=W[:]; random.shuffle(M); nul.append(min(scan(M,K)))
nul.sort(); print('unsolved: min z=%.2f at lag %d ; max z=%.2f ; null min-z 5%% quantile=%.2f median=%.2f ; p(min)=%.3f'%(zmin,kmin,zmax,nul[3],nul[30],(sum(x<=zmin for x in nul)+1)/61))
print('  lag1..6 z:',[round(x,2) for x in z[:6]])
# positive control: English window, word-columnar transposition with C columns (read off column by column), then scan
ws=gp.load_text('pride.txt')
for C in (2,7,29,56):
    det=0; fracs=[]
    for t in range(6):
        st=random.randrange(0,len(ws)-2896); L=[len(w) for w in ws[st:st+2896]]
        T=[L[i] for c in range(C) for i in range(c,len(L),C)]
        zz=scan(T,K); det+=min(zz)<=nul[3]; fracs.append(min(zz))
    print('  control: pride + %d-column word transposition: detected %d/6 ; typical min z %.1f'%(C,det,sorted(fracs)[3]))
# dose: only a fraction f of the book is ordered English (rest shuffled), 7 columns
for f in (0.5,0.3):
    det=0
    for t in range(6):
        st=random.randrange(0,len(ws)-2896); L=[len(w) for w in ws[st:st+2896]]
        idx=[i for i in range(len(L)) if random.random()>f]; vals=[L[i] for i in idx]; random.shuffle(vals)
        for i,v in zip(idx,vals): L[i]=v
        T=[L[i] for c in range(7) for i in range(c,len(L),7)]
        det+=min(scan(T,K))<=nul[3]
    print('  dose f=%.1f: detected %d/6'%(f,det))
# solved-LP control at lag 1 (the other repo's LP1 plaintext reference, Latin transliteration -> GP rune lengths)
# R46-A1: was the external lpx clone; the W1 inputs/ copy is sha256-identical (902e9db8...).
ref=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','round45','W1-spaces','inputs','lp1-plaintext-reference.txt'),encoding='utf8').read()
lw=[len(gp.to_runes(w)) for line in ref.splitlines() if not line.startswith('#') for w in re.findall(r"[A-Za-z]+",line)]
lw=[x for x in lw if x]
zz=scan(lw,3); print('solved LP reference: %d words, lag-1 r=%.3f z=%.2f'%(len(lw),zz[0]/math.sqrt(len(lw)-1),zz[0]))
