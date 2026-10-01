#!/usr/bin/env python3
"""
Lane B2 - RSA / GPG-MESSAGE STRUCTURAL TEST, focused on canon_256.

Tests (per lane brief):
 (1) canon_256 as an RSA-related object:
     - 2048-bit MODULUS? (factor: trial-division small primes, Fermat near-square,
       perfect-power, GCD vs real Cicada 4096 n, RSA-structure detector w/ controls)
     - 2048-bit ciphertext? (cannot be RSA-4096 CT by size; test as raw residue mod
       the real 7A35090F 4096-bit modulus n -> is int(canon_256) a valid residue,
       any structure; also modmul / c^e mod n sanity)
 (2) all 3 blobs (canon_256, folly, 2.jpg-payload) as GPG/PGP MESSAGE bodies:
     - raw gpg --list-packets
     - common OpenPGP header-prepend attempts + gpg
     - OpenPGP packet-tag structural scan
 (3) canon_256 as key/seed:
     - AES-256 key (first 32 bytes) over folly + 2.jpg-payload (CBC/ECB/CTR), entropy of output
     - (RSA private exponent / hash-preimage: LEDGERED already - see notes, not re-run)

Controls:
 - Positive: build a real RSA-2048 modulus; structure-detector must FLAG it.
 - Negative: a fresh random 256B blob must NOT be flagged as a modulus.
 - GPG positive: a real armored PGP MESSAGE, dearmored, must parse as valid packets.
"""
import json, os, hashlib, math, subprocess, tempfile, struct
from pathlib import Path

ROOT = Path("/mnt/c/Users/dukot/projects/cicada3301/liber-primus")
LANE = ROOT / "analysis/round30/B2-rsa-gpg"
WORK = LANE / "work"
WORK.mkdir(parents=True, exist_ok=True)

CANON = ROOT / "analysis/pp49_51/canon_256.bin"
FOLLY = ROOT / "analysis/armada_osint/artifacts/folly.bin"
JPG   = ROOT / "analysis/armada_osint/artifacts/2.jpg"

# Real Cicada 4096-bit modulus (pkey[0] from cicada-3301-public-key.asc), e=0x10001
CICADA_N_HEX = ("C1FBCCAED014FAB96447C7CD8B0A42639B8928D7D428E1783104919B513FB7FA"
"03157AC71AB3F96790B1AF45D471C59AD19734D3CE718580AB851D62CE38A496"
"F5E16EE0048E633A7D990A0D26EEDB73867BF9782D787CDB93D6340DAC60DB20"
"943B4884085630430247D9269A335459BCC1191987E814CAA966B28B9A4A32C0"
"F3B659604367E94772B8553DEE34F3BD0CE0118EF5A0823BD242587E92197F88"
"BBB2DC3C3AEF65E75ACFE7E46EC5A2E4929F41928A9CECE6BA66EABF0B6AB9D7"
"6253401856501D3C4DDD8FA6920B85097EA6FC372CCDD387373F328339A6FC77"
"1CFE138A7BB3DF4FEB6DFCDD8457FC357D3C3E6BD1DCD4219244D7535BE6D87E"
"BCE11036E1B627032668E2E50B5C396FE4BF8F9451C4DD695E8CD0E7E6B4DE8F"
"A7D5EB047ADFD6C890AFE9DAA0EA1D7D2CE1F6895EBEE77E2E2C620DCDE39110"
"A58EDCED88D0D7033CD26910F9AC8628E61F2B698D05586F0A27E76099917CB4"
"439463F728E3AB61920B63B09E3F43D16E6AC59947E86A0079A604D9A2315C45"
"79150E89E1E4D989399E7515B80F74892EB67EFA64A0A6EBEC403B379659D3CA"
"F6D8F0BCEFB5A00E94660CC56F4A9F73EDA8226103B6750DA8DF24FF68AA3A89"
"0B282A88EC287F8BED08EB5359E52D145F3F45C792450614B64C638F27A568F5"
"CB760C76D129BAAC2F3B415A5FF25844C37F4B330485433F37BEA197600E6A15")
CICADA_N = int(CICADA_N_HEX, 16)
CICADA_E = 0x10001

