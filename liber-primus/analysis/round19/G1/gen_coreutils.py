"""Round 19 / G1 -- the coreutils / openssl siblings L1 names alongside bash $RANDOM
(round18/L1-toolchain/RESULTS.md section 6.2 row 4: "Bash/coreutils composites --
$RANDOM, /dev/urandom, shuf --random-source, openssl rand", x2, "never swept").

This module deliberately does NOT pretend all four are searchable.  Each one gets a
precise reachability statement, and only the reachable ones get a generator.

  shuf --random-source=FILE   REACHABLE, but DICTIONARY-shaped, not seed-shaped.
                              Implemented as an ORACLE around the real installed
                              `shuf` binary -- no reimplementation, so nothing to
                              mis-validate.  Version caveat in RESULTS.md section 5.
  shuf  (no --random-source)  UNREACHABLE: coreutils randread() opens /dev/urandom.
  openssl rand N              UNREACHABLE: OpenSSL 1.0.1's RAND_bytes is seeded from
                              /dev/urandom + PID + time.  There is no `-seed`/`-pass`
                              option; `-rand FILE` only ADDS FILE to a pool that still
                              contains OS entropy.  A passphrase cannot produce it.
  openssl enc -k PASS         REACHABLE and deterministic: EVP_BytesToKey(MD5) derives
                              key+IV from the passphrase, and encrypting a zero stream
                              with RC4 (or AES-CTR) yields a keystream.  This IS the
                              "openssl with a short passphrase" object; it is a
                              dictionary over passphrases, overlapping LEDGER R16-KDF.
  /dev/urandom                UNREACHABLE, permanently.  No seed, no record.  Stated,
                              not swept.  (bash 5.1's $SRANDOM reads it too -- and did
                              not exist until 2020, four years after LP2, so it is
                              excluded by date as well.)

REACHABILITY is a property of the object, not of our effort.  Nothing here reports a
null for an unreachable object.
"""
import hashlib
import os
import subprocess

N = 29

# ---------------------------------------------------------------- reachability table
REACHABILITY = {
    "dev_urandom": {
        "reachable": False,
        "why": "No seed and no public record. The kernel CSPRNG state is entropy from "
               "interrupt timing; nothing about it is recoverable from the ciphertext "
               "or from any artifact. This is the branch ARMADA-DOCTRINE section 5 calls "
               "possibly the true one and beyond any instrument.",
        "swept": "NOT SWEPT, and cannot be. Any claim otherwise is false.",
    },
    "shuf_default": {
        "reachable": False,
        "why": "coreutils randread_new() with no --random-source opens /dev/urandom "
               "(falling back to an AES/ISAAC pool seeded from it). Same argument as "
               "dev_urandom.",
        "swept": "NOT SWEPT, and cannot be.",
    },
    "openssl_rand": {
        "reachable": False,
        "why": "`openssl rand` has no passphrase/seed option in any 1.0.x release. "
               "RAND_bytes draws from a pool seeded by /dev/urandom, getpid() and "
               "time(); `-rand FILE` only stirs FILE INTO that pool, it does not "
               "replace it. A 2012 author could not reproduce their own pad this way, "
               "which is the whole point of using a generator.",
        "swept": "NOT SWEPT, and cannot be. The brief's phrase 'openssl rand with a "
                 "short passphrase' does not name a real command; the real object with "
                 "that shape is openssl_enc_k below.",
    },
    "shuf_random_source": {
        "reachable": True,
        "why": "`shuf -i 0-28 -r -n L --random-source=FILE` is a deterministic function "
               "of FILE's bytes. The space is the space of FILES, so it is a DICTIONARY, "
               "not an enumerable seed range.",
        "swept": "never swept",
    },
    "openssl_enc_k": {
        "reachable": True,
        "why": "EVP_BytesToKey(MD5, no salt, count 1) over a passphrase gives key+IV; "
               "encrypting zeros gives a deterministic keystream. Dictionary over "
               "passphrases. Overlaps LEDGER R16-KDF (692,064 configs) -- S1 must "
               "de-duplicate rather than re-run.",
        "swept": "partly (R16-KDF); the EVP_BytesToKey key schedule specifically is not "
                 "named in R16-KDF's coverage field",
    },
}


