"""Round 19 / C1 -- E-01: the pp49-51 payload as an RSA signature/ciphertext under every
published 3301 modulus. Closes the coverage gap Round 16 named in its own source.

Round 16's zerofp_tests.py left E-01 partially-run and justified it in a comment:

    "NOTE: 7A35090F 4096-bit key modulus not on disk (fetch was planned but not done).
     The payload is 256 bytes (2048-bit); under a 4096-bit modulus, pow(s,e,n)
     would trivially return s^e as-is (s << n), so PKCS1 padding is impossible."

Both halves of that are wrong. The moduli ARE on disk under ten witnesses
(extract_moduli.py), and `pow(s,e,n)` does not "return s^e as-is" for any e > 1: s is
2048-bit, so s^3 is ~6144-bit and s^65537 is ~1.3e8 bits, and both reduce modulo a
4096-bit n. The test is runnable and this script runs it.

Order of operations is fixed by C1/PREREG.md 3.2 and is not negotiable: the positive
control runs FIRST, in this same process, and if it fails the 3301 moduli are not touched.

    python3 e01_rsa.py
"""
import glob
import hashlib
import json
import os
import secrets
from collections import Counter
from math import log2

import extract_moduli as em

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PP = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51")

EXPONENTS = [65537, 3, 17]
FP_TRIALS = 10_000          # the pre-registered bar (PREREG 3.2)
FP_TRIALS_RATE = 100_000    # additional, for rate estimation only -- not a bar

HASHES = {"sha1": hashlib.sha1, "sha256": hashlib.sha256,
          "sha384": hashlib.sha384, "sha512": hashlib.sha512}
STD_SALT_LENS = [0, 20, 28, 32, 48, 64]

DIGEST_OIDS = {
    "SHA-1":   bytes.fromhex("3021300906052b0e03021a05000414"),
    "SHA-224": bytes.fromhex("302d300d060960864801650304020405001c"),
    "SHA-256": bytes.fromhex("3031300d060960864801650304020105000420"),
    "SHA-384": bytes.fromhex("3041300d060960864801650304020205000430"),
    "SHA-512": bytes.fromhex("3051300d060960864801650304020305000440"),
    "MD5":     bytes.fromhex("3020300c06082a864886f70d020505000410"),
}


# --------------------------------------------------------------- the matchers
def match_v15_type1(block):
    """EMSA-PKCS1-v1_5: 00 01 FF*k (k>=8) 00 <DigestInfo>."""
    if len(block) < 11 or block[0] != 0x00 or block[1] != 0x01:
        return None
    i = 2
    while i < len(block) and block[i] == 0xFF:
        i += 1
    k = i - 2
    if k < 8 or i >= len(block) or block[i] != 0x00:
        return None
    rest = block[i + 1:]
    out = {"scheme": "pkcs1_v15_type1", "ff_bytes": k, "tail_hex": rest[:24].hex(),
           "digest_info": None, "digest": None}
    for name, pfx in DIGEST_OIDS.items():
        if rest[:len(pfx)] == pfx:
            out["digest_info"] = name
            out["digest"] = rest[len(pfx):].hex()
    return out


def match_v15_type2(block):
    """EME-PKCS1-v1_5: 00 02 <>=8 nonzero> 00 <message>."""
    if len(block) < 11 or block[0] != 0x00 or block[1] != 0x02:
        return None
    i = 2
    while i < len(block) and block[i] != 0x00:
        i += 1
    if (i - 2) < 8 or i >= len(block):
        return None
    msg = block[i + 1:]
    if not msg:
        return None
    return {"scheme": "pkcs1_v15_type2", "ps_bytes": i - 2, "msg_len": len(msg),
            "msg_hex": msg[:32].hex()}


def _mgf1(seed, length, hf):
    out = b""
    c = 0
    while len(out) < length:
        out += hf(seed + c.to_bytes(4, "big")).digest()
        c += 1
    return out[:length]


