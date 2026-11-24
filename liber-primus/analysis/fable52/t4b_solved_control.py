# T4b: does the word-length ORDER test have power against Cicada's OWN register? Solved-LP reference (875 words) vs
# 875-word windows of the unsolved book and of English controls, same MI statistic and shuffle null.
import sys,os,random,math,re,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2, gp
random.seed(99)
def clip(n): return min(n,7)
def MI(L):
    n=len(L)-1; j=collections.Counter(zip(L,L[1:])); a=collections.Counter(L[:-1]); b=collections.Counter(L[1:])
    return sum(c/n*math.log(c*n/(a[x]*b[y])) for (x,y),c in j.items())
def z(L,R=400):
    o=MI(L); s=[]
    for _ in range(R):
        M=L[:]; random.shuffle(M); s.append(MI(M))
    m=sum(s)/R; sd=(sum((v-m)**2 for v in s)/R)**.5; return (o-m)/sd,(sum(v>=o for v in s)+1)/(R+1)
ref=open(r'C:\Users\dukot\AppData\Local\Temp\lpx\r\resources\liber-primus\lp1-plaintext-reference.txt',encoding='utf8').read()
secs=[];cur=[]
for line in ref.splitlines():
    if line.startswith('#'):
        if cur: secs.append(cur); cur=[]
        continue
    cur+=[len(gp.to_runes(w)) for w in re.findall(r"[A-Za-z]+",line) if gp.to_runes(w)]
if cur: secs.append(cur)
lw=[x for s in secs for x in s]; n=len(lw)
print('solved-LP reference: %d words in %d sections; mean len %.2f; MI z=%.2f p=%.3f'%(n,len(secs),sum(lw)/n,*z([clip(x) for x in lw])))
out,canon=load2.stream(); S=out[:12956]
W=[]; c=0
for i,x in enumerate(S):
    if i>0 and any(ch in x['sep'] for ch in '-.&$§'): W.append(c); c=0
    c+=1
W.append(c)
zs=[z([clip(x) for x in W[st:st+n]],150)[0] for st in range(0,len(W)-n,250)]
print('unsolved, %d-word windows (step 250): z values'%n,[round(v,2) for v in zs])
print('unsolved whole book (clip 7): z=%.2f p=%.3f'%z([clip(x) for x in W]))
for fn in ('pride.txt','kjv.txt','moby.txt'):
    ws=gp.load_text(fn); v=[]
    for k in range(12):
        st=random.randrange(0,len(ws)-n); v.append(z([clip(len(w)) for w in ws[st:st+n]],150)[0])
    v.sort(); print('control %s %d-word windows: z min %.2f med %.2f max %.2f'%(fn,n,v[0],v[6],v[-1]))
# scaled expectation: if unsolved had the solved-LP per-word MI excess, expected z at 2896 words:
zl=z([clip(x) for x in lw])[0]; print('solved-LP z scaled to 2,896 words (x n ratio): about %.1f'%(zl*2896/n))
