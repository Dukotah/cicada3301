#!/usr/bin/env python3
"""L3 POSITIVE CONTROL — per (reducer, map) config, plant a Py2.7 init_by_array key and recover
it RANK-1 through the full pipeline (I1 keyskip1 -> I2 panel -> P3a bar -> HITFN is_hit) BEFORE
trusting any null. Doctrine: a null from an unvalidated instrument is not a negative. Kill
condition: a config whose control does not recover rank-1 at pmax>=bar is a WIRING GAP -> skip it,
do not report its null.

Configs (S-G3 covered only random29/i386-1word; this lane adds the rest):
  grb5_mod   / i386 1-word      getrandbits(5)%29
  grb5_rej   / i386 1-word      getrandbits(5) rejection
  shuffle29  / i386 1-word      repeated shuffle(range(29))
  random29   / amd64 2-word     init_by_array([w_lo, w_hi])

    python3 poscontrol.py
writes out_poscontrol.json ; exit 0 iff every config PASSES.
"""
import json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("../../round19/I1", "../../round19/I2", "../../round19/I3", "../../round20/P3",
          "../../round19/G3", "../../campaign18_skip", "../../../src", "../../round11",
          "../../round20/HITFN"):
    ap = os.path.abspath(os.path.join(HERE, p))
    if ap not in sys.path:
        sys.path.insert(0, ap)

import gen_py27 as G          # noqa: E402
import driftbeam as DB        # noqa: E402
import adjudicate as AD       # noqa: E402
import skipdecode as sk       # noqa: E402
import plants as PL3          # noqa: E402
import hitfn20 as H           # noqa: E402

L = 240
SUPP = 0.83
W_TRUE = 1325734783           # top P3b prior seed used AS the 32-bit word

# (config-id, reducer mode, key-words builder taking w). i386 map = [w]; amd64 map = [lo, hi].
CONFIGS = [
    ("grb5_mod_i386",  "grb5_mod",  lambda w: [w] if w else [0]),
    ("grb5_rej_i386",  "grb5_rej",  lambda w: [w] if w else [0]),
    ("shuffle29_i386", "shuffle29", lambda w: [w] if w else [0]),
    ("random29_amd64", "random29",  lambda w: [w & 0xFFFFFFFF, (w >> 32) & 0xFFFFFFFF]),
]


def word_stream(words, mode, n=L * 6 + 64):
    r = G.MT19937()
    r.init_by_array(words)
    return G.REDUCERS[mode](r, n)


def run_config(cfg_id, mode, keybuilder):
    # For amd64 config give W_TRUE a nonzero high word so the 2-word path is genuinely exercised.
    w = W_TRUE if mode != "random29" else (W_TRUE | (0x9E3779B9 << 32))
    panels = PL3._panels()
    P = list(panels["EN_MODERN"][2000:2000 + L])
    Ktrue = word_stream(keybuilder(w), mode)
    C, _sk, _ = sk.encipher_keyskip(P, Ktrue, sign=-1, supp=SUPP, seed=42)

    dec_strict = H.HitDecode(C=C, K=Ktrue, o=0, preset="exact",
                             n_round_adjudicated=10 ** 6, truth_idx=P)
    vs = H.evaluate(dec_strict)
    dec_real = H.HitDecode(C=C, K=Ktrue, o=0, preset="exact", n_round_adjudicated=10 ** 6)
    vr = H.evaluate(dec_real)

    # rank the true word among +-500 wrong-word neighborhood on pmax (low word perturbed)
    def pmax_of(ww):
        K = word_stream(keybuilder(ww), mode)
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **DB.PRESETS["exact"])
        return AD.adjudicate(d["plain_idx"], translit=d.get("translit"))["pmax"]

    true_pmax = pmax_of(w)
    rng = random.Random(7)
    wrong = []
    while len(wrong) < 99:
        ww = w + rng.randint(-500, 500)
        if ww != w:
            wrong.append(ww)
    wp = [pmax_of(x) for x in wrong]
    rank = 1 + sum(1 for x in wp if x >= true_pmax)

    return {
        "config": cfg_id, "reducer": mode, "planted_word": w,
        "n_key_words": len(keybuilder(w)),
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


def run():
    results = [run_config(*c) for c in CONFIGS]
    out = {
        "lane": "round21/L3-py27-reducers-plus-64bit-map positive control",
        "generator": "gen_py27.init_by_array(words) reducer sweep (Py2.7 string-seed word)",
        "plaintext_register": "EN_MODERN", "L": L, "supp": SUPP,
        "configs": results,
        "PASS_all": all(r["PASS"] for r in results),
        "passing_configs": [r["config"] for r in results if r["PASS"]],
        "wiring_gaps": [r["config"] for r in results if not r["PASS"]],
    }
    json.dump(out, open(os.path.join(HERE, "out_poscontrol.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    r = run()
    print("\nPOSITIVE CONTROL:", "PASS" if r["PASS_all"] else "PARTIAL/FAIL",
          "passing=", r["passing_configs"], "gaps=", r["wiring_gaps"])
    sys.exit(0 if r["PASS_all"] else 1)
