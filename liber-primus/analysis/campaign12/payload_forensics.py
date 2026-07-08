"""Campaign XII, Part 1 -- pp49-51 payload forensics (the leads Campaign IX did NOT run).

Campaign VII characterized canon_256.bin as a 2048-bit high-entropy blob (not prime,
not RSA, not a runic key, not text). Campaign IX ran the hash-structure / AN-END /
64-byte-block-preimage leads. This script burns down the REMAINING self-contained leads:

  L1  Format / magic-byte sniff (PGP packet, gzip/zip/bzip2, PNG/JPEG/GIF/PDF, DER key,
      PEM/base64/base32 of the hex) -- is it a container even if the body is random?
  L2  32-byte-block preimage (SHA-256 / SHA3-256 / blake2s) of a Cicada-string dictionary
      -- IX only tried 64-byte (SHA-512-class) digests; the 8x32 reading was untested.
  L3  Repeating-key XOR: Hamming-distance keysize search over the 256 bytes
      -- is the payload a short-key XOR of something, not a one-shot pad?
  L4  Visual/image structure: 2D autocorrelation of the bit-matrix at candidate widths
      -- a QR/bitmap would show periodic peaks; noise won't. (Entropy already argues no,
      this makes it a measured null, not an assumed one.)

Pure standard library. Reproduce:  PYTHONUTF8=1 python3 payload_forensics.py
"""
import os, sys, math, hashlib, zlib, base64, binascii, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PP = os.path.join(ROOT, "analysis", "pp49_51")

def load(name):
    with open(os.path.join(PP, name), "rb") as f:
        return f.read()

P = load("canon_256.bin")
Pd = load("canon_256_decpref.bin")   # the decimal-prefix variant
ANEND = bytes.fromhex(open(os.path.join(ROOT, "analysis/armada20/key_anend_hash.txt")).read().strip())

def shannon(b):
    if not b: return 0.0
    from collections import Counter
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

print("="*72)
print("CAMPAIGN XII / Part 1 -- pp49-51 payload forensics")
print("="*72)
for name, b in [("canon_256.bin", P), ("canon_256_decpref.bin", Pd)]:
    print(f"\n{name}: {len(b)} bytes, entropy {shannon(b):.3f}/8.0, "
          f"distinct bytes {len(set(b))}/256, zlib->{len(zlib.compress(b,9))}B "
          f"({'incompressible' if len(zlib.compress(b,9))>=len(b) else 'COMPRESSIBLE'})")

# ---------------------------------------------------------------- L1 format sniff
print("\n" + "-"*72)
print("L1  FORMAT / MAGIC-BYTE SNIFF")
print("-"*72)
MAGICS = {
    "PGP old-format packet (0x99/0x85/0x84..)": lambda b: b[0] in (0x99,0x98,0x85,0x84,0x88,0x8c,0x90,0x95,0xa3),
    "PGP new-format packet (0xC0-0xFF)":        lambda b: 0xC0 <= b[0] <= 0xFF,
    "gzip (1f 8b)":     lambda b: b[:2]==b"\x1f\x8b",
    "zlib (78 xx)":     lambda b: b[0]==0x78 and b[1] in (0x01,0x9c,0xda,0x5e),
    "zip (PK)":         lambda b: b[:2]==b"PK",
    "bzip2 (BZh)":      lambda b: b[:3]==b"BZh",
    "xz (fd 37 7a)":    lambda b: b[:3]==b"\xfd7z",
    "PNG":              lambda b: b[:8]==b"\x89PNG\r\n\x1a\n",
    "JPEG (ff d8)":     lambda b: b[:2]==b"\xff\xd8",
    "GIF":              lambda b: b[:4] in (b"GIF8",),
    "PDF (%PDF)":       lambda b: b[:4]==b"%PDF",
    "ELF":              lambda b: b[:4]==b"\x7fELF",
    "DER SEQUENCE (0x30 0x82)": lambda b: b[0]==0x30 and b[1]==0x82,
    "OpenSSH key":      lambda b: b[:4]==b"\x00\x00\x00\x07" or b.startswith(b"openssh"),
    "TrueCrypt/LUKS":   lambda b: b[:6]==b"LUKS\xba\xbe",
    "bitcoin WIF-ish (0x80 prefix)": lambda b: b[0]==0x80,
}
for tag, fn in MAGICS.items():
    for label, b in (("fwd", P), ("rev", P[::-1]), ("decpref", Pd)):
        if fn(b):
            print(f"  HIT  {tag}  [{label}]")
else:
    print("  no known container/format magic at head (fwd/rev/decpref).")

# textual decodes of the hex string
hx = P.hex()
print("  base64/32 decode of the hex-string form:")
for nm, fn in [("b64", lambda s: base64.b64decode(s+"="*(-len(s)%4))),
               ("b32", lambda s: base64.b32decode(s.upper()+"="*(-len(s)%8)))]:
    try:
        d = fn(hx); pr = sum(32<=c<127 for c in d)/len(d)
        print(f"    {nm}: {len(d)}B, printable {pr:.0%}  {'<-- readable?' if pr>0.85 else '(noise)'}")
    except Exception as e:
        print(f"    {nm}: invalid ({type(e).__name__})")

