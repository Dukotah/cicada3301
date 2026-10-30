import sys, os, json, re
import numpy as np
sys.dont_write_bytecode=True
LP="C:/Users/Jeff/cicada3301/liber-primus"
sys.path.insert(0, LP+'/src'); sys.path.insert(0, LP+'/analysis/round19/I2'); sys.path.insert(0, LP+'/analysis/round10/L2-map')
from lp import gematria as g
import adjudicate as A
pan=A.Panel(LP+'/data/panels/panel-r36.npz'); ne=pan.ne_idx
def pm(x):
    x=np.asarray(x,dtype=np.int64); mu,sd,_,_=pan.cal(len(x)); z=(pan.raw(x)-mu)/sd; return float(z[ne].max())
txt=open(LP+'/data/keys/armada18/cicada_koans_and_lp_sections.txt',encoding='utf-8').read()
W=[]
for ln in txt.split('\n'):
    for w in re.sub(r'[^A-Z ]',' ',ln.upper()).split(): W.append(g.keyword_to_indices(w))
sent="THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED".split()
real=[r for w in sent for r in g.keyword_to_indices(w)]
rng=np.random.default_rng(37001)
print("n_words",len(W),"real n",len(real),"pmax_ne",pm(real))
vals=[]
for _ in range(400):
    # random bag of LP1 words (random positions), concatenated to >= len(real) runes then trimmed
    out=[]
    while len(out)<len(real): out+=W[rng.integers(len(W))]
    vals.append(pm(out[:len(real)]))
vals=np.array(vals)
# a control: random bag of runes (uniform)
rr=np.array([pm(rng.integers(0,29,len(real))) for _ in range(200)])
res={"real_sentence_pmax_ne":pm(real),"n":len(real),"random_LP1_word_bags":{"draws":400,"mean":float(vals.mean()),"max":float(vals.max()),"q95":float(np.quantile(vals,.95)),"frac_ge_real":float((vals>=pm(real)).mean())},"uniform_rune_strings":{"draws":200,"mean":float(rr.mean()),"max":float(rr.max())}}
print(json.dumps(res,indent=1)); json.dump(res,open(LP+'/analysis/round37/X1-redteam/rerun_u7_controlB.json','w'),indent=1)
