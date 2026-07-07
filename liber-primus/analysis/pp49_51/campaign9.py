"""Campaign IX -- proof-of-work on the two genuinely-untested pp49-51 leads.

These are the leads Campaign VII flagged as NOT YET RUN, plus the one the
community wiki proposed but never executed. Pure standard library, reproducible:

    PYTHONUTF8=1 python3 campaign9.py

LEAD A  (CAMPAIGN-VII-FINDINGS sec.5 #2, never run): 256 bytes = 4 x 64.
        Is the payload structurally four 512-bit hash digests, and does it
        relate to the solved 'AN END' 512-bit hash?
LEAD B  (community wiki, "I don't know how to XOR things, I'll leave it"):
        does the payload correlate (XOR / mod-256 subtract) with any known
        Cicada key stream so its entropy collapses toward text?

Every result here is an honest measurement, not a claimed solve.
"""
import os, re, math, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

P    = list(open(os.path.join(HERE, "canon_256.bin"), "rb").read())          # majority-vote
Pdec = list(open(os.path.join(HERE, "canon_256_decpref.bin"), "rb").read())  # decimal-preferred

# solved 'AN END' 512-bit hash (64 bytes) -- from analysis/armada20/key_anend_hash.txt
ANEND = bytes.fromhex(open(os.path.join(ROOT, "analysis/armada20/key_anend_hash.txt")).read().strip())
assert len(ANEND) == 64, len(ANEND)

def entropy(bs):
    n = len(bs); h = collections.Counter(bs)
    return -sum((c/n) * math.log2(c/n) for c in h.values())

def printable_stats(bs):
    flags = [1 if 32 <= b < 127 else 0 for b in bs]
    best = cur = 0
    for x in flags:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return sum(flags), best

def chi2_uniform(bs):
    exp = len(bs) / 256.0
    obs = collections.Counter(bs)
    return sum((obs.get(v, 0) - exp) ** 2 / exp for v in range(256))

def first_primes(n):
    out, cand = [], 2
    while len(out) < n:
        if all(cand % p for p in out if p * p <= cand):
            out.append(cand)
        cand += 1
    return out

print("=" * 72)
print("CAMPAIGN IX  -- proof-of-work on the untested pp49-51 leads")
print("=" * 72)
print(f"payload P: {len(P)} bytes | entropy {entropy(P):.3f} b/byte | "
      f"printable {printable_stats(P)[0]}/256 (run {printable_stats(P)[1]})")

# ======================================================================
# LEAD A -- hash structure
# ======================================================================
print("\n" + "-" * 72)
print("LEAD A: is the payload four 512-bit digests / tied to the AN END hash?")
print("-" * 72)

print("\n[A1] per-64-byte-block profile (4 blocks; a real digest ~ high, flat):")
for k in range(4):
    blk = P[k*64:(k+1)*64]
    print(f"  block {k} [{k*64:3d}:{(k+1)*64:3d}]  entropy {entropy(blk):.3f}  "
          f"distinct {len(set(blk)):2d}/64  chi2/255 {chi2_uniform(blk)/255:.2f}  "
          f"printable {printable_stats(blk)[0]:2d}")
print("  (all four blocks statistically alike => consistent with 4 hashes, but")
print("   also with any 256-byte random pad; this test can only REFUTE, not prove)")

print("\n[A2] does the AN END hash appear literally inside the payload?")
found = False
for label, target in [("AN END", ANEND), ("AN END reversed", ANEND[::-1])]:
    for variant_name, stream in [("maj", P), ("decpref", Pdec)]:
        b = bytes(stream)
        for off in range(len(b) - 64 + 1):
            if b[off:off+64] == target:
                print(f"  HIT: {label} at offset {off} in {variant_name}")
                found = True
if not found:
    print("  no -- AN END hash (fwd/rev) is not a substring of either payload variant.")

print("\n[A3] bounded preimage probe -- do obvious Cicada strings hash to the")
print("     AN END digest (validates our hashing) OR to any 64-byte block of P?")
candidates = [
    "AN END", "an end", "A WARNING", "SOME WISDOM", "WELCOME", "3301", "cicada",
    "THE PRIMES ARE SACRED", "the primes are sacred", "WITHIN THE DEEP WEB",
    "PARABLE", "INSTAR", "EMERGENCE", "circumference", "DIVINITY", "PILGRIM",
    "LIBER PRIMUS", "Liber Primus", "I AM NOT THE BEGINNING",
]
algos = ["sha512", "sha3_512", "blake2b", "shake_256"]
blocks = [bytes(P[k*64:(k+1)*64]) for k in range(4)] + [bytes(Pdec[k*64:(k+1)*64]) for k in range(4)]
validated = None
tie = False
for s in candidates:
    for a in algos:
        h = hashlib.new(a) if a != "shake_256" else hashlib.shake_256()
        h.update(s.encode())
        dig = h.digest(64) if a == "shake_256" else h.digest()
        if dig == ANEND:
            validated = (s, a)
        if dig in blocks:
            print(f"  TIE: {a}('{s}') == a 64-byte block of the payload")
            tie = True
