"""L5 / E-01 - close the Round 16 coverage gap: the pp49-51 payload as an RSA
signature/ciphertext under EVERY published 3301 modulus, in both endiannesses.

Round 16 (`analysis/round16/zeroFP/RESULTS.md`) recorded E-01 as coverage-limited for one
concrete reason: only the 2013 432-bit modulus was on disk, and "the 7A35090F RSA-4096
moduli (the correct size) were not on disk and not fetched". `extract_moduli.py` found them
in corpus/ (including two independent keyserver pulls) and computed their v4 fingerprints
from the packet bytes; `gpg --with-colons --import-options show-only` confirms both.

This script EXTENDS round16's instrument rather than replacing it: the PKCS#1 v1.5 matcher
and the DigestInfo OID table are imported from `zerofp_tests.py` and used unchanged, so a
hit here would be a hit there. What is added is (a) the 4096-bit moduli, (b) little-endian
and block-alignment encodings, (c) an EMSA-PSS structural matcher, (d) the three payload
variants from lane L5's A-04 adjudication, and (e) the mandatory positive/negative controls
that PREREG B.4 requires before any null may be reported.

Zero-false-positive discipline (PREREG B.1/B.5): the verdict is a structural predicate, not
a score. Every matcher is run against genuine signatures produced locally (must fire) and
against random blocks of the same length (must not fire), and both counts are reported.

    python3 e01_extended.py
"""
import hashlib
import json
import os
import secrets
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PP = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51")
Z16 = os.path.join(ROOT, "liber-primus", "analysis", "round16", "zeroFP")
sys.path.insert(0, Z16)
import zerofp_tests as zfp   # noqa: E402  -- round16 instrument, reused unchanged

N_RANDOM_TRIALS = 10000
MIN_FF = 8          # PKCS#1 requires at least 8 padding bytes
MIN_PS_STRICT = 8   # strict PSS tier: at least this many zero bytes before the 0x01


# --------------------------------------------------------------------------- matchers
def mgf1(seed, length, hashfn):
    out = b""
    counter = 0
    while len(out) < length:
        out += hashfn(seed + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]


def match_v15_signature(em):
    """00 01 FF*n(>=8) 00 <DigestInfo>. Returns (tier, detail).
    tier: 'strict' when the DigestInfo DER prefix is a known one, 'loose' when only the
    padding frame is present, None otherwise."""
    ok, desc = zfp.pkcs1_v15_check(em)          # round16's matcher, unchanged
    if not ok:
        return None, desc
    i = 2
    while i < len(em) and em[i] == 0xFF:
        i += 1
    if i - 2 < MIN_FF:
        return None, "only %d FF bytes (<%d)" % (i - 2, MIN_FF)
    tail = em[i + 1:]
    hit, ddesc = zfp.check_digest_info(tail)     # round16's OID table, unchanged
    if hit:
        return "strict", desc + " | " + ddesc
    return "loose", desc


def match_v15_encryption(em):
    """00 02 <>=8 nonzero> 00 <msg>. Type-2 blocks are a much weaker predicate than
    type-1 and their measured false-positive rate is reported separately."""
    if len(em) < 12 or em[0] != 0x00 or em[1] != 0x02:
        return None, "no 00 02 prefix"
    i = 2
    while i < len(em) and em[i] != 0x00:
        i += 1
    if i >= len(em):
        return None, "no 00 terminator"
    if i - 2 < MIN_FF:
        return None, "only %d pad bytes" % (i - 2)
    return "loose", "PKCS#1 v1.5 type 2: %d pad bytes, msg=%s" % (i - 2, em[i + 1:i + 17].hex())


PSS_HASHES = {"SHA-1": hashlib.sha1, "SHA-256": hashlib.sha256,
              "SHA-384": hashlib.sha384, "SHA-512": hashlib.sha512}


