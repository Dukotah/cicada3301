"""Lane B1 -- External-key symmetric-cipher battery on the 3 genuinely-random blobs.

Blobs (from Round 29 L2-blob-cross, the ONLY three artifacts proven ~uniform-random):
  T2   : analysis/armada_osint/extracts/T2.bin           7524 B  (2.jpg stage04 payload)
  folly: analysis/armada_osint/artifacts/folly.bin       3368 B
  canon: analysis/pp49_51/canon_256.bin                   256 B

Battery:
  (1) structural crypto-ID: length%8/16, byte histogram, chi-square vs uniform,
      block-repeat detection (ECB tell), entropy.
  (2) each blob as CIPHERTEXT under AES-{128,192,256}-{ECB,CBC}, RC4, Blowfish,
      DES, 3DES, plus openssl/gpg symmetric -- keyed by every Cicada-derivable key.
      Success = magic header (PGP/gzip/zlib/PDF/PNG/bzip2/xz) OR readable ASCII/English.
  (3) blob-as-keystream over blob (XOR each pair, look for structure).

Controls:
  POSITIVE: encrypt a known plaintext under AES-256-CBC with a known key; confirm
            the harness decrypts it back and the success-detector fires.
  NEGATIVE: decrypt real random bytes under a wrong key; confirm detector stays SILENT
            (avoid the wrong-key-artifact trap).
"""
import os, sys, json, hashlib, string, itertools, collections, math

from Crypto.Cipher import AES, ARC4, Blowfish, DES, DES3
from Crypto.Util.Padding import unpad

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

BLOBS = {
    "T2":    os.path.join(ROOT, "analysis", "armada_osint", "extracts", "T2.bin"),
    "folly": os.path.join(ROOT, "analysis", "armada_osint", "artifacts", "folly.bin"),
    "canon": os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin"),
}

# ---------------------------------------------------------------- magic headers
MAGICS = {
    b"\x1f\x8b\x08":            "gzip",
    b"\x78\x01":                "zlib-low",
    b"\x78\x9c":                "zlib-default",
    b"\x78\xda":                "zlib-best",
    b"BZh":                     "bzip2",
    b"\xfd7zXZ\x00":            "xz",
    b"PK\x03\x04":              "zip",
    b"%PDF":                    "pdf",
    b"\x89PNG":                 "png",
    b"\xff\xd8\xff":            "jpeg",
    b"-----BEGIN PGP":          "pgp-armor",
    b"\x85":                    "pgp-binary-maybe",   # OpenPGP old-format packet tag, weak
    b"\x99":                    "pgp-pubkey-maybe",
    b"\xc1":                    "pgp-new-format-maybe",
    b"SQLite format 3":         "sqlite",
    b"\x37\x03":                "gpg-symmetric-maybe",
}

PRINTABLE = set(bytes(string.printable, "ascii"))
COMMON_WORDS = [b"THE", b"AND", b"CICADA", b"3301", b"PRIME", b"WELCOME",
                b"PILGRIM", b"WISDOM", b"INSTAR", b"DIVINITY", b"TRUTH",
                b"SACRED", b"the ", b"and ", b" of ", b"http", b"BEGIN"]

def shannon(bs):
    if not bs: return 0.0
    c = collections.Counter(bs); n = len(bs)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def looks_english(bs):
    """Return (score, reason) if plausibly readable text, else (0, '')."""
    if len(bs) < 8:
        return 0, ""
    printable = sum(1 for b in bs if b in PRINTABLE)
    frac = printable / len(bs)
    if frac < 0.85:
        return 0, ""
    up = bs.upper()
    hits = [w for w in COMMON_WORDS if w.upper() in up]
    score = frac + 0.5*len(hits)
    if len(hits) >= 2 or (frac > 0.97 and len(bs) > 16):
        return score, f"printable={frac:.2f} words={[w.decode(errors='replace') for w in hits]}"
    return 0, ""

def check_magic(bs):
    for sig, name in MAGICS.items():
        if bs.startswith(sig):
            # weak single-byte PGP tags: only flag if not super common
            if name.endswith("-maybe") and len(sig) < 2:
                continue
            return name
    return None

