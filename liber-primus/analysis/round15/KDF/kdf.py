"""Round 15 / KDF — key-stretching keystream generators.

Each function takes (secret: bytes, salt: bytes) and returns 64 bytes of derived key
material. The full runic keystream is then expanded from that block by SHA-256 counter
mode (`expand`), which is the same expander D3's positive control validated.

Deliberately excluded: Argon2 (PHC winner 2015, after LP2's 2014 publication — including
it would be anachronistic) and bcrypt (no natural long-output mode). Recorded in PREREG §4.2
so the absences read as decisions.
"""
import hashlib, hmac

N = 29
DK = 64                       # derived block length, bytes


# ---------------------------------------------------------------- KDFs
def pbkdf2(secret, salt, iters, hashname):
    return hashlib.pbkdf2_hmac(hashname, secret, salt, iters, dklen=DK)


def scrypt_rfc(secret, salt):
    """RFC 7914 'interactive' parameters — the era's common recommendation."""
    return hashlib.scrypt(secret, salt=salt, n=16384, r=8, p=1, dklen=DK, maxmem=64 << 20)


def iterated(secret, salt, rounds, hashname):
    """Plain iterated hashing: h = H(h), the naive stretch an author might hand-roll."""
    h = hashlib.new(hashname, salt + secret).digest()
    for _ in range(rounds):
        h = hashlib.new(hashname, h).digest()
    out = b""
    ctr = 0
    while len(out) < DK:
        out += hashlib.new(hashname, h + ctr.to_bytes(4, "big")).digest()
        ctr += 1
    return out[:DK]


def evp_bytestokey(secret, salt, rounds, hashname):
    """OpenSSL EVP_BytesToKey — period-ubiquitous (it is what `openssl enc` used by
    default), and exactly the sort of thing a 2013 author would reach for without
    thinking about it."""
    d = b""
    out = b""
    while len(out) < DK:
        d = hashlib.new(hashname, d + secret + salt).digest()
        for _ in range(rounds - 1):
            d = hashlib.new(hashname, d).digest()
        out += d
    return out[:DK]


# Pre-registered grid (PREREG s4.2). 3301 appears in every family: this author signs
# everything with it.
KDFS = []
for it in (1000, 2048, 4096, 10000, 100000):
    KDFS.append((f"pbkdf2_sha1_{it}", lambda s, sa, it=it: pbkdf2(s, sa, it, "sha1")))
    KDFS.append((f"pbkdf2_sha256_{it}", lambda s, sa, it=it: pbkdf2(s, sa, it, "sha256")))
for it in (1000, 4096, 10000):
    KDFS.append((f"pbkdf2_sha512_{it}", lambda s, sa, it=it: pbkdf2(s, sa, it, "sha512")))
KDFS.append(("pbkdf2_sha256_3301", lambda s, sa: pbkdf2(s, sa, 3301, "sha256")))
KDFS.append(("pbkdf2_sha1_3301", lambda s, sa: pbkdf2(s, sa, 3301, "sha1")))
KDFS.append(("scrypt_16384_8_1", scrypt_rfc))
for r in (1000, 10000, 100000, 3301):
    KDFS.append((f"iter_sha256_{r}", lambda s, sa, r=r: iterated(s, sa, r, "sha256")))
for r in (1000, 10000, 3301):
    KDFS.append((f"iter_md5_{r}", lambda s, sa, r=r: iterated(s, sa, r, "md5")))
for r in (1, 3301):
    KDFS.append((f"evp_md5_{r}", lambda s, sa, r=r: evp_bytestokey(s, sa, r, "md5")))
    KDFS.append((f"evp_sha256_{r}", lambda s, sa, r=r: evp_bytestokey(s, sa, r, "sha256")))

KDF_NAMES = [n for n, _ in KDFS]
KDF_MAP = dict(KDFS)

# PREREG s4.3
SALTS = {
    "empty": b"",
    "3301": b"3301",
    "cicada": b"cicada",
    "CICADA": b"CICADA",
    "Cicada": b"Cicada",
    "cicada3301": b"cicada3301",
    "onion2014": b"ky2khlqdf7qdznac",
    "1033": b"1033",
    "761": b"761",
    "self": None,            # salt = the secret itself (a common lazy construction)
    "anend16": bytes.fromhex("36367763ab73783c7af284446c"
                             "59466b4cd653239a311cb7116d")[:16],
}


def expand(block, nsym, reduction="mod29"):
    """Derive-then-expand: SHA-256 counter mode over the KDF output block, reduced to Z29."""
    out = []
    ctr = 0
    if reduction == "mod29":
        while len(out) < nsym:
            h = hashlib.sha256(block + ctr.to_bytes(4, "big")).digest()
            out.extend(b % N for b in h)
            ctr += 1
    elif reduction == "rej29":
        # unbiased: keep bytes < 232 = 8*29, then mod. What a careful author would do.
        while len(out) < nsym:
            h = hashlib.sha256(block + ctr.to_bytes(4, "big")).digest()
            out.extend(b % N for b in h if b < 232)
            ctr += 1
    else:
        raise ValueError(reduction)
    return out[:nsym]


def derive(secret, salt_name, kdf_name):
    salt = SALTS[salt_name]
    if salt is None:
        salt = secret
    return KDF_MAP[kdf_name](secret, salt)


def keystream(secret, salt_name, kdf_name, nsym, reduction="mod29"):
    return expand(derive(secret, salt_name, kdf_name), nsym, reduction)
