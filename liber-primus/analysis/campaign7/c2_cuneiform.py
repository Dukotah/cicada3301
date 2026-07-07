"""Campaign VII — C2: the cuneiform / base-60 numerals as explicit keys.

Campaign VI confirmed the cuneiform numerals on the Babylonian-margin pages read
17, 13, 55, 1 -> base-60 -> 1033 (magic-square sum) and 3301 (group signature).
Short keys like these are, in principle, already covered by the exhaustive
Vigenere L1-4 sweep (do-not-redo) -- but a future researcher will specifically
ask "did anyone try the cuneiform numbers as a key?", so we run them EXPLICITLY
and record the direct negative rather than leaving it to inference.

Keys tested as mod-29 shifts (full sweep, all pages + whole book):
  17,13,55,1  and its reverse; 1033 & 3301 digit strings; the concatenation.
Any score_norm > -5.2 is a hit. (Expected: subsumed => null.)
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, ciphers, score as _score  # noqa
from run_stats import load_pages  # noqa

N = gp.N
SC = _score.default()
THRESHOLD = -5.2

KEYS = {
    "cuneiform_17_13_55_1": [17, 13, 55, 1],
    "cuneiform_rev": [1, 55, 13, 17],
    "digits_1033": [1, 0, 3, 3],
    "digits_3301": [3, 3, 0, 1],
    "cuneiform+1033+3301": [17, 13, 55, 1, 1, 0, 3, 3, 3, 3, 0, 1],
}


def run():
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    best = {"score": -99.0, "rec": None}
    per_key = {}
    hits = []

    def consider(s, rec):
        if s > best["score"]:
            best.update(score=s, rec=rec)
        if s > per_key.get(rec["key"], -99):
            per_key[rec["key"]] = round(s, 3)
        if s > THRESHOLD:
            hits.append({**rec, "score": round(s, 3)})

    for kname, raw in KEYS.items():
        seq = [v % N for v in raw]
        for tname, idxs in targets:
            runes = gp.indices_to_runes(idxs)
            for sign in (-1, +1):
                for atb in (False, True):
                    ks = ciphers.repeat_key(seq, len(idxs))
                    p = [((N - 1 - c if atb else c) + sign * ks[j]) % N
                         for j, c in enumerate(idxs)]
                    consider(SC.score_norm(gp.indices_to_translit(p)),
                             {"key": kname, "target": tname,
                              "method": f"sign{sign:+d} atb{int(atb)} noint",
                              "plaintext": gp.indices_to_translit(p)[:80]})
                    txt, _ = ciphers.transform_runes(
                        runes, lambda L, k=seq: ciphers.repeat_key(k, L),
                        sign=sign, interrupters=True, atbash=atb)
                    consider(SC.score_norm(txt),
                             {"key": kname, "target": tname,
                              "method": f"sign{sign:+d} atb{int(atb)} INT",
                              "plaintext": txt[:80]})

    out = {"campaign": "VII", "track": "C2", "threshold": THRESHOLD,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_key_best": per_key, "n_hits": len(hits),
           "note": "Short keys; subsumed by exhaustive Vigenere L1-4. Run explicitly "
                   "for the record."}
    json.dump(out, open(os.path.join(HERE, "c2_cuneiform_results.json"), "w"), indent=2)
    print(f"Track C2 — cuneiform/base-60 keys. best score_norm = {best['score']:.3f} "
          f"(threshold {THRESHOLD})")
    for nm, sc in sorted(per_key.items(), key=lambda x: -x[1]):
        print(f"  {nm:22} best {sc}")
    print(f"  hits: {len(hits)}  ->  {'BREAK' if hits else 'null (subsumed, confirmed)'}")
    return out


if __name__ == "__main__":
    run()
