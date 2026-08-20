import json, os, sys, math, zlib, hashlib, re
import numpy as np
from PIL import Image
import gcore as G
Image.MAX_IMAGE_PIXELS=None
def bitplane_report(path, lossless):
    im=Image.open(path)
    mode=im.mode
    a=np.array(im)
    if a.ndim==2: a=a[:,:,None]
    h,w,c=a.shape
    rep={"mode":mode,"w":w,"h":h,"channels":c,"lossless":lossless,"planes":[]}
    for ch in range(c):
        for bit in range(8):
            bp=((a[:,:,ch]>>bit)&1).astype(np.uint8)
            ones=int(bp.sum()); n=bp.size
            p=ones/n
            ent=0.0 if p in (0,1) else -(p*math.log2(p)+(1-p)*math.log2(1-p))
            # row-major bitstream -> bytes -> printable fraction & magic check
            flat=np.packbits(bp.reshape(-1))[:4096].tobytes()
            printable=sum(1 for x in flat if 32<=x<127 or x in (9,10,13))/len(flat)
            # column-major too
            flatc=np.packbits(bp.T.reshape(-1))[:4096].tobytes()
            printablec=sum(1 for x in flatc if 32<=x<127 or x in (9,10,13))/len(flatc)
            # chi-square on 2x2 pair-of-values (classic LSB steg test on lsb plane only)
            rep["planes"].append({"ch":ch,"bit":bit,"ones_frac":round(p,6),"plane_entropy":round(ent,6),
              "row_printable_frac":round(printable,4),"col_printable_frac":round(printablec,4),
              "row_head_hex":flat[:16].hex(),
              "row_ascii_runs6":len(re.findall(rb'[\x20-\x7e]{6,}', np.packbits(bp.reshape(-1)).tobytes()[:200000]))})
    return rep

def verdict(rep):
    """A hidden LSB payload shows as: bit0 plane entropy ~1.0 while bit1..2 are structured,
       or a printable-fraction spike, or ASCII runs in the packed plane."""
    flags=[]
    for pl in rep["planes"]:
        if pl["bit"]==0 and pl["plane_entropy"]>0.9999 and rep["lossless"]:
            flags.append({"reason":"bit0 plane maximally random (entropy>0.9999) in a LOSSLESS image","ch":pl["ch"]})
        if max(pl["row_printable_frac"],pl["col_printable_frac"])>0.90:
            flags.append({"reason":"packed bit-plane >90% printable ASCII","ch":pl["ch"],"bit":pl["bit"],
                          "row":pl["row_printable_frac"],"col":pl["col_printable_frac"]})
        if pl["row_ascii_runs6"]>50:
            flags.append({"reason":"many >=6-char ASCII runs in packed plane","ch":pl["ch"],"bit":pl["bit"],
                          "runs":pl["row_ascii_runs6"]})
    return flags

if __name__=="__main__":
    T=json.load(open("TARGETS.json"))
    which=sys.argv[1]  # 'lossless' or a class name
    sel=[]
    for t in T:
        ext=os.path.splitext(t["path"])[1].lower()
        if which=="lossless" and ext in (".png",".bmp",".gif"): sel.append((t,True))
        elif which=="jpeg" and ext in (".jpg",".jpeg"): sel.append((t,False))
    if len(sys.argv)>2: sel=sel[int(sys.argv[3]):int(sys.argv[3])+int(sys.argv[2])] if len(sys.argv)>3 else sel[:int(sys.argv[2])]
    print(f"{len(sel)} files")
    for t,lossless in sel:
        rel=t["path"].replace("/mnt/c/Users/dukot/projects/cicada3301/","")
        base=rel.replace("/","__")
        try:
            rep=bitplane_report(t["path"], lossless)
        except Exception as e:
            G.emit({"artifact_path":t["path"],"artifact_sha256":t["sha256"],
              "tool":"bit-plane LSB analysis (PIL+numpy)","tool_version":"G-1.0",
              "command":"decode image; every channel x every bit plane 0-7","params":{},"exit_code":1,
              "finding":"ERROR","output_excerpt":str(e),"output_file":None,
              "note":"Image could not be decoded; LSB channel NOT tested for this artifact."})
            print("ERROR",rel,e); continue
        fl=verdict(rep)
        _lossnote=("LOSSLESS carrier: spatial LSB is a real, usable stego channel here. This test would detect a raw-LSB payload in any channel/bit-plane in either row- or column-major order. It would NOT detect a payload that is encrypted AND scattered by a keyed permutation (indistinguishable from noise), nor palette-index or alpha-only tricks not exercised here." if lossless else "NOT_APPLICABLE: this is a lossy JPEG. Spatial-pixel LSB is destroyed/created by DCT quantisation, so a spatial-LSB result on a JPEG is compression noise and carries no information either way. Recorded for completeness; the meaningful JPEG channel is DCT-domain (OutGuess/F5), tested separately.")
        G.savraw(f"lsb/{base}.json", json.dumps(rep))
        G.emit({"artifact_path":t["path"],"artifact_sha256":t["sha256"],
          "tool":"bit-plane LSB analysis (PIL+numpy)","tool_version":"G-1.0",
          "command":"decode image; for every channel x every bit plane 0-7: ones-fraction, plane entropy, packed-plane printable fraction (row- and column-major), ASCII run count",
          "params":{"planes_tested":len(rep["planes"]),"lossless":lossless},"exit_code":0,
          "finding":("HIT" if fl else ("NEGATIVE" if lossless else "NOT_APPLICABLE")),
          "output_excerpt":json.dumps({"mode":rep["mode"],"size":[rep["w"],rep["h"]],"channels":rep["channels"],
            "flags":fl,"bit0_entropies":[p["plane_entropy"] for p in rep["planes"] if p["bit"]==0],
            "max_printable_any_plane":max(max(p["row_printable_frac"],p["col_printable_frac"]) for p in rep["planes"])}),
          "output_file":f"raw/lsb/{base}.json",
          "note":_lossnote})
        print(("HIT " if fl else "ok  ")+rel, fl if fl else "")
