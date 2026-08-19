"""Round 13 / B-05 -- PRF expansion of the pp49-51 256-byte payload into a runic keystream.

RECON-A B-05: "pp49-51's 256-byte payload as a PRF SEED expanded into a runic keystream
(RC4 / AES-CTR / SHA-counter / HMAC-DRBG), rather than used directly as key material.
Campaign XX applied AES/RC4/ChaCha to the payload as *ciphertext*; nobody expanded it
into a keystream over the runes."   -- status: never-run.

This module holds only the primitives: payload representations, PRF generators, and the
two mod-29 reductions.  The sweep, the control and the meta-parameter tests import it.

Pure stdlib except `cryptography` (already a repo dependency; Campaign XX used it).
"""
import os
import hashlib
import hmac

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PP = os.path.join(ROOT, "analysis", "pp49_51")

N = 29

# ------------------------------------------------------------------ payload
CONTESTED = [25, 175, 182, 199, 215, 237]   # RECON-A A-04


def load_payloads():
    """The two adjudicated 256-byte canonical payloads."""
    maj = open(os.path.join(PP, "canon_256.bin"), "rb").read()
    dec = open(os.path.join(PP, "canon_256_decpref.bin"), "rb").read()
    assert len(maj) == len(dec) == 256
    return maj, dec


def contested_alternatives():
    """[(idx, token_value, decimal_value), ...] -- exactly two candidates per index."""
    maj, dec = load_payloads()
    return [(i, maj[i], dec[i]) for i in CONTESTED]


# --------------------------------------------------- payload representations
def _bitrev_byte(b):
    return int(f"{b:08b}"[::-1], 2)


def _bitrev_all(bs):
    """Reverse the whole bitstream: equivalent to byte-reverse then per-byte bit-reverse."""
    return bytes(_bitrev_byte(b) for b in bs[::-1])


def _swap32(bs):
    out = bytearray()
    for i in range(0, len(bs), 4):
        out += bs[i:i + 4][::-1]
    return bytes(out)


def _swap16(bs):
    out = bytearray()
    for i in range(0, len(bs), 2):
        out += bs[i:i + 2][::-1]
    return bytes(out)


REPR_FNS = {
    "raw":      lambda b: b,
    "byterev":  lambda b: b[::-1],                       # little-endian integer reading
    "bitrev8":  lambda b: bytes(_bitrev_byte(x) for x in b),
    "bitrevall": _bitrev_all,
    "swap32":   _swap32,                                 # endianness variant (characterize.py)
    "hexascii": lambda b: b.hex().encode(),              # the form a human would paste
}
# swap16 is kept available for ad-hoc use but is not in the pinned grid
REPR_FNS_EXTRA = {"swap16": _swap16}


def representations():
    """dict name -> seed bytes.  12 entries (2 adjudications x 6 forms)."""
    maj, dec = load_payloads()
    out = {}
    for base_name, base in (("maj", maj), ("dec", dec)):
        for rname, fn in REPR_FNS.items():
            out[f"{base_name}.{rname}"] = fn(base)
    return out


# ------------------------------------------------------------- PRF generators
# Each returns `nbytes` of raw keystream BYTES from the seed.  Reduction to mod 29
# happens afterwards so that rejection sampling can be applied to the same byte stream.

def _ctr(seed, nbytes, algo, ctr_bytes=4, endian="big"):
    out = bytearray()
    ctr = 0
    while len(out) < nbytes:
        out += hashlib.new(algo, seed + ctr.to_bytes(ctr_bytes, endian)).digest()
        ctr += 1
    return bytes(out[:nbytes])


def _chain(seed, nbytes, algo):
    out = bytearray()
    h = hashlib.new(algo, seed).digest()
    while len(out) < nbytes:
        out += h
        h = hashlib.new(algo, h).digest()
    return bytes(out[:nbytes])


def _hmac_drbg(seed, nbytes, algo="sha256"):
    """NIST SP800-90A HMAC_DRBG, payload as entropy input, empty nonce/personalization."""
    hlen = hashlib.new(algo).digest_size
    K = b"\x00" * hlen
    V = b"\x01" * hlen

    def update(provided):
        nonlocal K, V
        K = hmac.new(K, V + b"\x00" + provided, algo).digest()
        V = hmac.new(K, V, algo).digest()
        if provided:
            K = hmac.new(K, V + b"\x01" + provided, algo).digest()
            V = hmac.new(K, V, algo).digest()

    update(seed)                      # instantiate
    out = bytearray()
    while len(out) < nbytes:
        V = hmac.new(K, V, algo).digest()
        out += V
    update(b"")                       # reseed-counter update (spec-faithful, unused)
    return bytes(out[:nbytes])


