"""i11 AUTHOR-EMPATHY (final pass): SMIRNOV-REWRITE COLLISION-DECODE.

HYPOTHESIS (operationalizes iter-10 best lead + the observed anti-repeat signature):
The 0-54 ciphertext's *below-random* adjacent-equal rate (measured 0.0066 vs 1/29=0.0345,
and even below English PARABLE's 0.0106) is the fingerprint of a SMIRNOV REWRITE: the
encoder, when its base keystream would emit a symbol equal to the PREVIOUS OUTPUT, BUMPS
it to the next-allowed symbol under some alphabet ordering. This is a deterministic,
(near) parameter-free construction -> combinatorialist-encoder profile.

INVERSE (un-bump): given output o at position i and previous output p (both in the SAME
ordered alphabet), the collided base b is recovered by:
      b = o        if  rank(o) < rank(p)
      b = prev(o)  if  rank(o) > rank(p)     (o was bumped past p, so step back one)
  ( rank(o)==rank(p) never happens in a Smirnov word )
This is the classic Smirnov<->free-word bijection: it maps a length-N anti-repeat stream
back onto a length-(N-1)-alphabet base stream. If the underlying base IS the true plaintext
residual (English-in-runes), un-bumping under the CORRECT ordering restores it; the
VALIDATED blind oracle (bigram plausibility P, learned only from PARABLE) then lights up.

We sweep a few hundred alphabet ORDERINGS (identity, gematria/prime order, atbash, and all
29 cyclic SHIFTS of each, plus the standard futhorc order) and score the un-bumped stream
by P (primary; model-free) and D (doubling ratio, secondary/noisy).

VALIDATION GATE: build a synthetic Smirnov-rewritten English-in-runes sample, confirm that
un-bump under the GENERATING ordering restores P into the English band while a WRONG ordering
does not. Abort the real sweep unless the gate passes.
"""
import os, sys, random, json, itertools
HERE = os.path.dirname(__file__)
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROOT = os.path.dirname(LP)
sys.path.insert(0, os.path.join(LP, "src"))
from lp import gematria as gp

N = gp.N
KRIS = os.path.join(LP, "data", "krisyotam_runes.txt")

# ---------------------------------------------------------------- data
segs = [s for s in open(KRIS, encoding="utf-8").read().split("%") if gp.runes_to_indices(s)]
PAGES = [gp.runes_to_indices(s) for s in segs]
UNSOLVED = [i for p in PAGES[:55] for i in p]
PARABLE = PAGES[56]

# ---- LEGAL bigram set learned ONLY from PARABLE (same as validated i7 oracle)
LEGAL = {(a, b) for a, b in zip(PARABLE, PARABLE[1:])}

def P_score(seq):
    if len(seq) < 2: return float("nan")
    return sum(1 for a, b in zip(seq, seq[1:]) if (a, b) in LEGAL) / (len(seq) - 1)

def D_ratio(seq):
    if len(seq) < 2: return float("nan")
    eq = sum(1 for a, b in zip(seq, seq[1:]) if a == b)
    return (eq / (len(seq) - 1)) / (1.0 / N)

# ---------------------------------------------------------------- Smirnov codec
# An ORDERING is a permutation of 0..N-1 defining "rank". rank[symbol] = position.
def make_ranks(order):
    rank = [0] * N
    for pos, sym in enumerate(order):
        rank[sym] = pos
    return rank

def smirnov_encode(base, order):
    """Encode a base stream (values 0..N-2 = an (N-1)-symbol free word) into an
    anti-repeat output stream over N symbols, under `order`. This is the forward
    rewrite: it never emits the previous output.
    Position i's output = the (base[i])-th symbol among the N-1 symbols != prev,
    taken in `order`. First symbol: base in 0..N-1 mapped directly (order[base])."""
    rank = make_ranks(order)
    out = []
    prev = None
    for i, b in enumerate(base):
        if prev is None:
            out.append(order[b % N])
        else:
            # the N-1 allowed symbols are order[] minus prev, keep order
            pr = rank[prev]
            # choose the b-th allowed rank; ranks 0..N-1 excluding pr
            r = b % (N - 1)
            chosen = r if r < pr else r + 1  # skip the forbidden rank pr
            out.append(order[chosen])
        prev = out[-1]
    return out

def smirnov_unbump(stream, order):
    """Inverse: recover base stream (0..N-2 after first) from anti-repeat output."""
    rank = make_ranks(order)
    base = []
    prev = None
    for o in stream:
        r = rank[o]
        if prev is None:
            base.append(r)
        else:
            pr = rank[prev]
            # r != pr in a true Smirnov word. base = r if r<pr else r-1
            b = r if r < pr else r - 1
            base.append(b)
        prev = o
    return base

# ---------------------------------------------------------------- orderings
def cyclic_shifts(order):
    return [order[k:] + order[:k] for k in range(N)]

