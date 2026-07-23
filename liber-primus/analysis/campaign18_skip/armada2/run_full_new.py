"""Orchestrator driver: FULL 55-page runs for the two new validated decoders that
lack a --full mode. --mode autokey  |  --mode interrupter."""
import os,sys,argparse,time
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..","..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis"))
sys.path.insert(0,os.path.join(ROOT,"analysis","campaign18_skip")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from run_stats import load_pages
from skipdecode import eng_to_idx, idx_to_trans
Q=sc.default(); N=gp.N; CONF=-5.5
pages=load_pages()[:-2]

def run_autokey():
    import autokey_skip as AK
    primers=[[i] for i in range(N)]+[eng_to_idx(w) for w in
        ("THE","DIVINITY","CIRCUMFERENCE","PRIMES","TOTIENT","INSTAR","WISDOM","PILGRIM",
         "MOBIUS","THEPRIMESARESACRED","ANEND","EMERGENCE","SACRED","WELCOME","LOSS","SHADOW")]
    primers=[p for p in primers if p]
    best=(-99,None); hits=0; t0=time.time()
    for pno,ct in enumerate(pages):
        pb=(-99,None)
        for primer in primers:
            for mode,dec in (("P",AK.beam_decode_ptautokey),("C",AK.beam_decode_ctautokey)):
                for sign in (-1,1):
                    r=dec(ct,primer,sign=sign,beam_w=450,max_skip=3)
                    s=r["score"]
                    if s>pb[0]: pb=(s,(idx_to_trans(primer),mode,sign))
                    if s>best[0]: best=(s,(pno,idx_to_trans(primer),mode,sign))
                    if s>CONF:
                        hits+=1; print(f"  HIT p{pno} {mode} primer={idx_to_trans(primer)} sign={sign} score={s:.3f}: {r['translit'][:80]}",flush=True)
        print(f"page {pno:2d} best={pb[0]:6.3f} via {pb[1]}  [{time.time()-t0:5.0f}s]",flush=True)
    print(f"\nDONE autokey+skip. GLOBAL best={best[0]:.3f} via {best[1]}  hits>{CONF}: {hits}")
    print("NULL." if hits==0 else "CANDIDATES FOUND — escalate.")

def run_interrupter():
    import interrupter_skip as IS
    from sweep import prefilter, load_text
    # highest-prior for interrupters: referenced + Cicada's own text
    names=["mabinogion","self_reliance","king_in_yellow","agrippa","book_of_the_law",
           "runepoem_oe","solved_plaintext"]
    corp=[]
    for nm in names:
        fp=os.path.join(ROOT,"data","keys",nm+".txt")
        if os.path.exists(fp): corp.append((nm,load_text(fp)))
    for extra in ("armada18/lp1_english_forward.txt","armada18/cicada_koans_and_lp_sections.txt",
                  "armada18/lp1_english_reversed.txt"):
        fp=os.path.join(ROOT,"data","keys",extra)
        if os.path.exists(fp): corp.append((os.path.basename(extra),load_text(fp)))
    best=(-99,None); hits=0; t0=time.time()
    for pno,ct in enumerate(pages):
        ctn=np.array(ct,dtype=np.int64); pb=(-99,None)
        for nm,K in corp:
            for sign in (-1,1):
                for atb in (0,1):
                    ct2=((N-1)-ctn)%N if atb else ctn
                    for o in prefilter(ct2,K,sign)[:8]:
                        r=IS.beam_decode_int(list(ct2),list(K),sign=sign,o=int(o),beam_w=350,max_skip=3)
                        s=r["score"]
                        if s>pb[0]: pb=(s,(nm,sign,atb,int(o)))
                        if s>best[0]: best=(s,(pno,nm,sign,atb,int(o)))
                        if s>CONF:
                            hits+=1; print(f"  HIT p{pno} key={nm} sign={sign} atb={atb} o={o} score={s:.3f} nint={r['n_int']}: {r['translit'][:80]}",flush=True)
        print(f"page {pno:2d} best={pb[0]:6.3f} via {pb[1]}  [{time.time()-t0:5.0f}s]",flush=True)
    print(f"\nDONE interrupter+skip. GLOBAL best={best[0]:.3f} via {best[1]}  hits>{CONF}: {hits}")
    print("NULL." if hits==0 else "CANDIDATES FOUND — escalate.")

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--mode",required=True); a=ap.parse_args()
    (run_autokey if a.mode=="autokey" else run_interrupter)()
