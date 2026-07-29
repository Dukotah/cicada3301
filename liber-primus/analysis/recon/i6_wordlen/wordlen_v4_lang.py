#!/usr/bin/env python3
"""
i6 v4 — DECISIVE language-discrimination + positional length structure.

The marginal length distribution alone is weakly identifying (any over-dispersed
count model fits it; v3 showed a neg-binom filler can too). The honest, strong
tests are:

  TEST 1 (cross-language): encode ENGLISH, LATIN, WELSH into futhorc and measure
  which natural language's word-length distribution the cipher matches best. If the
  cipher matches natural languages generally AND English specifically better than a
  filler, that is language-specific fine structure a one-time pad cannot possess.

  TEST 2 (positional structure): in real prose, word length is not i.i.d. — the
  FIRST word of a clause and words adjacent to clause boundaries have a different
  length profile than clause-interior words (function words cluster at edges). The
  cipher preserves clause boundaries ('.') and line boundaries ('/'). A one-time pad
  / random filler has ZERO length-vs-position structure. We test whether the cipher
  shows the natural-language positional length signature.

Deterministic; honest; writes RESULTS_v4.txt.
"""
import sys, os, re, random, math
from collections import Counter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","..","src")))
from lp.gematria import keyword_to_indices, RUNE_TO_IDX

HERE=os.path.dirname(__file__); ROOT=os.path.abspath(os.path.join(HERE,"..","..",".."))
RUNESET=set(RUNE_TO_IDX); random.seed(3301)

def encode_corpus(paths, cap=100000, skiphead=200):
    out=[]
    for path in paths:
        full=os.path.join(ROOT,path)
        if not os.path.exists(full): continue
        txt=open(full,encoding="utf-8",errors="ignore").read()
        # strip diacritics crudely to A-Z
        txt=txt.upper()
        words=re.findall(r"[A-Z]+",txt)[skiphead:]  # skip gutenberg english header
        for w in words:
            if len(w)>20: continue
            try: out.append(len(keyword_to_indices(w)))
            except ValueError: pass
            if len(out)>=cap: return out
    return out

def ks(a,b,maxk=20):
    ca=Counter(a);cb=Counter(b);na=len(a);nb=len(b);d=cua=cub=0.0
    for k in range(1,maxk+1):
        cua+=ca.get(k,0)/na;cub+=cb.get(k,0)/nb;d=max(d,abs(cua-cub))
    return d

def cipher_structured():
    """Return (all_lens, clause_first_lens, clause_last_lens, interior_lens).
    Clause = run of words between '.' or '/' or '%' boundaries."""
    data=open(os.path.join(ROOT,"data","krisyotam_runes.txt"),encoding="utf-8").read()
    pages=data.split("%")[:55]
    allL=[]; first=[]; last=[]; interior=[]
    for p in pages:
        # split into clauses on . and / ; words within clause on -
        s=p.replace("\n","").replace("\r","")
        # unify clause separators
        for cb in "./":
            s=s.replace(cb,"\x01")
        clauses=s.split("\x01")
        for cl in clauses:
            words=[w for w in cl.split("-") if any(c in RUNESET for c in w)]
            lens=[len([c for c in w if c in RUNESET]) for w in words]
            lens=[l for l in lens if l>0]
            if not lens: continue
            allL+=lens
            first.append(lens[0]); last.append(lens[-1])
            if len(lens)>2: interior+=lens[1:-1]
    return allL, first, last, interior

def mean(x): return sum(x)/len(x) if x else float('nan')

