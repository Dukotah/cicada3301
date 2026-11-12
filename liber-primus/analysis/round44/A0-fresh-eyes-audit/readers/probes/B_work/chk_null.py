# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
import random, numpy as np
from drift_kappa import *
rng=random.Random(3301)
out=[]
for t in range(40):
    C=null_stream(rng); z=zlags(C); b,r=scan(z); out.append((round(b[0],2),b[1],t))
out.sort(); print(out[-4:])
# inspect the top one
t=out[-1][2]
rng=random.Random(3301)
for k in range(t+1): C=null_stream(rng)
z=zlags(C); p,d=out[-1][1]; idx,w=FILT[(p,d)]
print("filter lags",idx[:12],"weights",np.round(w[:12],2)); print("z at those",np.round(z[idx][:12],2))
