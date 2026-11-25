"""C10 checker: find the key AND the word starts when the printed lengths are shuffled (CHALLENGES.md, C10).

    python challenges/c10_shuffled_lengths.py --self-test                     # baselines (i) true spaces, (ii) printed
    python challenges/c10_shuffled_lengths.py my_attack.py --n 20             # iterate
    python challenges/c10_shuffled_lengths.py my_attack.py --seed <maintainer seed> --text heldout.txt   # scored (n=100)

R47-H2 redesign (H1 PREREG Addendum 3). The R47-H1 version handed the attack the key; R47-X1 crossed it in a
minute with a beam over each sentence's length orderings (0.962), so with the key in hand the (b') loss was the
decoder's, not the information's. That version is kept, with X1's crossing, in
liber-primus/analysis/round47/H2-harden/c10_v1_keyed.py. Here the key is UNKNOWN, drawn from a stated bounded
family that the repo's decoder searches exhaustively when the word spaces are true (baseline (i) recovers it), so
the one added difficulty is the shuffled print.

Your file defines   attack(C, printed) -> list[int]   (your decoded plaintext, rune indices 0-28), where
  C        cipher rune indices (0-28) for one unit (whole English sentences, 236-472 runes)
  printed  a list of sentences, each a list of printed word lengths. Sentence boundaries and each sentence's
           MULTISET of lengths are true; the ORDER inside each sentence is shuffled (R46-L1 regime b').
It runs in an isolated child process (challenges/_sandbox.py), one unit per call, in random order, with a
wall-clock limit of --budget seconds per call (default 60; a timed-out unit fails). It is never shown the key,
the key index, the plaintext or the seed.

THE KEY FAMILY (public, bounded: F = 65,536 keys). Key s in [0, F) is the counter-mode stream
    K_s[t] = splitmix64(SALT + s * 2**32 + t) mod 29,    t = 0, 1, 2, ...        (key_stream / key_block below)
THE PLANT is the R37-U2b word-jump construction: rune i of TRUE word k is enciphered with K_s[i + J_k],
J_k = S[0] + ... + S[k], S[j] = PRIMES[j mod 29] = 2, 3, 5, ..., 109, and c = (p + K) mod 29 (decode p = c - K).
s is drawn uniformly per unit. THE NULL is a unit with the same kind of print enciphered under a key from
OUTSIDE the family (s >= 2**20), so no key you can search decodes it.

A plant PASSES when your output's rune recovery is >= 0.90 (R37 judge()'s bar) and the checker-recomputed
English score is >= -5.2. Your output on the nulls must stay at or below -5.2 on >= 95 % of them.

Baselines (the repo's decoder, exhaustive over all F keys: decode, rank by a rune-bigram score, re-score the top
64 with the repo's quadgram score, return the best):
  (i)  with the TRUE word lengths in order (ceiling; not available to you): recovers the plant;
  (ii) with jumps at the PRINTED starts (the L1 battery's rule).
STATUS: RETIRED pending Round 48. H1 PREREG Addendum 3 fixed the rule FINISH = max(0.80, best in-house + 0.20)
before any number; the obvious in-house composition (rank all F keys by the printed-start decode, run R47-X1's
beam on the top 512) recovered 88/100 at seed 4710, so the rule gives 1.10 > 0.95 and C10 is not offered.
The checker stays as an instrument for the R48 re-scope (larger family, doublet filter, other constructions).
Exit 0 = instrument bar reached at the scored size (or, with --self-test, the controls held). Nothing is credited.
"""
import argparse
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _heavy as H  # noqa: E402
from lp import gematria as gp  # noqa: E402

N = H.N
LMIN, LMAX = H.LP2_PAGE, 2 * H.LP2_PAGE
S = [gp.PRIMES[j % 29] for j in range(4096)]
F_KEYS = 1 << 16
SALT = 0xC10C_4702_B1A5_0000
NULL_KEY_MIN = 1 << 20
MIN_RECOVERY, ENGLISH, NULL_OK = 0.90, -5.2, 0.95
SCORED_N = 100
FINISH = 0.80               # instrument bar only. H1 PREREG Addendum 3's rule gave FINISH = max(0.80, B + 0.20) with
                            # B = 0.88 (in-house two-stage (iv), m = 512) -> 1.10 > 0.95, so C10 is NOT published as a
                            # challenge: RETIRED pending a Round 48 re-scope (R47-H2 RESULTS §4).
