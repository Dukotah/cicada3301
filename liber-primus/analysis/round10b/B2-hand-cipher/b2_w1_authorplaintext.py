"""B2 lane, W1-hardening — recompute the drift-invariant key-length bound using
the AUTHOR'S OWN plaintext statistics (the five SOLVED Liber Primus pages),
not generic English prose.

The bound is: for a Vigenere with key length k,
    E[IoC*29 of ciphertext] = 1 + (IoC*29 of plaintext - 1) / k
and this is invariant to (a) key-phase drift of any rate, (b) any transposition
of the plaintext, and (c) any monoalphabetic substitution of the plaintext --
because IoC is invariant under permutation of positions and of symbols.

Usage: PYTHONUTF8=1 python3 b2_w1_authorplaintext.py
"""
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(REPO, "liber-primus")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp, ciphers, corpus  # noqa: E402
from b2_sim import load_lp2, ioc_norm, N  # noqa: E402


import re


def solved_plaintexts():
    """The AUTHOR'S OWN plaintext, in rune space.

    Page 01 is taken as the direct Atbash decode of its runes (verified
    readable).  Pages 03/05/14 are taken from the documented English plaintext
    held in the corpus and re-encoded to Gematria Primus indices with the
    greedy-digraph runeglish parser.  (Pages 03/14 are NOT re-derived from
    runes here because their F-interrupter masks are only recoverable by the
    beam search in tests/validate.py; the documented plaintext is the same
    object and is what we want the language statistics of.)
    """
    out = {}
    p = corpus.page_by_label("Runes - 01.jpg")
    out["01_A_WARNING(atbash decode)"] = ciphers.atbash_indices(
        gp.runes_to_indices(p["runes"]))
    for lab, name in (("05.jpg", "05_SOME_WISDOM"),
                      ("03.jpg", "03_WELCOME"),
                      ("14.jpg", "14_A_KOAN/CIRCUMFERENCE")):
        txt = corpus.page_by_label(lab)["plaintext"]
        txt = re.sub(r"=\s*\d+\*?", " ", txt)      # strip gematria value columns
        txt = re.sub(r"[^A-Za-z]", "", txt).upper()
        out[name] = gp.keyword_to_indices(txt)
    return out


def main():
    real = load_lp2()
    n = len(real)
    pts = solved_plaintexts()
    rows = []
    allpt = []
    for k, v in pts.items():
        allpt.extend(v)
        rows.append({"page": k, "n": len(v), "ioc29": ioc_norm(np.array(v)),
                     "text": gp.indices_to_translit(v)[:70]})
        print(f"  {k:20s} n={len(v):4d}  IoC*29 = {rows[-1]['ioc29']:.4f}   "
              f"{rows[-1]['text'][:60]}")
    ioc_author = ioc_norm(np.array(allpt))
    print(f"\n  POOLED author plaintext: n={len(allpt)}  IoC*29 = {ioc_author:.4f}")

    rs = np.random.RandomState(2027)
    nulls = [ioc_norm(rs.randint(0, N, n)) for _ in range(400)]
    mu, sd = float(np.mean(nulls)), float(np.std(nulls, ddof=1))
    real_ioc = ioc_norm(real)
    print(f"  LP2 0-54 IoC*29 = {real_ioc:.5f}   uniform null {mu:.5f} +/- {sd:.5f}"
          f"   -> z = {(real_ioc-mu)/sd:+.2f}")

    print("\n  Predicted ciphertext IoC*29 under a length-k Vigenere over the "
          "AUTHOR'S plaintext (drift-invariant):")
    pred = {}
    for k in (4, 8, 12, 16, 24, 32, 48, 64, 96, 128, 200, 400, 800):
        v = 1 + (ioc_author - 1) / k
        pred[k] = v
        print(f"    k={k:4d} -> IoC*29 {v:.5f}   z vs uniform null {(v-mu)/sd:+9.1f}"
              f"   z vs REAL {(v-real_ioc)/sd:+9.1f}")
    k3 = (ioc_author - 1) / (3 * sd)
    k5 = (ioc_author - 1) / (5 * sd)
    print(f"\n  => EXCLUDED: every key length k < {k3:.0f} at 3 sigma, "
          f"k < {k5:.0f} at 5 sigma.")
    json.dump({"pages": rows, "ioc29_author_pooled": ioc_author,
               "ioc29_real_lp2": real_ioc, "null_mean": mu, "null_sd": sd,
               "real_z": (real_ioc - mu) / sd, "predicted": pred,
               "k_excluded_below_3sigma": k3, "k_excluded_below_5sigma": k5},
              io.open(os.path.join(HERE, "results_w1_author.json"), "w",
                      encoding="utf-8"))
    print("wrote results_w1_author.json")


if __name__ == "__main__":
    main()
