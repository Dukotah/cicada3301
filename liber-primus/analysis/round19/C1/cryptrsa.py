"""Round 19 / C1 -- what does Crypt::RSA 1.99 ES::OAEP ACTUALLY emit?

R1 found 3301 naming their encryption library in a SIGNED, verified message, and C3
confirmed the signature: the armour headers say

    Version: 1.99
    Scheme: Crypt::RSA::ES::OAEP

So E-01 must test the author's declared scheme, not only OpenSSL-shaped PKCS#1. The
question is what that scheme's encoded block looks like on the wire.

We do NOT have to reconstruct that from memory or from a modern library, because the corpus
contains the 2013/2014 puzzle key's PRIME FACTORS:

    corpus/E-tooling/vendor/ctvrty-rozmer__bruh/perl-rsa-decrypt.pl
    corpus/A-primary-artifacts/cijhho123/2014/additional docs/scripts/Program to decrypt RSA message in perl.txt

both hard-code p and q, and p*q is exactly the published 432-bit modulus. That means 3301's
own ES::OAEP ciphertext can be decrypted here and the encoded message read off directly.
The layout below is therefore MEASURED ON A HELD ARTIFACT -- 3301's own ciphertext, produced
by the very library version in question -- which is the strongest positive control this test
could have.

    python3 cryptrsa.py
"""
import base64
import hashlib
import json
import os
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

P = 97513779050322159297664671238670850085661086043266591739338007321
Q = 77506098606928780021829964781695212837195959082370473820509360759
E = 65537

MSG_FILES = [
    "corpus/A-primary-artifacts/pgp/messages/2014-01-rsa-oaep-challenge.asc",
    "corpus/A-primary-artifacts/ibotpeaches/messages/2014/welcome.asc",
    "corpus/A-primary-artifacts/ibotpeaches/messages/2012/this-message-will-only-be-displayed.asc",
    "liber-primus/analysis/armada20/pgp_welcome.txt",
]
SHA1_EMPTY = hashlib.sha1(b"").hexdigest()   # lHash for the default empty label P


def mgf1(seed, length, hf=hashlib.sha1):
    out, c = b"", 0
    while len(out) < length:
        out += hf(seed + c.to_bytes(4, "big")).digest()
        c += 1
    return out[:length]


def unarmour(text):
    """Convert::ASCII::Armour container -> {field: bytes}. Returns (fields, raw, declared)."""
    lines, inblk = [], False
    for ln in text.splitlines():
        # clearsigned bodies dash-escape lines as "- <line>"; strip exactly that prefix,
        # never a character class (lstrip("- ") would eat the armour's own dashes).
        s = (ln[2:] if ln.startswith("- ") else ln).rstrip()
        if s.startswith("-----BEGIN COMPRESSED RSA"):
            inblk = True
            continue
        if s.startswith("-----END COMPRESSED RSA"):
            break
        if not inblk:
            continue
        if not s or ":" in s or s.startswith("="):
            continue
        lines.append(s)
    if not lines:
        return None
    raw = zlib.decompress(base64.b64decode("".join(lines)))
    i = raw.index(b"\x00")
    nlen = int(raw[:i])
    j = raw.index(b"\x00", i + 1)
    vlen = int(raw[i + 1:j])
    rest = raw[j + 1:]
    name = rest[:nlen].decode()
    # NO separator byte: the container is  len(name)NUL len(value)NUL name value.
    # (The "," that looks like a separator in the 2014 message is 0x2c, the first byte
    # of the ciphertext itself. Taking it as a delimiter is what makes the value come out
    # one byte short of its declared length -- and the armour's own MD5 checksum, which
    # matches the compressed blob exactly, proves nothing was lost in transcription.)
    val = rest[nlen:]
    return {"name": name, "declared_name_len": nlen, "declared_value_len": vlen,
            "actual_value_len": len(val), "value": val, "raw_len": len(raw)}


def oaep_decode(em, hlen=20):
    """Crypt::RSA::ES::OAEP decode, per the layout this script MEASURES below:
       EM = maskedSeed(hLen) || maskedDB, with NO leading 0x00 octet (emLen = k-1).
       DB = lHash(hLen) || PS(0x00*) || 0x01 || M."""
    if len(em) < 2 * hlen + 1:
        return None
    mseed, mdb = em[:hlen], em[hlen:]
    seed = bytes(a ^ b for a, b in zip(mseed, mgf1(mdb, hlen)))
    db = bytes(a ^ b for a, b in zip(mdb, mgf1(seed, len(mdb))))
    lhash = db[:hlen].hex()
    rest = db[hlen:]
    k = 0
    while k < len(rest) and rest[k] == 0x00:
        k += 1
    ok = (lhash == SHA1_EMPTY) and k < len(rest) and rest[k] == 0x01
    return {"lhash": lhash, "lhash_ok": lhash == SHA1_EMPTY, "ps_zeros": k,
            "delimiter_ok": k < len(rest) and rest[k] == 0x01,
            "message": rest[k + 1:] if ok else None, "structure_ok": ok}