RETIRED = ("C10 is retired pending Round 48: an in-house two-stage attack (printed-start key ranking + R47-X1's "
           "beam on the top 512) already recovers 0.88 (R47-H2)")
TOPK = 64
M64 = (1 << 64) - 1


# ------------------------------------------------------------------ the key family
def _splitmix(z):
    z = (z + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


def key_stream(s, length):
    """K_s[0:length] as a list (pure Python)."""
    base = (SALT + (s << 32)) & M64
    return [_splitmix((base + t) & M64) % N for t in range(length)]


def key_block(s_lo, s_hi, ts):
    """numpy uint8 array [s_hi - s_lo, len(ts)]: K_s[t] for s in [s_lo, s_hi), t in ts (vectorised splitmix)."""
    import numpy as np
    with np.errstate(over="ignore"):
        s = np.arange(s_lo, s_hi, dtype=np.uint64)
        z = (np.uint64(SALT) + (s << np.uint64(32)))[:, None] + np.asarray(ts, dtype=np.uint64)[None, :]
        z = z + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
        return (z % np.uint64(N)).astype(np.uint8)


# ------------------------------------------------------------------ the plant
def jumps(lens):
    """Pointer offset per rune: rune i of word k uses K[i + J_k]."""
    out, J = [], 0
    for k, l in enumerate(lens):
        J += S[k]
        out.extend([J] * l)
    return out


def positions(lens):
    return [i + o for i, o in enumerate(jumps(lens))]


def encipher(P, lens, K):
    return [(p + K[t]) % N for p, t in zip(P, positions(lens))]


def decode_with(C_, K, lens):
    return [(c - K[t]) % N for c, t in zip(C_, positions(lens))]


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
    """n plants and n nulls. Each case: dict(C, printed, P, true_lens, s). s is the key index (plants: in the
    family; nulls: outside it). Only C and printed are ever sent to a submission."""
    rng = random.Random(f"{seed}|c10v2")
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
            s = rng.randrange(F_KEYS) if arm is plants else rng.randrange(NULL_KEY_MIN, 1 << 32)
            K = key_stream(s, max(positions(true_lens)) + 1)
            arm.append({"C": encipher(P, true_lens, K), "printed": printed, "P": P, "true_lens": true_lens, "s": s})
    return plants, nulls


# ------------------------------------------------------------------ the repo's decoder, exhaustive over F
_BG = None


def bigram_table():
    """log P(b | a) over rune indices from the English dev stream (add-0.5): the cheap first-pass ranker."""
    global _BG
    if _BG is None:
        import numpy as np
        x = np.asarray(H.english_stream(), dtype=np.int64)
        c = np.full((N, N), 0.5)
        np.add.at(c, (x[:-1], x[1:]), 1)
        _BG = np.log(c / c.sum(1, keepdims=True))
    return _BG


def rank_keys(C_, lens, block=4096):
    """Decode C under every key of the family with jumps from `lens`; return [(bigram score, s)] for all F."""
    import numpy as np
    bg = bigram_table()
    ts = positions(lens)
    c = np.asarray(C_, dtype=np.int16)
    out = []
    for lo in range(0, F_KEYS, block):
        D = (c[None, :] - key_block(lo, lo + block, ts).astype(np.int16)) % N
        sc = bg[D[:, :-1], D[:, 1:]].mean(1)
        out.extend(zip(sc.tolist(), range(lo, lo + block)))
    return out


def exhaustive(C_, lens, topk=TOPK):
    """Best decode over the whole family for a FIXED length sequence (the repo's decoder: rank, re-score, pick)."""
    top = sorted(rank_keys(C_, lens), reverse=True)[:topk]
    best = None
    ts_len = max(positions(lens)) + 1
    for _, s in top:
        d = decode_with(C_, key_stream(s, ts_len), lens)
        q = H.english_score(d)
        if best is None or q > best[0]:
            best = (q, d, s)
    return best


def baseline_true(case):
    return exhaustive(case["C"], case["true_lens"])[1]


def baseline_printed(case):
    return exhaustive(case["C"], [l for s in case["printed"] for l in s])[1]


# ------------------------------------------------------------------ scoring
def recovery(x, P):
    return sum(1 for a, b in zip(x, P) if a == b) / len(P)


def summarise(plants, nulls, out_p, out_n):
    ok, recs = 0, []
    for c, out in zip(plants, out_p):
        r = recovery(out, c["P"])
        recs.append(r)
        ok += r >= MIN_RECOVERY and H.english_score(out) >= ENGLISH
    fp = sum(1 for out in out_n if len(out) >= 4 and H.english_score(out) > ENGLISH) / max(1, len(nulls))
    return {"pass": ok / len(plants), "k": ok, "n": len(plants), "null_fp": fp,
            "mean_recovery": sum(recs) / len(recs)}


def evaluate_local(fn, plants, nulls):
    """fn(case) -> plain_idx, in-process. Only for the repo's own baselines (they may read the case)."""
    return summarise(plants, nulls, [list(fn(c)) for c in plants], [list(fn(c)) for c in nulls])


def row(name, r, secs=None):
    print(f"  {name:46s} {r['k']:>4}/{r['n']:<4} {r['pass']:6.3f} {str(H.wilson(r['k'], r['n'])):>15} "
          f"{r['mean_recovery']:9.3f} {r['null_fp']:8.3f}" + (f" {secs:8.0f}s" if secs is not None else ""))


def header():
    print(f"\n  {'attack':46s} {'plants ok':>9} {'rate':>6} {'Wilson 95%':>15} {'mean rec':>9} {'null FP':>8} {'time':>9}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("submission", nargs="?", help=".py defining attack(C, printed) -> plain_idx")
    ap.add_argument("--n", type=int, default=None, help=f"plants and nulls each (scored run: {SCORED_N}; self-test default 20)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--text", action="append", help="English plaintext source(s) instead of the dev texts")
    ap.add_argument("--budget", type=float, default=60.0, help="wall-clock seconds per unit (scored run: 60)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    n = a.n or (20 if (a.self_test or not a.submission) else SCORED_N)
    seed = H.resolve_seed(a.seed)
    sents = H.english_sentences(a.text) if a.text else H.english_sentences()
    H.banner("C10 unknown key + shuffled word lengths", seed, f"n={n} plants + {n} nulls, F={F_KEYS} keys")
    plants, nulls = make_cases(n, seed, sents)
    exact = sum(decode_with(c["C"], key_stream(c["s"], max(positions(c["true_lens"])) + 1), c["true_lens"]) == c["P"]
                for c in plants)
    print(f"units: mean {sum(len(c['P']) for c in plants) / n:.0f} runes; true-key true-length decode exact "
          f"{exact}/{n}")

    if a.self_test or not a.submission:
        header()
        t0 = time.time()
        r1 = evaluate_local(baseline_true, plants, nulls)
        row("(i) exhaustive, TRUE lengths (ceiling)", r1, time.time() - t0)
        t0 = time.time()
        r2 = evaluate_local(baseline_printed, plants, nulls)
        row("(ii) exhaustive, PRINTED starts (L1 rule)", r2, time.time() - t0)
        ok = exact == n and r1["pass"] >= 0.95 and r1["null_fp"] <= 1 - NULL_OK
        print(f"\ncontrols: exact decode {exact}/{n}, ceiling (i) {r1['pass']:.3f} (need >= 0.95, null FP <= "
              f"{1 - NULL_OK:.2f})")
        print("SELF-TEST " + ("PASS" if ok else "FAIL"))
        sys.exit(0 if ok else 1)

    import _sandbox
    print(f"\nsubmission runs isolated; {a.budget:.0f} s wall-clock per unit")
    header()
    t1 = time.time()
    cases = plants + nulls
    with _sandbox.Sandbox(a.submission, "attack", "list", timeout=a.budget) as sb:
        outs = sb.map([(list(c["C"]), [list(s) for s in c["printed"]]) for c in cases],
                      on_error=lambda i, e: (print(f"  unit failed: {str(e)[:100]}"), [])[1])
    r = summarise(plants, nulls, outs[:n], outs[n:])
    row(a.submission[-46:], r, time.time() - t1)
    done = exact == n and r["pass"] >= FINISH and r["null_fp"] <= 1 - NULL_OK
    if done and n < SCORED_N:
        print(f"Looks good: re-run at the scored size (--n {SCORED_N}) before you submit.")
    met = done and n >= SCORED_N and a.budget <= 60
    print(f"\ninstrument bar: pass rate >= {FINISH} and null FP <= {1 - NULL_OK:.2f} at n >= {SCORED_N}, budget <= 60 s: "
          + ("reached" if met else "not reached"))
    print(RETIRED + ". No crossing is credited.")
    sys.exit(0 if met else 1)


if __name__ == "__main__":
    main()
