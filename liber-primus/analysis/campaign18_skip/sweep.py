"""Campaign XVIII sweep -- re-run the keytext corpus under the skip-tolerant
decoder validated in skipdecode.py / robustness.py.

Architecture (speed):
  1. numpy MONOGRAM prefilter over all offsets of a text -> top-K offsets
  2. SCREEN: skip-aware beam on first S runes (index-bigram pruning) ->
     canonical translit Q.score_norm; keep offsets that beat SCREEN_THR
  3. CONFIRM: full-page skip-aware beam on survivors; report Q.score_norm

Discovery threshold from robustness.py: null-max -6.82, English ~-4.3.
"""
import os, sys, glob, re, time
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from run_stats import load_pages
from skipdecode import eng_to_idx, idx_to_trans
Q=sc.default(); N=gp.N
TAG=re.compile(r"<[^>]+>")

SCREEN_LEN=90; SCREEN_THR=-6.0; CONF_THR=-5.5
PREFILTER_BG=300; PREFILTER_K=24; SCREEN_BEAM=400; FULL_BEAM=500; MAXSKIP=3
PREFIX_W=22

# ---- index-space bigram LM for fast pruning (NOT for final ranking) ----
def build_lm():
    txt=""
    for f in ["solved_plaintext.txt","self_reliance.txt","campaign12/walden.txt"]:
        p=os.path.join(ROOT,"data","keys",f)
        if os.path.exists(p): txt+=open(p,encoding="utf-8",errors="ignore").read()+" "
    idx=eng_to_idx(txt)
    mono=np.ones(N); bg=np.ones((N,N))
    for a in idx: mono[a]+=1
    for a,b in zip(idx,idx[1:]): bg[a,b]+=1
    M=np.log(mono/mono.sum())
    BG=np.log(bg/bg.sum(1,keepdims=True))
    return M, BG
M_LM, BG_LM = build_lm()

def load_text(path):
    s=open(path,encoding="utf-8",errors="ignore").read()
    if path.endswith(".html"): s=TAG.sub(" ",s)
    return np.array(eng_to_idx(s),dtype=np.int64)

_SKIPGRID=(0,5,9,13,17)   # candidate first-skip positions to tolerate in prefix
def prefilter(ct2, K, sign, W=PREFIX_W):
    """Skip-tolerant offset finder over ALL valid offsets of the running key.
    Tier 1: vectorised index-BIGRAM on the rigid prefix, but scored as the MAX
    over {no skip} U {one key-skip inserted at each grid position}, so an early
    first-skip (the case that silently dropped real keys) no longer corrupts the
    ranking -> top PREFILTER_BG. Tier 2: a small skip-aware beam quadgram-scores
    each survivor's first ~30 runes -> top PREFILTER_K for the full beam."""
    L=len(ct2); no=len(K)-L-MAXSKIP*L-4
    if no<=0: return []
    W=min(W,L)
    # base rigid prefix, plus one shifted so a single inserted skip is cheap
    base=np.empty((W+1,no),dtype=np.int64)
    for i in range(W+1):
        base[i]=(ct2[min(i,W-1)]+sign*K[i:i+no])%N
    def bigram_of(rows):
        s=np.zeros(no)
        for i in range(1,W): s+=BG_LM[rows[i-1],rows[i]]
        return s
    best=None
    for j in _SKIPGRID:
        rows=[]
        for i in range(W):
            k=i+(1 if (j and i>=j) else 0)         # +1 key advance after skip@j
            rows.append((ct2[i]+sign*K[k:k+no])%N)
        s=bigram_of(rows)
        best=s if best is None else np.maximum(best,s)
    kb=min(PREFILTER_BG,no)
    cand=np.argpartition(best,-kb)[-kb:]
    # tier2: skip-aware tiny beam on the prefix (robust to skip position)
    Wt=min(30,L)
    rescored=[]
    for o in cand:
        pi=beam(ct2,K,sign,int(o),Wt,60)
        rescored.append((Q.score_norm(idx_to_trans(pi)),int(o)))
    rescored.sort(reverse=True)
    return [o for _,o in rescored[:PREFILTER_K]]

_QD=Q.d; _QF=Q.floor; _TR=gp.IDX_TO_TRANS
def _qdelta(tl,add):
    L1=len(tl); s=tl+add; L2=len(s); tot=0.0
    for e in range(max(4,L1+1),L2+1): tot+=_QD.get(s[e-4:e],_QF)
    return tot

