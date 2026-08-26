"""Round 19 / C1 -- E-01, sub-result B: the payload against 3301's OWN DECLARED SCHEME.

R1 found 3301 naming their library in a signed message; C3 verified the signature. The
armour says `Scheme: Crypt::RSA::ES::OAEP`, `Version: 1.99`. Testing only OpenSSL-shaped
PKCS#1 would be a mis-specified test - the exact "broken magnet" pattern Round 19 exists to
correct - so this script tests the declared shape as a first-class hypothesis.

THE SHAPE IS MEASURED, NOT ASSUMED. cryptrsa.py decrypts 3301's own 2013/2014 ES::OAEP
ciphertext using the prime factors that sit in the corpus decrypt scripts, and reads the
layout off the wire:

    block size            k = ceil(bits/8)          (54 for the 432-bit 2013 key)
    encoded message       emLen = k - 1             (every block's m is exactly 53 bytes)
    EM                    maskedSeed(hLen) || maskedDB(emLen-hLen)
    MGF                   MGF1, SHA-1, 4-byte big-endian counter
    hLen                  20  (SHA-1)
    DB[0:hLen]            SHA-1(P) with the label P = ""  ->  da39a3ee...afd80709

The identification did not assume the hash or the field order: it searched (hash x order)
for the combination that makes DB[0:hLen] IDENTICAL across all three of 3301's blocks, and
exactly one combination does - and its constant is SHA-1(""), which is the value the
specification predicts. That is the positive control, and it is 3301's own ciphertext
rather than a modern library's analogue.

The matcher therefore requires DB[0:20] == SHA-1(""), a 160-bit predicate: FP ~ 2^-160.

    python3 e01_cryptrsa.py
"""
import hashlib
import json
import os
import secrets

import cryptrsa as cr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PP = os.path.join(ROOT, "liber-primus", "analysis", "pp49_51")

LHASH = hashlib.sha1(b"").digest()
HLEN = 20
EXPONENTS = [65537, 3, 17]


def mgf1(seed, length, hf=hashlib.sha1):
    out, c = b"", 0
    while len(out) < length:
        out += hf(seed + c.to_bytes(4, "big")).digest()
        c += 1
    return out[:length]


def oaep_unmask(em, hlen=HLEN):
    """Return DB, or None if the block is too short. Layout measured in cryptrsa.py."""
    if len(em) < 2 * hlen + 1:
        return None
    ms, md = em[:hlen], em[hlen:]
    seed = bytes(a ^ b for a, b in zip(ms, mgf1(md, hlen)))
    return bytes(a ^ b for a, b in zip(md, mgf1(seed, len(md))))


def match_cryptrsa_oaep(em):
    """HIT iff the unmasked DB opens with SHA-1(P='') - the 160-bit predicate."""
    db = oaep_unmask(em)
    if db is None or db[:HLEN] != LHASH:
        return None
    rest = db[HLEN:]
    z = 0
    while z < len(rest) and rest[z] == 0x00:
        z += 1
    return {"scheme": "Crypt::RSA::ES::OAEP(1.99)", "lhash_ok": True,
            "ps_zeros": z, "db_tail_hex": rest.hex()[:64]}


