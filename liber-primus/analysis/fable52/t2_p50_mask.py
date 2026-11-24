# Independent check of the other group's "p50 leading-zero doublet enrichment" (33/86, p=6e-4)
# with a look-elsewhere correction over phase (256) and predicate family.
import sys,os,json,random,math,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
pos=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'doublet_positions.json')))  # index of 2nd rune, 0-based
G=json.load(open(r'C:\Users\dukot\AppData\Local\Temp\lpx\r\resources\liber-primus\lp2-grid-256.json',encoding='utf8'))
tok=[t for p in G['pages'] for t in p['tokens']]; assert len(tok)==256
A=G['alphabet']; val=[60*A.index(t[0])+A.index(t[1]) for t in tok]
N=12956
def hits(mask,ph,P=pos): return sum(mask[(p+ph)%256] for p in P)
lead0=[t[0]=='0' for t in tok]; print('lead0 cells',sum(lead0))
h=[hits(lead0,ph) for ph in range(256)]
print('their convention cell=(event_pos-1)%256: 1-based second-rune => ph=0 :',h[0],' ph=-1:',h[255],' ph=+1:',h[1])
print('max over phases',max(h),'at',h.index(max(h)),' mean',sum(h)/256)
# predicates family (declared before looking): leading char 0..4, second char class, value parity, value<128, value mod3==0, bit k of value (8)
preds={}
for c in '01234': preds['lead'+c]=[t[0]==c for t in tok]
preds['even']=[v%2==0 for v in val]; preds['lt128']=[v<128 for v in val]; preds['mod3']=[v%3==0 for v in val]
for k in range(8): preds['bit%d'%k]=[(v>>k)&1==1 for v in val]
preds['prime']=[v>1 and all(v%d for d in range(2,int(v**.5)+1)) for v in val]
def z(mask,ph,P):
    m=sum(mask)/256; x=hits(mask,ph,P); n=len(P); return (x-n*m)/math.sqrt(n*m*(1-m)) if 0<m<1 else 0
def stat_fixed(P): return z(lead0,0,P)
def stat_phase(P): return max(z(lead0,ph,P) for ph in range(256))
def stat_family(P): return max(abs(z(m,ph,P)) for m in preds.values() for ph in range(256))
obs=(stat_fixed(pos),stat_phase(pos),stat_family(pos)); print('observed z: fixed %.2f  max-phase %.2f  max-family(|z|) %.2f'%obs)
random.seed(52)
def null_draw():
    # null A: uniform random 86 sites
    return random.sample(range(1,N),len(pos))
def null_shift():
    # null B: preserve gap structure (T7 clustering) exactly: random circular shift
    s=random.randrange(N); return [ (p+s)%N for p in pos]
for name,nd,R in (('uniform',null_draw,400),('circular-shift',null_shift,400)):
    c=[0,0,0]
    for _ in range(R):
        P=nd(); 
        c[0]+=stat_fixed(P)>=obs[0]; c[1]+=stat_phase(P)>=obs[1]; c[2]+=stat_family(P)>=obs[2]
    print(name,'p fixed=%.4f  p max-phase=%.4f  p family=%.4f'%tuple((x+1)/(R+1) for x in c))
# positive control: plant mask-modulated leak (odds ratio 2.43 as they report) and check the family test power
def plant(orr=2.43):
    w=[orr if lead0[p%256] else 1 for p in range(N)]; 
    return sorted(set(random.choices(range(1,N),weights=w[1:],k=len(pos))))
thr=[]
for _ in range(200): thr.append(stat_family(null_draw()))
thr.sort(); t95=thr[int(.95*len(thr))]
pw=sum(stat_family(plant())>=t95 for _ in range(100))/100
pw1=sum(stat_fixed(plant())>=1.645 for _ in range(300))/300
print('power at OR=2.43: family-max test %.2f ; fixed-phase one-sided 5%% test %.2f ; family 95%% bar z=%.2f'%(pw,pw1,t95))