def match_pss(em, embits):
    """EMSA-PSS structure: trailer 0xBC, MGF1-unmasked DB = 00*k || 01 || salt.
    Returns (tier, detail); 'strict' requires k >= MIN_PS_STRICT."""
    if not em or em[-1] != 0xBC:
        return None, "no BC trailer"
    emlen = len(em)
    best = (None, "BC trailer but no valid DB under any hash")
    for hname, hf in PSS_HASHES.items():
        hlen = hf().digest_size
        if emlen < hlen + 2:
            continue
        maskeddb = em[:emlen - hlen - 1]
        h = em[emlen - hlen - 1:emlen - 1]
        db = bytes(a ^ b for a, b in zip(maskeddb, mgf1(h, len(maskeddb), hf)))
        # clear the leftmost 8*emLen - emBits bits, per RFC 8017 step 6
        nbits = 8 * emlen - embits
        if nbits:
            db = bytes([db[0] & (0xFF >> nbits)]) + db[1:]
        k = 0
        while k < len(db) and db[k] == 0x00:
            k += 1
        if k < len(db) and db[k] == 0x01:
            detail = "EMSA-PSS %s: %d zero bytes then 0x01, saltlen=%d" % (
                hname, k, len(db) - k - 1)
            if k >= MIN_PS_STRICT:
                return "strict", detail
            best = ("loose", detail)
    return best


MATCHERS = [
    ("pkcs1_v15_signature", lambda em, bits: match_v15_signature(em)),
    ("pkcs1_v15_encryption", lambda em, bits: match_v15_encryption(em)),
    ("emsa_pss", lambda em, bits: match_pss(em, bits)),
]


