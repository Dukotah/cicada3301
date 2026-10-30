"""Campaign VII — Track B3: the HINTS-NEVER-USED numerics as Gematria keystreams.

Source: krisyotam/cicada3301 `HINTS-NEVER-USED.md` (vendored at
sources/community/krisyotam_HINTS-NEVER-USED.md). These are numeric artifacts
Cicada embedded in 2012-2015 messages that the community catalogued but never
tried as keys against the runes. Campaign VI flagged them (lead #4). Numeric keys
are the class the doublet-mechanism proof leaves open (MASTER-ROADMAP §1).

Streams tested (each mod 29, both as a repeating key and truncated-if-longer):
  - PS digits         : the 2012 end-message P.S. digit string, 3 readings
                        (single decimal digits; 2-digit groups; big-int base-29)
  - missing primes    : the telnet 'primes' gap (all primes 73..1223) mod 29
  - missing gaps      : first-differences of that missing-prime list mod 29
  - trailing 2012/13/14/15 : the whitespace-count sequences

Full variant sweep per stream: sign +/-, +/-atbash, interrupter-aware & not,
per-page + whole-book. Any score_norm > -5.2 is a hit (English ~ -4.0..-4.4).
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

PS = ("1041279065891998535982789873959431895640"
      "442510695567564373922695237268242385295908173"
      "9834390370374475764863415203423499357108713631")


def _sieve(lo, hi):
    primes = []
    for c in range(2, hi + 1):
        if all(c % p for p in primes if p * p <= c):
            primes.append(c)
    return [p for p in primes if lo <= p <= hi]


def build_streams():
    s = {}
    # P.S. digit string, three readings
    s["ps_digits"] = [int(c) % N for c in PS]
    s["ps_2dig"] = [int(PS[i:i + 2]) % N for i in range(0, len(PS) - 1, 2)]
    big = int(PS)
    b29 = []
    while big:
        b29.append(big % N)
        big //= N
    s["ps_base29"] = b29[::-1]
    # telnet missing primes (between 71 and 1229 -> 73..1223)
    miss = _sieve(73, 1223)
    s["missing_primes"] = [p % N for p in miss]
    s["missing_gaps"] = [(miss[i + 1] - miss[i]) % N for i in range(len(miss) - 1)]
    # trailing-space whitespace sequences
    s["trail_2012"] = [x % N for x in [0, 2, 3, 5, 7, 11, 13, 1, 1, 2, 11, 0, 7, 0, 5, 0, 3, 2]]
    s["trail_2013"] = [x % N for x in [5, 3, 2, 2, 3, 5]]
    s["trail_2014"] = [x % N for x in [2, 3, 5, 7, 11, 13, 17, 23, 29, 31, 37]]
    s["trail_2015"] = [x % N for x in [5, 3, 2, 5, 7]]
    return s


def run():
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    streams = build_streams()

    best = {"score": -99.0, "rec": None}
    per_stream = {}
    hits = []

    def consider(s, rec):
        if s > best["score"]:
            best.update(score=s, rec=rec)
        nm = rec["stream"]
        if s > per_stream.get(nm, -99):
            per_stream[nm] = round(s, 3)
        if s > THRESHOLD:
            hits.append({**rec, "score": round(s, 3)})

    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    for sname, seq in streams.items():
        if not seq:
            continue
        for tname, idxs in targets:
            runes = gp.indices_to_runes(idxs)
            for sign in (-1, +1):
                for atb in (False, True):
                    ks = ciphers.repeat_key(seq, len(idxs))
                    p = [((N - 1 - c if atb else c) + sign * ks[j]) % N
                         for j, c in enumerate(idxs)]
                    consider(SC.score_norm(gp.indices_to_translit(p)),
                             {"stream": sname, "target": tname,
                              "method": f"sign{sign:+d} atb{int(atb)} noint",
                              "plaintext": gp.indices_to_translit(p)[:80]})
                    txt, _ = ciphers.transform_runes(
                        runes, lambda L, k=seq: ciphers.repeat_key(k, L),
                        sign=sign, interrupters=True, atbash=atb)
                    consider(SC.score_norm(txt),
                             {"stream": sname, "target": tname,
                              "method": f"sign{sign:+d} atb{int(atb)} INT",
                              "plaintext": txt[:80]})

    hits.sort(key=lambda h: -h["score"])
    out = {"campaign": "VII", "track": "B3", "threshold": THRESHOLD,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_stream_best": per_stream, "n_hits": len(hits), "hits": hits[:20]}
    json.dump(out, open(os.path.join(HERE, "b3_hints_results.json"), "w"), indent=2)
    print(f"Track B3 — HINTS numerics. best score_norm = {best['score']:.3f} "
          f"(English ~ -4.0..-4.4, noise ~ -7.4)")
    for nm, sc in sorted(per_stream.items(), key=lambda x: -x[1]):
        print(f"  {nm:16} best {sc}")
    print(f"  hits over threshold {THRESHOLD}: {len(hits)}")
    r = best["rec"]
    print(f"  overall best: {r['stream']} {r['target']} {r['method']}\n    {r['plaintext']}")
    return out


if __name__ == "__main__":
    run()