def detect_success(pt):
    """The success detector used everywhere. Returns list of (kind, detail)."""
    hits = []
    m = check_magic(pt)
    if m:
        hits.append(("magic", m))
    esc, reason = looks_english(pt)
    if esc:
        hits.append(("english", reason))
    return hits

# ---------------------------------------------------------------- key material
def load_keys():
    keys = {}   # name -> bytes (raw key material, hashed/truncated per-cipher at use)
    # numeric constants
    for n in ["3301", "1595277641", "509", "503", "13", "1033", "761", "3","301"]:
        keys[f"num:{n}"] = n.encode()
    # page-56 512-bit hash (hex string form AND raw bytes form)
    h = "36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"
    keys["hash56:hexstr"] = h.encode()
    keys["hash56:raw"] = bytes.fromhex(h)
    # solved-english concatenation (the whole decoded corpus as one string) + phrases
    try:
        eng = open(os.path.join(ROOT, "analysis", "armada20", "key_solved_english.txt"), "rb").read().strip()
        keys["solved:full"] = eng
    except Exception:
        eng = b""
    phrases = [
        b"WELCOMEPILGRIM", b"THEPRIMESARESACRED", b"THETOTIENTFUNCTIONISSACRED",
        b"ALLTHINGSSHOULDBEENCRYPTED", b"QUESTIONALLTHINGS", b"DIVINITYWITHIN",
        b"ANEND", b"WITHINTHEDEEPWEB", b"AWARENING", b"CIRCUMFERENCE",
        b"KNOWTHIS", b"INSTAR", b"EMERGENCE", b"AWARENESS", b"PARABLE",
        b"WELCOME", b"CICADA3301", b"LIBERPRIMUS", b"AWAKEN",
    ]
    for p in phrases:
        keys[f"phrase:{p.decode()}"] = p
    # canonical passphrases known from Cicada history
    for p in [b"firfumferenfe", b"a warning", b"parable", b"the loss of divinity",
              b"an end", b"instar emergence"]:
        keys[f"cic:{p.decode().replace(' ','_')}"] = p
    return keys, eng

# ---------------------------------------------------------------- key adapters
def fit_key(raw, length, mode="hash"):
    """Produce a key of exactly `length` bytes from raw material.
       mode 'hash' -> sha256/sha512-derived; mode 'trunc' -> truncate/zero-pad raw."""
    if mode == "trunc":
        if len(raw) >= length:
            return raw[:length]
        return raw + b"\x00" * (length - len(raw))
    # hash mode
    if length <= 32:
        return hashlib.sha256(raw).digest()[:length]
    elif length <= 64:
        return hashlib.sha512(raw).digest()[:length]
    else:
        out = b""
        i = 0
        while len(out) < length:
            out += hashlib.sha512(raw + bytes([i])).digest()
            i += 1
        return out[:length]

# ---------------------------------------------------------------- cipher trials
def try_aes(ct, key_raw, results, tag):
    for klen, name in [(16,"AES-128"),(24,"AES-192"),(32,"AES-256")]:
        for kmode in ("hash","trunc"):
            k = fit_key(key_raw, klen, kmode)
            # ECB (requires block-multiple)
            if len(ct) % 16 == 0:
                try:
                    pt = AES.new(k, AES.MODE_ECB).decrypt(ct)
                    for kind, det in detect_success(pt):
                        results.append((f"{name}-ECB k={kmode}", tag, kind, det, pt[:64].hex()))
                except Exception:
                    pass
            # CBC with IV = first 16 bytes as IV, rest as ct  (common convention)
            if len(ct) >= 32 and (len(ct)-16) % 16 == 0:
                try:
                    iv, body = ct[:16], ct[16:]
                    pt = AES.new(k, AES.MODE_CBC, iv).decrypt(body)
                    for kind, det in detect_success(pt):
                        results.append((f"{name}-CBC(IV=head) k={kmode}", tag, kind, det, pt[:64].hex()))
                except Exception:
                    pass
            # CBC with zero IV over full ct
            if len(ct) % 16 == 0:
                try:
                    pt = AES.new(k, AES.MODE_CBC, b"\x00"*16).decrypt(ct)
                    for kind, det in detect_success(pt):
                        results.append((f"{name}-CBC(IV=0) k={kmode}", tag, kind, det, pt[:64].hex()))
                except Exception:
                    pass

