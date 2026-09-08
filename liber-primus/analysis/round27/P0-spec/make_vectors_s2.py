#!/usr/bin/env python3
"""Round 27 / P0 -- S2 reference-vector extraction (keyskip1 'exact' relation).

PREREG S2 gate: the 'exact' lane may not contribute a null until it has its OWN
planted control + V1-style vector file. This script delivers both, by RUNNING the
existing control-validated Python pipeline (imports round25/compute-tail/runner.py and
its modules verbatim; reimplements NOTHING -- the same pattern as make_vectors.py):

    seed -> first 128 post-reducer keystream values (random29; identical to S1 --
            the keystream does not depend on the relation)
         -> stage-A beam decode under DB.PRESETS["exact"] (mode keyskip1, max_skip=3)
            of C_SCREEN (plain_idx, beam score, ptr_end, n_skips)
         -> the exact stage-A pmax at full float precision

plus the S2 constants (claim bar panelmax_bar('exact',1e6,0.01), cell contract) and the
S2 planted control: held-out English enciphered under the ONE-DRAW rejection loop
(`skipdecode.encipher_keyskip` -- the construction keyskip1 is exact for; NOT
skip_by_two, which is S1's plant) with a known seed's random29 keystream, then pushed
through the real hitfn20 3-clause gate (preset="exact", strict truth_idx recovery).

The same 64 seeds as vectors.json (FIXED_SEEDS + Random(20260907)) are reused on
purpose: their ks128 parity is already established by the S1 V1 gate, so the S2 check
isolates the relation change.

Regenerate:  python3 make_vectors_s2.py   (writes vectors_s2.json next to this file)
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
R25 = os.path.join(LP, "analysis", "round25", "compute-tail")
sys.path.insert(0, R25)

import runner  # noqa: the R25 pipeline, verbatim
import driftbeam as DB
import adjudicate as AD
import hitfn20 as H

OUT = os.path.join(HERE, "vectors_s2.json")

PRESET_S2 = "exact"                    # keyskip1, max_skip=3 -- one-draw rejection loop
CLAIM_BAR_S2_EXPECTED = 7.6341931878728095   # sweep_plan.json S2 / engine.dat CLAIM_BAR_EXACT
PLANT_SEED = 777

FIXED_SEEDS = [0, 1, 3301, 1325734783, 2149309687, 2 ** 32 - 1]
N_RANDOM = 58
RAND_SEED = 20260907                   # frozen: same seed list as vectors.json


def stage_a_s2(w, cipher=None):
    """runner.stage_a with the intermediates exposed, under the S2 'exact' preset."""
    K = runner.word_stream(w, runner.L_SCREEN * 6 + 64)
    C = runner.C_SCREEN if cipher is None else cipher
    d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=runner.SCREEN_BEAM_W,
                       **DB.PRESETS[PRESET_S2])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return K, d, a


def main():
    rng = random.Random(RAND_SEED)
    seeds = FIXED_SEEDS + sorted(rng.randrange(0, 2 ** 32) for _ in range(N_RANDOM))
    rows = []
    for w in seeds:
        K, d, a = stage_a_s2(w)
        rows.append({
            "seed": w,
            "ks128": runner.word_stream(w, 128),
            "pmax": repr(float(a["pmax"])),
            "en": repr(float(a["en"])),
            "beam_score": repr(float(d["score"])),
            "quad_score": repr(float(d["quad_score"])),
            "plain_idx": d["plain_idx"],
            "ptr_end": d["ptr_end"],
            "n_skips": d["n_skips"],
            "nchars": d["nchars"],
        })

    # ---- S2 constants ---------------------------------------------------------
    pan = AD.panel()
    mu, sd, _, _ = pan.cal(runner.L_SCREEN)
    bar = H.PM.panelmax_bar(PRESET_S2, 10 ** 6, 0.01)
    cell = H.PM.panelmax_contract(preset=PRESET_S2, n_round_adjudicated=10 ** 6)
    assert abs(float(bar) - CLAIM_BAR_S2_EXPECTED) < 1e-12, (bar, CLAIM_BAR_S2_EXPECTED)
    Q = DB.Q

    # ---- S2 planted control: encipher_keyskip (ONE-draw rejection loop) ------
    # This is the construction driftbeam mode="keyskip1" is exact for (driftbeam
    # docstring + campaign18_skip controls). skip_by_two (j += 2) is S1's plant and
    # would be WRONG here.
    import skipdecode as sk
    with open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
              encoding="utf-8", errors="ignore") as f:
        truth = sk.eng_to_idx(f.read())[5000:5000 + runner.L_HIT]
    Kp = runner.word_stream(PLANT_SEED, runner.L_HIT * 6 + 64)
    C, skips, used = sk.encipher_keyskip(truth, Kp, sign=-1, supp=0.83, seed=PLANT_SEED)

    # full 3-clause gate (hitfn20, preset='exact', strict truth_idx recovery)
    dec = H.HitDecode(C=C, K=Kp, o=0, preset=PRESET_S2, n_round_adjudicated=10 ** 6,
                      truth_idx=truth[:len(C)])
    v = H.evaluate(dec)
    verdict = {"seed": PLANT_SEED, "recovery": round(v.recovery, 4),
               "heldout": round(v.heldout_recovery, 4), "pmax": round(v.pmax, 3),
               "bar": round(v.bar, 3), "hit": bool(v.hit),
               "recovery_1000": bool(v.recovery >= 0.999),
               "recovery_source": v.recovery_source}
    assert v.hit and v.recovery >= 0.90, verdict

    # ---- planted STAGE-A construct: the screen-level positive control the C engine
    # runs through its real sweep code path (relation 'exact'). pmax must clear the
    # candidate bar AND the S2 claim bar so the plant lands in candidates.jsonl and
    # raises the HIT-CANDIDATE flag.
    da = DB.beam_decode(C[:runner.L_SCREEN], Kp, sign=-1, o=0,
                        beam_w=runner.SCREEN_BEAM_W, **DB.PRESETS[PRESET_S2])
    aa = AD.adjudicate(da["plain_idx"], translit=da.get("translit"))
    planted_stage_a = {
        "seed": PLANT_SEED,
        "cipher_idx_120": C[:runner.L_SCREEN],
        "pmax": repr(float(aa["pmax"])),
        "beam_score": repr(float(da["score"])),
        "plain_idx": da["plain_idx"],
        "note": "S2 C-engine control: micro-sweep a band containing seed 777 against "
                "this cipher under relation 'exact'; seed 777's pmax must match this "
                "value, exceed cand_bar 5.0 and the S2 claim bar 7.6341931878728095.",
    }
    assert float(aa["pmax"]) >= runner.SCREEN_BAR, aa["pmax"]
    assert float(aa["pmax"]) >= CLAIM_BAR_S2_EXPECTED, aa["pmax"]

    out = {
        "provenance": {
            "generated_by": "analysis/round27/P0-spec/make_vectors_s2.py",
            "pipeline": "analysis/round25/compute-tail/runner.py (imported verbatim)",
            "lane": "round27 S2 -- relation 'exact' (keyskip1, max_skip=3)",
            "rand_seed": RAND_SEED,
            "n_seeds": len(seeds),
        },
        "constants": {
            "SPACE": runner.SPACE,
            "PRESET": PRESET_S2,
            "preset_kw": DB.PRESETS[PRESET_S2],
            "MODE": runner.MODE,
            "L_SCREEN": runner.L_SCREEN,
            "L_HIT": runner.L_HIT,
            "SCREEN_BAR": runner.SCREEN_BAR,
            "SCREEN_BEAM_W": runner.SCREEN_BEAM_W,
            "sign": -1, "offset": 0,
            "keystream_len_stage_a": runner.L_SCREEN * 6 + 64,
            "keystream_len_stage_b": runner.L_HIT * 6 + 64,
            "claim_bar_exact_1e6": repr(float(bar)),
            "panelmax_cell": {"mu": repr(cell["mu"]), "beta": repr(cell["beta"]),
                              "cell": cell["cell"], "M": cell["cell_M"],
                              "alpha": 0.01, "n_round_adjudicated": 10 ** 6},
            "registers": pan.registers,
            "panel_mu_n120": [repr(float(v_)) for v_ in mu],
            "panel_sd_n120": [repr(float(v_)) for v_ in sd],
            "quadgram": {"file": "data/english_quadgrams.txt",
                         "total": Q.total, "floor": repr(Q.floor),
                         "n_entries": len(Q.d)},
        },
        "ciphertext": {
            "source": "lib_numchannel.unsolved() -- LP2 pages 0-54 flattened, 12956 runes"
                      " (identical slice to vectors.json)",
            "C_SCREEN": runner.C_SCREEN,
            "C_HIT": runner.C_HIT,
        },
        "seed_vectors": rows,
        "planted_selftest": {
            "seed": PLANT_SEED,
            "relation": "encipher_keyskip sign=-1 supp=0.83 rng=random.Random(777) "
                        "(ONE-draw rejection loop -- the construction keyskip1 is exact for)",
            "truth_source": "data/keys/self_reliance.txt eng_to_idx[5000:5240]",
            "truth_idx": truth,
            "keystream_first128": Kp[:128],
            "cipher_idx": C,
            "n_key_skips_in_plant": sum(skips),
            "verdict": verdict,
        },
        "planted_stage_a": planted_stage_a,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", OUT)
    print("seeds:", len(seeds), " claim_bar_exact_1e6:", repr(float(bar)))
    print("stage-A pmax range over vectors: [%s, %s]"
          % (min(float(r["pmax"]) for r in rows), max(float(r["pmax"]) for r in rows)))
    print("planted stage-A pmax:", planted_stage_a["pmax"])
    print("planted full-gate verdict:", verdict)


if __name__ == "__main__":
    main()
