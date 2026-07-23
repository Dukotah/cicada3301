"""Campaign XVIII — PAYLOAD-AS-CIPHERTEXT hypothesis.

Previous work:
  Campaign VII/IX: payload is NOT a keystream (rigid test); not structurally
    four 512-bit hashes with link to AN END; XOR with known streams -> no entropy
    collapse.
  Campaign XVIII (payload_skip.py): payload bytes mod 29 as KEY over 55 pages,
    skip-aware -> best -6.756, 0 hits. Dead as a key.

THIS FILE: the OPPOSITE hypothesis — the 256-byte payload IS ITSELF an
ENCIPHERED MESSAGE under some unknown key, and we can probe structure with:

  §1. Skip-aware beam decode of payload-mod-29 as CIPHERTEXT under the known
      Cicada key generators (phi(prime), thematic keywords, solved-LP English)
      and the page-56 512-bit hash.

  §2. Byte-level transforms (XOR / subtract mod 256) against every known
      Cicada constant stream, then structure sniffing: printable ASCII,
      magic bytes, entropy, longest-run.

  §3. zlib / gzip / bz2 / lzma decompression attempt after every transform.

  §4. '4x64 = four 512-bit hash digests' fresh re-test: does XOR or subtraction
      of one block against an adjacent block yield low-entropy or text?  Does
      mod-29-stacking reveal an alternating-key pattern?

All runs complete in << 60 s.  Honest null is the expected result — document
every measured result, flag any positive.
"""
import os, sys, math, hashlib, collections, zlib, gzip, bz2, lzma, struct
import numpy as np

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
sys.path.insert(0, os.path.join(HERE, ".."))          # campaign18_skip/
sys.path.insert(0, HERE)

from lp import gematria as gp, score as sc
from skipdecode import eng_to_idx, idx_to_trans, beam_decode
Q = sc.default()
N = gp.N   # 29

# ── constants ──────────────────────────────────────────────────────────────────
PAYLOAD_BIN = os.path.join(ROOT, "analysis", "pp49_51", "canon_256.bin")
PAYLOAD_BIN2 = os.path.join(ROOT, "analysis", "pp49_51", "canon_256_decpref.bin")
ANEND_HEX = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a84"
              "25893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4")
ANEND_BYTES = bytes.fromhex(ANEND_HEX)

# ── helpers ────────────────────────────────────────────────────────────────────
def entropy(bs):
    n = len(bs)
    if n == 0:
        return 0.0
    c = collections.Counter(bs)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def printable_stats(bs):
    """Return (printable_count, longest_printable_run)."""
    best = cur = 0
    cnt = 0
    for b in bs:
        if 32 <= b < 127:
            cur += 1; cnt += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return cnt, best


def try_decompress(label, data):
    """Try every standard decompressor; return list of (method, result_bytes)."""
    hits = []
    for name, fn in [
        ("zlib",     lambda d: zlib.decompress(d)),
        ("zlib-raw", lambda d: zlib.decompress(d, wbits=-15)),
        ("gzip",     lambda d: gzip.decompress(d)),
        ("bz2",      lambda d: bz2.decompress(d)),
        ("lzma",     lambda d: lzma.decompress(d)),
    ]:
        try:
            out = fn(data)
            hits.append((name, out))
        except Exception:
            pass
    return hits


def sniff_structure(label, bs):
    """Report printability, entropy, magic bytes, compression; return summary."""
    cnt, run = printable_stats(bs)
    ent = entropy(bs)
    pct = cnt / len(bs) * 100
    # magic bytes
    magic = ""
    if bs[:2] == b'\x1f\x8b':     magic = " [GZIP!]"
    if bs[:4] == b'PK\x03\x04':   magic = " [ZIP!]"
    if bs[:4] == b'\x89PNG':       magic = " [PNG!]"
    if bs[:3] == b'BZh':           magic = " [BZ2!]"
    if bs[:6] == b'\xfd7zXZ\x00': magic = " [XZ!]"
    if bs[:2] == b'\x78\x9c' or bs[:2] == b'\x78\x01' or bs[:2] == b'\x78\xda':
        magic = " [ZLIB!]"
    if bs[:4] == b'\x7fELF':       magic = " [ELF!]"
    summary = (f"{label}  ent={ent:.3f}  print={pct:.0f}%  run={run}"
               f"{magic}")
    # try decompression on every hit that isn't obviously binary
    dc = try_decompress(label, bs)
    return summary, dc


