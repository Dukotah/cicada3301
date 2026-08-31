#!/usr/bin/env python3
"""Rebuild lib_padsweep's index-space trigram prefilter model OFFLINE.

lib_padsweep.trigram_model() trains a 29x29x29 rune-index trigram model from
data/{kjv,moby,pride,war}.txt. Those raw corpora are gitignored (see
data/BUILD-QUADGRAMS.md) and Gutenberg is blocked at this environment's egress
proxy, so on a fresh checkout the model silently falls back to Laplace-only —
i.e. UNIFORM (every trigram = log10(1/29)). A uniform prefilter scores every key
offset identically, so lib_padsweep.control() reports survival 0.0 and the whole
dense-scan lane is dead-on-arrival. (This is exactly README lesson #1: a null from
an unvalidated instrument is not a negative — and here the instrument was quietly
unvalidated on any clone without the corpus.)

This script rebuilds an equivalent model from the COMMITTED `english_quadgrams.txt`
by pushing every quadgram through the repo's own `eng_to_idx` and accumulating its
consecutive index-trigrams, weighted by the quadgram's corpus count. It writes
`analysis/round17/trigram_idx.npy` in the exact format trigram_model() caches, so
the instrument loads it transparently. Fully offline and reproducible.

Run from liber-primus/:  python analysis/round18/marsaglia/build_trigram_from_quadgrams.py
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))   # liber-primus/
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
from lp import gematria as gp          # noqa: E402
import skipdecode as sk                # noqa: E402

N = gp.N
QUAD = os.path.join(ROOT, "data", "english_quadgrams.txt")
CACHE = os.path.join(ROOT, "analysis", "round17", "trigram_idx.npy")


def build():
    counts = np.ones((N, N, N), dtype=np.float64)      # Laplace, same as the original
    n_quad = 0
    with open(QUAD, encoding="ascii") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 2:
                continue
            quad, c = parts[0], float(parts[1])
            idx = sk.eng_to_idx(quad)                  # same transform the corpus model used
            for a, b, cc in zip(idx, idx[1:], idx[2:]):
                counts[a, b, cc] += c
            n_quad += 1
    model = np.log10(counts / counts.sum(axis=2, keepdims=True)).astype(np.float32)
    return model, n_quad


def main():
    model, n_quad = build()
    # sanity: a trained model must NOT be uniform
    uniform = np.log10(1.0 / N)
    spread = float(model.max() - model.min())
    np.save(CACHE, model)
    print(f"quadgrams read : {n_quad:,}")
    print(f"wrote          : {CACHE}")
    print(f"model spread   : {spread:.3f}  (uniform would be 0.000; ~{uniform:.3f} flat)")
    tri = sk.eng_to_idx("ETHER")[:3]      # a common English index-trigram
    print(f"sanity trigram : logP[{tri}] = {float(model[tuple(tri)]):.3f}  vs flat {uniform:.3f}")
    assert spread > 1.0, "model is ~uniform; rebuild failed"
    print("OK: non-uniform English-trained trigram model in place")


if __name__ == "__main__":
    main()
