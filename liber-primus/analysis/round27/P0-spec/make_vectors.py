#!/usr/bin/env python3
"""Round 27 / P0 -- reference-vector extraction for the C port of the R25 grind.

RUNS the existing control-validated Python pipeline (imports round25/compute-tail/runner.py
and its modules verbatim; reimplements NOTHING) and freezes, for ~64 seeds spread over the
2^32 space:

    seed -> first 128 post-reducer keystream values (random29)
         -> stage_a beam decode artifacts (plain_idx, beam score, ptr_end, n_skips)
         -> the exact stage_a pmax score at full float precision

plus the pipeline constants a C engine must match (claim bar, screen bar, panel mu/sd at
n=120, quadgram floor, ciphertext slices) and the planted-seed self-test construct
(synthetic ciphertext + seed that MUST fire HIT=True through hitfn20).

Regenerate:  python3 make_vectors.py   (writes vectors.json next to this file)
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

OUT = os.path.join(HERE, "vectors.json")

FIXED_SEEDS = [0, 1, 3301, 1325734783, 2149309687, 2 ** 32 - 1]
N_RANDOM = 58
RAND_SEED = 20260907          # frozen: vectors are reproducible


def stage_a_full(w):
    """runner.stage_a with the intermediates exposed (same calls, same order)."""
    K = runner.word_stream(w, runner.L_SCREEN * 6 + 64)
    d = DB.beam_decode(runner.C_SCREEN, K, sign=-1, o=0, beam_w=runner.SCREEN_BEAM_W,
                       **DB.PRESETS[runner.PRESET])
    a = AD.adjudicate(d["plain_idx"], translit=d.get("translit"))
    return K, d, a


def main():
    rng = random.Random(RAND_SEED)
    seeds = FIXED_SEEDS + sorted(rng.randrange(0, 2 ** 32) for _ in range(N_RANDOM))
    rows = []
    for w in seeds:
        K, d, a = stage_a_full(w)
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

    # ---- cross-check: R25's global best must reproduce (pmax 6.826 @ 2149309687)
    best = next(r for r in rows if r["seed"] == 2149309687)
    assert round(float(best["pmax"]), 3) == 6.826, best["pmax"]

    # ---- pipeline constants ---------------------------------------------------
    pan = AD.panel()
    mu, sd, _, _ = pan.cal(runner.L_SCREEN)
    bar = H.PM.panelmax_bar(runner.PRESET, 10 ** 6, 0.01)
    cell = H.PM.panelmax_contract(preset=runner.PRESET, n_round_adjudicated=10 ** 6)
    Q = DB.Q

    # ---- planted-seed self-test construct (must fire HIT=True) ---------------
    st = runner.planted_seed_selftest(seed=777)
    assert st["hit"] and st["recovery_1000"], st
    # reconstruct the exact plant artifacts (same code path as runner.planted_seed_selftest)
    import skipdecode as sk
    with open(os.path.join(LP, "data", "keys", "self_reliance.txt"),
              encoding="utf-8", errors="ignore") as f:
        truth = sk.eng_to_idx(f.read())[5000:5000 + runner.L_HIT]
    Kp = runner.word_stream(777, runner.L_HIT * 6 + 64)
    prng = random.Random(777)
    C, j, c_prev = [], 0, None
    for p in truth:
        while True:
            c = (p + Kp[j]) % 29
            if c_prev is not None and c == c_prev and prng.random() < 0.83:
                j += 2
                continue
            break
        C.append(c)
        j += 1
        c_prev = c

    # ---- planted STAGE-A construct: the screen-level positive control a C engine can
    # run directly. Decode the first 120 runes of the plant cipher with the SAME seed's
    # keystream through the exact stage_a configuration; the resulting pmax must clear
    # the candidate bar by a wide margin, proving the screen cannot reject a true seed
    # (of this register/construction class).
    da = DB.beam_decode(C[:runner.L_SCREEN], Kp, sign=-1, o=0,
                        beam_w=runner.SCREEN_BEAM_W, **DB.PRESETS[runner.PRESET])
    aa = AD.adjudicate(da["plain_idx"], translit=da.get("translit"))
    planted_stage_a = {
        "seed": 777,
        "cipher_idx_120": C[:runner.L_SCREEN],
        "pmax": repr(float(aa["pmax"])),
        "beam_score": repr(float(da["score"])),
        "plain_idx": da["plain_idx"],
        "note": "C engine self-test: screen this cipher with seed 777; pmax must match "
                "and must exceed the candidate bar.",
    }
    assert float(aa["pmax"]) >= runner.SCREEN_BAR, aa["pmax"]

    # ---- a full stage_b record for the R25 best word (pins the Python re-scorer)
    sb = runner.stage_b(2149309687, 10 ** 6)

    out = {
        "provenance": {
            "generated_by": "analysis/round27/P0-spec/make_vectors.py",
            "pipeline": "analysis/round25/compute-tail/runner.py (imported verbatim)",
            "rand_seed": RAND_SEED,
            "n_seeds": len(seeds),
        },
        "constants": {
            "SPACE": runner.SPACE,
            "PRESET": runner.PRESET,
            "preset_kw": DB.PRESETS[runner.PRESET],
            "MODE": runner.MODE,
            "L_SCREEN": runner.L_SCREEN,
            "L_HIT": runner.L_HIT,
            "SCREEN_BAR": runner.SCREEN_BAR,
            "SCREEN_BEAM_W": runner.SCREEN_BEAM_W,
            "sign": -1, "offset": 0,
            "keystream_len_stage_a": runner.L_SCREEN * 6 + 64,
            "keystream_len_stage_b": runner.L_HIT * 6 + 64,
            "claim_bar_pair_1e6": repr(float(bar)),
            "panelmax_cell": {"mu": repr(cell["mu"]), "beta": repr(cell["beta"]),
                              "cell": cell["cell"], "M": cell["cell_M"],
                              "alpha": 0.01, "n_round_adjudicated": 10 ** 6},
            "candidate_margin_recommended": 1.5,
            "candidate_bar_recommended": repr(float(bar) - 1.5),
            "registers": pan.registers,
            "panel_mu_n120": [repr(float(v)) for v in mu],
            "panel_sd_n120": [repr(float(v)) for v in sd],
            "quadgram": {"file": "data/english_quadgrams.txt",
                         "total": Q.total, "floor": repr(Q.floor),
                         "n_entries": len(Q.d)},
            "dense_max": runner.DENSE_MAX,
            "tail_start_default": runner.TAIL_START_DEFAULT,
            "exclusion_set_size": len(runner.build_exclusion()),
        },
        "ciphertext": {
            "source": "lib_numchannel.unsolved() -- LP2 pages 0-54 flattened, 12956 runes",
            "C_SCREEN": runner.C_SCREEN,
            "C_HIT": runner.C_HIT,
        },
        "seed_vectors": rows,
        "planted_selftest": {
            "seed": 777,
            "relation": "skip_by_two supp=0.83, rng=random.Random(777) (Py3 int-seed MT)",
            "truth_source": "data/keys/self_reliance.txt eng_to_idx[5000:5240]",
            "truth_idx": truth,
            "keystream_first128": Kp[:128],
            "cipher_idx": C,
            "verdict": st,
        },
        "planted_stage_a": planted_stage_a,
        "stage_b_best_word": sb,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", OUT)
    print("seeds:", len(seeds), " best pmax @2149309687:", best["pmax"],
          " bar:", repr(float(bar)))
    print("self-test:", st)


if __name__ == "__main__":
    main()