# ── load payloads ──────────────────────────────────────────────────────────────
P1 = open(PAYLOAD_BIN,  "rb").read()          # 256 bytes, majority vote
P2 = open(PAYLOAD_BIN2, "rb").read()          # 256 bytes, decimal-preferred
assert len(P1) == len(P2) == 256

# mod-29 ciphertext from payload
CT1 = np.array([b % N for b in P1], dtype=np.int64)   # 256 runes
CT2 = np.array([b % N for b in P2], dtype=np.int64)

print("=" * 72)
print("CAMPAIGN XVIII  — PAYLOAD-AS-CIPHERTEXT  (payload_ciphertext.py)")
print("=" * 72)
print(f"payload:  256 bytes | entropy {entropy(P1):.3f} b/byte | "
      f"printable {printable_stats(P1)[0]}/256")
print(f"CT1 (mod 29): {len(CT1)} rune indices")
print()

# ============================================================
# §1  SKIP-AWARE BEAM DECODE  (payload-mod-29 as ciphertext)
# ============================================================
print("-" * 72)
print("§1  SKIP-AWARE BEAM DECODE  of payload mod-29 as ciphertext")
print("    Keys: Cicada number-theory streams + thematic keywords + page-56 hash")
print("-" * 72)

def _primes(count):
    out, cand = [], 2
    while len(out) < count:
        if all(cand % p for p in out if p * p <= cand):
            out.append(cand)
        cand += 1
    return out

def key_phi_prime(length):
    primes = _primes(length + 1)
    out = []
    for p in primes:
        if p == 2:
            val = 1
        else:
            phi = p - 1  # phi(prime p) = p - 1
            val = phi % N
        out.append(val)
        if len(out) >= length:
            break
    return out

def key_primes_mod29(length):
    primes = _primes(length)
    return [p % N for p in primes]

def key_totient_int(length):
    """phi(n) mod 29 for n = 1..length (Euler's totient as integer-mod)."""
    out = [0, 1]  # phi(1)=1 but seed with 0 for index alignment
    def phi(n):
        result = n
        p = 2
        while p * p <= n:
            if n % p == 0:
                while n % p == 0:
                    n //= p
                result -= result // p
            p += 1
        if n > 1:
            result -= result // n
        return result
    for i in range(2, length + 2):
        out.append(phi(i) % N)
    return out[:length]

def key_thematic(word, length):
    idx = eng_to_idx(word)
    if not idx:
        return [0] * length
    return [idx[i % len(idx)] for i in range(length)]

def key_anend_hash_mod29(length):
    """page-56 512-bit hash bytes, cycled, mod 29."""
    return [ANEND_BYTES[i % len(ANEND_BYTES)] % N for i in range(length)]

# Solved LP1 English as running key
SOLVED_EN = (
    "AWARNINGBELIEVENOTHINGFROMTHISBOOKEXCEPTWHATYOUKNOWTOBETRUE"
    "TESTTHEKNOWLEDGEFINDYOURTRUTHEXPERIENCEYOURDEATH"
    "AKOANAMANDECIDEDTOGOANDSTUDYWITHAMASTERHEWENTTOTHEDOOROFTHEMASTER"
    "WHOAREYOUWHOWISHESTOSTUDYHEREASKEDTHEMASTER"
    "WELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALLTHINGS"
    "ITISNOTANEASYTRIPBUTFORTHOSEWHOFINDTHEIRWAYHEREITISANECESSARYONE"
    "THELOSSOFDIVINITYTHECIRCUMFERENCEPRACTICESTHREEBEHAVIOURS"
    "THEPRIMESARESACREDTHETOTIENTFUNCTIONISSACRED"
    "ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTOITISTHEDUTYOFEVERYPILGRIM"
)
def key_solved_lp1(length):
    idx = eng_to_idx(SOLVED_EN)
    return [idx[i % len(idx)] for i in range(length)]

L = 256   # ciphertext length
THRESHOLD = -5.5  # confirm threshold (from robustness / Campaign XI)
BEAM_W = 300

