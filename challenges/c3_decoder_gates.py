"""C3 checker: certify a decoder on the plant-and-recover gates (CHALLENGES.md, C3).

    python challenges/c3_decoder_gates.py                                   # reference beam: 7/7
    python challenges/c3_decoder_gates.py challenges/examples/rigid_decoder.py   # 4/7, not qualified
    python challenges/c3_decoder_gates.py my_decoder.py                     # your submission

Your file defines   decode(C, K, sign=-1) -> {"score": float, "translit": str, "plain_idx": [int]}
exactly as liber-primus/benchmark/README.md describes. `score` is per-symbol English
log-probability. Every gate asserts both directions: the plant is recovered AND a wrong
key stays in noise.

7/7 is the qualifier. A sweep run through a qualified decoder can be filed as a negative;
a sweep through an unqualified one is an unknown, however large it was.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import gates  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining decode(C, K, sign=-1)")
    a = ap.parse_args()

    decoder = C.load_module(a.submission).decode if a.submission else None
    print(f"C3 - {a.submission or 'reference decoder (skip-aware beam)'}")
    rows = gates.run_all(decoder=decoder, verbose=True)
    n_ok = sum(r["passed"] for r in rows)
    print("QUALIFIED" if n_ok == len(rows) else
          "NOT QUALIFIED: a failing gate means this decoder cannot see the family that gate plants.")
    sys.exit(0 if n_ok == len(rows) else 1)


if __name__ == "__main__":
    main()
