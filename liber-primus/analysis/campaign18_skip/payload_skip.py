"""Lead #1 -- the pp49-51 256-byte payload as a KEYSTREAM under the skip-tolerant
decoder. Campaign VII tested this key RIGIDLY (null); but the ~83% doublet filter
desyncs the key, so a rigid test would miss it even if correct -- the same
soundness hole Campaign XVIII fixed. This re-tests it skip-aware.

Interpretations tried: both canonical byte variants (majority / decimal-pref),
forward + reversed byte order, bytes mod 29 as the keystream, over EACH page at
offset 0 AND as a period-256 repeating key over the whole corpus; both signs; atbash.
"""
import os,sys,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from run_stats import load_pages
from skipdecode import idx_to_trans
import sweep as SW
Q=sc.default(); N=gp.N
CONF=-5.5; NULLMAX=-6.82

def load_payload(name):
    b=open(os.path.join(ROOT,"analysis","pp49_51",name),"rb").read()
    return np.array(list(b),dtype=np.int64)

variants={}
for nm in ["canon_256.bin","canon_256_decpref.bin"]:
    b=load_payload(nm)
    variants[nm]=b
    variants[nm+"~rev"]=b[::-1].copy()

pages=load_pages()[:-2]
best=(-99,None); hits=[]
# how the payload becomes a 0..28 keystream: raw byte mod 29
for vname,b in variants.items():
    ks=(b%N)
    for sign in (-1,1):
        for atb in (0,1):
            # (a) key over each page independently at offset 0
            for pn,pg in enumerate(pages):
                ct=np.array(pg,dtype=np.int64)
                ct2=((N-1)-ct)%N if atb else ct
                L=len(ct2)
                if L>len(ks): 
                    K=np.concatenate([ks]*(L//len(ks)+2))   # repeat to cover page
                else: K=ks
                pi=SW.beam(ct2,K,sign,0,L,320)
                s=Q.score_norm(idx_to_trans(pi))
                if s>best[0]: best=(s,(vname,sign,atb,f"page{pn}",0))
                if s>CONF: hits.append((s,vname,sign,atb,pn,idx_to_trans(pi)))
print(f"pp49-51 payload as keystream (skip-aware): tested {len(variants)} variants x 2 signs x 2 atbash x 55 pages")
print(f"  BEST score = {best[0]:.3f}  via {best[1]}")
print(f"  (English -4.3 | confirm {CONF} | noise-max {NULLMAX})")
print(f"  hits over {CONF}: {len(hits)}")
for h in sorted(hits,reverse=True)[:5]:
    print(f"   HIT {h[0]:.3f} {h[1]} sign={h[2]} atb={h[3]} page={h[4]}: {h[5][:80]}")
if not hits: print("  -> NULL. Payload is not a skip-aware polyalphabetic key over any single page.")
