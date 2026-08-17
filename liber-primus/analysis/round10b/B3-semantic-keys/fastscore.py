"""Vectorised rune-level 4-gram scorer, so T2 can screen ~10^6 decodes.

Built from the SAME English source the repo's baseline uses (run_stats.english_baseline),
mapped onto Gematria Primus indices.  It is a DIFFERENT instrument from lp.score, so it
carries its own gate (see gate_fast() -- it must rank DIVINITY / FIRFUMFERENFE first on the
two solved keyed pages, exactly like the Latin-space scorer does).
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))

from lp import gematria as gp  # noqa
from run_stats import english_baseline  # noqa

N = gp.N
_TABLE = None


def table():
    global _TABLE
    if _TABLE is None:
        eng = np.array(english_baseline(), dtype=np.int64)
        cnt = np.ones(N ** 4, dtype=np.float32) * 0.05  # additive smoothing
        k = (eng[:-3] * N ** 3 + eng[1:-2] * N ** 2 + eng[2:-1] * N + eng[3:])
        np.add.at(cnt, k, 1.0)
        _TABLE = np.log10(cnt / cnt.sum()).astype(np.float32)
    return _TABLE


def score_rows(P):
    """P: (m, n) int array of rune indices. Returns (m,) mean log10 4-gram score."""
    T = table()
    k = (P[:, :-3] * N ** 3 + P[:, 1:-2] * N ** 2 + P[:, 2:-1] * N + P[:, 3:])
    return T[k].mean(axis=1)


def score_one(idxs):
    P = np.asarray(idxs, dtype=np.int64)[None, :]
    return float(score_rows(P)[0])


def decode_all_rotations(ct, key, sign, atbash):
    """ct: (n,) int array. key: tuple. Returns (L, n) decoded array, one row per rotation."""
    n = len(ct)
    L = len(key)
    base = (N - 1 - ct) if atbash else ct
    ka = np.asarray(key, dtype=np.int64)
    j = np.arange(n)
    rots = (j[None, :] + np.arange(L)[:, None]) % L
    stream = ka[rots]
    return (base[None, :] + sign * stream) % N
