#!/usr/bin/env python3
"""R28-L1 PLANTED CONTROLS (mandatory, pre-registered; run BEFORE any null decode).

Two plants, both enciphered with the REAL authoritative `_560.00.iso-authoritative`
bytes (sha256-verified) reduced mod29, at a NON-ZERO on-grid offset (o=49152=3*16384):

  (i)  one-draw key-skip filter  (sk.encipher_keyskip, supp=0.83)
       -> must be recovered >=0.90 with HIT=True by the keyskip1 relation
          (driftbeam preset "exact") through the SAME hitfn20 gate the sweep uses.
  (ii) skip_by_two filter        (enc_skip_by_two, j+=2 per rejection, supp=0.83)
       -> must be recovered >=0.90 with HIT=True by the keyskip2 relation
          (driftbeam preset "pair") through the same gate.

Also, per PREREG, each plant is screened through the lane's ACTUAL screen path
(L=400 beam + I2 adjudicate pmax vs the 5.0 candidate bar) to prove a real key
cannot slip past the screen either.

PASS iff both plants: screen pmax >= 5.0 AND hitfn20 HIT=True AND recovery >= 0.90.
If either fails the lane HALTS (PREREG Q5a): no null is published.

Writes control.json.
"""
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("src", "analysis/round11", "analysis/campaign18_skip",
          "analysis/round19/I1", "analysis/round19/I2",
          "analysis/round20/P3", "analysis/round20/HITFN"):
    q = os.path.join(LP, p)
    if q not in sys.path:
        sys.path.insert(0, q)

from lp import gematria as gp        # noqa: E402
import skipdecode as sk              # noqa: E402
import driftbeam as DB               # noqa: E402
import adjudicate as AD              # noqa: E402
import hitfn20 as H                  # noqa: E402

N = gp.N
PAD = os.path.join(LP, "analysis", "round12", "A1", "pads",
                   "DATA__560.00.iso-authoritative")
PAD_SHA = "a24051a87f0eb25ca21accbd3158fdf7b4911243e5ee1b9778b81182f0d36573"
PAD_LEN = 3992970
O_TRUE = 49152            # 3 * 16384 : non-zero, ON the lane's _560.00 offset grid
SUPP = 0.83               # the L7-B / A1 suppression level
L_PLANT = 240             # hitfn20's gate length
SCREEN_BAR = 5.0
RECOVERY_BAR = 0.90

# PARABLE-register plaintext (the register of LP's solved pages), long enough for 240 runes.
PLAIN_EN = (
    "THE PRIMES ARE SACRED AND THE TOTIENT FUNCTION IS SACRED ALL THINGS "
    "SHOULD BE ENCRYPTED KNOW THIS THAT THE INSTAR EMERGENCE IS AT HAND AND "
    "THE PILGRIM WHO SOLVES THE DEEP WEB SHALL FIND THE TRUTH WITHIN THE "
    "SACRED GEOMETRY OF THE CIRCUMFERENCE LIKE THE INSTAR TUNNELING TO THE "
    "SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN "
    "AND EMERGE"
)


def enc_skip_by_two(P, K, supp=0.83, seed=3301):
    """The 2013 rejection loop that burns TWO key draws per rejection (j += 2).
    Verbatim from round24/C2-skip-by-two/control.py / round18 L7-B."""
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


def verify_pad():
    h = hashlib.sha256()
    n = 0
    with open(PAD, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
            n += len(ch)
    ok = h.hexdigest() == PAD_SHA and n == PAD_LEN
    if not ok:
        print("FATAL: authoritative pad drifted; refusing to run.")
        sys.exit(2)
    return n


def screen(C, K, o, preset):
    """The lane's ACTUAL screen path: L=400-capped beam + adjudicate pmax."""
    d = DB.beam_decode(list(C)[:400], K, sign=-1, o=o, beam_w=120,
                       **DB.PRESETS[preset])
    a = AD.adjudicate(d["plain_idx"])
    return float(a["pmax"]), d["score"]


def gate(C, K, o, preset, truth):
    dec = H.HitDecode(C=list(C), K=list(K), o=o, sign=-1, preset=preset,
                      n_round_adjudicated=10 ** 6, truth_idx=list(truth))
    v = H.evaluate(dec)
    return dict(hit=bool(v.hit), reason=v.reason, pmax=round(v.pmax, 3),
                bar=round(v.bar, 3), recovery=round(v.recovery, 4),
                heldout=round(v.heldout_recovery, 4), score=round(v.score, 3),
                preg=v.preg_name, recovery_source=v.recovery_source)


def main():
    verify_pad()
    b = open(PAD, "rb").read()
    Kfull = [x % N for x in b]
    P = sk.eng_to_idx(PLAIN_EN)[:L_PLANT]
    assert len(P) == L_PLANT, f"plaintext too short: {len(P)}"

    out = {"lane": "round28/L1/control", "pad": os.path.basename(PAD),
           "pad_sha256": PAD_SHA, "offset_true": O_TRUE, "supp": SUPP,
           "plain_len": L_PLANT, "screen_bar": SCREEN_BAR,
           "recovery_bar": RECOVERY_BAR}

    # ---- plant (i): one-draw keyskip -> keyskip1/"exact"
    C1, skips1, _ = sk.encipher_keyskip(P, Kfull[O_TRUE:], sign=-1, supp=SUPP)
    pm1, sc1 = screen(C1, Kfull, O_TRUE, "exact")
    g1 = gate(C1, Kfull, O_TRUE, "exact", P)
    out["plant_keyskip1"] = {"n_skips": sum(skips1), "screen_pmax": round(pm1, 3),
                             "screen_beam_score": round(sc1, 3), "gate": g1}

    # ---- plant (ii): skip_by_two -> keyskip2/"pair"
    # enc_skip_by_two adds the key (c = p + k); decode convention sign=-1 (per C2 control);
    # to keep the lane's sign=-1 semantics identical we encipher c = (p - k) mod N by
    # feeding the negated keystream, exactly as sweep sign=-1 assumes p = c + k? No:
    # C2's measured control enciphers c=(p+K) and decodes sign=-1 -- we reproduce that
    # exact, already-validated convention.
    C2, nsk2 = enc_skip_by_two(P, Kfull[O_TRUE:], supp=SUPP, seed=3301)
    pm2, sc2 = screen(C2, Kfull, O_TRUE, "pair")
    g2 = gate(C2, Kfull, O_TRUE, "pair", P)
    out["plant_skip_by_two"] = {"n_rejections": nsk2, "screen_pmax": round(pm2, 3),
                                "screen_beam_score": round(sc2, 3), "gate": g2}

    # cross-check: the beam (keyskip1) must NOT be able to stand in for pair on plant (ii)
    gx = gate(C2, Kfull, O_TRUE, "exact", P)
    out["crosscheck_beam_on_skip_by_two"] = gx

    ok1 = g1["hit"] and g1["recovery"] >= RECOVERY_BAR and pm1 >= SCREEN_BAR
    ok2 = g2["hit"] and g2["recovery"] >= RECOVERY_BAR and pm2 >= SCREEN_BAR
    out["PASS"] = bool(ok1 and ok2)
    out["verdict"] = ("VALIDATED -- both relations recover their plant through the real "
                      "screen+gate path" if out["PASS"] else
                      "FAILED -- LANE HALTS, no null is published (PREREG Q5a)")
    json.dump(out, open(os.path.join(HERE, "control.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out["PASS"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
