"""W2-C3 step 3b — deep dive on the three residues the inventory left unexplained:
   1) the 360-byte gap in the 05.jpg/0_wisdom trailer (tb[:360], ASCII under reversal);
   2) the Outt.png 13,592-B trailer: exact decomposition vs the 30-bit-periodic carrier,
      break positions, anomaly stream, relation to the PNG's own pixels;
   3) the onion5-liber-primus.jpg residue (9,288 B after the appended Eyebyext.jpg).
"""
import io
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

OUT = {}

# ---------------------------------------------------------- 1) the 360-byte gap
p05 = os.path.join(CORPUS, "cijhho123/2014/Liber Primus/liber primus images full/05.jpg")
b = open(p05, "rb").read()
tb = b[336353:]
gap = tb[:360]                       # reversed-JPEG occupies tb[360:]; gap = tb[:360]
gap_rev = gap[::-1]
OUT["gap05"] = {
    "bytes": len(gap), "sha256": R.sha(gap),
    "reversed_ascii": gap_rev.decode("latin1"),
    "as_is_ascii": gap.decode("latin1"),
}
print("=== 05 gap reversed ===")
print(gap_rev.decode("latin1"))

# ---------------------------------------------------------- 2) Outt.png trailer
po = os.path.join(CORPUS, "wiki-uncovering-cicada/images/Outt.png")
ob = open(po, "rb").read()
end, _ = R.png_end(ob)
t = ob[end:]
unit = t[:15]
rep = {"bytes": len(t), "unit15_hex": unit.hex()}
# exact mismatches vs pure periodic extension of the first 15 bytes
ideal = (unit * (len(t) // 15 + 1))[:len(t)]
mism = [i for i in range(len(t)) if t[i] != ideal[i]]
rep["n_mismatch_vs_unit15"] = len(mism)
rep["first_mismatch"] = mism[0] if mism else None
if mism:
    # contiguous anomaly regions
    regions, s, prev = [], mism[0], mism[0]
    for i in mism[1:]:
        if i > prev + 32:
            regions.append((s, prev + 1))
            s = i
        prev = i
    regions.append((s, prev + 1))
    rep["anomaly_regions"] = regions[:40]
    rep["n_anomaly_regions"] = len(regions)
    anom = b"".join(t[a:z] for a, z in regions)
    rep["anomaly_bytes_total"] = len(anom)
    rep["anomaly_head_hex"] = anom[:64].hex()
    open(os.path.join(CELL, "results", "outt_anomaly.bin"), "wb").write(anom)
    rep["anomaly_identify"] = R.identify(anom, transforms=R.CORE, decomp_headers_only=False)
# does the periodic carrier relate to the image itself?
try:
    from PIL import Image
    import numpy as np
    im = Image.open(io.BytesIO(ob))
    im.load()
    rep["png_mode_size"] = [im.mode, list(im.size)]
    a = np.asarray(im.convert("L"))
    rep["png_mean_lum"] = float(a.mean())
except Exception as ex:
    rep["png_err"] = str(ex)
# bit-phase check: is the WHOLE trailer one 30-bit periodic stream (incl. tail)?
bits = "".join(f"{x:08b}" for x in t)
per30_breaks = [i for i in range(len(bits) - 30) if bits[i] != bits[i + 30]]
rep["n_bit30_breaks"] = len(per30_breaks)
rep["bit30_break_head"] = per30_breaks[:20]
rep["tail16_hex"] = t[-16:].hex()
OUT["outt"] = rep
print("outt: mismatches vs unit15:", rep["n_mismatch_vs_unit15"], "bit30 breaks:", rep["n_bit30_breaks"])

# ---------------------------------------------------------- 3) onion5 residue
p5 = os.path.join(CORPUS, "signed-payloads/2014-01-onion5-liber-primus.jpg")
b5 = open(p5, "rb").read()
t5 = b5[1084:]
segs = R.walk_chain(t5)
res = t5[1635:]
r5 = {"residue_bytes": len(res), "sha256": R.sha(res), "head_hex": res[:32].hex(),
      "entropy": round(R.entropy(res), 3), "printable": round(R.printable_ratio(res), 3)}
# is it a truncated JPEG? walk from 0
e5, why5 = R.jpeg_end_scan(res)
r5["walk"] = [e5, why5]
# try PIL truncated decode
try:
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    im = Image.open(io.BytesIO(res))
    im.load()
    r5["pil"] = [im.format, list(im.size)]
except Exception as ex:
    r5["pil"] = f"FAIL: {str(ex)[:100]}"
r5["identify"] = R.identify(res, transforms=R.CORE, decomp_headers_only=False)
# compare against corpus: is res a PREFIX of some corpus jpg (truncated append)?
cand = []
for root, dirs, files in os.walk(CORPUS):
    for f in files:
        if f.lower().endswith((".jpg", ".jpeg", ".png")):
            try:
                hb = open(os.path.join(root, f), "rb").read(len(res))
            except OSError:
                continue
            if hb == res:
                cand.append(os.path.relpath(os.path.join(root, f), CORPUS))
r5["is_prefix_of"] = cand
OUT["onion5_residue"] = r5
print("onion5 residue:", r5["walk"], r5["pil"], "prefix-of:", cand)

json.dump(OUT, open(os.path.join(CELL, "results", "deepdive.json"), "w"), indent=1)
print("WROTE results/deepdive.json")
