"""Driver: controls first, then structural-ID, cipher battery, cross-XOR, openssl/gpg."""
import os, sys, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from battery import (BLOBS, load_keys, struct_id, run_cipher_battery,
                     detect_success, fit_key, shannon)
from Crypto.Cipher import AES

HERE = os.path.dirname(os.path.abspath(__file__))
out = {"controls": {}, "structural": {}, "cipher_hits": [], "cross_xor": [],
       "openssl_gpg": [], "summary": {}}

# ---------------------------------------------------------------- CONTROLS
def control_positive():
    """Encrypt known PT under AES-256-CBC(IV=0), key=sha256('CICADA3301'); confirm
       our battery's detector recovers it."""
    pt = b"THE PRIMES ARE SACRED AND CICADA 3301 WELCOMES THE PILGRIM HOME.\n" * 2
    # pad to 16
    padlen = (-len(pt)) % 16
    ptp = pt + b" " * padlen
    key = fit_key(b"CICADA3301", 32, "hash")
    ct = AES.new(key, AES.MODE_CBC, b"\x00"*16).encrypt(ptp)
    # now decrypt via the same path the battery would use
    dec = AES.new(key, AES.MODE_CBC, b"\x00"*16).decrypt(ct)
    hits = detect_success(dec)
    return {"recovered": dec[:64].decode(errors="replace"),
            "detector_fired": bool(hits), "hits": hits,
            "PASS": bool(hits)}

def control_negative():
    """Decrypt genuine random bytes under a WRONG key; detector MUST stay silent.
       Do it many times to estimate the false-positive rate of the detector."""
    import os as _os
    fires = 0; trials = 500
    for _ in range(trials):
        rnd = _os.urandom(256)
        key = _os.urandom(32)
        dec = AES.new(key, AES.MODE_CBC, b"\x00"*16).decrypt(rnd)
        if detect_success(dec):
            fires += 1
    return {"trials": trials, "false_fires": fires,
            "fp_rate": fires/trials, "PASS": fires == 0}

out["controls"]["positive"] = control_positive()
out["controls"]["negative"] = control_negative()
print("CONTROL positive:", out["controls"]["positive"]["PASS"])
print("CONTROL negative:", out["controls"]["negative"]["PASS"],
      "fp_rate=", out["controls"]["negative"]["fp_rate"])

# ---------------------------------------------------------------- load blobs
data = {name: open(p, "rb").read() for name, p in BLOBS.items()}
keys, eng = load_keys()
print(f"\nkeys loaded: {len(keys)}   blobs: {list(data.keys())}")

# ---------------------------------------------------------------- structural ID
for name, bs in data.items():
    out["structural"][name] = struct_id(name, bs)
    s = out["structural"][name]
    print(f"\n[{name}] len={s['len']} (mod8={s['len_mod_8']} mod16={s['len_mod_16']}) "
          f"H={s['entropy_bits_per_byte']} chi={s['chi_square_vs_uniform']} "
          f"unif={s['chi_consistent_uniform']} rep16={s['repeated_16B_blocks']}")

# ---------------------------------------------------------------- add blobs as keys
# each blob may itself be a key over the others (task 2 clause "pp49-51 payload as key")
for name, bs in data.items():
    keys[f"blob:{name}"] = bs

# ---------------------------------------------------------------- cipher battery
results = []
for name, bs in data.items():
    run_cipher_battery(bs, name, keys, results)
out["cipher_hits"] = [{"cipher": r[0], "key": r[1], "kind": r[2],
                       "detail": r[3], "pt_head_hex": r[4]} for r in results]
print(f"\ncipher battery: {len(results)} success-hits "
      f"(over ~{len(keys)} keys x 3 blobs x many ciphers)")
for r in results[:40]:
    print("  HIT", r[0], r[1], r[2], r[3])

# ---------------------------------------------------------------- cross-XOR
# blob-as-keystream over blob: XOR pairwise (aligned + reversed), inspect for structure
def xor_stream(a, b):
    n = min(len(a), len(b))
    return bytes(a[i] ^ b[i] for i in range(n))

