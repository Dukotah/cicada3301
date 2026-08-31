#!/usr/bin/env python3
"""C2 POSITIVE CONTROL (mandatory, pre-registered) -- the skip_by_two decoder.

The transition relation the beam CANNOT express (round18/L7-B) is
`enc_skip_by_two`: a 2013 rejection loop that burns TWO key draws per rejection
(`j += 2`), so one key position between the previous accepted rune and the next
is silently consumed -- it is constrained to nothing. The repo beam
(driftbeam mode='keyskip1' == campaign18_skip.beam_decode) admits a skip only if
every skipped key position reproduces the previous cipher rune; the silently-burned
position violates that with prob (N-1)/N, so the true path is OUTSIDE the beam's
transition relation.

driftbeam mode='keyskip2' (preset 'pair') IS that relation: skipped positions come
in pairs; the first of each pair must reproduce c_prev, the second is unconstrained.
This is the decoder C2 registers -- it already exists in round19/I1 and is gated
G-EQ against the repo beam. This control PROVES it recovers a skip_by_two plant at
>=0.90 where the beam gets ~0.26 (the L7-B number). If it does not, C2 STOPS.

Protocol matches round18/L7-redteam/b1_power_envelope.py exactly (L=240, sha256_ctr
key, English held-out plaintext from self_reliance.txt, supp in {0.4,0.83,1.0},
seeds 3301+s). We additionally report supp=0.83 at the L7-B multi-seed setting so
the number is directly comparable to RESULTS.md B (-6.90 / 25.8%).

Run: python3 control.py            # writes control.json
"""
import os, sys, json, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "benchmark",
          os.path.join("analysis", "campaign18_skip"),
          os.path.join("analysis", "round19", "I1"),
          os.path.join("analysis", "round18", "L7-redteam")):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp                      # noqa
import skipdecode as sk                            # noqa  (eng_to_idx, encipher; the repo beam)
import driftbeam as DB                             # noqa  (keyskip1/keyskip2/permissive)
import plant as PL                                 # noqa  (make_key)

N = gp.N
L = 240
NSEED = 7
RECOVERY_BAR = 0.90


def english_stream():
    p = os.path.join(LP, "data", "keys", "self_reliance.txt")
    with open(p, encoding="utf-8", errors="ignore") as f:
        return sk.eng_to_idx(f.read())[5000:]


ENG = english_stream()


def take_plain(Ln, seed):
    r = random.Random(9000 + seed)
    s = r.randrange(0, len(ENG) - Ln - 1)
    return ENG[s:s + Ln]


def key_sha(n, seed=b"CICADA3301"):
    return PL.make_key("sha256_ctr", length=n, seed=seed)


def enc_skip_by_two(P, K, supp=0.83, seed=3301):
    """Rejection CONSUMES TWO draws (j += 2). Identical to
    round18/L7-redteam/b1_power_envelope.enc_skip_by_two and I1/constructions."""
    rng = random.Random(seed)
    C, j, c_prev, nsk = [], 0, None, 0
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                nsk += 1
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C, nsk


def rec(plain_idx, truth):
    return sum(1 for a, b in zip(plain_idx, truth) if a == b) / max(1, len(truth))


def run(supp):
    rows = []
    for s in range(NSEED):
        P = take_plain(L, s)
        need = L * 10 + 1024
        K = key_sha(need)
        C, nsk = enc_skip_by_two(P, K, supp=supp, seed=3301 + s)
        dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / max(1, len(C) - 1)
        # BEAM (repo relation, keyskip1) at ms=3 AND ms=8 -- L7-B showed both identical
        b3 = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, mode="keyskip1", max_skip=3)
        b8 = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, mode="keyskip1", max_skip=8)
        # PAIR (skip_by_two-exact, keyskip2)
        pr = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, mode="keyskip2", max_skip=8)
        rows.append({
            "seed": 3301 + s, "n_rejections": nsk, "ct_doublet_pct": 100 * dbl,
            "beam_ms3_score": b3["score"], "beam_ms3_rec": rec(b3["plain_idx"], P),
            "beam_ms8_score": b8["score"], "beam_ms8_rec": rec(b8["plain_idx"], P),
            "pair_score": pr["score"], "pair_rec": rec(pr["plain_idx"], P),
        })
    return rows


def med(rows, k):
    return statistics.median(r[k] for r in rows)


def main():
    out = {"lane": "round24/C2-skip-by-two/control",
           "plant": "enc_skip_by_two (j+=2 per rejection); English self_reliance L=240; sha256_ctr key",
           "recovery_bar": RECOVERY_BAR, "n_seeds": NSEED, "supp_levels": {}}
    print("supp | beam(keyskip1) ms3      ms8         | PAIR(keyskip2)   | ct-dbl")
    print("-" * 78)
    all_pair_rec = []
    all_beam_rec = []
    for supp in (0.4, 0.83, 1.0):
        rows = run(supp)
        cell = {
            "beam_ms3_score": med(rows, "beam_ms3_score"), "beam_ms3_rec": med(rows, "beam_ms3_rec"),
            "beam_ms8_score": med(rows, "beam_ms8_score"), "beam_ms8_rec": med(rows, "beam_ms8_rec"),
            "pair_score": med(rows, "pair_score"), "pair_rec": med(rows, "pair_rec"),
            "ct_doublet_pct": med(rows, "ct_doublet_pct"),
            "min_pair_rec": min(r["pair_rec"] for r in rows),
            "rows": rows,
        }
        out["supp_levels"][str(supp)] = cell
        all_pair_rec.append(cell["pair_rec"])
        all_beam_rec.append(cell["beam_ms3_rec"])
        print(f"{supp:4} | {cell['beam_ms3_score']:6.3f}/{cell['beam_ms3_rec']:5.1%}  "
              f"{cell['beam_ms8_score']:6.3f}/{cell['beam_ms8_rec']:5.1%} | "
              f"{cell['pair_score']:6.3f}/{cell['pair_rec']:5.1%} | "
              f"{cell['ct_doublet_pct']:4.2f}%")

    # verdict: pair recovers >=0.90 at every supp AND beats the beam decisively
    pair_min = min(all_pair_rec)
    beam_max = max(all_beam_rec)
    validated = pair_min >= RECOVERY_BAR and beam_max < 0.90
    out["verdict"] = {
        "pair_median_recovery_min_over_supp": pair_min,
        "beam_median_recovery_max_over_supp": beam_max,
        "control_validated": bool(validated),
        "rule": "validated iff pair median recovery >=0.90 at every supp AND beam <0.90 everywhere",
    }
    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print("-" * 78)
    print(f"PAIR min median recovery over supp : {pair_min:.1%}  (bar {RECOVERY_BAR:.0%})")
    print(f"BEAM max median recovery over supp : {beam_max:.1%}")
    print("CONTROL:", "VALIDATED -- pair decoder models skip_by_two; beam cannot"
          if validated else "FAILED -- STOP, decoder is wrong")
    return validated


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