candidates = {
    "phi_prime":      key_phi_prime(L + 100),
    "primes_mod29":   key_primes_mod29(L + 100),
    "totient_int":    key_totient_int(L + 100),
    "anend_hash":     key_anend_hash_mod29(L + 100),
    "solved_lp1":     key_solved_lp1(L + 100),
    "kw:DIVINITY":    key_thematic("DIVINITY", L + 100),
    "kw:CIRCUMFERENCE": key_thematic("CIRCUMFERENCE", L + 100),
    "kw:INSTAR":      key_thematic("INSTAR", L + 100),
    "kw:EMERGENCE":   key_thematic("EMERGENCE", L + 100),
    "kw:MOBIUS":      key_thematic("MOBIUS", L + 100),
    "kw:PILGRIM":     key_thematic("PILGRIM", L + 100),
    "kw:THEPRIMESARESACRED": key_thematic("THEPRIMESARESACRED", L + 100),
}

best_s1 = (-99, None, None, None, None, None)
s1_hits = []
for vname, CT in [("maj-byte", CT1), ("decpref-byte", CT2)]:
    for kname, K in candidates.items():
        Knp = np.array(K, dtype=np.int64)
        for sign in (-1, 1):
            for atb in (0, 1):
                ct = ((N - 1) - CT) % N if atb else CT
                try:
                    res = beam_decode(list(ct), K, sign=sign, o=0, beam_w=BEAM_W, max_skip=3)
                    s = res["score"]
                except Exception:
                    continue
                if s > best_s1[0]:
                    best_s1 = (s, vname, kname, sign, atb, res["translit"][:60])
                if s > THRESHOLD:
                    s1_hits.append((s, vname, kname, sign, atb, res["translit"][:80]))

print(f"Tested {len(candidates)} keys x 2 ciphertext variants x 2 signs x 2 atbash")
print(f"BEST  score={best_s1[0]:.3f}  [{best_s1[1]}] key={best_s1[2]}"
      f"  sign={best_s1[3]} atb={best_s1[4]}")
print(f"  -> {best_s1[5]}")
print(f"Hits above {THRESHOLD}: {len(s1_hits)}")
if s1_hits:
    for h in sorted(s1_hits, reverse=True)[:3]:
        print(f"  HIT {h[0]:.3f} [{h[1]}] {h[2]} sign={h[3]} atb={h[4]}: {h[5]}")
else:
    print("  -> NULL: payload-mod-29 is not a skip-aware OTP message under any tested key.")
print()

# ============================================================
# §2  BYTE-LEVEL TRANSFORMS + STRUCTURE SNIFF
# ============================================================
print("-" * 72)
print("§2  BYTE-LEVEL TRANSFORMS  (XOR / subtract) + structure sniff")
print("-" * 72)

# Build candidate byte-streams for combining with the payload
def stream_anend_tiled(length):
    return bytes(ANEND_BYTES[i % 64] for i in range(length))

def stream_constant(val, length):
    return bytes([val] * length)

def stream_3301_le(length):
    """3301 as repeated little-endian 2-byte word."""
    word = struct.pack("<H", 3301)  # b'\xe5\x0c'
    return bytes(word[i % 2] for i in range(length))

def stream_primes_bytes(length):
    primes = _primes(length)
    return bytes(p & 0xFF for p in primes)

def stream_ps_digits():
    """The P.S. 2012 Cicada digit string used in Campaign IX."""
    digits = ("1117113315091312891614710131114148531173114118"
              "13131111151097111321181613111310138141591712113"
              "7101316971315131416911137141311131117151397")
    return bytes(int(d) % 256 for d in digits if d.isdigit())[:256]

def stream_sha512_iter(seed_bytes, length):
    """Iterated SHA-512 keystream: H0=seed, H_i = SHA512(H_{i-1}), output bytes."""
    out = bytearray()
    h = seed_bytes
    while len(out) < length:
        h = hashlib.sha512(h).digest()
        out.extend(h)
    return bytes(out[:length])

byte_streams = {
    "anend_tiled":   stream_anend_tiled(256),
    "anend_rev":     bytes(reversed(stream_anend_tiled(256))),
    "3301_le":       stream_3301_le(256),
    "primes_bytes":  stream_primes_bytes(256),
    "ps_digits":     stream_ps_digits(),
    "sha512iter_p1": stream_sha512_iter(P1, 256),       # SHA512 chain seeded by payload itself
    "sha512iter_ae": stream_sha512_iter(ANEND_BYTES, 256),  # SHA512 chain seeded by ANEND
    "const_0x29":    stream_constant(0x29, 256),
    "const_3301lo":  stream_constant(3301 & 0xFF, 256),
}

