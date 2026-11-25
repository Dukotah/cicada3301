"""[R47-H2: the R47-H1 C10 checker, kept verbatim except this note and the sys.path line, so that R47-X1's
crossing of it (481/500, 488/500) stays reproducible. Superseded by challenges/c10_shuffled_lengths.py.
    python liber-primus/analysis/round47/H2-harden/c10_v1_keyed.py liber-primus/analysis/round47/X1-redteam/x1_c10_beam_attack.py --n 500 --seed 4702
NOTE: this version imports the submission IN-PROCESS (R47-X1 §3.4: frame reading passes it).]

C10 checker: an attack that still works when the printed word lengths are shuffled (CHALLENGES.md, C10).

    python challenges/c10_shuffled_lengths.py --self-test                     # baseline + true-length ceiling
    python challenges/c10_shuffled_lengths.py my_attack.py                    # your attack, fresh seed
    python challenges/c10_shuffled_lengths.py my_attack.py --n 500 --seed <maintainer seed> --text heldout.txt

Your file defines   attack(C, K, printed) -> list[int]   (your decoded plaintext, rune indices 0-28), where
  C        list of cipher rune indices (0-28) for one unit (a few whole sentences, 236-472 runes)
  K        the claimed base keystream (list of ints 0-28, long enough for every jump)
  printed  the print: a list of sentences, each a list of printed word lengths. Sentence boundaries and the
           per-sentence MULTISET of lengths are true; the ORDER inside each sentence is shuffled (R46-L1 b').

The plant is the R37-U2b word-jump construction on the benchmark's derived-key family. Rune i of TRUE word k
is enciphered with K[i + J_k], J_k = S[0] + ... + S[k], S[j] = PRIMES[j mod 29] = 2, 3, 5, ..., 109, and
c = (p + K[.]) mod 29 (decode p = c - K[.]). Plaintext: whole English sentences (dev texts; held-out at review).
The NULL is the same unit with the same print, enciphered under an independent key K'; the attack is still
handed K. So an attack has to find the true word starts inside each sentence.

A plant PASSES when your output's rune recovery is >= 0.90 (R37 judge()'s bar) and the checker-recomputed
English score is >= -5.2. On the nulls your output must stay at or below -5.2 on >= 95 % of units (an attack
that turns every key into English is not an instrument).

Baseline (the L1 battery's rule for U2b): put the jumps at the PRINTED word starts and decode.
Ceiling (positive control): the same decoder at the TRUE starts. The checker also prints, for reference, the
baseline's power as a plain detector at FPR 0.01 (PREREG Addendum 2: it is high; recovery is what fails).

Finish line: >= 0.80 of plants pass and the null condition holds, at --n 500 on the maintainers' seed and
held-out text. Exit 0 = finish line met (or, with --self-test, the controls held).
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "challenges"))
import _heavy as H  # noqa: E402
import _common as C  # noqa: E402
from lp import gematria as gp  # noqa: E402

N = H.N
LMIN, LMAX = H.LP2_PAGE, 2 * H.LP2_PAGE
S = [gp.PRIMES[j % 29] for j in range(4096)]
FPR, FINISH = 0.01, 0.80
MIN_RECOVERY, ENGLISH, NULL_OK = 0.90, -5.2, 0.95


def jumps(lens):
    """Pointer offset per rune: rune i of word k uses K[i + J_k]."""
    out, J = [], 0
    for k, l in enumerate(lens):
        J += S[k]
        out.extend([J] * l)
    return out


def encipher(P, lens, K):
    off = jumps(lens)
    return [(p + K[i + off[i]]) % N for i, p in enumerate(P)]


def decode_with(C_, K, lens):
    off = jumps(lens)
    return [(c - K[i + off[i]]) % N for i, c in enumerate(C_)]


def make_unit(rng, sents):
    while True:
        i = rng.randrange(len(sents))
        unit, tot = [], 0
        while tot < LMIN and i < len(sents):
            unit.append(sents[i])
            tot += sum(len(w) for w in sents[i])
            i += 1
        if LMIN <= tot <= LMAX:
            return unit


def make_cases(n, seed, sents):
    """n plants and n nulls. Each case: (C, K, printed, P, true_lens)."""
    rng = random.Random(f"{seed}|c10")
    plants, nulls = [], []
    for arm in (plants, nulls):
        for _ in range(n):
            unit = make_unit(rng, sents)
            true_lens = [len(w) for s in unit for w in s]
            P = [x for s in unit for w in s for x in w]
            printed = []
            for s in unit:
                v = [len(w) for w in s]
                rng.shuffle(v)
                printed.append(v)
            need = len(P) + sum(S[:len(true_lens)]) + 8
            K = H.rand_key(rng, need)
            Kenc = K if arm is plants else H.rand_key(rng, need)
            arm.append((encipher(P, true_lens, Kenc), K, printed, P, true_lens))
    return plants, nulls


def baseline(C_, K, printed):
    return decode_with(C_, K, [l for s in printed for l in s])


def recovery(x, P):
    return sum(1 for a, b in zip(x, P) if a == b) / len(P)


def evaluate(fn, plants, nulls):
    """fn(C, K, printed) -> plain_idx. Returns pass rate on plants and null false-positive rate."""
    ok = 0
    recs, sp, sn = [], [], []
    for c in plants:
        out = list(fn(list(c[0]), list(c[1]), [list(s) for s in c[2]]))
        r, s = recovery(out, c[3]), H.english_score(out)
        recs.append(r)
        sp.append(s)
        ok += r >= MIN_RECOVERY and s >= ENGLISH
    for c in nulls:
        sn.append(H.english_score(list(fn(list(c[0]), list(c[1]), [list(s) for s in c[2]]))))
    fp = sum(1 for s in sn if s > ENGLISH) / len(sn)
    det, _ = H.power(sp, sn, FPR)
    return {"pass": ok / len(plants), "k": ok, "n": len(plants), "null_fp": fp,
            "mean_recovery": sum(recs) / len(recs), "detect_power_fpr01": det}


def row(name, r):
    print(f"  {name:44s} {r['k']:>4}/{r['n']:<4} {r['pass']:6.3f} {str(H.wilson(r['k'], r['n'])):>15} "
          f"{r['mean_recovery']:9.3f} {r['null_fp']:8.3f} {r['detect_power_fpr01']:10.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining attack(C, K, printed) -> plain_idx")
    ap.add_argument("--n", type=int, default=500, help="plants and nulls each (scored run: 500)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--text", action="append", help="English plaintext source(s) instead of the dev texts")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    seed = H.resolve_seed(a.seed)
    sents = H.english_sentences(a.text) if a.text else H.english_sentences()
    H.banner("C10 attack under shuffled word lengths", seed, f"n={a.n} plants + {a.n} nulls, FPR {FPR}")
    plants, nulls = make_cases(a.n, seed, sents)
    exact = sum(decode_with(c[0], c[1], c[4]) == c[3] for c in plants)
    same = 0
    for c in plants:
        k, ident = 0, True
        for s in c[2]:
            if s != c[4][k:k + len(s)]:
                ident = False
            k += len(s)
        same += ident
    mean_len = sum(len(c[3]) for c in plants) / len(plants)
    print(f"units: mean {mean_len:.0f} runes; {same}/{len(plants)} plants whose shuffle left every sentence's order intact")

    t0 = time.time()
    print(f"\n  {'attack':44s} {'plants ok':>9} {'rate':>6} {'Wilson 95%':>15} {'mean rec':>9} {'null FP':>8} {'detect@1%':>10}")
    rb = evaluate(baseline, plants, nulls)
    row("baseline: jumps at printed starts (L1 rule)", rb)
    truth = {tuple(c[0]): c[4] for c in plants + nulls}
    rc = evaluate(lambda C_, K, pr: decode_with(C_, K, truth[tuple(C_)]), plants, nulls)
    row("ceiling: jumps at TRUE starts (control)", rc)
    controls = exact == len(plants) and rc["pass"] >= 0.95

    if a.self_test or not a.submission:
        print(f"\ntrue-length decode reproduces the plaintext: {exact}/{len(plants)}   ({time.time() - t0:.0f}s)")
        print("SELF-TEST " + ("PASS" if controls else "FAIL"))
        sys.exit(0 if controls else 1)

    fn = C.load_module(a.submission).attack
    t1 = time.time()
    r = evaluate(fn, plants, nulls)
    row(a.submission[-44:], r)
    print(f"  ({time.time() - t1:.0f}s)")
    done = controls and r["pass"] >= FINISH and r["null_fp"] <= 1 - NULL_OK
    if done and a.n < 500:
        print("Looks good: re-run with --n 500 before you submit (the scored run uses 500).")
    print(f"\nneed pass rate >= {FINISH} and null FP <= {1 - NULL_OK:.2f}: "
          + ("FINISH LINE MET" if done and a.n >= 500 else "not yet"))
    sys.exit(0 if done and a.n >= 500 else 1)


if __name__ == "__main__":
    main()
