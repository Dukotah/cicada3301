#!/usr/bin/env python3
import struct

def jpeg_walk(path):
    with open(path,"rb") as f:
        data=f.read()
    print(f"FILE {path} size={len(data)}")
    if data[:2]!=b"\xff\xd8":
        print("  not jpeg soi");
    i=2
    last_real_end=None
    while i < len(data)-1:
        if data[i]!=0xff:
            i+=1; continue
        marker=data[i+1]
        if marker==0xd9:
            print(f"  EOI (FFD9) at {i}")
        if marker==0xd8:
            print(f"  SOI (FFD8) at {i}")
        if marker==0xda:  # SOS - entropy coded data follows
            print(f"  SOS at {i} (scan data follows)")
        i+=1
    # count FFD9 and FFD8
    import re
    eois=[m.start() for m in re.finditer(b"\xff\xd9",data)]
    sois=[m.start() for m in re.finditer(b"\xff\xd8",data)]
    print(f"  total FFD8(SOI)={len(sois)} positions(first few)={sois[:5]}")
    print(f"  total FFD9(EOI)={len(eois)} positions(last few)={eois[-5:]}")
    last=eois[-1]
    print(f"  bytes after last FFD9: {len(data)-(last+2)}")
    # Is there a second JPEG (SOI) embedded? Check structure: maybe EXIF thumbnail
    return data, eois, sois

for p in ["/mnt/c/Users/dukot/projects/cicada3301/puzzles/2014/images/liber_primus_pages/lp_page_05.jpg",
          "/mnt/c/Users/dukot/projects/cicada3301/liber-primus/data/relikd/0_wisdom.jpg"]:
    data,eois,sois=jpeg_walk(p)
    print()
