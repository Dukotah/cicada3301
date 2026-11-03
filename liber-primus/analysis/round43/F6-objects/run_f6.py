"""R43/F6 — the open internal objects, joined. Implements PREREG.md exactly.

Parts (a) payload-vs-blob, (b) blob structure, (c-xor) hash XOR payload, (d) T4 bound.
Part (c) keystream over the 55 pages lives in run_f6_keystream.py (panel import glue).
Outputs: f6_results.json (+ prints).
"""
import hashlib, json, math, os, re, sys, zlib, bz2, lzma, base64, binascii

HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for p in ("analysis", "src", "analysis/round19/I2", "analysis/round34/I1-v3-null"):
    sys.path.insert(0, os.path.join(LP, p))

import adjudicate as A          # noqa
import bars_v3 as B             # noqa

PAN = A.Panel(os.path.join(LP, "data", "panels", "panel-r36.npz"))
HASH56 = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
          "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")

ONIONS = {
    "blob3301": "onions__avowyfgl5lkzfj3n.onion__pre__index.html",
    "blob761":  "onions__cu343l33nqaekrnw.onion__pre__index.html",
    "blob1033": "onions__fv7lyucmeozzd5j4.onion__pre__index.html",
}
MAGICS = [(b"PK\x03\x04", "zip"), (b"\x1f\x8b", "gzip"), (b"BZh", "bzip2"),
          (b"\xfd7zXZ", "xz"), (b"%PDF", "pdf"), (b"\x89PNG", "png"),
          (b"GIF8", "gif"), (b"\xff\xd8\xff", "jpeg"), (b"7z\xbc\xaf", "7z"),
          (b"Rar!", "rar"), (b"-----BEGIN", "pem")]
PRINTABLE = set(range(0x20, 0x7F)) | {9, 10, 13}


def sha(b): return hashlib.sha256(b).hexdigest()


def entropy(b):
    if not b: return 0.0
    n = len(b); cnt = [0] * 256
    for x in b: cnt[x] += 1
    return -sum(c / n * math.log2(c / n) for c in cnt if c)


def printable_stats(b):
    frac = sum(1 for x in b if x in PRINTABLE) / len(b)
    run = best = 0
    for x in b:
        run = run + 1 if x in PRINTABLE else 0
        best = max(best, run)
    return frac, best


def der_ok(b):
    """D5: DER SEQUENCE covering 254 or 256 total bytes."""
    if b[0] != 0x30: return False
    if b[1] == 0x82:
        total = 4 + (b[2] << 8 | b[3])
    elif b[1] == 0x81:
        total = 3 + b[2]
    elif b[1] < 0x80:
        total = 2 + b[1]
    else:
        return False
    return total in (254, 256)


def pgp_ok(b):
    """D4 PGP: old/new-format packet tag whose length covers >= 64 bytes."""
    t = b[0]
    if not (t & 0x80): return False
    if t & 0x40:                      # new format
        if len(b) < 2: return False
        l1 = b[1]
        n = l1 if l1 < 192 else ((l1 - 192) << 8) + b[2] + 192 if l1 < 224 else None
        return n is not None and n >= 64
    ltype = t & 3
    if ltype == 0: n = b[1]
    elif ltype == 1: n = b[1] << 8 | b[2]
    elif ltype == 2: n = int.from_bytes(b[1:5], "big")
    else: return False
    return n >= 64


def magic_at0(b):
    for m, name in MAGICS:
        if b.startswith(m): return name
    if b[0] == 0x30 and der_ok(b): return "der"
    if pgp_ok(b): return "pgp"
    return None


def mod29_screen(b):
    r = A.adjudicate([x % 29 for x in b], pan=PAN)
    return round(r["pmax"], 3), r["preg"], bool(r["degenerate"])


D6_BAR = B.bar_v3(36, 240, "free")   # family: 36 outputs in (a)


def detect(name, b, screen=True):
    frac, run = printable_stats(b)
    ent = entropy(b)
    mg = magic_at0(b)
    d5 = der_ok(b)
    row = {"name": name, "printable_frac": round(frac, 3), "max_print_run": run,
           "entropy": round(ent, 3), "magic": mg, "der": d5,
           "D1": frac >= 0.85, "D2": run >= 40, "D3": ent <= 6.0,
           "D4": mg is not None, "D5": d5}
    if screen:
        pmax, preg, deg = mod29_screen(b)
        row.update(mod29_pmax=pmax, mod29_preg=preg, mod29_degenerate=deg,
                   D6=bool((not deg) and pmax >= float(D6_BAR)))
    else:
        row["D6"] = False
    row["hit"] = row["D1"] or row["D2"] or row["D4"] or row["D5"] or (row["D3"] and row["D6"])
    return row


