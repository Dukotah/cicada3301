import sys,os,re,json,numpy as np
sys.path.insert(0,'src'); sys.path.insert(0,'analysis')
from lp import gematria as gp, solve, score as _score
N=gp.N; SC=_score.default()
import run_stats
raw=open(run_stats.KRIS,encoding="utf-8").read()
segs=[s for s in raw.split("%")]
def runes_only(s):
    return "".join(ch for ch in s if ch in gp.RUNE_TO_IDX or ch==gp.INTERRUPTER)
page_runes=[]
for s in segs:
    r=runes_only(s)
    if r: page_runes.append((s,r))
page_runes=page_runes[:-2]  # drop solved
MONO=run_stats.english_baseline()
counts=np.bincount(np.array(MONO),minlength=N).astype(float)+1.0
MONOLP=np.log10(counts/counts.sum())

def load_key(f):
    letters=re.sub(r"[^A-Za-z]","",open(f,encoding="utf-8",errors="ignore").read())
    return np.array(gp.keyword_to_indices(letters))

key=load_key("analysis/foundation/chymical_wedding_letters.txt")
print("key len (rune indices):",len(key))
glob_best=(-99,None)
per_page_best=[]
for pi,(seg,r) in enumerate(page_runes):
    idxs=np.array([gp.RUNE_TO_IDX[ch] for ch in r if ch in gp.RUNE_TO_IDX])
    L=len(idxs)
    if len(key)<L+1: continue
    noff=len(key)-L
    cand=[]
    for sign in (-1,1):
        for atb in (False,True):
            cc=(N-1-idxs) if atb else idxs
            win=np.lib.stride_tricks.sliding_window_view(key,L)[:noff]
            p=(cc[None,:]-sign*win)%N
            mono=MONOLP[p].sum(axis=1)
            k=min(4,len(mono))
            top=np.argpartition(-mono,k-1)[:k]
            for t in top:
                cand.append((float(mono[t]),sign,atb,int(t)))
    cand.sort(reverse=True)
    page_best=(-99,None)
    for mono,sign,atb,o in cand[:4]:
        stream=[int(x) for x in key[o:o+L]]
        res=solve.find_interrupters(r,stream,sign=sign,atbash=atb,beam_width=200)
        s=res["score_norm"]
        if s>page_best[0]:
            page_best=(s,{"page":pi,"sign":sign,"atb":atb,"off":o,
                "n_int":res["n_interrupters"],"pt":res["plaintext"][:90]})
        if s>glob_best[0]:
            glob_best=(s,{"page":pi,"sign":sign,"atb":atb,"off":o,
                "n_int":res["n_interrupters"],"pt":res["plaintext"][:90]})
    per_page_best.append((pi,page_best[0]))
print("GLOBAL best interrupter-beam score:", round(glob_best[0],3))
print("   ", glob_best[1])
per_page_best.sort(key=lambda x:-x[1])
print("top pages:", [(p,round(s,3)) for p,s in per_page_best[:8]])
json.dump({"global_best":glob_best[0],"detail":glob_best[1]},
          open("analysis/foundation/cw_interrupt.json","w"),indent=2)
