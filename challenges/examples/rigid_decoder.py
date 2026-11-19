"""C3 example: the RIGID decoder that Round 8 swept 2.52e9 decodes with. It should NOT qualify:
it cannot see a keystream that desyncs under the skip filter (benchmark/README.md)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _common  # noqa: E402,F401  (sets sys.path)
import skipdecode as sk  # noqa: E402


def decode(C, K, sign=-1):
    return sk.rigid_decode(C, K, sign=sign)
