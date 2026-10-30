"""Campaign VII — Track A2/B2: the pp49-51 base-60 token tables as a key/pad.

DISCOVERY (2026-07-07): scream314's catalog shows relikd pages 49/50/51 are NOT
runic prose but base-60 two-char token tables, already decoded to decimal bytes
(0-255). Our rig's %-split page set only contains *runic* pages, so these token
pages were EXCLUDED and never tested. The three pages total EXACTLY 256 bytes
(80 + 104 + 72) with values across the full 0-255 range -- suggestive of a pad,
an S-box, or a 256-entry substitution table. This is Roadmap Track A2/B2.

Tests:
  1. Structure: are the 256 bytes a permutation of 0..255? distinct-count, hist.
  2. As an additive keystream (mod 29) against the runic pages -- per page, whole
     book, each token page alone and concatenated, both byte-orders, +/- sign,
     +/- atbash, interrupter-aware.  (Track A2: token data == the missing key.)
  3. XOR combinations among the three token pages, then mod-29 keystream.
     (Track B2 shape: XOR leftover data, look for structure.)
Any runic score_norm > -5.2 is a hit (English ~ -4.0..-4.4; noise ~ -7.4).
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

P49 = [203,231,167,186,97,237,126,183,92,249,156,222,247,4,183,212,121,202,15,33,
       102,137,59,87,109,224,173,25,150,66,141,133,115,114,197,39,54,80,133,5,80,
       84,28,73,230,81,199,76,253,16,21,59,86,171,156,80,254,118,146,69,106,196,
       124,51,122,255,25,192,199,73,169,108,164,79,205,177,114,144,46,82]
P50 = [142,58,201,193,173,28,111,65,211,220,198,49,236,84,56,35,222,150,72,34,83,
       229,32,206,122,63,31,218,14,184,32,115,73,143,197,247,54,171,35,184,42,237,
       86,54,13,20,163,193,201,179,86,120,169,141,72,171,10,129,233,13,245,46,160,
       152,125,210,92,173,246,174,153,189,231,33,14,112,52,251,249,248,233,217,192,
       82,105,18,250,248,240,228,254,54,148,117,209,44,235,131,166,175,144,40,141,81]
P51 = [128,156,19,81,38,192,170,33,0,155,159,89,176,115,105,21,110,74,209,68,194,76,
       127,21,57,175,6,61,70,150,251,5,142,219,148,59,58,52,51,151,68,52,73,249,144,
       0,117,175,106,234,196,121,238,58,129,173,144,141,42,214,22,56,224,192,113,158,
       172,230,180,36,189,80]


def structure_report():
    allb = P49 + P50 + P51
    d = {"len_p49": len(P49), "len_p50": len(P50), "len_p51": len(P51),
         "total": len(allb), "distinct": len(set(allb)),
         "is_perm_0_255": (len(allb) == 256 and set(allb) == set(range(256))),
         "min": min(allb), "max": max(allb)}
    # near-permutation? how many of 0..255 are covered
    d["coverage_0_255"] = len(set(allb) & set(range(256)))
    d["duplicates"] = sorted([v for v in set(allb) if allb.count(v) > 1])
    return d, allb


def keystreams():
    """Named integer streams to try as mod-29 additive keys."""
    ks = {}
    for nm, b in [("p49", P49), ("p50", P50), ("p51", P51),
                  ("p49+50+51", P49 + P50 + P51),
                  ("p49+51", P49 + P51),               # drop the 'wrong!!!' p50
                  ("p51+50+49_rev", (P49 + P50 + P51)[::-1])]:
        ks[nm] = [x % N for x in b]
    # XOR combinations (Track B2 shape). Align on min length.
    def xzip(a, b):
        m = min(len(a), len(b))
        return [(a[i] ^ b[i]) for i in range(m)]
    ks["xor_49_51"] = [x % N for x in xzip(P49, P51)]
    ks["xor_49_50"] = [x % N for x in xzip(P49, P50)]
    ks["xor_50_51"] = [x % N for x in xzip(P50, P51)]
    return ks


def run():
    struct, allb = structure_report()
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

    for kname, seq in keystreams().items():
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
    out = {"campaign": "VII", "track": "A2/B2",
           "discovery": "relikd 49/50/51 are base-60 token tables = 256 bytes, "
                        "excluded from rig; tested here as key/pad",
           "structure": struct, "threshold": THRESHOLD,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_key_best": per_key, "n_hits": len(hits), "hits": hits[:20]}
    json.dump(out, open(os.path.join(HERE, "a2_tokenpad_results.json"), "w"), indent=2)
    print("Structure:", json.dumps(struct))
    print(f"\nTrack A2/B2 — token pad as key. best score_norm = {best['score']:.3f} "
          f"(English ~ -4.0..-4.4, noise ~ -7.4)")
    for nm, sc in sorted(per_key.items(), key=lambda x: -x[1]):
        print(f"  {nm:16} best {sc}")
    print(f"  hits over threshold {THRESHOLD}: {len(hits)}")
    r = best["rec"]
    print(f"  overall best: {r['key']} {r['target']} {r['method']}\n    {r['plaintext']}")
    return out


if __name__ == "__main__":
    run()
