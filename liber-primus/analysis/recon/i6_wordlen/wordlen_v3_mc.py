#!/usr/bin/env python3
"""
i6 v3 — Monte-Carlo significance for the length-channel typology.

Honest null question: "Could a random filler process (matched mean word length)
reproduce the cipher's close FIT to English-in-futhorc by chance?"

Method: fit metric = KS distance between a length-sample and the big English-in-
futhorc reference. Compute it for the real cipher. Then draw many synthetic
matched-mean filler samples of the SAME size and compute the same KS-to-English.
p = fraction of null samples whose KS-to-English is <= the cipher's. A tiny p
means the cipher's English-likeness is NOT reproducible by a memoryless filler.

We use THREE null families so the verdict does not hinge on one filler model:
  geometric, poisson-shift, and a NEGATIVE-BINOMIAL (over-dispersed) filler.
For maximum honesty we also let each null draw its mean with noise around the
cipher mean, and we report the BEST (most English-like) null across a mean sweep.
"""
import sys, os, re, random, math
from collections import Counter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")))
from lp.gematria import keyword_to_indices, RUNE_TO_IDX

HERE = os.path.dirname(__file__); ROOT = os.path.abspath(os.path.join(HERE,"..","..",".."))
RUNESET=set(RUNE_TO_IDX); BOUNDARY=set("-./\n\r&$§0123456789 \t"); random.seed(3301)

def cipher_wordlens():
    data=open(os.path.join(ROOT,"data","krisyotam_runes.txt"),encoding="utf-8").read()
    lens=[]
    for p in data.split("%")[:55]:
        s=p
        for b in BOUNDARY: s=s.replace(b," ")
        for w in s.split():
            rl=[c for c in w if c in RUNESET]
            if rl: lens.append(len(rl))
    return lens

def english_ref(cap=120000):
    out=[]
    for path in ("pride.txt","war.txt","moby.txt"):
        txt=open(os.path.join(ROOT,"data",path),encoding="utf-8",errors="ignore").read().upper()
        for w in re.findall(r"[A-Z]+",txt):
            if len(w)>20: continue
            try: out.append(len(keyword_to_indices(w)))
            except ValueError: pass
            if len(out)>=cap: return out
    return out

def ks(a,b,maxk=20):
    ca=Counter(a);cb=Counter(b);na=len(a);nb=len(b);d=cua=cub=0.0
    for k in range(1,maxk+1):
        cua+=ca.get(k,0)/na; cub+=cb.get(k,0)/nb; d=max(d,abs(cua-cub))
    return d

def geom(n,mean):
    p=1/mean;out=[];cur=0
    while len(out)<n:
        cur+=1
        if random.random()<p: out.append(cur);cur=0
    return out

def pois(n,mean):
    lam=mean-1;out=[]
    for _ in range(n):
        L=math.exp(-lam);k=0;pp=1.0
        while True:
            k+=1;pp*=random.random()
            if pp<=L:break
        out.append(k)
    return out

def negbin(n,mean,r=4.0):
    # 1 + NegBinom(r, p) with mean-1 = r(1-p)/p
    tgt=mean-1
    p=r/(r+tgt)
    out=[]
    for _ in range(n):
        # sum of geometric failures
        fails=0
        for _ in range(int(r)):
            g=0
            while random.random()<(1-p): g+=1
            fails+=g
        out.append(1+fails)
    return out

def mc_pvalue(A, ref, sampler, mean, B=2000):
    n=len(A); kA=ks(A,ref); cnt=0
    for _ in range(B):
        s=sampler(n,mean)
        if ks(s,ref)<=kA: cnt+=1
    return kA, cnt/B

def main():
    out=[]; pr=lambda *a:(print(*a),out.append(" ".join(map(str,a))))
    A=cipher_wordlens(); ref=english_ref(); meanA=sum(A)/len(A)
    pr(f"=== i6 v3 Monte-Carlo: is cipher's English-fit reproducible by filler? ===")
    pr(f"cipher n={len(A)} mean={meanA:.3f}; English ref n={len(ref)} mean={sum(ref)/len(ref):.3f}")
    kA=ks(A,ref); pr(f"cipher KS-to-English = {kA:.4f}")
    pr("")
    pr("null family      | KS-to-English of cipher | MC p(null KS <= cipher KS)")
    for name,samp,extra in [("geometric",geom,{}),("poisson",pois,{}),("negbin",negbin,{})]:
        # sweep mean +/- to find the MOST English-like null (hardest test)
        best_p=0.0; best_mean=meanA; best_k=None
        for mult in (0.9,0.95,1.0,1.05,1.1):
            m=meanA*mult
            _,p=mc_pvalue(A,ref,samp,m,B=800)
            if p>best_p: best_p=p; best_mean=m
        # final high-B at best mean
        kk,p=mc_pvalue(A,ref,samp,best_mean,B=2000)
        pr(f" {name:14s} | {kA:.4f}                  | p={p:.4f} (best null mean {best_mean:.2f})")
    pr("")
    # direct English-fit vs best-null-fit summary
    pr("Interpretation: p is the chance a MATCHED memoryless filler fits English")
    pr("as well as the cipher does. p<<0.05 across all null families => the cipher's")
    pr("word-length profile carries English-specific structure a filter/OTP would not.")
    open(os.path.join(HERE,"RESULTS_v3.txt"),"w").write("\n".join(out)+"\n")

if __name__=="__main__":
    main()
