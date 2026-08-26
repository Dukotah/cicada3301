"""ROUND 19 / G4 — POSITIVE CONTROL (PREREG.md 5, gate V5).

Ground-truth plant-and-recover for the TeX-generator enumerator. It deliberately
does NOT use the English adjudicator: Round 18's L7-A measured that instrument's
power at 0.33 (Latin) and 0.00 (vowel-dropped English), so borrowing power from it
would make this control meaningless. The ranking statistic here is **exact rune
agreement with the known planted plaintext** — ground truth, power 1.0 by
construction.

What it proves: the enumerator's plumbing — seed -> state -> mapping -> direction ->
sign -> atbash -> offset -> decode — is wired correctly, and a planted TeX-generated
pad is recovered at rank 1. What it does NOT prove: anything about whether LP2's
keystream came from TeX, or about any adjudicator's power. That is Phase 2's job and
it is gated on I1/I2/I3.

The pad is drawn from the REAL pdflatex binary (tex/ref_pgf.txt), not from Python, so
a Python-side bug cannot cancel itself out.

    python3 control.py
"""
from __future__ import annotations

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis", os.path.join("analysis", "round11"),
          os.path.join("analysis", "campaign18_skip")):
    sys.path.insert(0, os.path.join(ROOT, p))
sys.path.insert(0, HERE)

import skipdecode as sk                     # noqa: E402
import gen_tex as gt                        # noqa: E402

N = 29
L = 120
PLANT_SEED = 3301
PLANT_GEN = "pgf_mod29"
PLANT_SIGN = -1
PLANT_DIR = "fwd"
PLANT_ATBASH = 0
WINDOW = 10000                              # +/- phases around the planted phase

PLAINTEXT = (
    "THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBEENCRYPTED"
    "WITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOTHISVALUEANDITISTHEENDOF"
    "ALLTHINGSTHATWEHAVEKNOWNANDTHEBEGINNINGOFWHATWEHAVENOTYETSEENAMEN"
)


def real_tex_pad(seed=PLANT_SEED, label="R029"):
    """The planted pad, read out of the REAL pdflatex run (tex/ref_pgf.txt)."""
    path = os.path.join(HERE, "tex", "ref_pgf.txt")
    for line in open(path, encoding="utf-8", errors="replace"):
        parts = line.split()
        if len(parts) > 3 and parts[0] == "PGF" and parts[1] == str(seed) and parts[2] == label:
            return [int(x) for x in parts[3:]]
    raise SystemExit(f"no real-TeX vector for seed={seed} label={label} in {path}")


def atbash(C):
    return [(N - 1) - c for c in C]


def agreement(a, b):
    n = min(len(a), len(b))
    return sum(1 for i in range(n) if a[i] == b[i]) / float(n) if n else 0.0