# --------------------------------------------------------------------------- controls
def controls():
    """PREREG B.4: the matchers must fire on genuine signatures and stay silent on random
    blocks of the same length. Both numbers are reported; a failure of either invalidates
    the null."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    out = {"positive": {}, "negative": {}}
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = key.public_key().public_numbers()
    n, e = pub.n, pub.e
    klen = (n.bit_length() + 7) // 8
    msg = b"cicada 3301 liber primus L5 positive control"

    sig = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
    em = pow(int.from_bytes(sig, "big"), e, n).to_bytes(klen, "big")
    tier, detail = match_v15_signature(em)
    out["positive"]["pkcs1_v15_signature"] = {"fired": tier is not None, "tier": tier,
                                              "detail": detail}

    sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                    salt_length=32), hashes.SHA256())
    embits = n.bit_length() - 1
    emlen = (embits + 7) // 8
    em = pow(int.from_bytes(sig, "big"), e, n).to_bytes(emlen, "big")
    tier, detail = match_pss(em, embits)
    out["positive"]["emsa_pss"] = {"fired": tier is not None, "tier": tier, "detail": detail}

    ct = key.public_key().encrypt(b"hello", padding.PKCS1v15())
    em = pow(int.from_bytes(ct, "big"), key.private_numbers().d, n).to_bytes(klen, "big")
    tier, detail = match_v15_encryption(em)
    out["positive"]["pkcs1_v15_encryption"] = {"fired": tier is not None, "tier": tier,
                                               "detail": detail}

    counts = {name: {"strict": 0, "loose": 0} for name, _ in MATCHERS}
    for _ in range(N_RANDOM_TRIALS):
        blk = secrets.token_bytes(klen)
        for name, fn in MATCHERS:
            tier, _d = fn(blk, 8 * klen - 1)
            if tier:
                counts[name][tier] += 1
    out["negative"] = {"trials": N_RANDOM_TRIALS, "block_len": klen, "hits": counts}
    return out


# --------------------------------------------------------------------------- the sweep
def payload_variants():
    v = {}
    for name, path in (("canon_majority", os.path.join(PP, "canon_256.bin")),
                       ("canon_decimal_preferred", os.path.join(PP, "canon_256_decpref.bin")),
                       ("L5_resolved", os.path.join(HERE, "payload_resolved.bin"))):
        if os.path.exists(path):
            v[name] = open(path, "rb").read()
    return v


def encodings(payload, nbytes):
    """Every (name, integer) the PREREG B.3 encoding list produces for one modulus size."""
    be = payload
    le = payload[::-1]
    out = [("big_endian", int.from_bytes(be, "big")),
           ("little_endian", int.from_bytes(le, "big"))]
    if nbytes > len(payload):
        pad = b"\x00" * (nbytes - len(payload))
        out += [("big_endian_left_aligned", int.from_bytes(be + pad, "big")),
                ("little_endian_left_aligned", int.from_bytes(le + pad, "big"))]
    return out


def main():
    ctrl = controls()
    print("=" * 74)
    print("PREREG B.4 CONTROLS")
    print("=" * 74)
    for k, v in ctrl["positive"].items():
        print("  positive  %-24s fired=%s tier=%s" % (k, v["fired"], v["tier"]))
        print("            %s" % v["detail"][:110])
    print("  negative  %d random %d-byte blocks:" % (ctrl["negative"]["trials"],
                                                     ctrl["negative"]["block_len"]))
    for k, v in ctrl["negative"]["hits"].items():
        print("            %-24s strict=%d loose=%d" % (k, v["strict"], v["loose"]))

    ctrl_ok = (ctrl["positive"]["pkcs1_v15_signature"]["fired"]
               and ctrl["positive"]["emsa_pss"]["fired"]
               and ctrl["negative"]["hits"]["pkcs1_v15_signature"]["strict"] == 0
               and ctrl["negative"]["hits"]["emsa_pss"]["strict"] == 0)
    print("\n  CONTROL VERDICT: %s" % ("PASS - nulls below are trustworthy"
                                       if ctrl_ok else "FAIL - do not trust the null"))

    mod = json.load(open(os.path.join(HERE, "moduli.json")))
    moduli = []
    for k in mod["pgp_moduli"]:
        moduli.append((k["fingerprint"][-16:] + "/" + k["role"], int(k["n_hex"], 16),
                       k["fingerprint"], k["bits"]))
    for k in mod["other_moduli"]:
        moduli.append((k["name"], int(k["n_hex"], 16), None, k["bits"]))

    variants = payload_variants()
    exps = [65537, 3, 17]

    print("\n" + "=" * 74)
    print("E-01 SWEEP")
    print("=" * 74)
    print("  moduli    : " + ", ".join("%s (%d bits)" % (m[0], m[3]) for m in moduli))
    print("  payloads  : " + ", ".join(variants))
    print("  exponents : " + ", ".join(map(str, exps)))

    rows, hits, skipped = [], [], []
    for mname, n, fp, bits in moduli:
        nbytes = (n.bit_length() + 7) // 8
        embits = n.bit_length() - 1
        for pname, pay in variants.items():
            for ename, s in encodings(pay, nbytes):
                if s >= n:
                    skipped.append({"modulus": mname, "payload": pname, "encoding": ename,
                                    "reason": "s >= n (payload does not fit this modulus)"})
                    continue
                for e in exps:
                    em_int = pow(s, e, n)
                    em = em_int.to_bytes(nbytes, "big")
                    empss = em_int.to_bytes((embits + 7) // 8, "big") \
                        if em_int.bit_length() <= embits else None
                    for matcher, fn in MATCHERS:
                        blk = empss if (matcher == "emsa_pss" and empss is not None) else em
                        tier, detail = fn(blk, embits)
                        row = {"modulus": mname, "fingerprint": fp, "bits": bits,
                               "payload": pname, "encoding": ename, "e": e,
                               "matcher": matcher, "tier": tier,
                               "result_head": em[:8].hex()}
                        if tier:
                            row["detail"] = detail
                            hits.append(row)
                        rows.append(row)

    print("\n  tuples evaluated : %d" % len(rows))
    by_reason = {}
    for k in skipped:
        by_reason.setdefault((k["modulus"], k["encoding"]), 0)
        by_reason[(k["modulus"], k["encoding"])] += 1
    print("  encodings skipped: %d  (s >= n, so the payload is not a valid RSA element "
          "in that encoding)" % len(skipped))
    for (m, enc), c in sorted(by_reason.items()):
        print("      %-28s %-28s x%d payload variants" % (m, enc, c))
    if hits:
        print("\n  *** STRUCTURAL MATCHES ***")
        for h in hits:
            print("   %(matcher)s [%(tier)s] %(modulus)s e=%(e)d %(payload)s/%(encoding)s"
                  % h)
            print("      %s" % h.get("detail", "")[:110])
    else:
        print("\n  NULL: no structural match on any tuple.")

    strict_hits = [h for h in hits if h["tier"] == "strict"]
    verdict = ("HIT" if strict_hits else
               ("NULL" if ctrl_ok else "NULL (UNTRUSTED - control failed)"))
    out = {"test": "E-01 (Round 18 L5 extension of round16/zeroFP)",
           "verdict": verdict,
           "controls": ctrl,
           "control_verdict": "PASS" if ctrl_ok else "FAIL",
           "moduli": [{"name": m[0], "fingerprint": m[2], "bits": m[3]} for m in moduli],
           "payload_variants": sorted(variants),
           "exponents": exps,
           "matchers": [m[0] for m in MATCHERS],
           "tuples_evaluated": len(rows),
           "tuples_skipped": skipped,
           "hits": hits,
           "rows": rows}
    with open(os.path.join(HERE, "e01_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\n  VERDICT: %s   -> e01_results.json" % verdict)


if __name__ == "__main__":
    main()
