"""Pure-Python reference implementation of the ORIGINAL BLAKE hash function
(the SHA-3 finalist by Aumasson, Henzen, Meier, Phan) — NOT BLAKE2.

Supports BLAKE-256 and BLAKE-512. Salt defaults to zero.

Ported from the public-domain reference / spec (BLAKE submission v1.4). This
module VALIDATES itself against the official known-answer test vectors at the
bottom when run as __main__, and exposes blake256()/blake512() helpers.
"""

# ---- constants ----

# 64-bit sigma permutation table (16 rounds; BLAKE-512 uses 16, wraps mod 10)
SIGMA = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
    [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
    [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
    [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
    [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
    [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
    [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
    [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
    [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0],
]

# BLAKE-256 constants (32-bit)
IV256 = [
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
]
C256 = [
    0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344,
    0xA4093822, 0x299F31D0, 0x082EFA98, 0xEC4E6C89,
    0x452821E6, 0x38D01377, 0xBE5466CF, 0x34E90C6C,
    0xC0AC29B7, 0xC97C50DD, 0x3F84D5B5, 0xB5470917,
]

# BLAKE-512 constants (64-bit) — digits of pi
IV512 = [
    0x6A09E667F3BCC908, 0xBB67AE8584CAA73B,
    0x3C6EF372FE94F82B, 0xA54FF53A5F1D36F1,
    0x510E527FADE682D1, 0x9B05688C2B3E6C1F,
    0x1F83D9ABFB41BD6B, 0x5BE0CD19137E2179,
]
C512 = [
    0x243F6A8885A308D3, 0x13198A2E03707344,
    0xA4093822299F31D0, 0x082EFA98EC4E6C89,
    0x452821E638D01377, 0xBE5466CF34E90C6C,
    0xC0AC29B7C97C50DD, 0x3F84D5B5B5470917,
    0x9216D5D98979FB1B, 0xD1310BA698DFB5AC,
    0x2FFD72DBD01ADFB7, 0xB8E1AFED6A267E96,
    0xBA7C9045F12C7F99, 0x24A19947B3916CF7,
    0x0801F2E2858EFC16, 0x636920D871574E69,
]


def _rotr(x, n, bits):
    mask = (1 << bits) - 1
    return ((x >> n) | (x << (bits - n))) & mask


class _Blake:
    def __init__(self, bits):
        self.bits = bits
        if bits == 256:
            self.wordbits = 32
            self.h = list(IV256)
            self.const = C256
            self.rounds = 14
            # rotation amounts for G (BLAKE-256)
            self.rot = (16, 12, 8, 7)
            self.blocksize = 64  # bytes
            self.wordbytes = 4
        elif bits == 512:
            self.wordbits = 64
            self.h = list(IV512)
            self.const = C512
            self.rounds = 16
            self.rot = (32, 25, 16, 11)
            self.blocksize = 128
            self.wordbytes = 8
        else:
            raise ValueError("only 256/512")
        self.salt = [0, 0, 0, 0]
        self.t = 0            # bit counter
        self.buf = b""
        self.mask = (1 << self.wordbits) - 1

    def _compress(self, block, counter):
        wb = self.wordbytes
        m = [int.from_bytes(block[i * wb:(i + 1) * wb], "big") for i in range(16)]
        v = [0] * 16
        v[:8] = self.h[:8]
        c = self.const
        v[8] = self.salt[0] ^ c[0]
        v[9] = self.salt[1] ^ c[1]
        v[10] = self.salt[2] ^ c[2]
        v[11] = self.salt[3] ^ c[3]
        # counter t0/t1
        t0 = counter & self.mask
        t1 = (counter >> self.wordbits) & self.mask
        v[12] = t0 ^ c[4]
        v[13] = t0 ^ c[5]
        v[14] = t1 ^ c[6]
        v[15] = t1 ^ c[7]

        r0, r1, r2, r3 = self.rot
        mask = self.mask
        wbits = self.wordbits

        def G(a, b, cc, d, i, r):
            s = SIGMA[r % 10]
            v[a] = (v[a] + v[b] + (m[s[2 * i]] ^ c[s[2 * i + 1]])) & mask
            v[d] = _rotr(v[d] ^ v[a], r0, wbits)
            v[cc] = (v[cc] + v[d]) & mask
            v[b] = _rotr(v[b] ^ v[cc], r1, wbits)
            v[a] = (v[a] + v[b] + (m[s[2 * i + 1]] ^ c[s[2 * i]])) & mask
            v[d] = _rotr(v[d] ^ v[a], r2, wbits)
            v[cc] = (v[cc] + v[d]) & mask
            v[b] = _rotr(v[b] ^ v[cc], r3, wbits)

        for r in range(self.rounds):
            # column step
            G(0, 4, 8, 12, 0, r)
            G(1, 5, 9, 13, 1, r)
            G(2, 6, 10, 14, 2, r)
            G(3, 7, 11, 15, 3, r)
            # diagonal step
            G(0, 5, 10, 15, 4, r)
            G(1, 6, 11, 12, 5, r)
            G(2, 7, 8, 13, 6, r)
            G(3, 4, 9, 14, 7, r)

        for i in range(8):
            self.h[i] ^= self.salt[i % 4] ^ v[i] ^ v[i + 8]

    def update(self, data):
        self.buf += data
        while len(self.buf) >= self.blocksize:
            block = self.buf[:self.blocksize]
            self.buf = self.buf[self.blocksize:]
            self.t += self.blocksize * 8
            self._compress(block, self.t)

    def digest(self):
        # padding per BLAKE spec
        buflen_bits = len(self.buf) * 8
        # total message length in bits = self.t (fully consumed blocks) + buflen_bits
        total_bits = self.t + buflen_bits

        # length field: 64 bits for 256, 128 bits for 512
        lenfield = 16 if self.bits == 256 else 32  # hex-nibble count? no—compute bytes
        lenbytes = 8 if self.bits == 256 else 16

        # The "01" marker byte before length; padding rule:
        # append 0x80 ... then bits, with the byte just before length ORed with 0x01
        # Standard BLAKE padding:
        msg = self.buf
        # number of zero bytes so that (len(msg)+1 + padzeros + lenbytes) % blocksize == 0
        # first pad byte is 0x80
        # last data byte region: block ends with lenbytes-byte big-endian total_bits,
        # and the byte immediately before is ORed with 0x01.
        pad_target = self.blocksize
        # length of remaining after adding 0x80 marker and length field
        # We need final length ≡ 0 mod blocksize
        ll = len(msg)
        # bytes used: msg + 0x80 + zeros + (0x01 marker into last pad byte) + lenbytes
        # Compute how many total bytes in final padded region
        rem = (ll + 1 + lenbytes) % pad_target
        if rem == 0:
            zeros = 0
        else:
            zeros = pad_target - rem

        if zeros == 0 and (ll + 1 + lenbytes) % pad_target == 0:
            padbyte0 = 0x80
        # Build pad
        pad = bytearray()
        pad.append(0x80)
        pad.extend(b"\x00" * zeros)
        # OR the marker 0x01 into the last byte before length
        if len(pad) == 0:
            pad = bytearray(b"\x01")
        else:
            pad[-1] |= 0x01
        pad.extend(total_bits.to_bytes(lenbytes, "big"))

        # Now feed. Special case: if original message ended on a block boundary and
        # buf is empty, the counter for the final padding block must be 0 (per spec:
        # when the last block contains no message bits, t=0).
        final_data = msg + bytes(pad)
        # Feed block by block with correct counters
        # After update() consumed full blocks, self.t counted those. Now the padding
        # blocks: BLAKE sets the counter to the number of message bits SO FAR at the
        # time the block is compressed. For a padding-only block with no msg bits, t=0.
        pos = 0
        # process the remaining (msg-tail + pad) as blocks
        while pos < len(final_data):
            block = final_data[pos:pos + self.blocksize]
            pos += self.blocksize
            # bits of actual message contained up to end of this block:
            # message bits are only in the leading `ll` bytes of final_data
            msg_bytes_in_block_end = min(pos, ll)
            counter = self.t + msg_bytes_in_block_end * 8
            if msg_bytes_in_block_end * 8 == 0 and self.t == 0:
                # padding-only block, no message bits at all -> counter 0
                counter = 0
            self._compress(block, counter)

        wb = self.wordbytes
        out = b"".join(self.h[i].to_bytes(wb, "big") for i in range(self.bits // self.wordbits))
        return out

    def hexdigest(self):
        return self.digest().hex()


def blake256(data=b""):
    h = _Blake(256)
    h.update(data)
    return h.hexdigest()


def blake512(data=b""):
    h = _Blake(512)
    h.update(data)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# OFFICIAL known-answer test vectors from the BLAKE SHA-3 submission (v1.4),
# section "test values", and the reference C distribution.
# ---------------------------------------------------------------------------
TEST_VECTORS_512 = {
    # BLAKE-512 of the single byte 0x00
    b"\x00":
        "97961587f6d970faba6d2478045de6d1fabd09b61ae50932054d52bc29d31be4"
        "ff9102b9f69e2bbdb83be13d4b9c06091e5fa0b48bd081b634058be0ec49beb3",
    # BLAKE-512 of 144 bytes of 0x00
    b"\x00" * 144:
        "313717d608e9cf758dcb1eb0f0c3cf9fc150b2d500fb33f51c52afc99d358a2f"
        "1374b8a38bba7974e7f6ef79cab16f22ce1e649d6e01ad9589c213045d545dde",
}
TEST_VECTORS_256 = {
    b"\x00":
        "0ce8d4ef4dd7cd8d62dfded9d4edb0a774ae6a41929a74da23109e8f11139c87",
    b"\x00" * 72:
        "d419bad32d504fb7d44d460c42c5593fe544fa4c135dec31e21bd9abdcc22d41",
}


if __name__ == "__main__":
    ok = True
    print("=== BLAKE-512 known-answer validation ===")
    for msg, expect in TEST_VECTORS_512.items():
        got = blake512(msg)
        good = got == expect
        ok &= good
        print(f"  input={len(msg)}B of 0x00  {'PASS' if good else 'FAIL'}")
        print(f"    expect: {expect}")
        print(f"    got   : {got}")
    print("=== BLAKE-256 known-answer validation ===")
    for msg, expect in TEST_VECTORS_256.items():
        got = blake256(msg)
        good = got == expect
        ok &= good
        print(f"  input={len(msg)}B of 0x00  {'PASS' if good else 'FAIL'}  got={got[:32]}...")
    print()
    print("ALL VECTORS PASS" if ok else "*** VALIDATION FAILED ***")
    import sys
    sys.exit(0 if ok else 1)