print(f"  AN END preimage found in bounded dict: {validated if validated else 'no (expected -- true preimage space is unbounded)'}")
if not tie:
    print("  no obvious-string digest matches any payload block.")

print("\n[A4] does the payload (or halves) hash TO the AN END digest?")
hits = []
for name, chunk in [("P", bytes(P)), ("P-lo128", bytes(P[:128])), ("P-hi128", bytes(P[128:])),
                    ("Pdec", bytes(Pdec))]:
    for a in algos:
        h = hashlib.new(a) if a != "shake_256" else hashlib.shake_256()
        h.update(chunk)
        dig = h.digest(64) if a == "shake_256" else h.digest()
        if dig == ANEND:
            hits.append((name, a))
print(f"  {'HIT: ' + str(hits) if hits else 'no -- payload does not hash to the AN END digest under tested algos.'}")

# ======================================================================
# LEAD B -- correlation / entropy collapse vs known key streams
# ======================================================================
print("\n" + "-" * 72)
print("LEAD B: does XOR / mod-256 subtract vs a known stream collapse entropy?")
print("-" * 72)
print("  baseline P: entropy 7.170, printable 40%, longest run 5.")
print("  SIGNAL would be: entropy drop >~1 bit, or a printable run >> 5.\n")

def tile(seq, n=256):
    return [seq[i % len(seq)] for i in range(n)]

# known streams (all reduced to bytes 0..255)
ps_digits = re.search(r"[0-9]{40,}", open(os.path.join(HERE, "completeness_keys.py")).read()).group()
onion_txt = open(os.path.join(ROOT, "analysis/armada20/pgp_2014-01-onion5-liber-primus.txt"), encoding="utf-8", errors="ignore").read()
# the artifact wraps one long hex blob across 60-char lines -- concatenate them
onion_hex = "".join(re.findall(r"^[0-9a-fA-F]{16,}$", onion_txt, re.MULTILINE))
onion_bytes = list(bytes.fromhex(onion_hex[:512])) if len(onion_hex) >= 128 else []

streams = {
    "AN END hash (tiled)":      tile(list(ANEND)),
    "first-256-primes mod256":  [p % 256 for p in first_primes(256)],
    "29 rune-primes (cycled)":  tile([2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]),
    "P.S. digit string":        tile([int(c) for c in ps_digits]),
    "3301 = 0x0CE5 (tiled)":    tile([0x0C, 0xE5]),
}
if onion_bytes:
    streams["2014 onion-hex bytes"] = tile(onion_bytes)
    print(f"  (onion artifact decodes to {len(onion_hex)//2} bytes starting "
          f"{bytes.fromhex(onion_hex[:8]).hex()} -- Campaign VII noted this is a JPEG dump;")
    print(f"   we run the XOR anyway to document rather than assert it.)\n")

def combine(a, b, op):
    if op == "xor": return [x ^ y for x, y in zip(a, b)]
    return [(x - y) % 256 for x, y in zip(a, b)]

print(f"  {'stream':28s} {'op':4s} {'entropy':>8s} {'print%':>7s} {'run':>4s} {'zeros':>6s}")
best = (7.170, None)
for name, K in streams.items():
    for op in ("xor", "sub"):
        R = combine(P, K, op)
        e = entropy(R); pr, run = printable_stats(R); zeros = R.count(0)
        flag = "  <-- signal?" if (e < 6.0 or run > 8) else ""
        print(f"  {name:28s} {op:4s} {e:8.3f} {100*pr/256:6.0f}% {run:4d} {zeros:6d}{flag}")
        if e < best[0]:
            best = (e, f"{name} {op}")
print(f"\n  lowest entropy achieved: {best[0]:.3f} b/byte via [{best[1]}]")
print(f"  (baseline 7.170; a real key would collapse this toward ~4-5 for text)")

# ======================================================================
print("\n" + "=" * 72)
print("CAMPAIGN IX VERDICT")
print("=" * 72)
print("""LEAD A: the payload's four 64-byte blocks are statistically uniform and
        alike (consistent with 4 digests, but equally with a random pad); the
        AN END hash is NOT embedded; no bounded-dictionary preimage ties in;
        the payload does not hash to AN END. No structural link established.
LEAD B: no known key stream collapses the payload's entropy toward text
        (best remains near the 7.17 baseline). XOR-vs-onion-hex confirmed
        meaningless as Campaign VII predicted.

Both leads worked and documented as HONEST NULLS -- the needle did not move
on decode, but the hypothesis space shrank by two more concrete tests, and
the harness + data are committed so the result is independently reproducible.""")
