"""ROUND 13 / B-04 — cryptographic keystream generators + mod-29 reductions.

This is the B-04 family the RECON-A register lists as NEVER-RUN: MD5 / SHA-1 /
SHA-256 / SHA-512 in chain and counter mode, HMAC (SP800-108 counter KDF),
HMAC-DRBG, AES-CTR, RC4, ChaCha20 — each expanded from a SHORT SEED into a byte
stream and reduced to Z_29.

Everything is deterministic and depends only on `hashlib`/`hmac` from the stdlib
plus (for AES/ChaCha) `cryptography`, which is present in this environment; if it
is absent those two generators are dropped and the drop is recorded in
results.json rather than silently ignored.
"""
import hashlib, hmac

N = 29

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives.ciphers.algorithms import ChaCha20
    _HAVE_CRYPTO = True
except Exception:                                       # pragma: no cover
    _HAVE_CRYPTO = False


# ------------------------------------------------------------------ byte streams
def _ctr(hfun, seed, nbytes, order="big", ascii_ctr=False):
    out, c = bytearray(), 0
    while len(out) < nbytes:
        tag = str(c).encode() if ascii_ctr else c.to_bytes(4, order)
        out += hfun(seed + tag).digest()
        c += 1
    return bytes(out[:nbytes])


def _chain(hfun, seed, nbytes):
    out, h = bytearray(), hfun(seed).digest()
    while len(out) < nbytes:
        out += h
        h = hfun(h).digest()
    return bytes(out[:nbytes])


def _hmac_ctr(seed, nbytes):
    """NIST SP800-108 counter-mode KDF shape: HMAC(key=seed, msg=ctr)."""
    out, c = bytearray(), 0
    while len(out) < nbytes:
        out += hmac.new(seed, c.to_bytes(4, "big"), hashlib.sha256).digest()
        c += 1
    return bytes(out[:nbytes])


def _hmac_drbg(seed, nbytes):
    """HMAC-DRBG(SHA-256), NIST SP800-90A: instantiate with seed, generate."""
    K = b"\x00" * 32
    V = b"\x01" * 32
    K = hmac.new(K, V + b"\x00" + seed, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    K = hmac.new(K, V + b"\x01" + seed, hashlib.sha256).digest()
    V = hmac.new(K, V, hashlib.sha256).digest()
    out = bytearray()
    while len(out) < nbytes:
        V = hmac.new(K, V, hashlib.sha256).digest()
        out += V
    return bytes(out[:nbytes])


def _rc4(seed, nbytes):
    S = list(range(256))
    j = 0
    kl = len(seed)
    for i in range(256):
        j = (j + S[i] + seed[i % kl]) & 0xFF
        S[i], S[j] = S[j], S[i]
    out = bytearray()
    i = j = 0
    for _ in range(nbytes):
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)


def _aes_ctr(seed, nbytes, derived_iv=False):
    key = hashlib.sha256(seed).digest()
    iv = hashlib.md5(seed).digest() if derived_iv else b"\x00" * 16
    enc = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return enc.update(b"\x00" * nbytes)


def _chacha20(seed, nbytes):
    key = hashlib.sha256(seed).digest()
    nonce = b"\x00" * 16
    enc = Cipher(ChaCha20(key, nonce), None).encryptor()
    return enc.update(b"\x00" * nbytes)


GENERATORS = {
    "sha256_ctr":      lambda s, n: _ctr(hashlib.sha256, s, n),
    "sha512_ctr":      lambda s, n: _ctr(hashlib.sha512, s, n),
    "sha1_ctr":        lambda s, n: _ctr(hashlib.sha1, s, n),
    "md5_ctr":         lambda s, n: _ctr(hashlib.md5, s, n),
    "sha256_ctr_le":   lambda s, n: _ctr(hashlib.sha256, s, n, order="little"),
    "sha256_ctr_asc":  lambda s, n: _ctr(hashlib.sha256, s, n, ascii_ctr=True),
    "sha256_chain":    lambda s, n: _chain(hashlib.sha256, s, n),
    "sha512_chain":    lambda s, n: _chain(hashlib.sha512, s, n),
    "sha1_chain":      lambda s, n: _chain(hashlib.sha1, s, n),
    "md5_chain":       lambda s, n: _chain(hashlib.md5, s, n),
    "hmac_sha256_ctr": _hmac_ctr,
    "hmac_drbg_sha256": _hmac_drbg,
    "rc4":             _rc4,
}
if _HAVE_CRYPTO:
    GENERATORS["aes_ctr_zeroiv"] = lambda s, n: _aes_ctr(s, n, False)
    GENERATORS["aes_ctr_deriviv"] = lambda s, n: _aes_ctr(s, n, True)
    GENERATORS["chacha20"] = _chacha20

GEN_NAMES = list(GENERATORS)


# ------------------------------------------------------------------ reductions
def r_mod29(b):
    return [x % N for x in b]


def r_rej29(b):
    """Unbiased rejection sampling: 232 = 8*29, so bytes < 232 are uniform mod 29."""
    return [x % N for x in b if x < 232]


def r_hi_nib(b):
    return [(x >> 4) % N for x in b]


def r_lo_nib(b):
    return [x & 0x0F for x in b]


def r_bits5(b):
    """5-bit groups off the bit stream, rejecting groups >= 29 (values 29..31)."""
    out, acc, nb = [], 0, 0
    for x in b:
        acc = (acc << 8) | x
        nb += 8
        while nb >= 5:
            v = (acc >> (nb - 5)) & 0x1F
            nb -= 5
            acc &= (1 << nb) - 1
            if v < N:
                out.append(v)
    return out


REDUCTIONS = {
    "mod29": r_mod29,
    "rej29": r_rej29,
    "hi_nib": r_hi_nib,
    "lo_nib": r_lo_nib,
    "bits5": r_bits5,
}
RED_NAMES = list(REDUCTIONS)

# how many bytes are needed per output symbol, worst case (with slack)
_YIELD = {"mod29": 1.0, "rej29": 1.20, "hi_nib": 1.0, "lo_nib": 1.0, "bits5": 0.95}


def make_bytes(gen, seed, nbytes):
    return GENERATORS[gen](seed, nbytes)


def make_ks(gen, red, seed, nsym, raw=None):
    """Return >= nsym keystream symbols in Z_29 (or Z_16 for lo_nib)."""
    need = int(nsym * _YIELD[red]) + 128
    b = raw[:need] if (raw is not None and len(raw) >= need) else make_bytes(gen, seed, need)
    ks = REDUCTIONS[red](b)
    while len(ks) < nsym:
        need *= 2
        b = make_bytes(gen, seed, need)
        ks = REDUCTIONS[red](b)
    return ks


if __name__ == "__main__":
    for g in GEN_NAMES:
        b = make_bytes(g, b"CICADA3301", 32)
        print(f"{g:18s} {b[:16].hex()}")
    print("reductions:", RED_NAMES, "  crypto backend:", _HAVE_CRYPTO)
