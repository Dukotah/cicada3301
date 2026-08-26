"""Round 19 / C1 -- propagation of the resolved payload into every zero-false-positive
payload-consuming test (PREREG 4.3). Cheap, exact, and re-run on BOTH byte strings so the
comparison is like-for-like.

Covered here:
  * characterize.py's structural battery  (entropy / printability / primality / factors)
  * hash_hunt.py's AN-END page-56 preimage probe, re-implemented over the payload
    representations only -- with the POSITIVE CONTROL hash_hunt.py never had
  * round16/zeroFP E-02A, E-02B and H-03, by reusing zerofp_tests.py itself with only the
    payload bytes swapped, so the false-positive accounting stays identical to Round 16's

The B-05 re-run is a separate, expensive job and lives in b05_rerun.py.

    python3 propagate.py
"""
import hashlib
import json
import os
import sys
from collections import Counter
from math import log2
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LP = os.path.join(ROOT, "liber-primus")
PP = os.path.join(LP, "analysis", "pp49_51")
ZFP = os.path.join(LP, "analysis", "round16", "zeroFP")

AN_END = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
ALGOS = ["sha512", "sha256", "sha384", "sha3_512", "sha3_256",
         "blake2b", "blake2s", "shake_256", "md5", "sha1"]


# ------------------------------------------------------- characterize.py battery
def miller_rabin(n, witnesses=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)):
    if n < 2:
        return False
    for p in witnesses:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in witnesses:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def small_factor(n, limit=100000):
    if n % 2 == 0:
        return 2
    f = 3
    while f < limit:
        if n % f == 0:
            return f
        f += 2
    return None


def entropy(b):
    c = Counter(b)
    return -sum((v / len(b)) * log2(v / len(b)) for v in c.values())


def characterize(data):
    out = {"entropy_bits_per_byte": round(entropy(data), 4),
           "printable_ratio": round(sum(0x20 <= x < 0x7F for x in data) / len(data), 4),
           "distinct_bytes": len(set(data)),
           "interpretations": {}}
    views = [("big-endian", int.from_bytes(data, "big")),
             ("little-endian", int.from_bytes(data, "little")),
             ("reversed-bytes", int.from_bytes(data[::-1], "big")),
             ("high-1024", int.from_bytes(data[:128], "big")),
             ("low-1024", int.from_bytes(data[128:], "big"))]
    for name, n in views:
        out["interpretations"][name] = {
            "bits": n.bit_length(),
            "smallest_factor_under_1e5": small_factor(n),
            "probable_prime": miller_rabin(n),
        }
    return out


# ------------------------------------------- hash_hunt AN-END probe + its control
def digests(b):
    out = {}
    for name in ALGOS:
        h = hashlib.new(name)
        h.update(b)
        out[name] = h.hexdigest(64) if name == "shake_256" else h.hexdigest()
    return out


def payload_reps(data, label):
    yield label, data
    yield label + ":reversed", data[::-1]
    yield label + ":hexstr", data.hex().encode()
    yield label + ":HEXSTR", data.hex().upper().encode()
    yield label + ":+newline", data + b"\n"


def anend_probe(data, label, target=AN_END):
    hits, tested = [], 0
    for lab, b in payload_reps(data, label):
        for alg, dig in digests(b).items():
            tested += 1
            if dig == target:
                hits.append({"rep": lab, "alg": alg, "kind": "FULL"})
            elif dig[:128] == target or target.startswith(dig) or dig.startswith(target[:64]):
                hits.append({"rep": lab, "alg": alg, "kind": "PARTIAL", "digest": dig[:64]})
    return {"tested": tested, "hits": hits}


def anend_control(data, n_noise=10000):
    """hash_hunt.py has no positive control at all. Plant one.

    POSITIVE: make the target the real sha512 of a real payload representation; the matcher
      must fire, and must fire as a FULL match.
    NEGATIVE: 10,000 uniformly random 512-bit targets; the matcher must fire zero times.
    DOCUMENTED BEHAVIOUR (not a failure): a target whose LAST nibble is flipped still fires
      as PARTIAL, because hash_hunt's partial clause `dig.startswith(target[:64])` is a
      deliberate truncated-digest allowance -- it accepts a 256-bit prefix agreement. That
      is by design; it is recorded here so nobody mistakes a PARTIAL for a preimage. A
      target whose FIRST nibble is flipped must NOT fire, and that is the real sharpness
      test."""
    import secrets
    planted = hashlib.sha512(data[::-1]).hexdigest()
    fire = anend_probe(data, "ctrl", target=planted)
    full = [h for h in fire["hits"] if h["kind"] == "FULL"]
    last_off = planted[:-1] + ("0" if planted[-1] != "0" else "1")
    first_off = ("0" if planted[0] != "0" else "1") + planted[1:]
    lastres = anend_probe(data, "ctrl", target=last_off)
    firstres = anend_probe(data, "ctrl", target=first_off)
    noise = 0
    for _ in range(n_noise):
        t = secrets.token_hex(64)
        if anend_probe(data, "ctrl", target=t)["hits"]:
            noise += 1
    ok = bool(full) and not firstres["hits"] and noise == 0
    return {"planted_target": planted[:32] + "...",
            "fires_on_planted": bool(fire["hits"]),
            "fires_FULL_on_planted": bool(full),
            "planted_hits": fire["hits"],
            "fires_on_last_nibble_flipped": bool(lastres["hits"]),
            "last_nibble_hit_kinds": sorted({h["kind"] for h in lastres["hits"]}),
            "fires_on_first_nibble_flipped": bool(firstres["hits"]),
            "false_positives_on_%d_random_targets" % n_noise: noise,
            "verdict": "PASS" if ok else "FAIL"}


