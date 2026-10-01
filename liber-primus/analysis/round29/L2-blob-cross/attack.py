#!/usr/bin/env python3
"""L2-blob-cross: two-time-pad / crib-drag attack on the unidentified high-entropy
opaque blobs.

Three batteries:
  1. CROSS-XOR every unordered pair of blobs (offset 0 + slide short-vs-long window).
     If two share a pad, XOR(c1,c2)=XOR(p1,p2) collapses entropy -> English structure.
  2. Each blob as an OTP PAD over KNOWN Cicada plaintexts (solved LP pages, PGP bodies,
     "For Every Thing That Lives Is Holy"). If blob^plaintext yields a structured
     keystream, that's a hit.
  3. Self-structure: byte-entropy, IC, autocorrelation / repeated-block search, and
     header-hunt after reverse / xor-0xFF / rotate / base64-decode.

CONTROLS (run first): positive control must FIRE, negative control must NOT.
"""
import os, sys, math, base64, itertools, json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ART = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/artifacts"
EXTR = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/armada_osint/extracts"
PP49 = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/analysis/pp49_51/canon_256.bin"
ROOT = "/mnt/c/Users/dukot/projects/cicada3301/liber-primus"

# ---------------- metrics ----------------
def entropy(b):
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def ic(b):
    if len(b) < 2: return 0.0
    c = Counter(b); n = len(b)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1))

def printable_ratio(b):
    if not b: return 0.0
    p = sum(1 for x in b if 32 <= x < 127 or x in (9,10,13))
    return p/len(b)

def longest_printable_run(b):
    best = cur = 0
    for x in b:
        if 32 <= x < 127:
            cur += 1; best = max(best, cur)
        else:
            cur = 0
    return best

# space-heavy English cribs for crib-drag (two-time-pad drag). Kept LONG
# (>=5 incl. bounding spaces) so a chance all-alpha hit is astronomically unlikely.
CRIBS = [b" the ", b" and ", b" cicada ", b" you ", b" that ", b" within ",
         b" primus ", b" there ", b" this ", b" every ", b" thing "]

# common English fragments the *other* message would reveal if a crib aligns to a
# real word boundary. We require the recovered fragment to itself contain a common
# English substring -- a random 4-5 char alpha window will NOT, so this kills the
# birthday-paradox false positives that a bare all-alpha test suffers.
COMMON = [b"the", b"and", b"ing", b"ion", b"ent", b"tha", b"her", b"you", b"are",
          b" a ", b" i ", b" to", b" of", b" in", b" is", b"th", b"in", b"er",
          b"an ", b"on ", b"at ", b"es ", b"ed ", b"or ", b"cic", b"ada", b"330"]

def crib_drag(x, cribs=CRIBS):
    """Two-time-pad crib drag with a WORD-VALIDATED gate. Slide each space-heavy
    crib across the XOR stream; the window decodes to a candidate fragment of the
    OTHER plaintext. Only count it a hit if that fragment is all printable-text AND
    contains a common English trigram/word -- this makes the detector fire on real
    English^English and stay silent on random^random (see controls)."""
    hits = []
    n = len(x)
    for crib in cribs:
        lc = len(crib)
        for pos in range(0, n - lc + 1):
            frag = bytes(x[pos+i] ^ crib[i] for i in range(lc))
            if not all(32 <= c < 127 for c in frag):
                continue
            low = frag.lower()
            if not all(chr(c).isalpha() or c == 0x20 for c in frag):
                continue
            if any(w in low for w in COMMON):
                hits.append((crib, pos, frag))
    return hits

def xor_bytes(a, b):
    n = min(len(a), len(b))
    return bytes(a[i] ^ b[i] for i in range(n))

# ---------------- load blobs ----------------
def load(path):
    try:
        return open(path, "rb").read()
    except Exception:
        return None

BLOBS = {}
def add(name, path):
    d = load(path)
    if d and len(d) > 0:
        BLOBS[name] = d