def match_pss(block, embits, hname, hf):
    """EMSA-PSS-ENCODE output, structurally: maskedDB || H || 0xBC, and after MGF1
    unmasking DB must be exactly 00*(emLen-hLen-sLen-2) || 01 || salt for a standard
    salt length. Pinning sLen to the standard set is what keeps this zero-FP: it forces
    an exact multi-hundred-byte zero run rather than 'the first nonzero byte is 01'."""
    emlen = len(block)
    hlen = hf().digest_size
    if emlen < hlen + 2 or block[-1] != 0xBC:
        return None
    maskeddb = block[:emlen - hlen - 1]
    h = block[emlen - hlen - 1:emlen - 1]
    dbmask = _mgf1(h, len(maskeddb), hf)
    db = bytearray(a ^ b for a, b in zip(maskeddb, dbmask))
    nbits = 8 * emlen - embits
    if nbits:
        db[0] &= 0xFF >> nbits
    for slen in STD_SALT_LENS + [hlen]:
        pslen = emlen - hlen - slen - 2
        if pslen < 0:
            continue
        if bytes(db[:pslen]) == b"\x00" * pslen and len(db) > pslen and db[pslen] == 0x01:
            return {"scheme": "pss", "hash": hname, "salt_len": slen,
                    "salt_hex": bytes(db[pslen + 1:]).hex()[:64],
                    "H_hex": h.hex()[:64]}
    return None


def all_matchers(block, embits):
    hits = []
    for m in (match_v15_type1(block), match_v15_type2(block)):
        if m:
            hits.append(m)
    for hname, hf in HASHES.items():
        m = match_pss(block, embits, hname, hf)
        if m:
            hits.append(m)
    return hits


# --------------------------------------------------- mandatory positive control
def positive_control():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa

    rep = {"planted": [], "false_positives": {}, "verdict": None}
    msg = b"3301 L5/C1 positive control -- a genuine signature, planted deliberately."
    ok = True

    for bits in (2048, 4096):
        key = rsa.generate_private_key(public_exponent=65537, key_size=bits)
        pub = key.public_key().public_numbers()
        n, e = pub.n, pub.e
        klen = (n.bit_length() + 7) // 8

        # --- genuine PKCS#1 v1.5 signature ---------------------------------
        sig = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
        m = pow(int.from_bytes(sig, "big"), e, n)
        blk = m.to_bytes(klen, "big")
        hit = match_v15_type1(blk)
        want = hashlib.sha256(msg).hexdigest()
        good = bool(hit) and hit["digest_info"] == "SHA-256" and hit["digest"] == want
        rep["planted"].append({"bits": bits, "scheme": "pkcs1_v15_type1", "fired": bool(hit),
                               "digest_info": hit and hit["digest_info"],
                               "digest_matches_sha256_of_message": bool(hit) and hit["digest"] == want,
                               "PASS": good})
        ok &= good

        # --- genuine PSS signature -----------------------------------------
        slen = 32
        sig = key.sign(msg, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=slen), hashes.SHA256())
        m = pow(int.from_bytes(sig, "big"), e, n)
        embits = n.bit_length() - 1
        emlen = (embits + 7) // 8
        blk = m.to_bytes(emlen, "big")
        hit = match_pss(blk, embits, "sha256", hashlib.sha256)
        good = bool(hit) and hit["salt_len"] == slen and hit["hash"] == "sha256"
        rep["planted"].append({"bits": bits, "scheme": "pss", "fired": bool(hit),
                               "recovered_salt_len": hit and hit["salt_len"],
                               "used_salt_len": slen, "PASS": good})
        ok &= good

        # --- genuine PKCS#1 v1.5 type 2 (encryption) ------------------------
        pt = b"cicada"
        ct = key.public_key().encrypt(pt, padding.PKCS1v15())
        # recover the EM with the PRIVATE exponent (this is what an unpad sees)
        d = key.private_numbers().d
        m = pow(int.from_bytes(ct, "big"), d, n)
        blk = m.to_bytes(klen, "big")
        hit = match_v15_type2(blk)
        good = bool(hit) and bytes.fromhex(hit["msg_hex"])[:len(pt)] == pt
        rep["planted"].append({"bits": bits, "scheme": "pkcs1_v15_type2", "fired": bool(hit),
                               "message_recovered": good, "PASS": good})
        ok &= good

        # --- false positives on random blocks -------------------------------
        for label, trials in (("bar_10k", FP_TRIALS), ("rate_100k", FP_TRIALS_RATE)):
            cnt = Counter()
            for _ in range(trials):
                r = secrets.randbelow(n)
                b1 = r.to_bytes(klen, "big")
                if match_v15_type1(b1):
                    cnt["pkcs1_v15_type1"] += 1
                if match_v15_type2(b1):
                    cnt["pkcs1_v15_type2"] += 1
                b2 = (r % (1 << embits)).to_bytes(emlen, "big")
                for hname, hf in HASHES.items():
                    if match_pss(b2, embits, hname, hf):
                        cnt["pss_" + hname] += 1
            rep["false_positives"]["%d_%s" % (bits, label)] = {
                "trials": trials, "hits": dict(cnt), "total": sum(cnt.values())}
            print("  FP %4d-bit %-9s: %d/%d  %s" % (bits, label, sum(cnt.values()),
                                                    trials, dict(cnt) or "clean"))

    fp_bar = all(v["total"] == 0 for k, v in rep["false_positives"].items()
                 if k.endswith("bar_10k"))
    rep["planted_all_pass"] = bool(ok)
    rep["zero_fp_at_10k"] = bool(fp_bar)
    rep["verdict"] = "PASS" if (ok and fp_bar) else "INSTRUMENT-FAILURE"
    return rep


