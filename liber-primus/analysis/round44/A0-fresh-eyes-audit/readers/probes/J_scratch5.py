# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
# Fork J scratch: plant check of the monogram-IoC bound for natural-language running keys under the pinned filter.
import os, sys, collections, random, statistics as st
LP=_ROOT+'/liber-primus'
for p in ("src","analysis/round19/I1"): sys.path.insert(0, os.path.join(LP,p))
from lp import gematria as gp
import constructions as C
n=12956
def idx(path):
    t=open(path,encoding='utf-8',errors='ignore').read().upper()
    return gp.keyword_to_indices(''.join(ch for ch in t if 'A'<=ch<='Z'))
def ioc29(x):
    c=collections.Counter(x); L=len(x); return 29*sum(v*(v-1) for v in c.values())/(L*(L-1))
sr=idx(LP+'/data/keys/self_reliance.txt'); rp=idx(LP+'/data/keys/runepoem_translit.txt'); th=idx(LP+'/data/keys/thematic.txt')
print("lens",len(sr),len(rp),len(th))
rng=random.Random(11); out=[]
for rep in range(8):
    P=C.long_plain(n,seed=rep)                       # repo's English plaintext stream
    o=rng.randrange(0,len(sr)-2*n); K=sr[o:o+2*n]     # Self-Reliance as running key
    for mech in ("keyskip","rewrite","skip_by_two"):
        f={"keyskip":C.enc_keyskip,"rewrite":C.enc_rewrite,"skip_by_two":C.enc_skip_by_two}[mech]
        cx=f(P,K,supp=0.83,seed=rep); cx=list(cx[0] if isinstance(cx,tuple) else cx)[:n]
        out.append((mech,ioc29(cx)))
for mech in ("keyskip","rewrite","skip_by_two"):
    v=[x for m,x in out if m==mech]; print(f"running key (Self-Reliance) + {mech:11s}: IoC29 mean {st.mean(v):.4f} min {min(v):.4f}")
# short word key + skip
kw=gp.keyword_to_indices("FIRFUMFERENFE"); v=[]
for rep in range(8):
    P=C.long_plain(n,seed=rep); K=(kw*((2*n)//len(kw)+1))[:2*n]
    cx=C.enc_keyskip(P,K,supp=0.83,seed=rep); cx=list(cx[0] if isinstance(cx,tuple) else cx)[:n]; v.append(ioc29(cx))
print("13-rune word key + keyskip: IoC29 mean %.4f min %.4f"%(st.mean(v),min(v)))
print("LP2 measured 0.99987, sd 0.00058 -> 2-sigma ceiling 1.0010")