add("T2_2jpg", os.path.join(EXTR, "T2.bin"))
add("T3_folly_extract", os.path.join(EXTR, "T3.bin"))
add("T4_blob1", os.path.join(ART, "T4_blob1.bin"))
add("T4_blob2", os.path.join(ART, "T4_blob2.bin"))
add("T4_blob3", os.path.join(ART, "T4_blob3.bin"))
add("folly", os.path.join(ART, "folly.bin"))
add("folly_snap2", os.path.join(ART, "folly_snap2.bin"))
add("wisdom", os.path.join(ART, "wisdom.bin"))
add("lpc02_out", os.path.join(ART, "lpc02_out.bin"))
add("nokey_dl_1033", os.path.join(ART, "nokey_dl_1033.bin"))
add("t5_nokey", os.path.join(ART, "t5_nokey.bin"))
add("T1_onion3", os.path.join(EXTR, "T1-onion3-5x5-rune-outguess.bin"))
add("canon_256", PP49)

print("=== LOADED BLOBS ===")
for n, d in sorted(BLOBS.items()):
    print(f"  {n:20s} {len(d):>9d} bytes   H={entropy(d):.3f}  IC={ic(d):.5f}  "
          f"printable={printable_ratio(d):.2f}")
print()

# ---------------- CONTROLS ----------------
def controls():
    import random
    rng = random.Random(3301)
    pad = bytes(rng.randrange(256) for _ in range(400))
    p1 = (b"the quick brown fox jumps over the lazy dog and the cicada sings within "*6)[:400]
    p2 = (b"within the deep web there exists a page that hashes to a sacred prime and "*6)[:400]
    c1 = bytes(p1[i]^pad[i] for i in range(400))
    c2 = bytes(p2[i]^pad[i] for i in range(400))
    xored = xor_bytes(c1, c2)          # = p1 ^ p2 (English^English)
    pos_H = entropy(xored)
    pos_hits = crib_drag(xored)
    # negative: two independent random strings
    r1 = bytes(rng.randrange(256) for _ in range(400))
    r2 = bytes(rng.randrange(256) for _ in range(400))
    negx = xor_bytes(r1, r2)
    neg_H = entropy(negx)
    neg_hits = crib_drag(negx)
    print("=== CONTROLS ===")
    print(f"  POSITIVE (shared pad, English^English): H={pos_H:.3f} IC={ic(xored):.5f} "
          f"printable={printable_ratio(xored):.2f} crib_hits={len(pos_hits)}")
    if pos_hits:
        for crib,pos,frag in pos_hits[:3]:
            print(f"      crib {crib!r} @ {pos}: {frag!r}")
    print(f"  NEGATIVE (independent random):          H={neg_H:.3f} IC={ic(negx):.5f} "
          f"printable={printable_ratio(negx):.2f} crib_hits={len(neg_hits)}")
    fired_pos = len(pos_hits) > 0
    fired_neg = len(neg_hits) > 0
    ok = fired_pos and not fired_neg
    print(f"  DETECTOR VALID: positive fired={fired_pos}  negative fired={fired_neg}  -> {'PASS' if ok else 'FAIL'}")
    print()
    return ok

