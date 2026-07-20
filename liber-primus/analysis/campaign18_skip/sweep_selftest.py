"""Sweep recall gate: plant a skip-enciphered page (realistic length + skip
count) from a corpus text and confirm the FULL sweep pipeline surfaces it.
A null from sweep.py is only trustworthy if this passes."""
import os,sys,numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,os.path.join(ROOT,"analysis")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from skipdecode import eng_to_idx, encipher_keyskip, idx_to_trans
import sweep as SW
Q=sc.default(); N=gp.N

plain=("BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE EXPERIENCE THE "
"KNOWLEDGE AND FIND YOUR TRUTH WITHIN THE SACRED CIRCUMFERENCE FOR ALL THINGS EMERGE "
"FROM THE VOID AND RETURN UNTO IT AGAIN AS THE INSTAR TUNNELS TOWARD THE LIGHT THAT "
"NO MAN MAY EXTINGUISH AND THE PILGRIM WHO WALKS THE PATH SHALL LOSE THE SELF TO GAIN THE WHOLE")
P=eng_to_idx(plain)
print(f"planted plaintext {len(P)} runes (mirrors real page length)")
REF=["mabinogion.txt","self_reliance.txt","king_in_yellow.txt","agrippa.txt",
     "book_of_the_law.txt","runepoem_oe.txt","solved_plaintext.txt","thematic.txt"]
texts=[(f,SW.load_text(os.path.join(ROOT,"data","keys",f))) for f in REF]
npass=0; ntot=0
for kt,o_true in [("king_in_yellow.txt",4000),("agrippa.txt",2201),("mabinogion.txt",50000),("self_reliance.txt",5000)]:
    K=SW.load_text(os.path.join(ROOT,"data","keys",kt))
    while o_true+len(P)*4>=len(K): o_true//=2
    for sign in (-1,1):
        C,skips,_=encipher_keyskip(P,K[o_true:],sign=sign,supp=0.83,seed=o_true+sign)
        ct=np.array(C,dtype=np.int64)
        hits,bg=SW.attack_page(ct,0,texts)
        ok=any(h[1]==kt and abs(h[4]-o_true)<=SW.MAXSKIP for h in hits)
        ntot+=1; npass+=ok
        tophit=max(hits)[0] if hits else float('nan')
        print(f"  {kt:20s} o={o_true:6d} sign={sign:+d} skips={sum(skips):2d} "
              f"best_screen={bg[0]:6.2f} tophit={tophit:6.2f}  recovered={'YES' if ok else 'NO '}")
print(f"\nRECALL GATE: {npass}/{ntot} planted keys recovered end-to-end by the sweep")
print("PASS" if npass>=ntot-1 else "FAIL -- still dropping real keys")