def _rc4(key, nbytes):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    out = bytearray()
    i = j = 0
    while len(out) < nbytes:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)


def _aes_ctr(key, iv, nbytes):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    c = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
    return c.update(b"\x00" * nbytes)


def _chacha20(key, nonce, nbytes):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
    c = Cipher(algorithms.ChaCha20(key, nonce), None).encryptor()
    return c.update(b"\x00" * nbytes)


def _pad32(seed, n):
    """Seeds shorter than n bytes (never happens for the 256-byte payload, but the
    hexascii representation is longer, and this keeps every generator total)."""
    if len(seed) >= n:
        return seed[:n]
    return (seed * ((n // len(seed)) + 1))[:n]


GENERATORS = {
    "md5_ctr":          lambda s, n: _ctr(s, n, "md5"),
    "sha1_ctr":         lambda s, n: _ctr(s, n, "sha1"),
    "sha256_ctr":       lambda s, n: _ctr(s, n, "sha256"),
    "sha512_ctr":       lambda s, n: _ctr(s, n, "sha512"),
    "sha256_ctr_le":    lambda s, n: _ctr(s, n, "sha256", endian="little"),
    "sha256_chain":     lambda s, n: _chain(s, n, "sha256"),
    "sha512_chain":     lambda s, n: _chain(s, n, "sha512"),
    "hmac_drbg_sha256": lambda s, n: _hmac_drbg(s, n, "sha256"),
    "aes256_ctr_k":     lambda s, n: _aes_ctr(_pad32(s, 32), b"\x00" * 16, n),
    "aes256_ctr_kiv":   lambda s, n: _aes_ctr(_pad32(s, 32), _pad32(s[32:] or s, 16), n),
    "aes128_ctr_k":     lambda s, n: _aes_ctr(_pad32(s, 16), b"\x00" * 16, n),
    "rc4":              lambda s, n: _rc4(s, n),
    "chacha20_k":       lambda s, n: _chacha20(_pad32(s, 32), b"\x00" * 16, n),
    "chacha20_kn":      lambda s, n: _chacha20(_pad32(s, 32), _pad32(s[32:] or s, 16), n),
    "shake256":         lambda s, n: hashlib.shake_256(s).digest(n),
}


# ------------------------------------------------------------- mod-29 reduction
def reduce_mod(bs, mode="mod"):
    """`mod`  : every byte -> b % 29   (slightly biased: 0..23 get 9 preimages, 24..28 get 8)
       `reject`: unbiased rejection sampling -- keep bytes < 232 (=8*29), drop the rest."""
    if mode == "mod":
        return [b % N for b in bs]
    if mode == "reject":
        return [b % N for b in bs if b < 232]
    raise ValueError(mode)


def keystream(seed, gen, red, nvals):
    """Expand `seed` under generator `gen`, reduce mod 29 under `red`, return >= nvals values."""
    fn = GENERATORS[gen]
    # rejection sampling discards ~9.4% of bytes; ask for 25% headroom, then top up.
    nb = int(nvals * 1.30) + 64
    for _ in range(6):
        ks = reduce_mod(fn(seed, nb), red)
        if len(ks) >= nvals:
            return ks[:nvals]
        nb = int(nb * 1.5) + 64
    return ks


def atbash(ks):
    return [(N - 1 - k) % N for k in ks]


if __name__ == "__main__":
    maj, dec = load_payloads()
    print("payload majority  sha256:", hashlib.sha256(maj).hexdigest()[:32])
    print("payload decpref   sha256:", hashlib.sha256(dec).hexdigest()[:32])
    print("contested (idx, token, decimal):", contested_alternatives())
    reps = representations()
    print(f"{len(reps)} representations:", ", ".join(sorted(reps)))
    print(f"{len(GENERATORS)} generators:", ", ".join(GENERATORS))
    for g in GENERATORS:
        k = keystream(maj, g, "reject", 40)
        print(f"  {g:18s} -> {k[:12]}")