# ---------------- BATTERY 1: cross-XOR pair matrix ----------------
def battery1():
    print("=== BATTERY 1: CROSS-XOR PAIR MATRIX ===")
    names = sorted(BLOBS.keys())
    rows = []
    flagged = []
    for a, b in itertools.combinations(names, 2):
        da, db = BLOBS[a], BLOBS[b]
        n = min(len(da), len(db))
        # offset-0 align
        x = xor_bytes(da, db)
        H = entropy(x); I = ic(x); pr = printable_ratio(x); lr = longest_printable_run(x)
        hits = crib_drag(x)
        flag = ""
        if H < 7.5 or len(hits) > 0 or lr > 12:
            flag = "  <== INSPECT"
            flagged.append((a, b, "off0", H, I, pr, lr, hits))
        rows.append((a, b, n, H, I, pr, lr, len(hits)))
        # slide: if lengths differ a lot, slide shorter over longer sampling offsets
        if len(da) != len(db):
            short, longb = (da, db) if len(da) < len(db) else (db, da)
            step = max(1, (len(longb)-len(short)) // 32)
            best_off = None; best_H = 8.1
            for off in range(0, len(longb)-len(short)+1, step):
                xx = bytes(short[i] ^ longb[off+i] for i in range(len(short)))
                HH = entropy(xx)
                if HH < best_H:
                    best_H = HH; best_off = off
            if best_off is not None and best_H < 7.3:
                xx = bytes(short[i] ^ longb[best_off+i] for i in range(len(short)))
                h2 = crib_drag(xx)
                flagged.append((a, b, f"slide off{best_off}", best_H, ic(xx),
                                printable_ratio(xx), longest_printable_run(xx), h2))
    # print matrix
    print(f"  {'blob A':20s} {'blob B':20s} {'ovl':>8s} {'H':>6s} {'IC':>7s} {'pr':>4s} {'run':>4s} {'crib':>4s}")
    for a,b,n,H,I,pr,lr,nh in sorted(rows, key=lambda r: r[3]):
        print(f"  {a:20s} {b:20s} {n:>8d} {H:6.3f} {I:7.5f} {pr:4.2f} {lr:>4d} {nh:>4d}")
    print(f"\n  pairs tested: {len(rows)}   flagged for inspection: {len(flagged)}")
    for a,b,mode,H,I,pr,lr,hits in flagged:
        print(f"  FLAG {a}^{b} [{mode}] H={H:.3f} IC={I:.5f} pr={pr:.2f} run={lr} cribs={len(hits)}")
        for crib,pos,frag in hits[:5]:
            print(f"       crib {crib!r} @ {pos}: {frag!r}")
    print()
    return rows, flagged

# ---------------- known plaintexts ----------------
def load_plaintexts():
    pts = {}
    d = json.load(open(os.path.join(ROOT, "SOLVED-PAGES.json")))
    for p in d["pages"]:
        pts["LP_"+p["title"][:16].replace(" ","_")] = p["plaintext_transliteration"].encode()
    pts["HOLY"] = b"FOR EVERY THING THAT LIVES IS HOLY"
    # PGP body hex (the 2013 message body) from solved_plaintext.txt tail region
    return pts

# ---------------- BATTERY 2: blob as OTP pad over known plaintext ----------------
def battery2():
    print("=== BATTERY 2: BLOB AS OTP PAD OVER KNOWN PLAINTEXT ===")
    pts = load_plaintexts()
    print("  plaintexts:", ", ".join(f"{k}({len(v)})" for k,v in pts.items()))
    flagged = []
    for bn, blob in sorted(BLOBS.items()):
        for pn, pt in pts.items():
            n = min(len(blob), len(pt))
            if n < 20: continue
            # slide the plaintext window across the blob (find alignment giving low-entropy keystream)
            best = None
            step = max(1, (len(blob)-n)//64) if len(blob) > n else 1
            for off in range(0, max(1, len(blob)-n+1), step):
                ks = bytes(blob[off+i] ^ pt[i] for i in range(n))
                H = entropy(ks)
                if best is None or H < best[0]:
                    best = (H, off, ks)
            H, off, ks = best
            pr = printable_ratio(ks); lr = longest_printable_run(ks); I = ic(ks)
            # a "structured keystream" hit: low entropy OR high printable OR long run OR repeated block
            rep = repeated_block(ks)
            hit = (H < 6.0 and n >= 40) or pr > 0.85 or lr > 20 or rep
            tag = "  <== HIT" if hit else ""
            if hit:
                flagged.append((bn, pn, H, off, pr, lr, rep, ks))
            print(f"  {bn:18s} ^ {pn:20s} n={n:>4d} off={off:>7d} H={H:5.3f} IC={I:.4f} "
                  f"pr={pr:.2f} run={lr:>3d} rep={rep}{tag}")
    print(f"\n  battery2 hits: {len(flagged)}")
    for bn,pn,H,off,pr,lr,rep,ks in flagged:
        print(f"  HIT {bn}^{pn} H={H:.3f} off={off} pr={pr:.2f} run={lr} rep={rep}")
        print(f"      keystream[:60]={ks[:60]!r}")
    print()
    return flagged

def repeated_block(b, blk=8):
    """Return the most common repeated block>=2 occurrences, else None."""
    if len(b) < blk*2: return None
    seen = Counter(bytes(b[i:i+blk]) for i in range(0, len(b)-blk+1, blk))
    top = seen.most_common(1)
    if top and top[0][1] >= 3:
        return top[0][1]
    return None

# ---------------- BATTERY 3: self-structure ----------------
def autocorr_peaks(b, maxlag=None):
    """Byte-equality autocorrelation: for each lag, fraction of positions where
    b[i]==b[i+lag]. Random ~1/256=0.0039. Peaks reveal period/structure."""
    n = len(b)
    if maxlag is None: maxlag = min(n//2, 2048)
    base = 1/256
    peaks = []
    for lag in range(1, maxlag):
        m = n - lag
        if m < 64: break
        eq = sum(1 for i in range(0, m, max(1, m//4000)) )  # sample
        # do a real sampled count
        step = max(1, m//4000)
        cnt = tot = 0
        for i in range(0, m, step):
            tot += 1
            if b[i] == b[i+lag]: cnt += 1
        r = cnt/tot if tot else 0
        if r > base*4 and r > 0.02:
            peaks.append((lag, r))
    peaks.sort(key=lambda x:-x[1])
    return peaks[:10]

def header_hunt(b):
    """After common transforms, look for known magic bytes at offset 0."""
    MAGICS = {
        b"\xff\xd8\xff":"JPEG", b"\x89PNG":"PNG", b"PK\x03\x04":"ZIP",
        b"\x1f\x8b":"GZIP", b"BZh":"BZIP2", b"7z\xbc\xaf":"7Z",
        b"-----BEGIN":"PGP/PEM", b"%PDF":"PDF", b"OggS":"OGG",
        b"RIFF":"RIFF", b"\x00\x00\x01":"MPEG", b"ID3":"MP3",
        b"\xfd7zXZ":"XZ", b"BM":"BMP", b"GIF8":"GIF",
    }
    def check(data, label):
        found = []
        for mg, name in MAGICS.items():
            if data[:len(mg)] == mg:
                found.append((label, name))
        return found
    out = []
    out += check(b, "raw")
    out += check(b[::-1], "reversed")
    out += check(bytes(x^0xFF for x in b), "xor0xFF")
    for r in (1,2,3,4,7):
        out += check(bytes(((x<<r)|(x>>(8-r)))&0xFF for x in b), f"rotl{r}")
    # base64 decode attempt if it looks base64-ish
    try:
        txt = b.decode("ascii")
        if all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in txt[:200]):
            dec = base64.b64decode(txt + "="*(-len(txt)%4), validate=False)
            out += check(dec, "b64decode")
    except Exception:
        pass
    return out

def battery3():
    print("=== BATTERY 3: SELF-STRUCTURE ===")
    findings = {}
    for bn, blob in sorted(BLOBS.items()):
        rep = repeated_block(blob)
        peaks = autocorr_peaks(blob)
        hdr = header_hunt(blob)
        findings[bn] = dict(rep=rep, peaks=peaks, hdr=hdr)
        print(f"  {bn:20s} H={entropy(blob):.3f} IC={ic(blob):.5f}")
        print(f"      repeated_block(8): {rep}")
        print(f"      autocorr peaks (lag,rate): {peaks[:5]}")
        print(f"      header_hunt: {hdr if hdr else 'none'}")
    print()
    return findings

if __name__ == "__main__":
    ok = controls()
    if not ok:
        print("!!! CONTROL FAILED -- detector invalid, aborting claims !!!")
    b1 = battery1()
    b2 = battery2()
    b3 = battery3()
    print("=== DONE ===")
