"""RANK 2 driver -- feed every LP1-discipline Rosetta keystream through the
skip-tolerant beam over all 55 unsolved pages. Keys are full-length streams
(phi(prime)/primes/totient/thematic/constants/running-LP1), so no offset scan:
one beam per (page, key, sign). Discipline sign is -1; we test both to be safe."""
import os,sys,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..","..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis"))
sys.path.insert(0,os.path.join(ROOT,"analysis","campaign18_skip")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from run_stats import load_pages
from sweep import beam
from skipdecode import idx_to_trans
import rosetta_keys as RK
Q=sc.default(); N=gp.N; CONF=-5.5; FULL_BEAM=400
pages=load_pages()[:-2]
best=(-99,None); hits=[]; t=0
import time; t0=time.time()
for pn,pg in enumerate(pages):
    ct=np.array(pg,dtype=np.int64); L=len(ct)
    reg=RK.build_registry(L)
    pbest=(-99,None)
    for name,(kind,ks) in reg.items():
        ct2=((N-1)-ct)%N if kind=="atbash" else ct
        K=np.array(ks,dtype=np.int64)
        for sign in (-1,1):
            pi=beam(ct2,K,sign,0,L,FULL_BEAM)
            s=Q.score_norm(idx_to_trans(pi))
            if s>pbest[0]: pbest=(s,(name,sign))
            if s>best[0]: best=(s,(pn,name,sign))
            if s>CONF: hits.append((s,pn,name,sign,idx_to_trans(pi)))
    print(f"page {pn:2d} (L={L:3d}) best={pbest[0]:6.3f} via {pbest[1]}  [{time.time()-t0:5.0f}s]",flush=True)
    for h in sorted(hits,reverse=True)[:1]:
        if h[1]==pn: print(f"    HIT {h[0]:.3f} {h[2]} sign={h[3]}: {h[4][:80]}",flush=True)
print(f"\nDONE {time.time()-t0:.0f}s. GLOBAL best={best[0]:.3f} via {best[1]}")
print(f"hits over {CONF}: {len(hits)}  (English -4.3 | noise-max -6.82)")
if not hits: print("NULL -- no LP1-discipline keystream decodes any page skip-aware.")
