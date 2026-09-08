#!/usr/bin/env python3
"""Round 27 / P2 -- shared Python-reference plumbing for the validation harness.

Imports the R25 pipeline VERBATIM (runner.py + its module graph); reimplements nothing.
Everything the checks need from the Python side of the parity comparison lives here:

    stage_a_full(w, cipher=None)  -> the exact per-seed artifacts a C engine must match
    score_many(seeds, ...)        -> multiprocess pmax scoring (6 workers by default)
    build_plant(seed)             -> the skip_by_two planted construct for ANY seed
                                     (same recipe as runner.planted_seed_selftest)
    vectors()                     -> parsed P0-spec/vectors.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R25 = os.path.join(LP, "analysis", "round25", "compute-tail")
if R25 not in sys.path:
    sys.path.insert(0, R25)

import runner  # noqa: E402  -- the R25 pipeline, verbatim
import driftbeam as DB  # noqa: E402
import adjudicate as AD  # noqa: E402
import hitfn20 as H  # noqa: E402

VECTORS_PATH = os.path.join(LP, "analysis", "round27", "P0-spec", "vectors.json")
P1_DIR = os.path.join(LP, "analysis", "round27", "P1-engine")

CAND_BAR = runner.SCREEN_BAR                 # 5.0 -- the ONLY bar the C engine gates on
CLAIM_BAR = 7.383520294328688                # pair, N=1e6, alpha=0.01 (Python-side only)
HARD_GATE = CLAIM_BAR - 1.5                  # 5.883520294328688 -- false-reject hard gate

_VECTORS = None


def vectors():
    global _VECTORS
    if _VECTORS is None:
        with open(VECTORS_PATH) as f:
            _VECTORS = json.load(f)
    return _VECTORS


def stage_a_full(w, cipher=None):
    """runner.stage_a with intermediates exposed (same calls, same order as make_vectors)."""
    C = runner.C_SCREEN if cipher is None else list(cipher)[: runner.L_SCREEN]
    K = runner.word_stream(w, runner.L_SCREEN * 6 + 64)
    d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=runner.SCREEN_BEAM_W,
                       **DB.PRESETS[runner.PRESET])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return {
        "seed": w,
        "ks128": runner.word_stream(w, 128),
        "pmax": float(a["pmax"]),
        "beam_score": float(d["score"]),
        "plain_idx": d["plain_idx"],
        "ptr_end": d["ptr_end"],
        "n_skips": d["n_skips"],
        "nchars": d["nchars"],
    }


# ---------------------------------------------------------------- multiprocess scoring
_MP_CIPHER = None


def _mp_init(cipher):
    global _MP_CIPHER
    _MP_CIPHER = cipher


def _mp_score(w):
    if _MP_CIPHER is None:
        return (w, runner.stage_a(w))
    r = stage_a_full(w, cipher=_MP_CIPHER)
    return (w, r["pmax"])


def score_many(seeds, cipher=None, workers=6, chunksize=64, progress_every=20000):
    """pmax for each seed via the Python reference, on `workers` processes.
    Returns list of (seed, pmax) in input order."""
    import multiprocessing as mp
    out = []
    with mp.Pool(workers, initializer=_mp_init, initargs=(cipher,)) as pool:
        for i, row in enumerate(pool.imap(_mp_score, seeds, chunksize=chunksize)):
            out.append(row)
            if progress_every and (i + 1) % progress_every == 0:
                print("  pyref scored %d/%d" % (i + 1, len(seeds)), file=sys.stderr)
    return out


# ---------------------------------------------------------------- plant construct
def build_plant(seed, L=None):
    """The skip_by_two planted construct for an arbitrary seed -- byte-identical recipe
    to runner.planted_seed_selftest / make_vectors.py (supp=0.83, rng=random.Random(seed),
    truth = self_reliance eng_to_idx[5000:5000+L], keystream = word_stream(seed, L*6+64)).
    Returns dict(truth_idx, keystream, cipher_idx)."""
    import skipdecode as sk
    if L is None:
        L = runner.L_HIT
    with open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
              encoding="utf-8", errors="ignore") as f:
        truth = sk.eng_to_idx(f.read())[5000:5000 + L]
    K = runner.word_stream(seed, L * 6 + 64)
    prng = random.Random(seed)
    C, j, c_prev = [], 0, None
    for p in truth:
        while True:
            c = (p + K[j]) % 29
            if c_prev is not None and c == c_prev and prng.random() < 0.83:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return {"seed": seed, "truth_idx": truth, "keystream": K, "cipher_idx": C}


# ---------------------------------------------------------------- misc
def expected_lm_sha256():
    """sha256 of the panel_lm.f32 export the P1 lane must produce (9x24389 LE float32,
    row-major, from round19/I2/models/panel.npz key LM)."""
    import hashlib
    import numpy as np
    z = np.load(os.path.join(LP, "analysis", "round19", "I2", "models", "panel.npz"))
    return hashlib.sha256(z["LM"].astype("<f4").reshape(9, 24389).tobytes()).hexdigest()