def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))
def add(a, b): return bytes((x + y) % 256 for x, y in zip(a, b))
def sub(a, b): return bytes((x - y) % 256 for x, y in zip(a, b))


def main():
    out = {"prereg": "PREREG.md", "D6_bar": round(float(D6_BAR), 4), "objects": {}, "a": [],
           "control": None, "b": {}, "c_xor": [], "d": []}

    # ---- objects + extraction
    payloads = {}
    for tag, fn in (("canon_256", "analysis/pp49_51/canon_256.bin"),
                    ("canon_256_decpref", "analysis/pp49_51/canon_256_decpref.bin")):
        b = open(os.path.join(LP, fn), "rb").read()
        assert len(b) == 256, (tag, len(b))
        payloads[tag] = b
        out["objects"][tag] = {"path": fn, "len": len(b), "sha256": sha(b)}

    blobs = {}
    for tag, fn in ONIONS.items():
        path = os.path.join(LP, "analysis/armada_osint/onions_ibotpeaches", fn)
        txt = open(path, encoding="utf-8", errors="replace").read()
        marker = re.findall(r"<!--(\d+)-->", txt)
        hexes = re.findall(r"[0-9a-fA-F]{512,}", txt)
        assert len(hexes) == 1, (tag, len(hexes))
        b = bytes.fromhex(hexes[0])
        assert len(b) == 256
        blobs[tag] = b
        out["objects"][tag] = {"file": fn, "marker": marker, "len": len(b),
                               "sha256": sha(b), "hex_prefix": hexes[0][:16]}

    hb = bytes.fromhex(HASH56)
    out["objects"]["page56_hash"] = {"len": len(hb), "sha256": sha(hb), "hex": HASH56}

    # ---- CONTROL through the same glue
    pride = open(os.path.join(LP, "data", "pride.txt"), "rb").read()[:256]
    enc = xor(pride, blobs["blob761"])
    rec = xor(enc, blobs["blob761"])
    ctl_enc = detect("control_encrypted", enc)
    ctl_rec = detect("control_recovered", rec)
    out["control"] = {"encrypted": ctl_enc, "recovered": ctl_rec,
                      "valid": ctl_rec["D1"] and ctl_rec["D2"] and ctl_rec["D3"]
                               and not ctl_enc["hit"]}
    assert out["control"]["valid"], "CONTROL FAILED - detector pipeline invalid"

    # ---- (a) payload x blob grid
    for ptag, pb in payloads.items():
        for btag, bb in blobs.items():
            for otag, kb in (("fwd", bb), ("rev", bb[::-1])):
                for opname, op in (("xor", xor), ("add", add), ("sub", sub)):
                    out["a"].append(detect(f"{ptag}^{btag}.{otag}.{opname}", op(pb, kb)))

    # ---- (b) blob structure
    import sympy  # only for primerange sieve; fall back if absent
    small_primes = list(sympy.primerange(2, 10**6))
    names = list(blobs)
    for tag in names:
        n = int.from_bytes(blobs[tag], "big")
        facs = [p for p in small_primes if n % p == 0][:10]
        out["b"][tag] = {"bitlen": n.bit_length(), "odd": bool(n & 1),
                         "small_factors_lt_1e6": facs,
                         "gcds": {str(k): math.gcd(n, k) for k in
                                  (3301, 503, 509, 761, 1033, 503*509, 503*509*3301)}}
    pair = {}
    for i in range(3):
        for j in range(i + 1, 3):
            a, bq = names[i], names[j]
            na, nb = (int.from_bytes(blobs[t], "big") for t in (a, bq))
            x = xor(blobs[a], blobs[bq])
            frac, run = printable_stats(x)
            pre = next((k for k in range(256) if blobs[a][k] != blobs[bq][k]), 256)
            suf = next((k for k in range(256) if blobs[a][255-k] != blobs[bq][255-k]), 256)
            pair[f"{a}~{bq}"] = {"gcd": math.gcd(na, nb),
                                 "xor_printable_frac": round(frac, 3),
                                 "xor_entropy": round(entropy(x), 3),
                                 "shared_prefix_bytes": pre, "shared_suffix_bytes": suf}
    out["b"]["pairwise"] = pair

    # ---- (c-xor) hash x payload
    for htag, h in (("hash_fwd", hb), ("hash_rev", hb[::-1])):
        k = (h * 4)[:256]
        for ptag, pb in payloads.items():
            out["c_xor"].append(detect(f"{ptag}^{htag}x4", xor(pb, k)))

    # ---- (d) T4 blobs
    art = os.path.join(LP, "analysis/armada_osint/artifacts")
    t4files = sorted(f for f in os.listdir(art)
                     if f.startswith("T4_blob") and f.endswith(".bin"))
    HDRS = {"gzip": re.compile(rb"\x1f\x8b"), "bz2": re.compile(rb"BZh[1-9]"),
            "xz": re.compile(rb"\xfd7zXZ"), "zlib": re.compile(rb"\x78[\x01\x9c\xda\x5e]")}
    for f in t4files:
        b = open(os.path.join(art, f), "rb").read()
        wents = [entropy(b[i:i+4096]) for i in range(0, len(b) - 4095, 4096)]
        magichits = []
        for m, nm in MAGICS:
            c = b.count(m)
            if c: magichits.append({"magic": nm, "count": c, "first": b.find(m)})
        dec = []
        for nm, rx in HDRS.items():
            offs = [mo.start() for mo in rx.finditer(b)][:10000]
            for o in offs:
                try:
                    if nm == "gzip":
                        d = zlib.decompress(b[o:], 31)
                    elif nm == "zlib":
                        d = zlib.decompress(b[o:])
                    elif nm == "bz2":
                        d = bz2.decompress(b[o:])
                    else:
                        d = lzma.decompress(b[o:])
                    dec.append({"fmt": nm, "offset": o, "out_len": len(d),
                                "out_entropy": round(entropy(d[:65536]), 3),
                                "out_sha256": sha(d)})
                    if len(dec) >= 5: break
                except Exception:
                    pass
        # base64/85 on any >=1KiB printable run
        frac, run = printable_stats(b)
        b64 = None
        if run >= 1024:
            # find the run
            cur = st = 0; best = (0, 0)
            for i, x in enumerate(b):
                if x in PRINTABLE:
                    if cur == 0: st = i
                    cur += 1
                    if cur > best[1]: best = (st, cur)
                else:
                    cur = 0
            seg = b[best[0]:best[0]+best[1]]
            for dn, fn2 in (("b64", lambda s: base64.b64decode(s, validate=True)),
                            ("b85", base64.b85decode)):
                try:
                    d = fn2(bytes(seg).translate(None, b" \t\r\n"))
                    b64 = {"fmt": dn, "run_at": best[0], "run_len": best[1],
                           "out_len": len(d), "out_entropy": round(entropy(d[:65536]), 3)}
                    break
                except (binascii.Error, ValueError):
                    pass
        out["d"].append({"file": f, "size": len(b), "sha256": sha(b),
                         "entropy": round(entropy(b), 4),
                         "win4k_entropy_min": round(min(wents), 3),
                         "win4k_entropy_med": round(sorted(wents)[len(wents)//2], 3),
                         "win4k_entropy_max": round(max(wents), 3),
                         "magic_hits": magichits, "decomp_successes": dec,
                         "printable_frac": round(frac, 3), "max_print_run": run,
                         "base_decode": b64})
    # gunzip artifact too
    g = os.path.join(art, "T4_blob1_gunzip.bin")
    if os.path.exists(g):
        b = open(g, "rb").read()
        out["d"].append({"file": "T4_blob1_gunzip.bin", "size": len(b), "sha256": sha(b),
                         "entropy": round(entropy(b), 4),
                         "magic0": magic_at0(b[:64] + b"\0"*64),
                         "printable_frac": round(printable_stats(b)[0], 3)})

    hits_a = [r["name"] for r in out["a"] if r["hit"]]
    hits_c = [r["name"] for r in out["c_xor"] if r["hit"]]
    out["summary"] = {"a_hits": hits_a, "c_xor_hits": hits_c,
                      "a_n": len(out["a"]), "c_xor_n": len(out["c_xor"]),
                      "control_valid": out["control"]["valid"]}
    json.dump(out, open(os.path.join(HERE, "f6_results.json"), "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))
    print("b:", json.dumps(out["b"], indent=1)[:2000])


if __name__ == "__main__":
    main()