# --------------------------------------------------- zeroFP reuse with swapped bytes
def run_zerofp(data, tag):
    """Reuse round16/zeroFP/zerofp_tests.py unmodified, swapping only what
    `canon_256.bin` reads as. Everything else -- windows, bars, gap sequence, cookies --
    is Round 16's, so the false-positive accounting is identical."""
    sys.path.insert(0, ZFP)
    for m in ("zerofp_tests",):
        sys.modules.pop(m, None)
    import zerofp_tests as z
    orig = z.load_bytes

    def patched(path):
        if str(path).replace("\\", "/").endswith("pp49_51/canon_256.bin"):
            return data
        return orig(path)

    z.load_bytes = patched
    out = {"E-02": z.e02_meta_parameters(), "H-03": z.h03_cookies_xor()}
    z.load_bytes = orig
    return out


def main():
    canon = open(os.path.join(PP, "canon_256.bin"), "rb").read()
    decpref = open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read()
    resolved = open(os.path.join(HERE, "payload_resolved.bin"), "rb").read()
    changed = [i for i in range(256) if resolved[i] != canon[i]]

    rep = {"bytes_changed_vs_canon": changed,
           "sha256": {k: hashlib.sha256(v).hexdigest()
                      for k, v in (("canon_256", canon), ("canon_256_decpref", decpref),
                                   ("payload_resolved", resolved))}}
    print("resolved differs from canon_256.bin at %s" % changed)

    print("\n" + "=" * 74)
    print("characterize.py battery, on BOTH payloads")
    print("=" * 74)
    rep["characterize"] = {}
    for name, d in (("canon_256", canon), ("payload_resolved", resolved)):
        c = characterize(d)
        rep["characterize"][name] = c
        print("  %-17s H=%.4f  printable=%.3f  distinct=%d"
              % (name, c["entropy_bits_per_byte"], c["printable_ratio"],
                 c["distinct_bytes"]))
        for k, v in c["interpretations"].items():
            print("     %-15s %4d bits  smallest factor<1e5=%-7s probable prime=%s"
                  % (k, v["bits"], v["smallest_factor_under_1e5"], v["probable_prime"]))

    print("\n" + "=" * 74)
    print("hash_hunt AN-END page-56 preimage probe")
    print("=" * 74)
    ctrl = anend_control(resolved)
    print("  CONTROL (new in C1 -- hash_hunt.py never had one): %s" % ctrl["verdict"])
    for k, v in ctrl.items():
        if k not in ("planted_hits",):
            print("     %-40s %s" % (k, v))
    rep["anend_control"] = ctrl
    rep["anend"] = {}
    for name, d in (("canon_256", canon), ("payload_resolved", resolved)):
        r = anend_probe(d, name)
        rep["anend"][name] = r
        print("  %-17s %d (rep x alg) combinations, hits: %s"
              % (name, r["tested"], r["hits"] or "none"))

    print("\n" + "=" * 74)
    print("round16/zeroFP E-02 + H-03, reusing zerofp_tests.py with the payload swapped")
    print("=" * 74)
    rep["zerofp"] = {}
    for name, d in (("canon_256", canon), ("payload_resolved", resolved)):
        print("\n########## %s ##########" % name)
        rep["zerofp"][name] = run_zerofp(d, name)

    same = {}
    for t in ("E-02", "H-03"):
        a = rep["zerofp"]["canon_256"][t].get("verdict")
        b = rep["zerofp"]["payload_resolved"][t].get("verdict")
        same[t] = {"canon": a, "resolved": b, "unchanged": a == b}
    rep["zerofp_verdict_comparison"] = same
    print("\nverdict comparison: %s" % json.dumps(same))

    json.dump(rep, open(os.path.join(HERE, "out_propagation.json"), "w"), indent=1)
    print("\nwrote out_propagation.json")


if __name__ == "__main__":
    main()
