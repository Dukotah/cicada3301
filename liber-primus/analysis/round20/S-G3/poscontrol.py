#!/usr/bin/env python3
"""S-G3 POSITIVE CONTROL — plant a Py2.7 `init_by_array([w])` key and recover it RANK-1
through the full pipeline (I1 keyskip1 -> I2 panel -> P3a bar -> HITFN is_hit) BEFORE trusting
any null. Doctrine: a null from an unvalidated instrument is not a negative.

Plants the top P3b prior seed (1325734783) AS THE WORD w, enciphers a real English plaintext via
keyskip (supp 0.83), then:
  (a) recovers it via is_hit in STRICT (truth_idx) and REAL (held-out) modes -> both must HIT;
  (b) ranks the true word among a +/-500 neighborhood of wrong words on pmax -> must be rank 1.

    python3 poscontrol.py
writes out_poscontrol.json.
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("../../round19/I1", "../../round19/I2", "../../round19/I3", "../../round20/P3",
          "../../round19/G3", "../../campaign18_skip", "../../../src", "../../round11"):
    ap = os.path.abspath(os.path.join(HERE, p))
    if ap not in sys.path:
        sys.path.insert(0, ap)

import gen_py27 as G          # noqa: E402
import driftbeam as DB        # noqa: E402
import adjudicate as AD       # noqa: E402
import skipdecode as sk       # noqa: E402
import plants as PL3          # noqa: E402
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "HITFN")))
import hitfn20 as H           # noqa: E402

L = 240
SUPP = 0.83
W_TRUE = 1325734783           # top P3b prior seed used AS the 32-bit word


def word_stream(w, mode="random29", n=L * 6 + 64):
    r = G.MT19937()
    r.init_by_array([w] if w else [0])
    return G.REDUCERS[mode](r, n)


def run():
    panels = PL3._panels()
    P = list(panels["EN_MODERN"][2000:2000 + L])
    Ktrue = word_stream(W_TRUE)
    C, _sk, _ = sk.encipher_keyskip(P, Ktrue, sign=-1, supp=SUPP, seed=42)

    # (a) recover through is_hit, strict + real modes
    dec_strict = H.HitDecode(C=C, K=Ktrue, o=0, preset="exact",
                             n_round_adjudicated=10 ** 6, truth_idx=P)
    vs = H.evaluate(dec_strict)
    dec_real = H.HitDecode(C=C, K=Ktrue, o=0, preset="exact", n_round_adjudicated=10 ** 6)
    vr = H.evaluate(dec_real)

    # (b) rank the true word among +/-500 wrong-word neighborhood on pmax
    def pmax_of(w):
        K = word_stream(w)
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
        return AD.adjudicate(d["plain_idx"], translit=d.get("translit"))["pmax"]

    true_pmax = pmax_of(W_TRUE)
    rng = random.Random(7)
    wrong = []
    while len(wrong) < 199:
        w = W_TRUE + rng.randint(-500, 500)
        if w != W_TRUE:
            wrong.append(w)
    wp = [pmax_of(w) for w in wrong]
    rank = 1 + sum(1 for x in wp if x >= true_pmax)

    out = {
        "lane": "round20/S-G3 positive control",
        "generator": "gen_py27.init_by_array([w]) random29 (Py2.7 32-bit string-seed word)",
        "planted_word": W_TRUE,
        "plaintext_register": "EN_MODERN",
        "L": L, "supp": SUPP,
        "panelmax_bar_exact_1e6": round(vs.bar, 4),
        "strict_mode": {"hit": vs.hit, "pmax": round(vs.pmax, 3),
                        "recovery": round(vs.recovery, 4),
                        "heldout_recovery": round(vs.heldout_recovery, 4),
                        "preg": vs.preg_name},
        "real_mode": {"hit": vr.hit, "pmax": round(vr.pmax, 3),
                      "recovery": round(vr.recovery, 4),
                      "heldout_recovery": round(vr.heldout_recovery, 4),
                      "preg": vr.preg_name},
        "rank1_recovery": {"true_word_pmax": round(true_pmax, 3),
                           "wrong_neighborhood_max_pmax": round(max(wp), 3),
                           "n_wrong": len(wp), "rank": rank,
                           "n_wrong_above_bar": sum(1 for x in wp if x >= vs.bar)},
        "PASS": bool(vs.hit and vr.hit and rank == 1),
    }
    json.dump(out, open(os.path.join(HERE, "out_poscontrol.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    r = run()
    print("\nPOSITIVE CONTROL:", "PASS" if r["PASS"] else "FAIL")
    sys.exit(0 if r["PASS"] else 1)
