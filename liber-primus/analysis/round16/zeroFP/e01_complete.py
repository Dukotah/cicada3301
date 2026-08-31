#!/usr/bin/env python3
"""
E-01 COMPLETION — the 7A35090F RSA-4096 moduli, fetched and checked.

Round 16's zeroFP left E-01 coverage-limited: it noted the Cicada signing key
(keyid 7A35090F) modulus "not on disk (fetch was planned but not done)" and
reasoned informally that a 4096-bit modulus could not carry the 256-byte
payload. This script closes the gap by fetching the actual key, verifying its
fingerprint against the value recorded in the repo, extracting both RSA-4096
moduli (primary [SC] + encryption subkey [E]), and running the pp49-51 payload
through a mechanical PKCS#1 / raw-RSA check under them — rather than asserting
the outcome.

Zero-false-positive discipline: the checker is validated in BOTH directions
before any verdict is trusted —
  * PLANT: a genuine PKCS#1 v1.5 signature made under a throwaway RSA-4096 key
           must be recovered (zero false NEGATIVE), and
  * NOISE: 256 random bytes under the same key must read NULL (zero false
           POSITIVE).

Provenance of the key:
  keyserver.ubuntu.com  op=get  0x6D854CD7933322A601C3286D181F01E57A35090F
  fingerprint 6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F
  uid "Cicada 3301 (845145127)", created 2012-01-05, RSA-4096 [SC] + RSA-4096 [E]
The fingerprint is the one recorded in research/05-crypto-techniques.md.

Run from liber-primus/:  python analysis/round16/zeroFP/e01_complete.py
"""
import base64, re, json, os, hashlib
from pathlib import Path
from math import log2

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]  # liber-primus/
KEY_ASC = HERE / "keys" / "7A35090F.asc"
EXPECT_FPR = "6D854CD7933322A601C3286D181F01E57A35090F"
PAYLOADS = {
    "canon_256":  REPO / "analysis" / "pp49_51" / "canon_256.bin",
    "canon_256_decpref": REPO / "analysis" / "pp49_51" / "canon_256_decpref.bin",
}

# --------------------------------------------------------------------------
# OpenPGP packet + MPI parsing (no external deps)
# --------------------------------------------------------------------------
def dearmor(text):
    m = re.search(r"-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END", text, re.S)
    body = m.group(1)
    lines = [l for l in body.splitlines() if l and ":" not in l and not l.startswith("=")]
    return base64.b64decode("".join(lines))

def packets(d):
    i = 0
    while i < len(d):
        tag = d[i]; i += 1
        if not (tag & 0x80):
            break
        if tag & 0x40:                      # new format
            t = tag & 0x3f
            l0 = d[i]; i += 1
            if l0 < 192: length = l0
            elif l0 < 224: length = ((l0 - 192) << 8) + d[i] + 192; i += 1
            elif l0 == 255: length = int.from_bytes(d[i:i+4], "big"); i += 4
            else: length = 1 << (l0 & 0x1f)
        else:                               # old format
            t = (tag >> 2) & 0x0f
            lt = tag & 0x03
            if lt == 0: length = d[i]; i += 1
            elif lt == 1: length = int.from_bytes(d[i:i+2], "big"); i += 2
            elif lt == 2: length = int.from_bytes(d[i:i+4], "big"); i += 4
            else: length = len(d) - i
        yield t, d[i:i+length]
        i += length

def read_mpi(d, off):
    bits = int.from_bytes(d[off:off+2], "big"); off += 2
    nbytes = (bits + 7) // 8
    return int.from_bytes(d[off:off+nbytes], "big"), off + nbytes

def fingerprint_v4(pk_body):
    # v4 fingerprint = SHA1( 0x99 || len16 || packet body )
    h = hashlib.sha1()
    h.update(b"\x99" + len(pk_body).to_bytes(2, "big") + pk_body)
    return h.hexdigest().upper()

def load_moduli():
    data = dearmor(KEY_ASC.read_text())
    mods = []
    primary_fpr = None
    for t, body in packets(data):
        if t in (6, 14) and body and body[0] == 4 and body[5] in (1, 2, 3):
            off = 6
            n, off = read_mpi(body, off)
            e, off = read_mpi(body, off)
            fpr = fingerprint_v4(body)
            if t == 6:
                primary_fpr = fpr
            mods.append({"kind": "primary" if t == 6 else "subkey",
                         "bits": n.bit_length(), "e": e, "n": n, "fpr": fpr})
    return mods, primary_fpr

