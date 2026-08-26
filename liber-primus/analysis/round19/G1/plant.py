"""Round 19 / G1 -- THE PLANT, and the pilot that proves the plumbing.

PREREG section 1 Q1: G1 does not own the recognizer, so G1 ships the object the
recognizer must recover.  This builds a synthetic ciphertext from a keystream this lane
produces, under the repo's key-skip encipher model, and hands S1 both the ciphertext
and the correct spec.

    S1 MAY NOT REPORT A G1 NEGATIVE UNTIL IT HAS RECOVERED THIS PLANT AT RANK #1.

Running this file with I1's driftbeam and I2's adjudicator present also executes a
PILOT: a small, bounded cross-product around the planted spec, purely to prove the
plumbing and time it.  A pilot is not a sweep.  It carries no verdict and its score
distribution is not interpreted.

Run:  python3 plant.py            # build plant + (if I1/I2 present) run the pilot
      python3 plant.py --plant    # build the plant only
"""
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.dirname(HERE)
LP = os.path.dirname(os.path.dirname(R19))          # liber-primus/
for p in (HERE, os.path.join(LP, "src"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(R19, "I1"), os.path.join(R19, "I2")):
    if p not in sys.path:
        sys.path.insert(0, p)

import keystream as KS                              # noqa: E402
import reduce29 as R29                              # noqa: E402

PLANT_SPEC = {
    "family": "bash", "generator": "bash4.2", "seed": 3301,
    "reduction": "mod29", "sign": -1, "direction": "fwd", "atbash": False, "offset": 0,
}
PLANT_L = 120
PLANT_SUPP = 0.83          # the repo's pinned anti-repeat strength (campaigns X/XI)
PLANT_RNG_SEED = 3301

# LP-register English.  Taken from the solved pages so the plant is in the SAME
# register the real plaintext would be, not modern prose.
PLANT_TEXT = (
    "SOMEWISDOMTHEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
    "ENCRYPTEDKNOWTHISSHADOWSWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALL"
    "THINGSITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHERE"
)


def build_plant():
    import skipdecode as sk
    P = sk.eng_to_idx(PLANT_TEXT)[:PLANT_L]
    K = KS.keystream(PLANT_SPEC, PLANT_L * 8)
    C, skips, used = sk.encipher_keyskip(P, K, sign=PLANT_SPEC["sign"],
                                         supp=PLANT_SUPP, seed=PLANT_RNG_SEED)
    return {
        "spec": PLANT_SPEC,
        "L": PLANT_L,
        "supp": PLANT_SUPP,
        "encipher_rng_seed": PLANT_RNG_SEED,
        "plain_idx": P,
        "cipher_idx": C,
        "n_skips": int(sum(skips)),
        "key_ptr_end": int(used[-1]),
        "note": "Encipher model = campaign18_skip.encipher_keyskip (the repo's pinned "
                "key-skip filter). Round 18 L7-B showed a one-character variant "
                "(skip_by_two) is NOT representable by the old beam; I1's driftbeam is "
                "the thing that has to handle it, and S1 should plant BOTH.",
    }


def run_pilot(plant, n_seeds=200, stage="A", beam_w=400, max_skip=3, mode="keyskip1"):
    """PILOT -- bounded at n_seeds * 48 decodes.  Proves plumbing, reports timing.
    NOT A SWEEP.  No threshold is applied and no verdict is drawn."""
    import driftbeam as DB
    import adjudicate as AD

    C = plant["cipher_idx"]
    L = len(C)
    truth = plant["spec"]

    rng = random.Random(20260826)
    seeds = [truth["seed"]] + [rng.randrange(1, 2**31 - 1) for _ in range(n_seeds - 1)]

    pan = AD.panel()
    rows = []
    t0 = time.time()
    ndec = 0
    for s in seeds:
        for v in R29.variants(stage):
            spec = {"family": "bash", "generator": truth["generator"], "seed": s}
            spec.update(v)
            K = KS.keystream(spec, L * (max_skip + 2) + 64)
            r = DB.beam_decode(C, K, sign=spec["sign"], o=0, beam_w=beam_w,
                               max_skip=max_skip, mode=mode)
            a = AD.adjudicate(r["plain_idx"], pan=pan)
            rows.append((KS.spec_id(spec), r["score"], a["pmax"], a["pcon"],
                         a["ioc"], a["mds"], a["zl"],
                         spec == {**spec, **truth} and s == truth["seed"]
                         and v["reduction"] == truth["reduction"]
                         and v["sign"] == truth["sign"]
                         and v["direction"] == truth["direction"]
                         and v["atbash"] == truth["atbash"]
                         and v["offset"] == truth["offset"]))
            ndec += 1
    dt = time.time() - t0

    by_en = sorted(rows, key=lambda r: -r[1])
    by_pcon = sorted(rows, key=lambda r: -r[3])
    rank_en = next(i for i, r in enumerate(by_en) if r[7]) + 1
    rank_pcon = next(i for i, r in enumerate(by_pcon) if r[7]) + 1
    truth_row = next(r for r in rows if r[7])

    return {
        "label": "PILOT -- NOT A SWEEP. No threshold applied, no verdict drawn.",
        "decodes": ndec,
        "seconds": round(dt, 1),
        "decodes_per_sec": round(ndec / dt, 1),
        "decoder": {"module": "round19/I1/driftbeam.py", "mode": mode,
                    "beam_w": beam_w, "max_skip": max_skip},
        "adjudicator": "round19/I2/adjudicate.py",
        "planted_spec_id": KS.spec_id({**truth}),
        "planted_rank_by_english": rank_en,
        "planted_rank_by_pcon": rank_pcon,
        "planted_row": {"en": truth_row[1], "pmax": truth_row[2], "pcon": truth_row[3],
                        "ioc": truth_row[4], "mds": truth_row[5], "zl": truth_row[6]},
        "best_other_english": by_en[0][1] if not by_en[0][7] else by_en[1][1],
        "top5_by_english": [(r[0], round(r[1], 3)) for r in by_en[:5]],
    }


def main():
    plant = build_plant()
    out = {"plant": {k: v for k, v in plant.items() if k != "plain_idx"},
           "plain_head": plant["plain_idx"][:24]}
    with open(os.path.join(HERE, "plant.json"), "w") as fh:
        json.dump({**plant}, fh)
    print("plant built: L=%d skips=%d key_ptr_end=%d"
          % (plant["L"], plant["n_skips"], plant["key_ptr_end"]))

    if "--plant" in sys.argv:
        return 0

    have_i1 = os.path.exists(os.path.join(R19, "I1", "driftbeam.py"))
    have_i2 = os.path.exists(os.path.join(R19, "I2", "adjudicate.py"))
    if not (have_i1 and have_i2):
        print("I1/I2 interfaces not published -- HOLDING at the scoring boundary.")
        return 0

    n_seeds = 200
    for a in sys.argv[1:]:
        if a.startswith("--seeds="):
            n_seeds = int(a.split("=", 1)[1])
    res = run_pilot(plant, n_seeds=n_seeds)
    with open(os.path.join(HERE, "pilot.json"), "w") as fh:
        json.dump({"plant": out, "pilot": res}, fh, indent=1)
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
