"""Round 19 / C1 -- re-adjudicate the B-05 propagation sweep under I2 + I3.

Why this exists. `b05_rerun.py` reproduced B-05's Round-13 grid on the RESOLVED payload and
scored it exactly the way Round 13 did: English quadgram only, against the constant -5.5.
Two Round-19 findings make that write-up inadmissible on its own:

  * I3 measured -5.5 to be the wrong bar in 14 of 14 historical sweeps (usually too strict),
    and publishes a calibrated contract instead. A bar is a property of the triple
    (null generator, decoder transition relation, adjudicator statistic), not a constant.
  * Doctrine R3 requires the four language-agnostic statistics to be persisted AT SWEEP TIME.
    `out_b05_rerun.json` stores only (parameters, English score, 48-char head) -- i.e. it is
    the 16th consecutive R3-non-compliant sweep. That is exactly the defect I2's SWEEPROW/1
    exists to end, and it cannot be retro-fitted after the decodes are discarded.

So the grid is decoded again and adjudicated through I2, and every decode is persisted as a
SWEEPROW/1 row. The DECODER is unchanged from B-05 (skipdecode.beam_decode, beam_w=120,
max_skip=3) so the sweep stays comparable to Round 13; I3's R-I1-5 records that this decoder
is numerically identical to driftbeam's `keyskip1` preset, which licenses the
`I19:vecbeam.keyskip1+I2` calibration cells.

Length note, stated because it cuts against us. B-05 decodes HEAD=400 runes; I3's cells for
this register exist at L in {31, 120}. The panel statistics are therefore computed on the
first 120 indices of a decode the beam optimised over 400. That makes the statistic slightly
LARGER than a true 120-rune decode's, i.e. it biases toward FALSE POSITIVES, not toward a
false negative -- so a null under it is safe, while a hit would have needed re-checking at a
matched length. The legacy `en` is also reported on the full 400 for Round-13 comparability.

    python3 b05_readjudicate.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
R19 = os.path.abspath(os.path.join(HERE, ".."))
LP = os.path.abspath(os.path.join(R19, "..", ".."))
B05 = os.path.join(LP, "analysis", "round13", "B05")
for p in (os.path.join(LP, "src"), os.path.join(LP, "analysis"),
          os.path.join(LP, "analysis", "campaign18_skip"),
          os.path.join(LP, "analysis", "round11"), B05,
          os.path.join(R19, "I2"), os.path.join(R19, "I3")):
    sys.path.insert(0, p)

import numpy as np                     # noqa: E402
import skipdecode as sk                # noqa: E402
import lib_numchannel as nc            # noqa: E402
import prf                             # noqa: E402
import adjudicate as ADJ               # noqa: E402
import nullcurve19 as NCV              # noqa: E402

HEAD, BEAM_W, MAX_SKIP = 400, 120, 3
ADJ_LEN = 120                          # a CALIBRATED length (I3 R-I2-5)
OFFSETS = [0, 1, 2, 3, 5, 8, 13, 29, 64, 128, 256, 512, 1024, 3301]
REDUCTIONS, SIGNS = ["mod", "reject"], [-1, +1]
DIRECTIONS, ATBASH = ["fwd", "rev"], [False, True]
REGISTER = "I19:vecbeam.keyskip1+I2"

UNS = nc.unsolved()
HEADSEQ = UNS[:HEAD]
TOTAL_KS = len(UNS) * (MAX_SKIP + 1) + max(OFFSETS) + 64
RESOLVED = open(os.path.join(HERE, "payload_resolved.bin"), "rb").read()
CANON = open(os.path.join(LP, "analysis", "pp49_51", "canon_256.bin"), "rb").read()
CHANGED = [i for i in range(256) if RESOLVED[i] != CANON[i]]


def main():
    t0 = time.time()
    reps = {"res." + k: fn(RESOLVED) for k, fn in prf.REPR_FNS.items()}
    gens = list(prf.GENERATORS)
    n_planned = (len(reps) * len(gens) * len(REDUCTIONS) * len(DIRECTIONS)
                 * len(ATBASH) * len(SIGNS) * len(OFFSETS))

    contract = {s: NCV.threshold_contract(n_trials=n_planned, segment_len=ADJ_LEN,
                                          register=REGISTER, statistic=s)
                for s in ("pmax", "en")}
    print("planned decodes: %d" % n_planned)
    for s, c in contract.items():
        print("  bar[%-4s] escalate %.4f  claim %.4f   cell %s (%s, M=%s, extrapolated=%s)"
              % (s, c["escalate_bar"], c["claim_bar"], c["cell"], c["cell_status"],
                 c["cell_n_null_decodes"], c["extrapolated"]))

    hdr = ADJ.header(
        "round19/C1/B-05-propagation-resolved-payload",
        key_space=("B-05's Round-13 pinned Part-1 grid, restricted to the 6 representations "
                   "of the RESOLVED pp49-51 payload (sha256 3b9b07d9...b290; differs from "
                   "canon_256.bin at indices %s). 6 reps x 15 PRF generators x {mod,reject} "
                   "x {fwd,rev} x {atbash,plain} x {+1,-1} x 14 offsets = %d decodes, "
                   "exhaustive over that grid." % (CHANGED, n_planned)),
        decoder=("skipdecode.beam_decode, beam_w=%d, max_skip=%d, HEAD=%d. The transition "
                 "relation is EXACT for encipher_keyskip and NOTHING else (round18 L7-B); "
                 "skip_by_two and free drift are not representable. I1's repaired decoder is "
                 "deliberately not used: this sweep's purpose is comparability with Round 13."
                 % (BEAM_W, MAX_SKIP, HEAD)),
        adjudicator=("I2 adjudicate() 9-register panel on RUNE INDICES; panel statistics at "
                     "L=%d (a calibrated length); legacy en also reported at L=%d."
                     % (ADJ_LEN, HEAD)),
        threshold_contract=contract,
        beam_w=BEAM_W, max_skip=MAX_SKIP, head=HEAD, adj_len=ADJ_LEN,
        lane="round19/C1", propagates_from="A-04")

    path = os.path.join(HERE, "out_b05_sweeprow.jsonl")
    f = open(path, "w")
    f.write(json.dumps(hdr) + "\n")

    best_en = (-99.0, None)
    best_pmax = (-99.0, None, 0)
    esc, en400 = [], []
    ndone = 0
    for rname in sorted(reps):
        seed = reps[rname]
        for gname in gens:
            for red in REDUCTIONS:
                base = prf.keystream(seed, gname, red, TOTAL_KS)
                for direction in DIRECTIONS:
                    Kd = base if direction == "fwd" else base[::-1]
                    for atb in ATBASH:
                        K = prf.atbash(Kd) if atb else Kd
                        for sign in SIGNS:
                            for o in OFFSETS:
                                bd = sk.beam_decode(HEADSEQ, K, sign=sign, o=o,
                                                    beam_w=BEAM_W, max_skip=MAX_SKIP)
                                idx = np.asarray(bd["plain_idx"][:ADJ_LEN], dtype=np.int64)
                                res = ADJ.adjudicate(idx)
                                kid = "%s|%s|%s|%s|atb%d|s%+d|o%d" % (
                                    rname, gname, red, direction, int(atb), sign, o)
                                f.write(json.dumps(ADJ.to_row(res, kid)) + "\n")
                                ndone += 1
                                en400.append(bd["score"])
                                if res["en"] > best_en[0]:
                                    best_en = (res["en"], kid)
                                if res["pmax"] > best_pmax[0]:
                                    best_pmax = (float(res["pmax"]), kid, int(res["preg"]))
                                if (res["pmax"] >= contract["pmax"]["escalate_bar"]
                                        or res["en"] >= contract["en"]["escalate_bar"]):
                                    esc.append({"kid": kid, "en": res["en"],
                                                "pmax": float(res["pmax"]),
                                                "preg": int(res["preg"]),
                                                "ioc": res["ioc"], "mds": int(res["mds"]),
                                                "h2": res["h2"], "zl": res["zl"]})
            print("  [%-14s %-18s] cum=%6d %6.0fs  best_en(L%d)=%.3f  best_pmax=%.3f"
                  % (rname, gname, ndone, time.time() - t0, ADJ_LEN,
                     best_en[0], best_pmax[0]), flush=True)
    f.close()

    regs = ADJ.panel().registers
    out = {"lane": "round19/C1 -- B-05 propagation, re-adjudicated under I2 + I3",
           "n_decodes": ndone, "seconds": time.time() - t0,
           "sweeprow_store": os.path.basename(path),
           "threshold_contract": contract,
           "best_en_at_L%d" % ADJ_LEN: {"value": best_en[0], "kid": best_en[1]},
           "best_legacy_en_at_L%d" % HEAD: max(en400),
           "best_pmax": {"value": best_pmax[0], "kid": best_pmax[1],
                         "register": regs[best_pmax[2]]},
           "n_escalations": len(esc), "escalations": esc[:50],
           "verdict": "ESCALATE" if esc else "NEGATIVE",
           "conditionals": {
               "key_space": hdr["key_space"],
               "decoder_transition_model": hdr["decoder"],
               "adjudicator_register": ("I2's 9-register panel (%s) -- NOT English-only. "
                                        "pmax is the max standardised register score."
                                        % ", ".join(regs))}}
    json.dump(out, open(os.path.join(HERE, "out_b05_readjudicated.json"), "w"), indent=1)
    print("\nbest en   (L%d) = %.4f   vs claim bar %.4f"
          % (ADJ_LEN, best_en[0], contract["en"]["claim_bar"]))
    print("best pmax       = %.4f   vs claim bar %.4f   (register %s)"
          % (best_pmax[0], contract["pmax"]["claim_bar"], regs[best_pmax[2]]))
    print("legacy en at L=%d (Round-13 comparable) = %.4f" % (HEAD, max(en400)))
    print("escalations: %d    VERDICT: %s" % (len(esc), out["verdict"]))
    print("wrote out_b05_readjudicated.json + %s" % os.path.basename(path))


if __name__ == "__main__":
    main()
