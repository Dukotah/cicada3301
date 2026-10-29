#!/usr/bin/env python3
"""R34-P1 reader R30-B1 (blob crypto), canon-blob arm only. Original battery.py, unmodified, with a pycryptodome-API shim.
T2.bin / folly.bin are absent (gitignored): cross-XOR and the blob:T2 / blob:folly keys are NOT re-runnable."""
import os, sys, json, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "R30-B1")
LP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "shim")); sys.path.insert(0, os.path.join(LP, "analysis", "round30", "B1-blob-crypto"))
GH = os.path.join(OUT, "gnupghome"); os.makedirs(GH, exist_ok=True); os.environ["GNUPGHOME"] = "gnupghome"
import battery as B
from battery import load_keys, struct_id, run_cipher_battery, detect_success, fit_key, shannon
from Crypto.Cipher import AES, ARC4, Blowfish, DES, DES3
log = open(os.path.join(OUT, "run.log"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); log.write(s + "\n"); log.flush()
res = {"shim_known_answers": {}, "controls": {}, "arms": {}}
# ---- shim fidelity (known-answer vectors)
ka = res["shim_known_answers"]
ka["AES128_ECB_FIPS197"] = AES.new(bytes.fromhex("000102030405060708090a0b0c0d0e0f"), AES.MODE_ECB).decrypt(bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")).hex() == "00112233445566778899aabbccddeeff"
ka["RC4_Secret"] = ARC4.new(b"Secret").decrypt(bytes.fromhex("45A01F645FC35B383552544B9BF5")) == b"Attack at dawn"
ka["Blowfish_ECB_zero"] = Blowfish.new(bytes(8), Blowfish.MODE_ECB).decrypt(bytes.fromhex("4EF997456198DD78")) == bytes(8)
ka["DES_ECB_classic"] = DES.new(bytes.fromhex("133457799BBCDFF1"), DES.MODE_ECB).decrypt(bytes.fromhex("85E813540F0AB405")) == bytes.fromhex("0123456789ABCDEF")
k3 = bytes.fromhex("0123456789abcdef23456789abcdef01456789abcdef0123")
ka["3DES_ECB_roundtrip"] = None
P("shim known answers:", ka)
# ---- original controls (copied from run.py)
def control_positive():
    pt = b"THE PRIMES ARE SACRED AND CICADA 3301 WELCOMES THE PILGRIM HOME.\n" * 2
    ptp = pt + b" " * ((-len(pt)) % 16)
    key = fit_key(b"CICADA3301", 32, "hash")
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    e = Cipher(algorithms.AES(key), modes.CBC(b"\x00" * 16)).encryptor()
    ct = e.update(ptp) + e.finalize()
    dec = AES.new(key, AES.MODE_CBC, b"\x00" * 16).decrypt(ct)
    hits = detect_success(dec)
    # and through the battery path itself: the planted ct must be found by run_cipher_battery under key CICADA3301
    results = []; run_cipher_battery(ct, "plant", {"phrase:CICADA3301": b"CICADA3301"}, results)
    return {"recovered": dec[:64].decode(errors="replace"), "detector_fired": bool(hits), "battery_path_hits": len(results),
            "battery_path_cipher": sorted(set(r[0] for r in results)), "PASS": bool(hits) and any("AES-256-CBC(IV=0) k=hash" in r[0] for r in results)}
def control_negative():
    fires = 0; trials = 500
    for _ in range(trials):
        dec = AES.new(os.urandom(32), AES.MODE_CBC, b"\x00" * 16).decrypt(os.urandom(256))
        if detect_success(dec): fires += 1
    return {"trials": trials, "false_fires": fires, "PASS": fires == 0}
res["controls"]["positive"] = control_positive(); res["controls"]["negative"] = control_negative()
P("controls:", res["controls"])
# ---- arm
def gpg_try(path, pw):
    try:
        r = subprocess.run(["gpg", "--batch", "--yes", "--passphrase", pw, "--pinentry-mode", "loopback", "-d", os.path.basename(path)], capture_output=True, timeout=30, cwd=OUT)
        if r.returncode == 0 and r.stdout: return r.stdout
    except Exception: pass
    return None
def ossl(path, algo, pw):
    try:
        r = subprocess.run(["openssl", "enc", "-d", f"-{algo}", "-in", os.path.basename(path), "-pass", f"pass:{pw}", "-pbkdf2"], capture_output=True, timeout=30, cwd=OUT)
        if r.returncode == 0 and r.stdout: return r.stdout
    except Exception: pass
    return None
pps = [k.split(":", 1)[1] for k in ["num:3301", "num:1595277641", "num:509", "num:503", "hash56:hexstr"]]
pps += ["CICADA3301", "WELCOME", "PILGRIM", "ANEND", "INSTAR", "THEPRIMESARESACRED", "firfumferenfe", "3301",
        "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"]
pps = list(dict.fromkeys(pps))
for tag in ("canon", "resolved"):
    bs = open(os.path.join(HERE, "inputs", tag, "canon_256.bin"), "rb").read()
    keys, eng = load_keys(); keys["blob:canon"] = bs
    sid = struct_id("canon", bs); results = []
    run_cipher_battery(bs, "canon", keys, results)
    og = []
    tf = os.path.join(OUT, f"_tmp_{tag}.bin"); open(tf, "wb").write(bs)
    for pw in pps:
        g = gpg_try(tf, pw)
        if g: og.append({"tool": "gpg", "pass": pw[:20], "len": len(g), "hits": detect_success(g), "sha1": __import__("hashlib").sha1(g).hexdigest()})
    for algo in ["aes-256-cbc", "aes-128-cbc", "aes-256-ecb", "des-ede3-cbc", "bf-cbc", "rc4"]:
        for pw in pps:
            o = ossl(tf, algo, pw)
            if o and detect_success(o): og.append({"tool": "openssl", "algo": algo, "pass": pw[:20], "len": len(o), "hits": detect_success(o)})
    os.remove(tf)
    res["arms"][tag] = {"struct_id": sid, "n_keys": len(keys), "cipher_hits": [[r[0], r[1], r[2], r[3]] for r in results],
                        "gpg_openssl_rows": og}
    P(tag, "keys", len(keys), "struct entropy", sid["entropy_bits_per_byte"], "chi", sid["chi_square_vs_uniform"], "cipher_hits", len(results), "gpg/openssl rows", len(og), [(o["tool"], o["pass"], o["len"], o["hits"]) for o in og])
stored = json.load(open(os.path.join(LP, "analysis", "round30", "B1-blob-crypto", "results.json")))
res["stored_canon_struct"] = stored["structural"]["canon"]
res["stored_openssl_gpg_canon_rows"] = [r for r in stored["openssl_gpg"] if r["blob"] == "canon"]
res["canon_struct_reproduces_stored"] = res["arms"]["canon"]["struct_id"] == stored["structural"]["canon"]
res["verdict_same"] = (res["arms"]["canon"]["cipher_hits"] == [] and res["arms"]["resolved"]["cipher_hits"] == []
                       and [(o["tool"], o["pass"], o["hits"]) for o in res["arms"]["canon"]["gpg_openssl_rows"]] == [(o["tool"], o["pass"], o["hits"]) for o in res["arms"]["resolved"]["gpg_openssl_rows"]])
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
P("canon struct reproduces stored:", res["canon_struct_reproduces_stored"], " verdict_same:", res["verdict_same"])
shutil.rmtree(GH, ignore_errors=True)
