"""Campaign VII — Track B4: the page-56 512-bit hash as a key / KDF seed.

Page 56 (AN END region) states "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT
HASHES TO" the 512-bit value below. It points at an unfound page, but it is also
concrete structured data never tested as key material. We expand it several ways
into a mod-29 additive keystream and run the full variant sweep over the runes.

    36367763ab73783c...132c2a8b4   (128 hex = 64 bytes)

Keystreams:
  hash_bytes      : the 64 bytes, mod 29, repeated
  hash_hexdigits  : the 128 hex nibbles (0-15), mod 29, repeated
  shake256        : SHAKE-256(hash) expanded to book length, mod 29
  sha512_chain    : h, sha512(h), sha512^2(h), ... concatenated, mod 29
  blake2b_chain   : same with BLAKE2b (Cicada used BLAKE-512-shaped hashes)
Any runic score_norm > -5.2 is a hit (English ~ -4.0..-4.4; noise ~ -7.4).
"""
import hashlib
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

HEX = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
       "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
HBYTES = bytes.fromhex(HEX)


def chain(hfn, need):
    out, cur = [], HBYTES
    while len(out) < need:
        cur = hfn(cur).digest()
        out.extend(cur)
    return out[:need]


def build(need):
    ks = {}
    ks["hash_bytes"] = [b % N for b in HBYTES]
    ks["hash_hexdigits"] = [int(c, 16) % N for c in HEX]
    ks["shake256"] = [b % N for b in hashlib.shake_256(HBYTES).digest(need)]
    ks["sha512_chain"] = [b % N for b in chain(hashlib.sha512, need)]
    ks["blake2b_chain"] = [b % N for b in chain(hashlib.blake2b, need)]
    return ks


def run():
    pages = load_pages()
    unsolved = pages[:-2]
    whole = [i for pg in unsolved for i in pg]
    targets = [("p%02d" % pi, pg) for pi, pg in enumerate(unsolved)]
    targets.append(("WHOLE", whole))
    ks_all = build(len(whole) + 8)

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

    for kname, seq in ks_all.items():
        for tname, idxs in targets:
            runes = gp.indices_to_runes(idxs)
            for sign in (-1, +1):
                for atb in (False, True):
                    kk = ciphers.repeat_key(seq, len(idxs))
                    p = [((N - 1 - c if atb else c) + sign * kk[j]) % N
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
    out = {"campaign": "VII", "track": "B4", "hash": HEX, "threshold": THRESHOLD,
           "best_score": round(best["score"], 3), "best": best["rec"],
           "per_key_best": per_key, "n_hits": len(hits), "hits": hits[:20]}
    json.dump(out, open(os.path.join(HERE, "b4_hash_kdf_results.json"), "w"), indent=2)
    print(f"Track B4 — page-56 hash as key. best score_norm = {best['score']:.3f} "
          f"(English ~ -4.0..-4.4, noise ~ -7.4)")
    for nm, sc in sorted(per_key.items(), key=lambda x: -x[1]):
        print(f"  {nm:16} best {sc}")
    print(f"  hits over threshold {THRESHOLD}: {len(hits)}")
    r = best["rec"]
    print(f"  overall best: {r['key']} {r['target']} {r['method']}\n    {r['plaintext']}")
    return out


if __name__ == "__main__":
    run()
