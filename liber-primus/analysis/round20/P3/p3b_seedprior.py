"""P3b -- integrate L8's 433 ranked seed candidates as an ORDERING over each generator's
seed axis, so the Phase-S sweeps are prior-weighted, not flat (doctrine R4).

Round 8 enumerated every unix second 2011-2015 uniformly for 10 generators -- the exact
flat-prior error the doctrine names. L8 (round18/L8-provenance) built the correction: 433 unix
seconds a human demonstrably had in front of them, ranked by provenance x authorship-proximity
x derivation-distance, top = 1325734783 (the second the 3301 primary key + subkey + UID
self-sig were all created; 3 independent verified sources).

This module:
  1. LIFTS those 433 into a compact, machine-readable prior file `seedprior20.json` (rank, seed,
     tier, score, n_sources) -- the ordering, stripped of the bulky provenance evidence.
  2. Provides `seed_order(generator=...)` -> the seeds to try FIRST, in order, for any Phase-S
     generator, plus a `weight(rank)` a sweep can use to prioritise compute.
  3. Round-trips against the source JSON (0 mismatches) as its positive control.

The candidates are UNIX SECONDS. How each generator consumes them:
  - S-G3 Python 2.7 random.seed(int)     : the int seed directly (also string-seed => init_by_array)
  - S-BASH bash $RANDOM / glibc srandom() : srand(seed) then the stream; seed==offset (one orbit)
  - S-PERL Perl 5.14 srand(seed)          : the int seed directly
  - S-TEX  pgfmathsetseed{seed}           : the int seed directly (Lehmer LCG, mult 69621)
So the ORDERING is generator-independent; only the per-seed decode call differs. A seed absent
from this list is NOT excluded (L8's own caveat); the list says what to try FIRST, not what is
possible.

Run: python3 p3b_seedprior.py       # -> seedprior20.json + round-trip check
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SRC = os.path.join(LP, "analysis", "round18", "L8-provenance",
                   "TIMESTAMP-SEED-CANDIDATES.json")

# tier -> a coarse prior weight, monotone in L8's own tier ordering (A>B>C>D). These are a
# PRIOR ORDERING, not probabilities; a sweep uses them to allocate compute, not to claim.
TIER_WEIGHT = {"A": 8.0, "B": 4.0, "C": 2.0, "D": 1.0}


def load_source():
    return json.load(open(SRC, encoding="utf-8"))


def build():
    d = load_source()
    cands = d["candidates"]
    # verify the source is already rank-sorted and rank 1 is the key-creation second
    assert cands[0]["seed"] == 1325734783, cands[0]["seed"]
    assert cands[0]["rank"] == 1
    ranks = [c["rank"] for c in cands]
    assert ranks == sorted(ranks), "source not rank-ordered"
    order = []
    for c in cands:
        rs = c["rank_score"]
        order.append({
            "rank": c["rank"], "seed": c["seed"], "tier": c["tier"],
            "tier_weight": TIER_WEIGHT[c["tier"]],
            "n_independent_sources": c.get("n_independent_sources", 1),
            "score_provenance": rs["provenance"],
            "score_authorship_proximity": rs["authorship_proximity"],
            "score_derivation_distance": rs["derivation_distance"],
            # a single scalar priority a sweep can sort/weight on: tier weight boosted by
            # corroboration (more independent sources = higher). Monotone in rank within a tier.
            "priority": TIER_WEIGHT[c["tier"]] * (1.0 + 0.25 * (c.get("n_independent_sources", 1) - 1)),
        })
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "lane": "round20/P3 (P3b)",
        "source": os.path.relpath(SRC, LP),
        "what_this_is": ("A RANKED PRIOR ORDERING over RNG seeds for Round-20 Phase-S sweeps. "
                         "Not a keyspace, not a claim, not exclusive (a seed absent here is not "
                         "excluded). These are the unix seconds a human demonstrably had, so they "
                         "are the seeds to try FIRST if a seed sweep is run."),
        "top_seed": 1325734783,
        "top_seed_meaning": ("2012-01-05T03:39:43Z -- the second the 3301 PGP primary key, "
                             "encryption subkey, and UID self-signature were all created "
                             "(3 independent verified sources on the author's own machine)."),
        "candidate_count": len(order),
        "tier_counts": d["tier_counts"],
        "tier_weight": TIER_WEIGHT,
        "how_generators_consume_a_seed": {
            "S-G3_python27": "random.seed(int_seed) OR string-seed -> init_by_array([w])",
            "S-BASH": "srand(seed); glibc random() stream; seed==offset (one orbit)",
            "S-PERL": "srand(seed); Perl 5.14 rand",
            "S-TEX": "\\pgfmathsetseed{seed}; Lehmer LCG mult 69621, period 2^31-1",
        },
        "caveat": ("A PGP sig creation time is a settable RFC-4880 subpacket; but a spoofed "
                   "timestamp is still a number the author chose and typed -- the very property "
                   "that makes it a plausible srand() argument (L8 declared this before running)."),
        "order": order,
    }
    json.dump(out, open(os.path.join(HERE, "seedprior20.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    print(f"wrote seedprior20.json  ({len(order)} candidates)")
    return out


# ------------------------------------------------------------------ callable API for S-lanes
_PRIOR = None


def _prior():
    global _PRIOR
    if _PRIOR is None:
        p = os.path.join(HERE, "seedprior20.json")
        _PRIOR = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else build()
    return _PRIOR


def seed_order(top=None):
    """The seeds to try FIRST, in prior order (rank 1 = 1325734783). `top` truncates the list."""
    seeds = [e["seed"] for e in _prior()["order"]]
    return seeds[:top] if top else seeds


def weighted_order(top=None):
    """(seed, priority, tier) tuples in prior order -- for compute allocation."""
    o = [(e["seed"], e["priority"], e["tier"]) for e in _prior()["order"]]
    return o[:top] if top else o


def roundtrip_check():
    """Positive control: the emitted ordering reproduces the source rank order and tiers."""
    src = load_source()["candidates"]
    pri = _prior()["order"]
    mism = 0
    for s, p in zip(src, pri):
        if s["seed"] != p["seed"] or s["tier"] != p["tier"] or s["rank"] != p["rank"]:
            mism += 1
    ok = (len(src) == len(pri) == 433 and pri[0]["seed"] == 1325734783 and mism == 0)
    tiers = [e["tier"] for e in pri]
    # tiers are non-worsening down the list (A block, then B, then C, then D)
    tier_rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    monotone = all(tier_rank[tiers[i]] <= tier_rank[tiers[i + 1]] for i in range(len(tiers) - 1))
    return {"n_source": len(src), "n_prior": len(pri), "mismatches": mism,
            "rank1_seed": pri[0]["seed"], "tier_monotone": monotone, "passed": bool(ok and monotone)}


if __name__ == "__main__":
    build()
    r = roundtrip_check()
    print("round-trip check:", json.dumps(r))
    print("first 5 seeds (prior order):", seed_order(5))
    print("PASS" if r["passed"] else "FAIL")