IDENTITY = list(range(N))
# gematria/prime order: sort symbols by their prime value
PRIME_ORDER = sorted(range(N), key=lambda i: gp.PRIMES[i] if i < len(gp.PRIMES) else 999)
ATBASH = list(range(N - 1, -1, -1))
# futhorc standard order is the identity of the rune table already; add reversed prime
REV_PRIME = list(reversed(PRIME_ORDER))

BASE_ORDERINGS = {
    "identity": IDENTITY,
    "prime_order": PRIME_ORDER,
    "atbash": ATBASH,
    "rev_prime": REV_PRIME,
}

def all_orderings():
    out = {}
    for name, o in BASE_ORDERINGS.items():
        for k, sh in enumerate(cyclic_shifts(o)):
            out[f"{name}+shift{k}"] = sh
    return out

# ---------------------------------------------------------------- validation gate
def synthetic_english_base(n, seed=7):
    """Build a base free-word over N-1 symbols whose bigrams resemble English:
    reuse PARABLE plaintext (real English-in-runes) as the base, folded to 0..N-2."""
    rng = random.Random(seed)
    # take PARABLE, map each rune index into 0..N-2 by clamping (drop symbol 28 rarely)
    base = [min(x, N - 2) for x in PARABLE]
    return base

def gate():
    order = PRIME_ORDER  # the "true" generating ordering for the synthetic
    base = synthetic_english_base(0)
    enc = smirnov_encode(base, order)
    # confirm enc is a real Smirnov word (no adjacent repeats)
    reps = sum(1 for a, b in zip(enc, enc[1:]) if a == b)
    dec_right = smirnov_unbump(enc, order)
    # a WRONG ordering
    wrong = ATBASH
    dec_wrong = smirnov_unbump(enc, wrong)

    p_base = P_score(base)
    p_enc = P_score(enc)
    p_right = P_score(dec_right)
    p_wrong = P_score(dec_wrong)
    d_enc = D_ratio(enc)
    d_right = D_ratio(dec_right)

    print("=== SMIRNOV VALIDATION GATE (synthetic English base) ===")
    print(f"  base (English-in-runes) P={p_base:.3f}")
    print(f"  smirnov-encoded         P={p_enc:.3f}  D={d_enc:.3f}  adj-reps={reps}")
    print(f"  un-bump RIGHT ordering  P={p_right:.3f}  D={d_right:.3f}  exact-restore={dec_right==base}")
    print(f"  un-bump WRONG ordering  P={p_wrong:.3f}")
    # gate: right un-bump restores P to base band AND clearly beats the encoded stream
    # AND clearly beats the wrong ordering
    passed = (p_right > 0.8 * p_base) and (p_right > p_enc + 0.2) and (p_right > p_wrong + 0.2)
    print(f"  GATE {'PASS' if passed else 'FAIL'}")
    return passed, {
        "p_base": p_base, "p_enc": p_enc, "p_right": p_right,
        "p_wrong": p_wrong, "exact_restore": dec_right == base,
        "enc_adj_reps": reps,
    }

# ---------------------------------------------------------------- real sweep
def sweep():
    target = UNSOLVED
    # controls: (a) raw ct P, (b) 200 random anti-repeat streams un-bumped,
    #           (c) P of un-bumping a genuinely-random Smirnov stream
    p_raw = P_score(target)
    d_raw = D_ratio(target)

    rng = random.Random(3301)
    # random-control: random Smirnov words of same length, un-bumped under identity
    ctrl_ps = []
    for s in range(200):
        r = random.Random(s)
        rand_smir = []
        prev = None
        for _ in range(len(target)):
            while True:
                x = r.randrange(N)
                if x != prev:
                    break
            rand_smir.append(x); prev = x
        ctrl_ps.append(P_score(smirnov_unbump(rand_smir, IDENTITY)))
    ctrl_ps.sort()
    ctrl_band = {"mean": sum(ctrl_ps)/len(ctrl_ps), "p95": ctrl_ps[189],
                 "max": ctrl_ps[-1]}

    rows = []
    for name, order in all_orderings().items():
        dec = smirnov_unbump(target, order)
        rows.append({"ordering": name, "P": round(P_score(dec), 4),
                     "D": round(D_ratio(dec), 4)})
    rows.sort(key=lambda r: -r["P"])
    return {
        "raw_ct_P": round(p_raw, 4), "raw_ct_D": round(d_raw, 4),
        "control_band": {k: round(v, 4) for k, v in ctrl_band.items()},
        "english_ref_PARABLE_P": 1.0,
        "n_orderings": len(rows),
        "best": rows[:8],
        "worst": rows[-3:],
    }

if __name__ == "__main__":
    ok, gdata = gate()
    result = {"gate_passed": ok, "gate": {k: (round(v,4) if isinstance(v,float) else v)
                                          for k, v in gdata.items()}}
    if ok:
        result["sweep"] = sweep()
    else:
        result["sweep"] = "SKIPPED (gate failed; oracle cannot detect the rewrite)"
    print("\n" + json.dumps(result, indent=2))
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(result, f, indent=2)
