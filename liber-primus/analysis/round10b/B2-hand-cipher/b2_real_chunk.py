"""B2 lane, Stage 2 (real data) — chunked/parallel runner.

Identical model, decoder, segment length, rho, iteration count and RNG discipline
as b2_decode.py; split by (offset, key length) so the 18 real configurations can
be run across cores instead of serially (~3.5 min per anneal single-threaded).

Usage:  PYTHONUTF8=1 python3 b2_real_chunk.py <offset> <k1,k2,...>
Writes: results_real_off<offset>_k<k1>-<kn>.json
"""
import io
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(REPO, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
from b2_sim import load_lp2, load_english_runes, N  # noqa: E402
from b2_decode import bigram_model, anneal  # noqa: E402
from lp import gematria as gp, score as _score  # noqa: E402

SEG, RHO, ITERS, RESTARTS = 800, 0.03, 2000, 2


def main():
    off = int(sys.argv[1])
    ks = [int(x) for x in sys.argv[2].split(",")]
    rng = random.Random(424242 + off * 97 + ks[0])
    q = _score.default()
    real = load_lp2()
    B = bigram_model(load_english_runes(60000))
    seg = np.asarray(real[off:off + SEG], dtype=np.int64)
    res = []
    for k in ks:
        s, kf, dec = anneal(seg, k, B, RHO, rng, ITERS, RESTARTS)
        txt = gp.indices_to_translit(dec)
        sc = q.score_norm(txt)
        res.append({"offset": off, "k": k, "viterbi": s, "quadgram": sc,
                    "key_found": kf, "text": txt[:160]})
        print(f"  off={off:5d} k={k:2d}: quadgram {sc:+.3f}  {txt[:80]}", flush=True)
    fn = os.path.join(HERE, "results_real_off%d_k%d-%d.json" % (off, ks[0], ks[-1]))
    json.dump({"segment_len": SEG, "rho": RHO, "iters": ITERS,
               "restarts": RESTARTS, "real": res},
              io.open(fn, "w", encoding="utf-8"))
    print("wrote", os.path.basename(fn))


if __name__ == "__main__":
    main()