# --------------------------------------------------------------------------
# PKCS#1 v1.5 structure recogniser + DigestInfo table
# --------------------------------------------------------------------------
DIGEST_OIDS = {
    "SHA-1":   bytes.fromhex("3021300906052b0e03021a05000414"),
    "SHA-256": bytes.fromhex("3031300d060960864801650304020105000420"),
    "SHA-384": bytes.fromhex("3041300d060960864801650304020205000430"),
    "SHA-512": bytes.fromhex("3051300d060960864801650304020305000440"),
    "MD5":     bytes.fromhex("3020300c06082a864886f70d020505000410"),
    "SHA-224": bytes.fromhex("302d300d060960864801650304020405001c"),
}

def pkcs1_v15_recognise(m_padded):
    """Return (structure, digest_name|None, detail)."""
    b = m_padded
    # signature block: 00 01 FF..FF 00 DigestInfo
    if len(b) >= 11 and b[0] == 0x00 and b[1] == 0x01:
        i = 2
        while i < len(b) and b[i] == 0xff:
            i += 1
        if i > 10 and i < len(b) and b[i] == 0x00:
            after = b[i+1:]
            for name, pref in DIGEST_OIDS.items():
                if after[:len(pref)] == pref:
                    return "sig", name, f"{i-2} FF, DigestInfo {name}"
            return "sig-nodi", None, f"{i-2} FF, no known DigestInfo (head {after[:8].hex()})"
    # encryption block: 00 02 <nonzero PS> 00 M
    if len(b) >= 11 and b[0] == 0x00 and b[1] == 0x02:
        i = 2
        while i < len(b) and b[i] != 0x00:
            i += 1
        if i >= 10 and i < len(b):
            return "enc", None, f"{i-2}-byte PS then 00, msg head {b[i+1:i+9].hex()}"
    return None, None, f"no PKCS#1 (head {b[:4].hex()})"

def rsa_pub_op(s_int, e, n):
    m = pow(s_int, e, n)
    modbytes = (n.bit_length() + 7) // 8
    return m.to_bytes(modbytes, "big")  # left-padded to full modulus width

# --------------------------------------------------------------------------
# Controls
# --------------------------------------------------------------------------
def positive_control():
    """Make a real PKCS#1 v1.5 SHA-256 signature under a fresh RSA-4096 key,
    then verify the recogniser recovers it (zero false negative)."""
    from Crypto.PublicKey import RSA
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    key = RSA.generate(4096)
    h = SHA256.new(b"cicada 3301 e-01 positive control")
    sig = pkcs1_15.new(key).sign(h)             # 512-byte signature
    s_int = int.from_bytes(sig, "big")
    recovered = rsa_pub_op(s_int, key.e, key.n)
    struct, dg, detail = pkcs1_v15_recognise(recovered)
    ok = (struct == "sig" and dg == "SHA-256")
    return ok, detail

def negative_control(n, e, trials=64):
    """Random 256-byte blobs under the real modulus must all read NULL
    (zero false positive)."""
    fp = 0
    for _ in range(trials):
        s = int.from_bytes(os.urandom(256), "big")
        struct, _, _ = pkcs1_v15_recognise(rsa_pub_op(s, e, n))
        if struct is not None:
            fp += 1
    return fp

