#!/usr/bin/env python3
"""Round 26 Lane C POSITIVE CONTROL (mandatory, pre-registered).

Prove recovery >= 0.90 for a SEMANTIC-SEED plant through EVERY generator in the zoo, under the
control-validated skip_by_two (pair/keyskip2) decoder + hitfn20 three-clause gate, BEFORE any
sweep null is allowed to count (doctrine: an unvalidated instrument's null is not a negative).

Protocol mirrors round24/C2-skip-by-two/control.py: L=240, English held-out plaintext from
self_reliance.txt, enc_skip_by_two (j += 2 per rejection, supp=0.83), RECOVERY_BAR=0.90.
The keystream is produced by feeding a SEMANTIC seed through each generator family.

Run: python3 control.py            # writes control.json
"""
import os, sys, json, random

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis/round19/G3", "analysis/round19/G2", "analysis/round19/I1",
          "analysis/round20/P3", "analysis/round20/HITFN", "analysis/round11",
          "analysis/campaign18_skip", "benchmark", "src"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

import gen_py27 as GPY                 # noqa
import gen_perl as GPERL               # noqa
import hitfn20 as H                    # noqa
import skipdecode as sk                # noqa
from lp import gematria as gp, ciphers as CI   # noqa

N = gp.N
L = 240
SUPP = 0.83
RECOVERY_BAR = 0.90
NEED = L * 10 + 1024


def enc_skip_by_two(P, K, supp=SUPP, seed=3301):
    rng = random.Random(seed)
    C, j, c_prev = [], 0, None
    for p in P:
        while True:
            c = (p + K[j]) % N
            if c_prev is not None and c == c_prev and rng.random() < supp:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c
    return C


def english_plain(Ln, off=5000):
    eng = sk.eng_to_idx(open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
                             encoding="utf-8", errors="ignore").read())[off:]
    return eng[:Ln]


# ---- generator zoo: name -> callable(seed)->keystream of length NEED ----------
def gen_py27_r29(seed):     return GPY.keystream(seed, mode="random29", n=NEED)
def gen_py27_grbmod(seed):  return GPY.keystream(seed, mode="grb5_mod", n=NEED)
def gen_py27_grbrej(seed):  return GPY.keystream(seed, mode="grb5_rej", n=NEED)
def gen_perl_r29(seed):     return GPERL.g_r29(int(seed) & 0xFFFFFFFF, NEED)
def gen_prime(seed):        return CI.prime_stream(NEED, start=int(seed) % 5000)
def gen_totient(seed):      return CI.totient_stream(NEED, start=2 + int(seed) % 5000)
def gen_prime_totient(seed):return CI.prime_totient_stream(NEED, start=int(seed) % 5000)

ZOO = {
    "py27_random29": gen_py27_r29,
    "py27_grb5_mod": gen_py27_grbmod,
    "py27_grb5_rej": gen_py27_grbrej,
    "perl_glibc_r29": gen_perl_r29,
    "ladder_prime": gen_prime,
    "ladder_totient": gen_totient,
    "ladder_prime_totient": gen_prime_totient,
}

# seeds usable per generator: ladders/perl need INT; py27 accepts int or str.
STR_OK = {"py27_random29", "py27_grb5_mod", "py27_grb5_rej"}


def main():
    P = english_plain(L)
    results = {}
    all_pass = True
    # int-seed control on every generator + a str-seed control on py27
    for gname, gfn in ZOO.items():
        seed = 3301
        K = gfn(seed)
        C = enc_skip_by_two(P, K)
        v = H.evaluate(H.HitDecode(C=C, K=K, o=0, preset="pair",
                                   n_round_adjudicated=100000, truth_idx=P))
        ok = v.recovery >= RECOVERY_BAR and v.hit
        all_pass = all_pass and ok
        results[gname] = {"seed": seed, "recovery": round(v.recovery, 4),
                          "heldout": round(v.heldout_recovery, 4),
                          "pmax": round(v.pmax, 3), "bar": round(v.bar, 3),
                          "hit": v.hit, "pass": ok}
        print(f"{gname:24s} int-seed 3301  rec={v.recovery:.3f} ho={v.heldout_recovery:.3f} "
              f"pmax={v.pmax:.2f}/bar={v.bar:.2f} HIT={v.hit}")
    # str-seed path (Py2 str-hash) control
    for gname in ("py27_random29",):
        K = ZOO[gname]("THE PRIMES ARE SACRED")
        C = enc_skip_by_two(P, K)
        v = H.evaluate(H.HitDecode(C=C, K=K, o=0, preset="pair",
                                   n_round_adjudicated=100000, truth_idx=P))
        ok = v.recovery >= RECOVERY_BAR and v.hit
        all_pass = all_pass and ok
        results[gname + "_STR"] = {"seed": "THE PRIMES ARE SACRED",
                                   "recovery": round(v.recovery, 4), "hit": v.hit, "pass": ok}
        print(f"{gname:24s} str-seed       rec={v.recovery:.3f} HIT={v.hit}")

    out = {"lane": "round26/C/control", "recovery_bar": RECOVERY_BAR,
           "plant": "enc_skip_by_two supp=0.83, English self_reliance L=240, semantic seed",
           "all_pass": all_pass, "generators": results,
           "min_recovery": min(r["recovery"] for r in results.values())}
    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print(f"\nALL PASS = {all_pass}   min recovery = {out['min_recovery']}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
