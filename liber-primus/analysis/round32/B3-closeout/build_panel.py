"""Rebuild the I2 panel into THIS lane's dir (I2/models is gitignored and absent on this checkout)."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round19", "I2"))
import build_models as bm
bm.MODELDIR = os.path.join(HERE, "models"); bm.HERE = HERE
bm.main()