# ------------------------------------------------------- broadened key scan
def broadened_scan():
    """PREREG 3.1 -- every key-shaped file under corpus/ and liber-primus/, not just the
    nine globs L5 used. Fingerprints are computed from the packet body, so a misleading
    filename cannot smuggle a key in or out."""
    pats = ["corpus/**/*.asc", "corpus/**/*.gpg", "corpus/**/*.pgp", "corpus/**/*.key",
            "corpus/**/*.txt", "liber-primus/**/*.asc", "liber-primus/**/*.gpg",
            "liber-primus/**/*.pgp", "liber-primus/**/*.key"]
    found, srcs, nfiles = {}, {}, 0
    for p in pats:
        for path in glob.glob(os.path.join(ROOT, p), recursive=True):
            if not os.path.isfile(path):
                continue
            nfiles += 1
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if "PGP PUBLIC KEY BLOCK" not in text:
                continue
            for blob in em.dearmor(text):
                for tag, body in em.packets(blob):
                    if tag not in (6, 14):
                        continue
                    try:
                        k = em.parse_key_packet(body)
                    except Exception:
                        k = None
                    if not k:
                        continue
                    rel = os.path.relpath(path, ROOT).replace("\\", "/")
                    srcs.setdefault(k["fingerprint"], set()).add(rel)
                    k["role"] = "primary" if tag == 6 else "subkey"
                    found.setdefault(k["fingerprint"], k)
    return nfiles, found, {f: sorted(v) for f, v in srcs.items()}


# ------------------------------------------------------------------ the test
def entropy(b):
    c = Counter(b)
    return -sum((v / len(b)) * log2(v / len(b)) for v in c.values())


