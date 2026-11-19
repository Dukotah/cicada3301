"""C2 checker: recognize plaintext in SHORT rune windows (CHALLENGES.md, C2).

    python challenges/c2_short_recognizer.py                          # the quadgram baseline
    python challenges/c2_short_recognizer.py my_scorer.py             # your submission
    python challenges/c2_short_recognizer.py my_scorer.py --seed 7    # reproducible draw

Your file defines   score(idx: list[int]) -> float   (rune indices 0-28, higher = more
plaintext-like). For each length L, the checker draws fresh windows:

  positives   random L-rune windows of real text, transliterated to runes
  negatives   (a) uniform random runes - what a wrong key decodes to
              (b) the positive windows shuffled - same letters, structure destroyed

and reports TPR at a 1% false-positive rate, with the threshold set on the negatives.
Negatives (b) are the ones that matter: a scorer that only rewards letter frequency
passes (a) and fails (b), and the benchmark's shuffled_plant gate exists for the same reason.

The dev texts are public, so you can overfit them. Credit is decided on a held-out text
the maintainers run privately with the same code; see CHALLENGES.md.
"""
import argparse
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import skipdecode as sk  # noqa: E402

LENGTHS = (6, 8, 10, 12)
FPR = 0.01
DEV_TEXTS = ("solved_plaintext.txt", "self_reliance.txt", "thematic.txt")


def text_to_idx(path):
    raw = open(path, encoding="utf-8", errors="ignore").read().upper()
    return sk.eng_to_idx(re.sub(r"[^A-Z]", "", raw))


def baseline_score(idx):
    """Per-quadgram English log-probability of the transliteration (src/lp/score.py)."""
    from lp import score
    return score.default().score_norm(sk.idx_to_trans(idx))


def evaluate(score, texts, n=2000, seed=None, lengths=LENGTHS):
    rng = random.Random(seed)
    pools = [t for t in texts if len(t) > 100]
    rows = []
    for L in lengths:
        pos = []
        for _ in range(n):
            t = rng.choice(pools)
            i = rng.randrange(len(t) - L)
            pos.append(list(t[i:i + L]))
        uni = [[rng.randrange(C.N) for _ in range(L)] for _ in range(n)]
        shuf = [rng.sample(w, L) for w in pos]
        s_pos = [score(w) for w in pos]
        s_uni = sorted(score(w) for w in uni)
        s_shuf = sorted(score(w) for w in shuf)
        row = {"L": L}
        for name, neg in (("uniform", s_uni), ("shuffled", s_shuf), ("both", sorted(s_uni + s_shuf))):
            thr = neg[int((1 - FPR) * len(neg))]
            row[name] = sum(s > thr for s in s_pos) / n
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining score(idx) -> float")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--n", type=int, default=2000, help="windows per class per length")
    ap.add_argument("--text", action="append", help="evaluate on this text file instead of the dev set")
    a = ap.parse_args()

    score = C.load_module(a.submission).score if a.submission else baseline_score
    paths = a.text or [os.path.join(C.LP, "data", "keys", t) for t in DEV_TEXTS]
    texts = [text_to_idx(p) for p in paths]
    rows = evaluate(score, texts, n=a.n, seed=a.seed)

    who = a.submission or "baseline (quadgram)"
    print(f"C2 short recognizer - {who}   TPR at {FPR:.0%} FPR, n={a.n} per class")
    print(f"{'L':>4} {'vs uniform':>11} {'vs shuffled':>12} {'vs both':>9}")
    for r in rows:
        print(f"{r['L']:>4} {r['uniform']:>11.3f} {r['shuffled']:>12.3f} {r['both']:>9.3f}")
    mean = sum(r["both"] for r in rows) / len(rows)
    print(f"\nheadline (mean TPR vs both, L={'/'.join(map(str, LENGTHS))}): {mean:.3f}")


if __name__ == "__main__":
    main()