def main():
    n = P * Q
    k = (n.bit_length() + 7) // 8
    phi = (P - 1) * (Q - 1)
    lam = phi // __import__("math").gcd(P - 1, Q - 1)
    rep = {"n_bits": n.bit_length(), "k_bytes": k,
           "n_equals_published_2013_modulus": None, "messages": {}}

    pub = int("7557912574608535164426718292058021255641310207187633095795069445700059"
              "210248050757270234679993673844203148013173091173786572116639")
    rep["n_equals_published_2013_modulus"] = (n == pub)
    print("p,q from the corpus decrypt scripts -> n is %d bits, k=%d bytes; "
          "n == published 2013 modulus: %s" % (n.bit_length(), k, n == pub))

    for dname, d in (("d_mod_phi", pow(E, -1, phi)), ("d_mod_lambda", pow(E, -1, lam))):
        rep.setdefault("private_exponents", {})[dname] = d.bit_length()

    for rel in MSG_FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8", errors="ignore").read()
        try:
            a = unarmour(text)
        except Exception as ex:
            rep["messages"][rel] = {"error": str(ex)}
            continue
        if not a:
            continue
        print("\n%s" % rel)
        print("  container: field %r  declared value len %d  actual %d  (k=%d -> %.2f blocks)"
              % (a["name"], a["declared_value_len"], a["actual_value_len"], k,
                 a["declared_value_len"] / k))
        entry = {kk: a[kk] for kk in ("name", "declared_name_len", "declared_value_len",
                                      "actual_value_len", "raw_len")}
        entry["value_sha256"] = hashlib.sha256(a["value"]).hexdigest()

        # The 2014 container declares 162 = 3*54 but carries 161 bytes: exactly one octet
        # short. Try the three repairs and let the OAEP structure decide which is right.
        cands = {"as_is": a["value"]}
        if a["actual_value_len"] == a["declared_value_len"] - 1:
            cands["prepend_00"] = b"\x00" + a["value"]
            cands["append_00"] = a["value"] + b"\x00"
        entry["blocks"] = {}
        for cname, buf in cands.items():
            if len(buf) % k:
                entry["blocks"][cname] = {"skip": "len %d not a multiple of k=%d"
                                                  % (len(buf), k)}
                continue
            res = []
            for bi in range(len(buf) // k):
                c = int.from_bytes(buf[bi * k:(bi + 1) * k], "big")
                if c >= n:
                    res.append({"block": bi, "error": "c >= n"})
                    continue
                for dname, d in (("d_mod_phi", pow(E, -1, phi)),
                                 ("d_mod_lambda", pow(E, -1, lam))):
                    m = pow(c, d, n)
                    for emlen in (k - 1, k):
                        em = m.to_bytes(emlen, "big") if m.bit_length() <= 8 * emlen else None
                        if em is None:
                            continue
                        dec = oaep_decode(em)
                        if dec and dec["structure_ok"]:
                            res.append({"block": bi, "d": dname, "emLen": emlen,
                                        "emLen_rel_k": "k-1" if emlen == k - 1 else "k",
                                        "lhash": dec["lhash"], "ps_zeros": dec["ps_zeros"],
                                        "msg_hex": dec["message"].hex(),
                                        "msg_text": dec["message"].decode(
                                            "utf-8", "replace")})
                            break
                    else:
                        continue
                    break
                else:
                    res.append({"block": bi, "structure_ok": False})
            entry["blocks"][cname] = res
            good = [r for r in res if r.get("msg_hex")]
            print("    %-12s %d block(s): %d decode with valid OAEP structure"
                  % (cname, len(buf) // k, len(good)))
            for r in good:
                print("       block %d  d=%s emLen=%s  lHash=SHA1('')  PS zeros=%d  "
                      "msg=%r" % (r["block"], r["d"], r["emLen_rel_k"], r["ps_zeros"],
                                  r["msg_text"]))
        rep["messages"][rel] = entry

    json.dump(rep, open(os.path.join(HERE, "out_cryptrsa.json"), "w"), indent=1)
    print("\nwrote out_cryptrsa.json")


if __name__ == "__main__":
    main()
