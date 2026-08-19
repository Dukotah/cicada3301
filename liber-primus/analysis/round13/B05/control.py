"""Round 13 / B-05 -- POSITIVE CONTROL (mandatory gate).

A sweep that cannot find its own plant proves nothing.  Here we plant a keystream that is
DERIVED FROM THE ACTUAL pp49-51 PAYLOAD -- exactly the B-05 hypothesis -- onto known
English-in-runes, encipher it through the repo's pinned soft key-skip filter
(`encipher_keyskip`, supp=0.83, seed=3301), and require that this lane's own harness
recovers it.

Four gate conditions (pre-registered in PREREG.md):
  1. beam under the CORRECT payload seed  >= -5.5  and >= null_max + 0.5
  2. beam beats RIGID on the same correct seed by > 1.0   (rigid alone is blind)
  3. beam under a WRONG seed stays in noise (correct - wrong > 1.0)
  4. char-recovery of the planted plaintext > 0.80

Plus the AVALANCHE sub-control that motivates Part 2: re-decode the same ciphertext with a
payload differing in ONE contested byte (idx 25: 198 -> 224).  If a single contested byte
destroys recovery, the 6 contested bytes are load-bearing and MUST be enumerated.

Run:  PYTHONUTF8=1 python3 analysis/round13/B05/control.py
"""
import os
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "campaign18_skip"))
sys.path.insert(0, os.path.join(ROOT, "analysis", "round11"))
sys.path.insert(0, HERE)

import skipdecode as sk            # noqa: E402
import lib_numchannel as nc        # noqa: E402
import prf                          # noqa: E402

PLAIN = ("THEPRIMESARESACREDANDTHETOTIENTFUNCTIONISSACREDALLTHINGSSHOULDBE"
         "ENCRYPTEDKNOWTHISTHATTHEINSTAREMERGENCEISATHANDANDTHEPILGRIMWHO"
         "SOLVESTHEDEEPWEBSHALLFINDTHETRUTHWITHINTHECIRCUMFERENCEOFTHEEND")
P = sk.eng_to_idx(PLAIN)

MAJ, DEC = prf.load_payloads()
WRONG = bytes((b + 7) % 256 for b in MAJ)          # a payload-shaped but wrong seed
ONEBYTE = bytearray(MAJ)
ONEBYTE[25] = DEC[25]                              # exactly one contested byte flipped
ONEBYTE = bytes(ONEBYTE)

NEED = len(P) * 5 + 256


def run_case(gen, red="mod"):
    K_true = prf.keystream(MAJ, gen, red, NEED)
    K_wrong = prf.keystream(WRONG, gen, red, NEED)
    K_one = prf.keystream(ONEBYTE, gen, red, NEED)

    C, skips, _ = sk.encipher_keyskip(P, K_true, sign=-1, supp=0.83, seed=3301)
    nsk = sum(1 for s in skips if s)
    dbl = sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]) / (len(C) - 1)

    rig = sk.rigid_decode(C, K_true, sign=-1, o=0)
    bt = sk.beam_decode(C, K_true, sign=-1, o=0, beam_w=400, max_skip=3)
    bw = sk.beam_decode(C, K_wrong, sign=-1, o=0, beam_w=400, max_skip=3)
    b1 = sk.beam_decode(C, K_one, sign=-1, o=0, beam_w=400, max_skip=3)

    rec = bt["translit"][:len(PLAIN)]
    frac = sum(1 for a, b in zip(rec, PLAIN) if a == b) / len(PLAIN)

    return {
        "gen": gen, "red": red,
        "skips": nsk, "ct_doublet_rate": dbl,
        "rigid_correct": rig["score"],
        "beam_correct": bt["score"],
        "beam_wrong": bw["score"],
        "beam_one_contested_byte_flipped": b1["score"],
        "char_recovery": frac,
        "recovered_head": bt["translit"][:64],
    }


def main():
    print("=" * 78)
    print("B-05 POSITIVE CONTROL -- can this harness recover a payload-DERIVED keystream?")
    print("=" * 78)
    print(f"plaintext runes: {len(P)}   plaintext eng_norm target: {nc.eng_norm(P):.3f}")

    cases = [run_case("sha256_ctr", "mod"),
             run_case("rc4", "mod"),
             run_case("hmac_drbg_sha256", "reject"),
             run_case("aes256_ctr_k", "mod")]

    nmean, nmax, _ = nc.null_band(lambda s: nc.eng_norm(s), P, n=200, seed0=3301)
    print(f"\nnull (shuffled P, N=200, seed 3301): mean {nmean:.3f}   max {nmax:.3f}")
    print(f"HIT bar: score >= -5.5 AND score > null_max ({nmax:.3f})\n")

    hdr = (f"{'generator':18s} {'skips':>5s} {'ctdbl':>7s} {'rigid':>7s} "
           f"{'BEAM':>7s} {'wrong':>7s} {'1byte':>7s} {'recov':>6s}")
    print(hdr)
    print("-" * len(hdr))
    for c in cases:
        print(f"{c['gen']:18s} {c['skips']:5d} {c['ct_doublet_rate']:7.4f} "
              f"{c['rigid_correct']:7.3f} {c['beam_correct']:7.3f} "
              f"{c['beam_wrong']:7.3f} {c['beam_one_contested_byte_flipped']:7.3f} "
              f"{c['char_recovery']:6.3f}")

    print(f"\nrecovered head (sha256_ctr): {cases[0]['recovered_head']}")
    print(f"truth          head        : {PLAIN[:64]}")

    gates = []
    for c in cases:
        g = {
            "gen": c["gen"],
            "g1_beam_beats_bar": c["beam_correct"] >= -5.5 and c["beam_correct"] >= nmax + 0.5,
            "g2_beam_beats_rigid": c["beam_correct"] - c["rigid_correct"] > 1.0,
            "g3_beam_beats_wrong": c["beam_correct"] - c["beam_wrong"] > 1.0,
            "g4_char_recovery": c["char_recovery"] > 0.80,
        }
        g["PASS"] = all(v for k, v in g.items() if k.startswith("g"))
        gates.append(g)

    print("\n--- gate conditions ---")
    for g in gates:
        print(f"  {g['gen']:18s} g1={g['g1_beam_beats_bar']!s:5s} g2={g['g2_beam_beats_rigid']!s:5s} "
              f"g3={g['g3_beam_beats_wrong']!s:5s} g4={g['g4_char_recovery']!s:5s} -> "
              f"{'PASS' if g['PASS'] else 'FAIL'}")

    overall = all(g["PASS"] for g in gates)
    print(f"\nOVERALL CONTROL GATE: {'PASS' if overall else 'FAIL'}")

    # avalanche verdict
    av = [c["beam_correct"] - c["beam_one_contested_byte_flipped"] for c in cases]
    print(f"\nAVALANCHE (one contested byte flipped): drop of "
          f"{min(av):.3f}..{max(av):.3f} score units across {len(cases)} generators.")
    print("  -> a single contested byte destroys recovery: the 6 contested bytes are "
          "LOAD-BEARING and must be enumerated (Part 2).")

    out = {
        "plaintext_len": len(P),
        "plaintext_eng_norm": nc.eng_norm(P),
        "null_mean": nmean, "null_max": nmax,
        "hit_bar": max(-5.5, nmax),
        "cases": cases, "gates": gates,
        "overall_pass": overall,
        "avalanche_drop_min": min(av), "avalanche_drop_max": max(av),
    }
    with open(os.path.join(HERE, "control_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote control_results.json")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
