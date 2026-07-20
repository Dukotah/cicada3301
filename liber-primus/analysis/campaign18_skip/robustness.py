"""Gate part 2: realistic-length robustness + false-positive ceiling.
Determines the discovery threshold for the corpus sweep."""
import os, sys, random
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,"..",".."))
sys.path.insert(0,os.path.join(ROOT,"src")); sys.path.insert(0,HERE)
from lp import gematria as gp, score as sc
from skipdecode import eng_to_idx, idx_to_trans, encipher_keyskip, beam_decode
Q=sc.default()

def load(name): return open(os.path.join(ROOT,"data","keys",name),encoding="utf-8",errors="ignore").read()

# --- true-positive robustness: several texts/offsets, realistic page length ~230 ---
plain=("BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE "
"KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK "
"OR THE MESSAGE WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED THE "
"INSTAR EMERGES AND THE PILGRIM WALKS THE PATH OF THE CIRCUMFERENCE UNTO THE END")
P=eng_to_idx(plain)
print("=== TRUE-POSITIVE robustness (realistic length %d, soft filter supp=0.83) ==="%len(P))
for kt in ["mabinogion.txt","king_in_yellow.txt","agrippa.txt","book_of_the_law.txt"]:
    K=eng_to_idx(load(kt))
    for o in (137,4096):
        C,skips,_=encipher_keyskip(P,K[o:],sign=-1,supp=0.83,seed=o+7)
        dbl=sum(1 for i in range(1,len(C)) if C[i]==C[i-1])/(len(C)-1)
        bd=beam_decode(C,K,sign=-1,o=o,beam_w=600,max_skip=3)
        m=sum(a==b for a,b in zip(bd['plain_idx'],P))/len(P)
        print(f"  {kt:22s} o={o:5d} skips={sum(skips):2d} dbl={dbl*100:4.2f}%  beam={bd['score']:6.3f}  match={m*100:5.1f}%")

# --- FALSE-POSITIVE ceiling: beam vs many WRONG (key,offset) on real-ish ct ---
print("\n=== FALSE-POSITIVE ceiling: beam on WRONG keys/offsets ===")
# make one realistic ciphertext, then attack with wrong keys at random offsets
K0=eng_to_idx(load("self_reliance.txt")); C,_,_=encipher_keyskip(P,K0[900:],sign=-1,supp=0.83,seed=3301)
wrongs=["mabinogion.txt","king_in_yellow.txt","agrippa.txt","thematic.txt","words_expanded.txt"]
rng=random.Random(11); scores=[]
for _ in range(400):
    kt=rng.choice(wrongs); WK=eng_to_idx(load(kt)); o=rng.randint(0,len(WK)-len(C)-16)
    s=beam_decode(C,WK,sign=rng.choice([-1,1]),o=o,beam_w=300,max_skip=3)['score']
    scores.append(s)
scores.sort(reverse=True)
import statistics as st
print(f"  trials={len(scores)}  max={scores[0]:.3f}  p99={scores[int(len(scores)*0.01)]:.3f}  "
      f"mean={st.mean(scores):.3f}  min={scores[-1]:.3f}")
print(f"  -> discovery threshold should sit above null-max ({scores[0]:.2f}); "
      f"genuine English lands ~ -4.0 to -4.5")
print(f"  top-5 null scores: {[round(x,2) for x in scores[:5]]}")
