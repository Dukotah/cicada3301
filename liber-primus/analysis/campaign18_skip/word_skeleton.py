"""Lead #2 -- word-length skeleton match (open ledger item 2b).
An OTP hides symbol VALUES but not word BOUNDARIES. If the plaintext is a known
published text, a page's sequence of rune-counts-per-word must match a contiguous
run of that text's word-lengths. CIPHER-MODEL-INDEPENDENT and falsifiable.
"""
import os,sys,re
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis")); sys.path.insert(0,HERE)
from lp import gematria as gp
from skipdecode import eng_to_idx
TAG=re.compile(r"<[^>]+>")

def page_wordlens():
    raw=open(os.path.join(ROOT,"data","krisyotam_runes.txt"),encoding="utf-8").read()
    pages=[]
    for seg in raw.split("%"):
        if not any(gp.is_rune(c) for c in seg): continue
        words=[]; w=0
        for ch in seg:
            if gp.is_rune(ch): w+=1
            elif w: words.append(w); w=0
        if w: words.append(w)
        pages.append(words)
    return pages[:-2]

def text_wordlens(path):
    s=open(path,encoding="utf-8",errors="ignore").read()
    if path.endswith(".html"): s=TAG.sub(" ",s)
    out=[]
    for w in re.split(r"[^A-Za-z]+",s):
        if w:
            try: out.append(len(eng_to_idx(w)))
            except Exception: pass
    return np.array(out,dtype=np.int16)

def best_match(pseq,tarr):
    """Longest CONSECUTIVE run of exactly-matching word-lengths over all
    alignments -- high-power fingerprint (chance of a length-R run ~ 0.4^R)."""
    L=len(pseq); M=len(tarr)
    if M<L: return 0
    W=(np.lib.stride_tricks.sliding_window_view(tarr,L)==np.array(pseq,dtype=np.int16))
    run=np.zeros(W.shape[0]); best=np.zeros(W.shape[0])
    for c in range(L):
        run=(run+1.0)*W[:,c]; best=np.maximum(best,run)
    return int(best.max())

REF=["mabinogion.txt","self_reliance.txt","king_in_yellow.txt","agrippa.txt",
     "book_of_the_law.txt","runepoem_oe.txt","solved_plaintext.txt","thematic.txt",
     "campaign12/walden.txt","campaign12/meditations.txt","campaign13/englishcanon_alice_wonderland.txt"]
files=[os.path.join(ROOT,"data","keys",f) for f in REF if os.path.exists(os.path.join(ROOT,"data","keys",f))]
texts=[(os.path.basename(f),text_wordlens(f)) for f in files]
pw=page_wordlens()
print(f"{len(pw)} pages, {len(texts)} texts. LONGEST consecutive word-length run vs shuffled control:")
rng=np.random.default_rng(3301); flagged=0
for pn,pseq in enumerate(pw):
    if len(pseq)<12:
        print(f"  page {pn:2d} words={len(pseq):3d}  (too short, skipped)"); continue
    real,who=max((best_match(pseq,t),nm) for nm,t in texts)
    ctrl=0
    for _ in range(8):
        sh=list(pseq); rng.shuffle(sh); ctrl=max(ctrl,max(best_match(sh,t) for _,t in texts))
    flag=""
    if real>=ctrl+4 and real>=8: flag=f"  <== SIGNAL via {who}"; flagged+=1
    print(f"  page {pn:2d} words={len(pseq):3d}  longest_run={real:2d}  ctrl_ceiling={ctrl:2d}{flag}")
print(f"\nflagged pages: {flagged}")
print("NULL -- no page's word-length run exceeds chance for any referenced text."
      if not flagged else "SIGNAL -- investigate flagged pages (candidate plaintext!).")
