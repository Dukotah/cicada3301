"""C9 example submission: the C3 reference beam (skip-aware, keyskip1 relation). It qualifies on the C3
gates and fails V-BACK and V-NULL, which is the point of C9.

    python challenges/c9_rejection_loops.py challenges/examples/c9_reference_decoder.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _common  # noqa: E402,F401  (sets sys.path)
import skipdecode as sk  # noqa: E402


def decode(C, K, sign=-1):
    return sk.beam_decode(C, K, sign=sign, o=0, beam_w=400, max_skip=3)