sniff_results = []
for sname, stream in byte_streams.items():
    for pname, payload in [("P1", P1), ("P2", P2)]:
        for op, fn in [
            ("XOR",  lambda p, s: bytes(a ^ b for a, b in zip(p, s))),
            ("SUB",  lambda p, s: bytes((a - b) % 256 for a, b in zip(p, s))),
            ("ADD",  lambda p, s: bytes((a + b) % 256 for a, b in zip(p, s))),
        ]:
            result = fn(payload, stream)
            label = f"{pname} {op} {sname}"
            summary, dc = sniff_structure(label, result)
            cnt, run = printable_stats(result)
            ent = entropy(result)
            sniff_results.append((ent, cnt, run, label, summary, dc, result))

# Sort by lowest entropy first (most compressed-looking)
sniff_results.sort(key=lambda x: x[0])

print(f"Tested {len(sniff_results)} byte-transform combos.  Baseline P1 entropy={entropy(P1):.3f}")
print("Top 10 by lowest entropy (text/compression candidate):")
for ent, cnt, run, label, summary, dc, result in sniff_results[:10]:
    print(f"  {summary}")
    if dc:
        for method, decompressed in dc:
            print(f"    *** DECOMPRESSED via {method}: {len(decompressed)} bytes -> "
                  f"{decompressed[:40]!r}")

# Also flag any with long printable runs (text signal)
print("\nTop 5 by longest printable run:")
by_run = sorted(sniff_results, key=lambda x: -x[2])
for ent, cnt, run, label, summary, dc, result in by_run[:5]:
    print(f"  {summary}  sample: {result[:20]!r}")

print()

# ============================================================
# §3  COMPRESSION PROBES ON RAW PAYLOAD + KEY VARIANTS
# ============================================================
print("-" * 72)
print("§3  COMPRESSION PROBES  on raw payload and byte variants")
print("-" * 72)

raw_variants = [
    ("P1_raw",         P1),
    ("P1_rev",         P1[::-1]),
    ("P2_raw",         P2),
    ("P2_rev",         P2[::-1]),
    ("P1_nibble_swap", bytes(((b >> 4) | ((b & 0xF) << 4)) for b in P1)),
    ("P1_bit_reverse", bytes(int(f'{b:08b}'[::-1], 2) for b in P1)),
    ("P1_xor_anend",   bytes(a ^ b for a, b in zip(P1, ANEND_BYTES[:256]))),
    ("P1_rotate1",     P1[1:] + P1[:1]),
]
for vname, data in raw_variants:
    dc = try_decompress(vname, data)
    cnt, run = printable_stats(data)
    ent = entropy(data)
    if dc:
        for method, out in dc:
            print(f"  *** {vname} decompressed via {method}: {len(out)} bytes  "
                  f"-> {out[:40]!r}")
    else:
        # Only print the most informative non-hits
        if run > 5 or ent < 7.0:
            print(f"  {vname}: ent={ent:.3f} print={cnt}/256 run={run}  [no decomp]")

print("  (if no lines above: all raw variants are opaque binary, no decompression hit)")
print()

# ============================================================
# §4  4×64 = FOUR BLOCKS — CROSS-BLOCK STRUCTURE + MOD-29 STACKING
# ============================================================
print("-" * 72)
print("§4  4×64 = FOUR BLOCKS  — cross-block differencing & mod-29 stacking")
print("-" * 72)

blocks = [P1[i*64:(i+1)*64] for i in range(4)]

# 4a: XOR / subtract adjacent blocks -> does output collapse to low-entropy?
print("[4a] adjacent-block XOR / subtract:")
for i in range(3):
    for j in range(i+1, 4):
        for op, fn in [("XOR", lambda a,b: bytes(x^y for x,y in zip(a,b))),
                        ("SUB", lambda a,b: bytes((x-y)%256 for x,y in zip(a,b)))]:
            out = fn(blocks[i], blocks[j])
            cnt, run = printable_stats(out)
            ent = entropy(out)
            if ent < 7.0 or run > 6:
                print(f"  block{i} {op} block{j}: ent={ent:.3f} print={cnt}/64 run={run}  "
                      f"sample={out[:12].hex()}")
            dc = try_decompress(f"block{i}_{op}_block{j}", out)
            for method, decompressed in dc:
                print(f"    *** DECOMPRESSED block{i} {op} block{j} via {method}: "
                      f"{len(decompressed)} bytes")

