"""L5 / E-01 — extract every published Cicada 3301 RSA modulus, with fingerprint proof.

Round 16's zeroFP lane recorded E-01 as coverage-limited for one concrete reason:
"the 7A35090F RSA-4096 moduli (the correct size) were not on disk and not fetched".
They ARE on disk -- in corpus/, under several independent witnesses including two
keyserver pulls. This script parses the OpenPGP packets directly (stdlib only), computes
the v4 fingerprint of every public-key packet itself, and writes moduli.json.

Fingerprint (RFC 4880 §12.2): SHA-1 over 0x99 || len16 || <the key packet body>.
Computing it here means we do not have to trust the filename or gpg's keyring.

    python3 extract_moduli.py
"""
import base64
import glob
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

CANDIDATE_GLOBS = [
    "corpus/A-primary-artifacts/pgp/keys/*.asc",
    "corpus/A-primary-artifacts/ibotpeaches/keys/*.asc",
    "corpus/A-primary-artifacts/krisyotam/pgp/key/*.asc",
    "corpus/E-tooling/vendor/AegisTrustCore__Liber-Primus-HMS-Run-Time/keys/*.asc",
    "corpus/E-tooling/vendor/cicada-solvers__isitcicada/assets/pgp/*.txt",
    "corpus/E-tooling/vendor/ztlw30813__cicada3301/public.key",
    "liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/corpus/*.asc",
    "liber-primus/analysis/round10/L6-archives/fetched/jaxonkuipers/comms/*.asc",
    "corpus/H-branch-recovery/recovered/*/liber-primus/analysis/campaign15/*.asc",
]

ARMOR = re.compile(
    r"-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----",
    re.S)


def dearmor(text):
    """Return the raw packet stream of every PGP PUBLIC KEY BLOCK in `text`.

    Armor headers ("Comment:", "Version:") may appear on the first line or after a
    leading blank line depending on the producer, so headers are skipped by shape
    (a line containing ':' before any base64 has been seen), not by position.
    """
    out = []
    for m in ARMOR.finditer(text):
        lines = []
        for ln in m.group(1).splitlines():
            s = ln.strip()
            if not s:
                continue
            if s.startswith("="):        # CRC24 footer ends the data
                break
            if not lines and ":" in s:   # armor header
                continue
            lines.append(s)
        try:
            out.append(base64.b64decode("".join(lines)))
        except Exception:
            pass
    return out


def packets(buf):
    """Yield (tag, body) for OpenPGP packets (old + new format)."""
    i = 0
    n = len(buf)
    while i < n:
        c = buf[i]
        if not (c & 0x80):
            return
        if c & 0x40:                                # new format
            tag = c & 0x3F
            i += 1
            o = buf[i]
            if o < 192:
                ln = o
                i += 1
            elif o < 224:
                ln = ((o - 192) << 8) + buf[i + 1] + 192
                i += 2
            elif o == 255:
                ln = int.from_bytes(buf[i + 1:i + 5], "big")
                i += 5
            else:
                return                              # partial lengths: not used in keys
        else:                                       # old format
            tag = (c >> 2) & 0x0F
            lt = c & 0x03
            i += 1
            if lt == 0:
                ln = buf[i]; i += 1
            elif lt == 1:
                ln = int.from_bytes(buf[i:i + 2], "big"); i += 2
            elif lt == 2:
                ln = int.from_bytes(buf[i:i + 4], "big"); i += 4
            else:
                return
        yield tag, buf[i:i + ln]
        i += ln


def mpi(buf, off):
    bits = int.from_bytes(buf[off:off + 2], "big")
    nb = (bits + 7) // 8
    return int.from_bytes(buf[off + 2:off + 2 + nb], "big"), off + 2 + nb


def fingerprint_v4(body):
    return hashlib.sha1(b"\x99" + len(body).to_bytes(2, "big") + body).hexdigest().upper()


def parse_key_packet(body):
    if body[0] != 4:
        return None
    algo = body[5]
    if algo not in (1, 2, 3):        # RSA (encrypt+sign / encrypt / sign)
        return None
    n, off = mpi(body, 6)
    e, off = mpi(body, off)
    return {"n": n, "e": e, "bits": n.bit_length(), "algo": algo,
            "fingerprint": fingerprint_v4(body),
            "keyid": fingerprint_v4(body)[-16:]}


def main():
    found = {}
    sources = {}
    for g in CANDIDATE_GLOBS:
        for path in glob.glob(os.path.join(ROOT, g)):
            try:
                text = open(path, "r", encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for blob in dearmor(text):
                for tag, body in packets(blob):
                    if tag not in (6, 14):           # public key / public subkey
                        continue
                    k = parse_key_packet(body)
                    if not k:
                        continue
                    fp = k["fingerprint"]
                    rel = os.path.relpath(path, ROOT).replace("\\", "/")
                    sources.setdefault(fp, set()).add(rel)
                    if fp in found:
                        assert found[fp]["n"] == k["n"], f"MODULUS MISMATCH for {fp}!"
                    else:
                        k["role"] = "primary" if tag == 6 else "subkey"
                        found[fp] = k

    # 2013 puzzle modulus (decimal, in the local welcome text) -- kept for completeness
    pw = os.path.join(ROOT, "liber-primus", "analysis", "armada20", "pgp_welcome.txt")
    n2013 = None
    if os.path.exists(pw):
        t = open(pw, encoding="utf-8", errors="ignore").read()
        m = re.search(r"n\s*=\s*([0-9\s\\]+)", t)
        if m:
            try:
                n2013 = int(re.sub(r"[^0-9]", "", m.group(1)))
            except Exception:
                n2013 = None

    out = {"pgp_moduli": [], "other_moduli": []}
    print(f"{'fingerprint':<44} {'bits':>5} {'e':>7}  role      witnesses")
    for fp, k in sorted(found.items(), key=lambda kv: -kv[1]["bits"]):
        w = sorted(sources[fp])
        print(f"{fp:<44} {k['bits']:>5} {k['e']:>7}  {k['role']:<9} {len(w)}")
        for s in w:
            print(f"{'':<44} {'':>5} {'':>7}             {s}")
        out["pgp_moduli"].append({
            "fingerprint": fp, "keyid": k["keyid"], "bits": k["bits"],
            "e": k["e"], "role": k["role"], "n_hex": format(k["n"], "x"),
            "witnesses": w,
        })
    if n2013:
        print(f"\n2013 puzzle modulus: {n2013.bit_length()} bits (from armada20/pgp_welcome.txt)")
        out["other_moduli"].append({
            "name": "2013_puzzle", "bits": n2013.bit_length(),
            "n_hex": format(n2013, "x"), "e": 65537,
            "witnesses": ["liber-primus/analysis/armada20/pgp_welcome.txt"],
        })

    with open(os.path.join(HERE, "moduli.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote moduli.json  ({len(out['pgp_moduli'])} PGP + "
          f"{len(out['other_moduli'])} other)")


if __name__ == "__main__":
    main()
