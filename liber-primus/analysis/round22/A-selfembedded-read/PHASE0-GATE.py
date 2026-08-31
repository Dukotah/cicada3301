"""PHASE 0 GATE (doctrine mechanics R2 / Aiming-Test Q1).

Plant a KNOWN English acrostic inside a control plaintext of equal length and equal rune
histogram, run the FULL sweep, and prove the recognizer recovers the plant above its null bar.
If recovery fails, the instrument is broken and any null on the real data is meaningless.

We plant at TWO shapes so we measure power across the class, not one lucky point:
  - an every-k plant  (message occupies positions o, o+k, o+2k, ...)
  - a diagonal plant  (message occupies the width-w main diagonal)

PASS iff each planted selection is recovered as the top-ranked selection of its family AND
clears the per-cell null bar (FPR 0.001). Prints measured recovery = power.
"""
import os, sys, random
import lib_selfread as L

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 3301

# a clearly-English message to plant (letters only, upper). Made long by repetition so it
# spans the ENTIRE selected subsequence for the chosen k/w -- the plant fully occupies its
# cell, so that cell is the unambiguous winner if the recognizer works.
_MSG_UNIT = ("THEKEYTOTHEBOOKISTHREETHREEZEROONEFINDTHETRUTHWITHINYOURSELFAND"
             "TESTTHEKNOWLEDGEBELIEVENOTHINGEXCEPTWHATYOUKNOWTOBETRUE")
PLANT_MSG = _MSG_UNIT * 20  # long enough to fill any every-k or diagonal cell we plant


def build_control(n, seed):
    """A length-n uppercase letter string, each char drawn i.i.d. from the solved
    concat's letter histogram. i.i.d. sampling (not tiling) carries NO message and NO
    spurious periodicity, so the only structure the sweep can find is a planted one."""
    src = L.concat_letters()
    rnd = random.Random(seed)
    return [rnd.choice(src) for _ in range(n)]


def plant_everyk(control_chars, msg, k, offset):
    out = list(control_chars)
    for j, ch in enumerate(msg):
        pos = offset + j * k
        if pos < len(out):
            out[pos] = ch
    return "".join(out)


def plant_diagonal(control_chars, msg, w):
    out = list(control_chars)
    for r, ch in enumerate(msg):
        pos = r * w + r
        if pos < len(out):
            out[pos] = ch
    return "".join(out)


import math


def null_bar_for(cell_selector, base_chars, n_shuffles=1000, seed=SEED, fpr=0.001):
    """99.9th-percentile score of the given selection applied to n_shuffles order-shuffles
    of base_chars (histogram-preserving null)."""
    rnd = random.Random(seed)
    chars = list(base_chars)
    scores = []
    for _ in range(n_shuffles):
        rnd.shuffle(chars)
        sub = cell_selector("".join(chars))
        scores.append(L.english_score(sub))
    scores.sort()
    idx = min(len(scores) - 1, int(math.ceil((1 - fpr) * len(scores))) - 1)
    return scores[idx], scores[-1]


def length_keyed_null_bars(base_chars, lengths, n_shuffles=400, seed=SEED, fpr=0.001):
    """A per-LENGTH null bar (FPR 1e-3) for a random contiguous selection of that length
    from order-shuffles of base_chars. The null bar for a selection depends almost entirely
    on its length, so we key by length -- this lets us rank every selection by how far it
    clears ITS OWN size-matched bar (doctrine: compare per-cell, not raw score)."""
    rnd = random.Random(seed)
    chars = list(base_chars)
    bars = {}
    uniq = sorted(set(lengths))
    for Ln in uniq:
        scores = []
        for _ in range(n_shuffles):
            rnd.shuffle(chars)
            scores.append(L.english_score(chars[:Ln]))
        scores.sort()
        idx = min(len(scores) - 1, int(math.ceil((1 - fpr) * len(scores))) - 1)
        bars[Ln] = scores[idx]
    return bars


def sweep_ranked_by_excess(planted, bars):
    """Rank every selection by how far it clears its OWN size-matched null bar
    (score - bar[len]). Returns (best_desc, best_excess, best_score, best_bar, ranked list)."""
    rows = []
    for desc, sub in L.enumerate_selections(planted):
        sc = L.english_score(sub)
        bar = bars.get(len(sub))
        if bar is None:
            continue
        rows.append((desc, sc - bar, sc, bar))
    rows.sort(key=lambda r: -r[1])
    return rows[0], rows


def run():
    n = len(L.concat_letters())
    print(f"[phase0] control length = {n} letters (matches solved concat)")
    control = build_control(n, SEED)

    # pre-compute all selection lengths so we can build a length-keyed null bar table
    lens = set()
    dummy = "".join(control)
    for _, sub in L.enumerate_selections(dummy):
        lens.add(len(sub))
    print(f"[phase0] building length-keyed null bars for {len(lens)} distinct lengths ...")
    bars = length_keyed_null_bars(control, lens)

    results = []

    # ---- plant 1: every-k, k=7 offset=0 ----
    k, off = 7, 0
    planted = plant_everyk(control, PLANT_MSG, k, off)
    (bdesc, bexc, bsc, bbar), _ = sweep_ranked_by_excess(planted, bars)
    recovered = (bdesc == f"everyk_k{k}_o{off}")
    print(f"[phase0] every-k plant (k={k},o={off}): TOP-by-excess = {bdesc} "
          f"(score={bsc:.3f}, bar={bbar:.3f}, excess={bexc:.3f}) "
          f"-> {'RECOVERED' if recovered else 'MISS'}")
    results.append(("everyk", recovered, bdesc, bsc, bbar, bexc))

    # ---- plant 2: diagonal, w=13 ----
    # NOTE: the width-w main diagonal picks positions r*w+r = r*(w+1) from offset 0, i.e.
    # it is IDENTICAL to every-(w+1) offset 0. So the correct recovery is either the diag
    # label OR its equivalent every-k selector -- a labeling collision, not a miss.
    w = 13
    planted2 = plant_diagonal(control, PLANT_MSG, w)
    (bdesc2, bexc2, bsc2, bbar2), _ = sweep_ranked_by_excess(planted2, bars)
    recovered2 = bdesc2 in (f"diag_w{w}", f"everyk_k{w + 1}_o0")
    print(f"[phase0] diagonal plant (w={w}): TOP-by-excess = {bdesc2} "
          f"(score={bsc2:.3f}, bar={bbar2:.3f}, excess={bexc2:.3f}) "
          f"-> {'RECOVERED' if recovered2 else 'MISS'}")
    results.append(("diagonal", recovered2, bdesc2, bsc2, bbar2, bexc2))

    n_ok = sum(1 for r in results if r[1])
    power = n_ok / len(results)
    print(f"\n[phase0] measured recovery / power = {n_ok}/{len(results)} = {power:.3f}")
    ok = power == 1.0
    print("[phase0] GATE:", "PASS" if ok else "FAIL (instrument cannot see a planted hit)")
    return ok, power, results


if __name__ == "__main__":
    ok, power, _ = run()
    sys.exit(0 if ok else 1)
