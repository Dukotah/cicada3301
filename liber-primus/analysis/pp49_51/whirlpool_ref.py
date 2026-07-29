"""Pure-Python Whirlpool (ISO/IEC 10118-3:2004, the final "Whirlpool" a.k.a. WHIRLPOOL-T/-0 corrected).
Validated against official ISO test vectors in __main__ and by the caller's KAT gate.
Implements the block cipher W (10 rounds, AES-like over GF(2^8) with poly 0x11d) in
Miyaguchi-Preneel mode. 512-bit digest, 512-bit block, big-endian.
"""

R = 10
# S-box (official Whirlpool S-box)
_SBOX_HEX = (
"18 23 c6 e8 87 b8 01 4f 36 a6 d2 f5 79 6f 91 52 "
"60 bc 9b 8e a3 0c 7b 35 1d e0 d7 c2 2e 4b fe 57 "
"15 77 37 e5 9f f0 4a da 58 c9 29 0a b1 a0 6b 85 "
"bd 5d 10 f4 cb 3e 05 67 e4 27 41 8b a7 7d 95 d8 "
"fb ee 7c 66 dd 17 47 9e ca 2d bf 07 ad 5a 83 33 "
"63 02 aa 71 c8 19 49 d9 f2 e3 5b 88 9a 26 32 b0 "
"e9 0f d5 80 be cd 34 48 ff 7a 90 5f 20 68 1a ae "
"b4 54 93 22 64 f1 73 12 40 08 c3 ec db a1 8d 3d "
"97 00 cf 2b 76 82 d6 1b b5 af 6a 50 45 f3 30 ef "
"3f 55 a2 ea 65 ba 2f c0 de 1c fd 4d 92 75 06 8a "
"b2 e6 0e 1f 62 d4 a8 96 f9 c5 25 59 84 72 39 4c "
"5e 78 38 8c d1 a5 e2 61 b3 21 9c 1e 43 c7 fc 04 "
"51 99 6d 0d fa df 7e 24 3b ab ce 11 8f 4e b7 eb "
"3c 81 94 f7 b9 13 2c d3 e7 6e c4 03 56 44 7f a9 "
"2a bb c1 53 dc 0b 9d 6c 31 74 f6 46 ac 89 14 e1 "
"16 3a 69 09 70 b6 d0 ed cc 42 98 a4 28 5c f8 86"
)
SBOX = bytes(int(x, 16) for x in _SBOX_HEX.split())

def _xtime_mul(a, b):
    # GF(2^8) multiply with reduction poly 0x11d
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1d
        b >>= 1
    return p

# Circulant MDS row of the diffusion matrix: [1,1,4,1,8,5,2,9]
_CIRC = [1, 1, 4, 1, 8, 5, 2, 9]

# Precompute C tables: for each byte value v and each column j, contribution
# Build round constants and cipher via the standard "long" tables approach on the fly.
def _mds_mult(state):
    # state: 8x8 bytes (list of 8 rows, each 8 bytes). Apply MixRows: each row multiplied
    # by circulant MDS matrix C (row i output byte j = sum_k a[i][k] * C[(j-k) mod 8])
    out = [[0]*8 for _ in range(8)]
    for i in range(8):
        for j in range(8):
            acc = 0
            for k in range(8):
                acc ^= _xtime_mul(state[i][k], _CIRC[(j - k) % 8])
            out[i][j] = acc
    return out

def _sub(state):
    return [[SBOX[b] for b in row] for row in state]

def _shift_columns(state):
    # ShiftColumns: column j shifted down by j (cyclically). Equivalently element (i,j)
    # comes from (i-j mod 8, j).
    out = [[0]*8 for _ in range(8)]
    for i in range(8):
        for j in range(8):
            out[i][j] = state[(i - j) % 8][j]
    return out

def _add_key(state, key):
    return [[state[i][j] ^ key[i][j] for j in range(8)] for i in range(8)]

# Round constants
_RC = []
for r in range(1, R + 1):
    rc = [[0]*8 for _ in range(8)]
    for j in range(8):
        rc[0][j] = SBOX[8 * (r - 1) + j]
    _RC.append(rc)

def _bytes_to_matrix(b):
    return [[b[i*8 + j] for j in range(8)] for i in range(8)]

def _matrix_to_bytes(m):
    return bytes(m[i][j] for i in range(8) for j in range(8))

def _W(K, block):
    # block cipher W: encrypt `block` (matrix) with key `K` (matrix)
    state = _add_key(block, K)
    Kr = K
    for r in range(R):
        # key schedule round
        Kr = _sub(Kr)
        Kr = _shift_columns(Kr)
        Kr = _mds_mult(Kr)
        Kr = _add_key(Kr, _RC[r])
        # data round
        state = _sub(state)
        state = _shift_columns(state)
        state = _mds_mult(state)
        state = _add_key(state, Kr)
    return state

def _compress(H, block):
    # Miyaguchi-Preneel: H' = W_H(block) XOR block XOR H
    Hm = _bytes_to_matrix(H)
    Bm = _bytes_to_matrix(block)
    Em = _W(Hm, Bm)
    out = bytearray(64)
    for i in range(8):
        for j in range(8):
            out[i*8+j] = Em[i][j] ^ Bm[i][j] ^ Hm[i][j]
    return bytes(out)

def whirlpool(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    bitlen = len(data) * 8
    # padding: 0x80, then zeros, then 256-bit big-endian length, to multiple of 512 bits
    msg = bytearray(data)
    msg.append(0x80)
    while (len(msg) % 64) != 32:
        msg.append(0x00)
    msg += bitlen.to_bytes(32, 'big')
    H = bytes(64)
    for off in range(0, len(msg), 64):
        H = _compress(H, bytes(msg[off:off+64]))
    return H.hex()

# Official ISO/IEC 10118-3 Whirlpool test vectors
TEST_VECTORS = {
    b"": "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a73e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3",
    b"a": "8aca2602792aec6f11a67206531fb7d7f0dff59413145e6973c45001d0087b42d11bc645413aeff63a42391a39145a591a92200d560195e53b478584fdae231a",
    b"abc": "4e2448a4c6f486bb16b6562c73b4020bf3043e3a731bce721ae1b303d97e6d4c7181eebdb6c57e277d0e34957114cbd6c797fc9d95d8b582d225292076d4eef5",
    b"message digest": "378c84a4126e2dc6e56dcc7458377aac838d00032230f53ce1f5700c0ffb4d3b8421557659ef55c106b4b52ac5a4aaa692ed920052838f3362e86dbd37a8903e",
    b"abcdefghijklmnopqrstuvwxyz": "f1d754662636ffe92c82ebb9212a484a8d38631ead4238f5442ee13b8054e41b08bf2a9251c30b6a0b8aae86177ab4a6f68f673e7207865d5d9819a3dba4eb3b",
}

if __name__ == "__main__":
    ok = True
    for m, e in TEST_VECTORS.items():
        g = whirlpool(m)
        good = g == e
        ok &= good
        print(f"Whirlpool({m!r:18}) {'PASS' if good else 'FAIL'}")
        if not good:
            print("  exp:", e)
            print("  got:", g)
    print("ALL PASS" if ok else "*** FAIL ***")
    import sys
    sys.exit(0 if ok else 1)
