#!/usr/bin/env python3
"""R33-B1 rows E-01 / E-02: run round16/zeroFP/zerofp_tests.py UNMODIFIED with the payload bytes substituted."""
import os, sys, io, json, random, shutil, contextlib, hashlib
from pathlib import Path
HERE = os.path.dirname(os.path.abspath(__file__))
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LP, "analysis", "round16", "zeroFP"))
import zerofp_tests as Z

PP = Path(LP) / "analysis" / "pp49_51"
canon = (PP / "canon_256.bin").read_bytes()
res = (Path(LP) / "analysis" / "round19" / "C1" / "payload_resolved.bin").read_bytes()
decc = (PP / "canon_256_decpref.bin").read_bytes()
dec = bytearray(decc)
for i in (45, 50, 246):
    dec[i] = res[i]
dec = bytes(dec)
_orig_load = Z.load_bytes


def with_payload(c, d, tmp=None, fn=None):
    """run fn() with load_bytes serving payload c (canon_256.bin) and d (canon_256_decpref.bin)."""
    def lb(path):
        n = os.path.basename(str(path))
        if n == "canon_256.bin": return c
        if n == "canon_256_decpref.bin": return d
        return _orig_load(path)
    Z.load_bytes = lb
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            r = fn()
    finally:
        Z.load_bytes = _orig_load
    return r, buf.getvalue()


def mr(n, k=24):
    if n < 4: return n in (2, 3)
    if n % 2 == 0: return False
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(k):
        a = random.randrange(2, n - 1); x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True


def prime(bits, rng):
    while True:
        p = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if mr(p) and (p - 1) % 65537: return p


def e01_plant():
    """Plant: own 365-bit-class modulus, a genuine PKCS#1 v1.5 type-1 SHA-1 signature as the payload; the unmodified e01 must HIT."""
    random.seed(3301)
    while True:
        p, q = prime(183, random), prime(183, random); n = p * q
        if n.bit_length() == 365: break
    em = b"\x00\x01" + b"\xff" * 8 + b"\x00" + bytes.fromhex("3021300906052b0e03021a05000414") + hashlib.sha1(b"planted").digest()
    assert len(em) == 46 and int.from_bytes(em, "big") < n
    d = pow(65537, -1, (p - 1) * (q - 1))
    s = pow(int.from_bytes(em, "big"), d, n)
    payload = s.to_bytes(256, "big")
    tmp = Path(HERE) / "E01" / "plant_analysis"
    (tmp / "armada20").mkdir(parents=True, exist_ok=True)
    (tmp / "pp49_51").mkdir(parents=True, exist_ok=True)
    (tmp / "pp49_51" / "canon_256.bin").write_bytes(payload); (tmp / "pp49_51" / "canon_256_decpref.bin").write_bytes(payload)
    (tmp / "armada20" / "pgp_welcome.txt").write_text("n = %d\ne = 65537\n" % n)
    old = Z.ANALYSIS; Z.ANALYSIS = tmp
    try:
        r, _ = with_payload(payload, payload, fn=Z.e01_rsa_pkcs1)
    finally:
        Z.ANALYSIS = old
    # unplanted random payloads under the same planted modulus: zero false positives
    rng = random.Random(7); fp = 0
    Z.ANALYSIS = tmp
    try:
        for _ in range(300):
            rp = bytes(rng.getrandbits(8) for _ in range(40)).rjust(256, b"\x00")
            rr, _ = with_payload(rp, rp, fn=Z.e01_rsa_pkcs1)
            fp += rr["verdict"] != "NULL"
    finally:
        Z.ANALYSIS = old
    shutil.rmtree(tmp, ignore_errors=True)
    hits = [x for x in r["results"] if x.get("verdict") == "HIT"]
    return {"verdict": r["verdict"], "n_hit_rows": len(hits), "digest": hits[0]["digest_info_detail"][:40] if hits else None,
            "random_payload_fp_trials": 300, "random_payload_fp": fp, "PASS": bool(r["verdict"] == "HIT" and fp == 0)}


def e02_plant():
    rng = random.Random(5)
    buf = bytearray(rng.getrandbits(8) for _ in range(256)); perm = list(range(56)); rng.shuffle(perm)
    buf[100:156] = bytes(perm)
    r, _ = with_payload(bytes(buf), bytes(buf), fn=Z.e02_meta_parameters)
    ok = any(h[0] == 100 for h in r["E-02A_perm56_hits"])
    # and a window with ONE byte off the permutation (single-byte sensitivity) must NOT fire
    buf2 = bytearray(buf); buf2[120] = (buf2[120] + 1) % 56 if buf2[120] + 1 < 56 else 0
    r2, _ = with_payload(bytes(buf2), bytes(buf2), fn=Z.e02_meta_parameters)
    return {"planted_found_at_100": ok, "verdict": r["verdict"], "one_byte_broken_verdict": r2["verdict"],
            "PASS": bool(ok and r["verdict"] == "HIT" and r2["verdict"] == "NULL")}


def strip(r):
    return {k: v for k, v in r.items() if k != "results"}


out = {"payload_diff_idx": [i for i in range(256) if canon[i] != res[i]],
       "decpref_corrected_diff_vs_decpref": [i for i in range(256) if decc[i] != dec[i]]}
out["control"] = {"E-01_planted": e01_plant(), "E-02_planted": e02_plant()}
print(json.dumps(out["control"], indent=1), flush=True)
out["control"]["ALL_PASS"] = all(v["PASS"] for v in out["control"].values())
if out["control"]["ALL_PASS"]:
    for tag, (c, d) in (("canon", (canon, decc)), ("resolved", (res, dec))):
        r1, t1 = with_payload(c, d, fn=Z.e01_rsa_pkcs1)
        r2, t2 = with_payload(c, d, fn=Z.e02_meta_parameters)
        out[tag] = {"E-01": strip(r1), "E-01_results": r1["results"], "E-02": r2, "E-02_stdout": t2.splitlines()}
        (Path(HERE) / "E01" / ("stdout_%s.txt" % tag)).write_text(t1)
        (Path(HERE) / "E02" / ("stdout_%s.txt" % tag)).write_text(t2)
    pub = json.load(open(os.path.join(LP, "analysis", "round16", "zeroFP", "results.json")))
    out["published"] = {"E-01": pub["E-01"]["verdict"], "E-01_pow_checks": pub["E-01"]["pow_checks"], "E-02": pub["E-02"]["verdict"],
                        "E-02A_windows_checked": pub["E-02"]["E-02A_windows_checked"]}
    out["changed_vs_canon"] = {
        "E-01": out["canon"]["E-01_results"] != out["resolved"]["E-01_results"] or out["canon"]["E-01"]["verdict"] != out["resolved"]["E-01"]["verdict"],
        "E-02": out["canon"]["E-02"] != out["resolved"]["E-02"]}
    out["canon_reproduces_published"] = {"E-01": out["canon"]["E-01"]["verdict"] == pub["E-01"]["verdict"] and out["canon"]["E-01"]["pow_checks"] == pub["E-01"]["pow_checks"],
                                         "E-02": out["canon"]["E-02"]["verdict"] == pub["E-02"]["verdict"] and out["canon"]["E-02"]["E-02A_windows_checked"] == pub["E-02"]["E-02A_windows_checked"]}
json.dump(out, open(os.path.join(HERE, "E01", "e01_e02_results.json"), "w"), indent=1, default=str)
print(json.dumps({k: out.get(k) for k in ("control", "published", "changed_vs_canon", "canon_reproduces_published")}, indent=1, default=str))
