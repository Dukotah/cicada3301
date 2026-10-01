"""Round 19 — LANE 1 — AN-END ground-truth row.

The PREREG uses AN-END (page 56 / 73.jpg) as a second, NON-synthetic-keyskip positive
control: its real construction is a totient keystream (phi(prime): p-1 mod 29, shift-down)
plus F-interrupter runes that are removed on decode and do NOT advance the key. That is a
genuinely different transition model from keyskip. The question this row answers:

  Can the project's instrument (the keyskip beam + any adjudicator) even SEE a page the
  project has already solved -- i.e. recover the plaintext of an AN-END-class construction?

We build the construction forward (totient keystream + spliced F-interrupters) over a known
English plaintext, then decode three ways:
  1. rigid decode with the totient key but WITHOUT removing interrupters (what a keyskip-only
     pipeline does) -- the desync test;
  2. the keyskip beam with the totient key (the repo's live LP2 decoder) -- the real test;
  3. the interrupter-aware solve.decode with the CORRECT interrupter set (the oracle upper
     bound) -- proves the plant is sound and recoverable in principle.

Appends rows to power_table.json / power_summary.json under register 'ANEND_EN'.

    PYTHONUTF8=1 python3 anend_row.py
"""
import os, sys, json, statistics, sympy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in (os.path.join(LP, "src"), os.path.join(LP, "benchmark"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round16", "scorer")):
    if p not in sys.path:
        sys.path.insert(0, p)

from lp import gematria as gp, score as _score, solve as _solve      # noqa: E402
import skipdecode as sk                                              # noqa: E402
from scorer import matched_scorer                                    # noqa: E402

N = gp.N
Q = _score.default()
ENG_MATCHED = matched_scorer()
F_IDX = gp.RUNE_TO_IDX[gp.INTERRUPTER]        # interrupter rune index (0)

PLAIN = ("WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO A VALUE IT IS THE DUTY OF "
         "EVERY PILGRIM TO SEEK OUT THIS PAGE FOR ALL IS SACRED AND THE PRIMES ARE SACRED "
         "AND THE TOTIENT FUNCTION IS SACRED KNOW THIS AND FIND YOUR TRUTH WITHIN THE DEEP")


def totient_keystream(n, start_prime=2):
    """phi(prime) for successive primes p -> (p-1) mod 29, used as a SHIFT-DOWN key.
    This is AN-END's stated external input (the prime sequence); the keystream is
    derived from it, NOT handed over."""
    ks, p = [], start_prime
    while len(ks) < n:
        ks.append((p - 1) % N)
        p = sympy.nextprime(p)
    return ks


def build_anend(plain_idx, n_interrupters=6, seed=3301):
    """Encipher with the totient key (shift-DOWN: c = (p - k) mod N, i.e. sign=+1 in the
    p=(c+sign*k) convention would be sign=-1 -> here we use shift-down so decode is
    p=(c+k)), then splice F-interrupters that do NOT advance the key."""
    import random
    K = totient_keystream(len(plain_idx) + 16)
    # shift-DOWN encipher: c = (p - k) mod N  ->  decode p = (c + k) mod N (sign=+1)
    C = [(plain_idx[i] - K[i]) % N for i in range(len(plain_idx))]
    runes = [C[i] for i in range(len(C))]
    rng = random.Random(seed)
    pos = sorted(rng.sample(range(4, len(runes) - 4), n_interrupters))
    for j, pp in enumerate(pos):
        runes.insert(pp + j, F_IDX)           # splice interrupter; key not advanced
    return runes, K, [pp + j for j, pp in enumerate(pos)]


def main():
    plain_idx = sk.eng_to_idx(PLAIN)
    L = len(plain_idx)
    rows, summ = [], []

    for seed in range(7):
        C_with_int, K, int_pos = build_anend(plain_idx, n_interrupters=6, seed=3301 + seed)
        # ---- test 1: rigid decode, totient key, interrupters NOT removed (desync)
        # decode relation for shift-down: p = (c + k) mod N  => sign=+1
        rd = sk.rigid_decode(C_with_int, K + [0] * (len(C_with_int) + 8), sign=+1, o=0)
        rec_rigid = sum(1 for a, b in zip(rd["plain_idx"], plain_idx)
                        if a == b) / len(plain_idx)

        # ---- test 2: keyskip beam, totient key (the live LP2 decoder)
        bd = sk.beam_decode(C_with_int, K + [0] * (len(C_with_int) * 4 + 8),
                            sign=+1, o=0, beam_w=400, max_skip=3)
        rec_beam = sum(1 for a, b in zip(bd["plain_idx"], plain_idx)
                       if a == b) / len(plain_idx)

        # ---- test 3: interrupter-aware oracle (correct interrupter set) -> upper bound
        # occurrence-index set of the spliced F runes among all F occurrences
        f_occ = [i for i, c in enumerate(C_with_int) if c == F_IDX]
        spliced_occ = {f_occ.index(p) for p in int_pos if p in f_occ}
        runes_str = gp.indices_to_runes(C_with_int)
        try:
            pt, _ = _solve.decode(runes_str, K + [0] * (len(C_with_int) + 8),
                                  sign=+1, atbash=False, interrupter_idx=spliced_occ)
            oracle_translit = pt
            # measure on the transliteration STRING, not a re-parse (re-encoding the
            # decoded translit through eng_to_idx desyncs on any natural F/doublet rune;
            # the decoded string itself is the ground truth to compare).
            truth_tr = sk.idx_to_trans(plain_idx)
            m = min(len(pt), len(truth_tr))
            oracle_rec = (sum(1 for a, b in zip(pt[:m], truth_tr[:m]) if a == b)
                          / len(truth_tr)) if truth_tr else None
        except Exception as e:
            oracle_translit, oracle_rec = f"<solve err {e}>", None

        rows.append({
            "register": "ANEND_EN", "construction": "totient_interrupters",
            "L": L, "key_family": "totient(phi_prime)", "seed": seed,
            "recovery_rigid_no_interrupt": round(rec_rigid, 4),
            "recovery_keyskip_beam": round(rec_beam, 4),
            "recovery_oracle_interrupt_aware": (round(oracle_rec, 4)
                                                if oracle_rec is not None else None),
            "beam_en_quadgram_score": round(bd["score"], 4),
            "beam_en_matched_score": round(ENG_MATCHED.score_norm(bd["translit"]), 4),
            "n_interrupters": 6,
        })

    out = {
        "register": "ANEND_EN", "construction": "totient_interrupters",
        "key_family": "totient(phi_prime: p-1 mod 29, shift-down)",
        "n_seeds": len(rows),
        "median_recovery_rigid_no_interrupt":
            statistics.median(r["recovery_rigid_no_interrupt"] for r in rows),
        "median_recovery_keyskip_beam":
            statistics.median(r["recovery_keyskip_beam"] for r in rows),
        "median_recovery_oracle_interrupt_aware":
            statistics.median(r["recovery_oracle_interrupt_aware"] for r in rows
                              if r["recovery_oracle_interrupt_aware"] is not None) or None,
        "median_beam_en_quadgram":
            statistics.median(r["beam_en_quadgram_score"] for r in rows),
        "finding": ("whether the keyskip beam / its scorer can recover an AN-END-class "
                    "(totient keystream + F-interrupter) construction it was not built for"),
    }
    json.dump({"summary": out, "rows": rows},
              open(os.path.join(HERE, "anend_row.json"), "w"), indent=1)
    print("AN-END-class ground-truth row:")
    print(f"  rigid (interrupters NOT removed) recovery : {out['median_recovery_rigid_no_interrupt']:.1%}")
    print(f"  keyskip BEAM (live LP2 decoder)  recovery : {out['median_recovery_keyskip_beam']:.1%}")
    print(f"  oracle (correct interrupter set) recovery : "
          f"{out['median_recovery_oracle_interrupt_aware']}")
    print(f"  beam English-quadgram median score        : {out['median_beam_en_quadgram']:.3f}")
    print("wrote anend_row.json")


if __name__ == "__main__":
    main()
