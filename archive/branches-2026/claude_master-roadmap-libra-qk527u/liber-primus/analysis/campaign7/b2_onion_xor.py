"""Campaign VII — Track B2: pp49-51 token pad XOR the 2014 onion-trail hex.

THE operation a wiki author explicitly proposed and nobody ran (Campaign VI lead
#2): "XORing the data ... probably the strings of hex from the 2nd, 3rd and 4th
onion pages of the 2014 trail, which have never been used for anything yet."

We now have both sides vendored:
  - token pad = pp49-51 base-60 bytes (80+104+72 = EXACTLY 256 bytes)
  - onion2 cu343l33nqaekrnw.onion  "Patience is a virtue"  256 bytes
  - onion3 (grew over time)         "1033"                  256 bytes
  - onion4 avowyfgl5lkzfj3n.onion   "3301"                  256 bytes
All four are 256 bytes -> clean full-length XOR alignment (suggestive of an
intended one-time-pad pairing).

Tests:
  A. Forensics on each XOR result (token_all XOR onion_k): printable-ASCII ratio,
     Shannon entropy, leading magic bytes. A real payload should drop entropy /
     become printable / show structure.
  B. Each XOR result as a mod-29 additive keystream over the runic pages.
  C. The onion hex ALONE as a mod-29 keystream (also never tested as a key).
Any runic score_norm > -5.2 is a hit (English ~ -4.0..-4.4; noise ~ -7.4).
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, os.path.join(HERE, ".."))
from lp import gematria as gp, ciphers, score as _score  # noqa
from run_stats import load_pages  # noqa
from campaign7.a2_tokenpad import P49, P50, P51  # reuse the vendored byte tables

N = gp.N
SC = _score.default()
THRESHOLD = -5.2
Y2014 = os.path.join(HERE, "..", "..", "..", "sources", "community", "scream314_2014.md")

TOKEN = P49 + P50 + P51  # 256 bytes


def onion_hex():
    t = open(Y2014, encoding="utf-8").read()
    out = {}
    for label, anchor in [("onion2", "634292ba49fe"), ("onion3", "87de5b7fa26ab8"),
                          ("onion4", "bf1d5574ca36")]:
        i = t.find(anchor)
        h = re.match(r"[0-9a-f]+", t[i:]).group(0)[:512]
        out[label] = [int(h[j:j + 2], 16) for j in range(0, len(h), 2)]
    return out


def entropy(b):
    if not b:
        return 0.0
    counts = [b.count(v) for v in set(b)]
    tot = len(b)
    return -sum((c / tot) * math.log2(c / tot) for c in counts)


def printable_ratio(b):
    return sum(1 for v in b if 32 <= v <= 126) / len(b)


def forensics(b):
    return {"entropy_bits": round(entropy(b), 3),
            "printable_ratio": round(printable_ratio(b), 3),
            "head_hex": "".join(f"{v:02x}" for v in b[:8]),
            "distinct": len(set(b))}


def run():
    onions = onion_hex()
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))

    # A. XOR forensics
    xor_forensics = {"token_pad": forensics(TOKEN)}
    keys = {}  # name -> byte stream to try as mod-29 key
    for name, ob in onions.items():
        xor = [TOKEN[i] ^ ob[i] for i in range(256)]
        xor_forensics[f"token^{name}"] = forensics(xor)
        keys[f"token^{name}"] = xor
        keys[name] = ob  # onion alone as key
    # all three onions XOR'd, and token ^ (o2^o3^o4)
    o234 = [onions["onion2"][i] ^ onions["onion3"][i] ^ onions["onion4"][i] for i in range(256)]
    xor_forensics["onion2^3^4"] = forensics(o234)
    keys["onion2^3^4"] = o234
    keys["token^onion2^3^4"] = [TOKEN[i] ^ o234[i] for i in range(256)]

    # B/C. test each byte stream as mod-29 additive key over the runes
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

    for kname, raw in keys.items():
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
    out = {"campaign": "VII", "track": "B2",
           "operation": "pp49-51 token pad XOR 2014 onion-trail hex (never run)",
           "xor_forensics": xor_forensics, "threshold": THRESHOLD,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_key_best": per_key, "n_hits": len(hits), "hits": hits[:20]}
    json.dump(out, open(os.path.join(HERE, "b2_onion_xor_results.json"), "w"), indent=2)

    print("XOR forensics (a real payload should drop entropy / rise printable):")
    for nm, f in xor_forensics.items():
        print(f"  {nm:18} entropy={f['entropy_bits']:>5} bits  "
              f"printable={f['printable_ratio']:>4}  distinct={f['distinct']}")
    print(f"\nTrack B2 — best score_norm = {best['score']:.3f} (English ~ -4.0..-4.4)")
    for nm, sc in sorted(per_key.items(), key=lambda x: -x[1])[:6]:
        print(f"  {nm:18} best {sc}")
    print(f"  hits over threshold {THRESHOLD}: {len(hits)}")
    r = best["rec"]
    print(f"  overall best: {r['key']} {r['target']} {r['method']}\n    {r['plaintext']}")
    return out


if __name__ == "__main__":
    run()