def try_rc4(ct, key_raw, results, tag):
    for kmode in ("hash","trunc"):
        k = fit_key(key_raw, 32, kmode)
        try:
            pt = ARC4.new(k).decrypt(ct)
            for kind, det in detect_success(pt):
                results.append((f"RC4 k={kmode}", tag, kind, det, pt[:64].hex()))
        except Exception:
            pass
        # also raw key (RC4 takes 1..256 byte keys)
        try:
            rk = key_raw[:256] if len(key_raw) else b"\x00"
            pt = ARC4.new(rk).decrypt(ct)
            for kind, det in detect_success(pt):
                results.append((f"RC4 k=raw", tag, kind, det, pt[:64].hex()))
        except Exception:
            pass

def try_blowfish(ct, key_raw, results, tag):
    if len(ct) % 8 != 0:
        return
    for kmode in ("hash","trunc"):
        k = fit_key(key_raw, 16, kmode)
        for mode, iv in [(Blowfish.MODE_ECB, None), (Blowfish.MODE_CBC, b"\x00"*8)]:
            try:
                c = Blowfish.new(k, mode) if iv is None else Blowfish.new(k, mode, iv)
                pt = c.decrypt(ct)
                mname = "ECB" if iv is None else "CBC(IV=0)"
                for kind, det in detect_success(pt):
                    results.append((f"Blowfish-{mname} k={kmode}", tag, kind, det, pt[:64].hex()))
            except Exception:
                pass

def try_des(ct, key_raw, results, tag):
    if len(ct) % 8 != 0:
        return
    for kmode in ("hash","trunc"):
        k = fit_key(key_raw, 8, kmode)
        for mode, iv in [(DES.MODE_ECB, None), (DES.MODE_CBC, b"\x00"*8)]:
            try:
                c = DES.new(k, mode) if iv is None else DES.new(k, mode, iv)
                pt = c.decrypt(ct)
                mname = "ECB" if iv is None else "CBC(IV=0)"
                for kind, det in detect_success(pt):
                    results.append((f"DES-{mname} k={kmode}", tag, kind, det, pt[:64].hex()))
            except Exception:
                pass
        # 3DES (24-byte key)
        k3 = fit_key(key_raw, 24, kmode)
        try:
            k3 = DES3.adjust_key_parity(k3)
        except Exception:
            pass
        for mode, iv in [(DES3.MODE_ECB, None), (DES3.MODE_CBC, b"\x00"*8)]:
            try:
                c = DES3.new(k3, mode) if iv is None else DES3.new(k3, mode, iv)
                pt = c.decrypt(ct)
                mname = "ECB" if iv is None else "CBC(IV=0)"
                for kind, det in detect_success(pt):
                    results.append((f"3DES-{mname} k={kmode}", tag, kind, det, pt[:64].hex()))
            except Exception:
                pass

def run_cipher_battery(ct, tag, keys, results):
    for kname, kraw in keys.items():
        t = f"{tag}|{kname}"
        try_aes(ct, kraw, results, t)
        try_rc4(ct, kraw, results, t)
        try_blowfish(ct, kraw, results, t)
        try_des(ct, kraw, results, t)

# ---------------------------------------------------------------- structural ID
def struct_id(name, bs):
    n = len(bs)
    c = collections.Counter(bs)
    # chi-square vs uniform over 256 symbols
    exp = n/256
    chi = sum((c.get(b,0)-exp)**2/exp for b in range(256))
    # ECB tell: any repeated 16-byte block?
    blocks16 = [bytes(bs[i:i+16]) for i in range(0, n-n%16, 16)]
    rep16 = len(blocks16) - len(set(blocks16))
    return {
        "name": name, "len": n,
        "len_mod_8": n % 8, "len_mod_16": n % 16,
        "entropy_bits_per_byte": round(shannon(bs), 5),
        "distinct_byte_values": len(c),
        "chi_square_vs_uniform": round(chi, 2),
        "chi_df": 255,
        # df=255: mean 255, sd ~22.6; |chi-255|<~66 => consistent-with-uniform (3 sigma)
        "chi_consistent_uniform": abs(chi-255) < 70,
        "repeated_16B_blocks": rep16,
        "first16_hex": bs[:16].hex(),
        "min_count": min(c.values()), "max_count": max(c.values()),
    }