# 4b: mod-29 stacking — view the four 64-byte blocks as four 64-rune ciphertext segments
#    keyed by the page-56 hash interpreted as a running key.
print("\n[4b] four 64-rune segments decoded as ciphertext under page-56 hash key (mod 29):")
hash_key = [ANEND_BYTES[i % len(ANEND_BYTES)] % N for i in range(256)]
for bidx, blk in enumerate(blocks):
    ct_blk = np.array([b % N for b in blk], dtype=np.int64)
    hash_k_np = np.array(hash_key[bidx*64:(bidx+1)*64], dtype=np.int64)
    # Simple rigid decode (the beam would need more key material)
    for sign in (-1, 1):
        plain = [(int(ct_blk[i]) + sign * int(hash_k_np[i])) % N for i in range(len(ct_blk))]
        tl = idx_to_trans(plain)
        s = Q.score_norm(tl)
        if s > -6.5:
            print(f"  block{bidx} sign={sign:+d}: score={s:.3f}  {tl[:40]}")

# 4c: do the four 64-byte blocks, treated as mod-29 vectors, show any mutual
#    cancellation (i.e. does block_A - block_B mod 29 look like text)?
print("\n[4c] block-pair mod-29 subtraction -> English sniff:")
for i in range(4):
    for j in range(i+1, 4):
        a = np.array([b % N for b in blocks[i]], dtype=np.int64)
        b = np.array([b % N for b in blocks[j]], dtype=np.int64)
        diff = (a - b) % N
        tl = idx_to_trans(diff)
        s = Q.score_norm(tl)
        if s > -6.5:
            print(f"  block{i} - block{j} mod29: score={s:.3f}  {tl[:40]}")
        diff2 = (b - a) % N
        tl2 = idx_to_trans(diff2)
        s2 = Q.score_norm(tl2)
        if s2 > -6.5:
            print(f"  block{j} - block{i} mod29: score={s2:.3f}  {tl2[:40]}")

# 4d: hash preimage afresh — can any single block of the payload, under any
#    simple transform, equal the ANEND digest?  (More thorough than campaign9.)
print("\n[4d] hash preimage / partial match (ANEND target):")
ANEND_INT = int(ANEND_HEX, 16)
for algo in ("sha512", "sha3_512", "blake2b", "shake_256"):
    for bidx, blk in enumerate(blocks):
        for transform_name, tb in [
            ("raw",     blk),
            ("xor_ff",  bytes(b ^ 0xFF for b in blk)),
            ("rev",     blk[::-1]),
        ]:
            try:
                h = hashlib.new(algo) if algo != "shake_256" else hashlib.shake_256()
                h.update(tb)
                dig = h.hexdigest(64) if algo == "shake_256" else h.hexdigest()
                if ANEND_HEX.startswith(dig[:16]) or dig.startswith(ANEND_HEX[:16]):
                    print(f"  PARTIAL HIT: block{bidx} {transform_name} via {algo}: {dig[:32]}...")
                if dig == ANEND_HEX:
                    print(f"  *** FULL PREIMAGE MATCH: block{bidx} {transform_name} {algo} ***")
            except Exception:
                pass

print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 72)
print("SUMMARY  — payload_ciphertext.py")
print("=" * 72)
print(f"§1 skip-aware beam (mod-29 ciphertext, {len(candidates)} keys):  "
      f"best={best_s1[0]:.3f}  hits={len(s1_hits)}")
print(f"   English -4.0 / confirm -5.5 / noise-max -6.82")

best_transform = sniff_results[0]
print(f"§2 byte transforms ({len(sniff_results)} combos): "
      f"best entropy={best_transform[0]:.3f} ({best_transform[3]})")
all_dc = [(t[3], m, out) for t in sniff_results for m, out in t[5]]
print(f"   decompression hits: {len(all_dc)}")
for label, method, out in all_dc[:5]:
    print(f"   *** {label} decompressed via {method}: {len(out)} bytes -> {out[:40]!r}")

print(f"§3 raw-payload compression probes: "
      f"(reported inline above — no output = all binary / no hits)")

if best_s1[0] > THRESHOLD or len(s1_hits) > 0 or len(all_dc) > 0:
    print("\n*** POSITIVE STRUCTURE FOUND — review details above ***")
else:
    print("\nAll §§ null.  Payload is not a compressed or skip-OTP-enciphered message")
    print("under any tested key from the Cicada key-discipline space.")
    print("Consistent with: either a true OTP (key unknown) or public-key/hash material.")