def main():
    out=[]; pr=lambda *a:(print(*a),out.append(" ".join(map(str,a))))
    A,first,lastw,interior=cipher_structured()

    ENG=encode_corpus(["data/pride.txt","data/war.txt","data/moby.txt"])
    LAT=encode_corpus(["analysis/latin/latin_218.txt","analysis/latin/latin_28233.txt"])
    WEL=encode_corpus(["data/keys/welsh/welsh_mabinogion.txt"], skiphead=50)

    pr("=== i6 v4 language discrimination (futhorc word-length KS to cipher) ===")
    pr(f"cipher n={len(A)} mean={mean(A):.3f}")
    for name,ref in [("ENGLISH",ENG),("LATIN",LAT),("WELSH",WEL)]:
        pr(f"  {name:8s} ref n={len(ref)} mean={mean(ref):.3f}  KS(cipher,{name})={ks(A,ref):.4f}")
    best=min([("ENGLISH",ENG),("LATIN",LAT),("WELSH",WEL)],key=lambda kv:ks(A,kv[1]))
    pr(f"  --> closest natural language: {best[0]}")
    pr("")

    # cross-language sanity: how far are the languages from each OTHER?
    pr("  [language separation] KS(ENG,LAT)={:.4f} KS(ENG,WEL)={:.4f} KS(LAT,WEL)={:.4f}"
       .format(ks(ENG,LAT),ks(ENG,WEL),ks(LAT,WEL)))
    pr("")

    pr("=== TEST 2 positional length structure (NL has clause-edge effects) ===")
    pr(f" clause-FIRST word mean len = {mean(first):.3f} (n={len(first)})")
    pr(f" clause-LAST  word mean len = {mean(lastw):.3f} (n={len(lastw)})")
    pr(f" clause-INTERIOR word mean  = {mean(interior):.3f} (n={len(interior)})")
    pr(f" all words mean             = {mean(A):.3f}")
    # English positional reference
    pr("")
    pr(" [English futhorc positional ref, from sentence structure]")
    engpos=english_positional()
    for k,v in engpos.items(): pr(f"   {k}: {v:.3f}")
    pr("")
    # permutation test: is first != interior beyond chance?
    p_first=perm_mean_diff(first,interior)
    p_last =perm_mean_diff(lastw,interior)
    pr(f" perm-test clause-first vs interior: diff={mean(first)-mean(interior):+.3f} p={p_first:.4f}")
    pr(f" perm-test clause-last  vs interior: diff={mean(lastw)-mean(interior):+.3f} p={p_last:.4f}")
    pr("")
    pr("Interpretation:")
    pr(" - If cipher's closest language is ENGLISH (and all NL beat random), the")
    pr("   length channel carries language-specific structure => NL plaintext exists.")
    pr(" - Significant clause-edge length effect (p<0.05) = NL positional structure")
    pr("   that an OTP/filler cannot produce.")
    open(os.path.join(HERE,"RESULTS_v4.txt"),"w").write("\n".join(out)+"\n")

def english_positional():
    """Mean futhorc word length by clause position in English prose."""
    txt=""
    for path in ("data/pride.txt","data/war.txt"):
        txt+=open(os.path.join(ROOT,path),encoding="utf-8",errors="ignore").read().upper()
    # split into clauses on . ; ! ? ,
    clauses=re.split(r"[.;!?,]",txt)
    first=[];last=[];interior=[]
    cnt=0
    for cl in clauses:
        ws=re.findall(r"[A-Z]+",cl)
        lens=[]
        for w in ws:
            if len(w)>20: continue
            try: lens.append(len(keyword_to_indices(w)))
            except ValueError: pass
        if not lens: continue
        first.append(lens[0]);last.append(lens[-1])
        if len(lens)>2: interior+=lens[1:-1]
        cnt+=1
        if cnt>20000: break
    m=lambda x:sum(x)/len(x)
    return {"clause-first":m(first),"clause-last":m(last),"interior":m(interior)}

def perm_mean_diff(a,b,B=2000):
    obs=abs(sum(a)/len(a)-sum(b)/len(b))
    pool=a+b; na=len(a); cnt=0
    for _ in range(B):
        random.shuffle(pool)
        d=abs(sum(pool[:na])/na - sum(pool[na:])/(len(pool)-na))
        if d>=obs: cnt+=1
    return cnt/B

if __name__=="__main__":
    main()
