"""Minimal pycryptodome-API shim over the `cryptography` package (decrypt-only), for R34-P1 re-runs.
Mimics pycryptodome key-validity errors so the original try/except flow is unchanged."""
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.primitives.ciphers import algorithms as _alg
from cryptography.hazmat.decrepit.ciphers import algorithms as _dalg

class _Dec:
    def __init__(self, algo, mode):
        self._d = Cipher(algo, mode).decryptor(); self._a = (algo, mode)
    def encrypt(self, pt):  # R35-B2 addition: needed by the original run.py positive control
        e = Cipher(*self._a).encryptor(); return e.update(bytes(pt)) + e.finalize()
    def decrypt(self, ct):
        return self._d.update(bytes(ct)) + self._d.finalize()

def _mode(m, iv, bs):
    if m == 1:  # ECB
        return modes.ECB()
    if m == 2:  # CBC
        if iv is None or len(iv) != bs:
            raise ValueError("bad IV")
        return modes.CBC(iv)
    if m == 6:  # CTR, zero nonce / initial counter 0 (big-endian 128-bit), as Counter.new(128, initial_value=0)
        return modes.CTR(bytes(16))
    raise ValueError("unsupported mode")

class _Block:
    MODE_ECB = 1
    MODE_CBC = 2

class AES(_Block):
    MODE_CTR = 6
    @staticmethod
    def new(key, mode, iv=None, **kw):
        if len(key) not in (16, 24, 32):
            raise ValueError("Incorrect AES key length")
        return _Dec(_alg.AES(key), _mode(mode, iv, 16))

class Blowfish(_Block):
    @staticmethod
    def new(key, mode, iv=None, **kw):
        if not (5 <= len(key) <= 56):
            raise ValueError("Incorrect Blowfish key length")
        return _Dec(_dalg.Blowfish(key), _mode(mode, iv, 8))

class DES(_Block):
    @staticmethod
    def new(key, mode, iv=None, **kw):
        if len(key) != 8:
            raise ValueError("Incorrect DES key length")
        return _Dec(_alg.TripleDES(key), _mode(mode, iv, 8))   # 8-byte key == single DES

class DES3(_Block):
    @staticmethod
    def adjust_key_parity(k):
        out = bytearray()
        for b in k:
            hi = b & 0xFE
            out.append(hi | (1 if bin(hi).count("1") % 2 == 0 else 0))
        return bytes(out)
    @staticmethod
    def new(key, mode, iv=None, **kw):
        if len(key) not in (16, 24):
            raise ValueError("Incorrect Triple DES key length")
        k = key if len(key) == 24 else key + key[:8]
        if k[:8] == k[8:16] or k[8:16] == k[16:24]:
            raise ValueError("Triple DES key degenerates to single DES")
        return _Dec(_alg.TripleDES(k), _mode(mode, iv, 8))

class ARC4:
    """Pure-python RC4 (cryptography only allows a few key sizes; pycryptodome allows 5..256 bytes)."""
    class _R:
        def __init__(self, key):
            S = list(range(256)); j = 0
            for i in range(256):
                j = (j + S[i] + key[i % len(key)]) & 255
                S[i], S[j] = S[j], S[i]
            self.S, self.i, self.j = S, 0, 0
        def decrypt(self, ct):
            S, i, j = self.S, self.i, self.j; out = bytearray()
            for c in bytes(ct):
                i = (i + 1) & 255; j = (j + S[i]) & 255
                S[i], S[j] = S[j], S[i]
                out.append(c ^ S[(S[i] + S[j]) & 255])
            self.i, self.j = i, j
            return bytes(out)
    @staticmethod
    def new(key, **kw):
        if not (5 <= len(key) <= 256):
            raise ValueError("Incorrect ARC4 key length")
        return ARC4._R(bytes(key))