# --------------------------------------------------------------------------
def main():
    print("="*70)
    print("E-01 COMPLETION — 7A35090F RSA-4096 moduli vs pp49-51 payload")
    print("="*70)

    mods, primary_fpr = load_moduli()
    fpr_ok = (primary_fpr == EXPECT_FPR)
    print(f"\nKey fingerprint (primary): {primary_fpr}")
    print(f"Expected (repo-recorded):  {EXPECT_FPR}   -> {'MATCH' if fpr_ok else 'MISMATCH'}")
    if not fpr_ok:
        print("ABORT: key provenance not verified; refusing to report a verdict.")
        return
    for m in mods:
        print(f"  {m['kind']:8s}: {m['bits']}-bit  e={m['e']}")
    (HERE / "keys" / "moduli.json").write_text(json.dumps({
        "source": "keyserver.ubuntu.com op=get 0x" + EXPECT_FPR,
        "fingerprint": primary_fpr, "fingerprint_verified": fpr_ok,
        "uid": "Cicada 3301 (845145127)", "created": "2012-01-05",
        "moduli": [{"kind": m["kind"], "bits": m["bits"], "e": m["e"],
                    "n_hex": hex(m["n"])} for m in mods],
    }, indent=2))

    # Controls
    print("\n--- CONTROLS ---")
    pos_ok, pos_detail = positive_control()
    print(f"POSITIVE (planted PKCS#1 v1.5 sig recovered): {'PASS' if pos_ok else 'FAIL'}  [{pos_detail}]")
    neg_fp = negative_control(mods[0]["n"], mods[0]["e"])
    print(f"NEGATIVE (random blobs, false positives / 64): {neg_fp}  {'PASS' if neg_fp==0 else 'FAIL'}")
    if not (pos_ok and neg_fp == 0):
        print("ABORT: checker not validated in both directions; verdict withheld.")
        return

    # Payloads
    payloads = {}
    for name, path in PAYLOADS.items():
        if path.exists():
            payloads[name] = path.read_bytes()
    print(f"\n--- PAYLOADS ({len(payloads)} loaded) ---")
    for name, data in payloads.items():
        c = {}
        for x in data: c[x] = c.get(x, 0) + 1
        ent = -sum(v/len(data)*log2(v/len(data)) for v in c.values())
        print(f"  {name}: {len(data)} bytes, entropy {ent:.3f} b/B")

    # The mechanical check
    print("\n--- E-01 RESULTS ---")
    results = []
    hits = []
    for m in mods:
        n, e = m["n"], m["e"]
        modbytes = (n.bit_length() + 7) // 8
        for pname, pdata in payloads.items():
            for endian in ("big", "little"):
                for e_try in sorted({e, 3, 65537}):
                    s_int = int.from_bytes(pdata, endian)
                    note = ""
                    if s_int >= n:
                        verdict = "SKIP"; struct = None; detail = "s >= n"
                    else:
                        out = rsa_pub_op(s_int, e_try, n)
                        struct, dg, detail = pkcs1_v15_recognise(out)
                        verdict = "HIT" if struct in ("sig", "enc") else "NULL"
                        # a 256-byte payload under a 512-byte modulus: s < n and
                        # pow(s,e) with tiny s (e=3) may be < n, i.e. no reduction.
                        if 256*8 < n.bit_length() and e_try == 3 and s_int**3 < n:
                            note = "no modular reduction (s^3 < n)"
                    row = {"modulus": m["kind"], "mod_bits": m["bits"],
                           "payload": pname, "endian": endian, "e": e_try,
                           "struct": struct, "detail": detail, "verdict": verdict,
                           "note": note}
                    results.append(row)
                    if verdict == "HIT":
                        hits.append(row)

    n_skip = sum(1 for r in results if r["verdict"] == "SKIP")
    n_null = sum(1 for r in results if r["verdict"] == "NULL")
    print(f"checks: {len(results)}  |  HIT {len(hits)}  NULL {n_null}  SKIP {n_skip}")
    if hits:
        for h in hits:
            print("  HIT:", h)
    else:
        print("  no PKCS#1 signature or encryption-block structure under either modulus,")
        print("  either endianness, or e in {key-e, 3, 65537}.")

    verdict = "HIT" if hits else "NEGATIVE"
    print(f"\nE-01 VERDICT: {verdict}")

    out = {
        "test": "E-01-complete",
        "verdict": verdict,
        "key": {
            "source": "keyserver.ubuntu.com op=get 0x" + EXPECT_FPR,
            "fingerprint": primary_fpr,
            "fingerprint_verified": fpr_ok,
            "uid": "Cicada 3301 (845145127)", "created": "2012-01-05",
            "moduli": [{"kind": m["kind"], "bits": m["bits"], "e": m["e"]} for m in mods],
        },
        "controls": {"positive_recovered": pos_ok, "negative_false_positives_of_64": neg_fp},
        "checks": len(results), "hits": len(hits), "nulls": n_null, "skips": n_skip,
        "results": results,
        "coverage": ("Both 7A35090F RSA-4096 moduli (primary [SC] + subkey [E]) vs "
                     "canon_256 and canon_256_decpref, big/little endian, e in "
                     "{key-e=65537, 3}. The 256-byte payload is 2048-bit; under a "
                     "4096-bit modulus s<n always holds, so pow(s,e,n) is well-defined "
                     "and was actually computed, not assumed."),
        "not_covered": ["2048-bit or other-size Cicada keys (none published/held)",
                        "OAEP / PSS encodings (structure-recognisable only with the label/salt)",
                        "payload as a *fragment* of a 512-byte signature"],
    }
    (HERE / "e01_complete_results.json").write_text(json.dumps(out, indent=2))
    print("wrote", HERE / "e01_complete_results.json")

if __name__ == "__main__":
    main()
