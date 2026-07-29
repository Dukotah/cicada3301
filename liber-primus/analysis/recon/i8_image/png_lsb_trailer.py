"""
Two unchecked stego angles (pure Python):

(A) LOSSLESS PNG LSB bit-planes. Prior stego sweep dismissed spatial LSB as
    "JPEG compression noise" -- TRUE for JPEG, but the repo also holds ~600 PNGs
    (relikd crops, solver renders). PNG is LOSSLESS, so spatial LSB IS a valid
    carrier there. Extract all 8 bit-planes per channel; flag any plane whose
    packed bytes are unusually printable / low-entropy (a hidden message) rather
    than the ~0/near-constant of a clean bilevel rune crop.

(B) Rigorous JPEG trailer / multi-EOI scan on the LP2 page JPEGs. Prior scan only
    read bytes after the LAST 0xFFD9. This walks EVERY 0xFFD9 occurrence and reports
    any data BETWEEN a mid-file EOI and the file end, plus bytes after the true EOI,
    and any second SOI (concatenated image = classic append trick).
"""
import sys, os, math, struct, json, glob
from collections import Counter
import numpy as np
from PIL import Image

def entropy(b):
    if not b: return 0.0
    c = Counter(b); n=len(b)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def png_lsb(paths):
    out = {}
    for p in paths:
        try:
            im = Image.open(p)
            if im.format not in ("PNG","BMP","GIF","TIFF"): continue
            im = im.convert("RGB"); a = np.asarray(im)
        except Exception as e:
            out[p] = {"error": str(e)}; continue
        rec = {"format": Image.open(p).format, "size": a.shape}
        planes = {}
        for ci,cn in enumerate("RGB"):
            ch = a[:,:,ci]
            for bit in range(8):
                plane = ((ch>>bit)&1).astype(np.uint8).flatten()
                nb = len(plane)//8
                if nb==0: continue
                packed = np.packbits(plane[:nb*8]).tobytes()
                # bilevel/constant planes are boring; flag only rich printable ones
                pr = sum(32<=x<127 for x in packed[:512])/min(512,len(packed))
                ent = entropy(packed[:4096])
                frac1 = plane.mean()
                # anomaly heuristic: a hidden ascii msg -> printable>0.85 AND 3<ent<6
                if pr>0.80 and 2.5<ent<6.5 and 0.05<frac1<0.95:
                    planes[f"{cn}b{bit}"] = {
                        "printable512": round(pr,3), "entropy4k": round(ent,3),
                        "frac_ones": round(float(frac1),4),
                        "preview": packed[:80].decode("latin1","replace")}
        if planes: rec["anomalous_planes"] = planes; out[p]=rec
    return out

def jpeg_trailer(paths):
    out = {}
    for p in paths:
        d = open(p,"rb").read()
        eois = []
        i = 0
        while True:
            j = d.find(b"\xff\xd9", i)
            if j<0: break
            eois.append(j); i=j+2
        sois = []
        i=0
        while True:
            j = d.find(b"\xff\xd8\xff", i)
            if j<0: break
            sois.append(j); i=j+3
        last = eois[-1] if eois else -1
        trailing = d[last+2:] if last>=0 else b""
        rec = {"size": len(d), "n_EOI": len(eois), "n_SOI": len(sois),
               "trailing_after_last_EOI": len(trailing)}
        if len(sois)>1:
            rec["multi_SOI_offsets"] = sois[:5]
        if trailing:
            rec["trailing_hex64"] = trailing[:64].hex()
            rec["trailing_entropy"] = round(entropy(trailing),3)
            rec["trailing_ascii"] = trailing[:80].decode("latin1","replace")
        # data between a mid-file EOI (not the last) and next marker: only interesting
        # if an EOI appears before SOS end -> unusual. Report count of EOI>1.
        out[os.path.basename(p)] = rec
    return out

def main():
    lp2 = sorted(glob.glob("liber-primus/data/relikd/p*.jpg"),
                 key=lambda x:(len(x),x))
    tr = jpeg_trailer(lp2)
    # PNG LSB: sample the relikd crop PNGs + rune-page-derived PNGs
    pngs = (glob.glob("liber-primus/data/relikd/*.png") +
            glob.glob("liber-primus/data/relikd/crops/*.png") +
            glob.glob("liber-primus/analysis/independent-read/reps/*.png"))
    pl = png_lsb(pngs)
    res = {"jpeg_trailer": tr, "png_lsb_anomalies": pl,
           "png_files_scanned": len(pngs)}
    json.dump(res, open("liber-primus/analysis/recon/i8_image/png_trailer_results.json","w"), indent=1)
    # summary
    any_trail = [k for k,v in tr.items() if v["trailing_after_last_EOI"]>0]
    multi_soi = [k for k,v in tr.items() if v.get("n_SOI",1)>1]
    print(f"JPEG trailer: {len(tr)} pages; with trailing bytes: {any_trail}; multi-SOI: {multi_soi}")
    print(f"PNG LSB: scanned {len(pngs)} png; anomalous planes on: {list(pl.keys())[:20]}")
    for k,v in list(pl.items())[:10]:
        print("  ", k, v.get("anomalous_planes"))

if __name__=="__main__":
    main()