def beam(ct2, K, sign, o, length, beam_w):
    """skip-aware beam pruned by the CANONICAL translit-quadgram score
    (proven in robustness.py to recover keys through up to 14 skips).
    Returns the best plaintext-index path."""
    Kx=K
    need=o+length+MAXSKIP*length+8
    if need>len(Kx):
        Kx=np.concatenate([K,np.zeros(need-len(K),dtype=np.int64)])
    p0=int((ct2[0]+sign*Kx[o])%N)
    t0=_TR[p0]
    # hyp: (score, pa, translit, path).  Skip-validity compares a rejected key
    # against the previous CIPHERTEXT rune ct2[i-1] (a suppressed doublet is an
    # equal *output*), which is constant across hyps at each step.
    beams=[(0.0,o,t0,(p0,))]
    for i in range(1,length):
        ci=int(ct2[i]); cprev=int(ct2[i-1]); nxt=[]
        for sc0,pa,tl,path in beams:
            for d in range(MAXSKIP+1):
                acc=pa+1+d
                if acc>=len(Kx): break
                p=int((ci+sign*Kx[acc])%N)
                ok=True
                for m in range(pa+1,acc):
                    if (p-sign*int(Kx[m]))%N!=cprev: ok=False; break
                if not ok: continue
                add=_TR[p]
                nxt.append((sc0+_qdelta(tl,add),acc,tl+add,path+(p,)))
        if not nxt: break
        nxt.sort(key=lambda x:x[0],reverse=True)
        beams=nxt[:beam_w]
    best=max(beams,key=lambda x:x[0])
    return list(best[3])

def attack_page(ct, pageno, texts):
    hits=[]
    best_glob=(-99,None)
    for tname,K in texts:
        for sign in (-1,1):
            for atb in (0,1):
                ct2=((N-1)-ct)%N if atb else ct
                offs=prefilter(ct2,K,sign)
                for o in offs:
                    pi=beam(ct2,K,sign,o,min(SCREEN_LEN,len(ct2)),SCREEN_BEAM)
                    s=Q.score_norm(idx_to_trans(pi))
                    if s>best_glob[0]: best_glob=(s,(tname,sign,atb,o))
                    if s>SCREEN_THR:
                        pf=beam(ct2,K,sign,o,len(ct2),FULL_BEAM)
                        fs=Q.score_norm(idx_to_trans(pf))
                        if fs>CONF_THR:
                            hits.append((fs,tname,sign,atb,o,idx_to_trans(pf)))
    return hits,best_glob

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--texts",default="referenced")  # referenced | all
    ap.add_argument("--pages",default="")            # e.g. 0-10 or blank=all
    args=ap.parse_args()
    REFERENCED=["mabinogion.txt","self_reliance.txt","king_in_yellow.txt","agrippa.txt",
                "book_of_the_law.txt","runepoem_oe.txt","runepoem_translit.txt",
                "solved_plaintext.txt","thematic.txt"]
    if args.texts=="referenced":
        files=[os.path.join(ROOT,"data","keys",f) for f in REFERENCED]
        files=[f for f in files if os.path.exists(f)]
    else:
        files=sorted(glob.glob(os.path.join(ROOT,"data","keys","**","*.txt"),recursive=True)+
                     glob.glob(os.path.join(ROOT,"data","keys","**","*.html"),recursive=True))
    texts=[(os.path.basename(f),load_text(f)) for f in files]
    texts=[(n,k) for n,k in texts if len(k)>300]
    print(f"loaded {len(texts)} texts; screen_thr={SCREEN_THR} conf_thr={CONF_THR} null-max=-6.82")
    pages=load_pages()[:-2]
    sel=range(len(pages))
    if args.pages:
        a,b=args.pages.split("-"); sel=range(int(a),int(b)+1)
    t0=time.time(); allhits=[]
    for pn in sel:
        ct=np.array(pages[pn],dtype=np.int64)
        hits,bg=attack_page(ct,pn,texts)
        flag="  <== HIT" if hits else ""
        print(f"page {pn:2d} (len {len(ct):3d})  best_screen={bg[0]:6.3f} via {bg[1]}{flag}  [{time.time()-t0:5.0f}s]")
        for h in sorted(hits,reverse=True)[:3]:
            print(f"     HIT score={h[0]:.3f} text={h[1]} sign={h[2]} atb={h[3]} off={h[4]}")
            print(f"        {h[5][:90]}")
        allhits+=[(pn,)+h for h in hits]
    print(f"\nDONE {time.time()-t0:.0f}s. total hits over conf_thr={CONF_THR}: {len(allhits)}")
    if not allhits:
        print("NO hits above threshold in this run.")