def main():
    res = {"lane": "round19/G4", "control": "V5 ground-truth plant-and-recover",
           "statistic": "exact rune agreement with known plaintext (NOT an English score)"}

    # ---------------------------------------------------------------- plant
    P = sk.eng_to_idx(PLAINTEXT)[:L]
    if len(P) < L:
        raise SystemExit(f"plaintext too short: {len(P)} < {L}")

    # A. the pad the real binary produced, and the Python reimplementation of it
    tex_pad = real_tex_pad()
    py_pad = gt.make_ks(PLANT_GEN, PLANT_SEED, len(tex_pad))
    res["A_python_matches_real_binary"] = {
        "n": len(tex_pad), "equal": tex_pad == py_pad,
        "status": "PASS" if tex_pad == py_pad else "FAIL",
    }

    # B. encipher with the project's own pinned key-skip filter, using a key long
    #    enough that the skips cannot run off the end
    K = gt.make_ks(PLANT_GEN, PLANT_SEED, L * 6 + 256)
    assert K[:len(tex_pad)] == tex_pad, "planted key head must be the real-binary pad"
    C, skips, used = sk.encipher_keyskip(P, K, sign=PLANT_SIGN, supp=0.83, seed=3301)
    res["B_plant"] = {"generator": PLANT_GEN, "seed": PLANT_SEED, "L": L,
                      "n_key_skips": int(sum(skips)), "key_index_consumed": used[-1] + 1}

    # ---------------------------------------------------------------- recover
    # Enumerate PHASES around the planted phase.  This is the Q3 claim in action:
    # a phase is a seed, so walking phases is walking the whole single cycle.
    base = gt.advance("pgf", PLANT_SEED, -WINDOW % (gt.M31 - 1))
    phases = []
    z = base
    for _ in range(2 * WINDOW + 1):
        phases.append(z)
        z = gt.pgf_next(z)
    planted_index = WINDOW
    assert phases[planted_index] == PLANT_SEED, "phase arithmetic is wrong"

    C_at = atbash(C)
    rows = []
    ndec = 0
    for idx, ph in enumerate(phases):
        ks = gt.make_ks(PLANT_GEN, ph, L + 8)
        for sign in (-1, 1):
            for ab in (0, 1):
                Cx = C if ab == 0 else C_at
                dec = [(Cx[i] + sign * ks[i]) % N for i in range(L)]
                ndec += 1
                a = agreement(dec, P)
                if a > 0.30:
                    rows.append({"phase": ph, "phase_index": idx - WINDOW,
                                 "sign": sign, "atbash": ab, "agreement": round(a, 4)})
    rows.sort(key=lambda r: -r["agreement"])
    res["C_enumeration"] = {"phases": len(phases), "decodes": ndec,
                            "rigid_top": rows[:5]}

    top = rows[0] if rows else None
    planted_rank = next((i + 1 for i, r in enumerate(rows)
                         if r["phase"] == PLANT_SEED and r["sign"] == PLANT_SIGN
                         and r["atbash"] == PLANT_ATBASH), None)
    rigid_ok = bool(top and top["phase"] == PLANT_SEED and top["sign"] == PLANT_SIGN
                    and top["atbash"] == PLANT_ATBASH)
    res["C_rigid_rank1_is_planted"] = {
        "status": "PASS" if rigid_ok else "FAIL",
        "top": top,
        "planted_rank_of": len(rows),
        "planted_rank": planted_rank,
        "n_key_skips": int(sum(skips)),
        "note": ("rigid agreement is < 1.00 by design: the key-skip filter desynchronises "
                 "the key after the first skip, which is exactly the L7-B problem I1 exists "
                 "to fix. As pre-registered this gate asked for rank 1 at agreement 1.00; "
                 "see PREREG.md ADDENDUM 2026-08-26 for why that criterion is unattainable "
                 "by construction and what V5a measures instead."),
    }

    # V5a (see PREREG ADDENDUM): the planted phase must sit inside the top
    # (1 + n_skips) rigid band, because the rigid optimum is planted_phase + n_skips
    # by construction, not by chance.
    band = 1 + int(sum(skips))
    v5a_ok = bool(planted_rank is not None and planted_rank <= band
                  and top and abs(top["phase_index"]) <= band
                  and top["sign"] == PLANT_SIGN and top["atbash"] == PLANT_ATBASH)
    res["C_V5a_planted_in_skip_band"] = {
        "band": band, "planted_rank": planted_rank,
        "rigid_argmax_phase_index": top["phase_index"] if top else None,
        "status": "PASS" if v5a_ok else "FAIL",
        "mechanism": ("encipher_keyskip consumed key index 0..%d for %d plaintext runes, i.e. "
                      "the key ran %d ahead; the rigidly best-aligned phase is therefore the "
                      "planted phase advanced by that many steps"
                      % (used[-1], L, int(sum(skips)))),
    }

    # D. the skip-aware beam at the planted phase — recovery, not score
    ksK = gt.make_ks(PLANT_GEN, PLANT_SEED, L * 6 + 256)
    bd = sk.beam_decode(C, ksK, sign=PLANT_SIGN, o=0, beam_w=400, max_skip=3)
    rec = agreement(sk.eng_to_idx(bd["translit"]), P)
    res["D_beam_at_planted_seed"] = {
        "char_recovery_vs_known_plaintext": round(rec, 4),
        "translit_head": bd["translit"][:72],
        "score_recorded_not_interpreted": round(float(bd["score"]), 4),
        "status": "PASS" if rec >= 0.90 else "FAIL",
        "note": ("the score is recorded for the record and is NOT a decision statistic: "
                 "doctrine forbids adjudicating with the Round-18 instrument (L7-A/L7-B)."),
    }

    # E. a wrong-phase null, so 'rank 1' has something to be above
    wrong = []
    rng = random.Random(3301)
    for _ in range(200):
        ph = rng.randrange(1, gt.M31)
        ks = gt.make_ks(PLANT_GEN, ph, L + 8)
        wrong.append(agreement([(C[i] - ks[i]) % N for i in range(L)], P))
    res["E_wrong_phase_null"] = {
        "n": len(wrong), "mean": round(sum(wrong) / len(wrong), 4),
        "max": round(max(wrong), 4), "expected_mean_1_over_29": round(1 / 29, 4),
    }

    res["V5_status_as_prereg"] = "PASS" if (res["A_python_matches_real_binary"]["status"] == "PASS"
                                            and rigid_ok
                                            and res["D_beam_at_planted_seed"]["status"] == "PASS"
                                            and top["agreement"] > max(wrong) + 0.10) else "FAIL"
    res["V5a_status"] = "PASS" if (res["A_python_matches_real_binary"]["status"] == "PASS"
                                   and v5a_ok
                                   and res["D_beam_at_planted_seed"]["status"] == "PASS"
                                   and top["agreement"] > max(wrong) + 0.10) else "FAIL"

    out = os.path.join(HERE, "control_results.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "C_enumeration"}, indent=1))
    print("C_enumeration:", res["C_enumeration"]["phases"], "phases,",
          res["C_enumeration"]["decodes"], "decodes; top:", res["C_enumeration"]["rigid_top"][:3])
    print("wrote", out)
    return 0 if res["V5a_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