names = list(data.keys())
for i in range(len(names)):
    for j in range(len(names)):
        if i == j: continue
        a, b = data[names[i]], data[names[j]]
        for variant, bb in [("fwd", b), ("rev", b[::-1])]:
            x = xor_stream(a, bb)
            H = shannon(x)
            hits = detect_success(x)
            rec = {"a": names[i], "b": f"{names[j]}:{variant}",
                   "xlen": len(x), "entropy": round(H,4),
                   "hits": hits, "head_hex": x[:16].hex()}
            out["cross_xor"].append(rec)
            flag = "  <== STRUCTURE" if (hits or H < 7.0) else ""
            print(f"  XOR {names[i]} ^ {names[j]}:{variant}  H={H:.4f}{flag}")

# ---------------------------------------------------------------- openssl / gpg symmetric
def openssl_try(ct_path, algo, passphrase):
    """openssl enc -d with -pass pass:... . Returns decrypted bytes or None."""
    try:
        r = subprocess.run(
            ["openssl", "enc", "-d", f"-{algo}", "-in", ct_path,
             "-pass", f"pass:{passphrase}", "-pbkdf2"],
            capture_output=True, timeout=15)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except Exception:
        pass
    return None

def gpg_try(ct_path, passphrase):
    try:
        r = subprocess.run(
            ["gpg", "--batch", "--yes", "--passphrase", passphrase,
             "--pinentry-mode", "loopback", "-d", ct_path],
            capture_output=True, timeout=15)
        if r.returncode == 0 and r.stdout:
            return r.stdout
    except Exception:
        pass
    return None

# passphrases: the human-readable Cicada strings (openssl/gpg key-derive from passphrase)
passphrases = [k.split(":",1)[1] if ":" in k else k
               for k in ["num:3301","num:1595277641","num:509","num:503",
                         "hash56:hexstr"]]
passphrases += ["CICADA3301","WELCOME","PILGRIM","ANEND","INSTAR",
                "THEPRIMESARESACRED","firfumferenfe","3301",
                "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"]
passphrases = list(dict.fromkeys(passphrases))

ssl_algos = ["aes-256-cbc","aes-128-cbc","aes-256-ecb","des-ede3-cbc","bf-cbc","rc4"]
for name, bs in data.items():
    tf = os.path.join(HERE, f"_tmp_{name}.bin")
    open(tf, "wb").write(bs)
    # gpg: does it even parse as an OpenPGP message? try decrypt w/ each passphrase
    for pp in passphrases:
        g = gpg_try(tf, pp)
        if g:
            hits = detect_success(g)
            out["openssl_gpg"].append({"tool":"gpg","blob":name,"pass":pp[:20],
                                       "len":len(g),"hits":hits})
            print(f"  GPG DECRYPT {name} pass={pp[:12]} -> {len(g)}B hits={hits}")
    for algo in ssl_algos:
        for pp in passphrases:
            o = openssl_try(tf, algo, pp)
            if o:
                hits = detect_success(o)
                if hits:   # only record success-hits (openssl often emits garbage w/o error on stream ciphers)
                    out["openssl_gpg"].append({"tool":"openssl","algo":algo,
                        "blob":name,"pass":pp[:20],"len":len(o),"hits":hits})
                    print(f"  OPENSSL {algo} {name} pass={pp[:12]} -> hits={hits}")
    os.remove(tf)

print(f"\nopenssl/gpg recorded hits: {len(out['openssl_gpg'])}")

# ---------------------------------------------------------------- summary
out["summary"] = {
    "cipher_success_hits": len(out["cipher_hits"]),
    "cross_xor_structure": sum(1 for r in out["cross_xor"] if r["hits"] or r["entropy"]<7.0),
    "openssl_gpg_hits": len(out["openssl_gpg"]),
    "control_positive_PASS": out["controls"]["positive"]["PASS"],
    "control_negative_PASS": out["controls"]["negative"]["PASS"],
    "negative_fp_rate": out["controls"]["negative"]["fp_rate"],
    "all_three_random": all(out["structural"][n]["chi_consistent_uniform"] for n in data),
}
json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
print("\n=== SUMMARY ===")
print(json.dumps(out["summary"], indent=1))
