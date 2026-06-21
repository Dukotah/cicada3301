#!/usr/bin/env python3
import os, glob
from PIL import Image
from PIL.ExifTags import TAGS

ROOTS = [
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2012",
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2013",
    "/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014",
    "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd",
]
Image.MAX_IMAGE_PIXELS=None

def scan_segments_jpeg(path):
    """Read APPn / COM segments raw."""
    out=[]
    with open(path,"rb") as f:
        d=f.read()
    if d[:2]!=b"\xff\xd8": return out
    i=2; n=len(d)
    while i<n-1:
        if d[i]!=0xff: i+=1; continue
        m=d[i+1]
        if m==0xd9 or m==0xda: break
        if 0xd0<=m<=0xd7 or m in (0x01,): i+=2; continue
        if i+3>=n: break
        seglen=(d[i+2]<<8)|d[i+3]
        seg=d[i+4:i+2+seglen]
        if m==0xfe:  # COM
            out.append(("COM",seg))
        elif 0xe0<=m<=0xef:  # APPn
            # only interesting if not standard JFIF/Exif/ICC/Adobe
            tag=seg[:6]
            if not tag.startswith((b"JFIF",b"Exif",b"ICC_",b"http",b"Adobe",b"Ducky",b"\x00",b"MPF")):
                out.append((f"APP{m-0xe0}",seg))
        i+=2+seglen
    return out

found=[]
nfiles=0
for root in ROOTS:
    for p in sorted(glob.glob(os.path.join(root,"**","*"),recursive=True)):
        if not os.path.isfile(p): continue
        ext=p.lower().rsplit(".",1)[-1]
        if ext not in ("jpg","jpeg","png","gif"): continue
        nfiles+=1
        # PIL exif
        try:
            im=Image.open(p)
            ex=im.getexif()
            for k,v in ex.items():
                tag=TAGS.get(k,k)
                if tag in ("UserComment","ImageDescription","XPComment","XPKeywords","Artist","Copyright","Software","Make","Model"):
                    sv=str(v)
                    if sv.strip() and sv.strip()!="0":
                        found.append((p,"EXIF:"+str(tag),sv[:200]))
            # PNG text
            if hasattr(im,"text") and im.text:
                for k,v in im.text.items():
                    found.append((p,"PNGtext:"+k,str(v)[:200]))
            im.info_keys=list(im.info.keys())
        except Exception as e:
            pass
        # raw COM/APP segments
        if ext in ("jpg","jpeg"):
            for typ,seg in scan_segments_jpeg(p):
                # printable?
                txt=bytes(c for c in seg if 32<=c<127)
                if len(txt)>=4:
                    found.append((p,"SEG:"+typ,txt.decode('latin1')[:200]))

print(f"Scanned {nfiles} files")
print(f"Interesting metadata/segment hits: {len(found)}")
for p,t,v in found:
    print(f"\n{p}\n  [{t}] {v!r}")