# ------------------------------------------------------------------ controls
def controls():
    """POSITIVE: 3301's own three ES::OAEP blocks must fire, 3/3.
       NEGATIVE: 10,000 random blocks of the same length must fire 0 times."""
    n = cr.P * cr.Q
    k = (n.bit_length() + 7) // 8
    d = pow(cr.E, -1, (cr.P - 1) * (cr.Q - 1))
    src = os.path.join(ROOT, "corpus", "A-primary-artifacts", "pgp", "messages",
                       "2014-01-rsa-oaep-challenge.asc")
    v = cr.unarmour(open(src, encoding="utf-8", errors="ignore").read())["value"]
    fired = []
    for i in range(len(v) // k):
        c = int.from_bytes(v[i * k:(i + 1) * k], "big")
        em = pow(c, d, n).to_bytes(k - 1, "big")
        fired.append(bool(match_cryptrsa_oaep(em)))
    fp = 0
    for _ in range(10000):
        if match_cryptrsa_oaep(secrets.token_bytes(k - 1)):
            fp += 1
    # and on blocks the size the payload test actually uses
    fp512 = sum(1 for _ in range(10000) if match_cryptrsa_oaep(secrets.token_bytes(511)))
    out = {"positive_source": os.path.relpath(src, ROOT).replace("\\", "/"),
           "blocks": len(fired), "fired": sum(fired),
           "recovery": sum(fired) / len(fired) if fired else 0.0,
           "false_positives_10k_at_%dB" % (k - 1): fp,
           "false_positives_10k_at_511B": fp512,
           "verdict": "PASS" if (all(fired) and fired and fp == 0 and fp512 == 0)
                      else "INSTRUMENT-FAILURE"}
    return out


def main():
    print("=" * 78)
    print("E-01 sub-result B -- payload vs Crypt::RSA::ES::OAEP 1.99 (3301's own scheme)")
    print("=" * 78)

    print("\n--- CONTROL: 3301's own ciphertext ---")
    ctl = controls()
    print("  positive: %d/%d blocks of %s fire (recovery %.3f)"
          % (ctl["fired"], ctl["blocks"], ctl["positive_source"], ctl["recovery"]))
    for kk, vv in ctl.items():
        if kk.startswith("false_positives"):
            print("  negative: %s = %d" % (kk, vv))
    print("  control verdict: %s" % ctl["verdict"])
    if ctl["verdict"] != "PASS":
        json.dump({"control": ctl, "verdict": "INSTRUMENT-FAILURE"},
                  open(os.path.join(HERE, "out_e01_cryptrsa.json"), "w"), indent=1)
        return

    payloads = {
        "canon_256": open(os.path.join(PP, "canon_256.bin"), "rb").read(),
        "canon_256_decpref": open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read(),
        "payload_resolved": open(os.path.join(HERE, "payload_resolved.bin"), "rb").read(),
    }
    mods = json.load(open(os.path.join(HERE, "moduli.json")))
    modlist = [(m["fingerprint"][-16:] + "/" + m["role"], int(m["n_hex"], 16), m["e"])
               for m in mods["pgp_moduli"]]
    modlist += [(m["name"], int(m["n_hex"], 16), m["e"]) for m in mods["other_moduli"]]

    rows, hits = [], []

    # --- B1: the payload as an OAEP-ENCODED BLOCK directly (no modulus involved) -----
    # If the payload were an EM that was never enciphered (or enciphered under e=1), the
    # 160-bit lHash predicate would show it. Costs nothing and is a distinct hypothesis.
    print("\n--- B1: payload read directly as an ES::OAEP encoded block ---")
    for pname, pdata in payloads.items():
        for enc, buf in (("big", pdata), ("little", pdata[::-1])):
            for bs in (256, 128, 64, 53, 52):
                if 256 % bs:
                    continue
                for off in (0, 1):     # emLen = k-1 means a block may start one byte in
                    ok = []
                    for i in range(0, 256 - off, bs):
                        blk = buf[off + i:off + i + bs]
                        if len(blk) < 2 * HLEN + 1:
                            continue
                        ok.append(bool(match_cryptrsa_oaep(blk)))
                    r = {"test": "B1_direct_block", "payload": pname, "endian": enc,
                         "block_size": bs, "offset": off, "blocks": len(ok),
                         "fired": sum(ok), "verdict": "HIT" if any(ok) else "NULL"}
                    rows.append(r)
                    if any(ok):
                        hits.append(r)
    print("  %d configurations, %d hits" % (sum(1 for r in rows), len(hits)))

    # --- B2: pow(s,e,n) then read the result as an OAEP encoded block ---------------
    print("\n--- B2: pow(s,e,n) result read as an ES::OAEP encoded block ---")
    for pname, pdata in payloads.items():
        for enc in ("big", "little"):
            base = int.from_bytes(pdata if enc == "big" else pdata[::-1], "big")
            for mname, n, e_pub in modlist:
                k = (n.bit_length() + 7) // 8
                aligns = [("right", base)]
                if k > len(pdata):
                    aligns.append(("left", base << (8 * (k - len(pdata)))))
                for aname, s in aligns:
                    for e_val in sorted(set(EXPONENTS + [e_pub])):
                        r = {"test": "B2_pow_then_oaep", "payload": pname, "endian": enc,
                             "align": aname, "modulus": mname, "modulus_bits": n.bit_length(),
                             "e": e_val}
                        if s >= n:
                            r["verdict"] = "SKIP"
                            r["why"] = "s >= n"
                            rows.append(r)
                            continue
                        m = pow(s, e_val, n)
                        h = None
                        for emlen in (k - 1, k):
                            if m.bit_length() <= 8 * emlen:
                                h = match_cryptrsa_oaep(m.to_bytes(emlen, "big"))
                                if h:
                                    r["emLen"] = emlen
                                    break
                        r["verdict"] = "HIT" if h else "NULL"
                        if h:
                            r["structure"] = h
                            hits.append(r)
                        rows.append(r)

    # --- B3: can the payload even BE a Crypt::RSA ciphertext under these keys? -------
    print("\n--- B3: block-count arithmetic (Crypt::RSA concatenates k-byte blocks) ---")
    arith = []
    for mname, n, _ in modlist:
        k = (n.bit_length() + 7) // 8
        a = {"modulus": mname, "bits": n.bit_length(), "k_bytes": k,
             "payload_is_whole_number_of_blocks": (256 % k == 0),
             "blocks_if_so": 256 // k if 256 % k == 0 else None}
        arith.append(a)
        print("   %-28s k=%3d  256/k = %s"
              % (mname, k, "%d blocks" % (256 // k) if 256 % k == 0
                 else "NOT an integer -> cannot be a whole ciphertext"))
    for bits in (512, 1024, 2048):
        print("   (a %d-bit key would give k=%d -> %d block(s); 3301 published no such key)"
              % (bits, bits // 8, 256 // (bits // 8)))

    nskip = sum(1 for r in rows if r["verdict"] == "SKIP")
    out = {"control": ctl,
           "measured_layout": {
               "source": "cryptrsa.py, on 3301's own 2013/2014 ES::OAEP ciphertext",
               "emLen": "k-1", "EM": "maskedSeed(20) || maskedDB(emLen-20)",
               "MGF": "MGF1/SHA-1, 4-byte BE counter", "hLen": 20,
               "lHash": LHASH.hex(), "label_P": "\"\" (empty)"},
           "block_arithmetic": arith,
           "n_rows": len(rows), "n_skipped": nskip, "n_hits": len(hits),
           "verdict": "HIT" if hits else "NULL", "hits": hits, "rows": rows}
    json.dump(out, open(os.path.join(HERE, "out_e01_cryptrsa.json"), "w"), indent=1)
    print("\n  rows: %d   skipped(s>=n): %d   HITS: %d" % (len(rows), nskip, len(hits)))
    print("\nwrote out_e01_cryptrsa.json   VERDICT: %s" % out["verdict"])


if __name__ == "__main__":
    main()
