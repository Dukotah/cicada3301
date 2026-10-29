"""X1/R33 target 2: replicate I4's D5c (frozen m_NV=14.0128) on a THIRD clean key (b'CICADA-X1R33') at L=240 and L=120.
Reuses round32/I4 extract.py recipe verbatim (POPS patched to the new key/seeds); outputs only into this directory.
Run: python d5c_replicate.py <L>"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
I4 = os.path.abspath(os.path.join(HERE, '..', '..', 'round32', 'I4-nonfold-seal'))
os.environ['I4_L'] = sys.argv[1]
sys.path.insert(0, I4)
import shim
import extract as X
shim.HERE = HERE          # outputs (feat_*.json) land here, not in I4
L = int(sys.argv[1])
KEY = b"CICADA-X1R33"
X.POPS.update({f"x1_nv_{L}": (["EN_NOVOWEL"], KEY, 300, 52000, 46000),
               f"x1_en_{L}": (["EN_MODERN"], KEY, 30, 53100, 48800),
               f"x1_sp_{L}": (["LATIN", "DE", "OE", "EN_KJV"], KEY, 12, 54500, 49900)})
X.FAST = X.FAST + tuple(f"x1_{p}_{L}" for p in ("nv", "en", "sp"))
os.chdir(HERE)
for p in ("en", "sp", "nv"):
    X.main(f"x1_{p}_{L}")
