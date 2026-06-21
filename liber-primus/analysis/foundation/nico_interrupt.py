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
    return np.array(gp.keyword_to_indices(letters[:600000]))

texts=[("nico_dooge","analysis/foundation/nicomachus_dooge.txt"),
       ("nico_clean","analysis/foundation/nicomachus_dooge_clean.txt")]

best_overall=[]
for lab,f in texts:
    key=load_key(f)
    glob_best=(-99,None)
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
                k=min(3,len(mono))
                top=np.argpartition(-mono,k-1)[:k]
                for t in top:
                    cand.append((float(mono[t]),sign,atb,int(t)))
        cand.sort(reverse=True)
        for mono,sign,atb,o in cand[:4]:
            stream=[int(x) for x in key[o:o+L]]
            res=solve.find_interrupters(r,stream,sign=sign,atbash=atb,beam_width=200)
            s=res["score_norm"]
            if s>glob_best[0]:
                glob_best=(s,{"page":pi,"sign":sign,"atb":atb,"off":o,
                    "n_int":res["n_interrupters"],"pt":res["plaintext"][:90]})
    print(f"[{lab}] best interrupter-beam score: {glob_best[0]:.3f}")
    print("   ",glob_best[1])
    best_overall.append((lab,glob_best))

json.dump([{"label":l,"score":b[0],"detail":b[1]} for l,b in best_overall],
          open("analysis/foundation/nico_interrupt.json","w"),indent=2)