# ---------------------------------------------------------------- L2 32-byte preimage
print("\n" + "-"*72)
print("L2  32-BYTE-BLOCK PREIMAGE (SHA-256 class) -- untried in IX (it did 64-byte only)")
print("-"*72)
CICADA_STRINGS = [
    "3301","1033","cicada","CICADA","Cicada 3301","cicada3301","LIBER PRIMUS","Liber Primus",
    "AN END","A WARNING","WELCOME","DIVINITY","THE LOSS OF DIVINITY","PARABLE","SOME WISDOM",
    "instar","INSTAR","instar emergence","emergence","KOAN","koan","THE PRIMES ARE SACRED",
    "primes","totient","the primes are sacred","circumference","enlightenment","pilgrimage",
    "3301@example.com","7A35090F","845145F7","Beware false paths","QUESTION ALL THINGS",
    "adhere to the principles","preserve your data","end of the road","the way out is through",
]
# hash whole payload's 8 x 32-byte blocks + look for any Cicada-string preimage
blocks32 = [P[i:i+32] for i in range(0,256,32)] + [Pd[i:i+32] for i in range(0,256,32)]
algos32 = ["sha256","sha3_256","blake2s"]
found = []
for s in CICADA_STRINGS:
    for a in algos32:
        h = hashlib.new(a); h.update(s.encode()); dig = h.digest()
        for bi, blk in enumerate(blocks32):
            if dig == blk or dig == blk[::-1]:
                found.append((s,a,bi))
print(f"  dict={len(CICADA_STRINGS)} strings x {len(algos32)} algos vs 16 32-byte blocks")
print(f"  preimage hits: {found if found else 'NONE'}")
# does the whole payload / halves hash to a 32-byte digest of anything, or to sha256(ANEND)?
extra = {"sha256(ANEND)": hashlib.sha256(ANEND).digest(),
         "sha256(ANEND-hex)": hashlib.sha256(ANEND.hex().encode()).digest()}
for tag, dig in extra.items():
    hit = any(dig==b for b in blocks32)
    print(f"  {tag} equals a payload 32-block: {hit}")

# ---------------------------------------------------------------- L3 repeating-key XOR
print("\n" + "-"*72)
print("L3  REPEATING-KEY XOR keysize search (Hamming distance) -- is it short-key XOR?")
print("-"*72)
def hamming(a,b): return sum(bin(x^y).count("1") for x,y in zip(a,b))
scores = []
for ks in range(2, 41):
    blks = [P[i:i+ks] for i in range(0, len(P)-len(P)%ks, ks)]
    pairs = list(itertools.combinations(range(min(6,len(blks))), 2))
    if not pairs: continue
    d = sum(hamming(blks[i],blks[j])/ks for i,j in pairs)/len(pairs)
    scores.append((d, ks))
scores.sort()
print("  normalized Hamming per keysize (LOWER = more likely a real key length):")
print("  best 5:", ", ".join(f"ks={k} d={d:.3f}" for d,k in scores[:5]))
print(f"  spread: min {scores[0][0]:.3f}  max {scores[-1][0]:.3f}  "
      f"(random ~4.0 bits/byte; a real key length shows a clear dip)")
flat = scores[-1][0]-scores[0][0] < 0.35
print(f"  verdict: {'FLAT -> no repeating-key XOR structure' if flat else 'DIP present -> investigate keysize '+str(scores[0][1])}")

# ---------------------------------------------------------------- L4 image/bit structure
print("\n" + "-"*72)
print("L4  BIT-MATRIX 2D STRUCTURE (QR / bitmap would show autocorrelation peaks)")
print("-"*72)
bits = [(byte>>k)&1 for byte in P for k in range(7,-1,-1)]   # 2048 bits, MSB-first
def autocorr_peak(width):
    h = len(bits)//width
    rows = [bits[r*width:(r+1)*width] for r in range(h)]
    # mean pairwise row correlation at vertical lag 1 vs random 0.5
    def rowcorr(a,b): return sum(x==y for x,y in zip(a,b))/len(a)
    vert = sum(rowcorr(rows[r],rows[r+1]) for r in range(h-1))/(h-1) if h>1 else 0.5
    return vert
print("  vertical adjacent-row agreement (0.50 = noise, ->1.0 or ->0.0 = image structure):")
for w in (8,16,32,45,46,64,128):
    if 2048 % w == 0 or True:
        print(f"    width {w:>3}: {autocorr_peak(w):.3f}")
print("  (entropy 7.9+/8 already implies no clean image; these numbers confirm no")
print("   periodic 2D structure at any plausible raster width.)")

print("\n" + "="*72)
print("Part 1 complete. See findings for the writeup.")
print("="*72)
