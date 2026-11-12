# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""Fork B verification snippet: drift-smeared long-period kappa scan (NOT a repo lane; audit-only).
Question: is a periodic key with period 64..6000 under a key-advancing soft anti-repeat correction (B2 rule R2_KEYADV)
detectable by a drift-matched lag-coincidence filter, and what does the real LP2 stream show?"""
import sys, math, time, random
import numpy as np
sys.path.insert(0,_PROBES)
sys.path.insert(0,_ROOT+'/liber-primus/src'); sys.path.insert(0,_ROOT+'/liber-primus/analysis')
from lpdata import unsolved_pages, flat
from lp import gematria as gp
import run_stats
N29=29; MAXLAG=6200; RHO=0.0279
U=np.array(flat(unsolved_pages()),dtype=np.uint8); N=len(U)

def zlags(c,maxlag=MAXLAG):
    n=len(c); z=np.zeros(maxlag+1)
    for l in range(1,maxlag+1):
        m=n-l; k=np.count_nonzero(c[l:]==c[:-l])
        z[l]=(k-m/29)/math.sqrt(m*(1/29)*(28/29))
    return z

def pois(lam,kmax):
    out=[math.exp(-lam)]
    for k in range(1,kmax+1): out.append(out[-1]*lam/k)
    return np.array(out)

PGRID=list(range(64,3001))
def build_filters():
    F={}
    for p in PGRID:
        for d in (-1,+1):
            idx=[];w=[]
            for m in (1,2):
                lam=RHO*m*p; kmax=int(lam+4*math.sqrt(lam)+3); pm=pois(lam,kmax)
                for s,ws in enumerate(pm):
                    lag=m*p+d*s
                    if 2<=lag<=MAXLAG and ws>1e-4:
                        idx.append(lag); w.append(ws*math.sqrt((N-lag)/N))
            idx=np.array(idx); w=np.array(w)
            F[(p,d)]=(idx,w/np.sqrt((w*w).sum()))
    return F
FILT=build_filters()
def scan(z):
    best=(-9,None); rig=(-9,None)
    for (p,d),(idx,w) in FILT.items():
        t=float((z[idx]*w).sum())
        if t>best[0]: best=(t,(p,d))
    for p in PGRID:   # rigid (no drift): lags p,2p
        lags=[l for l in (p,2*p) if l<=MAXLAG]
        t=float(z[lags].sum()/math.sqrt(len(lags)))
        if t>rig[0]: rig=(t,p)
    return best,rig

def english_runes(n,seed):
    random.seed(seed)
    # quadgram-Markov English from the repo's committed model, greedy multigraph transliteration
    txt=run_stats._english_from_quadgrams(int(n*1.25)+200)
    rs=random.Random(seed); off=rs.randrange(0,50)
    idx=gp.keyword_to_indices(txt[off:])
    return np.array(idx[:n],dtype=np.uint8)

def encipher(P,key,rule,pfix=0.81,rng=None):
    """rule: 'KEYADV' (advance key one extra step and re-encipher), 'REPICK' (no drift), 'NONE'."""
    n=len(P); p=len(key); C=np.zeros(n,dtype=np.uint8); j=0; prev=-1
    for i in range(n):
        c=(int(P[i])+int(key[j%p]))%29
        if c==prev and rule!='NONE' and rng.random()<pfix:
            if rule=='KEYADV':
                j+=1; c=(int(P[i])+int(key[j%p]))%29
            else:
                c=rng.choice([x for x in range(29) if x!=prev])
        C[i]=c; prev=c; j+=1
    return C

def null_stream(rng):
    C=np.zeros(N,dtype=np.uint8); prev=-1
    for i in range(N):
        c=rng.randrange(29)
        if c==prev and rng.random()<0.81: c=rng.randrange(29)
        C[i]=c; prev=c
    return C

if __name__=='__main__':
    t0=time.time()
    zr=zlags(U); br,rr=scan(zr)
    print("REAL LP2: drift-matched best T=%.2f at (p,dir)=%s ; rigid best T=%.2f at p=%s"%(br[0],br[1],rr[0],rr[1]))
    print("REAL top single-lag |z| (2..%d):"%MAXLAG, sorted([(round(abs(zr[l]),2),l) for l in range(2,MAXLAG+1)],reverse=True)[:6])
    rng=random.Random(3301)
    nb=[];nr=[]
    for t in range(40):
        z=zlags(null_stream(rng)); b,r=scan(z); nb.append(b[0]); nr.append(r[0])
    nb.sort(); nr.sort()
    print("NULL (40 soft-filtered uniform streams): drift-matched max T: median %.2f  max %.2f ; rigid max T: median %.2f max %.2f"%(nb[20],nb[-1],nr[20],nr[-1]))
    print("elapsed %.0fs"%(time.time()-t0))
    Pt=english_runes(N,11)
    print("plaintext IoC*29 = %.3f"%(29*sum((np.bincount(Pt,minlength=29)/N)**2)))
    for per in (100,250,450,700,1000,1500,2200,3000):
        res=[]
        for rep in range(3):
            key=np.array([rng.randrange(29) for _ in range(per)],dtype=np.uint8)
            C=encipher(Pt,key,'KEYADV',rng=rng)
            dbl=np.count_nonzero(C[1:]==C[:-1])/(N-1)
            ioc=29*sum((np.bincount(C,minlength=29)/N)**2)*N/(N-1)
            b,r=scan(zlags(C)); res.append((round(b[0],2),b[1],round(r[0],2),round(100*dbl,2),round(ioc,4)))
        print("PLANT period",per,"KEYADV:",res)
    print("elapsed %.0fs"%(time.time()-t0))
