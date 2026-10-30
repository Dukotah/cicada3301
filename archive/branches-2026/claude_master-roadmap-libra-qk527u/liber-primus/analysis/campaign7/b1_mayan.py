"""Campaign VII — Track B1: the 2012 Mayan rotation key vs the LP2 rune pages.

The 2012 puzzle's Mayan numerals decoded to a per-character polyalphabetic
rotation key (clevcode write-up; catalogued in Campaign VI OSINT findings):

    KEY = 10 2 14 7 19 6 18 12 7 8 17 0 19   (13 rotations)

This is a *confirmed Cicada-authored numeric key* that has never been applied to
the Liber Primus runes. Numeric (non-linguistic) keys are exactly the class the
doublet-mechanism proof leaves open (see MASTER-ROADMAP §1). Cheap to run.

We test it exhaustively as a repeating polyalphabetic shift over Gematria-Primus
indices (mod 29): forward + reversed key, decrypt/encrypt sign, ±atbash,
interrupter-aware and not, per-page and whole-book. Any score_norm > -5.2 is a
hit (real English ~ -4.0..-4.4; noise ~ -7.4). Emits JSON + prints the leader.
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, ciphers, solve, score as _score  # noqa
from run_stats import load_pages  # noqa

N = gp.N
SC = _score.default()
THRESHOLD = -5.2

MAYAN = [10, 2, 14, 7, 19, 6, 18, 12, 7, 8, 17, 0, 19]
KEY_VARIANTS = {
    "mayan_fwd": [k % N for k in MAYAN],
    "mayan_rev": [k % N for k in MAYAN[::-1]],
}


def score_idx(idxs):
    return SC.score_norm(gp.indices_to_translit(idxs))


def run():
    pages = load_pages()
    unsolved = pages[:-2]            # last two are solved AN END / PARABLE
    whole = [i for pg in unsolved for i in pg]

    best = {"score": -99.0, "rec": None}
    hits = []

    def consider(s, rec):
        if s > best["score"]:
            best.update(score=s, rec=rec)
        if s > THRESHOLD:
            hits.append({**rec, "score": round(s, 3)})

    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    for kname, key in KEY_VARIANTS.items():
        for tname, idxs in targets:
            runes = gp.indices_to_runes(idxs)
            for sign in (-1, +1):
                for atb in (False, True):
                    # (a) plain repeating key, no interrupters
                    stream = ciphers.repeat_key(key, len(idxs))
                    p = [((N - 1 - c if atb else c) + sign * stream[j]) % N
                         for j, c in enumerate(idxs)]
                    s = score_idx(p)
                    consider(s, {"target": tname, "key": kname,
                                 "method": f"shift sign{sign:+d} atb{int(atb)} noint",
                                 "plaintext": gp.indices_to_translit(p)[:80]})

                    # (b) interrupter-aware (ᚠ = null, does not advance keystream)
                    txt, pidx = ciphers.transform_runes(
                        runes, lambda L, k=key: ciphers.repeat_key(k, L),
                        sign=sign, interrupters=True, atbash=atb)
                    s2 = SC.score_norm(txt)
                    consider(s2, {"target": tname, "key": kname,
                                  "method": f"shift sign{sign:+d} atb{int(atb)} INT",
                                  "plaintext": txt[:80]})

    hits.sort(key=lambda h: -h["score"])
    out = {
        "campaign": "VII", "track": "B1", "key_source": "2012 Mayan rotation key",
        "key": MAYAN, "threshold": THRESHOLD,
        "best_score": round(best["score"], 3), "best": best["rec"],
        "n_hits": len(hits), "hits": hits[:20],
    }
    json.dump(out, open(os.path.join(HERE, "b1_mayan_results.json"), "w"), indent=2)
    print(f"Track B1 — Mayan key. best score_norm = {best['score']:.3f}  "
          f"(English ~ -4.0..-4.4, noise ~ -7.4, threshold {THRESHOLD})")
    r = best["rec"]
    print(f"  best: {r['target']} {r['key']} {r['method']}\n        {r['plaintext']}")
    print(f"  hits over threshold: {len(hits)}")
    return out


if __name__ == "__main__":
    run()