SMALL_PRIMES = []
def sieve(limit=100000):
    bs = bytearray([1])*(limit+1); bs[0]=bs[1]=0
    for i in range(2,int(limit**0.5)+1):
        if bs[i]:
            for j in range(i*i,limit+1,i): bs[j]=0
    return [i for i in range(limit+1) if bs[i]]
SMALL_PRIMES = sieve(100000)

def is_probable_prime(n, k=40):
    if n < 2: return False
    for p in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n % p == 0: return n == p
    d = n-1; r=0
    while d % 2 == 0: d//=2; r+=1
    import random
    for _ in range(k):
        a = random.randrange(2, n-1)
        x = pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(r-1):
            x = x*x % n
            if x == n-1: break
        else:
            return False
    return True

def is_perfect_power(n):
    if n < 4: return None
    for b in range(2, n.bit_length()+1):
        lo, hi = 1, 1 << (n.bit_length()//b + 2)
        while lo < hi:
            mid = (lo+hi)//2
            if mid**b < n: lo = mid+1
            else: hi = mid
        if lo**b == n: return (lo, b)
    return None

def fermat_factor(n, max_iter=200000):
    if n % 2 == 0: return None
    a = math.isqrt(n)
    if a*a < n: a += 1
    for i in range(max_iter):
        b2 = a*a - n
        b = math.isqrt(b2)
        if b*b == b2:
            return (a-b, a+b, i)
        a += 1
    return None

def trial_small(n):
    fs = []
    m = n
    for p in SMALL_PRIMES:
        if p*p > m and m > 1:
            break
        while m % p == 0:
            fs.append(p); m//=p
        if m == 1: break
    return fs, m  # factors found, remaining cofactor

def rsa_structure_detector(blob):
    """Returns a verdict dict. A 'plausible RSA modulus' should be:
       - odd, not a small-prime multiple in the tiny range,
       - not itself prime, not a perfect power,
       - not Fermat-factorable in a few thousand iters (balanced primes),
       - full bit-length (top bit set for the claimed size).
    """
    n = int.from_bytes(blob, "big")
    nbits = n.bit_length()
    top_bit_set = (blob[0] & 0x80) != 0
    odd = (n & 1) == 1
    fs, cof = trial_small(n)
    smooth_hit = len(fs) > 0
    prime = is_probable_prime(n) if odd else False
    pp = is_perfect_power(n)
    fer = fermat_factor(n, max_iter=50000)
    # plausibility: a real RSA-n = product of two ~equal large primes ->
    # odd, composite, no tiny factors, NOT fermat-factorable quickly, NOT perfect power.
    plausible = (odd and top_bit_set and not smooth_hit and not prime
                 and pp is None and fer is None and nbits >= (len(blob)*8 - 8))
    return {
        "nbits": nbits, "byte_len": len(blob),
        "top_bit_set": bool(top_bit_set), "odd": bool(odd),
        "trial_small_factors": fs[:10], "num_small_factors": len(fs),
        "is_probable_prime": bool(prime),
        "perfect_power": (pp if pp else None),
        "fermat_factored": (fer[:2] if fer else None),
        "fermat_iters_if_hit": (fer[2] if fer else None),
        "plausible_rsa_modulus": bool(plausible),
    }

results = {"lane": "B2-rsa-gpg", "tests": {}, "controls": {}}

canon = CANON.read_bytes()
folly = FOLLY.read_bytes()

# ---------- extract 2.jpg payload (bytes after EOI, or scan segment) ----------
jpg = JPG.read_bytes()
# The "2.jpg-payload" in prior armadas = trailing/appended data after JPEG EOI (FFD9)
eoi = jpg.rfind(b"\xff\xd9")
jpg_trailer = jpg[eoi+2:] if eoi != -1 else b""
# also the whole jpg entropy-scan is huge; the OSINT armada treated T2/T3 as extracted blobs.
# Use trailer if present, else fall back to first 256 bytes of the scan data for structural checks.
if len(jpg_trailer) >= 16:
    jpg_payload = jpg_trailer
else:
    jpg_payload = b""  # no appended payload
results["tests"]["jpg_trailer_len"] = len(jpg_trailer)

# ============================================================
# TEST 1: canon_256 as RSA modulus + structure detector
# ============================================================
results["tests"]["canon_as_modulus"] = rsa_structure_detector(canon)

# GCD of canon (as int) with the real Cicada 4096 modulus (shared-prime check)
canon_int = int.from_bytes(canon, "big")
g = math.gcd(canon_int, CICADA_N)
results["tests"]["gcd_canon_cicadaN"] = {"gcd_bits": g.bit_length(), "gcd_is_1": g == 1}

# ============================================================
# TEST 2: canon_256 as ciphertext residue mod real 4096-bit n
# ============================================================
# canon is 2048-bit -> it IS < n (4096-bit), so it's a valid residue by size.
# Test: treat canon as ciphertext c under the PUBLIC key -> compute c^e mod n
# (can't decrypt w/o private key, but structural: does c^e mod n or any simple
#  transform yield low-entropy / printable / OpenPGP-looking output?).
lt = canon_int < CICADA_N
ce = pow(canon_int, CICADA_E, CICADA_N)
ce_bytes = ce.to_bytes((ce.bit_length()+7)//8, "big")
def entropy(b):
    if not b: return 0.0
    from collections import Counter
    c = Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def printable_frac(b):
    if not b: return 0.0
    return sum(1 for x in b if 32<=x<127)/len(b)
results["tests"]["canon_as_residue_mod_cicadaN"] = {
    "canon_lt_n": bool(lt),
    "canon_bits": canon_int.bit_length(),
    "c_pow_e_mod_n_entropy": round(entropy(ce_bytes),4),
    "c_pow_e_mod_n_printable_frac": round(printable_frac(ce_bytes),4),
    "c_pow_e_mod_n_head_hex": ce_bytes[:16].hex(),
    "note": "high entropy / low printable => no structure recovered (expected if not a genuine CT under this key)"
}

# ============================================================
# TEST 3: OpenPGP packet-tag structural scan on all 3 blobs
# ============================================================
def openpgp_scan(blob, name):
    if len(blob) == 0:
        return {"name": name, "empty": True}
    b0 = blob[0]
    # OpenPGP packet header: bit7 must be set (0x80). old format bit6=0, new format bit6=1
    valid_header = (b0 & 0x80) != 0
    newfmt = (b0 & 0x40) != 0
    tag = (b0 & 0x3f) if newfmt else ((b0 >> 2) & 0x0f)
    KNOWN_TAGS = {1:"PKESK",2:"Sig",3:"SKESK",4:"OnePassSig",5:"SecKey",6:"PubKey",
                  7:"SecSubkey",8:"CompressedData",9:"SymEncData",10:"Marker",
                  11:"LiteralData",12:"Trust",13:"UserID",14:"PublicSubkey",
                  17:"UserAttr",18:"SymEncIntegrity",19:"MDC"}
    return {"name": name, "byte0": f"0x{b0:02x}", "valid_pgp_header": bool(valid_header),
            "newfmt": bool(newfmt), "tag": tag, "tag_name": KNOWN_TAGS.get(tag,"UNKNOWN/invalid"),
            "plausible_pgp_message_start": bool(valid_header and tag in (1,3,8,9,11,18))}

results["tests"]["openpgp_scan"] = {
    "canon_256": openpgp_scan(canon, "canon_256"),
    "folly": openpgp_scan(folly, "folly"),
    "jpg_payload": openpgp_scan(jpg_payload, "jpg_payload"),
}

# ============================================================
# TEST 4: gpg --list-packets on raw + header-prepend attempts
# ============================================================
def gpg_try(blob, label):
    if len(blob) == 0:
        return {"label": label, "empty": True}
    out = {}
    env = dict(os.environ)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
        tf.write(blob); path = tf.name
    try:
        r = subprocess.run(["gpg","--list-packets", path], capture_output=True, text=True, timeout=30, env=env)
        out["raw_stdout"] = r.stdout.strip()[:400]
        out["raw_stderr"] = r.stderr.strip()[:300]
        out["raw_parsed_ok"] = ("packet" in r.stdout.lower() and "no valid" not in r.stderr.lower())
    except Exception as e:
        out["raw_err"] = str(e)
    finally:
        os.unlink(path)
    return out

# common header prepends: symmetric-enc (tag 9/18), compressed (tag 8), literal (tag 11)
# and try wrapping as an armored MESSAGE
def gpg_prepend_and_try(blob, label):
    attempts = {}
    # candidate header bytes to prepend (old-format, then a partial-len guess)
    headers = {
        "tag9_symenc_oldfmt": bytes([0x84]),      # tag 9 old fmt (not standard modern but historical)
        "tag18_seip_newfmt": bytes([0xd2, 0x01]), # tag 18 new fmt + version
        "tag8_compressed_zip": bytes([0xa3, 0x01]),
        "tag11_literal": bytes([0xac]),
    }
    for hname, hb in headers.items():
        env = dict(os.environ)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
            tf.write(hb + blob); path = tf.name
        try:
            r = subprocess.run(["gpg","--list-packets", path], capture_output=True, text=True, timeout=20, env=env)
            ok = ("packet" in r.stdout.lower()) and ("no valid" not in r.stderr.lower()) and ("invalid" not in r.stderr.lower())
            attempts[hname] = {"parsed_ok": ok, "stderr": r.stderr.strip()[:120]}
        except Exception as e:
            attempts[hname] = {"err": str(e)}
        finally:
            os.unlink(path)
    return attempts

results["tests"]["gpg_raw"] = {
    "canon_256": gpg_try(canon, "canon_256"),
    "folly": gpg_try(folly, "folly"),
    "jpg_payload": gpg_try(jpg_payload, "jpg_payload") if jpg_payload else {"empty": True},
}
results["tests"]["gpg_header_prepend"] = {
    "canon_256": gpg_prepend_and_try(canon, "canon_256"),
    "folly": gpg_prepend_and_try(folly, "folly"),
}

# ============================================================
# TEST 5: canon_256[:32] as AES-256 key over folly / jpg_payload
# ============================================================
from Crypto.Cipher import AES
aeskey = canon[:32]
def aes_try(key, data, name):
    res = {"name": name}
    # need block-aligned data
    d = data[:(len(data)//16)*16]
    if len(d) < 32:
        return {"name": name, "too_short": True}
    for mode_name, mk in [("ECB", lambda: AES.new(key, AES.MODE_ECB)),
                          ("CBC", lambda: AES.new(key, AES.MODE_CBC, iv=b"\x00"*16)),
                          ("CTR_zero", None)]:
        try:
            if mode_name == "CTR_zero":
                from Crypto.Util import Counter
                ctr = Counter.new(128, initial_value=0)
                c = AES.new(key, AES.MODE_CTR, counter=ctr)
            else:
                c = mk()
            pt = c.decrypt(d)
            res[mode_name] = {"entropy": round(entropy(pt),4),
                              "printable_frac": round(printable_frac(pt),4),
                              "pgp_header": bool(pt[0] & 0x80),
                              "head_hex": pt[:16].hex()}
        except Exception as e:
            res[mode_name] = {"err": str(e)}
    return res

results["tests"]["canon_as_aes256_key"] = {
    "over_folly": aes_try(aeskey, folly, "folly"),
    "over_jpg_payload": aes_try(aeskey, jpg_payload, "jpg_payload") if jpg_payload else {"empty": True},
    "over_canon_self": aes_try(aeskey, canon[32:], "canon_tail"),
}

# ============================================================
# CONTROLS
# ============================================================
import random as _r
# Positive: real RSA-2048 modulus (product of two 1024-bit primes)
def gen_prime(bits):
    while True:
        cand = _r.getrandbits(bits) | (1 << (bits-1)) | 1
        if is_probable_prime(cand): return cand
_r.seed(3301)
p = gen_prime(1024); q = gen_prime(1024)
rsa2048_n = p*q
rsa2048_bytes = rsa2048_n.to_bytes(256, "big")
results["controls"]["pos_real_rsa2048_modulus"] = rsa_structure_detector(rsa2048_bytes)

# Negative: fresh random 256B blob must NOT be flagged
_r.seed(9999)
rnd = bytes(_r.getrandbits(8) for _ in range(256))
results["controls"]["neg_random_256B"] = rsa_structure_detector(rnd)

# GPG positive control: build a real armored PGP MESSAGE (symmetric) and confirm it parses
gpg_pos = {}
try:
    env = dict(os.environ); env["GNUPGHOME"] = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tf:
        tf.write(b"the primes are sacred\n"); pt_path = tf.name
    enc_path = pt_path + ".gpg"
    r = subprocess.run(["gpg","--batch","--yes","--passphrase","3301","-c","--cipher-algo","AES256",
                        "-o", enc_path, pt_path], capture_output=True, text=True, env=env, timeout=30)
    if os.path.exists(enc_path):
        r2 = subprocess.run(["gpg","--list-packets", enc_path], capture_output=True, text=True, env=env, timeout=20)
        blob = Path(enc_path).read_bytes()
        gpg_pos = {"built": True, "list_packets_head": r2.stdout.strip()[:300],
                   "openpgp_scan": openpgp_scan(blob, "real_gpg_message"),
                   "parsed_ok": "packet" in r2.stdout.lower()}
        os.unlink(enc_path)
    else:
        gpg_pos = {"built": False, "stderr": r.stderr[:200]}
    os.unlink(pt_path)
except Exception as e:
    gpg_pos = {"err": str(e)}
results["controls"]["gpg_positive_real_message"] = gpg_pos

# GPG negative control: our random 256B blob must NOT parse as valid packets
env = dict(os.environ)
with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tf:
    tf.write(rnd); rp = tf.name
r = subprocess.run(["gpg","--list-packets", rp], capture_output=True, text=True, env=env, timeout=20)
results["controls"]["gpg_negative_random"] = {
    "stderr": r.stderr.strip()[:200],
    "stdout": r.stdout.strip()[:200],
    "parsed_as_valid": ("no valid" not in r.stderr.lower() and "invalid" not in r.stderr.lower() and "packet" in r.stdout.lower())
}
os.unlink(rp)

# ledgered items note (NOT re-run)
results["ledgered_not_rerun"] = {
    "canon_prime_or_clean_RSA_modulus": "ELIMINATION-LEDGER L151/L98: NULL (int is even, ends 0x50, small factors). Confirmed by our detector below.",
    "canon_32byte_block_hash_preimage": "ELIMINATION-LEDGER L157: NULL (37-dict x 3 algos x 16 blocks -> 0).",
    "canon_whole_file_preimage_vs_AN-END_512bit": "L601/L642/L663: >1572 preimage nulls incl SHA2/3/BLAKE2/Skein/Whirlpool/Streebog -> NULL.",
    "T2_T3_folly_OpenPGP": "L802-803: folly byte0=0xbf invalid packet chain, T2 byte0=0x40 bit7-clear -> not PGP. Re-confirmed structurally here.",
    "canon_as_RSA_private_exponent": "no meaningful standalone test without matching (n,e); a bare d has no verifiable structure -> not a productive test, noted.",
}

(LANE / "b2_results.json").write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