# ------------------------------------------------------------------ shuf, as an oracle
# Ubuntu 25.10+/26.04 ships the RUST uutils reimplementation as /usr/bin/shuf.  Its
# --random-source consumption order is NOT guaranteed to match GNU coreutils, so we
# prefer a real GNU binary when one is installed (Ubuntu packages it as `gnushuf`).
SHUF_CANDIDATES = ("gnushuf", "/usr/bin/gnushuf", "shuf")


def shuf_binary():
    for b in SHUF_CANDIDATES:
        try:
            out = subprocess.run([b, "--version"], capture_output=True, text=True,
                                 timeout=10).stdout
        except Exception:
            continue
        if out:
            first = out.splitlines()[0]
            if "uutils" not in first or b == SHUF_CANDIDATES[-1]:
                return b, first
    return None, None


def shuf_available():
    _b, v = shuf_binary()
    return v


def shuf_stream(src_path, n, lo=0, hi=28):
    """Real `shuf -i lo-hi -r -n n --random-source=src_path`.

    Returns a list of n ints in [lo, hi], or None if shuf refuses (the commonest
    reason is that the source file has too few bytes: coreutils requires roughly
    n * ceil(log256(hi-lo+1)) bytes and errors out otherwise).
    """
    b, _v = shuf_binary()
    if b is None:
        return None
    try:
        r = subprocess.run(
            [b, "-i", f"{lo}-{hi}", "-r", "-n", str(n),
             "--random-source", src_path],
            capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    vals = [int(x) for x in r.stdout.split()]
    return vals if len(vals) == n else None


def shuf_source_dictionary(repo_root):
    """The finite, human-checkable file set worth trying as --random-source.

    Doctrine R5 rank 1: a finite object beats an unbounded space. These are files the
    author demonstrably held, in the order L1's evidence ranks them.
    """
    cands = []
    lp2 = os.path.join(repo_root, "liber-primus", "corpus", "A-primary-artifacts")
    for base, _dirs, files in os.walk(lp2):
        for f in sorted(files):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".asc", ".txt", ".bin")):
                cands.append(os.path.join(base, f))
    return cands


# --------------------------------------------------- openssl enc -k  (EVP_BytesToKey)
def evp_bytes_to_key(password, salt=b"", keylen=16, ivlen=16, digest="md5", count=1):
    """OpenSSL 1.0.x EVP_BytesToKey. Default digest for `enc` in 1.0.1 is MD5."""
    d = b""
    out = b""
    while len(out) < keylen + ivlen:
        h = hashlib.new(digest)
        h.update(d + password + salt)
        dgst = h.digest()
        for _ in range(count - 1):
            dgst = hashlib.new(digest, dgst).digest()
        d = dgst
        out += d
    return out[:keylen], out[keylen:keylen + ivlen]


def _rc4(key, n):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    out = bytearray()
    i = j = 0
    while len(out) < n:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(S[(S[i] + S[j]) & 0xFF])
    return bytes(out)


def openssl_enc_rc4_keystream(passphrase, n):
    """`openssl enc -rc4 -k PASS -nosalt < /dev/zero` -- exactly the bytes it emits.
    RC4 key length for the `rc4` alias is 16 bytes (128 bit); no IV is used."""
    if isinstance(passphrase, str):
        passphrase = passphrase.encode()
    key, _iv = evp_bytes_to_key(passphrase, b"", keylen=16, ivlen=0)
    return _rc4(key, n)


def raws_openssl_enc(passphrase, n):
    """Byte stream as ints 0..255, for reduce29."""
    return list(openssl_enc_rc4_keystream(passphrase, n))


RMAX_BYTE = 255


if __name__ == "__main__":
    print("shuf:", shuf_available())
    print("rc4 keystream for 'CICADA':", openssl_enc_rc4_keystream("CICADA", 8).hex())
