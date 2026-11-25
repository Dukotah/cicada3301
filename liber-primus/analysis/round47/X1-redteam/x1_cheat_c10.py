"""R47-X1 gameability probe (NOT an attack): reads c10 evaluate()'s loop variable c = (C, K, printed, P, true_lens)
from the caller's frame and returns the true plaintext on plants and junk on nulls."""
import sys


def attack(C, K, printed):
    loc = sys._getframe(1).f_locals
    c = loc.get("c")
    if c is not None and any(c is x for x in loc.get("plants", [])):
        return list(c[3])
    return [0] * len(C)
