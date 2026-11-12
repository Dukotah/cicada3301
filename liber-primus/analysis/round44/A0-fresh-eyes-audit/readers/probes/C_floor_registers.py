# --- path preamble added when these probes were filed in the repo (they were written in a scratch dir) ---
import os as _o
_d = _o.path.dirname(_o.path.abspath(__file__))
while not _o.path.exists(_o.path.join(_d, "lpdata.py")):
    _d = _o.path.dirname(_d)
_PROBES = _d
_ROOT = _o.path.abspath(_o.path.join(_PROBES, "..", "..", "..", "..", "..", ".."))
# ---------------------------------------------------------------------------------------------------
"""G3 doublet-floor (min_d P(dP=d)) per register, derived from the committed panel-R36 trigram LMs
(log10 P(c|a,b)); stationary bigram of the order-2 chain -> first-difference distribution.
Also: for each register, the doublet rate an INDEPENDENT uniform-nonzero-step key would give, and the floor."""
import numpy as np
z=np.load(_ROOT+'/liber-primus/data/panels/panel-r36.npz',allow_pickle=True)
LM=np.power(10.0,z['LM'].astype(np.float64)); regs=list(z['registers'])
print("register       floor=min_d Pdp   argmin   2nd-min   P(d=0)   [LP2 observed 0.664%]")
for r,name in enumerate(regs):
    T=LM[r]                      # T[a,b,c]=P(c|a,b)
    pi=np.full((29,29),1/841.0)
    for _ in range(400):
        pi=np.einsum('ab,abc->bc',pi,T); pi/=pi.sum()
    d=np.zeros(29)
    for b in range(29):
        for c in range(29): d[(c-b)%29]+=pi[b,c]
    o=np.argsort(d)
    print(f"{name:13s} {100*d[o[0]]:8.3f}%        d={o[0]:2d}   {100*d[o[1]]:6.3f}%  {100*d[0]:6.2f}%")
