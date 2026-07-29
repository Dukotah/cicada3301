"""Pure-Python Skein-512-512 (Skein v1.3, the SHA-3 finalist).
Threefish-512 block cipher in UBI (Unique Block Iteration) chaining mode.
Validated in __main__ and by caller's gate against the official Skein v1.3 KAT.
"""

MASK = (1 << 64) - 1

# Threefish-512 rotation constants (8 words, 8 rounds cycle -> subkey every 4 rounds)
ROT_512 = [
    [46, 36, 19, 37],
    [33, 27, 14, 42],
    [17, 49, 36, 39],
    [44,  9, 54, 56],
    [39, 30, 34, 24],
    [13, 50, 10, 17],
    [25, 29, 39, 43],
    [ 8, 35, 56, 22],
]
PERM_512 = [2, 1, 4, 7, 6, 5, 0, 3]
NW = 8
NROUNDS = 72
C240 = 0x1BD11BDAA9FC1A22

def _rotl(x, r):
    return ((x << r) | (x >> (64 - r))) & MASK

def threefish512_encrypt(key_words, tweak, plain_words):
    # key_words: 8 x 64-bit ints ; tweak: 2 x 64-bit ints ; plain: 8 words
    k = list(key_words) + [C240]
    for w in key_words:
        k[8] ^= w
    t = [tweak[0], tweak[1], tweak[0] ^ tweak[1]]

    v = list(plain_words)
    # subkeys
    for d in range(NROUNDS // 4 + 1):
        # not precomputing all; add subkey s = d
        pass

    def subkey(s):
        ks = [0]*NW
        for i in range(NW):
            ks[i] = k[(s + i) % (NW + 1)]
        ks[NW-3] = (ks[NW-3] + t[s % 3]) & MASK
        ks[NW-2] = (ks[NW-2] + t[(s+1) % 3]) & MASK
        ks[NW-1] = (ks[NW-1] + s) & MASK
        return ks

    for rnd in range(NROUNDS):
        if rnd % 4 == 0:
            sk = subkey(rnd // 4)
            for i in range(NW):
                v[i] = (v[i] + sk[i]) & MASK
        # MIX + permute
        rc = ROT_512[rnd % 8]
        nv = [0]*NW
        for j in range(NW // 2):
            a = v[2*j]
            b = v[2*j+1]
            a = (a + b) & MASK
            b = _rotl(b, rc[j]) ^ a
            v[2*j] = a
            v[2*j+1] = b
        # permutation
        nv = [v[PERM_512[i]] for i in range(NW)]
        v = nv
    # final subkey
    sk = subkey(NROUNDS // 4)
    for i in range(NW):
        v[i] = (v[i] + sk[i]) & MASK
    return v

# UBI type values
T_KEY = 0
T_CFG = 4
T_MSG = 48
T_OUT = 63

def _bytes_to_words(b):
    assert len(b) % 8 == 0
    return [int.from_bytes(b[i:i+8], 'little') for i in range(0, len(b), 8)]

def _words_to_bytes(w):
    return b''.join(x.to_bytes(8, 'little') for x in w)

def _ubi(G, msg, type_val):
    # G: 8 words chaining value. msg: bytes. Returns new 8 words.
    pos = 0
    total = len(msg)
    chain = list(G)
    first = True
    if total == 0:
        # single empty block
        block = b'\x00' * 64
        tweak0 = 0
        tweak1 = (type_val << 56) | (1 << 62) | (1 << 63)  # first & final, bitpad off
        pt = _bytes_to_words(block)
        enc = threefish512_encrypt(chain, [tweak0 & MASK, tweak1 & MASK], pt)
        return [enc[i] ^ pt[i] for i in range(8)]
    while pos < total:
        take = min(64, total - pos)
        block = msg[pos:pos+take]
        last = (pos + take) >= total
        if take < 64:
            block = block + b'\x00' * (64 - take)
        processed = pos + take
        tweak0 = processed & MASK
        tw1 = (type_val << 56)
        if first:
            tw1 |= (1 << 62)
        if last:
            tw1 |= (1 << 63)
        tweak1 = tw1 & MASK
        pt = _bytes_to_words(block)
        enc = threefish512_encrypt(chain, [tweak0, tweak1], pt)
        chain = [enc[i] ^ pt[i] for i in range(8)]
        first = False
        pos += take
    return chain

def skein512_512(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    # Config block: schema 'SHA3', ver 1, output length 512 bits
    # 32-byte config string
    cfg = bytearray(32)
    cfg[0:4] = b'SHA3'
    cfg[4] = 1  # version (16-bit LE) low byte
    cfg[5] = 0  # version high
    # bytes 6,7 reserved =0
    # output length in bits (64-bit LE) at offset 8
    cfg[8:16] = (512).to_bytes(8, 'little')
    # remaining zero
    G0 = [0]*8
    G_cfg = _ubi(G0, bytes(cfg), T_CFG)
    G_msg = _ubi(G_cfg, data, T_MSG)
    # output transform: UBI on 8-byte counter 0
    out = _ubi(G_msg, (0).to_bytes(8, 'little'), T_OUT)
    return _words_to_bytes(out)[:64].hex()

# Official Skein v1.3 KAT (from the NIST submission "skein_golden_kat.txt"):
#   Skein-512-512, message = empty (0 bits)
TEST_VECTORS = {
    b"": "bc5b4c50925519c290cc634277ae3d6257212395cba733bbad37a4af0fa06af41fca7903d06564fea7a2d3730dbdb80c1f85562dfcc070334ea4d1d9e72cba7a",
    # Skein-512-512 of the single byte 0xFF (Skein KAT "one byte, all ones")
    b"\xff": "71b7bce6fe6452227b9ced6014249e5bf9a9754c3ad618ccc4e0aae16b316cc8ca698d864307ed3e80b6ef1570812ac5272dc409b5a012df2a579102f340617a",
}

if __name__ == "__main__":
    ok = True
    for m, e in TEST_VECTORS.items():
        g = skein512_512(m)
        good = g == e
        ok &= good
        print(f"Skein-512-512({m!r:6}) {'PASS' if good else 'FAIL'}")
        if not good:
            print("  exp:", e)
            print("  got:", g)
    print("ALL PASS" if ok else "*** FAIL ***")
    import sys
    sys.exit(0 if ok else 1)
