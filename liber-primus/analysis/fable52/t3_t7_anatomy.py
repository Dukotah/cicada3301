# T7 anatomy: (a) is r=+0.38 one void or a distributed property? (b) power of the other group's
# per-printed-line-count conditioned null (is p=0.23 informative or over-conditioned?)
import sys,os,json,random,math,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import load2
out,canon=load2.stream(); S=out[:12956]; N=len(S)
pos=[i for i in range(1,N) if S[i]['v']==S[i-1]['v']]
def r1(P):
    g=[b-a for a,b in zip(P,P[1:])]; x=g[:-1]; y=g[1:]; n=len(x)
    if n<3: return 0
    mx=sum(x)/n; my=sum(y)/n
    sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); sx=sum((a-mx)**2 for a in x); sy=sum((b-my)**2 for b in y)
    return sxy/math.sqrt(sx*sy) if sx>0 and sy>0 else 0
def rank_r1(P):
    g=[b-a for a,b in zip(P,P[1:])]
    order=sorted(range(len(g)),key=lambda i:g[i]); rk=[0]*len(g)
    for k,i in enumerate(order): rk[i]=k
    x=rk[:-1]; y=rk[1:]; n=len(x); mx=sum(x)/n; my=sum(y)/n
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
g=[b-a for a,b in zip(pos,pos[1:])]
print('T7 r1 =',round(r1(pos),4),' rank(Spearman-like) r1 =',round(rank_r1(pos),4))
big=sorted(range(len(g)),key=lambda i:-g[i])[:5]; print('largest gaps (idx,gap,start):',[(i,g[i],pos[i]) for i in big])
# drop-the-void: remove sites so the three big gaps merge? Instead: winsorize gaps at 300
gw=[min(x,300) for x in g]
def r_of(g):
    x=g[:-1]; y=g[1:]; n=len(x); mx=sum(x)/n; my=sum(y)/n
    return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
print('r1 with gaps winsorized at 300:',round(r_of(gw),4),'; r1 of log gaps:',round(r_of([math.log(x) for x in g]),4))
# r1 excluding the void region (sites before 2700 and after 4400 treated as two separate series, pooled deviations)
A=[p for p in pos if p<2741]; B=[p for p in pos if p>4380]
print('r1 before void (n=%d): %.3f ; after void (n=%d): %.3f'%(len(A),r1(A),len(B),r1(B)))
random.seed(7)
R=4000
def pval(stat,obs,gen): 
    c=sum(stat(gen())>=obs for _ in range(R)); return (c+1)/(R+1)
uni=lambda: sorted(random.sample(range(1,N),len(pos)))
print('uniform null: p(r1)=%.4f p(rank r1)=%.4f p(log-gap r1)=%.4f'%(pval(r1,r1(pos),uni),pval(rank_r1,rank_r1(pos),uni),
      pval(lambda P:r_of([math.log(b-a) for a,b in zip(P,P[1:])]),r_of([math.log(x) for x in g]),uni)))
print('  after-void segment alone vs uniform-in-segment: p=%.4f'%pval(r1,r1(B),lambda: sorted(random.sample(range(4381,N),len(B)))))
# scan statistic: max gap-sum of 3 consecutive gaps, and max single gap
s3=lambda P: max(P[i+3]-P[i] for i in range(len(P)-3)); s1=lambda P:max(b-a for a,b in zip(P,P[1:]))
print('scan: max 3-gap span obs=%d p=%.4f ; max single gap obs=%d p=%.4f'%(s3(pos),pval(s3,s3(pos),uni),s1(pos),pval(s1,s1(pos),uni)))
# (b) per-line-count-conditioned null and its power
line_of=[x['line'] for x in S]
lines=collections.defaultdict(list)
for i in range(1,N): lines[line_of[i]].append(i)
def line_null(P):
    cnt=collections.Counter(line_of[p] for p in P); Q=[]
    for L,k in cnt.items(): Q+=random.sample(lines[L],k)
    return sorted(Q)
def page_null(P):
    cnt=collections.Counter(S[p]['page'] for p in P); Q=[]
    return None
obs=r1(pos); sims=[r1(line_null(pos)) for _ in range(2000)]
print('line-count-conditioned null: mean r1=%.3f sd=%.3f p=%.3f  (other group: mean +0.373, p=0.232)'%(sum(sims)/len(sims),(sum((s-sum(sims)/len(sims))**2 for s in sims)/len(sims))**.5,(sum(s>=obs for s in sims)+1)/2001))
# power: plant a genuinely non-stationary leak (rate regime: low-rate window of 1650 runes at 1/4 rate, i.e. the T7 picture, random location),
# then test with (i) uniform null (ii) line-conditioned null. A test with power ~= alpha cannot "explain away" anything.
def planted():
    st=random.randrange(1,N-1650); w=[0.2 if st<=i<st+1650 else 1.0 for i in range(1,N)]
    return sorted(set(random.choices(range(1,N),weights=w,k=len(pos))))
U=sorted(r1(uni()) for _ in range(2000)); u95=U[int(.95*2000)]
pw_u=pw_l=0; T=150
for _ in range(T):
    P=planted(); o=r1(P); pw_u+=o>=u95
    sm=[r1(line_null(P)) for _ in range(120)]; pw_l+=(sum(s>=o for s in sm)+1)/121<=0.05
print('power vs planted low-rate window (rate x0.2 over 1650 runes): uniform-null test %.2f ; line-conditioned test %.2f (alpha=0.05)'%(pw_u/T,pw_l/T))
