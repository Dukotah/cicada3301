"""guard.py -- THE hallucination guard for hitfn20 (the whole point of defect (d)).

Two planted decodes, one required outcome each:

  FAKE  a decode that SCORES ABOVE the panel-max bar but has LOW rune-index recovery -- the
        EN_NOVOWEL failure mode (recovery 0.26-0.84 while pmax clears 7.634). is_hit MUST
        REJECT it. If the gate accepted this, an S-lane would certify a hallucinating decode.

  REAL  a genuine high-score high-recovery decode (correct key over English plaintext,
        recovery ~1.0). is_hit MUST ACCEPT it. If the gate rejected this, the gate is so
        strict it kills the power I1/I2/P3 bought -- an over-tight gate is also a defect.

The FAKE is not synthetic noise dressed up: it is REAL vowel-dropped English plaintext,
enciphered with a REAL key and decoded with the CORRECT key -- and it STILL fails to recover,
because at the `exact` preset the beam lands in a vowel-dropped-English-plausible basin that
is not the truth. That is precisely the score/recovery decoupling R1 A-iv named and the reason
`pmax >= bar` alone cannot certify a hit.

Run:  python3 guard.py           # prints PASS/FAIL + writes out_guard.json
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(LP, "analysis", "round19", "I1"),
           os.path.join(LP, "analysis", "round19", "I2"),
           os.path.join(LP, "analysis", "round19", "I3"),
           os.path.join(LP, "analysis", "round20", "P3"),
           os.path.join(LP, "src"), os.path.join(LP, "analysis", "campaign18_skip")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import driftbeam as DB                 # noqa: E402
import adjudicate as AD                # noqa: E402
import plants as PL3                   # noqa: E402  I3 register plaintext streams
import skipdecode as sk                # noqa: E402
import plant as PLK                    # noqa: E402
import hitfn20 as H                    # noqa: E402

L = 240
SUPP = 0.83
PRESET = "exact"                        # the CALIBRATED M=1e6 bar; the EN_NOVOWEL failure lives here


def _key():
    return PLK.make_key("sha256_ctr", length=L * 12 + 1024, seed=b"CICADA3301")


def _find_fake(K, stream, want_lo=0.26, want_hi=0.85, tries=40):
    """Search EN_NOVOWEL plants for one that CLEARS the panel-max bar on pmax but recovers in
    [want_lo, want_hi] -- the documented hallucination the guard must reject."""
    bar = H.PM.panelmax_bar(PRESET, 10 ** 6, 0.01)
    for rep in range(tries):
        rng = random.Random(1000 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _sk, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=500 + rep)
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **DB.PRESETS[PRESET])
        a = AD.adjudicate(d["plain_idx"], translit=d["translit"])
        rec = DB.recovery(d["plain_idx"], P)
        if a["pmax"] >= bar and want_lo <= rec <= want_hi:
            return dict(C=C, K=list(K), P=P, pmax=float(a["pmax"]), bar=float(bar),
                        recovery=rec, score=float(d["score"]),
                        preg=AD.panel().registers[a["preg"]], rep=rep, seed=500 + rep)
    return None


def _find_real(K, stream, tries=20):
    """A genuine decode: correct key over English plaintext, recovery ~1.0, pmax >> bar."""
    bar = H.PM.panelmax_bar(PRESET, 10 ** 6, 0.01)
    for rep in range(tries):
        rng = random.Random(7000 + rep)
        s = rng.randrange(0, len(stream) - L - 1)
        P = list(stream[s:s + L])
        C, _sk, _ = sk.encipher_keyskip(P, K, sign=-1, supp=SUPP, seed=99 + rep)
        d = DB.beam_decode(C, K, sign=-1, o=0, beam_w=400, **DB.PRESETS[PRESET])
        a = AD.adjudicate(d["plain_idx"], translit=d["translit"])
        rec = DB.recovery(d["plain_idx"], P)
        if a["pmax"] >= bar and rec >= 0.95:
            return dict(C=C, K=list(K), P=P, pmax=float(a["pmax"]), bar=float(bar),
                        recovery=rec, score=float(d["score"]),
                        preg=AD.panel().registers[a["preg"]], rep=rep, seed=99 + rep)
    return None


def run_guard():
    panels = PL3._panels()
    K = _key()
    fake_src = _find_fake(K, panels["EN_NOVOWEL"])
    real_src = _find_real(K, panels["EN_MODERN"])
    assert fake_src is not None, "could not construct a bar-clearing low-recovery EN_NOVOWEL fake"
    assert real_src is not None, "could not construct a genuine high-recovery decode"

    # ---- adjudicate BOTH through is_hit, in BOTH modes ---------------------------------
    # strict/control mode (truth_idx supplied) is what proves the guard; the real-candidate
    # held-out mode is the deployable proxy, reported alongside to show they agree.
    def judge(src, truth):
        strict = H.HitDecode(C=src["C"], K=src["K"], o=0, preset=PRESET,
                             n_round_adjudicated=10 ** 6, truth_idx=truth)
        vs = H.evaluate(strict)
        real = H.HitDecode(C=src["C"], K=src["K"], o=0, preset=PRESET,
                           n_round_adjudicated=10 ** 6)      # NO truth -> held-out proxy
        vr = H.evaluate(real)
        return vs, vr

    fs, fr = judge(fake_src, fake_src["P"])
    rs, rr = judge(real_src, real_src["P"])

    fake_rejected_strict = (fs.hit is False)
    fake_rejected_real = (fr.hit is False)
    real_accepted_strict = (rs.hit is True)

    guard_pass = bool(fake_rejected_strict and fake_rejected_real and real_accepted_strict)

    summary = {
        "guard_pass": guard_pass,
        "panelmax_bar_exact_1e6": fake_src["bar"],
        "FAKE_hallucination": {
            "what": "REAL vowel-dropped-English plaintext, correct key, exact preset -- clears "
                    "the panel-max bar on pmax but the decode does not recover the plaintext",
            "pmax": fake_src["pmax"], "score": fake_src["score"],
            "clears_null": fs.clears_null,
            "true_rune_index_recovery": fake_src["recovery"],
            "preg": fake_src["preg"],
            "is_hit_strict": fs.hit, "strict_reason": fs.reason,
            "is_hit_realmode_heldout": fr.hit, "realmode_reason": fr.reason,
            "heldout_recovery": fr.heldout_recovery,
            "REJECTED": fake_rejected_strict and fake_rejected_real,
        },
        "REAL_genuine": {
            "what": "correct key over English plaintext, recovery ~1.0",
            "pmax": real_src["pmax"], "score": real_src["score"],
            "clears_null": rs.clears_null,
            "true_rune_index_recovery": real_src["recovery"],
            "preg": real_src["preg"],
            "is_hit_strict": rs.hit, "strict_reason": rs.reason,
            "is_hit_realmode_heldout": rr.hit,
            "heldout_recovery": rr.heldout_recovery,
            "ACCEPTED": real_accepted_strict,
        },
    }
    out = {"summary": summary, "fake_src_meta": {k: fake_src[k] for k in
                                                 ("rep", "seed", "pmax", "bar", "recovery", "preg")},
           "real_src_meta": {k: real_src[k] for k in
                             ("rep", "seed", "pmax", "bar", "recovery", "preg")}}
    json.dump(out, open(os.path.join(HERE, "out_guard.json"), "w", encoding="utf-8"),
              indent=1, default=float)
    return out


if __name__ == "__main__":
    out = run_guard()
    s = out["summary"]
    print("=" * 70)
    print("HALLUCINATION GUARD  (resolves red-team defect (d))")
    print("=" * 70)
    print(f"panel-max bar (exact preset, N=1e6, a=0.01): {s['panelmax_bar_exact_1e6']:.3f}")
    f = s["FAKE_hallucination"]
    print(f"\nFAKE  pmax={f['pmax']:.2f} (clears={f['clears_null']})  "
          f"true recovery={f['true_rune_index_recovery']:.3f}  preg={f['preg']}")
    print(f"      held-out recovery={f['heldout_recovery']:.3f}")
    print(f"      is_hit strict={f['is_hit_strict']}  realmode={f['is_hit_realmode_heldout']}  "
          f"-> REJECTED={f['REJECTED']}")
    print(f"      reason: {f['strict_reason']}")
    r = s["REAL_genuine"]
    print(f"\nREAL  pmax={r['pmax']:.2f} (clears={r['clears_null']})  "
          f"true recovery={r['true_rune_index_recovery']:.3f}  preg={r['preg']}")
    print(f"      held-out recovery={r['heldout_recovery']:.3f}")
    print(f"      is_hit strict={r['is_hit_strict']}  realmode={r['is_hit_realmode_heldout']}  "
          f"-> ACCEPTED={r['ACCEPTED']}")
    print(f"\n{'='*70}\nGUARD {'PASS' if s['guard_pass'] else 'FAIL'} "
          f"(rejects the fake AND accepts the real)\n{'='*70}")