def main():
    print("=" * 78)
    print("E-01 -- payload as RSA signature/ciphertext under published 3301 moduli")
    print("=" * 78)

    print("\n--- MANDATORY POSITIVE CONTROL (PREREG B.4 / C1 3.2) -----------------")
    pc = positive_control()
    for p in pc["planted"]:
        print("  plant %4d-bit %-18s fired=%-5s PASS=%s"
              % (p["bits"], p["scheme"], p["fired"], p["PASS"]))
    print("  control verdict: %s" % pc["verdict"])
    if pc["verdict"] != "PASS":
        json.dump({"control": pc, "verdict": "INSTRUMENT-FAILURE"},
                  open(os.path.join(HERE, "out_e01.json"), "w"), indent=1)
        print("  STOP: PREREG Q5 kill condition met. 3301 moduli not touched.")
        return

    print("\n--- BROADENED KEY SCAN (PREREG 3.1) ----------------------------------")
    nfiles, found, srcs = broadened_scan()
    print("  scanned %d files; distinct RSA public-key packets: %d" % (nfiles, len(found)))
    for fp, k in sorted(found.items(), key=lambda kv: -kv[1]["bits"]):
        print("   %s  %5d bits  e=%-6d %-8s  %d witness(es)"
              % (fp, k["bits"], k["e"], k["role"], len(srcs[fp])))

    mods = json.load(open(os.path.join(HERE, "moduli.json")))
    modlist = [(m["fingerprint"][-16:] + "/" + m["role"], int(m["n_hex"], 16), m["e"],
                m["fingerprint"]) for m in mods["pgp_moduli"]]
    modlist += [(m["name"], int(m["n_hex"], 16), m["e"], None) for m in mods["other_moduli"]]
    for fp, k in found.items():
        if all(k["n"] != n for _, n, _, _ in modlist):
            modlist.append((fp[-16:] + "/" + k["role"] + "/NEW", k["n"], k["e"], fp))
            print("   *** NEW modulus not in moduli.json: %s (%d bits)" % (fp, k["bits"]))

    payloads = {
        "canon_256": open(os.path.join(PP, "canon_256.bin"), "rb").read(),
        "canon_256_decpref": open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read(),
        "payload_resolved": open(os.path.join(HERE, "payload_resolved.bin"), "rb").read(),
    }

    print("\n--- THE TEST ---------------------------------------------------------")
    rows, hits = [], []
    for pname, pdata in payloads.items():
        for enc in ("big", "little"):
            base = int.from_bytes(pdata if enc == "big" else pdata[::-1], "big")
            for mname, n, e_pub, fpr in modlist:
                klen = (n.bit_length() + 7) // 8
                aligns = [("right", base)]
                if klen > len(pdata):
                    aligns.append(("left", base << (8 * (klen - len(pdata)))))
                for aname, s in aligns:
                    for e_val in sorted(set(EXPONENTS + [e_pub])):
                        row = {"payload": pname, "endian": enc, "align": aname,
                               "modulus": mname, "modulus_bits": n.bit_length(),
                               "e": e_val}
                        if s >= n:
                            row["verdict"] = "SKIP"
                            row["why"] = ("s >= n: a signature/ciphertext under this "
                                          "modulus is %d bytes, the payload is %d"
                                          % (klen, len(pdata)))
                            rows.append(row)
                            continue
                        m = pow(s, e_val, n)
                        blk = m.to_bytes(klen, "big")
                        embits = n.bit_length() - 1
                        emlen = (embits + 7) // 8
                        blk2 = (m % (1 << embits)).to_bytes(emlen, "big")
                        h = all_matchers(blk, n.bit_length())
                        h += [x for x in
                              (match_pss(blk2, embits, hn, hf) for hn, hf in HASHES.items())
                              if x]
                        row["head_hex"] = blk[:12].hex()
                        row["entropy_bits_per_byte"] = round(entropy(blk), 3)
                        row["printable_ratio"] = round(
                            sum(0x20 <= b < 0x7F for b in blk) / len(blk), 3)
                        row["verdict"] = "HIT" if h else "NULL"
                        if h:
                            row["structures"] = h
                            hits.append(row)
                        rows.append(row)

    nskip = sum(r["verdict"] == "SKIP" for r in rows)
    nnull = sum(r["verdict"] == "NULL" for r in rows)
    print("  tuples: %d   evaluated: %d   skipped(s>=n): %d   NULL: %d   HIT: %d"
          % (len(rows), len(rows) - nskip, nskip, nnull, len(hits)))
    for r in rows:
        if r["verdict"] == "SKIP":
            continue
        print("   %-18s %-6s %-5s %-28s e=%-6d %s  head=%s H=%.2f"
              % (r["payload"], r["endian"], r["align"], r["modulus"], r["e"],
                 r["verdict"], r["head_hex"], r["entropy_bits_per_byte"]))
    if hits:
        print("\n  *** STRUCTURAL HITS ***")
        for h in hits:
            print("   ", json.dumps(h)[:400])

    out = {
        "control": pc,
        "broadened_scan": {"files_scanned": nfiles,
                           "distinct_rsa_public_keys": len(found),
                           "keys": [{"fingerprint": f, "bits": k["bits"], "e": k["e"],
                                     "role": k["role"], "witnesses": srcs[f]}
                                    for f, k in sorted(found.items(),
                                                       key=lambda kv: -kv[1]["bits"])]},
        "moduli_tested": [{"name": m, "bits": n.bit_length(), "e_published": e,
                           "fingerprint": f} for m, n, e, f in modlist],
        "exponents": EXPONENTS,
        "encodings": ["big-endian", "little-endian(byte-reversed)",
                      "right-aligned(zero-pad high)", "left-aligned(zero-pad low)"],
        "payload_variants": sorted(payloads),
        "n_tuples": len(rows), "n_evaluated": len(rows) - nskip,
        "n_skipped_s_ge_n": nskip, "n_null": nnull, "n_hits": len(hits),
        "verdict": "HIT" if hits else "NULL",
        "rows": rows,
    }
    json.dump(out, open(os.path.join(HERE, "out_e01.json"), "w"), indent=1)
    print("\nwrote out_e01.json   VERDICT: %s" % out["verdict"])


if __name__ == "__main__":
    main()
