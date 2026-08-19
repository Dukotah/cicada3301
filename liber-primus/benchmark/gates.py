"""PLANT-AND-RECOVER GATES — prove your instrument can find the answer before you claim
there isn't one.

For each cipher family this project has faced, a gate plants a KNOWN answer and asserts
the reference decoder recovers it. Each gate also runs the negative direction: a wrong key
must stay in noise, and a shuffled plant must not be "recovered". A benchmark that only
ever passes is decoration.

    python3 gates.py                 # run them all, print a table
    python3 -m pytest test_gates.py  # same thing, as assertions

Why this exists, concretely: every seed sweep in this repository before Round 12 used RIGID
alignment. Under the anti-repeat filter, rigid decoding scores the CORRECT key at -6.835 --
indistinguishable from noise -- while the skip-aware beam recovers it at -4.170. Billions of
decodes were run through an instrument that could not have succeeded even if the hypothesis
had been right. `gate_rigid_vs_beam` below reproduces that fact in about two seconds.

To validate your OWN decoder, pass it in:

    from gates import run_all
    run_all(decoder=my_decode)     # my_decode(C, K, sign) -> {"score": float,
                                   #                          "translit": str}
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LP, "src"))
sys.path.insert(0, os.path.join(LP, "analysis", "round11"))
sys.path.insert(0, os.path.join(LP, "analysis", "campaign18_skip"))

import plant as PL
import skipdecode as sk

N = 29
ENGLISH = -5.2          # a recovered plant must reach at least this
NOISE_CEIL = -6.0       # a wrong key must stay at or below this
MIN_RECOVERY = 0.85     # fraction of ground-truth runes recovered


def _beam(C, K, sign=-1, **kw):
    return sk.beam_decode(C, K, sign=sign, o=0, beam_w=kw.get("beam_w", 400),
                          max_skip=kw.get("max_skip", 3))


def _rigid(C, K, sign=-1, **kw):
    return sk.rigid_decode(C, K, sign=sign)


def _gate(name, p, decoder, why, wrong_key=None, min_recovery=MIN_RECOVERY):
    """Run one gate: recover the plant, then fail to recover a wrong key."""
    t0 = time.time()
    d = decoder(p.C, p.K, sign=p.truth.get("sign", -1))
    # Compare RUNE INDICES, not the transliteration string. 7 of 29 runes expand to two
    # characters, so a single wrong rune shifts the string and makes a 99%-correct decode
    # look ~30% correct. Measuring recovery on the string is a real trap -- it cost this
    # gate a false FAIL before it was caught.
    rec = (p.recovery(d["plain_idx"]) if "plain_idx" in d
           else p.recovery_text(d["translit"]))
    wk = wrong_key or [(i * 7 + 13) % N for i in range(len(p.K))]
    dw = decoder(p.C, wk, sign=p.truth.get("sign", -1))
    ok = (d["score"] >= ENGLISH and rec >= min_recovery
          and dw["score"] <= NOISE_CEIL)
    return {"gate": name, "passed": ok, "why": why,
            "recovered_score": d["score"], "recovery": rec,
            "wrong_key_score": dw["score"], "margin": d["score"] - dw["score"],
            "elapsed_s": round(time.time() - t0, 2),
            "text": d["translit"][:56]}


# ---------------------------------------------------------------- the gates
def gate_running_rigid(decoder=_rigid):
    """A plain running key with NO filter. The easiest case; if this fails, stop."""
    p = PL.plant(key="running", mechanism="none", length=240)
    return _gate("running_key/no_filter/rigid", p, decoder,
                 "baseline: rigid decode recovers an unfiltered running key")


def gate_running_skip(decoder=_beam):
    """Running key under the pinned KEY-SKIP filter (the key desyncs)."""
    p = PL.plant(key="running", mechanism="skip", length=240)
    return _gate("running_key/skip_filter/beam", p, decoder,
                 "the mechanism Campaign XVIII validated against")


def gate_running_rewrite(decoder=_beam):
    """Running key under the VALUE-REWRITE filter (key stays synced, output corrupted).

    RECON-B/B-16 flagged that the decoder had never been validated against this form;
    Round 12 D1 tested it and it holds. This gate keeps that honest.
    """
    p = PL.plant(key="running", mechanism="rewrite", length=240)
    return _gate("running_key/rewrite_filter/beam", p, decoder,
                 "the mechanism Campaigns X/XI actually pinned (B-16)",
                 min_recovery=0.80)


def gate_derived_sha_ctr(decoder=_beam):
    """A SHA-256 counter-mode keystream from a short seed, under the filter.

    THE lane the ciphertext cannot exclude. If your instrument cannot pass this, any
    'the pad is not derived' claim you make is empty.
    """
    p = PL.plant(key="sha256_ctr", mechanism="skip", length=240,
                 key_kw={"seed": b"CICADA3301"})
    return _gate("derived_sha256_ctr/skip/beam", p, decoder,
                 "short-seed derived keystream — the one live hypothesis class")


def gate_prng(decoder=_beam):
    """A seeded-PRNG pad under the filter."""
    p = PL.plant(key="prng", mechanism="skip", length=240, key_kw={"seed": 3301})
    return _gate("seeded_prng/skip/beam", p, decoder,
                 "the family Round 8 swept — but swept RIGIDLY, see below")


def gate_rigid_vs_beam():
    """THE gate that matters most. Same filtered ciphertext, same CORRECT key, two
    decoders. Rigid must FAIL and beam must SUCCEED.

    This single comparison is why most published 'ruled out' claims about Liber Primus --
    including years of this repository's own -- do not mean what they say.
    """
    p = PL.plant(key="sha256_ctr", mechanism="skip", length=240,
                 key_kw={"seed": b"CICADA3301"})
    r = _rigid(p.C, p.K, sign=-1)
    b = _beam(p.C, p.K, sign=-1)
    ok = r["score"] <= NOISE_CEIL and b["score"] >= ENGLISH
    return {"gate": "rigid_vs_beam/DIAGNOSTIC", "passed": ok,
            "why": "rigid scores the CORRECT key as noise; beam recovers it",
            "rigid_correct_key": r["score"], "beam_correct_key": b["score"],
            "margin": b["score"] - r["score"],
            "recovery": p.recovery_text(b["translit"]),
            "text": b["translit"][:56],
            "lesson": "A rigid-decoder null over ANY filtered cipher is unsound."}


def gate_shuffled_plant_not_recovered(decoder=_beam):
    """Negative direction: destroy the plant's ordering; recovery must collapse.

    Guards against a scorer that rewards letter frequency rather than structure.
    """
    import random
    p = PL.plant(key="running", mechanism="skip", length=240)
    r = random.Random(3301)
    C = list(p.C)
    r.shuffle(C)
    d = decoder(C, p.K, sign=-1)
    ok = d["score"] <= NOISE_CEIL
    return {"gate": "shuffled_plant/NEGATIVE", "passed": ok,
            "why": "a shuffled plant must NOT be recoverable",
            "shuffled_score": d["score"], "text": d["translit"][:56]}


ALL_GATES = [gate_running_rigid, gate_running_skip, gate_running_rewrite,
             gate_derived_sha_ctr, gate_prng, gate_rigid_vs_beam,
             gate_shuffled_plant_not_recovered]


def run_all(decoder=None, verbose=True):
    out = []
    for g in ALL_GATES:
        try:
            r = g(decoder) if (decoder and g is not gate_rigid_vs_beam
                               and g is not gate_running_rigid) else g()
        except TypeError:
            r = g()
        out.append(r)
        if verbose:
            mark = "PASS" if r["passed"] else "FAIL"
            extra = (f"recovered {r.get('recovered_score', r.get('beam_correct_key', 0)):.3f}"
                     f"  wrong {r.get('wrong_key_score', r.get('rigid_correct_key', 0)):.3f}")
            print(f"  [{mark}] {r['gate']:38s} {extra}")
            if r.get("recovery") is not None:
                print(f"         recovery {r['recovery']:.1%}   {r.get('text','')[:48]}")
    if verbose:
        n_ok = sum(1 for r in out if r["passed"])
        print(f"\n{n_ok}/{len(out)} gates passed")
        if n_ok < len(out):
            print("A failing gate means your instrument cannot detect the family it")
            print("covers. Any null you produce over that family is not a negative.")
    return out


if __name__ == "__main__":
    print("=" * 74)
    print("PLANT-AND-RECOVER GATES")
    print("=" * 74)
    run_all()
