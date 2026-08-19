"""Campaign VII — Track A2 refined: pp49-51 token tables under ALL candidate bases.

scream314 decoded the two-char tokens as base-60. The uncovering-cicada wiki
(via Campaign VI) claims base-59 is the meaningful reading -- "the only permutation
whose decoded values all fall in 0-255." We test that directly: re-decode the raw
tokens (alphabet 0-9 A-Z a-z, value = hi*B + lo) for B in {59,60,62,64}, report
which bases keep every value in 0-255, and test each resulting byte stream as a
mod-29 additive keystream against the runic pages (full variant sweep).

Raw tokens are lifted verbatim from sources/community/scream314_liber_primus.md.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, ciphers, score as _score  # noqa
from run_stats import load_pages  # noqa

N = gp.N
SC = _score.default()
THRESHOLD = -5.2
SRC = os.path.join(HERE, "..", "..", "..", "sources", "community",
                   "scream314_liber_primus.md")

ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
VAL = {c: i for i, c in enumerate(ALPHA)}


def extract_tokens():
    txt = open(SRC, encoding="utf-8").read()
    out = {}
    for h, name in [("## 66.jpg - 49.jpg", "p49"),
                    ("## 67.jpg - 50.jpg", "p50"),
                    ("## 68.jpg - 51.jpg", "p51")]:
        i = txt.index(h)
        j = txt.index("base60", i)
        block = txt[j:txt.index("dec", j)].split("base60", 1)[1]
        out[name] = re.findall(r"\b([0-9A-Za-z]{2})\b", block)
    return out


def decode(tokens, base):
    return [VAL[t[0]] * base + VAL[t[1]] for t in tokens]


def run():
    tok = extract_tokens()
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    base_report = {}
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

    for base in (59, 60, 62, 64):
        streams = {}
        allvals = []
        for pg in ("p49", "p50", "p51"):
            vals = decode(tok[pg], base)
            streams[pg] = vals
            allvals += vals
        in_range = all(0 <= v <= 255 for v in allvals)
        base_report[base] = {"all_in_0_255": in_range,
                             "max": max(allvals), "min": min(allvals)}
        # build candidate keys for this base
        cand = {f"b{base}_p49": streams["p49"],
                f"b{base}_p51": streams["p51"],
                f"b{base}_all": streams["p49"] + streams["p50"] + streams["p51"],
                f"b{base}_49+51": streams["p49"] + streams["p51"]}
        for kname, raw in cand.items():
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

    hits.sort(key=lambda h: -h["score"])
    out = {"campaign": "VII", "track": "A2-altbase", "threshold": THRESHOLD,
           "base_report": base_report, "best_score": round(best["score"], 3),
           "best": best["rec"], "per_key_best": per_key,
           "n_hits": len(hits), "hits": hits[:20]}
    json.dump(out, open(os.path.join(HERE, "a2_altbase_results.json"), "w"), indent=2)
    print("Base viability (all values in 0-255?):")
    for b, r in base_report.items():
        print(f"  base{b}: {r}")
    print(f"\nBest score_norm = {best['score']:.3f} (English ~ -4.0..-4.4, noise ~ -7.4)")
    for nm, sc in sorted(per_key.items(), key=lambda x: -x[1])[:6]:
        print(f"  {nm:14} best {sc}")
    print(f"  hits over threshold {THRESHOLD}: {len(hits)}")
    r = best["rec"]
    print(f"  overall best: {r['key']} {r['target']} {r['method']}\n    {r['plaintext']}")
    return out


if __name__ == "__main__":
    run()
