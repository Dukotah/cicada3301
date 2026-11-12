"""W2-C3 step 3 — residue inventory (PREREG §4.3).

a) verify every TRAILING-DATA.json row on disk (file sha + trailer sha);
b) identify() every distinct trailer under the CORE transform family;
c) walk appended-image chains recursively + match inner images against a corpus sha index;
d) byte-account the 05/0_wisdom trailer and the Huh2 trailer end-to-end;
e) verify/refute the Outt.png palindrome + 15-byte-unit claims;
f) classify the 9 unparseable files (walker failure point + residue battery).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
LP = os.path.abspath(os.path.join(CELL, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(LP, ".."))
CORPUS = os.path.join(REPO, "corpus", "A-primary-artifacts")
sys.path.insert(0, HERE)
import residue_lib as R

TD = json.load(open(os.path.join(CORPUS, "TRAILING-DATA.json")))
OUT = {"a_row_verification": [], "b_trailer_identify": {}, "c_chains": {},
       "d_byte_accounting": {}, "e_outt": {}, "f_unparseable": []}

# ---------------------------------------------------------------- corpus sha index
print("building corpus sha index ...", flush=True)
sha_index = {}
for root, dirs, files in os.walk(CORPUS):
    if ".gnupg-lane-a" in root:
        continue
    for f in files:
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            p = os.path.join(root, f)
            try:
                b = open(p, "rb").read()
            except OSError:
                continue
            rel = os.path.relpath(p, CORPUS)
            sha_index.setdefault(R.sha(b), []).append(rel)
            # image-only prefix sha (so "X == image part of Y" matches too)
            if b[:2] == b"\xff\xd8":
                e, _ = R.jpeg_end_scan(b)
            elif b[:8] == b"\x89PNG\r\n\x1a\n":
                e, _ = R.png_end(b)
            else:
                e = None
            if e and e < len(b):
                sha_index.setdefault(R.sha(b[:e]), []).append(rel + "#image-prefix")
# relikd masters too
RELIKD = os.path.join(LP, "data", "relikd")
for f in sorted(os.listdir(RELIKD)):
    if f.lower().endswith(".jpg"):
        b = open(os.path.join(RELIKD, f), "rb").read()
        sha_index.setdefault(R.sha(b), []).append("relikd/" + f)
        e, _ = R.jpeg_end_scan(b)
        if e and e < len(b):
            sha_index.setdefault(R.sha(b[:e]), []).append("relikd/" + f + "#image-prefix")
print("index:", len(sha_index), "shas", flush=True)

def match(s):
    return sha_index.get(s, [])

# ---------------------------------------------------------------- (a) verify rows
trailers = {}   # trailing_sha -> (bytes, example path)
for row in TD["trailing"]:
    p = os.path.join(CORPUS, row["path"])
    ver = {"path": row["path"], "on_disk": os.path.exists(p)}
    if ver["on_disk"]:
        b = open(p, "rb").read()
        ver["file_sha_match"] = R.sha(b) == row["sha256"]
        tb = b[row["image_ends_at"]:]
        ver["trailer_sha_match"] = R.sha(tb) == row["trailing_sha256"]
        if ver["trailer_sha_match"]:
            trailers.setdefault(row["trailing_sha256"], (tb, row["path"]))
    OUT["a_row_verification"].append(ver)

# ---------------------------------------------------------------- (b)+(c) identify + chains
for tsha, (tb, path) in sorted(trailers.items(), key=lambda kv: -len(kv[1][0])):
    small = len(tb) <= 65536
    rep = R.identify(tb, transforms=R.CORE, decomp_headers_only=not small)
    rep["from"] = path
    OUT["b_trailer_identify"][tsha[:16]] = rep
    segs = R.walk_chain(tb)
    OUT["c_chains"][tsha[:16]] = [
        {"kind": s[0], "start": s[1], "end": s[2], "sha16": s[3][:16],
         "matches": match(s[3]), "why": (s[4] if len(s) > 4 else None)} for s in segs]
    print("identified", path, len(tb), "segs:", [(s[0], s[1], s[2]) for s in segs], flush=True)

# ---------------------------------------------------------------- (d) byte accounting
def account_reversed_jpeg(tb, label):
    """Trailer suspected to be (part of) a byte-reversed JPEG.  Reverse, walk, account."""
    rb = tb[::-1]
    acc = {"label": label, "trailer_bytes": len(tb)}
    # the reversed stream should END with a JPEG whose EOI is rb[-?]; a reversed JPEG
    # trailer that was appended tail-first begins with d9ff -> reversed, the JPEG sits at
    # the END of rb.  Find last SOI in rb and walk from there; also walk any prefix.
    soi = rb.rfind(b"\xff\xd8\xff")
    acc["last_soi_in_reversed"] = soi
    if soi >= 0:
        e, why = R.jpeg_end_scan(rb[soi:])
        acc["jpeg_from_last_soi"] = {"end": e, "why": why,
                                     "complete": bool(e and soi + e == len(rb))}
        if e:
            jb = rb[soi:soi + e]
            acc["jpeg_sha16"] = R.sha(jb)[:16]
            acc["jpeg_matches"] = match(R.sha(jb))
            try:
                from PIL import Image
                import io
                im = Image.open(io.BytesIO(jb))
                im.load()
                acc["jpeg_decodes"] = True
                acc["jpeg_size"] = im.size
            except Exception as ex:
                acc["jpeg_decodes"] = f"FAIL: {ex}"
        pre = rb[:soi]
        acc["gap_before_jpeg_bytes"] = len(pre)
        if pre:
            acc["gap_report"] = R.identify(pre, transforms=R.CORE,
                                           decomp_headers_only=len(pre) > 65536)
            acc["gap_printable_head"] = pre[:400].decode("latin1")
            acc["gap_sha16"] = R.sha(pre)[:16]
    return acc

for key, label in [("0d7a3ec5339b6578", "Huh2.jpg trailer (175159B, starts d9ff)"),
                   ("3814d8b9ca2e3694", "05.jpg / relikd 0_wisdom.jpg trailer (336713B)")]:
    full = [t for t in trailers if t.startswith(key)]
    if full:
        tb, path = trailers[full[0]]
        OUT["d_byte_accounting"][key] = account_reversed_jpeg(tb, label + " @ " + path)
        print("accounted", label, flush=True)

# ---------------------------------------------------------------- (e) Outt.png trailer
full = [t for t in trailers if t.startswith("044a0b54dcf7ebc5")]
if full:
    tb, path = trailers[full[0]]
    e = {"bytes": len(tb), "sha256": R.sha(tb)}
    e["byte_palindrome"] = R.is_byte_palindrome(tb)
    e["palindrome_core_bytes"] = R.palindrome_core(tb)
    bits = "".join(f"{x:08b}" for x in tb)
    e["bit_palindrome"] = bits == bits[::-1]
    p, mism = R.smallest_period(tb, max_p=256)
    e["smallest_byte_period"] = p
    e["period_mismatches"] = mism
    # bit-level period
    bp = None
    for q in range(1, 512):
        if all(bits[i] == bits[i + q] for i in range(0, len(bits) - q, max(1, (len(bits) - q) // 4096) or 1)):
            if all(bits[i] == bits[i + q] for i in range(len(bits) - q)):
                bp = q
                break
    e["smallest_bit_period"] = bp
    e["unit15_hex"] = tb[:15].hex()
    # where does pure periodicity break?
    if p:
        brk = [i for i in range(len(tb) - p) if tb[i] != tb[i + p]]
        e["period_break_positions"] = brk[:50]
        e["n_period_breaks"] = len(brk)
    # 5-bit view of the repeating unit (120 bits = 24 x 5-bit)
    u = bits[:120]
    e["unit_bits"] = u
    e["unit_as_5bit"] = [int(u[i:i + 5], 2) for i in range(0, 120, 5)]
    e["unit_as_4bit"] = [int(u[i:i + 4], 2) for i in range(0, 120, 4)]
    e["unit_as_3bit"] = [int(u[i:i + 3], 2) for i in range(0, 120, 3)]
    e["ones_density"] = bits.count("1") / len(bits)
    OUT["e_outt"] = e
    print("outt analysed", flush=True)

# ---------------------------------------------------------------- (f) unparseable 9
from PIL import Image
for rel in TD["unparseable"]:
    p = os.path.join(CORPUS, rel)
    f = {"path": rel, "on_disk": os.path.exists(p)}
    if f["on_disk"]:
        b = open(p, "rb").read()
        f["bytes"] = len(b)
        f["sha16"] = R.sha(b)[:16]
        f["head_hex"] = b[:16].hex()
        if b[:2] == b"\xff\xd8":
            e2, why = R.jpeg_end_scan(b)
            f["walker"] = {"end": e2, "why": why}
        elif b[:8] == b"\x89PNG\r\n\x1a\n":
            e2, why = R.png_end(b)
            f["walker"] = {"end": e2, "why": why}
        else:
            f["walker"] = {"end": None, "why": "not JPEG/PNG signature"}
        try:
            import io
            im = Image.open(io.BytesIO(b))
            im.load()
            f["pil_decodes"] = True
            f["pil_format_size"] = [im.format, im.size]
        except Exception as ex:
            f["pil_decodes"] = f"FAIL: {str(ex)[:120]}"
        f["dupes_in_corpus"] = match(R.sha(b))
        # if the walker failed mid-file, battery on the bytes after the failure point
        end = f["walker"]["end"]
        if end is None and f["walker"]["why"] and "sync" in str(f["walker"]["why"]):
            off = int(str(f["walker"]["why"]).split(" at offset ")[1].split()[0]) if " at offset " in str(f["walker"]["why"]) else None
            if off:
                res = b[off:]
                f["post_failure_identify"] = R.identify(res, transforms=R.CORE,
                                                        decomp_headers_only=len(res) > 65536)
    OUT["f_unparseable"].append(f)
    print("unparseable:", rel, f.get("walker"), f.get("pil_decodes"), flush=True)

json.dump(OUT, open(os.path.join(CELL, "results", "inventory.json"), "w"), indent=1)
print("WROTE results/inventory.json")
